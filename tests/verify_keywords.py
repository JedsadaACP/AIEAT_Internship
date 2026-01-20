"""Verify keywords actually appear in scored article content"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3

conn = sqlite3.connect('data/aieat_news.db')
conn.row_factory = sqlite3.Row

# Get top scored articles with content
cursor = conn.execute('''
    SELECT m.article_id, m.headline, m.ai_score, c.original_content
    FROM articles_meta m
    JOIN article_content c ON m.article_id = c.article_id
    WHERE m.ai_score >= 4
    ORDER BY m.ai_score DESC
    LIMIT 5
''')

keywords = ['A.I.', 'Google', 'Microsoft', 'Nvidia', 'Crypto', 'Chipset', 'AI']

print('=' * 70)
print('KEYWORD VERIFICATION - Top Scored Articles')
print('=' * 70)

for row in cursor:
    article_id = row['article_id']
    headline = row['headline']
    score = row['ai_score']
    content = row['original_content'].lower() if row['original_content'] else ''
    
    print(f'\nArticle {article_id}: Score {score}')
    print(f'Headline: {headline[:60]}...')
    
    found = []
    for kw in keywords:
        if kw.lower() in content:
            found.append(kw)
    
    print(f'Keywords found in content: {found}')
    print(f'Content preview: {content[:300]}...')
    print('-' * 50)

conn.close()
