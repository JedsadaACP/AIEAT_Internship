"""
AIEAT Path Utilities - Centralized path resolution for both dev and .exe.
When running as source: paths are relative to the project root.
When running as .exe: paths are relative to the executable's directory.
PyInstaller sets sys.frozen = True and sys._MEIPASS to the temp bundle dir.
"""
import os
import sys


def get_project_root() -> str:
    """
    Get the project root directory.
    
    - Development: returns the directory containing app/, data/, etc.
    - Frozen .exe: returns the directory containing the .exe file.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_data_dir() -> str:
    """Get path to data/ directory (contains DB, schema, CSV)."""
    return os.path.join(get_project_root(), "data")


def get_config_dir() -> str:
    """Get path to app/config/ directory (contains JSON configs)."""
    return os.path.join(get_project_root(), "app", "config")


def get_logs_dir() -> str:
    """Get path to logs/ directory."""
    log_dir = os.path.join(get_project_root(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir
