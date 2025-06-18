# tests/conftest.py
"""Pytest configuration and fixtures"""

import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_text_file(temp_directory):
    """Create a sample text file for testing"""
    content = "This is a sample document for testing.\nIt has multiple lines.\nAnd some content."
    file_path = temp_directory / "sample.txt"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for mocking"""
    return {
        "text": "Sample PDF text content",
        "pages": ["Page 1 content", "Page 2 content"],
        "metadata": {"title": "Sample PDF", "author": "Test Author"}
    }