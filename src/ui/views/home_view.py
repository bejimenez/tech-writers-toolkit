# src/ui/views/home_view.py
"""Home view for the Technical Writing Assistant with navigation and overview"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import TechnicalWritingApp

class HomeView:
    """Home view for the Technical Writing Assistant application"""

    def __init__(self, app: "TechnicalWritingApp"):
        self.app = app

    def build(self) -> ft.Control:
        """Build the home view UI components"""

        # Navigation rail
        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon="home",
                    selected_icon="home",
                    label="Home",
                ),
                ft.NavigationRailDestination(
                    icon="reviews",
                    selected_icon="reviews",
                    label="Review",
                ),
                ft.NavigationRailDestination(
                    icon="settings",
                    selected_icon="settings",
                    label="Settings",
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
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    "Technical Writing Assistant",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Row(
                                    [
                                        ft.Text(f"Welcome, {self.app.current_user}"),
                                        ft.TextButton(
                                            "Logout",
                                            on_click=self._on_logout
                                        )
                                    ],
                                    spacing=10
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=ft.padding.all(20),
                        bgcolor="surface_variant",
                    ),

                    # Dashboard content
                    ft.Container(
                        content=self._build_dashboard(),
                        padding=20,
                        expand=True
                    )
                ]
            ),
            expand=True,
        )

        return ft.Row(
            [nav_rail, ft.VerticalDivider(width=1), main_content],
            expand=True,
            spacing=0,
        )
    
    def _build_dashboard(self) -> ft.Control:
        """Build the dashboard content"""

        # Quick actions
        quick_actions = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Quick Actions",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    content=ft.Column(
                                        [
                                            ft.Icon(name="upload_file", size=32),
                                            ft.Text("Review Document")
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5
                                    ),
                                    width=150,
                                    height=100,
                                    on_click=lambda _: self.app.navigate_to("review")
                                ),
                                ft.ElevatedButton(
                                    content=ft.Column(
                                        [
                                            ft.Icon(name="history", size=32),
                                            ft.Text("Recent Reviews")
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5
                                    ),
                                    width=150,
                                    height=100,
                                    on_click=self._show_recent_reviews
                                ),
                                ft.ElevatedButton(
                                    content=ft.Column(
                                        [
                                            ft.Icon(name="settings", size=32),
                                            ft.Text("Settings")
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5
                                    ),
                                    width=150,
                                    height=100,
                                    on_click=lambda _: self.app.navigate_to("settings")
                                ),
                            ],
                            spacing=20
                        )
                    ],
                    spacing=15
                ),
                padding=20
            )
        )

        # System status
        status_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "System Status",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Row(
                            [
                                ft.Icon(name="check_circle", color="green"),
                                ft.Text("Document Processing: Ready")
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(name="check_circle", color="green"),
                                ft.Text("AI Services: Connected")
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(name="check_circle", color="green"),
                                ft.Text("Database: Online")
                            ]
                        ),
                    ],
                    spacing=10
                ),
                padding=20
            )
        )
        
        return ft.Column(
            [
                quick_actions,
                ft.Container(height=20),
                status_card,
            ],
            spacing=0
        )
    
    def _on_nav_change(self, e):
        """Handle navigation rail selection"""
        selected = e.control.selected_index
        
        if selected == 0:
            pass  # Already on home
        elif selected == 1:
            self.app.navigate_to("review")
        elif selected == 2:
            self.app.navigate_to("settings")
    
    def _on_logout(self, e):
        """Handle logout"""
        self.app.logout()
    
    def _show_recent_reviews(self, e):
        """Show recent reviews dialog"""
        # TODO: Implement recent reviews functionality
        dialog = ft.AlertDialog(
            title=ft.Text("Recent Reviews"),
            content=ft.Text("No recent reviews found."),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self._close_dialog(dialog))
            ]
        )
        dialog.open = True
        if self.app.page and hasattr(self.app.page, 'overlay'):
            self.app.page.overlay.append(dialog)
            self.app.page.update()

    def _close_dialog(self, dialog):
        """Close any open dialog"""
        dialog.open = False
        if self.app.page:
            self.app.page.update()