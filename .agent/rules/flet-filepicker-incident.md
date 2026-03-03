# Flet Incident Log: FilePicker Desync

## Observed Problem
*   **Error Message**: `Unknown control: FilePicker` (UI-side banner) or `TypeError: FilePicker.__init__() got an unexpected keyword argument 'on_result'`.
*   **Behavior**: The `FilePicker` control becomes "unregistered" or "unknown" to the Flet client (browser/window) after page navigation or UI refreshes, even if the Python object persists in a cache.
*   **Async Collision**: `FilePicker.pick_files()` is a coroutine and must be `awaited`. Calling it from a synchronous event handler without a bridge results in a `RuntimeWarning: coroutine was never awaited` and the dialog failing to open.

## Constraints Encountered
1.  **Overlay Sync**: Adding a control to `page.overlay` is not a guarantee of persistence if the page content is swapped and the client-side state is reset.
2.  **Constructor Syntax**: Certain versions of Flet do not support `on_result` as a constructor argument for `FilePicker`; it must be assigned as a property: `picker.on_result = handler`.
3.  **Caching Conflict**: Using `page_cache` for UI pages can cause desynchronization between the "live" Frontend DOM and "cached" Python Control IDs.
