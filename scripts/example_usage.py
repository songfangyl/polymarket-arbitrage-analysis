"""
Example: How to use the market metadata with your trade data
"""
import pandas as pd

print("="*60)
print("EXAMPLE: Using Market Metadata with Trade Data")
print("="*60)
print()

# Method 1: Load the pre-built token lookup
print("Method 1: Using the pre-built lookup table")
print("-" * 60)

lookup = pd.read_csv('data/token_lookup.csv', index_col='token_id', dtype={'token_id': str})
print(f"✓ Loaded lookup for {len(lookup):,} tokens")
print()

# Show a sample
print("Sample token lookup:")
sample_token = lookup.index[0]
print(f"\nToken: {sample_token}")
print(lookup.loc[sample_token].to_string())
print()

# Method 2: Enrich your trade data
print("\nMethod 2: Enriching trade data with metadata")
print("-" * 60)

# Load a sample trade file
trades = pd.read_csv('../joined_data/trades-joined-2025-04-08.csv')
print(f"✓ Loaded {len(trades):,} trades")

# Convert token_id to string for matching
trades['market_token_id'] = trades['market_token_id'].astype(str)

# Merge with metadata
enriched = trades.merge(
    lookup,
    left_on='market_token_id',
    right_index=True,
    how='left',
    suffixes=('_original', '_metadata')
)

print(f"✓ Enriched {len(enriched):,} trades with metadata")
print()

# Show what you get
print("Sample enriched trade:")
sample_cols = [
    'market_token_id',
    'question',
    'outcome',
    'category',
    'end_date',
    'price',
    'volume_usdc',
    'side'
]
print(enriched[sample_cols].head(3).to_string(index=False))
print()

# Method 3: Analyze by category
print("\nMethod 3: Analyze trades by category")
print("-" * 60)

category_stats = enriched.groupby('category').agg({
    'volume_usdc': ['sum', 'count'],
    'market_token_id': 'nunique'
}).round(2)

category_stats.columns = ['Total Volume (USDC)', 'Num Trades', 'Unique Tokens']
category_stats = category_stats.sort_values('Total Volume (USDC)', ascending=False)

print("\nTop 10 categories by volume:")
print(category_stats.head(10))
print()

# Method 4: Group by market (condition_id)
print("\nMethod 4: Group trades by market")
print("-" * 60)

market_stats = enriched.groupby('condition_id').agg({
    'question': 'first',
    'category': 'first',
    'volume_usdc': 'sum',
    'market_token_id': 'nunique'
}).round(2)

market_stats.columns = ['Question', 'Category', 'Total Volume', 'Num Outcomes']
market_stats = market_stats.sort_values('Total Volume', ascending=False)

print("\nTop 5 markets by trading volume:")
for i, (cond_id, row) in enumerate(market_stats.head(5).iterrows(), 1):
    print(f"\n{i}. {row['Question'][:70]}...")
    print(f"   Category: {row['Category']}")
    print(f"   Volume: ${row['Total Volume']:,.2f}")
    print(f"   Outcomes: {row['Num Outcomes']}")
print()

# Method 5: Find related tokens (same market)
print("\nMethod 5: Find related outcomes for a market")
print("-" * 60)

# Pick a sample token
sample_token = enriched['market_token_id'].iloc[0]
sample_condition = enriched[enriched['market_token_id'] == sample_token]['condition_id'].iloc[0]

# Find all tokens for this market
related = lookup[lookup['condition_id'] == sample_condition]

print(f"Market: {related['question'].iloc[0]}")
print(f"Condition ID: {sample_condition[:20]}...")
print(f"\nAll outcomes:")
for idx, row in related.iterrows():
    print(f"  {row['outcome']}: Token {idx[:20]}...")
print()

print("="*60)
print("✅ Examples complete!")
print("="*60)
print("\nNow you can:")
print("  1. Filter trades by category (Sports, Crypto, etc.)")
print("  2. Group trades by market using condition_id")
print("  3. Analyze volume across different market types")
print("  4. Find all outcomes/tokens for a specific market")
print("  5. Build arbitrage detection across related outcomes")
