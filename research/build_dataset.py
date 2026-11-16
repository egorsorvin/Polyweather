"""
Rebuild the raw Open-Meteo downloads (data/forecasts/, written by fetch_forecasts.py) into a
clean dataset for Hugging Face: two long tables in Parquet, one file per month, plus
reference tables and a dataset card.

Input (whatever exists is used, missing folders are skipped):
  data/forecasts/single/<city>.csv.gz           run_utc, time_utc, model, value      (temperature_2m)
  data/forecasts/single-0618/<city>.csv.gz      run_utc, time_utc, model, var, value
  data/forecasts/single-extras/<city>.csv.gz    run_utc, time_utc, model, var, value
  data/forecasts/previous/<city>.csv.gz         time_utc, model, lead0, lead1d, lead2d
  data/forecasts/previous-extras/<city>.csv.gz  time_utc, model, var(<x>_previous_dayN), value
  data/forecasts/_missing_single.txt            city|run|model
  data/stations.csv

Output (data/dataset/, not in git):
  single_runs/<YYYY-MM>.parquet    city, model, run_utc, valid_utc, lead_h, var, value
                                   one row = one hourly value of one published model run
                                   (month = month of run_utc)
  previous_runs/<YYYY-MM>.parquet  city, model, valid_utc, lead_days, var, value
                                   lead_days 0 = latest run, 1 = run ~24 h earlier, 2 = ~48 h
                                   (month = month of valid_utc)
  missing_single_runs.parquet      city, run_utc, model   (requested, not available upstream)
  stations.csv, models.csv, README.md (dataset card)

Not copied: _done_*.txt (download progress logs, only useful on the machine that downloads).

Checks printed at the end: rows, cities, models, date ranges, exact duplicates removed,
conflicting duplicates (same key, different value), negative lead times.

Usage:
  python research/build_dataset.py
  python research/build_dataset.py --finish-only   # tables already built: card + report only
  hf upload <user>/polyweather-data data/dataset . --repo-type dataset --delete "forecasts/*"
"""
import argparse
import csv
import gzip
import shutil
from pathlib import Path

import pandas as pd

SRC = Path("data/forecasts")
OUT = Path("data/dataset")

MODELS = [
    # model, api, provider, type, first Single Run available (00z)
    ("ecmwf_ifs025", "single+previous", "ECMWF", "physical", "2026-04-02"),
    ("ecmwf_aifs025_single", "single+previous", "ECMWF", "AI", "2026-04-02"),
    ("icon_global", "single", "DWD", "physical", "2026-04-02"),
    ("gfs_global", "single", "NOAA", "physical", "2026-04-02"),
    ("gem_global", "single", "ECCC", "physical", "2026-08-19"),
    ("ukmo_global_deterministic_10km", "single", "UK Met Office", "physical", "2026-04-02"),
    ("jma_gsm", "single", "JMA", "physical", "2026-05-13"),
    ("meteofrance_arpege_world", "single", "Meteo-France", "physical", "2026-04-02"),
    ("icon_seamless", "previous", "DWD", "physical (blend)", ""),
    ("gfs_seamless", "previous", "NOAA", "physical (blend)", ""),
    ("gem_seamless", "previous", "ECCC", "physical (blend)", ""),
    ("ukmo_seamless", "previous", "UK Met Office", "physical (blend)", ""),
    ("jma_seamless", "previous", "JMA", "physical (blend)", ""),
    ("meteofrance_seamless", "previous", "Meteo-France", "physical (blend)", ""),
    ("cma_grapes_global", "previous", "CMA", "physical", ""),
]


def read_gz(path: Path) -> pd.DataFrame:
    """Read a csv.gz; if the tail is truncated (download killed mid-write) keep what is readable."""
    try:
        return pd.read_csv(path, dtype=str)
    except (EOFError, OSError, pd.errors.ParserError):
        rows = []
        try:
            with gzip.open(path, "rt", newline="") as fh:
                for row in csv.reader(fh):
                    rows.append(row)
        except (EOFError, OSError):
            pass
        if not rows:
            return pd.DataFrame()
        header, body = rows[0], rows[1:]
        body = [r for r in body if len(r) == len(header) and r != header]
        print(f"  ! {path}: truncated, kept {len(body)} rows")
        return pd.DataFrame(body, columns=header)


def dedup(df: pd.DataFrame, key: list, stats: dict, name: str) -> pd.DataFrame:
    n0 = len(df)
    df = df.drop_duplicates()                                   # exact duplicates (resumed downloads)
    stats[name]["exact_dups"] += n0 - len(df)
    dup = df.duplicated(key, keep=False)
    if dup.any():                                               # same key, different value
        stats[name]["conflicts"] += int(dup.sum())
        df = df.drop_duplicates(key, keep="last")
    return df


def single_city(city: str) -> pd.DataFrame:
    parts = []
    p = SRC / "single" / f"{city}.csv.gz"
    if p.exists():
        d = read_gz(p)
        if len(d):
            d["var"] = "temperature_2m"
            parts.append(d)
    for tag in ("single-0618", "single-extras"):
        p = SRC / tag / f"{city}.csv.gz"
        if p.exists():
            d = read_gz(p)
            if len(d):
                parts.append(d)
    if not parts:
        return pd.DataFrame()
    d = pd.concat(parts, ignore_index=True)
    d = d[d["run_utc"] != "run_utc"]                            # stray headers from appends
    out = pd.DataFrame({
        "city": city,
        "model": d["model"],
        "run_utc": pd.to_datetime(d["run_utc"], utc=True),
        "valid_utc": pd.to_datetime(d["time_utc"], utc=True),
        "var": d["var"],
        "value": pd.to_numeric(d["value"], errors="coerce").astype("float32"),
    }).dropna(subset=["value"])
    out["lead_h"] = ((out["valid_utc"] - out["run_utc"]).dt.total_seconds() // 3600).astype("int16")
    return out[["city", "model", "run_utc", "valid_utc", "lead_h", "var", "value"]]


def previous_city(city: str) -> pd.DataFrame:
    parts = []
    p = SRC / "previous" / f"{city}.csv.gz"
    if p.exists():
        d = read_gz(p)
        if len(d):
            d = d[d["time_utc"] != "time_utc"]
            long = d.melt(id_vars=["time_utc", "model"], value_vars=["lead0", "lead1d", "lead2d"],
                          var_name="lead", value_name="value")
            long["lead_days"] = long["lead"].map({"lead0": 0, "lead1d": 1, "lead2d": 2})
            long["var"] = "temperature_2m"
            parts.append(long.drop(columns="lead"))
    p = SRC / "previous-extras" / f"{city}.csv.gz"
    if p.exists():
        d = read_gz(p)
        if len(d):
            d = d[d["time_utc"] != "time_utc"]
            m = d["var"].str.extract(r"^(.*)_previous_day(\d+)$")
            d["lead_days"] = pd.to_numeric(m[1]).fillna(0).astype(int)
            d["var"] = m[0].fillna(d["var"])
            parts.append(d)
    if not parts:
        return pd.DataFrame()
    d = pd.concat(parts, ignore_index=True)
    out = pd.DataFrame({
        "city": city,
        "model": d["model"],
        "valid_utc": pd.to_datetime(d["time_utc"], utc=True),
        "lead_days": d["lead_days"].astype("int8"),
        "var": d["var"],
        "value": pd.to_numeric(d["value"], errors="coerce").astype("float32"),
    }).dropna(subset=["value"])
    return out


def write_months(tmp: Path, table: str, month_col: str, out: Path, sort: list) -> list:
    """Combine per-city temporary files into one parquet per month (bounded memory)."""
    months = sorted({f.parent.name for f in (tmp / table).glob("*/*.parquet")})
    (out / table).mkdir(parents=True, exist_ok=True)
    for m in months:
        d = pd.concat([pd.read_parquet(f) for f in sorted((tmp / table / m).glob("*.parquet"))],
                      ignore_index=True)
        for c in ("city", "model", "var"):
            d[c] = d[c].astype("category")
        d.sort_values(sort).to_parquet(out / table / f"{m}.parquet", index=False,
                                       compression="zstd")
    return months


def main():
    global SRC
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=str(SRC))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--finish-only", action="store_true",
                    help="parquet tables already built: only write reference files, card and report")
    args = ap.parse_args()
    SRC, out = Path(args.src), Path(args.out)
    stats = {t: {"exact_dups": 0, "conflicts": 0} for t in ("single_runs", "previous_runs")}
    if not args.finish_only:
        build(out, stats)
    finish(out, stats if not args.finish_only else None)


def build(out: Path, stats: dict):
    if out.exists():
        shutil.rmtree(out)
    tmp = out / "_tmp"
    stations = pd.read_csv("data/stations.csv")
    for city in stations["city"]:
        for table, fn, key, mcol in (
            ("single_runs", single_city, ["model", "run_utc", "valid_utc", "var"], "run_utc"),
            ("previous_runs", previous_city, ["model", "valid_utc", "lead_days", "var"], "valid_utc"),
        ):
            d = fn(city)
            if d.empty:
                continue
            d = dedup(d, key, stats, table)
            month = d[mcol].dt.strftime("%Y-%m")
            for m, part in d.groupby(month):
                (tmp / table / m).mkdir(parents=True, exist_ok=True)
                part.to_parquet(tmp / table / m / f"{city}.parquet", index=False)
        print(f"{city:14s} done")
    write_months(tmp, "single_runs", "run_utc", out, ["city", "model", "var", "run_utc", "valid_utc"])
    write_months(tmp, "previous_runs", "valid_utc", out, ["city", "model", "var", "lead_days", "valid_utc"])
    shutil.rmtree(tmp, ignore_errors=True)


def finish(out: Path, stats):
    """Reference tables, dataset card, and a report computed from the written parquet files."""
    stations = pd.read_csv("data/stations.csv")
    miss = SRC / "_missing_single.txt"
    if miss.exists():
        rows = [l.split("|") for l in miss.read_text(encoding="utf-8").split() if l.count("|") == 2]
        m = pd.DataFrame(rows, columns=["city", "run_utc", "model"]).drop_duplicates()
        m["run_utc"] = pd.to_datetime(m["run_utc"], utc=True)
        m.sort_values(["city", "run_utc", "model"]).to_parquet(out / "missing_single_runs.parquet", index=False)
    stations.drop(columns=[c for c in ("n_events", "volume_musd", "first_event", "last_event")
                           if c in stations]).to_csv(out / "stations.csv", index=False, encoding="utf-8")
    pd.DataFrame(MODELS, columns=["model", "api", "provider", "type", "first_single_run"]).to_csv(
        out / "models.csv", index=False, encoding="utf-8")
    (out / "README.md").write_text(CARD, encoding="utf-8")

    print("\n=== report ===")
    for table, tcol, key in (("single_runs", "run_utc", ["city", "model", "run_utc", "valid_utc", "var"]),
                             ("previous_runs", "valid_utc", ["city", "model", "valid_utc", "lead_days", "var"])):
        files = sorted((out / table).glob("*.parquet"))
        if not files:
            print(f"\n{table}: no files")
            continue
        parts, rows, dups, neg = [], 0, 0, 0
        for f in files:                                      # one month at a time (bounded memory)
            d = pd.read_parquet(f)
            rows += len(d)
            dups += int(d.duplicated(key).sum())
            if "lead_h" in d:
                neg += int((d["lead_h"] < 0).sum())
            parts.append(d.groupby(["var", "model"], observed=True).agg(
                cities=("city", "nunique"), rows=("value", "size"), first=(tcol, "min"), last=(tcol, "max"),
                vmin=("value", "min"), vmax=("value", "max")))
        line = f"\n{table}: {rows:,} rows, {len(files)} months ({files[0].stem}..{files[-1].stem}), " \
               f"duplicate keys in output {dups:,}"
        if table == "single_runs":
            line += f", negative lead {neg:,}"
        if stats:
            line += f"; removed while building: exact dups {stats[table]['exact_dups']:,}, " \
                    f"conflicting {stats[table]['conflicts']:,}"
        print(line)
        agg = pd.concat(parts).groupby(level=[0, 1]).agg(
            cities=("cities", "max"), rows=("rows", "sum"), first=("first", "min"), last=("last", "max"),
            vmin=("vmin", "min"), vmax=("vmax", "max"))
        agg["first"] = agg["first"].dt.strftime("%Y-%m-%d")
        agg["last"] = agg["last"].dt.strftime("%Y-%m-%d")
        print(agg.to_string())
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"\ntotal size: {size / 1e6:.1f} MB in {out}")


CARD = """---
license: cc-by-4.0
pretty_name: PolyWeather forecasts
configs:
- config_name: single_runs
  data_files: "single_runs/*.parquet"
- config_name: previous_runs
  data_files: "previous_runs/*.parquet"
---

# PolyWeather forecasts

Point forecasts of global NWP and AI weather models at the resolution stations of Polymarket
"highest temperature" markets (53 cities), downloaded from Open-Meteo. Part of the PolyWeather
research project. **Private, work in progress.**

## Tables

### `single_runs/<YYYY-MM>.parquet` — runs exactly as published (point-in-time)
Open-Meteo Single Runs API: the complete output of one model run. Use for honest backtests.

| column | type | meaning |
|---|---|---|
| city | str | city id, see `stations.csv` |
| model | str | Open-Meteo model id, see `models.csv` |
| run_utc | timestamp UTC | model initialisation time (00/06/12/18z) |
| valid_utc | timestamp UTC | forecast hour |
| lead_h | int | valid_utc - run_utc, hours (0–71) |
| var | str | temperature_2m (°C), dew_point_2m (°C), shortwave_radiation (W/m², preceding-hour mean), cloud_cover (%), wind_speed_10m (km/h), wind_direction_10m (°) |
| value | float32 | value |

Coverage: temperature_2m from 00/12z runs of 8 models and 06/18z runs of 5 models;
other variables from 00/12z runs of icon_global, ecmwf_ifs025, ecmwf_aifs025_single.
Runs from 2026-04-02 (jma_gsm from 2026-05-13, gem_global from 2026-08-19).
File month = month of `run_utc`.

**Important:** `run_utc` is the initialisation time, not the publication time. Runs become
available several hours later (roughly 3.5–8 h depending on the model). Add a publication lag
before using a run at decision time t.

### `previous_runs/<YYYY-MM>.parquet` — long history, approximate lead
Open-Meteo Previous Runs API: for each hour, the value from the run ~N days earlier.

| column | type | meaning |
|---|---|---|
| city, model, valid_utc, var, value | | as above |
| lead_days | int | 0 = latest run covering the hour, 1 = run ~24 h earlier, 2 = ~48 h earlier |

From 2024-01-01. Lead is per hour, not per run: values of one "lead_days" row set can come from
different runs, and lead 1 for late hours can be shorter than 24 h. Fine for pretraining; do not
use for point-in-time backtests (look-ahead risk).
File month = month of `valid_utc`.

### Reference
* `stations.csv` — settlement station per city (ICAO, coordinates, elevation, timezone, unit).
* `models.csv` — model ids, provider, type, first available Single Run.
* `missing_single_runs.parquet` — (city, run, model) requested but not available upstream.

## Example

```python
import pandas as pd
from huggingface_hub import snapshot_download
path = snapshot_download("<user>/polyweather-data", repo_type="dataset")
df = pd.read_parquet(f"{path}/single_runs")          # all months
```

## Source and licence
Weather data by [Open-Meteo.com](https://open-meteo.com/), CC BY 4.0; upstream model licences
apply (ECMWF, DWD, NOAA, ECCC, UK Met Office, JMA, Météo-France, CMA).
"""


if __name__ == "__main__":
    main()
