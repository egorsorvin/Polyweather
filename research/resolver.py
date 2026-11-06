"""
Resolver: rebuild the settlement value of every Polymarket "highest temperature" event
from raw METAR, following the rule regime written in that event's own description,
and check it against the bucket the market actually resolved to.

Rule regimes (from the events' resolutionSource / description, see research/sota/SOTA.md):
  WU    Wunderground daily history (to ~2026-08-22)      -> all reports incl. SPECI
  NOAA  weather.gov/wrh/timeseries (2026-08-23..10-22)   -> all reports incl. SPECI
  AWC   aviationweather.gov METAR API (from 2026-10-23)  -> ROUTINE reports only, SPECI excluded
  HKO / CWA  national observatories, not METAR           -> cannot be rebuilt here, skipped

Value of a report: T-group remark in tenths of °C if present, else the body temperature in
whole °C. Daily value = max over the station's LOCAL calendar day. °C markets: round half
up to whole °C. °F markets: °F = °C*9/5+32, round half up.

Routine vs SPECI: US stations use IEM report type (3 = routine, 4 = SPECI). IEM type 1 is
MADIS 5-minute data and is dropped. Elsewhere IEM's 3/4 labels
are unreliable, so a report is routine when its minute is one of the station's scheduled
minutes that month (e.g. RKSI :00/:30, EGLC :20/:50).

Outputs (data/raw/analysis/):
  resolver_check.csv  one row per event: regime, station, value, our bucket, winner, match
  prints match rates by regime and city, and the largest mismatch groups.

Usage: python research/resolver.py
"""
import csv
import gzip
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

EVENTS = Path("data/raw/events.jsonl")
METAR = Path("data/raw/metar")
OUT = Path("data/raw/analysis")
TZ = json.loads(Path("research/timezones.json").read_text())
MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
ALIASES = {"new-york-city": "nyc"}


# ─── METAR parsing ────────────────────────────────────────────────────────────

TGROUP = re.compile(r"\bT([01])(\d{3})([01])(\d{3})\b")
BODY = re.compile(r"(?<![\w/])(M?\d{2})/(M?\d{2}|//)?(?![\w/])")


def report_temp_c(metar: str):
    m = TGROUP.search(metar)
    if m:
        v = int(m.group(2)) / 10
        return -v if m.group(1) == "1" else v, True
    body = metar.split(" RMK")[0]
    m = BODY.search(body)
    if m:
        t = m.group(1)
        return (-int(t[1:]) if t.startswith("M") else int(t)), False
    return None, False


def half_up(x: float) -> int:
    return math.floor(x + 0.5 + 1e-9)


_obs_cache = {}


def load_obs(icao: str):
    """DataFrame of reports for a station: valid (UTC), temp_c, has_tgroup, routine."""
    if icao in _obs_cache:
        return _obs_cache[icao]
    path = METAR / f"{icao}.csv.gz"
    if not path.exists():
        _obs_cache[icao] = None
        return None
    types = defaultdict(set)
    with gzip.open(path, "rt", newline="") as f:
        for row in csv.DictReader(f):
            types[(row["valid_utc"], row["metar"])].add(int(row["rtype"]))
    recs = []
    for (valid, metar), rts in types.items():
        # IEM type 1 = MADIS high-frequency (5-minute) ASOS data, not METAR: never counts
        if rts == {1} or "MADISHF" in metar:
            continue
        t, tg = report_temp_c(metar)
        if t is None:
            continue
        recs.append((valid, t, tg, 3 in rts, metar))
    df = pd.DataFrame(recs, columns=["valid", "temp_c", "tgroup", "iem_routine", "metar"])
    df["valid"] = pd.to_datetime(df["valid"], utc=True)
    df = df.sort_values("valid").drop_duplicates("valid", keep="last")
    if icao.startswith("K"):
        df["routine"] = df["iem_routine"]
    else:
        df["minute"] = df["valid"].dt.minute
        df["month"] = df["valid"].dt.strftime("%Y-%m")
        days = df.groupby("month")["valid"].apply(lambda s: s.dt.date.nunique())
        cnt = df.groupby(["month", "minute"]).size().rename("n").reset_index()
        cnt["share"] = cnt["n"] / cnt["month"].map(days)
        sched = set(map(tuple, cnt.loc[cnt["share"] >= 0.4, ["month", "minute"]].values))
        df["routine"] = [(mo, mi) in sched for mo, mi in zip(df["month"], df["minute"])]
    _obs_cache[icao] = df
    return df


# ─── events ───────────────────────────────────────────────────────────────────

RANGE_PATTERNS = [
    (re.compile(r"(-?\d+)\s*°\s*([CF])\s+or\s+(below|lower)", re.I), "le"),
    (re.compile(r"(-?\d+)\s*°\s*([CF])\s+or\s+(higher|above)", re.I), "ge"),
    (re.compile(r"(-?\d+)\s*°?\s*[CF]?\s*(?:-|–|and)\s*(-?\d+)\s*°\s*([CF])", re.I), "between"),
    (re.compile(r"be\s+(-?\d+)\s*°\s*([CF])\b", re.I), "eq"),
]


def parse_bucket(q: str):
    for pat, kind in RANGE_PATTERNS:
        m = pat.search(q)
        if not m:
            continue
        if kind == "le":
            return (-10**6, int(m.group(1)), m.group(2).upper())
        if kind == "ge":
            return (int(m.group(1)), 10**6, m.group(2).upper())
        if kind == "between":
            return (int(m.group(1)), int(m.group(2)), m.group(3).upper())
        return (int(m.group(1)), int(m.group(1)), m.group(2).upper())
    return None


def regime_of(e: dict) -> str:
    src = (e.get("resolutionSource") or "").lower()
    desc = e.get("description", "").lower()
    for key, name in (("aviationweather.gov", "AWC"), ("weather.gov/wrh", "NOAA"),
                      ("wunderground", "WU"), ("weather.gov.hk", "HKO"), ("cwa.gov.tw", "CWA")):
        if key in src:
            return name
    if "hong kong observatory" in desc:
        return "HKO"
    if "cwa.gov.tw" in desc or "central weather" in desc:
        return "CWA"
    for key, name in (("aviationweather.gov", "AWC"), ("weather.gov/wrh", "NOAA"),
                      ("wunderground", "WU")):
        if key in desc:
            return name
    return "?"


ICAO_RE = re.compile(r"(?:history/daily/[^\s\"]*?/|site=|ids=|/weather/|\()([A-Za-z]{4})\b")


def station_of(e: dict):
    txt = (e.get("resolutionSource") or "") + " " + e.get("description", "")
    ids = [x.upper() for x in ICAO_RE.findall(txt) if x.upper() not in ("HTTP", "WWW.")]
    return ids[0] if ids else None


def target_date(slug: str, end_iso: str):
    m = re.search(rf"-on-({MONTHS})-(\d+)(?:-(\d{{4}}))?", slug)
    if not m:
        return None
    month = MONTHS.split("|").index(m.group(1)) + 1
    year = int(m.group(3)) if m.group(3) else int(end_iso[:4])
    if not m.group(3) and month == 12 and end_iso[5:7] == "01":
        year -= 1
    return pd.Timestamp(year=year, month=month, day=int(m.group(2)))


def daily_value(icao: str, city: str, day: pd.Timestamp, regime: str):
    obs = load_obs(icao)
    if obs is None:
        return None, "no_metar_file"
    lo = day.tz_localize(TZ[city]).tz_convert("UTC")
    hi = (day + pd.Timedelta(days=1)).tz_localize(TZ[city]).tz_convert("UTC")
    x = obs[(obs["valid"] >= lo) & (obs["valid"] < hi)]
    if regime == "AWC":
        x = x[x["routine"]]
    if len(x) < 12:
        return None, f"few_reports({len(x)})"
    return float(x["temp_c"].max()), "ok"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for line in EVENTS.open():
        e = json.loads(line)
        m = re.match(r"highest-temperature-in-(.+?)-on-", e["slug"])
        if not m or not e.get("closed"):
            continue
        city = ALIASES.get(m.group(1), m.group(1))
        day = target_date(e["slug"], e["endDate"])
        if day is None or city not in TZ:
            continue
        buckets, winner = [], None
        for mk in e.get("markets", []):
            b = parse_bucket(mk.get("question", ""))
            if b is None:
                continue
            buckets.append(b)
            try:
                if float(json.loads(mk.get("outcomePrices") or "[]")[0]) == 1.0:
                    winner = b
            except Exception:
                pass
        regime, icao = regime_of(e), station_of(e)
        row = {"event_id": e["id"], "city": city, "date": day.date().isoformat(), "regime": regime,
               "station": icao, "unit": buckets[0][2] if buckets else None,
               "winner_lo": winner[0] if winner else None, "winner_hi": winner[1] if winner else None}
        if winner is None:
            row["status"] = "no_winner"
        elif regime in ("HKO", "CWA", "?") or not icao:
            row["status"] = f"not_rebuildable_{regime}"
        else:
            v, status = daily_value(icao, city, day, regime)
            row["value_c"] = v
            row["status"] = status
            if v is not None:
                val = half_up(v * 9 / 5 + 32) if winner[2] == "F" else half_up(v)
                row["value"] = val
                lo, hi = winner[0], winner[1]
                row["match"] = lo <= val <= hi
                row["miss"] = 0 if row["match"] else (val - hi if val > hi else val - lo)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "resolver_check.csv", index=False)
    chk = df[df["match"].notna()].copy()
    chk["match"] = chk["match"].astype(bool)
    print(f"events: {len(df)}, rebuildable & checked: {len(chk)}")
    print(df["status"].value_counts().to_string())
    print("\nmatch rate by regime:")
    print(chk.groupby("regime")["match"].agg(["size", "mean"]).round(4).to_string())
    print("\nmiss distribution (our value - winner bucket edge):")
    print(chk.loc[~chk["match"], "miss"].value_counts().sort_index().to_string())
    print("\nmatch rate by city x regime (worst first):")
    g = chk.groupby(["city", "regime"])["match"].agg(["size", "mean"]).round(3)
    print(g.sort_values("mean").head(40).to_string())


if __name__ == "__main__":
    main()
