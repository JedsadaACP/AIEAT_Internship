"""
AIEAT News Detail Page
Original/Output view with export and actions
"""
import flet as ft
import os
import threading
from datetime import datetime
from app.ui.theme import COLORS, get_score_color
from app.services.backend_api import BackendAPI


class DetailPage:
    """News detail page component."""
    
    def __init__(self, page: ft.Page, api: BackendAPI, article: dict, on_back):
        self.page = page
        self.api = api
        self.article = article
        self.on_back = on_back
        self.detail = None
        self.is_translating = False
        self.output_container = None
        self.main_column = None
        self.score_button = None  # Reference to score button
        self.loading_indicator = None  # Reference to loading indicator
        
    def build(self) -> ft.Control:
        """Build the detail page."""
        # Fetch full article detail
        self.detail = self.api.get_article_detail(self.article['article_id'])
        if not self.detail:
            return ft.Text("Article not found")
        
        self.main_column = ft.Column(
            controls=self._build_layout_controls(),
            expand=True,
            spacing=0
        )
        return self.main_column
    
    def _build_layout_controls(self):
        """Build the list of layout controls."""
        return [
            self._build_header(),
            ft.Container(height=10),
            self._build_metadata(),
            ft.Container(height=10),
            self._build_content_area(),
        ]
    
    def _build_header(self) -> ft.Control:
        """Build header with headline and actions."""
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Column([
                # Title row
                ft.Text(
                    self.detail.get('headline', 'Untitled'),
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS['text_primary']
                ),
                ft.Container(height=10),
                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        "Translate",
                        icon=ft.Icons.TRANSLATE,
                        style=ft.ButtonStyle(
                            bgcolor=COLORS['warning'],
                            color=ft.Colors.WHITE,
                        ),
                        on_click=self._translate_article
                    ),
                    ft.ElevatedButton(
                        "Export Source",
                        icon=ft.Icons.DOWNLOAD,
                        style=ft.ButtonStyle(
                            bgcolor=COLORS['accent'],
                            color=ft.Colors.WHITE,
                        ),
                        on_click=self._export_source
                    ),
                    ft.ElevatedButton(
                        "Export Output",
                        icon=ft.Icons.DOWNLOAD,
                        style=ft.ButtonStyle(
                            bgcolor=COLORS['accent'],
                            color=ft.Colors.WHITE,
                        ),
                        on_click=self._export_output
                    ),
                    ft.Container(expand=True),
                    ft.TextButton(
                        "← Back",
                        on_click=lambda e: self.on_back(),
                        style=ft.ButtonStyle(color=COLORS['accent'])
                    )
                ], spacing=10)
            ])
        )
    
    def _build_metadata(self) -> ft.Control:
        """Build metadata section."""
        score = self.detail.get('ai_score', 0) or 0
        
        return ft.Container(
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Text("Author:", weight=ft.FontWeight.BOLD, size=12),
                        ft.Text(self.detail.get('author_name', 'Unknown'), size=12)
                    ]),
                    ft.Row([
                        ft.Text("Date:", weight=ft.FontWeight.BOLD, size=12),
                        ft.Text(self._format_date(self.detail.get('published_at', '')), size=12)
                    ]),
                    ft.Row([
                        ft.Text("Source URL:", weight=ft.FontWeight.BOLD, size=12),
                        ft.TextButton(
                            self.detail.get('source_name', ''),
                            url=self.detail.get('article_url', '#'),
                            style=ft.ButtonStyle(color=COLORS['accent'])
                        )
                    ]),
                ], spacing=5),
                ft.Container(expand=True),
                # Score
                ft.Column([
                    ft.Row([
                        ft.Text("Score:", weight=ft.FontWeight.BOLD, size=12),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            bgcolor=get_score_color(score),
                            border_radius=5,
                            content=ft.Text(f"{score} / 8", color=ft.Colors.WHITE, size=12)
                        ),
                    ]),
                    # Loading indicator (initially hidden)
                    ft.Container(
                        content=ft.Row([
                            ft.ProgressRing(width=16, height=16, stroke_width=2),
                            ft.Text("Scoring with AI...", size=11, color=COLORS['accent'])
                        ], spacing=5),
                        visible=False,
                        ref=ft.Ref[ft.Container](),
                    ),
                    ft.TextButton(
                        "Regenerate Score",
                        icon=ft.Icons.REFRESH,
                        style=ft.ButtonStyle(color=COLORS['accent']),
                        on_click=self._regenerate_score
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.END)
            ])
        )
    
    def _build_content_area(self) -> ft.Control:
        """Build the two-column content area (Original | Output)."""
        original = self.detail.get('original_content', '')
        thai = self.detail.get('thai_content', '')
        
        # Build output content based on translation status
        if thai:
            output_content = ft.Markdown(thai, selectable=True)
        else:
            output_content = ft.Column([
                ft.Text("No translation available.", size=14, color=COLORS['text_secondary']),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Translate Now",
                    icon=ft.Icons.TRANSLATE,
                    style=ft.ButtonStyle(
                        bgcolor=COLORS['accent'],
                        color=ft.Colors.WHITE,
                    ),
                    on_click=self._translate_article
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.output_container = ft.Container(
            expand=True,
            bgcolor=ft.Colors.WHITE,
            padding=10,
            content=output_content
        )
        
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor=COLORS['card_bg'],
            border_radius=8,
            content=ft.Row([
                # Original Source column
                ft.Container(
                    expand=True,
                    padding=15,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=5,
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Original Source", weight=ft.FontWeight.BOLD, size=14),
                            ft.Container(expand=True),
                            ft.IconButton(
                                ft.Icons.COPY,
                                tooltip="Copy",
                                icon_size=18,
                                on_click=lambda e: self._copy_to_clipboard(original)
                            )
                        ]),
                        ft.Divider(),
                        ft.Container(
                            expand=True,
                            padding=10,
                            content=ft.Text(
                                original[:3000] if original else "No content available",
                                size=13,
                                selectable=True,
                            )
                        )
                    ], expand=True, scroll=ft.ScrollMode.AUTO)
                ),
                
                ft.Container(width=10),
                
                # Output column
                ft.Container(
                    expand=True,
                    padding=15,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=5,
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Output", weight=ft.FontWeight.BOLD, size=14),
                            ft.TextButton(
                                "Regenerate",
                                icon=ft.Icons.REFRESH,
                                on_click=self._translate_article
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                ft.Icons.COPY,
                                tooltip="Copy",
                                icon_size=18,
                                on_click=lambda e: self._copy_to_clipboard(thai)
                            )
                        ]),
                        ft.Divider(),
                        self.output_container
                    ], expand=True, scroll=ft.ScrollMode.AUTO)
                ),
            ], expand=True)
        )
    
    def _translate_article(self, e):
        """Translate the article in background thread."""
        if self.is_translating:
            return
        
        self.is_translating = True
        
        # Show loading indicator with more info
        self.output_container.content = ft.Column([
            ft.ProgressRing(width=40, height=40),
            ft.Container(height=10),
            ft.Text("Loading AI model...", color=COLORS['text_secondary']),
            ft.Text("This may take 30-60 seconds", size=10, color=COLORS['text_secondary'])
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
        
        # Run translation in background thread
        import threading
        thread = threading.Thread(target=self._run_translation_thread, daemon=True)
        thread.start()
    
    def _run_translation_thread(self):
        """Run translation in background (called from thread)."""
        try:
            # Update status
            self.output_container.content = ft.Column([
                ft.ProgressRing(width=40, height=40),
                ft.Container(height=10),
                ft.Text("Translating with Typhoon 2.5...", color=COLORS['text_secondary']),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            try:
                self.page.update()
            except:
                pass
            
            # Call translation API
            result = self.api.translate_article(self.article['article_id'])
            
            if result and result.get('thai_content'):
                self.detail['thai_content'] = result['thai_content']
                self.output_container.content = ft.Markdown(
                    result['thai_content'],
                    selectable=True
                )
                self._show_snackbar(f"✓ Translation complete! ({result.get('chars', 0)} chars)", COLORS['success'])
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'No response'
                self.output_container.content = ft.Column([
                    ft.Text(f"Translation failed: {error_msg}", size=12, color=COLORS['error']),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Retry",
                        icon=ft.Icons.REFRESH,
                        on_click=self._translate_article
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                self._show_snackbar("Translation failed. Please try again.", COLORS['error'])
        except Exception as ex:
            self.output_container.content = ft.Column([
                ft.Text(f"Error: {str(ex)}", size=12, color=COLORS['error']),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Retry",
                    icon=ft.Icons.REFRESH,
                    on_click=self._translate_article
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self._show_snackbar(f"Error: {str(ex)}", COLORS['error'])
        finally:
            self.is_translating = False
            try:
                self.page.update()
            except:
                pass
    
    def _regenerate_score(self, e):
        """Regenerate article score."""
        # Find the loading indicator (sibling of button)
        button = e.control
        parent_column = button.parent
        
        # Show loading, hide button
        for control in parent_column.controls:
            if isinstance(control, ft.Container) and control.visible == False:
                self.loading_indicator = control
                control.visible = True
        
        button.visible = False
        self.score_button = button
        
        # Update UI immediately
        self.page.update()
        
        # Run scoring using async pattern (proper Flet way)
        async def run_scoring():
            try:
                # Call scoring API (in executor to not block)
                import asyncio
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    lambda: self.api.score_article(self.article['article_id'])
                )
                
                if result and result.get('success'):
                    new_score = result.get('total_score', 0)
                    # Update article data
                    self.detail['ai_score'] = new_score
                    self.article['ai_score'] = new_score
                    
                    # Refresh page content (rebuilds with new score)
                    self.main_column.controls = self._build_layout_controls()
                    self.page.update()
                    
                    self._show_snackbar(f"✓ Score updated to {new_score}/8", COLORS['success'])
                else:
                    error = result.get('error', 'Unknown error') if result else 'No response'
                    self._show_snackbar(f"Scoring failed: {error}", COLORS['error'])
                    # Restore button, hide loading
                    if self.loading_indicator:
                        self.loading_indicator.visible = False
                    if self.score_button:
                        self.score_button.visible = True
                    self.page.update()
            except Exception as ex:
                self._show_snackbar(f"Error: {str(ex)}", COLORS['error'])
                # Restore button, hide loading
                if self.loading_indicator:
                    self.loading_indicator.visible = False
                if self.score_button:
                    self.score_button.visible = True
                self.page.update()
        
        # Run the async task
        self.page.run_task(run_scoring)
    
    def _export_source(self, e):
        """Export original source."""
        self._save_file("source", self.detail.get('original_content', ''))

    def _export_output(self, e):
        """Export translated output."""
        self._save_file("translated", self.detail.get('thai_content', ''))
        
    def _save_file(self, type_prefix, content):
        """Save content to file on Desktop."""
        if not content:
            self._show_snackbar("No content to export", COLORS['warning'])
            return
            
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"AIEAT_{type_prefix}_{timestamp}.txt"
            filepath = os.path.join(desktop, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
                
            self._show_snackbar(f"Saved to Desktop: {filename}", COLORS['success'])
        except Exception as ex:
            self._show_snackbar(f"Export failed: {str(ex)}", COLORS['error'])
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        if text:
            self.page.set_clipboard(text)
            self._show_snackbar("Copied to clipboard!", COLORS['success'])
        else:
            self._show_snackbar("No content to copy", COLORS['warning'])
    
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
    
    def _format_date(self, date_str: str) -> str:
        """Format date to DD/MM/YYYY."""
        if not date_str:
            return "Unknown"
        try:
            date_str = str(date_str)
            for fmt in [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
            ]:
                try:
                    dt = datetime.strptime(date_str[:26].replace('Z', ''), fmt.replace('.%fZ', '.%f').replace('Z', ''))
                    return dt.strftime('%d/%m/%Y')
                except:
                    continue
            
            if len(date_str) >= 10 and '-' in date_str[:10]:
                parts = date_str[:10].split('-')
                if len(parts) == 3:
                    return f"{parts[2]}/{parts[1]}/{parts[0]}"
            
            return date_str[:20] if len(date_str) > 20 else date_str
        except:
            return date_str[:20] if len(date_str) > 20 else date_str
