# Primary-source evidence: efficiency of temperature prediction markets and calibrated station Tmax forecasts

Method note (2026-11-05). Full texts read, either as arXiv HTML or as PDFs converted with pdftotext: Crosier 2609.23969; Qiu & Qiu 2610.13593; Cardozo & Rivero-Wildemauwe 2609.12878 (read the weather passages); Le 2602.19520 (read the weather passages); Rasp & Lerch 1805.09091; Schulz & Lerch 2106.09512; Höhlein et al. 2309.04452; Mlakar et al. 2303.17610; 2406.02141; 2412.13957; NWS SCN for NBM v5.0 and v4.1; NBM user webinar of 2026-04-15; MDL AMS 2017 NBM verification poster.

Not reachable from this session (proxy returned 403):
- essd.copernicus.org, so the EUPPBench paper itself is unread
- export.arxiv.org (DNS failure). I used the arxiv.org/search HTML search instead.
- ucd.ie and karlwhelan.com (Bürgi, Deng & Whelan)
- vlab.noaa.gov and blend.mdl.nws.noaa.gov
- nwas.org (Craven et al. 2020 JOM)
- wpc.ncep.noaa.gov

Corrections to the earlier notes in `Торговля погодными рынками Polymarket/`:
1. Crosier measures **RMSE of the market-implied mean**. The paper has no Brier or log-loss numbers and no trading-profit analysis.
2. In Miami the market does **not** beat the NBM. Earlier notes said only that its advantage was "smallest".
3. arXiv 2406.02141 is **not** an EUPPBench study. It post-processes the deterministic GDPS model against 1,066 North American METAR stations.
4. Schulz & Lerch 2022 studies **wind gusts**, not temperature, so its CRPS values are in m/s.
5. The operational NBM before v5.0 was **v4.3**, not v4.2.
6. The Lerch-slides figure of "0.85 °C" is EMOS-loc-bst. The best model in Rasp & Lerch scores 0.82 (2015 training) or 0.78 (2007–2015 training).

---

## Q1. Crosier (arXiv 2609.23969): Kalshi daily-high markets vs public forecasts

### Takeaway
The Kalshi-implied mean high temperature has roughly 10–11% lower RMSE than the best single public product (the NBM), from market open on d−1 through the NBM's final bulletin on the target morning. It beats an out-of-sample optimal combination of all public products by only 3–4%. Miami is the one city where the market does not beat the NBM. NBM revisions move toward the market about four times as much as the market moves toward the NBM. The paper measures information content only. It does **not** test whether trading against the market is profitable, and it reports no Brier or log-loss scores.

### Cited Findings
**Data**
- Seven cities, each settling on the NWS Daily Climate Report (CLI). Kalshi first listed markets in Aug 2021 for NYC and Chicago, May 2023 for Miami and Austin, Nov 2024 for Philadelphia and Denver, and Jan 2025 for LA.
- Sample start and days: NYC (Central Park) Jan 2022, 1,684 days; Chicago (Midway) Jan 2022, 1,684; Miami Intl May 2023, 1,189; Austin–Bergstrom May 2023, 1,186; Philadelphia Intl Nov 2024, 631; Denver Intl Nov 2024, 631; LAX Jan 2025, 585.
- Total 7,590 city-days. The last markets are from Aug 12, 2026. After that date Kalshi switched settlement to The Weather Company, and those contracts are excluded.
- Source: [Crosier 2026, §2.3, Table 1](https://arxiv.org/html/2609.23969v1)

**Method**
- Market forecast μ_M = Σ π_i c_i, using bid–ask midpoints with mass spread uniformly within each bracket.
- Open tails get geometrically decaying mass with τ = 0.55 over the next 15 integers, which puts 95% of tail mass within 5°F.
- Liquidity screens:
  - at least 3 quoted intervals
  - spread no more than 50¢
  - midpoints summing to 1 ± 30%
- The screens keep 86% of observations; most dropped markets are from 2022–24.
- The implied median gives the same results to within 0.05°F, and the gaps move by less than 2%.
- Source: [§2.1, App. A.1, B.2](https://arxiv.org/html/2609.23969v1)

**Benchmarks and tests**
- Public benchmarks: NBM, NDFD, LAMP, GFS MOS, HRRR and ECMWF.
- HRRR, ECMWF and LAMP have no daily-max field, so their high is the max of hourly values. These run cold: HRRR by up to about 2°F, ECMWF by 1–5°F, LAMP by 1–2°F. They are de-biased with each station's mean error over the previous 365 days.
- The NBM, NDFD and MOS daytime-max fields miss the calendar-day high on 4.6% of days. For those days the forecast is completed with LAMP's night hours and the observed running max.
- Accuracy is tested with Diebold–Mariano tests using Newey–West standard errors, on daily cross-city averages. Confidence bands use a 10-day block bootstrap.
- Source: [§2.4, App. A.2–A.3, B.1](https://arxiv.org/html/2609.23969v1)

**Headline RMSE (°F), Table 2: market vs public products, pooled over all cities**

| Product | Opening hour d−1 (11:00 ET) | Evening d−1 (19:00 local) | Final NBM bulletin (13:00 UTC, day d) |
|---|---|---|---|
| Market | 2.44 | 2.21 | 1.88 |
| NBM | 2.70 (gap +9.8%) | 2.45 (+10.0%) | 2.12 (+11.4%) |
| LAMP (de-biased) | 2.83 (+13.9%) | 2.63 (+16.3%) | 2.19 (+14.2%) |
| NDFD | 2.83 (+13.9%) | 2.66 (+17.0%) | 2.33 (+19.3%) |
| GFS MOS | 3.17 (+23.0%) | 2.95 (+25.2%) | 2.69 (+30.2%) |
| HRRR (de-biased) | 3.32 (+26.6%) | 3.07 (+28.1%) | 2.63 (+28.6%) |
| ECMWF (de-biased) | 3.31 (+26.4%) | 3.16 (+30.3%) | 2.68 (+30.6%) |
| Out-of-sample OLS combination | 2.45 (+3.1%) | 2.25 (+4.3%) | 1.90 (+3.0%, significant only at 10%) |

All other gaps are significant at 1%. — [Table 2, §3.2](https://arxiv.org/html/2609.23969v1)

**Combinations and LAMP**
- The combination is an OLS refit daily, city by city, on past days only. On the days it exists, the market's RMSE is 2.38, 2.16 and 1.84.
- An equal-weight average beats the fitted combination at the opening hour (2.43 vs 2.45). Against the equal-weight average, the market's margin is 2.1% rather than 3.1%.
- Dropping LAMP from the combination raises the market's lead to 3.3%, 4.7% and 6.4%. LAMP's live observations do the most to close the gap during the day.
- Source: [§3.2, App. B.2](https://arxiv.org/html/2609.23969v1)

**Robustness without the liquidity screens**
- The gap over the NBM is 8.0%, 9.0% and 8.0%.
- The gap over the combination is 1.9%, 3.2% and 0.7%; the last is not significant.
- Source: [App. B.2](https://arxiv.org/html/2609.23969v1)

**Cities and seasons**
- The market has lower error than the NBM in every city and at every anchor **except Miami**.
- Miami NBM RMSE on the d−1 morning is 1.6°F, against 2.6–3.5°F in the other six cities.
- At the opening hour, Miami traders stay within 2°F of the NBM on 98% of days. Chicago traders deviate by 2°F or more on 20% of days.
- In Nov–Jun, when the NBM d−1 error is 3°F or more, the market beats it by 10–16%. In Jul–Oct it wins by only 1–4%.
- Each extra 1°F of NBM error adds about 6 percentage points of market advantage (R² = 0.22).
- The largest edge is in Philadelphia, Chicago and NYC in winter, when cold-front timing matters.
- Source: [§1, §4](https://arxiv.org/html/2609.23969v1)

**Event study around NBM postings (eq. 7, Table 3)**
- A 1-σ disagreement (1.49°F) moves the next NBM by 0.063°F. A 1-σ NBM revision (0.43°F) moves the market by 0.016°F.
- Pooled estimates: β_ant = 0.042 (t = 15.9), γ_react = 0.037 (t = 11.9), β_gap = 0.153, n = 112,491.
- Chicago: after a 1°F NBM revision the market had moved 0.011°F in the previous 45 minutes and moves 0.007°F afterwards. That is about 2% of the revision, with no jump at publication.
- Source: [§5, Table 3](https://arxiv.org/html/2609.23969v1)

**Error decay over time**
- NBM RMSE falls from 2.7°F at open to 2.1°F on the target morning; the market's falls from 2.4°F to 1.9°F.
- The study window ends at 13:00 UTC on the target day, so it does not cover target-day afternoon nowcasting.
- Source: [§3.1, §2.2](https://arxiv.org/html/2609.23969v1)

**Concurrent work cited by Crosier**
- Brown (2026), "Improvement of daily temperature forecasts from a prediction market" (Trend Analytics working paper, 18 Sep 2026). It compares ForecastEx markets with 20 products at 24 locations over 7 months of 2026.
- Crosier summarises both studies as finding the market ahead of every single product, and ahead of a de-biased combination by a much smaller margin.
- Brown's paper itself was not read. — [Crosier, Related work](https://arxiv.org/html/2609.23969v1)

### Inferences
- Pricing off the NBM alone means facing a crowd whose mean is about 10% more accurate in RMSE. A de-biased, LAMP-inclusive, equal-weight public combination closes most of that gap, leaving about 2–4%.
- Any remaining forecast edge is likely small and concentrated in the high-variance regimes (winter, frontal timing) and in Miami-like regimes where the market adds nothing over the NBM.
- RMSE of the mean says nothing direct about bracket-level calibration. The Qiu & Qiu (Q2) and GitHub results in the earlier notes cover that.

### Gaps
- Per-city and per-season numbers appear only in Figure 4, which is an image, so I have no exact values.
- There are no probabilistic (Brier, log-loss, CRPS) or P&L results in Crosier.
- Brown (2026) is unread; I found no URL.

---

## Q2. Other 2024–2026 arXiv evidence on weather-market calibration and favourite-longshot bias (FLB)

### Takeaway
The one weather-specific Polymarket study (Qiu & Qiu, Oct 2026) finds mid and low prices near calibrated. Favourites (75–95¢) in the final 1–12 h before the daily peak are overpriced by about 10 percentage points. A naive "buy NO" on those favourites returned +50.7% after fees out-of-sample (184 trades, very wide CI, no spread or slippage). Fading longshots made nothing (−0.23%). Kalshi-wide (Le 2026) and Polymarket-wide (Cardozo & Rivero-Wildemauwe 2026) studies agree that short-horizon weather prices are *too extreme*, the opposite of political markets. The Polymarket weather longshot result flips sign depending on how contracts are aggregated.

### Cited Findings
**Qiu & Qiu, "Time-Varying Favorite–Longshot Bias in Polymarket Weather Markets", arXiv 2610.13593 (9 Oct 2026)** — [arXiv HTML](https://arxiv.org/html/2610.13593); code at [GitHub ShouchenQiu/PolyWeatherData](https://github.com/ShouchenQiu/PolyWeatherData)

*Data and setup*
- Dec 5, 2025 to Jul 31, 2026: 10 cities, 2,189 events, 21,697 bucket contracts and 8,544,732 taker trades, from the Polymarket API.
- Events per city: Atlanta 246, Chicago 201, London 249, Miami 201, NYC 246, Seattle 245, Seoul 248, Shanghai 151, Tokyo 154, Toronto 248.
- Events usually have 7–11 buckets. The split is chronological: train Dec–May (1,585 events), validation June (294), test July (310). (Table I, §III)
- The price at horizon h is the mean taker price in the h ± 0.5 h window before the daily temperature peak. (§IV-A)
- How the peak time is determined is not stated in the text I read.

*Range bias (training sample)*
- Range bias D_h = mean(y − p). Longshots are 0 < p ≤ 0.10; favourites are 0.75 ≤ p ≤ 0.95.
- Longshot overpricing is concentrated at 30–48 h, about −0.009 at 48 h. It turns into slight *under*pricing around 3–9 h.
- Favourite overpricing is strongest at 1–12 h, about −0.10 at 6 h. That is roughly an order of magnitude larger.
- The 70–90% bin reaches −11.2 percentage points at 6 h (Fig. 3).
- The pattern holds with cities weighted equally. (§IV-B)

*Event-level scores and recalibration (July test, Table II)*
- Brier, log loss and RPS all fall toward the peak, most sharply inside 12 h. (§IV-C)
- Cubic B-spline recalibration on logit(p), with knots at the 0.35 and 0.65 quantiles:
  - Brier 0.7045 → 0.7044
  - log loss 1.4450 → 1.4445
  - RPS 0.5705 → 0.5700
  - All 95% CIs include zero, so recalibration gives **no significant gain**.

*Buy-NO test (July test, Table III)*
- $10 notional per trade, fee F = C·0.05·r(1−r) on the NO price r.
- Favourites at 1–12 h: 184 trades, NO win rate 20.7%, pre-fee ROI +54.96%, post-fee +50.71% (+$5.07 per trade), 95% CI [1.76, 102.98] ¢ per $.
- Longshots at 30–48 h: 11,924 trades, NO win rate 97.8%, post-fee ROI −0.23%, CI [−0.47, 0.03].
- The authors say this uses mean taker prices and excludes depth, spread and slippage, so it does **not** establish executable profits. They also note it does not compare the market with public forecasts.

**Cardozo & Rivero-Wildemauwe, "The Favorite–Longshot Bias in Prediction Markets: Evidence from Polymarket", arXiv 2609.12878 (Sep 2026)** — [arXiv HTML](https://arxiv.org/html/2609.12878)
- 588M trades by 2.48M accounts. Purchases below 10¢ lose 19.3¢ per $; purchases at or above 90¢ earn 0.83¢ per $.
- How contracts are grouped matters. With equal weight per contract, longshots lose 6.3¢; grouped by parent event, they gain 4.1¢. (Abstract)
- Weather category: 8.3M purchases (1.4% of all), $155.5M paid (0.7%). 98.2% of the amount paid had a known payoff by Mar 29, 2026. Weather events have a median of 7 child markets, a mean of 7.75 and a max of 11.
- **Weather FLB depends on aggregation.** With equal weight per child market, longshots lose 25.15% and favourites earn +0.502%. With purchases pooled, longshots *earn* +24.74%. (§4.1)

**Le, "Decomposing Crowd Wisdom: Domain-Specific Calibration Dynamics in Prediction Markets", arXiv 2602.19520 v2 (Aug 2026)** — [arXiv HTML](https://arxiv.org/html/2602.19520)
- Data: 353M trades across 429k binary contracts, with Kalshi as the primary source. The analysis keeps trades priced 5–95¢. Kalshi Weather has 26,911 markets with a 24.0% base rate, which reflects threshold-exceedance contracts.
- Weather logistic calibration slopes are 0.69–0.97 within 48 h. A slope below 1 means prices are **too extreme (overconfident)**. Weather is the only domain like this; Politics is compressed, with slopes of 0.93–1.83.
- Isotonic recalibration: a raw price of 0.75 maps to 0.691 in Weather, against 0.886 in Politics.
- Weather's Bayesian domain intercept is −0.072 [−0.111, −0.034].
- The author's interpretation is over-reaction to meteorological signals. At moderate horizons weather markets are "among the best calibrated".
- Caveat: "Weather" here pools temperature, precipitation and natural events, and Polymarket weather is "negligible" in the dataset. (§4, §6, §9; Table 6)

**Other**
- Akey, Grégoire, Harvie & Martineau, "Who wins and who loses in prediction markets? Evidence from Polymarket", CEPR DP 21615 (Jun 2026), is cited by Qiu & Qiu as finding "especially large bias in weather markets". I have not read it. — [cited in 2610.13593 §II-B](https://arxiv.org/html/2610.13593)
- Bürgi, Deng & Whelan (2025): the PDF was unreachable (ucd.ie and karlwhelan.com returned 403), so there are no new numbers beyond the earlier snippet-based notes.
- An arXiv search for "kalshi" (sorted by date) also returned several Sept 2026 papers on Kalshi settlement and decidability: 2610.00165, 2610.00173, 2609.16642. I did not read them; from their titles they are not about weather pricing. — [arXiv search](https://arxiv.org/search/?query=kalshi&searchtype=all)

### Inferences
- Taken together: daily-temperature markets are well calibrated in the middle of the price range. They are *overconfident* on near-certain favourites close to the outcome; this holds on both Kalshi (Le) and Polymarket (Qiu & Qiu).
- This conflicts with the GitHub maker result in the earlier notes, where buying 97–99¢ made +0.9%. But Qiu & Qiu's favourite range stops at 95¢, so the two findings may not overlap. A strategy that sells YES or buys NO on 75–95¢ favourites in the last 12 h is the one academically flagged niche. It needs out-of-sample testing with real order-book costs; the n = 184 result is very noisy.
- Fading longshots does not work in weather on either venue (Qiu & Qiu −0.23%; the GitHub Kalshi backtest −2% to −8%).

### Gaps
- No academic study compares Polymarket weather probabilities with NBM or ECMWF probabilities at matched times. Qiu & Qiu list this as future work.
- How Qiu & Qiu define "time of daily peak" is not stated in the text I read; it may be in the code.
- I could not read the Bürgi, Deng & Whelan or Akey et al. full texts.

---

## Q3. Post-processing benchmarks: exact numbers

### Takeaway
For station T2m at about 24–48 h:
- the raw ECMWF ENS has CRPS of about 1.16–1.21 K
- local EMOS has about 0.82–0.90 K
- the best neural or boosted models have about 0.66–0.82 K

That is roughly 30–45% better than raw, and about 10–20% better than EMOS at day 1, with the gain shrinking to a few percent by day 5. EUPPBench's own per-method table could not be read; the numbers below come from papers run on EUPPBench data.

### Cited Findings
**Rasp & Lerch (2018), arXiv 1805.09091 v1** — [PDF](https://arxiv.org/pdf/1805.09091)
- Setup: ECMWF 50-member ENS from TIGGE (0.5°), 00 UTC runs, T2m at **48 h lead**, 537 DWD stations in Germany. Test year 2016; training on either 2015 or 2007–2015. (§2.1)

*Table 2: mean CRPS (°C) on the 2016 test year*

| Model | 2015 training | 2007–15 training |
|---|---|---|
| Raw ensemble | 1.16 | 1.16 |
| EMOS-gl (global) | 1.01 | 1.00 |
| EMOS-loc (local) | 0.90 | 0.90 |
| EMOS-loc-bst (local, boosting) | 0.85 | 0.80 |
| QRF | 0.95 | 0.81 |
| FCN | 1.01 | 1.01 |
| FCN-aux | 0.92 | 0.91 |
| FCN-emb | 0.91 | 0.91 |
| FCN-aux-emb | 0.88 | 0.87 |
| NN-aux | 0.90 | 0.86 |
| NN-aux-emb | **0.82** | **0.78** |

- EMOS-gl improves 13% on raw, and local information adds another 10%. NN-aux-emb is 3% better than EMOS-loc-bst and 29% better than raw (2015 training).
- More training data helps nonlinear models by 4–5% but barely helps linear ones. Rolling-window EMOS gave "only marginal improvements".
- NN-aux-emb is best at 65.9% of stations (2015) and 73.5% (2007–15). It is significantly better than EMOS-loc-bst at 30% of stations and worse at 2% or fewer. Local EMOS or QRF tend to win at coastal and offshore stations. (§5.1–5.2)

**Schulz & Lerch (2022), arXiv 2106.09512 — wind gusts, not temperature** — [PDF](https://arxiv.org/pdf/2106.09512)
- Setup: COSMO-DE-EPS (20 members), 175 German stations, 6 years, lead times 0–21 h.
- Table 3 mean CRPS (m/s), averaged over lead times and stations:

| Method | CRPS |
|---|---|
| Raw EPS | 1.33 |
| EMOS | 0.95 |
| MBM | 0.97 |
| IDR | 0.98 |
| EMOS-GB | 0.88 |
| QRF | 0.87 |
| DRN | 0.84 |
| BQN | 0.84 |
| HEN | 0.86 |

- The basic methods improve on the raw ensemble by about 26–29%.
- NN methods are significantly better than the basic methods at more than 97% of station × lead-time cases, and better than the ML methods at more than 80%.

**EUPPBench T2m (Demaeyer et al. 2023, ESSD 15:2635)**
- The paper was not read (ESSD returned 403). Numbers below come from later arXiv studies on its data.
- Höhlein et al., arXiv 2309.04452, Table 4 — [arXiv HTML](https://arxiv.org/html/2309.04452)
  - Train on 11-member IFS reforecasts; test on 2013–2016. Mean CRPS in K:

| Method | 24 h | 72 h | 120 h |
|---|---|---|---|
| Raw EPS | 1.21 | 1.28 | 1.54 |
| EMOS | 0.82 | 0.96 | 1.25 |
| DRN | 0.67 | 0.86 | 1.19 |
| BQN | 0.67 | 0.87 | 1.20 |
| Set-transformer (ST-DRN/ST-BQN) | 0.66 | 0.87 | 1.19 |

  - Prediction-interval coverage at a nominal 83.33%: raw 39.85% at 24 h; EMOS 82.56%; DRN 84.16%.
  - Gains over EMOS are about 19% at 24 h and about 5% at 120 h.
- Mlakar et al., arXiv 2303.17610 (ANET), Table 1 — [arXiv HTML](https://arxiv.org/html/2303.17610)
  - EUPPBench 51-member test set, averaged over 229 stations and all lead times (1–5 days).
  - CRPS: ANET2 0.923, ANET2-BERN 0.935, ANET2-NORM 0.940, ANET1 0.988.
  - ANET2 is best at 204 of 229 stations. Mean and variance statistics "contain enough information".
- arXiv 2606.08587 (Jun 2026) adds a sharpness penalty to a Gaussian DRN on EUPPBench T2m. Central prediction intervals shrink by 8.2–12.5% with no loss in CRPS or RMSE. (abstract only) — [arXiv abs](https://arxiv.org/abs/2606.08587)
- Van Poecke et al., arXiv 2412.13957: a self-attentive Transformer applied to *gridded* EUPPBench data. It beats classical MBM; for 10 m wind it improves CRPS by 10% over raw vs 8% for MBM. I could not parse the T2m numbers from the table. — [arXiv HTML](https://arxiv.org/html/2412.13957)
- arXiv 2504.03463 (FMAP, flow matching with a spatial-attention transformer) on EUPPBench stations, T2m and gusts up to 5 days. (abstract only) — [arXiv abs](https://arxiv.org/abs/2504.03463)

**Deterministic model → probabilistic at METAR stations: arXiv 2406.02141 (corrects the earlier note)** — [arXiv HTML](https://arxiv.org/html/2406.02141)
- GDPS deterministic surface temperature up to 10 days, 1,066 METAR stations in Canada and the US from IEM.
- Table 3, CRPS pooled over all lead times:

| Model | CRPS | CRPSS vs naive |
|---|---|---|
| Raw | 2.925 | −0.523 |
| Naive (past errors) | 1.921 | 0 |
| MOS | 2.467 | −0.284 |
| EMOS | 1.700 | +0.115 |
| DRN | 1.633 | +0.150 |
| BQN | 1.622 | +0.156 |
| QRN | 1.635 | +0.149 |

- RMSE: raw 4.07, EMOS 3.33, BQN 3.22.
- The NN advantage over EMOS is larger at early lead times and shrinks to about 2.5% later.

**AI weather models**
- arXiv 2606.19642 (Jun 2026): the coverage of GenCast, NeuralGCM and AIFS-ENS "can struggle, especially on extreme events". Online conformal prediction restores coverage for temperature and precipitation. (abstract only) — [arXiv abs](https://arxiv.org/abs/2606.19642)
- An arXiv search for "AIFS postprocessing stations" and "GraphCast station temperature post-processing" returned nothing new.

### Inferences
- For bucket pricing: a calibrated day-1 station CRPS of about 0.66–0.85 K implies σ ≈ CRPS/0.56 ≈ 1.2–1.5 K ≈ 2.1–2.7 °F. That is consistent with Crosier's NBM RMSE of 2.1–2.7°F. The NBM is already a strong post-processed product, so further ML gains over it are likely a few percent, not tens of percent.
- All of these numbers are instantaneous T2m at fixed hours, not the daily max, and they are European or German stations. Tmax-specific CRPS benchmarks remain a gap.

### Gaps
- The EUPPBench paper's own CRPSS-by-method table (§5) is unread because ESSD was blocked.
- I found no peer-reviewed post-processing of AIFS or GraphCast **daily Tmax** at US stations.

---

## Q4. Intraday nowcasting of the daily maximum (P(max already reached), remaining warming)

### Takeaway
I found no dedicated academic method for "the probability the daily max has already occurred" or for the conditional distribution of remaining warming. This covers arXiv searches and web search. The nearest primary-source practices are:
- Crosier's "completed forecast", which takes the max of the observed running max and LAMP's remaining hours
- LAMP itself, statistical guidance conditioned on observations
- Qiu & Qiu's evidence that market scores sharpen most within 12 h of the peak, while favourites are overconfident there

### Cited Findings
- Crosier completes daytime-max forecasts by taking the highest of the product's daily max, LAMP's hourly forecast for the remaining night hours, and the observed max since local midnight. The high falls outside the daytime window on 4.6% of days. — [Crosier App. A.2](https://arxiv.org/html/2609.23969v1)
- Taking the max of hourly forecasts runs cold because of Jensen's inequality (max_h E[T_h] ≤ E[max_h T_h]) and because the official high falls between hours. LAMP runs 1–2°F cold. — [Crosier App. A.3](https://arxiv.org/html/2609.23969v1)
- LAMP "drives the public stack's improvement the most over the course of the day". The IEM archive keeps only the 00/06/12/18 UTC LAMP cycles. — [Crosier §3.2, App. A.3](https://arxiv.org/html/2609.23969v1)
- In Polymarket weather markets, Brier, log loss and RPS fall gradually from 48 h to 12 h and then much faster inside 12 h of the peak. Favourites at 75–95¢ are overpriced by about 10 percentage points in that window. — [Qiu & Qiu §IV](https://arxiv.org/html/2610.13593)
- Climatology of the hour of maximum: one Brazilian automatic-station study found the daily max most frequent at 16:00, shifting to 17:00 in Dec–Jan. Snippet only, not read. — [Santa Maria study (aminer)](https://aminer.org/pub/62284cf55aee126c0f26815b/hours-of-occurrence-of-daily-extreme-air-temperature-and-relative-humidity-in)

### Inferences
- A practical model: fit an empirical conditional distribution of (final CLI max − running max) by station, season, local hour, current temperature trend and LAMP/HRRR remaining-hour max. Estimate it from IEM ASOS 1-min or 5-min data plus CLI. This is where the documented favourite-overconfidence niche (1–12 h before the peak) would be exploited or rejected.

### Gaps
- No peer-reviewed paper on this topic was found. This may reflect search limits (AMS journals and the export.arxiv API were not reachable) rather than absence.

---

## Q5. NBM versions and Tmax verification

### Takeaway
- NBM v4.1 (Jan 17, 2023) calibrates probabilistic MaxT/MinT quantile mapping to METAR observations instead of URMA.
- NBM v5.0 (Apr 21, 2026) makes deterministic daily Max/Min T equal to the **mean of the QM distribution**, with a standard deviation also taken from QM.
- The operational version before v5.0 was v4.3.
- I found no official numeric Tmax MAE or calibration table; MDL verification pages were unreachable. The best recent independent numbers are Crosier's NBM RMSEs at Kalshi stations.

### Cited Findings
- v4.1 SCN (effective Jan 17, 2023, 12 UTC run):
  - URMA is replaced by the METAR value for bias correction in the quantile mapping of daily probabilistic MaxT/MinT, "allow[ing] all available input models … to be calibrated to METAR observations rather than the URMA analysis".
  - Percentile elements TXNP1/2/5/7/9 (10th/25th/50th/75th/90th) are listed for the NBP text bulletin. In this SCN the new MaxT/MinT percentiles are described for the Alaska domain.
  - Daily mean MaxT/MinT dissemination moves to 01 and 13 UTC.
  - Source: [SCN22-131](https://www.weather.gov/media/notification/pdf2/scn22-131_nbm_v4.1.pdf)
- v5.0 SCN (effective Apr 21, 2026, 13 UTC run):
  - "the Daily Maximum and Minimum temperature values … now represent the mean of the QM distribution … The associated standard deviation values are also derived from the QM solution space."
  - Deterministic temperatures are "no longer computed independently from the probabilistic values".
  - Decaying-average instantaneous T, Td, apparent T and RH are replaced by QM with percentiles.
  - Station lists and text-card links are at vlab .../nbm-stations-v5.0 and .../nbm-textcard-v5.0.
  - Source: [SCN26-24](https://www.weather.gov/media/notification/pdf_2026/scn26-24NBM_V5(1).0_aaa.pdf)
- NBM user webinar (2026-04-15):
  - Bias correction tracks each model's errors over the past "60–120, depending on the parameter" days. More weight goes to models that have recently performed well, by element and forecast hour.
  - Temperature quantile mapping uses a **Gaussian** distribution.
  - At METAR sites the NBM corrects to METAR, and elsewhere to URMA, which produces "bullseye" artifacts.
  - Known failure mode: the first heat wave of the season, when the bias correction "is working off of the biases during the end of winter and spring and increases already predicted hot values", and forecasts sit in the distribution tails.
  - The slides contrast "ops v4.3" with v5.0.
  - Source: [NBM webinar PDF, slides 15–17, 21–23, 31](https://www.weather.gov/media/wrn/calendar/NBMUserWebinar4-15-26.pdf)
- NBM v4.2 went operational on May 15, 2024. Snippet only, not read. — [vlab news](https://vlab.noaa.gov/web/mdl/-/nbm-upgraded-to-version-4-2)
- MDL AMS 2017 poster (NBM v1.0/v2.0):
  - Station verification against 1,319 METARs.
  - "Day 4 NBM forecast is as skillful as Day 2 BC GFS". NBM skill is comparable to NDFD. NBM verifies better against URMA than against METARs because it was tuned to URMA.
  - Numbers appear in figures only.
  - Source: [AMS2017-NBMVerification](https://www.weather.gov/media/mdl/AMS2017-NBMVerification.pdf)
- Independent recent numbers, NBM daily-high RMSE at 7 Kalshi CLI stations, 2022–Aug 2026:
  - 2.70°F at 11:00 ET on d−1, 2.45°F at 19:00 local on d−1, 2.12°F at 13:00 UTC on day d
  - Miami about 1.6°F; other cities 2.6–3.5°F (d−1 morning)
  - NBM and LAMP are the strongest public products; NDFD is next, and raw models last.
  - Source: [Crosier Table 2, §4](https://arxiv.org/html/2609.23969v1)

### Inferences
- Since v5.0, the NBS/NBP deterministic MaxT is the QM mean and comes with a QM standard deviation. A Gaussian N(mean, sd) from NBM is therefore an internally consistent baseline distribution for bucket pricing.
- The NBM's 60–120-day bias memory implies known lag at seasonal transitions. Local recalibration on recent CLI errors should help most in spring.

### Gaps
- There is no official NBM PMaxT reliability or PIT verification. The only calibration evidence is the AMS 2024 Boise abstract in the earlier notes (90th percentile exceeded about 16% of the time).
- Craven et al. 2020 (JOM) and the v4.2 slides were unreachable (403).
