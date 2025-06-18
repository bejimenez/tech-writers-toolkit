# src/ui/views/login_view.py
"""Login view for user authentication"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import TechnicalWritingApp

class LoginView:
    """Login view for user authentication"""

    def __init__(self, app: "TechnicalWritingApp"):
        self.app = app
        self.username_field = None
        self.password_field = None
        self.error_text = None

    def build(self) -> ft.Control:
        """Build the login view UI components"""

        # Create input fields for username and password
        self.username_field = ft.TextField(
            label="Username",
            width=300,
            autofocus=True,
            on_submit=self._on_login_click
        )

        self.password_field = ft.TextField(
            label="Password",
            width=300,
            password=True,
            can_reveal_password=True,
            on_submit=self._on_login_click
        )

        self.error_text = ft.Text(
            "",
            color=ft.colors.ERROR,
            size=14
        )

        login_button = ft.ElevatedButton(
            "Login",
            width=100,
            on_click=self._on_login_click
        )

        # Create the login form layout
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=100), # Spacer for top margin
                    ft.Text(
                        self.app.page.title,
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=50),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Login",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.Container(height=20),
                                    self.username_field,
                                    self.password_field
                                    self.error_text,
                                    ft.Container(height=20),
                                    login_button
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10
                            ),
                            padding=30
                        ),
                        width=400,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
            ),
            expand=True,
            alighnment=ft.Alignment.center
        )
    
    def _on_login_click(self, e):
        """Handle login button click"""
        username = self.username_field.value
        password = self.password_field.value

        if not username or not password:
            self.error_text.value = "Username and password cannot be empty."
            self.app.page.update()
            return
        
        if self.app.authenticate_user(username, password):
            self.app.navigate_to("home")
        else:
            self.error_text.value = "Invalid username or password."
            self.app.page.update()