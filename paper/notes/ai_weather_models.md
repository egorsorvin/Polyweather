# ML/AI weather forecasting models (2023–2026) and how they are evaluated: gaps for station-level, settlement-exact probabilistic daily Tmax

Method note (read first): research done on 2026-11-06. **WebFetch to arxiv.org and zenodo.org was blocked** (DNS not allowed in this sandbox), so almost all findings below come from **search-engine snippets/summaries** [S]. Only one page was **read in full** [F]: the CastCheck GitHub README. Items marked [P] are from my prior knowledge, not re-verified this session — treat them as leads to check, not citations. Several important papers are 2026 arXiv preprints (IDs 26xx.xxxxx) and are not peer-reviewed.

## Q1. Models: release, resolution, probabilistic or not, data availability

### Takeaway
By late 2026 the frontier has moved from deterministic ERA5-trained emulators (GraphCast, Pangu, FourCastNet, 2023) to operational probabilistic ensembles (ECMWF AIFS-ENS operational July 2025; NOAA AIGEFS Dec 2025; Google WeatherNext 2 Nov 2025) and, most recently, models trained on raw observations with a dedicated station head (WeatherNext 3, Sept 2026). Real-time output is publicly available for AIFS/AIFS-ENS (ECMWF open data), NOAA AI models, and WeatherNext 2 (BigQuery/Earth Engine).

### Cited Findings
**Google DeepMind / Google Research**
- GraphCast: "Learning skillful medium-range global weather forecasting", Science vol. 382, 2023 [S] — [Awesome-LWMs list](https://github.com/jaychempan/Awesome-LWMs). [P] deterministic, 0.25°, 6-hourly, ERA5-trained.
- GenCast: "Diffusion-based ensemble forecasting for medium-range weather", Nature, Dec 2024 [S] — [Awesome-LWMs](https://github.com/jaychempan/Awesome-LWMs). On WeatherBench 2 at 1.5°, GenCast Z500 CRPS 20.2 vs 22.4 for IFS ENS (as reported in a third-party comparison; GenCast regridded from native 0.25°; GenCast is 12-hourly) [S] — [Demystifying Data-Driven Probabilistic Medium-Range Weather Forecasting, arXiv 2601.18111](https://arxiv.org/pdf/2601.18111); [FourCastNet 3 paper](https://arxiv.org/pdf/2507.12144). The commonly cited "beats ENS on 97.2% of targets" figure was NOT confirmed by search this session.
- Weather Lab (launched 12 June 2025): public preview website for DeepMind AI weather models plus an experimental stochastic cyclone model producing 50 scenarios up to 15 days; Google's internal tests: 5-day track ~140 km closer than ECMWF ENS; partnership with US NHC [S] — [DeepMind blog](https://deepmind.google/discover/blog/weather-lab-cyclone-predictions-with-ai/); [HPCwire](https://www.hpcwire.com/2025/06/18/google-deepmind-launches-interactive-ai-that-lets-you-explore-storm-forecasts/).
- WeatherNext 2 (announced 17 Nov 2025): built on a Functional Generative Network (FGN) that injects noise into the architecture; 8x faster generation, up to 1-hour temporal resolution; beats previous WeatherNext on 99.9% of variables and lead times (0–15 days); data in Earth Engine and BigQuery, early access on Vertex AI; embedded in Google Search, Gemini, Pixel Weather, Maps Weather API [S] — [Google blog](https://blog.google/technology/google-deepmind/weathernext-2/).
- WeatherNext 3 (arXiv 2609.03582, ~3–4 Sept 2026): 0.1° internal representation (~5 km marketing, hourly refresh), trained with raw observations; a **station head** predicts 2 m temperature and RH at arbitrary lat/lon/time using interpolated latent + elevation, land/sea, time offset; trained on METAR, regional Mesonets, ICOADS ships/buoys; evaluated on **held-out METAR stations with CRPS**: up to 30% CRPS improvement for short-lead 2 m T vs WN2 and 40% vs ECMWF ENS ("up to" = best lead, not average); station head overfits training stations by a few percent [S] — [arXiv 2609.03582](https://arxiv.org/html/2609.03582v1); [MarkTechPost 2026-09-03](https://www.marktechpost.com/2026/09/03/google-deepminds-weathernext-3-trains-on-weather-station-observations-to-deliver-5-km-global-forecasts-refreshed-every-hour/); [note.com analysis](https://note.com/ai_driven/n/nf896b8d9f804?hl=en).
- A snippet (source paper uncertain, appeared in the WN3 result cluster) reported station-level ensemble CRPS improving 24–28% for 2 m T at every lead time but **station ensembles under-dispersive at all leads** (worse calibration than on the grid) [S, attribution unverified] — [arXiv 2609.03582](https://arxiv.org/html/2609.03582v1).

**ECMWF**
- AIFS (deterministic, "AIFS Single") paper arXiv 2406.01465 (2024); an update paper arXiv 2509.18994 (Sept 2025) [S] — [AIFS paper](https://arxiv.org/pdf/2406.01465); [AIFS update](https://arxiv.org/html/2509.18994v1). ECMWF reports AIFS surface forecasts (e.g., 2 m T) consistently better than IFS against analyses and observations [S] — [AIFS update](https://arxiv.org/html/2509.18994v1).
- AIFS-ENS: operational from the 06 UTC run on 1 July 2025 (release candidate from 23 June); trained with a CRPS loss (predecessor experimental version was diffusion-based); 50 perturbed members + control, initialized from IFS-ENS perturbed ICs; open-data delay removed; files at data.ecmwf.int/forecasts/YYYYMMDD/HHz/aifs-ens (0p25); ECMWF says it outperforms the physics ENS in the medium range (no numbers in snippet). Another Confluence page dates "v1" to 27 Aug 2025 — conflicting/unclear [S] — [ECMWF Confluence: Implementation of AIFS ENS v1](https://confluence.ecmwf.int/spaces/FCST/pages/540554034/Implementation+of+AIFS+ENS+v1); [ECMWF open data directory](https://data.ecmwf.int/forecasts/20250901/12z/aifs-ens).

**NOAA**
- 17 Dec 2025 NOAA made operational AIGFS (16-day forecast at ~0.3% of GFS compute, ~40 min), AIGEFS (31-member AI ensemble, skill comparable to GEFS at 9% of compute) and HGEFS (62-member hybrid GEFS+AIGEFS, outperforms both on most metrics). Built from GraphCast, fine-tuned on NOAA GDAS analyses (Project EAGLE). v1.0 degrades TC intensity [S] — [NOAA EPIC](https://epic.noaa.gov/noaa-deploys-new-ai-driven-global-weather-models/); [HPCwire](https://www.hpcwire.com/aiwire/2025/12/17/noaa-deploys-new-generation-of-ai-driven-global-weather-models/); [ForecastWatch](https://forecastwatch.com/2026/01/06/noaa-launches-new-suite-of-weather-models/).
- NOAA/CIRA runs experimental real-time GraphCast, Pangu-Weather, FourCastNet v2 and Aurora from both GFS and IFS initial conditions (used as CastCheck inputs) [F] — [CastCheck README](https://github.com/ZzZTripleZzZ/castcheck). Archived GraphCast-GFS forecasts are resold via APIs (GribStream) [S] — [GribStream GraphCast](https://gribstream.com/models/graphcast).

**Microsoft**
- Aurora: "A foundation model for the Earth system", Nature 641, 1180–1187, published 21 May 2025 (preprint May 2024); 1.3B parameters; pretrained on ERA5, CMIP6, GFS analyses, CAMS; fine-tuned for tasks; Aurora 1.5 adds 22 variables, hourly resolution and probabilistic ensemble forecasting [S] — [Nature](https://www.nature.com/articles/s41586-025-09005-y); [Microsoft Research blog Aurora 1.5](https://www.microsoft.com/en-us/research/blog/aurora-1-5-extending-open-foundation-models-for-weather-and-earth-system-applications/); [GitHub](https://github.com/microsoft/aurora).

**NVIDIA**
- FourCastNet 3 (arXiv 2507.12144, July 2025): probabilistic, 6-hourly, outperforms IFS-ENS at ~60x lower cost, competitive with GenCast [S] — [arXiv 2507.12144](https://arxiv.org/pdf/2507.12144); [NVIDIA PDF](https://d1qx31qr3h6wln.cloudfront.net/publications/FourCastNet3_0.pdf).

**Others**
- FuXi-ENS (Fudan, May 2024 arXiv); NeuralGCM (hybrid differentiable dynamical core + NN; arXiv 2023) [S] — [Awesome-LWMs](https://github.com/jaychempan/Awesome-LWMs).
- WeatherBench 2 published in JAMES, 2024 [S] — [ResearchGate](https://www.researchgate.net/publication/381490654_WeatherBench_2_A_Benchmark_for_the_Next_Generation_of_Data-Driven_Global_Weather_Models).
- Newer probabilistic entrants: U-Cast (arXiv 2604.09041), AdaWeather adaptive mixing of probabilistic forecasts (arXiv 2606.02663) [S] — [U-Cast](https://arxiv.org/pdf/2604.09041); [AdaWeather](https://arxiv.org/pdf/2606.02663).

### Inferences
- [P, not verified this session] Pangu-Weather (Huawei; Nature July 2023; deterministic 0.25°); NeuralGCM (Nature, July 2024; stochastic version ~1.4°, deterministic up to 0.7°; ERA5); Stormer (Nguyen et al., 2023/2024, transformer, deterministic w/ randomized dynamics); MetNet-3 (Google, 2023, regional US nowcasting to 24 h, trained on station observations – one of the few models trained directly against point obs); ClimaX (Microsoft, 2023, foundation model, coarse 1.4–5.6°); Prithvi WxC (NASA/IBM, Sept 2024, 2.3B-parameter foundation model on MERRA-2). Open-Meteo serves AIFS and (per its docs) some AI models. These should be checked before citation.
- Most deterministic models (GraphCast, Pangu, AIFS Single, AIGFS) are only 6-hourly at 0.25°, so daily Tmax must be approximated from 4 synoptic times — structurally biased low versus the true max (CastCheck explicitly calls this a "sampling penalty").
- The probabilistic, publicly archived, real-time candidates for a Tmax-at-airport study are: AIFS-ENS (open data, 51 members), AIGEFS/HGEFS (NOAA), WeatherNext 2 (BigQuery; access terms and archive depth not verified), Aurora 1.5 ensemble (if run locally).

### Gaps
- Exact native resolutions/time-steps of WN2 and AIFS-ENS, and whether WN2 archived forecasts in BigQuery include hourly 2 m T or Tmax: not verified.
- Whether WeatherNext 3 station-head forecasts are publicly available: not found.
- GenCast "97.2%" headline not confirmed by search.

## Q2. How are AI weather models evaluated? (grid vs station; deterministic vs probabilistic)

### Takeaway
Headline evaluations remain grid-based vs ERA5/own analysis (WeatherBench 2: RMSE/ACC; CRPS/spread-skill for ensembles). Station-level verification exploded in 2025–2026 (China, Europe, Inner Mongolia, US airports, Google's held-out METAR), but it is mostly deterministic 2 m T at synoptic hours, nearest-grid-point, no post-processing, and mostly preprints or vendor papers.

### Cited Findings
- WeatherBench 2 (JAMES 2024) is the standard benchmark for data-driven global models [S] — [WB2](https://www.researchgate.net/publication/381490654_WeatherBench_2_A_Benchmark_for_the_Next_Generation_of_Data-Driven_Global_Weather_Models). Ensemble comparisons are reported as CRPS on WB2 at 1.5° [S] — [arXiv 2601.18111](https://arxiv.org/pdf/2601.18111).
- Aurora authors compared to raw WeatherReal-ISD station observations: Aurora beats IFS HRES for 10 m wind at all leads to 10 days; for 2 m T they warn the official IFS analysis includes an extra surface assimilation step, giving Aurora an "unfair advantage" in initial conditions [S] — [Aurora arXiv 2405.13063](https://arxiv.org/pdf/2405.13063).
- **CastCheck** (2026, independent, open data): daily station-level verification at 23 US first-order stations (22 major airports + NYC Central Park) of raw 2 m T from IFS HRES, GFS, AIFS Single and NOAA/CIRA GraphCast, Pangu, FourCastNet v2, Aurora (from GFS and IFS ICs). Headline metric = instantaneous t2 at 00/06/12/18 UTC; daily extremes reported as tmax_s/tmin_s (vs METAR-derived extremes) and **tmax_cli/tmin_cli vs NWS Daily Climate Report (CLI)** — the CLI comparison is secondary, "never used for ranking" due to a model-dependent sampling penalty. Bootstrap CIs, paired MAE differences, Holm-corrected significance. **Deterministic only; no MOS/bias correction/downscaling; no mention of markets.** Version v0.3.x, Aug 2026 [F] — [CastCheck GitHub](https://github.com/ZzZTripleZzZ/castcheck); [Zenodo DOI 10.5281/zenodo.22237426](https://zenodo.org/records/22237426).
- Jua (company) "Do AI weather models miss extremes? Evidence from ten months of verification against European weather stations" (arXiv 2608.09972, 2026): 11–12 systems; no uniform AI-specific tail deficit; AIFS loses 4.9±2.0% skill in heat tail vs GFS 22.8±2.0%; **all systems, NWP included, conditionally under-forecast extremes (bias toward centre of distribution)** [S] — [arXiv abs](https://arxiv.org/abs/2608.09972); [GitHub juaAI/aiweather-extremes](https://github.com/juaAI/aiweather-extremes); [Jua summary](https://jua.ai/extremes-benchmarks/).
- China: station-based extremes verification vs GFS with common initialization, 2022–2025 [S] — [ResearchGate](https://www.researchgate.net/publication/415274447_Do_AI_weather_models_forecast_extremes_better_than_GFS_A_station-based_verification_over_China_with_a_common_initialization_source_2022-2025); 210 stations, eastern coastal China, Pangu/FengWu/FuXi vs GFS for 2 m T, pressure, wind [S] — [ResearchGate](https://www.researchgate.net/publication/414134895_Station-Based_Evaluation_of_AI_Weather_Models_for_Near-Surface_Temperature_Pressure_and_Wind_Forecasts_over_Eastern_Coastal_China).
- Inner Mongolia (Atmosphere 17(11):1053, 2026): IFS-Control vs AIFS vs **WeatherNext 2 mean** for 6–84 h temperature and precipitation at stations; nearest-grid-point by design, no interpolation or lapse-rate correction (so terrain mismatch is in the error) [S] — [MDPI](https://www.mdpi.com/2073-4433/17/11/1053).
- Flash-flood / extreme precip AI vs WRF studies (GMD 2026; arXiv 2510.25045) use threshold-weighted spatial verification [S] — [GMD](https://gmd.copernicus.org/articles/19/9831/2026/); [arXiv 2510.25045](https://arxiv.org/pdf/2510.25045).
- Weighted potential CRPS proposed for fair AI-vs-physics extreme-event comparisons (arXiv 2606.21170) [S] — [arXiv 2606.21170](https://arxiv.org/pdf/2606.21170).
- Google WN3 station head: CRPS on held-out METAR stations (see Q1) [S] — [arXiv 2609.03582](https://arxiv.org/html/2609.03582v1).

**Post-processing of AI output**
- Statistical post-processing of AIFS etc. against 569 Australian stations (BoM; arXiv 2504.12672): bias-correct against fine MSAS analysis + lapse-rate adjustment to site altitude; yields accurate probabilistic forecasts from AI models [S] — [arXiv 2504.12672](https://arxiv.org/html/2504.12672).
- Station-wise ridge/XGBoost post-processing of FourCastNetv2-small, Pangu, GraphCast over 163 NE Asian stations during heat waves (dataset) [S] — [Zenodo 22828592](https://zenodo.org/records/22828592).
- ML post-processing ensemble of GraphCast/Pangu (IFS and GFS ICs) + NWP for short-term air temperature over Beijing (Met. Applications 2026): AI beats corresponding NWP; Pangu > GraphCast there [S] — [Wiley](https://rmets.onlinelibrary.wiley.com/doi/10.1002/met.70238?af=R).
- NBM is NOAA's flagship post-processed gridded product (MOS, quantile mapping, ensemble weighting; URMA as reference) [S] — [GribStream NBM](https://gribstream.com/models/nbm). No search hit found a head-to-head of post-processed AI model vs NBM at the same stations.

### Inferences
- Station verification is converging on: instantaneous 2 m T, deterministic MAE/RMSE, nearest grid point. Daily Tmax as defined by NWS CLI (local standard time calendar day, 1-min/5-min ASOS max) is at best a secondary metric (CastCheck) — none rank models on it probabilistically.
- Grid-to-station representativeness (elevation, coastline, urban heat) is a first-order error source; AI-native fixes (WN3 station head) and classical fixes (lapse rate, MOS) both exist but haven't been compared on the same target.

### Gaps
- Couldn't read full texts (arxiv blocked) for exact metrics/periods of Jua, WN3, BoM papers.
- No study found that scores AI ensembles' **probabilistic daily Tmax** (CRPS/Brier on bins) against **NWS CLI** values at airports.

## Q3. Known weaknesses/criticisms (smoothing, extremes, diurnal cycle, representativeness, decision relevance)

### Takeaway
Strongest peer-reviewed criticism: AI models underperform physics HRES on record-breaking extremes (Science Advances 2026). Counter-evidence (Jua, company preprint) says tail deficits are model-specific and all models, NWP included, regress toward the mean. Diurnal-cycle/Tmax-specific and decision-relevant critiques are largely absent from the literature found.

### Cited Findings
- Zhang, Fischer, Zscheischler, Engelke, "Physics-based models outperform AI weather forecasts of record-breaking extremes", Science Advances 2026 (doi 10.1126/sciadv.aec1433; preprint arXiv 2508.15724, Aug 2025): GraphCast, Pangu, FuXi vs ECMWF HRES on heat/cold/wind records in 2018 and 2020 vs 1979–2017 baseline; AI shows consistently larger errors for record events, underestimates frequency and intensity; "For high-risk applications, one should not rely solely on AI" [S] — [UNIGE press](https://www.unige.ch/medias/en/2026/lia-demunie-pour-predire-les-phenomenes-meteorologiques-extremes); [KIT press 040/2026](https://www.kit.edu/kit/english/pi_2026_040_physics-based-weather-models-more-reliable-than-ai-for-extreme-events.php); [arXiv 2508.15724](https://arxiv.org/html/2508.15724v1); [EurekAlert](https://www.eurekalert.org/news-releases/1126742).
- Contrasting: Jua station study finds no uniform AI tail deficit; shared conditional bias toward centre in all systems [S] — [arXiv 2608.09972](https://arxiv.org/abs/2608.09972).
- Initial-condition confound for 2 m T comparisons (IFS surface analysis advantage) [S] — [Aurora arXiv](https://arxiv.org/pdf/2405.13063).
- GraphCast reportedly comparable to HRES medium-range but larger errors at <24 h (blog-level evidence) [S] — [predictandprofit blog](https://predictandprofit.io/blog/noaas-graphcast-goes-operational-what-it-means-for-weather-t).
- Station ensembles under-dispersive (calibration worse at points than on grid) [S, attribution uncertain] — [arXiv 2609.03582](https://arxiv.org/html/2609.03582v1).
- NOAA AIGFS v1.0 degraded TC intensity [S] — [NOAA EPIC](https://epic.noaa.gov/noaa-deploys-new-ai-driven-global-weather-models/).
- CastCheck: raw scores "likely understate operational forecast quality"; CLI Tmax has model-dependent sampling penalty [F] — [CastCheck](https://github.com/ZzZTripleZzZ/castcheck).

### Inferences
- [P] Smoothing/blurring of deterministic MSE-trained models (GraphCast, Pangu) at longer leads is widely documented (e.g., WB2 spectra); ensembles trained with CRPS (AIFS-ENS, FGN/WN2, FCN3) address this. Not re-verified this session.
- 6-hourly output undersamples the diurnal max — a structural weakness for Tmax specifically, distinct from "smoothing".

### Gaps
- No dedicated study found on AI models' 2 m T diurnal-cycle amplitude or Tmax timing bias at stations.

## Q4. Decision-relevant evaluation: markets, NBM, human/crowd forecasts

### Takeaway
There is now (Sept–Oct 2026) evidence that Kalshi daily-high markets beat NBM and other public forecasts, but **no study found that puts AI weather models (AIFS-ENS, WN2/WN3, AIGEFS, GenCast) in the same comparison against market prices or settles on the exact CLI/settlement value probabilistically.** That is the clearest gap.

### Cited Findings
- Crosier, "Prediction Markets Beat the Weather Forecast on Tomorrow's High Temperature" (arXiv 2609.23969, q-fin.GN, 21 Sept 2026): 7,590 city-days of Kalshi markets in NYC, Chicago, Miami, Austin, Philadelphia, Denver, LA; market-implied forecast derived from bracket prices, compared hour-by-hour with six public forecasts; market beats the best single public forecast (NBM) in 6/7 cities; public forecasts lag information already in the market; edge narrows against combined forecasts [S] — [arXiv abs](https://arxiv.org/abs/2609.23969); [nextpredict](https://nextpredict.io/market-news/industry/study-kalshi-weather-markets-outperform-public-forecasts/); [FOW](https://www.fow.com/insights/kalshi-prediction-markets-beat-public-weather-forecasts-study-finds). Whether any of the "six public forecasts" is an AI model: unknown (not in snippets).
- Patrick Brown (Interactive Brokers), reported 29 Oct 2026, also finds prediction markets more accurate than forecasting systems for daily highs; hypothesizes larger advantage in winter [S] — [John Lothian News](https://johnlothiannews.com/prediction-markets-beat-weather-models-in-temperature-study-interactive-brokers-brown-says/); April 2026 Claims Journal piece on IBKR analysis [S] — [Claims Journal](https://www.claimsjournal.com/news/national/2026/04/15/336839.htm).
- Kalshi markets: binary contracts on official daily high/low, typically 2–5°F brackets [S] — [precipitation-ai page](https://precipitation-ai.pages.dev/predictions/temperature). A secondary source says Kalshi changed its temperature settlement source from NWS climate reports to The Weather Company (unverified, important for any study) [S] — [nextpredict](https://nextpredict.io/market-news/industry/study-kalshi-weather-markets-outperform-public-forecasts/).
- Blog backtests: NWS forecast + normal error does not beat day-before Kalshi price; station biases (e.g., Miami +3.7°F, LAX −4.0°F vs forecast); markets absorb new forecasts within 10–30 min; Gaussian error underestimates fat tails [S, anecdotal] — [dev.to](https://dev.to/myfirstcodeo/i-backtested-a-forecast-based-model-against-kalshis-temperature-markets-the-market-won-heres-442c); [oddsreference](https://oddsreference.com/predictions/research/kalshi-weather-model); [northlakelabs postmortem](https://www.northlakelabs.com/max/blog/kalshi-weather-postmortem-and-pivot/).
- Commercial "edge" tools use NWS/GFS/ECMWF via Open-Meteo, not AI ensembles explicitly; claims unverified [S] — [weatheredge](https://weatheredge.it.com/); [predictandprofit on GraphCast for bots](https://predictandprofit.io/blog/noaas-graphcast-goes-operational-what-it-means-for-weather-t).
- A station-by-station weather-markets site exists (content not read) [S] — [weatherclimatehumansystems](https://weather.weatherclimatehumansystems.org/index.html).

### Inferences
- Gap matrix (what exists vs not):
  - Station-level AI verification: yes (many, 2025–26).
  - Probabilistic at stations: yes but limited (WN3 held-out METAR CRPS for instantaneous 2 m T; BoM post-processing; under-dispersion noted).
  - Daily Tmax specifically at settlement definition (NWS CLI, LST day): only deterministic/secondary (CastCheck).
  - Against NBM / markets: market-vs-NBM exists (Crosier, Brown) but without AI models; AI-vs-NBM at stations not found.
  - Post-processed AI ensemble (e.g., AIFS-ENS/AIGEFS + EMOS/quantile regression) vs NBM vs Kalshi prices on bracket-level log score/Brier, with value/profit metrics: **not found — clear novelty opportunity.**
- Required methodological elements a novel study could add: (1) settlement-exact target (CLI Tmax, LST calendar day, rounding to °F integers, settlement-source change); (2) hourly or sub-daily max reconstruction from 6-hourly AI output; (3) station representativeness correction; (4) bracket-level probabilistic scores (RPS/log score) and calibration; (5) economic evaluation vs market prices with timing (information-release lag).

### Gaps
- Could not read Crosier's full paper: unknown which six forecasts, whether any AI model included, and how settlement-source change was handled.
- No peer-reviewed study of AI models vs prediction markets or human crowds (e.g., Metaculus/Good Judgment) for weather found.
- Brown (IBKR) study's paper/URL not located.
