"""
Generate Checklist Report from Test Results

Runs all tests, then maps results back to the original
Testing_Checklists CSV format with EVERY row filled in.
No row is left blank.
"""
import subprocess
import sys
import os
import csv
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


# ============================================================
# COMPLETE MAPPING: Checklist row number -> test function name
# Every single row (1-210) is accounted for.
#   - String value = test function name to look for
#   - "N/A"        = UI rendering, no logic
#   - "SKIP:..."   = known skip with reason
# ============================================================
ITEM_MAP = {
    # === Database (1-34) ===
    1:  'test_insert_full_article',
    2:  'test_get_article_by_id',
    3:  'test_get_new_articles',
    4:  'test_update_article_score',
    5:  'test_update_thai_content',
    6:  'test_get_article_count',
    7:  'test_get_filtered_articles',
    8:  'test_get_all_sources',
    9:  'test_insert_source',
    10: 'test_delete_source',
    11: 'test_get_or_create_source',
    12: 'test_get_source_by_url',
    13: 'test_get_keywords',
    14: 'test_add_keyword',
    15: 'test_delete_keyword',
    16: 'test_get_domains',
    17: 'test_add_domain',
    18: 'test_delete_domain',
    19: 'test_get_system_profile',
    20: 'test_update_system_profile',
    21: 'test_add_style',
    22: 'test_get_style',
    23: 'test_update_style',
    24: 'test_delete_style',
    25: 'test_set_active_style',
    26: 'test_get_active_style',
    27: 'test_get_styles',
    28: 'test_update_article_status',
    29: 'test_get_articles_by_source',
    30: 'test_get_article_by_url',
    31: 'test_insert_article_minimal',
    32: 'test_get_source_count',
    33: 'test_get_article_tags',
    34: 'test_search_articles',

    # === Scraper (35-50) ===
    35: 'SKIP:Requires async HTTP mocking',
    36: 'test_discover_source',
    37: 'test_discover_articles',
    38: 'SKIP:Requires trafilatura + async',
    39: 'SKIP:Requires async HTTP',
    40: 'SKIP:Requires async HTTP',
    41: 'SKIP:Requires async HTTP',
    42: 'test_discover_homepage',
    43: 'test_check_paywall',
    44: 'test_match_keywords',
    45: 'test_check_same_domain',
    46: 'test_load_config',
    47: 'test_clean_text',
    48: 'test_clean_author',
    49: 'test_parse_date',
    50: 'test_check_too_old',

    # === AI Engine (51-57) ===
    51: 'test_process_new_articles',
    52: 'test_score_article',
    53: 'test_check_freshness',
    54: 'test_translate_article',
    55: 'test_build_messages',
    56: 'test_load_model',
    57: 'test_unload_model',

    # === Ollama (58-63) ===
    58: 'test_check_ollama_running',
    59: 'test_check_model_available',
    60: 'test_generate_text',
    61: 'test_ollama_score_article',
    62: 'test_ollama_translate',
    63: 'test_get_controller',

    # === Prompt Builder (64-66) ===
    64: 'test_build_translation_prompt',
    65: 'test_parse_translation_response',
    66: 'test_parse_markdown_format',

    # === Backend API (67-97) ===
    67: 'test_preload_model',
    68: 'test_reload_model',
    69: 'test_unload_model',
    70: 'test_get_config',
    71: 'test_get_keywords',
    72: 'test_get_domains',
    73: 'test_update_config',
    74: 'test_add_keyword',
    75: 'test_add_domain',
    76: 'test_remove_keyword',
    77: 'test_delete_keyword',
    78: 'test_delete_domain',
    79: 'test_get_styles',
    80: 'test_get_style',
    81: 'test_add_style',
    82: 'test_update_style',
    83: 'test_delete_style',
    84: 'test_set_active_style',
    85: 'test_get_articles',
    86: 'test_get_article_detail',
    87: 'test_get_article_count',
    88: 'test_get_sources',
    89: 'test_get_source_count',
    90: 'test_add_source',
    91: 'test_run_scraper',
    92: 'test_score_article',
    93: 'test_translate_article',
    94: 'test_batch_process_articles',
    95: 'test_get_dashboard_stats',
    96: 'test_get_stats',
    97: 'N/A',  # Get dashboard stats (duplicate of 95)

    # === Config UI (98-129) ===
    98:  'test_config_build',             # Build page
    99:  'N/A',                            # Build header
    100: 'N/A',                            # Build automation section
    101: 'N/A',                            # Build org section
    102: 'N/A',                            # Build scoring section
    103: 'N/A',                            # Build sources section
    104: 'N/A',                            # Build threshold section
    105: 'N/A',                            # Build save button
    106: 'test_config_refresh_state',      # Refresh state
    107: 'test_config_load_models',        # Load models
    108: 'test_config_update_threshold_display', # Update threshold display
    109: 'N/A',                            # Create domain chip
    110: 'test_config_add_domain',         # Add domain (Config UI)
    111: 'test_config_remove_domain',      # Remove domain (Config UI)
    112: 'N/A',                            # Create keyword chip
    113: 'test_config_add_keyword',        # Add keyword
    114: 'test_config_remove_keyword',     # Remove keyword
    115: 'test_config_add_source',         # Add source
    116: 'test_config_delete_source',      # Delete source
    117: 'test_config_filter_sources',     # Filter sources
    118: 'test_config_import_sources_file',  # Import sources file (FIXED)
    119: 'test_config_on_import_result',  # On import result (FIXED)
    120: 'N/A',                            # Rebuild sources list
    121: 'N/A',                            # Create source item
    122: 'test_config_on_date_radio_change', # On date radio change
    123: 'test_config_on_model_change',    # On model change
    124: 'test_config_show_save_confirmation', # Show save confirmation
    125: 'test_config_save_config',        # Save config (DUPLICATE - same as item 104)
    126: 'N/A',                            # Create tag chip
    127: 'N/A',                            # Refresh page
    128: 'N/A',                            # Show snackbar
    129: 'N/A',                            # Build threshold wrapper

    # === Dashboard UI (130-181) ===
    130: 'test_dashboard_build',           # Build page
    131: 'N/A',                            # Build header
    132: 'N/A',                            # Build top bar
    133: 'N/A',                            # Build filter panel
    134: 'N/A',                            # Build progress section
    135: 'N/A',                            # Build news table
    136: 'N/A',                            # Build bottom controls
    137: 'N/A',                            # Build start button
    138: 'test_dashboard_refresh_state',   # Refresh state
    139: 'test_dashboard_load_models',     # Load available models
    140: 'test_dashboard_get_filtered_articles',  # Get filtered articles
    141: 'NOT_TESTED:Lifecycle issue',     # Refresh table
    142: 'test_dashboard_open_source_filter_dialog', # Open source filter dialog
    143: 'test_dashboard_create_keyword_dropdown', # Create keyword dropdown
    144: 'test_dashboard_toggle_filter_panel',    # Toggle filter panel
    145: 'test_dashboard_apply_filters',   # Apply filters
    146: 'test_dashboard_reset_filters',   # Reset filters
    147: 'test_dashboard_on_date_filter_change', # On date filter change
    148: 'test_dashboard_on_score_filter_change', # On score filter change
    149: 'NOT_TESTED:No test written',     # On source filter change
    150: 'NOT_TESTED:No test written',     # On keyword filter change
    151: 'test_dashboard_open_batch_dialog',      # Open batch dialog
    152: 'test_dashboard_close_batch_dialog',     # Close batch dialog
    153: 'test_dashboard_toggle_batch_process',   # Toggle batch process
    154: 'NOT_TESTED:Requires async',      # Process batch async
    155: 'N/A',                            # Reset batch button
    156: 'test_dashboard_sort_by',         # Sort by column
    157: 'N/A',                            # Get sort icon
    158: 'test_dashboard_set_page_size',   # Set page size
    159: 'test_dashboard_goto_page',       # Goto page
    160: 'test_dashboard_previous_page',   # Previous page
    161: 'test_dashboard_next_page',       # Next page
    162: 'NOT_TESTED:No test written',     # Get articles for page
    163: 'test_dashboard_on_start_click',  # On start click
    164: 'NOT_TESTED:Requires async',      # Start scraper
    165: 'NOT_TESTED:Requires async',      # Run scraper async
    166: 'NOT_TESTED:Requires async',      # Run scraper sync logic
    167: 'NOT_TESTED:Lifecycle issue',     # On scraper complete
    168: 'NOT_TESTED:Lifecycle issue',     # On scraper error
    169: 'NOT_TESTED:Lifecycle issue',     # Stop scraper
    170: 'NOT_TESTED:Lifecycle issue',     # Update status
    171: 'test_dashboard_on_auto_score_change',   # On auto score change
    172: 'test_dashboard_on_auto_translate_change',  # On auto translate change
    173: 'test_dashboard_on_model_change', # On model change
    174: 'test_dashboard_on_search',       # On search
    175: 'test_dashboard_edit_score',      # Edit score
    176: 'test_dashboard_export_csv',      # Export CSV
    177: 'test_dashboard_format_date',     # Format date
    178: 'N/A',                            # Build keyword chips
    179: 'N/A',                            # Show snackbar
    180: 'test_dashboard_safe_update',     # Safe update
    181: 'test_dashboard_parse_date_for_sort', # Parse date for sort

    # === Detail UI (182-195) ===
    182: 'test_detail_build',              # Build page
    183: 'N/A',                            # Build layout controls
    184: 'N/A',                            # Build header
    185: 'N/A',                            # Build metadata
    186: 'N/A',                            # Build content area
    187: 'test_detail_translate_article',  # Translate article
    188: 'NOT_TESTED:Requires async',      # Run translation async
    189: 'test_detail_regenerate_score',   # Regenerate score
    190: 'test_detail_export_source',      # Export source
    191: 'test_detail_export_output',      # Export output
    192: 'test_detail_save_file',          # Save file
    193: 'test_detail_copy_to_clipboard',  # Copy to clipboard
    194: 'test_detail_format_date',        # Format date
    195: 'N/A',                            # Show snackbar

    # === Style UI (196-207) ===
    196: 'test_style_build',               # Build page
    197: 'N/A',                            # Build header
    198: 'test_style_refresh_state',       # Refresh state
    199: 'test_style_load_styles_data',    # Load styles data
    200: 'test_style_update_form_values',  # Update form values
    201: 'N/A',                            # Rebuild list items
    202: 'test_style_handle_select',       # Handle select
    203: 'test_style_add_style',           # Add style
    204: 'test_style_delete_style',        # Delete style
    205: 'test_style_save_style',          # Save style
    206: 'test_style_set_active',          # Set active
    207: 'N/A',                            # Show snackbar

    # === About UI (208-210) ===
    208: 'test_about_build',               # Build page
    209: 'test_about_build_layout',        # Build layout
    210: 'test_about_info_row',            # Info row
}


def load_original_checklist():
    """Load the original CSV as template."""
    path = os.path.join(project_root, "Testing_Checklists - Unit Testing (1).csv")
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for i, row in enumerate(reader, start=1):
            if len(row) >= 2:
                rows.append({
                    'item': i,
                    'module': row[0].strip() if len(row) > 0 else '',
                    'function': row[1].strip() if len(row) > 1 else '',
                    'input': row[2].strip() if len(row) > 2 else '',
                    'expected': row[3].strip() if len(row) > 3 else '',
                    'output': row[4].strip() if len(row) > 4 else '',
                    'note': row[6].strip() if len(row) > 6 else '',
                })
    # Debug: print first item to verify numbering
    if rows:
        print(f"DEBUG: First checklist item loaded: {rows[0]}")
    return rows


def run_tests():
    """Run pytest and return stdout."""
    print("Running pytest...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration/",
         "-v", "--tb=line", "--no-header", "--disable-warnings"],
        capture_output=True, text=True, cwd=project_root
    )
    return result.stdout


def parse_results(stdout):
    """Parse pytest output -> dict of test_name -> PASSED/FAILED/SKIPPED."""
    results = {}
    for line in stdout.split('\n'):
        if '::' not in line:
            continue
        for status in ('PASSED', 'FAILED', 'SKIPPED'):
            if status in line:
                name = line.split('::')[-1].split()[0].strip()
                results[name] = status
                break
    return results


def generate_csv(checklist, test_results):
    """Generate output CSV — every row gets a status, no blanks."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = os.path.join(project_root, f"test_results_{timestamp}.csv")

    stats = {'PASSED': 0, 'FAILED': 0, 'SKIPPED': 0, 'N/A': 0,
             'NOT_TESTED': 0, 'CODE_BUG': 0}

    with open(outpath, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Module', 'Function', 'Input', 'Expected Result',
                     'Output', 'Testing Result', 'Note'])

        for row in checklist:
            item = row['item']
            mapping = ITEM_MAP.get(item, 'NOT_TESTED:No mapping')

            if mapping == 'N/A':
                status = 'N/A'
                note = 'UI rendering - no logic'
            elif mapping.startswith('SKIP:'):
                status = 'SKIPPED'
                note = mapping[5:]
            elif mapping.startswith('NOT_TESTED:'):
                status = 'NOT_TESTED'
                note = mapping[11:]
            elif mapping.startswith('CODE_BUG:'):
                status = 'CODE_BUG'
                note = mapping[9:]
            else:
                # It's a test function name — look up result
                if mapping in test_results:
                    status = test_results[mapping]
                    note = row['note']
                else:
                    status = 'NOT_TESTED'
                    note = f'Test "{mapping}" not found in results'

            # Keep original note if it has useful info
            if row['note'] and status not in ('N/A',) and not note:
                note = row['note']

            stats[status] = stats.get(status, 0) + 1

            w.writerow([
                row['module'], row['function'], row['input'],
                row['expected'], row['output'], status, note
            ])

    return outpath, stats


def main():
    print("=" * 70)
    print("AIEAT TEST RESULTS -> CHECKLIST CSV")
    print("=" * 70)

    checklist = load_original_checklist()
    print(f"Loaded {len(checklist)} checklist items")

    stdout = run_tests()
    results = parse_results(stdout)
    print(f"Captured {len(results)} test results")
    print()

    outpath, stats = generate_csv(checklist, results)

    testable = stats['PASSED'] + stats['FAILED'] + stats['SKIPPED']

    print("-" * 70)
    print(f"  PASSED:      {stats['PASSED']:4d}")
    print(f"  FAILED:      {stats['FAILED']:4d}")
    print(f"  SKIPPED:     {stats['SKIPPED']:4d}")
    print(f"  CODE_BUG:    {stats['CODE_BUG']:4d}")
    print(f"  NOT_TESTED:  {stats['NOT_TESTED']:4d}")
    print(f"  N/A:         {stats['N/A']:4d}  (UI rendering)")
    print(f"  ---")
    print(f"  Total:       {len(checklist):4d}")
    if testable > 0:
        print(f"  Pass Rate:   {stats['PASSED']/testable*100:.1f}%  (of ran tests)")
    print("-" * 70)
    print(f"\nSaved: {outpath}")
    print("Format matches: Testing_Checklists - Unit Testing (1).csv")
    print("=" * 70)


if __name__ == "__main__":
    main()
