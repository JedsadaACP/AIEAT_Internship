"""
AIEAT UI Launcher
Run from project root: python run_ui.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft
from app.ui.main import main

if __name__ == "__main__":
    ft.run(main)
