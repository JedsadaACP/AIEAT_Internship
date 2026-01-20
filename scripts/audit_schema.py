"""
Audit database schema - list all tables and columns.
"""
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')
conn.row_factory = sqlite3.Row

# Get all tables
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print("=" * 60)
print("DATABASE SCHEMA AUDIT")
print("=" * 60)

for table in tables:
    name = table[0]
    print(f"\n[TABLE] {name}")
    print("-" * 40)
    
    # Get columns
    cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
    for col in cols:
        col_name = col[1]
        col_type = col[2]
        not_null = "NOT NULL" if col[3] else ""
        default = f"DEFAULT {col[4]}" if col[4] else ""
        pk = "PK" if col[5] else ""
        print(f"  {col_name}: {col_type} {pk} {not_null} {default}".strip())
    
    # Get row count
    count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    print(f"  [Rows: {count}]")

conn.close()
