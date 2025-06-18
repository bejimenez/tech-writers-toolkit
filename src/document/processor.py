# src/document/processor.py
"""Main document processing coordinator"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..utils.logger import LoggerMixin
from ..utils.decorators import log_execution_time, handle_exceptions
from .extractor import ContentExtractor
from .ocr_handler import OCRHandler

@dataclass
class DocumentInfo:
    """Information about a processed document"""
    filename: str
    page_count: int
    file_size: int
    has_text: bool
    has_images: bool
    processing_method: str  # "text_extraction" or "ocr"
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

class DocumentProcessor(LoggerMixin):
    """Main document processor that coordinates extraction methods"""
    
    def __init__(self):
        self.content_extractor = ContentExtractor()
        self.ocr_handler = OCRHandler()
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    @log_execution_time
    def process_document(self, file_path: Path) -> ProcessedContent:
        """
        Process a document and extract all relevant content
        
        Args:
            file_path: Path to the document file
            
        Returns:
            ProcessedContent object with extracted information
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        self.logger.info("Starting document processing", filename=file_path.name)
        
        # Get document info
        doc_info = self._get_document_info(file_path)
        
        # Choose processing method based on content
        if doc_info.has_text:
            content = self._process_with_text_extraction(file_path, doc_info)
        else:
            content = self._process_with_ocr(file_path, doc_info)
        
        self.logger.info(
            "Document processing completed",
            filename=file_path.name,
            method=doc_info.processing_method,
            pages=doc_info.page_count,
            text_length=len(content.text)
        )
        
        return content
    
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
            if file_path.suffix.lower() == '.pdf':
                content = self._process_pdf_with_ocr(file_path, doc_info)
            else:
                return self._create_empty_content(doc_info, "OCR only supports PDF files")
            
            processing_time = time.time() - start_time
            content.processing_time = processing_time
            
            return content
            
        except Exception as e:
            self.logger.error("OCR processing failed", error=str(e))
            return self._create_empty_content(doc_info, f"OCR failed: {str(e)}")
    
    def _process_pdf_with_ocr(
        self, file_path: Path, doc_info: DocumentInfo
    ) -> ProcessedContent:
        """Process PDF using OCR"""
        
        self.logger.info("Starting OCR processing", filename=file_path.name)
        
        # Convert PDF to images
        try:
            pages = convert_from_path(str(file_path))
        except Exception as e:
            self.logger.error("Failed to convert PDF to images", error=str(e))
            raise
        
        page_texts = []
        images = []
        
        for i, page in enumerate(pages):
            self.logger.info(f"Processing page {i + 1}/{len(pages)} with OCR")
            
            try:
                # Perform OCR on the page
                text = pytesseract.image_to_string(page, lang='eng')
                page_texts.append(text)
                
                # Save page as image bytes
                import io
                img_bytes = io.BytesIO()
                page.save(img_bytes, format='PNG')
                images.append(img_bytes.getvalue())
                
            except Exception as e:
                self.logger.warning(f"OCR failed for page {i + 1}", error=str(e))
                page_texts.append("")
        
        # Combine all text
        full_text = "\n\n".join(page_texts)
        
        return ProcessedContent(
            text=full_text,
            pages=page_texts,
            images=images,
            tables=[],  # Table extraction from OCR is complex, skip for now
            document_info=doc_info,
            processing_time=0.0  # Will be set by caller
        )
    
    def _create_empty_content(
        self, doc_info: DocumentInfo, reason: str
    ) -> ProcessedContent:
        """Create empty content with error message"""
        
        return ProcessedContent(
            text=f"Error: {reason}",
            pages=[],
            images=[],
            tables=[],
            document_info=doc_info,
            processing_time=0.0
        )
            doc = fitz.open(file_path)
            
            # Check if document has extractable text
            has_text = False
            has_images = False
            
            for page_num in range(min(3, len(doc))):  # Check first 3 pages
                page = doc[page_num]
                text = page.get_text().strip()
                if len(text) > 50:  # Reasonable amount of text
                    has_text = True
                
                # Check for images
                image_list = page.get_images()
                if image_list:
                    has_images = True
                
                if has_text and has_images:
                    break
            
            metadata = doc.metadata
            doc.close()
            
            return DocumentInfo(
                filename=file_path.name,
                page_count=len(doc),
                file_size=file_path.stat().st_size,
                has_text=has_text,
                has_images=has_images,
                processing_method="text_extraction" if has_text else "ocr",
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
                processing_method="ocr",
                metadata={}
            )
    
    def _get_text_info(self, file_path: Path) -> DocumentInfo:
        """Get information about a text document"""
        
        return DocumentInfo(
            filename=file_path.name,
            page_count=1,
            file_size=file_path.stat().st_size,
            has_text=True,
            has_images=False,
            processing_method="text_extraction",
            metadata={}
        )
    
    def _process_with_text_extraction(
        self, file_path: Path, doc_info: DocumentInfo
    ) -> ProcessedContent:
        """Process document using text extraction"""
        
        return self.content_extractor.extract_content(file_path, doc_info)
    
    def _process_with_ocr(
        self, file_path: Path, doc_info: DocumentInfo
    ) -> ProcessedContent:
        """Process document using OCR"""
        
        return self.ocr_handler.process_with_ocr(file_path, doc_info)