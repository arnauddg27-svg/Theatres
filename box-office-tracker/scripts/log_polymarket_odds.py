#!/usr/bin/env python3
"""Append a timestamped snapshot of every live opening-weekend Polymarket
bracket to data/polymarket-odds-log.csv.

2026-10-24: polymarket-markets.csv keeps one row per bracket per DAY (the first
observation), so intraday moves were lost — Wildwood's $12-14M favourite at
Friday 15Z had flipped to $10-12M by Saturday and only one of the two prices
was on disk. This runs in finalize right after predict.py, so every logged
forecast has the market odds of the same moment next to it.

Standalone (stdlib only): finalize does not install playwright, which
scraper.py imports. Advisory: any error prints a ::warning:: and exits 0.

    python3 scripts/log_polymarket_odds.py
"""
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ODDS_LOG = os.path.join(DATA_DIR, "polymarket-odds-log.csv")
SEARCH_URL = "https://gamma-api.polymarket.com/public-search"
FIELDS = ["logged_at", "weekend_of", "movie", "event_slug", "bracket", "yes_price",
          "best_bid", "best_ask", "last_trade", "volume", "market_id"]


def opening_weekend_friday(now):
    """Fri-Sun -> that Friday; Mon-Thu -> the coming Friday."""
    if now.weekday() >= 4:
        return (now - timedelta(days=now.weekday() - 4)).strftime("%Y-%m-%d")
    return (now + timedelta(days=4 - now.weekday())).strftime("%Y-%m-%d")


def event_weekend(ev, now):
    """The Friday on or before the market's end date (markets end Sun/Mon of
    the opening weekend); falls back to the calendar weekend of `now`."""
    try:
        end = datetime.fromisoformat(str(ev.get("endDate")).replace("Z", "+00:00"))
        return (end - timedelta(days=(end.weekday() - 4) % 7)).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return opening_weekend_friday(now)


def _get(url, params):
    req = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params)}",
                                 headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def fetch_events():
    # limit_per_type, not limit: the plain `limit` param returns 5 events, which
    # missed Ali G and Klara and the Sun on 2026-10-24.
    data = _get(SEARCH_URL, {"q": "opening weekend box office", "limit_per_type": 50,
                             "events_status": "active"})
    return data.get("events", []) if isinstance(data, dict) else (data or [])


def movie_name(title):
    title = (title or "").replace("“", '"').replace("”", '"')
    m = re.search(r'"([^"]+)"', title)
    return m.group(1).strip() if m else None


def _f(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return ""


def odds_rows(events, now):
    logged_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for ev in events:
        title = str(ev.get("title") or "")
        tl = title.lower()
        if ev.get("closed") or "opening weekend" not in tl or "box office" not in tl:
            continue
        movie = movie_name(title)
        if not movie:
            continue
        weekend = event_weekend(ev, now)
        for m in ev.get("markets") or []:
            if m.get("closed"):
                continue
            try:
                prices = json.loads(m.get("outcomePrices") or "[]")
            except ValueError:
                prices = []
            rows.append({
                "logged_at": logged_at, "weekend_of": weekend, "movie": movie,
                "event_slug": ev.get("slug", ""),
                "bracket": m.get("groupItemTitle") or m.get("question", ""),
                "yes_price": _f(prices[0]) if prices else "",
                "best_bid": _f(m.get("bestBid")), "best_ask": _f(m.get("bestAsk")),
                "last_trade": _f(m.get("lastTradePrice")), "volume": _f(m.get("volume")),
                "market_id": str(m.get("id", "")),
            })
    return rows


def append(rows, path=ODDS_LOG):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def main():
    now = datetime.now(timezone.utc)
    try:
        rows = odds_rows(fetch_events(), now)
    except Exception as exc:  # advisory
        print(f"::warning::Polymarket odds snapshot failed: {type(exc).__name__}: {exc}")
        return 0
    if not rows:
        print("Polymarket odds: no live opening-weekend brackets")
        return 0
    append(rows)
    films = sorted({r["movie"] for r in rows})
    print(f"Polymarket odds: logged {len(rows)} brackets for {len(films)} film(s): {', '.join(films)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
