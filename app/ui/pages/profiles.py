"""
AIEAT Profiles Page - Intelligence Profile Management
"""
import flet as ft
from app.ui.theme import COLORS
from app.services.backend_api import BackendAPI

class ProfilesPage:
    """Profiles management page."""
    
    def __init__(self, page: ft.Page, api: BackendAPI, on_switch_callback=None):
        self.page = page
        self.api = api
        self.on_switch_callback = on_switch_callback
        self.profiles = []
        self.active_profile = None
    
    def build(self) -> ft.Control:
        """Build the profiles page."""
        self.profiles = self.api.get_profiles()
        self.active_profile = self.api.get_active_profile()
        
        # Profile cards
        cards = [self._build_profile_card(p) for p in self.profiles]
        
        return ft.Container(
            padding=30,
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=32, color=COLORS['accent']),
                    ft.Text("Intelligence Profiles", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "+ New Profile",
                        icon=ft.Icons.ADD,
                        bgcolor=COLORS['accent'],
                        color=ft.Colors.WHITE,
                        on_click=lambda e: self._show_add_dialog()
                    ),
                ], spacing=10),
                ft.Text("Select a profile to change your news focus. Each profile has its own keywords, domains, and style.",
                        size=12, color=COLORS['text_secondary']),
                ft.Divider(height=20),
                
                # Profile cards grid
                ft.Column(controls=cards, spacing=15, scroll=ft.ScrollMode.AUTO),
            ])
        )
    
    def _build_profile_card(self, profile: dict) -> ft.Control:
        """Build a single profile card."""
        is_active = profile.get('is_active', 0) == 1
        is_system = profile.get('is_system', 0) == 1
        pid = profile['profile_id']
        
        # Badge
        badges = []
        if is_system:
            badges.append(ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                bgcolor=ft.Colors.BLUE_100,
                border_radius=10,
                content=ft.Text("System", size=10, color=ft.Colors.BLUE_800)
            ))
        if is_active:
            badges.append(ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                bgcolor=ft.Colors.GREEN_100,
                border_radius=10,
                content=ft.Text("Active", size=10, color=ft.Colors.GREEN_800, weight=ft.FontWeight.BOLD)
            ))
        
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=10,
            border=ft.border.all(2, COLORS['success'] if is_active else ft.Colors.GREY_300),
            on_click=lambda e, p=pid: self._select_profile(p),
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Text(profile.get('profile_name', f"Profile {pid}"), size=16, weight=ft.FontWeight.BOLD),
                        *badges,
                    ], spacing=8),
                    ft.Text(profile.get('description', ''), size=12, color=COLORS['text_secondary']),
                    ft.TextField(
                        label="Organization Name", 
                        value=profile.get('org_name', ''), 
                        height=40, 
                        text_size=13,
                        on_submit=lambda e, pid=profile['profile_id']: self.api.update_profile_org(pid, e.control.value)
                    ),
                ], expand=True, spacing=5),
                
                # Action buttons
                ft.Row([
                    ft.IconButton(
                        ft.Icons.EDIT, icon_size=18, tooltip="Rename",
                        icon_color=COLORS['accent'],
                        on_click=lambda e, p=profile: self._show_rename_dialog(p),
                        disabled=is_system,
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE, icon_size=18, tooltip="Delete",
                        icon_color=COLORS['error'],
                        on_click=lambda e, p=pid: self._delete_profile(p),
                        disabled=is_system,
                    ),
                ], spacing=0),
            ])
        )
    
    def _select_profile(self, profile_id: int):
        """Select and switch to a profile."""
        result = self.api.switch_profile(profile_id)
        if result.get('success'):
            self._show_snackbar(f"✓ Switched to: {result['profile_name']}", COLORS['success'])
            if self.on_switch_callback:
                self.on_switch_callback()
            else:
                self._refresh()
        else:
            self._show_snackbar(f"Error: {result.get('error')}", COLORS['error'])
    
    def _show_add_dialog(self):
        """Show dialog to add new profile."""
        name_field = ft.TextField(label="Profile Name", autofocus=True)
        desc_field = ft.TextField(label="Description")
        
        def close(e):
            dialog.open = False
            self.page.update()
        
        def save(e):
            name = name_field.value.strip() if name_field.value else ""
            if not name:
                return
            result = self.api.add_profile(name, desc_field.value or "")
            dialog.open = False
            self.page.update()
            if result.get('success'):
                self._show_snackbar(f"✓ Created: {name}", COLORS['success'])
                self._refresh()
            else:
                self._show_snackbar(f"Error: {result.get('error')}", COLORS['error'])
        
        dialog = ft.AlertDialog(
            title=ft.Text("New Profile"),
            content=ft.Column([name_field, desc_field], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=close),
                ft.ElevatedButton("Create", on_click=save, bgcolor=COLORS['accent'], color=ft.Colors.WHITE),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _show_rename_dialog(self, profile: dict):
        """Show dialog to rename a profile."""
        name_field = ft.TextField(label="New Name", value=profile['profile_name'], autofocus=True)
        
        def close(e):
            dialog.open = False
            self.page.update()
        
        def save(e):
            new_name = name_field.value.strip() if name_field.value else ""
            if not new_name:
                return
            result = self.api.rename_profile(profile['profile_id'], new_name)
            dialog.open = False
            self.page.update()
            if result.get('success'):
                self._show_snackbar(f"✓ Renamed to: {new_name}", COLORS['success'])
                self._refresh()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Rename Profile"),
            content=name_field,
            actions=[
                ft.TextButton("Cancel", on_click=close),
                ft.ElevatedButton("Save", on_click=save, bgcolor=COLORS['accent'], color=ft.Colors.WHITE),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _delete_profile(self, profile_id: int):
        """Delete a profile with confirmation."""
        def close(e):
            dialog.open = False
            self.page.update()
        
        def confirm(e):
            result = self.api.delete_profile(profile_id)
            dialog.open = False
            self.page.update()
            if result.get('success'):
                self._show_snackbar("✓ Profile deleted", COLORS['success'])
                self._refresh()
            else:
                self._show_snackbar(f"Error: {result.get('error')}", COLORS['error'])
        
        dialog = ft.AlertDialog(
            title=ft.Text("Delete Profile?"),
            content=ft.Text("This will permanently delete this profile and all its keywords/domains."),
            actions=[
                ft.TextButton("Cancel", on_click=close),
                ft.ElevatedButton("Delete", on_click=confirm, bgcolor=COLORS['error'], color=ft.Colors.WHITE),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _refresh(self):
        """Refresh the page content."""
        self.page.controls[0].controls[1].content = self.build()
        self.page.update()
    
    def _show_snackbar(self, message: str, color: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()