# src/document/processor.py
"""Main document processing coordinator"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from src.utils.logger import LoggerMixin
from src.utils.decorators import log_execution_time, handle_exceptions
from src.document.extractor import ContentExtractor

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

class DocumentProcessor(LoggerMixin):
    """Main document processor that coordinates extraction methods"""
    
    def __init__(self):
        self.content_extractor = ContentExtractor()
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
        
        # Choose processing method based on content and user preference
        if file_path.suffix.lower() == '.pdf':
            # For PDFs, we'll give user the choice or use OCR if no readable text
            if doc_info.has_text:
                try:
                    content = self._process_with_text_extraction(file_path, doc_info)
                    # If text extraction yields very little content, fall back to OCR
                    if len(content.text.strip()) < 100:  # Arbitrary threshold
                        self.logger.info("Text extraction yielded minimal content, using OCR")
                        content = self._process_with_mistral_ocr(file_path, doc_info)
                except Exception as e:
                    self.logger.warning("Text extraction failed, falling back to OCR", error=str(e))
                    content = self._process_with_mistral_ocr(file_path, doc_info)
            else:
                content = self._process_with_mistral_ocr(file_path, doc_info)
        else:
            # For text files and other formats, use text extraction
            content = self._process_with_text_extraction(file_path, doc_info)
        
        self.logger.info(
            "Document processing completed",
            filename=file_path.name,
            method=content.document_info.processing_method,
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
            doc = fitz.open(file_path)
            has_text = False
            has_images = False
            
            for page in doc:
                # Use the most basic text extraction for maximum compatibility
                try:
                    text = page.getText("text")  # type: ignore
                except Exception:
                    text = ""
                if text and text.strip():
                    has_text = True
                    
                image_list = page.get_images(full=True)
                if image_list:
                    has_images = True
                    
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
        from src.document.ocr_handler import OCRHandler  # Local import to avoid circular import
        doc_info.processing_method = "mistral_ocr"
        ocr_handler = OCRHandler()
        return ocr_handler.process_with_ocr(file_path, doc_info)