#!/usr/bin/env python3
"""
Extract a master list of all unique markets (condition_id + question)
from the enriched trade data
"""
import pandas as pd
import glob

print("="*70)
print("EXTRACTING MASTER MARKET LIST")
print("="*70)
print()

# Find all enriched files
files = sorted(glob.glob('data/enriched/enriched-*.csv'))
print(f"Found {len(files)} enriched files")
print()

# Collect unique markets
print("Processing files to extract unique markets...")
all_markets = []

for i, file in enumerate(files, 1):
    if i % 20 == 0:
        print(f"  Processed {i}/{len(files)} files...")

    # Read only the columns we need
    df = pd.read_csv(file, usecols=['condition_id', 'question', 'category', 'event_title', 'end_date'])

    # Get unique markets from this file
    markets = df.drop_duplicates(subset=['condition_id'])
    all_markets.append(markets)

print(f"  Processed {len(files)}/{len(files)} files...")
print()

# Combine all markets
print("Combining and deduplicating...")
combined = pd.concat(all_markets, ignore_index=True)
unique_markets = combined.drop_duplicates(subset=['condition_id']).reset_index(drop=True)

print(f"✓ Found {len(unique_markets):,} unique markets")
print()

# Sort by end_date
unique_markets['end_date'] = pd.to_datetime(unique_markets['end_date'], errors='coerce')
unique_markets = unique_markets.sort_values('end_date', ascending=False)

# Save to CSV
output_file = 'data/market_list.csv'
unique_markets.to_csv(output_file, index=False)
print(f"✓ Saved to {output_file}")
print()

# Show statistics
print("="*70)
print("MARKET STATISTICS")
print("="*70)
print()
print(f"Total unique markets: {len(unique_markets):,}")
print()

# Category breakdown
print("Markets by category:")
category_counts = unique_markets['category'].value_counts()
for cat, count in category_counts.head(10).items():
    print(f"  {cat}: {count:,}")
if len(category_counts) > 10:
    print(f"  ... and {len(category_counts) - 10} more categories")
print()

# Date range
print("Date range:")
print(f"  Earliest: {unique_markets['end_date'].min().date()}")
print(f"  Latest: {unique_markets['end_date'].max().date()}")
print()

# Sample markets
print("="*70)
print("SAMPLE MARKETS (most recent)")
print("="*70)
print()

for i, row in unique_markets.head(10).iterrows():
    print(f"{i+1}. {row['question']}")
    print(f"   Condition ID: {row['condition_id']}")
    print(f"   Category: {row['category']}")
    print(f"   End Date: {row['end_date'].date() if pd.notna(row['end_date']) else 'N/A'}")
    print()

print("="*70)
print("✅ COMPLETE!")
print("="*70)
print()
print(f"Master market list saved to: {output_file}")
print(f"Total markets: {len(unique_markets):,}")
print()
print("Columns:")
print("  - condition_id: Unique market identifier")
print("  - question: Market question")
print("  - category: Market category")
print("  - event_title: Event name")
print("  - end_date: Market end date")
print()
