# tests/test_file_uploader.py
"""Tests for file uploader component"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.ui.components.file_uploader import FileUploader
import flet as ft

class TestFileUploader:
    """Test cases for FileUploader component"""
    
    def setup_method(self):
        """Setup for each test"""
        self.on_file_selected = Mock()
        self.uploader = FileUploader(
            on_file_selected=self.on_file_selected,
            accepted_extensions=['.pdf', '.txt', '.docx'],
            max_file_size_mb=50
        )
    
    def test_initialization(self):
        """Test that FileUploader initializes correctly"""
        assert self.uploader.on_file_selected == self.on_file_selected
        assert self.uploader.accepted_extensions == ['.pdf', '.txt', '.docx']
        assert self.uploader.max_file_size_mb == 50
        assert self.uploader.selected_file is None
        assert self.uploader.file_picker is not None
        assert self.uploader._upload_area is None
    
    def test_build_creates_upload_area(self):
        """Test that build method creates the upload area"""
        component = self.uploader.build()
        
        # Should return a Column with FilePicker and upload area
        assert isinstance(component, ft.Column)
        assert len(component.controls) == 2
        assert isinstance(component.controls[0], ft.FilePicker)
        
        # Upload area should be set
        assert self.uploader._upload_area is not None
        assert isinstance(self.uploader._upload_area, ft.Container)
        
        # Container should be clickable
        assert self.uploader._upload_area.on_click is not None
        assert self.uploader._upload_area.on_hover is not None
    
    def test_container_properties(self):
        """Test that the upload container has correct properties"""
        self.uploader.build()
        container = self.uploader._upload_area
        
        assert container.width == 400
        assert container.height == 200
        assert container.border_radius == 10
        assert container.padding == 20
        assert container.alignment == ft.alignment.center
    
    def test_validate_and_process_file_valid_extension(self):
        """Test file validation with valid extension"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = Path(temp_file.name)
        
        try:
            self.uploader._validate_and_process_file(temp_path)
            
            # Should call on_file_selected callback
            self.on_file_selected.assert_called_once_with(temp_path)
            assert self.uploader.selected_file == temp_path
            
        finally:
            os.unlink(temp_path)
    
    def test_validate_and_process_file_invalid_extension(self):
        """Test file validation with invalid extension"""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = Path(temp_file.name)
        
        try:
            # Mock the error display
            with patch.object(self.uploader, '_show_error') as mock_show_error:
                self.uploader._validate_and_process_file(temp_path)
                
                # Should show error and not call callback
                mock_show_error.assert_called_once()
                self.on_file_selected.assert_not_called()
                assert self.uploader.selected_file is None
            
        finally:
            os.unlink(temp_path)
    
    def test_validate_and_process_file_too_large(self):
        """Test file validation with file too large"""
        # Create a file and mock its size
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = Path(temp_file.name)
        
        try:
            # Mock the file size by patching the stat result
            mock_stat = Mock()
            mock_stat.st_size = 60 * 1024 * 1024  # 60MB
            
            with patch('pathlib.Path.stat', return_value=mock_stat):
                with patch.object(self.uploader, '_show_error') as mock_show_error:
                    self.uploader._validate_and_process_file(temp_path)
                    
                    # Should show error and not call callback
                    mock_show_error.assert_called_once()
                    assert "too large" in mock_show_error.call_args[0][0].lower()
                    self.on_file_selected.assert_not_called()
                    assert self.uploader.selected_file is None
            
        finally:
            os.unlink(temp_path)
    
    def test_file_picker_result_handler(self):
        """Test FilePicker result handling"""
        # Mock file picker result event
        mock_event = Mock()
        mock_file = Mock()
        mock_file.path = "/test/path/document.pdf"
        mock_event.files = [mock_file]
        
        with patch.object(self.uploader, '_validate_and_process_file') as mock_validate:
            self.uploader._on_file_picker_result(mock_event)
            
            # Should call validation with the file path
            mock_validate.assert_called_once_with(Path("/test/path/document.pdf"))
    
    def test_file_picker_result_no_files(self):
        """Test FilePicker result handling when no files selected"""
        mock_event = Mock()
        mock_event.files = None
        
        with patch.object(self.uploader, '_validate_and_process_file') as mock_validate:
            self.uploader._on_file_picker_result(mock_event)
            
            # Should not call validation
            mock_validate.assert_not_called()
    
    def test_browse_click_handler(self):
        """Test that browse click opens file picker"""
        mock_event = Mock()
        
        # Should call pick_files on the file picker
        with patch.object(self.uploader.file_picker, 'pick_files') as mock_pick:
            self.uploader._on_browse_click(mock_event)
            
            mock_pick.assert_called_once_with(
                dialog_title="Select Document",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=['pdf', 'txt', 'docx']
            )
    
    def test_hover_handler_enter(self):
        """Test hover handler when mouse enters"""
        self.uploader.build()
        mock_event = Mock()
        mock_event.data = "true"
        
        # Mock the update method to avoid page requirement
        with patch.object(self.uploader._upload_area, 'update'):
            self.uploader._on_area_hover(mock_event)
            
            # Should change colors for hover state
            assert self.uploader._upload_area.bgcolor == "primary"
            assert self.uploader._upload_area.border.top.width == 3
    
    def test_hover_handler_leave(self):
        """Test hover handler when mouse leaves"""
        self.uploader.build()
        mock_event = Mock()
        mock_event.data = "false"
        
        # Mock the update method to avoid page requirement
        with patch.object(self.uploader._upload_area, 'update'):
            self.uploader._on_area_hover(mock_event)
            
            # Should restore normal colors
            assert self.uploader._upload_area.bgcolor == "primary_container"
            assert self.uploader._upload_area.border.top.width == 2