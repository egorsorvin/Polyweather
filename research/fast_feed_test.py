"""
Step 3e: can a fast observation feed beat the market on "killed" buckets? (US stations first)

For US °F markets a bucket [lo, hi] dies when the settlement value exceeds hi. Fast feeds:
  * 1-minute ASOS (IEM archive asos1min.py, whole °F — the same sensor ASOS builds METAR from)
  * MADIS 5-minute (already in data/raw/metar, IEM report type 1, T-group tenths °C)
For every killed bucket in US events (resolver-matched) we compare, on one clock:
  fast_time   first minute the fast feed shows a value >= hi + 1 on that local day
  obs_time    observation time of the routine METAR that actually killed it
  mkt_time    first trade with YES <= 0.05 (market has priced the kill)
and count FALSE ALARMS: days where the fast feed touched >= hi + 1 but the bucket never died.

Pie for a fast trader: NO bought by takers at <= 0.98 after fast_time + 1 min (we could have
been those takers), minus taker fee. Note: the IEM 1-minute archive is not real-time; in live
trading the same data must come from a real-time source (ASOS phone/OMO lines, paid feeds).

Writes data/raw/fast1min/<STATION>.csv.gz and data/raw/analysis/fast_feed.csv.
Usage: python research/fast_feed_test.py
"""
import csv
import gzip
import io
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
import resolver as R  # noqa: E402
from nowcast_dead_buckets import event_markets, day_reports, FEE_RATE  # noqa: E402

OUT = Path("data/raw/analysis")
FAST = Path("data/raw/fast1min")
TRADES = Path("data/raw/trades")
IEM1 = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos1min.py"


def fetch_1min(icao: str, start: date, end: date) -> pd.DataFrame:
    path = FAST / f"{icao}.csv.gz"
    if path.exists():
        return pd.read_csv(path, parse_dates=["valid"])
    FAST.mkdir(parents=True, exist_ok=True)
    rows = []
    d = start.replace(day=1)
    while d <= end:
        nxt = (d + timedelta(days=32)).replace(day=1)
        params = {"station": icao[1:], "vars": "tmpf", "sts": f"{d}T00:00Z", "ets": f"{nxt}T00:00Z",
                  "sample": "1min", "what": "download", "delim": "comma", "gis": "no"}
        for attempt in range(5):
            try:
                r = requests.get(IEM1, params=params, timeout=300)
                r.raise_for_status()
                break
            except Exception as e:
                print(f"   retry {icao} {d}: {e}")
                time.sleep(5 * (attempt + 1))
        for x in csv.DictReader(io.StringIO(r.text)):
            if x.get("tmpf") not in (None, "", "M"):
                rows.append((x["valid(UTC)"], float(x["tmpf"])))
        time.sleep(1.1)
        d = nxt
    df = pd.DataFrame(rows, columns=["valid", "tmpf"])
    df["valid"] = pd.to_datetime(df["valid"])
    with gzip.open(path, "wt") as f:
        df.to_csv(f, index=False)
    print(f"  {icao}: {len(df)} one-minute values")
    return df


def main():
    chk = pd.read_csv(OUT / "resolver_check.csv", dtype={"event_id": str})
    chk = chk[(chk["match"] == True) & (chk["unit"] == "F") & chk["station"].str.startswith("K", na=False)]  # noqa: E712
    markets = event_markets()
    rows = []
    for icao, g in chk.groupby("station"):
        start, end = date.fromisoformat(g["date"].min()), date.fromisoformat(g["date"].max())
        one = fetch_1min(icao, start, end)
        one["valid"] = one["valid"].dt.tz_localize("UTC")
        obs = R.load_obs(icao)
        madis = None
        path = R.METAR / f"{icao}.csv.gz"
        mrows = []
        with gzip.open(path, "rt", newline="") as f:
            for x in csv.DictReader(f):
                if x["rtype"] == "1":
                    t, _ = R.report_temp_c(x["metar"])
                    if t is not None:
                        mrows.append((x["valid_utc"], R.half_up(t * 9 / 5 + 32)))
        madis = pd.DataFrame(mrows, columns=["valid", "tf"])
        madis["valid"] = pd.to_datetime(madis["valid"], utc=True)
        madis = madis.sort_values("valid")
        for r in g.itertuples(index=False):
            day = pd.Timestamp(r.date)
            rep, day_start = day_reports(icao, r.city, day, r.regime)
            if len(rep) < 12:
                continue
            day_end = day_start + pd.Timedelta(days=1)
            vals = rep["temp_c"].map(lambda c: R.half_up(c * 9 / 5 + 32)).values
            runmax, times = np.maximum.accumulate(vals), rep["valid"].values
            o1 = one[(one["valid"] >= day_start) & (one["valid"] < day_end)]
            m5 = madis[(madis["valid"] >= day_start) & (madis["valid"] < day_end)]
            if o1.empty:
                continue
            f = TRADES / f"{r.event_id}.csv.gz"
            t = pd.read_csv(f, dtype={"condition_id": str}) if f.exists() else pd.DataFrame()
            if not t.empty:
                t["ts"] = pd.to_datetime(t["timestamp"], unit="s", utc=True)
                t["p_yes"] = np.where(t["outcome"] == "Yes", t["price"], 1 - t["price"])
                t["no_px"] = 1 - t["p_yes"]
                t["buy_no"] = ((t["outcome"] == "No") & (t["side"] == "BUY")) | ((t["outcome"] == "Yes") & (t["side"] == "SELL"))
                t = t.sort_values("ts")
            for cid, (lo, hi, _u, fees) in markets.get(r.event_id, {}).items():
                if hi >= 10**5 or lo <= -10**5 and hi < vals.min():
                    continue
                died = bool((runmax > hi).any())
                hit1 = o1[o1["tmpf"] >= hi + 1]
                hit5 = m5[m5["tf"] >= hi + 1]
                if not died and hit1.empty and hit5.empty:
                    continue
                rec = {"event_id": r.event_id, "city": r.city, "date": r.date, "hi": hi, "died": died,
                       "fast1_time": hit1["valid"].iloc[0] if len(hit1) else pd.NaT,
                       "fast5_time": hit5["valid"].iloc[0] if len(hit5) else pd.NaT,
                       "obs_time": pd.Timestamp(times[np.argmax(runmax > hi)], tz="UTC") if died else pd.NaT}
                if not t.empty:
                    gm = t[t["condition_id"] == cid]
                    ref = rec["fast1_time"] if pd.notna(rec["fast1_time"]) else rec["obs_time"]
                    if pd.notna(ref) and len(gm):
                        bef = gm[gm["ts"] < ref]
                        rec["p_yes_before_fast"] = float(bef["p_yes"].iloc[-1]) if len(bef) else np.nan
                        mv = gm[(gm["ts"] >= ref - pd.Timedelta(hours=1)) & (gm["p_yes"] <= 0.05)]
                        rec["mkt_time"] = mv["ts"].iloc[0] if len(mv) else pd.NaT
                        if died and pd.notna(rec["fast1_time"]):
                            w = gm[gm["buy_no"] & (gm["no_px"] <= 0.98) & (gm["ts"] >= rec["fast1_time"] + pd.Timedelta(minutes=1))]
                            fee = FEE_RATE * w["no_px"] * (1 - w["no_px"]) * w["size"] if fees else 0 * w["size"]
                            rec["pie_fast"] = float((w["size"] * (1 - w["no_px"]) - fee).sum())
                            w2 = w[w["ts"] < rec["obs_time"] + pd.Timedelta(minutes=5)]
                            fee2 = FEE_RATE * w2["no_px"] * (1 - w2["no_px"]) * w2["size"] if fees else 0 * w2["size"]
                            rec["pie_fast_before_metar"] = float((w2["size"] * (1 - w2["no_px"]) - fee2).sum())
                rows.append(rec)
        print(f"{icao}: {len(g)} events done", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "fast_feed.csv", index=False)
    for c in ("fast1_time", "fast5_time", "obs_time", "mkt_time"):
        df[c] = pd.to_datetime(df[c], utc=True)
    d = df[df["died"]]
    m = lambda a, b: (d[a] - d[b]).dt.total_seconds() / 60  # noqa: E731
    print(f"\nUS killed buckets: {len(d)}")
    print("minutes the fast feed was AHEAD of the killing METAR observation (obs - fast):")
    print("  1-min:", m("obs_time", "fast1_time").describe(percentiles=[.25, .5, .75]).round(1).to_dict())
    print("  5-min:", m("obs_time", "fast5_time").describe(percentiles=[.25, .5, .75]).round(1).to_dict())
    s = d[d["p_yes_before_fast"] >= 0.05]
    lead = (s["mkt_time"] - s["fast1_time"]).dt.total_seconds() / 60
    print(f"\nsurprised kills (YES >= 0.05 just before the 1-min signal): {len(s)}")
    print("minutes from 1-min signal to market pricing it (mkt - fast1):",
          lead.describe(percentiles=[.1, .25, .5, .75, .9]).round(1).to_dict())
    print("share where market moved BEFORE the 1-min signal:", round((lead < 0).mean(), 3))
    alarms = df[~df["died"] & df["fast1_time"].notna()]
    sig = df[df["fast1_time"].notna()]
    print(f"\nfalse alarms: 1-min feed touched hi+1 but bucket never died: {len(alarms)} of {len(sig)} "
          f"signals ({len(alarms) / max(len(sig), 1):.1%})")
    a5 = df[~df["died"] & df["fast5_time"].notna()]
    s5 = df[df["fast5_time"].notna()]
    print(f"false alarms 5-min: {len(a5)} of {len(s5)} ({len(a5) / max(len(s5), 1):.1%})")
    print(f"\npie for a trader acting 1 min after the 1-min signal: ${d['pie_fast'].sum():,.0f} "
          f"(of which before METAR+5min: ${d['pie_fast_before_metar'].sum():,.0f})")
    print("by city:")
    print(d.groupby("city")[["pie_fast", "pie_fast_before_metar"]].sum().round(0).sort_values("pie_fast", ascending=False).to_string())
    since = d[d["date"] >= "2026-04-01"]
    print(f"since Apr-2026: ${since['pie_fast'].sum():,.0f} (~${since['pie_fast'].sum() / 7.2:,.0f}/month)")


if __name__ == "__main__":
    main()
