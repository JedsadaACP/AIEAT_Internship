"""
AIEAT News Dashboard - Main Application
Flet UI Entry Point
"""
import flet as ft
import sys
import os

from app.ui.theme import COLORS, APP_CONFIG
from app.ui.components.sidebar import create_sidebar
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.detail import DetailPage
from app.ui.pages.config import ConfigPage
from app.ui.pages.style import StylePage
from app.ui.pages.about import AboutPage
from app.services.backend_api import BackendAPI


class AIEATApp:
    """Main application controller."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.api = BackendAPI()
        self.current_route = 'dashboard'
        self.current_article = None
        self.page_cache = {}  # Cache for heavy pages
        
        # Page setup
        self.page.title = APP_CONFIG['title']
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.bgcolor = COLORS['background']
        self.page.window.width = 1200
        self.page.window.height = 800
        
        # Preload AI model in background (non-blocking)
        import threading
        threading.Thread(target=self.api.preload_model, daemon=True).start()
        
        # Build UI
        self._build_layout()
        self.page.update()  # CRITICAL: Register all controls with frontend
    
    def _build_layout(self):
        """Build the main layout with sidebar and content area."""
        self.content_area = ft.Container(
            expand=True,
            padding=20,
            content=self._get_page_content()
        )
        
        self.page.add(
            ft.Row(
                controls=[
                    create_sidebar(self.page, self.current_route, self._navigate),
                    self.content_area
                ],
                expand=True,
                spacing=0
            )
        )
    
    def _navigate(self, route: str):
        """Navigate to a different page."""
        self.current_route = route
        self.current_article = None
        self._refresh_content()
    
    def _view_article(self, article: dict):
        """View article detail."""
        self.current_article = article
        self._refresh_content()
    
    def _back_to_dashboard(self):
        """Go back to dashboard from detail view."""
        self.current_article = None
        self._refresh_content()
    
    def _refresh_content(self):
        """Refresh the content area."""
        self.content_area.content = self._get_page_content()
        
        # Rebuild sidebar to update selection
        self.page.controls[0].controls[0] = create_sidebar(
            self.page, self.current_route, self._navigate
        )
        self.page.update()
    
    def _get_page_content(self) -> ft.Control:
        """Get the content for current route."""
        # If viewing article detail
        if self.current_article:
            return DetailPage(
                self.page,
                self.api,
                self.current_article,
                self._back_to_dashboard
            ).build()
        
        if self.current_route == 'dashboard':
            # Check if we have a cached instance
            if 'dashboard_logic' in self.page_cache:
                # REFRESH: It's a revisit, so update the state
                logic = self.page_cache['dashboard_logic']
                # Safe wrapper in case of weird state
                try:
                    logic.refresh_state() 
                except:
                    pass
                return self.page_cache['dashboard_view']
            else:
                # NEW: First load, build fresh (state is already fresh)
                logic = DashboardPage(self.page, self.api, self._view_article)
                view = logic.build()
                self.page_cache['dashboard_logic'] = logic
                self.page_cache['dashboard_view'] = view
                return view
            
        elif self.current_route == 'config':
            # Always rebuild ConfigPage for fresh state
            if 'config_logic' in self.page_cache:
                del self.page_cache['config_logic']
            if 'config_view' in self.page_cache:
                del self.page_cache['config_view']
                
            logic = ConfigPage(self.page, self.api)
            view = logic.build()
            self.page_cache['config_logic'] = logic
            self.page_cache['config_view'] = view
            return view
            
        elif self.current_route == 'style':
            if 'style_logic' in self.page_cache:
                logic = self.page_cache['style_logic']
                try:
                    logic.refresh_state()
                except Exception as e:
                    print(f"Style refresh error: {e}")
                return self.page_cache['style_view']
            else:
                logic = StylePage(self.page, self.api)
                view = logic.build()
                self.page_cache['style_logic'] = logic
                self.page_cache['style_view'] = view
                return view
                
        elif self.current_route == 'log':
            return ft.Container(
                padding=40,
                content=ft.Text("Logs - Coming Soon", size=24)
            )
        elif self.current_route == 'about':
            return AboutPage(self.page).build()
        else:
            return ft.Text("Page not found")
    
    def _build_about(self) -> ft.Control:
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
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )


def main(page: ft.Page):
    """Main entry point."""
    AIEATApp(page)


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
