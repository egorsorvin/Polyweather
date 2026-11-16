"""
B3: the B2.1 as-of model (research/unified_model.py) with the new forecast data, as an ablation
on exactly the same decision states (same events, same hours, same METAR / skill features):

  V0  B2.1 as stored (00/12z runs, one publication lag of 8 h for all models)   - control
  V1  same, NWP features recomputed from the Hugging Face dataset (data/dataset)  - sanity, ~= V0
  V2  + 06/18z runs, per-model publication lag (LAG_H)
  V3  + forecast weather of day D (cloud, radiation, wind, dew point; ICON / IFS / AIFS)
  V4  + inside day D: max over the remaining hours of the newest run (also runs that do not
        cover the whole day), and its gap to the running max

Same model (LightGBM multiclass over offsets, walk-forward by month, temperature scaling),
same market evaluation (live buckets, last trade <= 2 h old) and trading simulation as B2.1.

Input: data/dataset/single_runs (python research/build_dataset.py, or download from HF),
data/raw/analysis/b2_states.csv (run research/unified_model.py once), trades, events.
Usage: python research/b3_model.py
"""
import sys
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import resolver as R  # noqa: E402
import unified_model as U  # noqa: E402
from fast_feed_sim import clustered_t  # noqa: E402
from nowcast_dead_buckets import event_markets  # noqa: E402

DS = Path("data/dataset/single_runs")
OUT = Path("data/raw/analysis")
MODELS = U.MODELS
CORE = U.CORE
# hours after initialisation until a run can be used. Conservative guesses from typical
# availability (ICON / GFS / ARPEGE ~3.5-5 h, ECMWF / UKMO ~6-8 h); to be measured live.
LAG_H = {"icon_global": 5, "gfs_global": 5, "meteofrance_arpege_world": 5, "jma_gsm": 6,
         "gem_global": 7, "ecmwf_ifs025": 8, "ecmwf_aifs025_single": 8,
         "ukmo_global_deterministic_10km": 8}
EXTRA_MODELS = ["icon_global", "ecmwf_ifs025", "ecmwf_aifs025_single"]
NWP_COLS_OLD = None  # filled in main(): columns of b2_states that depend on NWP


class CityNWP:
    """Hourly forecasts of one city as matrices runs x valid-hours, per (model, var)."""

    def __init__(self, df):
        run_s = df["run_utc"].dt.tz_convert(None).values.astype("datetime64[s]").astype(np.int64)
        val_s = df["valid_utc"].dt.tz_convert(None).values.astype("datetime64[s]").astype(np.int64)
        self.t0s = int(val_s.min() // 3600 * 3600)
        self.mats = {}
        mv = df["model"].astype(str).values + "|" + df["var"].astype(str).values
        vals = df["value"].values
        for key in np.unique(mv):
            sel = mv == key
            r, c = run_s[sel], (val_s[sel] - self.t0s) // 3600
            runs = np.unique(r)
            M = np.full((len(runs), int(c.max()) + 1), np.nan, dtype=np.float32)
            M[np.searchsorted(runs, r), c] = vals[sel]
            self.mats[tuple(key.split("|"))] = (runs, M)

    def col(self, ts):
        return int((ts - self.t0s) // 3600)


def nwp_features(st, variant):
    """Recompute NWP columns of states `st` (one city) for a variant."""
    city = st["city"].iloc[0]
    df = SINGLE[SINGLE["city"] == city]
    if variant == "V1":
        df = df[df["run_utc"].dt.hour.isin([0, 12])]
    nwp = CityNWP(df)
    tz = R.TZ[city]
    F = st["unit"].iloc[0] == "F"
    conv = (lambda c: c * 9 / 5 + 32) if F else (lambda c: c)
    out = []
    for (date, unit), g in st.groupby(["date", "unit"]):
        d0 = int(pd.Timestamp(date).tz_localize(tz).tz_convert("UTC").timestamp())
        a, b = nwp.col(d0), nwp.col(d0 + 86400)
        # local daytime 08-18 for the weather variables
        da, db = nwp.col(d0 + 8 * 3600), nwp.col(d0 + 18 * 3600)
        per_model = {}
        for m in MODELS:
            key = (m, "temperature_2m")
            if key not in nwp.mats:
                continue
            runs, M = nwp.mats[key]
            if a < 0 or b > M.shape[1]:
                continue
            day = M[:, a:b]
            cnt = np.isfinite(day).sum(1)
            dmax = np.where(cnt > 0, np.nanmax(np.where(np.isfinite(day), day, -np.inf), 1), np.nan)
            lag = 8 if variant == "V1" else LAG_H[m]
            avail = runs + lag * 3600
            per_model[m] = (avail, runs, dmax, cnt >= 20, M)
        wx = {}
        if variant in ("V3", "V4"):
            for v in ("cloud_cover", "shortwave_radiation", "wind_speed_10m", "dew_point_2m"):
                for m in EXTRA_MODELS:
                    if (m, v) in nwp.mats:
                        runs, M = nwp.mats[(m, v)]
                        if db <= M.shape[1] and da >= 0:
                            x = M[:, da:db]
                            if v == "shortwave_radiation":
                                x = np.clip(x, 0, None)
                            ok = np.isfinite(x).sum(1) >= 8
                            agg = np.nansum(x, 1) / 1000 if v == "shortwave_radiation" else np.nanmean(
                                np.where(np.isfinite(x), x, np.nan), 1)
                            wx[(m, v)] = (runs + LAG_H[m] * 3600, np.where(ok, agg, np.nan))
        for r in g.itertuples():
            T = d0 + int(r.hour) * 3600
            row = {"_i": r.Index}
            vals, rems = [], []
            for m, (avail, runs, dmax, full, M) in per_model.items():
                n = int(np.searchsorted(avail, T, side="right"))
                if n == 0:
                    continue
                okf = np.nonzero(full[:n])[0]
                if len(okf):
                    i = okf[-1]
                    x = conv(float(dmax[i]))
                    row[U.short(m)] = x
                    row[f"age_{U.short(m)}"] = (T - runs[i]) / 3600
                    if m in CORE:
                        vals.append(x)
                if variant == "V4" and T > d0:
                    j = n - 1                                     # newest run, any coverage
                    seg = M[j, max(nwp.col(T), a):b]
                    if np.isfinite(seg).any():
                        rems.append(conv(float(np.nanmax(seg))))
            if len(vals) >= 3:
                v_ = np.array(vals)
                row.update({"mm_mean": v_.mean(), "mm_std": v_.std(), "mm_min": v_.min(),
                            "mm_max": v_.max(), "n_models": len(v_)})
            if rems:
                row["rem_mean"], row["rem_max"] = float(np.mean(rems)), float(np.max(rems))
            if wx:
                acc = {}
                for (m, v), (av, agg) in wx.items():
                    n = int(np.searchsorted(av, T, side="right"))
                    if n and np.isfinite(agg[:n]).any():
                        i = np.nonzero(np.isfinite(agg[:n]))[0][-1]
                        acc.setdefault(v, []).append(float(agg[i]))
                for v, xs in acc.items():
                    xs = np.array(xs)
                    if v == "dew_point_2m":
                        xs = conv(xs)
                    row[f"fx_{v}"] = xs.mean()
                    if v == "cloud_cover":
                        row["fx_cloud_spread"] = xs.max() - xs.min()
            out.append(row)
    return pd.DataFrame(out).set_index("_i")


def make_variant(st0, variant):
    if variant == "V0":
        return st0.copy()
    parts = []
    for city, g in st0.groupby("city"):
        parts.append(nwp_features(g, variant))
    nw = pd.concat(parts)
    st = st0.drop(columns=[c for c in NWP_COLS_OLD if c in st0]).join(nw)
    st["M_minus_mm"] = st["M"] - st["mm_mean"]
    if "fx_dew_point_2m" in st:
        st["fx_tmax_minus_td"] = st["mm_mean"] - st["fx_dew_point_2m"]
    if "rem_mean" in st:
        st["rem_minus_M"] = st["rem_max"] - st["M"]
        st["rem_minus_mm"] = st["rem_mean"] - st["mm_mean"]
    return st


def eval_base(st):
    """Market rows (state index, bucket, market price, fills) - independent of the variant."""
    p = OUT / f"b3_eval_base_{len(st)}.parquet"
    if p.exists():
        return pd.read_parquet(p)
    markets = event_markets()
    rows = []
    for eid, ix in st.groupby("event_id").indices.items():
        f = U.TRADES / f"{eid}.csv.gz"
        if not f.exists() or eid not in markets:
            continue
        t = pd.read_csv(f, dtype={"condition_id": str})
        if t.empty:
            continue
        t["p_yes"] = np.where(t["outcome"] == "Yes", t["price"], 1 - t["price"])
        isno = (((t["outcome"] == "No") & (t["side"] == "BUY")) | ((t["outcome"] == "Yes") & (t["side"] == "SELL"))).values
        t["isno"] = isno
        t["spx"] = np.where(isno, 1 - t["p_yes"], t["p_yes"])
        t = t.sort_values("timestamp")
        by = {c: (x["timestamp"].values, x["p_yes"].values, x["isno"].values, x["spx"].values, x["size"].values)
              for c, x in t.groupby("condition_id")}
        for i in ix:
            s = st.iloc[i]
            T = (pd.Timestamp(s["date"]).tz_localize(R.TZ[s["city"]]) + pd.Timedelta(hours=int(s["hour"]))).timestamp()
            for cid, (lo, hi, _u, fees) in markets[eid].items():
                if pd.notna(s["M"]) and hi < s["M"]:
                    continue
                if cid not in by:
                    continue
                ts, py, isn, spx, sz = by[cid]
                a, b = np.searchsorted(ts, T - 7200, side="right"), np.searchsorted(ts, T, side="right")
                if b <= a:
                    continue
                c = np.searchsorted(ts, T + 1800, side="right")
                rec = {"i": i, "event_id": eid, "city": s["city"], "date": s["date"], "hour": int(s["hour"]),
                       "cid": cid, "lo": lo, "hi": hi, "p_mkt": float(py[b - 1]),
                       "won": int(lo <= s["V"] <= hi), "fees": fees}
                wn, wp, wz = isn[b:c], spx[b:c], sz[b:c]
                for side, msk in (("NO", wn), ("YES", ~wn)):
                    rec[f"vwap_{side}"] = float((wp[msk] * wz[msk]).sum() / wz[msk].sum()) if msk.any() else np.nan
                    rec[f"usd_{side}"] = float((wp[msk] * wz[msk]).sum()) if msk.any() else 0.0
                rows.append(rec)
    ev = pd.DataFrame(rows)
    ev.to_parquet(p, index=False)
    return ev


def bucket_probs(ev, P, centre):
    i = ev["i"].values
    k = np.arange(2 * U.OFF + 1)[None, :] - U.OFF + centre[i][:, None]
    sel = (k >= ev["lo"].values[:, None]) & (k <= ev["hi"].values[:, None])
    return np.clip((P[i] * sel).sum(1), 1e-4, 1 - 1e-4)


def blend(ev, col):
    from sklearn.linear_model import LogisticRegression
    lg = lambda p: np.log(np.clip(p, 1e-3, 1 - 1e-3) / (1 - np.clip(p, 1e-3, 1 - 1e-3)))  # noqa: E731
    X = np.c_[lg(ev.p_mkt.values), lg(ev[col].values)]
    month = ev["date"].str[:7].values
    pb = np.full(len(ev), np.nan)
    w = None
    for m in sorted(set(month)):
        tr, te = month < m, month == m
        if tr.sum() < 50000:
            continue
        clf = LogisticRegression(max_iter=1000).fit(X[tr], ev["won"].values[tr])
        pb[te] = clf.predict_proba(X[te])[:, 1]
        w = clf.coef_[0]
    return pb, w


def main():
    global SINGLE, NWP_COLS_OLD
    st0 = pd.read_csv(OUT / "b2_states.csv", dtype={"event_id": str}).reset_index(drop=True)
    NWP_COLS_OLD = [c for c in st0.columns if c in {U.short(m) for m in MODELS}
                    or c.startswith("age_") or c.startswith("mm_") or c in ("n_models", "M_minus_mm")]
    print(f"states: {len(st0)}; loading single runs ...", flush=True)
    SINGLE = pd.read_parquet(DS, filters=[("var", "in", ["temperature_2m", "cloud_cover", "shortwave_radiation",
                                                          "wind_speed_10m", "dew_point_2m"])])
    SINGLE = SINGLE[SINGLE["run_utc"] < pd.Timestamp("2026-11-09", tz="UTC")]
    variants = {}
    for v in ("V0", "V1", "V2", "V3", "V4"):
        variants[v] = make_variant(st0, v)
        print(f"{v}: built, {variants[v].shape[1]} columns", flush=True)
    del SINGLE
    ok = np.ones(len(st0), bool)
    for st in variants.values():
        ok &= st["mm_mean"].notna().values
    print(f"states valid in all variants: {ok.sum()} of {len(st0)}")
    keep = np.nonzero(ok)[0]
    base_st = st0.iloc[keep].reset_index(drop=True)
    ev = eval_base(base_st)
    ev["band"] = ev["hour"].map(U.band)
    print(f"live bucket states with market price: {len(ev)}", flush=True)

    res, imps = [], {}
    for v, st in variants.items():
        st = st.iloc[keep].reset_index(drop=True)
        st, P, feats, booster = U.walk_forward(st)
        col = f"p_{v}"
        ev[col] = bucket_probs(ev, P, st["centre"].values)
        ev.loc[np.isnan(P[ev["i"].values, 0]), col] = np.nan
        imps[v] = pd.Series(booster.feature_importance("gain"), index=feats).sort_values(ascending=False)
        print(f"{v}: done", flush=True)

    e = ev.dropna(subset=[f"p_{v}" for v in variants])
    lines = [f"evaluated bucket-states (all variants predicted): {len(e)}, events {e.event_id.nunique()}"]
    tab = []
    for name, g in [("all", e)] + list(e.groupby("band")):
        r = {"set": name, "n": len(g), "mkt": ((g.p_mkt - g.won) ** 2).mean()}
        for v in variants:
            r[v] = ((g[f"p_{v}"] - g.won) ** 2).mean()
        tab.append(r)
    tab = pd.DataFrame(tab)
    lines.append("\nBrier by band (lower is better):\n" + tab.round(5).to_string(index=False))
    gap = tab.copy()
    for v in variants:
        gap[v] = (tab[v] / tab["mkt"] - 1) * 100
    lines.append("\ngap to market, % of market Brier:\n" + gap.drop(columns=["n", "mkt"]).round(1).to_string(index=False))
    ll = {v: U.ll(e[f"p_{v}"].values, e.won.values) for v in variants}
    lines.append(f"\nlog loss: market {U.ll(e.p_mkt.values, e.won.values):.4f}; "
                 + "; ".join(f"{v} {x:.4f}" for v, x in ll.items()))

    lines.append("\nwalk-forward logit blend market + model:")
    for v in variants:
        pb, w = blend(e, f"p_{v}")
        g = e.assign(pb=pb).dropna(subset=["pb"])
        lines.append(f"  {v}: Brier market {((g.p_mkt - g.won) ** 2).mean():.5f} blend {((g.pb - g.won) ** 2).mean():.5f}"
                     f"  weights market {w[0]:.2f} model {w[1]:.2f}")

    lines.append("\ndynamic trading (as B2.1; t clustered by city-day):")
    out = []
    for v in ("V0", "V4"):
        for mg in (0.05, 0.10):
            tr = U.trade_dynamic(e.rename(columns={f"p_{v}": "pv"}), "pv", mg)
            if tr.empty:
                continue
            roi, t, nc = clustered_t(tr.pnl, tr.stake, tr.city + "|" + tr.date)
            out.append({"variant": v, "margin": mg, "bets": len(tr), "city_days": nc, "roi": round(roi, 4),
                        "t": round(t, 2), "pnl": round(tr.pnl.sum())})
    lines.append(pd.DataFrame(out).to_string(index=False))
    for v in ("V3", "V4"):
        im = imps[v] / imps[v].sum()
        lines.append(f"\ntop features {v} (gain share, last model):\n" + im.round(3).head(15).to_string())
    rep = "\n".join(lines)
    print(rep)
    (OUT / "b3_report.txt").write_text(rep, encoding="utf-8")
    e.to_parquet(OUT / "b3_eval.parquet", index=False)


if __name__ == "__main__":
    main()
