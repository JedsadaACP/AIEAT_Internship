"""
Check date analysis in database.
"""
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')

print('=== Date Analysis ===')

# Count missing dates
cursor = conn.execute('SELECT COUNT(*) FROM articles_meta WHERE published_at IS NULL OR published_at = ""')
print(f'No date: {cursor.fetchone()[0]}')

cursor = conn.execute('SELECT COUNT(*) FROM articles_meta WHERE published_at IS NOT NULL AND published_at != ""')
print(f'Has date: {cursor.fetchone()[0]}')

print()
print('Sample dates:')
cursor = conn.execute('SELECT published_at FROM articles_meta WHERE published_at IS NOT NULL AND published_at != "" LIMIT 5')
for r in cursor:
    print(f'  {r[0]}')

print()
print('Articles WITHOUT dates:')
cursor = conn.execute('SELECT headline FROM articles_meta WHERE published_at IS NULL OR published_at = "" LIMIT 5')
for r in cursor:
    print(f'  {r[0][:50]}...')

conn.close()
