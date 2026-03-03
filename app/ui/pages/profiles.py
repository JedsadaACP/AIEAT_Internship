"""
AIEAT Profiles Page - Profile selection and management.
"""
import flet as ft
from app.ui.theme import COLORS
from app.services.backend_api import BackendAPI


class ProfilesPage:
    """Profiles page component for profile selection and management."""
    
    def __init__(self, page: ft.Page, api: BackendAPI, on_switch_callback=None):
        self.page = page
        self.api = api
        self.on_switch_callback = on_switch_callback
        self.profiles = []
        self.profile_cards = []
        
    def build(self) -> ft.Control:
        """Build the profiles page."""
        self.profiles = self.api.get_profiles()
        active = self.api.get_active_profile()
        active_id = active['profile_id'] if active else 1
        
        # Build profile cards
        self.profile_cards = []
        for p in self.profiles:
            card = self._create_profile_card(p, p['profile_id'] == active_id)
            self.profile_cards.append(card)
        
        # Header
        header = ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=32, color=COLORS['accent']),
                ft.Text("Choose Your Intelligence Profile", size=22, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "+ New Profile",
                    icon=ft.Icons.ADD,
                    style=ft.ButtonStyle(
                        bgcolor=COLORS['success'],
                        color=ft.Colors.WHITE,
                    ),
                    on_click=lambda e: self._show_add_dialog(),
                ),
            ], spacing=10)
        )
        
        # Profile grid
        grid = ft.Container(
            padding=ft.padding.only(top=20),
            content=ft.Row(
                controls=self.profile_cards,
                wrap=True,
                spacing=15,
                run_spacing=15,
            )
        )
        
        return ft.Container(
            padding=10,
            content=ft.Column([
                header,
                grid,
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    
    def _create_profile_card(self, profile: dict, is_active: bool) -> ft.Control:
        """Create a profile card with actions."""
        is_system = profile.get('is_system', 0) == 1
        
        # Active indicator
        border_color = COLORS['success'] if is_active else ft.Colors.TRANSPARENT
        border_width = 3 if is_active else 0
        
        # Active badge
        active_badge = ft.Container(
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            bgcolor=COLORS['success'],
            border_radius=10,
            content=ft.Text("Active", size=10, color=ft.Colors.WHITE),
            visible=is_active,
        )
        
        # System badge
        system_badge = ft.Container(
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            bgcolor=COLORS['accent'],
            border_radius=10,
            content=ft.Text("System", size=10, color=ft.Colors.WHITE),
            visible=is_system,
        )
        
        # Actions
        actions = []
        
        # Select button
        if not is_active:
            actions.append(
                ft.ElevatedButton(
                    "Select",
                    style=ft.ButtonStyle(
                        bgcolor=COLORS['accent'],
                        color=ft.Colors.WHITE,
                    ),
                    on_click=lambda e, pid=profile['profile_id']: self._select_profile(pid),
                )
            )
        else:
            actions.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    bgcolor=COLORS['success'],
                    border_radius=5,
                    content=ft.Text("✓ Active", size=12, color=ft.Colors.WHITE),
                )
            )
        
        # Edit button
        actions.append(
            ft.IconButton(
                icon=ft.Icons.EDIT,
                icon_color=COLORS['accent'],
                tooltip="Rename",
                on_click=lambda e, p=profile: self._show_rename_dialog(p),
            )
        )
        
        # Delete button (disabled for system profiles)
        actions.append(
            ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED_400 if not is_system else ft.Colors.GREY_400,
                tooltip="Delete" if not is_system else "Cannot delete system profile",
                disabled=is_system,
                on_click=None if is_system else lambda e, p=profile: self._show_delete_dialog(p),
            )
        )
        
        # Description
        description = profile.get('description', '') or 'No description'
        
        card = ft.Container(
            width=300,
            padding=15,
            bgcolor=COLORS['card_bg'],
            border_radius=10,
            border=ft.border.all(border_width, border_color),
            content=ft.Column([
                # Header with badges
                ft.Row([
                    ft.Text(profile['profile_name'], size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    active_badge,
                    system_badge,
                ]),
                ft.Container(height=5),
                # Description
                ft.Text(description, size=12, color=COLORS['text_secondary']),
                ft.Container(height=15),
                # Actions
                ft.Row(actions, spacing=10),
            ], spacing=0)
        )
        
        return card
    
    def _select_profile(self, profile_id: int):
        """Select a profile and switch to it."""
        result = self.api.switch_profile(profile_id)
        if result.get('success'):
            # Clear page cache and refresh
            if self.on_switch_callback:
                self.on_switch_callback()
            
            # Show success snackbar
            snackbar = ft.SnackBar(
                content=ft.Text(f"✓ Switched to: {result.get('profile_name', '')}", color=ft.Colors.WHITE),
                bgcolor=COLORS['success'],
                duration=2000,
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()
    
    def _show_add_dialog(self):
        """Show dialog to add a new profile."""
        name_field = ft.TextField(label="Profile Name", hint_text="e.g., Sports News", width=300)
        desc_field = ft.TextField(label="Description", hint_text="e.g., Sports, athletes, tournaments", width=300)
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def confirm_add(e):
            name = name_field.value.strip()
            if not name:
                return
            
            result = self.api.add_profile(name, desc_field.value.strip())
            if result.get('success'):
                dialog.open = False
                self.page.update()
                # Rebuild page
                if self.on_switch_callback:
                    self.on_switch_callback()
            else:
                self._show_error(result.get('error', 'Failed to create profile'))
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New Profile"),
            content=ft.Column([
                name_field,
                desc_field,
                ft.Text("New profiles start with an empty keyword/domain list.", 
                        size=11, color=COLORS['text_secondary']),
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Create", on_click=confirm_add, 
                                style=ft.ButtonStyle(bgcolor=COLORS['success'], color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        dialog.open = True
        self.page.overlay.append(dialog)
        self.page.update()
    
    def _show_rename_dialog(self, profile: dict):
        """Show dialog to rename a profile."""
        is_system = profile.get('is_system', 0) == 1
        if is_system:
            self._show_error("Cannot rename system profiles")
            return
        
        name_field = ft.TextField(
            label="Profile Name", 
            value=profile['profile_name'], 
            width=300
        )
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def confirm_rename(e):
            name = name_field.value.strip()
            if not name:
                return
            
            result = self.api.rename_profile(profile['profile_id'], name)
            if result.get('success'):
                dialog.open = False
                self.page.update()
                # Rebuild page
                if self.on_switch_callback:
                    self.on_switch_callback()
            else:
                self._show_error(result.get('error', 'Failed to rename profile'))
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Rename Profile"),
            content=ft.Column([
                name_field,
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Rename", on_click=confirm_rename,
                                style=ft.ButtonStyle(bgcolor=COLORS['accent'], color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        dialog.open = True
        self.page.overlay.append(dialog)
        self.page.update()
    
    def _show_delete_dialog(self, profile: dict):
        """Show dialog to confirm profile deletion."""
        is_system = profile.get('is_system', 0) == 1
        if is_system:
            self._show_error("Cannot delete system profiles")
            return
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def confirm_delete(e):
            result = self.api.delete_profile(profile['profile_id'])
            if result.get('success'):
                dialog.open = False
                self.page.update()
                # Rebuild page
                if self.on_switch_callback:
                    self.on_switch_callback()
            else:
                self._show_error(result.get('error', 'Failed to delete profile'))
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Profile"),
            content=ft.Text(f"Are you sure you want to delete '{profile['profile_name']}'?\n\nThis will also delete all associated keywords and domains."),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Delete", on_click=confirm_delete,
                                style=ft.ButtonStyle(bgcolor=COLORS['error'], color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        dialog.open = True
        self.page.overlay.append(dialog)
        self.page.update()
    
    def _show_error(self, message: str):
        """Show error snackbar."""
        snackbar = ft.SnackBar(
            content=ft.Text(f"Error: {message}", color=ft.Colors.WHITE),
            bgcolor=COLORS['error'],
            duration=3000,
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()
