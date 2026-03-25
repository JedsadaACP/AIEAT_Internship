"""
AIEAT News Dashboard - Sidebar Component
"""
import flet as ft
from app.ui.theme import COLORS, NAV_ITEMS, APP_CONFIG


def create_sidebar(page: ft.Page, current_route: str, on_navigate, api=None):
    """Create the sidebar navigation component."""
    
    nav_items = []
    for item in NAV_ITEMS:
        is_selected = item['route'] == current_route
        nav_items.append(
            ft.Container(
                padding=ft.padding.symmetric(horizontal=15, vertical=12),
                bgcolor=COLORS['sidebar_selected'] if is_selected else None,
                border_radius=ft.border_radius.only(top_right=25, bottom_right=25) if is_selected else None,
                on_click=lambda e, r=item['route']: on_navigate(r),
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            getattr(ft.Icons, item['icon']),
                            color=ft.Colors.WHITE,
                            size=18
                        ),
                        ft.Text(
                            item['label'],
                            color=ft.Colors.WHITE,
                            size=13,
                            weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL
                        )
                    ],
                    spacing=10
                )
            )
        )
    
    return ft.Container(
        width=APP_CONFIG['sidebar_width'],
        bgcolor=COLORS['sidebar_bg'],
        padding=0,
        content=ft.Column(
            controls=[
                # Logo/Title
                ft.Container(
                    padding=ft.padding.only(left=15, top=20, bottom=20),
                    content=ft.Text(
                        APP_CONFIG['title'],
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    )
                ),
                ft.Divider(height=1, color=ft.Colors.WHITE24),
                
                # Navigation items
                ft.Column(controls=nav_items, spacing=2),
                
                # Spacer
                ft.Container(expand=True),
                
                # Version
                ft.Container(
                    padding=ft.padding.only(left=15, bottom=10),
                    content=ft.Text(
                        APP_CONFIG['version'],
                        size=10,
                        color=ft.Colors.WHITE54
                    )
                )
            ],
            spacing=0
        )
    )
