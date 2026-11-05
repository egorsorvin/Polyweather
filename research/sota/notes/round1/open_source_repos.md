# Open-source code for trading daily temperature / weather markets on Polymarket and Kalshi

Method note: research date 2026-11-05. Repos were found with `gh search repos` using queries such as "polymarket weather", "polymarket temperature", "kalshi weather", "kalshi temperature", "KXHIGHNY", "weather prediction market", "poly_data", "kalshi historical data" and "prediction market data". READMEs were read from raw.githubusercontent.com. Star counts and the "updated" date come from GitHub search metadata on 2026-11-05. The "updated" date changes on any repo activity, stars included, so it is not necessarily the last commit date.

**Verified** means seen in the README text. **Claim** means a self-reported result that I did not reproduce. I could not open the code, issues or commit history (the GitHub API was blocked for this session), and Hugging Face was unreachable.

Almost every repo found was created or updated in 2026. Material from 2024 is rare; the BU CS542 Spring 2024 course projects are the main exception.

---

## Q1. Which repos exist for Polymarket weather markets, and which for Kalshi weather (KXHIGH*, rain, snow)?

### Takeaway
There are dozens of small repos, nearly all from 2026. The most-starred is a combined Kalshi+Polymarket bot, suislanchez (804★), which counts members of a 31-member GFS ensemble. The most useful repos are a handful of rigorous negative-result studies, mostly Kalshi-focused, plus a few Polymarket repos that document resolution-source traps. Almost everything targets daily-high temperature buckets. I found no dedicated open-source rain or snow bots, only generic mentions (for example, hcharper scans "rain, snow, temperature").

### Cited Findings — Kalshi and cross-platform (catalogue)

- **suislanchez/polymarket-kalshi-weather-bot**: 804★, updated 2026-11-04, Python with a React/TS dashboard, MIT.
  - Two strategies: BTC 5-minute markets and weather.
  - Weather scan runs every 5 minutes. It discovers Kalshi markets via series `KXHIGHNY, KXHIGHCHI, KXHIGHMIA, KXHIGHLAX, KXHIGHDEN` (RSA-PSS auth) and Polymarket markets via the Gamma API.
  - Probability = fraction of the 31 Open-Meteo GFS ensemble members above or below the threshold. It trades when edge > 8%, sized at 15% fractional Kelly, capped at $100 and 5% of bankroll.
  - NWS API is used for observed temperatures at settlement. Stations: KNYC, KORD, KMIA, KLAX, KDEN.
  - Paper mode, Brier score tracking. No PnL is published (verified).
  - Pitfall (my reading): the README lists KORD for Chicago, while anaborne reports that Kalshi Chicago settles at Midway.
  - [README](https://raw.githubusercontent.com/suislanchez/polymarket-kalshi-weather-bot/HEAD/README.md)
- **AruneshDev/Automated-Trading-System-Kalshi-Weather-Model**: 144★, updated 2026-10-20, Jupyter. BU CS542 coursework from spring 2024 (trades dated 3 April).
  - XGBoost next-day tmax for NYC, Austin, Chicago and Miami, using legacy tickers HIGHNY, HIGHAUS, HIGHCHI, HIGHMIA on the Kalshi demo account.
  - Trained on 3 years of Visual Crossing data. Reported MSE: Austin 3.4, Chicago 27.4, Miami 7.6, NYC 31.6. No PnL.
  - [README](https://raw.githubusercontent.com/AruneshDev/Automated-Trading-System-Kalshi-Weather-Model/HEAD/README.md)
  - Sibling 2024 course repos: pranavgoyanka/LSTM-Automated-Trading-System (6★, "Kalshi Weather Prediction Common Task for BU's CS542 Spring 2024") and akshatgurbuxani/Kalshi-Weather-Forecasting-Financial-Trading (9★) — [GitHub search](https://github.com/search?q=kalshi+weather&type=repositories)
- **JHenzi/weatherbots**: 5★, updated 2026-10-27, Python/Docker.
  - Cities: KXHIGHNY, KXHIGHCHI, KXHIGHAUS, KXHIGHMIA.
  - Combines 8 forecast sources: Open-Meteo, Visual Crossing, Tomorrow.io, WeatherAPI, OWM, Pirate Weather, NWS, Google Weather. Weights are re-set nightly by inverse MAE against **NWS CLI settlement truth**.
  - A LinUCB contextual bandit chooses between the raw ensemble and a bias-corrected "blend". Rolling 14-day per-city bias is typically a +0.4–0.6°F cold-bias correction.
  - Trades at 13:00 local. Exit manager uses an observation-based "bucket-breach" stop-loss (1.5°F) and a trailing take-profit.
  - Demo and dry-run by default. No PnL figures.
  - [README](https://raw.githubusercontent.com/JHenzi/weatherbots/HEAD/README.md)
- **AwpDemon/kalshi-weather-bot**: 2★, updated 2026-10-06, Python 3.12, 98 tests.
  - Explicitly rebuilt from suislanchez. Thesis: a systematic ~1–2°F warm bias in NWS forecasts.
  - Uses the 31-member GFS ensemble from Open-Meteo plus rolling empirical bias correction. Trades at >10% edge after fees. Seeded with 729 station-days of calibration residuals.
  - Claim: Phase 1 paper trading, Apr 5–15 2026, 20 settled trades, 9W/11L, +$3.89 on ~$39.75. The author says this is too small a sample.
  - Notes a VALIDATION.md on Kalshi API changes (`strike_type` fields, dollar-string prices).
  - [README](https://raw.githubusercontent.com/AwpDemon/kalshi-weather-bot/HEAD/README.md)
- **jdeepsingh28/kalshi-weather-bot**: updated 2026-07-23, Python, GCP. Live in early 2026 across 18 cities; retired March 2026.
  - Forecast pipeline: NWS daily high, **NWS-CLI (settlement truth)**, METAR, HRRR via Herbie/GRIB2, the 31-member GEFS (Herbie and Open-Meteo), and ECMWF IFS / GraphCast / ICON via Open-Meteo.
  - Pitfall the author documents: this pipeline was *never wired into live pricing*. The live trader used METAR only.
  - Strategies: `structural_sell` (sell YES tails, maker), `convergence`, `metar_buy` (running max plus offset), and `cross_contract` (bracket mids not summing to 100).
  - Verified-as-reported live record:
    - 1,026 settlements, 85.2% expired NO.
    - Reconciled Feb 27–Mar 16 window, 5,143 fills: spread capture +$394, tails −$355, net +$39 before fees. After estimated maker fees (−$55 to −$67): **−$16 to −$28**.
    - The offline backtest had estimated +$62 / Sharpe 0.55.
  - [README](https://raw.githubusercontent.com/jdeepsingh28/kalshi-weather-bot/HEAD/README.md)
- **bnbi/kalshi-weather-trading**: updated 2026-10-30, Python. Real-money postmortem.
  - Model: GFS/ECMWF/ICON/NWS ensemble with ML bias correction. Trained only on true lead-1 forecasts and scored against **NOAA GHCND official settlement-station data**, never the provisional NWS feed max or reanalysis.
  - Day-specific σ regressor. Shrinkage toward market, `p̂ = w·model + (1−w)·price`. Refuses trades with >25¢ disagreement. Quarter-Kelly. Fill-or-cancel after 20 s.
  - Live result, 92 settled trades: model Brier 0.22 vs market 0.13 (skill −0.74). **−$27.01 net of fees.** Point MAE was good (1.4°F); in the author's words, "the edge died in the probability layer under adverse selection" (winner's curse).
  - Second strategy is a "same-day sniper" using station observations and Monte-Carlo final-high, gated on ≥30 real-settlement signals.
  - [README](https://raw.githubusercontent.com/bnbi/kalshi-weather-trading/HEAD/README.md)
- **Sully-Ok/weather-prediction-market-model**: started June 2026, Python, 20 US cities on Kalshi.
  - Inputs: NWS gridpoint, NOAA CDO normals, Open-Meteo ensembles. Walk-forward 45-day per-station bias and σ (e.g., Miami NWS runs ~1.5°F warm).
  - Student-t (df=5) tails. Blends toward market price. Filters on spread, price floor and extremity.
  - Fee formula `ceil(0.07×C×P×(1−P))` is charged on paper trades too.
  - Claim: 80 settled positions, Jun 19–Aug 12 2026, +$0.97 on $43.86 (+2.2%), Brier 0.240. The author says this is not evidence of edge.
  - [README](https://raw.githubusercontent.com/Sully-Ok/weather-prediction-market-model/HEAD/README.md)
- **EddieTGH/kalshi-weather-predictor**: 7★, Denver only.
  - XGBoost (MAE 1.551°F) plus a custom temporal transformer (MAE 1.002°F). Data: NOAA, IEM ASOS, Open-Meteo. Live Kalshi trading with Kelly sizing.
  - Notes that Denver markets are absent from Kalshi's demo API.
  - [README](https://raw.githubusercontent.com/EddieTGH/kalshi-weather-predictor/HEAD/README.md)
- **Other Kalshi repos (description only, READMEs not read):**
  - ethanterrero/Kalshi-Weather-Bot: Rust, NWS-vs-market directional.
  - alanshen421/KalshiWeatherBot: NWS + Open-Meteo, using Claude for decisions.
  - giulioelmi/kalshi-weather-trading: LA ML model.
  - Ciarnan-Moloney/Kalshi-Weather-Spread-Algo: logistic regression, 5 cities.
  - RealGB80/AeroAlpha: KXHIGHNY, paper-only.
  - Schmiedey/kalshi-weather: longshot strategy.
  - julianPolicarpio/weather-pro-max.
  - [GitHub search](https://github.com/search?q=kalshi+temperature&type=repositories)

### Cited Findings — Polymarket (catalogue)

- **hcharper/polyBot-Weather**: 50★, updated 2026-10-30, Python.
  - Multi-strategy: weather, crypto via Black-Scholes, and YES+NO<1 arbitrage.
  - Weather model: NOAA point forecast plus a Gaussian with ±2.5–7.5°F RMSE by lead time. Trades at edge >10% and z ≥ 1.5, with Kelly sizing capped at 25%. Also covers precipitation by calibrating NOAA PoP.
  - Claim: "Weather: 15-25% APY" expected return. This is unsupported; backtesting is listed as "future".
  - [README](https://raw.githubusercontent.com/hcharper/polyBot-Weather/HEAD/README.md)
- **natestokens/polymarket-weather-bot**: 17★, built live on YouTube by @rainmoneymaker.
  - 173-member ensemble from Open-Meteo (ECMWF IFS, AIFS, GEFS, ICON). City bias corrections against Iowa State ASOS: NYC +1.4°F warm (29-day LGA analysis), MIA −2.2°F, CHI and LAX "assumed".
  - Thresholds: NO at 5pp, YES at 15pp. A 3°F "MEAN_BUFFER" keeps it away from brackets near the mean. NWS is used as a tiebreaker.
  - Notes that Tokyo and Singapore markets use 1°C brackets.
  - Claim: as of 2026-05-27, +$77.01 on $279, 14/23 wins (+27.6%).
  - [README](https://raw.githubusercontent.com/natestokens/polymarket-weather-bot/HEAD/README.md)
- **AadiXD200/polymarket-weather-bot**: 15★, updated 2026-11-05.
  - Five deterministic NWP models from Open-Meteo: GFS, ECMWF, ICON, GEM, Météo-France. Student-t (ν=4) bucket integral.
  - **Nowcasting**: ASOS observation weight rises from 0% at midnight to 80% at close.
  - Filters: NO entry price 0.20–0.75; skip NO when model std < 0.8°C; CLOB top-5 depth ≥ $150. Quarter-Kelly, $15 cap.
  - Claim: paper, 7 days (Mar 28–Apr 3 2026), 63 trades, 82.5% wins, +$806 (+35.6%), using mid-price fills. Houston alone contributed +$623 and Paris −$234. 18 live positions as of Apr 5 2026.
  - [README](https://raw.githubusercontent.com/AadiXD200/polymarket-weather-bot/HEAD/README.md)
- **RiekertQuant/polymarket-weather-bot-poc**: 23★, updated 2026-11-05.
  - Paper only, NYC/London/Seoul, Open-Meteo, optional ML calibrator.
  - Backtester produces PnL, Sharpe and drawdown, but the README examples use `--synthetic` data. GitHub Actions run a daily signal log.
  - [README](https://raw.githubusercontent.com/RiekertQuant/polymarket-weather-bot-poc/HEAD/README.md)
- **yannbellec/polymarket-weather-bot**: 11★.
  - ECMWF IFS 51-member ensemble from Copernicus CDS, with NWS/Open-Meteo fallback. Fraction-of-members probability. WebSocket CLOB prices, Docker, DRY_RUN by default.
  - Claim (unsourced): "public accounts turned $1k into mid-five figures".
  - [README](https://raw.githubusercontent.com/yannbellec/polymarket-weather-bot/HEAD/README.md)
- **MihirM9/polymarket-weather-bot**: 10★, "v5".
  - Inputs: NWS/NOAA, METAR and station observations, blended into a Gaussian CDF over ~11 buckets. 2-minute loop, "13 layers" of risk controls, and a `backtesting/` replay package.
  - Explicitly does **not** publish PnL or a backtest scorecard.
  - [README](https://raw.githubusercontent.com/MihirM9/polymarket-weather-bot/HEAD/README.md)
- **BallesJr/polymarket-weather-edge**: 8★, updated 2026-11-05. Paper trading, GitHub Actions every 30 minutes. METAR from aviationweather.gov plus Open-Meteo, Gaussian model, Random Forest calibration. Pitfalls and results are under Q5 and Q3.
  - [README](https://raw.githubusercontent.com/BallesJr/polymarket-weather-edge/HEAD/README.md)
- **muzard/deadBracketBot**: updated 2026-11-02.
  - "Dead-bracket NO capture": once the resolution-METAR running max passes a bracket, that bracket's NO is worth $1. The bot buys NO below 98¢ and rests a sell at 99.9¢.
  - Runs 11 European cities concurrently, plus Shenzhen, Tokyo and Singapore via national feeds.
  - [README](https://raw.githubusercontent.com/muzard/deadBracketBot/HEAD/README.md)
- **testedmedia/polymarket-weather-command-center**: 4★, updated 2026-10-23, TypeScript, Apache-2.0.
  - Dashboard for 41 cities with up to 28 models per city, live ASOS/METAR, WU V1/V3 archive cross-checks, and a peak-time and "@3PM hold rate".
  - Backtest artifact shipped: 730 days.
  - [README](https://raw.githubusercontent.com/testedmedia/polymarket-weather-command-center/HEAD/README.md)
- **idlepraxis/polymarket-weather-bot**: 23★.
  - "Extreme value" rule: buy YES at 3–12¢ (skip sub-3¢), buy NO when YES > 50¢. Needs a 10% edge vs NWS. Positions $1.50–5.
  - [README](https://raw.githubusercontent.com/idlepraxis/polymarket-weather-bot/HEAD/README.md)
- **Augustforge/weather-prediction-market-bot**: ~32k lines of Python, paper only.
  - 48 cities, each mapped to its exact resolution station and source. Per-station calibration against Polymarket resolutions.
  - Champion/challenger shadow runtime, drift rollback, immutable timestamped forecasts.
  - [README](https://raw.githubusercontent.com/Augustforge/weather-prediction-market-bot/HEAD/README.md)
- **utosrad/weather-edge**: parses question → contract terms. σ(h) is fitted against forecast error, e.g. `2.23·sqrt(1+h/45.8)`. Order-book walk for fills, fractional Kelly, uses Tomorrow.io. 77 tests. The README states its Brier 0.161 comes from **synthetic data and is not evidence of edge**.
  - [README](https://raw.githubusercontent.com/utosrad/weather-edge/HEAD/README.md)
- **portrara/weather-market-predictor**: Kalshi and Polymarket.
  - Blends ERA5 climatology (harmonic regression), a recent regime offset, a ~100-member GFS+ECMWF+ICON+GEM ensemble and a station offset. Monte Carlo with 60k samples. Extreme Value Theory context for the hot tail. Optional LLM commentary. Streamlit demo.
  - [README](https://raw.githubusercontent.com/portrara/weather-market-predictor/HEAD/README.md)
- **Gpar307/Polymarket_Weather_XGBoost_Template**: research template (Milan YAML).
  - XGBoost tmax with a **Wunderground scraper**. Historical Polymarket order-book snapshots via the **Predexon API**. Backtest with EV filter and Kelly. No live execution.
  - [README](https://raw.githubusercontent.com/Gpar307/Polymarket_Weather_XGBoost_Template/HEAD/README.md)
- **sdnwrd/PolyWeather**: signals only, 8 US cities. NWS hourly → normal distribution with fixed σ=2°F, which the author says is uncalibrated. Alerts when EV ≥ 8×, price ≤ 15¢ and p ≥ 5%; sends to Telegram.
  - [README](https://raw.githubusercontent.com/sdnwrd/PolyWeather/HEAD/README.md)
- **Other Polymarket repos (description only):**
  - kylesnav/polymarket-sim: NOAA paper trading.
  - goldengooseHD/polymarket-weather-bot: NOAA ensemble plus "Nash maker strategy".
  - NPCmillionaire/wxwhales: follows the biggest wallets in temperature markets.
  - Heldinhow/worker-weather: C#, "contested-NO".
  - erosalf/polymarket-weather: European signals.
  - Chinese-language repos: lelvzuche321, qianyubtc, djhyes.
  - [GitHub search](https://github.com/search?q=polymarket+temperature&type=repositories)
- **Caution — likely SEO or spam repos:**
  - MoonsatProtocol/Polymarket-Weather-Bot (64★): the description repeats "polymarket weather betting bot" many times. The README requires `POLYMARKET_PRIVATE_KEY` and advertises a "paid version".
  - risedownlabs/polymarket-weather-bot, Changnoixx/Polymarket-Weather-Trading-Bot and devgen88/... use the same keyword-stuffed descriptions.
  - I did not verify that they are malicious. Treat them as untrusted, especially anything asking for a private key.
  - [MoonsatProtocol README](https://raw.githubusercontent.com/MoonsatProtocol/Polymarket-Weather-Bot/HEAD/README.md)
- **Naming oddity:** kevinbadi/polymarket-weather-quant (description: "Calibrated weather-prediction trading engine") has a README that is a copy of warproxxx/poly_data's data-pipeline README. Issy1000/poly_data likewise uses the name "poly_data" for a weather bot — [kevinbadi README](https://raw.githubusercontent.com/kevinbadi/polymarket-weather-quant/HEAD/README.md)

### Inferences
- The space is crowded with near-identical bots built on the free Open-Meteo GFS ensemble. Many are likely LLM-assisted and published in 2026. Star counts are low except suislanchez.
- The ensemble-count edge on free public data is widely replicated, which by itself argues it is priced in.
- Polymarket repos increasingly cover non-US cities in °C (London, Paris, Seoul, Shenzhen, Tokyo). Kalshi repos stay on KXHIGH US cities.

### Gaps
- I could not read issues, commit history or code (GitHub API blocked), so "last update" reflects any repo activity.
- No dedicated open-source Kalshi rain or snow bots were found; I did not search exhaustively for KXRAIN/KXSNOW tickers.
- Hugging Face could not be queried directly.

---

## Q2. What forecasting approaches do they use?

### Takeaway
Approaches span a ladder:
1. A single NWS point forecast with a fixed-σ Gaussian.
2. Counting ensemble members (31 GFS, 51 ECMWF, or a 173–~100-member multi-model mix via Open-Meteo).
3. Per-station bias correction and Student-t tails.
4. MOS/NBM text (GFS MOS, NBS) or EMOS-calibrated NWS.
5. ML (XGBoost, LSTM/transformer, Random Forest calibrators, LinUCB bandits).
6. Intraday METAR/ASOS nowcasting, i.e. running-max "dead bracket" logic.

The better-documented repos shrink the model toward the market price.

### Cited Findings
- **Raw ensemble fraction:**
  - suislanchez: 28/31 members above 70°F = 90% — [README](https://raw.githubusercontent.com/suislanchez/polymarket-kalshi-weather-bot/HEAD/README.md)
  - yannbellec: ECMWF 51 members from CDS — [README](https://raw.githubusercontent.com/yannbellec/polymarket-weather-bot/HEAD/README.md)
  - natestokens: 173 members — [README](https://raw.githubusercontent.com/natestokens/polymarket-weather-bot/HEAD/README.md)
- **Bias correction:**
  - natestokens per-city mean shifts — [README](https://raw.githubusercontent.com/natestokens/polymarket-weather-bot/HEAD/README.md)
  - AwpDemon rolling NWS warm-bias correction — [README](https://raw.githubusercontent.com/AwpDemon/kalshi-weather-bot/HEAD/README.md)
  - JHenzi 14-day rolling bias, +0.4–0.6°F — [README](https://raw.githubusercontent.com/JHenzi/weatherbots/HEAD/README.md)
  - Sully-Ok 45-day walk-forward bias and σ — [README](https://raw.githubusercontent.com/Sully-Ok/weather-prediction-market-model/HEAD/README.md)
- **Fat tails:** Student-t ν=4 in AadiXD200 and df=5 in Sully-Ok. Sully-Ok explains that a normal distribution would assign ~2% to outcomes that happen ~5% of the time, which creates fake edges on cheap contracts — [Sully-Ok](https://raw.githubusercontent.com/Sully-Ok/weather-prediction-market-model/HEAD/README.md); [AadiXD200](https://raw.githubusercontent.com/AadiXD200/polymarket-weather-bot/HEAD/README.md)
- **MOS/NBM:** k1hbles uses GFS MOS and NBM text (NBS) daily max from the Iowa Environmental Mesonet archive, keeping only runs available at decision time — [README](https://raw.githubusercontent.com/k1hbles/kalshi-edge/HEAD/README.md)
- **isotherm:**
  - Learned logarithmic opinion pool of market price, EMOS-calibrated NWS forecasts and climatology, plus a small MLP, normalized over the ladder and trained on log score. Starts equal to the market.
  - Tested NBM's own spread inside EMOS: "+0.04 to +0.05 for the forecast; isotherm +0.013 at 16:00, fails its 3-of-4 gate".
  - [README](https://raw.githubusercontent.com/physicalreasoning/isotherm/HEAD/README.md)
- **HRRR/GEFS via GRIB:** jdeepsingh28 uses Herbie/cfgrib for HRRR and GEFS — [README](https://raw.githubusercontent.com/jdeepsingh28/kalshi-weather-bot/HEAD/README.md)
- **Per-city model skill:** testedmedia claims "HRRR is strong for NYC, UKMO for London" across up to 28 models per city — [README](https://raw.githubusercontent.com/testedmedia/polymarket-weather-command-center/HEAD/README.md)
- **ML:**
  - XGBoost: AruneshDev, EddieTGH, Gpar307.
  - Transformer: EddieTGH, MAE 1.0°F claim.
  - Random Forest calibrator: BallesJr.
  - LinUCB bandit: JHenzi.
  - [AruneshDev](https://raw.githubusercontent.com/AruneshDev/Automated-Trading-System-Kalshi-Weather-Model/HEAD/README.md); [EddieTGH](https://raw.githubusercontent.com/EddieTGH/kalshi-weather-predictor/HEAD/README.md); [BallesJr](https://raw.githubusercontent.com/BallesJr/polymarket-weather-edge/HEAD/README.md)
- **METAR nowcasting:**
  - AadiXD200 ramps the observation weight from 0% to 80% through the day — [README](https://raw.githubusercontent.com/AadiXD200/polymarket-weather-bot/HEAD/README.md)
  - muzard:
    - Dead brackets come from the running max.
    - An optional "forecast path" uses sub-hourly national feeds as signal only (6-min Météo-France; 10-min KNMI/FMI/JMA; 1-min NEA), which give a 10–30+ minute lead over METAR.
    - Guards: ≥0.4°C margin because METAR rounds, and no entries 17–21h local.
    - [README](https://raw.githubusercontent.com/muzard/deadBracketBot/HEAD/README.md)
  - bnbi "same-day sniper" uses Monte-Carlo final-high from settlement-station observations — [README](https://raw.githubusercontent.com/bnbi/kalshi-weather-trading/HEAD/README.md)
- **Shrinkage to market:**
  - bnbi: `p̂ = w·model + (1−w)·price`, refuses trades beyond 25¢ disagreement — [README](https://raw.githubusercontent.com/bnbi/kalshi-weather-trading/HEAD/README.md)
  - Sully-Ok: fitted blend weight — [README](https://raw.githubusercontent.com/Sully-Ok/weather-prediction-market-model/HEAD/README.md)
  - k1hbles: logistic blend of market and model log-odds — [README](https://raw.githubusercontent.com/k1hbles/kalshi-edge/HEAD/README.md)
- **Market-structure (non-forecast) approaches:**
  - jdeepsingh28 tail premium selling as maker — [README](https://raw.githubusercontent.com/jdeepsingh28/kalshi-weather-bot/HEAD/README.md)
  - idlepraxis cheap-YES / expensive-NO rules — [README](https://raw.githubusercontent.com/idlepraxis/polymarket-weather-bot/HEAD/README.md)
  - BallesJr BUY_NO-only, inside a NO-token price band of [0.15, 0.40] — [README](https://raw.githubusercontent.com/BallesJr/polymarket-weather-edge/HEAD/README.md)

### Inferences
- The repos that tested hardest (bnbi, k1hbles, anaborne, tarang-tj, isotherm) agree that point-forecast accuracy is not the bottleneck. **Calibration of the probability layer, and selection bias when trading the largest disagreements, is.**
- The sophistication that matters is shrinkage to market, proper scoring, and point-in-time data.

### Gaps
- No repo found uses NBM probabilistic percentile grids (as opposed to NBS text) as a primary input. isotherm reports testing "NBM's own spread".
- Code-level details (exact Open-Meteo endpoints and model names) were not verified.

---

## Q3. Do any backtest against historical market prices, and what do they report?

### Takeaway
Yes. The rigorous studies show that **free public forecasts do not beat Kalshi daily-high prices after fees**:
- anaborne: 60,906 settled contracts. Market Brier 0.0772 vs model 0.1739; holdout −8.75¢ per contract.
- k1hbles: taker −2.5¢ per contract, t=−2.66.
- tarang-tj: contested Brier 0.305 vs 0.211.
- Nemesis-0: no edge established.
- bnbi: live −$27.

The only strong positive claim with proper methodology is isotherm, whose model starts from the market price and adds small corrections: sealed-test +$1,851, t=1.77, below conventional significance.

Positive Polymarket claims are mostly short paper runs at mid prices. BallesJr's edge decayed out of sample. The thin-market "dead bracket" captures are small (+$49.72).

### Cited Findings
- **anaborne/kalshi-temperature-calibration** (pre-registered, 2026-08-27):
  - Data: 21 city series, 60,906 settled markets, 10,677 city-days (2021-08-06 → 2026-08-25), 6.82M hourly ASOS rows.
  - Calibration: over 235,145 bucket-hours, Kalshi mid Brier **0.0772 vs model 0.1739**. "Where the model says 0.99, the bucket settles 0.71. Where the market says 0.99, it settles 1.00."
  - Holdout of 9 cities: 19,348 trades, **−8.75¢ per contract, −$27,039 paper**. Negative in all 4 seasons and all trade shapes.
  - Explanation: the entry rule "is an error-maximiser" because it selects on maximum disagreement.
  - [README](https://raw.githubusercontent.com/anaborne/kalshi-temperature-calibration/HEAD/README.md)
- **k1hbles/kalshi-edge**:
  - Setup: KXHIGH NY/CHI/MIA/AUS/DEN/LAX/PHIL, 96 days (Jul–Oct 2026), hourly bid/ask candles at 4 decision times, walk-forward.
  - Market Brier is best at every time (0.503 vs ~0.70 at same-day 12:00).
  - Taker blend: −2.5¢ per contract (t=−2.66).
  - Market+MOS combination: +1.7–2.2¢ (not significant). +4.6¢ before the settlement switch, +0.6¢ after.
  - Maker: −0.7¢. Spreads are 1¢ wide 64% of the time. Capacity ~$300–800 per day across 7 cities.
  - [README](https://raw.githubusercontent.com/k1hbles/kalshi-edge/HEAD/README.md)
- **tarang-tj/kalshi-weather-engine-report** (write-up only, code private):
  - First backtest +7.7% (22 fills), but model Brier 0.218 vs market 0.084.
  - After fixing 3 bugs (strike direction, bucket edges, settling on ERA5 instead of the official value): +29.7% on 134 fills, but Brier 0.139 vs 0.075.
  - Forward test, 4,433 markets through 2026-10-22: contested Brier 0.3047 vs 0.2114; paper ROI −3.37% on 212 picks.
  - Day-before: 420/420 test markets had zero trades before the cutoff.
  - [README](https://raw.githubusercontent.com/tarang-tj/kalshi-weather-engine-report/HEAD/README.md)
- **Nemesis-0/weather-prediction-market** (project closed):
  - V1: NOAA/NBM information beyond the 10 AM market state adds no reliable value. Log-loss delta +0.0144, CI [−0.0376, +0.0863]. Before a point-in-time timing fix, 4 observations had leaked.
  - V2: forecast revisions do not predict market moves.
  - V3, ForecastEx via IBKR: 76 of 78 apparent edges were blocked once Weather Underground settlement-source state was added.
  - [README](https://raw.githubusercontent.com/Nemesis-0/weather-prediction-market/HEAD/README.md)
- **physicalreasoning/isotherm** (Kalshi, 24,344 out-of-sample ladders, 7 cities, 4 read times; Zenodo DOI):
  - Skill: +0.035 to +0.070 nats per ladder over the market in all periods, but only +0.009 to +0.017 in the last 12 months.
  - Backtest Sharpe 2.06, deflated Sharpe 0.865, PBO 0.24.
  - Sealed test on highs (Jul–Oct 2026): +$1,851, Newey-West t 1.77. Monthly amounts declined: $1,029, $517, $246.
  - Twelve unseen cities: no read time clears zero.
  - [README](https://raw.githubusercontent.com/physicalreasoning/isotherm/HEAD/README.md)
- **bnbi**: live, 92 trades, −$27.01 net; model Brier 0.22 vs market 0.13 — [README](https://raw.githubusercontent.com/bnbi/kalshi-weather-trading/HEAD/README.md)
- **jdeepsingh28**: live maker, −$16 to −$28 after fees (detail in Q1) — [README](https://raw.githubusercontent.com/jdeepsingh28/kalshi-weather-bot/HEAD/README.md)
- **BallesJr** (Polymarket paper, clean regime):
  - 2026-06-10 → 07-10: 527 trades, +$157, win rate 32.5% vs 29.8% break-even.
  - 2026-07-10 → 08-12: 847 trades, −$592, t=−2.79. The author says the edge "has not held out of sample".
  - Data filters: BUY_YES won 11%. T+1 and T+2 were disabled at 18% and 4% win rates. NO priced under 0.10 had a ~0% win rate (adverse selection).
  - [README](https://raw.githubusercontent.com/BallesJr/polymarket-weather-edge/HEAD/README.md)
- **testedmedia**:
  - 730-day backtest against resolved Polymarket outcomes, gated at n ≥ 300 and a Wilson lower bound > 49%.
  - Only 4 bets pass: London/UKMO 60.05% (n=438), London/UKMO 2km 59.13%, London/ICON 57.53%, NYC/GFS-HRRR 55.73%. Base rate for a single bucket call is ~17%.
  - Warns that ASOS-proxy combos backtesting at 74–88% are overfit.
  - The README also shows a cherry-picked list of the account's biggest winning positions ($975–$2,241), which is a self-reported claim.
  - [README](https://raw.githubusercontent.com/testedmedia/polymarket-weather-command-center/HEAD/README.md)
- **muzard/deadBracketBot**:
  - In liquid markets (Paris), over 3,481 snapshots dead-NO asks had a minimum of 0.997, because the market leads the resolution METAR by ~7 minutes via the 6-minute feed.
  - In thin markets (Moscow, Shenzhen), sub-98¢ dead NO was captured. Live total +$49.72 over 2026-06-16 → 06-29, with zero losers. The author says scale was limited by bankroll and caps rather than liquidity.
  - [README](https://raw.githubusercontent.com/muzard/deadBracketBot/HEAD/README.md); [FINDINGS.md](https://raw.githubusercontent.com/muzard/deadBracketBot/HEAD/FINDINGS.md)
- **Short paper or tiny-sample claims:**
  - AadiXD200: +35.6% in 7 days at mid prices, excluding spread.
  - natestokens: +$77 on 23 trades.
  - AwpDemon: +$3.89 on 20 trades.
  - Sully-Ok: +$0.97 on 80.
  - [AadiXD200](https://raw.githubusercontent.com/AadiXD200/polymarket-weather-bot/HEAD/README.md); [natestokens](https://raw.githubusercontent.com/natestokens/polymarket-weather-bot/HEAD/README.md); [AwpDemon](https://raw.githubusercontent.com/AwpDemon/kalshi-weather-bot/HEAD/README.md); [Sully-Ok](https://raw.githubusercontent.com/Sully-Ok/weather-prediction-market-model/HEAD/README.md)
- **Backtest harnesses without published real-price results:**
  - Hongzhii/polymarket_temperature: websocket order-book recorder plus METAR, with a manual tick-stepping viewer.
  - Gpar307: Predexon order-book snapshots.
  - MihirM9 `backtesting/`.
  - RiekertQuant: synthetic data.
  - [Hongzhii](https://raw.githubusercontent.com/Hongzhii/polymarket_temperature/HEAD/README.md); [Gpar307](https://raw.githubusercontent.com/Gpar307/Polymarket_Weather_XGBoost_Template/HEAD/README.md)

### Inferences
- Kalshi KXHIGH prices are well calibrated and sharp by settlement morning. Free forecasts lose after the fee `ceil(0.07·P·(1−P))` and spread.
- Any surviving edge appears to be in:
  - (a) combining the market with a model rather than opposing it (isotherm; k1hbles' non-significant blend);
  - (b) thin or less-watched Polymarket cities with intraday observation latency (muzard);
  - (c) structural tail-selling, which was roughly break-even after fees.
- Polymarket has no equivalent large pre-registered study. Its edge claims are weaker but cover a more fragmented set of international markets.

### Gaps
- No rigorous Polymarket-wide historical-price backtest was found. testedmedia measures win rate against resolutions, not PnL against historical prices.
- isotherm's sealed-test details and FINDINGS.md were not read beyond the README.

---

## Q4. Data-collection tools for Polymarket/Kalshi historical prices, trades and order books

### Takeaway
For Polymarket, the key tools are:
- warproxxx/poly_data (2,346★): v2 on-chain fills via Envio HyperSync, after the 2026-04-28 CTF Exchange V2 migration broke the Goldsky path.
- Jon-Becker/prediction-market-analysis (3,932★): a 36 GiB Polymarket+Kalshi trades dataset plus indexers.
- SII-WANGZJ/Polymarket_data (894★): 1.1B records, on HF.

For Kalshi, the public candlestick and `/historical` endpoints are used directly by k1hbles and anaborne. Commercial or third-party scrapers exist on Apify.

### Cited Findings
- **warproxxx/poly_data** (2,346★, updated 2026-11-04, GPL-3.0):
  - v2 streams order events from the CTF Exchange V2 contract via Envio HyperSync.
  - "Polymarket migrated to a new set of CTF Exchange contracts on 2026-04-28 and stopped supporting their old subgraph indexer". The old Goldsky pipeline "no longer returns complete data". v1 is preserved at tag `v1-final`.
  - The v1 README offered an S3 snapshot `orderFilled_complete.csv.xz` (seen in the kevinbadi copy).
  - [poly_data README](https://raw.githubusercontent.com/warproxxx/poly_data/HEAD/README.md); [kevinbadi copy of v1 README](https://raw.githubusercontent.com/kevinbadi/polymarket-weather-quant/HEAD/README.md)
- **Jon-Becker/prediction-market-analysis** (3,932★, updated 2026-11-05): "largest publicly available dataset of Polymarket and Kalshi market and trade data". 36 GiB compressed `data.tar.zst`, plus indexers for market metadata and trades via API and blockchain, stored as Parquet — [README](https://raw.githubusercontent.com/Jon-Becker/prediction-market-analysis/HEAD/README.md)
- **SII-WANGZJ/Polymarket_data** (894★): 1.1 billion Polymarket trading records from Polygon plus Gamma, published on Hugging Face as `SII-WANGZJ/Polymarket_data` — [README](https://raw.githubusercontent.com/SII-WANGZJ/Polymarket_data/HEAD/README.md)
- **Other Polymarket data repos (description only):**
  - suitedaces/polyterminal: millisecond order book to ClickHouse, with backtesting.
  - DineshKumar8399/polymarket-orderbook-dataset: 237M order-book observations, Jul–Aug 2026.
  - LuciferForge/polymarket-historical-data: 18.6M 15-minute snapshots.
  - tickfoundry and crowdintel-xyz: L2 tick samples.
  - [GitHub search](https://github.com/search?q=polymarket+historical+data&type=repositories)
- **Commercial Polymarket order-book history:** Gpar307 pulls historical order-book snapshots via the **Predexon API** — [README](https://raw.githubusercontent.com/Gpar307/Polymarket_Weather_XGBoost_Template/HEAD/README.md)
- **Kalshi:**
  - k1hbles `fetch_kalshi.py` pulls events, markets and hourly candles and "switches to `/historical` endpoints automatically". All endpoints are public and unauthenticated — [README](https://raw.githubusercontent.com/k1hbles/kalshi-edge/HEAD/README.md)
  - anaborne pulled 60,906 settled markets "across two API tiers". Its own correction notes that an early claim of "no archive of settled markets" was false — [README](https://raw.githubusercontent.com/anaborne/kalshi-temperature-calibration/HEAD/README.md)
  - harrodyuan/kalshi-data-collector (20★) collects open events and markets with authentication — [README](https://raw.githubusercontent.com/harrodyuan/kalshi-data-collector/HEAD/README.md)
- **Apify actors** for Kalshi KXHIGH/KXLOW prices and settled temperatures (bigdavidson, diopside, dataio) — [Apify bigdavidson](https://apify.com/bigdavidson/kalshi-weather-markets); [Apify diopside](https://apify.com/diopside/kalshi-weather-markets)
- **Hugging Face:** search found only general datasets, e.g. ImpliedData/prediction-markets (Kalshi metadata, no prices) and athetus/predmarkets-kalshi-live (contents not described). No Kalshi-weather-specific dataset was found — [HF ImpliedData](https://huggingface.co/datasets/ImpliedData/prediction-markets); [HF athetus](https://huggingface.co/athetus)
- **Weather archives used:**
  - Iowa Environmental Mesonet for GFS MOS/NBS archives and ASOS (k1hbles, natestokens, EddieTGH).
  - Open-Meteo historical-forecast archive (Sully-Ok).
  - NOAA GHCND (bnbi).
  - [k1hbles](https://raw.githubusercontent.com/k1hbles/kalshi-edge/HEAD/README.md); [Sully-Ok](https://raw.githubusercontent.com/Sully-Ok/weather-prediction-market-model/HEAD/README.md)

### Inferences
- For weather-market backtests:
  - Kalshi: public hourly candles plus historical settled markets are enough for quote-level studies, but give no size.
  - Polymarket: on-chain fills (poly_data v2, Jon-Becker) give trades. Order-book history needs self-recording (Hongzhii, polyterminal) or vendors (Predexon, tick datasets).
- Pipelines built on Goldsky before 2026-04-28 are incomplete afterwards.

### Gaps
- Kalshi `/historical` endpoint semantics and cutoffs were not verified against Kalshi docs.
- PyPI packages (e.g., Kalshi or Polymarket clients) were not surveyed in depth.

---

## Q5. Resolution-source specifics (NWS CLI vs METAR, Wunderground, °F/°C rounding)

### Takeaway
Resolution-source mismatch is the most-documented pitfall.
- **Kalshi daily highs** historically settled on the NWS Daily Climate Report (CLI). From about **2026-08-14** at least some daily markets moved to The Weather Company, which shifted measured edges.
- **Polymarket** resolves on Weather Underground's whole-degree daily max for a specific airport station. Station choice (Le Bourget vs CDG, Midway vs O'Hare, Hobby vs Bush, Lau Fau Shan for Shenzhen) and WU-vs-METAR divergence create false edges.

### Cited Findings
- **Kalshi switch to TWC:**
  - k1hbles: "Kalshi moved to The Weather Company on 2026-08-14." Over 672 city-days, settlement matched the NWS climate report on 671; the exception was Miami 2026-08-29 (Kalshi 90°F vs NWS 85°F). Blend edge was +4.6¢ before the switch and +0.6¢ after — [README](https://raw.githubusercontent.com/k1hbles/kalshi-edge/HEAD/README.md)
  - Gizmodo reports that the NYC daily-high market rules said it would settle on The Weather Company data from Aug 14, replacing NWS — [Gizmodo](https://gizmodo.com/kalshi-teams-up-with-the-weather-co-on-markets-that-are-nearly-impossible-to-insider-trade-2000803871)
  - The partnership was announced 2026-08-28 — [Artemis](https://artemis.bm/news/prediction-market-kalshi-partners-with-the-weather-company-for-weather-hedge-settlements)
  - Conflict: Kalshi's general weather-markets help page still names the NWS Daily Climate Report — [Kalshi help](https://help.kalshi.com/markets/popular-markets/weather-markets)
- **anaborne (NWS vs TWC regimes):**
  - Settled value runs **+0.72°F above the final observed hourly ASOS max** (sd 0.74) on NWS, and +0.86°F (sd 0.67) on TWC.
  - "Dominated" buckets still settled YES on 0.186% of NWS bucket-hours, up to 0.39% in spring. So "observation floor" logic leaks.
  - Station map: Houston = Hobby (not Bush), Chicago = Midway (not O'Hare).
  - [README](https://raw.githubusercontent.com/anaborne/kalshi-temperature-calibration/HEAD/README.md)
- **Settling on the wrong data:**
  - tarang-tj settled on ERA5 instead of Kalshi's official rounded high and fixed it as one of three bugs — [README](https://raw.githubusercontent.com/tarang-tj/kalshi-weather-engine-report/HEAD/README.md)
  - bnbi uses GHCND official station data, "never the provisional NWS obs-feed max or reanalysis" — [README](https://raw.githubusercontent.com/bnbi/kalshi-weather-trading/HEAD/README.md)
  - JHenzi and jdeepsingh28 treat NWS CLI as truth — [JHenzi](https://raw.githubusercontent.com/JHenzi/weatherbots/HEAD/README.md); [jdeepsingh28](https://raw.githubusercontent.com/jdeepsingh28/kalshi-weather-bot/HEAD/README.md)
- **Polymarket / Wunderground:**
  - Market rules say the source "measures temperatures to whole degrees Fahrenheit" or Celsius, using Wunderground's highest reading for a named airport station. Markets cannot resolve YES until the day's data is finalized — [polyguana mirror of rules](https://polyguana.com/market/2074633); [frenzycap](https://www.frenzycap.com/predictions/event/polymarket/highest-temperature-in-chicago-on-june-16-2026)
  - testedmedia:
    - Uses the WU **V1 archive** as "the number the market actually resolves on", cross-checked against WU V3 and METAR.
    - Found London WU-vs-ASOS divergence on **382 of 730 days**.
    - An NYC cross-check showed ASOS-exact scoring "can be 20+ points off" the actual Polymarket rate.
    - [README](https://raw.githubusercontent.com/testedmedia/polymarket-weather-command-center/HEAD/README.md)
  - BallesJr:
    - Paris resolves at **Le Bourget, not CDG**.
    - Across 500+ historical trades, daily highs from station METARs agreed with resolutions 93% of the time vs **66% for ERA5**.
    - Early trades were invalidated by a wrong station, unparsed °F markets and model-interpolated observations.
    - [README](https://raw.githubusercontent.com/BallesJr/polymarket-weather-edge/HEAD/README.md)
  - muzard:
    - The repo description says it "measured that its apparent edge was a resolution-source mismatch". It has a "post-Seoul failsafe" `resolver_guard.py` requiring 24h agreement with the resolver's own table before a city trades.
    - Shenzhen resolves on WU's table for HKO AWS 45035 (Lau Fau Shan). Their h:00 sampling disagreed with WU on ~45% of rows. The repo models rounding (`half_up`) and row-versioning, and its `--twc` mode reads the resolver's own TWC timeseries.
    - Moscow resolves off a non-WU source.
    - METAR rounding motivates a ≥0.4°C margin.
    - [README](https://raw.githubusercontent.com/muzard/deadBracketBot/HEAD/README.md); [FINDINGS](https://raw.githubusercontent.com/muzard/deadBracketBot/HEAD/FINDINGS.md); [GitHub search listing](https://github.com/search?q=polymarket+temperature&type=repositories)
  - Nemesis-0: adding already-observed **Weather Underground settlement-source state** removed 76 of 78 apparent edges — [README](https://raw.githubusercontent.com/Nemesis-0/weather-prediction-market/HEAD/README.md)
  - Gpar307 ships a `Wundergrounds_scraper.py` for outcome resolution — [README](https://raw.githubusercontent.com/Gpar307/Polymarket_Weather_XGBoost_Template/HEAD/README.md)
- **°C vs °F:**
  - natestokens: Tokyo and Singapore use single-degree Celsius brackets, which are not supported natively — [README](https://raw.githubusercontent.com/natestokens/polymarket-weather-bot/HEAD/README.md)
  - BallesJr handles both formats "with unit-aware bin corrections" — [README](https://raw.githubusercontent.com/BallesJr/polymarket-weather-edge/HEAD/README.md)
  - Typical Polymarket US layout: 7 buckets (two tails plus five 2-degree middles) per testedmedia, or ~11 per MihirM9 — [testedmedia](https://raw.githubusercontent.com/testedmedia/polymarket-weather-command-center/HEAD/README.md); [MihirM9](https://raw.githubusercontent.com/MihirM9/polymarket-weather-bot/HEAD/README.md)
- **Kalshi parsing pitfalls:** "less than" tail strikes, wrong bucket edges (tarang-tj), `strike_type` and dollar-string price fields (AwpDemon), and schema bugs that silently dropped 52,704 markets (anaborne) — [tarang-tj](https://raw.githubusercontent.com/tarang-tj/kalshi-weather-engine-report/HEAD/README.md); [AwpDemon](https://raw.githubusercontent.com/AwpDemon/kalshi-weather-bot/HEAD/README.md); [anaborne](https://raw.githubusercontent.com/anaborne/kalshi-temperature-calibration/HEAD/README.md)

### Inferences
- Any bot must map every market to its exact resolution station and source, and validate it against historical resolutions before trusting edges. Many of the dramatic "edges" in naive bots are likely station or source or rounding artifacts.
- Kalshi's mid-2026 move to TWC for (at least some) daily markets breaks older NWS-CLI-based calibrations.
- Settlement values sit systematically above the hourly-ASOS max. Hourly METAR misses sub-hourly peaks, so 1-minute or 5-minute ASOS and CLI data matter for Kalshi.

### Gaps
- The exact Polymarket rounding rule for fractional readings and WU's finalization behaviour are not documented in primary Polymarket docs found here. The aggregator mirrors do not state how fractional readings are rounded.
- The scope of Kalshi's TWC switch (all KXHIGH cities, or NYC first) is not confirmed by a primary Kalshi rules document; sources conflict.
- www.cs.utexas.edu (a Kalshi weather calibration blog) and huggingface.co were unreachable from this session.
