"""Populate tags table with keywords and domains"""
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')

# Get Active status ID
active_id = conn.execute("SELECT status_id FROM master_status WHERE status_name='Active'").fetchone()[0]
print(f'Active status ID: {active_id}')

# Clear existing tags
conn.execute('DELETE FROM tags')

# Keywords from JSON
keywords = ['A.I.', 'Google', 'Microsoft', 'Nvidia', 'Crypto', 'Chipset']
print(f'Adding {len(keywords)} keywords...')
for kw in keywords:
    conn.execute('''
        INSERT INTO tags (tag_name, tag_type, weight_score, status_id)
        VALUES (?, 'Keyword', 1, ?)
    ''', (kw, active_id))

# Domains from UI mockup
domains = ['Technology', 'Economics', 'Politics']
print(f'Adding {len(domains)} domains...')
for d in domains:
    conn.execute('''
        INSERT INTO tags (tag_name, tag_type, weight_score, status_id)
        VALUES (?, 'Domain', 1, ?)
    ''', (d, active_id))

conn.commit()

# Verify
tags = conn.execute('SELECT tag_id, tag_name, tag_type FROM tags ORDER BY tag_type, tag_id').fetchall()
for t in tags:
    print(f'  [{t[2]}] {t[0]}: {t[1]}')

print(f'Total tags: {len(tags)}')
conn.close()
