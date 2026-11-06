#!/usr/bin/env python3
"""
Replay the order-book record written by logger/book_logger.py.

    from logger.replay import Replay
    rp = Replay("data/orderbook")
    for t_ms, aid in rp.run(start="2026-11-06T12:00", end="2026-11-06T13:00"):
        book = rp.books[aid]                 # current state after this event
        book.best_bid(), book.best_ask()
        book.cost_to_buy("YES", 100)         # (avg price, filled shares) walking the asks
        book.cost_to_buy("NO", 100)          # NO bought = YES bids hit at 1 - bid

`rp.token(aid)` / `rp.aid_of(token)` map between the compact id and the CLOB token id;
`rp.meta[token]` holds question, event slug and end date from meta/markets.jsonl.

CLI:  python logger/replay.py --out data/orderbook --start 2026-11-06T12:00 --end 2026-11-06T12:10
      prints a short summary (events, books, median spread, depth within 2c of the touch).
"""
import argparse
import glob
import gzip
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path


class Book:
    __slots__ = ("bids", "asks", "ts")

    def __init__(self):
        self.bids, self.asks, self.ts = {}, {}, 0

    def best_bid(self):
        return max(self.bids) if self.bids else None

    def best_ask(self):
        return min(self.asks) if self.asks else None

    def cost_to_buy(self, outcome: str, shares: float):
        """Average price and filled shares when buying `shares` of YES or NO as a taker."""
        if outcome.upper() == "YES":
            levels = sorted(self.asks.items())                       # cheapest ask first
        else:
            levels = [(round(1 - p, 6), s) for p, s in sorted(self.bids.items(), reverse=True)]
        left, cost = shares, 0.0
        for p, s in levels:
            take = min(left, s)
            cost += take * p
            left -= take
            if left <= 1e-9:
                break
        filled = shares - max(left, 0.0)
        return (cost / filled if filled else None), filled

    def depth(self, outcome: str, within: float = 0.02) -> float:
        """Shares available within `within` of the best price for buying `outcome`."""
        if outcome.upper() == "YES":
            a = self.best_ask()
            return sum(s for p, s in self.asks.items() if a is not None and p <= a + within)
        b = self.best_bid()
        return sum(s for p, s in self.bids.items() if b is not None and p >= b - within)


class Replay:
    def __init__(self, out="data/orderbook"):
        self.out = Path(out)
        self.books = {}
        self._tok = {}
        for line in (self.out / "meta" / "assets.jsonl").open():
            x = json.loads(line)
            self._tok[x["aid"]] = x["token"]
        self._aid = {t: a for a, t in self._tok.items()}
        self.meta = {}
        mp = self.out / "meta" / "markets.jsonl"
        if mp.exists():
            for line in mp.open():
                x = json.loads(line)
                self.meta[x["token"]] = x

    def token(self, aid):
        return self._tok.get(aid)

    def aid_of(self, token):
        return self._aid.get(token)

    def _files(self, start, end):
        fs = sorted(glob.glob(str(self.out / "raw" / "*" / "*.jsonl.gz")))
        key = lambda f: f.split("/raw/")[1][:13].replace("/", "T")  # noqa: E731  YYYY-MM-DDTHH
        return [f for f in fs if (start is None or key(f) >= start[:13]) and (end is None or key(f) <= end[:13])]

    def run(self, start=None, end=None):
        """Yield (receive_ms, aid) after applying each event in time order within [start, end]."""
        t0 = int(datetime.fromisoformat(start).replace(tzinfo=timezone.utc).timestamp() * 1000) if start else None
        t1 = int(datetime.fromisoformat(end).replace(tzinfo=timezone.utc).timestamp() * 1000) if end else None
        for f in self._files(start, end):
            fh = gzip.open(f, "rt")
            try:
                for line in fh:
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    kind, recv, ts, aid = r[0], r[1], r[2], r[3]
                    if t1 is not None and recv > t1:
                        return
                    b = self.books.setdefault(aid, Book())
                    if kind == "b":
                        b.bids = {p: s for p, s in r[4] if s > 0}
                        b.asks = {p: s for p, s in r[5] if s > 0}
                    elif kind == "c":
                        side = b.bids if r[6] == "B" else b.asks
                        if r[5] > 0:
                            side[r[4]] = r[5]
                        else:
                            side.pop(r[4], None)
                    b.ts = ts or recv
                    if t0 is None or recv >= t0:
                        yield recv, aid
            except EOFError:
                pass  # file of a crashed run: keep what was readable
            finally:
                fh.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/orderbook")
    ap.add_argument("--start")
    ap.add_argument("--end")
    args = ap.parse_args()
    rp = Replay(args.out)
    n = 0
    for _ in rp.run(args.start, args.end):
        n += 1
    spreads = [b.best_ask() - b.best_bid() for b in rp.books.values() if b.best_bid() and b.best_ask()]
    dy = [b.depth("YES") for b in rp.books.values() if b.asks]
    dn = [b.depth("NO") for b in rp.books.values() if b.bids]
    print(f"events {n}, books {len(rp.books)} ({len(spreads)} two-sided)")
    if spreads:
        print(f"median spread {statistics.median(spreads):.3f}; median depth within 2c: "
              f"YES {statistics.median(dy):.0f} sh, NO {statistics.median(dn):.0f} sh")


if __name__ == "__main__":
    main()
