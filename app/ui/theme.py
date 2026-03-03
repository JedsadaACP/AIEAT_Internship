"""
AIEAT News Dashboard - Flet UI
App Configuration and Theme
"""

# Color Theme (Blue - Professional)
COLORS = {
    'sidebar_bg': '#1e3a5f',      # Dark blue
    'sidebar_selected': '#2d5a8f', # Lighter blue (selected)
    'accent': '#3498db',           # Bright blue
    'accent_light': '#5dade2',     # Light accent
    'background': '#f5f5f5',       # Light gray
    'card_bg': '#ffffff',          # White
    'text_primary': '#2c3e50',     # Dark gray
    'text_secondary': '#7f8c8d',   # Medium gray
    'success': '#27ae60',          # Green
    'warning': '#f39c12',          # Orange
    'error': '#e74c3c',            # Red
    'primary': '#1e3a5f',          # Primary Blue (Same as sidebar)
}

# App Configuration
APP_CONFIG = {
    'title': 'A.I. News Dashboard',
    'version': 'v1.0.0',
    'sidebar_width': 180,
    'default_page_size': 10,
}

# Navigation Items
NAV_ITEMS = [
    {'label': 'Dashboard', 'icon': 'DASHBOARD', 'route': 'dashboard'},
    {'label': 'Profiles', 'icon': 'ACCOUNT_CIRCLE', 'route': 'profiles'},
    {'label': 'User Config', 'icon': 'SETTINGS', 'route': 'config'},
    {'label': 'Style Setting', 'icon': 'PALETTE', 'route': 'style'},
    {'label': 'Log', 'icon': 'LIST_ALT', 'route': 'log'},
    {'label': 'About', 'icon': 'INFO', 'route': 'about'},
]

# Score Colors
def get_score_color(score: int) -> str:
    """Get color based on score value."""
    if score >= 5:
        return COLORS['success']
    elif score >= 3:
        return COLORS['warning']
    else:
        return COLORS['error']
