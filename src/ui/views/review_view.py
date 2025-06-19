# src/ui/views/review_view.py
import flet as ft
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from src.ui.components.file_uploader import FileUploader
from src.document.processor import DocumentProcessor
from src.utils.logger import LoggerMixin

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
                                self.file_uploader.build(),
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
        """Handle file selection with database integration"""
        self.logger.info("File selected for review", filename=file_path.name)
        
        if self.progress_bar:
            self.progress_bar.visible = True
        if self.status_text:
            self.status_text.value = f"Processing {file_path.name}..."
        if self.app.page:
            self.app.page.update()
        
        try:
            # Pass user_id to document processor
            user_id = self.app.current_user or "anonymous"
            self.current_document = self.document_processor.process_document(
                file_path, 
                user_id=user_id
            )
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
        """Display document processing results with session info"""
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
                
                # Session Information Card
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Session Information", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Session ID: {doc.session_id}"),
                                ft.Text(f"User: {self.app.current_user}"),
                                ft.Text(f"Status: Completed"),
                            ],
                            spacing=5
                        ),
                        padding=15
                    )
                ),
                
                # Document Information Card
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
                                ft.Text(f"Has Text: {'Yes' if doc_info.has_text else 'No'}"),
                                ft.Text(f"Has Images: {'Yes' if doc_info.has_images else 'No'}"),
                            ],
                            spacing=5
                        ),
                        padding=15
                    )
                ),
                
                # Text Content Preview Card
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
                
                # Action Buttons
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Start AI Review",
                            icon="smart_toy",
                            on_click=self._start_ai_review,
                            disabled=True  # Will be enabled in Phase 2
                        ),
                        ft.ElevatedButton(
                            "View Session History",
                            icon="history",
                            on_click=self._view_session_history
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

    def _view_session_history(self, e):
        """View recent processing sessions"""
        try:
            user_id = self.app.current_user or "anonymous"
            recent_sessions = self.document_processor.get_recent_reviews(user_id, limit=5)
            
            if not recent_sessions:
                content = ft.Text("No recent sessions found.")
            else:
                session_list = []
                for session in recent_sessions:
                    session_list.append(
                        ft.ListTile(
                            leading=ft.Icon("description"),
                            title=ft.Text(session.document_filename),
                            subtitle=ft.Text(
                                f"Status: {session.status} | "
                                f"Method: {session.processing_method} | "
                                f"Time: {session.total_processing_time:.2f}s"
                            ),
                            trailing=ft.Text(
                                session.created_at.strftime("%m/%d %H:%M") 
                                if session.created_at else "Unknown"
                            )
                        )
                    )
                
                content = ft.Column(
                    [
                        ft.Text("Recent Processing Sessions:", weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        *session_list
                    ],
                    height=300,
                    scroll=ft.ScrollMode.AUTO
                )
            
            dialog = ft.AlertDialog(
                title=ft.Text("Session History"),
                content=content,
                actions=[
                    ft.TextButton("Close", on_click=lambda _: self._close_dialog(dialog))
                ]
            )
            
            if self.app.page and hasattr(self.app.page, 'overlay'):
                dialog.open = True
                self.app.page.overlay.append(dialog)
                self.app.page.update()
                
        except Exception as e:
            self.logger.error("Failed to load session history", error=str(e))
            error_dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"Failed to load session history: {str(e)}"),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self._close_dialog(error_dialog))
                ]
            )
            if self.app.page and hasattr(self.app.page, 'overlay'):
                error_dialog.open = True
                self.app.page.overlay.append(error_dialog)
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
