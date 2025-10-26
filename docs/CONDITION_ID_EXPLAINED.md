# Understanding condition_id

## The Hierarchy

```
📋 MARKET (condition_id)
   "Will Bitcoin hit $100k by end of 2025?"
   condition_id: 0xabc123...
   │
   ├─ 🎫 TOKEN 1 (market_token_id)
   │    Outcome: "Yes"
   │    token_id: 9995555471508730920...
   │    → People BUY this if they think Yes
   │    → People SELL this if they think No
   │
   └─ 🎫 TOKEN 2 (market_token_id)
        Outcome: "No"
        token_id: 1980026463393154732...
        → People BUY this if they think No
        → People SELL this if they think Yes
```

## Key Concepts

### 1. condition_id = The Market Question

**One condition_id identifies ONE market/question**

Examples:
- `0x07c0a8319...` → "Bitcoin Up or Down on April 8?"
- `0xa5ac4cdcf...` → "Trump ends Ukraine war in first 90 days?"
- `0x3ce13561c...` → "Ethereum Up or Down on April 8?"

### 2. Each Market Has Multiple Outcomes

**Most markets have 2 outcomes (Yes/No or Up/Down)**

But some have more:
- Binary: Yes/No, Up/Down, Win/Lose
- Multiple choice: "Who will win?" (Candidate A, B, C, D)
- Ranges: "What will the price be?" ($90-95k, $95-100k, $100-105k)

### 3. Each Outcome = One Tradeable Token

**Each outcome has its own unique token_id (market_token_id)**

This is what you actually TRADE on Polymarket:
- You don't trade "the market"
- You trade specific OUTCOME TOKENS
- Each token represents a bet on one specific outcome

### 4. Prices Must Sum to ~$1.00

**Because outcomes are mutually exclusive:**

Example: "Bitcoin Up or Down?"
- Up token price: $0.60
- Down token price: $0.40
- Total: $1.00 ✓

If one goes up, the other must go down!

## Real Example from Your Data

```python
Market: "Bitcoin Up or Down on April 8?"
condition_id: 0x07c0a8319e8864912a7c22a523de1a3368430ef4709563ed78858b8182fc9966

Token 1 (Up):
  token_id: 13027592035273708312237061948078258923635616407334901585479060781535110944053
  trades: 969
  volume: $151,518
  avg_price: 0.58 → 58% chance of Up

Token 2 (Down):
  token_id: 99760067903618629482814639771270083397986122088690140394268208959112416787588
  trades: 582
  volume: $113,587
  avg_price: 0.36 → 36% chance of Down

Note: 0.58 + 0.36 = 0.94 (close to 1.00, with small spread/fees)
```

## Why This Matters

### For Arbitrage Detection

**Look for price inconsistencies within the same market:**

```python
# Get all tokens for a market
market = df[df['condition_id'] == some_condition_id]

# Check if prices sum to 1.00
price_sum = market.groupby('outcome')['price'].mean().sum()

if price_sum > 1.05:
    print("Arbitrage opportunity! Prices don't add up correctly")
```

### For Market Analysis

**Group trades by market (not by individual tokens):**

```python
# Volume per MARKET (not per token)
market_volume = df.groupby(['condition_id', 'question'])['volume_usdc'].sum()

# Compare outcomes within the same market
by_outcome = df.groupby(['condition_id', 'outcome'])['volume_usdc'].sum()
```

### For Understanding Market Sentiment

**Compare trading between Yes/No:**

```python
# Which side is getting more volume?
sentiment = df.groupby(['condition_id', 'outcome']).agg({
    'volume_usdc': 'sum',
    'price': 'mean'
})

# If Yes has higher volume AND higher price → Strong bullish sentiment
# If prices are close but volumes differ → Uncertainty
```

## Summary Table

| Field | Level | Uniqueness | Example |
|-------|-------|------------|---------|
| `condition_id` | Market | 1 per question | `0x07c0a8319...` |
| `question` | Market | Same for all outcomes | "Bitcoin Up or Down?" |
| `market_token_id` | Outcome | 1 per outcome | `13027592035...` |
| `outcome` | Outcome | Describes what token represents | "Yes", "No", "Up", "Down" |

## In Your Trade Data

```csv
trade_id,price,volume_usdc,market_token_id,condition_id,question,outcome
trade1,0.58,100,130275920...,0x07c0a8319...,"Bitcoin Up?","Up"
trade2,0.36,50,997600679...,0x07c0a8319...,"Bitcoin Up?","Down"
                                    ↑
                            Same condition_id!
                            = Same market
                            Different tokens = Different outcomes
```

## Think of It Like This:

```
🎰 CASINO ANALOGY:

condition_id = The Roulette Table
   (one question: where will the ball land?)

market_token_id = Individual Bets
   Token A = Betting on Red
   Token B = Betting on Black
   Token C = Betting on Green

You can trade (buy/sell) individual bets with other people,
but they're all about the SAME roulette spin (same condition_id)!
```
