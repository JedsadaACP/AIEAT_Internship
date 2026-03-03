"""
AIEAT Style Page - Style presets for translation output.

Allows users to configure translation style settings including:
- Output type (Facebook/Article/Summary)
- Tone (Conversational/Professional/Technical)
- Length settings for each section
- Section toggles (what to include in output)
"""
import flet as ft
from app.ui.theme import COLORS
from app.services.backend_api import BackendAPI


class StylePage:
    """Style Settings page component."""
    
    def __init__(self, page: ft.Page, api: BackendAPI):
        self.page = page
        self.api = api
        self.styles = []
        self.selected_style = None
        self.selected_style_id = None
        

        
        # --- UI Containers ---
        self.style_list_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        self.form_card = None  # Will be created in build
        
        # --- Form Controls (Created ONCE) ---
        self.name_field = ft.TextField(label="Style Name", width=300, border_radius=8, text_size=14)
        
        self.output_type_dropdown = ft.Dropdown(
            label="Prompt Template", width=220, border_radius=8,
            options=[
                ft.dropdown.Option("facebook", "Social Media"),
                ft.dropdown.Option("article", "News Article"),
                ft.dropdown.Option("summary", "Briefing"),
            ]
        )
        
        self.tone_dropdown = ft.Dropdown(
            label="Tone", width=220, border_radius=8,
            options=[
                ft.dropdown.Option("conversational", "Conversational"),
                ft.dropdown.Option("professional", "Professional"),
                ft.dropdown.Option("technical", "Technical"),
            ]
        )
        
        # Lengths
        opts = [
            ft.dropdown.Option("short", "Short"),
            ft.dropdown.Option("medium", "Medium"),
            ft.dropdown.Option("long", "Long"),
        ]
        self.headline_length = ft.Dropdown(label="Headline", width=130, border_radius=8, options=[o for o in opts], text_size=13)
        self.lead_length = ft.Dropdown(label="Lead", width=130, border_radius=8, options=[o for o in opts], text_size=13)
        self.body_length = ft.Dropdown(label="Body", width=130, border_radius=8, options=[o for o in opts], text_size=13)
        self.analysis_length = ft.Dropdown(label="Analysis", width=130, border_radius=8, options=[o for o in opts], text_size=13)
        
        # Toggles
        self.include_keywords = ft.Checkbox(label="Keywords")
        self.include_lead = ft.Checkbox(label="Lead Paragraph")
        self.include_analysis = ft.Checkbox(label="Analysis Section")
        self.include_source = ft.Checkbox(label="Source Citation")
        self.include_hashtags = ft.Checkbox(label="Hashtags")
        
        self.analysis_focus = ft.TextField(
            label="Custom Context / Instructions", width=500, border_radius=8, 
            multiline=True, min_lines=2, max_lines=3, text_size=13,
            hint_text="e.g. 'Translate for a 5-year old', 'Focus on economic impact'"
        )
        
        # Action Buttons
        self.btn_save = ft.ElevatedButton(
            "Save Changes", icon=ft.Icons.SAVE, 
            style=ft.ButtonStyle(bgcolor=COLORS['success'], color="#ffffff"),
            on_click=self._save_style
        )
        self.btn_active = ft.ElevatedButton(
            "Set as Active", icon=ft.Icons.CHECK_CIRCLE,
            style=ft.ButtonStyle(bgcolor=COLORS['accent'], color="#ffffff"),
            on_click=self._set_active
        )
        
    def refresh_state(self):
        """Reload styles from database."""
        self._load_styles_data()
        
        # If we have a selected style, try to update it; otherwise select active/first
        if self.selected_style_id:
            # Try to find currently selected style in new data
            updated = next((s for s in self.styles if s.get('style_id') == self.selected_style_id), None)
            if updated:
                self.selected_style = updated
            else:
                # Fallback if deleted
                self.selected_style = self.styles[0] if self.styles else None
        
        # Update UI
        if self.selected_style:
            self.selected_style_id = self.selected_style.get('style_id')
            self._update_form_values(self.selected_style)
        else:
            self.selected_style_id = None
            # Clear form or set defaults if needed
            
        self._rebuild_list_items()
        self.page.update()

    def build(self) -> ft.Control:
        """Build the static page structure."""
        self._load_styles_data()
        
        # Populate initial values
        if self.selected_style:
            self._update_form_values(self.selected_style)
            self._rebuild_list_items()
            
        # Left Panel: Style List
        left_panel = ft.Container(
            width=280,
            bgcolor=COLORS['card_bg'],
            border_radius=12,
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Text("Presets", size=16, weight=ft.FontWeight.BOLD, color=COLORS['text_primary']),
                    ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=COLORS['accent'], tooltip="New Style", on_click=self._add_style)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=self.style_list_col,
                    expand=True,
                ),
                ft.Divider(),
                ft.TextButton("Delete Selected", icon=ft.Icons.DELETE, icon_color=COLORS['error'], on_click=self._delete_style)
            ])
        )
        
        # Right Panel: Form
        self.form_card = ft.Container(
            expand=True,
            bgcolor=COLORS['card_bg'],
            border_radius=12,
            padding=25,
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Icon(ft.Icons.TUNE, color=COLORS['primary']),
                    ft.Text("Configuration", size=18, weight=ft.FontWeight.BOLD, color=COLORS['text_primary']),
                ]),
                ft.Divider(height=20),
                
                # Basic Settings
                ft.Text("Basic Info", size=14, weight=ft.FontWeight.W_600, color=COLORS['text_secondary']),
                ft.Container(height=5),
                ft.Row([self.name_field]),
                ft.Container(height=10),
                ft.Row([self.output_type_dropdown, self.tone_dropdown]),
                
                ft.Divider(height=30),
                
                # Lengths
                ft.Text("Content Length", size=14, weight=ft.FontWeight.W_600, color=COLORS['text_secondary']),
                ft.Container(height=5),
                ft.Row([self.headline_length, self.lead_length, self.body_length, self.analysis_length], spacing=10),
                
                ft.Divider(height=30),
                
                # Sections
                ft.Text("Include Sections", size=14, weight=ft.FontWeight.W_600, color=COLORS['text_secondary']),
                ft.Container(height=5),
                ft.Row([self.include_keywords, self.include_lead, self.include_analysis, self.include_source], spacing=20),
                ft.Row([self.include_hashtags]),
                
                ft.Divider(height=30),
                
                # Advanced
                ft.Text("Advanced", size=14, weight=ft.FontWeight.W_600, color=COLORS['text_secondary']),
                ft.Container(height=5),
                self.analysis_focus,
                
                ft.Container(height=30),
                
                # Footer Actions
                ft.Row([self.btn_save, self.btn_active], alignment=ft.MainAxisAlignment.END, spacing=15)
            ], scroll=ft.ScrollMode.AUTO)
        )

        return ft.Column([
            self._build_header(),
            ft.Container(height=15),
            ft.Row([left_panel, self.form_card], expand=True, spacing=15)
        ], expand=True)

    def _load_styles_data(self):
        """Load data from API."""
        try:
            self.styles = self.api.get_styles()
            if self.styles and not self.selected_style:
                active = next((s for s in self.styles if s.get('is_active')), None)
                self.selected_style = active or self.styles[0]
                self.selected_style_id = self.selected_style.get('style_id')
        except:
            self.styles = []

    def _update_form_values(self, style: dict):
        """Update form controls with values from style dict."""
        if not style: return
        
        self.name_field.value = style.get('name', '')
        self.output_type_dropdown.value = style.get('output_type', 'facebook')
        self.tone_dropdown.value = style.get('tone', 'conversational')
        
        self.headline_length.value = style.get('headline_length', 'medium')
        self.lead_length.value = style.get('lead_length', 'medium')
        self.body_length.value = style.get('body_length', 'medium')
        self.analysis_length.value = style.get('analysis_length', 'short')
        
        self.include_keywords.value = bool(style.get('include_keywords', 1))
        self.include_lead.value = bool(style.get('include_lead', 1))
        self.include_analysis.value = bool(style.get('include_analysis', 1))
        self.include_source.value = bool(style.get('include_source', 1))
        self.include_hashtags.value = bool(style.get('include_hashtags', 1))
        
        self.analysis_focus.value = style.get('custom_instructions', '')
        
        # Update button state
        is_active = style.get('is_active', False)
        if is_active:
            self.btn_active.text = "Active Style"
            self.btn_active.disabled = True
        else:
            self.btn_active.text = "Set as Active"
            self.btn_active.disabled = False

    def _rebuild_list_items(self):
        """Rebuild only the list items."""
        items = []
        for style in self.styles:
            is_sel = style.get('style_id') == self.selected_style_id
            is_active = style.get('is_active', False)
            
            # Card Item
            items.append(
                ft.Container(
                    padding=10,
                    border_radius=8,
                    bgcolor=COLORS['accent'] if is_sel else "transparent",
                    border=ft.border.all(1, COLORS['accent']) if not is_sel else None,
                    on_click=lambda e, s=style: self._handle_select(s),
                    content=ft.Row([
                        ft.Icon(ft.Icons.STAR if is_active else ft.Icons.CIRCLE_OUTLINED, 
                                size=16, 
                                color="#ffffff" if is_sel else (COLORS['success'] if is_active else COLORS['text_secondary'])),
                        ft.Column([
                            ft.Text(style.get('name', 'Unnamed'), weight=ft.FontWeight.W_600, 
                                    color="#ffffff" if is_sel else COLORS['text_primary']),
                            ft.Text(style.get('output_type', '').title(), size=10, 
                                    color="#eeeeee" if is_sel else COLORS['text_secondary'])
                        ], spacing=2)
                    ])
                )
            )
        self.style_list_col.controls = items

    def _handle_select(self, style):
        """Handle click on list item."""
        self.selected_style = style
        self.selected_style_id = style.get('style_id')
        
        # Update UI components directly
        self._update_form_values(style)
        self._rebuild_list_items()
        self.page.update()

    def _add_style(self, e):
        try:
            nid = self.api.add_style("New Custom Style")
            self._load_styles_data()
            new = next((s for s in self.styles if s.get('style_id') == nid), None)
            if new: self._handle_select(new)
            else: self.page.update()
        except Exception as ex:
            self._snack(f"Error: {ex}", COLORS['error'])

    def _delete_style(self, e):
        if not self.selected_style_id: return
        try:
            self.api.delete_style(self.selected_style_id)
            self.selected_style = None # Reset
            self._load_styles_data() # Reload
            
            if self.styles:
                self._handle_select(self.styles[0])
            else:
                self.style_list_col.controls = []
                self.page.update()
                
            self._snack("Deleted", COLORS['warning'])
        except Exception as ex:
            self._snack(f"Error: {ex}", COLORS['error'])

    def _save_style(self, e):
        if not self.selected_style_id: return
        try:
            data = {
                'name': self.name_field.value,
                'output_type': self.output_type_dropdown.value,
                'tone': self.tone_dropdown.value,
                'headline_length': self.headline_length.value,
                'lead_length': self.lead_length.value,
                'body_length': self.body_length.value,
                'analysis_length': self.analysis_length.value,
                'include_keywords': 1 if self.include_keywords.value else 0,
                'include_lead': 1 if self.include_lead.value else 0,
                'include_analysis': 1 if self.include_analysis.value else 0,
                'include_source': 1 if self.include_source.value else 0,
                'include_hashtags': 1 if self.include_hashtags.value else 0,
                'custom_instructions': self.analysis_focus.value
            }
            self.api.update_style(self.selected_style_id, **data)
            self._load_styles_data() # Reload to get updates
            # Re-select to refresh list name if changed
            updated = next((s for s in self.styles if s.get('style_id') == self.selected_style_id), None)
            if updated: self._handle_select(updated)
            self._snack("Saved!", COLORS['success'])
        except Exception as ex:
            self._snack(f"Error: {ex}", COLORS['error'])

    def _set_active(self, e):
        if not self.selected_style_id: return
        try:
            self.api.set_active_style(self.selected_style_id)
            self._load_styles_data()
            updated = next((s for s in self.styles if s.get('style_id') == self.selected_style_id), None)
            if updated: self._handle_select(updated)
            self._snack("Activated!", COLORS['success'])
        except Exception as ex:
            self._snack(f"Error: {ex}", COLORS['error'])

    def _build_header(self):
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=12,
            content=ft.Row([
                ft.Container(
                    padding=10, bgcolor=COLORS['accent'], border_radius=8,
                    content=ft.Icon(ft.Icons.PALETTE, color="#ffffff", size=24)
                ),
                ft.Column([
                    ft.Text("Style Settings", size=22, weight=ft.FontWeight.BOLD, color=COLORS['text_primary']),
                    ft.Text("Customize how AI translates and formats news", size=14, color=COLORS['text_secondary'])
                ], spacing=2)
            ], spacing=15)
        )

    def _snack(self, msg, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg, color="#ffffff"), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()
