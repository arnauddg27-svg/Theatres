#!/usr/bin/env python3
"""Probe: can a GitHub runner read Cinemark seat maps over PLAIN HTTP?

The TicketSeatMap page is server-rendered: one <button available="True|False"
class="seat... seatBlock"> per seat. From a residential address a plain GET
returns the full map in ~1 s (2026-09-27); the browser lane spends ~10 s per
map and ~half come back as the client-side "Something went wrong" page. This
probe harvests showtime links from a few theatre pages over HTTP and counts
seats on up to 40 maps, printing status/timing only.
"""
import re
import sys
import time
from curl_cffi import requests as cr

THEATRES = ["tx-dallas/cinemark-dallas-xd-and-imax", "co-denver/cinemark-denver-and-xd",
            "ca-sacramento/century-arden-14-and-xd", "oh-columbus/cinemark-movies-10",
            "tx-plano/cinemark-legacy-and-imax"]
SEAT_RE = re.compile(r'<button[^>]*?available="(True|False)"[^>]*?class="[^"]*seatBlock', re.I)
LINK_RE = re.compile(r'href="(/TicketSeatMap/\?[^"]+)"')


def main():
    s = cr.Session(impersonate="chrome")
    links, stats = [], {"theatre_ok": 0, "theatre_fail": 0, "maps_ok": 0, "maps_empty": 0, "maps_fail": 0, "wrong": 0}
    import csv, os, random
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cinemark-showtime-links.csv")
    rows = list(csv.DictReader(open(path))) if os.path.exists(path) else []
    random.seed(7); random.shuffle(rows)
    links = [r["href"].replace("https://www.cinemark.com", "") for r in rows]
    print(f"stored links available: {len(rows)}", flush=True)
    t0 = time.time()
    for h in links[:60]:
        try:
            r = s.get("https://www.cinemark.com" + h, timeout=30)
            av = SEAT_RE.findall(r.text)
            if "Something went wrong" in r.text:
                stats["wrong"] += 1
            if r.status_code == 429:
                stats["throttled"] = stats.get("throttled", 0) + 1
            if av:
                stats["maps_ok"] += 1
                print(f"  map status={r.status_code} seats={len(av)} sold={av.count('False')} {len(r.content)//1024}KB", flush=True)
            else:
                stats["maps_empty"] += 1
                print(f"  map status={r.status_code} EMPTY {len(r.content)//1024}KB title={re.search(r'<title>([^<]*)', r.text).group(1)[:50] if '<title>' in r.text else ''}", flush=True)
        except Exception as e:
            stats["maps_fail"] += 1
            print(f"  map {type(e).__name__}", flush=True)
        time.sleep(float(__import__('os').environ.get('PROBE_PACE_SEC', '5')))
    n = max(1, len(links[:60]))
    print(f"SUMMARY {stats} per_map={(time.time() - t0) / n:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
