import sqlite3
conn = sqlite3.connect('data/aieat_news.db')
try:
    conn.execute("ALTER TABLE system_profile ADD COLUMN inference_device TEXT DEFAULT 'auto'")
    conn.commit()
    print("Column 'inference_device' added successfully")
except Exception as e:
    print(f"Error or already exists: {e}")
conn.close()
