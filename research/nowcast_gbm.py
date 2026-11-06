"""
Step 3d: intraday nowcast with WEATHER features from METAR (clouds, wind, humidity, pressure,
present weather) and gradient boosting, vs the market.

Same setup as research/nowcast_model.py (local hours 11-19, only reports already published by T,
target = further rise k = V - M, walk-forward by month, same market evaluation), but the state
also carries what the reports say about the weather:
  latest report: cloud cover (0 clear .. 4 overcast), ceiling, wind dir (sin/cos) & speed, gust,
                 dewpoint depression, pressure, rain / thunder / showers / fog flags
  last 2-3 h:    mean cloud cover, temperature trend 1 h and 3 h, pressure change 3 h
  day so far:    running max M, hours since M was reached, day min so far, M - min
Model: LightGBM multiclass over k = 0..KMAX (cumulative P(k >= j) derived), city categorical.

Usage: python research/nowcast_gbm.py
"""
import re
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import resolver as R  # noqa: E402
import nowcast_model as NM  # noqa: E402
from nowcast_dead_buckets import event_markets, day_reports  # noqa: E402

OUT = Path("data/raw/analysis")
HOURS = NM.HOURS
KMAX = 20
NM.JMAX = KMAX

COVER = {"SKC": 0, "CLR": 0, "NSC": 0, "NCD": 0, "CAVOK": 0, "FEW": 1, "SCT": 2, "BKN": 3, "OVC": 4, "VV": 4}
CLOUD_RE = re.compile(r"\b(FEW|SCT|BKN|OVC|VV)(\d{3}|///)")
WIND_RE = re.compile(r"\b(\d{3}|VRB)(\d{2,3})(?:G(\d{2,3}))?(KT|MPS)\b")
TD_RE = re.compile(r"(?<![\w/])(M?\d{2})/(M?\d{2})(?![\w/])")
Q_RE = re.compile(r"\bQ(\d{4})\b")
A_RE = re.compile(r"\bA(\d{4})\b")
WX = {"rain": re.compile(r"(?<![A-Z])[-+]?(?:VC)?(?:SH|TS)?(?:RA|DZ)\b"),
      "thunder": re.compile(r"\bTS|\bVCTS"), "shower": re.compile(r"\bSH|\bVCSH"),
      "fog": re.compile(r"\b(?:FG|BR|HZ)\b")}


def parse_weather(metar: str) -> dict:
    body = metar.split(" RMK")[0]
    cover, ceiling = 0, 99.0
    if "CAVOK" in body:
        cover = 0
    for kind, h in CLOUD_RE.findall(body):
        cover = max(cover, COVER[kind])
        if kind in ("BKN", "OVC", "VV") and h != "///":
            ceiling = min(ceiling, int(h) / 10.0)        # thousands of feet
    for k in ("SKC", "CLR", "NSC", "NCD"):
        if f" {k}" in body:
            cover = max(cover, 0)
    wd, ws, wg = np.nan, np.nan, np.nan
    m = WIND_RE.search(body)
    if m:
        ws = float(m.group(2)) * (1.94 if m.group(4) == "MPS" else 1.0)
        wg = float(m.group(3)) * (1.94 if m.group(4) == "MPS" else 1.0) if m.group(3) else ws
        wd = np.nan if m.group(1) == "VRB" else float(m.group(1))
    dep = np.nan
    m = TD_RE.search(body)
    if m:
        t = -int(m.group(1)[1:]) if m.group(1).startswith("M") else int(m.group(1))
        d = -int(m.group(2)[1:]) if m.group(2).startswith("M") else int(m.group(2))
        dep = t - d
    p = np.nan
    m = Q_RE.search(body)
    if m:
        p = float(m.group(1))
    else:
        m = A_RE.search(body)
        if m:
            p = float(m.group(1)) / 100 * 33.8639
    out = {"cover": cover, "ceiling": ceiling, "wdir": wd, "wspd": ws, "gust": wg, "dewdep": dep, "pres": p}
    for k, rx in WX.items():
        out[k] = int(bool(rx.search(body)))
    return out


_wx_cache = {}


def station_weather(icao):
    if icao not in _wx_cache:
        obs = R.load_obs(icao)
        w = pd.DataFrame([parse_weather(m) for m in obs["metar"].values], index=obs.index)
        _wx_cache[icao] = pd.concat([obs[["valid"]], w], axis=1)
    return _wx_cache[icao]


def build_states(chk, city_delay):
    rows = []
    for r in chk.itertuples(index=False):
        day = pd.Timestamp(r.date)
        rep, day_start = day_reports(r.station, r.city, day, r.regime)
        if len(rep) < 12:
            continue
        wx = station_weather(r.station).loc[rep.index]
        conv = (lambda c: R.half_up(c * 9 / 5 + 32)) if r.unit == "F" else R.half_up
        vals = rep["temp_c"].map(conv).values.astype(float)
        tim = rep["valid"].values
        pub = (rep["valid"] + pd.Timedelta(minutes=city_delay.get(r.city, 5.0) + 1.0)).values
        for h in HOURS:
            T = (day_start + pd.Timedelta(hours=h)).to_datetime64()
            n = int((pub <= T).sum())
            if n < 4:
                continue
            kv, kt, kw = vals[:n], tim[:n], wx.iloc[:n]
            M = kv.max()
            last_t = kt[-1]

            def back(hours):
                j = np.searchsorted(kt, last_t - np.timedelta64(int(hours * 60), "m"))
                return min(j, n - 1)
            i1, i3, i2 = back(1), back(3), back(2)
            lw = kw.iloc[-1]
            rows.append({
                "event_id": r.event_id, "city": r.city, "date": r.date, "unit": r.unit, "hour": h,
                "M": int(M), "V": int(r.value), "k": int(max(r.value - M, 0)),
                "cur": kv[-1], "gap": M - kv[-1], "trend1": kv[-1] - kv[i1], "trend3": kv[-1] - kv[i3],
                "dmin": kv.min(), "amp": M - kv.min(),
                "h_since_max": float((last_t - kt[int(np.argmax(kv == M))]) / np.timedelta64(1, "h")),
                "stale_min": float((T - last_t) / np.timedelta64(1, "m")),
                "cover": lw["cover"], "ceiling": lw["ceiling"], "cover2h": float(kw["cover"].iloc[i2:].mean()),
                "wsin": np.sin(np.deg2rad(lw["wdir"])) if pd.notna(lw["wdir"]) else np.nan,
                "wcos": np.cos(np.deg2rad(lw["wdir"])) if pd.notna(lw["wdir"]) else np.nan,
                "wspd": lw["wspd"], "gust": lw["gust"], "dewdep": lw["dewdep"], "pres": lw["pres"],
                "dpres3": lw["pres"] - kw["pres"].iloc[i3] if pd.notna(lw["pres"]) else np.nan,
                "rain": lw["rain"], "thunder": lw["thunder"], "shower": lw["shower"], "fog": lw["fog"],
                "rain2h": float(kw["rain"].iloc[i2:].max()),
            })
    return pd.DataFrame(rows)


FEATS = ["hour", "gap", "trend1", "trend3", "amp", "h_since_max", "stale_min", "cover", "ceiling",
         "cover2h", "wsin", "wcos", "wspd", "gust", "dewdep", "pres", "dpres3", "rain", "thunder",
         "shower", "fog", "rain2h", "unitF", "doy_s", "doy_c", "city_c"]


def walk_forward(st):
    st = st.copy()
    st["month"] = st["date"].str[:7]
    st["unitF"] = (st["unit"] == "F").astype(int)
    doy = pd.to_datetime(st["date"]).dt.dayofyear
    st["doy_s"], st["doy_c"] = np.sin(2 * np.pi * doy / 365), np.cos(2 * np.pi * doy / 365)
    st["city_c"] = st["city"].astype("category")
    y = st["k"].clip(0, KMAX).astype(int)
    probs = np.full((len(st), KMAX + 1), np.nan)
    params = {"objective": "multiclass", "num_class": KMAX + 1, "learning_rate": 0.05,
              "num_leaves": 31, "min_data_in_leaf": 200, "feature_fraction": 0.8,
              "bagging_fraction": 0.8, "bagging_freq": 1, "lambda_l2": 1.0, "verbose": -1,
              "num_threads": 4}
    for m in sorted(st["month"].unique()):
        tr, te = (st["month"] < m).values, (st["month"] == m).values
        if tr.sum() < 3000 or te.sum() == 0:
            continue
        ds = lgb.Dataset(st.loc[tr, FEATS], y[tr], categorical_feature=["city_c"], free_raw_data=False)
        booster = lgb.train(params, ds, num_boost_round=250)
        probs[te] = booster.predict(st.loc[te, FEATS])
        print(f"  month {m}: trained on {tr.sum()}, predicted {te.sum()}", flush=True)
    for j in range(1, KMAX + 1):
        st[f"p_ge{j}"] = probs[:, j:].sum(axis=1)
    return st, booster


def main():
    chk = pd.read_csv(OUT / "resolver_check.csv", dtype={"event_id": str})
    chk = chk[(chk["match"] == True) & chk["value"].notna()]  # noqa: E712
    lat = pd.read_csv(OUT / "awc_latency.csv")
    city_delay = lat[lat["type"] == "METAR"].groupby("city")["delay_min"].median().clip(lower=0).to_dict()
    sp = OUT / "nowcast_states_wx.csv"
    if sp.exists():
        st = pd.read_csv(sp, dtype={"event_id": str})
    else:
        st = build_states(chk, city_delay)
        st.to_csv(sp, index=False)
    print(f"states: {len(st)} (events {st.event_id.nunique()})")
    st, booster = walk_forward(st)
    imp = pd.Series(booster.feature_importance("gain"), index=FEATS).sort_values(ascending=False)
    print("\nfeature importance (gain, last model):")
    print((imp / imp.sum()).round(3).head(15).to_string())

    ev = NM.evaluate(st, event_markets(), city_delay)
    ev.to_csv(OUT / "nowcast_gbm_eval.csv", index=False)
    print(f"\nlive bucket snapshots with market price: {len(ev)}")
    sc = [NM.scores(ev, "all")] + [NM.scores(ev[ev.hour == h], f"hour {h}") for h in HOURS] + \
         [NM.scores(ev[ev.date >= "2026-04-01"], "since Apr-2026"), NM.scores(ev[ev.date >= "2026-10-23"], "AWC regime")]
    print("\nGBM+weather model vs market on live buckets (lower is better):")
    print(pd.DataFrame(sc).round(4).to_string(index=False))

    # blend: is the model useful ON TOP of the market? logit pool fitted on the past, tested forward
    from sklearn.linear_model import LogisticRegression
    ev = ev.sort_values("date")
    lg = lambda p: np.log(np.clip(p, 1e-3, 1 - 1e-3) / (1 - np.clip(p, 1e-3, 1 - 1e-3)))  # noqa: E731
    ev["lm"], ev["lo_"] = lg(ev.p_mkt), lg(ev.p_mod)
    ev["month"] = ev["date"].str[:7]
    ev["p_blend"] = np.nan
    for m in sorted(ev.month.unique()):
        tr, te = ev.month < m, ev.month == m
        if tr.sum() < 20000:
            continue
        clf = LogisticRegression(max_iter=1000).fit(ev.loc[tr, ["lm", "lo_"]], ev.loc[tr, "won"])
        ev.loc[te, "p_blend"] = clf.predict_proba(ev.loc[te, ["lm", "lo_"]])[:, 1]
    b = ev.dropna(subset=["p_blend"])
    print(f"\nmarket+model logit blend (walk-forward), n={len(b)}: Brier market {((b.p_mkt-b.won)**2).mean():.5f} "
          f"vs blend {((b.p_blend-b.won)**2).mean():.5f}; last weights {clf.coef_.round(3)}")

    res = []
    for mgn in NM.MARGINS:
        for entry in ("vwap", "last+1c"):
            res += NM.trade_sim(ev[ev.date >= "2026-04-01"], mgn, entry)
    print("\ntrading since Apr-2026 on GBM disagreement:")
    print(pd.DataFrame(res).round(3).to_string(index=False))
    bb = b[b.date >= "2026-04-01"].assign(p_mod=b["p_blend"])
    res = []
    for mgn in NM.MARGINS:
        res += NM.trade_sim(bb, mgn, "last+1c")
    print("\ntrading since Apr-2026 on BLEND disagreement (last+1c):")
    print(pd.DataFrame(res).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
