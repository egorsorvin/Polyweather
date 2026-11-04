"""
Download NWP forecasts from Open-Meteo for every station in data/stations.csv.
Meant to run on your own machine (the free tier is limited per IP address).

Design rules
------------
* Store RAW HOURLY values in UTC, never pre-aggregated. Daily max over the
  station's local day, run selection, lead time etc. are decided later in
  analysis code, so a methodology change never needs a re-download.
* Resumable: every finished (city, chunk) is recorded; rerun the same command
  after a crash, a limit pause or a reboot and it continues.
* Polite: paces requests and sleeps automatically when Open-Meteo answers
  "minutely / hourly / daily API request limit exceeded".

Modes
-----
  probe     one tiny request per model on both APIs -> prints what is available.
            Run this first and send me the output.
  previous  Previous Runs API: for each hour, the value forecast N days earlier
            (temperature_2m, _previous_day1, _previous_day2). Cheap: ~1 request
            per city per month. Used for model training (long history).
  single    Single Runs API: the complete output of ONE model run (e.g. 00z),
            exactly as published. This is the only way to know precisely what
            a trader could have seen at a given moment. 1 request per city per
            run. Used for the honest backtest against market prices.

Output
------
  data/forecasts/previous/<city>.csv.gz   time_utc, model, lead0, lead1d, lead2d
                                          (lead0 = latest run, lead1d = run ~24h earlier, ...)
  data/forecasts/single/<city>.csv.gz     run_utc, time_utc, model, value
  data/forecasts/_done_<mode>.txt         progress log (resume)

Examples
--------
  python research/fetch_forecasts.py probe
  python research/fetch_forecasts.py previous --start 2024-01-01
  python research/fetch_forecasts.py single --start 2025-09-01 --top 20
  python research/fetch_forecasts.py single --start 2025-09-01 --top 20 --apikey XXXX   # paid plan
"""
import argparse
import csv
import gzip
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

STATIONS = Path("data/stations.csv")
OUT = Path("data/forecasts")

# Global deterministic models. Seamless = Open-Meteo's best blend for a point
# (e.g. ICON-D2/EU/global); fine for Previous Runs. For Single Runs we need the
# concrete global model, since a "run" belongs to one model.
PREVIOUS_MODELS = [
    "ecmwf_ifs025", "ecmwf_aifs025_single", "icon_seamless", "gfs_seamless",
    "gem_seamless", "ukmo_seamless", "jma_seamless", "meteofrance_seamless",
    "cma_grapes_global", "ncep_gfs_graphcast025",
]
SINGLE_MODELS = [
    "ecmwf_ifs025", "ecmwf_aifs025_single", "icon_global", "gfs025", "gem_global",
    "ukmo_global_deterministic_10km", "jma_gsm", "meteofrance_arpege_world",
]
PREVIOUS_VARS = ["temperature_2m", "temperature_2m_previous_day1", "temperature_2m_previous_day2"]
RUN_HOURS = (0, 12)

HOSTS = {
    "previous": "previous-runs-api.open-meteo.com",
    "single": "single-runs-api.open-meteo.com",
}

session = requests.Session()
_last_call = 0.0


def load_stations(top: int) -> list:
    with STATIONS.open() as f:
        rows = [r for r in csv.DictReader(f) if r["lat"]]
    return rows[:top] if top else rows


def api_url(mode: str, apikey: str) -> str:
    host = HOSTS[mode]
    if apikey:
        host = "customer-" + host
    return f"https://{host}/v1/forecast"


def call(url: str, params: dict, apikey: str, min_interval: float) -> dict:
    """GET with pacing and automatic waiting on Open-Meteo rate limits."""
    global _last_call
    if apikey:
        params = {**params, "apikey": apikey}
    for attempt in range(20):
        wait = min_interval - (time.time() - _last_call)
        if wait > 0:
            time.sleep(wait)
        _last_call = time.time()
        try:
            r = session.get(url, params=params, timeout=120)
            data = r.json()
        except Exception as e:
            print(f"    network error ({e}); retry in 30s")
            time.sleep(30)
            continue
        if not data.get("error"):
            return data
        reason = str(data.get("reason", ""))
        if "Minutely" in reason:
            print("    minutely limit -> sleep 65s"); time.sleep(65)
        elif "Hourly" in reason:
            print("    hourly limit -> sleep 1h"); time.sleep(3600)
        elif "Daily" in reason:
            print("    daily limit -> sleep 3h (will keep retrying)"); time.sleep(3 * 3600)
        else:
            return data  # real error (bad model/run/params): let caller handle it
    raise RuntimeError("too many retries")


def done_set(mode: str) -> set:
    p = OUT / f"_done_{mode}.txt"
    return set(p.read_text().split()) if p.exists() else set()


def mark_done(mode: str, key: str):
    with (OUT / f"_done_{mode}.txt").open("a") as f:
        f.write(key + "\n")


def append_rows(path: Path, header: list, rows: list):
    new = not path.exists()
    with gzip.open(path, "at", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(header)
        w.writerows(rows)


# ─── probe ────────────────────────────────────────────────────────────────────

def probe(args):
    st = load_stations(1)[0]
    base = {"latitude": st["lat"], "longitude": st["lon"], "timezone": "GMT"}
    print(f"probe location: {st['city']} {st['icao']}")
    day = (date.today() - timedelta(days=10)).isoformat()
    print("\n[previous runs]")
    for m in PREVIOUS_MODELS:
        d = call(api_url("previous", args.apikey), {**base, "hourly": ",".join(PREVIOUS_VARS),
                 "models": m, "start_date": day, "end_date": day}, args.apikey, 1.0)
        if d.get("error"):
            print(f"  {m:32s} ERROR {d.get('reason')}")
            continue
        h = d["hourly"]
        ok = {v: sum(x is not None for x in h.get(v, [])) for v in PREVIOUS_VARS}
        print(f"  {m:32s} {ok}")
    print("\n[single runs]")
    for run_day in [date(2025, 9, 15), date.today() - timedelta(days=5)]:
        run = f"{run_day.isoformat()}T00:00"
        for m in SINGLE_MODELS:
            d = call(api_url("single", args.apikey), {**base, "hourly": "temperature_2m", "models": m,
                     "run": run, "forecast_days": 3}, args.apikey, 1.0)
            if d.get("error"):
                print(f"  {run} {m:32s} ERROR {d.get('reason')}")
            else:
                vals = d["hourly"].get("temperature_2m", [])
                print(f"  {run} {m:32s} {sum(v is not None for v in vals)}/{len(vals)} values")


# ─── previous runs ────────────────────────────────────────────────────────────

def month_chunks(start: date, end: date):
    d = start.replace(day=1)
    while d <= end:
        nxt = (d + timedelta(days=32)).replace(day=1)
        yield max(d, start), min(nxt - timedelta(days=1), end)
        d = nxt


def fetch_previous(args):
    (OUT / "previous").mkdir(parents=True, exist_ok=True)
    done = done_set("previous")
    end = date.today() - timedelta(days=1)
    stations = load_stations(args.top)
    url = api_url("previous", args.apikey)
    for st in stations:
        path = OUT / "previous" / f"{st['city']}.csv.gz"
        for lo, hi in month_chunks(date.fromisoformat(args.start), end):
            key = f"{st['city']}|{lo}"
            if key in done:
                continue
            rows = []
            # one model per request keeps the weighted cost low and isolates failures
            for m in args.models or PREVIOUS_MODELS:
                d = call(url, {"latitude": st["lat"], "longitude": st["lon"], "timezone": "GMT",
                               "hourly": ",".join(PREVIOUS_VARS), "models": m,
                               "start_date": lo.isoformat(), "end_date": hi.isoformat()},
                         args.apikey, args.interval)
                if d.get("error"):
                    print(f"  {st['city']} {lo} {m}: {d.get('reason')}")
                    continue
                h = d["hourly"]
                cols = [h.get(v, [None] * len(h["time"])) for v in PREVIOUS_VARS]
                for i, t in enumerate(h["time"]):
                    vals = [c[i] for c in cols]
                    if any(v is not None for v in vals):
                        rows.append([t, m] + ["" if v is None else v for v in vals])
            append_rows(path, ["time_utc", "model", "lead0", "lead1d", "lead2d"], rows)
            mark_done("previous", key)
            print(f"{st['city']:14s} {lo} .. {hi}: {len(rows)} values")


# ─── single runs ──────────────────────────────────────────────────────────────

def fetch_single(args):
    (OUT / "single").mkdir(parents=True, exist_ok=True)
    done = done_set("single")
    stations = load_stations(args.top)
    url = api_url("single", args.apikey)
    models = args.models or SINGLE_MODELS
    now = datetime.now(timezone.utc)
    runs = []
    d = date.fromisoformat(args.start)
    while d <= now.date():
        for h in RUN_HOURS:
            run = datetime(d.year, d.month, d.day, h, tzinfo=timezone.utc)
            if run < now - timedelta(hours=12):
                runs.append(run)
        d += timedelta(days=1)
    total = len(runs) * len(stations) * len(models)
    print(f"{len(stations)} stations x {len(runs)} runs x {len(models)} models = {total} requests (minus done)")
    # loop runs outermost so that an interrupted download still covers all cities evenly
    for run in runs:
        run_s = run.strftime("%Y-%m-%dT%H:%M")
        for st in stations:
            for m in models:
                key = f"{st['city']}|{m}|{run_s}"
                if key in done:
                    continue
                d = call(url, {"latitude": st["lat"], "longitude": st["lon"], "timezone": "GMT",
                               "hourly": "temperature_2m", "models": m, "run": run_s,
                               "forecast_days": 3}, args.apikey, args.interval)
                if d.get("error"):
                    # unavailable run/model: record so we don't retry forever
                    print(f"  {st['city']} {m} {run_s}: {d.get('reason')}")
                    mark_done("single", key)
                    continue
                h = d["hourly"]
                rows = [[run_s, t, m, v] for t, v in zip(h["time"], h.get("temperature_2m", [])) if v is not None]
                append_rows(OUT / "single" / f"{st['city']}.csv.gz",
                            ["run_utc", "time_utc", "model", "value"], rows)
                mark_done("single", key)
        print(f"run {run_s} done")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["probe", "previous", "single"])
    ap.add_argument("--start", default="2024-01-01")
    ap.add_argument("--top", type=int, default=0, help="only the N most liquid cities (0 = all)")
    ap.add_argument("--models", nargs="*", help="override model list")
    ap.add_argument("--apikey", default="", help="Open-Meteo commercial key (optional)")
    ap.add_argument("--interval", type=float, default=0.8, help="min seconds between requests")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"probe": probe, "previous": fetch_previous, "single": fetch_single}[args.mode](args)


if __name__ == "__main__":
    main()
