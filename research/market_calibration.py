"""
Recon step 3: how well calibrated are Polymarket temperature markets?

For every closed "highest temperature" event with a downloaded trade tape:
  - every bucket market's outcome (did YES win?) from Gamma outcomePrices
  - the market-implied P(YES) at fixed LOCAL times around the target day
    (Gamma endDate is a nominal 12:00 UTC for every city, so it is useless as
    an anchor), taken as the last trade price (No trades converted to 1 - p),
    only if that trade is fresh (within MAX_STALE_H hours of the snapshot)

Outputs (data/raw/analysis/):
  snapshots.csv      one row per (market, horizon): price, outcome, city, ...
and prints:
  - calibration table: implied prob bin -> realised frequency
  - naive "buy YES at last price" return per price bin, before/after taker fee
  - same split by horizon and by city

Usage: python research/market_calibration.py
"""
import gzip
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

EVENTS = Path("data/raw/events.jsonl")
TRADES = Path("data/raw/trades")
OUT = Path("data/raw/analysis")
# snapshot label -> hours relative to local midnight starting the target day D
SNAPS = {"D-1 12:00": -12, "D-1 18:00": -6, "D 00:00": 0, "D 09:00": 9, "D 12:00": 12, "D 15:00": 15}
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]
TZ = {
    "london": "Europe/London", "nyc": "America/New_York", "new-york-city": "America/New_York",
    "dc": "America/New_York", "seoul": "Asia/Seoul", "busan": "Asia/Seoul",
    "hong-kong": "Asia/Hong_Kong", "shanghai": "Asia/Shanghai", "beijing": "Asia/Shanghai",
    "shenzhen": "Asia/Shanghai", "chengdu": "Asia/Shanghai", "chongqing": "Asia/Shanghai",
    "guangzhou": "Asia/Shanghai", "wuhan": "Asia/Shanghai", "qingdao": "Asia/Shanghai",
    "zhengzhou": "Asia/Shanghai", "jinan": "Asia/Shanghai", "taipei": "Asia/Taipei",
    "tokyo": "Asia/Tokyo", "singapore": "Asia/Singapore", "kuala-lumpur": "Asia/Kuala_Lumpur",
    "jakarta": "Asia/Jakarta", "manila": "Asia/Manila", "lucknow": "Asia/Kolkata",
    "karachi": "Asia/Karachi", "jeddah": "Asia/Riyadh", "dubai": "Asia/Dubai",
    "tel-aviv": "Asia/Jerusalem", "ankara": "Europe/Istanbul", "istanbul": "Europe/Istanbul",
    "moscow": "Europe/Moscow", "paris": "Europe/Paris", "madrid": "Europe/Madrid",
    "munich": "Europe/Berlin", "milan": "Europe/Rome", "amsterdam": "Europe/Amsterdam",
    "warsaw": "Europe/Warsaw", "helsinki": "Europe/Helsinki", "cape-town": "Africa/Johannesburg",
    "lagos": "Africa/Lagos", "wellington": "Pacific/Auckland", "toronto": "America/Toronto",
    "miami": "America/New_York", "atlanta": "America/New_York", "chicago": "America/Chicago",
    "dallas": "America/Chicago", "houston": "America/Chicago", "austin": "America/Chicago",
    "denver": "America/Denver", "phoenix": "America/Phoenix", "seattle": "America/Los_Angeles",
    "los-angeles": "America/Los_Angeles", "san-francisco": "America/Los_Angeles",
    "mexico-city": "America/Mexico_City", "panama-city": "America/Panama",
    "buenos-aires": "America/Argentina/Buenos_Aires", "sao-paulo": "America/Sao_Paulo",
}


def target_date(slug: str, end_iso: str):
    m = re.search(r"-on-([a-z]+)-(\d+)(?:-(\d{4}))?", slug)
    if not m or m.group(1) not in MONTHS:
        return None  # one-off events such as "...-on-inauguration-day"
    month, day = MONTHS.index(m.group(1)) + 1, int(m.group(2))
    year = int(m.group(3)) if m.group(3) else int(end_iso[:4])
    if not m.group(3) and month == 12 and end_iso[5:7] == "01":
        year -= 1
    return pd.Timestamp(year=year, month=month, day=day)
MAX_STALE_H = 3.0
FEE_RATE = 0.05          # weather feeSchedule: rate 0.05, exponent 1, taker only
BINS = [0, .02, .05, .1, .2, .3, .4, .5, .6, .7, .8, .9, .95, .98, 1.0001]


def taker_fee_per_share(p):
    return FEE_RATE * p * (1 - p)


def load_events() -> dict:
    out = {}
    for line in EVENTS.open():
        e = json.loads(line)
        m = re.match(r"highest-temperature-in-(.+?)-on-", e["slug"])
        if not m or not e.get("closed"):
            continue
        markets = {}
        for mk in e.get("markets", []):
            try:
                prices = json.loads(mk.get("outcomePrices") or "[]")
                yes_final = float(prices[0])
            except Exception:
                continue
            if yes_final not in (0.0, 1.0):
                continue  # unresolved / disputed
            markets[mk["conditionId"]] = {
                "won": int(yes_final == 1.0),
                "question": mk.get("question", ""),
                "fees": bool(mk.get("feesEnabled")),
            }
        if markets:
            city = m.group(1)
            if city not in TZ:
                continue
            td = target_date(e["slug"], e["endDate"])
            if td is None:
                continue
            d0 = td.tz_localize(TZ[city]).tz_convert("UTC")
            out[e["id"]] = {"city": city, "d0_utc": d0, "markets": markets}
    return out


def snapshots_for_event(eid: str, ev: dict) -> list:
    f = TRADES / f"{eid}.csv.gz"
    t = pd.read_csv(f, dtype={"condition_id": str})
    if t.empty:
        return []
    t["ts"] = pd.to_datetime(t["timestamp"], unit="s", utc=True)
    t["p_yes"] = np.where(t["outcome"] == "Yes", t["price"], 1 - t["price"])
    t = t.sort_values("ts")
    rows = []
    for cid, g in t.groupby("condition_id"):
        mk = ev["markets"].get(cid)
        if mk is None:
            continue
        ts = g["ts"].values
        for label, off in SNAPS.items():
            snap = ev["d0_utc"] + pd.Timedelta(hours=off)
            i = np.searchsorted(ts, np.datetime64(snap.tz_convert(None)), side="right") - 1
            if i < 0:
                continue
            age_h = (snap.tz_convert(None) - pd.Timestamp(ts[i])).total_seconds() / 3600
            if age_h > MAX_STALE_H:
                continue
            rows.append({
                "event_id": eid, "city": ev["city"], "d0_utc": ev["d0_utc"], "condition_id": cid,
                "snap": label, "p": float(g["p_yes"].iloc[i]), "won": mk["won"],
                "fees": mk["fees"], "age_h": round(age_h, 2),
            })
    return rows


def report(s: pd.DataFrame, title: str):
    s = s.copy()
    s["bin"] = pd.cut(s["p"], BINS, right=False)
    s["fee"] = taker_fee_per_share(s["p"])
    s["pnl"] = s["won"] - s["p"]               # per share, buy YES at p
    s["pnl_fee"] = s["pnl"] - s["fee"]
    g = s.groupby("bin", observed=True).agg(
        n=("won", "size"), p_mean=("p", "mean"), freq=("won", "mean"),
        ret_per_usd=("pnl", lambda x: x.sum() / s.loc[x.index, "p"].sum()),
        ret_fee_per_usd=("pnl_fee", lambda x: x.sum() / s.loc[x.index, "p"].sum()),
    )
    g["se_freq"] = np.sqrt(g["freq"] * (1 - g["freq"]) / g["n"])
    print(f"\n=== {title}  (n={len(s)}, events={s.event_id.nunique()}) ===")
    print(g.round(4).to_string())
    brier = ((s["p"] - s["won"]) ** 2).mean()
    print(f"Brier={brier:.4f}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events = load_events()
    have = {p.name.split(".")[0] for p in TRADES.glob("*.csv.gz")}
    ids = [eid for eid in events if eid in have]
    print(f"{len(ids)} closed events with trade tapes")
    rows = []
    for k, eid in enumerate(ids):
        rows.extend(snapshots_for_event(eid, events[eid]))
        if (k + 1) % 1000 == 0:
            print(f"  {k+1}/{len(ids)}")
    s = pd.DataFrame(rows)
    s.to_csv(OUT / "snapshots.csv", index=False)

    for label in SNAPS:
        report(s[s.snap == label], f"snapshot {label} local")

    # per-event sum of bucket prices (overround) at 24h
    s24 = s[s.snap == "D-1 12:00"]
    cov = s24.groupby("event_id").agg(n=("p", "size"), total=("p", "sum"))
    full = cov[cov.n >= 5]
    print(f"\nsum of last prices per event @D-1 12:00 (events with >=5 fresh buckets): "
          f"median={full.total.median():.3f}, IQR={full.total.quantile(.25):.3f}..{full.total.quantile(.75):.3f}")

    # by city @D-1 12:00: Brier of market, and longshot/favourite returns
    c = s24.assign(pnl=s24.won - s24.p).groupby("city").agg(
        n=("p", "size"), events=("event_id", "nunique"),
        brier=("p", lambda x: ((x - s24.loc[x.index, "won"]) ** 2).mean()),
        ret_lt10=("pnl", lambda x: x[s24.loc[x.index, "p"] < .10].sum() / max(s24.loc[x.index][s24.loc[x.index, "p"] < .10].p.sum(), 1e-9)),
        ret_gt50=("pnl", lambda x: x[s24.loc[x.index, "p"] > .50].sum() / max(s24.loc[x.index][s24.loc[x.index, "p"] > .50].p.sum(), 1e-9)),
    ).sort_values("events", ascending=False)
    print("\n=== by city @D-1 12:00 ===")
    print(c.round(3).to_string())


if __name__ == "__main__":
    main()
