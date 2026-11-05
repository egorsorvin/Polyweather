# Practitioner Knowledge: Trading Daily Temperature Markets on Polymarket and Kalshi (2024–2026)

Research date: 2026-11-05. Method note: web search worked, but the sandbox blocked direct fetches of medium.com, x.com, substack, docs.polymarket.com, help.kalshi.com, wethr.net, krypton.bot and kucoin.com. Claims from those domains come from search-result summaries and snippets, not full-page reads, so they are lower confidence. GitHub pages were read in full. No Reddit threads came up in searches (r/Kalshi, r/Polymarket, r/algotrading), so Reddit practitioner opinion is a gap.

## 1. Which strategies do practitioners use and claim work?

### Takeaway
The dominant public "strategy" is model-vs-market divergence: compare NWP or ensemble probabilities with bracket prices and buy what is underpriced. The best-documented independent evidence (open-source backtests and post-mortems from 2026) says naive model-vs-market no longer has an edge, because the market already beats raw models. What survives in the evidence: blending the market price with a bias-corrected model, possibly selling overpriced tails a day out, and the cheap-tail ladder style tied to top wallet gopfan2. All the rest is mostly vendor marketing.

### Cited Findings
**Model-vs-market divergence (the standard pitch)**
- Most viral bot write-ups describe comparing forecast probability with market probability and buying when they diverge. One open-source bot uses the 31-member GFS ensemble and trades when edge exceeds 8%. Its own header claims "Highest profits $1.8k" — [suislanchez/polymarket-kalshi-weather-bot](https://github.com/suislanchez/polymarket-kalshi-weather-bot)
- A viral X pitch frames it as "Weather models update constantly. Prediction markets update slowly." It claims $80,749 profit over 4,137 predictions, about $19.52 per trade, and the post discloses a paid partnership — [Kirill on X](https://x.com/kirillk_web3/status/2036142991899754829)
- Guides say the order book between official model runs "often reflects stale probabilities based on the previous model cycle." They suggest trading 12Z GFS/ECMWF shifts, e.g. "if the GFS 12Z run is 3 degrees warmer than the 06Z run, and the ECMWF 12Z confirms…". These are affiliate-style guides, not verified — [tradetheoutcome](https://www.tradetheoutcome.com/polymarket-weather-strategy/); [turbinefi](https://www.turbinefi.com/blog/how-to-trade-kalshi-weather-markets-2026)
- Model timing: HRRR, RAP and NBM run hourly, while GFS, NAM and ECMWF run on 6-hour cycles. NBM data lands about 2 hours after the run starts — [wethr.net model schedule](https://wethr.net/model-schedule). One guide warns that NBM's max-temperature window is not the calendar day the contract settles on, so traders have to align them — [turbinefi](https://www.turbinefi.com/blog/how-to-trade-kalshi-weather-markets-2026)

**Rigorous independent evidence (Kalshi, 2022-12 to 2026-10)**
- Data: 12,765 events and 447,818 snapshots. The model uses NWS MOS/NBM, plus LightGBM correcting with global models, station observations and the market-implied mean. 2026 out-of-sample MAE for the evening high fell from 1.85 to 1.68°F — [Deivid-Negoita/kalshi-weather](https://github.com/Deivid-Negoita/kalshi-weather)
- Results: the model alone made +2.9¢, +3.0¢ and +1.3¢ per contract on evening highs in 2023, 2024 and 2025, then lost 1.5¢ in 2026. A market+model blend made +3.2¢ (t 4.3) on evening highs and +4.1¢ (t 4.9) on evening lows out of sample in 2026 — [same](https://github.com/Deivid-Negoita/kalshi-weather)
- Paper trading from 16 to 26 Oct 2026: 83 trades lost $19.88 on $121.88 staked (−16.3%), and $4.45 of that was fees. Highs lost 30.6% and lows made 11.8%. The author turned highs off on 26 Oct — [same](https://github.com/Deivid-Negoita/kalshi-weather)
- Tails: the market "prices too wide until the final hours." The realized/implied SD ratio was about 0.94 at 30 h, 0.86–0.88 at 8–10 h, and about 1.02 in the last 6 h. Both tails are overpriced a day out, which points to selling wings at roughly 1–2¢ per contract after costs. The author says this "needs a walk-forward test" — [same](https://github.com/Deivid-Negoita/kalshi-weather)

**Polymarket post-mortems (2026)**
- jattree/weather-edge used a multi-model consensus bias-corrected against METAR. A live run went from $210 to $51.61 (−75.4%), mostly because of bugs. After the fixes, a September 2026 evaluation over 697 events found the market's probabilities scored better than the model. Simulated trades at market prices with a 1¢ half-spread plus taker fee lost 13.9% ± 5.3% per trade over 1,905 trades. The market-implied temperature was about 0.2°C from the observed value, versus about 0.8°C for raw models. Conclusion: "the model had no edge" — [jattree/weather-edge](https://github.com/jattree/weather-edge)
- BallesJr/polymarket-weather-edge buys NO at T+0 using live METAR plus a Gaussian model. Filters are a NO price of 0.15–0.40 and edge of at least 0.25, with half-Kelly sizing capped at $5. Paper results: 2026-06-10 to 07-10, 527 trades, +$157. 2026-07-10 to 08-12, 847 trades, −$592, with a 28.9% win rate against a 31.3% break-even (t = −2.79). Total PnL was −$1,196 on $10k. The author says the early edge "has not held out of sample" and suspects heat-wave tails. NO entries priced below 0.10 won about 0% of the time, which the author reads as adverse selection — [BallesJr/polymarket-weather-edge](https://github.com/BallesJr/polymarket-weather-edge)

**Cheap tails and ladders (the gopfan2 style)**
- gopfan2 reportedly bought YES under $0.15 and NO above $0.45, risking about $1 per position over thousands of trades. Guides argue that markets overprice the modal bucket and underprice adjacent ones. These rules are secondhand, mostly from bot-marketing posts — [search summary of guides incl. laikalabs](https://laikalabs.ai/prediction-markets/trade-polymarket-weather-markets); [0xMovez on X (bot promo "trained on gopfan2's +$2M weather trading strategy")](https://x.com/0xMovez/status/2019532692065243484)
- neobrother is described as running systematic temperature-ladder bets across cities — [KuCoin flash news](https://www.kucoin.com/news/flash/traders-on-polymarket-earn-millions-by-predicting-weather)

**METAR and intraday nowcasting, plus Kalshi "bots" (data-release products)**
- wethr.net's guide on "market bots" covers DSM, OMO, 6-Hour, CLI and "240" bots in Kalshi and Polymarket weather markets. These are alerting bots tied to specific NWS data releases. The 6-Hour bot tracks the 6-hour max, which can include 1-minute observations missing from the 5-minute series — [wethr.net market-bots](https://wethr.net/edu/market-bots)
- Knowing whether the daily high has already passed is described as central to late-day pricing — [MEXC news summary](https://www.mexc.com/tr-CT/news/954544)

**Market making and liquidity rewards** — see section 5.

### Inferences
- The two most careful public datasets, Kalshi 2022–2026 and Polymarket 2026, agree. Raw or bias-corrected NWP no longer beats the market price on its own. The edge from 2023–2025 shrank as spreads compressed. What remains is small (a few cents per contract), regime-dependent, and needs the market price as an input.
- Overpriced tails a day out (Kalshi) fit the "sell longshots / buy NO" approach, but the BallesJr results show heat-wave regimes can wipe that out. Buying very cheap NO (below 0.10) looks like adverse selection.
- I found no rigorous public evidence that "buy cheap tails" is profitable. Its credibility rests on gopfan2's leaderboard PnL, and his actual rules are known only secondhand.

### Gaps
- No Reddit or YouTube practitioner content could be read. A YouTube video titled "How Trading Bots Make $10K+ Monthly Predicting the Weather on Polymarket" exists but was not reviewed ([YouTube](https://www.youtube.com/watch?v=86xl8sINErw)).
- The polydao "Complete guide to trading weather markets like a quant" (X article) could not be read ([x.com](https://x.com/polydao/article/2041113454023475370)).
- I found no quantitative evidence for an edge from waiting for 00z/12z runs.

## 2. Evidence of profitability; top weather traders

### Takeaway
Polymarket's official weather-category leaderboard is the only semi-verified source. It shows gopfan2 (about $317K all-time weather profit) and aenews2 (about $285.7K) at the top. aenews says the two are linked or cooperating and that other top-10 accounts copy them. Viral bot wallets (around $80–88K) are real accounts but have low win rates and concentrated wins. Vendor claims (WeatherBot "$700 to $85,000", "18–48% margins in 24h") are unverified marketing.

### Cited Findings
- Polymarket's weather leaderboard (all-time profit) has gopfan2 at #1 with about $317K. The Krypton tracker shows the same about $317.2K, with aenews2 #2 at about $285.7K. Both come from search snippets and the date is not shown — [Polymarket leaderboard](https://polymarket.com/leaderboard/weather/all/profit); [Krypton](https://krypton.bot/leaderboard?period=all&category=weather)
- gopfan2's all-category all-time PnL is about +$1.68M — [predicting.top](https://predicting.top/). A Russian-language summary of an interview on Evgeny Feldman's podcast says gopfan made over $1.5M in about 1.5 years and started with temperature bets, not politics — [rationalanswer.substack](https://rationalanswer.substack.com/p/polymarket-250). Bot promoters claim "+$2M weather," which conflicts with the leaderboard's ~$317K weather figure — [0xMovez](https://x.com/0xMovez/status/2019532692065243484)
- In October 2025, aenews posted that after Polymarket added category leaderboards, "@r_gopfan and I easily are the #1 and #2 weather guys, with our other accounts taking #3 and #6. The rest are just traders who tailed our bets." This is self-reported — [aenews on X](https://x.com/aenews/status/1981509520510898610)
- neobrother: one article says over $20K profit; Krypton ranks the account about #38 with about $37.5K. The figures are inconsistent — [KuCoin](https://www.kucoin.com/news/flash/traders-on-polymarket-earn-millions-by-predicting-weather); [Krypton](https://krypton.bot/leaderboard?period=all&category=weather)
- Rivo's tracker computes a different weather leader (hello.67, about $75K, for its own period). Third-party trackers disagree with each other — [rivo.markets](https://rivo.markets/polymarket-leaderboard)
- The viral "automatedAItradingbot" account: a Medium analysis puts it at about $88K profit on about $3.3M volume, with 1,537 losses against 349 wins. Much of the profit came from one large Paris win. The bio claims the operator is a meteorologist plus IT engineer — [Medium (snippet)](https://medium.com/mountain-movers/inside-the-data-behind-polymarkets-viral-88k-weather-prediction-trading-strategy-and-results-2e65a8389f37)
- Vendor and affiliate claims: WeatherBot.fi "$700 into $85,000," "profit margins … 18%–48% within 24 hours." These are marketing — [paragraph.com](https://paragraph.com/@0x2e5e2abe2812f022bb1227bb2d7b5eb50568101c/how-one-trader-turned-dollar700-into-dollar85000-trading-weather-on-polymarket-using-weatherbotfinance); [weatherbot.bot](https://weatherbot.bot/). There is also a "Hermes agent $100 to $5,000" guide — [moonsat Medium](https://moonsat.medium.com/hermes-agent-polymarket-how-i-built-self-learning-weather-trading-bot-100-5-000-guide-233fd4a008f2)
- Kalshi: searches found no public trader PnL write-up. Kalshi has no public PnL leaderboard comparable to Polymarket's wallets — [search result: pillarlabai playbook has no PnL](https://pillarlabai.com/blog/how-to-trade-temperature-markets-kalshi/)

### Inferences
- Total realized weather PnL among the top accounts is modest, in the hundreds of thousands of dollars, compared with the multi-million figures in promotional posts. Wealth is concentrated in a small cluster (gopfan2/aenews and their alt accounts).
- Viral wallets with low win rates and lumpy outcomes (one Paris win driving profits) suggest high variance and survivorship bias.

### Gaps
- I could not pull current leaderboard numbers directly (the fetch was blocked). Figures above come from snippets with unknown dates.
- I found no Dune dashboard or hashdive/polymarketanalytics breakdown of weather PnL.

## 3. Market speed, competition and latency

### Takeaway
Competition has clearly intensified. On Kalshi, bracket spreads fell from 15.2¢ (2023) to 4.9¢ (2026), and model information value dropped to around zero or negative by September–October 2026. Guides claim bots correct mispricings within minutes of model updates. No hard latency measurements were found.

### Cited Findings
- On Kalshi, mean bracket spread fell from 15.2¢ to 4.9¢ over 2023–2026. Regime spreads went from 8.4¢ (regime A) to 2.6¢ (regime C). The model's information coefficient on evening highs was 0.19–0.41 per quarter in 2023–2025, then 0.05 in September 2026 and −0.14 in early October 2026 — [Deivid-Negoita/kalshi-weather](https://github.com/Deivid-Negoita/kalshi-weather)
- Execution reality on Kalshi: taker-only fills, and capped orders filled 44% of the time — [same](https://github.com/Deivid-Negoita/kalshi-weather)
- On Polymarket, the market-implied temperature was about 0.2°C from the observed value, versus about 0.8°C for raw models. That points to an efficient market — [jattree/weather-edge](https://github.com/jattree/weather-edge)
- Guides conflict on speed. One says weather updates are slow enough to favor retail. Another says automated bots reading NOAA feeds correct mispricings within minutes of model updates. Search summaries also reference a guide saying sub-second bots are the main competition — [polymarkets.co.il](https://polymarkets.co.il/en/bots/polymarket-weather-prediction-bot/); [tradetheoutcome](https://www.tradetheoutcome.com/polymarket-weather-strategy/)
- Liquidity is thin. A Polymarket weather page showed 586 live weather markets with over $4.7M volume (Nov 5, 2026). A vendor puts a typical city market at about $50–200K volume — [polymarket.com/predictions/weather](https://polymarket.com/predictions/weather); [search summary](https://meteorabot.org/)
- There is a commercial tool ecosystem: wethr.net (real-time data plus release bots), polyweather.pro, HuskyWeatherBot on Telegram, Simmer's "polymarket-weather-trader" agent skill (NOAA plus Open-Meteo), WeatherBot, MeteoraBot, and Apify scrapers — [polyweather.pro](https://polyweather.pro/); [polymart HuskyWeatherBot](https://polymart.app/huskyweatherbot); [Simmer](https://www.simmer.markets/skills/polymarket-weather-trader); [Apify](https://apify.com/bigdavidson/polymarket-weather-markets)

### Inferences
- With free data (Open-Meteo, NOAA) and ready-made bot templates widely available, the easy model-vs-market edge has been competed away. Any remaining edge comes from better calibration, settlement-specific details (6-hour max, 1-minute data, local standard time day) and faster reaction to observation releases, not from access to forecasts.

### Gaps
- I found no measured latency from a 00z/12z run or METAR release to the price move.
- I found no data on the share of volume that comes from bots in weather markets.

## 4. Pitfalls: resolution, stations, rounding, data

### Takeaway
Settlement mechanics are the biggest source of practitioner losses and disputes. Common problems: wrong station, UTC day instead of local standard time day, gridded data or reanalysis instead of station METAR, Fahrenheit/Celsius rounding, 6-hour max spikes, and changing resolution sources. Both venues changed sources in August 2026. Polymarket moved from Wunderground to NOAA/NWS; Kalshi moved from NWS CLI to The Weather Company.

### Cited Findings
**Polymarket: Wunderground to NOAA (August 2026)**
- On 2026-08-22, Polymarket rewrote resolution criteria. "recorded at the LaGuardia Airport Station" became "recorded by NOAA at the LaGuardia Airport Station," and the Wunderground history URL was dropped. 2,195 of 2,596 active markets had the new wording, and 84 still had the old. This broke third-party bots' parsers — [simmer-sdk PR #341](https://github.com/SpartanLabsXyz/simmer-sdk/pull/341)
- BeefSlayer on X: "Starting Aug 23rd, all temperature markets will resolve from … (NWS) instead of Weather Underground. Resolution is still based on METARs and SPECIs" — [BeefSlayer_ on X](https://x.com/BeefSlayer_/status/2091291881594372231)
- 48 of 51 cities now settle on NOAA. Jinan and Taipei remain on Wunderground. Wunderground is the fallback if NOAA has no data by 11:59 PM ET the next day — [Apify resolution checker](https://apify.com/bigdavidson/polymarket-weather-resolution)
- Before the change, practitioners noted that Wunderground's displayed value comes from hourly METAR. They also noted a spike between hourly METARs can show up in the CLI (via the 6-hour max) but not on Wunderground, and 1°F can flip a bracket — [wethr.net trading guide snippet](https://wethr.net/edu/trading-guide)

**Paris sensor tampering (April 2026)**
- Météo-France readings at Charles de Gaulle spiked 4–5°C on the evenings of April 6 and April 15, 2026, and Euronews reports another anomaly on April 19. A Polymarket trader profited: about $34K per Startup Fortune, €25K per Euronews. A complaint was filed with airport police. The hair-dryer theory is unverified — [NPR](https://www.npr.org/2026/04/23/nx-s1-5797876/polymarket-paris-weather-bet); [Bloomberg](https://www.bloomberg.com/news/articles/2026-04-23/france-probes-weather-data-glitch-after-surge-in-polymarket-bets); [Euronews](https://www.euronews.com/business/2026/04/23/hair-dryer-trick-behind-25000-win-france-probes-potential-weather-data-scam-linked-to-poly); [Newsweek](https://www.newsweek.com/did-man-with-hairdryer-trick-polymarket-temperature-bet-what-to-know-11868152); [Startup Fortune](https://startupfortune.com/someone-allegedly-used-a-hairdryer-on-a-paris-airport-weather-sensor-and-walked-away-with-34000-from-polymarket/)
- Polymarket moved Paris settlement to Paris–Le Bourget and did not pause the markets — [NPR](https://www.npr.org/2026/04/23/nx-s1-5797876/polymarket-paris-weather-bet); [Startup Fortune](https://startupfortune.com/someone-allegedly-used-a-hairdryer-on-a-paris-airport-weather-sensor-and-walked-away-with-34000-from-polymarket/)

**Kalshi: NWS CLI to The Weather Company (August 2026)**
- Before the switch, daily highs and lows settled on the final NWS Daily Climate Report (CLI), released the next morning. Settlement could be delayed when the CLI was inconsistent with 6-hour or 24-hour METAR highs, or when the final value came in lower than the preliminary one — [Kalshi help center (snippet)](https://help.kalshi.com/en/articles/13823837-weather-markets)
- Daily temperature contracts moved to The Weather Company data on August 14, 2026 (Polypunter, NextPredict). Another guide says "as of August 27, 2026." The partnership was announced on 2026-08-28 — [The Insurer](https://www.theinsurer.com/parametric-insurer/news/prediction-market-kalshi-partners-with-the-weather-company-for-settlement-data-2026-08-28/); [Polypunter](https://polypunter.com/kalshi-partners-with-the-weather-channel-as-weather-prediction-markets-surge-toward-1-1-billion/); [turbinefi](https://www.turbinefi.com/blog/how-to-trade-kalshi-weather-markets-2026)
- The NYC rules don't specify whether the initial reading or a later corrected one governs — [predictionmarketspicks KXHIGHNY](https://predictionmarketspicks.com/how-it-settles/KXHIGHNY)
- Under the old CLI regime, the climate report matched Kalshi settlement on 12,738 of 12,753 market-days (99.9%) — [Deivid-Negoita/kalshi-weather](https://github.com/Deivid-Negoita/kalshi-weather)

**Technical pitfalls reported by bot builders**
- The CLI day runs from 12:00 AM to 11:59 PM local standard time, so a 12:15 AM daylight-time reading can count toward the previous day — [wethr.net (snippet)](https://wethr.net/edu/trading-guide)
- jattree's bugs: forecasts used the UTC day instead of the local day, and three stations were wrong (Houston KHOU, Denver KBKF, Hong Kong). Backtests used gridded reanalysis instead of METAR, which differed by about 0.9°C on average. The daily max must include SPECI reports and the 6-hour max group, and is rounded half-up to whole degrees in the market's unit. Hong Kong uses HKO's daily max, where label L covers [L, L+1). Precipitation markets use different stations — [jattree/weather-edge](https://github.com/jattree/weather-edge)
- BallesJr: station METAR matched market resolution 93% of the time, versus 66% for the ERA5 grid. Earlier bugs included a wrong Paris station, unparsed °F markets and interpolated observations. New Zealand stations are missing from the IEM archive — [BallesJr](https://github.com/BallesJr/polymarket-weather-edge)

### Inferences
- The August 2026 switches on both venues mean any historical backtest needs per-period settlement logic. Before August 2026, Polymarket backtests should use Wunderground/METAR and Kalshi backtests the CLI. After August 2026, Polymarket should use NOAA timeseries and Kalshi The Weather Company. Bots that parse the rules text can break silently.
- Single-sensor settlement creates manipulation and anomaly risk, as Paris showed. Tail outcomes can be driven by sensor glitches rather than weather.

### Gaps
- I found no documented UMA dispute cases for weather markets beyond Paris.
- I found no discussion of NOAA timeseries data revisions after the Polymarket switch.

## 5. Fees, maker rebates and liquidity rewards for weather

### Takeaway
Polymarket added taker fees to almost all categories on 30 March 2026. Weather has a fee coefficient of 0.05, which peaks at about 1.25¢ per share at a 50¢ price. Makers pay nothing and get a 25% maker rebate funded by taker fees, and the separate Liquidity Rewards program pays for resting quotes near the midpoint. Practitioners' backtests show fees matter: they made up about 22% of one Kalshi paper loss, and a 1¢ half-spread plus fee turned Polymarket model trades negative.

### Cited Findings
- Weather taker fee coefficient 0.05; makers pay no fee and receive rebates; rollout across nearly all categories on March 30, 2026, with geopolitics staying fee-free; peak about 1.25% of notional at a 50¢ price, or "max $1.25 per 100 shares" — [Polymarket docs (snippet)](https://docs.polymarket.com/trading/fees); [predictionhunt](https://www.predictionhunt.com/blog/polymarket-fees-complete-guide); [PineAnalytics fee rollout](https://pineanalytics.substack.com/p/polymarket-fee-rollout); [predictefy](https://blog.predictefy.com/polymarket-fees)
- Maker rebates: Weather 25%, weighted by the fee curve and computed per market. Only filled maker orders earn, paid in pUSD (an older help page says USDC) — [Polymarket maker rebates docs](https://docs.polymarket.com/programs/maker-rebates); [help center](https://help.polymarket.com/en/articles/13364471-maker-rebates-program)
- The Liquidity Rewards Program is separate. It pays daily for resting limit orders near the midpoint whether filled or not, with scores sampled about once a minute, payouts around midnight UTC and a $1 minimum. These details come from third-party guides — [startpolymarket rebates & rewards](https://startpolymarket.com/learn/polymarket-rebates-rewards/); [polymarkets.co.il farming](https://polymarkets.co.il/en/bots/polymarket-liquidity-rewards-farming/)
- Polymarket US (the separate product) has a flat 0.30% taker fee and a 0.20% maker rebate — [predictionhunt (snippet)](https://www.predictionhunt.com/blog/polymarket-fees-complete-guide)
- Fee impact: the Kalshi paper run lost $19.88, of which $4.45 was fees. jattree's simulation with fee and spread came out at −13.9% per trade — [Deivid-Negoita](https://github.com/Deivid-Negoita/kalshi-weather); [jattree](https://github.com/jattree/weather-edge)

### Inferences
- Since March 2026, the cheap-tail taker style pays low fees in absolute terms, because the fee scales with p(1−p) and is small at 5–15¢. Mid-priced taker trades near 50¢ pay the most. Fees push the economics toward maker-side quoting, which now earns rebates plus liquidity rewards. I found no practitioner PnL report on weather market making.

### Gaps
- I found no data on weather volume changes after fees, or on practitioner reaction to weather fees specifically. The PineAnalytics post could not be read.
- I could not confirm the weather-specific liquidity-reward budgets.
