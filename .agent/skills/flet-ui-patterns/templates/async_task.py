
import asyncio
import flet as ft

# BOILERPLATE: Copy this pattern for long-running tasks in Flet
# ------------------------------------------------------------

def start_long_task(self, e):
    """Event handler wrapper."""
    # 1. Show loading state
    self.loading_indicator.visible = True
    self.page.update()
    
    # 2. Run async task via Flet's run_task
    self.page.run_task(self._run_task_async)

async def _run_task_async(self):
    """The actual async logic."""
    try:
        # 3. Offload blocking Sync I/O to thread
        result = await asyncio.to_thread(self.heavy_blocking_function)
        
        # 4. Update UI with result (safe on main thread)
        self.result_text.value = f"Done: {result}"
        
    except Exception as e:
        self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error: {e}")))
        
    finally:
        # 5. Cleanup / Reset UI
        self.loading_indicator.visible = False
        self.page.update()

def heavy_blocking_function(self):
    """Your existing blocking code (Ollama, DB, Requests)."""
    import time
    time.sleep(2) # Simulate work
    return "Success"
