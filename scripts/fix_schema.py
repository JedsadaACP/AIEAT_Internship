
import sqlite3
import os
import sys

# Force UTF-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Constants
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "aieat_news.db")

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Checking schema at {DB_PATH}...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Check system_profile for date_limit_days
        cursor.execute("PRAGMA table_info(system_profile)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "date_limit_days" not in columns:
            print("Adding missing column 'date_limit_days' to system_profile...")
            conn.execute("ALTER TABLE system_profile ADD COLUMN date_limit_days INTEGER DEFAULT 14")
            conn.commit()
            print("✅ Column added successfully.")
        else:
            print("✅ 'date_limit_days' column already exists.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")

if __name__ == "__main__":
    fix_schema()
