import os

def create_structure():
    # Define the folder hierarchy
    folders = [
        "app",
        "app/config",
        "app/services",  # Logic (Scraper, DB, AI)
        "app/ui",        # PyQt6 Widgets
        "app/utils",     # Helpers (Logger, Formatting)
        "data",          # DB file location
        "data/models",   # .gguf file location
        "logs",          # Log files
        "notebooks"      # <--- ADDED: For your Jupyter Presentation
    ]
    
    # Define empty files to initialize
    files = [
        "app/__init__.py",
        "app/config/__init__.py",
        "app/config/settings.py",        # Paths & Constants
        "app/services/__init__.py",
        "app/services/database_manager.py",
        "app/services/scraper_service.py",
        "app/services/ai_engine.py",     # <--- ADDED: Placeholder for Week 6
        "app/ui/__init__.py",
        "app/ui/main_window.py",         # <--- ADDED: Main Entry for GUI
        "app/utils/__init__.py",
        "data/schema.sql",               # <--- ADDED: Place your SQL here
        "main.py",
        "requirements.txt"
    ]

    print("🚀 Initializing Project Structure...")

    # Create Folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"   [OK] Created Folder: {folder}/")

    # Create Files
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                pass  # Create empty file
            print(f"   [OK] Created File:   {file}")
        else:
            print(f"   [Skip] File exists:  {file}")

    print("\n✅ Project Structure Ready!")
    print("Next Step: Paste the SQL code into 'data/schema.sql'")

if __name__ == "__main__":
    create_structure()