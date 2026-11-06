"""
Download raw METAR history for every resolution station from the IEM ASOS archive
(mesonet.agron.iastate.edu), the observation source behind Polymarket's current rule.

IEM's `report_type` labels are inconsistent for non-US stations (e.g. RKSI half-hourly
routine reports come back as type 4, the :00 ones only with type 1/2), so each type is
requested separately and stored in a `rtype` column. Routine vs SPECI is decided later
in research/resolver.py (scheduled-minute rule per station).

Writes: data/raw/metar/<ICAO>.csv.gz   columns: valid_utc, rtype, metar
Resumable: stations already downloaded up to `--end` are skipped.

Usage: python research/fetch_metar.py [--start 2024-12-25] [--end YYYY-MM-DD]
       python research/fetch_metar.py --icao KBKF LFPG RCTP   # former stations
"""
import argparse
import csv
import gzip
import io
import time
from datetime import date, timedelta
from pathlib import Path

import requests

IEM = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
STATIONS = Path("data/stations.csv")
OUT = Path("data/raw/metar")


def fetch(icao: str, lo: date, hi: date, rtype: int) -> list:
    params = {"station": icao, "data": "metar", "tz": "Etc/UTC", "format": "onlycomma",
              "latlon": "no", "missing": "M", "direct": "no", "report_type": rtype,
              "year1": lo.year, "month1": lo.month, "day1": lo.day,
              "year2": hi.year, "month2": hi.month, "day2": hi.day}
    for attempt in range(6):
        try:
            r = requests.get(IEM, params=params, timeout=300)
            if r.status_code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            r.raise_for_status()
            rows = list(csv.DictReader(io.StringIO(r.text)))
            return [(x["valid"], rtype, x["metar"]) for x in rows if x.get("metar") not in (None, "", "M")]
        except Exception as e:
            print(f"    retry {attempt + 1}: {e}")
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"IEM failed for {icao} {lo}..{hi} type {rtype}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2024-12-25")
    ap.add_argument("--end", default=(date.today() + timedelta(days=1)).isoformat())
    ap.add_argument("--icao", nargs="*", help="explicit stations (e.g. former resolution stations)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)

    with STATIONS.open() as f:
        stations = [r for r in csv.DictReader(f) if r["icao"] and r["icao"] != "HKO"]
    if args.icao:
        stations = [{"icao": i, "city": "extra", "first_event": args.start} for i in args.icao]
    for st in stations:
        icao = st["icao"]
        path = OUT / f"{icao}.csv.gz"
        if path.exists():
            print(f"{icao}: exists, skip")
            continue
        first = max(start, date.fromisoformat(st["first_event"]) - timedelta(days=3))
        rows = set()
        lo = first
        while lo < end:
            hi = min(lo + timedelta(days=180), end)
            for rt in (1, 2, 3, 4):
                rows.update(fetch(icao, lo, hi, rt))
                time.sleep(1.1)       # IEM asks for <= 1 request/s per IP
            lo = hi
        tmp = path.with_suffix(".tmp")
        with gzip.open(tmp, "wt", newline="") as f:
            w = csv.writer(f)
            w.writerow(["valid_utc", "rtype", "metar"])
            w.writerows(sorted(rows))
        tmp.rename(path)
        print(f"{icao} ({st['city']}): {len(rows)} reports from {first}")


if __name__ == "__main__":
    main()
