"""
Compare sources.json to database entries to find missing sources.
"""
import json
import sqlite3

# Load sources from config
with open('app/config/sources.json', 'r') as f:
    data = json.load(f)
    config_sources = data.get('sources', data) if isinstance(data, dict) else data

# Get sources from DB
conn = sqlite3.connect('data/aieat_news.db')
cursor = conn.execute('SELECT base_url FROM sources')
db_urls = {row[0] for row in cursor}
conn.close()

print('=== MISSING SOURCES ===')
print(f'Total in config: {len(config_sources)}')
print(f'Total in DB: {len(db_urls)}')
print()

missing = []
for src in config_sources:
    if src['url'] not in db_urls:
        missing.append(src)
        print(f"- {src['name']}: {src['url']}")

print()
print(f'Missing: {len(missing)} sources')
