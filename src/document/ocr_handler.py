# src/document/ocr_handler.py
"""OCR processing for scanned documents"""

import time
from pathlib import Path
from typing import List
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from ..utils.logger import LoggerMixin
from .processor import ProcessedContent, DocumentInfo

class OCRHandler(LoggerMixin):
    """Handle OCR processing for scanned documents"""
    
    def __init__(self):
        if not OCR_AVAILABLE:
            self.logger.warning(
                "OCR libraries not available. Install pytesseract and pdf2image for OCR support."
            )
    
    def process_with_ocr(
        self, file_path: Path, doc_info: DocumentInfo
    ) -> ProcessedContent:
        """
        Process document using OCR
        
        Args:
            file_path: Path to the document
            doc_info: Document information
            
        Returns:
            ProcessedContent with OCR-extracted text
        """
        if not OCR_AVAILABLE:
            return self._create_empty_content(doc_info, "OCR libraries not available")
        
        start_time = time.time()
        
        try:
            if file_path.suffix.lower() == '.pdf':
                content = self._process_pdf_with_ocr(file_path, doc_info)
            else:
                return self._create_empty_content(doc_info, "OCR only supports PDF files")