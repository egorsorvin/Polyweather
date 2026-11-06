"""
Step 3e honest simulation: trade the fast-feed signal, false alarms included.

Signal: the first minute a fast feed (1-min ASOS or 5-min MADIS) shows >= hi + 1 for a US bucket.
Action: after a feed latency L (minutes), buy NO with taker prices actually traded in
        [signal + L, signal + L + 10 min] (VWAP, at most 10 % of that volume, cap $STAKE),
        only if the bucket's last YES before the signal was >= 0.05 (still alive in the market).
Outcome: NO pays $1 unless that bucket won (false alarms lose when the bucket wins).
Fees: 0.05 p (1-p) per share where enabled.
Stats: ROI, and a t-stat with standard errors clustered by city-day (bets on one day are
       not independent).

Input: data/raw/analysis/fast_feed.csv (research/fast_feed_test.py). Usage: python research/fast_feed_sim.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from nowcast_dead_buckets import event_markets, FEE_RATE  # noqa: E402

OUT = Path("data/raw/analysis")
TRADES = Path("data/raw/trades")
LATENCIES = [1, 3, 5, 10, 15]
STAKE, LIQ = 200.0, 0.10


def clustered_t(pnl, stake, cluster):
    df = pd.DataFrame({"p": pnl, "s": stake, "c": cluster}).groupby("c").sum()
    roi = df.p.sum() / df.s.sum()
    # ratio estimator: residuals per cluster
    e = df.p - roi * df.s
    se = np.sqrt((e ** 2).sum()) / df.s.sum()
    return roi, roi / se if se > 0 else np.nan, len(df)


def main():
    ff = pd.read_csv(OUT / "fast_feed.csv", dtype={"event_id": str})
    for c in ("fast1_time", "fast5_time"):
        ff[c] = pd.to_datetime(ff[c], utc=True)
    rc = pd.read_csv(OUT / "resolver_check.csv", dtype={"event_id": str}).set_index("event_id")
    markets = event_markets()
    bets = []
    for eid, g in ff.groupby("event_id"):
        f = TRADES / f"{eid}.csv.gz"
        if not f.exists():
            continue
        t = pd.read_csv(f, dtype={"condition_id": str})
        if t.empty:
            continue
        t["ts"] = pd.to_datetime(t["timestamp"], unit="s", utc=True)
        t["p_yes"] = np.where(t["outcome"] == "Yes", t["price"], 1 - t["price"])
        t["no_px"] = 1 - t["p_yes"]
        t["buy_no"] = ((t["outcome"] == "No") & (t["side"] == "BUY")) | ((t["outcome"] == "Yes") & (t["side"] == "SELL"))
        t = t.sort_values("ts")
        V = rc.loc[eid, "value"]
        hi2cid = {hi: (cid, lo, fees) for cid, (lo, hi, _u, fees) in markets.get(eid, {}).items()}
        for r in g.itertuples(index=False):
            if r.hi not in hi2cid:
                continue
            cid, lo, fees = hi2cid[r.hi]
            won = int(lo <= V <= r.hi)
            gm = t[t["condition_id"] == cid]
            for feed, sig in (("1min", r.fast1_time), ("5min", r.fast5_time)):
                if pd.isna(sig):
                    continue
                bef = gm[gm["ts"] < sig]
                if bef.empty or bef["p_yes"].iloc[-1] < 0.05:
                    continue
                for L in LATENCIES:
                    a = sig + pd.Timedelta(minutes=L)
                    w = gm[gm["buy_no"] & (gm["ts"] >= a) & (gm["ts"] < a + pd.Timedelta(minutes=10))]
                    if w.empty:
                        continue
                    usd = float((w["size"] * w["no_px"]).sum())
                    px = float((w["size"] * w["no_px"]).sum() / w["size"].sum())
                    stake = min(STAKE, LIQ * usd)
                    if stake < 1 or px >= 0.995:
                        continue
                    sh = stake / px
                    fee = FEE_RATE * px * (1 - px) * sh if fees else 0.0
                    bets.append({"event_id": eid, "city": r.city, "date": r.date, "feed": feed, "L": L,
                                 "px": px, "stake": stake, "won_no": 1 - won, "died": r.died,
                                 "pnl": sh * (1 - won) - stake - fee})
    b = pd.DataFrame(bets)
    b.to_csv(OUT / "fast_feed_bets.csv", index=False)
    b["cluster"] = b["city"] + "|" + b["date"]
    print("honest fast-feed NO strategy (false alarms included), all periods:")
    rows = []
    for (feed, L), x in b.groupby(["feed", "L"]):
        roi, t, nc = clustered_t(x.pnl, x.stake, x.cluster)
        rows.append({"feed": feed, "latency_min": L, "bets": len(x), "city_days": nc,
                     "no_hit": x.won_no.mean(), "avg_px": x.px.mean(), "staked": x.stake.sum(),
                     "pnl": x.pnl.sum(), "roi": roi, "t_clustered": t,
                     "false_alarm_share": 1 - x.died.mean()})
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    s = b[b["date"] >= "2026-04-01"]
    print("\nsince Apr-2026:")
    rows = []
    for (feed, L), x in s.groupby(["feed", "L"]):
        roi, t, nc = clustered_t(x.pnl, x.stake, x.cluster)
        rows.append({"feed": feed, "L": L, "bets": len(x), "pnl": round(x.pnl.sum()), "pnl_per_month": round(x.pnl.sum() / 7.2),
                     "roi": round(roi, 3), "t": round(t, 2)})
    print(pd.DataFrame(rows).to_string(index=False))
    x = b[(b.feed == "1min") & (b.L == 3)]
    print("\n1-min feed, latency 3 min, by city:")
    print(x.groupby("city").apply(lambda y: pd.Series({"bets": len(y), "pnl": y.pnl.sum(), "roi": y.pnl.sum() / y.stake.sum(),
                                                        "no_hit": y.won_no.mean()}), include_groups=False).round(3)
          .sort_values("pnl", ascending=False).to_string())
    print("\nby month (1-min, L=3):")
    print(x.groupby(x.date.str[:7]).apply(lambda y: pd.Series({"bets": len(y), "pnl": y.pnl.sum(), "roi": y.pnl.sum() / y.stake.sum()}),
                                          include_groups=False).round(3).to_string())


if __name__ == "__main__":
    main()
