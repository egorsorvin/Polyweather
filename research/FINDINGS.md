# Research findings (recon, Nov 2026)

## 1. Data that exists

| What | Source | Coverage |
|---|---|---|
| Every temperature event + buckets + outcome | Gamma `/events?tag_slug=weather` (windowed by endDate, limit 100, offset < 2000) | 12,990 "highest" + 4,658 "lowest" events, 53 cities, Jan 2025 – now |
| Full trade tape (time, price, size, side, wallet) | Data API **v2** `/v2/trades?eventId=…` (cursor pagination) | from market open; ~2,250 trades/event, 29M trades, 1.8 GB gz |
| Price series | CLOB `/prices-history?market=<token>&startTs&endTs&fidelity=10` | works for closed markets only with explicit range |
| Station per city | event `resolutionSource` / description | `data/stations.csv` |
| Order book history | not public (paid: Oddpool since 2026-03, MarketLens) | — |

## 2. Resolution rules changed over time (ground truth must follow the rule of each date)

* to ~Jul 2026: Wunderground daily history, whole degrees
* Aug – Sep 2026: NOAA `weather.gov/wrh/timeseries`, whole degrees
* Oct 2026 →: max of **routine METAR hourly T-group remark, tenths °C** (SPECI excluded);
  US markets in whole °F
* Hong Kong: Hong Kong Observatory "Absolute Daily Max", 0.1 °C
* station changes: Paris LFPG → LFPB, Denver KBKF → KDEN
* old `cities.py` used Narita coordinates for Tokyo; market resolves on Haneda (RJTT)

## 3. Fees

Weather markets have taker fees since Apr 2026: `feeSchedule = {rate 0.05, exponent 1, takerOnly}`
≈ `0.05·p·(1−p)` per share (2.5 % of notional at p=0.5, 4 % at p=0.2). Makers pay nothing.

## 4. Market calibration (last trade ≤3 h old, ~98k bucket-snapshots per time point)

`research/market_calibration.py`, snapshot at local **D-1 12:00**:

| implied p | n | mean(outcome − p) | s.e. |
|---|---|---|---|
| 0 – 10 % | 63,717 | −0.13 pp | 0.05 |
| 10 – 30 % | 19,662 | −0.76 pp | 0.28 |
| 30 – 50 % | 12,518 | +0.83 pp | 0.43 |
| 50 – 100 % | 2,601 | +0.94 pp | 0.90 |

* The market is **well calibrated**. A small favourite–longshot bias exists (~1 pp) but is
  smaller than the taker fee + spread: no price-only mechanical strategy is profitable.
* Bucket prices sum to 1.003 (median) — almost no overround.
* Brier of market bucket probabilities: 0.0755 (D-1 12:00) → 0.069 (D 12:00) → 0.036 (D 15:00).
  **This is the number a forecast model has to beat**, on the same buckets and timestamps.

## 5. Implication

Any edge must come from *information*: a better probability than the market at the moment of
trading (better post-processing, faster reaction to new model runs, intraday METAR nowcasting),
large enough to beat ~2–4 % taker fee (or be captured as a maker).
