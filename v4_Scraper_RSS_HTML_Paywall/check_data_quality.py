import pandas as pd
import csv

# Load the diagnostic data
df = pd.read_csv('diagnostic_all_articles.csv')

print('=' * 70)
print('DATA QUALITY CHECK - diagnostic_all_articles.csv')
print('=' * 70)

# 1. Basic stats
print(f'\n1. BASIC STATS:')
print(f'   Total articles: {len(df)}')
print(f'   Columns: {list(df.columns)}')
print(f'   Unique sources: {df["source"].nunique()}')

# 2. Check for missing values
print(f'\n2. MISSING VALUES:')
missing_found = False
for col in df.columns:
    missing = df[col].isna().sum()
    empty = (df[col] == '').sum() if df[col].dtype == 'object' else 0
    if missing > 0 or empty > 0:
        print(f'   {col}: {missing} null, {empty} empty')
        missing_found = True
if not missing_found:
    print('   No missing values found!')

# 3. Check content lengths
print(f'\n3. CONTENT LENGTH ANALYSIS:')
df['content_len'] = df['full_content'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
print(f'   Min length: {df["content_len"].min()} chars')
print(f'   Max length: {df["content_len"].max()} chars')
print(f'   Avg length: {df["content_len"].mean():.0f} chars')
short = (df['content_len'] < 100).sum()
print(f'   Articles < 100 chars: {short}')

# 4. Check headline quality
print(f'\n4. HEADLINE QUALITY:')
df['headline_len'] = df['headline'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
print(f'   Min headline: {df["headline_len"].min()} chars')
print(f'   Max headline: {df["headline_len"].max()} chars')
short_headlines = (df['headline_len'] < 20).sum()
print(f'   Headlines < 20 chars: {short_headlines}')

# 5. Check for junk headlines
print(f'\n5. POTENTIAL JUNK HEADLINES:')
junk_patterns = ['video', 'menu', 'subscribe', 'login', 'navigation', 'cookie']
junk_found = False
for pattern in junk_patterns:
    matches = df[df['headline'].str.lower().str.contains(pattern, na=False)]
    if len(matches) > 0:
        junk_found = True
        print(f'   Contains "{pattern}": {len(matches)} articles')
        for h in matches['headline'].head(2).tolist():
            print(f'      - {h[:60]}...')
if not junk_found:
    print('   No obvious junk headlines found!')

# 6. Check method distribution
print(f'\n6. METHOD DISTRIBUTION:')
for method, count in df['method'].value_counts().items():
    pct = count / len(df) * 100
    print(f'   {method}: {count} ({pct:.1f}%)')

# 7. Check status distribution
print(f'\n7. STATUS DISTRIBUTION:')
for status, count in df['status'].value_counts().items():
    pct = count / len(df) * 100
    print(f'   {status}: {count} ({pct:.1f}%)')

# 8. Sample headlines by source
print(f'\n8. SAMPLE HEADLINES BY SOURCE (first 10 sources):')
for source in df['source'].unique()[:10]:
    sample = df[df['source'] == source]['headline'].iloc[0]
    print(f'   {source}: {sample[:55]}...')

# 9. Check for duplicate URLs
print(f'\n9. DUPLICATE CHECK:')
dup_urls = df[df.duplicated(subset=['url'], keep=False)]
print(f'   Duplicate URLs: {len(dup_urls)} articles')
if len(dup_urls) > 0:
    print('   Sample duplicates:')
    for url in dup_urls['url'].unique()[:3]:
        count = len(df[df['url'] == url])
        print(f'      - {url[:50]}... ({count}x)')

# 10. Check URL validity
print(f'\n10. URL VALIDITY:')
invalid_urls = df[~df['url'].str.startswith('http', na=False)]
print(f'   Invalid URLs (not starting with http): {len(invalid_urls)}')

# 11. Check for encoding issues
print(f'\n11. ENCODING ISSUES:')
encoding_issues = df[df['headline'].str.contains('â€', na=False) | df['full_content'].str.contains('â€', na=False)]
print(f'   Articles with potential encoding issues: {len(encoding_issues)}')
if len(encoding_issues) > 0:
    print('   (This is UTF-8 decoded as Windows-1252, shows as â€™ instead of apostrophe)')

print('\n' + '=' * 70)
print('SUMMARY:')
print('=' * 70)
print(f'✅ Total articles: {len(df)}')
print(f'✅ Unique sources: {df["source"].nunique()}')
print(f'✅ All 12 columns present: {len(df.columns) == 12}')
print(f'{"✅" if short == 0 else "⚠️"} No short content (<100 chars): {short == 0}')
print(f'{"✅" if len(dup_urls) == 0 else "⚠️"} No duplicate URLs: {len(dup_urls) == 0}')
print(f'{"✅" if len(invalid_urls) == 0 else "⚠️"} All URLs valid: {len(invalid_urls) == 0}')
print(f'{"⚠️" if len(encoding_issues) > 0 else "✅"} Encoding issues: {len(encoding_issues)} articles')
print('=' * 70)
