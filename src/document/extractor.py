"""Content extraction from documents with text"""

import fitz  # PyMuPDF
import time
from pathlib import Path
from typing import List, Dict

from utils.logger import LoggerMixin

class ContentExtractor(LoggerMixin):
    """Extract content from documents with readable text"""
    
    def extract_content(
        self, file_path: Path, doc_info
    ):
        """
        Extract content from a document
        
        Args:
            file_path: Path to the document
            doc_info: Document information
            
        Returns:
            ProcessedContent with extracted text and metadata
        """
        from .processor import ProcessedContent
        
        start_time = time.time()
        
        if file_path.suffix.lower() == '.pdf':
            content = self._extract_pdf_content(file_path, doc_info)
        elif file_path.suffix.lower() == '.txt':
            content = self._extract_text_content(file_path, doc_info)
        else:
            raise ValueError(f"Unsupported format for text extraction: {file_path.suffix}")
        
        processing_time = time.time() - start_time
        content.processing_time = processing_time
        
        return content
    
    def _extract_pdf_content(
        self, file_path: Path, doc_info
    ):
        from .processor import ProcessedContent
        
        """Extract content from PDF using PyMuPDF"""
        
        doc = fitz.open(file_path)
        pages = []
        images = []
        tables = []
        
        self.logger.info("Extracting PDF content", pages=len(doc))
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text
            text = page.get_text("text") # type: ignore
            pages.append(text)
            
            # Extract images
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    images.append(image_bytes)
                except Exception as e:
                    self.logger.warning(
                        "Failed to extract image",
                        page=page_num,
                        image=img_index,
                        error=str(e)
                    )
            
            # Extract tables (basic implementation)
            tables_on_page = self._extract_tables_from_page(page)
            tables.extend(tables_on_page)
        
        doc.close()
        
        # Combine all text
        full_text = "\n\n".join(pages)
        
        return ProcessedContent(
            text=full_text,
            pages=pages,
            images=images,
            tables=tables,
            document_info=doc_info,
            processing_time=0.0  # Will be set by caller
        )
    
    def _extract_text_content(
        self, file_path: Path, doc_info
    ):
        from .processor import ProcessedContent
        
        """Extract content from plain text file"""
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        return ProcessedContent(
            text=text,
            pages=[text],  # Single page for text files
            images=[],
            tables=[],
            document_info=doc_info,
            processing_time=0.0
        )
    
    def _extract_tables_from_page(self, page) -> List[str]:
        """
        Basic table extraction from PDF page
        This is a simplified implementation - can be enhanced later
        """
        tables = []
        
        try:
            # Look for table-like structures in the text
            text = page.get_text("text")
            lines = text.split('\n')
            
            current_table = []
            in_table = False
            
            for line in lines:
                # Simple heuristic: lines with multiple spaces or tabs might be tables
                if '\t' in line or '  ' in line:
                    if not in_table:
                        in_table = True
                        current_table = []
                    current_table.append(line.strip())
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
            self.logger.warning("Error extracting tables", error=str(e))
        
        return tables