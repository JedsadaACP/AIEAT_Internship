import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="aieat_news.db"):
        # 1. Calculate paths relative to THIS file
        # This ensures it works no matter where you run the project from
        base_dir = os.path.dirname(os.path.abspath(__file__)) # inside app/services/
        project_root = os.path.dirname(os.path.dirname(base_dir)) # go up to project root
        
        self.db_path = os.path.join(project_root, "data", db_name)
        self.schema_path = os.path.join(project_root, "data", "schema.sql")

        # 2. Check if DB exists. If not, build it.
        if not os.path.exists(self.db_path):
            print(f"⚠️ Database file not found at: {self.db_path}")
            print("🔨 Starting construction based on your design...")
            self._initialize_db()
        else:
            print(f"✅ Database already exists at: {self.db_path}")

    def get_connection(self):
        """Returns a connection to the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name (row['url'])
        conn.execute("PRAGMA foreign_keys = ON") # Enforce your Relationship Lines
        return conn

    def _initialize_db(self):
        """Reads schema.sql and builds the 11 tables"""
        # Check if the Blueprint exists
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"❌ Critical Error: Blueprint missing at {self.schema_path}")

        # Read the SQL file
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute the entire script at once
            cursor.executescript(schema_sql)
            
            conn.commit()
            conn.close()
            print("✅ Success: The Database has been built matching your Schema.")
        except sqlite3.Error as e:
            print(f"❌ SQL Error: {e}")

# This block allows you to run this file directly to test it
if __name__ == "__main__":
    db = DatabaseManager()