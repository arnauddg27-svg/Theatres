#!/usr/bin/env python3
"""Refresh data/theatre-counts.json from Box Office Mojo once Friday's chart
is up, so sync_opening_theatre_counts has an opening count to write.

    python3 scripts/refresh_theatre_counts.py [--force]

Why (2026-11-08): the counts file was only ever written by Phase 1
collect-links, which the scheduler runs Monday-Thursday. The Saturday/Sunday
refreshes that let the sync replace BOM's pre-release placeholder (The Cat
in the Hat: 216 in metadata vs 4,003 on the chart) came from six legacy cron
lines on a second droplet, retired today. Without them the sync printed "no
post-Friday chart counts; nothing to do" on every weekend finalize.

Runs in finalize before the sync. It fetches only from Saturday 18:00Z (BOM
posts the Friday daily chart Saturday afternoon ET; an earlier fetch would
stamp Thursday-preview counts as the opening count) through Sunday, for the
current collection weekend's tracked openers. Holdovers are left out: their
opening count is already in metadata. Never fails the run.

Not Monday (2026-11-09): by then the tracked state has rolled to NEXT
weekend's calendar titles, so the Monday run looked up five unreleased films,
matched none, and rewrote the file with no counts — the same file Monday's
collect-links owns for the new weekend. A title list that still contains a
film released after today is skipped for the same reason.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FETCH_FROM_UTC_HOUR_SATURDAY = 18


def window_open(now=None):
    """True from Saturday 18:00Z through Sunday 23:59Z (UTC)."""
    now = now or datetime.now(timezone.utc)
    wd = now.weekday()  # Mon=0 ... Sat=5, Sun=6
    if wd == 5:
        return now.hour >= FETCH_FROM_UTC_HOUR_SATURDAY
    return wd == 6


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    force = "--force" in argv
    if not force and not window_open():
        print("refresh_theatre_counts: outside the Sat 18Z-Sun window; nothing to do")
        return 0
    import holdover
    import scraper

    weekend = scraper.opening_weekend_friday(datetime.now())
    if weekend > datetime.now(timezone.utc).strftime("%Y-%m-%d"):
        print(f"refresh_theatre_counts: weekend {weekend} has not opened yet; nothing to do")
        return 0
    titles = scraper.tracked_movie_titles_from_state(weekend)
    openers = holdover.without_holdovers(titles, weekend)
    if not openers:
        print(f"refresh_theatre_counts: no tracked openers for weekend {weekend}; nothing to do")
        return 0
    print(f"refresh_theatre_counts: weekend {weekend}, {len(openers)} opener(s)")
    scraper.fetch_bom_theatre_counts(openers)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never fail finalize over a chart fetch
        print(f"refresh_theatre_counts: failed ({exc}); counts file left as is")
        sys.exit(0)
