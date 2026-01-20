"""
AIEAT Sources Dialog
Popup for managing news sources
"""
import flet as ft
from app.ui.theme import COLORS
from app.services.backend_api import BackendAPI


class SourcesDialog:
    """Sources management popup dialog."""
    
    def __init__(self, page: ft.Page, api: BackendAPI, on_close):
        self.page = page
        self.api = api
        self.on_close = on_close
        self.sources = []
        self.search_text = ""
        self.dialog = None
        
    def show(self):
        """Show the sources dialog."""
        self.sources = self.api.get_sources()
        self.dialog = self._build_dialog()
        self.dialog.open = True
        self.page.overlay.append(self.dialog)
        self.page.update()
    
    def close(self):
        """Close the dialog."""
        if self.dialog:
            self.dialog.open = False
            if self.dialog in self.page.overlay:
                self.page.overlay.remove(self.dialog)
            self.page.update()
    
    def _build_dialog(self) -> ft.AlertDialog:
        """Build the dialog."""
        return ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.SOURCE, color=COLORS['accent']),
                ft.Text("Manage Sources", weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    ft.Icons.CLOSE,
                    on_click=lambda e: self.close(),
                    icon_size=20
                )
            ]),
            content=ft.Container(
                width=600,
                height=450,
                content=ft.Column([
                    # Stats
                    ft.Row([
                        ft.Text(f"Total: {len(self.sources)} sources", size=12),
                        ft.Container(expand=True),
                        self._get_status_summary(),
                    ]),
                    ft.Container(height=10),
                    
                    # Search
                    ft.TextField(
                        hint_text="Search sources...",
                        prefix_icon=ft.Icons.SEARCH,
                        height=40,
                        border_radius=5,
                        on_change=self._on_search,
                    ),
                    ft.Container(height=10),
                    
                    # Sources list
                    ft.Container(
                        expand=True,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        padding=5,
                        content=ft.Column(
                            controls=self._build_source_items(),
                            scroll=ft.ScrollMode.AUTO,
                            spacing=2,
                        )
                    ),
                    ft.Container(height=10),
                    
                    # Actions
                    ft.Row([
                        ft.ElevatedButton(
                            "Import CSV",
                            icon=ft.Icons.UPLOAD,
                            style=ft.ButtonStyle(
                                bgcolor=COLORS['accent'],
                                color=ft.Colors.WHITE,
                            ),
                            on_click=self._import_csv,
                        ),
                        ft.OutlinedButton(
                            "Remove Duplicates",
                            on_click=self._remove_duplicates,
                        ),
                        ft.Container(expand=True),
                        ft.OutlinedButton(
                            "Add Source",
                            icon=ft.Icons.ADD,
                            on_click=self._add_source,
                        ),
                    ]),
                ])
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.close()),
            ],
        )
    
    def _build_source_items(self) -> list:
        """Build source list items with search filter."""
        items = []
        filtered = self.sources
        
        if self.search_text:
            filtered = [s for s in self.sources 
                       if self.search_text.lower() in s.get('domain_name', '').lower()]
        
        for source in filtered[:50]:  # Limit to 50 for performance
            status = source.get('status_id', 6)
            is_online = status == 6
            
            items.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    border_radius=5,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Row([
                        ft.Checkbox(value=True),
                        ft.Text(
                            source.get('domain_name', 'Unknown'),
                            size=12,
                            expand=True,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            bgcolor=COLORS['success'] if is_online else COLORS['error'],
                            border_radius=10,
                            content=ft.Text(
                                "Online" if is_online else "Offline",
                                size=10,
                                color=ft.Colors.WHITE
                            )
                        ),
                        ft.IconButton(
                            ft.Icons.REFRESH,
                            icon_size=16,
                            tooltip="Check Status",
                            on_click=lambda e, s=source: self._check_source(s)
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            icon_size=16,
                            tooltip="Remove",
                            icon_color=COLORS['error'],
                            on_click=lambda e, s=source: self._remove_source(s)
                        ),
                    ])
                )
            )
        
        if not items:
            items.append(
                ft.Container(
                    padding=20,
                    content=ft.Text("No sources found", color=COLORS['text_secondary'])
                )
            )
        
        return items
    
    def _get_status_summary(self) -> ft.Control:
        """Get status summary badges."""
        online = sum(1 for s in self.sources if s.get('status_id') == 6)
        offline = len(self.sources) - online
        
        return ft.Row([
            ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                bgcolor=COLORS['success'],
                border_radius=10,
                content=ft.Text(f"{online} Online", size=10, color=ft.Colors.WHITE)
            ),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                bgcolor=COLORS['error'],
                border_radius=10,
                content=ft.Text(f"{offline} Offline", size=10, color=ft.Colors.WHITE)
            ),
        ], spacing=5)
    
    def _on_search(self, e):
        """Handle search input."""
        self.search_text = e.control.value
        # Rebuild dialog content
        if self.dialog and self.dialog.content:
            list_container = self.dialog.content.content.controls[4].content
            list_container.controls = self._build_source_items()
            self.page.update()
    
    def _import_csv(self, e):
        """Handle import CSV."""
        # TODO: Implement file picker and import
        print("Import CSV clicked")
    
    def _remove_duplicates(self, e):
        """Handle remove duplicates."""
        # TODO: Implement duplicate removal
        print("Remove duplicates clicked")
    
    def _add_source(self, e):
        """Handle add source."""
        # TODO: Show add source dialog
        print("Add source clicked")
    
    def _check_source(self, source: dict):
        """Check source status."""
        print(f"Check source: {source.get('domain_name')}")
    
    def _remove_source(self, source: dict):
        """Remove a source."""
        print(f"Remove source: {source.get('domain_name')}")
