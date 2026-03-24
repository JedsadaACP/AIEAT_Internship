"""
AIEAT About Page - Application information and credits.
"""
import flet as ft
from app.ui.theme import COLORS


class AboutPage:
    """About page component with app information."""
    
    def __init__(self, page: ft.Page):
        self.page = page
    
    def build(self) -> ft.Control:
        """Build the about page."""
        return ft.Container(
            padding=30,
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=32, color=COLORS['accent']),
                    ft.Text("About AIEAT", size=24, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Divider(height=20),
                
                # App Info Card
                ft.Container(
                    padding=20,
                    bgcolor=COLORS['card_bg'],
                    border_radius=8,
                    content=ft.Column([
                        ft.Text("AIEAT News Dashboard", 
                                size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        
                        self._info_row("Version", "1.0.0"),
                        self._info_row("Built With", "Flet + Ollama + SQLite"),
                        self._info_row("AI Models", "Typhoon 2.5"),
                        self._info_row("Purpose", "News aggregation, scoring, and Thai translation"),
                        
                        ft.Container(height=15),
                        ft.Divider(),
                        ft.Container(height=15),
                        
                        ft.Text("Features", weight=ft.FontWeight.W_600, size=14),
                        ft.Container(height=5),
                        ft.Text("• Automated news scraping from configured sources", size=12),
                        ft.Text("• AI-powered relevance scoring", size=12),
                        ft.Text("• Thai translation with customizable styles", size=12),
                        ft.Text("• Export to CSV and clipboard", size=12),
                        
                    ], spacing=2)
                ),
                
                ft.Container(height=20),
                
                # Tech Stack Card
                ft.Container(
                    padding=20,
                    bgcolor=COLORS['card_bg'],
                    border_radius=8,
                    content=ft.Column([
                        ft.Text("Tech Stack", weight=ft.FontWeight.BOLD, size=14),
                        ft.Container(height=10),
                        
                        ft.Row([
                            self._tech_chip("Python 3.10+"),
                            self._tech_chip("Flet UI"),
                            self._tech_chip("Ollama API"),
                        ], wrap=True, spacing=8),
                        ft.Row([
                            self._tech_chip("SQLite"),
                            self._tech_chip("aiohttp"),
                            self._tech_chip("trafilatura"),
                        ], wrap=True, spacing=8),
                    ])
                ),
                
                ft.Container(height=20),
                
                # Credits
                ft.Container(
                    padding=15,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=8,
                    content=ft.Column([
                        ft.Text("Developed for AIEAT Internship Project", 
                                size=11, color=COLORS['text_secondary']),
                        ft.Text("© 2026 AIEAT Team", 
                                size=11, color=COLORS['text_secondary']),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),
                
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _info_row(self, label: str, value: str) -> ft.Control:
        """Create an info row with label and value."""
        return ft.Row([
            ft.Text(f"{label}:", size=12, weight=ft.FontWeight.W_500, width=120),
            ft.Text(value, size=12, color=COLORS['text_secondary']),
        ])
    
    def _tech_chip(self, text: str) -> ft.Control:
        """Create a tech stack chip."""
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            bgcolor=COLORS['accent'],
            border_radius=12,
            content=ft.Text(text, size=11, color=ft.Colors.WHITE)
        )
