"""Sync all sources from JSON to DB"""
import json
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')

# Get existing URLs in DB
existing = set(r[0] for r in conn.execute('SELECT base_url FROM sources').fetchall())
print(f'Existing in DB: {len(existing)}')

# Load JSON sources
with open('app/config/sources.json', 'r') as f:
    json_sources = json.load(f)['sources']
print(f'Sources in JSON: {len(json_sources)}')

# Get Online status ID
online_id = conn.execute("SELECT status_id FROM master_status WHERE status_name='Online'").fetchone()[0]

# Add missing sources
added = 0
for s in json_sources:
    url = s.get('url', s.get('base_url', ''))
    name = s.get('name', s.get('domain_name', 'Unknown'))
    
    if url and url not in existing:
        try:
            conn.execute('''
                INSERT INTO sources (domain_name, base_url, scraper_type, status_id)
                VALUES (?, ?, 'RSS', ?)
            ''', (name, url, online_id))
            print(f'  Added: {name}')
            added += 1
        except Exception as e:
            print(f'  Error adding {name}: {e}')

conn.commit()

# Final count
final = conn.execute('SELECT COUNT(*) FROM sources').fetchone()[0]
print(f'\nAdded: {added}')
print(f'Total sources in DB: {final}')

conn.close()
