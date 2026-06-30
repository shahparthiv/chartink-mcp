---
name: chartink-query
description: Write, validate, and run Chartink stock scanner queries (scan_clause strings) for the Indian NSE/BSE market. Use whenever the user asks to build a Chartink scan, screener, or scanner query, or describes stock conditions to screen for (e.g. "find stocks where RSI crossed above 60 and price above 50 SMA", "scan for bullish breakouts", "write a chartink query for ..."). Covers price/volume attributes, all technical indicators (SMA, EMA, WMA, MA envelopes, RSI, MACD, ADX, CCI, Stochastic, ROC, MFI, Bollinger, ATR, Donchian, Supertrend, Parabolic SAR, VWAP, OBV, pivot points, etc.), crossovers, candle offsets/timeframes (daily/weekly/monthly/intraday), functions (Min/Max/count/abs), segments/index groups, and fundamental filters (market cap, PE, PB, EPS, book value, net profit, sales, TTM metrics).
---

# Chartink Query Builder

Generate valid Chartink **scan_clause** strings from a plain-English description of what to screen for, then (optionally) validate and run them via the `chartink` MCP server.

## What a Chartink scan_clause looks like

A scan clause is a single string with this overall shape:

```
( {segment} ( <condition> [and|or <condition>] ... ) )
```

- The **outer `( ... )`** and **`{segment}`** are mandatory. Default segment is `{cash}` (all NSE cash stocks).
- Conditions are joined with lowercase **`and`** / **`or`**. Group with extra nested parentheses to control precedence.
- Every token is **lowercase**. Spaces around operators, commas, and parentheses are expected — write `sma( latest close , 50 )`, not `sma(latest close,50)`.

A condition is built as:

```
[timeframe] [attribute-or-indicator] [comparison-operator] [timeframe] [value-or-indicator]
```

Examples:

```
( {cash} ( latest close > latest sma( latest close , 50 ) ) )

( {cash} ( latest rsi( 14 ) > 60 and latest close > 1 day ago close ) )

( {cash} ( latest close > latest open and latest volume > latest sma( latest volume , 20 ) and latest close > 50 ) )
```

## Always output BOTH forms

Every time you produce a query, give the user two versions side by side:

1. **MCP / API form** (`run_screener` `scan_clause`) — the **fully wrapped** string including segment:
   ```
   ( {cash} ( latest close > latest sma( latest close , 50 ) ) )
   ```
2. **Chartink.com form** (paste into the *Scan conditions* box at chartink.com/screener) — the **inner conditions only**, no outer `( {cash} ( ... ) )` wrapper, since the segment is chosen from the page's dropdown:
   ```
   latest close > latest sma( latest close , 50 )
   ```
   Also state which **segment dropdown** to select (e.g. "Cash" for `{cash}`, "Intraday" for an intraday timeframe).

The two are the same conditions — the only difference is that the MCP form wraps them in `( {segment} ( ... ) )` and the website supplies the segment via its UI. Label each clearly so the user knows which to use where.

## Workflow (follow this when asked to write a query)

1. **Parse intent** into discrete conditions (price, indicator, volume, timeframe, crossover, fundamental).
2. **Pick the segment.** Default `{cash}`. Use an index group (see `reference.md` → Segments & Groups) only if the user names an index like "Nifty 50".
3. **Translate each condition** using `reference.md`. Mind the gotchas in "Crossovers" and "Timeframes" below.
4. **Assemble** the full `( {segment} ( ... ) )` string.
5. **Present BOTH forms** (see "Always output BOTH forms" above) in separate code blocks — the wrapped MCP `scan_clause` and the website paste-in conditions + segment to select — with a one-line explanation of what it screens for.
6. **Offer to run it.** If the user wants results, call `mcp__chartink__run_screener` with the wrapped `scan_clause` form. If it returns a parse/syntax error, fix the clause and retry — Chartink's error message usually points at the bad token. (Backtests use `mcp__chartink__run_backtest`; a saved scan slug uses `mcp__chartink__run_saved_screener`. `set_cookies` must have been called first for runs to work.)

When unsure about an exact indicator token, prefer the spellings in `reference.md`; if a run errors on a token, that's the fastest ground-truth fix.

## Key rules & gotchas (read before assembling)

- **Crossovers.** Chartink has no single "crossed above" keyword in the raw clause — express it as a two-part condition:
  - `A crossed above B`  →  `latest A > latest B and 1 day ago A <= 1 day ago B`
  - `A crossed below B`  →  `latest A < latest B and 1 day ago A >= 1 day ago B`
  - Example (RSI crosses above 60): `latest rsi( 14 ) > 60 and 1 day ago rsi( 14 ) <= 60`
- **Timeframe prefix carries the candle.** `latest close` = today's daily close; `1 day ago close` = previous daily candle; `weekly close` = current weekly candle; `1 week ago close` = previous weekly; `monthly close` / `1 month ago close` for monthly. Don't mix incompatible timeframes inside a crossover (e.g. a 5-minute close crossing a 1-day-ago high) — use `>`/`<` instead.
- **Indicators take a source + period.** Price MAs reference a source series: `sma( latest close , 20 )`, `ema( latest close , 50 )`. Volume MA: `sma( latest volume , 20 )`. Oscillators take just a period: `rsi( 14 )`, `cci( 20 )`, `mfi( 14 )`.
- **One comparison per condition.** Chain ranges with `and`: `latest close > 25 and latest close < 1200`.
- **Percentages are multipliers.** "3% gap up" → `latest open > 1 day ago close * 1.03`. "Down 5% from yesterday" → `latest close < 1 day ago close * 0.95`.
- **Fundamentals are supported.** Chartink allows fundamental filters (Market Cap, PE, PB, EPS, Book Value, Net Profit, Sales, TTM variants, etc., in ₹ crore, consolidated) mixed with technical conditions in the same clause — see `reference.md` → Fundamentals for the full list. ROE/ROCE/dividend-yield/debt-equity are NOT yet available. Fundamental tokens carry no `latest`/timeframe prefix; if a token's exact spelling is uncertain, validate with a quick `run_screener` test rather than asserting it works.

## Quick reference (full catalog in reference.md)

| Need | Token |
|------|-------|
| Price/volume | `latest open/high/low/close/volume` |
| Prev candle | `1 day ago close`, `2 days ago high`, ... |
| Simple MA | `sma( latest close , 50 )` |
| Exp. MA | `ema( latest close , 21 )` |
| RSI | `rsi( 14 )` |
| MACD | `macd line( 26 , 12 , 9 )`, `macd signal( 26 , 12 , 9 )` |
| Bollinger | `bollinger band upper/lower/middle( latest close , 20 , 2 )` |
| ADX / DI | `adx( 14 )`, `plus di( 14 )`, `minus di( 14 )` |
| Stochastic | `stochastic %k( 14 , 3 )`, `stochastic %d( 14 , 3 , 3 )` |
| Supertrend | `supertrend( 10 , 3 )` |
| ATR / VWAP | `atr( 14 )`, `vwap` |
| 52-week high | `max( 252 , latest high )` |
| N-day low | `min( 20 , latest low )` |

For the exhaustive keyword/parameter list see **`reference.md`**. For copy-ready query patterns see **`examples.md`**.
