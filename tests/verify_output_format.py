"""
Verify Score and Translation output format in DB.
"""
import sys
import os
import io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3

conn = sqlite3.connect('data/aieat_news.db')
conn.row_factory = sqlite3.Row

print("=" * 70)
print("SCORING OUTPUT VERIFICATION")
print("=" * 70)

# Get scored articles
cursor = conn.execute("""
    SELECT m.article_id, m.headline, m.ai_score, m.published_at, m.status_id
    FROM articles_meta m
    WHERE m.ai_score > 0
    ORDER BY m.ai_score DESC
    LIMIT 5
""")

for row in cursor:
    print(f"\nArticle ID: {row['article_id']}")
    print(f"  Headline: {row['headline'][:60]}...")
    print(f"  Score: {row['ai_score']}")
    print(f"  Date: {row['published_at']}")
    print(f"  Status ID: {row['status_id']}")

print("\n" + "=" * 70)
print("TRANSLATION OUTPUT VERIFICATION")
print("=" * 70)

# Get translated articles
cursor = conn.execute("""
    SELECT m.article_id, m.headline, m.ai_score, c.thai_content, c.original_content
    FROM articles_meta m
    JOIN article_content c ON m.article_id = c.article_id
    WHERE c.thai_content IS NOT NULL AND c.thai_content != ''
""")

for row in cursor:
    print(f"\nArticle ID: {row['article_id']}")
    print(f"  Original: {row['headline'][:50]}...")
    print(f"  Score: {row['ai_score']}")
    print(f"  Thai Length: {len(row['thai_content'])} chars")
    print(f"  Original Length: {len(row['original_content'])} chars")
    
    thai = row['thai_content']
    
    # Check format
    print(f"\n  === THAI CONTENT STRUCTURE ===")
    has_headline = 'หัวข้อ:' in thai or 'หัวข้อ' in thai
    has_lead = 'นำเรื่อง:' in thai or 'Lead:' in thai
    has_body = len(thai) > 500
    has_analysis = 'วิเคราะห์' in thai or 'Analysis' in thai
    
    print(f"  Has headline section: {has_headline}")
    print(f"  Has lead section: {has_lead}")
    print(f"  Has body (>500 chars): {has_body}")
    print(f"  Has analysis section: {has_analysis}")
    
    # Show first 500 chars
    print(f"\n  === PREVIEW (first 500 chars) ===")
    print(f"  {thai[:500]}...")

print("\n" + "=" * 70)
print("FORMAT ANALYSIS")
print("=" * 70)

# Check overall data quality
cursor = conn.execute("SELECT COUNT(*) FROM articles_meta WHERE ai_score > 0")
scored_count = cursor.fetchone()[0]

cursor = conn.execute("SELECT COUNT(*) FROM article_content WHERE thai_content IS NOT NULL AND thai_content != ''")
translated_count = cursor.fetchone()[0]

cursor = conn.execute("SELECT AVG(ai_score) FROM articles_meta WHERE ai_score > 0")
avg_score = cursor.fetchone()[0]

print(f"Scored articles: {scored_count}")
print(f"Translated articles: {translated_count}")
print(f"Average score: {avg_score:.2f}")

conn.close()
