"""
Recon step 1: enumerate every Polymarket "highest temperature" event (closed + open).

Gamma caps `limit` at 100 and rejects offsets beyond ~2000, so we walk the
calendar in short endDate windows and paginate inside each window.

Writes:
  data/raw/events.jsonl   one raw Gamma event per line (all markets/buckets included)

Usage: python research/fetch_events.py [--start 2024-01-01]
"""
import argparse
import json
import time
from datetime import date, timedelta
from pathlib import Path

import requests

GAMMA = "https://gamma-api.polymarket.com/events"
OUT = Path("data/raw/events.jsonl")
PAGE = 100          # Gamma caps limit at 100
WINDOW_DAYS = 3     # keeps each window well under the offset cap


def get(params: dict) -> list:
    for attempt in range(5):
        try:
            r = requests.get(GAMMA, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"  retry {attempt+1}: {e}")
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Gamma failed for {params}")


def fetch_window(lo: date, hi: date, closed: bool) -> list:
    out, offset = [], 0
    while True:
        page = get({
            "tag_slug": "weather", "closed": str(closed).lower(),
            "end_date_min": f"{lo.isoformat()}T00:00:00Z",
            "end_date_max": f"{hi.isoformat()}T00:00:00Z",
            "limit": PAGE, "offset": offset,
        })
        out.extend(page)
        if len(page) < PAGE:
            return out
        offset += PAGE
        if offset >= 2000:
            raise RuntimeError(f"window {lo}..{hi} too dense, shrink WINDOW_DAYS")
        time.sleep(0.2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2024-01-01")
    args = ap.parse_args()

    seen = {}
    d = date.fromisoformat(args.start)
    end = date.today() + timedelta(days=10)
    while d < end:
        hi = d + timedelta(days=WINDOW_DAYS)
        n_before = len(seen)
        for closed in (True, False):
            for e in fetch_window(d, hi, closed):
                if "temperature" in e.get("slug", ""):
                    seen[e["id"]] = e
        if len(seen) > n_before:
            print(f"{d} .. {hi}: +{len(seen) - n_before} (total {len(seen)})")
        d = hi
        time.sleep(0.2)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        for e in sorted(seen.values(), key=lambda e: e.get("endDate", "")):
            f.write(json.dumps(e) + "\n")
    print(f"saved {len(seen)} temperature events -> {OUT}")


if __name__ == "__main__":
    main()
