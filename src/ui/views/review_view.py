# src/ui/views/review_view.py
import flet as ft
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from src.ui.components.file_uploader import FileUploader
from src.document.processor import DocumentProcessor
from src.utils.logger import LoggerMixin
from src.utils.config import Config
from src.utils.export_utils import ReviewExporter

if TYPE_CHECKING:
    from ui.app import TechnicalWritingApp

class ReviewView(LoggerMixin):
    """Review view for document processing and analysis"""
    
    def __init__(self, app: "TechnicalWritingApp"):
        self.app = app
        self.document_processor = DocumentProcessor()
        self.current_document = None
        self.review_results = None
        self.exporter = ReviewExporter()
        
        # Initialize LLM manager if AI is enabled
        self.llm_manager = None
        if self._is_ai_enabled():
            try:
                from src.ai.llm_provider import LLMManager
                self.llm_manager = LLMManager()
                self.logger.info("LLM Manager initialized for review view")
            except Exception as e:
                self.logger.warning("Failed to initialize LLM Manager", error=str(e))
        
        # UI components
        self.file_uploader = None
        self.progress_bar = None
        self.status_text = None
        self.results_container = None
    
    def _is_ai_enabled(self) -> bool:
        """Check if AI features are enabled"""
        return (Config.GROQ_API_KEY is not None or 
                Config.GEMINI_API_KEY is not None)
    
    def build(self) -> ft.Control:
        """Build the review view with escape key handler"""

        # Add keyboard handler for escape key
        if self.app.page:
            self.app.page.on_keyboard_event = self._on_keyboard_event
        
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
    
    def _on_keyboard_event(self, e):
        """Handle keyboard events for escape key"""
        if e.key == "Escape":
            self._clear_all_dialogs()
            
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
        
        # OCR force option
        self.force_ocr_checkbox = ft.Checkbox(
            label="Force OCR (for testing OCR on readable PDFs)",
            value=False
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
        
        # AI Status Card
        ai_status_card = self._build_ai_status_card()
        
        return ft.Column(
            [
                # AI Status section
                ai_status_card,
                
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
                                self.force_ocr_checkbox,
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
    
    def _build_ai_status_card(self) -> ft.Control:
        """Build AI status and testing card"""
        
        if not self._is_ai_enabled():
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon("info", color="orange"),
                                    ft.Text(
                                        "AI Features Disabled",
                                        size=18,
                                        weight=ft.FontWeight.BOLD
                                    )
                                ]
                            ),
                            ft.Text(
                                "Add GROQ_API_KEY or GEMINI_API_KEY to .env file to enable AI review features.",
                                size=12,
                                color="outline"
                            )
                        ],
                        spacing=10
                    ),
                    padding=15
                )
            )
        
        # AI is enabled - show status and test buttons
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon("smart_toy", color="green"),
                                ft.Text(
                                    "AI Review System",
                                    size=18,
                                    weight=ft.FontWeight.BOLD
                                )
                            ]
                        ),
                        ft.Text(
                            f"Default Provider: {Config.DEFAULT_PROVIDER.title()} | "
                            f"Fallback: {Config.FALLBACK_PROVIDER.title()}",
                            size=12,
                            color="outline"
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Test AI Connection",
                                    icon="wifi_tethering",
                                    on_click=self._test_ai_connection
                                ),
                                ft.ElevatedButton(
                                    "Test Groq",
                                    icon="api",
                                    on_click=lambda _: self._test_specific_provider("groq"),
                                    disabled=not Config.GROQ_API_KEY
                                ),
                                ft.ElevatedButton(
                                    "Test Gemini", 
                                    icon="api",
                                    on_click=lambda _: self._test_specific_provider("gemini"),
                                    disabled=not Config.GEMINI_API_KEY
                                )
                            ],
                            spacing=10
                        )
                    ],
                    spacing=10
                ),
                padding=15
            )
        )
    
    def _test_ai_connection(self, e):
        """Test AI connection using default provider"""
        if not self.llm_manager:
            self._show_error_dialog("AI Manager not initialized")
            return
        
        self._show_ai_test_dialog("Testing AI Connection...")
        
        try:
            # Test default provider first
            results = self.llm_manager.test_connection()
            self._show_ai_test_results(results)
            
        except Exception as e:
            self.logger.error("AI connection test failed", error=str(e))
            self._show_error_dialog(f"AI test failed: {str(e)}")
    
    def _test_specific_provider(self, provider: str):
        """Test specific AI provider"""
        if not self.llm_manager:
            self._show_error_dialog("AI Manager not initialized")
            return
        
        self._show_ai_test_dialog(f"Testing {provider.title()} connection...")
        
        try:
            results = self.llm_manager.test_connection(provider)
            self._show_ai_test_results(results)
            
        except Exception as e:
            self.logger.error(f"{provider} connection test failed", error=str(e))
            self._show_error_dialog(f"{provider.title()} test failed: {str(e)}")
    
    def _show_ai_test_dialog(self, message: str):
        """Show AI test in progress dialog"""

        self._clear_all_dialogs()  # Clear any existing dialogs
        
        dialog = ft.AlertDialog(
            title=ft.Text("AI Connection Test"),
            content=ft.Row(
                [
                    ft.ProgressRing(width=30, height=30),
                    ft.Text(message)
                ],
                spacing=15
            ),
            # Remove modal behavior that might cause issues
            modal=False
        )
        
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()
    
    def _show_ai_test_results(self, results: dict):
        """Show AI test results dialog"""
        # Close any existing dialogs
        self._clear_all_dialogs()
        
        # Build results content
        results_content = []
        
        for provider, result in results.items():
            if result["available"]:
                results_content.append(
                    ft.Row(
                        [
                            ft.Icon("check_circle", color="green"),
                            ft.Text(f"{provider.title()}: "),
                            ft.Text(
                                f"✓ Connected ({result['response_time']})",
                                color="green"
                            )
                        ]
                    )
                )
                
                # Show sample response
                if "response" in result and result["response"]:
                    results_content.append(
                        ft.Container(
                            content=ft.Text(
                                f"Response: {result['response']}",
                                size=10,
                                color="outline"
                            ),
                            padding=ft.padding.only(left=30)
                        )
                    )
            else:
                results_content.append(
                    ft.Row(
                        [
                            ft.Icon("error", color="red"),
                            ft.Text(f"{provider.title()}: "),
                            ft.Text(
                                f"✗ Failed - {result['error']}",
                                color="red"
                            )
                        ]
                    )
                )
        
        dialog = ft.AlertDialog(
            title=ft.Text("AI Connection Test Results"),
            content=ft.Container(
                content=ft.Column(
                    results_content,
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                width=500,
                height=300  # Set max height to prevent overflow
            ),
            actions=[
                ft.TextButton(
                    "Close", 
                    on_click=lambda _: self._close_dialog(dialog)
                )
            ],
            modal=False  # Remove modal behavior
        )
        
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()
    
    def _show_error_dialog(self, message: str):
        """Show error dialog"""
        # Close any existing dialogs
        self._clear_all_dialogs()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog(dialog))
            ],
            modal=False  # Remove modal behavior
        )
        
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()
    
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
            # Pass user_id and force_ocr option to document processor
            user_id = self.app.current_user or "anonymous"
            force_ocr = self.force_ocr_checkbox.value if self.force_ocr_checkbox else False
            
            self.current_document = self.document_processor.process_document(
                file_path, 
                user_id=user_id,
                force_ocr=force_ocr
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
        
        # Determine if AI review is available
        ai_review_available = self._is_ai_enabled() and self.llm_manager is not None
        
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
                            disabled=not ai_review_available
                        ),
                        ft.ElevatedButton(
                            "Export Results",
                            icon="download",
                            on_click=self._export_results,
                            tooltip="Export document processing results"
                        ),
                        ft.ElevatedButton(
                            "View Session History",
                            icon="history",
                            on_click=self._view_session_history
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
        """Start AI-powered review using agents"""
        if not self.current_document:
            self._show_error_dialog("No document loaded")
            return
        
        # Show progress dialog
        self._show_ai_review_progress("Starting AI review...")
        
        try:
            # Initialize agent manager
            from src.ai.agent_manager import AgentManager
            agent_manager = AgentManager()
            
            # Start the review process
            review_result = agent_manager.start_review(
                self.current_document,
                agents_to_use=["technical", "diagram", "formatting"]  # Current version uses technical, diagram, formatting agents only
            )
            
            # Show results
            self._show_agent_review_results(review_result)
            
        except Exception as e:
            self.logger.error("AI agent review failed", error=str(e))
            self._show_error_dialog(f"AI review failed: {str(e)}")
    
    def _show_ai_review_progress(self, message: str):
        """Show AI review progress dialog"""
        self._clear_all_dialogs()
        
        dialog = ft.AlertDialog(
            title=ft.Text("AI Agent Review"),
            content=ft.Row(
                [
                    ft.ProgressRing(width=30, height=30),
                    ft.Text(message)
                ],
                spacing=15
            ),
            modal=False
        )
        
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()
    
    def _show_agent_review_results(self, review_result):
        """Show comprehensive agent review results"""
        self._clear_all_dialogs()
        
        # Build results content
        results_content = []
        
        # Summary section
        results_content.append(
            ft.Text("Review Summary", size=18, weight=ft.FontWeight.BOLD)
        )
        results_content.append(
            ft.Container(
                content=ft.Text(
                    review_result.summary,
                    size=14
                ),
                bgcolor="surface_variant",
                padding=10,
                border_radius=5
            )
        )
        
        # Statistics
        stats_row = ft.Row([
            ft.Text(f"Status: {review_result.status.title()}", weight=ft.FontWeight.BOLD),
            ft.Text(f"Total Findings: {len(review_result.findings)}"),
            ft.Text(f"Processing Time: {review_result.total_processing_time:.2f}s")
        ], spacing=20)
        results_content.append(stats_row)
        
        results_content.append(ft.Divider())
        
        # Agent-specific results
        if review_result.agent_results:
            for agent_name, agent_findings in review_result.agent_results.items():
                results_content.append(
                    ft.Text(
                        f"{agent_name.replace('_', ' ').title()} Agent Results ({len(agent_findings)} findings)",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    )
                )
                
                if not agent_findings:
                    results_content.append(
                        ft.Text("No issues found by this agent.", color="green")
                    )
                else:
                    # Group findings by severity
                    severity_groups = {"error": [], "warning": [], "info": []}
                    for finding in agent_findings:
                        severity_groups[finding.severity].append(finding)
                    
                    # Display findings by severity
                    for severity in ["error", "warning", "info"]:
                        findings = severity_groups[severity]
                        if findings:
                            severity_colors = {
                                "error": "red",
                                "warning": "orange", 
                                "info": "blue"
                            }
                            
                            results_content.append(
                                ft.Text(
                                    f"{severity.title()}s ({len(findings)}):",
                                    weight=ft.FontWeight.BOLD,
                                    color=severity_colors[severity]
                                )
                            )
                            
                            for finding in findings:
                                finding_card = ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Row([
                                                ft.Icon(
                                                    "error" if severity == "error" else 
                                                    "warning" if severity == "warning" else "info",
                                                    color=severity_colors[severity]
                                                ),
                                                ft.Text(f"Location: {finding.location}", weight=ft.FontWeight.BOLD)
                                            ]),
                                            ft.Text(finding.description),
                                            ft.Text(
                                                f"Suggestion: {finding.suggestion}",
                                                size=12,
                                                color="outline"
                                            ) if finding.suggestion else ft.Container(),
                                            ft.Text(
                                                f"Confidence: {finding.confidence:.1%}",
                                                size=10,
                                                color="outline"
                                            )
                                        ], spacing=5),
                                        padding=10
                                    )
                                )
                                results_content.append(finding_card)
                
                results_content.append(ft.Container(height=20))
        
        # Create scrollable content
        dialog = ft.AlertDialog(
            title=ft.Text("AI Agent Review Results"),
            content=ft.Container(
                content=ft.Column(
                    results_content,
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                width=700,
                height=500
            ),
            actions=[
                ft.ElevatedButton(
                    "Export Report",
                    icon="download",
                    on_click=lambda _: self._export_agent_report(review_result)
                ),
                ft.TextButton(
                    "Close",
                    on_click=lambda _: self._close_dialog(dialog)
                )
            ],
            modal=False
        )
        
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()
    
    def _export_agent_report(self, review_result):
        """Export agent review report"""
        self._clear_all_dialogs()

        # Store review results for export
        self.review_results = review_result

        # Show format selection dialog
        self._show_export_format_dialog()

    def _show_info_dialog(self, title: str, message: str):
        """Show informational dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog(dialog))
            ]
        )
        
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
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
            self._show_error_dialog(f"Failed to load session history: {str(e)}")

    def _export_results(self, e):
        """Export processing results with format selection"""
        if not self.current_document:
            self._show_error_dialog("No document to export")
            return
        
        # show format selection dialog
        self._show_export_format_dialog()

    def _show_export_format_dialog(self):
        """Show dialog to select export format"""
        self._clear_all_dialogs()

        format_buttons = []

        # JSON export button
        json_btn = ft.ElevatedButton(
            "Export as JSON",
            icon="code",
            on_click=lambda _: self._perform_export("json"),
            tooltip="Export results in a structured JSON format"
        )
        format_buttons.append(json_btn)

        # Text Export Button
        txt_btn = ft.ElevatedButton(
            "Export as Text Report",
            icon="description",
            on_click=lambda _: self._perform_export("txt"),  # FIX: use 'txt' not 'text'
            tooltip="Export results as a human-readable text report"
        )
        format_buttons.append(txt_btn)

        # HTML export button
        html_btn = ft.ElevatedButton(
            "Export as HTML Report",
            icon="web",
            on_click=lambda _: self._perform_export("html"),
            tooltip="Export results as a formatted HTML report"
        )
        format_buttons.append(html_btn)

        dialog = ft.AlertDialog(
            title=ft.Text("Select Export Format"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Choose the format for exporting your review results:",
                        size=14
                    ),
                    ft.Container(height=10),
                    ft.Column(format_buttons, spacing=10)
                ]),
                width=300
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda _: self._close_dialog(dialog)
                )
            ],
            modal=False
        )
        
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()

    def _perform_export(self, format_type: str):
        """Perform the actual export operation"""
        self._clear_all_dialogs()
        
        # Show progress
        progress_dialog = ft.AlertDialog(
            title=ft.Text("Exporting..."),
            content=ft.Row([
                ft.ProgressRing(width=30, height=30),
                ft.Text(f"Exporting as {format_type.upper()}...")
            ], spacing=15),
            modal=False
        )
        
        if self.app.page and hasattr(self.app.page, 'overlay'):
            progress_dialog.open = True
            self.app.page.overlay.append(progress_dialog)
            self.app.page.update()
        
        try:
            # Ensure current_document is not None before exporting
            if self.current_document is None:
                self._close_dialog(progress_dialog)
                self._show_error_dialog("No document loaded to export.")
                return

            # Perform export
            exported_path = self.exporter.export_review_results(
                self.current_document,
                self.review_results,
                format_type
            )
            
            # Close progress dialog
            self._close_dialog(progress_dialog)
            
            if exported_path:
                # Show success dialog
                self._show_export_success_dialog(exported_path, format_type)
            else:
                self._show_error_dialog("Export was cancelled or failed")
            
        except Exception as e:
            self.logger.error("Export operation failed", error=str(e))
            self._close_dialog(progress_dialog)
            self._show_error_dialog(f"Export failed: {str(e)}")

    def _show_export_success_dialog(self, exported_path: Path, format_type: str):
        """Show export success confirmation"""
        dialog = ft.AlertDialog(
            title=ft.Text("Export Successful"),
            content=ft.Column([
                ft.Row([
                    ft.Icon("check_circle", color="green"),
                    ft.Text("Review results exported successfully!")
                ]),
                ft.Container(height=10),
                ft.Text(f"Format: {format_type.upper()}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Location: {exported_path}", size=12, color="outline"),
                ft.Container(height=10),
                ft.Row([
                    ft.ElevatedButton(
                        "Open File Location",
                        icon="folder_open",
                        on_click=lambda _: self._open_file_location(exported_path)
                    ),
                    ft.ElevatedButton(
                        "Export Another Format",
                        icon="download",
                        on_click=lambda _: self._export_another_format(dialog)
                    )
                ], spacing=10)
            ], spacing=5),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self._close_dialog(dialog))
            ],
            modal=False
        )
        
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()
    
    def _open_file_location(self, file_path: Path):
        """Open file location in system file manager"""
        try:
            import subprocess
            import sys
            
            if sys.platform == "win32":
                subprocess.run(["explorer", "/select,", str(file_path)])
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", "-R", str(file_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(file_path.parent)])
            
            self.logger.info("Opened file location", path=str(file_path))
            
        except Exception as e:
            self.logger.error("Failed to open file location", error=str(e))
            self._show_error_dialog("Could not open file location")
    
    def _export_another_format(self, current_dialog):
        """Close current dialog and show format selection again"""
        self._close_dialog(current_dialog)
        self._show_export_format_dialog()

    def _close_dialog(self, dialog):
        """Close any open dialog"""
        try:
            dialog.open = False
            if self.app.page and hasattr(self.app.page, 'overlay'):
                # Remove the specific dialog from overlay
                if dialog in self.app.page.overlay:
                    self.app.page.overlay.remove(dialog)
                self.app.page.update()
        except Exception as e:
            self.logger.error("Error closing dialog", error=str(e))
            # Force clear all overlays if there's an issue
            if self.app.page and hasattr(self.app.page, 'overlay'):
                self.app.page.overlay.clear()
                self.app.page.update()

    def _clear_all_dialogs(self):
        """Force clear all dialogs and overlays"""
        try:
            if self.app.page and hasattr(self.app.page, 'overlay'):
                # Close all open dialogs first
                for overlay_item in self.app.page.overlay[:]:
                    # Only close if it's an AlertDialog
                    if isinstance(overlay_item, ft.AlertDialog):
                        overlay_item.open = False
                # Clear the overlay list
                self.app.page.overlay.clear()
                self.app.page.update()
        except Exception as e:
            self.logger.error("Error clearing dialogs", error=str(e))
    
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