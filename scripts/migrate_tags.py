"""
Migration script to fix unique constraint on tags table.
Allows same name for different tag types (e.g., 'IT' can be both Keyword and Domain)
"""
import sqlite3
import os

def run_migration():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'aieat_news.db')
    db_path = os.path.normpath(db_path)
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Step 1: Create new table with correct constraint
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags_new (
                tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL,
                tag_type TEXT DEFAULT 'Keyword',
                weight_score INTEGER DEFAULT 1,
                status_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT,
                UNIQUE(tag_name, tag_type),
                FOREIGN KEY (status_id) REFERENCES master_status(status_id)
            )
        """)
        
        # Step 2: Copy data from old table
        cursor.execute("""
            INSERT OR IGNORE INTO tags_new 
            (tag_id, tag_name, tag_type, weight_score, status_id, created_at, updated_at, updated_by)
            SELECT tag_id, tag_name, tag_type, weight_score, status_id, created_at, updated_at, updated_by
            FROM tags
        """)
        
        # Step 3: Drop old table
        cursor.execute("DROP TABLE tags")
        
        # Step 4: Rename new table
        cursor.execute("ALTER TABLE tags_new RENAME TO tags")
        
        conn.commit()
        print("✓ Migration complete! Tags table now allows same name for different types.")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
