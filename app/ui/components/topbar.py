import flet as ft
from app.services.backend_api import BackendAPI

class TopBar(ft.Container):
    def __init__(self, api: BackendAPI, on_profile_click):
        super().__init__()
        self.api = api
        self.on_profile_click = on_profile_click
        self.profile_btn = ft.OutlinedButton(" ", on_click=self.on_profile_click)
        
        # In Flet 0.80+, we configure the Container properties directly in __init__
        self.padding = ft.padding.only(top=10, right=20, bottom=10)
        self.content = ft.Row(
            controls=[
                ft.Text("AIEAT Dashboard", size=20, weight="bold", expand=True),
                self.profile_btn
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Load initial state immediately upon construction
        self._load_state()

    def refresh(self):
        """Public method to force a state reload."""
        self._load_state()
        self.update()

    def _load_state(self):
        """Dynamically pulls the active profile from the database."""
        try:
            active_prof = self.api.get_active_profile()
            prof_name = active_prof['profile_name'] if active_prof else "Default"
            self.profile_btn.content = ft.Text(f"👤 Profile: {prof_name}")
        except Exception as e:
            self.profile_btn.content = ft.Text("👤 Profile: Error")
