# src/document/ocr_handler.py
"""OCR processing for scanned documents"""

import time
from pathlib import Path
from typing import List, Optional
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
            elif file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                content = self._process_image_with_ocr(file_path, doc_info)
            else:
                return self._create_empty_content(
                    doc_info, 
                    f"OCR does not support {file_path.suffix} files"
                )
            
            processing_time = time.time() - start_time
            content.processing_time = processing_time
            
            self.logger.info(
                "OCR processing completed",
                filename=file_path.name,
                pages=len(content.pages),
                text_length=len(content.text),
                processing_time=f"{processing_time:.3f}s"
            )
            
            return content
            
        except Exception as e:
            self.logger.error(
                "OCR processing failed",
                filename=file_path.name,
                error=str(e)
            )
            return self._create_empty_content(
                doc_info, 
                f"OCR processing failed: {str(e)}"
            )
    
    def _process_pdf_with_ocr(
        self, file_path: Path, doc_info: DocumentInfo
    ) -> ProcessedContent:
        """Process PDF using OCR"""
        
        self.logger.info("Starting PDF OCR processing", filename=file_path.name)
        
        try:
            # Convert PDF to images
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
                # Configure Tesseract for better accuracy
                custom_config = r'--oem 3 --psm 6 -l eng'
                
                # Perform OCR on the page
                text = pytesseract.image_to_string(page, config=custom_config)
                page_texts.append(text.strip())
                
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
            tables=self._extract_tables_from_text(full_text),
            document_info=doc_info,
            processing_time=0.0  # Will be set by caller
        )
    
    def _process_image_with_ocr(
        self, file_path: Path, doc_info: DocumentInfo
    ) -> ProcessedContent:
        """Process a single image file using OCR"""
        
        self.logger.info("Starting image OCR processing", filename=file_path.name)
        
        try:
            # Open the image
            image = Image.open(file_path)
            
            # Configure Tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6 -l eng'
            
            # Perform OCR
            text = pytesseract.image_to_string(image, config=custom_config)
            text = text.strip()
            
            # Convert image to bytes for storage
            import io
            img_bytes = io.BytesIO()
            image.save(img_bytes, format=image.format or 'PNG')
            
            return ProcessedContent(
                text=text,
                pages=[text],  # Single page for images
                images=[img_bytes.getvalue()],
                tables=self._extract_tables_from_text(text),
                document_info=doc_info,
                processing_time=0.0  # Will be set by caller
            )
            
        except Exception as e:
            self.logger.error("Failed to process image with OCR", error=str(e))
            raise
    
    def _extract_tables_from_text(self, text: str) -> List[str]:
        """
        Extract table-like structures from OCR text
        This is a basic implementation that looks for tabular patterns
        """
        tables = []
        
        try:
            lines = text.split('\n')
            current_table = []
            in_table = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    if in_table and current_table:
                        # End of table
                        tables.append('\n'.join(current_table))
                        current_table = []
                        in_table = False
                    continue
                
                # Simple heuristic: lines with multiple spaces or tabs might be tables
                # Also look for common table separators
                if (
                    '\t' in line or 
                    '  ' in line or 
                    '|' in line or
                    line.count(' ') > 3
                ):
                    if not in_table:
                        in_table = True
                        current_table = []
                    current_table.append(line)
                else:
                    if in_table and current_table:
                        # End of table
                        tables.append('\n'.join(current_table))
                        current_table = []
                        in_table = False
            
            # Don't forget the last table
            if in_table and current_table:
                tables.append('\n'.join(current_table))
        
        except Exception as e:
            self.logger.warning("Error extracting tables from OCR text", error=str(e))
        
        return tables
    
    def _create_empty_content(
        self, doc_info: DocumentInfo, reason: str
    ) -> ProcessedContent:
        """Create empty content with error message"""
        
        self.logger.warning("Creating empty content", reason=reason)
        
        return ProcessedContent(
            text=f"Error: {reason}",
            pages=[],
            images=[],
            tables=[],
            document_info=doc_info,
            processing_time=0.0
        )
    
    def is_available(self) -> bool:
        """Check if OCR functionality is available"""
        return OCR_AVAILABLE
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats for OCR"""
        return ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    
    def configure_tesseract(self, tesseract_path: Optional[str] = None):
        """
        Configure Tesseract executable path if needed
        
        Args:
            tesseract_path: Path to tesseract executable
        """
        if not OCR_AVAILABLE:
            self.logger.warning("OCR libraries not available")
            return
        
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            self.logger.info("Tesseract path configured", path=tesseract_path)