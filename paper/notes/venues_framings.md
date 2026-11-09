# Publication venues and framings for "Polymarket daily temperature markets vs NWP/AI forecasts" (independent author)

Research date: 2026-11-06. Network note: arxiv.org, info.arxiv.org, jmlr.org and climatechange.ai could not be fetched from this session (DNS blocked), so their content below comes from search snippets, not full pages. Dates are approximate; check them before relying on them.

**Most important novelty finding (relevant to every venue choice):** there is a recent closely related preprint, Alexander W. Crosier, "Prediction Markets Beat the Weather Forecast on Tomorrow's High Temperature" (arXiv 2609.23969, about Sept 2026). It uses five years of **Kalshi** data for 7 US cities and builds an hourly market-implied forecast of the next-day high. It reports that the market beats NBM in 6 of 7 cities, by about 10% RMSE at the end of the first trading hour. It also argues that public forecasts "slowly publish information the market had already reflected" and that the market does not react to forecast updates — [arXiv abs](https://arxiv.org/abs/2609.23969); [Prediction News coverage](https://predictionnews.com/story/study-finds-kalshi-weather-markets-outperform-public-meteorologists); [FOW](https://www.fow.com/insights/kalshi-prediction-markets-beat-public-weather-forecasts-study-finds). Any framing has to position against this paper: Polymarket rather than Kalshi, settlement-exact data, AI models (GraphCast/AIFS-type) and not only NBM, and information-latency methods. A finding that the market lags the forecasts would directly contradict Crosier, which would itself be an interesting result.

## 1. ML workshops and conference tracks (format, archival status, acceptance, deadlines)

### Takeaway
Two venues are the realistic first entry points for this work. The CCAI "Tackling Climate Change with ML" workshop is non-archival, takes 4-page papers and runs mentorship, but it requires a climate-impact argument, which is only a loose fit for temperature-market efficiency. ICAIF (ACM AI in Finance) is archival, its deadline is around August and it requires in-person attendance. The NeurIPS Evaluations & Datasets track (renamed from Datasets & Benchmarks in 2026) is main-conference tier (about 25% acceptance) and requires Croissant metadata plus public data and code. ICBINB is a good fit for negative results, but its 2026 edition was LLM-themed.

### Cited Findings
**CCAI "Tackling Climate Change with ML" workshop**
- NeurIPS 2026 edition: the submission deadline was Aug 29, 2026 AoE, decisions came Sept 29, 2026, and the workshop runs Dec 11/12, 2026 in Sydney. The theme is "Fostering Ground-Up Innovation in AI and Climate". It has a Papers track (work that is in progress, published or deployed), a Proposals track and a Tutorials track. It moved to OpenReview for the first time, and submissions must explain their positive climate impact — [CCAI NeurIPS 2026 page](https://www.climatechange.ai/events/neurips2026); [NeurIPS virtual listing](https://neurips.cc/virtual/2026/workshop/137516) (from search snippets)
- Past format: papers of up to 4 pages excluding references and appendix, proposals of up to 3 pages. Contributions are **non-archival**, so the work can be published later. Papers "need not contain complex ML if the application is compelling" — [CCAI NeurIPS 2022 blog](https://climatechange.ai/blog/2022-09-12-neurips-22); [ICML 2021 CFP](https://groups.google.com/g/openmod-initiative/c/E_oZLBirB5c)
- The series has run at ICLR in the past (e.g. ICLR 2025), so the cadence is roughly two editions a year, one at ICLR or ICML in spring and one at NeurIPS in December — [CCAI ICLR 2025](https://climatechange.ai/events/iclr2025)
- A Cambridge *Environmental Data Science* special collection on "Tackling Climate Change with ML" offers an archival route after the workshop — [Cambridge EDS collection](https://www.cambridge.org/core/journals/environmental-data-science/special-collections/tackling-climate-change-with-machine-learning)
- No acceptance-rate statistics were found for any edition.

**ICAIF (ACM International Conference on AI in Finance)**
- ICAIF 2026 (7th edition) is in Milan, Nov 14–17, 2026. Papers were due Aug 2, 2026 AoE and notification was Sept 27, 2026. It is in-person only, and at least one author must present — [aifin-worldwide mailing list](https://groups.google.com/g/aifin-worldwide/c/zh7y9B-Gw-4); [PaperPilot](https://www.getpaperpilot.com/deadlines/icaif-2026.html) (the official icaif2026.org page was not retrieved)
- ICAIF'25 was in Singapore, Nov 15–18, 2025. Its deadline moved from July 18 to Aug 3, 2025. Organizers state: "ICAIF is an archival peer-reviewed conference, so please do not submit working papers to the main conference" — [CFP extension](https://groups.google.com/g/aifin-worldwide/c/dY48xjkNjaI); [3rd call](https://groups.google.com/g/aifin-worldwide/c/TWcQJmcEX94)
- ICAIF also hosts satellite workshops, e.g. an AI-Quant workshop at ICAIF'25, which are lower-barrier entry points — [ICAIF25 AIQuant workshop](https://cspun.github.io/ICAIF25-AIQuant)
- No ICAIF acceptance rate was found (gap). There are also finance workshops at ICLR, e.g. an ICLR 2026 FinAI workshop — [ICLR 2026 FinAI CFP](https://sites.google.com/view/iclr2026finai/call-for-papers)

**NeurIPS Evaluations & Datasets track (formerly Datasets & Benchmarks)**
- For 2026 the track was renamed Evaluations & Datasets and broadened so that evaluation itself counts as an object of study. Review is meant to be as stringent as the main track, and the track follows main-track requirements and timelines. Full papers were due May 6, 2026 and notification was Sept 24, 2026. Datasets must be documented in **Croissant** format, and code and data must be public by camera-ready — [NeurIPS 2026 E&D CFP](https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets)
- The 2024 D&B acceptance rate was 25.3%, against 25.8% for the main track. The 2025 track received 1,995 submissions (rate not found) — [NeurIPS blog: 2025 D&B review reflections](https://blog.neurips.cc/2025/09/30/reflecting-on-the-2025-review-process-from-the-datasets-and-benchmarks-chairs/); [NeurIPS blog, Dec 2025](https://blog.neurips.cc/2025/12/05/neurips-datasets-benchmarks-track-from-art-to-science-in-ai-evaluations/)
- The NeurIPS main-track page limit is about 9 pages (from memory, not verified this session).

**ICBINB ("I Can't Believe It's Not Better")**
- The 2026 edition was at ICLR 2026 (Rio), themed "Where Large Language Models Need to Improve" and focused on negative results and limitations of LLMs. The deadline was Jan 31, 2026, notification Mar 1 and camera-ready Mar 8. A 2-page "tiny paper" type was offered — [ICBINB 2026 submit page](https://sites.google.com/view/icbinb-2026/submit); [ML-news CFP](https://groups.google.com/g/ML-news/c/ZOPDi5FT39M)
- Earlier editions (NeurIPS 2020, 2021) had broader themes ("beautiful ideas that should have worked") — [ICBINB NeurIPS 2020 CFP](https://i-cant-believe-its-not-better.github.io/neurips2020/cfp)
- No call for a later 2026 or 2027 edition was found (gap).

### Inferences
- The 2026 deadlines for CCAI (Aug), ICAIF (Aug) and NeurIPS E&D (May) have all passed. The realistic next windows are about Jan–Feb 2027 for ICLR 2027 workshops (CCAI, finance, possibly ICBINB), about May 2027 for NeurIPS 2027 E&D, about Aug 2027 for ICAIF 2027 and CCAI@NeurIPS 2027. These are extrapolated from past cadence and should be treated as uncertain.
- Fit by framing:
  - "Market vs AI/NWP forecasts" as a forecasting benchmark suits CCAI (pitched as weather-risk pricing or adaptation information, though this is weak on climate) or a forecasting workshop.
  - "Market efficiency and latency" suits ICAIF or a finance workshop.
  - "Settlement-exact dataset plus evaluation protocol" suits NeurIPS E&D (Croissant metadata and a public repository required).
  - "AI weather models do not beat the market" or "no exploitable edge" suits ICBINB if a non-LLM edition reappears, or TMLR.
- Workshops are good places to get feedback because they are non-archival (CCAI) and do not block a later journal submission. ICAIF main-track papers are archival, which may conflict with a later journal version.
- ICAIF's in-person requirement (Milan in 2026) means real travel cost for a self-funded author.

### Gaps
- Acceptance rates for CCAI, ICAIF and ICBINB were not found.
- The exact 2027 dates are not yet announced.
- Whether CCAI reviewers accept weather-market efficiency as climate-relevant is a judgement call; it was not verified.

## 2. Journals: scope fit, review times, costs

### Takeaway
The International Journal of Forecasting (IJF) is the strongest scope fit: it covers forecast evaluation and prediction markets, and it has run a prediction-markets special issue. Its review is slow and acceptance requires passing a reproducibility check. The AMS journals (Weather and Forecasting, MWR, BAMS) fit a meteorology-audience framing, but Weather and Forecasting charges about $120 per typeset page (waivable) plus $1,300 for open access. RMetS's *Meteorological Applications* is fully open access (APC), double-blind and explicitly user- and verification-oriented, which is a natural home. The Journal of Prediction Markets appears inactive after 2015.

### Cited Findings
- **IJF:** acceptance is "conditioned to passing a reproducibility check" led by the Editor-in-Chief. The journal points to its annual reports for submission times — [IJF site](https://ijf.forecasters.org); [forecasters.org/ijf](https://forecasters.org/ijf/). An aggregator lists review time as about 296 days (unverified, field undefined) — [PJIP profile](https://www.pjip.org/journal/1001169/International%20Journal%20of%20Forecasting). IJF ran a special issue on prediction markets (call from 2016) — [IIF blog](https://forecasters.org/blog/2016/12/17/ijf-special-issue-prediction-markets)
- **Weather and Forecasting (AMS):** a hybrid journal charging about $120 per typeset page. Page charges can be waived, but the $1,300 Open Choice fee cannot. Read-and-publish deals apply only through institutions — [AMS page charges](https://www.ametsoc.org/ams/publications/author-information/page-charges-waivers-and-fees/); [AMS waivers](https://www.ametsoc.org/AMS/publications/author-information/page-charges-waivers-and-fees/page-charge-waivers/); [AMS open access](https://www.ametsoc.org/ams/publications/ethical-guidelines-and-ams-policies/open-access-for-ams-journals-and-bams/). The 2026 fee level is not confirmed.
- **Meteorological Applications (RMetS/Wiley):** fully open access (since about 2019/2020), double-blind review. Its scope covers "all applications of meteorology … including observation, prediction, data assimilation and verification", and its readership includes users of met services in energy, transport and similar sectors. It ran a forecast-verification virtual issue driven by questions from "modellers, forecasters or customers" — [RMetS journal page](https://www.rmets.org/publication/meteorological-applications); [Charlton-Perez & Zardi 2020 editorial](https://iris.unitn.it/retrieve/e3835196-74df-72ef-e053-3705fe0ad821/Charlton-Perez%20and%20Zardi%20Met%20Apps%202020%20Meteorology%20applications.pdf). The current APC amount was not found; waivers depend on country.
- **Journal of Prediction Markets (Univ. of Buckingham Press):** RePEc indexes issues from 2007 to 2015 only, edited by Leighton Vaughan Williams. Its current status is unclear and it is probably dormant — [EconPapers](https://econpapers.repec.org/article/bucjpredm/default1.htm)
- **ML-for-weather journal precedent:** WeatherBench 2, a benchmark of data-driven weather models, was published in AGU's *JAMES* (2024, DOI 10.1029/2023MS004019). Benchmark-style ML-vs-operational papers are therefore accepted in geoscience journals — [AGU Eos highlight](https://eos.org/editor-highlights/machine-learning-masters-weather-prediction); [arXiv 2308.15560](https://arxiv.org/abs/2308.15560)
- Not researched this session (scope from general knowledge, unverified): QJRMS (RMetS flagship, more dynamical and methodological), Monthly Weather Review (more on modelling and data assimilation), BAMS (wide audience, "essay"-style articles suit a short "markets as a forecast-verification signal" piece), Quantitative Finance (mathematical finance, weaker fit). Other candidates worth checking are *Artificial Intelligence for the Earth Systems* (AMS, ML-focused) and *Journal of Forecasting* (Wiley).

### Inferences
- Best journal per framing:
  - Forecast-evaluation and market-efficiency paper: IJF.
  - "What markets tell meteorologists about forecast value and latency": Meteorological Applications or Weather and Forecasting (W&F costs money).
  - ML-model comparison: AMS AI for the Earth Systems (AIES) or JAMES.
  - Short provocative piece: BAMS.
- IJF's reproducibility check works in the author's favour, because the study's selling point is a settlement-exact, reproducible dataset.

### Gaps
- Current review times for IJF, W&F, MWR, QJRMS and Met Apps were not obtained from primary sources.
- APC amounts for Met Apps and the AIES fees were not found.

## 3. arXiv: categories and endorsement for a first-time author without institutional email

### Takeaway
Since 21 Jan 2026, arXiv requires **every first-time submitter in a section to be personally endorsed by an established author in that field**. An institutional email no longer qualifies on its own, so an independent author needs an endorser. Posting through HAL is reported to bypass endorsement. Plausible categories are q-fin.ST or q-fin.TR as primary, with stat.AP, physics.ao-ph and cs.LG as cross-lists.

### Cited Findings
- Mathematics section, Dec 10, 2025: an institutional email is no longer sufficient for automatic endorsement; new submitters need an institutional email plus prior authorship in arXiv math, or a personal endorsement — [arXiv blog](https://blog.arxiv.org/arxiv/2025/12/10/updated-endorsement-policy-for-arxiv-mathematics)
- All sections, Jan 21, 2026: first-time posters must be endorsed by an established arXiv author in their field. Authors who have already posted in the same section are exempt — [CASRAI news](https://casrai.org/news/arxiv-2026-endorsement-english-ai-policy-changes); [CCSD/HAL note](https://www.ccsd.cnrs.fr/?p=18532) (secondary sources; the official arXiv policy page could not be fetched)
- HAL deposit with transfer to arXiv reportedly does not require endorsement even for a first submission, and the HAL–arXiv agreement is unaffected by the change — [CCSD](https://www.ccsd.cnrs.fr/?p=18532) (verify)
- Secondary sources also report a 2026 arXiv policy of one-year bans for fully AI-written submissions — [NewsBytes](https://www.newsbytesapp.com/news/science/ai-generated-papers-could-lead-to-year-long-ban-on-arxiv/story) (unverified)
- q-fin.TR (Trading and Market Microstructure) listings include market-making, execution and volatility-forecasting papers. q-fin.ST (Statistical Finance) is used for empirical and stylized-facts work, often cross-listed with TR — [q-fin.TR listing](https://arxiv.org/list/q-fin.TR/2025-11) (formal definitions not retrieved)
- Precedent: the Crosier weather-market paper and other prediction-market papers are on arXiv (e.g. 2609.23969; 2602.19520 on calibration; 2606.04217 on Polymarket microstructure) — [arXiv 2609.23969](https://arxiv.org/abs/2609.23969); [alphaxiv 2602.19520](https://www.alphaxiv.org/abs/2602.19520); [arXiv 2606.04217](https://arxiv.org/html/2606.04217v1)

### Inferences
- Endorsement is per section, so endorsement in q-fin does not cover physics.ao-ph as a primary category. Cross-lists normally do not need separate endorsement (standard arXiv practice from memory; verify). A good strategy is one primary category (q-fin.ST, or stat.AP) with cross-lists.
- Practical routes to an endorser: authors of related work (Crosier; the Polymarket calibration and arbitrage authors), workshop co-authors or mentors (CCAI runs mentorship), or HAL deposit.
- An alternative is to accept a non-arXiv preprint (SSRN for the finance framing, ESS Open Archive for geoscience, or OpenReview through TMLR, where the paper is public under review).

### Gaps
- The official arXiv endorsement page text could not be fetched (arxiv.org is blocked here).
- The exact rules for cross-list endorsement after the 2026 change are unconfirmed.

## 4. Independent-researcher considerations (TMLR, affiliation, cost, entry points)

### Takeaway
TMLR is the best-matched archival ML venue for an unaffiliated author. It is free, rolling, runs on OpenReview, and judges whether claims are supported by evidence and of interest to some audience, explicitly not novelty. Recent median turnaround is about 3–4 months rather than the advertised 2. Workshops (non-archival, often with virtual or mentorship options) are the cheapest entry. Conferences with mandatory in-person presentation (ICAIF) and AMS page charges are real costs.

### Cited Findings
- TMLR's two criteria are: (1) the claims are supported by accurate, convincing evidence (the most important criterion), and (2) some part of the TMLR audience would be interested. The editors deliberately avoid "significant/impactful/novel", and method novelty is not required — [TMLR acceptance criteria](https://www.jmlr.org/tmlr/acceptance-criteria.html); [launch announcement](https://medium.com/@hugo_larochelle_65309/announcing-the-transactions-on-machine-learning-research-3ea6101c936f)
- There is no length limit, but papers with more than 12 pages of main text lose the short review timeline. The original goal was reviews within 4 weeks and a decision within 2 months. Reported medians are 97 days for conference-length papers and 113 days for long papers (2024) — [TMLR FAQ](https://jmlr.org/tmlr/faq.html); [author guide](https://jmlr.org/tmlr/author-guide.html) (median figures come from a TMLR report via search snippet)
- TMLR charges no fees. Review and publication run on OpenReview with anonymized submissions, and all authors need OpenReview profiles with conflict-of-interest information — [TMLR submissions](https://jmlr.org/tmlr/submissions.html); [editorial policies](https://jmlr.csail.mit.edu/tmlr/editorial-policies)
- CCAI workshop papers are non-archival and can be work in progress — [CCAI 2022 blog](https://climatechange.ai/blog/2022-09-12-neurips-22)
- ICAIF requires at least one author to present in person — [aifin-worldwide](https://groups.google.com/g/aifin-worldwide/c/zh7y9B-Gw-4)
- AMS page charges (about $120 per page) can be waived. Open Choice ($1,300) cannot — [AMS waivers](https://www.ametsoc.org/AMS/publications/author-information/page-charges-waivers-and-fees/page-charge-waivers/)

### Inferences
- Affiliation: OpenReview and most venues accept "Independent Researcher" as an affiliation. OpenReview profiles without an institutional email may face slower moderation (from general knowledge; unverified).
- A sensible sequence for building an academic track record:
  1. Workshop paper (CCAI or a finance workshop at ICLR 2027) for feedback and visibility.
  2. Full version to TMLR (free, open reviews visible to future employers) or IJF (forecasting community).
  3. Dataset release with Croissant metadata, possibly for NeurIPS 2027 E&D.
- TMLR accepted papers can be presented at ICLR, NeurIPS and ICML through the journal-to-conference track (from memory; verify), which gives conference visibility without conference-acceptance odds.

### Gaps
- No source specifically on independent-author eligibility or treatment at TMLR or the workshops.
- Registration fees and travel grants for 2027 venues were not researched.

## 5. Examples of similar accepted papers (benchmarks vs crowds/markets/operational forecasts; negative results)

### Takeaway
Close precedents exist and mostly sit at top ML venues or on arXiv:
- ForecastBench (ICLR 2025): ML vs crowds and superforecasters, a negative result for LLMs.
- WeatherBench 2 (JAMES 2024): ML vs operational NWP.
- Polymarket calibration and arbitrage studies (AFT 2025, arXiv).
- Crosier 2026: Kalshi temperature markets vs NBM, the direct competitor.

### Cited Findings
- **ForecastBench** (Karger et al., ICLR 2025): a dynamic benchmark of about 1,000 questions. Expert forecasters beat the best LLM (p < 0.001). On a 200-question subset the Brier scores were 0.093 for superforecasters, 0.107 for the public and 0.111 for the best LLM. Giving LLMs crowd/market forecasts improved them. This is an accepted main-conference benchmark whose headline is essentially a negative result for ML — [ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ea74e45a229dac70b5b63b28d8934db6-Abstract-Conference.html)
- **WeatherBench 2** (Rasp et al., JAMES 2024; Google Research, DeepMind and ECMWF): an evaluation framework and leaderboard comparing data-driven models with operational IFS — [Eos](https://eos.org/editor-highlights/machine-learning-masters-weather-prediction); [Google Research blog](https://www.research.google/blog/weatherbench-2-a-benchmark-for-the-next-generation-of-data-driven-weather-models/)
- **"Unravelling the Probabilistic Forest"** (AFT 2025, LIPIcs): presented as the first large-scale analysis of arbitrage on Polymarket, separating market-rebalancing from combinatorial arbitrage. This shows that crypto and economics venues such as AFT (Advances in Financial Technologies) publish Polymarket empirics — [LIPIcs AFT 2025](https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/html/LIPIcs.AFT.2025.27/LIPIcs.AFT.2025.27.html)
- **"Decomposing Crowd Wisdom"** (arXiv 2602.19520): calibration by domain, horizon and trade size. Political markets are underconfident, and the pattern replicates on Polymarket. Trade counts differ between abstract versions — [alphaxiv](https://www.alphaxiv.org/abs/2602.19520)
- **Polymarket microstructure** (arXiv 2606.04217): 1.2B trades, trade-classification accuracy — [arXiv HTML](https://arxiv.org/html/2606.04217v1)
- **Whelan et al., "Makers or Takers: The Economics of the Kalshi Prediction Market"** (GWU working paper 2026-001): Kalshi economics including short-lived temperature markets — [GWU WP](https://www2.gwu.edu/~forcpgm/2026-001.pdf); [karlwhelan.com](https://www.karlwhelan.com/Papers/Kalshi.pdf)
- **Crosier (2026)**, Kalshi temperature vs NBM, an unrefereed preprint — [arXiv 2609.23969](https://arxiv.org/abs/2609.23969)
- **A Princeton senior thesis** (Apr 2026) on Polymarket calibration across 188,509 markets shows the topic is popular at student level — [Princeton](https://theses-dissertations.princeton.edu/entities/publication/d5708372-5ea3-4252-b669-7f9cee07387c)

### Inferences
- Reviewers at ML venues will expect:
  - strong baselines (NBM/MOS, ECMWF ENS, GraphCast/AIFS-type AI models, bias-corrected versions);
  - proper scores (CRPS, Brier or log score on bins, reliability diagrams);
  - significance testing (Diebold–Mariano, block bootstrap over city-days);
  - leakage-free timing alignment (forecast issue and availability time versus market timestamp), which is the core of an "information latency" claim;
  - transaction-cost and fee-aware efficiency tests;
  - a public dataset and code.
  Meteorology reviewers will also ask about station versus grid representativeness and the exact settlement source (e.g. NWS CLI reports or the station Polymarket uses).
- A negative result (AI or NWP forecasts give no tradable edge after costs, or markets already embed the forecasts) is publishable at TMLR and IJF if it is rigorous. ForecastBench shows that "ML does not beat the crowd" headlines are acceptable at top venues.
- Because Crosier has priority on "markets beat NBM", the strongest novelty lies in: Polymarket specifically; settlement-exact reconstruction; AI models; latency measured at the timing of forecast releases (does the market move when a model run is published?); and possibly replicating or contesting Crosier's "market doesn't react to forecast updates" finding.

### Gaps
- Whether Crosier's paper has been submitted to a venue is unknown.
- No accepted paper specifically on Polymarket weather markets was found.

## 6. Ethical and financial-conflict considerations for trading-relevant findings

### Takeaway
No venue-specific rule on trading positions was found. Standard journal conflict-of-interest policies require disclosing financial interests, so an author who trades these markets should disclose this explicitly in the paper. Publishing a working edge will likely erase it (alpha decay), and reviewers may question the motives behind the paper if positions are not disclosed.

### Cited Findings
- About 80% of 49 surveyed journals had a conflict-of-interest policy, but more than half gave no definition — [comparison of COI policies](https://typeset.io/pdf/a-comparison-of-conflict-of-interest-policies-at-peer-2ysogj5opv.pdf)
- Disclosure windows vary: some apply at submission, others from the start of the study; one model policy covers any financial relationship in the previous 3 years — [PMC COI policy analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC5913791/table/Tab6); [Research Information](https://www.researchinformation.info/node/13310)
- TMLR requires conflict-of-interest information on every author's OpenReview profile (this covers reviewer conflicts, not finances) — [TMLR author guide](https://jmlr.org/tmlr/author-guide.html)

### Inferences
- Recommended practice:
  - Include a "Competing interests / Financial disclosure" statement saying whether the author held or traded positions in the studied markets during or after the sample, and whether they plan to trade.
  - Report efficiency results with realistic costs (fees, spread, slippage, depth) so that claimed edges are not overstated.
  - Use a hold-out period that ends before publication.
  - Consider describing aggregate inefficiency without releasing a turnkey live strategy.
  - Note Polymarket's legal and jurisdictional status (access restrictions for US users historically) as context. This is from general knowledge and was not verified here.
- The American Finance Association (AFA) and the *Journal of Finance* have explicit disclosure policies for financial interests, which can serve as a template. This is from memory and was not verified this session.
- Do not use any trading capital or insider-style information (e.g. early access to settlement data) in a way that could appear manipulative. Describe data provenance (public APIs, on-chain data).

### Gaps
- No primary source was found on norms for "not publishing alpha" or on disclosure policies specific to prediction-market research.
- Polymarket's terms of service on data redistribution, which matters for releasing the dataset, were not checked.
