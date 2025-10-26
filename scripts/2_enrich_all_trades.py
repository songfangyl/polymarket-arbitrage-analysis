#!/usr/bin/env python3
"""
Enrich All Trade Files with Market Metadata

This script:
1. Loads all trade CSV files from ../joined_data/
2. Enriches each with metadata (condition_id, question, outcome, category)
3. Saves enriched files to ./data/enriched/

Output: One enriched CSV per date with all metadata columns added
"""
import pandas as pd
import glob
import os
from pathlib import Path

print("="*70)
print("ENRICHING ALL TRADE FILES WITH MARKET METADATA")
print("="*70)
print()

# Configuration
TRADE_DIR = '../joined_data'
LOOKUP_FILE = 'data/token_lookup.csv'
OUTPUT_DIR = 'data/enriched'

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 1: Load token lookup
print("Step 1: Loading token lookup...")
try:
    lookup = pd.read_csv(LOOKUP_FILE, index_col='token_id', dtype={'token_id': str})
    print(f"   ✓ Loaded {len(lookup):,} token mappings")
except FileNotFoundError:
    print(f"   ✗ Error: {LOOKUP_FILE} not found!")
    print("   Run: uv run --with pandas create_token_lookup.py")
    exit(1)
print()

# Step 2: Find all trade files
print("Step 2: Finding trade files...")
trade_files = sorted(glob.glob(f'{TRADE_DIR}/trades-joined-*.csv'))
print(f"   ✓ Found {len(trade_files)} files")
print(f"   Date range: {trade_files[0].split('/')[-1]} to {trade_files[-1].split('/')[-1]}")
print()

# Step 3: Process each file
print("Step 3: Processing files...")
print("-" * 70)

stats = {
    'total_trades': 0,
    'matched_trades': 0,
    'unique_markets': set(),
    'unique_tokens': set()
}

for i, file_path in enumerate(trade_files, 1):
    filename = file_path.split('/')[-1]
    date = filename.replace('trades-joined-', '').replace('.csv', '')

    print(f"\n[{i}/{len(trade_files)}] {date}")

    # Load trades
    trades = pd.read_csv(file_path, dtype={'market_token_id': str})
    print(f"   Loading: {len(trades):,} trades", end='')

    # Merge with metadata
    enriched = trades.merge(
        lookup,
        left_on='market_token_id',
        right_index=True,
        how='left',
        suffixes=('_original', '_meta')
    )

    # Clean up: Use metadata columns, drop originals if they exist
    metadata_cols = ['condition_id', 'question', 'outcome', 'event_title', 'category', 'end_date']

    for col in metadata_cols:
        if f'{col}_meta' in enriched.columns:
            enriched[col] = enriched[f'{col}_meta']
            # Remove both _original and _meta versions
            enriched = enriched.drop(columns=[c for c in [f'{col}_original', f'{col}_meta'] if c in enriched.columns], errors='ignore')
        elif f'{col}_original' in enriched.columns:
            # If only _original exists, rename it
            enriched[col] = enriched[f'{col}_original']
            enriched = enriched.drop(columns=[f'{col}_original'], errors='ignore')

    # Count matches
    matched = enriched['condition_id'].notna().sum()
    match_rate = 100 * matched / len(trades)

    # Update stats
    stats['total_trades'] += len(trades)
    stats['matched_trades'] += matched
    stats['unique_markets'].update(enriched['condition_id'].dropna().unique())
    stats['unique_tokens'].update(enriched['market_token_id'].dropna().unique())

    print(f" → {matched:,} matched ({match_rate:.1f}%)")

    # Save enriched file
    output_file = f'{OUTPUT_DIR}/enriched-{date}.csv'
    enriched.to_csv(output_file, index=False)

    # Show file size
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"   Saved: {output_file} ({file_size_mb:.1f} MB)")

print()
print("-" * 70)
print()

# Step 4: Summary
print("="*70)
print("ENRICHMENT COMPLETE")
print("="*70)
print()
print(f"Processed: {len(trade_files)} files")
print(f"Total trades: {stats['total_trades']:,}")
print(f"Matched trades: {stats['matched_trades']:,} ({100*stats['matched_trades']/stats['total_trades']:.2f}%)")
print(f"Unique markets: {len(stats['unique_markets']):,}")
print(f"Unique tokens: {len(stats['unique_tokens']):,}")
print()

print(f"Output directory: {OUTPUT_DIR}/")
print(f"Files: enriched-2025-04-08.csv through enriched-2025-09-21.csv")
print()

# Show sample columns
sample_file = f'{OUTPUT_DIR}/enriched-{trade_files[0].split("/")[-1].replace("trades-joined-", "")}'
sample = pd.read_csv(sample_file, nrows=1)

print("Columns in enriched files:")
original_cols = ['trade_id', 'timestamp', 'price', 'volume_usdc', 'side', 'market_token_id']
metadata_cols = ['condition_id', 'question', 'outcome', 'category', 'event_title', 'end_date']

print("\n  Original columns:")
for col in original_cols:
    if col in sample.columns:
        print(f"    ✓ {col}")

print("\n  NEW metadata columns:")
for col in metadata_cols:
    if col in sample.columns:
        print(f"    ✓ {col}")

print("\n  ...and", len(sample.columns) - len(original_cols) - len(metadata_cols), "other columns")
print()

print("="*70)
print("✅ Ready to use!")
print("="*70)
print()
print("Example usage:")
print("  import pandas as pd")
print("  df = pd.read_csv('data/enriched/enriched-2025-04-08.csv')")
print("  print(df[['question', 'outcome', 'category', 'volume_usdc']].head())")
print()
