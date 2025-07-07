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
        
        # Upload area - make entire area clickable for better UX and add drag/drop support
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
                        "Drag files here or click anywhere to browse",
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
        
        # Add HTML5 drag and drop event handlers
        self._setup_drag_drop_handlers()
        
        return ft.Column(
            [
                self.file_picker,
                self._upload_area
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        return ft.Column(
            [
                self.file_picker,
                self._upload_area
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    
    def _setup_drag_drop_handlers(self):
        """Setup HTML5 drag and drop event handlers"""
        if self._upload_area:
            # Add drag and drop event handlers
            self._upload_area._add_event_handler("dragover", self._on_drag_over)
            self._upload_area._add_event_handler("dragenter", self._on_drag_enter)
            self._upload_area._add_event_handler("dragleave", self._on_drag_leave)
            self._upload_area._add_event_handler("drop", self._on_drop)
    
    def _on_drag_over(self, e):
        """Handle drag over event - prevent default to allow drop"""
        # This event fires continuously while dragging over the element
        # We need to prevent default to allow dropping
        pass
    
    def _on_drag_enter(self, e):
        """Handle drag enter event - visual feedback when drag enters"""
        if self._upload_area:
            self._upload_area.bgcolor = "secondary_container"
            self._upload_area.border = ft.border.all(3, "secondary")
            if hasattr(self._upload_area, 'update') and self._upload_area.page:
                self._upload_area.update()
    
    def _on_drag_leave(self, e):
        """Handle drag leave event - restore normal appearance"""
        if self._upload_area:
            self._upload_area.bgcolor = "primary_container"
            self._upload_area.border = ft.border.all(2, "primary")
            if hasattr(self._upload_area, 'update') and self._upload_area.page:
                self._upload_area.update()
    
    def _on_drop(self, e):
        """Handle file drop event"""
        # Restore normal appearance
        self._on_drag_leave(e)
        
        # Process dropped files
        try:
            # The event should contain file information
            # Note: The exact structure of the event data may vary
            # We'll need to handle this based on how Flet passes file information
            if hasattr(e, 'data') and e.data:
                # Try to extract file information from the event
                self._process_dropped_files(e.data)
            else:
                # Fallback to file picker if drag data is not available
                self._show_error("Drag and drop detected but file data not available. Please use click to browse.")
        except Exception as ex:
            self._show_error(f"Error processing dropped file: {str(ex)}")
    
    def _process_dropped_files(self, drop_data):
        """Process files from drag and drop event"""
        try:
            # Handle different possible data formats
            # This might need adjustment based on actual Flet implementation
            files = []
            
            if isinstance(drop_data, str):
                # Single file path
                files = [drop_data]
            elif isinstance(drop_data, list):
                # Multiple files
                files = drop_data
            elif hasattr(drop_data, 'files'):
                # Event with files property
                files = [f.path if hasattr(f, 'path') else str(f) for f in drop_data.files]
            
            if files:
                # Process the first file (since we only support single file upload)
                file_path = Path(files[0])
                self._validate_and_process_file(file_path)
            else:
                self._show_error("No valid files found in drop data")
                
        except Exception as e:
            self._show_error(f"Error processing dropped files: {str(e)}")
    
    def _on_area_hover(self, e):
        """Handle hover over upload area for visual feedback"""
        if e.data == "true":  # Mouse entered
            self._upload_area.bgcolor = "primary"
            self._upload_area.border = ft.border.all(3, "on_primary")
        else:  # Mouse left
            self._upload_area.bgcolor = "primary_container"
            self._upload_area.border = ft.border.all(2, "primary")
        if hasattr(self._upload_area, 'update') and self._upload_area.page:
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