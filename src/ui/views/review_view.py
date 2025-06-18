# src/ui/views/review_view.py
import flet as ft
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from ui.components.file_uploader import FileUploader
from document.processor import DocumentProcessor
from utils.logger import LoggerMixin

if TYPE_CHECKING:
    from ui.app import TechnicalWritingApp

class ReviewView(LoggerMixin):
    """Review view for document processing and analysis"""
    
    def __init__(self, app: "TechnicalWritingApp"):
        self.app = app
        self.document_processor = DocumentProcessor()
        self.current_document = None
        self.review_results = None
        
        # UI components
        self.file_uploader = None
        self.progress_bar = None
        self.status_text = None
        self.results_container = None
    
    def build(self) -> ft.Control:
        """Build the review view"""
        
        # Navigation rail
        nav_rail = ft.NavigationRail(
            selected_index=1,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon="home",
                    selected_icon="home",
                    label="Home"
                ),
                ft.NavigationRailDestination(
                    icon="description",
                    selected_icon="description",
                    label="Review"
                ),
                ft.NavigationRailDestination(
                    icon="settings",
                    selected_icon="settings",
                    label="Settings"
                ),
            ],
            on_change=self._on_nav_change,
            width=100
        )
        
        # Main content
        main_content = ft.Container(
            content=ft.Column(
                [
                    # Header
                    self._build_header(),
                    
                    # Content area
                    ft.Container(
                        content=self._build_content_area(),
                        padding=20,
                        expand=True
                    )
                ]
            ),
            expand=True
        )
        
        return ft.Row(
            [nav_rail, ft.VerticalDivider(width=1), main_content],
            expand=True,
            spacing=0
        )
    
    def _build_header(self) -> ft.Control:
        """Build the header section"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Document Review",
                        size=28,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Row(
                        [
                            ft.Text(f"Welcome, {self.app.current_user}"),
                            ft.TextButton(
                                "Logout",
                                on_click=lambda _: self.app.logout()
                            )
                        ],
                        spacing=10
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.all(20),
            bgcolor="surface_variant",
        )
    
    def _build_content_area(self) -> ft.Control:
        """Build the main content area"""
        
        # Initialize components
        self.file_uploader = FileUploader(
            on_file_selected=self._on_file_selected,
            accepted_extensions=['.pdf', '.txt', '.docx']
        )
        
        self.progress_bar = ft.ProgressBar(
            width=400,
            visible=False
        )
        
        self.status_text = ft.Text(
            "Select a document to begin review",
            size=16,
            text_align=ft.TextAlign.CENTER
        )
        
        self.results_container = ft.Container(
            content=ft.Text(""),
            visible=False
        )
        
        return ft.Column(
            [
                # Upload section
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Upload Document",
                                    size=20,
                                    weight=ft.FontWeight.BOLD
                                ),
                                self.file_uploader,
                                self.progress_bar,
                                self.status_text,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20
                        ),
                        padding=30
                    )
                ),
                
                # Results section
                self.results_container
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO
        )
    
    def _on_file_selected(self, file_path: Path):
        """Handle file selection"""
        self.logger.info("File selected for review", filename=file_path.name)
        if self.progress_bar:
            self.progress_bar.visible = True
        if self.status_text:
            self.status_text.value = f"Processing {file_path.name}..."
        if self.app.page:
            self.app.page.update()
        try:
            self.current_document = self.document_processor.process_document(file_path)
            self._show_processing_results()
        except Exception as e:
            self.logger.error("Document processing failed", error=str(e))
            if self.status_text:
                self.status_text.value = f"Error processing document: {str(e)}"
            if self.progress_bar:
                self.progress_bar.visible = False
            if self.app.page:
                self.app.page.update()
    
    def _show_processing_results(self):
        """Display document processing results"""
        if not self.current_document:
            return
        doc = self.current_document
        doc_info = doc.document_info
        results_content = ft.Column(
            [
                ft.Text(
                    "Document Processing Complete",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Document Information", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Filename: {doc_info.filename}"),
                                ft.Text(f"Pages: {doc_info.page_count}"),
                                ft.Text(f"File Size: {doc_info.file_size:,} bytes"),
                                ft.Text(f"Processing Method: {doc_info.processing_method}"),
                                ft.Text(f"Processing Time: {doc.processing_time:.2f} seconds"),
                            ],
                            spacing=5
                        ),
                        padding=15
                    )
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Text Content Preview", weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text(
                                        doc.text[:1000] + "..." if len(doc.text) > 1000 else doc.text,
                                        size=12,
                                        selectable=True
                                    ),
                                    bgcolor="surface_variant",
                                    padding=10,
                                    border_radius=5,
                                    height=200,
                                    width=600
                                ),
                                ft.Text(f"Total text length: {len(doc.text)} characters")
                            ],
                            spacing=10
                        ),
                        padding=15
                    )
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Start AI Review",
                            icon="smart_toy",
                            on_click=self._start_ai_review,
                            disabled=True  # Will be enabled in Phase 2
                        ),
                        ft.ElevatedButton(
                            "Export Results",
                            icon="download",
                            on_click=self._export_results
                        ),
                        ft.ElevatedButton(
                            "Process Another Document",
                            icon="add",
                            on_click=self._reset_view
                        )
                    ],
                    spacing=10
                )
            ],
            spacing=15
        )
        if self.results_container:
            self.results_container.content = results_content
            self.results_container.visible = True
        if self.progress_bar:
            self.progress_bar.visible = False
        if self.status_text:
            self.status_text.value = "Document processed successfully!"
        if self.app.page:
            self.app.page.update()
    
    def _start_ai_review(self, e):
        """Start AI-powered review (placeholder for Phase 2)"""
        dialog = ft.AlertDialog(
            title=ft.Text("AI Review"),
            content=ft.Text("AI review functionality will be implemented in Phase 2."),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog(dialog))
            ]
        )
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()

    def _export_results(self, e):
        """Export processing results"""
        if not self.current_document:
            return
        dialog = ft.AlertDialog(
            title=ft.Text("Export Results"),
            content=ft.Text("Export functionality will be implemented soon."),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog(dialog))
            ]
        )
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()

    def _close_dialog(self, dialog):
        """Close any open dialog"""
        dialog.open = False
        if self.app.page and hasattr(self.app.page, 'overlay') and dialog in self.app.page.overlay:
            self.app.page.overlay.remove(dialog)
            self.app.page.update()
    
    def _reset_view(self, e):
        """Reset the view to upload a new document"""
        self.current_document = None
        self.review_results = None
        if self.results_container:
            self.results_container.visible = False
        if self.progress_bar:
            self.progress_bar.visible = False
        if self.status_text:
            self.status_text.value = "Select a document to begin review"
        if self.app.page:
            self.app.page.update()
    
    def _on_nav_change(self, e):
        """Handle navigation rail selection"""
        selected = e.control.selected_index
        
        if selected == 0:
            self.app.navigate_to("home")
        elif selected == 1:
            pass  # Already on review
        elif selected == 2:
            self.app.navigate_to("settings")
