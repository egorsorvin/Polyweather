"""
Recon step 2: download the full trade tape for every closed "highest temperature" event.

Source: Polymarket Data API v2  GET /v2/trades?eventId=<id>  (cursor pagination).
Each trade = one taker fill: timestamp, token, outcome (Yes/No), side, price, size.

Writes one gzip CSV per event:
  data/raw/trades/<event_id>.csv.gz
Already-downloaded events are skipped, so the script can be resumed.

Usage:
  python research/fetch_trades.py                    # all closed events
  python research/fetch_trades.py --since 2025-09-01 # only events ending after a date
  python research/fetch_trades.py --limit 200        # quick sample
"""
import argparse
import csv
import gzip
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

API = "https://data-api.polymarket.com/v2/trades"
EVENTS = Path("data/raw/events.jsonl")
OUT_DIR = Path("data/raw/trades")
FIELDS = ["timestamp", "condition_id", "token_id", "outcome", "outcome_index",
          "side", "price", "size", "proxy_wallet", "transaction_hash"]

session = requests.Session()


def get(params: dict) -> dict:
    for attempt in range(6):
        try:
            r = session.get(API, params=params, timeout=60)
            if r.status_code == 429:
                time.sleep(5 + 5 * attempt)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == 5:
                raise
            time.sleep(2 ** attempt + random.random())
    raise RuntimeError("unreachable")


def fetch_event(event_id: str) -> int:
    out = OUT_DIR / f"{event_id}.csv.gz"
    if out.exists():
        return -1
    rows, cursor = [], None
    while True:
        params = {"eventId": event_id, "limit": 1000}
        if cursor:
            params["cursor"] = cursor
        page = get(params)
        rows.extend(page.get("data", []))
        cursor = page.get("pagination", {}).get("next_cursor")
        if not cursor or not page.get("pagination", {}).get("has_more"):
            break
    tmp = out.with_suffix(".tmp")
    with gzip.open(tmp, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    tmp.rename(out)
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2000-01-01")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = [json.loads(l) for l in EVENTS.open()]
    todo = [e["id"] for e in events
            if e["slug"].startswith("highest-temperature-in-")
            and e.get("closed") and e.get("endDate", "") >= args.since]
    random.Random(0).shuffle(todo)
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(todo)} events to fetch")

    done = n_trades = 0
    with ThreadPoolExecutor(args.workers) as pool:
        futs = {pool.submit(fetch_event, eid): eid for eid in todo}
        for fut in as_completed(futs):
            try:
                n = fut.result()
                n_trades += max(n, 0)
            except Exception as e:
                print(f"  event {futs[fut]} failed: {e}")
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(todo)} events, {n_trades} trades")
    print(f"done: {done} events, {n_trades} new trades")


if __name__ == "__main__":
    main()
