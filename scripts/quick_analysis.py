#!/usr/bin/env python3
"""
Quick Analysis: Explore trade data with market metadata

This script:
1. Loads one day of trade data
2. Enriches it with market metadata
3. Shows category breakdown, top markets, and sample data
"""
import pandas as pd
import sys

print("="*70)
print("QUICK ANALYSIS: Trade Data with Market Metadata")
print("="*70)
print()

# Configuration
TRADE_FILE = '../joined_data/trades-joined-2025-04-08.csv'
LOOKUP_FILE = 'data/token_lookup.csv'

# Step 1: Load token lookup
print("Step 1: Loading token lookup...")
try:
    lookup = pd.read_csv(LOOKUP_FILE, index_col='token_id', dtype={'token_id': str})
    print(f"   ✓ Loaded {len(lookup):,} token mappings")
except FileNotFoundError:
    print(f"   ✗ Error: {LOOKUP_FILE} not found!")
    print("   Run: uv run --with pandas create_token_lookup.py")
    sys.exit(1)
print()

# Step 2: Load trade data
print("Step 2: Loading trade data...")
try:
    trades = pd.read_csv(TRADE_FILE, dtype={'market_token_id': str})
    print(f"   ✓ Loaded {len(trades):,} trades from {TRADE_FILE.split('/')[-1]}")
    print(f"   Date range: {pd.to_datetime(trades['timestamp'], unit='s').min().date()} to {pd.to_datetime(trades['timestamp'], unit='s').max().date()}")
    print(f"   Total volume: ${trades['volume_usdc'].sum():,.2f}")
except FileNotFoundError:
    print(f"   ✗ Error: {TRADE_FILE} not found!")
    sys.exit(1)
print()

# Step 3: Merge with metadata
print("Step 3: Enriching with metadata...")
enriched = trades.merge(
    lookup,
    left_on='market_token_id',
    right_index=True,
    how='left',
    suffixes=('_trade', '_meta')
)

# Use metadata columns (not the ones from trades which may be incomplete)
if 'category_meta' in enriched.columns:
    enriched['category'] = enriched['category_meta']
if 'outcome_meta' in enriched.columns:
    enriched['outcome'] = enriched['outcome_meta']
if 'end_date_meta' in enriched.columns:
    enriched['end_date'] = enriched['end_date_meta']

# Drop duplicate columns
enriched = enriched.drop(columns=[col for col in enriched.columns if col.endswith('_trade') or col.endswith('_meta')], errors='ignore')

matched = enriched['question'].notna().sum()
print(f"   ✓ Matched {matched:,} / {len(trades):,} trades ({100*matched/len(trades):.1f}%)")
print()

# Step 4: Category breakdown
print("="*70)
print("CATEGORY BREAKDOWN")
print("="*70)

category_stats = enriched.groupby('category').agg({
    'volume_usdc': 'sum',
    'trade_id': 'count',
    'market_token_id': 'nunique'
}).round(2)

category_stats.columns = ['Total Volume ($)', 'Num Trades', 'Unique Tokens']
category_stats = category_stats.sort_values('Total Volume ($)', ascending=False)

print(category_stats.head(15).to_string())
print()

# Step 5: Top markets by volume
print("="*70)
print("TOP 10 MARKETS BY VOLUME")
print("="*70)

market_stats = enriched.groupby('condition_id').agg({
    'question': 'first',
    'category': 'first',
    'volume_usdc': 'sum'
}).round(2)

market_stats = market_stats.sort_values('volume_usdc', ascending=False).head(10)

for i, (cond_id, row) in enumerate(market_stats.iterrows(), 1):
    question = row['question']
    if pd.isna(question):
        question = "Unknown Market"
    print(f"\n{i}. {question[:65]}...")
    print(f"   Category: {row['category']}")
    print(f"   Volume: ${row['volume_usdc']:,.2f}")
print()

# Step 6: Sample enriched data
print("="*70)
print("SAMPLE ENRICHED DATA")
print("="*70)

sample_cols = [
    'timestamp',
    'price',
    'volume_usdc',
    'side',
    'question',
    'outcome',
    'category'
]

sample = enriched[sample_cols].head(5).copy()
sample['timestamp'] = pd.to_datetime(sample['timestamp'], unit='s').dt.strftime('%Y-%m-%d %H:%M')
sample['question'] = sample['question'].str[:40] + '...'

print(sample.to_string(index=False))
print()

# Step 7: Market grouping example
print("="*70)
print("EXAMPLE: MARKET WITH MULTIPLE OUTCOMES")
print("="*70)

# Find a market with both Yes and No trades
sample_condition = enriched[enriched['question'].notna()]['condition_id'].iloc[0]
market_trades = enriched[enriched['condition_id'] == sample_condition]

print(f"Market: {market_trades['question'].iloc[0]}")
print(f"Category: {market_trades['category'].iloc[0]}")
print(f"Condition ID: {sample_condition[:30]}...")
print()

outcome_stats = market_trades.groupby('outcome').agg({
    'volume_usdc': 'sum',
    'trade_id': 'count',
    'price': 'mean'
}).round(2)

outcome_stats.columns = ['Volume ($)', 'Num Trades', 'Avg Price']
print(outcome_stats.to_string())
print()

# Step 8: Summary
print("="*70)
print("SUMMARY & NEXT STEPS")
print("="*70)
print()
print(f"✓ Processed {len(trades):,} trades from {TRADE_FILE.split('/')[-1]}")
print(f"✓ Matched {100*matched/len(trades):.1f}% with market metadata")
print(f"✓ Found {enriched['category'].nunique()} categories")
print(f"✓ Found {enriched['condition_id'].nunique():,} unique markets")
print()
print("Next steps:")
print("  1. Review the category breakdown above")
print("  2. Check if the enriched data looks correct")
print("  3. Decide what analysis you want to run")
print()
print("To process all trade files, run:")
print("  uv run --with pandas scripts/enrich_all_trades.py")
print()
