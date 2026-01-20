"""Database integrity and schema verification"""
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')
conn.row_factory = sqlite3.Row

print('=== DATABASE SCHEMA CHECK ===')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f'Tables: {[t[0] for t in tables]}')

print('\n=== FOREIGN KEY INTEGRITY ===')
fk_check = conn.execute('PRAGMA foreign_key_check').fetchall()
print(f'FK violations: {len(fk_check)}')

print('\n=== DATA COUNTS ===')
for table in ['sources', 'articles_meta', 'article_content', 'master_status', 'tags', 'models', 'system_profile', 'styles']:
    try:
        count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        print(f'  {table}: {count} rows')
    except Exception as e:
        print(f'  {table}: ERROR - {e}')

print('\n=== ARTICLES DATA QUALITY ===')
missing_content = conn.execute('SELECT COUNT(*) FROM articles_meta m LEFT JOIN article_content c ON m.article_id = c.article_id WHERE c.original_content IS NULL').fetchone()[0]
print(f'  Articles missing content: {missing_content}')

missing_source = conn.execute('SELECT COUNT(*) FROM articles_meta WHERE source_id NOT IN (SELECT source_id FROM sources)').fetchone()[0]
print(f'  Articles with invalid source_id: {missing_source}')

null_headlines = conn.execute("SELECT COUNT(*) FROM articles_meta WHERE headline IS NULL OR headline = ''").fetchone()[0]
print(f'  Articles with null/empty headline: {null_headlines}')

print('\n=== SCORING STATUS ===')
scored = conn.execute('SELECT COUNT(*) FROM articles_meta WHERE ai_score > 0').fetchone()[0]
unscored = conn.execute('SELECT COUNT(*) FROM articles_meta WHERE ai_score IS NULL OR ai_score = 0').fetchone()[0]
print(f'  Scored: {scored}')
print(f'  Unscored: {unscored}')

print('\n=== TRANSLATION STATUS ===')
translated = conn.execute("SELECT COUNT(*) FROM article_content WHERE thai_content IS NOT NULL AND thai_content != ''").fetchone()[0]
print(f'  Translated: {translated}')

print('\n=== STATUS CODES ===')
for row in conn.execute("SELECT status_id, status_name, status_group FROM master_status"):
    print(f'  {row[0]}: {row[1]} ({row[2]})')

conn.close()
