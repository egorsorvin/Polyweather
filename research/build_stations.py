"""
Build data/stations.csv: the station each city's market resolves on (latest event),
with coordinates from aviationweather.gov, unit, activity and volume.

Usage: python research/build_stations.py
"""
import csv
import collections
import json
import re
from pathlib import Path

import requests

EVENTS = Path("data/raw/events.jsonl")
OUT = Path("data/stations.csv")
MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
ALIASES = {"new-york-city": "nyc"}
SKIP = {"dc", "phoenix", "dubai"}          # one-off events
# Not METAR stations: resolved on a national met service's own observatory.
MANUAL = {"hong-kong": {"icao": "HKO", "lat": 22.302, "lon": 114.174, "elev_m": 32,
                        "name": "Hong Kong Observatory HQ"}}
TZ = json.loads(Path("research/timezones.json").read_text())


def main():
    info = collections.defaultdict(lambda: {"n": 0, "vol": 0.0, "first": "9", "last": "0",
                                            "icao": None, "unit": None, "source": None})
    for line in EVENTS.open():
        e = json.loads(line)
        m = re.match(r"highest-temperature-in-(.+?)-on-", e["slug"])
        if not m or not re.search(rf"-on-({MONTHS})-", e["slug"]):
            continue
        city = ALIASES.get(m.group(1), m.group(1))
        if city in SKIP:
            continue
        d = info[city]
        d["n"] += 1
        d["vol"] += float(e.get("volume") or 0)
        d["first"] = min(d["first"], e["endDate"][:10])
        if e["endDate"][:10] >= d["last"]:
            d["last"] = e["endDate"][:10]
            src = (e.get("resolutionSource") or "") + " " + e.get("description", "")
            ids = re.findall(r"(?:history/daily/[^\s\"]*?/|site=|ids=|\()([A-Za-z0-9]{4})\b", src)
            ids = [x.upper() for x in ids if x.upper() != "HTTP"]
            if ids:
                d["icao"] = ids[0]
            q = " ".join(x.get("question", "") for x in e.get("markets", []))
            d["unit"] = "F" if "°F" in q else "C"
            d["source"] = re.sub(r"https?://(www\.)?", "", (e.get("resolutionSource") or "")).split("/")[0] or "see description"

    icaos = sorted({d["icao"] for c, d in info.items() if d["icao"] and c not in MANUAL})
    st = {x["icaoId"]: x for x in requests.get(
        "https://aviationweather.gov/api/data/stationinfo",
        params={"ids": ",".join(icaos), "format": "json"}, timeout=60).json()}

    rows = []
    for city, d in sorted(info.items(), key=lambda kv: -kv[1]["vol"]):
        s = MANUAL.get(city) or st.get(d["icao"], {})
        rows.append({
            "city": city, "icao": s.get("icao", d["icao"]), "lat": s.get("lat"), "lon": s.get("lon"),
            "elev_m": s.get("elev_m", s.get("elev")), "station_name": s.get("name", s.get("site")),
            "timezone": TZ[city], "unit": d["unit"], "latest_source": d["source"],
            "n_events": d["n"], "volume_musd": round(d["vol"] / 1e6, 2),
            "first_event": d["first"], "last_event": d["last"],
        })
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"saved {len(rows)} stations -> {OUT}")


if __name__ == "__main__":
    main()
