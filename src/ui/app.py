# src/ui/app.py
"""Main application entry point for the UI"""

import flet as ft
from typing import Dict, Any

from utils.config import Config
from utils.logger import LoggerMixin
from src.ui.views.home_view import HomeView
from src.ui.views.login_view import LoginView
from src.ui.views.review_view import ReviewView
from src.ui.views.settings_view import SettingsView

class TechnicalWritingApp(LoggerMixin):
    """Main application class for the Technical Writing Assistant UI"""

    def __init__(self):
        self.current_view = "home"
        self.views: Dict[str, Any] = {}
        self.page = None
        self.authenticated = False
        self.current_user = None

    def main(self, page: ft.Page):
        """Main entry point for the Flet application"""
        self.page = page
        if self.page:
            self._setup_page()
            self._initialize_views()
            self._setup_navigation()
            self._show_initial_view()
            self.logger.info("Technical Writing Assistant started successfully", view=self.current_view)

    def _setup_page(self):
        """Configure the main page properties"""
        if not self.page:
            return
        self.page.title = Config.APP_NAME
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0

        # Set up theme
        self.page.theme = ft.Theme(
            color_scheme_seed="indigo",
            use_material3=True
        )

    def _initialize_views(self):
        """Initialize all views used in the application"""
        self.views = {
            "login": LoginView(self),
            "home": HomeView(self),
            "review": ReviewView(self),
            "settings": SettingsView(self)
        }

    def _setup_navigation(self):
        """Set up navigation and routing between views"""
        if not self.page:
            return
        def on_route_change(route):
            self.logger.info("Route changed", route=route.route)
            self.navigate_to(route.route.strip("/"))

        self.page.on_route_change = on_route_change

    def _show_initial_view(self):
        """Show the initial view based on authentication status"""
        if self.authenticated:
            self.navigate_to("home")
        else:
            self.navigate_to("login")

    def navigate_to(self, view_name: str):
        """Navigate to a specific view"""
        if view_name not in self.views:
            self.logger.warning("Unknown view", view=view_name)
            view_name = "home"
        self.current_view = view_name
        if not self.page:
            return
        
        # Clear existing controls
        self.page.clean()
        
        # Add the requested view
        view_instance = self.views[view_name]
        self.page.add(view_instance.build())
        
        # Update the page route
        self.page.route = f"/{view_name}"
        self.page.update()
        self.logger.info("Navigated to view", view=view_name)

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user (placeholder for actual authentication logic)"""
        # TODO: Implement actual authentication
        if username and password:
            self.authenticated = True
            self.current_user = username
            self.logger.info("User authenticated", user=username)
            return True
        return False
    
    def logout(self):
        """Logout the current user"""
        self.logger.info("User logged out", user=self.current_user)
        self.authenticated = False
        self.current_user = None
        self.navigate_to("login")
