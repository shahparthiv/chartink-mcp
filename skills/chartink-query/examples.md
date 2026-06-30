# Chartink scan_clause — Example Library

Copy-ready patterns. Swap thresholds/periods as needed. All default to `{cash}`.

> Each example below is the **MCP / API form** (fully wrapped, for `run_screener`). To get the **chartink.com form**, drop the outer `( {cash} ( ` and trailing ` ) )` and paste just the inner conditions into the *Scan conditions* box, then pick the matching segment (e.g. "Cash") from the dropdown. Example: `( {cash} ( latest rsi( 14 ) > 60 ) )` → website: `latest rsi( 14 ) > 60`.

## Price & trend

**Above 50 & 200 SMA (uptrend)**
```
( {cash} ( latest close > latest sma( latest close , 50 ) and latest close > latest sma( latest close , 200 ) ) )
```

**Golden cross (50 SMA crosses above 200 SMA)**
```
( {cash} ( latest sma( latest close , 50 ) > latest sma( latest close , 200 ) and 1 day ago sma( latest close , 50 ) <= 1 day ago sma( latest close , 200 ) ) )
```

**Price crosses above 50 EMA**
```
( {cash} ( latest close > latest ema( latest close , 50 ) and 1 day ago close <= 1 day ago ema( latest close , 50 ) ) )
```

**Bullish candle on rising volume**
```
( {cash} ( latest close > latest open and latest volume > latest sma( latest volume , 20 ) and latest close > 50 ) )
```

## Breakouts

**52-week high breakout**
```
( {cash} ( latest close > 1 day ago max( 252 , latest high ) ) )
```

**20-day high breakout with volume surge**
```
( {cash} ( latest close > 1 day ago max( 20 , latest high ) and latest volume > 2 * latest sma( latest volume , 20 ) ) )
```

**3% gap up**
```
( {cash} ( latest open > 1 day ago close * 1.03 and latest volume > 100000 ) )
```

## Momentum / oscillators

**RSI crossed above 60**
```
( {cash} ( latest rsi( 14 ) > 60 and 1 day ago rsi( 14 ) <= 60 ) )
```

**Oversold bounce (RSI < 30, close up vs yesterday)**
```
( {cash} ( latest rsi( 14 ) < 30 and latest close > 1 day ago close ) )
```

**MACD bullish crossover above zero**
```
( {cash} ( latest macd line( 26 , 12 , 9 ) > latest macd signal( 26 , 12 , 9 ) and 1 day ago macd line( 26 , 12 , 9 ) <= 1 day ago macd signal( 26 , 12 , 9 ) and latest macd line( 26 , 12 , 9 ) > 0 ) )
```

**Strong trend (ADX > 25, +DI above −DI)**
```
( {cash} ( latest adx( 14 ) > 25 and latest plus di( 14 ) > latest minus di( 14 ) ) )
```

**Stochastic bullish crossover in oversold zone**
```
( {cash} ( latest stochastic %k( 14 , 3 ) > latest stochastic %d( 14 , 3 , 3 ) and 1 day ago stochastic %k( 14 , 3 ) <= 1 day ago stochastic %d( 14 , 3 , 3 ) and latest stochastic %k( 14 , 3 ) < 30 ) )
```

## Bands & volatility

**Close above upper Bollinger band (expansion)**
```
( {cash} ( latest close > latest bollinger band upper( latest close , 20 , 2 ) and latest volume > latest sma( latest volume , 20 ) ) )
```

**Close above Supertrend (10,3)**
```
( {cash} ( latest close > latest supertrend( 10 , 3 ) and 1 day ago close <= 1 day ago supertrend( 10 , 3 ) ) )
```

**Close above VWAP (intraday view)**
```
( {cash} ( latest close > latest vwap ) )
```

**Donchian channel breakout (20-period)**
```
( {cash} ( latest close > 1 day ago donchian channel upper( 20 ) and latest volume > latest sma( latest volume , 20 ) ) )
```

**Price above daily pivot point**
```
( {cash} ( latest close > latest pivot point and latest close > latest open ) )
```

**Rising price confirmed by OBV (proxy: OBV above its 20 EMA)**
```
( {cash} ( latest obv > latest ema( latest obv , 20 ) and latest close > 1 day ago close ) )
```

## Multi-timeframe

**Daily breakout aligned with weekly uptrend**
```
( {cash} ( latest close > 1 day ago max( 20 , latest high ) and weekly close > weekly sma( weekly close , 20 ) ) )
```

## Liquidity / housekeeping filters (combine with any of the above via `and`)

```
latest close > 50 and latest close < 5000
latest volume > 200000
latest sma( latest volume , 20 ) > 100000
```

## Counting pattern

**At least 3 of last 5 days closed green**
```
( {cash} ( count( 5 , latest close > latest open ) >= 3 ) )
```
