# PolyWeather

Research project on **Polymarket daily "highest temperature" markets**: can forecasts built from
numerical / AI weather models and live observations beat the market price at the moment of
trading — honestly, after fees, spreads and realistic execution?

The project started as a trading bot (see [Legacy bot](#legacy-bot)). It was re-started in
November 2026 as a research project: measure the market first, rebuild data and targets exactly
by the settlement rules, and test every hypothesis with point-in-time data and real fill prices.

> Status (Nov 2026): **research phase, no live trading.** Docs are partly in Russian.

---

## Key results so far

Full numbers and methods: [`research/FINDINGS.md`](research/FINDINGS.md) (§ numbers below).

* **Data:** 12,990 Polymarket "highest temperature" events, 53 cities, Jan 2025 → Nov 2026;
  29 M trades; resolution stations; METAR archive; point-in-time forecasts of 8 NWP / AI models
  (Open-Meteo Single Runs, Apr 2026 →).
* **Settlement rules changed three times** (Wunderground → NOAA timeseries → aviationweather METAR,
  routine reports only, SPECI excluded). A resolver rebuilds the settlement value of every event
  under its own regime and matches the actual outcomes: **100 %** (current AWC regime),
  99.0 % (NOAA), 98.2 % (WU) (§6).
* **The market is well calibrated** (~1 pp deviations; bucket prices sum to ≈ 1.00) (§4).
  Price-only strategies — longshots, favourites — lose after fees (§7).
* **Forecast models vs the market:** EMOS post-processing of 6–8 models is ~7.5 % worse in Brier
  than the market at D−1 12:00 (§14); a unified as-of LightGBM model (forecasts + METAR + recent
  model errors) is calibrated but ~15 % worse overall (§15). Intraday models from observations
  lose to the market as well (§10–§11).
* **The only confirmed edge is information latency:** in US cities routine METAR is hourly and the
  market waits for it; 1-minute ASOS observations give **+3–5 % ROI (t ≈ 3.5, clustered by
  city-day)**, decaying with delay, capacity ≈ $1–1.5k / month (upper bound) (§12). Tokyo and
  Singapore show no significant edge (§13).
* **Backtest pitfalls found on the way:** look-ahead in Open-Meteo `previous_day1`, the
  stale-last-price artefact (+8.7 % on last trades vs −1.8 % on real fills, §11), rule-regime
  changes, over-confidence of boosting on near-duplicate states (§15).

---

## Repository

```
research/        research scripts and documents
  PLAN.md          current status + to-do list (start here)
  FINDINGS.md      lab notebook: every experiment with numbers (§1–§15, appendices)
  sota/            literature / open-source / wallet review (SOTA.md)
  fetch_*.py       data collection (events, trades, METAR, forecasts, fast feeds)
  resolver.py      settlement value per rule regime
  *_model.py, *_test.py, *_sim.py   experiments referenced in FINDINGS
logger/          Polymarket order-book recorder (WebSocket) + replay tool + systemd unit
paper/           publication plan, model design (SettleCast), novelty review
data/
  stations.csv     resolution station per city (ICAO, coordinates, timezone, unit)
  forecasts/       Open-Meteo forecasts (kept in git — old runs cannot be re-downloaded)
  raw/             events, trades, METAR, analysis outputs (not in git, re-downloadable)
bot.py, strategy.py, forecast.py, predictor.py, markets.py, executor.py, retrain.py, cities.py
                 legacy bot (see below)
```

Branch for this work: `claude/brave-hawking-jzbxx3`.

---

## Getting started

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Rebuild the public market and observation data (not stored in git; see FINDINGS appendix B):

```bash
python research/fetch_events.py --start 2024-01-01
python research/fetch_trades.py --workers 16
python research/build_stations.py
python research/fetch_metar.py
python research/resolver.py
python research/market_calibration.py
```

Forecasts (free Open-Meteo tier, ~10k requests/day per IP, resumable; run on your own machine):

```bash
python research/fetch_forecasts.py single --start 2026-04-02
python research/fetch_forecasts.py extra --preset single-extras
python research/fetch_forecasts.py extra --preset single-0618
python research/fetch_forecasts.py previous --start 2024-01-01
python research/fetch_forecasts.py extra --preset previous-extras --start 2024-01-01
```

Order-book logger (24/7 on a server; ~90 MB RAM, ~0.5 GB/day): see [`logger/README.md`](logger/README.md).

---

## Next steps

Tracked in [`research/PLAN.md`](research/PLAN.md). In short: finish the forecast download
(forecast radiation / cloud / wind / dew point, 06z/18z runs, Previous Runs history), deploy the
order-book logger, add AI ensembles (AIFS-ENS, AIGEFS, WeatherNext 2) and NBM as baselines,
build the streaming model SettleCast ([`paper/MODEL_DESIGN.md`](paper/MODEL_DESIGN.md)), and only
then decide on paper trading. Publication plan: [`paper/PUBLICATION_PLAN.md`](paper/PUBLICATION_PLAN.md).

---

## Legacy bot

The original bot (`bot.py` and the modules next to it) trained LightGBM on Open-Meteo
`previous_day1` forecasts and Wunderground maxima for 10 cities and paper-traded edges against
Polymarket prices. An audit (FINDINGS appendix A) found methodological problems — wrong metric,
look-ahead in the training data, over-confident probabilities, Narita instead of Haneda for Tokyo,
exits never sent, fills assumed — so **its results and its pretrained model
(`data/models/`, `data/model_forecasts_day1.csv`, `data/wu_historical.csv`) should not be relied on.**
It is kept for reference only and will be replaced if a strategy passes the research phase.

## Data sources and licences

Polymarket Gamma / Data / CLOB APIs (trades are also public on-chain), Open-Meteo (CC BY 4.0,
upstream model licences apply), ECMWF open data (CC BY 4.0), NOAA aviationweather.gov and
Iowa Environmental Mesonet (METAR, 1-minute ASOS), JMA, data.gov.sg (NEA). Check each source's
terms before redistributing data.
