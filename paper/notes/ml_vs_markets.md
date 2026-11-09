# ML/AI forecasters vs human crowds and prediction markets; prediction-market efficiency and information-incorporation speed — positioning a Polymarket temperature-markets vs NWP/AI study

> Method note: arxiv.org and nextpredict.io could NOT be fetched from this session (DNS blocked). Every arXiv item below rests on search-engine snippets or secondary summaries (RePEc/IDEAS, emergentmind, alphaxiv, deeppaper, news). Items marked **[snippet-only]** were not verified against full text. Numbers should be rechecked against the PDFs before citing in a paper.

## Q1. ML/LLM forecasters vs human crowds and prediction markets (what exists, findings, venues)

### Takeaway
A substantial 2024–2026 literature benchmarks LLM forecasters against human crowds (Metaculus, superforecasters) and, more recently, against live Polymarket/Kalshi prices. The consistent result: the best LLM systems approach but do not beat strong human crowds or market prices on average. Markets serve either as the ground-truth "crowd" baseline or as the trading venue. All of this work is about *general event questions* (politics, economics, sports) answered by LLMs. None of it uses physical-model forecasts (NWP or AI weather emulators) against markets on physical outcomes.

### Cited Findings
**Core benchmarks (peer-reviewed venues)**
- ForecastBench (Karger et al., ICLR 2025): a dynamic, automatically updated benchmark of 1,000 questions, part drawn from prediction markets. Superforecasters scored Brier 0.093, the general public 0.107 and the best LLM (Claude 3.5 Sonnet) 0.111. Experts beat the top LLM with p < 0.001. Giving LLMs access to crowd forecasts on market questions significantly improves their scores. — [ICLR 2025 proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ea74e45a229dac70b5b63b28d8934db6-Abstract-Conference.html); [GitHub](https://github.com/forecastingresearch/forecastbench)
- A secondary wiki reports GPT-4.5 (Feb 2025) at a difficulty-adjusted Brier of 0.101 against 0.081 for superforecasters, and projects LLM–superforecaster parity around Nov 2026. That projection is the wiki's own linear extrapolation, not a finding of the paper. — [LongTermWiki](https://www.longtermwiki.com/wiki/E144) [secondary]
- Halawi, Zhang, Chen (Yueh-Han), Steinhardt, "Approaching Human-Level Forecasting with Language Models" (NeurIPS 2024). The system combines retrieval with a fine-tuned LM and was tested on 914 binary questions from competitive forecasting platforms opened after June 2023. Its Brier was 0.179 against the crowd's 0.149, and accuracy 71.5% against 77.0%. In a selective setting (when the crowd is uncertain at 0.3–0.7, or on early retrieval dates) it matches or beats the crowd (0.238 vs 0.240). Averaging system and crowd forecasts beats the crowd alone (reported 0.149 → 0.146). RMS calibration error was 0.42 against 0.38 for the crowd. — [arXiv 2402.18563](https://arxiv.org/html/2402.18563v1); [NeurIPS 2024 poster](https://neurips.cc/virtual/2024/poster/95949) [snippet-only for numbers]
- Schoenegger, Tuminauskaite, Park, Bastos, Tetlock, "Wisdom of the silicon crowd" (Science Advances 10(45), 2024, doi:10.1126/sciadv.adp1528). An ensemble of 12 LLMs forecast 31 binary questions and was statistically indistinguishable from a crowd of 925 humans in a 3-month tournament. Exposure to the human median improved LLM accuracy by 17–28%, but simply averaging human and machine forecasts was still better. — [arXiv 2402.19379](https://arxiv.org/abs/2402.19379v6); [LSE repository](https://researchonline.lse.ac.uk/id/eprint/125626)

**Metaculus AI Benchmark / FutureEval (non-peer-reviewed, organisation reports)**
- Q2 2025: 54 bot-makers and $30k in prizes, on 348 questions. A team of 10 Metaculus Pros beat the top-10 bot team (p = 0.00001, one-sided t-test on Peer scores). Later models clearly outperform earlier ones, and o3 led the baseline bots. — [LessWrong, Metaculus](https://www.lesswrong.com/posts/Surnjh8A4WjgtQTkZ/q2-ai-benchmark-results-pros-maintain-clear-lead)
- Q1 2025 report title: "Pro forecasters crush bots". A later "FutureEval spring" report says "pros beat bots but the gap is [narrowing]". — [Q1](https://www.lesswrong.com/posts/rDy5z8ZEtMrEGnfBd/q1-ai-benchmark-results-pro-forecasters-crush-bots); [FutureEval spring](https://www.lesswrong.com/posts/wZBbDqzfBjYG58CxK/futureeval-spring-results-pros-beat-bots-but-the-gap-is); [FutureEval description](https://metaculus.substack.com/p/metaculus-futureeval-ai-forecasting-benchmark) [snippet-only]
- Survey: "AI forecasting in 2026: what 11 analyses say". — [LessWrong](https://www.lesswrong.com/posts/a82q6yd8zKpYk56cF/ai-forecasting-in-2026-what-11-analyses-say) [not read]

**LLMs vs live Polymarket/Kalshi ("pitting LLMs against markets") — mostly 2026 arXiv preprints**
- Prediction Arena (arXiv 2604.07355, submitted 28 Mar 2026). Frontier LLMs traded as autonomous agents with real capital on Kalshi and Polymarket for 57 days (12 Jan – 9 Mar 2026). There were six live models and four paper-trading models; the second cohort ran only 3 days. Cohort-1 Kalshi returns ranged from −16.0% to −30.8%. One summary reports an average of −1.1% on Polymarket against −22.6% on Kalshi. Initial prediction accuracy drove outcomes, and research volume showed no correlation. A separate summary of the paper reports that **weather markets dominate settlement volume on Kalshi**. I found no weather-specific performance breakdown. — [IDEAS/RePEc](https://ideas.repec.org/p/arx/papers/2604.07355.html); [arXiv PDF](https://arxiv.org/pdf/2604.07355) [snippet-only]
- PolyBench (Cheng, Liu, Long; arXiv 2604.14199): 38,666 binary Polymarket markets across 4,997 events, with order-book snapshots and paired news. Seven LLMs produced 36,165 predictions on early-Feb-2026 market states, scored on directional accuracy and a return-based metric. — [IDEAS/RePEc](https://ideas.repec.org/p/arx/papers/2604.14199.html); [secondary](https://letsdatascience.com/news/polybench-evaluates-llm-forecasting-and-trading-performance-8e2c781c) [snippet-only]
- Foresight Arena (arXiv 2605.00420): an on-chain benchmark. Agents commit-reveal probabilistic forecasts on Polymarket binaries on Polygon and are scored by Brier and its decompositions. — [arXiv html](https://arxiv.org/html/2605.00420v1) [snippet-only]
- TU Delft MSc thesis (2026), "Performance of LLMs in Prediction Markets": compares LLM probabilities with live Polymarket prices. It concludes that current LLMs cannot substitute for markets as information aggregators. — [TU Delft repository](https://repository.tudelft.nl/record/uuid:6add2e07-a494-442a-8e6a-ac352db40b19) [snippet-only]
- Lightning Rod Labs blog: a fine-tuned "Foresight 32B" beat frontier LLMs on live Polymarket questions, but the market price beat all the models. — [blog](https://blog.lightningrod.ai/p/foresight-32b-beats-frontier-llms-on-live-polymarket-predictions) [company blog, not peer-reviewed]
- Other related arXiv work: "Reinforcement Learning for LLM-based Event Forecasting" (arXiv 2606.15917) and an analysis of which question types LLMs forecast well (arXiv 2511.18394). — [2606.15917](https://arxiv.org/pdf/2606.15917); [2511.18394](https://arxiv.org/html/2511.18394v1) [title/snippet-only]

### Inferences
- The field's framing is now "human crowd/market = the bar; LLMs approaching it". Hybrids (model + crowd) beat either alone (Halawi; Schoenegger). This maps directly onto the weather case, where a natural test is whether NWP/AI + market beats the market.
- Venues: ICLR (ForecastBench), NeurIPS (Halawi), Science Advances (Schoenegger). The live-market LLM benchmarks are so far arXiv/q-fin/cs.AI preprints.
- None of these works evaluates *physics-based or AI weather models* against markets. The forecasters are LLMs answering text questions, so the weather study occupies a different niche: domain-specialised quantitative models against markets on physically measured outcomes.

### Gaps
- Exact Prediction Arena per-category results (weather) could not be retrieved because arXiv was unreachable.
- I could not confirm a single paper titled exactly "Pitting LLMs against prediction markets". The closest matches are PolyBench, Prediction Arena, Foresight Arena and the TU Delft thesis.

## Q2. Market-as-benchmark in other domains (sports, elections, macro, weather derivatives)

### Takeaway
Across domains, markets are the hard baseline. Sports ML models roughly match but rarely beat liquid betting markets. Kalshi beats Bloomberg consensus on headline CPI. CME temperature futures beat meteorological-forecast-derived index forecasts. Roll (1984) showed orange-juice futures predicted errors in National Weather Service forecasts. The weather-derivatives literature is the closest precedent for "markets vs NWP", but it is monthly-index, pre-2015 and pre-AI.

### Cited Findings
**Macro / Kalshi**
- Federal Reserve FEDS 2026-010, "Kalshi and the Rise of Macro Markets". Kalshi gives a statistically significant improvement over the Bloomberg consensus for headline CPI. It is roughly equal to consensus for core CPI and unemployment. Kalshi's modal forecast on the day before every FOMC meeting since 2022 matched the decision. Caveat: surveys are fielded 1–2 weeks earlier, so the comparison has a timing advantage. Benchmarks were the NY Fed Survey of Market Expectations, Bloomberg consensus and fed funds futures. — [Fed paper PDF](https://www.federalreserve.gov/econres/feds/files/2026010pap.pdf); [The Defiant](https://thedefiant.io/news/research-and-opinion/fed-research-finds-kalshi-markets-outperform-wall-street-surveys) [snippet/secondary]
- Goel (2026, International Review of Economics and Finance) asks whether Kalshi prices contain information about the magnitude of macro surprises beyond professional forecasts. — [search snippet via Glasgow eprints](https://eprints.gla.ac.uk/390184/) [snippet-only; authorship/URL association uncertain]
- "The Shape of Macroeconomic Beliefs" (arXiv 2606.30040) uses Kalshi distributions. — [arXiv](https://arxiv.org/pdf/2606.30040) [title-only]

**Sports**
- Evidence is mixed and of low quality. A random forest roughly matched Betfair implied probabilities on Brier score (Malta MSc 2018, small sample). Some ML strategies beat "both teams to score" markets. A 2025 preprint argues the model–market gap has closed in the big-data era, but it uses bookmaker odds as a feature. — [UM Malta](https://www.um.edu.mt/library/oar/handle/123456789/39745); [Qeios preprint](https://www.qeios.com/read/7A61RS/pdf) [snippet-only]
- A market-calibrated in-play football model (arXiv 2605.16066) reports that **99% of Betfair price reactions to 470 goals are absorbed within two minutes**. — [arXiv 2605.16066](https://arxiv.org/pdf/2605.16066) [snippet-only]
- "Convolutional Attention in Betting Exchange Markets" (arXiv 2510.16008) applies deep learning to exchange price data. — [arXiv](https://arxiv.org/pdf/2510.16008) [title-only]

**Weather derivatives / commodity futures (closest precedent)**
- Roll (1984), "Orange Juice and Weather", AER 74(5). Frozen concentrated orange juice (FCOJ) futures returns are significantly related to *subsequent errors* in NWS temperature forecasts for central Florida, so the market improves on the official forecast. Boudoukh et al. (2007) revisited this and found FCOJ prices do react significantly to temperature. — [Caltech record](https://resolver.caltech.edu/CaltechAUTHORS:20190501-112416217); [Columbia water paper (discussion)](https://water.columbia.edu/sites/water.columbia.edu/files/content/publications/Big-Data-Climate-Commodity-Production-Forecasts.pdf)
- A Humboldt University Berlin working paper finds that CME HDD/CDD monthly futures prices significantly outperform index forecasts derived from meteorological forecasts in predicting the end-of-month index. — [HU Berlin edoc](https://edoc.hu-berlin.de/bitstreams/03f4b6ce-a8a7-4f1f-924d-c6046ff9c98a/download) [snippet-only]
- Chincarini (2011, Journal of Futures Markets 31(1):1–33) tests weather-futures efficiency. It compares market-implied forecasts with other forecasts, checks for over- or under-reaction to temperature surprises, and looks at patterns across cities. A 2009 EFMA paper covers CME HDD/CDD futures in 18 US cities. — [IDEAS](https://ideas.repec.org/a/wly/jfutmk/v31y2011i1p1-33.html); [EFMA 2009](https://www.efmaefm.org/0efmameetings/EFMA%20ANNUAL%20MEETINGS/2009-Milan/papers/EFMA2009_0595_fullpaper.pdf) [snippet-only]
- Jewson & Caballero conclude that meteorological forecasts must be included in weather-derivative pricing (cited in HU Berlin work). — [HU Berlin edoc](https://edoc.hu-berlin.de/server/api/core/bitstreams/1d4ce83c-aa0e-433a-9d8e-f18b600950dd/content) [snippet-only]

**Elections**
- Ng, Peng et al. (SSRN 5331995), "Price Discovery and Trading in Modern Prediction Markets" (Polymarket, Kalshi, PredictIt, Robinhood; elections). The venue with more directional large-trade order flow leads price discovery, and Polymarket leads Kalshi when liquidity is high. — [SSRN](https://papers.ssrn.com/abstract=5331995); [seminar abstract](https://en.rmbs.ruc.edu.cn/Media/Seminars/cf4d5bbb42da4fac808ba83cbe692759.htm) [snippet-only]

### Inferences
- The weather-derivatives and FCOJ literature is the intellectual ancestor of "market vs NWP". It found markets beating the official forecast at monthly or seasonal scale. A modern station-level daily-max study can frame itself as revisiting Roll (1984) and Chincarini (2011) with (i) retail binary bucket markets, (ii) AI weather models (GraphCast/AIFS/Aurora etc.) and (iii) tick-level latency.
- In macro, the market's edge partly reflects later information timing (Fed paper caveat). A weather study should control for *forecast issuance time against market timestamp*, which is the core of a latency design.

### Gaps
- I found no peer-reviewed study benchmarking modern ML sports models against Pinnacle/Betfair closing lines in 2018–2026. The literature found is theses and preprints.
- I did not retrieve canonical election-market vs polls work (e.g., Berg/Rothschild) in this pass. Those works predate 2018 and are standard references.

## Q3. Prediction-market efficiency: calibration, favourite-longshot bias, speed of information incorporation, latency arbitrage

### Takeaway
Recent large-sample studies of Kalshi and Polymarket find prices informative but with a persistent favourite-longshot bias (FLB) or compression toward 0.5, which varies by domain and horizon. On speed, the only hard numbers found come from sports exchanges (seconds to two minutes) and equities HFT (milliseconds). No study was found that measures how fast Kalshi or Polymarket prices absorb a scheduled public data release (e.g., an NWS observation, METAR or model run) at seconds resolution. That is the open niche.

### Cited Findings
**Calibration / FLB on Kalshi/Polymarket**
- Bürgi, Deng & Whelan, "Makers and Takers: The Economics of the Kalshi Prediction Market" (GWU working paper 2026-001; VoxEU column), covering more than 300k Kalshi contracts. Prices are informative and improve as markets approach close, but show a clear FLB. Takers lose about 32% on longshots and makers about 10%. Price bias is diminishing over time. Next-day city high-temperature markets are among the most common short-lived Kalshi markets. — [Whelan PDF](https://www.karlwhelan.com/Papers/Kalshi.pdf); [GWU WP](https://www2.gwu.edu/~forcpgm/2026-001.pdf); [VoxEU](https://cepr.org/index%2Ephp/voxeu/columns/economics-kalshi-prediction-market)
- Le (arXiv 2602.19520, Feb 2026), "Decomposing Crowd Wisdom". Calibration depends on domain, time to resolution and trade size. Political contracts are underconfident, with a mean slope of 1.64 on Kalshi and 1.31 on Polymarket. A four-component model explains 87.3% of calibration variance on Kalshi, but only 71.5% in leave-one-cell-out prediction. The trade-size effect does not replicate on Polymarket. Version discrepancy: v1 reports 292M trades on 327k contracts, while a later listing reports 353M trades on 429k contracts. Le notes that Weather has negligible Polymarket presence in his classified sample. — [alphaxiv](https://www.alphaxiv.org/abs/2602.19520); [arXiv html v1](https://arxiv.org/html/2602.19520v1) [snippet-only]
- Princeton senior thesis, "The Price is (Almost) Right": 188,509 resolved Polymarket binaries (Nov 2022 – Dec 2025). Brier Skill Score is 0.398. Prices are compressed toward 0.5 (longshots overpriced), present in all domains and worse at long horizons. — [Princeton](https://theses-dissertations.princeton.edu/entities/publication/d5708372-5ea3-4252-b669-7f9cee07387c) [snippet-only]
- A secondary claim: in a study of 2,668 Kalshi macro contracts (UCD), Fed/rates contracts showed no FLB, while CPI/jobs contracts did. — [secondary blog](https://sportsgameodds.com/blog/prediction-markets-beat-professional-forecasters) [unverified]

**Speed of information incorporation**
- Betfair in-play football: 99% of reactions to goals are absorbed within 2 minutes (arXiv 2605.16066). — [arXiv](https://arxiv.org/pdf/2605.16066) [snippet-only]
- Betfair's speed bump (5–9 s) mechanically delays in-play reaction, which matters for timestamp alignment. Prices react efficiently to expected news but inefficiently to surprises (1,004 Premier League in-play markets). — [Reading EM DP 2019-20](https://www.reading.ac.uk/web/files/economics/emdp201920.pdf); [IJF 2021 (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0169207021000996)
- Breaking political news ("Bigotgate", 2010): Betfair prices adjusted with a delay and post-news drift. Social media identified inefficiencies. — [GWU WP 2016-002](https://www2.gwu.edu/~forcpgm/2016-002.pdf)
- Docherty & Easton, "Market Efficiency and Continuous Information Arrival: Evidence from Prediction Markets" (SSRN 1772811). — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1772811) [title-only]
- OpenMarket (arXiv 2607.26245): a synchronised Polymarket–Binance dataset for high-frequency prediction-market research. It is relevant as a methods and data precedent for tick-level Polymarket analysis. — [arXiv](https://arxiv.org/pdf/2607.26245) [title-only]

**Latency arbitrage (HFT)**
- Budish, Cramton & Shim (QJE 2015, 130(4):1547–1621). The median duration of ES–SPY arbitrage opportunities fell from 97 ms (2005) to 7 ms (2011) while profitability stayed constant. The continuous limit order book creates a speed arms race, and they propose frequent batch auctions. — [RePEc](https://econpapers.repec.org/RePEc:oup:qjecon:v:130:y:2015:i:4:p:1547-1621)
- Aquilina, Budish & O'Neill, "Quantifying the High-Frequency Trading Arms Race" (NBER w29011; later QJE 2022). Using LSE message data, latency-arbitrage races account for about 20% of volume, and the top 6 firms win or lose over 80% of races. This amounts to a 0.5 bp tax, a 17% cost of liquidity, and about $5bn/yr globally in equities. — [NBER](https://www.nber.org/system/files/working_papers/w29011/w29011.pdf)

### Inferences
- A weather-market latency study fits naturally in a Budish-style "stale quote sniping" framing. Station observations (METAR/ASOS 5-min data, NWS CLI reports) and model runs (HRRR hourly, GFS/ECMWF/AIFS 6-hourly) are public, scheduled, timestamped signals. The time from signal release to price move, and the profits available to fast traders, are measurable much as in a sports goals event study.
- Daily-temperature markets are a rare case of an objectively verifiable physical outcome with high-frequency, exogenous public information. That makes them a cleaner efficiency laboratory than politics.

### Gaps
- No seconds-level event study of Kalshi/Polymarket reactions to scheduled data (macro releases or weather observations or model runs) was found.
- I did not find studies of Polymarket order-book microstructure specific to weather markets, beyond Qiu & Qiu on FLB.

## Q4. Other 2024–2026 arXiv/SSRN works on Kalshi/Polymarket weather markets, and whether anyone has done "AI/NWP weather models vs weather prediction markets"

### Takeaway
Beyond the three known papers, searches found no other academic paper comparing NWP or AI weather models with Kalshi/Polymarket weather markets. What exists is (i) Crosier 2026 (Kalshi vs NBM and other public forecasts, 7 US cities), (ii) Qiu & Qiu 2026 (FLB in Polymarket temperature markets, 10 cities, 1-month test, explicitly not compared with forecasts), (iii) Le 2026 (cross-domain calibration, weather negligible on Polymarket), plus incidental mentions (Prediction Arena, Bürgi et al.) and many GitHub trading bots or blogs. No academic work uses AI weather models (GraphCast/GenCast/AIFS/Aurora) against these markets.

### Cited Findings
- Crosier (arXiv 2609.23969), "Prediction Markets Beat the Weather Forecast on Tomorrow's High Temperature". It builds a market-implied forecast from Kalshi next-day high-temperature bucket ladders (about 5 years of data, 7 US cities). Traders' forecasts beat "the entire stack of public weather forecasts". The Kalshi forecast beats the NBM in 6 of 7 cities, and on the target morning it still has about 11% lower error. — [arXiv PDF](https://arxiv.org/pdf/2609.23969); [nextpredict summary](https://nextpredict.io/market-news/industry/study-kalshi-weather-markets-outperform-public-forecasts/) [snippet-only, full text not fetched]
- Qiu & Qiu (arXiv 2610.13593, submitted 9 Oct 2026), "Time-Varying Favorite-Longshot Bias in Polymarket Weather Markets". Daily max-temperature markets in 10 cities over a 1-month test period, using event-level probability scores, cubic B-spline recalibration and Buy-NO tests. The authors state the results assess calibration and *do not establish an advantage over public weather forecasts*. It is a 5-page paper accepted at the IEEE ICDM 2026 Teen Research Symposium. — [arXiv abs](https://arxiv.org/abs/2610.13593); [html](https://arxiv.org/html/2610.13593) [snippet-only]
- Le (arXiv 2602.19520): Weather and Entertainment have negligible Polymarket presence in the 2021-onward classified data, while Kalshi has far more markets. — [arXiv PDF](https://arxiv.org/pdf/2602.19520) [snippet-only]
- Prediction Arena (arXiv 2604.07355): weather markets dominate Kalshi settlement volume. No weather-specific model evaluation was found. — [arXiv PDF](https://arxiv.org/pdf/2604.07355) [snippet-only]
- Bürgi, Deng & Whelan: daily city-high-temperature markets are among the most common short-lived Kalshi markets. — [Whelan PDF](https://www.karlwhelan.com/Papers/Kalshi.pdf)
- "What Happens When Institutional Liquidity Enters Prediction Markets" (arXiv 2604.10005) surfaced in weather searches but is not weather-focused. — [arXiv](https://arxiv.org/pdf/2604.10005) [title-only]
- Practitioner, non-academic work:
  - A Polymarket+Kalshi bot using the 31-member GFS ensemble (self-reported profits). — [GitHub suislanchez](https://github.com/suislanchez/polymarket-kalshi-weather-bot)
  - A grading harness comparing Kalshi daily-high buckets with an NBM/HRRR/GFS blend, listing GraphCast as a candidate. — [GitHub EdgeCast](https://github.com/SBasineni1/EdgeCast)
  - An open GitHub issue asking whether open AI weather models can price Kalshi NYC highs better than the market ("We don't know the answer"). It reports raw AIFS running +2.1°F cold. — [GitHub issue](https://github.com/fulton-ring/agent-content-demos/issues/89)
  - An agent listing GraphCast/Aurora/AIFS inference as a backend. — [GitHub openthomas](https://github.com/PredictionMarketTrader/openthomas)
  - A blog claiming NOAA operationalised an AI-enhanced global system in Dec 2025, with an unverified argument that the AI advantage over GFS is modest for 24-h T2m. — [predictandprofit blog](https://predictandprofit.io/blog/noaas-graphcast-goes-operational-what-it-means-for-weather-t) [unverified]
- Resolution-source heterogeneity, per secondary guides:
  - Kalshi's daily temperature markets reportedly use NWS climate data, with a source change reported in Aug 2026.
  - Polymarket's US markets reportedly use the NWS Daily Climate Report (CLI). Polymarket runs daily-high markets in more than 50 cities worldwide, and moved its Paris contracts to a different airport station.
  - Sources: [nextpredict weather guide](https://nextpredict.io/prediction-markets/weather/); [Prediction News](https://predictionnews.com/story/kalshi-and-polymarket-weigh-climate-markets-as-next-growth-area) [secondary, verify in platform rules]

### Inferences
- **Novelty gap.** No identified academic work does any of the following together:
  1. Compares *AI weather models* (GraphCast/GenCast/AIFS/Aurora/FourCastNet) as well as NWP (GFS/ECMWF/HRRR/NBM) with *Polymarket* temperature markets.
  2. Works at *station level*, matched to the exact resolution station (often an airport METAR/ICAO site) and covering *international* cities. Polymarket's 50+ global cities extend beyond Crosier's 7 US Kalshi cities and the NBM's US-only coverage.
  3. Uses *probabilistic* scoring (CRPS/Brier/log score over buckets), compared with Crosier's RMSE-style point-forecast comparison as described.
  4. Includes a *latency/information-incorporation* analysis: how many minutes after a model run becomes available, or a METAR/ASOS observation prints, the market reprices, and whether the market's edge (Crosier's 11% on the target morning) comes from intraday observations rather than better forecasting.
  5. Runs a *hybrid* test (model + market blend), following Halawi and Schoenegger, who found that combining the two beats either alone.
- Qiu & Qiu explicitly leaves "advantage over public weather forecasts" open for Polymarket. Crosier covers Kalshi/US only. The Polymarket × AI-model × station × latency combination appears unaddressed as of Nov 2026, based on search coverage only.
- Positioning: the study can be framed as a bridge between three literatures:
  - LLM/ML vs crowds (ICLR/NeurIPS), extended from LLMs on text questions to physical AI models;
  - commodity and weather-futures efficiency (Roll 1984; Chincarini 2011), extended from monthly indices to daily binary buckets;
  - HFT latency (Budish et al.), extended to stale quotes after public meteorological data.

### Gaps
- Full texts of Crosier, Qiu & Qiu and Le could not be read (arXiv blocked). Whether Crosier includes any AI model, ensemble/probabilistic scoring or intraday latency analysis is unconfirmed. The snippet mentions only "public forecasts" and NBM, plus a "target morning" comparison, which hints at some time-of-day analysis.
- SSRN was not searched directly. There may be unindexed SSRN working papers on Kalshi weather markets.
- The claim that this combination is novel rests on web-search coverage, not on a systematic arXiv/Google Scholar citation-forward search from Crosier 2609.23969. Doing that search is recommended.
