# Daily high-temperature markets: primary-source resolution rules, data sources, and observation data for rebuilding settlement values

Method note (research date 2026-11-05): all Polymarket rule texts below were pulled directly from the Gamma API (`https://gamma-api.polymarket.com/events?slug=...`, field `description`, plus `resolutionSource` and per-market fee fields). Fee and resolution docs come from docs.polymarket.com `.md` pages. Kalshi text comes from help.kalshi.com. NWS text comes from weather.gov (LOT FAQ, NWS Instruction 10-1004 PDF, ASOS User's Guide PDF). IEM was tested live.

**Not reachable from this session (proxy 403):** kalshi.com, api.elections.kalshi.com (KXHIGH contract terms and series rules), www.weather.gov.hk (HKO Daily Extract). The S3 contract-terms URL `kalshi-public-docs.s3.amazonaws.com/contract_terms/HIGHNY.pdf` returned 404.

**Corrections to the prior note** (`Торговля погодными рынками Polymarket/market_efficiency_resolution.md`):
1. Polymarket now runs **three regimes**, not two: Wunderground (until 22 Aug 2026), NOAA weather.gov/wrh/timeseries (23 Aug – 22 Oct 2026), and aviationweather.gov METAR API (from 23 Oct 2026).
2. The prior "SPECI is included" claim is **wrong for the current regime**. From 23 Oct 2026 the rule text explicitly says SPECI "does not count".
3. The current regime uses the **T-group in tenths °C**, falling back to the body temperature in whole °C, with explicit half-up rounding. It is not "whole °C as displayed".
4. Jinan and Taipei were on Wunderground in Sept 2026. Taipei moved to the METAR API on 23 Oct. No Jinan events exist for late Oct or Nov 2026.
5. The Kalshi help page (dated July 22, 2026) still says daily highs settle on the NWS Daily Climate Report. I could not retrieve primary confirmation of a CLI→TWC switch.

---

## Q1. Polymarket temperature-market rule text by period (sources, SPECI, T-group, rounding, °F, missing data, finalisation)

### Takeaway
For non-HK cities Polymarket has used three successive rule regimes, each identified from Gamma `resolutionSource` and `description`:

| Period | Market dates | Source | What counts |
|---|---|---|---|
| A | ≤ 22 Aug 2026 | Wunderground daily history | "highest temperature recorded for all times", whole degrees |
| B | 23 Aug – 22 Oct 2026 | NOAA `weather.gov/wrh/timeseries?site=XXXX` | "highest reading under the 'Temp' column"; for US stations from about 25 Aug, "Hourly Data" |
| C | ≥ 23 Oct 2026 | `aviationweather.gov/api/data/metar` raw | highest **routine METAR** value only (SPECI excluded); T-group tenths °C, else body °C; °F = °C×9/5+32 rounded half-up; local-time calendar day; Wunderground fallback; lowest bracket if no data |

Hong Kong is separate throughout: the HKO Daily Extract "Absolute Daily Max", to 0.1 °C, with initial publication as the revision cutoff.

### Cited Findings

**Regime switch dates (NYC/KLGA series, checked one date at a time)**
- NYC, 20–22 Aug 2026: `resolutionSource` = `https://www.wunderground.com/history/daily/us/ny/new-york-city/KLGA`. 23 Aug 2026: `https://www.weather.gov/wrh/timeseries?site=klga`. 22 Oct 2026: still weather.gov. 23 Oct 2026: `https://aviationweather.gov/api/data/metar?ids=KLGA&format=raw&date=2026-10-24T04:00:00Z&hours=27`. From 24 Oct on, the URL uses `hours=30` — [Gamma NYC Aug 22](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-august-22-2026); [Gamma NYC Aug 23](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-august-23-2026); [Gamma NYC Oct 22](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-october-22-2026); [Gamma NYC Oct 23](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-october-23-2026)
- The switch to the METAR API happened on the same date (market date 23 Oct 2026) for London (EGLC), Seoul (RKSI), Tokyo (RJTT) and Taipei (RCSS):
  - London, Seoul and Tokyo were on weather.gov/wrh/timeseries on 20 and 22 Oct.
  - Taipei was on Wunderground (`.../tw/taipei/RCSS`) on 20 and 22 Oct.
  - Source: [Gamma London Oct 23](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-london-on-october-23-2026); [Gamma Taipei Oct 22](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-taipei-on-october-22-2026)
- Jinan: the latest events found are from August to 5 Sep 2026, e.g. `highest-temperature-in-jinan-on-september-5-2026`, source `https://www.wunderground.com/history/daily/cn/jinan/ZSJN`. There are no Jinan events for 20–26 Oct or 5 Nov 2026 — [Gamma public-search "jinan temperature"](https://gamma-api.polymarket.com/public-search?q=jinan%20temperature&limit_per_type=5); [Gamma Jinan Sep 5](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-jinan-on-september-5-2026)

**Regime A: Wunderground (example NYC 15 Jul 2026; London/Seoul 15 Jul identical except °C)**
- Main rule: "The resolution source for this market will be information from Wunderground, specifically the highest temperature recorded for all times on this day for the LaGuardia Airport Station, available here: https://www.wunderground.com/history/daily/us/ny/new-york-city/KLGA."
- Timing and precision: "This market can not resolve until the first data point for the following date has been published on the resolution source." "The resolution source for this market measures temperatures to whole degrees Fahrenheit (eg, 21°F). Thus, this is the level of precision that will be used when resolving the market."
- Revisions: "Revisions to temperatures recorded within this market's timeframe will be considered until the first datapoint for the following date has been published, after which any alterations will not be considered."
- Source: [Gamma NYC Jul 15](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-july-15-2026)
- Later Wunderground-regime texts (Taipei Sep 15, Jinan Sep 5) add:
  - "This market will resolve based on the highest temperature recorded in the 'Daily Observations' table on Weather Underground, not the figure displayed in the 'Day High & Low' summary section…"
  - Missing data: "In the event that there is no data for the observation date by 11:59 PM ET on the day following the observation date, this market will resolve to the lowest bracket."
  - Sources: [Gamma Taipei Sep 15](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-taipei-on-september-15-2026); [Gamma Jinan Sep 5](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-jinan-on-september-5-2026)

**Regime B: NOAA weather.gov/wrh/timeseries (example NYC 15 Sep 2026)**
- Main rule: "The resolution source for this market will be information from NOAA, specifically the highest reading under the "Temp" column for all times on this day, available here: https://www.weather.gov/wrh/timeseries?site=klga"
- US hourly clause: "This market will resolve off of the Hourly Data provided using the "Show Hourly Data" button." This clause is present for NYC from 25 Aug 2026 and absent on 23 Aug. The London Sep 15 text does not have it.
- Fallback and missing data: "If NOAA data for the observation date is unavailable by 11:59 PM ET on the day following the observation date, the Weather Underground Daily Observations table will be used as the resolution source. In the event that there is no data … by 11:59 PM ET on the day following the observation date, this market will resolve to the lowest bracket."
- Timing: "This market will resolve once the first data point for the following date has been published on the resolution source, or by 11:59 PM ET on the day following the observation date, whichever comes first."
- Precision is stated as "whole degrees Fahrenheit (eg, 21°F)"; London uses whole °C.
- Sources: [Gamma NYC Sep 15](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-september-15-2026); [Gamma London Sep 15](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-london-on-september-15-2026)
- The Regime B rule text itself does **not** say METAR+SPECI or that 6-hour/DSM/CLI values are excluded. Those claims in the prior note come from third parties.

**Regime C: aviationweather.gov METAR API (exact text, NYC 5/6 Nov 2026; identical structure for London, Paris LFPB, Seoul RKSI, Tokyo RJTT, Taipei RCSS, Dallas KDAL)**
- Qualifying value and SPECI: "The qualifying value is the highest temperature reported in the hourly temperature remark of any routine (METAR) observation for LaGuardia Airport (KLGA) on that date, in tenths of a degree Celsius as reported. A report whose line begins with SPECI is a special observation and does not count. Every other report is routine, including one issued off the nominal hour and one that carries no METAR or SPECI label."
- T-group definition: "The hourly temperature remark is the group beginning with the letter T followed by exactly eight digits. After the T, one digit for sign (0 positive, 1 negative) and three for tenths of a degree Celsius give the temperature; the following four are the dew point and are not used. T01390133 is 13.9°C; T10171022 is −1.7°C."
- Body fallback: "If a routine observation does not carry the hourly temperature remark, the temperature group in the body of that observation governs for that observation, in whole degrees Celsius as reported. … 18/12 is 18°C; M11/M17 is −11°C. An observation that reports no temperature in either place is disregarded."
- °F markets (US cities): "Each market in this event states its range in whole degrees Fahrenheit. The qualifying value is converted using °F = °C × 9/5 + 32 and rounded to the nearest whole degree, with a value ending in exactly half rounded up to the next higher whole degree … 18.3°C is 64.94°F and counts as 65°F; 17.8°C is 64.04°F and counts as 64°F; 19°C is 66.2°F and counts as 66°F; −22.5°C is exactly −8.5°F and counts as −8°F."
- °C markets: "…The qualifying value is rounded to the nearest whole degree, with a value ending in exactly half rounded up to the next higher whole degree … 13.9°C counts as 14°C; 17.4°C counts as 17°C; 16.5°C counts as 17°C; −1.7°C counts as −2°C; −8.5°C counts as −8°C." — [Gamma London Nov 5](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-london-on-november-5-2026)
- Day window: "An observation counts if its time stamp, converted to the station's local time (including any daylight-saving shift in effect), falls on the observation date."
- Finalisation timing: "This market will resolve at the issuance of the first METAR observation for the station on the day following the observation date or by 11:59 PM ET on the day following the observation date, whichever comes first."
- Missing data: "In the event that the Aviation Weather Center has published no routine observation reporting a temperature for the observation date by 11:59 PM ET on the day following the observation date, the Weather Underground Daily Observations table will be used as the resolution source. In the event that neither source has published data sufficient to determine a temperature … this market will resolve to the lowest bracket."
- Corrections and revisions: "The report the resolution source shows for a given observation time is the one that counts, whether or not it is marked as a correction (COR). Changes to observations within this market's timeframe will be considered until the first datapoint for the following date has been published, after which any alterations will not be considered. Where the first routine observation for the following date is published before that deadline, resolution is determined from a read taken after it. Where it is not, resolution is determined from a read taken at that deadline."
- Erroneous-data clause: "In the case that the Resolution Source publishes data … that is clearly erroneous and the result of technical or operational error, or of unauthorized interference with the Resolution Source or its data, the Market may remain open for a period of up to seven (7) calendar days (ET) … If no corrected value is published within that period, Polymarket will issue a Clarification…"
- Resolution source URL format: `https://aviationweather.gov/api/data/metar?ids=KLGA&format=raw&date=2026-11-07T08:00:00Z&hours=30`, i.e. 30 hours back from about 03:00 local of the next day.
- Sources for the above: [Gamma NYC Nov 6](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-november-6-2026); [Gamma NYC Nov 5](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-november-5-2026); [Gamma Dallas Nov 4](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-dallas-on-november-4-2026)
- The rules link a METAR primer PDF: `https://polymarket-upload.s3.us-east-2.amazonaws.com/market_products/Weather/How+to+Read+the+METAR+Report.pdf` (not fetched) — [Gamma NYC Nov 6](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-november-6-2026)

**Live AWC output showing why the SPECI rule matters (fetched 2026-11-05)**
- KLGA mixes "METAR … T01780161" hourly reports with "SPECI KLGA 050642Z … T01720161" specials. Both carry a T-group.
- RCSS shows "SPECI RCSS 050702Z … 30/21" next to routine "METAR RCSS 050700Z … 29/22". In this example the SPECI is 1 °C warmer than the adjacent routine report and is excluded under Regime C.
- EGLC, RKSI and RCSS METARs carry **no T-group** (e.g. "METAR RKSI 050730Z 27010KT CAVOK 16/11 Q1012 NOSIG"), so the body whole-°C fallback governs.
- RKSI and RCSS issue routine METARs every 30 minutes, at :00 and :30.
- Source: [AWC raw METAR API](https://aviationweather.gov/api/data/metar?ids=RKSI,KLGA,EGLC,RCSS&format=raw&hours=6)

**Hong Kong (separate regime throughout)**
- Sep 15 2026 text: "…specifically the "Absolute Daily Max (deg. C)" the specified date once information is finalized in the relevant "Daily Extract", available here: https://www.weather.gov.hk/en/cis/climat.htm"
  - Missing data: "…no data for the observation date by 11:59 PM ET on the seventh day following the observation date, this market will resolve to the lowest bracket."
  - Precision: "measures temperatures in Celsius to one decimal place (eg, 9.1°C)."
  - Revisions: "Any revisions to temperatures recorded after data is initially published … will not be considered."
  - Source: [Gamma HK Sep 15](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-hong-kong-on-september-15-2026)
- Nov 5 2026 text keeps the same base and adds:
  - "That initial publication is the revisions cutoff."
  - The 7-day clearly-erroneous clause.
  - "The only exception is a correction of a clearly erroneous print under the preceding paragraph, which will be used even if published after the cutoff."
  - The "cutoff" paragraph is present from at least 20 Oct 2026.
  - Source: [Gamma HK Nov 5](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-hong-kong-on-november-5-2026)
- Bucket questions are in whole °C (e.g. "Will the highest temperature in Hong Kong be 23°C or below on November 5?"), yet precision is 0.1 °C. How 23.5 maps to a bucket is not stated in the text — [Gamma HK Nov 5](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-hong-kong-on-november-5-2026)

### Inferences
- **US stations (Regime C):** ASOS builds the T-group by rounding the 5-minute average to whole °F and converting to the nearest 0.1 °C (see Q3). The conversion error is at most 0.05 °C ≈ 0.09 °F, so Polymarket's rounding recovers the ASOS whole-°F value exactly. The settled value is therefore the max of ASOS whole-°F values at **routine (hourly, typically :51) report times only**. That systematically misses peaks between hourly reports, in SPECIs, and in the 6-hour/24-hour groups. It is a lower bound on the NWS CLI high.
- **Non-US stations without a T-group** (RKSI, EGLC, RJTT, LFPB, RCSS as seen today): the settled value is the max of **whole-°C body temperatures** of routine reports, which are half-hourly at many Asian/European airports. The half-up rounding clause effectively applies only to T-group values.
- Regime C counts a day by **local civil time, DST included**. This differs from NWS CLI and Kalshi's local-standard-time day (1 AM–1 AM local clock time in summer).
- Backtests across 2026 must split into the three regimes. The 25 Aug "Hourly Data" clause splits Regime B further for US stations.

### Gaps
- The Regime B "Temp" column of weather.gov/wrh/timeseries: whether it included SPECIs and how it rounded/converted is not documented in the rule text. Third-party claims that it was METAR+SPECI were not verified from a primary source.
- I found no Polymarket announcement of the 23 Aug or 23 Oct rule changes, and no Gamma field logging the change.
- How a 0.1 °C HKO value maps onto whole-°C buckets (e.g. "24°C" bucket vs 24.6) is not spelled out in the text retrieved.
- The METAR primer PDF was not fetched.

---

## Q2. Polymarket fees, rebates, liquidity rewards, and UMA resolution (docs.polymarket.com + Gamma fields)

### Takeaway
Weather markets carry a taker-only fee of `fee = C × 0.05 × p × (1−p)`, at most $1.25 per 100 shares at p=0.50. Makers pay 0, and 25% of taker fees are rebated to makers, weighted by the same fee curve. Gamma marks weather markets as `feeType: weather_fees`, `feeSchedule {rate 0.05, exponent 1, takerOnly true, rebateRate 0.25}`. Resolution goes through the UMA Optimistic Oracle: typically a $750 bond, a 2-hour challenge window, and DVM escalation after two disputes, taking 4–6 days.

### Cited Findings
- Fee formula: "fee = C × feeRate × p × (1 - p)". "**Makers are never charged fees.** Only takers pay fees."
- Weather row: Taker Fee Rate 0.05 | Maker 0 | Maker Rebate 25%. The 100-share table for Weather shows $0.05 at 1¢, $0.45 at 10¢, $1.25 at 50¢.
- "Fees are rounded to 5 decimal places. The smallest fee charged is 0.00001 USDC."
- Source for the three points above: [Polymarket Fees](https://docs.polymarket.com/trading/fees.md)
- Every sampled weather market returned these Gamma fields: `"feesEnabled": true, "feeType": "weather_fees", "feeSchedule": {"exponent": 1, "rate": 0.05, "takerOnly": true, "rebateRate": 0.25}`, plus legacy `makerBaseFee: 1000, takerBaseFee: 1000`. Liquidity-reward parameters were `rewardsMinSize: 20` (50 on Jul 2026 markets), `rewardsMaxSpread: 4.5` and `holdingRewardsEnabled: false`. `umaReward` was "0.6" (Nov 2026) and "2" (Jul 2026) — [Gamma NYC Nov 6](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-november-6-2026); [Gamma London Jul 15](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-london-on-july-15-2026)
- Maker rebates:
  - "Rebates are distributed using the same formula as taker fees… rebate = (your_fee_equivalent / total_fee_equivalent) * rebate_pool. Totals are calculated per market."
  - Weather: 25%, "Fee-curve weighted". Paid daily in pUSD, minimum $1.
  - "fills on markets with a 0% taker fee (including markets temporarily made fee-free during a fee holiday) earn **no maker rebate**."
  - Source: [Polymarket Maker Rebates](https://docs.polymarket.com/programs/maker-rebates.md)
- Liquidity rewards:
  - "Rewards are distributed directly to maker addresses daily at midnight UTC."
  - The minimum payout is $1. "Each incentivized market defines a minimum qualifying order size, maximum qualifying spread, and reward allocation."
  - Endpoint: `clob.polymarket.com/rewards/markets/multi`.
  - Source: [Polymarket Liquidity Rewards](https://docs.polymarket.com/programs/liquidity-rewards.md)
- There is also a tiered taker rebate program (not read in detail) — [Taker Rebates](https://docs.polymarket.com/programs/taker-rebates.md)
- UMA resolution:
  - "Posting a bond (typically $750 pUSD)"; "a **2-hour challenge period**". "If the second proposal is also disputed, the resolution escalates to UMA's DVM".
  - Debate period 24–48 h, voting about 48 h. "Undisputed resolution: ~2 hours after proposal; Disputed resolution: 4-6 days total."
  - The Unknown/50-50 outcome redeems at $0.50.
  - Clarifications "Cannot change the fundamental intent of the question" and are published onchain via the bulletin board contract.
  - Source: [Polymarket Resolution](https://docs.polymarket.com/concepts/resolution.md)

### Inferences
- Under Regime C, the earliest finalisation is the first routine METAR of the next local day, typically just after local midnight. The rule tells proposers to read *after* that report. Add the 2-hour UMA window, so undisputed payout is roughly local 02:00–03:00 the next day.
- `umaReward` (0.6) is presumably the proposer reward in pUSD. This is not confirmed by the docs read.

### Gaps
- The meaning of legacy `makerBaseFee`/`takerBaseFee` = 1000 vs `feeSchedule` was not explained in the pages read.
- I did not find the daily reward pool size per weather market (`rewardsConfig.rate_per_day`). It would need a `clob.polymarket.com/rewards/markets/multi` query.

---

## Q3. Kalshi KXHIGH settlement (help.kalshi.com) and the CLI→TWC question

### Takeaway
The only primary Kalshi text reachable is the help article "Weather Markets" (dated July 22, 2026). It says daily high/low markets settle on the **final NWS Daily Climate Report** in **local standard time**, and that **hourly** markets settle on The Weather Company. I could not confirm from a primary source that daily KXHIGH moved to TWC in Aug 2026; kalshi.com and its API were blocked.

### Cited Findings
- Help article, verbatim: "Each weather market names its official settlement source in its market rules. Daily high/low temperature markets settle based on the final climate report issued by the National Weather Service (NWS), typically released the following morning. Hourly temperature markets settle on readings from The Weather Company." Article date shown: "July 22, 2026" — [Kalshi Help: Weather Markets](https://help.kalshi.com/en/articles/13823837-weather-markets)
- Delay conditions, verbatim: "These markets settle the next morning based on the high temperature recorded in the final NWS Daily Climate Report. Market determination may be delayed in the rare instances of a) a high temperature is not consistent with 6-hr or 24-hr highs reported by METAR or b) the final NWS Climate Report high temperature value is lower than previous preliminary report." — [Kalshi Help: Weather Markets](https://help.kalshi.com/en/articles/13823837-weather-markets)
- Climate day, verbatim: "The NWS Climate Reports (used for daily temperature markets) use local standard time when reporting daily high temperatures. This means that during Daylight Saving Time, the high temperature will be recorded between 1:00 AM and 12:59 AM local time the following day" — [Kalshi Help: Weather Markets](https://help.kalshi.com/en/articles/13823837-weather-markets)
- Hourly markets, verbatim: "They settle on the temperature at that exact time as reported by The Weather Company for the station coordinates named in the market rules (for example, KORD for Chicago)… Settlement processes approximately 25-35 minutes after the market closes… Historical readings and market data are available at weather.com/kalshi." — [Kalshi Help: Weather Markets](https://help.kalshi.com/en/articles/13823837-weather-markets)
- Kalshi's help index has no other weather-specific settlement article. Searches for "weather" and "temperature" return only article 13823837 among weather topics — [Kalshi Help search](https://help.kalshi.com/en/?q=weather)
- On Kalshi fees, the help article says only: "Kalshi makes money by charging a transaction fee on the expected earnings on the contract… In some cases, markets will have maker fees". The exact formula is in the Fee Schedule PDF, which I did not retrieve — [Kalshi Help: Fees](https://help.kalshi.com/en/articles/13823805-fees)
- The prior note's claim of a CLI→TWC switch (Aug 14 or Aug 27, 2026) for daily markets rests on secondary sources: Yahoo and Kalshi News snippets, and GitHub backtests stating that markets "now settle on The Weather Company's reading". It is **not corroborated** by the help page. That page is dated before the alleged switch and has not been updated since — [Kalshi Help: Weather Markets](https://help.kalshi.com/en/articles/13823837-weather-markets); prior claims in [GitHub MiguelTheGamer](https://github.com/MiguelTheGamer/kalshi-weather-backtest)

### Inferences
- Under the NWS regime, the Kalshi value equals the CLI max: the ASOS 5-minute running average, whole °F, over the LST day. It is therefore ≥ the Polymarket Regime C value for the same US station on a non-DST day, and usually by 0–2 °F. The two platforms also use different stations for NYC: Kalshi uses Central Park (KNYC) per the prior note, Polymarket uses KLGA.

### Gaps
- KXHIGH contract terms (CFTC filing) and current series `rules_primary`/`settlement_sources` were blocked: kalshi.com and api.elections.kalshi.com returned 403, and the S3 contract_terms PDF returned 404.
- The date and exact wording of any daily-market switch to TWC is unconfirmed.

---

## Q4. NWS: CLI definition, ASOS 5-minute average, rounding/°F→°C chain, T-group, 6-hour max group

### Takeaway
ASOS samples about every 10 s and forms 1-minute averages. Each minute it forms a 5-minute running average, rounded to **whole °F** with mid-points rounded up, then converted to the **nearest 0.1 °C**. Hourly and special METARs carry that value in the T-group; 5-minute METARs carry only whole °C. The CLI daily max is the highest 5-minute average over midnight–midnight **LST**, taken from the ASOS Daily Summary Message (DSM). The 6-hour max ("1snTxTxTx") is computed at 00/06/12/18 UTC from hourly maxima, in tenths °C.

### Cited Findings
- ASOS User's Guide, verbatim: "Once each minute the ACU calculates the 5-minute average ambient temperature and dew point temperature from the 1-minute average observations (provided at least 4 valid 1-minute averages are available). These 5-minute averages are rounded to the nearest degree Fahrenheit, converted to the nearest 0.1 degree Celsius, and reported once each minute… All mid-point temperature values are rounded up (e.g., +3.5°F rounds up to +4.0°F; -3.5°F rounds up to -3.0°F; while -3.6 °F rounds to -4.0 °F)." — [ASOS User's Guide (aum-toc.pdf)](https://www.weather.gov/media/asos/aum-toc.pdf)
- ASOS User's Guide, verbatim:
  - "At synoptic hour (00, 06, 12, and 18 UTC) reporting times, the current 6-hour maximum and minimum ambient temperatures are computed from the hourly maximum and minimum ambient temperatures in tenths of degrees Celsius, and included as remarks ("1snTxTxTx" for maximum temperature, and "2snTnTnTn" for minimum temperature)".
  - "Once each hour (at the hourly METAR report time) the current hourly ambient temperature and dew point temperature are reported in the METAR Remarks section, to the nearest tenth of a degree Celsius, in the form "TsnT'T'T'snT'dT'dT'd.""
  - "The calendar day maximum and minimum ambient temperatures are reported in the midnight, LST hourly METAR remarks (4snTxTxTx snTnTnTn)… there may occasionally be a discrepancy between … the "4" group and the daily maximum and minimum temperatures reported in the ASOS Daily Summary Message (DSM) which runs from 00:00 to 23:59 LST."
  - Source: [ASOS User's Guide](https://www.weather.gov/media/asos/aum-toc.pdf)
- ASOS QC: a 1-minute value that differs from the last valid one by >10 °F within 2 minutes is marked missing. With no valid 5-minute average for 15 minutes, no temperature is reported — [ASOS User's Guide](https://www.weather.gov/media/asos/aum-toc.pdf)
- NWS Instruction 10-1004 (Climate Records):
  - "The first mandatory issuance will be between 12:30 a.m. and 5:00 a.m. local time to capture the previous calendar day's (midnight-to-midnight Local Standard Time [LST]) data. The second mandatory issuance will be in the late afternoon/early evening (typically between 3:00 p.m. and 5:30 p.m. local time)".
  - "AWIPS Climate Program uses the ASOS Daily Summary Message (DSM) to produce the CLI… The DSM is not subject to WFO quality control. If some data entries are not available from the DSM, other sources, such as the METARs … may be used to fill in data… WFOs should correct erroneous data in the CLI. The "PRIMARY DSM XMIT TIME" will be set to 00:15 a.m. LST for each ASOS site."
  - Source: [NWS Instruction 10-1004](https://www.weather.gov/media/directives/010_pdfs/pd01010004curr.pdf)
- NWS Chicago (LOT) FAQ, verbatim:
  - "An ASOS's temperature sensor will record an air temperature reading approximately every 10 seconds in tenths of a degree Fahrenheit. These readings are averaged and stored internally by the ASOS in whole degrees Fahrenheit every minute… these 1-minute observations are then aggregated into a rolling 5-minute average temperature… (once again in whole degrees Fahrenheit)… They are also used to determine the high and low temperature for a calendar day."
  - "For 5-minute METAR observations specifically, these converted temperatures will be rounded to the nearest whole degree Celsius… actual … 80°F … converts to 26.7°C, which is then rounded to 27°C … converts back to 80.6°F, which rounds to 81°F."
  - "This is not an issue with the temperatures that are reported in hourly and special METARs as an ASOS station's recorded temperatures will be rounded to the nearest tenth of a degree Celsius prior to being disseminated in those types of METARs."
  - "The observation period for a calendar day spans from midnight to midnight local standard time… during daylight saving time spans from 1 AM to 1 AM local daylight time."
  - Source: [NWS LOT Weather Observations FAQ](https://www.weather.gov/lot/weather_observations_faq)
- The LOT FAQ also explains why raw 1-minute archives do not match the CLI: the CLI uses the 5-minute running average, not raw 1-minute values. Its example table shows raw 82 °F at 12:41 PM vs a 5-minute average of 80 °F — [NWS LOT FAQ](https://www.weather.gov/lot/weather_observations_faq)

### Inferences
- **Rebuilding values from data:**
  - CLI/Kalshi (NWS regime): max of 5-minute averages in whole °F over LST midnight–midnight. Best proxies are the CLI itself, the DSM, or the midnight-LST "4" group or synoptic "1" groups (tenths °C → whole °F) as upper-bound checks.
  - Polymarket Regime C (US): max over routine METARs only of T-group → °F, rounded half-up.
  - The gap between the two is caused by sampling (sub-hourly peaks, SPECIs, 6-h groups), not rounding.
- The prior note's "unconfirmed" Wikipedia claim is now confirmed by the ASOS User's Guide: the T-group is derived from whole °F, so whole °F is recoverable.

### Gaps
- Federal Meteorological Handbook No. 1 (FMH-1) was not retrieved. Group definitions above come from the ASOS User's Guide instead.
- The current revision date of Instruction 10-1004 was not captured beyond "supersedes … dated October 1, 2024"; the type of issuance is "Correction".

---

## Q5. IEM (mesonet.agron.iastate.edu) for global METAR/ASOS history: endpoint, parameters, raw text, SPECI flag, limits (tested)

### Takeaway
`/cgi-bin/request/asos.py` serves global METAR history, including raw text (`data=metar`), with a 1 request/second per-IP throttle and a 1,000 station-year cap per request.

**Critical caveat:** IEM's `metar` string **drops the leading "METAR"/"SPECI" word**. For non-US stations, `report_type` does **not** cleanly separate routine from special: half-hourly routine METARs at RKSI, RCSS and others are classed as "4 (Specials)". IEM alone therefore cannot apply Polymarket's "line begins with SPECI" rule. Pair it with AWC raw, or apply heuristics.

### Cited Findings
- IEM documentation, verbatim:
  - "This cgi-bin script provides METAR/ASOS data. It has a IP-based rate limit… A 503 … if the server is under heavy load. A 429 Too Many Requests response will be returned if the IP-based rate limit is exceeded."
  - Changelog: "2026-04-21: … a 1 second per-IP throttle is now in place." "2026-01-23: Added a practical limit of 1,000 station years worth of data… HTTP 422".
  - Parameters: `station`, `data` (tmpf, dwpf, relh, … metar, snowdepth), `sts`/`ets`, `year1/month1/day1…`, `hours`, `tz`, `format` (onlycomma, tdf), `missing`, `trace`, `latlon`, `elev`, `nometa`, `network`, and `report_type` ("1 (HFMETAR), 3 (Routine), 4 (Specials)").
  - "if you do not specify any stations, you can only request 24 hours of data."
  - Source: [IEM asos.py help](https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?help)
- IEM download page, verbatim:
  - "The IEM maintains an ever growing archive of automated airport weather observations from around the world!… This archive simply provides the as-is collection of historical observations, very little quality control is done."
  - "Data Sources: … Unidata IDD, NCEI ISD, and MADIS One Minute ASOS."
  - "Data is synced from the real-time ingest every 10 minutes." On report types: "When in doubt, pick both routine and specials."
  - The network list includes per-country networks (e.g. KR__ASOS), and the date selector goes back to 1928.
  - Source: [IEM ASOS download](https://mesonet.agron.iastate.edu/request/download.phtml?network=KR__ASOS)
- **Test, RKSI 30 Oct – 2 Nov 2026, `data=all`:**
  - 144 rows, half-hourly.
  - Columns: `station,valid,tmpf,dwpf,relh,drct,sknt,p01i,alti,mslp,vsby,gust,skyc1..4,skyl1..4,wxcodes,ice_accretion_1hr/3hr/6hr,peak_wind_gust,peak_wind_drct,peak_wind_time,feel,metar,snowdepth`.
  - Sample row: `RKSI,2026-10-30 00:00,57.20,53.60,…,RKSI 300000Z 13006KT 8000 NSC 14/12 Q1018 NOSIG,M`. The raw METAR is included, with no "METAR" prefix and no T-group, and `tmpf` is the body °C converted to °F (14 °C → 57.20).
  - The string "SPECI" occurs 0 times.
  - Source: [IEM asos.py RKSI query](https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=RKSI&data=all&year1=2026&month1=10&day1=30&year2=2026&month2=11&day2=2&tz=Etc/UTC&format=onlycomma)
- **report_type test, 1–3 Nov 2026:**
  - RKSI: `report_type=3` gives 48 rows (all :00); `report_type=4` gives 48 rows (all :30, e.g. "RKSI 010030Z…"). AWC shows the :30 reports as "METAR RKSI 050630Z…", i.e. routine.
  - RCSS: rt=3 gives 52 rows, rt=4 gives 40.
  - The genuine AWC "SPECI RCSS 050702Z … 30/21" appears in IEM as "RCSS 050702Z …" under rt=4 and in the default (all) query.
  - Source: [IEM asos.py RKSI rt=4](https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?data=metar&station=RKSI&sts=2026-11-01T00:00Z&ets=2026-11-03T00:00Z&format=onlycomma&report_type=4); [AWC raw](https://aviationweather.gov/api/data/metar?ids=RKSI,KLGA,EGLC,RCSS&format=raw&hours=6)
- **US station test, KLGA (IEM ID "LGA"):**
  - rt=3 returns hourly :51 reports with T-groups, e.g. "KLGA 010051Z … 14/01 … RMK AO2 SLP306 T01390011".
  - rt=4 returned one special, "KLGA 012128Z … T01440039" (no SLP).
  - The T-group is in the raw string, so tenths °C can be parsed from IEM for US stations.
  - Source: [IEM asos.py KLGA](https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?data=metar&station=KLGA&year1=2026&month1=11&day1=1&year2=2026&month2=11&day2=3&tz=Etc/UTC&format=onlycomma&report_type=3)
- EGLC, RJTT, LFPB raw strings on IEM have no T-group, e.g. "EGLC 010050Z AUTO … 09/08 Q1032" and "LFPB 010000Z AUTO … 08/07 Q1030". RJTT and LFPB report hourly at :00; EGLC at :20/:50 — [IEM asos.py](https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?help)
- Rapid back-to-back requests returned "Too many requests from your IP address, slow down." Pacing at 2–3 s per request worked. A same-day query (RCSS 06:00–08:00Z on 5 Nov) returned only the 07:02 special, not the 06:30/07:00 routine reports that AWC had. That suggests lag or incompleteness in near-real-time international ingest — observed in my test against [IEM asos.py](https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?help)

### Inferences
- Recommended rebuild for Polymarket Regime C:
  1. Pull IEM history with `report_type=3,4` (all), `data=metar,tmpf`, `tz=Etc/UTC`, one station per request, paced at ≥1 s.
  2. Parse the T-group when present, else the body temp.
  3. Classify SPECI as follows. For US ASOS, routine reports are the :51-ish hourly reports with SLP/T-groups, and IEM rt=3 is reliable. For non-US, treat reports at the station's scheduled minutes (:00/:30, :20/:50) as routine and off-schedule ones (e.g. 07:02) as SPECI candidates. Where possible, cross-check against the AWC raw API, which prints the METAR/SPECI prefix.
  4. Bucket by local civil date, DST included.
- The rule says a report with no label counts as routine. An off-schedule IEM row could be either a SPECI or an off-nominal-hour routine report, so heuristics carry residual risk on exactly the days that matter.

### Gaps
- How far back the AWC API's `date` parameter can go was not tested.
- IEM's own documentation on how it assigns report_type 3 vs 4 for non-US stations was not found. The "news item on recent changes made for report types" is linked but was not read.
- Earliest available year per station (RKSI, EGLC, RJTT, LFPB) was not queried.

---

## Q6. Hong Kong Observatory Daily Extract (HK markets)

### Takeaway
Polymarket HK markets settle on the HKO "Absolute Daily Max (deg. C)" in the "Daily Extract" linked from `https://www.weather.gov.hk/en/cis/climat.htm`, at 0.1 °C precision. The first publication is the revisions cutoff, except for a clearly-erroneous-print correction within 7 days. HKO pages were blocked from this session, so the extract's format and publication timing were not verified.

### Cited Findings
- Rule text: see Q1, Hong Kong — [Gamma HK Nov 5](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-hong-kong-on-november-5-2026); [Gamma HK Sep 15](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-hong-kong-on-september-15-2026)
- The resolution window is "once data for this date has been published on the resolution source, or by 11:59 PM ET on the seventh day following the observation date", and no data by then resolves to the lowest bracket — [Gamma HK Nov 5](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-hong-kong-on-november-5-2026)

### Inferences
- Polymarket's "Absolute Daily Max" wording suggests an extract that lists both absolute daily max and mean values. A rebuild should pull HKO's own daily data (HKO Headquarters station), not airport METAR (VHHH).

### Gaps
- The format, URL pattern, publication lag and revision practice of the HKO Daily Extract could not be checked because www.weather.gov.hk returned 403.
