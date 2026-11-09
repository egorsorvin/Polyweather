"""
B2: one "as-of" model for any moment t from D-1 12:00 to D 18:00 local, vs the market.

State at time t (only information available at t):
  NWP    per model: max of hourly 2 m T over local day D from its newest run with
         init + PUB_LAG_H <= t (market unit), multi-model mean / spread / min / max, run age
  skill  each model's recent day-ahead error at this station (mean over last 1 / 3 / 7 resolved
         days, all <= D-2, from research/forecast_model.py features)
  METAR  reports published by t (obs + city AWC delay + 1 min): latest temperature, cloud cover,
         ceiling, wind, gust, dewpoint depression, pressure and 3-h change, rain / thunder / fog
  day D  once D has started: running max M so far (settlement rounding), gap to M, 1-h / 3-h trend,
         hours since M
  time   hours until the end of D, local hour, season, city, unit
Target: settlement value V, modelled as the offset V - centre (centre = rounded multi-model mean)
with LightGBM multiclass over offsets -OFF..+OFF; inside day D values below M get probability 0.
Walk-forward by month (a month is predicted by a model trained on earlier months only).

Market comparison on live buckets at every state: last trade <= 2 h old; Brier / log loss by
time-of-decision band; walk-forward logit blend; dynamic trading simulation: at each hourly state,
enter a bucket once when |p - market| > margin, at the real taker VWAP of the next 30 min,
taker fee, hold to resolution; t clustered by city-day.

Usage: python research/unified_model.py
"""
import json
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import resolver as R  # noqa: E402
from nowcast_dead_buckets import event_markets  # noqa: E402
from nowcast_gbm import station_weather  # noqa: E402
from fast_feed_sim import clustered_t  # noqa: E402

FC = Path("data/forecasts/single")
OUT = Path("data/raw/analysis")
TRADES = Path("data/raw/trades")
MODELS = ["ecmwf_ifs025", "ecmwf_aifs025_single", "icon_global", "gfs_global",
          "ukmo_global_deterministic_10km", "meteofrance_arpege_world", "jma_gsm", "gem_global"]
CORE = MODELS[:6]
PUB_LAG_H = 8
HOURS = [h - 24 for h in range(12, 24, 2)] + list(range(0, 19))   # -12..-2 every 2 h (D-1), 0..18 (D)
OFF = 12
FEE_RATE = 0.05
MARGINS = [0.03, 0.05, 0.10]


def short(m):
    return m.split("_")[0] + ("_aifs" if "aifs" in m else "")


# ─── NWP per city: (model) -> arrays over runs for each local day ──────────────

def load_nwp(city):
    f = FC / f"{city}.csv.gz"
    if not f.exists():
        return None
    fc = pd.read_csv(f)
    fc["run"] = pd.to_datetime(fc["run_utc"], utc=True)
    fc["local_day"] = pd.to_datetime(fc["time_utc"], utc=True).dt.tz_convert(R.TZ[city]).dt.strftime("%Y-%m-%d")
    d = fc.groupby(["model", "local_day", "run"])["value"].agg(["max", "count"]).reset_index()
    d = d[d["count"] >= 20]
    out = {}
    for (m, day), g in d.groupby(["model", "local_day"]):
        g = g.sort_values("run")
        out[(m, day)] = (g["run"].values.astype("datetime64[s]").astype(np.int64), g["max"].values)
    return out


# ─── build states ─────────────────────────────────────────────────────────────

def build_states(chk, city_delay, skill):
    rows = []
    for city, g in chk.groupby("city"):
        nwp = load_nwp(city)
        if nwp is None:
            continue
        tz = R.TZ[city]
        delay = city_delay.get(city, 5.0) + 1.0
        for r in g.itertuples(index=False):
            obs = R.load_obs(r.station)
            if obs is None:
                continue
            wx = station_weather(r.station)
            unit = r.unit
            conv = (lambda c: c * 9 / 5 + 32) if unit == "F" else (lambda c: c)
            D = pd.Timestamp(r.date)
            d0 = D.tz_localize(tz).tz_convert("UTC")
            win = obs[(obs["valid"] >= d0 - pd.Timedelta(days=1)) & (obs["valid"] < d0 + pd.Timedelta(days=1))]
            if len(win) < 12:
                continue
            w = wx.loc[win.index]
            pub = ((win["valid"] + pd.Timedelta(minutes=delay)).values.astype("datetime64[s]").astype(np.int64))
            vtime = win["valid"].values.astype("datetime64[s]").astype(np.int64)
            tc = win["temp_c"].values
            routine = win["routine"].values if r.regime == "AWC" else np.ones(len(win), bool)
            in_day = vtime >= int(d0.timestamp())
            settle = np.array([R.half_up(conv(c)) for c in tc], dtype=float)
            sk = skill.get((city, r.date), {})
            for h in HOURS:
                T = d0 + pd.Timedelta(hours=h)
                Ts = int(T.timestamp())
                row = {"event_id": r.event_id, "city": city, "date": r.date, "unit": unit, "hour": h,
                       "V": float(r.value)}
                vals = []
                for m in MODELS:
                    a = nwp.get((m, r.date))
                    if a is None:
                        continue
                    i = np.searchsorted(a[0], Ts - PUB_LAG_H * 3600, side="right") - 1
                    if i < 0:
                        continue
                    x = conv(float(a[1][i]))
                    row[short(m)] = x
                    row[f"age_{short(m)}"] = (Ts - a[0][i]) / 3600
                    if m in CORE:
                        vals.append(x)
                if len(vals) < 3:
                    continue
                vals = np.array(vals)
                row.update({"mm_mean": vals.mean(), "mm_std": vals.std(), "mm_min": vals.min(), "mm_max": vals.max(),
                            "n_models": len(vals)})
                row.update(sk)
                n = int(np.searchsorted(pub, Ts, side="right"))
                if n == 0:
                    continue
                last = w.iloc[n - 1]
                row.update({"obs_t": conv(tc[n - 1]), "obs_age_h": (Ts - vtime[n - 1]) / 3600,
                            "cover": last["cover"], "ceiling": last["ceiling"], "wspd": last["wspd"],
                            "gust": last["gust"], "dewdep": last["dewdep"], "pres": last["pres"],
                            "rain": last["rain"], "thunder": last["thunder"], "fog": last["fog"],
                            "wsin": np.sin(np.deg2rad(last["wdir"])) if pd.notna(last["wdir"]) else np.nan,
                            "wcos": np.cos(np.deg2rad(last["wdir"])) if pd.notna(last["wdir"]) else np.nan})
                j3 = int(np.searchsorted(vtime[:n], vtime[n - 1] - 3 * 3600))
                row["dpres3"] = last["pres"] - w["pres"].iloc[min(j3, n - 1)]
                row["trend3"] = conv(tc[n - 1]) - conv(tc[min(j3, n - 1)])
                mask = in_day[:n] & routine[:n]
                if mask.any():
                    M = settle[:n][mask].max()
                    row["M"] = M
                    row["gap"] = M - settle[n - 1]
                    row["h_since_max"] = (vtime[n - 1] - vtime[:n][mask][np.argmax(settle[:n][mask])]) / 3600
                    row["M_minus_mm"] = M - row["mm_mean"]
                rows.append(row)
        print(f"  {city}: {len(g)} events", flush=True)
    return pd.DataFrame(rows)


def recent_skill():
    """(city, date) -> recent day-ahead errors per model, using only days <= date - 2."""
    f = pd.read_csv(OUT / "fc_features.csv", dtype={"event_id": str}).sort_values(["city", "date"])
    out = {}
    for city, g in f.groupby("city"):
        g = g.set_index(pd.to_datetime(g["date"]))
        errs = pd.DataFrame({short(m): g["V"] - g[m] for m in CORE if m in g})
        errs["mm"] = g["V"] - g[CORE].mean(axis=1)
        for D in g.index:
            past = errs[errs.index <= D - pd.Timedelta(days=2)]
            if past.empty:
                continue
            rec = {}
            for k in (1, 3, 7):
                p = past.tail(k)
                for c in errs.columns:
                    rec[f"err{k}_{c}"] = float(p[c].mean())
            out[(city, D.strftime("%Y-%m-%d"))] = rec
    return out


# ─── model ────────────────────────────────────────────────────────────────────

def add_baseline(st):
    """Rolling station bias / error spread of the multi-model mean (only days <= D-2), as of t.
    Uses the D-1 12:00 day-ahead errors (fc_features.csv) like research/forecast_model.py."""
    f = pd.read_csv(OUT / "fc_features.csv", dtype={"event_id": str})
    f["e"] = f["V"] - f[CORE].mean(axis=1)
    f = f.sort_values(["city", "date"])
    base = {}
    for city, g in f.groupby("city"):
        g = g.set_index(pd.to_datetime(g["date"]))
        for D in g.index:
            past = g.loc[(g.index <= D - pd.Timedelta(days=2)) & (g.index >= D - pd.Timedelta(days=47)), "e"].dropna()
            if len(past) >= 10:
                base[(city, D.strftime("%Y-%m-%d"))] = (float(past.mean()), float(past.std()))
    b = [base.get((c, d), (np.nan, np.nan)) for c, d in zip(st["city"], st["date"])]
    st["bias45"], st["sd45"] = [x[0] for x in b], [x[1] for x in b]
    st["mm_corr"] = st["mm_mean"] + st["bias45"].fillna(0)
    return st


def tr_last_month(st, m):
    return np.zeros(len(st), bool)


def calibrate_T(P, y, mask_tr):
    """Temperature-scaling exponent fitted on past rows (log-prob power), returns calibrated P."""
    best, bestT = None, 1.0
    for T in np.arange(0.4, 1.31, 0.05):
        Q = P[mask_tr] ** T
        Q = Q / Q.sum(axis=1, keepdims=True)
        nll = -np.log(np.clip(Q[np.arange(Q.shape[0]), y[mask_tr]], 1e-6, 1)).mean()
        if best is None or nll < best:
            best, bestT = nll, T
    return bestT


def walk_forward(st):
    st = add_baseline(st.copy())
    st["centre"] = st["mm_corr"].round()
    st["y"] = (st["V"] - st["centre"]).clip(-OFF, OFF).astype(int) + OFF
    st["month"] = st["date"].str[:7]
    st["unitF"] = (st["unit"] == "F").astype(int)
    doy = pd.to_datetime(st["date"]).dt.dayofyear
    st["doy_s"], st["doy_c"] = np.sin(2 * np.pi * doy / 365), np.cos(2 * np.pi * doy / 365)
    st["city_c"] = st["city"].astype("category")
    for c in ("M", "gap", "h_since_max", "M_minus_mm"):
        if c not in st:
            st[c] = np.nan
    st["M_minus_c"] = st["M"] - st["centre"]
    st["mm_minus_centre"] = st["mm_corr"] - st["centre"]
    drop = {"event_id", "city", "date", "unit", "V", "centre", "y", "month", "M", "city_c"}
    feats = [c for c in st.columns if c not in drop]
    params = {"objective": "multiclass", "num_class": 2 * OFF + 1, "learning_rate": 0.03, "num_leaves": 15,
              "min_data_in_leaf": 2000, "feature_fraction": 0.7, "bagging_fraction": 0.7, "bagging_freq": 1,
              "lambda_l2": 10.0, "verbose": -1, "num_threads": 4}
    P = np.full((len(st), 2 * OFF + 1), np.nan)
    oof = np.zeros(len(st), bool)
    booster = None
    for m in sorted(st["month"].unique()):
        tr, te = (st["month"] < m).values, (st["month"] == m).values
        if tr.sum() < 20000:
            continue
        ds = lgb.Dataset(st.loc[tr, feats], st.loc[tr, "y"], free_raw_data=False)
        booster = lgb.train(params, ds, num_boost_round=250)
        P[te] = booster.predict(st.loc[te, feats])
        oof[tr_last_month(st, m)] = True
        print(f"  month {m}: trained on {tr.sum()}, predicted {te.sum()}", flush=True)
    # temperature scaling, walk-forward: month m uses T fitted on all earlier predicted months
    y = st["y"].values
    months = st["month"].values
    Pc = P.copy()
    for m in sorted(st["month"].unique()):
        te = months == m
        past = (months < m) & ~np.isnan(P[:, 0])
        if past.sum() < 20000 or np.isnan(P[te, 0]).all():
            continue
        T = calibrate_T(P, y, past)
        Q = P[te] ** T
        Pc[te] = Q / Q.sum(axis=1, keepdims=True)
        print(f"  calibration {m}: T = {T:.2f}")
    P = Pc
    # inside day D: values below the running max are impossible
    vals = st["centre"].values[:, None] + (np.arange(2 * OFF + 1) - OFF)[None, :]
    M = st["M"].values[:, None]
    imp = np.where(np.isnan(M), False, vals < M)
    P = np.where(imp, 0.0, P)
    P = P / P.sum(axis=1, keepdims=True)
    return st, P, feats, booster


# ─── market evaluation ────────────────────────────────────────────────────────

def bucket_p(probs, centre, lo, hi):
    k = np.arange(2 * OFF + 1) - OFF + centre
    sel = (k >= lo) & (k <= hi)
    return float(np.clip(probs[sel].sum(), 1e-4, 1 - 1e-4))


def evaluate(st, P, markets):
    rows = []
    idx_by_event = st.groupby("event_id").indices
    for eid, ix in idx_by_event.items():
        f = TRADES / f"{eid}.csv.gz"
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
            if np.isnan(P[i, 0]):
                continue
            tz = R.TZ[s["city"]]
            T = (pd.Timestamp(s["date"]).tz_localize(tz) + pd.Timedelta(hours=int(s["hour"]))).timestamp()
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
                rec = {"event_id": eid, "city": s["city"], "date": s["date"], "hour": int(s["hour"]), "cid": cid,
                       "p_mkt": float(py[b - 1]), "p_mod": bucket_p(P[i], s["centre"], lo, hi),
                       "won": int(lo <= s["V"] <= hi), "fees": fees}
                wn, wp, wz = isn[b:c], spx[b:c], sz[b:c]
                for side, msk in (("NO", wn), ("YES", ~wn)):
                    rec[f"vwap_{side}"] = float((wp[msk] * wz[msk]).sum() / wz[msk].sum()) if msk.any() else np.nan
                    rec[f"usd_{side}"] = float((wp[msk] * wz[msk]).sum()) if msk.any() else 0.0
                rows.append(rec)
    return pd.DataFrame(rows)


def ll(p, y):
    p = np.clip(p, 1e-3, 1 - 1e-3)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


def band(h):
    return "D-1 12-23" if h < 0 else ("D 00-05" if h < 6 else ("D 06-11" if h < 12 else "D 12-18"))


def trade_dynamic(ev, prob_col, margin):
    """Enter each (event, bucket) once, at the first state where |p - market| > margin."""
    rows = []
    for (eid, cid), g in ev.sort_values("hour").groupby(["event_id", "cid"]):
        for r in g.itertuples(index=False):
            p, pm = getattr(r, prob_col), r.p_mkt
            if p > pm + margin and not np.isnan(r.vwap_YES):
                side, px, win = "YES", r.vwap_YES, r.won
            elif p < pm - margin and not np.isnan(r.vwap_NO):
                side, px, win = "NO", r.vwap_NO, 1 - r.won
            else:
                continue
            if not (0 < px < 0.995):
                continue
            stake = min(100.0, 0.1 * (r.usd_YES if side == "YES" else r.usd_NO))
            if stake < 1:
                continue
            sh = stake / px
            fee = FEE_RATE * px * (1 - px) * sh if r.fees else 0.0
            rows.append({"event_id": eid, "city": r.city, "date": r.date, "hour": r.hour, "side": side,
                         "px": px, "stake": stake, "pnl": sh * win - stake - fee})
            break
    return pd.DataFrame(rows)


def main():
    chk = pd.read_csv(OUT / "resolver_check.csv", dtype={"event_id": str})
    chk = chk[(chk["match"] == True) & chk["value"].notna() & (chk["date"] >= "2026-04-04")]  # noqa: E712
    lat = pd.read_csv(OUT / "awc_latency.csv")
    city_delay = lat[lat["type"] == "METAR"].groupby("city")["delay_min"].median().clip(lower=0).to_dict()
    sp = OUT / "b2_states.csv"
    if sp.exists():
        st = pd.read_csv(sp, dtype={"event_id": str})
    else:
        st = build_states(chk, city_delay, recent_skill())
        st.to_csv(sp, index=False)
    print(f"states: {len(st)} ({st.event_id.nunique()} events, {st.city.nunique()} cities)")
    st, P, feats, booster = walk_forward(st)
    imp = pd.Series(booster.feature_importance("gain"), index=feats).sort_values(ascending=False)
    print("\ntop features (gain share, last model):")
    print((imp / imp.sum()).round(3).head(20).to_string())

    ev = evaluate(st, P, event_markets())
    ev.to_csv(OUT / "b2_eval.csv", index=False)
    ev["band"] = ev["hour"].map(band)
    print(f"\nlive bucket states with market price: {len(ev)}")
    rows = []
    for name, g in [("all", ev)] + list(ev.groupby("band")):
        rows.append({"set": name, "n": len(g), "brier_mkt": ((g.p_mkt - g.won) ** 2).mean(),
                     "brier_mod": ((g.p_mod - g.won) ** 2).mean(), "ll_mkt": ll(g.p_mkt, g.won), "ll_mod": ll(g.p_mod, g.won)})
    print(pd.DataFrame(rows).round(5).to_string(index=False))

    from sklearn.linear_model import LogisticRegression
    lg = lambda p: np.log(np.clip(p, 1e-3, 1 - 1e-3) / (1 - np.clip(p, 1e-3, 1 - 1e-3)))  # noqa: E731
    ev = ev.sort_values("date")
    ev["xm"], ev["x1"] = lg(ev.p_mkt), lg(ev.p_mod)
    ev["month"] = ev["date"].str[:7]
    ev["p_blend"] = np.nan
    for m in sorted(ev.month.unique()):
        tr, te = ev.month < m, ev.month == m
        if tr.sum() < 50000:
            continue
        clf = LogisticRegression(max_iter=1000).fit(ev.loc[tr, ["xm", "x1"]], ev.loc[tr, "won"])
        ev.loc[te, "p_blend"] = clf.predict_proba(ev.loc[te, ["xm", "x1"]])[:, 1]
    b = ev.dropna(subset=["p_blend"])
    print(f"\nblend market + B2 (walk-forward, n={len(b)}): Brier market {((b.p_mkt - b.won) ** 2).mean():.5f} vs blend "
          f"{((b.p_blend - b.won) ** 2).mean():.5f}; logloss {ll(b.p_mkt, b.won):.4f} vs {ll(b.p_blend, b.won):.4f}; "
          f"weights market {clf.coef_[0][0]:.2f} model {clf.coef_[0][1]:.2f}")
    for name, g in b.groupby("band"):
        print(f"  {name:10s} Brier market {((g.p_mkt - g.won) ** 2).mean():.5f} blend {((g.p_blend - g.won) ** 2).mean():.5f}")

    print("\ndynamic trading (first signal per bucket, taker VWAP next 30 min, fees, t clustered by city-day):")
    out = []
    for col, data in (("p_mod", ev), ("p_blend", b)):
        for mg in MARGINS:
            tr = trade_dynamic(data, col, mg)
            if tr.empty:
                continue
            roi, t, nc = clustered_t(tr.pnl, tr.stake, tr.city + "|" + tr.date)
            out.append({"signal": col, "margin": mg, "bets": len(tr), "city_days": nc, "roi": round(roi, 4),
                        "t": round(t, 2), "pnl": round(tr.pnl.sum()), "yes_share": round((tr.side == "YES").mean(), 2)})
    print(pd.DataFrame(out).to_string(index=False))


if __name__ == "__main__":
    main()
