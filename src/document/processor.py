# src/document/processor.py
"""Main document processing coordinator with database integration"""

import fitz  # PyMuPDF
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from src.utils.logger import LoggerMixin
from src.utils.decorators import log_execution_time, handle_exceptions
from src.document.extractor import ContentExtractor
from src.storage.models import DatabaseManager, ReviewSession

@dataclass
class DocumentInfo:
    """Information about a processed document"""
    filename: str
    page_count: int
    file_size: int
    has_text: bool
    has_images: bool
    processing_method: str  # "text_extraction" or "mistral_ocr"
    metadata: Dict

@dataclass
class ProcessedContent:
    """Container for processed document content"""
    text: str
    pages: List[str]  # Text content per page
    images: List[bytes]  # Extracted images
    tables: List[str]  # Extracted table data
    document_info: DocumentInfo
    processing_time: float
    session_id: Optional[int] = None  # Database session ID

class DocumentProcessor(LoggerMixin):
    """Main document processor that coordinates extraction methods"""
    
    def __init__(self):
        self.content_extractor = ContentExtractor()
        self.supported_formats = ['.pdf', '.docx', '.txt']
        self.db_manager = DatabaseManager()
    
    @log_execution_time
    def process_document(
        self, 
        file_path: Path, 
        user_id: str = "default",
        force_ocr: bool = False
    ) -> ProcessedContent:
        """
        Process a document and extract all relevant content with database tracking
        
        Args:
            file_path: Path to the document file
            user_id: ID of the user processing the document
            force_ocr: Force OCR processing even if text is available
            
        Returns:
            ProcessedContent object with extracted information and session ID
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        # Validate inputs
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        self.logger.info(
            "Starting document processing", 
            filename=file_path.name,
            user_id=user_id,
            force_ocr=force_ocr
        )
        
        # Create initial database session
        session = ReviewSession(
            document_filename=file_path.name,
            document_path=str(file_path.absolute()),
            user_id=user_id,
            processing_method="determining",
            status="processing"
        )
        
        session_id = self.db_manager.create_review_session(session)
        self.logger.info("Created review session", session_id=session_id)
        
        processing_start_time = time.time()
        
        try:
            # Get document info
            doc_info = self._get_document_info(file_path)
            
            # Determine and execute processing method
            processing_method = self._determine_processing_method(
                file_path, doc_info, force_ocr
            )
            
            # Update session with processing method
            self.db_manager.update_session_processing_method(session_id, processing_method)
            
            # Process the document
            content = self._execute_processing(file_path, doc_info, processing_method)
            
            # Calculate total processing time
            total_processing_time = time.time() - processing_start_time
            content.processing_time = total_processing_time
            content.session_id = session_id
            
            # Update session as completed
            self.db_manager.update_session_status(
                session_id, 
                "completed", 
                total_processing_time
            )
            
            self.logger.info(
                "Document processing completed successfully",
                filename=file_path.name,
                session_id=session_id,
                method=processing_method,
                pages=doc_info.page_count,
                text_length=len(content.text),
                processing_time=f"{total_processing_time:.2f}s"
            )
            
            return content
            
        except Exception as e:
            # Update session as failed
            processing_time = time.time() - processing_start_time
            self.db_manager.update_session_status(
                session_id, 
                "failed", 
                processing_time
            )
            
            self.logger.error(
                "Document processing failed",
                filename=file_path.name,
                session_id=session_id,
                error=str(e),
                processing_time=f"{processing_time:.2f}s"
            )
            
            # Re-raise the exception
            raise

    def _determine_processing_method(
        self, 
        file_path: Path, 
        doc_info: DocumentInfo, 
        force_ocr: bool
    ) -> str:
        """
        Determine the best processing method for the document
        
        Args:
            file_path: Path to document
            doc_info: Document information
            force_ocr: Whether to force OCR processing
            
        Returns:
            Processing method string
        """
        if force_ocr:
            return "mistral_ocr"
        
        if file_path.suffix.lower() == '.pdf':
            if doc_info.has_text:
                # Check if we should fallback to OCR based on text quality
                return "text_extraction_with_ocr_fallback"
            else:
                return "mistral_ocr"
        else:
            # Text files and other formats use text extraction
            return "text_extraction"
    
    def _execute_processing(
        self, 
        file_path: Path, 
        doc_info: DocumentInfo, 
        processing_method: str
    ) -> ProcessedContent:
        """
        Execute the actual document processing
        
        Args:
            file_path: Path to document
            doc_info: Document information
            processing_method: Processing method to use
            
        Returns:
            ProcessedContent with extracted information
        """
        if processing_method == "text_extraction":
            return self._process_with_text_extraction(file_path, doc_info)
        
        elif processing_method == "mistral_ocr":
            return self._process_with_mistral_ocr(file_path, doc_info)
        
        elif processing_method == "text_extraction_with_ocr_fallback":
            return self._process_with_fallback(file_path, doc_info)
        
        else:
            raise ValueError(f"Unknown processing method: {processing_method}")
    
    def _process_with_fallback(
        self, 
        file_path: Path, 
        doc_info: DocumentInfo
    ) -> ProcessedContent:
        """
        Process with text extraction and OCR fallback if needed
        
        Args:
            file_path: Path to document
            doc_info: Document information
            
        Returns:
            ProcessedContent with extracted information
        """
        try:
            # Try text extraction first
            content = self._process_with_text_extraction(file_path, doc_info)
            
            # Check if text extraction yielded meaningful content
            text_length = len(content.text.strip())
            
            if text_length < 100:  # Arbitrary threshold for "meaningful content"
                self.logger.info(
                    "Text extraction yielded minimal content, falling back to OCR",
                    text_length=text_length,
                    threshold=100
                )
                
                # Fall back to OCR
                doc_info.processing_method = "mistral_ocr"
                content = self._process_with_mistral_ocr(file_path, doc_info)
            else:
                doc_info.processing_method = "text_extraction"
            
            return content
            
        except Exception as e:
            self.logger.warning(
                "Text extraction failed, falling back to OCR", 
                error=str(e)
            )
            
            # Fall back to OCR
            doc_info.processing_method = "mistral_ocr"
            return self._process_with_mistral_ocr(file_path, doc_info)

    def _get_document_info(self, file_path: Path) -> DocumentInfo:
        """Extract basic document information"""
        if file_path.suffix.lower() == '.pdf':
            return self._get_pdf_info(file_path)
        elif file_path.suffix.lower() == '.txt':
            return self._get_text_info(file_path)
        else:
            # For now, assume text extraction works for other formats
            return DocumentInfo(
                filename=file_path.name,
                page_count=1,
                file_size=file_path.stat().st_size,
                has_text=True,
                has_images=False,
                processing_method="text_extraction",
                metadata={}
            )

    def _get_pdf_info(self, file_path: Path) -> DocumentInfo:
        """Get information about a PDF document"""
        try:
            doc = fitz.open(file_path)
            has_text = False
            has_images = False
            
            # Sample first few pages to determine content type
            max_pages_to_check = min(3, len(doc))
            
            for page_num in range(max_pages_to_check):
                page = doc[page_num]
                
                # Check for text content
                try:
                    text = page.get_text("text")  # type: ignore
                except Exception:
                    text = ""
                
                if text and text.strip():
                    has_text = True
                    
                # Check for images
                image_list = page.get_images(full=True)
                if image_list:
                    has_images = True
                    
                # Early exit if we found both
                if has_text and has_images:
                    break
            
            # Ensure metadata is always a dict
            metadata = doc.metadata if doc.metadata is not None else {}
            page_count = len(doc)
            doc.close()
            
            return DocumentInfo(
                filename=file_path.name,
                page_count=page_count,
                file_size=file_path.stat().st_size,
                has_text=has_text,
                has_images=has_images,
                processing_method="text_extraction" if has_text else "mistral_ocr",
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error("Error getting PDF info", error=str(e))
            # Fallback to OCR if we can't analyze the PDF
            return DocumentInfo(
                filename=file_path.name,
                page_count=1,
                file_size=file_path.stat().st_size,
                has_text=False,
                has_images=True,
                processing_method="mistral_ocr",
                metadata={}
            )

    def _get_text_info(self, file_path: Path) -> DocumentInfo:
        """Get information about a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            has_text = bool(text.strip())
            
            return DocumentInfo(
                filename=file_path.name,
                page_count=1,
                file_size=file_path.stat().st_size,
                has_text=has_text,
                has_images=False,
                processing_method="text_extraction",
                metadata={}
            )
        except Exception as e:
            self.logger.error("Error getting text file info", error=str(e))
            return DocumentInfo(
                filename=file_path.name,
                page_count=1,
                file_size=file_path.stat().st_size,
                has_text=False,
                has_images=False,
                processing_method="text_extraction",
                metadata={}
            )

    def _process_with_text_extraction(
        self, file_path: Path, doc_info: DocumentInfo
    ) -> ProcessedContent:
        """Process document using text extraction"""
        result = self.content_extractor.extract_content(file_path, doc_info)
        result.document_info.processing_method = "text_extraction"
        return result

    def _process_with_mistral_ocr(
        self, file_path: Path, doc_info: DocumentInfo
    ) -> ProcessedContent:
        """Process document using Mistral OCR"""
        try:
            from src.document.ocr_handler import OCRHandler
        except ImportError:
            self.logger.error("OCR handler not available")
            raise ImportError("OCR functionality requires Mistral API configuration")
        
        doc_info.processing_method = "mistral_ocr"
        ocr_handler = OCRHandler()
        return ocr_handler.process_with_ocr(file_path, doc_info)
    
    def get_recent_reviews(self, user_id: str, limit: int = 10) -> List[ReviewSession]:
        """
        Get recent review sessions for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of recent ReviewSession objects
        """
        return self.db_manager.get_recent_sessions(user_id, limit)
    
    def get_session_by_id(self, session_id: int) -> Optional[ReviewSession]:
        """
        Get a specific review session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            ReviewSession object or None if not found
        """
        return self.db_manager.get_session_by_id(session_id)