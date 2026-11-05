# Calibrated probabilistic Tmax forecasts at stations (1–2 days ahead) for temperature-bucket pricing

Method note (2026-11-05): WebFetch could not reach arxiv.org, essd.copernicus.org or weather.gov from this session (DNS blocked), so no full texts were read. Findings come from search-result snippets of primary sources. Items marked **[BK]** are background knowledge from well-known papers that I could not verify in this session. They are cited by DOI so the writer can check them, and they should be treated as lower confidence.

## 1. Classical statistical post-processing (EMOS/NGR, BMA, training windows, CRPS)

### Takeaway
EMOS/NGR is the standard baseline: a Gaussian with mean a+b·ensmean and variance c+d·ensvar, fitted by minimising CRPS over a rolling window of about 30–60 days. It reliably removes bias and underdispersion. Longer training sets, extra predictors and seasonally aware fitting improve on it further. Local (per-station) fitting usually beats regional or global fitting for temperature, provided enough data is available.

### Cited Findings
- EMOS coefficients (a0, a1, b0, b1) are estimated by minimising CRPS on the training set — [Search snippets, e.g. arXiv 2402.00555](https://arxiv.org/pdf/2402.00555)
- Training windows: a review says 20–40 days are most common. The original sliding-window approach used the most recent 30–60 days. Papers attribute 30 or 40 days to Gneiting et al. (2005). A 2 m temperature study found 45 days a good choice — [arXiv 2008.07857 (seamless multi-model T2m, complex topography)](https://arxiv.org/pdf/2008.07857); [arXiv 1811.05821](https://arxiv.org/pdf/1811.05821)
- The optimal window grows with lead time: 40 days for 24 h, 60 days for 48 h, 100 days for 120 h and 200 days for 240 h (vine-copula temperature study) — [arXiv 1811.02255](https://arxiv.org/pdf/1811.02255)
- Trade-off: short windows adapt to seasonal changes, while long windows reduce estimation variance — [arXiv 1811.02255 / related](https://arxiv.org/pdf/1811.02255)
- Raw ECMWF ensemble mean CRPS for German station T2m in 2015 was about 1.16 °C, against about 0.85 °C for local EMOS with boosting (Lerch slides summarising Rasp & Lerch 2018) — [Lerch 2020 talk slides](https://statmath.wu.ac.at/research/talks/resources/2020_03_Lerch.pdf)
- Time-series-based EMOS (AR-EMOS, SAR-SEMOS; Jobst et al., QJRMS 2024) handles autocorrelation and seasonality. The share of stations with significant CRPS improvement over the raw ensemble was 40% for EMOS, 63% for AR-EMOS and 90% for SAR-SEMOS — [Jobst et al. 2024 QJRMS](https://rmets.onlinelibrary.wiley.com/doi/10.1002/qj.4844); [arXiv 2402.00555](https://arxiv.org/pdf/2402.00555)
- R implementation of EMOS (ensembleMOS package) — [CRAN ensembleMOS](https://search.r-project.org/CRAN/refmans/ensembleMOS/html/ensembleMOS.html)
- [BK] Gneiting, Raftery, Westveld & Goldman (2005), MWR 133, 1098–1118, doi:10.1175/MWR2904.1, introduced EMOS/NGR with minimum-CRPS estimation. Raftery et al. (2005), MWR 133, 1155–1174, doi:10.1175/MWR2906.1, introduced BMA. BMA and EMOS give similar skill for temperature.
- [BK] Hemri et al. (2014, GRL, doi:10.1002/2014GL062472) showed that post-processing gains for T2m persist even as NWP improves.
- Review: Vannitsem et al. (2021), BAMS 102(3) E681–E699, doi:10.1175/BAMS-D-19-0308.1. It covers methods from bias correction to multivariate methods. Challenges it names include km-scale data volumes, model changes disrupting training parameters, and merging ensembles that behave differently — [arXiv 2004.06582](https://arxiv.org/pdf/2004.06582); [KNMI page](https://www.knmi.nl/research/publications/statistical-postprocessing-for-weather-forecasts-review-challenges-and-avenues-in-a-big-data-world)

### Inferences
- The raw-to-EMOS improvement implied by the Lerch slides is about 27% CRPS (1.16 to 0.85 °C) for station T2m at roughly 2-day lead. For a trader, the largest single gain comes from removing station-specific bias and correcting the spread.
- Minimum data for per-station EMOS: about 30–60 days of forecast–observation pairs is workable for day 1–2. One to three years, or reforecasts with seasonal terms, is better. A trader can fit per-airport EMOS on archived NBM/GFS/ECMWF open data plus METAR/CLI observations.
- Use a Gaussian (or skewed or logistic) predictive distribution, then integrate it over the bucket edges after the discretisation step described in Section 5.

### Gaps
- Could not retrieve the exact CRPS gain tables from Gneiting 2005 or Raftery 2005.

## 2. ML and distributional approaches (DRN, NGBoost, QRF, boosting, transformers; EUPPBench)

### Takeaway
Neural distributional regression is about 25–30% better than the raw ensemble and modestly better than EMOS, mostly because it can use extra predictors and station embeddings. DRN means a network that outputs μ and σ and is trained on CRPS, with station embeddings and auxiliary NWP predictors (Rasp & Lerch 2018). Quantile methods include BQN, QRF and boosting. On public benchmarks the gains over good EMOS are real but modest, on the order of a few to about 15% CRPS.

### Cited Findings
- Rasp & Lerch (2018), MWR 146, 3885–3900, used ECMWF ensemble T2m at German surface stations. The network was trained by CRPS minimisation, and its gains came from auxiliary predictors and station embeddings. It outperformed global and local EMOS and could reveal which predictors matter — [arXiv 1805.09091 (via search)](https://arxiv.org/abs/1805.09091v1); [AMS 2019 abstract](https://ams.confex.com/ams/2019Annual/webprogram/Paper353005.html)
- A secondary summary reports that the best variant (NN-aux-emb, trained on 2015) reduced CRPS by about 29% against the raw ensemble. This needs checking against the paper — [emergentmind summary](https://www.emergentmind.com/papers/1805.09091)
- Schulz & Lerch (2022), MWR 150, 235–257, compared eight methods for wind gusts: EMOS, member-by-member, IDR, gradient-boosting EMOS, QRF, DRN, BQN and HEN. Simple methods already calibrate the ensemble, extra predictors add skill, and neural networks handle extremes better. DRN and BQN became the standard benchmarks — [EGU22 abstract](https://meetingorganizer.copernicus.org/EGU22/EGU22-869.html); [arXiv 2309.04452](https://arxiv.org/pdf/2309.04452)
- Permutation-invariant neural networks (transformer/set-based) process ensemble members directly and are benchmarked against DRN, BQN and EMOS on EUPPBench T2m — [Höhlein et al., arXiv 2309.04452](https://arxiv.org/html/2309.04452)
- EUPPBench (Demaeyer et al. 2023, ESSD 15, 2635–2653) uses ECMWF ENS forecasts and reforecasts, with station observations over a domain of 45.75–53.5°N, 2.5–10.5°E. The first benchmark is T2m with only T2m and metadata as predictors. All methods reduce bias and improve calibration and accuracy. AR-EMOS has the smallest bias, and many methods keep a negative bias at altitude. CRPSS there is computed against ECMWF direct model output — [ESSD article](https://essd.copernicus.org/articles/15/2635/2023/); [EMS2023 presentation](https://presentations.copernicus.org/EMS2023/EMS2023-229_presentation.pdf); [ResearchGate PDF](https://www.researchgate.net/publication/367075920_The_EUPPBench_postprocessing_benchmark_dataset_v10); [code/data on GitHub](https://github.com/EUPP-benchmark/climetlab-eumetnet-postprocessing-benchmark)
- A deep-learning model producing probabilistic in-situ T2m from deterministic forecasts, run on EUPPBench, reached a CRPSS of about 15% against a naive probabilistic baseline. It significantly outperformed EMOS at all but the longest lead times — [arXiv 2406.02141](https://arxiv.org/html/2406.02141)
- Multi-model ML post-processing ensembles of GraphCast, Pangu, IFS and GFS have been tested for Beijing station temperature at 6–72 h (Meteorol. Appl. 2026) — [He et al. 2026](https://rmets.onlinelibrary.wiley.com/doi/10.1002/met.70238?af=R)
- [BK] Taillardat et al. (2016, MWR, doi:10.1175/MWR-D-15-0260.1) applied QRF to T2m and wind. QRF is competitive with EMOS and robust, but cannot extrapolate beyond the range of its training data. NGBoost (Duan et al. 2020, arXiv 1910.03225) gives LightGBM-style boosting with distributional outputs and is a convenient tabular choice.

### Inferences
- For a small number of stations (a few airports) and limited history, gradient-boosted or EMOS-with-covariates models are the pragmatic choice. Examples are EMOS-GB, NGBoost, or LightGBM quantile regression. DRN with station embeddings pays off when many stations are pooled.
- The ranking is stable: raw < EMOS < EMOS with covariates or boosting ≈ QRF < DRN/BQN. The gap from EMOS to the best ML is smaller (a few % to about 15%) than the gap from raw to EMOS (about 20–30%).

### Gaps
- Exact EUPPBench T2m CRPSS by method and lead time could not be retrieved; it is in Section 5 of the ESSD paper.
- No direct source was found on NGBoost specifically for station Tmax.

## 3. Operational products (NBM, LAMP, MOS, ECMWF ENS) and data access

### Takeaway
NBM provides calibrated station and grid Tmax percentiles (PMaxT/PMinT via quantile mapping). These have been bias-corrected to METAR observations since v4.1 (January 2023), and NBM v5.0 went live on 2026-04-21. NBM's text bulletins (NBS, NBE, NBP) are archived on AWS. This makes NBM the cheapest strong prior for US airport Tmax buckets. Its percentiles are not perfectly calibrated, and local recalibration helps.

### Cited Findings
- From v4.1 (12 UTC cycle, about 2023-01-17), NBM daily max/min temperature bias correction switched from URMA to METAR observations, so all input models are calibrated to METARs — [SCN22-131 NBM v4.1](https://www.weather.gov/media/notification/pdf2/scn22-131_nbm_v4.1.pdf)
- NAVGEM was removed from some PMaxT/PMinT quantile-mapping inputs because it caused overdispersion after quantile mapping — [SCN22-33](https://www.weather.gov/media/notification/pdf2/scn22-33_nbm_prob_maxt_mint_update.pdf)
- NBM v5.0 became effective 2026-04-21. Deterministic daily max/min now equal the mean of the quantile-mapping distribution — [SCN26-24 NBM v5.0](https://www.weather.gov/media/notification/pdf_2026/scn26-24NBM_V5(1).0_aaa.pdf); [NBM user webinar 2026-04-15](https://www.weather.gov/media/wrn/calendar/NBMUserWebinar4-15-26.pdf)
- NBM calibrates each input model against recent verification — [NBM webinar 2026](https://www.weather.gov/media/wrn/calendar/NBMUserWebinar4-15-26.pdf); [NBM documentation](https://blend.mdl.nws.noaa.gov/nbm-documentation)
- Calibration evidence (an AMS 2024 abstract, NWS Boise): in one example the NBM 90th-percentile Tmax was exceeded about 16% of the time, not 10%. Analog methods were used to recalibrate — [AMS 2024 Paper 429602](https://ams.confex.com/ams/104ANNUAL/webprogram/Paper429602.html)
- Archive: the text bulletins sit at `https://noaa-nbm-grib2-pds.s3.amazonaws.com/blend.YYYYMMDD/HH/text/` as files blend_nbhtx (hourly), nbstx (NBS short-range), nbetx (NBE extended), nbxtx (super-extended) and nbptx (NBP probabilistic). Operational files are kept only 1–2 days. Sources disagree on the archive start: about 2020-05-18 for text, or "since 2021" — [MDL NBM text archives](https://vlab.noaa.gov/web/mdl/nbm-text-archives); [NBM data download](https://vlab.noaa.gov/web/mdl/nbm-download); [Model Data v5.0](https://vlab.noaa.gov/documents/6609493/50324458/Model_Data_v5_0.pdf); [NBM text products](https://blend.mdl.nws.noaa.gov/nbm-text)
- The archive spans several NBM versions, so the statistics are non-stationary — [MDL NBM download](https://vlab.noaa.gov/web/mdl/nbm-download)
- GFS MOS (MAV) skill: a case study at Tulsa found day-1 max-temperature MAE of just over 4 °F the day after cold-front passages, against just over 3 °F for MET (NAM MOS). This is a hard-case subset — [NWS TA (Tulsa)](https://www.weather.gov/media/wrh/online_publications/talite/talite0817.pdf). MDL verification plots day-1 and day-2 MaxT MAE for about 80 CONUS stations (NDFD vs GFS MOS vs ECMWF MOS), with numbers in figures only — [Huntemann AMS 2015 poster](https://ams.confex.com/ams/95Annual/webprogram/Handout/Paper258606/Huntemann_449_NDFD-GFSMOS-ECMWFMOS_Verification.pdf). ECMWF MOS MaxT was nearly as accurate as NDFD — [Huntemann 2015 paper](https://www.weather.gov/media/mdl/AMSGlahnSymp2015_Huntemann_paper.pdf)
- A Mount Washington evaluation found MOS temperature MAE differences between GFS, NAM and NBM small (<1 °F) — [Mount Washington MOS presentation 2024](https://mountwashington.org/wp-content/uploads/2024/08/Final-Presentation-MOS.pdf). A CBRFC project compared GFS MOS, NBM, bias-corrected NBM and climatology for days 1–10 — [CBRFC NBM Temperature](https://www.cbrfc.noaa.gov/present/projects/NBM_Temperature.pdf)
- ECMWF ENS and AIFS ENS are available as open data, and AIFS ENS is on dynamical.org — [ECMWF open data](https://www.ecmwf.int/en/forecasts/datasets/open-data); [dynamical.org AIFS ENS](https://dynamical.org/catalog/ecmwf-aifs-ens-forecast/)
- [BK] LAMP (Localized Aviation MOS Program) runs hourly, updates GFS MOS with the latest observations, and is most useful for the first few hours. MEX is the extended-range GFS MOS.

### Inferences
- Trader workflow: pull NBP or NBS percentiles (or the GRIB2 PMaxT quantiles) for the settlement station. Fit a smooth distribution or interpolate the quantiles. Recalibrate locally with isotonic or EMOS-style regression against CLI observations over the post-January-2023 period. Then integrate over the integer-°F bucket edges.
- NBM tails look somewhat underdispersed (the 90th percentile exceeded about 16% of the time in one example), so widen the tails or recalibrate before pricing out-of-the-money buckets.

### Gaps
- No published numeric day-1 Tmax MAE was found for NBM, GFS MOS or ECMWF MOS in 2023–2026; MDL verification pages were unreachable.
- No LAMP Tmax skill numbers were retrieved.

## 4. Multi-model combination and AI weather models at stations

### Takeaway
Multi-model blending (the NBM approach, or ML stacking of IFS, GFS, AIFS and GraphCast) is consistently helpful. ECMWF reports that AIFS ENS has better station-verified T2m CRPS than IFS ENS. Raw AI models still carry large station biases, so they need the same post-processing. No consistent ranking of GraphCast, Pangu and AIFS at station level was found.

### Cited Findings
- AIFS-CRPS (the basis of AIFS ENS) is considerably more skilful than the IFS ensemble for many variables including T2m, verified against SYNOP observations. Its spread is reduced for most surface variables except T2m in the northern extratropics — [AIFS-CRPS, npj AI 2026](https://www.nature.com/articles/s44387-026-00073-7)
- AIFS ENS became operational at ECMWF in 2025 — [ECMWF Newsletter 185](https://www.ecmwf.int/en/newsletter/185/earth-system-science/aifs-ens-becomes-operational). For August 2025–February 2026 it had fewer large T2m errors, especially in wintertime stable situations — [ECMWF forecast performance 2025](https://www.ecmwf.int/en/newsletter/187/news/forecast-performance-2025). Open weights are published — [HF aifs-ens-1.0](https://huggingface.co/ecmwf/aifs-ens-1.0); [HF aifs-ens-2.0](https://huggingface.co/ecmwf/aifs-ens-2.0)
- Pangu scored better than both HRES and ENS at Norwegian stations, with and without probabilistic post-processing — [Bremnes et al., arXiv 2309.01247](https://arxiv.org/pdf/2309.01247)
- Beijing study (Meteorol. Appl. 2026): MAE for GraphCast-IFS was about 1.88 °C over 6–72 h. Pangu-IFS reportedly beat GraphCast-IFS, and an ML ensemble of AI and NWP models improved further. This comes from fragmentary snippets — [He et al. 2026](https://rmets.onlinelibrary.wiley.com/doi/10.1002/met.70238?af=R)
- Moroccan stations (non-peer-reviewed GitHub project): ML calibration cut RMSE from about 5.30 to 2.93 °C (AIFS), 4.37 to 3.40 °C (GraphCast) and 2.11 to 1.80 °C (Pangu). Raw station biases of AI models can be large — [GitHub ai-weather-model-calibration](https://github.com/HamzaIDM/ai-weather-model-calibration)
- CastCheck provides independent daily raw (no MOS) T2m verification of IFS, AIFS, GFS, GraphCast, Pangu, FourCastNet and Aurora at 23 US stations against NWS CLI reports — [CastCheck Zenodo](https://zenodo.org/records/22237426); [GitHub castcheck](https://github.com/ZzZTripleZzZ/castcheck)
- AI models show distinct T2m error behaviour in heat waves — [arXiv 2504.21195](https://arxiv.org/pdf/2504.21195)
- A seamless multi-model post-processing study for T2m in complex terrain (MeteoSwiss) combines several NWP systems — [arXiv 2008.07857](https://arxiv.org/pdf/2008.07857)
- Merging forecasts with different behaviour is a named open challenge — [Vannitsem et al. 2021](https://arxiv.org/pdf/2004.06582)

### Inferences
- A practical stack: NBM percentiles, ECMWF ENS or AIFS ENS (open data), GFS/GEFS and HRRR as features in an EMOS-with-covariates or boosting model per station. AI models are cheap extra features, but they underdisperse and need calibration.

### Gaps
- No peer-reviewed station-level Tmax (daily max rather than instantaneous T2m) comparison of AI models after post-processing in the US was found.

## 5. Practical specifics: hourly vs true max, representativeness, discretisation, °C/°F, intraday nowcasting

### Takeaway
The settlement value, usually the NWS CLI daily max in integer °F, is not the maximum of the hourly METAR temperatures. ASOS tracks the extreme internally from continuous sensor data, and it often falls between the routine observations. Models must therefore predict the CLI value directly, or add a positive "hourly-to-true-max" offset. Rounding chains between °F and °C can shift values by ±1 °F.

### Cited Findings
- ASOS samples about every 10 s, forms 1-min averages and a running 5-min average each minute. Daily highs and lows come from 24×60 running 5-min averages (USCRN uses discrete 5-min averages) — [NOAA ASOS vs USCRN, Sun et al.](https://www.ncei.noaa.gov/pub/data/uscrn/documentation/research/Sun.pdf); [ASOS notes](https://sites.google.com/site/cvhangar/home/wx/asos)
- The high or low can occur between the 5-minute observations; ASOS tracks it internally but does not report it publicly, and real-time 1-minute data is not public — [ASOS notes](https://sites.google.com/site/cvhangar/home/wx/asos)
- Longer averaging intervals produce a larger cooling (low) bias in Tmax, with 1-min better than 5-min averaging — [Lin, Hubbard & Baker, AMS 2005](https://ams.confex.com/ams/Annual2005/techprogram/paper_84069.htm)
- Observation-time effects: the annual mean Tmax differs by more than 1 °C between 15:00 and 09:00 reading times (Iowa) — [Rischard et al., arXiv 1805.10214](https://arxiv.org/pdf/1805.10214)
- ASOS measures in °F. METAR carries whole-°C temperature plus a tenths-of-°C T-group in remarks, and the round-trip conversion can differ by 1 °F from the CLI. The CLI/CF6 or the 6-hour max/min groups (1snTTT/2snTTT, in tenths °C) are better sources for daily extremes — [NWS Chicago observations FAQ](https://www.weather.gov/lot/weather_observations_faq); [IEM News #1469](https://mesonet.agron.iastate.edu/onsite/news.phtml?id=1469); [NWS METAR decode key](https://weather.gov/media/zse/metar_decode_key.pdf)
- The NWS says CLI and 5-minute data differences come from recording and reporting quirks rather than CLI errors — [NWS Chicago FAQ](https://www.weather.gov/lot/weather_observations_faq)

### Inferences
- Discretisation: if the predictive CDF F is for the continuous true max in °F, then P(bucket = k) = F(k+0.5) − F(k−0.5). Check the rounding convention in the CLI, and fit post-processing directly on integer CLI values so the rounding behaviour is absorbed.
- Converting whole-°C METAR values gives a ±0.9 °F ambiguity, so never build the training target from rounded whole-°C METARs. Use CLI, the 6-hour max group, or high-resolution 1-min or 5-min data (the IEM archive has ASOS 1-minute data with a lag).
- Intraday nowcasting: on settlement day, condition on the running max so far. The final max is at least the observed max, so truncate the distribution below the running max. Update with the latest hourly obs, LAMP or HRRR and RTMA/URMA. Late in the afternoon, the distribution collapses toward the observed value plus a small positive increment.
- Station representativeness: the station-specific bias (sea breeze, terrain, sensor siting) is exactly what local EMOS or embeddings learn. Gridded raw models at about 9–25 km often have Tmax biases of 1–3 °C at specific airports.

### Gaps
- No quantified ASOS "hourly-max vs CLI-max" offset distribution was found; it would have to be estimated empirically from IEM data.
- No literature was retrieved on intraday Tmax nowcasting methods specifically; this is a gap in the search, not evidence that none exist.

## 6. Typical achievable errors (MAE/CRPS of day-1 Tmax at airports)

### Takeaway
Good post-processed day-1 station Tmax forecasts typically reach an MAE of about 1.2–1.7 °C (about 2–3 °F) and a CRPS of about 0.8–1.2 °C. Errors are larger in transition seasons, after fronts, and at coastal or complex sites. "About 1 °C MAE" is optimistic as a general average. In integer-°F buckets, even an excellent forecast puts its modal bucket at only about 20–30% probability.

### Cited Findings
- Station T2m CRPS was about 1.16 °C for the raw ECMWF ensemble and about 0.85 °C for local EMOS with boosting (Germany, 2015, about 48 h lead; T2m, not Tmax) — [Lerch slides](https://statmath.wu.ac.at/research/talks/resources/2020_03_Lerch.pdf)
- GFS MOS day-1 MaxT MAE was just over 4 °F after cold fronts (a hard subset), and about 3 °F for NAM MOS in the same case — [NWS TA](https://www.weather.gov/media/wrh/online_publications/talite/talite0817.pdf)
- MOS temperature MAE differences between systems are under 1 °F — [Mount Washington 2024](https://mountwashington.org/wp-content/uploads/2024/08/Final-Presentation-MOS.pdf)
- GraphCast-IFS mean MAE was about 1.88 °C over 6–72 h at Beijing stations (all hours, not Tmax) — [He et al. 2026](https://rmets.onlinelibrary.wiley.com/doi/10.1002/met.70238?af=R)

### Inferences
- For a Gaussian forecast, MAE ≈ 0.8σ and CRPS ≈ 0.56σ when calibrated. A day-1 MAE of 2.5 °F therefore implies σ ≈ 3.1 °F. The probability mass in one 1 °F bucket at the mode is then about 1/(σ√(2π)) ≈ 13%, and about 25% for a 2 °F bucket. Edge comes mostly from correct centring (bias) and correct spread, not from sharp single-bucket calls.
- Rough day-2 degradation: MAE grows about 10–20% from day 1 to day 2 (based on the general MOS literature; unverified here).

### Gaps
- No authoritative current (2023–2026) NBM or MOS day-1 Tmax MAE table was retrieved. MDL point verification would supply it, but weather.gov and vlab were not fetchable from this session.
