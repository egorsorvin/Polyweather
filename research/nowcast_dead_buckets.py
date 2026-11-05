"""
Step 3 (hypothesis C): how fast does the market price "dead" buckets?

A bucket dies when the station's running daily max (by the event's own rule regime, rounded
exactly like the resolver does) exceeds the bucket's upper edge: the max can only rise, so
that bucket can no longer win and its NO is worth $1.

For every bucket that died during the local day (events where the resolver matched the actual
outcome, so death is reliable) we measure, from the trade tape:
  * obs_time: METAR observation time of the killing report (publication is a few minutes later)
  * last YES price before obs_time, and how long until YES traded <= 0.02
  * the "pie": NO bought by takers at price <= 0.98 after obs_time + delay
    profit = shares * (1 - price) - taker fee  (fee only if enabled)
    for delay = 2, 5, 10, 20 min (a bot that sees the report d minutes after observation)
  * how much NO was bought BEFORE obs_time at <= 0.98 (market anticipating: faster feeds)

Outputs: data/raw/analysis/dead_buckets.csv and printed tables.
Usage: python research/nowcast_dead_buckets.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import resolver as R  # noqa: E402

TRADES = Path("data/raw/trades")
OUT = Path("data/raw/analysis")
DELAYS_MIN = [2, 5, 10, 20]
FEE_RATE = 0.05
NO_MAX = 0.98


def event_markets():
    """event_id -> {conditionId: (lo, hi, unit, fees)}"""
    out = {}
    for line in R.EVENTS.open():
        e = json.loads(line)
        if not e["slug"].startswith("highest-temperature-in-") or not e.get("closed"):
            continue
        mk = {}
        for x in e.get("markets", []):
            b = R.parse_bucket(x.get("question", ""))
            if b:
                mk[x["conditionId"]] = (b[0], b[1], b[2], bool(x.get("feesEnabled")))
        out[str(e["id"])] = mk
    return out


def day_reports(icao, city, day, regime):
    obs = R.load_obs(icao)
    lo = day.tz_localize(R.TZ[city]).tz_convert("UTC")
    hi = (day + pd.Timedelta(days=1)).tz_localize(R.TZ[city]).tz_convert("UTC")
    x = obs[(obs["valid"] >= lo) & (obs["valid"] < hi)]
    if regime == "AWC":
        x = x[x["routine"]]
    return x.sort_values("valid"), lo


def main():
    chk = pd.read_csv(OUT / "resolver_check.csv", dtype={"event_id": str})
    chk = chk[chk["match"] == True]  # noqa: E712
    markets = event_markets()
    rows = []
    for k, r in enumerate(chk.itertuples(index=False)):
        f = TRADES / f"{r.event_id}.csv.gz"
        if not f.exists() or r.event_id not in markets:
            continue
        day = pd.Timestamp(r.date)
        rep, day_start = day_reports(r.station, r.city, day, r.regime)
        if rep.empty:
            continue
        unit = r.unit
        vals = rep["temp_c"].map(lambda c: R.half_up(c * 9 / 5 + 32) if unit == "F" else R.half_up(c))
        runmax = vals.cummax().values
        times = rep["valid"].values
        t = pd.read_csv(f, dtype={"condition_id": str})
        if t.empty:
            continue
        t["ts"] = pd.to_datetime(t["timestamp"], unit="s", utc=True)
        t["p_yes"] = np.where(t["outcome"] == "Yes", t["price"], 1 - t["price"])
        t["no_px"] = 1 - t["p_yes"]
        t["buy_no"] = ((t["outcome"] == "No") & (t["side"] == "BUY")) | ((t["outcome"] == "Yes") & (t["side"] == "SELL"))
        t = t.sort_values("ts")
        for cid, (lo, hi, _u, fees) in markets[r.event_id].items():
            if hi >= 10**5:
                continue                      # upper tail never dies
            idx = np.argmax(runmax > hi) if (runmax > hi).any() else None
            if idx is None:
                continue                      # bucket stayed alive all day
            obs_time = pd.Timestamp(times[idx]).tz_localize("UTC") if pd.Timestamp(times[idx]).tzinfo is None else pd.Timestamp(times[idx])
            g = t[t["condition_id"] == cid]
            if g.empty:
                continue
            before = g[g["ts"] < obs_time]
            p_before = float(before["p_yes"].iloc[-1]) if len(before) else np.nan
            age_before = (obs_time - before["ts"].iloc[-1]).total_seconds() / 60 if len(before) else np.nan
            after = g[g["ts"] >= obs_time]
            dead_px = after[after["p_yes"] <= 0.02]
            t_to_002 = (dead_px["ts"].iloc[0] - obs_time).total_seconds() / 60 if len(dead_px) else np.nan
            row = {"event_id": r.event_id, "city": r.city, "date": r.date, "regime": r.regime,
                   "lo": lo, "hi": hi, "fees": fees,
                   "obs_local_h": (obs_time - day_start).total_seconds() / 3600,
                   "p_yes_before": p_before, "age_before_min": age_before, "min_to_yes_002": t_to_002}
            nb = g[g["buy_no"] & (g["no_px"] <= NO_MAX)]
            pre = nb[(nb["ts"] < obs_time) & (nb["ts"] >= obs_time - pd.Timedelta(hours=1))]
            row["pre_usd"] = float((pre["size"] * pre["no_px"]).sum())
            for dmin in DELAYS_MIN:
                w = nb[nb["ts"] >= obs_time + pd.Timedelta(minutes=dmin)]
                prof = w["size"] * (1 - w["no_px"])
                fee = FEE_RATE * w["no_px"] * (1 - w["no_px"]) * w["size"] if fees else 0 * w["size"]
                row[f"pie_profit_{dmin}"] = float((prof - fee).sum())
                row[f"pie_usd_{dmin}"] = float((w["size"] * w["no_px"]).sum())
            rows.append(row)
        if (k + 1) % 2000 == 0:
            print(f"  {k+1}/{len(chk)} events", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "dead_buckets.csv", index=False)
    df["month"] = df["date"].str[:7]
    print(f"\ndead buckets: {len(df)} in {df.event_id.nunique()} events")
    alive = df[df["p_yes_before"].notna()]
    print("\nYES price just before the killing report (how surprised was the market):")
    print(alive["p_yes_before"].describe(percentiles=[.5, .75, .9, .95]).round(3).to_string())
    print("share of dead buckets with YES >= 0.05 just before:", round((alive.p_yes_before >= .05).mean(), 3))
    s = df[df["p_yes_before"] >= 0.05]
    print("\nfor those (YES >= 0.05 before): minutes from observation until YES trades <= 0.02:")
    print(s["min_to_yes_002"].describe(percentiles=[.1, .25, .5, .75, .9]).round(1).to_string())
    tot = {d: (df[f"pie_profit_{d}"].sum(), df[f"pie_usd_{d}"].sum()) for d in DELAYS_MIN}
    print("\nPIE: profit taken by takers buying dead NO <= 0.98 after obs + delay (all events)")
    for d, (p, u) in tot.items():
        print(f"  delay {d:2d} min: profit ${p:,.0f} on ${u:,.0f} spent")
    print(f"  NO bought <= 0.98 in the hour BEFORE the report: ${df['pre_usd'].sum():,.0f} (anticipation)")
    for d in (2, 5):
        g = df.groupby("month")[f"pie_profit_{d}"].sum().round(0)
        print(f"\npie profit by month, delay {d} min:")
        print(g.to_string())
    c = df.groupby("city").agg(dead=("event_id", "size"), pie5=("pie_profit_5", "sum"),
                               pie2=("pie_profit_2", "sum"), med_min=("min_to_yes_002", "median"),
                               surprised=("p_yes_before", lambda x: (x >= .05).mean()))
    print("\nby city (sorted by pie at 5 min):")
    print(c.sort_values("pie5", ascending=False).round(2).head(30).to_string())
    h = df.assign(hour=df["obs_local_h"].astype(int)).groupby("hour")["pie_profit_5"].sum().round(0)
    print("\npie (5 min) by local hour of the killing report:")
    print(h.to_string())


if __name__ == "__main__":
    main()
