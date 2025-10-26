# Understanding markets-raw-shared-2025-04-08.jsonl

## What Is This File?

This is a **complete snapshot of Polymarket market metadata** exported from the Polymarket Gamma API. It's stored in JSONL (JSON Lines) format, where each line is a separate JSON object.

**File Details:**
- **Location:** `../market_info_data/markets-raw-shared-2025-04-08.jsonl`
- **Size:** 471 MB
- **Format:** JSONL (one JSON object per line)
- **Lines:** 402 (each line is a paginated API response with ~100 events)
- **Total Events:** 40,147
- **Total Markets:** 108,083
- **Total Tokens:** 216,013

## File Structure

### Top Level (Each Line)
```json
{
  "offset": 0,           // Pagination offset
  "data": [...]          // Array of events (typically 100 per line)
}
```

### Event Level (Inside `data` array)
Each event represents a market group or series:

```json
{
  "id": "2890",
  "title": "NBA: Will the Mavericks beat the Grizzlies...",
  "category": "Sports",
  "endDate": "2021-12-04T00:00:00Z",
  "description": "...",
  "markets": [...]       // Array of markets (usually 1, sometimes multiple)
}
```

### Market Level (Inside `markets` array)
**This is the key level** - contains the data you need:

```json
{
  "id": "239826",
  "question": "NBA: Will the Mavericks beat the Grizzlies by more than 5.5 points...",
  "conditionId": "0x064d33e3f5703792aafa92bfb0ee10e08f461b1b34c02c1f02671892ede1609a",
  "category": "Sports",
  "outcomes": "[\"Yes\", \"No\"]",
  "clobTokenIds": "[\"28182404005967940652495463228537840901055649726248190462854914416579180110833\", \"47044845753450022047436429968808601130811164131571549682541703866165095016290\"]",
  "endDateIso": "2021-12-04",
  "volume": "1335.045385",
  "closed": true
}
```

## Key Fields Explained

### Critical Fields for Your Use Case:

| Field | Description | Example |
|-------|-------------|---------|
| `clobTokenIds` | **THE MOST IMPORTANT** - Array of token IDs (matches your `market_token_id`) | `["28182...10833", "47044...16290"]` |
| `conditionId` | Unique market identifier | `"0x064d33e3..."` |
| `question` | The market question | `"Will the Mavericks beat..."` |
| `outcomes` | Array of possible outcomes | `["Yes", "No"]` |
| `category` | Market category (often null/empty) | `"Sports"` or `null` |
| `endDateIso` | Market end date | `"2021-12-04"` |
| `closed` | Whether market is resolved | `true` or `false` |

### Relationship to Your Trade Data:

```
Your CSV:          markets-raw-shared file:
market_token_id ←→ clobTokenIds[0] or clobTokenIds[1]

Example:
9995555471... ←→ One of the tokens in clobTokenIds array
```

Each market typically has **2 tokens** (Yes/No), but some have more outcomes.

## How to Use This File

### Option 1: Use the Pre-Built Lookup (Easiest)

I already created `data/token_lookup.csv` from this file:

```python
import pandas as pd

# Just load and use!
lookup = pd.read_csv('data/token_lookup.csv', index_col='token_id', dtype={'token_id': str})

# Get info for a specific token
token_id = "9995555471508730920694746906220961554341980080276756998872079874395992236836"
print(lookup.loc[token_id])
# Output:
#   condition_id: 0x...
#   question: Will Elon tweet less than 250 times...
#   outcome: Yes
#   category: Uncategorized
#   ...
```

### Option 2: Parse the Raw JSONL File Yourself

```python
import json
import pandas as pd

# Build your own lookup
token_to_market = {}

with open('../market_info_data/markets-raw-shared-2025-04-08.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)

        # Iterate through events
        for event in data['data']:
            # Iterate through markets
            for market in event.get('markets', []):
                # Get token IDs
                if 'clobTokenIds' in market:
                    token_ids = json.loads(market['clobTokenIds'])
                    outcomes = json.loads(market.get('outcomes', '[]'))

                    # Map each token to its info
                    for i, token_id in enumerate(token_ids):
                        token_to_market[token_id] = {
                            'condition_id': market.get('conditionId'),
                            'question': market.get('question'),
                            'outcome': outcomes[i] if i < len(outcomes) else f"Outcome {i}",
                            'category': market.get('category') or event.get('category', 'Uncategorized'),
                            'end_date': market.get('endDateIso', '')
                        }

# Convert to DataFrame
df = pd.DataFrame.from_dict(token_to_market, orient='index')
print(f"Created lookup for {len(df):,} tokens")
```

### Option 3: Join with Your Trade Data

```python
import pandas as pd

# Load token lookup (from Option 1 or 2)
lookup = pd.read_csv('data/token_lookup.csv', index_col='token_id', dtype={'token_id': str})

# Load your trades
trades = pd.read_csv('../joined_data/trades-joined-2025-04-08.csv')
trades['market_token_id'] = trades['market_token_id'].astype(str)

# Merge to add metadata
enriched = trades.merge(
    lookup,
    left_on='market_token_id',
    right_index=True,
    how='left'
)

# Now you have all the metadata!
print(enriched[['market_token_id', 'question', 'outcome', 'category', 'end_date']].head())
```

## Common Use Cases

### 1. Filter Trades by Category

```python
# Get all Sports trades
sports_trades = enriched[enriched['category'] == 'Sports']

# Get all Crypto trades
crypto_trades = enriched[enriched['category'] == 'Crypto']
```

### 2. Group Markets by Condition ID

```python
# Group tokens by market (condition_id)
markets = enriched.groupby('condition_id').agg({
    'question': 'first',
    'volume_usdc': 'sum',
    'market_token_id': 'nunique'  # Number of outcomes
})
```

### 3. Find All Outcomes for a Market

```python
# Get both Yes and No tokens for a market
condition_id = "0x064d33e3f5703792aafa92bfb0ee10e08f461b1b34c02c1f02671892ede1609a"
market_outcomes = lookup[lookup['condition_id'] == condition_id]
print(market_outcomes[['question', 'outcome', 'token_id']])
```

## Important Notes

⚠️ **Category Coverage:** Only ~7% of markets have a category assigned. The rest are "Uncategorized" or `null`. You may want to categorize based on question text instead.

✅ **Token Coverage:** This file contains **100% of the tokens** in your April-September 2025 trade data. Verified!

📅 **Date Range:** Although named "2025-04-08", this file covers markets from **2002 to 2028** - it's a complete snapshot, not date-specific.

🔗 **Symlinks:** All the date-specific files (`markets-raw-2025-04-09.jsonl`, etc.) are just symbolic links pointing to this same file.

## Why This File Exists

This appears to be a bulk export from the Polymarket Gamma API, likely created by fetching all events with pagination (100 events per page × 402 pages = ~40,000 events). Each event can have multiple markets, and each market has multiple tokens (outcomes).

The API probably looked like:
```bash
GET /events?limit=100&offset=0     # Line 1
GET /events?limit=100&offset=100   # Line 2
GET /events?limit=100&offset=200   # Line 3
...
```

This is much more efficient than fetching markets individually via the API!
