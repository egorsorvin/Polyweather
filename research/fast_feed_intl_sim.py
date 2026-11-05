"""
Step 3f: the fast-feed test for Tokyo (JMA AMeDAS Haneda, 10-min) and Singapore (NEA Changi, 1-min).

Same honest simulation as research/fast_feed_sim.py:
  signal  = first fast-feed value (rounded half-up to whole °C) >= hi + 1 on the local day
  action  = after latency L, buy NO at taker VWAP in [signal + L, + 10 min] (100 % of that
            volume = capacity upper bound, and a conservative 10 % / $200 variant)
            only if the bucket's last YES before the signal was >= 0.05
  outcome = NO pays unless the bucket won; false alarms included; fees; t clustered by day.
For JMA the 10-min value is stamped at the END of its interval.

Usage: python research/fast_feed_intl_sim.py   (needs research/fetch_fast_intl.py output)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import resolver as R  # noqa: E402
from nowcast_dead_buckets import event_markets, day_reports, FEE_RATE  # noqa: E402
from fast_feed_sim import clustered_t  # noqa: E402

OUT = Path("data/raw/analysis")
TRADES = Path("data/raw/trades")
FASTDIR = Path("data/raw/fast_intl")
LATENCIES = [1, 3, 5, 10, 15, 20]


def main():
    chk = pd.read_csv(OUT / "resolver_check.csv", dtype={"event_id": str})
    CITIES = sys.argv[1:] or ["tokyo", "singapore"]
    chk = chk[(chk["match"] == True) & chk["city"].isin(CITIES)]  # noqa: E712
    markets = event_markets()
    sig_rows, bets = [], []
    for city, g in chk.groupby("city"):
        fast = pd.read_csv(FASTDIR / f"{city}.csv.gz")
        fast["valid"] = pd.to_datetime(fast["valid_utc"], utc=True)
        fast = fast.sort_values("valid").drop_duplicates("valid")
        fast["v"] = fast["temp_c"].map(R.half_up)
        for r in g.itertuples(index=False):
            day = pd.Timestamp(r.date)
            rep, day_start = day_reports(r.station, city, day, r.regime)
            if len(rep) < 12:
                continue
            vals = rep["temp_c"].map(R.half_up).values
            runmax, times = np.maximum.accumulate(vals), rep["valid"].values
            fd = fast[(fast["valid"] >= day_start) & (fast["valid"] < day_start + pd.Timedelta(days=1))]
            if len(fd) < 20:
                continue
            f = TRADES / f"{r.event_id}.csv.gz"
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
            V = int(r.value)
            for cid, (lo, hi, _u, fees) in markets.get(r.event_id, {}).items():
                if hi >= 10**5:
                    continue
                died = bool((runmax > hi).any())
                hit = fd[fd["v"] >= hi + 1]
                if hit.empty:
                    continue
                sig = hit["valid"].iloc[0]
                obs = pd.Timestamp(times[np.argmax(runmax > hi)], tz="UTC") if died else pd.NaT
                gm = t[t["condition_id"] == cid]
                bef = gm[gm["ts"] < sig]
                p_before = float(bef["p_yes"].iloc[-1]) if len(bef) else np.nan
                mv = gm[(gm["ts"] >= sig - pd.Timedelta(hours=1)) & (gm["p_yes"] <= 0.05)]
                sig_rows.append({"city": city, "date": r.date, "hi": hi, "died": died, "sig": sig, "obs": obs,
                                 "mkt": mv["ts"].iloc[0] if len(mv) else pd.NaT, "p_before": p_before})
                if not (p_before >= 0.05):
                    continue
                won = int(lo <= V <= hi)
                for L in LATENCIES:
                    a = sig + pd.Timedelta(minutes=L)
                    w = gm[gm["buy_no"] & (gm["ts"] >= a) & (gm["ts"] < a + pd.Timedelta(minutes=10))]
                    if w.empty:
                        continue
                    usd = float((w["size"] * w["no_px"]).sum())
                    px = usd / float((w["size"]).sum())
                    if px >= 0.995:
                        continue
                    for variant, stake in (("full", usd), ("10pct", min(200.0, 0.1 * usd))):
                        if stake < 1:
                            continue
                        sh = stake / px
                        fee = FEE_RATE * px * (1 - px) * sh if fees else 0.0
                        bets.append({"city": city, "date": r.date, "L": L, "variant": variant, "px": px,
                                     "stake": stake, "won_no": 1 - won, "died": died,
                                     "pnl": sh * (1 - won) - stake - fee})
    s = pd.DataFrame(sig_rows)
    s.to_csv(OUT / "fast_intl_signals.csv", index=False)
    for city, x in s.groupby("city"):
        d = x[x.died]
        lead = (d.obs - d.sig).dt.total_seconds() / 60
        sur = d[d.p_before >= 0.05]
        mk = (sur.mkt - sur.sig).dt.total_seconds() / 60
        print(f"\n== {city}: signals {len(x)}, false alarms {(~x.died).mean():.1%}")
        print("  fast feed ahead of the killing METAR obs (min):", lead.describe(percentiles=[.25, .5, .75]).round(1).to_dict())
        print(f"  surprised kills {len(sur)}; market priced it after the fast signal (min):",
              mk.describe(percentiles=[.1, .25, .5, .75]).round(1).to_dict())
    b = pd.DataFrame(bets)
    b.to_csv(OUT / "fast_intl_bets.csv", index=False)
    b["cluster"] = b["city"] + "|" + b["date"]
    rows = []
    for (city, variant, L), x in b.groupby(["city", "variant", "L"]):
        roi, t, nc = clustered_t(x.pnl, x.stake, x.cluster)
        rows.append({"city": city, "variant": variant, "L": L, "bets": len(x), "city_days": nc,
                     "no_hit": round(x.won_no.mean(), 3), "avg_px": round(x.px.mean(), 3),
                     "staked": round(x.stake.sum()), "pnl": round(x.pnl.sum()), "roi": round(roi, 3),
                     "t": round(t, 2), "pnl_per_month": round(x.pnl.sum() / 8.0)})
    print("\nhonest NO strategy on the fast signal (false alarms included):")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
