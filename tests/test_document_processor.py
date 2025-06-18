# tests/test_document_processor.py
"""Tests for document processing functionality"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import os

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.document.processor import DocumentProcessor, DocumentInfo
from src.utils.config import Config

class TestDocumentProcessor:
    """Test cases for DocumentProcessor"""
    
    def setup_method(self):
        """Setup for each test"""
        self.processor = DocumentProcessor()
    
    def test_supported_formats(self):
        """Test that supported formats are correctly defined"""
        expected_formats = ['.pdf', '.docx', '.txt']
        assert self.processor.supported_formats == expected_formats
    
    def test_unsupported_file_format(self):
        """Test handling of unsupported file formats"""
        with tempfile.NamedTemporaryFile(suffix='.xyz') as temp_file:
            temp_path = Path(temp_file.name)
            
            with pytest.raises(ValueError, match="Unsupported file format"):
                self.processor.process_document(temp_path)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent files"""
        nonexistent_path = Path("nonexistent_file.pdf")
        
        with pytest.raises(FileNotFoundError, match="Document not found"):
            self.processor.process_document(nonexistent_path)
    
    def test_text_file_processing(self):
        """Test processing of plain text files"""
        test_content = "This is a test document.\nWith multiple lines.\nAnd some content."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_path = Path(temp_file.name)
        
        try:
            result = self.processor.process_document(temp_path)
            
            assert result.text == test_content
            assert len(result.pages) == 1
            assert result.pages[0] == test_content
            assert result.document_info.filename == temp_path.name
            assert result.document_info.processing_method == "text_extraction"
            assert result.processing_time > 0
        
        finally:
            os.unlink(temp_path)
    
    @patch('fitz.open')
    def test_pdf_info_extraction(self, mock_fitz_open):
        """Test PDF information extraction"""
        # Mock PDF document
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=3)  # 3 pages
        mock_doc.metadata = {"title": "Test Document"}
        
        # Mock page with text
        mock_page = Mock()
        mock_page.get_text.return_value = "Sample text content for testing"
        mock_page.get_images.return_value = []
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_file:
            temp_path = Path(temp_file.name)
            
            doc_info = self.processor._get_pdf_info(temp_path)
            
            assert doc_info.filename == temp_path.name
            assert doc_info.page_count == 3
            assert doc_info.has_text == True
            assert doc_info.processing_method == "text_extraction"
            assert doc_info.metadata["title"] == "Test Document"