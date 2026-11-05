"""
Step 3c (hypothesis C2): intraday nowcast of the remaining rise of the daily max, vs the market.

At local hour T on the target day a bot knows only METAR reports already PUBLISHED
(observation time <= T - city AWC delay - 1 min). From them:
  M     running max so far (rounded exactly like the resolver, event's own regime/unit)
  cur   latest value, trend = cur - value ~2 h earlier, gap = M - cur
Target: k = V - M, the further rise until the end of the local day (V = resolver value).

Model: for j = 1..JMAX (20), logistic regression P(k >= j | hour, gap, trend, city, season, unit),
walk-forward by month (each month predicted by a model trained only on earlier months).
Bucket probability from the cumulative curve; buckets entirely below M are dead (0).

Market comparison on LIVE buckets at the same T:
  * Brier / log-loss of model vs last YES trade price (<= 2 h old)
  * trading: buy the side the model favours when |model - market| > margin;
    entry = taker VWAP in [T, T+30 min] on that side (conservative), and alternatively
    last price + 1c; taker fee 0.05 p (1-p) where enabled; one bet per (event, hour, bucket).

Outputs: data/raw/analysis/nowcast_states.csv, nowcast_eval.csv and printed tables.
Usage: python research/nowcast_model.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).parent))
import resolver as R  # noqa: E402
from nowcast_dead_buckets import event_markets, day_reports  # noqa: E402

TRADES = Path("data/raw/trades")
OUT = Path("data/raw/analysis")
HOURS = list(range(11, 20))
JMAX = 20      # max further rise modelled (°F markets can still rise 10-15 °F at 11 h)
FEE_RATE = 0.05
MARGINS = [0.03, 0.05, 0.10]


# ─── 1. states from METAR ─────────────────────────────────────────────────────

def build_states(chk, city_delay):
    rows = []
    for r in chk.itertuples(index=False):
        day = pd.Timestamp(r.date)
        rep, day_start = day_reports(r.station, r.city, day, r.regime)
        if len(rep) < 12:
            continue
        conv = (lambda c: R.half_up(c * 9 / 5 + 32)) if r.unit == "F" else R.half_up
        vals = rep["temp_c"].map(conv).values
        V = int(r.value)
        pub = rep["valid"] + pd.Timedelta(minutes=city_delay.get(r.city, 5.0) + 1.0)
        for h in HOURS:
            T = day_start + pd.Timedelta(hours=h)
            known = (pub <= T).values
            if known.sum() < 4:
                continue
            kv = vals[known]
            kt = rep["valid"].values[known]
            M, cur = int(kv.max()), int(kv[-1])
            t2 = kt[-1] - np.timedelta64(2, "h")
            j = np.searchsorted(kt, t2)
            trend = int(cur - kv[min(j, len(kv) - 1)])
            rows.append({"event_id": r.event_id, "city": r.city, "date": r.date, "unit": r.unit,
                         "regime": r.regime, "hour": h, "M": M, "cur": cur, "gap": M - cur,
                         "trend": trend, "V": V, "k": max(V - M, 0),
                         "staleness_min": (T - pd.Timestamp(kt[-1]).tz_localize("UTC")).total_seconds() / 60})
    return pd.DataFrame(rows)


# ─── 2. walk-forward model ────────────────────────────────────────────────────

def features(df, cities):
    X = pd.DataFrame(index=df.index)
    for h in HOURS:
        X[f"h{h}"] = (df["hour"] == h).astype(float)
    X["gap"] = df["gap"].clip(0, 15)
    X["gap2"] = X["gap"] ** 2
    X["trend"] = df["trend"].clip(-10, 10)
    X["trend_pos"] = (df["trend"] > 0).astype(float)
    X["unitF"] = (df["unit"] == "F").astype(float)
    doy = pd.to_datetime(df["date"]).dt.dayofyear
    X["s"], X["c"] = np.sin(2 * np.pi * doy / 365), np.cos(2 * np.pi * doy / 365)
    for c in cities:
        X[f"city_{c}"] = (df["city"] == c).astype(float)
    # hour x gap / trend interactions: late in the day a gap matters more
    X["hgap"] = df["hour"] * X["gap"]
    X["htrend"] = df["hour"] * X["trend"]
    # °F markets: same physics, ~1.8x the numbers -> unit-specific slopes
    for col in [f"h{h}" for h in HOURS] + ["gap", "trend", "hgap", "htrend"]:
        X[f"F_{col}"] = X["unitF"] * X[col]
    return X


def walk_forward(st):
    st = st.copy()
    st["month"] = st["date"].str[:7]
    cities = sorted(st["city"].unique())
    X = features(st, cities)
    for j in range(1, JMAX + 1):
        st[f"p_ge{j}"] = np.nan
    months = sorted(st["month"].unique())
    for m in months:
        tr, te = st["month"] < m, st["month"] == m
        if tr.sum() < 3000:
            continue
        for j in range(1, JMAX + 1):
            y = (st.loc[tr, "k"] >= j).astype(int)
            if y.nunique() < 2:
                st.loc[te, f"p_ge{j}"] = float(y.mean())
                continue
            clf = LogisticRegression(C=1.0, max_iter=2000)
            clf.fit(X[tr], y)
            st.loc[te, f"p_ge{j}"] = clf.predict_proba(X[te])[:, 1]
    # enforce monotone cumulative curve
    for j in range(2, JMAX + 1):
        st[f"p_ge{j}"] = np.minimum(st[f"p_ge{j}"], st[f"p_ge{j-1}"])
    return st


def p_ge(row, j):
    if j <= 0:
        return 1.0
    if j > JMAX:
        return 0.0
    return row[f"p_ge{j}"]


def bucket_prob(row, lo, hi):
    M = row["M"]
    if hi < M:
        return 0.0
    a = max(lo - M, 0)
    b = hi - M + 1 if hi < 10**5 else 10**9
    return p_ge(row, a) - (p_ge(row, b) if b <= JMAX else 0.0)


# ─── 3. market comparison ─────────────────────────────────────────────────────

def _eval_event(args):
    """Market comparison for one event; trades indexed once, windows found by binary search."""
    eid, g, mk = args
    f = TRADES / f"{eid}.csv.gz"
    if not f.exists():
        return []
    t = pd.read_csv(f, dtype={"condition_id": str})
    if t.empty:
        return []
    t["p_yes"] = np.where(t["outcome"] == "Yes", t["price"], 1 - t["price"])
    buy_no = (((t["outcome"] == "No") & (t["side"] == "BUY")) | ((t["outcome"] == "Yes") & (t["side"] == "SELL"))).values
    t["is_no"] = buy_no
    t["side_px"] = np.where(buy_no, 1 - t["p_yes"], t["p_yes"])
    t = t.sort_values("timestamp")
    by = {cid: (x["timestamp"].values, x["p_yes"].values, x["is_no"].values,
                x["side_px"].values, x["size"].values) for cid, x in t.groupby("condition_id")}
    first = g.iloc[0]
    day_start = pd.Timestamp(first["date"]).tz_localize(R.TZ[first["city"]]).tz_convert("UTC").timestamp()
    out = []
    for row in g.to_dict("records"):
        T = day_start + row["hour"] * 3600
        for cid, (lo, hi, _u, fees) in mk.items():
            if hi < row["M"] or cid not in by:
                continue                                  # dead buckets: covered in step 3/3b
            ts, py, isno, spx, sz = by[cid]
            i_T = np.searchsorted(ts, T, side="right")
            i_b = np.searchsorted(ts, T - 7200, side="right")
            if i_T <= i_b:
                continue
            pm = float(py[i_T - 1])
            pmod = float(np.clip(bucket_prob(row, lo, hi), 0.001, 0.999))
            i_w = np.searchsorted(ts, T + 1800, side="right")
            rec = {"event_id": eid, "city": row["city"], "date": row["date"], "hour": row["hour"],
                   "lo": lo, "hi": hi, "M": row["M"], "p_mkt": pm, "p_mod": pmod,
                   "won": int(lo <= row["V"] <= hi), "fees": fees}
            wn, wp, wz = isno[i_T:i_w], spx[i_T:i_w], sz[i_T:i_w]
            for side, m in (("NO", wn), ("YES", ~wn)):
                if m.any():
                    rec[f"vwap_{side}"] = float((wp[m] * wz[m]).sum() / wz[m].sum())
                    rec[f"usd_{side}"] = float((wp[m] * wz[m]).sum())
                else:
                    rec[f"vwap_{side}"], rec[f"usd_{side}"] = np.nan, 0.0
            out.append(rec)
    return out


def evaluate(st, markets, city_delay):
    from multiprocessing import Pool
    st = st.dropna(subset=["p_ge1"])
    jobs = [(eid, g, markets[eid]) for eid, g in st.groupby("event_id") if eid in markets]
    out = []
    with Pool(4) as pool:
        for k, res in enumerate(pool.imap_unordered(_eval_event, jobs, chunksize=20)):
            out.extend(res)
            if (k + 1) % 1000 == 0:
                print(f"  evaluated {k+1}/{len(jobs)} events", flush=True)
    return pd.DataFrame(out)


def scores(ev, label):
    eps = 1e-3
    def ll(p, y):
        p = np.clip(p, eps, 1 - eps)
        return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())
    return {"set": label, "n": len(ev),
            "brier_mkt": float(((ev.p_mkt - ev.won) ** 2).mean()),
            "brier_mod": float(((ev.p_mod - ev.won) ** 2).mean()),
            "ll_mkt": ll(ev.p_mkt, ev.won), "ll_mod": ll(ev.p_mod, ev.won)}


def trade_sim(ev, margin, entry):
    rows = []
    for side in ("NO", "YES"):
        if side == "NO":
            sel = ev[ev.p_mod < ev.p_mkt - margin]
            px = sel["vwap_NO"] if entry == "vwap" else (1 - sel["p_mkt"] + 0.01)
            win = 1 - sel["won"]
        else:
            sel = ev[ev.p_mod > ev.p_mkt + margin]
            px = sel["vwap_YES"] if entry == "vwap" else (sel["p_mkt"] + 0.01)
            win = sel["won"]
        ok = px.notna() & (px > 0) & (px < 1)
        sel, px, win = sel[ok], px[ok], win[ok]
        fee = np.where(sel["fees"], FEE_RATE * px * (1 - px), 0.0)
        pnl = win - px - fee                  # per share
        rows.append({"side": side, "margin": margin, "entry": entry, "bets": len(sel),
                     "roi": float(pnl.sum() / px.sum()) if len(sel) else np.nan,
                     "hit": float(win.mean()) if len(sel) else np.nan,
                     "avg_px": float(px.mean()) if len(sel) else np.nan,
                     "t": float((pnl / px).mean() / ((pnl / px).std(ddof=1) / np.sqrt(len(sel)))) if len(sel) > 2 else np.nan})
    return rows


def main():
    chk = pd.read_csv(OUT / "resolver_check.csv", dtype={"event_id": str})
    chk = chk[(chk["match"] == True) & chk["value"].notna()]  # noqa: E712
    lat = pd.read_csv(OUT / "awc_latency.csv")
    city_delay = lat[lat["type"] == "METAR"].groupby("city")["delay_min"].median().clip(lower=0).to_dict()
    sp = OUT / "nowcast_states.csv"
    if sp.exists():
        st = pd.read_csv(sp, dtype={"event_id": str})
    else:
        st = build_states(chk, city_delay)
        st.to_csv(sp, index=False)
    print(f"states: {len(st)} (events {st.event_id.nunique()})")
    print("share with further rise k>=1 by hour:")
    print(st.groupby("hour")["k"].apply(lambda k: (k >= 1).mean()).round(3).to_string())

    st = walk_forward(st)
    markets = event_markets()
    ev = evaluate(st, markets, city_delay)
    ev.to_csv(OUT / "nowcast_eval.csv", index=False)
    print(f"\nlive bucket snapshots with market price: {len(ev)}")
    sc = [scores(ev, "all")] + [scores(ev[ev.hour == h], f"hour {h}") for h in HOURS] + \
         [scores(ev[ev.date >= "2026-04-01"], "since Apr-2026"), scores(ev[ev.date >= "2026-10-23"], "AWC regime")]
    print("\nmodel vs market on live buckets (lower is better):")
    print(pd.DataFrame(sc).round(4).to_string(index=False))

    res = []
    for m in MARGINS:
        for entry in ("vwap", "last+1c"):
            res += trade_sim(ev[ev.date >= "2026-04-01"], m, entry)
    print("\ntrading since Apr-2026 (one bet per event/hour/bucket, fees on where enabled):")
    print(pd.DataFrame(res).round(3).to_string(index=False))

    # certainty harvesting: model says <= 3 %, market still >= 6 %
    ch = ev[(ev.date >= "2026-04-01") & (ev.p_mod <= 0.03) & (ev.p_mkt >= 0.06)]
    px = 1 - ch["p_mkt"] + 0.01
    pnl = (1 - ch["won"]) - px - np.where(ch["fees"], FEE_RATE * px * (1 - px), 0)
    print(f"\ncertainty harvesting (model <=3 %, market >=6 %), NO at last+1c: bets {len(ch)}, "
          f"NO hit {1 - ch.won.mean():.3f}, avg NO px {px.mean():.3f}, ROI {pnl.sum() / px.sum():+.3f}")
    print(ch.groupby("hour").apply(lambda x: pd.Series({"bets": len(x), "yes_hit": x.won.mean(),
                                                         "mkt": x.p_mkt.mean(), "mod": x.p_mod.mean()}),
                                   include_groups=False).round(3).to_string())


if __name__ == "__main__":
    main()
