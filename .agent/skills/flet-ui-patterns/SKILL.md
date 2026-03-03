---
name: flet-ui-patterns
description: Best practices for Flet UI development. Use when fixing UI bugs, FilePicker issues, or threading problems.
---

# Flet UI Patterns Skill

## 🔴 CRITICAL: FilePicker Pattern (KNOWN BUG)

**Location:** `app/ui/pages/config.py` lines 629-662

**Current Bug:**
```python
# ❌ WRONG — FilePicker created inline, not registered with page properly
def _import_sources_file(self, e):
    file_picker = ft.FilePicker()
    file_picker.on_result = on_file_picked
    self.page.overlay.append(file_picker)
    self.page.update()
    file_picker.pick_files(...)  # May fail — control not synced
```

**Correct Pattern:**
```python
# ✅ CORRECT — FilePicker created ONCE in __init__, reused
class ConfigPage:
    def __init__(self, page, api):
        self.page = page
        self.api = api
        
        # Create FilePicker ONCE and register immediately
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self._on_file_picked
        self.page.overlay.append(self.file_picker)
    
    def _import_sources_file(self, e):
        # Use async pattern to call pick_files
        self.page.run_task(self._pick_files_async)
    
    async def _pick_files_async(self):
        self.file_picker.pick_files(allowed_extensions=['txt', 'csv'])
    
    def _on_file_picked(self, e):
        if not e.files:
            return
        # Process files here...
```

---

## Threading Pattern (CRITICAL)

**Problem:** UI freezes when running long operations.

### ❌ WRONG Pattern
```python
import threading

def start_operation(self, e):
    thread = threading.Thread(target=self._run_operation)
    thread.start()

def _run_operation(self):
    result = api.long_call()
    self.text.value = result
    self.page.update()  # Won't redraw until focus change!
```

### ✅ CORRECT Pattern
```python
def start_operation(self, e):
    self.page.run_task(self._run_operation_async)

async def _run_operation_async(self):
    import asyncio
    result = await asyncio.to_thread(api.long_call)
    self.text.value = result
    self.page.update()  # Works!
```

---

## Dropdown on_change Handler

**IMPORTANT:** Define on_change AFTER the Dropdown constructor!

```python
# ❌ WRONG
dropdown = ft.Dropdown(options=[...], on_change=self._handler)

# ✅ CORRECT
dropdown = ft.Dropdown(options=[...])
dropdown.on_change = self._handler
```

---

## Common Pitfalls

1. **FilePicker desync** — Create in `__init__`, not inline
2. **Control references become None** — Store as class attributes
3. **Snackbar not showing** — Must call `page.update()` after adding
4. **Dialog not closing** — Set `dialog.open = False` then `page.update()`
