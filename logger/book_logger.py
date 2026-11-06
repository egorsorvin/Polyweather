#!/usr/bin/env python3
"""
Polymarket order-book logger for temperature markets.

Records every order-book event (full snapshots `book`, level updates `price_change`, trades
`last_trade_price`, `tick_size_change`, `market_resolved`) of the YES token of all OPEN
"highest / lowest temperature" markets (the NO book is its mirror), from the public WebSocket:

    wss://ws-subscriptions-clob.polymarket.com/ws/market

so that any strategy can later be backtested against the book that was really on offer
(see logger/replay.py).

Output (append-only, gzip, rotated every hour, UTC):
    <out>/raw/YYYY-MM-DD/HH.jsonl.gz     compact event lines (format in Writer docstring)
    <out>/meta/assets.jsonl              aid (small int used in raw lines) -> token id
    <out>/meta/markets.jsonl             one line per market when first seen (slug, question,
                                         token ids, condition id, end date)
    <out>/logger.log                     health: connections, assets, events per minute

Design:
  * discovery every 15 min via the Gamma API (events tagged "weather", not closed, ending
    between yesterday and +5 days); new tokens are subscribed on the fly
  * SIGTERM / Ctrl+C closes the current gzip file cleanly
  * assets are spread over several connections (CHUNK per connection)
  * application heartbeat: text "PING" every 10 s; reconnect with backoff; on reconnect the
    server re-sends a full `book` snapshot for every asset, so the record self-heals
  * writing never blocks receiving (asyncio queue)

Usage:
    pip install websockets requests
    python logger/book_logger.py --out data/orderbook
"""
import argparse
import asyncio
import gzip
import json
import logging
import os
import random
import signal
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
import websockets

WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
GAMMA = "https://gamma-api.polymarket.com/events"
CHUNK = 250                 # assets per WebSocket connection
DISCOVERY_EVERY_S = 15 * 60
PING_EVERY_S = 10

log = logging.getLogger("book_logger")


# ─── discovery ────────────────────────────────────────────────────────────────

def discover() -> dict:
    """token_id -> market meta, for all open temperature markets."""
    out = {}
    lo = date.today() - timedelta(days=1)
    for k in range(0, 6, 2):
        a, b = lo + timedelta(days=k), lo + timedelta(days=k + 2)
        offset = 0
        while True:
            params = {"tag_slug": "weather", "closed": "false", "limit": 100, "offset": offset,
                      "end_date_min": f"{a}T00:00:00Z", "end_date_max": f"{b}T00:00:00Z"}
            r = requests.get(GAMMA, params=params, timeout=60)
            r.raise_for_status()
            page = r.json()
            for e in page:
                if "temperature" not in e.get("slug", ""):
                    continue
                for m in e.get("markets", []):
                    if m.get("closed"):
                        continue
                    try:
                        toks = json.loads(m.get("clobTokenIds") or "[]")
                    except json.JSONDecodeError:
                        continue
                    # YES token only: the NO book is its mirror (NO bid = 1 - YES ask, NO ask = 1 - YES bid)
                    for i, tok in enumerate(toks[:1]):
                        out[tok] = {"token": tok, "outcome": "Yes",
                                    "condition_id": m.get("conditionId"), "market_id": m.get("id"),
                                    "question": m.get("question"), "event_slug": e.get("slug"),
                                    "event_id": e.get("id"), "end_date": e.get("endDate")}
            if len(page) < 100:
                break
            offset += 100
    return out


# ─── writer ───────────────────────────────────────────────────────────────────

class Writer:
    """Compact hourly-rotated gzip writer. One JSON array per line:
        ["b", recv_ms, ts, aid, [[p, s], ...bids], [[p, s], ...asks]]   full book snapshot
        ["c", recv_ms, ts, aid, price, size, side]                       level change (size 0 = level gone)
        ["t", recv_ms, ts, aid, price, size, side, fee_bps]              trade
        ["k", recv_ms, ts, aid, new_tick_size]                           tick size change
        ["r", recv_ms, ts, aid, winning_outcome]                         market resolved
    aid = small integer, mapping in <out>/meta/assets.jsonl ({"aid": n, "token": ...}).
    side: "B" = bid level / buy, "S" = ask level / sell. Prices and sizes as floats.
    """

    def __init__(self, out: Path):
        self.out = out
        self.cur_key = None
        self.fh = None
        self.count = 0
        self.aid = {}
        self.amap = out / "meta" / "assets.jsonl"
        self.amap.parent.mkdir(parents=True, exist_ok=True)
        if self.amap.exists():
            for line in self.amap.open():
                x = json.loads(line)
                self.aid[x["token"]] = x["aid"]

    def _aid(self, tok: str) -> int:
        a = self.aid.get(tok)
        if a is None:
            a = self.aid[tok] = len(self.aid)
            with self.amap.open("a") as f:
                f.write(json.dumps({"aid": a, "token": tok}) + "\n")
        return a

    def _rotate(self, now: datetime):
        key = now.strftime("%Y-%m-%d/%H")
        if key != self.cur_key:
            if self.fh:
                self.fh.close()
            path = self.out / "raw" / f"{key}.jsonl.gz"
            path.parent.mkdir(parents=True, exist_ok=True)
            self.fh = gzip.open(path, "at", compresslevel=6)
            self.cur_key = key

    def _line(self, row):
        self.fh.write(json.dumps(row, separators=(",", ":")) + "\n")
        self.count += 1

    def write(self, recv_ms: int, ev: dict):
        et = ev.get("event_type")
        self._rotate(datetime.fromtimestamp(recv_ms / 1000, tz=timezone.utc))
        ts = int(ev.get("timestamp") or 0)
        if et == "book":
            lv = lambda xs: [[float(x["price"]), float(x["size"])] for x in xs]  # noqa: E731
            self._line(["b", recv_ms, ts, self._aid(ev["asset_id"]), lv(ev.get("bids", [])), lv(ev.get("asks", []))])
        elif et == "price_change":
            for c in ev.get("price_changes", []):
                if c["asset_id"] in self.subscribed:
                    self._line(["c", recv_ms, ts, self._aid(c["asset_id"]), float(c["price"]),
                                float(c["size"]), "B" if c["side"] == "BUY" else "S"])
        elif et == "last_trade_price":
            self._line(["t", recv_ms, ts, self._aid(ev["asset_id"]), float(ev["price"]), float(ev["size"]),
                        "B" if ev.get("side") == "BUY" else "S", int(ev.get("fee_rate_bps") or 0)])
        elif et == "tick_size_change":
            self._line(["k", recv_ms, ts, self._aid(ev["asset_id"]), float(ev["new_tick_size"])])
        elif et == "market_resolved":
            for tok in ev.get("assets_ids", []):
                if tok in self.subscribed:
                    self._line(["r", recv_ms, ts, self._aid(tok), ev.get("winning_outcome")])

    subscribed: set = set()

    def flush(self):
        if self.fh:
            self.fh.flush()

    def close(self):
        if self.fh:
            self.fh.close()
            self.fh = None


async def writer_task(q: asyncio.Queue, w: Writer):
    last_flush = time.time()
    while True:
        recv_ms, raw = await q.get()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for ev in data if isinstance(data, list) else [data]:
            if isinstance(ev, dict):
                w.write(recv_ms, ev)
        if time.time() - last_flush > 5:
            w.flush()
            last_flush = time.time()


# ─── connections ──────────────────────────────────────────────────────────────

class Conn:
    """One WebSocket connection carrying up to CHUNK assets."""

    def __init__(self, cid: int, q: asyncio.Queue, stats: dict):
        self.cid, self.q, self.stats = cid, q, stats
        self.assets: set = set()
        self.ws = None
        self.pending_add: set = set()
        self.pending_remove: set = set()

    async def run(self):
        backoff = 1
        while True:
            if not self.assets:
                await asyncio.sleep(5)
                continue
            try:
                async with websockets.connect(WS_URL, ping_interval=None, max_size=2**24,
                                              open_timeout=30) as ws:
                    self.ws = ws
                    await ws.send(json.dumps({"assets_ids": sorted(self.assets), "type": "market"}))
                    self.pending_add.clear()
                    self.stats["connects"] += 1
                    log.info(f"conn {self.cid}: connected, {len(self.assets)} assets")
                    backoff = 1
                    pinger = asyncio.create_task(self._ping(ws))
                    try:
                        async for raw in ws:
                            if raw == "PONG":
                                continue
                            self.q.put_nowait((int(time.time() * 1000), raw))
                            self.stats["frames"] += 1
                            await self._apply_pending(ws)
                    finally:
                        pinger.cancel()
            except Exception as e:  # network errors, server closes, timeouts
                self.stats["errors"] += 1
                log.warning(f"conn {self.cid}: {type(e).__name__}: {e}; reconnect in {backoff}s")
            self.ws = None
            await asyncio.sleep(backoff + random.random())
            backoff = min(backoff * 2, 60)

    async def _ping(self, ws):
        while True:
            await asyncio.sleep(PING_EVERY_S)
            await ws.send("PING")
            await self._apply_pending(ws)

    async def _apply_pending(self, ws):
        if self.pending_add:
            add, self.pending_add = sorted(self.pending_add), set()
            await ws.send(json.dumps({"assets_ids": add, "operation": "subscribe"}))
        if self.pending_remove:
            rem, self.pending_remove = sorted(self.pending_remove), set()
            await ws.send(json.dumps({"assets_ids": rem, "operation": "unsubscribe"}))

    def add(self, toks):
        self.assets |= set(toks)
        if self.ws is not None:
            self.pending_add |= set(toks)

    def remove(self, toks):
        self.assets -= set(toks)
        if self.ws is not None:
            self.pending_remove |= set(toks)


async def manager(out: Path, q: asyncio.Queue, stats: dict, w: "Writer"):
    conns: list[Conn] = []
    known: dict = {}
    meta_path = out / "meta" / "markets.jsonl"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            found = await asyncio.to_thread(discover)
        except Exception as e:
            log.warning(f"discovery failed: {e}")
            await asyncio.sleep(60)
            continue
        new = [t for t in found if t not in known]
        gone = [t for t in known if t not in found]
        with meta_path.open("a") as f:
            for t in new:
                f.write(json.dumps({"seen": datetime.now(timezone.utc).isoformat(), **found[t]}) + "\n")
        for c in conns:
            g = [t for t in gone if t in c.assets]
            if g:
                c.remove(g)
        for t in gone:
            known.pop(t, None)
        while new:
            c = next((c for c in conns if len(c.assets) < CHUNK), None)
            if c is None:
                c = Conn(len(conns), q, stats)
                conns.append(c)
                asyncio.create_task(c.run())
            room = CHUNK - len(c.assets)
            c.add(new[:room])
            new = new[room:]
        known.update(found)
        w.subscribed = set(known)
        stats["assets"] = len(known)
        stats["conns"] = len(conns)
        log.info(f"discovery: {len(known)} assets on {len(conns)} connections")
        await asyncio.sleep(DISCOVERY_EVERY_S)


async def health(stats: dict, w: Writer):
    last_ev = 0
    while True:
        await asyncio.sleep(60)
        log.info(f"health: assets={stats['assets']} conns={stats['conns']} frames={stats['frames']} "
                 f"events/min={w.count - last_ev} errors={stats['errors']} connects={stats['connects']}")
        last_ev = w.count


async def main_async(out: Path):
    q: asyncio.Queue = asyncio.Queue()
    w = Writer(out)
    stats = {"frames": 0, "errors": 0, "connects": 0, "assets": 0, "conns": 0}
    try:
        loop = asyncio.get_running_loop()
        stop = asyncio.Event()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, stop.set)
        tasks = [asyncio.create_task(x) for x in (writer_task(q, w), manager(out, q, stats, w), health(stats, w))]
        await stop.wait()
        log.info("stop signal: closing files")
        for t in tasks:
            t.cancel()
    finally:
        w.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data/orderbook")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler(out / "logger.log")])
    log.info(f"book logger starting, pid {os.getpid()}, out={out.resolve()}")
    asyncio.run(main_async(out))


if __name__ == "__main__":
    main()
