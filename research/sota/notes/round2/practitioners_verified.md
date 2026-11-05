# Practitioner Write-ups and Verified Trader Data on Polymarket/Kalshi Temperature Markets (verification pass, 2026-11-05)

Method: the Polymarket Data API v2 was queried directly on 2026-11-05 (~08:00 UTC). Endpoints used: `/v2/leaderboard?category=WEATHER`, `/v2/positions?status=CLOSED&title=temperature`, `/v2/trades` with `taker_only=true/false`, and `/v2/user-stats`. Wallets were resolved through `gamma-api.polymarket.com/public-search?search_profiles=true`. dev.to articles were read in full through the dev.to public API (`/api/articles/{user}/{slug}`). wethr.net pages were read with curl. **polymarketanalytics.com returned HTTP 403 (Vercel block) to curl and does not resolve for WebFetch, so I got no data from it.** Data API v1 is retired ("Data API v1 retires on November 2, 2026") — [docs](https://docs.polymarket.com/migrate/data-api-v1-to-v2.md). Raw pulls are saved in the scratchpad (raw pulls kept only in the research session scratchpad, not in the repo)`).

Caveats on the API data:
- `realized_pnl` and `avg_price` per position can be distorted by negRisk conversions, merges and sells. ColdMath's per-position numbers are clearly inconsistent with its leaderboard PnL (see below).
- Positions pulls were capped at 10 pages (10,000 positions) for ColdMath and Poligarch, so their histories are truncated.
- "Maker share" was inferred as rows that appear with `taker_only=false` but not with `taker_only=true`. It is approximate.

## 1. dev.to practitioner articles: methods and evidence

### Takeaway
dev.to has very few substantive weather-market posts. The one rigorous one is a Kalshi backtest (Sep 2026): a day-ahead NWS/GFS/ECMWF forecast with a normal error model **lost to the market**, at −37.7% ROI buying YES and −7.2% buying NO. The others are a promotional ensemble-counting bot with no PnL shown, a Medium cross-post that repeats unverified X claims (gopfan2 "$2M… YES<15c / NO>45c / $1 per position"), and bot-engineering posts.

### Cited Findings
- **myfirstcodeo, "I backtested a forecast-based model against Kalshi's temperature markets. The market won" (2026-09-23).**
  - Data: every settled Kalshi US daily-high market from 25 Jul to 22 Sep 2026, covering 24 cities, 1,317 city-days and 7,902 markets.
  - Model: Open-Meteo previous-day GFS/ECMWF blend with a per-city Normal(bias, σ). It was compared with the Kalshi close on the day before.
  - Out-of-sample Brier score: model 0.1466, market mid 0.1195, base rate 0.1541. "It won in every city and in every price band." — [dev.to](https://dev.to/myfirstcodeo/i-backtested-a-forecast-based-model-against-kalshis-temperature-markets-the-market-won-heres-442c)
- Same post, trading results:
  - Buy YES at edge ≥8¢: 689 trades, 74 wins, $6,850.81 staked, $420.80 fees, P&L −$2,583.61 (ROI −37.7%).
  - Mirror NO strategy: 787 trades, P&L −$550.88 (−7.2%).
  - "Every price band loses. The worst are the sub-10-cent tails." — [dev.to](https://dev.to/myfirstcodeo/i-backtested-a-forecast-based-model-against-kalshis-temperature-markets-the-market-won-heres-442c)
- Same post, calibration and station bias:
  - In the model's 0–10% bin, events happened 7.9% of the time; in the market's 0–10% bin, 2.6%. The market's tails were close to calibrated, while the normal model was fat-tail-blind.
  - Large stable station biases exist (actual minus day-1 forecast): Miami +3.7°F, LAX −4.0°F, San Diego −3.4°F. The author's view: "If you trade weather markets and are not adjusting for the station, that is the edge you are leaving."
  - Kalshi settlement (The Weather Company) matched the NWS climate report on 1,316 of 1,317 city-days.
  - The post ends by selling a $29 scanner. — [dev.to](https://dev.to/myfirstcodeo/i-backtested-a-forecast-based-model-against-kalshis-temperature-markets-the-market-won-heres-442c)
- **predictandprofit, "Most weather traders check one app. My bot reads 164 forecasts" (2026-06-01).**
  - The bot pulls GFS (31 members), ECMWF (51), NOAA AIGEFS and ECMWF AIFS ensembles, up to 164 members. It counts the members clearing a threshold (e.g., 118/164 = 72% against a 40¢ price) and fires only if 3 of the 4 families agree.
  - No PnL is shown. The author says "fills and accounting, have been way more trouble than the model ever was." — [dev.to](https://dev.to/predictandprofit/most-weather-traders-check-one-app-my-bot-reads-164-forecasts-28o0)
- The same author's later post reports that a Google AI weather model had a −5.2°F cold bias across 16 Kalshi settlement stations. This comes from a search snippet; I did not read it in full — [dev.to](https://dev.to/predictandprofit/we-turned-down-googles-ai-weather-model-1blc)
- **cryptodeploy, "How Polymarket Weather Markets Actually Work" (2026-04-04; Medium cross-post).**
  - Repeats X claims without verification: gopfan2 "reportedly crossed $2 million in profit, mostly from weather markets… buy Yes below $0.15, buy No above $0.45, never risk more than $1 per position". Also meropi at ~$30K with $1–3 bets, and 1pixel at $18.5K from $2.3K deposits.
  - It also says "there are no taker fees on most weather markets", which is outdated: weather taker fees started 30 Mar 2026 (see prior notes). — [dev.to](https://dev.to/cryptodeploy/how-polymarket-weather-markets-actually-work-50nb)
- A post notes that Kalshi's "HIGHEST Temperature SATX" settles at a different station than the title implies. Search results also mention Chicago settling at Midway and Houston at Hobby, as practitioner warnings about stations (snippet) — [dev.to](https://dev.to/matveyg/kalshis-market-titled-highest-temperature-satx-settles-in-louisville-22eh)
- **botcookery (2026-11-04).**
  - A kill-switch post with logs from a quoting bot that joins the best bid on Kalshi KXHIGHNY/KXHIGHMIA and the Polymarket US `tc-temp-miahigh` markets.
  - Every order went to a mock exchange. The post is engineering only, with no PnL evidence. — [dev.to](https://dev.to/botcookery/our-bots-10-exposure-limit-held-1860-after-one-restart-kill-switch-fixes-34cg)
- The other dev.to hits are generic or marketing: a PolyCopy affiliate piece (2026-09-21), and manja316's "176 trades… about $2", which is about crypto 15-minute markets, not weather — [dev.to](https://dev.to/garage23auto_a7c1e189d84f/beyond-the-headlines-exploring-polymarkets-niche-weather-markets-1n8a); [dev.to](https://dev.to/manja316/176-trades-on-polymarket-what-my-bot-actually-made-its-not-what-you-think-3iib)

### Inferences
- An independent third backtest (Kalshi, Jul–Sep 2026) agrees with the GitHub post-mortems in the prior notes (Deivid-Negoita, jattree): the day-ahead price already embeds public forecasts and station bias. Cheap-tail YES buying driven by a model was the worst bucket.
- The "gopfan2 YES<15c / NO>45c" rule circulates only through promotional reposts. Section 3 shows it does not match gopfan2's actual weather PnL source.

### Gaps
- I found no dev.to post with live (not paper) Polymarket daily-temperature PnL backed by a wallet.
- The dev.to API tag search (polymarket, kalshi, predictionmarkets: 546 articles) found nothing beyond the posts above.

## 2. wethr.net: products, data and market-speed evidence

### Takeaway
wethr.net is a paid real-time observation and analytics service for weather-market traders. Its key products:
- a speed tier: free users get data 3 minutes later than paying users
- 1-minute ASOS (OMO) ingestion for about 94 US stations
- DSM/CLI/6-hour-max tracking
- push APIs
- a public latency page

It documents several kinds of release-driven "bots" that pick off stale limit orders. It publishes data-receipt latency, but no measurements of market price reaction speed.

### Cited Findings
- About: "aggregates a large amount of data from a range of sources… works the data into the tightest potential temperature ranges… serve up the data as quickly as possible". Its two stated goals are "simplicity and speed" — [wethr.net/about](https://wethr.net/about)
- Plans as of 2026-11-05:
  - Free: data delayed "Basic/Pro + 3 Mins", with ads.
  - Basic $14.99/mo: "3-Minute Head Start over free users", plus a data release schedule.
  - Professional $24.99/mo: model forecast tables for 18 models, model accuracy and bias tracking, NWS forecast-evolution tracker, High/Low Notifier, alerts, APIs, Push API for 5 stations.
  - Developer $99/mo: 300 requests/min, 100K/day, Push API for all stations. Enterprise pricing is separate.
  - [wethr.net/subscribe](https://wethr.net/subscribe)
- High/Low Notifier (Pro, beta): a live feed of new highs and lows from NWS and Wunderground (e.g., "New High: 88°F (was 86°)") — [wethr.net/notifier](https://wethr.net/notifier)
- Measured receipt latency, observation time to Wethr receipt, through 3 Nov 2026:

  | Feed | Median | p90 | p99 |
  |---|---|---|---|
  | US hourly METAR | 2m33s | 3m17s | 8m30s |
  | International hourly METAR | 4m28s | 7m14s | 17m18s |
  | US SPECI | 2m42s | — | — |
  | US 5-minute | 2m15s | — | — |
  | US 1-minute (OMO, 931,984 reports from 94 stations) | 2m26s | 2m43s | 4m32s |

  Some stations are much slower. KBKF (Aurora/Denver) had a 6m10s median with p90 above 30 minutes — [wethr.net/latency](https://wethr.net/latency)
- OMO feed status on 2026-11-05: 92 live, 1 delayed and 1 down out of 94 stations. KMCI had no 1-minute data for 27h29m — [wethr.net/omo-status](https://wethr.net/omo-status)
- "Beware of Bots" guide (updated 2026-02-15) describes the following bots — [wethr.net/edu/market-bots](https://wethr.net/edu/market-bots):
  - **DSM bot.** It "reacts quickly to the release of NWS Daily Summary Messages". The guide warns against resting sells below, or buys at, the current high near DSM times. Approximate DSM release times (Z): NYC 20:21, 21:21, 05:17; Miami 07:22, 20:12, 21:12, 05:17; Chicago 21:17, 22:17, 06:17; Austin 06:16, 13:16, 22:16, 23:16; Denver 12:17, 22:17, 23:17, 07:17; LAX 22:08, 01:08, 08:08.
  - **OMO bot.** It automates dial-in calls to ASOS phone lines to hear the minute temperature before it is public. "Often, only one call can access the ASOS line at a time."
  - **6-Hour bot.** It watches the 6-hour max in the hourly obs at about 23:51–23:54Z, 05:51–05:54Z, 11:51–11:54Z and 17:51–17:54Z. The 6-hour max "often includes OMOs… that might not appear on the standard 5-minute timeseries".
  - **CLI bot.** "possibly less active now".
  - **"240" market-maker bot.** It quotes about 240 contracts on both sides with roughly a 2¢ spread and adjusts to its forecast and inventory.
  - **"UI" and "1-Up" bots.** Order-book flicker and penny-jumping.
  - The guide also warns about paid "Entrepreneur's Bot" tools that "simply repackage publicly available information".
- Update log, relevant to Polymarket — [wethr.net/updates](https://wethr.net/updates):
  - 23 Oct 2026: "Changed Polymarket.com stations to AWC resolution (for the ones it applies to)".
  - 20 Oct 2026: added a 1-minute Fahrenheit ASOS archive API going back 25+ years.
  - 8 Oct 2026: changes to match "Kalshi resolution logic that is largely excluding fallback observations" in the hourly index markets.
  - 30 Sep 2026: latency page added.
  - 29 Sep 2026: OMO status page added.

### Inferences
- The commercial edge being sold is information latency on observations. That means 1-minute, 6-hour-max and DSM data a few minutes ahead of the public time series, plus a 3-minute gap between paid and free tiers. Forecasts are not the product. This fits the dominant same-day activity of profitable wallets (section 3).
- The AWC change suggests Polymarket.com temperature resolution now points to the Aviation Weather Center METAR feed for some stations. This is after the August 2026 NOAA wording change in the prior notes and needs confirmation from Polymarket's rules.

### Gaps
- wethr.net publishes no study of market price reaction to DSM, 6-hour or METAR releases. The bot descriptions are "common observations from the community", not measurements.
- I found no evidence on how much volume OMO bots handle, or whether they are legal under the terms of service.

## 3. Top weather wallets verified from the Polymarket API

### Takeaway
The official all-time weather leaderboard confirms gopfan2 at #1 (+$317.2K on $4.62M volume) and aenews2 at #2 (+$285.7K on $10.15M). **However, almost all of their weather profit comes from monthly global-temperature-anomaly and "hottest on record" markets in 2024–2025, not from daily city high/low markets.** Their daily-city footprint is essentially nil, and neither has traded weather recently.

The profitable daily-city specialists look different:
- **HighTempTation** (+$98K): a taker that buys near-certain NO (≥$0.90–0.99) on the target day.
- **BeefSlayer** (+$86K): mostly US cities, many cheap YES tickets, about 80% of rows as maker.
- **automatedAItradingbot** (+$65K): cheap-tail YES, with a 16% position win rate.

Recent monthly and weekly leaders are mostly different, new wallets.

### Cited Findings
**Leaderboard (all-time, WEATHER, PnL), from [data-api v2 leaderboard](https://data-api.polymarket.com/v2/leaderboard?category=WEATHER&time_period=ALL&sort_by=PNL&limit=50), pulled 2026-11-05**

| # | Name | PnL | Volume | PnL / volume |
|---|---|---|---|---|
| 1 | gopfan2 (X: r_gopfan) | $317,221 | $4.62M | 6.9% |
| 2 | aenews2 (X: aenews) | $285,676 | $10.15M | 2.8% |
| 3 | ColdMath | $134,264 | $11.10M | 1.2% |
| 4 | gopfan | $118,426 | $0.74M | |
| 5 | HighTempTation | $98,064 | $2.66M | 3.7% |
| 6 | Poligarch | $95,537 | $17.66M | 0.5% |
| 7 | duderr | $93,491 | $40K | |
| 8 | Hans323 | $87,714 | $7.38M | |
| 9 | bama124 | $86,601 | $0.41M | |
| 10 | BeefSlayer | $85,973 | $2.36M | |
| 16 | automatedAItradingbot | $64,861 | $2.73M | |
| 19 | hello.67 | $63,023 | | |
| 27 | aenews-915 | $55,093 | | |

- The #50 entry is about $40K. Relatives of gopfan2's handle on the board: gopfan (#4) and a "gopfan2.0" profile exists. Relatives of aenews2: aenews-915 (#27), plus "aenews2.5" and "aenews20" profiles. This is consistent with aenews' claim of alt accounts in the prior notes.
- Wallets via [gamma public-search](https://gamma-api.polymarket.com/public-search?q=gopfan2&search_profiles=true): gopfan2 = 0xf2f6af4f27ec2dcf4072095ab804016e14cd5817; aenews2 = 0x44c1dfe43260c94ed4f1d00de2e1f80fb113ebc1.
- **Monthly and weekly turnover.**
  - Monthly top 3: Poligarch +$31.2K, 1DVSBSTD +$22.7K, and an unnamed wallet 0x15d3… at +$22.7K.
  - Weekly top: Sylar012 +$11.4K.
  - None of gopfan2, aenews2 or ColdMath is in the monthly top 30.
  - [MONTH](https://data-api.polymarket.com/v2/leaderboard?category=WEATHER&time_period=MONTH&sort_by=PNL&limit=50); [WEEK](https://data-api.polymarket.com/v2/leaderboard?category=WEATHER&time_period=WEEK&sort_by=PNL&limit=50)
- Biggest single weather wins in the past month were about $4.7–10.1K, all daily-high markets (Paris 7 Oct, Cape Town 18 Oct, Qingdao 25 Oct, Istanbul 20 Oct, Hong Kong). kupoz turned $19 into $7,590 on Istanbul 20 Oct. aapang won about $4.75K three times on Hong Kong (11, 24 and 27 Oct) — [biggest-winners](https://data-api.polymarket.com/v2/biggest-winners?time_period=MONTH&category=WEATHER&limit=10)

**gopfan2: where the weather PnL actually comes from**
- Closed positions with "temperature" in the title: 102, all global-monthly anomaly markets (2024-08 to 2026-06). Realized PnL is +$149.9K with a 51% position win rate — [positions](https://data-api.polymarket.com/v2/positions?user=0xf2f6af4f27ec2dcf4072095ab804016e14cd5817&status=CLOSED&title=temperature&limit=1000)
- In his top 300 closed positions by PnL, 23 are weather-like, totalling +$408.9K. Examples (outcome, average entry):
  - "global temperature increase by more than 1.34ºC in January 2025": +$62.6K (YES at 0.573)
  - "Global heat increase between 1.28–1.30°C for 2024": +$61.6K (YES at 0.518)
  - "August [2024] temperature increase greater than 1.29°C": +$39.5K (YES at 0.257)
  - "2025 January hottest on record?": +$36.0K (YES at 0.655)
  - "November 2024 … 1.30–1.34°C": +$29.2K (YES at 0.38)
  - "2025 hottest year? NO": +$8.5K (NO at 0.917)
  - [positions sorted by REALIZED_PNL](https://data-api.polymarket.com/v2/positions?user=0xf2f6af4f27ec2dcf4072095ab804016e14cd5817&status=CLOSED&sort_by=REALIZED_PNL&limit=300)
- Most entries were YES between 0.23 and 0.70, not YES below 0.15. No daily city high/low position appears in his history. His last 4,000 trades (2 Jun to 3 Nov 2026) include only one temperature trade (Nov-2026 global anomaly YES at 0.425). The rest are politics and sports — [trades](https://data-api.polymarket.com/v2/trades?user=0xf2f6af4f27ec2dcf4072095ab804016e14cd5817&limit=1000)
- All categories: realized PnL $1.69M, trade_count 80,427, volume $70.8M. Fees paid $4.8K, maker rebate $2.7K, liquidity reward income $16.6K. He joined Aug 2024 — [user-stats](https://data-api.polymarket.com/v2/user-stats?user=0xf2f6af4f27ec2dcf4072095ab804016e14cd5817)

**aenews2**
- Closed "temperature" positions: 146, from 2024-07 to 2026-04.
  - 136 global-monthly positions: +$65.6K realized on about $4.7M cost.
  - 10 daily-city positions (London/Chicago, March 2026): −$129.
  - [positions](https://data-api.polymarket.com/v2/positions?user=0x44c1dfe43260c94ed4f1d00de2e1f80fb113ebc1&status=CLOSED&title=temperature&limit=1000)
- Largest weather wins:
  - "global temperature increase >1.19ºC in September 2025": +$171.8K (YES at 0.26)
  - "2024 July hottest on record?": +$148.4K (YES at 0.64)
  - "August 2024 >1.29°C": +$103.8K (YES at 0.32)
  - "Feb 2025 1.25–1.29ºC": +$71.9K (YES at 0.33)
  - There is also a tornado-count market: +$4.7K.
  - The weather-like rows in his top 300 sum to about +$871K, gross of losses. The leaderboard net is $285.7K.
  - [positions by PnL](https://data-api.polymarket.com/v2/positions?user=0x44c1dfe43260c94ed4f1d00de2e1f80fb113ebc1&status=CLOSED&sort_by=REALIZED_PNL&limit=300)
- His last 3,000 trades (21 Aug to 5 Nov 2026) contain zero temperature markets. They are Fed, geopolitics and tennis — [trades](https://data-api.polymarket.com/v2/trades?user=0x44c1dfe43260c94ed4f1d00de2e1f80fb113ebc1&limit=1000)

**HighTempTation (0x6011655c4afb76f36dd1b08a137a1ba73466b31e)**, joined Mar 2026
- 4,831 closed temperature positions (2026-04-03 to 2026-11-05), all daily city high/low, with roughly a 100% position win rate.
  - 4,372 of them were NO positions with average entry ≥0.85: PnL +$47.2K on about $1.03M cost.
  - 271 NO positions entered at 0.45–0.85: +$38.3K.
  - Median cost per position $132; p90 $583.
  - Spread across international cities: Taipei, Lucknow, Mexico City, Cape Town, Wellington, São Paulo, Buenos Aires, Paris, Panama City.
  - [positions](https://data-api.polymarket.com/v2/positions?user=0x6011655c4afb76f36dd1b08a137a1ba73466b31e&status=CLOSED&title=temperature&limit=1000)
- Trade sample (2,000 trades, 30 Sep to 5 Nov 2026), $238.6K notional:
  - 99% of trades are on the target local day (1,780 of 1,797 parsed).
  - Buys are mostly NO at ≥0.95 (516) or 0.85–0.95 (168).
  - 1,036 sells of NO at ≥0.95.
  - About 21% of rows and 11% of notional are maker; the rest are taker.
  - Median trade $49.5; p90 $370.
  - Same-day NO≥0.90 buys peak at 11:00–14:00 local, with a second cluster at 00:00–06:00 local.
  - [trades](https://data-api.polymarket.com/v2/trades?user=0x6011655c4afb76f36dd1b08a137a1ba73466b31e&limit=1000&taker_only=false)
- user-stats: realized $98.1K; fees paid $5,197 on $2.65M volume; maker rebate $3; 12,094 trades — [user-stats](https://data-api.polymarket.com/v2/user-stats?user=0x6011655c4afb76f36dd1b08a137a1ba73466b31e)

**BeefSlayer (0x331bf91c132af9d921e1908ca0979363fc47193f; X: BeefSlayer_)**
- 2,707 closed temperature positions (2025-10 to 2026-11), with a 46% win rate: daily-high +$77.2K, daily-low +$4.5K.
- City PnL: NYC 666 positions / +$24.7K, Seattle +$10.5K, Chicago +$9.7K, Dallas +$9.3K, Atlanta +$6.2K, Miami +$5.6K.
- YES below 5¢: 978 positions, 17% win rate, +$15.5K. YES 5–15¢: 400 positions, +$8.9K.
- Median cost per position $23; p90 $280.
- Biggest wins: Panama City "≤24°C" YES at 1.3¢ (+$4.9K); Dallas "≤99°F" YES at 0.9¢ (+$3.2K).
- [positions](https://data-api.polymarket.com/v2/positions?user=0x331bf91c132af9d921e1908ca0979363fc47193f&status=CLOSED&title=temperature&limit=1000)
- Trade sample (5 Oct to 5 Nov 2026):
  - 79% of trades on the target day, 17% on D−1.
  - Activity spreads through the local day, with peaks at 09:00–16:00 and 00:00.
  - Mostly BUY YES under 15¢ (1,122 of 1,824).
  - About 80% of rows and 49% of notional are maker.
  - Median trade $1.0; p90 $37.
  - [trades](https://data-api.polymarket.com/v2/trades?user=0x331bf91c132af9d921e1908ca0979363fc47193f&limit=1000&taker_only=false)
- user-stats: 21,514 trades; fees paid $2.5K; maker rebate $183 — [user-stats](https://data-api.polymarket.com/v2/user-stats?user=0x331bf91c132af9d921e1908ca0979363fc47193f)

**automatedAItradingbot (0xd8f8c13644ea84d62e1ec88c5d1215e436eb0f11)**
- Leaderboard: +$64.9K on $2.73M. That is below the Medium "$88K" figure in the prior notes.
- 6,141 closed temperature positions (2025-02 to 2026-07), with a 16% win rate.
  - YES below 5¢: 2,106 positions, 6% win rate, +$25.4K.
  - YES 5–15¢: 2,265 positions, 15% win rate, +$33.3K.
  - YES 45–85¢: −$17.9K.
  - Cities: London +$27.2K, NYC +$21.3K, plus another +$7.9K on "NYC"-titled markets, Seoul +$4.7K.
  - Median cost per position $5.
  - Top win: Hong Kong "≤15°C" YES at 0.50 (+$8.7K).
  - [positions](https://data-api.polymarket.com/v2/positions?user=0xd8f8c13644ea84d62e1ec88c5d1215e436eb0f11&status=CLOSED&title=temperature&limit=1000)
- Trade sample (14 Jun to 14 Jul 2026):
  - 98% of trades on the target day, peaking at 12:00–14:00 local.
  - Median trade $1.6.
  - About 63% of rows and 41% of notional are maker.
  - Hong Kong, Seoul, Moscow and Shenzhen were the most-traded cities.
  - No activity after July 2026.

**ColdMath and Poligarch (high volume, thin margin)**
- ColdMath: +$134K on $11.1M (1.2%). The per-position API data (9,764 positions, Dec 2025 to Aug 2026, truncated) sums to −$120K. That contradicts the leaderboard, which points to negRisk conversion artefacts, so I did not use its per-position details. Its recent trades (Nov 2026) are sports.
- Poligarch: +$95.5K on $17.7M (0.5%). The last 10,000 closed positions (9 Oct to 5 Nov 2026) are −$11K realized, with a 48% win rate and median cost $29.
  - A 1,000-trade sample on 5 Nov 2026: about 96% of rows are maker, balanced YES/NO buys mostly at 15–85¢, median trade $3.9, across Asian cities.
  - This pattern is consistent with market making or liquidity-reward farming. It is also the #1 monthly earner (+$31.2K).
  - [trades](https://data-api.polymarket.com/v2/trades?user=0xb40e89677d59665d5188541ad860450a6e2a7cc9&limit=1000&taker_only=false)

### Inferences
- The narrative that "gopfan2 made his weather money with ladders of cheap YES/NO on city temperatures" is not supported by on-chain data. gopfan2 and aenews2 earned most of their weather-category PnL from a handful of large (five- to six-figure) directional bets on monthly NASA/NOAA global-anomaly and "hottest month/year" markets in 2024–2025, at mid prices. The edge there is likely climate-data expertise, such as tracking ERA5/Copernicus daily anomalies ahead of the official monthly release. That is an inference; the API does not show the reasoning.
- Profitable daily-city styles that can be seen on-chain:
  - (a) Same-day "certainty harvesting": buying NO at 0.90–0.99 on brackets the observed or forecast trajectory has ruled out, as a taker, at about 3.7% PnL/volume (HighTempTation). Margins are thin and tail risk is high (one wrong 0.97 NO wipes out about 30 wins). It depends on fast observation data of the kind wethr.net sells.
  - (b) Cheap-tail lottery tickets on the target day with tiny sizes, where a few big hits carry the PnL (BeefSlayer, automatedAI). Their aggregate profits come from rare 50–500× winners; win rates are 6–17% in the sub-15¢ buckets.
  - (c) High-volume maker quoting (Poligarch, possibly ColdMath) at about 0.5–1.2% of volume.
- In absolute terms, daily-city PnL is small: the best verified daily-city account is about $98K over 7 months. Leaderboard churn suggests edges decay or rotate quickly.

### Gaps
- The maker/taker split is inferred from `taker_only` diffs and limited samples (1,000–2,000 trades per wallet).
- I could not link trades to model-run or METAR timestamps (no price-history or observation join).
- The leaderboard's WEATHER category boundary (global anomaly, tornado, hurricane, rain) is undocumented. Category-level PnL could not be split into daily-city versus other markets for the leaderboard itself.
- ColdMath and Poligarch histories are truncated at 10,000 positions.

## 4. polymarketanalytics.com and other leaderboard data for weather

### Takeaway
polymarketanalytics.com blocked access (HTTP 403 via curl; DNS failure for WebFetch), so I have no PnL or win-rate figures from it. The official Polymarket Data API v2 offers the same and better data (leaderboard by category and period, user-stats, positions, biggest-winners), and that is what section 3 uses.

### Cited Findings
- polymarketanalytics.com/traders returned "Forbidden" (Vercel edge), tested 2026-11-05 — [polymarketanalytics.com](https://polymarketanalytics.com/traders)
- The v2 API exposes `/v2/leaderboard` (time_period, category, sort_by), `/v2/biggest-winners`, `/v2/user-stats` (fees, maker_rebate, reward_income, trade_count) and `/v2/user-pnl` — [openapi](https://data-api.polymarket.com/v2/openapi.json)
- Weather leaderboard by volume (all-time): Poligarch $17.7M, OraculumNobius $14.4M (+$372), dpnd $14.1M (+$20K), largeleeks888 $13.9M (−$13K), Haradwaith $13.5M (−$77K), ColdMath $11.1M (+$134K), aenews2 $10.1M (+$286K). Several of the highest-volume accounts are flat or losing — [leaderboard by VOLUME](https://data-api.polymarket.com/v2/leaderboard?category=WEATHER&time_period=ALL&sort_by=VOLUME&limit=10)

### Inferences
- Among the highest-volume weather accounts, volume does not translate into profit. That fits a competitive market where bots trade large volumes at near-zero edge.

### Gaps
- Win rates in polymarketanalytics' own definition are unavailable. Rates in this file are position-level win rates computed from closed positions.
