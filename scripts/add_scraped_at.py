"""
Add scraped_at column to articles_meta for reliable date filtering.
"""
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')

try:
    conn.execute("ALTER TABLE articles_meta ADD COLUMN scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    conn.commit()
    print("Column 'scraped_at' added successfully")
except Exception as e:
    print(f"Error or already exists: {e}")

conn.close()
