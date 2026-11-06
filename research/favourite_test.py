"""
Step 2: is the favourite-overpricing effect (Qiu & Qiu, arXiv 2610.13593) tradeable?

Strategy simulated on the real trade tape:
  at local time T on the target day, take the event's favourite bucket (last YES trade
  price in [P_LO, P_HI], trade not older than 2 h) and BUY NO on it.

Execution, deliberately conservative:
  entry = VWAP of NO actually bought by takers in [T, T + 30 min]
          (taker BUY of No, or taker SELL of Yes at 1 - p)
  size  = min(STAKE, 10 % of the USD taker volume on that side in the window)
  fee   = feeSchedule 0.05 * p * (1 - p) per share, only if the market had fees enabled
  outcome from the resolved bucket.

Also runs the mirror (BUY YES on the favourite) as a sanity check.

Outputs: data/raw/analysis/favourite_trades.csv and printed tables.
Usage: python research/favourite_test.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from resolver import TZ, ALIASES, target_date  # noqa: E402

EVENTS = Path("data/raw/events.jsonl")
TRADES = Path("data/raw/trades")
OUT = Path("data/raw/analysis")
SNAP_HOURS = [6, 9, 11, 12, 13]       # local time on the target day
P_LO, P_HI = 0.75, 0.95
WINDOW_MIN = 30
MAX_AGE_H = 2.0
STAKE = 100.0                         # USD per bet before the liquidity cap
LIQ_SHARE = 0.10
FEE_RATE = 0.05


def load_events():
    out = {}
    for line in EVENTS.open():
        e = json.loads(line)
        m = re.match(r"highest-temperature-in-(.+?)-on-", e["slug"])
        if not m or not e.get("closed"):
            continue
        city = ALIASES.get(m.group(1), m.group(1))
        day = target_date(e["slug"], e["endDate"])
        if day is None or city not in TZ:
            continue
        mk = {}
        for x in e.get("markets", []):
            try:
                yes = float(json.loads(x.get("outcomePrices") or "[]")[0])
            except Exception:
                continue
            if yes in (0.0, 1.0):
                mk[x["conditionId"]] = {"won": int(yes == 1.0), "fees": bool(x.get("feesEnabled"))}
        if mk:
            out[e["id"]] = {"city": city, "day": day, "markets": mk}
    return out


def simulate_event(eid, ev):
    t = pd.read_csv(TRADES / f"{eid}.csv.gz", dtype={"condition_id": str})
    if t.empty:
        return []
    t["ts"] = pd.to_datetime(t["timestamp"], unit="s", utc=True)
    t["p_yes"] = np.where(t["outcome"] == "Yes", t["price"], 1 - t["price"])
    # price paid per share for the side the taker acquired
    buy_no = ((t["outcome"] == "No") & (t["side"] == "BUY")) | ((t["outcome"] == "Yes") & (t["side"] == "SELL"))
    buy_yes = ((t["outcome"] == "Yes") & (t["side"] == "BUY")) | ((t["outcome"] == "No") & (t["side"] == "SELL"))
    t["no_px"] = np.where(t["outcome"] == "No", t["price"], 1 - t["price"])
    t["yes_px"] = 1 - t["no_px"]
    t["usd_no"] = t["size"] * t["no_px"]
    t["usd_yes"] = t["size"] * t["yes_px"]
    t = t.sort_values("ts")
    d0 = ev["day"].tz_localize(TZ[ev["city"]])
    rows = []
    for h in SNAP_HOURS:
        T = (d0 + pd.Timedelta(hours=h)).tz_convert("UTC")
        before = t[(t["ts"] <= T) & (t["ts"] > T - pd.Timedelta(hours=MAX_AGE_H))]
        if before.empty:
            continue
        last = before.groupby("condition_id")["p_yes"].last()
        last = last[last.index.isin(ev["markets"].keys())]
        if last.empty:
            continue
        cid, p_last = last.idxmax(), float(last.max())
        if not (P_LO <= p_last <= P_HI):
            continue
        win = t[(t["condition_id"] == cid) & (t["ts"] > T) & (t["ts"] <= T + pd.Timedelta(minutes=WINDOW_MIN))]
        mk = ev["markets"][cid]
        for side, mask, pxcol, usdcol, wins in (
            ("NO", buy_no, "no_px", "usd_no", 1 - mk["won"]),
            ("YES", buy_yes, "yes_px", "usd_yes", mk["won"]),
        ):
            w = win[mask.loc[win.index]]
            if w.empty:
                continue
            vol = float(w[usdcol].sum())
            px = float((w[pxcol] * w["size"]).sum() / w["size"].sum())
            stake = min(STAKE, LIQ_SHARE * vol)
            if stake < 1 or not (0 < px < 1):
                continue
            shares = stake / px
            fee = FEE_RATE * px * (1 - px) * shares if mk["fees"] else 0.0
            pnl = shares * wins - stake - fee
            rows.append({"event_id": eid, "city": ev["city"], "day": ev["day"].date().isoformat(),
                         "hour": h, "side": side, "p_yes_last": p_last, "entry": px,
                         "stake": stake, "fee": fee, "won": wins, "pnl": pnl,
                         "window_usd": vol, "fees_on": mk["fees"]})
    return rows


def summary(df, by):
    g = df.groupby(by).apply(lambda x: pd.Series({
        "bets": len(x), "hit": x["won"].mean(), "avg_entry": x["entry"].mean(),
        "staked": x["stake"].sum(), "pnl": x["pnl"].sum(),
        "roi": x["pnl"].sum() / x["stake"].sum(),
        "t": (x["pnl"] / x["stake"]).mean() / ((x["pnl"] / x["stake"]).std(ddof=1) / np.sqrt(len(x)))
        if len(x) > 2 else np.nan,
    }), include_groups=False)
    return g.round(3)


def main():
    events = load_events()
    have = {p.name.split(".")[0] for p in TRADES.glob("*.csv.gz")}
    ids = [e for e in events if e in have]
    rows = []
    for k, eid in enumerate(ids):
        rows.extend(simulate_event(eid, events[eid]))
        if (k + 1) % 2000 == 0:
            print(f"  {k+1}/{len(ids)}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "favourite_trades.csv", index=False)
    df["month"] = df["day"].str[:7]
    for side in ("NO", "YES"):
        x = df[df["side"] == side]
        print(f"\n===== BUY {side} on favourite (YES last {P_LO}-{P_HI}) =====")
        print("by local hour:")
        print(summary(x, "hour").to_string())
        print("by month (all hours):")
        print(summary(x, "month").to_string())
        print("by fee regime:")
        print(summary(x, "fees_on").to_string())
    x = df[df["side"] == "NO"]
    c = summary(x, "city")
    print("\nBUY NO by city (>= 30 bets), sorted by roi:")
    print(c[c["bets"] >= 30].sort_values("roi", ascending=False).to_string())


if __name__ == "__main__":
    main()
