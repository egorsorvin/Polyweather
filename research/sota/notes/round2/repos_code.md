# Code-level deep dive: open-source weather/temperature prediction-market projects (Polymarket, Kalshi)

Method note (2026-11-05). The GitHub REST API refused per-repo calls in this session ("GitHub access to this repository is not enabled for this session"), and github.com issue pages returned HTTP 403. Anonymous `git clone` through the session proxy did work. Every repo below was therefore cloned and read locally as data. **No code was executed.**

Citations point to files at the HEAD commit read:
- isotherm `977fee6`
- muzard `baab319`
- anaborne `b53b2f5`
- k1hbles `d08164f`
- Deivid-Negoita `dfb6536`
- jattree `0fca067`
- BallesJr `aa96700`
- testedmedia `55fe92b`
- JHenzi `d9f41a1`
- suislanchez `e406394`
- AadiXD200 `6630804`
- Sully-Ok `a6a82a8`

**Issues could not be read** (API and HTML both blocked). PR numbers appear only where merge commits mention them.

This file extends `Торговля погодными рынками Polymarket/open_source_repos.md` and does not repeat its README-level catalogue.

Git-history facts from the clones:

| Repo | First commit | Last commit | Commits | Notes |
|---|---|---|---|---|
| isotherm | 2026-10-04 | 2026-10-21 | 305 | |
| deadBracketBot | 2026-06-30 | 2026-11-02 | 21 | |
| anaborne | 2026-08-29 | 2026-09-09 | 6 | |
| k1hbles | 2026-10-07 | 2026-10-07 | 1 | |
| Deivid-Negoita | 2026-10-27 | 2026-11-04 | 5 | |
| jattree | 2026-03-26 | 2026-09-25 | 313 | |
| BallesJr | 2026-04-19 | 2026-11-05 | ~9,280 | mostly automated "bot: portfolio update" commits |
| testedmedia | 2026-07-11 | 2026-07-13 | 10 | |
| JHenzi | 2024-02-28 | 2026-09-01 | 115 | |
| suislanchez | 2026-02-10 | 2026-03-01 | 33 | last code commit is 2026-03-01, although search metadata shows "updated 2026-11-04" (stars) |
| AadiXD200 | 2026-04-05 | 2026-04-05 | 2 | |
| Sully-Ok | 2026-08-12 | 2026-08-12 | 1 | |

Commit messages carrying "Co-Authored-By: Claude" or "Generated with Claude" lines:

| Repo | AI-attributed commits |
|---|---|
| suislanchez | 18 |
| muzard | 13 |
| JHenzi | 9 |
| BallesJr | 3 |
| AadiXD200 | 2 |
| All others | 0 |

**Spam/malice check.** None of the 12 cloned priority repos showed malicious patterns in the files read: no obfuscated payloads, and no requests to paste keys into third-party endpoints. The keyword-stuffed repos flagged in the prior notes (MoonsatProtocol and others) were not re-cloned and remain untrusted.

---

## Q1. Which designs avoided look-ahead and resolution mismatches, and what did they find?

### Takeaway
The projects that pinned decision-time availability and scored against the exact settlement label all find the same thing: **the market's probabilities beat free public forecasts**. Those projects are isotherm, k1hbles, anaborne, Deivid-Negoita and jattree.

Edge appears only when the model *corrects* the market price:
- isotherm: +1–2¢/contract;
- Deivid-Negoita: +1.7 to +4.1¢ in a 2026 backtest, which then lost on paper in October 2026.

Every edge measured shrank sharply from 2023 to 2026 as Kalshi books tightened from ~9–15¢ to ~1–5¢. The repos that did not pin these details made identifiable mistakes:
- grading on ERA5 or Open-Meteo reanalysis (AadiXD200, early jattree, early BallesJr);
- city-centre coordinates and the wrong station (suislanchez);
- leaked 23:00 labels (JHenzi);
- comparing the wrong station or the wrong "daily max" product (testedmedia).

### Cited Findings

**Decision-time alignment done right (code-verified)**
- **isotherm: forecast availability lags.** `AVAILABILITY_LAG = {"GFS": 5h, "NBS": 2h}`. The comment reads: "GFS MOS hits the wire roughly 4h after its nominal runtime; NBM text bulletins … about 1h after. One hour of margin on each: using a run before it was public is the classic forecast leak" — [weather.py](https://github.com/physicalreasoning/isotherm/blob/977fee6/src/isotherm/weather.py)
- **isotherm: observation lags.**
  - `OBS_LAG = 15 min` for METAR and `OBS5_LAG = 10 min` for 5-minute ASOS. Only observations at least that far before the read count.
  - The climate day is taken in local *standard* time.
  - The market input is "the last hourly candle closed at or before the read time".
  - EMOS is refit monthly on CLI highs strictly before that month, with a 2-day embargo.
  - [dataset.py](https://github.com/physicalreasoning/isotherm/blob/977fee6/src/isotherm/dataset.py)
- **isotherm caught a timestamp bug before it produced results.** "pandas 3 stores datetimes in microseconds, so `astype("int64") // 10**9` produced timestamps 1000× too small and the observation window spanned all of history (100% observation coverage at the day-before read, which must be 0%)" — [FINDINGS §8](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **isotherm uses 1-minute ASOS with a caveat.** The settled high is ≥ round(5-minute max) − 1 on 99.8–99.9% of days. But "IEM receives the 1-minute archive with a delay, so a live system needs a real-time 5-minute feed to use this" — [FINDINGS §12](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **k1hbles uses the same alignment scheme.** `DELAY = {"GFS": 5, "NBS": 3}` hours from model init until the text product is usable. A forecast is used only if `runtime + DELAY <= t_utc`. Bias and σ are estimated "from days <= date-2". Decision slots are D-1 11:00, D-1 18:00, D 09:00 and D 12:00 — [analyze.py](https://github.com/k1hbles/kalshi-edge/blob/d08164f/analyze.py)
- **anaborne measured its own intra-hour look-ahead.** "Removing the intra-hour lookahead (pairing `M_{H-1}` with hour H's quotes) makes it *worse*, at −10.98¢/contract over 21,985 trades. The frozen rule's small lookahead was flattering it" — [RESULTS.md §7](https://github.com/anaborne/kalshi-temperature-calibration/blob/b53b2f5/RESULTS.md)
- **Deivid-Negoita: point-in-time inputs and stale-quote filter.**
  - Uses "the newest NBM, GFS MOS and NAM MOS runs public at the decision time", refit monthly on the prior 3 years.
  - Quotes more than 6 hours old are dropped.
  - Open-Meteo "previous runs" (forecasts issued 1 and 2 days earlier) supply ECMWF/ICON/GEM/GFS.
  - Calendar-day fix: MOS daytime max is widened with 3-hourly forecasts outside its window, because Kalshi settles on the LST calendar day. The example: Austin 2025-11-30, NBM 50°F vs CLI 60°F.
  - The author flags this fix as found by "looking at 2026 misses" and not pre-registered.
  - [README](https://github.com/Deivid-Negoita/kalshi-weather/blob/dfb6536/README.md)
- **JHenzi: label-leak bug.** Commit "Grade forecasts at decision time, not after the fact" (2026-09-01). "calibrate_sources kept the *last* predictions_history row per city/date; on 60 of 64 recent days that row was written at 23:00, after the day's high had already occurred … which inverted the provider ranking outright."
  - A second bug: NWS fallback "returned the overnight low as the daily high: signed bias −15.01F".
  - Walk-forward on 432 city-days: equal weight MAE 2.041°F; leaked 1/MAE² weighting 2.170°F; clean labels 1.654°F.
  - The README withdraws earlier MAE claims (0.67–0.87°F); honest MAE at 09:00 is 2.21°F and at the 13:00–14:00 buy time ~1.5–1.8°F.
  - [README](https://github.com/JHenzi/weatherbots/blob/d9f41a1/README.md); commit `HEAD~1` in the clone of [JHenzi/weatherbots](https://github.com/JHenzi/weatherbots)

**Target definition: verified station, source and rounding**
- **Kalshi label (isotherm).** Kalshi settlement equalled the NWS CLI high on 1,545 of 1,546 NY days. Source switched to The Weather Company on **2026-08-14**; it matched CLI on all 51 days since in NY. One post-switch Miami day settled 5°F from CLI. 14.5% of NY markets have no strike fields, so bounds are parsed from rules text. Two 2021–22 Chicago records contradict themselves (likely post-settlement NWS revisions) — [FINDINGS §2, §4](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Kalshi label (Deivid-Negoita).** "The climate report matches Kalshi's own settlement value on 12,738 of 12,753 market-days (99.9%)" across all 40 NWS climate stations used by Kalshi weather series — [README](https://github.com/Deivid-Negoita/kalshi-weather/blob/dfb6536/README.md)
- **Kalshi API pitfalls (anaborne).**
  - Settlement authority is whatever `rules_primary` says, and the help centre is stale.
  - TWC switch "around 2026-08-13 … across 20 of 21 city series".
  - `/historical/cutoff` was 2026-06-27 on 2026-08-27; older markets are served by `/historical/markets…`.
  - Station traps: Chicago = CLIMDW (Midway), Houston = CLIHOU (Hobby). `stations.py` halts for human review of the mapping.
  - [METHOD.md](https://github.com/anaborne/kalshi-temperature-calibration/blob/b53b2f5/METHOD.md)
- **Silent sample loss (anaborne).** "Live candles carry `volume_fp` and suffix price keys `_dollars`; historical candles carry bare `volume`", which silently excluded 52,704 historical markets. 2,950 markets (4.8%) carry only `yes_sub_title` prose, with no strike fields — [RESULTS.md §5](https://github.com/anaborne/kalshi-temperature-calibration/blob/b53b2f5/RESULTS.md)
- **Hourly obs vs settlement offset (anaborne).** Settled value minus the final observed hourly ASOS max is +0.72°F (sd 0.74) under NWS and +0.86°F (sd 0.67) under TWC. This offset "re-enters at the bucket-membership step" and made the residual-warming model severely overconfident: model 0.95–1.01 → settles 0.713 — [RESULTS.md §6](https://github.com/anaborne/kalshi-temperature-calibration/blob/b53b2f5/RESULTS.md)
- **Polymarket label differs from Kalshi's (isotherm survey).**
  - Polymarket = highest *hourly* airport reading, whole °F: "Weather Underground's daily history until 2026-08-22, NWS timeseries hourly data since".
  - Even at the same station, the CLI high lands in Polymarket's winning bucket only 59–71% of the time, usually 1°F higher.
  - Stations: NYC KLGA (Kalshi KNYC), CHI KORD (Kalshi KMDW), DAL KDAL (Kalshi KDFW), DEN KBKF (Kalshi KDEN), HOU KHOU.
  - Ladder: 2°F buckets, 7 until spring 2026 and 11 since. Median volume $41k–$91k per city-day. 2,999 settled US city-days through 2026-10-06.
  - [docs/research/polymarket_2026-10.md](https://github.com/physicalreasoning/isotherm/blob/977fee6/docs/research/polymarket_2026-10.md)
- **Polymarket resolver change (muzard).**
  - Every event created from **2026-09-12** resolves on "the highest reading under the 'Temp' column" at `weather.gov/wrh/timeseries?site=<ICAO>`, with WU as fallback only if NOAA data is unavailable by 11:59 PM ET the next day.
  - That page renders Synoptic/MesoWest `api.synopticdata.com/v2/stations/timeseries` using a token published in weather.gov's `apiKey.js`.
  - Taipei (RCSS) was the lone WU holdout.
  - [docs/resolution_source_migration_2026-09-14.md](https://github.com/muzard/deadBracketBot/blob/baab319/docs/resolution_source_migration_2026-09-14.md)
- **NOAA dropped readings (muzard).**
  - Over 2026-09-14 → 09-23, 250 of 11,523 METARs (2.17%) were never ingested.
  - Two feed-wide outages: 09-20 02:30–07:30Z (up to 31 of 34 stations) and 09-22 10:30–11:30Z.
  - Five markets (Singapore, Beijing, Guangzhou, Qingdao, Manila) resolved on NOAA's *lower* max. "The METAR is not a safe proxy for the resolver; only the resolver's own table is."
  - [docs/noaa_ingest_outage_2026-09-20.md](https://github.com/muzard/deadBracketBot/blob/baab319/docs/noaa_ingest_outage_2026-09-20.md)
- **WU = METAR in most cities, before the switch (muzard).** For METAR-keyed stations the WU/TWC history table was a verbatim METAR copy: 44/44 rows matched on timestamp and value, SPECIs included (EGLC, LFPB, UUWW, CYYZ; one ~8-hour window). Exception: Shenzhen/Lau Fau Shan (HKO AWS 45035), resampled to top-of-hour — [docs/wu_metar_fidelity_2026-07-04.md](https://github.com/muzard/deadBracketBot/blob/baab319/docs/wu_metar_fidelity_2026-07-04.md)
- **Live loss from a source disagreement (muzard).** 2026-07-19 Seoul: "RKSI's METAR printed 27 °C, Weather Underground's row for the same instant read 26 °C (tenths pipeline: 79 °F = 26.1 °C) … the entire bankroll bought a NO that settled to $0". Live trading has been locked since 2026-08-18 — [LIVE.md](https://github.com/muzard/deadBracketBot/blob/baab319/LIVE.md)
- **jattree resolution rules.** Local civil day; daily max over METAR "including SPECI reports and the METAR 6-hour max group, rounded half up". Hong Kong uses the HKO "Absolute Daily Max", label L = [L, L+1) on its 0.1°C value — [README](https://github.com/jattree/weather-edge/blob/0fca067/README.md)
- **jattree proving-run bugs** included "Forecasts used the UTC day while markets settle on the local day, three stations were wrong, and backtests resolved against gridded reanalysis" — [README](https://github.com/jattree/weather-edge/blob/0fca067/README.md)
- **testedmedia: WU vs IEM.** The 14-city file compares IEM METAR daily max with WU V1 daily max, 2024-03-01 → 2026-02-28. Exact match: NYC KLGA 97.2%, Chicago KORD 96.7%, Paris **LFPG** 99.7%, and **London EGLL 47.7%** (WU higher 33.3%, lower 19.0%) — [asos_wu_all_cities_verify.json](https://github.com/testedmedia/polymarket-weather-command-center/blob/55fe92b/data/backtest/asos_wu_all_cities_verify.json)
- **testedmedia 17-city audit** compares IEM `daily.py` station-local max with WU V1 hourly obs. Exact match: Denver KBKF 61.9%, LAX 35.5%, Austin 36.0%, Houston KHOU 36.4%, SFO 33.8%, with WU *lower* on 270–478 of ~720 days. Most non-US stations were 99–100% — [buynosafe_audit_17cities_v1.json](https://github.com/testedmedia/polymarket-weather-command-center/blob/55fe92b/data/backtest/buynosafe_audit_17cities_v1.json)
- **testedmedia's engine is not public.** The repo is a Next.js dashboard; the `app/api/brain/trading` route proxies to a private engine. Only result JSONs are shipped, e.g. `wu_backtest_41cities_v1.json` ("WU hourly-proxy daily max as ground truth for all 41 cities", generated 2026-04-19) — [repo tree](https://github.com/testedmedia/polymarket-weather-command-center/tree/55fe92b)

**Known-wrong designs (code-verified)**
- **suislanchez.**
  - `CITY_CONFIG` uses city-centre coordinates (NYC 40.7128, −74.0060) and `nws_station` KNYC/**KORD**/KMIA/KLAX/KDEN for both Kalshi and Polymarket. Polymarket NYC resolves at KLGA and Kalshi Chicago at KMDW.
  - Probability = `sum(h > threshold)/n` over Open-Meteo `gfs_seamless` ensemble members, with no bias correction.
  - No fee term in `backend/core/weather_signals.py`.
  - [backend/data/weather.py](https://github.com/suislanchez/polymarket-kalshi-weather-bot/blob/e406394/backend/data/weather.py)
- **AadiXD200.**
  - `real_backtest.py` docstring: "real CLOB historical prices + real Open-Meteo day-ahead forecasts + **ERA5 actuals as ground truth**". `fetch_historical_actuals` calls the Open-Meteo Archive (ERA5) at city lat/lon.
  - Live scanning reads CLOB `mid` as the price ([main.py](https://github.com/AadiXD200/polymarket-weather-bot/blob/6630804/main.py)).
  - The claimed +35.6%/7 days therefore rests on mid fills and a non-resolution label.
  - [real_backtest.py](https://github.com/AadiXD200/polymarket-weather-bot/blob/6630804/real_backtest.py); [data/openmeteo.py](https://github.com/AadiXD200/polymarket-weather-bot/blob/6630804/data/openmeteo.py)
- **BallesJr live paper ledger** (`data/paper_portfolio_weather.json`, 2026-04-23 → 2026-11-05, read 2026-11-05 07:49 UTC):
  - bankroll $10,000 → $8,175.77; total PnL **−$1,731.30**; 1,350 won / 3,373 lost / 9 expired;
  - 4,732 closed trades, 3,948 BUY_NO and 784 BUY_YES;
  - monthly PnL (my aggregation of `pnl_usd` by `closed_at`):

    | Month | PnL |
    |---|---|
    | Apr | −$47 |
    | May | −$51 |
    | Jun | −$578 |
    | Jul | −$320 |
    | Aug | +$32 |
    | Sep | −$156 |
    | Oct | −$497 |
    | Nov (partial) | −$114 |

  - fees started being charged in June;
  - `obs_source` is "metar" on 3,263 trades but "openmeteo" on 55 and blank on 1,414;
  - [paper_portfolio_weather.json](https://github.com/BallesJr/polymarket-weather-edge/blob/aa96700/data/paper_portfolio_weather.json)

**Results tables from the clean designs**
- **k1hbles** (`results.txt`, 2,678 event×slot, Jul–Oct 2026, 7 cities):

  | Slot | Market Brier | q_blend Brier |
  |---|---|---|
  | D 12:00 | 0.503 | 0.662 |
  | D-1 11:00 | 0.654 | 0.710 |

  Taker results (fee `ceil(0.07P(1−P))`):
  - q_blend at threshold 0.10: −2.52¢/ct, t −4.1 (n 4,415).
  - q_nbs at 0.05: −3.68¢, t −8.1.
  - q_gfs at 0.20: **+0.6¢, t 0.71**.
  - By city, only Miami is positive: +6.7¢, t 3.4.
  - Optimistic-queue maker at 0.10: −0.74¢, t −0.7.
  - The GFS-MOS-least-negative pattern matches isotherm §5.
  - [results.txt](https://github.com/k1hbles/kalshi-edge/blob/d08164f/results.txt)
- **anaborne holdout** (9 cities, 19,348 trades, 1,463 dates):

  | Trade shape | Trades | Result |
  |---|---|---|
  | Dominated-bucket sell | 78 | −23.46¢/ct |
  | Mid-bucket buy | 7,819 | −9.06¢ |
  | Other | 11,451 | −8.38¢ |

  - Pooled −8.75¢, −$27,039.
  - Calibration on 235,145 bucket-hours: model Brier 0.1739 vs market 0.0772 (widest-spread mid) and 0.0683 (closing mid).
  - Four corrections dated 2026-09-03 fix side-awareness and trade-vs-contract weighting of settle rates.
  - [RESULTS.md](https://github.com/anaborne/kalshi-temperature-calibration/blob/b53b2f5/RESULTS.md)
- **Deivid-Negoita.**
  - Model alone, evening highs at θ 0.05: +2.9¢ (2023, t 2.7), +3.0¢ (2024), +1.3¢ (2025), **−1.5¢ (2026, t −4.1)**. The mean bracket spread fell 15.2¢ → 4.9¢ over the same years.
  - Logit of result on logit(mid) and logit(model), 2026: model coefficient 0.25 (t 12.8), 0.38 with LightGBM.
  - Market+model blend, 2026 holdout:

    | Set | Return/ct | Trades | t |
    |---|---|---|---|
    | Evening high | +3.2¢ | 3,606 | 4.3 |
    | Evening low | +4.1¢ | 3,308 | 4.9 |
    | Morning high | +1.7¢ | — | 2.1 |

  - Paper live 16–26 Oct 2026: 83 trades, **−$19.88 on $121.88 (−16.3%)**, fees $4.45. The model's information on evening highs fell to .05 in September and −.14 in early October.
  - Implied-vol inversion over 447,818 snapshots: realised/implied sd .94 at 30h for highs, so the market prices the day too wide. Both wings are overpriced by 1–5 points a day out; "selling the wings a day out" is flagged as untested.
  - Only 44% of contracts fill when capped at volume traded within an hour.
  - [README](https://github.com/Deivid-Negoita/kalshi-weather/blob/dfb6536/README.md)
- **jattree on Polymarket** (743 city-days / 9,086 markets, 2026-08-25 → 09-25, 24 cities):

  | Horizon | Log-loss, model − market | Simulated trades | Return per trade |
  |---|---|---|---|
  | 36h | +0.28 ± 0.03 | 1,905 | −13.9% ± 5.3% |
  | 24h | +0.22 ± 0.03 | — | — |

  - The best blend is 100% market.
  - The market's implied-mean bias is −0.23°C vs −0.09°C for the model, but its error is 0.81°C vs 0.97°C.
  - Raw consensus runs ~0.8°C colder than airport sensors; a trailing-30-day correction cuts 2-day MAE from 1.33 to 0.98°C.
  - Polymarket keeps "about a month" of price history.
  - Jev (an LLM-based decision model) log-loss 1.95 vs model 1.59 vs market 1.31.
  - Live proving run: $210 → $51.61 (−75.4%), mostly from software bugs.
  - [docs/FINDINGS_2026-09.md](https://github.com/jattree/weather-edge/blob/0fca067/docs/FINDINGS_2026-09.md); [README](https://github.com/jattree/weather-edge/blob/0fca067/README.md)

### Inferences
- **Converging evidence across five independent Kalshi studies.** The four non-isotherm studies used different code, periods and decision times. All find the market better calibrated than free forecasts by 2026. Any surviving value is a *correction to the price* worth roughly 1–4¢/contract before execution realism.
- **The Polymarket label is "max of the resolver's hourly/sub-hourly Temp column".** It is not the CLI high, the IEM `daily.py` max, the METAR 6-hour max group, or ERA5.
  - testedmedia's US WU-vs-IEM-daily disagreements (WU lower on ~65% of days at LAX/AUS/HOU/SFO) and isotherm's "CLI ~1°F higher" point the same way. IEM daily max includes values hourly readings miss (6-hour/24-hour max groups, CLI), so it overstates the Polymarket label.
  - By the same logic, jattree's inclusion of the "METAR 6-hour max group" is probably a source of upward bias for Polymarket. This is my reading; the repo does not test it.
- **testedmedia's London 47.7% agreement compares EGLL (Heathrow).** muzard's live market audit lists London as EGLC (London City). So the much-cited "382 of 730 days divergence" is likely at least partly a station mismatch, not WU-vs-METAR behaviour. This is inference; testedmedia's engine code is not public.
- **After 2026-09-12, a running max from METAR still needs confirmation against the NOAA/Synoptic table.** NOAA drops ~2% of observations, sometimes in multi-hour global outages, and these drops only ever lower the settlement.

### Gaps
- GitHub issues were not readable for any repo (API 403 for unattached repos; github.com 403). No issue-thread lessons are included.
- testedmedia's backtest generator scripts (e.g., `scripts/asos_strategy_backtest.py`) are referenced in JSON lineage but not in the repo, so its methodology cannot be audited.
- I did not re-run any numbers. All tables are as committed by the authors, except the BallesJr monthly aggregation, which I computed from the committed JSON.

---

## Q2. What exactly is isotherm's "market + correction" approach, and what did it find?

### Takeaway
isotherm has two models:
1. **Served model:** a frozen two-term log opinion pool, `p ∝ p_market^1.073 · p_EMOS-GFS^0.294`, renormalised over the ladder and read at 16:00 local the day before.
2. **Research model:** a learned log pool of market, EMOS-GFS, EMOS-NBM, EMOS-NBM conditioned on today's observed max, and climatology, plus a zero-initialised MLP correction trained on log score.

Both start equal to the market.

The served pool passed a lockbox (+$1,851 over 95 days, NW t 1.77). Its PnL halved monthly: $1,029 → $517 → $246. The edge is "about one to two cents per contract".

Live shadow, 2026-10-05 → 11-04: 176 ladders, +$606 paper, log-score gain +0.018 with a CI spanning zero.

The structural finding: **the market has priced NBM since ~2026-01 but still underweights GFS MOS**, and that weight is seasonal.

### Cited Findings

**Model form**
- **Served model.** `pool · market+GFS`, file `shadow/frozen.json` (hash `b200c51ce4ee`), fit on every daily-high ladder before 2026-06-29 (7,008 ladders at the 16:00 read).
  - EMOS: "per city, high ~ N(a + b · GFS MOS max, σ(day of year)), fit by interval likelihood on NWS CLI highs 2015 to 2026-06-29".
  - Inputs: "Live Kalshi ladder quotes (bid and ask per bucket) and the latest GFS MOS daytime max already on the wire (run time + 5 h). No observations are used at this read."
  - [docs/MODEL_CARD.md](https://github.com/physicalreasoning/isotherm/blob/977fee6/docs/MODEL_CARD.md)
- **EMOS design.**
  - `high ~ N(Xμ·β, exp(Xσ·γ))` with `Xμ = [1, fcst]` and `Xσ = [1, cos t, sin t]` (seasonal spread).
  - Optional `log s` term using NBM's own spread (XND).
  - Climatology uses two harmonics.
  - Integer highs are scored as the mass of [h−0.5, h+0.5).
  - [emos.py](https://github.com/physicalreasoning/isotherm/blob/977fee6/src/isotherm/emos.py)
- **Research model.** `score_j = Σ_s w_s · log p_s,j + MLP([x_j ; c])`, `p = softmax_j(score)`.
  - Bucket features x_j: z-scores against each forecast, whether today's observed max already rules the bucket out, quoted spread, tails.
  - Context c: city, season, lead time, forecast disagreement and spread, observations so far, ladder overround, traded volume before the read.
  - "The pool weights start at 'market only' and the MLP's output layer starts at zero, so an untrained IsothermNet *is* the market."
  - Training: sample weights halve every 365 days; early stopping on the latest 15% of dates; 5 seeds.
  - [model.py](https://github.com/physicalreasoning/isotherm/blob/977fee6/src/isotherm/model.py)
- **Evaluation design.**
  - Walk-forward by quarter with a 2-day embargo ([splits.py](https://github.com/physicalreasoning/isotherm/blob/977fee6/src/isotherm/splits.py)).
  - Taker fee `ceil(0.07·C·P·(1−P))` per order. Taker fills are capped at 5% participation of contracts traded in the bucket *after* the read.
  - Maker fills only on later prints strictly through the quote ([backtest.py](https://github.com/physicalreasoning/isotherm/blob/977fee6/src/isotherm/backtest.py)).
  - Lockbox config: `kelly 0.25`, $10,000 over 7 slots, held to settlement ([FINDINGS §9](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)).

**Results**
- **Decay, NY, 08:00 read** (best pool vs market, by half-year):

  | Half-year | Gain (nats) |
  |---|---|
  | 2023 H2 | +0.224 |
  | 2024 H1 | +0.124 |
  | 2024 H2 | +0.105 |
  | 2025 H1 | −0.035 |
  | 2025 H2 | +0.001 |
  | 2026 H1 | −0.047 (CI excludes zero on the wrong side) |

  [FINDINGS §3](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Seven cities, last 12 months** (market+GFS MOS vs market+NBM):

  | Read | market+GFS MOS | market+NBM |
  |---|---|---|
  | 08:00 | +0.012 | −0.021 |
  | 12:00 | +0.009 | −0.000 |
  | 16:00 D-1 | +0.020 [+0.012, +0.026] | −0.004 |

  "The market now fully prices the National Blend of Models … and still underweights GFS MOS" — [FINDINGS §5](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Simple-pool taker backtest, 16:00 D-1.**
  - +$37,459, Sharpe 1.67, DSR 0.619, PBO 0.27.
  - Attribution: +$95,867 alpha vs mid, −$37,326 spread, −$21,083 fees.
  - "One tick of slippage turns +$21,914 into −$31,243."
  - Realised edge 1.7¢ vs 8.4¢ predicted (winner's curse).
  - [FINDINGS §6](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **G2 (isotherm MLP).**
  - Gain vs market at 08:00 / 12:00 / 16:00 D-1: +0.071 / +0.033 / +0.045 nats over all periods, and +0.011 / +0.009 / +0.015 over the last 12 months.
  - ECE 0.004–0.007 vs the market's 0.013–0.020.
  - Leakage control (net trained on market-sampled labels) within ±0.002.
  - Nested backtest at 16:00 D-1, taker: +$22,122, Sharpe 2.05, DSR 0.849, PBO 0.26.
  - $18,018 of that came in 2025 H2 to 2026 H1; positive in 6 of 7 cities and negative only in NY, the most liquid.
  - The selected config is the simple market+GFS pool trading at ≥4¢ EV. It survives +1¢ slippage (+$6,513).
  - [FINDINGS §8](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Lockbox, 2026-07-01 → 10-03.**
  - +$1,851, 664 ladders, 1,925 trades, hit rate 80.4%.
  - Sharpe CI [−0.19, 8.95]. +1¢ slippage leaves +$462. EV 2.2¢ vs realised 1.3¢.
  - By city: NY +$666, MIA +$374, CHI +$339, PHIL +$219, LAX +$210, AUS +$67, DEN −$22.
  - By settlement regime: +$1,580 NWS vs +$272 TWC.
  - [FINDINGS §10](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Lows lockbox:** +$36 over 34 days (t 0.06) vs ~$63/day in backtest. The author attributes the in-sample gain to a newly launched market's miscalibration — [FINDINGS §14](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Regime audit.**
  - The market got ~0.15 nats sharper from May–Sep 2025 to May–Sep 2026 while NBM and GFS MOS MAE stood still. NBM v5 (2026-04-21) did not improve NBM at these stations.
  - NBM's weight in a trailing pool has been ≤0 since 2026-01.
  - GFS weight is seasonal: 0.27–0.38 Jul–Oct 2025, 0.08–0.11 Dec–Feb, 0.26–0.38 Apr–Aug 2026, 0.19 in Sep, 0.11 in early Oct.
  - [FINDINGS §24](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Same-day reads.**
  - The 14:00 read with 5-minute ASOS max-so-far and NBM rest-of-day max gives the largest recent gain: +0.017 [+0.010, +0.025].
  - But only 322 taker trades in three years at 14:00 (+$2,316), and afternoon maker quotes are "still picked off".
  - [FINDINGS §12](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Mid-price artefact.**
  - Sharpening the market (p^1.17–1.32) appeared to win, but "mostly, the mid price overstates buckets nobody is bidding on". 23–53% of buckets have no bid, depending on read time.
  - Against a bid-priced baseline, isotherm's edge survives at 3 of 4 reads (+0.009 / +0.005 / +0.014 / +0.013).
  - "Apparent arbitrage in ladders (bids summing above $1 after fees, 154 of 24,111) comes from non-simultaneous hourly quotes."
  - [FINDINGS §39, §41](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Unseen cities and LAMP.** Twelve unseen cities: +0.001 to +0.006, no read clears zero. LAMP is the better point forecast but adds nothing to isotherm — [README](https://github.com/physicalreasoning/isotherm/blob/977fee6/README.md); [FINDINGS §27, §33](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Live shadow** (`shadow-ledger` branch, `REPORT.md` at commit `b69eac9`, 2026-11-05):
  - 176 settled ladders, log-score gain +0.0179 [−0.0071, +0.0393].
  - Paper PnL $606 over 459 trades, hit rate 85.4%: Oct $378, Nov (so far) $229, all under TWC settlement.
  - Status OK.
  - The MODEL_CARD warns that backtests read hourly candle closes, while live scoring reads the book.
  - [shadow-ledger](https://github.com/physicalreasoning/isotherm/tree/shadow-ledger)

**Provenance caveat (from git history)**
- The 305 commits start 2026-10-04 19:58 −0400. Over 70 commits, including three-year backtests and a 17.0M-print trade fetch, are stamped within ~3.5 hours that evening.
- "Pre-register lockbox test" (`872597a`, 23:21:40) is stamped **79 seconds** before "Lockbox results" (`c63442d`, 23:22:59).
- FINDINGS §10 cites commit `b455496`, which does not exist in the published history.
- The history appears re-composed, so the pre-registration ordering cannot be independently verified from git timestamps.
- The forward tests frozen 2026-10-06 → 10-15 (sealed until 2027-04) are verifiable going forward.
- [isotherm commits](https://github.com/physicalreasoning/isotherm/commits/main)

### Inferences
- **"Market + correction" here means:**
  1. Start from the Kalshi ladder mid.
  2. Raise it to ~1.07 (mild sharpening, largely a mid-price artefact).
  3. Multiply by an EMOS-calibrated GFS MOS Gaussian to the power ~0.29.
  4. Renormalise over the ladder.
  5. Take only ≥4¢-EV taker trades the day before at 16:00 local, sized at quarter-Kelly over the whole ladder, capped at 5% of later volume.
- **The only robust ingredient is the information in GFS MOS that the crowd does not weight.** It is seasonal (weak in winter), decayed through 2025–26, and almost entirely eaten by one tick of slippage.
- For Polymarket, isotherm itself concluded the label is different (hourly max at sometimes different airports). Porting the model would need retargeting to the resolver's hourly series.

### Gaps
- No per-month × per-city table of the lockbox exists in the repo, only per-city and per-month totals separately. The raw `results/lockbox.json` was not parsed beyond the FINDINGS figures.
- The sealed forward tests (transformer-L, NBM-spread MLP, order-flow MLP, 576-station weather model, AIFS pool, sharpening, rain) score in 2027-01 → 2027-04. No results exist yet.

---

## Q3. How did deadBracketBot detect dead brackets and measure the market's lead over METAR, and which feeds are faster than METAR?

### Takeaway
**Detection.** A bracket is "dead" once the resolver-grade running max (reset at the city's local midnight, hard ICAO isolation) exceeds it. Since 2026-09-23 the bracket is dead only once the **resolver's own NOAA table** also reaches that max.

**The 7-minute lead** is a single traced example from one Paris day. Bracket 21's death showed on the Météo-France 6-minute feed at 22.0°C at 11:56 local. The METAR confirmed 22 at 12:03, with a +167-second publish delay.

**Systematic measurement, one day (2026-06-29, 34 cities).**
- The market priced dead NO ≥0.98 a median ~17 minutes *before* the running max reached the bracket in 24 of 34 cities.
- The bot's own METAR detection lag was median 277s (p90 438s), almost all METAR publish delay.

**Faster feeds** come from national met services on the same or co-located sensors:
- Météo-France 6-minute (Le Bourget);
- KNMI, FMI and JMA AMeDAS 10-minute;
- NEA Singapore 1-minute;
- in the US, NWS 1-/5-minute ASOS (IEM archive is delayed).

Captures happened only in thin books: Moscow and Shenzhen, +$49.72 over 9 trades. Later a source-mismatch caused a −$191.48 Singapore loss (2026-09-20).

### Cited Findings
- **Rule.** "Once the confirmed running-max temperature (from the resolution-grade airport METAR) passes a bracket, that bracket can never be the high — its NO is certain to settle at $1. … when a dead bracket's NO is offered below 98¢, buy it (IOC taker); immediately rest a 99.9¢ maker sell." The running max "resets at the city's local midnight" — [README](https://github.com/muzard/deadBracketBot/blob/baab319/README.md)
- **7-minute example.** "Our resolution METAR is the slowest signal: tracing bracket 21's death, the 6-minute feed read 22.0 at 11:56 (market knows 21 is dead) but our METAR only confirmed 22 at 12:03 (+167s publish delay) — a ~7-minute head start for the market."
  - Over 3,481 Paris snapshots with a dead-NO ask: min 0.997, median 0.999, zero below 0.98.
  - [FINDINGS.md §A](https://github.com/muzard/deadBracketBot/blob/baab319/FINDINGS.md)
- **Systematic one-day decomposition (2026-06-29).**
  - "In 24 of 34 cities the market priced the dead-NO up to ≥ 0.98 a median of ~1,005s (~17 min) before our running-max even reached that bracket."
  - "Our own METAR detection lag (obs-time → we log the new reading) was median 277s, p90 438s. We hot-poll at 1s, so almost all of that is the METAR's own ~160–490s publish delay."
  - Only Shenzhen had a liftable post-death tick. The bot hit it 0.3s after it appeared, and it stayed open 12 minutes.
  - Conclusion: "Lower latency buys nothing here; a bigger bankroll does."
  - [FINDINGS.md §E](https://github.com/muzard/deadBracketBot/blob/baab319/FINDINGS.md)
- **Captures and capacity (2026-06-16 → 06-29).**
  - Moscow (UUWW) and Shenzhen NO bought at 0.71–0.97, total +$49.72, zero losers. Two London/Paris fills on 06-10 were excluded as a discovery bug.
  - Shenzhen 06-29: depth at or below the cap had a median of ~981 shares and a peak of ~1,495, vs 132 taken. 251 of 253 ticks were blocked by "size/caps".
  - [FINDINGS.md §0, §C](https://github.com/muzard/deadBracketBot/blob/baab319/FINDINGS.md)
- **Operator hypothesis.** Captures come from "forecast-surprise" overshoots in thin books. The market prices sub-peak brackets dead early from the forecast; near-peak brackets keep YES value until a higher reading lands — [FINDINGS.md §F](https://github.com/muzard/deadBracketBot/blob/baab319/FINDINGS.md)
- **Sub-hourly feeds, Tier 1 (verified same-station).**

  | City | Feed | Cadence and access |
  |---|---|---|
  | Paris LFPB | Météo-France RADOME "Paquet Observations" | 6-min; free API key |
  | Amsterdam EHAM | KNMI `Actuele10mindataKNMIstations`, station 240 | 10-min |
  | Helsinki EFHK | FMI WFS, fmisid 100968 | 10-min, ~5-min lag, no key |
  | Tokyo RJTT | JMA AMeDAS JSON (Haneda) | 10-min, no key |
  | Singapore WSSS | NEA / data.gov.sg | **1-min**, Changi Climate Station; outages noted |

  Tier 2 (needs verification):
  - DWD 10-min (latency ~30 min);
  - MGM Turkey;
  - KMA API Hub 1-min AWS/AMOS;
  - CWA Taiwan 10-min;
  - IMS Israel (station ~7 km from LLBG);
  - ECCC SWOB-ML (faster METAR delivery);
  - REDEMET (Brazil).

  None usable: China CMA/NMC (hourly only), Moscow, Madrid AEMET and others. The feeds "let you know what the next METAR will say 6–30 min before it's filed" — [docs/subhourly_feed_openings_2026-07-02.md](https://github.com/muzard/deadBracketBot/blob/baab319/docs/subhourly_feed_openings_2026-07-02.md)
- **METAR cadence matters.**
  - :20/:50 half-hourly stations: EGLC, EHAM, Helsinki, Milan, Munich, Ankara, Istanbul.
  - :00/:30 stations: Paris, Madrid, Warsaw, Moscow, Seoul, Tokyo, Singapore and others.
  - Hourly-only: Busan, Toronto, Shenzhen and others.
  - SPECI-active: Moscow had 133 SPECIs in 25 days.
  - "68% of daily maxima are first seen on a sub-hourly/SPECI ob (avg lead 26 min before the next top-of-hour)".
  - 27% of daily maxima are "fragile" (appear in only one ob).
  - 0 temperature-changing corrections in ~13,000 obs.
  - [docs/early_reading_reliability_2026-07-02.md](https://github.com/muzard/deadBracketBot/blob/baab319/docs/early_reading_reliability_2026-07-02.md)
- **Forecast path guards** (paper only by default): ≥0.4°C margin because METAR rounds; p̂ ≤ 0.99; no entries 17–21h local; quarter-Kelly; 25% cap per feed observation; sticky global pause on any settled forecast loss — [README](https://github.com/muzard/deadBracketBot/blob/baab319/README.md)
- **Singapore false dead, 2026-09-20.**
  - The bot bought 500 NO on the 31°C bracket at an average 0.378. The market resolved YES on 31 (NOAA never ingested the 32°C METARs): real loss −$191.48, paper booked +$308.52.
  - "The market was telling us. The NO was offered at 0.149 at entry."
  - Fixes in commit `5281e27` ("only call a bracket dead once the resolver's own table says so") and PR #5 (`fix/resolver-confirmed-dead`, merged 2026-11-02):
    - `resolver_confirm_dead` on;
    - each city settles at its own midnight;
    - PnL booked from actual resolution.
  - [docs/noaa_ingest_outage_2026-09-20.md](https://github.com/muzard/deadBracketBot/blob/baab319/docs/noaa_ingest_outage_2026-09-20.md)
- **Polymarket weather taker fee in code.** `fee(a) = a · fee_rate · (a·(1−a))^fee_exponent` with `fee_rate 0.025`, `fee_exponent 0.5`; "Makers pay no fee, so the resting 99.9c exit is always fee-free" — [fees.py](https://github.com/muzard/deadBracketBot/blob/baab319/src/dead_bracket/fees.py); [config.py](https://github.com/muzard/deadBracketBot/blob/baab319/src/dead_bracket/config.py)
  - Conflicts with BallesJr, which uses `WEATHER_FEE_RATE = 0.05` in `fee = feeRate·C·p·(1−p)` ("confirmed from Polymarket docs") — [signal_engine.py](https://github.com/BallesJr/polymarket-weather-edge/blob/aa96700/signal_engine.py)
- **US 1-/5-minute ASOS.** isotherm uses the IEM ASOS 1-minute archive sampled at 5 minutes (10-minute reporting lag assumed). It warns IEM receives it with delay, so live use needs a real-time 5-minute feed — [FINDINGS §12](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md). muzard notes "NWS 1-min ASOS is US-only" — [early_reading_reliability](https://github.com/muzard/deadBracketBot/blob/baab319/docs/early_reading_reliability_2026-07-02.md)

### Inferences
- **The "7-minute lead" is anecdotal.** It rests on one traced bracket on one Paris day. The stronger, systematic statistic is the ~17-minute median pre-pricing on 2026-06-29 across 24 of 34 cities. It is still a single day.
- **In liquid Polymarket cities, intraday dead-bracket arbitrage is fully competed.** Competitors appear to use national sub-hourly feeds and/or nowcasting. Residual opportunity is in thin, non-standard-source cities. That is exactly where source mismatch risk is highest, as Seoul and Singapore show.
- **Since the NOAA switch, a safe design needs two data sources.** Use the national sub-hourly feed for speed, and require the resolver table (Synoptic timeseries) to confirm before risking near-certain-NO capital.

### Gaps
- No repo publishes a multi-day, multi-city latency distribution of feed time → market reprice time → METAR publish time.
- The Polymarket weather fee parameters conflict between repos (0.025 with exponent 0.5 vs 0.05 quadratic). I did not verify them against Polymarket's fee documentation here.
- The forecast-path paper results (`forecast_calibrate` output) are not committed.

---

## Q4. Evidence about market making / maker strategies in weather markets

### Takeaway
Every quantified maker test on Kalshi temperature ladders is flat or negative:
- isotherm: −$8k to −$35k nested in 2023–26;
- k1hbles: −0.7¢/contract;
- jdeepsingh28 live: −$16 to −$28 after fees (prior notes).

Resting quotes are filled mainly when better-informed flow trades through them. Forecasts cut that adverse selection by about two-thirds without eliminating it.

The only positive maker number is a liquidity-reward simulation on Kalshi **rain** (KXRAIN) books. There, rewards rather than spread capture carry net PnL.

On Polymarket, maker use is limited to fee-free exits, such as muzard's resting 99.9¢ sell. All 9 realised exits filled, after 0.7–234 minutes.

### Cited Findings
- **isotherm maker backtest** (17.0M prints over 40,553 markets; fills only on later prints strictly through the quote):

  | Read | Model as maker | Uninformed market maker | Matched noise |
  |---|---|---|---|
  | 08:00 | −$12,477 | −$42,779 | −$29,195 |
  | 12:00 | −$34,665 | −$101,869 | — |
  | 16:00 D-1 | −$8,071 | — | — |

  - Attribution at 08:00: "+$57,946 of spread captured, −$70,423 alpha vs mid".
  - Quotes held to the close lose −$243,506 ("stale quotes are picked off").
  - [FINDINGS §7](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **Later isotherm variants** (with cancel-on-new-GFS-run):
  - 16:00 D-1: +$2,985 (DSR 0.000; at-touch upper bound +$4,820).
  - 08:00: +$10,108 (DSR 0.023).
  - 12:00/14:00: −$23,991 / −$30,573.
  - "Queue position itself is not estimable without order-book depth history, which Kalshi does not publish."
  - [FINDINGS §12](https://github.com/physicalreasoning/isotherm/blob/977fee6/FINDINGS.md)
- **isotherm KXRAIN reward simulation** (recorded books; policy: rest S contracts at best bid with back-of-queue rejoin; Kalshi Liquidity Incentive Program rewards; maker fee 0.0175·C·P·(1−P)):

  | Size | Fills | Fill PnL | Maker fees | Rewards | Net |
  |---|---|---|---|---|---|
  | S=50 | 19,764 | +$704 | −$581 | +$558 | **+$681** |
  | S=200 | — | +$20 | −$868 | +$1,955 | **+$1,107** |

  - Fill edge is only 0.34¢/contract at S=50, and 201 reward programs were covered. The run was committed 2026-10-15 ("Paper market making on recorded books: rewards against fills").
  - Not written up in FINDINGS; one short recorded window.
  - [results/book/maker_sim.json](https://github.com/physicalreasoning/isotherm/blob/977fee6/results/book/maker_sim.json); [scripts/book/maker_sim.py](https://github.com/physicalreasoning/isotherm/blob/977fee6/scripts/book/maker_sim.py); [results/book/lip_estimate.json](https://github.com/physicalreasoning/isotherm/blob/977fee6/results/book/lip_estimate.json)
- **Kalshi maker fee for weather: conflicting.**
  - isotherm `backtest.py`: `maker_fee_rate: float = 0.0  # weather series: fee_type "quadratic", no maker fee`.
  - Its maker sim and anaborne quote `0.0175·C·P·(1−P)`, with anaborne noting "M defaults to 0" for maker.
  - [backtest.py](https://github.com/physicalreasoning/isotherm/blob/977fee6/src/isotherm/backtest.py); [anaborne METHOD.md](https://github.com/anaborne/kalshi-temperature-calibration/blob/b53b2f5/METHOD.md)
- **k1hbles maker** (optimistic queue: filled if the opposite quote later reaches the price): q_blend at 0.05 −0.85¢ (t −1.02); at 0.10 −0.74¢ (t −0.7) — [results.txt](https://github.com/k1hbles/kalshi-edge/blob/d08164f/results.txt)
- **Deivid-Negoita** lists "Fills. Taker only, with no queue position" as a limitation. It flags "selling the wings a day out" (~1–2¢ after ~1.3¢ half-spread and ~1¢ fee) as an untested lead — [README](https://github.com/Deivid-Negoita/kalshi-weather/blob/dfb6536/README.md)
- **muzard maker exit.** Always rest the 99.9¢ maker sell; per the config comment, everything realised came from such fills, "9 of 9 filled, 0.7-234 min" — [config.py](https://github.com/muzard/deadBracketBot/blob/baab319/src/dead_bracket/config.py); [STRATEGY.md](https://github.com/muzard/deadBracketBot/blob/baab319/STRATEGY.md)

### Inferences
- **On Kalshi temperature ladders, passive quoting loses to informed flow.** That flow is likely observation- and model-run-driven: isotherm finds afternoon quotes picked off and losses growing with quote lifetime.
- **Any maker edge would have to come from incentive programs, not spread.** Pairing quotes with fast cancellation on new data (model runs, sub-hourly observations) is a possible route but untested.
- **The rain reward sim hints that liquidity rewards can dominate on thin weather books.** It is too short and too unvalidated to rely on.

### Gaps
- No open-source repo tests a Polymarket weather maker strategy, or Polymarket liquidity rewards for weather markets, with real fills.
- No Kalshi order-book depth history is public, per isotherm. Queue position is unknown in all maker backtests.
- **Jon-Becker/prediction-market-analysis** (HEAD `2d69f73`, 2026-10-29) maps Kalshi weather prefixes (HIGHNY…, RAIN, SNOW, TORNADO, HURCAT) in `src/analysis/kalshi/util/categories.py` and has `maker_taker_returns_by_category.py`. No precomputed weather-specific numbers are committed, and running it needs the 36 GiB dataset — [categories.py](https://github.com/Jon-Becker/prediction-market-analysis/blob/2d69f73/src/analysis/kalshi/util/categories.py)
- **warproxxx/poly_data** (HEAD `136e129`) has no weather-specific files.
- **Hugging Face** search on 2026-11-05 found no Polymarket/Kalshi weather-market dataset.
  - Searches for "polymarket weather", "kalshi weather" and "kalshi temperature" returned nothing.
  - Nearest hits:
    - `willtherebenough/kalshi-metar-live`: 69 METAR rows, 2026-05-29.
    - General trade dumps: `RooseveltHonaker/kalshi-trades-data`, `TrevorJS/kalshi-trades`, `TimeSeventeen/Kalshi`, `SII-WANGZJ/Polymarket_data`, `TimeSeventeen/Polymarket-v1`.
    - Generic METAR archives: `consgicody/asos-metar-archive`.
  - [HF API search](https://huggingface.co/api/datasets?search=kalshi); [kalshi-metar-live](https://huggingface.co/datasets/willtherebenough/kalshi-metar-live)
