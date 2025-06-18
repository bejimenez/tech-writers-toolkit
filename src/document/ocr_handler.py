# src/document/ocr_handler.py
"""OCR processing for scanned documents"""

import time
import os
from pathlib import Path
from typing import List
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from src.utils.logger import LoggerMixin

class OCRHandler(LoggerMixin):
    """Handle OCR processing for scanned documents"""
    
    def __init__(self):
        if not OCR_AVAILABLE:
            self.logger.warning(
                "OCR libraries not available. Install pytesseract and pdf2image for OCR support."
            )
        else:
            # Configure Tesseract path if needed
            tesseract_path = r"C:\Users\brijim\OneDrive - ASSA ABLOY Group\Documents\tesseractOCR\tesseract.exe"
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                self.logger.info("Tesseract path configured", path=tesseract_path)
            
            # Configure Poppler path if needed
            poppler_path = r"C:\Users\brijim\OneDrive - ASSA ABLOY Group\Documents\poppler\Library\bin"
            if os.path.exists(poppler_path):
                # Add to PATH for this session
                current_path = os.environ.get('PATH', '')
                if poppler_path not in current_path:
                    os.environ['PATH'] = f"{poppler_path};{current_path}"
                    self.logger.info("Poppler path configured", path=poppler_path)
    
    def process_with_ocr(
        self, file_path: Path, doc_info
    ):
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
            
            processing_time = time.time() - start_time
            content.processing_time = processing_time
            
            return content
            
        except Exception as e:
            self.logger.error("OCR processing failed", error=str(e))
            return self._create_empty_content(doc_info, f"OCR failed: {str(e)}")
    
    def _process_pdf_with_ocr(
        self, file_path: Path, doc_info
    ):
        """Process PDF using OCR"""
        
        from src.document.processor import ProcessedContent
        
        self.logger.info("Starting OCR processing", filename=file_path.name)
        
        # Convert PDF to images with specific poppler path if configured
        try:
            # Try with poppler_path parameter first
            poppler_path = r"C:\Users\brijim\OneDrive - ASSA ABLOY Group\Documents\poppler\Library\bin"
            if os.path.exists(poppler_path):
                pages = convert_from_path(str(file_path), poppler_path=poppler_path, dpi=300)
            else:
                # Fall back to system PATH
                pages = convert_from_path(str(file_path), dpi=300)
            
            self.logger.info(f"Converted PDF to {len(pages)} images")
            
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
        self, doc_info, reason: str
    ):
        """Create empty content with error message"""
        
        from src.document.processor import ProcessedContent
        
        self.logger.warning("Creating empty content", reason=reason)
        
        return ProcessedContent(
            text=f"Error: {reason}",
            pages=[],
            images=[],
            tables=[],
            document_info=doc_info,
            processing_time=0.0
        )