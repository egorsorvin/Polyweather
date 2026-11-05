"""
Download historical fast observation feeds for non-US resolution stations.

  tokyo     JMA AMeDAS Haneda (prec 44, block 0371), 10-minute values, tenths °C
            https://www.data.jma.go.jp/stats/etrn/view/10min_a1.php
  singapore NEA Changi Meteorological Station S24, 1-minute values
            https://api.data.gov.sg/v1/environment/air-temperature?date=YYYY-MM-DD

Writes data/raw/fast_intl/<city>.csv.gz with columns valid_utc, temp_c (one row per obs).
Resumable per day. Usage: python research/fetch_fast_intl.py [--start 2026-03-01]
"""
import argparse
import gzip
import re
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

OUT = Path("data/raw/fast_intl")
JST, SGT = timezone(timedelta(hours=9)), timezone(timedelta(hours=8))


def jma_day(d: date):
    url = (f"https://www.data.jma.go.jp/stats/etrn/view/10min_a1.php?prec_no=44&block_no=0371"
           f"&year={d.year}&month={d.month}&day={d.day}&view=")
    t = requests.get(url, timeout=60).text
    out = []
    for row in re.findall(r'<tr class="mtx"[^>]*>(.*?)</tr>', t, re.S):
        cells = [re.sub("<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) < 3 or ":" not in cells[0]:
            continue
        hh, mm = map(int, cells[0].split(":"))
        try:
            temp = float(cells[2].rstrip(")] "))
        except ValueError:
            continue
        local = datetime(d.year, d.month, d.day, tzinfo=JST) + timedelta(hours=hh, minutes=mm)
        out.append((local.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M"), temp))
    return out


def nea_day(d: date):
    r = requests.get("https://api.data.gov.sg/v1/environment/air-temperature",
                     params={"date": d.isoformat()}, timeout=120).json()
    out = []
    for it in r.get("items", []):
        ts = datetime.fromisoformat(it["timestamp"]).astimezone(timezone.utc)
        for x in it.get("readings", []):
            if x.get("station_id") == "S24" and x.get("value") is not None:
                out.append((ts.strftime("%Y-%m-%d %H:%M"), float(x["value"])))
    return out


FEEDS = {"tokyo": jma_day, "singapore": nea_day}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-03-01")
    ap.add_argument("--end", default=date.today().isoformat())
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for city, fn in FEEDS.items():
        path = OUT / f"{city}.csv.gz"
        have = set()
        if path.exists():
            with gzip.open(path, "rt") as f:
                have = {line[:10] for line in f if line[0].isdigit()}
        d = date.fromisoformat(args.start)
        n = 0
        with gzip.open(path, "at") as f:
            if not have:
                f.write("valid_utc,temp_c\n")
            while d <= date.fromisoformat(args.end):
                if d.isoformat() not in have:
                    for attempt in range(4):
                        try:
                            rows = fn(d)
                            break
                        except Exception as e:
                            print(f"  retry {city} {d}: {e}")
                            time.sleep(5 * (attempt + 1))
                    else:
                        rows = []
                    f.writelines(f"{a},{b}\n" for a, b in rows)
                    n += len(rows)
                    time.sleep(1.0)
                d += timedelta(days=1)
        print(f"{city}: +{n} values")


if __name__ == "__main__":
    main()
