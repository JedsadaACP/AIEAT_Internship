"""
Verify scoring and translation data quality.
"""
import sqlite3
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('data/aieat_news.db')
conn.row_factory = sqlite3.Row

print("=" * 60)
print("SCORING DATA VERIFICATION")
print("=" * 60)

# Get scored articles
cursor = conn.execute("""
    SELECT m.article_id, m.headline, m.ai_score, m.published_at, m.author_name
    FROM articles_meta m
    WHERE m.ai_score > 0
    ORDER BY m.ai_score DESC
""")
scored = list(cursor)

print(f"\nScored articles: {len(scored)}")
for row in scored:
    print(f"\n  ID: {row['article_id']}")
    print(f"  Headline: {row['headline'][:60]}...")
    print(f"  Score: {row['ai_score']}/7")
    print(f"  Date: {row['published_at']}")
    print(f"  Author: {row['author_name'][:40] if row['author_name'] else 'N/A'}...")

print("\n" + "=" * 60)
print("TRANSLATION DATA VERIFICATION")
print("=" * 60)

# Get translated articles
cursor = conn.execute("""
    SELECT m.article_id, m.headline, m.ai_score, c.thai_content
    FROM articles_meta m
    JOIN article_content c ON m.article_id = c.article_id
    WHERE c.thai_content IS NOT NULL
""")
translated = list(cursor)

print(f"\nTranslated articles: {len(translated)}")
for row in translated:
    print(f"\n  ID: {row['article_id']}")
    print(f"  Original: {row['headline'][:50]}...")
    print(f"  Score: {row['ai_score']}/7")
    thai = row['thai_content']
    print(f"  Thai content length: {len(thai)} chars")
    
    # Check if Thai content has expected sections
    has_headline = 'หัวข้อ:' in thai
    has_lead = 'นำเรื่อง:' in thai
    has_analysis = 'วิเคราะห์' in thai
    
    print(f"  Has Thai headline: {'Yes' if has_headline else 'NO!'}")
    print(f"  Has Thai lead: {'Yes' if has_lead else 'NO!'}")
    print(f"  Has Thai analysis: {'Yes' if has_analysis else 'NO!'}")
    
    # Show first 200 chars of Thai content
    print(f"  Preview: {thai[:200]}...")

print("\n" + "=" * 60)
print("DATA QUALITY SUMMARY")
print("=" * 60)

# Check for issues
issues = []

# Check if any scores are out of range
cursor = conn.execute("SELECT COUNT(*) FROM articles_meta WHERE ai_score < 0 OR ai_score > 7")
bad_scores = cursor.fetchone()[0]
if bad_scores > 0:
    issues.append(f"  - {bad_scores} articles have invalid score (not 0-7)")

# Check if translations are too short
cursor = conn.execute("SELECT COUNT(*) FROM article_content WHERE thai_content IS NOT NULL AND LENGTH(thai_content) < 100")
short_trans = cursor.fetchone()[0]
if short_trans > 0:
    issues.append(f"  - {short_trans} translations are too short (<100 chars)")

if issues:
    print("\nISSUES FOUND:")
    for issue in issues:
        print(issue)
else:
    print("\nNo issues found! Data looks good.")

conn.close()
