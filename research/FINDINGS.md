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

## 7. Favourite overpricing (Qiu & Qiu) is not tradeable (step 2) — `research/favourite_test.py`

Setup: on the target day at local 06/09/11/12/13 h, take the event's favourite bucket
(last YES trade 0.75–0.95, ≤2 h old) and buy NO. 4,740 favourite snapshots, all closed events.

* **Realised NO hit rate ≈ implied NO price** (e.g. 12 h: 0.179 vs 0.155; 13 h: 0.156 vs 0.151).
  Favourites are at most ~1–2 pp overpriced, not ~10 pp.
* Buying NO at the implied price (zero slippage): ROI +3.1 %, t = 0.3 (noise).
  With 1¢ slippage: −3.4 % (t −1.8); 2¢: −9.1 % (t −3.8). Since Apr 2026 (fees on):
  −5.1 % even at zero slippage.
* Takers who actually bought NO in the 30 min after T paid on average **0.237** while the
  implied NO price at T was **0.165**: NO buying happens when the favourite is already
  collapsing (information arriving, e.g. a new report) — momentum / adverse selection,
  not a free discount.
* Mirror (buy YES on favourite): ≈ 0 to slightly negative.

**Conclusion:** no price-only edge here either. The interesting signal is the post-T price
move itself: prices react to information during the day → that is hypothesis C (nowcasting).

## 8. Intraday "dead bucket" reaction (step 3, first pass) — `research/nowcast_dead_buckets.py`

A bucket is dead once the running daily max (event's own rule regime, resolver rounding) exceeds
its upper edge. 67,608 dead buckets in 12,072 events (resolver-matched events only).

* **Mostly anticipated.** Median YES price just before the killing report: 0.002; only 14.6 % of
  dead buckets still had YES ≥ 0.05. $10.2M of NO ≤ 0.98 was bought in the hour *before* the
  killing report (forecasts + faster feeds).
* **When surprised, the market reprices within ~1.5 min of the observation time** (median; 75 %
  within 3 min, 90 % within 5.3 min). AWC METAR is published a few minutes after observation, so
  in most cities the fast traders use feeds faster than METAR.
* **The pie** = profit of takers who still bought dead NO ≤ 0.98 *after* obs + delay
  (fees deducted), Feb 2025 – Nov 2026, all cities:

  | delay after obs | profit | spent |
  |---|---|---|
  | 2 min | $331k | $3.26M |
  | 5 min | $136k | $1.23M |
  | 10 min | $98k | $0.81M |
  | 20 min | $80k | $0.60M |

  Since Apr 2026: ≈ $15.8k / month at 5 min, $11.9k / month at 10 min, shared by all competitors.
  Lumpy: at 5 min the top 20 events hold 44 % of it, median event with any pie ≈ $20.
* Slowest repricing (median minutes to YES ≤ 0.02): Denver 11.4, Lagos 10.8, Jakarta 5.3,
  Kuala Lumpur 5.0, Milan 4.7, Madrid 4.2. Largest 5-min pie: Seoul, Shenzhen, Istanbul, Denver,
  Shanghai, NYC, Kuala Lumpur, Lagos, Moscow.
* By local hour, the pie sits at 08–16 h (peak 13 h) plus around midnight (warm-night openings).

Open questions before calling this an edge: real AWC publication delay per station; who captures
the pie (a few bots?); whether the biggest pie events are genuine (stale orders) or data artefacts.

## 9. Step 3b — latency, who takes the pie, speed vs disbelief

**AWC publication delay** (obs → AWC receipt, routine METAR, 7 days, `awc_latency.csv`): median
5.1 min, p90 8.4. Fast: Jeddah 0.4, Singapore/Tel Aviv 1.0, Helsinki 1.4, Paris/Amsterdam 2.4,
US ≈3.1–3.6. Medium: London/Seoul/Wellington/Madrid 4.3–4.5, China 5.5–6.4, Moscow 6.2.
Slow: Istanbul/Tokyo/Toronto/Kuala Lumpur ≈8, Ankara 14, Mexico City 15, Lagos 30.
Since the market reprices surprised dead buckets ~1.5 min after observation, in most cities fast
traders use feeds that beat AWC.

**SPECI heuristic check:** our scheduled-minute rule agrees with AWC `metarType` on 99.4 % of
12,864 overlapping reports (disagreements mainly MMMX, UUWW).

**Reachable pie for a bot reading AWC** (trades after obs + city AWC delay + 1 min):
$123k total, ~$13.8k / month since Apr 2026. Spread over 3,932 wallets (top-1 4 %, top-20 29 %).
It splits into two very different things:

| part | trades | profit | events | median NO price |
|---|---|---|---|---|
| speed, < 15 min after obs | 3,983 | $37k | 577 | 0.94 |
| 15–60 min | 5,997 | $27k | 332 | 0.94 |
| **disbelief, > 60 min after obs** | 9,465 | $59k | 214 | 0.91 |

* **Speed pie** since Apr 2026 ≈ **$3.6k / month for everyone together** (median $17.5 per
  event; Denver, Seoul, Tel Aviv lead). Not a business on its own for an AWC-reading bot.
* **Disbelief pie:** the day max came from a single +1 °C blip (e.g. Istanbul 2026-10-21: 22 °C at
  09:20Z, then 20, 20, 20), and for hours many wallets kept buying NO at ~0.5 as if the blip
  would not count. It did count. Mostly WU/NOAA-regime events, where the source could drop
  reports; under the explicit current AWC rule a routine blip counts. Potential edge from reading
  the rules better than the crowd, but rare, lumpy and exposed to oracle/correction risk.

**Next (hypothesis C2):** not strictly dead but *almost dead* buckets — above the current max
late in the day. The market price vs the empirical probability that the max still rises given
local hour, current max and recent trend. This matches what the profitable wallet
HighTempTation does (NO at 0.90–0.99 on the target day).

## 10. Intraday nowcast from observations only loses to the market (step 3c) — `research/nowcast_model.py`

State at local hour T (11–19 h) from METAR already *published* by T (city AWC delay + 1 min):
running max M, latest value, 2-h trend, gap M − latest; target = further rise k = V − M.
Walk-forward logistic model of P(k ≥ j), j = 1..20 (°F needs large j: at 11 h a rise ≥ 5 °F
happens on 61 % of days, ≥ 10 °F on 20 %). 110,935 states, 508,076 live-bucket snapshots.

* The model is **well calibrated** (e.g. predicted 0.148 → realised 0.159, 0.705 → 0.702), but the
  market is calibrated **and sharper**: Brier on live buckets 0.0781 (model) vs **0.0563** (market);
  worse at every hour (17 h: 0.0219 vs 0.0147). The market knows the afternoon forecast and
  faster observations; history-of-the-day alone cannot match it.
* Trading on disagreements (|model − market| > 3/5/10 pp): −3 % to −12 % ROI everywhere.
* "Certainty harvesting" (model ≤ 3 %, market ≥ 6 %), NO at last + 1¢: 7,615 bets, ROI +1.8 % —
  the YES still won 12–20 % of the time (market was closer); not robust to execution.

**Conclusion:** observations alone give no edge. The only untested route is adding the NWP
forecast of the rest of the day (Single Runs hourly) to this intraday model, and combining
it with the market price (log-pool) rather than betting against the market.
