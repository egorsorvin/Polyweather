"""
Step 3b: who captures the dead-bucket pie, and how much is left for a bot that reads AWC METAR?

For every dead bucket with any pie (research/nowcast_dead_buckets.py output), list the taker
trades that bought dead NO <= 0.98 after the killing observation, with minutes after obs,
price, profit and wallet. Then:
  * per city "reachable" pie = trades after obs + (AWC median publication delay for that
    city, from data/raw/analysis/awc_latency.csv) + 1 min reaction
  * concentration by wallet (are a few bots taking it?)
  * largest single events (genuine stale orders or artefacts?)

Outputs: data/raw/analysis/dead_pie_trades.csv and printed tables.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import resolver as R  # noqa: E402
from nowcast_dead_buckets import event_markets, day_reports, FEE_RATE, NO_MAX  # noqa: E402

TRADES = Path("data/raw/trades")
OUT = Path("data/raw/analysis")
REACTION_MIN = 1.0


def main():
    dead = pd.read_csv(OUT / "dead_buckets.csv", dtype={"event_id": str})
    dead = dead[dead["pie_profit_2"] > 0]
    chk = pd.read_csv(OUT / "resolver_check.csv", dtype={"event_id": str}).set_index("event_id")
    lat = pd.read_csv(OUT / "awc_latency.csv")
    city_delay = lat[lat["type"] == "METAR"].groupby("city")["delay_min"].median().clip(lower=0)
    markets = event_markets()
    out = []
    for eid, g in dead.groupby("event_id"):
        r = chk.loc[eid]
        rep, _ = day_reports(r.station, r.city, pd.Timestamp(r.date), r.regime)
        vals = rep["temp_c"].map(lambda c: R.half_up(c * 9 / 5 + 32) if r.unit == "F" else R.half_up(c))
        runmax, times = vals.cummax().values, rep["valid"].values
        t = pd.read_csv(TRADES / f"{eid}.csv.gz", dtype={"condition_id": str})
        t["ts"] = pd.to_datetime(t["timestamp"], unit="s", utc=True)
        t["no_px"] = np.where(t["outcome"] == "No", t["price"], 1 - t["price"])
        buy_no = ((t["outcome"] == "No") & (t["side"] == "BUY")) | ((t["outcome"] == "Yes") & (t["side"] == "SELL"))
        t = t[buy_no & (t["no_px"] <= NO_MAX)]
        for cid, (lo, hi, _u, fees) in markets[eid].items():
            if hi >= 10**5 or not (runmax > hi).any():
                continue
            obs_time = pd.Timestamp(times[np.argmax(runmax > hi)])
            obs_time = obs_time.tz_localize("UTC") if obs_time.tzinfo is None else obs_time
            w = t[(t["condition_id"] == cid) & (t["ts"] >= obs_time + pd.Timedelta(minutes=2))]
            for x in w.itertuples(index=False):
                fee = FEE_RATE * x.no_px * (1 - x.no_px) * x.size if fees else 0.0
                out.append({"event_id": eid, "city": r.city, "date": r.date, "hi": hi,
                            "min_after_obs": (x.ts - obs_time).total_seconds() / 60,
                            "no_px": x.no_px, "usd": x.size * x.no_px,
                            "profit": x.size * (1 - x.no_px) - fee, "wallet": x.proxy_wallet})
    df = pd.DataFrame(out)
    df["city_delay"] = df["city"].map(city_delay).fillna(city_delay.median())
    df["reachable"] = df["min_after_obs"] >= df["city_delay"] + REACTION_MIN
    df.to_csv(OUT / "dead_pie_trades.csv", index=False)

    reach = df[df["reachable"]]
    reach_m = reach[reach["date"] >= "2026-04-01"]
    print(f"pie trades (>=2 min after obs): {len(df)}, profit ${df.profit.sum():,.0f}")
    print(f"reachable for an AWC-reading bot (city AWC delay + {REACTION_MIN} min): "
          f"{len(reach)} trades, profit ${reach.profit.sum():,.0f}, spent ${reach.usd.sum():,.0f}")
    print(f"  since Apr-2026: ${reach_m.profit.sum():,.0f} total, ~${reach_m.profit.sum() / 7.2:,.0f} / month")

    c = reach.groupby("city").agg(trades=("profit", "size"), profit=("profit", "sum"),
                                  events=("event_id", "nunique"), delay=("city_delay", "first"))
    print("\nreachable pie by city:")
    print(c.sort_values("profit", ascending=False).round(1).head(25).to_string())

    wl = reach.groupby("wallet").agg(profit=("profit", "sum"), trades=("profit", "size"),
                                     events=("event_id", "nunique"),
                                     med_min=("min_after_obs", "median")).sort_values("profit", ascending=False)
    tot = wl["profit"].sum()
    print(f"\nwallets capturing reachable pie: {len(wl)}; top-1 share {wl.profit.iloc[0] / tot:.2f}, "
          f"top-5 {wl.profit.head(5).sum() / tot:.2f}, top-20 {wl.profit.head(20).sum() / tot:.2f}")
    print(wl.head(12).round(1).to_string())

    ev = reach.groupby(["event_id", "city", "date"]).agg(profit=("profit", "sum"), trades=("profit", "size"),
                                                         wallets=("wallet", "nunique"),
                                                         px_med=("no_px", "median"),
                                                         min_med=("min_after_obs", "median"))
    print("\nlargest reachable-pie events:")
    print(ev.sort_values("profit", ascending=False).head(15).round(2).to_string())
    print("\nreachable profit by NO price band:")
    print(reach.groupby(pd.cut(reach.no_px, [0, .5, .8, .9, .95, .98]), observed=True)["profit"]
          .agg(["size", "sum"]).round(0).to_string())


if __name__ == "__main__":
    main()
