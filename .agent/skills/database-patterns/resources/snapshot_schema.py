
import sqlite3
import json
import os
import sys

# Default DB path
DB_PATH = os.path.join("data", "aieat_news.db")

def snapshot_schema(db_path=DB_PATH):
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        schema = {}
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
        
        for table in tables:
            # Get columns
            cursor.execute(f"PRAGMA table_info({table})")
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "pk": bool(col[5])
                })
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            schema[table] = {
                "columns": columns,
                "row_count": count
            }
            
        conn.close()
        print(json.dumps(schema, indent=2))
        
    except Exception as e:
        print(f"Error reading schema: {e}")

if __name__ == "__main__":
    snapshot_schema()
