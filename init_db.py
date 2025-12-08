from app.services.database_manager import DatabaseManager

if __name__ == "__main__":
    print("🔄 Starting Database Setup...")
    
    # Initializing the class automatically triggers db creation
    db = DatabaseManager()
    
    # Test a query to ensure seed data exists
    status_list = db.fetch_all("SELECT * FROM master_status")
    
    print(f"\n✅ Connection Successful! Found {len(status_list)} Status Types:")
    for status in status_list:
        print(f"   - [{status['status_code']}] {status['display_name']}")
    
    print("\n🚀 You are ready to build the Scraper!")