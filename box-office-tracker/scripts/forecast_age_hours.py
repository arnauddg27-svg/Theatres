#!/usr/bin/env python3
"""Whole hours since the newest opening-weekend forecast was logged.

The finalize guard skips the forecast step when an AMC run merged no rows.
During a block that is every run: on 2026-11-19 the legs were refused, wrote
next to nothing, and the forecast stayed as it was while the other chains'
lanes kept reading. The guard asks this script and regenerates when the newest
forecast is between FORECAST_REFRESH_MIN_HOURS and FORECAST_REFRESH_MAX_HOURS
old (older than that, nothing is being forecast and there is nothing to
refresh). Prints the age, or -1 when it cannot be read; never fails.
"""
import csv
import os
import sys
from datetime import datetime, timezone

LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "prediction-log.csv")
MIN_HOURS = float(os.environ.get("FORECAST_REFRESH_MIN_HOURS") or 6)
MAX_HOURS = float(os.environ.get("FORECAST_REFRESH_MAX_HOURS") or 72)


def newest_logged_at(path):
    newest = None
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            stamp = (row.get("logged_at") or "").strip()
            if not stamp:
                continue
            try:
                when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError:
                continue
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            if newest is None or when > newest:
                newest = when
    return newest


def age_hours(path=LOG, now=None):
    try:
        newest = newest_logged_at(path)
    except OSError:
        return -1
    if newest is None:
        return -1
    now = now or datetime.now(timezone.utc)
    return int(max((now - newest).total_seconds(), 0) // 3600)


def refresh_due(age, min_hours=MIN_HOURS, max_hours=MAX_HOURS):
    return min_hours <= age <= max_hours


def main(argv):
    age = age_hours()
    if "--due" in argv:
        print("1" if refresh_due(age) else "0")
    else:
        print(age)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
