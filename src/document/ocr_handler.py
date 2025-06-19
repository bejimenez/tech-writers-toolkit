# src/document/ocr_handler.py
"""Mistral OCR processing for scanned documents"""

import time
import base64
import io
from pathlib import Path
from typing import List, Dict, Any
import httpx
import fitz  # PyMuPDF
from PIL import Image

from src.utils.logger import LoggerMixin
from src.utils.config import Config
from src.utils.decorators import log_execution_time, log_api_call
from src.document.processor import ProcessedContent

class OCRHandler(LoggerMixin):
    """Handle OCR processing using Mistral Vision API"""
    
    def __init__(self):
        if not Config.MISTRAL_API_KEY:
            self.logger.error("Mistral API key not configured")
            raise ValueError("MISTRAL_API_KEY is required for OCR functionality")
        
        self.client = httpx.Client(
            base_url=Config.MISTRAL_BASE_URL,
            headers={
                "Authorization": f"Bearer {Config.MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=Config.OCR_TIMEOUT
        )
        
        self.logger.info("Mistral OCR handler initialized", model=Config.MISTRAL_MODEL)
    
    @log_execution_time
    def process_with_ocr(self, file_path: Path, doc_info) -> ProcessedContent:
        """
        Process document using Mistral OCR
        
        Args:
            file_path: Path to the document
            doc_info: Document information
            
        Returns:
            ProcessedContent with OCR-extracted text
        """
        start_time = time.time()
        
        try:
            if file_path.suffix.lower() == '.pdf':
                content = self._process_pdf_with_mistral(file_path, doc_info)
            else:
                return self._create_empty_content(doc_info, "OCR only supports PDF files")
            
            processing_time = time.time() - start_time
            content.processing_time = processing_time
            
            self.logger.info(
                "OCR processing completed",
                filename=file_path.name,
                pages=len(content.pages),
                text_length=len(content.text),
                processing_time=f"{processing_time:.2f}s"
            )
            
            return content
            
        except Exception as e:
            self.logger.error("Mistral OCR processing failed", error=str(e))
            return self._create_empty_content(doc_info, f"OCR failed: {str(e)}")
    
    def _process_pdf_with_mistral(self, file_path: Path, doc_info) -> ProcessedContent:
        """Process PDF using Mistral Vision API"""
        
        self.logger.info("Starting Mistral OCR processing", filename=file_path.name)
        
        # Open PDF and convert pages to images
        doc = fitz.open(file_path)
        page_texts = []
        images = []
        
        try:
            for page_num in range(len(doc)):
                self.logger.info(f"Processing page {page_num + 1}/{len(doc)} with Mistral OCR")
                
                page = doc[page_num]
                
                # Convert page to image
                mat = fitz.Matrix(Config.OCR_DPI / 72, Config.OCR_DPI / 72)
                # Use get_pixmap for PyMuPDF >= 1.18.0, but ensure the page is a fitz.Page
                if hasattr(page, 'get_pixmap'):
                    pix = page.get_pixmap(matrix=mat)  # type: ignore[attr-defined]
                else:
                    raise RuntimeError('fitz.Page object does not have get_pixmap method. PyMuPDF version may be incompatible.')
                
                img_data = pix.tobytes("png")
                
                # Resize image if too large
                img = Image.open(io.BytesIO(img_data))
                img = self._resize_image_if_needed(img)
                
                # Convert to base64 for API
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                
                # Store image
                images.append(img_buffer.getvalue())
                
                # Extract text using Mistral
                try:
                    text = self._extract_text_from_image(img_base64)
                    page_texts.append(text)
                except Exception as e:
                    self.logger.warning(f"OCR failed for page {page_num + 1}", error=str(e))
                    page_texts.append("")
                
        finally:
            doc.close()
        
        # Combine all text
        full_text = "\n\n".join(page_texts)
        
        return ProcessedContent(
            text=full_text,
            pages=page_texts,
            images=images,
            tables=[],  # Table extraction can be added later
            document_info=doc_info,
            processing_time=0.0  # Will be set by caller
        )
    
    @log_api_call(provider="mistral")
    def _extract_text_from_image(self, image_base64: str) -> str:
        """Extract text from image using Mistral Vision API"""
        
        prompt = """Please extract all text from this image. Return only the text content without any additional formatting or commentary. If the image contains tables, preserve the table structure using spaces or tabs. If there are multiple columns, separate them clearly."""
        
        payload = {
            "model": Config.MISTRAL_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": Config.MAX_TOKENS_PER_REQUEST,
            "temperature": 0.1  # Low temperature for consistent OCR results
        }
        
        try:
            response = self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return content.strip()
            else:
                self.logger.warning("No content in Mistral response", response=result)
                return ""
                
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Mistral API HTTP error",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
        except Exception as e:
            self.logger.error("Mistral API request failed", error=str(e))
            raise
    
    def _resize_image_if_needed(self, img: Image.Image) -> Image.Image:
        """Resize image if it exceeds maximum size"""
        max_size = Config.OCR_MAX_IMAGE_SIZE
        
        if img.width > max_size or img.height > max_size:
            # Calculate new size maintaining aspect ratio
            ratio = min(max_size / img.width, max_size / img.height)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logger.info(
                "Image resized for OCR",
                original_size=f"{img.width}x{img.height}",
                new_size=f"{new_width}x{new_height}"
            )
        
        return img
    
    def _create_empty_content(self, doc_info, reason: str) -> ProcessedContent:
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
    
    def __del__(self):
        """Clean up HTTP client"""
        if hasattr(self, 'client'):
            self.client.close()