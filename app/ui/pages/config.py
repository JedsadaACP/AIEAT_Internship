"""
AIEAT User Config Page
Configuration for keywords, domains, sources, threshold
"""
import flet as ft
import os
from app.ui.theme import COLORS
from app.services.backend_api import BackendAPI


class ConfigPage:
    """User Configuration page component."""
    
    # Class-level cache for models (loads once)
    _cached_models = None
    
    def __init__(self, page: ft.Page, api: BackendAPI):
        self.page = page
        self.api = api
        self.config = None
        self.all_sources = []
        self.source_search = ""
        self.available_models = []
        
        # UI element references for dynamic updates
        self.domain_input = None
        self.keyword_input = None
        self.org_name_input = None  # Added reference
        self.domains_row = None
        self.keywords_row = None
        self.main_content = None
        
        # Load models (uses cache or quick sync load)
        self._load_models()
        
    def _load_models(self):
        """Load available models from Ollama (fast, uses cache)."""
        # Use cache if available (instant)
        if ConfigPage._cached_models is not None:
            self.available_models = ConfigPage._cached_models
            return
        
        # Sync load with short timeout
        self.available_models = []
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=1)
            if r.status_code == 200:
                models = r.json().get('models', [])
                self.available_models = [{'file': m.get('name'), 'name': m.get('name')} for m in models]
                ConfigPage._cached_models = self.available_models
        except:
            pass  # Will show "No models found"
    
    def build(self) -> ft.Control:
        """Build the config page."""
        # Load config from API
        self.config = self.api.get_config()
        self.all_sources = self.api.get_sources()
        
        return ft.Column(
            controls=[
                self._build_header(),
                ft.Container(height=15),
                ft.Row([
                    # Left column: Organization, Domains, Keywords
                    ft.Container(
                        expand=True,
                        content=ft.Column([
                            self._build_org_section(),
                            ft.Container(height=15),
                            self._build_automation_section(),
                            ft.Container(height=15),
                            self._build_scoring_section(),
                            ft.Container(height=15),
                            self._build_threshold_section(),
                        ])
                    ),
                    ft.Container(width=15),
                    # Right column: Sources
                    ft.Container(
                        width=400,
                        content=self._build_sources_section(),
                    ),
                ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=20),
                self._build_save_button(),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0
        )
    
    def _build_header(self) -> ft.Control:
        """Build page header."""
        return ft.Container(
            padding=15,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Row([
                ft.Icon(ft.Icons.SETTINGS, size=28, color=COLORS['accent']),
                ft.Text("User Configuration", size=22, weight=ft.FontWeight.BOLD),
            ])
        )
    
    def _build_automation_section(self) -> ft.Control:
        """Build scraper settings section (model + date range)."""
        profile = self.config.get('profile', {})
        
        # Model options
        model_options = [ft.dropdown.Option(m['file'], m['name']) for m in self.available_models]
        if not model_options:
            model_options.append(ft.dropdown.Option("none", "No models found"))
        
        # Get saved model from profile
        saved_model = profile.get('model_name')
        # Check if saved model is in available options
        available_keys = [m['file'] for m in self.available_models]
        if saved_model and saved_model in available_keys:
            selected_model = saved_model
        else:
            selected_model = model_options[0].key if model_options else None
            
        self.model_dropdown = ft.Dropdown(
            options=model_options,
            width=400,
            height=40,
            text_size=13,
            hint_text="Select AI Model",
            border_radius=5,
            value=selected_model
        )
        
        # Date range options
        current_days = profile.get('date_limit_days', 14)
        
        # Determine initial value
        if current_days in [7, 14, 28]:
            date_radio_value = str(current_days)
            custom_value = ""
        else:
            date_radio_value = "custom"
            custom_value = str(current_days)
        
        # Custom days field (initially hidden)
        self.custom_days_field = ft.TextField(
            value=custom_value,
            width=60,
            height=35,
            text_size=13,
            hint_text="1-90",
            border_radius=5,
            keyboard_type=ft.KeyboardType.NUMBER,
            visible=(date_radio_value == "custom")
        )
        
        self.custom_days_label = ft.Text("days", size=12, visible=(date_radio_value == "custom"))
        
        # Radio buttons for date selection
        self.date_radio_group = ft.RadioGroup(
            value=date_radio_value,
            content=ft.Row([
                ft.Radio(value="7", label="7 days"),
                ft.Radio(value="14", label="14 days"),
                ft.Radio(value="28", label="28 days"),
                ft.Radio(value="custom", label="Custom:"),
                self.custom_days_field,
                self.custom_days_label,
            ], spacing=15),
            on_change=self._on_date_radio_change
        )
        
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Column([
                ft.Text("Scraper Settings:", weight=ft.FontWeight.BOLD, size=13),
                ft.Container(height=10),
                ft.Text("Scrape Articles From:", size=12, weight=ft.FontWeight.W_500),
                self.date_radio_group,
                ft.Text("How far back to look for new articles (max 30 days)", size=10, color=COLORS['text_secondary']),
                ft.Container(height=15),
                ft.Text("AI Model (Ollama):", size=12, weight=ft.FontWeight.W_500),
                self.model_dropdown,
                ft.Text("Models loaded from Ollama. Run 'ollama list' to see available.", size=10, color=COLORS['text_secondary']),
            ])
        )
    
    def _on_date_radio_change(self, e):
        """Show/hide custom field based on radio selection."""
        is_custom = (e.control.value == "custom")
        self.custom_days_field.visible = is_custom
        self.custom_days_label.visible = is_custom
        if not is_custom:
            self.custom_days_field.value = ""
        self.page.update()
    
    def _build_org_section(self) -> ft.Control:
        """Build organization and domains section."""
        profile = self.config.get('profile', {})
        domains = self.config.get('domains', [])
        
        # Domain input textfield
        self.domain_input = ft.TextField(
            hint_text="Add domain",
            width=130,
            height=35,
            text_size=12,
            border_radius=5,
            on_submit=lambda e: self._add_domain(e),
        )
        
        # Build domain chips with delete handlers
        domain_chips = []
        for d in domains:
            domain_chips.append(self._create_domain_chip(d))
        
        # Domain row reference for updates
        self.domains_row = ft.Row(
            controls=[
                *domain_chips,
                self.domain_input,
                ft.IconButton(
                    ft.Icons.ADD, 
                    icon_size=18, 
                    tooltip="Add Domain", 
                    icon_color=COLORS['accent'],
                    on_click=lambda e: self._add_domain(e)
                )
            ], 
            wrap=True, 
            spacing=8
        )
        
        # Organization Name Input - assigned before returning
        self.org_name_input = ft.TextField(
            value=profile.get('org_name', 'AIEAT'),
            read_only=False,  # Now editable
            border_radius=5,
            height=45,
        )
        
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Column([
                # Organization Name
                ft.Text("Organization Name:", weight=ft.FontWeight.BOLD, size=13),
                self.org_name_input,
                ft.Container(height=15),
                
                # Domains
                ft.Text("Domains:", weight=ft.FontWeight.BOLD, size=13),
                self.domains_row,
            ])
        )
    
    def _create_domain_chip(self, domain: str) -> ft.Control:
        """Create a domain chip with working delete button."""
        return ft.Container(
            padding=ft.padding.only(left=10, right=3, top=5, bottom=5),
            bgcolor=COLORS['accent'],
            border_radius=15,
            content=ft.Row([
                ft.Text(domain, color=ft.Colors.WHITE, size=12),
                ft.IconButton(
                    ft.Icons.CLOSE,
                    icon_size=14,
                    icon_color=ft.Colors.WHITE,
                    padding=0,
                    on_click=lambda e, d=domain: self._remove_domain(d)
                )
            ], spacing=0, tight=True)
        )
    
    def _add_domain(self, e):
        """Add a new domain."""
        domain = self.domain_input.value.strip() if self.domain_input.value else ""
        if not domain:
            self._show_snackbar("Please enter a domain name", COLORS['error'])
            return
        
        try:
            self.api.add_domain(domain)
            self.domain_input.value = ""
            
            # Reload config and rebuild domains row
            self.config = self.api.get_config()
            domains = self.config.get('domains', [])
            
            # Rebuild domain chips
            domain_chips = [self._create_domain_chip(d) for d in domains]
            self.domains_row.controls = [
                *domain_chips,
                self.domain_input,
                ft.IconButton(
                    ft.Icons.ADD,
                    icon_size=18,
                    tooltip="Add Domain",
                    icon_color=COLORS['accent'],
                    on_click=lambda e: self._add_domain(e)
                )
            ]
            self.page.update()
            self._show_snackbar(f"✓ Added domain: {domain}", COLORS['success'])
        except Exception as ex:
            err_msg = str(ex)
            if "UNIQUE constraint failed" in err_msg:
                self._show_snackbar(f"Domain '{domain}' already exists", COLORS['error'])
            else:
                self._show_snackbar(f"Error: {err_msg}", COLORS['error'])
    
    def _remove_domain(self, domain: str):
        """Remove a domain."""
        try:
            # Delete from database using API
            self.api.delete_domain(domain)
            
            # Reload config and rebuild domains row
            self.config = self.api.get_config()
            domains = self.config.get('domains', [])
            
            # Rebuild domain chips
            domain_chips = [self._create_domain_chip(d) for d in domains]
            self.domains_row.controls = [
                *domain_chips,
                self.domain_input,
                ft.IconButton(
                    ft.Icons.ADD,
                    icon_size=18,
                    tooltip="Add Domain",
                    icon_color=COLORS['accent'],
                    on_click=lambda e: self._add_domain(e)
                )
            ]
            self.page.update()
            self._show_snackbar(f"✓ Removed domain: {domain}", COLORS['success'])
        except Exception as ex:
            self._show_snackbar(f"Error: {str(ex)}", COLORS['error'])
    
    def _build_scoring_section(self) -> ft.Control:
        """Build mandatory scoring and keywords section."""
        keywords = self.config.get('keywords', [])
        profile = self.config.get('profile', {})
        
        # Keyword input textfield
        self.keyword_input = ft.TextField(
            hint_text="Type keyword and press Enter",
            width=250,
            height=35,
            text_size=12,
            border_radius=5,
            on_submit=lambda e: self._add_keyword(e),
        )
        
        # Build keyword chips with delete handlers
        keyword_chips = []
        for k in keywords:
            keyword_chips.append(self._create_keyword_chip(k))
        
        # Keywords row reference
        self.keywords_row = ft.Row(controls=keyword_chips, wrap=True, spacing=8)
        
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Column([
                # Mandatory Scoring
                ft.Text("Mandatory Scoring:", weight=ft.FontWeight.BOLD, size=13),
                ft.Row([
                    ft.Switch(
                        value=profile.get('is_new_news', 1) == 1,
                        active_color=COLORS['accent'],
                    ),
                    ft.Text("New news (+1)", size=12),
                    ft.Container(width=30),
                    ft.Switch(
                        value=profile.get('is_related', 1) == 1,
                        active_color=COLORS['accent'],
                    ),
                    ft.Text("Relate (+1)", size=12),
                ], spacing=10),
                ft.Container(height=15),
                
                # Keywords
                ft.Text("Keywords:", weight=ft.FontWeight.BOLD, size=13),
                self.keywords_row,
                ft.Container(height=8),
                ft.Row([
                    self.keyword_input,
                    ft.IconButton(
                        ft.Icons.ADD, 
                        icon_size=18, 
                        tooltip="Add Keyword",
                        icon_color=COLORS['accent'],
                        on_click=lambda e: self._add_keyword(e)
                    )
                ]),
            ])
        )
    
    def _create_keyword_chip(self, keyword: str) -> ft.Control:
        """Create a keyword chip with working delete button."""
        return ft.Container(
            padding=ft.padding.only(left=10, right=3, top=5, bottom=5),
            bgcolor=COLORS['accent'],
            border_radius=15,
            content=ft.Row([
                ft.Text(keyword, color=ft.Colors.WHITE, size=12),
                ft.IconButton(
                    ft.Icons.CLOSE,
                    icon_size=14,
                    icon_color=ft.Colors.WHITE,
                    padding=0,
                    on_click=lambda e, k=keyword: self._remove_keyword(k)
                )
            ], spacing=0, tight=True)
        )
    
    def _add_keyword(self, e):
        """Add a new keyword."""
        keyword = self.keyword_input.value.strip() if self.keyword_input.value else ""
        if not keyword:
            self._show_snackbar("Please enter a keyword", COLORS['error'])
            return
        
        try:
            self.api.add_keyword(keyword)
            self.keyword_input.value = ""
            
            # Reload config and rebuild keywords row
            self.config = self.api.get_config()
            keywords = self.config.get('keywords', [])
            
            # Rebuild keyword chips
            keyword_chips = [self._create_keyword_chip(k) for k in keywords]
            self.keywords_row.controls = [
                *keyword_chips,
                self.keyword_input,
                ft.IconButton(
                    ft.Icons.ADD,
                    icon_size=18,
                    tooltip="Add Keyword",
                    icon_color=COLORS['accent'],
                    on_click=lambda e: self._add_keyword(e)
                )
            ]
            self.page.update()
            self._show_snackbar(f"✓ Added keyword: {keyword}", COLORS['success'])
        except Exception as ex:
            err_msg = str(ex)
            if "UNIQUE constraint failed" in err_msg:
                self._show_snackbar(f"Keyword '{keyword}' already exists", COLORS['error'])
            else:
                self._show_snackbar(f"Error: {err_msg}", COLORS['error'])
    
    def _remove_keyword(self, keyword: str):
        """Remove a keyword."""
        try:
            # Delete from database using API
            self.api.delete_keyword(keyword)
            
            # Reload config and rebuild keywords row
            self.config = self.api.get_config()
            keywords = self.config.get('keywords', [])
            
            # Rebuild keyword chips
            keyword_chips = [self._create_keyword_chip(k) for k in keywords]
            self.keywords_row.controls = [
                *keyword_chips,
                self.keyword_input,
                ft.IconButton(
                    ft.Icons.ADD,
                    icon_size=18,
                    tooltip="Add Keyword",
                    icon_color=COLORS['accent'],
                    on_click=lambda e: self._add_keyword(e)
                )
            ]
            self.page.update()
            self._show_snackbar(f"✓ Removed keyword: {keyword}", COLORS['success'])
        except Exception as ex:
            self._show_snackbar(f"Error: {str(ex)}", COLORS['error'])
    
    def _build_sources_section(self) -> ft.Control:
        """Build news sources section with URL input and delete buttons."""
        total = len(self.all_sources)
        
        # URL input field
        self.source_url_input = ft.TextField(
            hint_text="Enter RSS URL or website...",
            expand=True,
            height=38,
            text_size=12,
            border_radius=5,
            on_submit=lambda e: self._add_source(e),
        )
        
        # Search filter
        self.source_search_field = ft.TextField(
            hint_text=f"Filter {total} sources...",
            prefix_icon=ft.Icons.SEARCH,
            height=35,
            width=200,
            border_radius=5,
            text_size=11,
            on_change=lambda e: self._filter_sources(e),
        )
        
        # Sources list reference for updates
        self.sources_list = ft.Column(
            controls=[self._create_source_item(s) for s in self.all_sources[:50]],
            scroll=ft.ScrollMode.AUTO,
            spacing=2,
        )
        
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            expand=True,
            content=ft.Column([
                # Header with count
                ft.Row([
                    ft.Text("News Sources:", weight=ft.FontWeight.BOLD, size=13),
                    ft.Container(expand=True),
                    ft.Text(f"{total} sources", size=11, color=ft.Colors.GREY_600),
                ]),
                ft.Container(height=8),
                
                # Add source row
                ft.Row([
                    self.source_url_input,
                    ft.IconButton(
                        ft.Icons.ADD,
                        icon_size=20,
                        tooltip="Add Source",
                        icon_color=COLORS['accent'],
                        on_click=lambda e: self._add_source(e)
                    ),
                ], spacing=5),
                ft.Container(height=8),
                
                # Filter and import row
                ft.Row([
                    self.source_search_field,
                    ft.Container(expand=True),
                    ft.OutlinedButton(
                        "Import File",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda e: self._import_sources_file(e)
                    ),
                ]),
                ft.Container(height=8),
                
                # Sources list (scrollable)
                ft.Container(
                    height=220,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=5,
                    padding=5,
                    content=self.sources_list
                ),
            ], expand=True)
        )
    
    def _add_source(self, e):
        """Add a new source from URL input."""
        url = self.source_url_input.value.strip() if self.source_url_input.value else ""
        if not url:
            self._show_snackbar("Please enter a URL", COLORS['error'])
            return
        
        # Add http:// if missing
        if not url.startswith('http'):
            url = 'https://' + url
        
        try:
            self.api.add_source(url)
            self.source_url_input.value = ""
            self.all_sources = self.api.get_sources()
            self._rebuild_sources_list()
            self._show_snackbar(f"✓ Added source", COLORS['success'])
        except Exception as ex:
            err_msg = str(ex)
            if "UNIQUE" in err_msg:
                self._show_snackbar("Source already exists", COLORS['error'])
            else:
                self._show_snackbar(f"Error: {err_msg}", COLORS['error'])
    
    def _delete_source(self, source_id: int, domain: str):
        """Delete a source by ID."""
        try:
            self.api.delete_source(source_id)
            self.all_sources = self.api.get_sources()
            self._rebuild_sources_list()
            self._show_snackbar(f"✓ Removed: {domain}", COLORS['success'])
        except Exception as ex:
            self._show_snackbar(f"Error: {str(ex)}", COLORS['error'])
    
    def _filter_sources(self, e):
        """Filter sources list by search text."""
        search = e.control.value.lower() if e.control.value else ""
        if search:
            filtered = [s for s in self.all_sources if search in s.get('domain_name', '').lower()]
        else:
            filtered = self.all_sources
        self.sources_list.controls = [self._create_source_item(s) for s in filtered[:50]]
        self.page.update()
    
    def _import_sources_file(self, e):
        """Import sources from text file (one URL per line)."""
        def on_file_picked(e):
            if not e.files:
                return
            try:
                file_path = e.files[0].path
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                added = 0
                for line in lines:
                    url = line.strip()
                    if not url or url.startswith('#'):
                        continue
                    if not url.startswith('http'):
                        url = 'https://' + url
                    try:
                        self.api.add_source(url)
                        added += 1
                    except:
                        pass  # Skip duplicates
                
                self.all_sources = self.api.get_sources()
                self._rebuild_sources_list()
                self._show_snackbar(f"✓ Imported {added} sources", COLORS['success'])
            except Exception as ex:
                self._show_snackbar(f"Import error: {str(ex)}", COLORS['error'])
        
        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(allowed_extensions=['txt', 'csv'])
    
    def _rebuild_sources_list(self):
        """Rebuild sources list after add/delete."""
        self.sources_list.controls = [self._create_source_item(s) for s in self.all_sources[:50]]
        self.page.update()
    
    def _build_threshold_section(self) -> ft.Control:
        """Build threshold setting section."""
        keywords = self.config.get('keywords', [])
        max_score = len(keywords) + 2  # keywords + is_new + relate
        threshold = self.config.get('threshold', max_score // 2 + 1)
        
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Column([
                ft.Text("Translation Threshold:", weight=ft.FontWeight.BOLD, size=13),
                ft.Row([
                    ft.Text("Translate articles with score ≥", size=12),
                    ft.TextField(
                        value=str(threshold),
                        width=50,
                        height=35,
                        text_align=ft.TextAlign.CENTER,
                        border_radius=5,
                    ),
                    ft.Text(f"/ {max_score}", size=12, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Text(f"Max = {len(keywords)} keywords + 2 mandatory", 
                       size=11, color=COLORS['text_secondary']),
            ])
        )
    
    def _build_save_button(self) -> ft.Control:
        """Build save button."""
        return ft.Container(
            padding=ft.padding.only(right=20, bottom=20),
            content=ft.Row([
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "SAVE CONFIGURATION",
                    icon=ft.Icons.SAVE,
                    style=ft.ButtonStyle(
                        bgcolor=COLORS['success'],
                        color=ft.Colors.WHITE,
                        padding=ft.padding.symmetric(horizontal=25, vertical=12),
                    ),
                    on_click=self._show_save_confirmation,
                )
            ])
        )
    
    def _show_save_confirmation(self, e):
        """Show confirmation dialog before saving."""
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def confirm_save(e):
            dialog.open = False
            self.page.update()
            self._save_config()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Save"),
            content=ft.Text("Are you sure you want to save the configuration?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Save",
                    style=ft.ButtonStyle(bgcolor=COLORS['success'], color=ft.Colors.WHITE),
                    on_click=confirm_save
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        dialog.open = True
        self.page.overlay.append(dialog)
        self.page.update()
    
    def _save_config(self):
        """Save configuration to database and show notification."""
        try:
            # Calculate date limit days based on radio selection
            radio_value = self.date_radio_group.value
            if radio_value == "custom":
                custom_val = self.custom_days_field.value.strip() if self.custom_days_field.value else ""
                if custom_val:
                    try:
                        date_days = int(custom_val)
                        date_days = max(1, min(30, date_days))  # Clamp to 1-30
                    except:
                        date_days = 14
                else:
                    date_days = 14  # Default if custom but empty
            else:
                date_days = int(radio_value)
                
            # Org name
            org_name = self.org_name_input.value.strip() if self.org_name_input.value else "AIEAT"
            
            # Model name from dropdown (if selected)
            model_name = self.model_dropdown.value if hasattr(self, 'model_dropdown') and self.model_dropdown.value else None
            
            # Collect values (only save fields that exist in DB)
            updates = {
                'date_limit_days': date_days,
                'org_name': org_name,
            }
            if model_name:
                updates['model_name'] = model_name
            
            # Save via API
            self.api.update_config(updates)
            
            # Reload model immediately if model changed
            if model_name and model_name != 'none':
                loaded_model = self.api.reload_model()
                msg = f"✓ Settings saved, model: {loaded_model}" if loaded_model else "✓ Settings saved"
            else:
                msg = "✓ Settings saved"
            
            # Show success snackbar
            snackbar = ft.SnackBar(
                content=ft.Text(msg, color=ft.Colors.WHITE),
                bgcolor=COLORS['success'],
                duration=3000,
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()
            
        except Exception as e:
            # Show error snackbar
            print(f"DEBUG: Save error: {e}")
            snackbar = ft.SnackBar(
                content=ft.Text(f"Error saving: {str(e)}", color=ft.Colors.WHITE),
                bgcolor=COLORS['error'],
                duration=4000,
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()
    
    # Helper methods
    def _create_tag_chip(self, text: str) -> ft.Control:
        """Create a tag chip with delete button."""
        return ft.Container(
            padding=ft.padding.only(left=10, right=3, top=5, bottom=5),
            bgcolor=COLORS['accent'],
            border_radius=15,
            content=ft.Row([
                ft.Text(text, color=ft.Colors.WHITE, size=12),
                ft.IconButton(
                    ft.Icons.CLOSE,
                    icon_size=14,
                    icon_color=ft.Colors.WHITE,
                    padding=0,
                )
            ], spacing=0, tight=True)
        )
    
    def _create_source_item(self, source: dict) -> ft.Control:
        """Create a source list item with delete button."""
        source_id = source.get('source_id')
        domain = source.get('domain_name', 'Unknown')
        
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=5,
            bgcolor=ft.Colors.GREY_50,
            content=ft.Row([
                ft.Text(
                    domain,
                    size=11,
                    expand=True,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_size=16,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Remove source",
                    on_click=lambda e, sid=source_id, d=domain: self._delete_source(sid, d)
                ),
            ])
        )
    
    def _refresh_page(self):
        """Refresh the config page by rebuilding it."""
        # Reload config from API
        self.config = self.api.get_config()
        self.all_sources = self.api.get_sources()
        
        # Rebuild the page content
        if self.main_content:
            self.main_content.controls = [self.build()]
            self.page.update()
        else:
            self.page.update()
    
    def _show_snackbar(self, message: str, color: str):
        """Show a snackbar notification."""
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            duration=3000,
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()
