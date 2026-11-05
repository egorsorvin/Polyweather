# Weather/Temperature Prediction Markets: Efficiency, Calibration and Resolution Pitfalls

Method note: this session's network blocked most hosts (arxiv.org, help.kalshi.com, weather.gov, mesonet.agron.iastate.edu, wethr.net, nextpredict.io, dev.to, minutetemp.com, interactivebrokers.com, autodidacts.io, papers.cool). Only github.com pages were fetched in full. Everything else below comes from **search-result snippets**, which are labelled. Primary rule texts (Kalshi contract terms, Polymarket market rules) could not be read directly. Check them before relying on any rule detail.

## Q1. Are Kalshi/Polymarket temperature markets efficient or beatable? (Academic and quantitative evidence; general favourite-longshot bias; weather derivatives)

### Takeaway
All the independent quantitative tests I found (2026) say Kalshi daily-high markets are well calibrated. Strategies using free public forecasts (GFS/ECMWF/ICON via Open-Meteo, hourly ASOS) lose money after fees. The market's mid-quote beats such models by a wide margin, especially intraday. The only leftover edges reported are thin maker-side ones (buying the 97–99c favourite at the front of the queue) and rule/settlement knowledge (the CLI vs hourly-METAR offset). Across Kalshi as a whole, a favourite-longshot bias exists and is shrinking over time. For weather specifically, one backtest found that fading longshots lost money after fees.

### Cited Findings
**Kalshi temperature-specific**
- Crosier, "Prediction Markets Beat the Weather Forecast on Tomorrow's High Temperature" (arXiv 2609.23969, Sept 2026). It reads the Kalshi bracket ladder as a probability distribution and measures how much information the market has beyond public forecasts. The market beats the forecast, and the advantage is smallest in Miami because day-to-day variation in highs is low there. Some city series start in 2021. I could not get the headline numbers because arxiv was blocked; this is from snippets — [arXiv PDF](https://arxiv.org/pdf/2609.23969); [arXiv HTML](https://arxiv.org/html/2609.23969v1)
- A search snippet says the Crosier study used contracts only through Aug 12, 2026, when NWS was still the settlement source — [search snippet re arXiv 2609.23969](https://arxiv.org/html/2609.23969v1)
- Concurrent work cited by Crosier: Brown (2026) compares ForecastEx temperature markets with 20 forecast products at 24 locations over seven months of 2026 — [arXiv PDF](https://arxiv.org/pdf/2609.23969)
- anaborne pre-registered study (GitHub, 2026), fetched in full:
  - Data: 21 Kalshi daily-max series and 60,906 settled contracts, for city-days 2021-08-06 to 2026-08-25 (10,677 city-days). Also 6.8M hourly ASOS rows.
  - Calibration: over 235,145 bucket-hours the market mid scored Brier **0.0772** against the model's **0.1739**. The market was better calibrated in 11 of 12 probability bins. Where the market said 0.99, outcomes settled 1.00; the model's 0.95+ bin settled 0.713.
  - Holdout of 9 cities, 19,348 trades: **−8.75c/contract** (−$27,039 on paper), negative in every season, with every 95% CI below zero. The kill criterion triggered.
  - Why it lost: the settled value ran **+0.72°F above the final observed hourly max** under NWS (sd 0.74) and **+0.86°F** under Weather Company (sd 0.67). An entry rule of "trade the largest disagreement with the market" picks out the cases where the model is most wrong (mid-bucket buys settled Yes only 11.1% of the time).
  - Observation-floor test: under NWS, 511 of 274,552 (0.186%) "dominated" bucket-hours, i.e. already ruled out by hourly obs, still settled Yes. Spring reached 0.39%. **52–64% of city-days sat within 2°F of a bucket flip.**
  - Source: [GitHub anaborne/kalshi-temperature-calibration](https://github.com/anaborne/kalshi-temperature-calibration)
- MiguelTheGamer walk-forward backtest (GitHub, May–Oct 2026; NYC/Chicago/Miami/LA; about 48 days per city), fetched in full:
  - The market beat the model's log loss in every cell. Example, NYC day-before: market 0.95 vs model 1.22. With live METAR, NYC at 5pm: market 0.03 vs model 0.65. Prices have essentially converged on the answer by about 5pm local.
  - Blending model and market never beat the market alone. Simulated P&L: −14% (day-before) and −9% (day-of).
  - Fee model: 7%·P·(1−P) taker. The best "risk-free" combination across 38 events returned −5c after fees.
  - Favourite-longshot test (about 11k snapshots): buying NO on longshots lost 2–8% after fees in every bucket. Mids were well calibrated.
  - Makers (1,500 markets, about 950k fills, 65M contracts): −0.9% ±3.1% overall. Buying the 97–99c side made **+0.9% ±0.2%**, but this is thin and depends on queue position.
  - Settlement vs hourly max over 204 station-days: equal 39% of the time, +1°F 52%, +2°F 7%.
  - Source: [GitHub MiguelTheGamer/kalshi-weather-backtest](https://github.com/MiguelTheGamer/kalshi-weather-backtest)
- CalibShi notebook (Zerve): ECE of 0.01624 for raw KXHIGHNY prices, falling to 0.00109 after isotonic recalibration. Methodology unverified and promotional in tone, from a snippet — [Zerve CalibShi](https://www.zerve.ai/gallery/85cce830-f612-4b23-8b78-34d7da65a2c6)
- Kalshi's own research says daily weather markets track perfect calibration across five horizons, with more divergence at the extremes. It reports accuracy/Brier on about 69.6k–73.3k resolved markets per horizon. This is the exchange's self-interested claim, from a snippet — [Kalshi research](https://kalshi.com/research/insights/hedging-climate-risk)
- arXiv 2602.19520, "Decomposing Crowd Wisdom": short-horizon weather markets show a calibration pattern different from political markets, which are compressed toward 50%. From a snippet — [arXiv 2602.19520](https://arxiv.org/pdf/2602.19520)

**General favourite-longshot bias (FLB)**
- Snowberg & Wolfers (JPE 2010) use horse-racing data, not Kalshi. They find FLB is driven by **misperception of probabilities** (Prospect Theory), not risk-love — [Wharton Mack Institute](https://mackinstitute.wharton.upenn.edu/2010/explaining-the-favorite-longshot-bias-is-it-risk-love-or-misperceptions/); [NBER w15923](https://www.nber.org/system/files/working_papers/w15923/w15923.pdf)
- Bürgi, Deng & Whelan (UCD WP2025_19, Sept 2025), more than 300k Kalshi contracts across all categories:
  - Systematic FLB; low-priced contracts return poorly.
  - Average return about −20% before fees and about −22% after.
  - Prices get more accurate near close, and the bias is shrinking over time.
  - Makers and Takers show different patterns.
  - Sources: [UCD WP2025_19](https://www.ucd.ie/economics/t4media/WP2025_19.pdf); [Whelan PDF](https://www.karlwhelan.com/Papers/Kalshi.pdf)
- A 2026 GWU working paper also finds FLB on Kalshi and links it to trader disagreement and the overweighting of small probabilities. Details not checked — [GWU 2026-001](https://www2.gwu.edu/~forcpgm/2026-001.pdf)

**Weather derivatives (CME HDD/CDD)**
- Chincarini, "No Chills or Burns from Temperature Surprises" (J. Futures Markets 31(1), 2011):
  - CME weather futures look "very efficient despite lack of liquidity". They are tested against forecasts and for over- or under-reaction to temperature surprises.
  - Risk premia vary across cities and over time. The 2009 working version calls them significant premia that do not look like standard speculator compensation.
  - Sources: [RePEc](https://ideas.repec.org/a/wly/jfutmk/v31y2011i1p1-33.html); [EFMA 2009 WP](https://www.efmaefm.org/0efmameetings/EFMA%20ANNUAL%20MEETINGS/2009-Milan/papers/EFMA2009_0595_fullpaper.pdf)
- CME HDD (Nov–Mar) and CDD (May–Sep) seasonal indices pay $20 per index point (°F). The market is incomplete because the underlying cannot be traded, so pricing uses burn analysis, temperature models and actuarial methods — [EFMA 2009 WP](https://efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2009-Milan/papers/EFMA2009_0595_fullpaper.pdf)

### Inferences
- Edge from public NWP forecasts alone is gone. The market already contains it, and the 7%·P(1−P) taker fee plus the spread wipe out small edges. What remains is (a) modelling the settlement source exactly (the +0.7–0.9°F CLI/TWC vs hourly-METAR offset, timing windows), (b) providing liquidity as a maker on near-certain favourites late in the day, and (c) possibly paid or ensemble data and nowcasting. None of these was shown to be profitable at scale.
- Because 52–64% of city-days sit within 2°F of a bracket edge, small systematic settlement offsets matter more than forecast skill.

### Gaps
- Crosier paper headline numbers (skill-score gap vs NBM/NWS, by city): not retrieved because arxiv was blocked.
- I found no peer-reviewed study of Polymarket weather market calibration.
- Weather-specific FLB numbers from academic work (as opposed to GitHub backtests): not found.

## Q2. Polymarket weather markets: growth, calibration, who profits, disputes

### Takeaway
Polymarket's weather markets grew fast in 2025–26, with reports of about $2M daily volume. P&L is concentrated among a few specialist and bot traders. The documented incidents are about **data integrity and resolution**, not calibration: the Paris CDG sensor-tampering probe, the Miami May 2026 misconfiguration and archived markets, and the Wunderground-vs-NWS daily-high mismatch. I found no rigorous calibration study.

### Cited Findings
- Headline: "Polymarket Turns Weather Forecasts into a $2 Million Daily Trading Market". Snippet only, date unverified — [KuCoin news](https://www.kucoin.com/news/flash/polymarket-turns-weather-forecasts-into-2m-daily-trading-market)
- DeFiRate lists the Weather category at about $70M (time window unclear) and total Polymarket 2026 volume at $77.6B through Nov 2 — [DeFiRate](https://defirate.com/prediction-markets/volume/polymarket/)
- Polycopy leaderboard (third party): the top weather trader made about +$41K over 30 days; the top 25 made +$286.7K combined over 30 days as of Oct 22, 2026 — [Polycopy](https://polycopy.app/polymarket-leaderboard/weather)
- Thin markets: over 80% of volume in markets under $10k comes from bots, per a professor quoted by CNBC (Jul 2026) — [CNBC](https://www.cnbc.com/2026/07/02/prediction-markets-mostly-have-thinly-traded-contracts-.html)
- Paris (Apr 2026): two accounts made about $37k from temperature spikes at Charles de Gaulle. French police are investigating possible weather-device tampering — [NPR](https://www.npr.org/2026/04/23/nx-s1-5797876/polymarket-paris-weather-bet); [Cointelegraph](https://cointelegraph.com/news/suspicion-rises-after-polymarket-traders-win-37k-on-paris-weather-data-glitch)
- Miami May 17, 2026:
  - Resolved No even though Wunderground KMIA showed 87°F, inside the 86–87 bucket. The market was later archived "along with the money bet on it".
  - Polymarket cited a "misconfiguration affecting a small set of markets, mostly weather markets". A secondhand digest names Seoul, Miami, Mexico City and Hong Kong as affected.
  - From a snippet — [Autodidacts](https://www.autodidacts.io/polymarket-temperature-markets-dissappear/)
- NYC LaGuardia (Dec 2025): Ryan Maue (X) says the NWS daily high was 30°F but the market resolved to 29°F because Polymarket used Wunderground hourly obs instead of the NWS daily high — [X/@RyanWeather](https://x.com/RyanWeather/status/2000941328306463201)
- Milan (LIMC) METAR outage: an opinion piece argues the rule fails to separate "no data" from "low temperature" and that Polymarket has not defined "no data". Outcome unverified — [PredictionsMarketFans](https://predictionsmarketfans.com/forecasting/polymarket-weather-markets-metar-data-failure)
- Hong Kong markets resolve on Hong Kong Observatory "Daily Extract" data once finalized; revisions after first publication are not considered. Spring 2026 HK markets show "No dispute". The snippet said "Absolute Daily Min" for a highest-temperature market, which is probably a snippet garble; check the market — [Polymarket HK May 4 2026](https://polymarket.com/event/highest-temperature-in-hong-kong-on-may-4-2026)
- The GitHub bot polymarket-kalshi-weather-bot (31-member GFS ensemble, Kelly sizing) reports "highest profits $1.8k", which is a tiny scale — [GitHub suislanchez](https://github.com/suislanchez/polymarket-kalshi-weather-bot)

### Inferences
- On Polymarket the risk sits mostly in the oracle and data layer: station outages, misconfigured sources, sensor manipulation, and archived or voided markets. Price calibration is the smaller concern. Profitable traders seem to be specialists exploiting settlement-source details, plus bots.

### Gaps
- I found no Dune dashboard isolating weather volume or P&L, and no Polymarket weather calibration analysis.
- I found no documented UMA vote dispute specific to a weather market. The incidents above were handled by Polymarket (archive or misconfiguration) or are still under investigation.

## Q3. Resolution mechanics and pitfalls (Kalshi CLI/TWC; Polymarket Wunderground → NOAA/METAR; ASOS/METAR quirks)

### Takeaway
**Kalshi** daily highs historically settled on the NWS CLI daily max (whole °F, local standard time midnight to midnight). In about mid/late Aug 2026 the source reportedly switched to **The Weather Company (TWC)**, while station naming still uses CLI codes. **Polymarket** moved most cities from Wunderground to NOAA weather.gov station timeseries around Aug 23 (year likely 2026). That source counts METAR and SPECI only; 5-min data, 6-hour extremes, DSM and CLI are excluded. Some markets link the aviationweather.gov METAR API instead. The core quirk is rounding and sampling: ASOS works in whole °F, METARs report whole °C, and the CLI max comes from a running mean that peaks between hourly obs. This makes settled CLI/TWC highs typically 0–2°F above the hourly-METAR max.

### Cited Findings
**Kalshi**
- Daily high/low markets switched from NWS CLI to The Weather Company in August 2026. Sources disagree on the date (Aug 14 vs Aug 27). Precipitation and snow reportedly still settle on NWS. Station naming still uses CLI codes (e.g., CLISDF), and a market titled "SATX" was reported to settle at a Louisville code. All from snippets — [Yahoo Finance: Kalshi & Weather Co.](https://finance.yahoo.com/markets/options/articles/kalshi-weather-co-join-forces-110000142.html); [Kalshi news: partnership](https://news.kalshi.com/p/kalshi-weather-company-partnership); [DEV.to "SATX settles in Louisville"](https://dev.to/matveyg/kalshis-market-titled-highest-temperature-satx-settles-in-louisville-22eh)
- The Kalshi help page (about 105 days old at time of search) still describes the old setup: daily markets on the NWS Daily Climate Report and hourly markets on TWC. It likely predates the switch — [Kalshi Help: Weather Markets](https://help.kalshi.com/en/articles/13823837-weather-markets)
- The backtest author also states: "Markets now settle on The Weather Company's reading, not the NWS climate report" — [GitHub MiguelTheGamer](https://github.com/MiguelTheGamer/kalshi-weather-backtest)
- Station traps: Chicago settles on **Midway (KMDW)**, not O'Hare; NYC on **Central Park (KNYC)**; Houston on **Hobby**, not Bush — [GitHub anaborne](https://github.com/anaborne/kalshi-temperature-calibration); [Polymart guide snippet](https://polymart.app/blog/polymarket-weather-markets)

**NWS CLI mechanics**
- The climate day is **midnight to midnight Local Standard Time**, so during DST it is effectively **1:00 a.m. to 1:00 a.m. local clock time**.
  - The first mandatory CLI issuance comes between 12:30 and 5:00 a.m. local for the previous LST day; later updates and corrections can follow.
  - Snippets of an NWS directive and a third-party scraper (the scraper says the final report usually lands 1–8 AM local).
  - Sources: [NWS Directive 10-1004](https://www.weather.gov/media/directives/010_pdfs/pd01010004curr.pdf); [Apify NWS CLI scraper](https://apify.com/staymeter-labs/nws-daily-climate-reports)
- The AWIPS climate program builds the CLI from the ASOS **Daily Summary Message (DSM)**. The DSM is the provisional high issued shortly after midnight — [Apify NWS daily high/low](https://apify.com/staymeter-labs/nws-daily-high-low-live)
- The CLI high is the **maximum of a 5-minute running mean, rounded to whole °F**. Interactive Brokers gives an example: the NWS Time Series Viewer showed 88°F, the CLI 87°F, and the hourly-METAR max 86°F. From a snippet; another guide says ASOS samples every 10 s and averages to 1 minute, so the exact averaging interval is unresolved — [IBKR Campus](https://www.interactivebrokers.com/campus/?p=238652); [precipitation-ai guide](https://precipitation-ai.pages.dev/learn/nws-settlement-data)
- NWS LOT FAQ, from snippets:
  - ASOS stores whole °F, which is converted to °C for METAR. 5-min METARs carry whole °C, and decoding sites convert back to °F and round again, which explains most mismatches.
  - The T-group carries tenths °C, but only in hourly reports and only at some stations.
  - Highs can occur between METARs; a 1–2 minute spike can set the daily high without appearing in any METAR.
  - "Almost all perceived discrepancies … are not errors in the CLI."
  - Source: [NWS LOT Weather Observations FAQ](https://www.weather.gov/lot/weather_observations_faq)
- A Wikipedia-sourced claim, tagged "citation needed": ASOS computes T-group °C from whole °F. If true, T-group tenths take only a limited set of values (every whole °F maps to one specific x.x°C), so the °F can be recovered exactly from the T-group. Unconfirmed — [Wikipedia SYNOP/METAR snippet](https://en.wikipedia.org/wiki/SYNOP)
- Measured offsets: settled value minus final hourly max averaged +0.72°F under NWS and +0.86°F under TWC. Across 204 station-days the offset was 0 in 39%, +1 in 52% and +2 in 7%. Under the NWS regime, 0.19% of buckets already ruled out by hourly obs still settled Yes — [GitHub anaborne](https://github.com/anaborne/kalshi-temperature-calibration); [GitHub MiguelTheGamer](https://github.com/MiguelTheGamer/kalshi-weather-backtest)

**Polymarket**
- A trader post (BeefSlayer, X) says that starting Aug 23 all temperature markets would resolve from NWS weather.gov instead of Weather Underground, "still based on METARs and SPECIs", which should end Wunderground discrepancies. A reply claims UUWW (Moscow Vnukovo) counted only METAR and not SPECI — [X/@BeefSlayer_](https://x.com/BeefSlayer_/status/2091291881594372231)
- Third-party resolution checker (Sept 2026):
  - 48 of 51 cities settle on NOAA station data; only Jinan and Taipei remain on Wunderground.
  - The NOAA page's Temp column holds only official METAR and SPECI obs; **5-min data, 6-hour extremes, DSM and CLI never count**.
  - Sources: [Apify Polymarket resolution checker](https://apify.com/bigdavidson/polymarket-weather-resolution); [Apify Polymarket weather markets](https://apify.com/bigdavidson/polymarket-weather-markets)
- Some markets (e.g., Dallas Nov 4, 2026) list an **aviationweather.gov METAR API** URL as the source, with the daily max taken from local midnight — [Polymarket Dallas Nov 4 2026](https://polymarket.com/event/highest-temperature-in-dallas-on-november-4-2026); [vweatherstation](https://vweatherstation.com/prediction-markets/)
- **Polymarket US** (the CFTC venue) reportedly settles on the NWS Daily Climate Report, unlike the international product — [Polymart guide snippet](https://polymart.app/blog/polymarket-weather-markets)
- Pre-switch Wunderground pitfall: hourly obs undercount the official daily high, as in the KLGA 29 vs 30°F case — [X/@RyanWeather](https://x.com/RyanWeather/status/2000941328306463201)

**Consolidated pitfall list**
1. **Wrong station**: city name ≠ settlement station (KMDW, KNYC, Hobby; Kalshi CLI code mislabels like "SATX"→Louisville).
2. **Source regime change**: Kalshi moved CLI→TWC (Aug 2026) and Polymarket moved Wunderground→NOAA timeseries/METAR (around Aug 23). Historical backtests mix regimes.
3. **Climate-day window**: NWS uses LST, so in summer the day runs 1am–1am local clock time. Polymarket METAR markets use local midnight. Late-evening or overnight warm advection can set the "daily" high outside the expected hours.
4. **Sampling**: the CLI/TWC max catches sub-hourly peaks (5-min running mean); hourly METAR does not. That is +0–2°F, about +0.7–0.9°F on average.
5. **Rounding chain**: whole °F (ASOS) → whole °C (METAR body) → °F again (decoders/Wunderground) can give off-by-one or "impossible" °F values. Using the T-group (tenths °C) recovers precision but exists only in hourly obs at some stations.
6. **METAR vs SPECI inclusion**: Polymarket's NOAA source reportedly includes SPECI. Some markets or stations reportedly counted METAR only (UUWW claim). Read the rule text per market.
7. **Excluded data**: on Polymarket NOAA-sourced markets, 6-hour max groups (1xxxx), 24-hour groups, DSM, CLI and 5-min data do not count, even if they show a higher value.
8. **Preliminary vs final and revisions**: CLI may be re-issued or corrected. Polymarket HK markets ignore post-publication revisions. Kalshi's revision policy was not verified.
9. **Missing data or outages**: undefined handling (Milan LIMC case).
10. **Oracle/config failures and manipulation**: Miami May 2026 archived markets; Paris CDG suspected sensor tampering.

### Inferences
- For Polymarket NOAA/METAR markets, the settled value is the max of reported obs (whole °C or derived °F), so it systematically comes in *below* the true ASOS peak. For Kalshi (CLI/TWC) the settled value comes in *above* the hourly max. A model trained on one platform's settlement is biased on the other.
- Because the CLI's LST window and the local-midnight METAR window differ by an hour in summer, the same station-day can settle differently on the two platforms.

### Gaps
- Exact Kalshi KXHIGH contract-term text after the TWC switch (window, rounding, revision cutoff): not retrieved because help.kalshi.com was blocked.
- Official Polymarket rule text on routine-METAR-only vs SPECI: conflicting third-party claims. The premise "SPECI excluded" was **not** confirmed; most sources say SPECI is included.
- Exact Wunderground rounding and revision behaviour: no source found.
- Whether 6-hour max groups ever enter Kalshi/TWC settlement: unknown.
