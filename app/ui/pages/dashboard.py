"""
AIEAT Dashboard Page
Main news listing with controls - FULLY WIRED TO BACKEND
"""
import flet as ft
import threading
import os
import time
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from app.ui.theme import COLORS, get_score_color, APP_CONFIG
from app.services.backend_api import BackendAPI


def _parse_date_for_sort(date_str: str) -> float:
    """Parse RFC 2822 date string for sorting. Returns Unix timestamp or 0 on error."""
    if not date_str:
        return 0
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.timestamp()
    except:
        try:
            # Try ISO format fallback
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.timestamp()
        except:
            return 0


class DashboardPage:
    """Dashboard page component with real backend integration."""
    
    def __init__(self, page: ft.Page, api: BackendAPI, on_view_article):
        self.page = page
        self.api = api
        self.on_view_article = on_view_article
        
        # State
        self.page_size = APP_CONFIG['default_page_size']
        self.current_page = 0  # For pagination
        self.total_articles = 0
        self.status = "Idle"
        self.is_running = False
        
        # Filter state
        self.filter_date_range = "all"  # all, today, week, month
        self.filter_score = "all"  # all, high, low, unscored
        self.filter_source = "all"
        self.filter_keyword = "all"
        self.selected_source_ids = set()  # Multi-select sources
        self.search_text = ""
        
        # Sort state
        self.sort_column = "date"  # date, source, score
        self.sort_ascending = False  # False = descending (newest first)
        
        # UI references
        self.start_button = None
        self.status_badge = None
        self.progress_text = None
        self.progress_bar = None
        self.progress_container = None
        self.news_table_container = None
        self.table_column = None
        self.filter_panel = None
        self.show_dropdown = None
        self.model_dropdown = None
        
        # Batch processing state
        self.batch_stop_flag = False
        self.batch_is_running = False
        self.batch_start_button = None
        self._last_refresh_time = 0  # For debouncing table refreshes
        
        # Load models from data folder
        self.available_models = self._load_available_models()
        
        # Load all keywords for tag matching
        self.all_keywords = self.api.get_keywords()
        
        # Load config settings from database
        config = self.api.get_config()
        profile = config.get('profile', {})
        self.auto_scoring = profile.get('auto_scoring_status', 0) == 1
        self.auto_translate = profile.get('auto_translate_status', 0) == 1
        
    def _load_available_models(self):
        """Load available models from Ollama."""
        models = []
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=1)
            if r.status_code == 200:
                for m in r.json().get('models', []):
                    name = m.get('name', 'unknown')
                    models.append({'file': name, 'name': name})
        except:
            pass
        if not models:
            models = [{'file': 'none', 'name': 'Ollama not running'}]
        if not models:
            models = [{'file': 'none', 'name': 'Ollama not running'}]
        return models
    
    def refresh_state(self):
        """Refresh page state from DB (called on navigation)."""
        # Reload system profile
        profile = self.api.db.get_system_profile() or {}
        
        # Helper for safe updates
        def safe_update(control, new_value):
            if hasattr(control, 'value') and control.value != new_value:
                control.value = new_value
                try:
                    if control.page:
                        control.update()
                except:
                    pass
        
        # Update model dropdown
        saved_model = profile.get('model_name')
        if saved_model and hasattr(self, 'model_dropdown'):
            safe_update(self.model_dropdown, saved_model)
            
        # Update toggles
        self.auto_scoring = profile.get('auto_scoring_status', 0) == 1
        self.auto_translate = profile.get('auto_translate_status', 0) == 1
        if hasattr(self, 'auto_score_checkbox'):
            safe_update(self.auto_score_checkbox, self.auto_scoring)
        if hasattr(self, 'auto_translate_checkbox'):
            safe_update(self.auto_translate_checkbox, self.auto_translate)
            
        # Update header stats
        if hasattr(self, 'header_articles_text') and hasattr(self, 'header_sources_text'):
            with self.api.db.get_connection() as conn:
                count = conn.execute("SELECT COUNT(*) FROM articles_meta").fetchone()[0]
            sources_len = len(self.api.get_sources())
            
            self.header_articles_text.value = f"{count} articles"
            self.header_sources_text.value = f"{sources_len} sources"
            try:
                if self.header_articles_text.page:
                    self.header_articles_text.update()
            except: pass
            try:
                if self.header_sources_text.page:
                    self.header_sources_text.update()
            except: pass
            
        # Refresh table content
        # Only refresh table if already mounted, otherwise build() will handle initial load
        try:
            if hasattr(self, 'news_table_container') and self.news_table_container.page:
                self._refresh_table()
        except:
            pass
        
    def build(self) -> ft.Control:
        """Build the dashboard page."""
        return ft.Column(
            controls=[
                self._build_header(),
                ft.Container(height=10),
                self._build_top_bar(),
                ft.Container(height=10),
                self._build_filter_panel(),
                self._build_progress_section(),
                self._build_news_table(),
                ft.Container(height=10),
                self._build_bottom_controls(),
            ],
            expand=True,
            spacing=0
        )
    
    def _build_header(self) -> ft.Control:
        """Build page header with stats."""
        # Get ALL articles count (not filtered)
        with self.api.db.get_connection() as conn:
            total_articles = conn.execute("SELECT COUNT(*) FROM articles_meta").fetchone()[0]
        sources = self.api.get_sources()
        
        # Store refs for refresh
        self.header_articles_text = ft.Text(f"{total_articles} articles", color=ft.Colors.WHITE, size=12)
        self.header_sources_text = ft.Text(f"{len(sources)} sources", color=ft.Colors.WHITE, size=12)
        
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Row([
                ft.Icon(ft.Icons.DASHBOARD, size=28, color=COLORS['accent']),
                ft.Text("Dashboard", size=22, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor=COLORS['accent'],
                    border_radius=15,
                    content=self.header_articles_text
                ),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor=COLORS['success'],
                    border_radius=15,
                    content=self.header_sources_text
                ),
            ])
        )
    
    def _build_top_bar(self) -> ft.Control:
        """Build top bar with search, filter, export, status."""
        self.status_badge = ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            bgcolor=COLORS['success'] if self.status == "Idle" else COLORS['warning'],
            border_radius=10,
            content=ft.Text(self.status, color=ft.Colors.WHITE, size=11)
        )
        
        self.search_field = ft.TextField(
            hint_text="Search articles...",
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            height=40,
            border_radius=5,
            text_size=13,
            on_submit=self._on_search,
        )
        
        return ft.Container(
            padding=15,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Row(
                controls=[
                    self.search_field,
                    ft.ElevatedButton(
                        "Batch Score",
                        icon=ft.Icons.AUTO_MODE,
                        style=ft.ButtonStyle(bgcolor=COLORS['primary'], color=ft.Colors.WHITE),
                        on_click=lambda e: self._open_batch_dialog("score")
                    ),
                    ft.ElevatedButton(
                        "Batch Translate",
                        icon=ft.Icons.TRANSLATE,
                        style=ft.ButtonStyle(bgcolor=COLORS['accent'], color=ft.Colors.WHITE),
                        on_click=lambda e: self._open_batch_dialog("translate")
                    ),
                    ft.Container(width=10),
                    ft.ElevatedButton(
                        "Filter",
                        icon=ft.Icons.FILTER_LIST,
                        style=ft.ButtonStyle(bgcolor=COLORS['accent'], color=ft.Colors.WHITE),
                        on_click=self._toggle_filter_panel
                    ),
                    ft.ElevatedButton(
                        "Export CSV",
                        icon=ft.Icons.DOWNLOAD,
                        style=ft.ButtonStyle(bgcolor=COLORS['accent'], color=ft.Colors.WHITE),
                        on_click=self._export_csv
                    ),
                    ft.IconButton(
                        ft.Icons.REFRESH,
                        tooltip="Refresh articles",
                        on_click=lambda e: self._refresh_table(),
                        icon_color=COLORS['accent'],
                    ),
                    ft.Container(expand=True),
                    ft.Row([
                        ft.Text("Status:", color=COLORS['text_secondary'], size=12),
                        self.status_badge
                    ])
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
    
    def _build_filter_panel(self) -> ft.Control:
        """Build collapsible filter panel."""
        sources = self.api.get_sources()
        keywords = self.api.get_keywords()
        
        # source_options removed - using dialog now
        
        keyword_options = [ft.dropdown.Option("all", "All Keywords")]
        for k in keywords:
            keyword_options.append(ft.dropdown.Option(k, k))
        
        self.filter_panel = ft.Container(
            visible=False,
            padding=15,
            bgcolor=ft.Colors.GREY_100,
            border_radius=8,
            margin=ft.margin.only(bottom=10),
            content=ft.Column([
                ft.Row([
                    ft.Text("Filter Articles", weight=ft.FontWeight.BOLD, size=14),
                    ft.Container(expand=True),
                    ft.IconButton(ft.Icons.CLOSE, on_click=self._toggle_filter_panel, icon_size=18)
                ]),
                ft.Divider(height=1),
                ft.Row([
                    # Date Range
                    ft.Column([
                        ft.Text("Date Range", weight=ft.FontWeight.W_500, color=COLORS['accent'], size=12),
                        ft.RadioGroup(
                            value=self.filter_date_range,
                            content=ft.Column([
                                ft.Radio(value="today", label="Today / Yesterday"),
                                ft.Radio(value="week", label="This Week (7 days)"),
                                ft.Radio(value="month", label="This Month"),
                                ft.Radio(value="all", label="All Time"),
                            ], spacing=3),
                            on_change=self._on_date_filter_change
                        )
                    ], spacing=5),
                    ft.Container(width=40),
                    # Score
                    ft.Column([
                        ft.Text("Score", weight=ft.FontWeight.W_500, color=COLORS['accent'], size=12),
                        ft.RadioGroup(
                            value=self.filter_score,
                            content=ft.Column([
                                ft.Radio(value="all", label="Show All"),
                                ft.Radio(value="high", label="High Relevance (5+)"),
                                ft.Radio(value="low", label="Low Relevance (<5)"),
                                ft.Radio(value="unscored", label="Unscored (New)"),
                            ], spacing=3),
                            on_change=self._on_score_filter_change
                        )
                    ], spacing=5),
                    ft.Container(width=40),
                    # Source & Keyword
                    ft.Column([
                        ft.Text("Source:", size=12, weight=ft.FontWeight.W_500),
                        ft.ElevatedButton(
                            "Select Sources (All)",
                            icon=ft.Icons.LIST,
                            on_click=self._open_source_filter_dialog,
                            ref=(btn_ref := ft.Ref[ft.ElevatedButton]())
                        ),
                        # self._create_source_dropdown(source_options),
                        ft.Container(height=8),
                        ft.Text("Keyword:", size=12, weight=ft.FontWeight.W_500),
                        self._create_keyword_dropdown(keyword_options),
                    ], spacing=5),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=10),
                ft.Row([
                    ft.TextButton("Reset Filters", on_click=self._reset_filters),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Apply Filters",
                        style=ft.ButtonStyle(bgcolor=COLORS['accent'], color=ft.Colors.WHITE),
                        on_click=self._apply_filters
                    )
                ])
            ])
        )

        return self.filter_panel
    
    def _build_toolbar_actions(self):
        """Build action buttons for the toolbar."""
        return ft.Row([
            ft.OutlinedButton(
                "Filter",
                icon=ft.Icons.FILTER_LIST,
                on_click=self._toggle_filter_panel,
                style=ft.ButtonStyle(padding=15)
            ),
            ft.OutlinedButton(
                "Export CSV",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._export_csv,
                style=ft.ButtonStyle(padding=15)
            ),
            ft.Container(width=10), # Spacer
            ft.ElevatedButton(
                "Batch Score",
                icon=ft.Icons.AUTO_MODE,
                bgcolor=COLORS['primary'],
                color=ft.Colors.WHITE,
                on_click=lambda e: self._open_batch_dialog("score")
            ),
            ft.ElevatedButton(
                "Batch Translate",
                icon=ft.Icons.TRANSLATE,
                bgcolor=COLORS['accent'],
                color=ft.Colors.WHITE,
                on_click=lambda e: self._open_batch_dialog("translate")
            ),
        ])

    def _open_source_filter_dialog(self, e):
        """Open a multi-select dialog for sources."""
        # Store button reference if not already stored (happens on first build)
        if not hasattr(self, 'source_selector_btn'):
            self.source_selector_btn = e.control
            
        sources = self.api.get_sources()
        # Sort alphabetically
        sources.sort(key=lambda x: x.get('domain_name', '').lower())
        
        search_field = ft.TextField(
            hint_text="Search sources...", 
            autofocus=True,
            prefix_icon=ft.Icons.SEARCH,
            height=40,
            text_size=12
        )
        source_list = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, height=300)
        
        # Temporary set for the dialog (so we can Cancel without affecting main state)
        temp_selected = self.selected_source_ids.copy()
        
        def on_checkbox_change(e, source_id):
            if e.control.value:
                temp_selected.add(source_id)
            else:
                temp_selected.discard(source_id)
                
        def update_list(search_term="", initial=False):
            items = []
            for s in sources:
                name = s.get('domain_name', '')
                if search_term.lower() in name.lower():
                    s_id = str(s.get('source_id'))
                    is_checked = s_id in temp_selected
                    items.append(
                        ft.Container(
                            content=ft.Checkbox(
                                label=name, 
                                value=is_checked,
                                on_change=lambda e, sid=s_id: on_checkbox_change(e, sid)
                            ),
                            padding=ft.padding.only(left=10)
                        )
                    )
            source_list.controls = items
            if not initial:
                source_list.update()
            
        search_field.on_change = lambda e: update_list(e.control.value)
        
        # Initial list populate (no update() call)
        update_list(initial=True)
        
        def close(e):
            dialog.open = False
            self.page.update()
            
        def apply(e):
            self.selected_source_ids = temp_selected.copy()
            # Update button text
            count = len(self.selected_source_ids)
            self.source_selector_btn.text = f"Sources: {count} Selected" if count > 0 else "Select Sources (All)"
            self.source_selector_btn.update()
            dialog.open = False
            self.page.update()
            
        def select_all(e):
            for s in sources:
                temp_selected.add(str(s.get('source_id')))
            update_list(search_field.value)
            
        def clear_all(e):
            temp_selected.clear()
            update_list(search_field.value)

        dialog = ft.AlertDialog(
            title=ft.Text("Select Sources", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=400,
                height=400, # Fixed height for scrollable content
                content=ft.Column([
                    search_field,
                    ft.Divider(height=1),
                    ft.Row([
                        ft.TextButton("Select All", on_click=select_all, height=30, style=ft.ButtonStyle(padding=5)),
                        ft.TextButton("Clear", on_click=clear_all, height=30, style=ft.ButtonStyle(padding=5)),
                    ]),
                    ft.Divider(height=1),
                    ft.Container(content=source_list, expand=True) # Scrollable list
                ])
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close),
                ft.ElevatedButton("Apply Selection", on_click=apply, bgcolor=COLORS['accent'], color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _create_source_dropdown(self, options):
        """(Deprecated) Create source dropdown and store reference."""
        # Kept only if needed to prevent errors if called elsewhere, but logic moved to dialog.
        return ft.Container()
    
    def _create_keyword_dropdown(self, options):
        """Create keyword dropdown and store reference."""
        self.keyword_dropdown = ft.Dropdown(
            value="all",
            options=options,
            width=180,
            height=35,
            text_size=11,
        )
        return self.keyword_dropdown
    
    def _open_batch_dialog(self, action: str):
        """Open the batch processing dialog."""
        self.batch_action = action
        title = "Batch Scoring" if action == "score" else "Batch Translation"
        action_text = "unscored" if action == "score" else "untranslated"
        
        # Keyword options (reuse existing if possible or fetch new)
        keywords = self.api.get_keywords()
        kw_opts = [ft.dropdown.Option("all", "All Keywords")] + [ft.dropdown.Option(k, k) for k in keywords]
        
        self.batch_date_dd = ft.Dropdown(
            label="Date Range",
            value="week",
            options=[
                ft.dropdown.Option("today", "Today (Since Midnight)"),
                ft.dropdown.Option("week", "Last 7 Days"),
                ft.dropdown.Option("custom_14", "Last 14 Days"),
                ft.dropdown.Option("month", "Last 28 Days"),
                ft.dropdown.Option("all", "All Time"),
            ],
            width=300
        )
        
        self.batch_keyword_dd = ft.Dropdown(
            label="Keyword Filter",
            value="all",
            options=kw_opts,
            width=300
        )
        
        # Get translation threshold from config
        profile = self.api.db.get_system_profile() or {}
        max_score = len(keywords) + 2  # keywords + is_new + is_related
        # Default behavior: if threshold is missing, default to >50%
        threshold = profile.get('threshold', max_score // 2 + 1) or (max_score // 2 + 1)
        
        # Custom score input container (Always visible but disabled by default)
        self.batch_custom_score_container = ft.Container(
            content=ft.Row([
                ft.Text("Custom Score:", size=12),
                ft.TextField(
                    value="3",
                    width=60,
                    height=35,
                    text_align=ft.TextAlign.CENTER,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    ref=(custom_score_ref := ft.Ref[ft.TextField]())
                ),
            ], spacing=10)
        )
        self.batch_custom_score = custom_score_ref
        
        def on_score_change(e):
            # No UI update needed - always editable
            pass
        
        self.batch_score_dd = ft.Dropdown(
            label="Minimum Score",
            value="threshold",
            visible=(action == "translate"),
            options=[
                ft.dropdown.Option("0", "All Scored Articles"),
                ft.dropdown.Option("threshold", f"Same as Threshold (≥ {threshold})"),
                ft.dropdown.Option("custom", "Custom (Use value below)"),
            ],
            width=300,
        )
        self.batch_score_dd.on_change = on_score_change
        
        self.batch_score_dd = ft.Dropdown(
            label="Minimum Score",
            value="threshold",
            visible=(action == "translate"),
            options=[
                ft.dropdown.Option("0", "All Scored Articles"),
                ft.dropdown.Option("threshold", f"Same as Threshold (≥ {threshold})"),
                ft.dropdown.Option("custom", "Custom..."),
            ],
            width=300,
        )
        self.batch_score_dd.on_change = on_score_change
        
        # Initial state check
        # We need to defer this slightly or call after dialog open, 
        # but calling here sets initial object state correctly
        pass 
        
        # Initial check count
        self.batch_status_text = ft.Text(f"Ready to check for {action_text} articles...", size=12, color=ft.Colors.GREY)
        self.batch_progress_bar = ft.ProgressBar(width=300, visible=False, value=0)
        self.batch_progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=3, visible=False)
        
        content = ft.Column([
            ft.Text(f"Process {action_text} articles matching criteria:", size=14),
            ft.Container(height=10),
            self.batch_date_dd,
            self.batch_keyword_dd,
            self.batch_score_dd,
            # FIX: Only show custom score input if action is 'translate'
            ft.Container(
                content=self.batch_custom_score_container, 
                visible=(action == "translate")
            ),
            ft.Container(height=10),
            ft.Row([self.batch_progress_ring, self.batch_status_text], spacing=10),
            self.batch_progress_bar
        ], tight=True)
        
        # Create Start/Stop button (will toggle during processing)
        self.batch_start_button = ft.ElevatedButton(
            "Start Processing", 
            on_click=self._toggle_batch_process, 
            bgcolor=COLORS['success'], 
            color=ft.Colors.WHITE
        )
        
        self.batch_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=content,
            actions=[
                ft.TextButton("Close", on_click=self._close_batch_dialog),
                self.batch_start_button,
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Reset state
        self.batch_stop_flag = False
        self.batch_is_running = False
        
        self.page.overlay.append(self.batch_dialog)
        self.batch_dialog.open = True
        self.page.update()

    def _close_batch_dialog(self, e):
        """Close the batch dialog."""
        self.batch_dialog.open = False
        self.page.update()

    def _toggle_batch_process(self, e):
        """Toggle between Start and Stop for batch processing."""
        if self.batch_is_running:
            # Stop the process - disable button to prevent double-click
            self.batch_stop_flag = True
            self.batch_start_button.text = None
            self.batch_start_button.content = ft.Text("Stopping...", color=ft.Colors.WHITE)
            self.batch_start_button.bgcolor = COLORS['warning']
            self.batch_start_button.disabled = True
            self.batch_status_text.value = "Stopping..."
            self.batch_status_text.color = COLORS['warning']
            self.page.update()
        else:
            # Start the process async
            self.batch_stop_flag = False
            self.batch_is_running = True
            
            # Use content property for reliable update
            self.batch_start_button.content = ft.Text("STOP", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            self.batch_start_button.bgcolor = ft.Colors.RED_600
            self.batch_start_button.update()
            
            self.batch_progress_bar.visible = True
            self.batch_progress_bar.value = None
            self.batch_progress_ring.visible = True
            self.batch_status_text.value = "Starting..."
            self.batch_status_text.color = COLORS['accent']
            self.page.update()
            
            # Use run_task instead of threading
            self.page.run_task(self._process_batch_async)

    async def _process_batch_async(self):
        """Async worker for batch process using step-by-step executor."""
        import asyncio
        action = self.batch_action
        date_range = self.batch_date_dd.value
        keyword = self.batch_keyword_dd.value
        
        # Get min_score
        score_selection = self.batch_score_dd.value
        if score_selection == "0":
            min_score = 0
        elif score_selection == "threshold":
            keywords = self.api.get_keywords()
            # Dynamic calculation matching profile
            max_score = len(keywords) + 2
            profile = self.api.db.get_system_profile() or {}
            min_score = profile.get('threshold', max_score // 2 + 1) or (max_score // 2 + 1)
        elif score_selection == "custom":
            try:
                # Get value from Ref
                score_field = self.batch_custom_score.current
                min_score = int(score_field.value) if score_field and score_field.value else 3
            except:
                min_score = 3
        else:
            min_score = int(score_selection) if score_selection.isdigit() else 0
        
        try:
            # We need to get the generator from the Sync API
            # Creating the generator is fast/non-blocking
            generator = self.api.batch_process_articles(
                action, 
                date_range, 
                keyword, 
                min_score,
                stop_callback=lambda: self.batch_stop_flag
            )
            
            def safe_next(g):
                try:
                    return next(g)
                except StopIteration:
                    return None

            while True:
                # Check for stop request (Double check for UI responsiveness)
                if self.batch_stop_flag:
                    self.batch_status_text.value = f"Stopped by user."
                    self.batch_status_text.color = COLORS['warning']
                    break
                
                # Execute ONE step of the generator in a thread
                # This prevents blocking the UI loop while waiting for LLM
                try:
                    # Use safe_next to avoid StopIteration bubbling into Future
                    step_result = await asyncio.to_thread(safe_next, generator)
                    
                    if step_result is None:
                        # Generator finished
                        self.batch_status_text.value = "Processing Complete!"
                        self.batch_status_text.color = COLORS['success']
                        self.batch_progress_bar.value = 1.0
                        break

                    processed, total, status = step_result
                    
                    if total == 0:
                        self.batch_status_text.value = "No matching articles found."
                        self.batch_status_text.color = COLORS['warning']
                        break

                    # Update UI on main thread (safe here!)
                    progress_pct = processed / total
                    if total > 0:
                        self.batch_progress_bar.value = progress_pct
                    
                    self.batch_status_text.value = f"Processing ({processed}/{total}): {status[:40]}..."
                    self.page.update()
                    
                    # Refresh table frequently (every article)
                    current_time = time.time()
                    if processed % 1 == 0 and (current_time - self._last_refresh_time) > 0.1:
                        self._last_refresh_time = current_time
                        self._refresh_table()
                        
                except Exception as loop_e:
                    # Handle unexpected errors in the loop
                    print(f"Loop Error: {loop_e}")
                    raise loop_e
            
        except Exception as e:
            print(f"Batch Error: {e}")
            self.batch_status_text.value = f"Error: {str(e)}"
            self.batch_status_text.color = COLORS['error']
            
        finally:
            self.batch_progress_ring.visible = False
            self._reset_batch_button()
            self._safe_update()
            self._refresh_table()
    
    def _safe_update(self):
        """Thread-safe page update wrapper for background threads."""
        try:
            self.page.update()
        except Exception as e:
            print(f"Safe update failed (expected if page closed): {e}")
    
    def _reset_batch_button(self):
        """Reset the batch button to Start state."""
        self.batch_is_running = False
        self.batch_start_button.text = None
        self.batch_start_button.content = ft.Text("Start Processing", color=ft.Colors.WHITE)
        self.batch_start_button.bgcolor = COLORS['success']
        self.batch_start_button.disabled = False
        self.batch_start_button.update()

    def _build_progress_section(self) -> ft.Control:
        """Build progress display (hidden initially)."""
        self.progress_text = ft.Text("", size=12, color=COLORS['text_secondary'])
        self.progress_bar = ft.ProgressBar(width=400, value=0, color=COLORS['accent'])
        
        self.progress_container = ft.Container(
            padding=15,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8,
            visible=False,
            margin=ft.margin.only(bottom=10),
            content=ft.Row([
                ft.ProgressRing(width=20, height=20, stroke_width=2),
                ft.Container(width=10),
                ft.Column([
                    self.progress_text,
                    self.progress_bar,
                ], spacing=5),
            ])
        )
        return self.progress_container
    
    def _build_news_table(self) -> ft.Control:
        """Build the news data table with ALL articles."""
        articles = self._get_filtered_articles()
        
        rows = []
        for art in articles:
            raw_score = art.get('ai_score')
            score = raw_score if raw_score and raw_score > 0 else 0
            score_display = str(score) if score > 0 else "—"
            headline = art.get('headline', '')[:200] if art.get('headline') else ''
            date_str = self._format_date(art.get('published_at', ''))
            source = art.get('source_name', '')[:20] if art.get('source_name') else ''
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(date_str, size=11)),
                        ft.DataCell(ft.Text(source, size=11)),
                        ft.DataCell(
                            ft.TextButton(
                                headline + ("..." if len(art.get('headline', '')) > 60 else ""),
                                on_click=lambda e, a=art: self.on_view_article(a),
                                style=ft.ButtonStyle(color=COLORS['accent'])
                            )
                        ),
                        ft.DataCell(self._build_keyword_chips(art)),
                        ft.DataCell(
                            ft.Row([
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    bgcolor=get_score_color(score) if score > 0 else ft.Colors.GREY_400,
                                    border_radius=4,
                                    content=ft.Text(score_display, color=ft.Colors.WHITE, size=11)
                                ),
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    icon_size=14,
                                    tooltip="Edit Score",
                                    on_click=lambda e, a=art: self._edit_score(a),
                                )
                            ], spacing=2)
                        ),
                    ],
                )
            )
        
        # Sortable column headers
        date_icon = self._get_sort_icon("date")
        score_icon = self._get_sort_icon("score")
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.TextButton(
                        content=ft.Row([
                            ft.Text("Date", size=11, weight=ft.FontWeight.BOLD),
                            ft.Text(date_icon, size=10) if date_icon else ft.Container()
                        ], spacing=2),
                        on_click=lambda e: self._sort_by("date")
                    )
                ),
                ft.DataColumn(ft.Text("Source", size=11, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Headline", size=11, weight=ft.FontWeight.BOLD), expand=True),
                ft.DataColumn(ft.Text("Tags", size=11, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(
                    ft.TextButton(
                        content=ft.Row([
                            ft.Text("Score", size=11, weight=ft.FontWeight.BOLD),
                            ft.Text(score_icon, size=10) if score_icon else ft.Container()
                        ], spacing=2),
                        on_click=lambda e: self._sort_by("score")
                    )
                ),
            ],
            rows=rows,
            heading_row_color=ft.Colors.GREY_100,
            border_radius=8,
            column_spacing=15,
        )
        
        self.table_column = ft.Column([table], scroll=ft.ScrollMode.AUTO, expand=True)
        
        self.news_table_container = ft.Container(
            expand=True,
            padding=15,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=self.table_column
        )
        return self.news_table_container
    
    def _get_filtered_articles(self):
        """Get articles with current filters applied."""
        # Build SQL with filters
        with self.api.db.get_connection() as conn:
            sql = """
                SELECT m.article_id, m.headline, m.author_name, m.published_at,
                       m.article_url, m.ai_score, ms.status_name,
                       s.domain_name as source_name, s.source_id,
                       GROUP_CONCAT(t.tag_name, ',') as tags
                FROM articles_meta m
                JOIN sources s ON m.source_id = s.source_id
                JOIN master_status ms ON m.status_id = ms.status_id
                LEFT JOIN article_tag_map atm ON m.article_id = atm.article_id
                LEFT JOIN tags t ON atm.tag_id = t.tag_id
                WHERE 1=1 AND m.profile_id = ?
            """
            params = [self.api.db._get_active_profile_id()]
            
            # Date filter
            if self.filter_date_range == "today":
                sql += " AND DATE(m.published_at) >= DATE('now', '-1 day')"
            elif self.filter_date_range == "week":
                sql += " AND DATE(m.published_at) >= DATE('now', '-7 days')"
            elif self.filter_date_range == "month":
                sql += " AND DATE(m.published_at) >= DATE('now', '-30 days')"
            
            # Score filter
            if self.filter_score == "high":
                sql += " AND COALESCE(m.ai_score, 0) >= 5"
            elif self.filter_score == "low":
                sql += " AND m.ai_score > 0 AND m.ai_score < 5"
            elif self.filter_score == "unscored":
                sql += " AND (m.ai_score IS NULL OR m.ai_score = 0)"
            
            # Source filter (Multi-select)
            if self.selected_source_ids:
                # Convert to ints for safety and SQL IN clause
                ids = [int(x) for x in self.selected_source_ids]
                placeholders = ','.join('?' for _ in ids)
                sql += f" AND s.source_id IN ({placeholders})"
                params.extend(ids)
            
            # Keyword filter - filter by actual tag association
            # Note: We'll use a subquery or adjust the WHERE to check tag matches
            if self.filter_keyword != "all":
                sql += " AND m.article_id IN (SELECT atm2.article_id FROM article_tag_map atm2 JOIN tags t2 ON atm2.tag_id = t2.tag_id WHERE LOWER(t2.tag_name) = LOWER(?))"
                params.append(self.filter_keyword)
            
            # Search text
            if self.search_text:
                sql += " AND (m.headline LIKE ? OR s.domain_name LIKE ?)"
                params.extend([f"%{self.search_text}%", f"%{self.search_text}%"])
            
            # GROUP BY for tag aggregation
            sql += " GROUP BY m.article_id"
            
            # Sorting - score can be done in SQL, date needs Python parsing
            if self.sort_column == "score":
                sql += f" ORDER BY COALESCE(m.ai_score, 0) {'ASC' if self.sort_ascending else 'DESC'}"
            # Note: date sorting done in Python after fetch
            
            cursor = conn.execute(sql, params)
            articles = [dict(row) for row in cursor]
            
            # Sort by date in Python for correct chronological order
            if self.sort_column == "date" or self.sort_column is None:
                articles.sort(
                    key=lambda a: _parse_date_for_sort(a.get('published_at', '')),
                    reverse=not self.sort_ascending  # DESC = newest first
                )
            
            # Apply pagination after sorting
            offset = self.current_page * self.page_size
            return articles[offset:offset + self.page_size]
    
    def _get_sort_icon(self, column):
        """Get sort indicator icon."""
        if self.sort_column == column:
            return "▲" if self.sort_ascending else "▼"
        return ""
    
    def _sort_by(self, column):
        """Sort table by column."""
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = False  # Default descending
        self._refresh_table()
    
    def _format_date(self, date_str: str) -> str:
        """Format date to readable format - always show actual date (standardized)."""
        if not date_str:
            return "-"
        try:
            import pytz
            date_str = str(date_str)
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(date_str[:19], fmt)
                    # Convert from UTC to local timezone (Bangkok)
                    utc_tz = pytz.UTC
                    local_tz = pytz.timezone('Asia/Bangkok')
                    dt_utc = utc_tz.localize(dt)
                    dt_local = dt_utc.astimezone(local_tz)
                    # Always show date format: "Thu, 09 Jan"
                    return dt_local.strftime('%a, %d %b')
                except:
                    continue
            return date_str[:10]
        except:
            return "-"
    
    def _build_keyword_chips(self, article) -> ft.Control:
        """Build keyword chips for an article."""
        matched = []
        
        # Try DB tags first
        tags_str = article.get('tags')
        if tags_str:
            matched = [t.strip() for t in tags_str.split(',') if t.strip()]
        
        # Fallback to headline if no DB tags
        if not matched:
            headline = (article.get('headline') or '').lower()
            for kw in self.all_keywords:
                # Handle both dict and string format
                keyword_name = kw.get('tag_name', kw) if isinstance(kw, dict) else str(kw)
                if keyword_name.lower() in headline:
                    matched.append(keyword_name)
        
        # De-duplicate
        matched = list(set(matched))

        if not matched:
            return ft.Container()
            
        # Build chips for matched keywords (limit to 3)
        chips = []
        for keyword in matched[:3]:
            chips.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    bgcolor=COLORS['accent'],
                    border_radius=4,
                    content=ft.Text(keyword[:10], color=ft.Colors.WHITE, size=9)
                )
            )
        
        return ft.Row(chips, spacing=3)
    
    def _build_bottom_controls(self) -> ft.Control:
        """Build bottom controls bar with START button."""
        # Model dropdown from real data
        model_options = [ft.dropdown.Option(m['file'], m['name']) for m in self.available_models]
        
        # Page size buttons (auto-apply on click)
        def make_size_btn(size):
            return ft.TextButton(
                str(size),
                on_click=lambda e, s=size: self._set_page_size(s),
                style=ft.ButtonStyle(
                    bgcolor=COLORS['accent'] if self.page_size == size else None,
                    color=ft.Colors.WHITE if self.page_size == size else COLORS['text_primary'],
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                )
            )
        
        self.size_buttons = [make_size_btn(s) for s in [10, 20, 50, 100]]
        
        # Get saved model from profile
        profile = self.api.db.get_system_profile()
        saved_model = profile.get('model_name') if profile else None
        available_keys = [m['file'] for m in self.available_models]
        if saved_model and saved_model in available_keys:
            selected_model = saved_model
        else:
            selected_model = self.available_models[0]['file'] if self.available_models else "none"
        
        self.model_dropdown = ft.Dropdown(
            value=selected_model,
            options=model_options,
            width=180,
            height=35,
            text_size=11,
        )
        self.model_dropdown.on_change = self._on_model_change
        # Dual-bind to ensure firing on all Flet versions
        if hasattr(self.model_dropdown, 'on_select'):
            self.model_dropdown.on_select = self._on_model_change
        
        # Pagination controls
        self.page_label = ft.Text(f"Page {self.current_page + 1}", size=12)
        
        # Go to page input
        self.goto_input = ft.TextField(
            width=50,
            height=30,
            text_size=11,
            hint_text="Go",
            text_align=ft.TextAlign.CENTER,
            on_submit=self._goto_page,
        )
        
        # Auto-scoring toggle (loaded from DB)
        self.auto_score_checkbox = ft.Checkbox(
            label="Auto Scoring",
            value=self.auto_scoring,
            on_change=self._on_auto_score_change,
        )
        
        # Auto-translation toggle (loaded from DB)
        self.auto_translate_checkbox = ft.Checkbox(
            label="Auto Translation",
            value=self.auto_translate,
            on_change=self._on_auto_translate_change,
        )
        
        return ft.Container(
            padding=15,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Row(
                controls=[
                    ft.Text("Show:", size=12),
                    *self.size_buttons,
                    ft.Container(width=15),
                    # Pagination
                    ft.IconButton(
                        ft.Icons.CHEVRON_LEFT,
                        on_click=self._prev_page,
                        tooltip="Previous page",
                        icon_size=20,
                    ),
                    self.page_label,
                    ft.IconButton(
                        ft.Icons.CHEVRON_RIGHT,
                        on_click=self._next_page,
                        tooltip="Next page",
                        icon_size=20,
                    ),
                    self.goto_input,
                    ft.Container(expand=True),
                    self.auto_score_checkbox,
                    ft.Container(width=10),
                    self.auto_translate_checkbox,
                    ft.Container(width=15),
                    self.model_dropdown,
                    ft.Container(width=10),
                    self._build_start_button(),
                ],
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
    
    def _build_start_button(self) -> ft.Control:
        """Build the START/STOP button."""
        # Use content property for reliable dynamic updates (text property doesn't update)
        self.start_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE, size=18),
                ft.Text("START SCRAPER", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ], spacing=8),
            style=ft.ButtonStyle(
                bgcolor=COLORS['success'],
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
            on_click=self._on_start_click
        )
        return self.start_button
    
    # ==================== EVENT HANDLERS ====================
    
    def _set_page_size(self, size):
        """Set page size from button click (keeps current page if possible)."""
        self.page_size = size
        # Adjust current_page if it would be past the last page
        # (e.g., if on page 50 with 10/page, and switch to 100/page)
        self._refresh_table()
        self._show_snackbar(f"Showing {size} per page", COLORS['accent'])
    
    def _goto_page(self, e):
        """Go to specific page from input."""
        try:
            page_num = int(e.control.value)
            if page_num >= 1:
                self.current_page = page_num - 1
                self.page_label.value = f"Page {page_num}"
                e.control.value = ""  # Clear input
                self._refresh_table()
            else:
                self._show_snackbar("Page must be 1 or higher", COLORS['warning'])
        except ValueError:
            self._show_snackbar("Enter a valid page number", COLORS['warning'])
    
    def _on_search(self, e):
        """Handle search submit."""
        self.search_text = e.control.value
        self._refresh_table()
    
    def _toggle_filter_panel(self, e):
        """Toggle filter panel visibility."""
        self.filter_panel.visible = not self.filter_panel.visible
        self.page.update()
    
    def _on_date_filter_change(self, e):
        """Handle date filter change."""
        self.filter_date_range = e.control.value
    
    def _on_score_filter_change(self, e):
        """Handle score filter change."""
        self.filter_score = e.control.value
    
    def _on_source_filter_change(self, e):
        """Handle source filter change."""
        self.filter_source = e.control.value
    
    def _on_keyword_filter_change(self, e):
        """Handle keyword filter change."""
        self.filter_keyword = e.control.value
    
    def _on_auto_score_change(self, e):
        """Handle auto scoring toggle."""
        value = 1 if e.control.value else 0
        self.api.update_config({'auto_scoring_status': value})
        status = "enabled" if value else "disabled"
        self._show_snackbar(f"Auto Scoring {status}", COLORS['accent'])
    
    def _on_auto_translate_change(self, e):
        """Handle auto translation toggle."""
        value = 1 if e.control.value else 0
        self.api.update_config({'auto_translate_status': value})
        status = "enabled" if value else "disabled"
        self._show_snackbar(f"Auto Translation {status}", COLORS['accent'])
    
    def _on_model_change(self, e):
        """Handle model change (auto-save)."""
        new_model = e.control.value
        # print(f"DEBUG: Model change detected! New value: {new_model}")
        if new_model:
            # Update DB immediately (Persistent sync)
            self.api.update_config({'model_name': new_model})
            
            # Reload backend model (CRITICAL: actually switches the engine)
            self._show_snackbar(f"Switching to {new_model}...", COLORS['accent'])
            settings = self.api.reload_model()
            
            self._show_snackbar(f"Model active: {new_model}", COLORS['success'])
    
    def _reset_filters(self, e):
        """Reset all filters."""
        self.filter_date_range = "all"
        self.filter_score = "all"
        self.filter_source = "all"
        self.filter_keyword = "all"
        self.selected_source_ids = set()
        self.search_text = ""
        
        # Update UI controls with guards
        if hasattr(self, 'search_input') and self.search_input:
            self.search_input.value = ""
        if hasattr(self, 'source_selector_btn') and self.source_selector_btn:
            self.source_selector_btn.text = "Select Sources (All)"
        if hasattr(self, 'keyword_dropdown') and self.keyword_dropdown:
            self.keyword_dropdown.value = "all"
        
        self.current_page = 0
        self._refresh_table()
        
        if self.page:
            try:
                self.page.update()
            except: pass
        self._show_snackbar("Filters reset", COLORS['accent'])
    
    def _prev_page(self, e):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.page_label.value = f"Page {self.current_page + 1}"
            self._refresh_table()
    
    def _next_page(self, e):
        """Go to next page if there are more articles."""
        # Check if next page would be empty
        next_page_articles = self._get_articles_for_page(self.current_page + 1)
        if next_page_articles:
            self.current_page += 1
            self.page_label.value = f"Page {self.current_page + 1}"
            self._refresh_table()
        else:
            self._show_snackbar("No more pages", COLORS['warning'])
    
    def _get_articles_for_page(self, page_num):
        """Check if a page has articles (for pagination limit)."""
        import sqlite3
        db_path = "data/aieat_news.db"
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            offset = page_num * self.page_size
            cursor = conn.execute(
                f"SELECT article_id FROM articles_meta LIMIT {self.page_size} OFFSET {offset}"
            )
            return cursor.fetchone() is not None
    
    def _apply_filters(self, e):
        """Apply current filters."""
        # Read values from dropdowns
        # Source handled by dialog state (self.selected_source_ids)
        self.filter_keyword = self.keyword_dropdown.value if hasattr(self, 'keyword_dropdown') else "all"
        
        self._refresh_table()
        self.filter_panel.visible = False
        self._show_snackbar("Filters applied", COLORS['success'])
    
    def _export_csv(self, e):
        """Export filtered articles to CSV."""
        import csv
        from datetime import datetime
        
        articles = self._get_filtered_articles()
        if not articles:
            self._show_snackbar("No articles to export", COLORS['error'])
            return
        
        # Create export filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aieat_export_{timestamp}.csv"
        
        # Save to Desktop
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        filepath = os.path.join(desktop, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header
                writer.writerow(['Date', 'Source', 'Headline', 'Score', 'URL', 'Tags'])
                # Data
                for art in articles:
                    writer.writerow([
                        art.get('published_at', ''),
                        art.get('source_name', ''),
                        art.get('headline', ''),
                        art.get('ai_score', 0),
                        art.get('article_url', ''),
                        art.get('tags', '')
                    ])
            
            self._show_snackbar(f"✓ Exported {len(articles)} articles to Desktop/{filename}", COLORS['success'])
        except Exception as ex:
            self._show_snackbar(f"Export failed: {str(ex)}", COLORS['error'])
    
    def _refresh_table(self):
        """Refresh the table with current filters."""
        articles = self._get_filtered_articles()
        
        rows = []
        for art in articles:
            raw_score = art.get('ai_score')
            score = raw_score if raw_score and raw_score > 0 else 0
            score_display = str(score) if score > 0 else "—"
            headline = art.get('headline', '')[:60] if art.get('headline') else ''
            date_str = self._format_date(art.get('published_at', ''))
            source = art.get('source_name', '')[:20] if art.get('source_name') else ''
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(date_str, size=11)),
                        ft.DataCell(ft.Text(source, size=11)),
                        ft.DataCell(
                            ft.TextButton(
                                headline + ("..." if len(art.get('headline', '')) > 60 else ""),
                                on_click=lambda e, a=art: self.on_view_article(a),
                                style=ft.ButtonStyle(color=COLORS['accent'])
                            )
                        ),
                        ft.DataCell(self._build_keyword_chips(art)),
                        ft.DataCell(
                            ft.Row([
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    bgcolor=get_score_color(score) if score > 0 else ft.Colors.GREY_400,
                                    border_radius=4,
                                    content=ft.Text(score_display, color=ft.Colors.WHITE, size=11)
                                ),
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    icon_size=14,
                                    tooltip="Edit Score",
                                    on_click=lambda e, a=art: self._edit_score(a),
                                )
                            ], spacing=2)
                        ),
                    ],
                )
            )
        
        # Rebuild table
        date_icon = self._get_sort_icon("date")
        score_icon = self._get_sort_icon("score")
        
        new_table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.TextButton(
                        content=ft.Row([
                            ft.Text("Date", size=11, weight=ft.FontWeight.BOLD),
                            ft.Text(date_icon, size=10) if date_icon else ft.Container()
                        ], spacing=2),
                        on_click=lambda e: self._sort_by("date")
                    )
                ),
                ft.DataColumn(ft.Text("Source", size=11, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Headline", size=11, weight=ft.FontWeight.BOLD), expand=True),
                ft.DataColumn(ft.Text("Tags", size=11, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(
                    ft.TextButton(
                        content=ft.Row([
                            ft.Text("Score", size=11, weight=ft.FontWeight.BOLD),
                            ft.Text(score_icon, size=10) if score_icon else ft.Container()
                        ], spacing=2),
                        on_click=lambda e: self._sort_by("score")
                    )
                ),
            ],
            rows=rows,
            heading_row_color=ft.Colors.GREY_100,
            border_radius=8,
            column_spacing=15,
        )
        
        self.table_column.controls = [new_table]
        self._safe_update()
    
    # ==================== SCRAPER CONTROLS ====================
    
    def _on_start_click(self, e):
        """Handle START/STOP button click."""
        if self.is_running:
            self._stop_scraper()
        else:
            self._start_scraper()
    
    def _start_scraper(self):
        """Start the scraper as an async task."""
        self.is_running = True
        self._update_status("Running")
        
        # Update button to STOP state
        self.start_button.content = ft.Row([
            ft.Icon(ft.Icons.STOP, color=ft.Colors.WHITE, size=18),
            ft.Text("STOP SCRAPER", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
        ], spacing=8)
        self.start_button.style = ft.ButtonStyle(
            bgcolor=COLORS['error'],
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        )
        self.start_button.update()
        
        self.progress_container.visible = True
        self.progress_text.value = "Starting scraper..."
        self.progress_bar.value = 0
        self.page.update()
        
        # Run async task
        self.page.run_task(self._run_scraper_async)
    
    async def _run_scraper_async(self):
        """Run scraper logic in background thread (async wrapper)."""
        import asyncio
        try:
            # Capture the main event loop BEFORE entering background thread
            self._main_loop = asyncio.get_running_loop()
            # Run the blocking scraper in a thread
            result = await asyncio.to_thread(self._run_scraper_sync_logic)
            
            # Check if stopped during execution
            if self.is_running:
                self._on_scraper_complete(result)
        except Exception as ex:
            self._on_scraper_error(str(ex))

    def _run_scraper_sync_logic(self):
        """The actual blocking scraper + AI logic invoked by asyncio."""
        
        # --- Step 1: Scraping ---
        def scrape_progress(current, total_count, source_name):
            """Update UI with scraping progress (thread-safe)."""
            self.progress_text.value = f"Scraping {current}/{total_count}: {source_name}"
            self.progress_bar.value = current / total_count if total_count > 0 else 0
            if hasattr(self, '_main_loop') and self._main_loop:
                self._main_loop.call_soon_threadsafe(self.page.update)
            return self.is_running
        scrape_result = self.api.run_scraper(progress_callback=scrape_progress)
        
        if not self.is_running:
            return scrape_result
        
        # --- Step 2: AI Processing ---
        def ai_progress(current, total_count, message):
            """Update UI with AI scoring progress (thread-safe)."""
            self.progress_text.value = f"AI Scoring {current}/{total_count}: {message}"
            self.progress_bar.value = current / total_count if total_count > 0 else None
            if hasattr(self, '_main_loop') and self._main_loop:
                self._main_loop.call_soon_threadsafe(self.page.update)
            return self.is_running
        # Show indeterminate state while checking
        self.progress_text.value = "Starting AI analysis..."
        self.progress_bar.value = None  # indeterminate mode
        if hasattr(self, '_main_loop') and self._main_loop:
            self._main_loop.call_soon_threadsafe(self.page.update)
        
        ai_result = self.api.run_ai_processing(progress_callback=ai_progress)
        
        # Merge results
        scrape_result['ai_stats'] = ai_result
        return scrape_result
    
    def _on_scraper_complete(self, result: dict):
        """Called when scraper completes."""
        self.is_running = False
        self._update_status("Idle")
        
        # Reset button to START state using content property
        if hasattr(self, 'start_button') and self.start_button:
            self.start_button.content = ft.Row([
                ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE, size=18),
                ft.Text("START SCRAPER", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ], spacing=8)
            self.start_button.style = ft.ButtonStyle(
                bgcolor=COLORS['success'],
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            )
        
        if hasattr(self, 'progress_container') and self.progress_container:
            self.progress_container.visible = False
        
        new_articles = result.get('new_articles', 0)
        elapsed = result.get('elapsed_minutes', 0)
        
        # Build completion message with AI stats if available
        ai_stats = result.get('ai_stats', {})
        scored = ai_stats.get('scored', 0)
        translated = ai_stats.get('translated', 0)
        
        if scored > 0:
            msg = f"✓ Done! {new_articles} articles, {scored} scored, {translated} translated ({elapsed:.1f} min)"
        else:
            msg = f"✓ Done! {new_articles} new articles ({elapsed:.1f} min)"
        
        self._show_snackbar(msg, COLORS['success'])
        
        if self.page:
            try: self.page.update()
            except: pass
        self._refresh_table()
    
    def _on_scraper_error(self, error: str):
        """Called when scraper fails."""
        self.is_running = False
        self._update_status("Error")
        
        # Reset button to START state using content property
        if hasattr(self, 'start_button') and self.start_button:
            self.start_button.content = ft.Row([
                ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE, size=18),
                ft.Text("START SCRAPER", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ], spacing=8)
            self.start_button.style = ft.ButtonStyle(
                bgcolor=COLORS['success'],
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            )
        
        if hasattr(self, 'progress_container') and self.progress_container:
            self.progress_container.visible = False
            
        self._show_snackbar(f"Error: {error}", COLORS['error'])
        
        self._refresh_table()
        
        if self.page:
            try:
                self.page.update()
            except:
                pass
    
    def _stop_scraper(self, e=None):
        """Stop the scraper."""
        if self.is_running:
            self.is_running = False
            self._update_status("Stopped")
            
            # Reset button to START state using content property
            if hasattr(self, 'start_button') and self.start_button:
                self.start_button.content = ft.Row([
                    ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE, size=18),
                    ft.Text("START SCRAPER", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                ], spacing=8)
                self.start_button.style = ft.ButtonStyle(
                    bgcolor=COLORS['success'],
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                )
            
            if self.page:
                try: self.page.update()
                except: pass
        
        # Hide progress
        self.progress_container.visible = False
        
        # Refresh table to show any new articles scraped before stop
        self._refresh_table()
        
        self._show_snackbar("Scraper stopped - showing new articles", COLORS['warning'])
        try:
            self.page.update()
        except:
            pass
    
    def _update_status(self, status: str):
        """Update status badge."""
        self.status = status
        if self.status_badge:
            self.status_badge.bgcolor = {
                "Idle": COLORS['success'],
                "Running": COLORS['warning'],
                "Error": COLORS['error'],
                "Stopping...": COLORS['warning'],
            }.get(status, COLORS['accent'])
            self.status_badge.content = ft.Text(status, color=ft.Colors.WHITE, size=11)
            try:
                if self.status_badge.page:
                    self.status_badge.update()
            except: pass
    
    def _edit_score(self, article):
        """Open dialog to edit article score."""
        article_id = article.get('article_id')
        current_score = article.get('ai_score', 0) or 0
        headline = article.get('headline', '')[:50]
        
        score_input = ft.TextField(
            value=str(current_score),
            width=80,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        def save_score(e):
            try:
                new_score = int(score_input.value)
                if 0 <= new_score <= 8:
                    self.api.db.update_article_score(article_id, new_score)
                    self._show_snackbar(f"Score updated to {new_score}", COLORS['success'])
                    self._refresh_table()
                    dialog.open = False
                    self.page.update()
                else:
                    self._show_snackbar("Score must be 0-8", COLORS['error'])
            except ValueError:
                self._show_snackbar("Invalid score value", COLORS['error'])
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Edit Score", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(headline + "...", size=12, color=COLORS['text_secondary']),
                ft.Container(height=10),
                ft.Row([
                    ft.Text("Score (0-8):", size=12),
                    score_input,
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Save", on_click=save_score, 
                                  style=ft.ButtonStyle(bgcolor=COLORS['accent'], color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _show_snackbar(self, message: str, color: str):
        """Show a snackbar notification."""
        if not self.page:
            return
            
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            duration=4000,
        )
        try:
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()
        except:
            pass

    def _reset_batch_button(self):
        """Reset batch button after completion."""
        if hasattr(self, 'batch_score_btn') and self.batch_score_btn:
            self.batch_score_btn.content = ft.Text("BATCH SCORE ALL (IDLE)", size=12)
            self.batch_score_btn.disabled = False
            if self.page:
                try: self.page.update()
                except: pass
