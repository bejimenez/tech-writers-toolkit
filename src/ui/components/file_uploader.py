# src/ui/components/file_uploader.py
"""File upload component"""

import flet as ft
from pathlib import Path
from typing import Callable, Optional, List

class FileUploader:
    """File upload component with drag-and-drop support"""
    
    def __init__(
        self,
        on_file_selected: Callable[[Path], None],
        accepted_extensions: Optional[List[str]] = None,
        max_file_size_mb: int = 50
    ):
        self.on_file_selected = on_file_selected
        self.accepted_extensions = accepted_extensions or ['.pdf', '.txt', '.docx']
        self.max_file_size_mb = max_file_size_mb
        self.selected_file = None
        self.file_picker = ft.FilePicker(
            on_result=self._on_file_picker_result
        )
        self._upload_area = None
    
    def build(self):
        """Build the file uploader component"""
        
        # Upload area - make entire area clickable for better UX
        self._upload_area = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(name="cloud_upload", size=48, color="primary"),
                    ft.Text(
                        "Click here or drag and drop your document",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        f"Supported formats: {', '.join(self.accepted_extensions)}",
                        size=12,
                        color="outline",
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Click anywhere in this area to browse files",
                        size=11,
                        color="outline",
                        text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(italic=True)
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            width=400,
            height=200,
            border=ft.border.all(2, "primary"),
            border_radius=10,
            padding=20,
            bgcolor="primary_container",
            alignment=ft.alignment.center,
            on_click=self._on_browse_click,
            on_hover=self._on_area_hover
        )
        
        return ft.Column(
            [
                self.file_picker,
                self._upload_area
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    
    def _on_area_hover(self, e):
        """Handle hover over upload area for visual feedback"""
        if e.data == "true":  # Mouse entered
            self._upload_area.bgcolor = "primary"
            self._upload_area.border = ft.border.all(3, "on_primary")
        else:  # Mouse left
            self._upload_area.bgcolor = "primary_container"
            self._upload_area.border = ft.border.all(2, "primary")
        self._upload_area.update()
    
    def _on_browse_click(self, e):
        """Handle browse button click"""
        self.file_picker.pick_files(
            dialog_title="Select Document",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=[ext.lstrip('.') for ext in self.accepted_extensions]
        )
    
    def _on_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle file picker result"""
        if e.files:
            file_path = Path(e.files[0].path)
            self._validate_and_process_file(file_path)
    
    def _validate_and_process_file(self, file_path: Path):
        """Validate and process selected file"""
        
        # Check file extension
        if file_path.suffix.lower() not in self.accepted_extensions:
            self._show_error(f"Unsupported file type: {file_path.suffix}")
            return
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            self._show_error(f"File too large: {file_size_mb:.1f}MB (max: {self.max_file_size_mb}MB)")
            return
        
        # File is valid, process it
        self.selected_file = file_path
        self.on_file_selected(file_path)
    
    def _show_error(self, message: str):
        """Show error message to user"""
        # This would typically show a snackbar or dialog
        # For now, we'll just print to console
        print(f"File upload error: {message}")