
import pytest
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.services.database_manager import DatabaseManager
from app.services.backend_api import BackendAPI

def test_db_persistence():
    # Setup in-memory DB
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Load schema
    with open("data/schema.sql", 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    
    # Init Managers
    db = DatabaseManager(":memory:")
    db.set_persistent_connection(conn)
    
    # Mock API with real DB
    api = BackendAPI()
    api.db = db 
    
    # 1. Initial State
    config = api.get_config()
    print(f"Initial model: {config['profile'].get('model_name')}")
    
    # 2. Update
    updates = {'model_name': 'new-model'}
    api.update_config(updates)
    
    # 3. Verify
    config = api.get_config()
    final_model = config['profile'].get('model_name')
    print(f"Updated model: {final_model}")
    
    assert final_model == 'new-model'

if __name__ == "__main__":
    try:
        test_db_persistence()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
