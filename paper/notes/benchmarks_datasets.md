# Benchmarks and datasets for probabilistic weather forecasting and post-processing; what ML venues expect from a new benchmark

Scope note: Research was done by web search plus a few fetches. Fetches to blog.neurips.cc, open-meteo.com, polymarket.com, arxiv.org and papers.cool failed (DNS blocked in this sandbox), so some items come from search-result snippets, not full pages. Items marked [UNVERIFIED] come from background knowledge and no source was retrieved in this session. Check them before citing.

## Q1. Catalogue of relevant benchmarks: scope, targets, metrics, baselines, venue

### Takeaway
The best-known weather benchmarks are gridded, reanalysis-based and global: WeatherBench, WeatherBench 2, ChaosBench, ClimateBench. They appear in JAMES or the NeurIPS D&B track. Station-level post-processing benchmarks exist (EUPPBench in ESSD, the Rasp & Lerch German station data on figshare, Weather2K at AISTATS, WeatherReal on arXiv). None of them targets settlement-exact, decision-relevant daily extremes at specific airports, and none uses a market baseline. The closest precedent is a 2026 arXiv preprint comparing Kalshi temperature markets with NBM forecasts.

### Cited Findings
**Global / gridded**
- **WeatherBench 2** (Rasp, Hoyer, Merose, Langmore, Battaglia, Russell et al., 2024). Published in *JAMES* 16, e2023MS004019, doi:10.1029/2023MS004019; arXiv 2308.15560. Scope is global medium-range (1–14 days). It provides an open-source evaluation framework, public training, ground-truth and baseline data, and a continuously updated website of results. Metrics follow operational-centre practice. Per a secondary summary they include RMSE, ACC, CRPS and SEEPS. Probabilistic skill is reported as CRPS relative to IFS ENS. — [arXiv](https://arxiv.org/pdf/2308.15560); [WB2 site](https://sites.research.google/weatherbench); [Eos/AGU highlight](https://eos.org/?p=224595)
- WB2 is explicitly an update to "the global, medium-range weather forecasting benchmark proposed by Rasp et al. (2020)". — [arXiv 2308.15560](https://arxiv.org/pdf/2308.15560). [UNVERIFIED: the original WeatherBench is Rasp et al. 2020, *JAMES* 12, e2020MS002203. It uses ERA5 regridded to 5.625°/2.8125°/1.4°, Z500/T850 at 3–5 days, with RMSE metrics.]
- **ChaosBench** (LEAP, NeurIPS 2024 Datasets & Benchmarks Track, **oral**; arXiv 2402.00712). It targets subseasonal-to-seasonal (S2S) prediction. Data go beyond ERA5 to ocean, ice and land reanalyses spanning more than 45 years. Baselines are physics-based forecasts from national agencies plus ViT/ClimaX, PanguWeather, GraphCast and FourCastNetV2. It proposes differentiable physics-based (spectral) metrics. A key finding is that weather-scale methods "collapse to an unskilled climatology" at S2S ranges. — [NeurIPS proceedings PDF](https://proceedings.nips.cc/paper_files/paper/2024/file/4d3684dd7926754b48bc6cd99a840232-Paper-Datasets_and_Benchmarks_Track.pdf); [NeurIPS oral page](https://neurips.cc/virtual/2024/oral/98017)
- **ClimateBench v1.0** (Watson-Parris et al., 2022). Published in *JAMES* 14, e2021MS002954, doi:10.1029/2021MS002954. It emulates NorESM2 (CMIP6/AerChemMIP/DAMIP) annual-mean temperature, diurnal temperature range, precipitation and extreme precipitation under emission scenarios, with baseline ML emulators. A 2024 JAMES follow-up (Lütjens et al., arXiv 2408.05288) found that linear regression beats deep learning on 3 of 4 variables. That illustrates how strong simple baselines can reframe a benchmark. — [ORA Oxford](https://ora.ox.ac.uk/objects/uuid:ddee9e44-80d5-439d-83f8-69839dedcc8c); [NOAA repository](https://repository.library.noaa.gov/view/noaa/48746); [Lütjens et al.](https://arxiv.org/pdf/2408.05288v2.pdf)
- **SEVIR** (Veillette, Samsi, Mattioli; NeurIPS 2020, main track, before D&B existed). Covers more than 10,000 weather events as 384×384 km, 4-hour sequences from GOES-16 ABI (3 channels), NEXRAD VIL and GLM lightning. Tasks are nowcasting and synthetic radar. Public reviews and a meta-review exist. — [NeurIPS PDF](https://proceedings.neurips.cc//paper/2020/file/fa78a16157fed00d7a80515818432169-Paper.pdf); [Meta-review](https://papers.neurips.cc/paper_files/paper/2020/file/fa78a16157fed00d7a80515818432169-MetaReview.html)

**Station / point-level post-processing**
- **EUPPBench v1.0** (Demaeyer et al., *ESSD* 15, 2635–2653, 2023, doi:10.5194/essd-15-2635-2023, published 28 June 2023). The EUMETNET post-processing benchmark is "a dataset of time-aligned forecasts and observations". It pairs ECMWF HRES, ENS and reforecasts over central Europe with station observations (BeNeLux, Germany, France, Austria, Switzerland) and ERA5 gridded analyses, covering more than 40 variables. Access is via a climetlab plugin and Zenodo. A companion Zenodo record holds benchmark outputs from several institutions (EMOS, AR-EMOS, DRN, DVQR, member-by-member). The open ESSD discussion (public review) is available. — [ESSD article](https://essd.copernicus.org/articles/15/2635/2023/); [ESSD discussion](https://essd.copernicus.org/articles/15/2635/2023/essd-15-2635-2023-discussion.html); [Zenodo](https://zenodo.org/records/7798350); [ECMWF Newsletter 179](https://www.ecmwf.int/node/29045); [EMS2023 slides](https://presentations.copernicus.org/EMS2023/EMS2023-229_presentation.pdf)
- **Rasp & Lerch (2018)**, "Neural networks for postprocessing ensemble weather forecasts", *Monthly Weather Review* 146(11):3885–3900, doi:10.1175/MWR-D-18-0187.1. Case study of German 2 m temperature, using distributional regression (DRN) against EMOS and related baselines. Later work reused the dataset: 419 German temperature stations, train 2007–2014, validation 2015, test 2016, hosted on figshare (doi:10.6084/m9.figshare.19453580; wind data: 10.6084/m9.figshare.19453622). — [arXiv 1805.09091](https://arxiv.org/abs/1805.09091v1); [Chen et al. arXiv 2211.01345](https://arxiv.org/pdf/2211.01345)
- **Schulz & Lerch** "Machine learning methods for postprocessing ensemble forecasts of wind gusts: a systematic comparison" (arXiv 2106.09512). This is a systematic comparison of post-processing methods. No standalone dataset record was located. — [arXiv](https://arxiv.org/pdf/2106.09512). [UNVERIFIED: published in *MWR* 2022 and uses DWD COSMO-DE-EPS gusts at about 175 stations.]
- **Weather2K** (Zhu et al., AISTATS 2023, PMLR 206:2704–2722). Uses 2,130 Chinese ground stations, of which 1,866 are released as Weather2K-R, plus a 15-station CSV subset. Data are hourly from Jan 2017 to Aug 2021, with 20 variables and 3 static fields. Tasks are time-series and spatio-temporal forecasting, with baselines and a proposed MFMGCN. Hosted on GitHub. It is deterministic and has no NWP inputs. — [PMLR](https://proceedings.mlr.press/v206/zhu23a.html); [arXiv 2302.10493](https://arxiv.org/pdf/2302.10493)
- **WeatherReal** (Jin et al., arXiv 2409.09371, Sept 2024; Microsoft/MSN). An in-situ benchmark, motivated by gaps between ERA5 and station measurements for near-surface variables. Versions are WeatherReal-ISD (NOAA Integrated Surface Database), WeatherReal-Synoptic (Synoptic Data PBC, more than 150k stations) and one from MSN user reports. Quality control merges duplicate stations and flags outliers against ERA5. It evaluates data-driven versus NWP models with RMSE and ACC. Publication venue unclear [UNCERTAIN whether peer-reviewed]. — [arXiv](https://arxiv.org/html/2409.09371v1)
- [UNVERIFIED, not searched: LargeST (NeurIPS 2023 D&B) is a traffic benchmark, not weather. It is useful only as a template for a large sensor-network D&B paper. CorrDiff (Mardani et al., NVIDIA; Taiwan km-scale generative downscaling) is a method paper, not a benchmark.]

**Market-based precedent (closest to the proposed benchmark)**
- "Prediction Markets Beat the Weather Forecast on Tomorrow's High Temperature" (Alexander W. Crosier, arXiv 2609.23969, Sept 2026). Uses five years of Kalshi daily high-temperature markets for 7 US cities. It extracts a market-implied forecast hour by hour and compares it with leading US and European forecasts. Reported result: "by the NBM's final posting on the target morning the Kalshi forecast still has lower error by 11 percent". It also reports that the market does not react to new forecast updates, and that forecasts "slowly publish" information the market already had. Seen only via search snippets; the full text was not read. — [arXiv PDF](https://arxiv.org/pdf/2609.23969)
- Informal analyses of Kalshi weather-market calibration exist: a UT Austin student blog uses Brier scores across 7 cities. Not peer-reviewed. — [UT CS blog](https://www.cs.utexas.edu/~kavish/blog/kalshi-weather-calibration.html)

### Inferences
- Venue pattern:
  - Gridded or global ML-facing benchmarks go to JAMES (WB, WB2, ClimateBench) or NeurIPS D&B (ChaosBench, oral).
  - Station post-processing datasets from the meteorology community go to ESSD (EUPPBench) or ship as figshare/Zenodo supplements to MWR/QJRMS papers.
  - ML-community station datasets go to AISTATS (Weather2K) or stay on arXiv (WeatherReal).
- No benchmark found combines (a) point-in-time (as-issued, no look-ahead) NWP and AI forecasts, (b) targets defined exactly by contract settlement rules, and (c) a real-money market baseline. EUPPBench is the nearest on (a) and on probabilistic station metrics. Crosier (2026) is the nearest on (c), but at 7 US cities, Kalshi only, and apparently no released dataset [UNCERTAIN]. A ~53-airport, multi-country, Polymarket-based benchmark would extend both. The novelty claim must cite and differentiate from Crosier 2026.
- ChaosBench's oral suggests D&B reviewers reward benchmarks that expose a failure mode of SOTA models ("collapse to climatology"). An analogous hook here would be "AI/NWP vs. market at settlement-relevant quantiles", or "markets are not efficient with respect to forecast updates".
- The ClimateBench follow-up shows that reviewers and later work will check whether simple baselines (climatology, persistence, EMOS, raw NWP, linear models) are strong. The benchmark must include them.

### Gaps
- Citation counts were not visible in any retrieved result.
- Full text of Crosier 2026 was not read (arxiv.org blocked). Unknown: whether data or code are released, the exact metric (MAE vs CRPS), and whether settlement-station specifics are handled.
- No search was done on other point-level probabilistic ML benchmarks such as the "PeMS-like" weather station sets, NWS NBM verification datasets, or Kaggle/AMS solar or temperature contests. A follow-up search is needed.

## Q2. NeurIPS Datasets & Benchmarks track: review criteria, requirements, rejection reasons

### Takeaway
Since 2025, NeurIPS D&B has required persistent public hosting plus valid Croissant metadata (one file per dataset) at submission time. Reviewers check documentation (datasheets or data cards), intended use, licence, a hosting and maintenance plan, and reviewer accessibility. Licensing and permission status reportedly gained weight in 2025. The track is moving toward evaluation-science rigour, beyond simply new data.

### Cited Findings
- 2023 reviewer guidelines say dataset submissions need documentation, intended uses, a reviewer-accessible URL, and a hosting, licensing and maintenance plan. Recommended documentation frameworks are datasheets for datasets, dataset nutrition labels, data statements, data cards and accountability frameworks. Reviewers use the NeurIPS paper checklist. — [NeurIPS 2023 D&B Review Guidelines](https://neurips.cc/Conferences/2023/DatasetsAndBenchmarks/ReviewGuidelines); [2023 CFP](https://neurips.cc/Conferences/2023/CallForDatasetsBenchmarks)
- 2025: Croissant metadata became **mandatory**, after being encouraged in 2024. The track required hosting on persistent public repositories. Each dataset in a submission needs its own valid Croissant file containing the dataset URLs. Authors whose file types Croissant cannot describe must still submit a Croissant file. The FAQ advises validating locally because the online validator can time out on Hugging Face due to rate limits. — [NeurIPS 2025 D&B FAQ](https://neurips.cc/Conferences/2025/DatasetsBenchmarks-FAQ); [NeurIPS blog, "Raising the Bar" (snippet)](https://blog.neurips.cc/2025/03/10/neurips-datasets-benchmarks-raising-the-bar-for-dataset-submissions/); [2025 CFP](https://neurips.cc/Conferences/2025/CallForDatasetsBenchmarks)
- The official NeurIPS blog (snippet) reports the common 2025 problems: very large datasets (1 TB or more), platform rate limits, and instability near deadlines. Adoption of the Croissant Responsible-AI (RAI) extension was low. It also says current guidance "leaves room for interpretation, particularly regarding licensing documentation and descriptive context in machine-readable form". — [NeurIPS blog Dec 2025, "From Art to Science in AI Evaluations"](https://blog.neurips.cc/2025/12/05/neurips-datasets-benchmarks-track-from-art-to-science-in-ai-evaluations/) (snippet only; fetch blocked)
- A third-party analysis found that 426 of 497 accepted 2025 D&B papers (85.7%) have a retrievable Croissant document and 71 (14.3%) do not. This is not an official figure. — [Croissant Baker, arXiv 2605.15079](https://arxiv.org/pdf/2605.15079); see also [Croissant Tasks, arXiv 2605.29786](https://arxiv.org/pdf/2605.29786)
- In 2025, reviewers received automatic dataset metadata reports. One reviewer's account says licensing and permission status carried more weight than in prior years (single, non-official source). — [cspaper forum post](https://forum.cspaper.org/post/249)
- A study of 238 D&B dataset papers found Creative Commons licences predominant, with some papers specifying no licence for public datasets. — [arXiv 2411.00266](https://export.arxiv.org/pdf/2411.00266)

### Inferences
Reviewer expectations for the proposed benchmark, synthesised from the above plus standard practice:
1. **Hosting and metadata.** Use a persistent DOI host (Zenodo, HF Datasets, Dataverse), with a valid Croissant file (and ideally RAI fields) per sub-dataset: forecasts, observations, targets, market prices. Keep it well under the 1 TB pain point.
2. **Licence clarity per component.** Mixed sources (CC BY 4.0, US public domain, JMA PDL, SG ODL, Polymarket ToS) need a per-file licence table. If redistribution of the market data is not cleanly permitted, this is the most likely blocking issue under 2025+ scrutiny.
3. **Leakage control.** "Point-in-time" must be provable: issuance timestamps, availability lags, archived as-issued runs rather than re-fetched "historical forecast" APIs that may be stitched or re-analysed. Reviewers in this field (WB2 caveats section) watch evaluation pitfalls.
4. **Proper scoring rules and baselines.** Required scores are CRPS, Brier and log score on settlement bins, PIT/reliability, and sharpness. Baselines should include climatology, raw NWP, EMOS/DRN (EUPPBench-style), AI models, and the market.
5. **Maintenance plan.** A living leaderboard and update cadence (as with WB2's website) suit a rolling, live dataset.
6. **A scientific finding, not only data.** The "Art to Science" framing, plus the ChaosBench oral, suggest the paper needs an insight beyond the release itself (e.g., market vs AI efficiency).
- Typical rejection reasons (inferred; no official list was retrieved): inaccessible or incomplete data at review time; missing or invalid Croissant; unclear licence or terms-of-service conflicts; insufficient documentation; weak or missing baselines; small or narrow scope relative to claims; lack of novelty versus existing benchmarks; no maintenance plan.

### Gaps
- The 2026 D&B CFP and its exact text were not retrieved. Whether 2026 changed the track structure (e.g., merged reviewing or new evaluation requirements) is [UNVERIFIED].
- No official acceptance-rate statistics were retrieved for 2024–2026.
- ICLR and ICML have no dedicated D&B track. Their dataset-paper norms were not researched.

## Q3. Any benchmark with a human crowd or market baseline, or decision-relevant, settlement-exact targets?

### Takeaway
No established weather benchmark (WB/WB2/EUPPBench/ChaosBench/Weather2K/WeatherReal) uses a market or crowd baseline, or settlement-exact targets. The only precedent found is Crosier (arXiv 2609.23969, 2026), which compares Kalshi daily-high markets with NBM and European forecasts for 7 US cities, plus informal blogs.

### Cited Findings
- Crosier 2026: Kalshi market-implied distribution versus public forecasts, 7 US cities, 5 years. The market beats the final NBM by 11% in error. The market does not react to forecast updates. — [arXiv 2609.23969](https://arxiv.org/pdf/2609.23969)
- Informal Kalshi calibration studies use Brier scores, e.g., a single-city NYC analysis reports a Brier score of 0.215 against a naive 0.25. Low reliability. — [UT CS blog](https://www.cs.utexas.edu/~kavish/blog/kalshi-weather-calibration.html); [oddsreference blog](https://oddsreference.pages.dev/predictions/research/kalshi-weather-model)
- Existing benchmarks' targets are reanalysis grids (WB2, ChaosBench) or raw station variables (EUPPBench, Weather2K, WeatherReal). None is defined by contract settlement rules. — sources in Q1.

### Inferences
- "Settlement-exact" daily Tmax is an operational definition: a specific station, a specific source (e.g., NWS CLI or Weather Underground history), local-standard-time day boundaries, integer rounding, and revision rules. It differs from the "Tmax from hourly METAR" used in typical datasets. This is a genuine, defensible novelty, but it must be documented precisely with a discrepancy analysis.
- A market baseline is novel for D&B. Reviewers will ask about:
  - liquidity and thin-market noise
  - the bid/ask versus mid choice
  - converting bins to a CDF
  - the vig/overround
  - timestamp alignment with forecast availability
  - survivorship (which markets exist)
- Crosier 2026 must be cited as concurrent or prior work.

### Gaps
- Not searched: crowd baselines in other domains (Metaculus, Good Judgment) used in ML benchmarks such as ForecastBench, or Kalshi/Polymarket datasets in ML venues. Both are relevant analogues.
- Not determined: whether Crosier 2026 releases data, and whether it handles settlement-station rules.

## Q4. Licensing for redistribution

### Takeaway
ECMWF real-time data (CC BY 4.0 since Oct 2025), Open-Meteo API data (CC BY 4.0), JMA (Public Data License 1.0, CC BY 4.0 compatible) and data.gov.sg (Singapore Open Data Licence 1.0) all appear redistributable with attribution. NOAA/NWS data are generally US public domain, and IEM lists no use constraints. Polymarket's own terms could not be retrieved. Market-price redistribution is the main legal uncertainty.

### Cited Findings
- **ECMWF:** on 1 Oct 2025, ECMWF opened its entire real-time catalogue under CC BY 4.0, allowing reuse and redistribution for research and commercial purposes. Delivery of high-volume data may carry service charges. Attribution is legally required, e.g., "Adapted from ECMWF IFS 15-day Forecast Data by ECMWF, licensed under CC BY 4.0". Before that, the open subset (IFS and AIFS) was CC BY 4.0 plus ECMWF Terms of Use. — [ECMWF open data](https://www.ecmwf.int/en/forecasts/datasets/open-data); [Meteorological Technology International](https://www.meteorologicaltechnologyinternational.com/news/data/ecmwf-opens-its-real-time-catalog-to-all-advancing-international-collaboration.html); [EurekAlert release](https://www.eurekalert.org/news-releases/1100113); [AWS registry](https://registry.opendata.aws/ecmwf-forecasts/)
- **Open-Meteo:** API data are offered under CC BY 4.0, with credit, a link to the licence and an indication of changes required, and no implied endorsement. The source code is AGPLv3. The homepage says data can be shared and adapted "even for commercial purposes". An older third-party README says to contact them for commercial API use (commercial API access is a separate paid tier, distinct from the data licence). The suggested citation is Zippenfenig, P. (2023), Open-Meteo.com Weather API, Zenodo, doi:10.5281/ZENODO.7970649. — [Open-Meteo licence (snippet)](https://open-meteo.com/en/licence); [Open-Meteo home](https://open-meteo.com/)
  - Caveat (inference): Open-Meteo aggregates national models (DWD, NOAA, Météo-France, JMA, etc.). The upstream licences still apply in principle, and its "historical forecast" archive may not be strictly point-in-time. Verify against [open-meteo.com/en/license](https://open-meteo.com/en/license) (data sources page).
- **NOAA/NWS:** NCEI states its data are in the public domain in the US, and NODD distributes them at no charge. Some NCEP/MADIS feeds are restricted; mesonet redistribution terms are set by each provider. — [NCEI open data policy PDF](https://www.ncei.noaa.gov/sites/default/files/2023-12/NCEI%20PD-10-2-02%20-%20Open%20Data%20Policy%20Signed.pdf); [NCEP restricted data](https://www.nco.ncep.noaa.gov/pmb/docs/restricted_data/); [MADIS restrictions](https://madis.ncep.noaa.gov/madis_restrictions.shtml)
- **IEM (Iowa Environmental Mesonet) ASOS/METAR:** the UCAR/EOL catalogue lists use constraints as "none". Suggested citation: Todey & Herzmann (2007), Iowa Mesonet Data. The IEM's own disclaimer was not retrieved. — [UCAR data record](https://data.ucar.edu/dataset/iowa-mesonet-data); [EOL record](https://data.eol.ucar.edu/dataset/114.180)
- **JMA:** website content is usable under the Public Data License (Version 1.0) unless otherwise indicated. It is compatible with CC BY 4.0 and may be used under CC BY instead. Logos and symbols are excluded. — [JMA copyright page](https://www.jma.go.jp/jma/en/copyright.html)
- **data.gov.sg:** Singapore Open Data Licence v1.0 permits use, copying, distribution, modification and adaptation, commercial or non-commercial, without implying endorsement. NEA weather datasets are listed under it. ASMC/MSS content has stricter, non-commercial terms. — [datagovsg blog](https://medium.com/datagovsg-blog/making-open-data-more-open-the-new-open-data-licence-and-api-terms-of-service-d310a4c5cdf0); [data.gov.sg historical daily weather](https://data.gov.sg/dataset/historical-daily-weather); [ASMC terms](https://asmc.asean.org/terms-of-use/)
- **Polymarket:** the official ToS could not be fetched (polymarket.com blocked) or found via search.
  - A secondhand source says the ToS bars US persons and some other jurisdictions from *trading*, including via API, while data are viewable globally. — [sourcepulse page on Polymarket agents](https://www.sourcepulse.org/projects/972586)
  - Third-party aggregators (Oddpool, Prediction Hunt) prohibit redistributing *their* data and require compliance with source-platform terms. — [Oddpool terms](https://oddpool.com/terms); [Prediction Hunt terms](https://www.predictionhunt.com/terms-of-service)
  - The API consists of Gamma (market metadata), CLOB (order book/prices) and Data API services (per a Medium overview, not official). — [Medium](https://medium.com/@gwrx2005/the-polymarket-api-architecture-endpoints-and-use-cases-f1d88fa6c1bf)

### Inferences
- Safest design for market data:
  - Release derived, aggregated series (e.g., hourly mid-price implied probabilities per bin) plus scripts to re-fetch raw data from public APIs.
  - Note that on-chain trade data (Polygon) are publicly verifiable, which strengthens a fair-use or factual-data argument. [UNVERIFIED legal reasoning; consult the actual ToS.]
  - Avoid redistributing Polymarket-branded content.
- Settlement sources (e.g., Weather Underground station history, used by many Polymarket weather markets) may carry their own restrictive terms. [UNVERIFIED; not searched.] Prefer to release NOAA/IEM equivalents and document any discrepancy.
- Add a per-component licence table and, in Croissant, `license` fields per distribution. This responds directly to the 2025 D&B licensing scrutiny.

### Gaps
- Polymarket ToS and API terms text (blocked). Kalshi's data terms were not checked.
- Not checked: the Open-Meteo per-source licence page and whether its Historical Forecast API is point-in-time.
- Not checked: terms for other national services the ~53 airports may need, e.g., UK Met Office, KMA, CMA, Environment Canada, BoM, and Weather Underground.
