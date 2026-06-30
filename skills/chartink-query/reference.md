# Chartink scan_clause — Full Reference

All tokens are **lowercase** with spaces around commas, operators, and parentheses.
Every clause is wrapped: `( {segment} ( <conditions> ) )`.

---

## 1. Structure & operators

| Element | Syntax | Notes |
|---|---|---|
| Outer wrapper | `( {cash} ( ... ) )` | Mandatory. |
| Logical AND | `and` | All must pass. |
| Logical OR | `or` | Any may pass. |
| Grouping | extra `( ... )` | Control precedence, e.g. `( a and ( b or c ) )`. |
| Greater / less | `>` , `<` | |
| Greater-eq / less-eq | `>=` , `<=` | |
| Equal | `=` | |
| Arithmetic | `+ - * /` | e.g. `1 day ago close * 1.03` |

> There is **no** literal `crossed above` / `crossed below` token in the raw clause. Express crossovers as a two-part `and` condition (see §7).

---

## 2. Price & volume attributes

| Attribute | Token |
|---|---|
| Open | `latest open` |
| High | `latest high` |
| Low | `latest low` |
| Close | `latest close` |
| Volume | `latest volume` |

Combine with a candle offset (§3): `1 day ago close`, `5 days ago high`, etc.

---

## 3. Timeframes & candle offsets

The timeframe word sits **in front of** the attribute/indicator and selects which candle.

| Meaning | Prefix examples |
|---|---|
| Current daily candle | `daily close` (canonical) or `latest close`; `daily rsi( 14 )` |
| Previous daily candle(s) | `1 day ago close`, `2 days ago close`, ... `N days ago close` |
| Current weekly candle | `weekly close`, `weekly rsi( 14 )` |
| Previous weekly candle(s) | `1 week ago close`, `2 weeks ago close` |
| Current monthly candle | `monthly close` |
| Previous monthly candle(s) | `1 month ago close`, `2 months ago close` |
| Intraday | select the timeframe (1/5/15/30/60 min) in the scanner UI; in clause use `latest ...` against that timeframe. 1–3 min is premium; 5 min+ free. |

Rules:
- **`daily` vs `latest`:** Chartink's scan builder emits `daily` as the daily-timeframe prefix (`daily close`, `daily macd line(...)`); `latest` also works as an alias for the current candle. Either is accepted — prefer `daily`/`weekly`/`monthly` to match what Chartink shows.
- Don't compare/cross mismatched timeframes (e.g. 5-min close vs 1-day-ago high) with crossover logic — use `>` / `<`.
- For "X candles ago" beyond price, the prefix still works: `2 days ago rsi( 14 )`, `1 week ago sma( weekly close , 20 )`.

---

## 4. Moving averages & bands (need a source series + period)

| Indicator | Token |
|---|---|
| Simple MA | `sma( latest close , 50 )` |
| Exponential MA | `ema( latest close , 21 )` |
| Weighted MA | `wma( latest close , 20 )` |
| Volume SMA | `sma( latest volume , 20 )` |
| Bollinger upper | `bollinger band upper( latest close , 20 , 2 )` |
| Bollinger middle | `bollinger band middle( latest close , 20 , 2 )` |
| Bollinger lower | `bollinger band lower( latest close , 20 , 2 )` |
| MA envelope upper | `ema envelope upper( latest close , 20 , 2.5 )` † |
| MA envelope lower | `ema envelope lower( latest close , 20 , 2.5 )` † |
| Donchian upper | `donchian channel upper( 20 )` † |
| Donchian lower | `donchian channel lower( 20 )` † |
| Donchian middle | `donchian channel middle( 20 )` † |
| VWAP | `vwap` |

Always prefix with a timeframe: `latest sma( latest close , 50 )`, `weekly ema( weekly close , 21 )`.

† Envelope / Donchian token spellings vary by build — confirm with a `run_screener` test (§11) before relying on them.

---

## 5. Oscillators & momentum (period only, unless noted)

| Indicator | Token |
|---|---|
| RSI | `rsi( 14 )` |
| MACD line | `macd line( 26 , 12 , 9 )` |
| MACD signal | `macd signal( 26 , 12 , 9 )` |
| MACD histogram | `macd histogram( 26 , 12 , 9 )` |
| ADX | `adx( 14 )` |
| +DI | `plus di( 14 )` |
| −DI | `minus di( 14 )` |
| Stochastic %K | `stochastic %k( 14 , 3 )` |
| Stochastic %D | `stochastic %d( 14 , 3 , 3 )` |
| CCI | `cci( 20 )` |
| MFI | `mfi( 14 )` |
| Williams %R | `williams %r( 14 )` |
| ATR | `atr( 14 )` |
| Supertrend | `supertrend( 10 , 3 )` |
| Parabolic SAR | `parabolic sar( 0.02 , 0.2 )` |
| Aroon up / down | `aroon up( 14 )` , `aroon down( 14 )` |
| Momentum | `mom( latest close , 14 )` |
| ROC (Rate of Change) | `roc( latest close , 12 )` |
| OBV (On-Balance Volume) | `obv` |

> If a run errors on one of these tokens, the indicator name or parameter spelling differs in your Chartink build — run a tiny test clause (`( {cash} ( latest <indicator> > 0 ) )`) to confirm the exact spelling, then fix.

---

## 5b. Pivot points & support/resistance

Classic floor-trader pivots (token spellings are build-dependent — verify with §11):

| Level | Token |
|---|---|
| Pivot | `pivot point` |
| Resistance 1/2/3 | `resistance 1` , `resistance 2` , `resistance 3` |
| Support 1/2/3 | `support 1` , `support 2` , `support 3` |

Pivots default to the **previous** period's H/L/C, so compare today's price to them directly: `latest close > latest pivot point`. For raw candle support/resistance, use `max( N , latest high )` / `min( N , latest low )` from §6.

---

## 6. Functions (lookbacks & math)

| Function | Syntax | Meaning |
|---|---|---|
| Max over N | `max( 252 , latest high )` | Highest value over N candles (252 ≈ 52-week high). |
| Min over N | `min( 20 , latest low )` | Lowest value over N candles. |
| Count | `count( 5 , 1 where daily close > daily open ) >= 3` | Counts candles in the last N where the condition holds. **Correct syntax is `count( period , <value> where <condition> )`** — note the `1 where` (return value `1` per matching candle), NOT `count( 5 , <condition> )`. Verified from a live Chartink scan. ⚠️ Putting a nested `1 day ago ...` offset inside the `where` is unverified/unreliable — for "crossover within last N days" use the OR-expansion in §7, not `count`. |
| Absolute | `abs( latest close - 1 day ago close )` | Absolute value. |
| Round | `round( latest close , 0 )` | Round to digits. |
| Ceil / Floor | `ceil( ... )` , `floor( ... )` | Round up / down. |

---

## 7. Crossovers (build as two-part conditions)

| Plain English | scan_clause |
|---|---|
| A crossed **above** B | `latest A > latest B and 1 day ago A <= 1 day ago B` |
| A crossed **below** B | `latest A < latest B and 1 day ago A >= 1 day ago B` |

Examples:
- Price crosses above 50 SMA: `latest close > latest sma( latest close , 50 ) and 1 day ago close <= 1 day ago sma( latest close , 50 )`
- Golden cross (50 over 200 SMA): `latest sma( latest close , 50 ) > latest sma( latest close , 200 ) and 1 day ago sma( latest close , 50 ) <= 1 day ago sma( latest close , 200 )`
- RSI crosses above 60: `latest rsi( 14 ) > 60 and 1 day ago rsi( 14 ) <= 60`
- MACD bullish cross: `latest macd line( 26 , 12 , 9 ) > latest macd signal( 26 , 12 , 9 ) and 1 day ago macd line( 26 , 12 , 9 ) <= 1 day ago macd signal( 26 , 12 , 9 )`

**"Crossover within the last N days" (verified pattern).** `count()` will NOT work here (it can't take a nested offset — returns 0). Instead OR one crossover block per day, shifting every offset by one each time. For "bullish cross in last 3 days":
```
( latest A > latest B and 1 day ago A <= 1 day ago B )
or ( 1 day ago A > 1 day ago B and 2 days ago A <= 2 days ago B )
or ( 2 days ago A > 2 days ago B and 3 days ago A <= 3 days ago B )
```
Add an "above zero at the cross" filter per block (e.g. `and 1 day ago A > 0` in the second block, matching that block's cross day).

---

## 8. Percentage / gap helpers

| Intent | Expression |
|---|---|
| Up 3% vs prev close | `latest close > 1 day ago close * 1.03` |
| Down 5% vs prev close | `latest close < 1 day ago close * 0.95` |
| Gap up open > 2% | `latest open > 1 day ago close * 1.02` |
| Within 5% of 52-wk high | `latest close > max( 252 , latest high ) * 0.95` |

---

## 9. Segments & index groups

Put the group code in the `{...}` slot. `{cash}` is the all-stocks default.

| Universe | Token |
|---|---|
| All NSE cash stocks | `{cash}` |
| F&O / Futures stocks | `{futures}` (uses cash prices) |
| An index's constituents | a numeric group code, e.g. Nifty 50 / Nifty 500 |

> Index group codes are numeric IDs Chartink assigns (e.g. `{57920}`-style). If the user names a specific index, the safest path is to create/inspect the scan in the Chartink UI for that index to capture its exact group code, or default to `{cash}` and note that the index filter wasn't applied. Don't guess a numeric code.

---

## 10. Fundamentals

Chartink **does** support fundamental filters in scans (added per the official "Fundamental filters now available" article). They mix freely with technical conditions via `and` / `or` inside the same `( {cash} ( ... ) )` clause.

**Units & basis:** values are **consolidated figures in ₹ crore** (Market Cap, Sales, Net Profit, Networth, etc. are in Cr). Ratios (PE, PB) and per-share figures (EPS, Book Value, CPS) are absolute numbers. Comparisons are numeric (`>`, `<`, `=`).

**Supported fundamental fields:**

| Category | Fields |
|---|---|
| Valuation | Market Cap, Yearly PE Ratio, Yearly PC Ratio, Price to Book Value, Book Value |
| Per share | Earning Per Share (EPS), Prev Year EPS, Cash Per Share — yearly / quarter / month |
| Profitability | Net Profit (yearly), Net Profit (quarter), Net Profit Variance (yr), Net Profit Variance (qr), Operating Profit Margin (yr / qr), Gross Profit Margin |
| Sales | Sales Turnover (yearly), Net Sales (quarter) |
| Balance sheet | Networth, Reserves, Face Value, Dividend, Gross Block, Total Loans |
| Banking-specific | Advance Given By Bank, Net Non-Performing Assets |
| Exchange value | BSE Value (lakhs), NSE Value (lakhs) |
| **TTM (trailing 12 months)** | Sales, Operating Profit, Gross Profit, Net Profit, EPS, PE, CPS, Depreciation |

**Not yet available:** ROE, ROCE, dividend yield, debt-to-equity, and historical/period-over-period fundamental comparisons (planned by Chartink, not live).

**Syntax note:** these tokens have no `latest`/timeframe prefix (they're point-in-time fundamentals, with yr/qr/TTM baked into the field name). The exact lowercase token string is taken from the fundamental filter picker on the create-scan page — e.g. a market-cap floor reads roughly `market cap > 5000` and a valuation cap `yearly pe ratio < 25`. Because the precise token spelling depends on the picker label, **validate with a quick `run_screener` test** (§11) before relying on a fundamental clause, and correct from Chartink's parse error if needed.

Example (mid-cap value + technical uptrend):
```
( {cash} ( market cap > 5000 and market cap < 20000 and yearly pe ratio < 25 and latest close > latest sma( latest close , 200 ) ) )
```

---

## 11. Validation tip

To confirm any uncertain token, run a minimal clause and watch for a parse error:

```
( {cash} ( latest <token> > 0 ) )
```

Chartink's error response names the offending token, which is the fastest way to lock in exact syntax for the current build.
