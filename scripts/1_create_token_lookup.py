"""Create a simple token ID to market metadata lookup"""
import json
import pandas as pd

print("Creating token lookup from metadata...")

# Load metadata and create lookup
token_lookup = {}
categories = {}

with open('../market_info_data/markets-raw-shared-2025-04-08.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        if 'data' in data:
            for event in data['data']:
                event_category = event.get('category') or 'Uncategorized'

                for market in event.get('markets', []):
                    if 'clobTokenIds' in market:
                        token_ids = json.loads(market['clobTokenIds'])
                        outcomes = json.loads(market.get('outcomes', '[]'))

                        market_category = market.get('category') or event_category
                        categories[market_category] = categories.get(market_category, 0) + 1

                        for i, token_id in enumerate(token_ids):
                            outcome = outcomes[i] if i < len(outcomes) else f"Outcome {i+1}"
                            token_lookup[token_id] = {
                                'condition_id': market.get('conditionId'),
                                'question': market.get('question'),
                                'outcome': outcome,
                                'event_title': event.get('title'),
                                'category': market_category,
                                'end_date': (market.get('endDateIso') or market.get('endDate', ''))[:10],
                            }

print(f"✓ Created lookup for {len(token_lookup):,} tokens")
print(f"✓ Found {len(categories)} categories")
print()

# Save as CSV
df = pd.DataFrame.from_dict(token_lookup, orient='index')
df.index.name = 'token_id'
df.to_csv('./data/token_lookup.csv')
print(f"✓ Saved to ./data/token_lookup.csv ({len(df):,} rows)")
print()

# Category breakdown
print("Top categories:")
for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
    print(f"  {cat}: {count:,} markets")
print()

# Sample lookup
sample_token = list(token_lookup.keys())[0]
print(f"Sample lookup for token {sample_token}:")
for k, v in token_lookup[sample_token].items():
    print(f"  {k}: {v}")
