"""
Step 4: day-ahead probabilistic forecast from NWP Single Runs vs the market.

Decision time T = local 12:00 on D-1. A run is usable only if init + PUB_LAG_H <= T
(conservative publication delay), so the newest usable 00z/12z run per model is taken.
Features per event: each model's max of hourly 2 m temperature over the station's local day D
(converted to the market unit), multi-model mean and spread.
Target: settlement value V (resolver, market unit), events where the resolver matched.

Models (walk-forward by day: a day is predicted from outcomes already known before D-1):
  B0  ICON + rolling station bias (last 45 days), Gaussian sigma = rolling RMSE
  B1  EMOS per city on a rolling window: mu = a + sum_i w_i x_i (ridge), sigma^2 = c + d * spread^2,
      sigma fitted by minimising CRPS
  then bucket P = Phi((hi + .5 - mu) / sigma) - Phi((lo - .5 - mu) / sigma)

Market at the same T = last trade <= 3 h old (data/raw/analysis/snapshots.csv, "D-1 12:00").
Scores: Brier and log loss on the same buckets; walk-forward logit blend market + model.

Usage: python research/forecast_model.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).parent))
import resolver as R  # noqa: E402
from nowcast_dead_buckets import event_markets  # noqa: E402

FC = Path("data/forecasts/single")
OUT = Path("data/raw/analysis")
PUB_LAG_H = 8
MODELS = ["ecmwf_ifs025", "ecmwf_aifs025_single", "icon_global", "gfs_global",
          "ukmo_global_deterministic_10km", "meteofrance_arpege_world", "jma_gsm", "gem_global"]
CORE = MODELS[:6]                       # available for the whole period
WINDOW_D = 45
MIN_TRAIN = 25


# ─── 1. features ──────────────────────────────────────────────────────────────

def build_features(chk):
    rows = []
    for city, g in chk.groupby("city"):
        f = FC / f"{city}.csv.gz"
        if not f.exists():
            continue
        fc = pd.read_csv(f)
        fc["run"] = pd.to_datetime(fc["run_utc"], utc=True)
        fc["time"] = pd.to_datetime(fc["time_utc"], utc=True)
        tz = R.TZ[city]
        fc["local_day"] = fc["time"].dt.tz_convert(tz).dt.strftime("%Y-%m-%d")
        daily = fc.groupby(["run", "model", "local_day"])["value"].agg(["max", "count"]).reset_index()
        daily = daily[daily["count"] >= 20]                       # whole local day covered
        for r in g.itertuples(index=False):
            D = pd.Timestamp(r.date)
            T = (D - pd.Timedelta(days=1) + pd.Timedelta(hours=12)).tz_localize(tz).tz_convert("UTC")
            cand = daily[(daily["local_day"] == r.date) & (daily["run"] <= T - pd.Timedelta(hours=PUB_LAG_H))]
            if cand.empty:
                continue
            latest = cand.sort_values("run").groupby("model").tail(1).set_index("model")
            row = {"event_id": r.event_id, "city": city, "date": r.date, "unit": r.unit, "V": float(r.value)}
            for m in MODELS:
                if m in latest.index:
                    c = float(latest.loc[m, "max"])
                    row[m] = c * 9 / 5 + 32 if r.unit == "F" else c
                    row[f"age_{m}"] = (T - latest.loc[m, "run"]).total_seconds() / 3600
            rows.append(row)
    df = pd.DataFrame(rows)
    core = df[CORE]
    df["mm_mean"], df["mm_std"] = core.mean(axis=1), core.std(axis=1)
    return df


# ─── 2. models ────────────────────────────────────────────────────────────────

def crps_gauss(mu, sigma, y):
    z = (y - mu) / sigma
    return sigma * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))


def fit_emos(tr):
    X = tr[CORE].values
    y = tr["V"].values
    ok = ~np.isnan(X).any(axis=1)
    X, y, s = X[ok], y[ok], tr["mm_std"].values[ok]
    if len(y) < MIN_TRAIN:
        return None
    A = np.column_stack([np.ones(len(y)), X])
    lam = 2.0 * np.eye(A.shape[1])
    lam[0, 0] = 0
    w = np.linalg.solve(A.T @ A + lam, A.T @ y)       # ridge mean (stable with few samples)
    mu = A @ w

    def loss(p):
        sig = np.sqrt(np.exp(p[0]) + np.exp(p[1]) * s ** 2)
        return crps_gauss(mu, sig, y).mean()
    p = minimize(loss, x0=[0.0, 0.0], method="Nelder-Mead").x
    return w, p


def predict_emos(par, te):
    w, p = par
    X = te[CORE].values
    mu = np.column_stack([np.ones(len(te)), X]) @ w
    sig = np.sqrt(np.exp(p[0]) + np.exp(p[1]) * te["mm_std"].values ** 2)
    return mu, sig


def walk_forward(df):
    df = df.sort_values(["city", "date"]).reset_index(drop=True)
    for c in ("mu0", "sig0", "mu1", "sig1"):
        df[c] = np.nan
    for city, g in df.groupby("city"):
        dates = pd.to_datetime(g["date"])
        for i, idx in enumerate(g.index):
            D = dates.loc[idx]
            past = g[(dates < D - pd.Timedelta(days=1)) & (dates >= D - pd.Timedelta(days=WINDOW_D + 1))]
            if len(past) < MIN_TRAIN or np.isnan(df.loc[idx, "icon_global"]):
                continue
            err = (past["V"] - past["icon_global"]).dropna()
            df.loc[idx, "mu0"] = df.loc[idx, "icon_global"] + err.mean()
            df.loc[idx, "sig0"] = max(np.sqrt(((err - err.mean()) ** 2).mean()), 0.5)
            row = df.loc[[idx]]
            if row[CORE].isna().any(axis=1).iloc[0]:
                continue
            par = fit_emos(past)
            if par is not None:
                mu, sig = predict_emos(par, row)
                df.loc[idx, "mu1"], df.loc[idx, "sig1"] = mu[0], max(sig[0], 0.4)
    return df


# ─── 3. vs market ─────────────────────────────────────────────────────────────

def bucket_p(mu, sig, lo, hi):
    a = -np.inf if lo <= -10**5 else (lo - 0.5 - mu) / sig
    b = np.inf if hi >= 10**5 else (hi + 0.5 - mu) / sig
    return float(np.clip(norm.cdf(b) - norm.cdf(a), 1e-4, 1 - 1e-4))


def main():
    chk = pd.read_csv(OUT / "resolver_check.csv", dtype={"event_id": str})
    chk = chk[(chk["match"] == True) & chk["value"].notna() & (chk["date"] >= "2026-04-02")]  # noqa: E712
    fp = OUT / "fc_features.csv"
    if fp.exists():
        df = pd.read_csv(fp, dtype={"event_id": str})
    else:
        df = build_features(chk)
        df.to_csv(fp, index=False)
    print(f"events with usable forecasts: {len(df)} ({df.city.nunique()} cities, {df.date.min()}..{df.date.max()})")
    raw = {m: float((df["V"] - df[m]).abs().mean()) for m in MODELS if m in df}
    print("raw MAE vs settlement (market unit):", {k.split('_')[0]: round(v, 2) for k, v in sorted(raw.items(), key=lambda x: x[1])})

    df = walk_forward(df)
    d0, d1 = df.dropna(subset=["mu0"]), df.dropna(subset=["mu1"])
    print(f"\nwalk-forward predictions: B0 {len(d0)}, B1 {len(d1)}")
    for name, d, mu, sg in (("B0 ICON+bias", d0, "mu0", "sig0"), ("B1 EMOS", d1, "mu1", "sig1")):
        print(f"  {name}: MAE {np.abs(d.V - d[mu]).mean():.3f}  CRPS {crps_gauss(d[mu], d[sg], d.V).mean():.3f}  "
              f"exact-integer hit {(d[mu].round() == d.V).mean():.3f}")

    snaps = pd.read_csv(OUT / "snapshots.csv", dtype={"event_id": str})
    snaps = snaps[snaps["snap"] == "D-1 12:00"]
    mk = event_markets()
    pred = df.set_index("event_id")
    rows = []
    for s in snaps.itertuples(index=False):
        if s.event_id not in pred.index:
            continue
        b = mk.get(s.event_id, {}).get(s.condition_id)
        if b is None:
            continue
        lo, hi, _u, fees = b
        p = pred.loc[s.event_id]
        rec = {"event_id": s.event_id, "city": s.city, "date": p["date"], "lo": lo, "hi": hi,
               "p_mkt": s.p, "won": s.won, "fees": fees}
        if pd.notna(p["mu0"]):
            rec["p_b0"] = bucket_p(p["mu0"], p["sig0"], lo, hi)
        if pd.notna(p["mu1"]):
            rec["p_b1"] = bucket_p(p["mu1"], p["sig1"], lo, hi)
        rows.append(rec)
    ev = pd.DataFrame(rows)
    ev.to_csv(OUT / "fc_eval.csv", index=False)

    def ll(p, y):
        p = np.clip(p, 1e-3, 1 - 1e-3)
        return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())
    e = ev.dropna(subset=["p_b0", "p_b1"])
    print(f"\nbuckets with market price and both models: {len(e)} ({e.event_id.nunique()} events)")
    for col in ("p_mkt", "p_b0", "p_b1"):
        print(f"  {col:6s} Brier {((e[col] - e.won) ** 2).mean():.5f}  logloss {ll(e[col], e.won):.4f}")

    from sklearn.linear_model import LogisticRegression
    lg = lambda p: np.log(np.clip(p, 1e-3, 1 - 1e-3) / (1 - np.clip(p, 1e-3, 1 - 1e-3)))  # noqa: E731
    e = e.sort_values("date").copy()
    e["xm"], e["x1"] = lg(e.p_mkt), lg(e.p_b1)
    e["p_blend"] = np.nan
    e["month"] = e["date"].str[:7]
    for m in sorted(e.month.unique()):
        tr, te = e.month < m, e.month == m
        if tr.sum() < 3000:
            continue
        clf = LogisticRegression(max_iter=1000).fit(e.loc[tr, ["xm", "x1"]], e.loc[tr, "won"])
        e.loc[te, "p_blend"] = clf.predict_proba(e.loc[te, ["xm", "x1"]])[:, 1]
    b = e.dropna(subset=["p_blend"])
    print(f"\nwalk-forward blend market + EMOS (n={len(b)}): Brier market {((b.p_mkt - b.won) ** 2).mean():.5f} "
          f"vs blend {((b.p_blend - b.won) ** 2).mean():.5f}; logloss {ll(b.p_mkt, b.won):.4f} vs {ll(b.p_blend, b.won):.4f}; "
          f"last weights market {clf.coef_[0][0]:.2f} model {clf.coef_[0][1]:.2f}")
    b.to_csv(OUT / "fc_blend.csv", index=False)
    print("\nBrier by city (EMOS vs market), most model-favourable first:")
    c = e.groupby("city").apply(lambda x: pd.Series({"n": len(x), "mkt": ((x.p_mkt - x.won) ** 2).mean(),
                                                     "emos": ((x.p_b1 - x.won) ** 2).mean()}), include_groups=False)
    c["emos_minus_mkt"] = c.emos - c.mkt
    print(c.sort_values("emos_minus_mkt").round(4).head(15).to_string())


if __name__ == "__main__":
    main()
