"""
AIEAT About Page
"""
import flet as ft
from app.ui.theme import COLORS, APP_CONFIG


class AboutPage:
    """About page component."""

    def __init__(self, page: ft.Page):
        self.page = page

    def build(self) -> ft.Control:
        """Build the about page."""
        return ft.Container(
            padding=40,
            bgcolor=COLORS['card_bg'],
            border_radius=10,
            content=ft.Column([
                ft.Text(APP_CONFIG['title'], size=32, weight=ft.FontWeight.BOLD),
                ft.Text(APP_CONFIG['version'], size=16, color=COLORS['text_secondary']),
                ft.Divider(),
                ft.Container(height=20),
                ft.Text("Artificial Intelligence Entrepreneur Association of Thailand (AIEAT)"),
                ft.Container(height=20),
                ft.Text("Features:", weight=ft.FontWeight.BOLD),
                ft.Text("• News scraping from 74 sources"),
                ft.Text("• AI-powered scoring with keywords"),
                ft.Text("• Thai translation"),
                ft.Text("• Configurable domains and keywords"),
                ft.Text("• Multiple intelligence profiles"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
