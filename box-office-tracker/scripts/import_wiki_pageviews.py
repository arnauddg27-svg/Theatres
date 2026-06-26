#!/usr/bin/env python3
"""Wikipedia release-week pageviews as a leak-free word-of-mouth / anticipation
signal for the box-office model.

Why Wikipedia: the Wikimedia pageviews API is official, free, unauthenticated,
and has full daily history back to 2015 — so unlike Twitter/Reddit/Trends it can
be BACKFILLED across the whole comp library and therefore *calibrated* (the same
discipline as the reviews layer). Release-week article traffic is a well-
established opening-weekend predictor.

Leak-free window: the Monday-Thursday immediately before the opening Friday.
  * Live (weekend_of known): window = [Fri-4, Fri-1].
  * Backfill (only release_year known): locate the opening Friday from the
    pageview spike, then take the Mon-Thu before it (validated 5/5 vs known
    dates), so the window never includes opening-weekend reaction.

Usage:
  python3 scripts/import_wiki_pageviews.py --backfill   # fill historical-comps.csv
  python3 scripts/import_wiki_pageviews.py              # current weekend -> social-signals.csv
  python3 scripts/import_wiki_pageviews.py --movies "Supergirl" --weekend 2026-06-26
  python3 scripts/import_wiki_pageviews.py --dry-run
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import predict as P  # noqa: E402

UA = "box-office-wom/0.1 (research; contact arnauddg27@gmail.com)"
COMPS_CSV = os.path.join(P.DATA_DIR, "historical-comps.csv")
CACHE_PATH = os.path.join(P.DATA_DIR, ".wiki-pageviews-cache.json")
PAGEVIEWS = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
             "en.wikipedia.org/all-access/all-agents/{article}/daily/{start}/{end}")
SOCIAL_FIELDS = ["weekend_of", "as_of_date", "movie_title", "platform", "source",
                 "mentions", "engagement", "views", "social_media_universe_m",
                 "likes", "comments", "shares", "positive_mentions",
                 "negative_mentions", "neutral_mentions", "sentiment_score",
                 "buzz_score", "notes"]


def _get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            last = e
            code = getattr(e, "code", None)
            if code == 404:
                return None
            time.sleep(0.6 * (i + 1))
    raise last


def _norm(s):
    return "".join(c for c in (s or "").lower() if c.isalnum())


def resolve_article(title, year):
    """Map a film title to its exact English Wikipedia article (film-biased)."""
    q = f"{title} {year} film".strip()
    url = ("https://en.wikipedia.org/w/api.php?action=query&list=search&format=json"
           "&srlimit=5&srsearch=" + urllib.parse.quote(q))
    data = _get(url) or {}
    hits = [h["title"] for h in data.get("query", {}).get("search", [])]
    nt = _norm(title)
    for c in hits:
        if nt in _norm(c) and ("film" in c.lower() or str(year) in c):
            return c
    for c in hits:
        if _norm(title) == _norm(c.split("(")[0]):
            return c
    return hits[0] if hits else None


def daily_pageviews(article, start, end):
    a = urllib.parse.quote(article.replace(" ", "_"), safe="")
    data = _get(PAGEVIEWS.format(article=a, start=start, end=end))
    return (data or {}).get("items", []) if data else []


def _window_sum(items, mon, days=4):
    by = {i["timestamp"][:8]: i["views"] for i in items}
    return sum(by.get((mon + timedelta(days=k)).strftime("%Y%m%d"), 0) for k in range(days))


def anticipation_for_weekend(article, weekend_of):
    """Exact leak-free Mon-Thu anticipation for a known opening Friday."""
    friday = datetime.strptime(weekend_of, "%Y-%m-%d")
    mon, thu = friday - timedelta(days=4), friday - timedelta(days=1)
    items = daily_pageviews(article, mon.strftime("%Y%m%d"), thu.strftime("%Y%m%d"))
    return _window_sum(items, mon), friday.strftime("%Y-%m-%d")


def opening_friday_from_peak(d):
    """Map a pageview-peak day to the opening Friday (pure; leak-free anchor).

    The release spike usually lands on opening Fri/Sat/Sun -> that week's Friday.
    A Mon/Tue peak means the weekend just ended -> the previous Friday. A
    mid-week (Wed/Thu) peak (preview-driven) -> that week's upcoming Friday.
    """
    wd = d.weekday()  # Mon=0 .. Sun=6
    if wd in (4, 5, 6):
        return d - timedelta(days=wd - 4)
    if wd in (0, 1):
        return d - timedelta(days=wd + 3)
    return d + timedelta(days=4 - wd)


def detect_opening_and_anticipation(article, year):
    """Locate the opening Friday from the pageview spike, return (friday, antic)."""
    items = daily_pageviews(article, f"{year}0101", f"{int(year) + 1}0228")
    if not items:
        return None, 0, 0
    peak = max(items, key=lambda i: i["views"])
    d = datetime.strptime(peak["timestamp"][:8], "%Y%m%d")
    friday = opening_friday_from_peak(d)
    antic = _window_sum(items, friday - timedelta(days=4))
    return friday.strftime("%Y-%m-%d"), antic, peak["views"]


# ── cache ────────────────────────────────────────────────────────────────────
def _load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            return json.load(open(CACHE_PATH))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def _save_cache(cache):
    json.dump(cache, open(CACHE_PATH, "w"), indent=0)


# ── backfill ─────────────────────────────────────────────────────────────────
def backfill_comps(dry_run=False, throttle=0.25):
    rows = list(csv.DictReader(open(COMPS_CSV)))
    fields = list(rows[0].keys())
    for col in ("wiki_release_week_views", "wiki_article", "wiki_opening_friday"):
        if col not in fields:
            fields.append(col)
    cache = _load_cache()
    filled = 0
    for r in rows:
        title, year = r["movie"], r.get("release_year", "")
        key = f"{title}|{year}"
        if key in cache:
            info = cache[key]
        else:
            art = resolve_article(title, year)
            time.sleep(throttle)
            friday, antic, peak = (detect_opening_and_anticipation(art, year)
                                   if art else (None, 0, 0))
            time.sleep(throttle)
            info = {"article": art, "friday": friday, "views": antic, "peak": peak}
            cache[key] = info
            _save_cache(cache)
        r["wiki_release_week_views"] = info["views"] or ""
        r["wiki_article"] = info["article"] or ""
        r["wiki_opening_friday"] = info["friday"] or ""
        if info["views"]:
            filled += 1
        print(f"  {title[:30]:30} {year} -> {str(info['article'])[:34]:34} "
              f"views={info['views'] or 0:>10,}")
    print(f"\nresolved release-week views for {filled}/{len(rows)} comps")
    if dry_run:
        print("[dry-run] historical-comps.csv NOT written")
        return
    with open(COMPS_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {COMPS_CSV}")


# ── live fetch -> social-signals.csv ─────────────────────────────────────────
def fetch_current(weekend, films, dry_run=False):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = []
    for title in films:
        art = resolve_article(title, int(weekend[:4]))
        if not art:
            print(f"  {title}: no Wikipedia article — skipped")
            continue
        views, friday = anticipation_for_weekend(art, weekend)
        print(f"  {title}: {art} release-week (Mon-Thu) views={views:,}")
        rows.append({
            "weekend_of": weekend, "as_of_date": today, "movie_title": title,
            "platform": "wikipedia", "source": "wikimedia-pageviews",
            "mentions": "", "engagement": "", "views": views,
            "social_media_universe_m": "", "likes": "", "comments": "",
            "shares": "", "positive_mentions": "", "negative_mentions": "",
            "neutral_mentions": "", "sentiment_score": "", "buzz_score": "",
            "notes": f"en.wikipedia/{art}; Mon-Thu before {friday}",
        })
    if dry_run:
        print(f"\n[dry-run] would write {len(rows)} row(s) to {P.SOCIAL_SIGNALS_CSV}")
        return
    _append_social(rows)


def _append_social(rows):
    path = P.SOCIAL_SIGNALS_CSV
    existing = set()
    if os.path.exists(path):
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                existing.add((r.get("movie_title", ""), r.get("as_of_date", ""),
                              r.get("platform", "")))
    new = [r for r in rows if (r["movie_title"], r["as_of_date"], r["platform"]) not in existing]
    write_header = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SOCIAL_FIELDS)
        if write_header:
            w.writeheader()
        w.writerows(new)
    print(f"\nwrote {len(new)} new wikipedia social-signal row(s) -> {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backfill", action="store_true", help="fill historical-comps.csv")
    ap.add_argument("--weekend", help="weekend_of (YYYY-MM-DD)")
    ap.add_argument("--movies", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.backfill:
        backfill_comps(dry_run=args.dry_run)
        return 0

    weekend = args.weekend or P._current_weekend_friday()
    films = args.movies or sorted(P.load_seat_data(weekend_of=weekend).keys())
    if not films:
        print("No films to fetch.")
        return 0
    print(f"Fetching Wikipedia anticipation for weekend {weekend}: {films}")
    fetch_current(weekend, films, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
