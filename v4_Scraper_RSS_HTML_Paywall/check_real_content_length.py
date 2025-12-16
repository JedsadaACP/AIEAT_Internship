import pandas as pd
import re

# Load diagnostic data
df = pd.read_csv('diagnostic_all_articles.csv')

print('=' * 90)
print('HOMEPAGE vs RSS - REAL CONTENT LENGTH (Whitespace Removed)')
print('=' * 90)

# Compare Homepage vs RSS
for method in ['homepage', 'rss']:
    method_df = df[df['method'] == method].copy()
    
    print(f'\n{method.upper()} METHOD:')
    print('-' * 90)
    
    # Calculate content length with whitespace
    method_df['total_chars'] = method_df['full_content'].apply(lambda x: len(str(x)))
    
    # Calculate meaningful content (remove whitespace, newlines, tabs)
    method_df['meaningful_chars'] = method_df['full_content'].apply(
        lambda x: len(re.sub(r'\s+', '', str(x)))
    )
    
    # Calculate word count
    method_df['words'] = method_df['full_content'].apply(
        lambda x: len(str(x).split())
    )
    
    print(f'\nWith Whitespace:')
    print(f'  Avg total chars: {method_df["total_chars"].mean():.0f}')
    print(f'  Min: {method_df["total_chars"].min()}, Max: {method_df["total_chars"].max()}')
    
    print(f'\nWithout Whitespace (Meaningful):')
    print(f'  Avg meaningful chars: {method_df["meaningful_chars"].mean():.0f}')
    print(f'  Min: {method_df["meaningful_chars"].min()}, Max: {method_df["meaningful_chars"].max()}')
    
    print(f'\nWord Count:')
    print(f'  Avg words: {method_df["words"].mean():.0f}')
    print(f'  Min: {method_df["words"].min()}, Max: {method_df["words"].max()}')
    
    print(f'\nWhitespace Ratio:')
    avg_whitespace_ratio = (1 - method_df['meaningful_chars'].mean() / method_df['total_chars'].mean()) * 100
    print(f'  {avg_whitespace_ratio:.1f}% is whitespace/formatting')
    
    # Show sample
    print(f'\nSample Article from {method.upper()}:')
    sample = method_df.iloc[0]
    print(f'  Headline: {sample["headline"][:60]}')
    print(f'  Total chars (with whitespace): {sample["total_chars"]}')
    print(f'  Meaningful chars (no whitespace): {sample["meaningful_chars"]}')
    print(f'  Words: {sample["words"]}')
    print(f'  Actual ratio: {(1 - sample["meaningful_chars"] / sample["total_chars"]) * 100:.1f}% whitespace')

# Compare all methods
print('\n' + '=' * 90)
print('COMPARISON - ALL METHODS')
print('=' * 90)

all_methods = df['method'].unique()
results = []

for method in sorted(all_methods):
    method_df = df[df['method'] == method].copy()
    method_df['meaningful_chars'] = method_df['full_content'].apply(
        lambda x: len(re.sub(r'\s+', '', str(x)))
    )
    method_df['words'] = method_df['full_content'].apply(
        lambda x: len(str(x).split())
    )
    
    results.append({
        'method': method.upper(),
        'articles': len(method_df),
        'avg_meaningful': method_df['meaningful_chars'].mean(),
        'avg_words': method_df['words'].mean(),
    })

results_df = pd.DataFrame(results).sort_values('avg_meaningful', ascending=False)

print('\nRanked by Meaningful Content Length:')
print(f'\n{"Method":<12} | {"Articles":>8} | {"Avg Chars":>10} | {"Avg Words":>10}')
print('-' * 50)
for _, row in results_df.iterrows():
    print(f'{row["method"]:<12} | {row["articles"]:>8} | {row["avg_meaningful"]:>10.0f} | {row["avg_words"]:>10.0f}')

print('\n' + '=' * 90)
print('CONCLUSION')
print('=' * 90)
print('\nHomepage articles might appear longer due to formatting,')
print('but meaningful content (actual words) is what matters.')
print('\nCheck the actual word count instead of total character count!')
