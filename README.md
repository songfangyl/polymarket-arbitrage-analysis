# Polymarket Trade Data Enrichment Pipeline

A Python pipeline to enrich Polymarket historical trade data with complete market metadata (condition_id, questions, outcomes, categories).

## 📊 What This Does

Transforms raw Polymarket trade data by adding comprehensive market metadata:

**Input:** Raw trade CSV files
```csv
market_token_id,price,volume_usdc,side
9995555471...,0.71,16.44,SELL
```

**Output:** Enriched trade data with metadata
```csv
market_token_id,price,volume_usdc,side,condition_id,question,outcome,category
9995555471...,0.71,16.44,SELL,0x4fd2...,"Will Elon tweet...","Yes","Uncategorized"
```

**New fields added:**
- `condition_id` - Unique market identifier (groups related outcomes)
- `question` - Full market question text
- `outcome` - Outcome label (Yes/No/Up/Down/etc.)
- `category` - Market category (if available)
- `event_title` - Event/series name
- `end_date` - Market close date

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Polymarket historical trade data (CSV format)
- Polymarket market metadata (JSONL format from Gamma API)

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd polymarket-arbitrage-analysis

# No installation needed! Scripts use uv to manage dependencies
```

### Usage

#### Step 1: Create Token Lookup Table

Generates a mapping from token IDs to market metadata.

```bash
uv run --with pandas scripts/1_create_token_lookup.py
```

**Input:** `../market_info_data/markets-raw-shared-*.jsonl`
**Output:** `data/token_lookup.csv` (token_id → market metadata)

#### Step 2: Enrich All Trade Files

Adds market metadata to all trade CSV files.

```bash
uv run --with pandas scripts/2_enrich_all_trades.py
```

**Input:** `../joined_data/trades-joined-*.csv`
**Output:** `data/enriched/enriched-*.csv` (all trades + metadata)

#### Step 3: Extract Master Market List

Creates a deduplicated list of all unique markets.

```bash
uv run --with pandas scripts/3_extract_market_list.py
```

**Input:** `data/enriched/*.csv`
**Output:** `data/market_list.csv` (56K+ unique markets)

#### Quick Analysis (Optional)

Run a quick analysis on one day of enriched data:

```bash
uv run --with pandas scripts/quick_analysis.py
```

## 📁 Project Structure

```
polymarket-arbitrage-analysis/
├── scripts/
│   ├── 1_create_token_lookup.py    # Step 1: Build token → market mapping
│   ├── 2_enrich_all_trades.py      # Step 2: Add metadata to trades
│   ├── 3_extract_market_list.py    # Step 3: Extract unique markets
│   ├── quick_analysis.py            # Optional: Analyze enriched data
│   └── example_usage.py             # Code examples
│
├── docs/
│   ├── METADATA_GUIDE.md           # Understanding the data structure
│   ├── CONDITION_ID_EXPLAINED.md   # What is condition_id?
│   └── IMPLEMENTATION_PLAN.md      # Implementation details
│
├── data/                            # Output directory (gitignored)
│   ├── token_lookup.csv
│   ├── market_list.csv
│   └── enriched/
│       ├── enriched-2025-04-08.csv
│       └── ...
│
├── .gitignore
├── LICENSE
└── README.md
```

## 📖 Data Pipeline Details

### Understanding the Data Model

**Key Concept:** One market (condition_id) has multiple tradeable outcomes (tokens)

```
Market: "Will Bitcoin hit $100k?"
├─ condition_id: 0xabc123...
├─ Token 1: 9995555... (Outcome: "Yes")
└─ Token 2: 1980026... (Outcome: "No")
```

See [docs/CONDITION_ID_EXPLAINED.md](docs/CONDITION_ID_EXPLAINED.md) for details.

### Data Sources

This pipeline expects:

1. **Trade Data**: CSV files with columns:
   - `market_token_id`, `price`, `volume_usdc`, `side`, `timestamp`, etc.

2. **Market Metadata**: JSONL file from Polymarket Gamma API with:
   - Market questions, categories, outcomes, token IDs

## 💡 Example Usage

### Load Enriched Data

```python
import pandas as pd

# Load enriched trades
df = pd.read_csv('data/enriched/enriched-2025-04-08.csv')

# Show sample
print(df[['question', 'outcome', 'category', 'volume_usdc']].head())
```

### Find Markets by Keyword

```python
# Find all Bitcoin markets
btc = df[df['question'].str.contains('Bitcoin', case=False, na=False)]

# Group by market
by_market = btc.groupby(['condition_id', 'question'])['volume_usdc'].sum()
print(by_market.sort_values(ascending=False).head())
```

### Compare Outcomes

```python
# Compare Yes vs No for a specific market
condition_id = '0xabc123...'
market = df[df['condition_id'] == condition_id]

outcome_stats = market.groupby('outcome').agg({
    'volume_usdc': 'sum',
    'price': 'mean',
    'trade_id': 'count'
})
print(outcome_stats)
```

## ⚠️ Important Notes

### Category Coverage

Only ~7% of markets have assigned categories. Most show as "Uncategorized".

**Workarounds:**
- Filter by question text keywords
- Create custom categories using NLP
- Group by date ranges or volume tiers

### Data Size

Enriched files are large (42GB+ for 167 days). The pipeline:
- Processes files one at a time (memory efficient)
- Outputs are gitignored (add `data/` to .gitignore)
- Use sampling for initial analysis

## 📊 Statistics

Based on April-September 2025 trade data:

- **Total Trades:** 53.3M
- **Unique Markets:** 56,524
- **Unique Tokens:** 113,189
- **Match Rate:** 99.98%

## 🔧 Customization

See [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) for:
- Custom analysis examples
- Database loading (ClickHouse/SQLite)
- Arbitrage detection strategies
- Advanced filtering techniques

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📚 Resources

- [Polymarket Documentation](https://docs.polymarket.com/)
- [Gamma API Reference](https://docs.polymarket.com/developers/gamma-markets-api/overview)
- [Project Documentation](docs/)

---

**Built for analyzing Polymarket prediction market data** 🎯
