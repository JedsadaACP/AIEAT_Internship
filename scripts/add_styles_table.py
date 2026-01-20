"""
Add styles table to database for Style page functionality.
"""
import sqlite3

conn = sqlite3.connect('data/aieat_news.db')

# Create styles table
conn.execute("""
CREATE TABLE IF NOT EXISTS styles (
    style_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    output_type TEXT DEFAULT 'Translation & Rewrite',
    persona TEXT DEFAULT '',
    structure_headline TEXT DEFAULT '',
    structure_lead TEXT DEFAULT '',
    structure_body TEXT DEFAULT '',
    structure_analysis TEXT DEFAULT '',
    content_order TEXT DEFAULT 'headline,lead,body,analysis',
    is_default INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert default styles
default_styles = [
    ('Web Article', 'Translation & Rewrite', 'Professional journalist', 'Clear headline', 'Summary lead', 'Detailed body', 'Brief analysis', 'headline,lead,body,analysis', 1),
    ('Facebook Post', 'Summary Only', 'Casual social media manager', 'Catchy hook', 'Key points', 'Short engaging text', 'Call to action', 'headline,body,analysis', 0),
    ('Executive Summary', 'Translation & Rewrite', 'Business analyst', 'Key finding', 'Business impact', 'Detailed insights', 'Recommendations', 'headline,lead,body,analysis', 0),
]

for style in default_styles:
    try:
        conn.execute("""
            INSERT INTO styles (name, output_type, persona, structure_headline, structure_lead, structure_body, structure_analysis, content_order, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, style)
    except sqlite3.IntegrityError:
        print(f"Style '{style[0]}' already exists, skipping")

conn.commit()
print("Styles table created with 3 default styles")
conn.close()
