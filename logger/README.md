# Order-book logger

Records the full order book of every open Polymarket temperature market (YES token; NO is its
mirror) from the public market WebSocket, so strategies can be backtested against the prices and
depth that were really on offer — not against the last trade.

* `book_logger.py` — the recorder (runs 24/7 on a server)
* `replay.py` — rebuilds the book at any moment and prices a taker order (`cost_to_buy`)
* `polyweather-book-logger.service` — systemd unit

## Install on the server (Ubuntu / Debian)

```bash
git clone https://github.com/egorsorvin/Polyweather.git
cd Polyweather
git checkout claude/brave-hawking-jzbxx3
python3 -m venv .venv
.venv/bin/pip install websockets requests
```

Test run (Ctrl+C to stop, the current file is closed cleanly):

```bash
.venv/bin/python logger/book_logger.py --out data/orderbook
```

Run as a service (starts on boot, restarts on crash). Edit `User` and the paths in the unit file
if your user or folder differ:

```bash
sudo cp logger/polyweather-book-logger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now polyweather-book-logger
```

Check it:

```bash
systemctl status polyweather-book-logger
tail -f data/orderbook/logger.log
```

A healthy log line every minute looks like
`health: assets=3080 conns=13 frames=... events/min=... errors=0`.

## Output

```
data/orderbook/raw/YYYY-MM-DD/HH.jsonl.gz   one compact JSON array per event (UTC hours)
data/orderbook/meta/assets.jsonl            compact id -> CLOB token id
data/orderbook/meta/markets.jsonl           token -> question, event slug, end date
data/orderbook/logger.log                   health log
```

Event lines (see `Writer` in `book_logger.py`):
`["b", recv_ms, ts, aid, bids, asks]` full snapshot, `["c", recv_ms, ts, aid, price, size, side]`
level change (size 0 removes the level), `["t", ...]` trade, `["k", ...]` tick size,
`["r", ...]` resolution.

Size: roughly 0.5–1 GB per day for ~3,000 markets. Keep at least a few weeks; back the folder up
off the server (e.g. `rclone sync data/orderbook remote:polyweather-orderbook` from cron) so the
record is not lost with the machine.

## Use it

```bash
python logger/replay.py --out data/orderbook --start 2026-11-07T12:00 --end 2026-11-07T13:00
```

```python
from logger.replay import Replay
rp = Replay("data/orderbook")
for t, aid in rp.run("2026-11-07T12:00", "2026-11-07T13:00"):
    avg_price, filled = rp.books[aid].cost_to_buy("NO", 200)
```
