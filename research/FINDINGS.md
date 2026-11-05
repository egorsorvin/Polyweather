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

## 6. Resolver check (step 1, Nov 2026) — `research/resolver.py`

Settlement value rebuilt from raw METAR (IEM archive, `research/fetch_metar.py`) under each
event's own rule regime, compared with the bucket the market actually resolved to.

| regime | events | match |
|---|---|---|
| **AWC** (aviationweather METAR API, routine only, from 2026-10-23) | 598 | **100.0 %** |
| NOAA (weather.gov/wrh/timeseries, 2026-08-23 .. 10-22) | 3,328 | 99.0 % |
| WU (Wunderground, to 2026-08-22) | 8,589 | 98.2 % |

Not rebuildable: Hong Kong (HKO, 229 events), early Taipei (CWA, 7), 65 days with missing METAR
(mostly Jinan ZSJN).

Known disagreements (old regimes only):
* **Shenzhen, WU period: 24 % match.** Rule names ZGSZ, but the WU page evidently carried another
  station's data (±1..4 °C both ways); not reproducible from airport METAR.
* **Seoul, WU period: 89 %**, ±1 °C both ways (WU-specific handling of RKSI).
* NOAA period: Moscow/Denver match better with routine-only reports, other cities with all
  reports; consistent with NOAA silently missing some reports. Overall 99.0 % either way.

IEM notes: report type 1 = MADIS 5-minute data (`MADISHF`), never counts. US stations: type 3 =
routine, 4 = SPECI. Non-US: IEM's 3/4 split is arbitrary, routine is decided by the station's
scheduled minutes (e.g. RKSI :00/:30, EGLC :20/:50).

**Consequence for modelling:** the label is the bucket the market actually resolved to; the METAR
value is used where it agrees, and for intraday running max (nowcasting). The current regime is
reproduced exactly, so live trading logic can rely on it.
