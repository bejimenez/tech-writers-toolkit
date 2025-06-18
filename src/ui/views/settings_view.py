# src/ui/views/settings_view.py
"""Settings view for application configuration"""

import flet as ft
from typing import TYPE_CHECKING
from utils.config import Config

if TYPE_CHECKING:
    from ui.app import TechnicalWritingApp

class SettingsView:
    """Settings view component"""
    
    def __init__(self, app: "TechnicalWritingApp"):
        self.app = app
    
    def build(self) -> ft.Control:
        """Build the settings view"""
        
        # Navigation rail
        nav_rail = ft.NavigationRail(
            selected_index=2,
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
                    
                    # Settings content
                    ft.Container(
                        content=self._build_settings_content(),
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
                        "Settings",
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
    
    def _build_settings_content(self) -> ft.Control:
        """Build the settings content"""
        
        # Application settings
        app_settings = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Application Settings",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Divider(),
                        
                        # Theme setting
                        ft.Row(
                            [
                                ft.Text("Theme:", width=150),
                                ft.Dropdown(
                                    width=200,
                                    value="light",
                                    options=[
                                        ft.dropdown.Option("light", "Light"),
                                        ft.dropdown.Option("dark", "Dark"),
                                        ft.dropdown.Option("system", "System")
                                    ],
                                    on_change=self._on_theme_change
                                )
                            ]
                        ),
                        
                        # Language setting
                        ft.Row(
                            [
                                ft.Text("Language:", width=150),
                                ft.Dropdown(
                                    width=200,
                                    value="en",
                                    options=[
                                        ft.dropdown.Option("en", "English"),
                                        ft.dropdown.Option("es", "Spanish"),
                                        ft.dropdown.Option("fr", "French")
                                    ],
                                    disabled=True  # Placeholder for future
                                )
                            ]
                        ),
                    ],
                    spacing=15
                ),
                padding=20
            )
        )
        
        # AI settings
        ai_settings = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "AI Settings",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Divider(),
                        
                        ft.Row(
                            [
                                ft.Text("Default Provider:", width=150),
                                ft.Dropdown(
                                    width=200,
                                    value=Config.DEFAULT_PROVIDER,
                                    options=[
                                        ft.dropdown.Option("grok", "Grok"),
                                        ft.dropdown.Option("gemini", "Gemini")
                                    ],
                                    disabled=True  # Read-only for now
                                )
                            ]
                        ),
                        
                        ft.Row(
                            [
                                ft.Text("Max Tokens:", width=150),
                                ft.TextField(
                                    width=200,
                                    value=str(Config.MAX_TOKENS_PER_REQUEST),
                                    disabled=True  # Read-only for now
                                )
                            ]
                        ),
                        
                        ft.Row(
                            [
                                ft.Text("Enable Cache:", width=150),
                                ft.Switch(
                                    value=Config.ENABLE_RESPONSE_CACHE,
                                    disabled=True  # Read-only for now
                                )
                            ]
                        ),
                    ],
                    spacing=15
                ),
                padding=20
            )
        )
        
        # System info
        system_info = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "System Information",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Divider(),
                        
                        ft.Text(f"Application: {Config.APP_NAME}"),
                        ft.Text(f"Version: {Config.APP_VERSION}"),
                        ft.Text(f"Debug Mode: {'Enabled' if Config.DEBUG else 'Disabled'}"),
                        ft.Text(f"Log Level: {Config.LOG_LEVEL}"),
                        
                        ft.Container(height=20),
                        
                        ft.ElevatedButton(
                            "View Logs",
                            icon="description",
                            on_click=self._view_logs
                        ),
                        
                        ft.ElevatedButton(
                            "Check for Updates",
                            icon="system_update",
                            on_click=self._check_updates,
                            disabled=True  # Placeholder
                        ),
                    ],
                    spacing=10
                ),
                padding=20
            )
        )
        
        return ft.Column(
            [
                app_settings,
                ft.Container(height=20),
                ai_settings,
                ft.Container(height=20),
                system_info,
            ],
            scroll=ft.ScrollMode.AUTO
        )
    
    def _on_theme_change(self, e):
        """Handle theme change"""
        theme = e.control.value
        if not self.app.page:
            return
        if theme == "light":
            self.app.page.theme_mode = ft.ThemeMode.LIGHT
        elif theme == "dark":
            self.app.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.app.page.theme_mode = ft.ThemeMode.SYSTEM
        self.app.page.update()
    
    def _view_logs(self, e):
        """View application logs"""
        dialog = ft.AlertDialog(
            title=ft.Text("Application Logs"),
            content=ft.Text("Log viewer will be implemented in a future update."),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog(dialog))
            ]
        )
        if self.app.page and hasattr(self.app.page, 'overlay'):
            dialog.open = True
            self.app.page.overlay.append(dialog)
            self.app.page.update()
    
    def _check_updates(self, e):
        """Check for application updates"""
        dialog = ft.AlertDialog(
            title=ft.Text("Check for Updates"),
            content=ft.Text("Update checker will be implemented in a future update."),
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

    def _on_nav_change(self, e):
        """Handle navigation rail selection"""
        selected = e.control.selected_index
        
        if selected == 0:
            self.app.navigate_to("home")
        elif selected == 1:
            self.app.navigate_to("review")
        elif selected == 2:
            pass  # Already on settings
