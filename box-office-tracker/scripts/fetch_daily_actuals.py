#!/usr/bin/env python3
"""Auto-fetch reported daily actuals from The Numbers into daily-actual-overrides.csv.

The model has fully-built same-week anchor machinery (predict.py:
same_week_amc_share_anchor + apply_same_week_actual_seat_scales) that
re-derives a film's true AMC share and seat-scale from a single reported
daily actual — exactly the correction that would have caught the 2026-08-28
misses (+40%/+79%, both share-driven) by Saturday. Its input file has been
hand-maintained and empty since June. The Numbers publishes each day's
grosses the next morning and calibrate.py already has a working fetcher, so
this script closes the loop: every finalize, fetch the tracked weekend's
completed days and upsert them into the overrides CSV.

Leak safety: rows carry as_of_date = today. calibrate.py's recording replay
loads overrides with through_date = the weekend's Sunday, so anything fetched
after the weekend closes is excluded from the recorded baseline, while rows
fetched DURING the weekend are included — matching what the live forecast
actually knew. Informational by design: always exits 0 (a fetch hiccup must
not brick finalize; the next finalize retries).
"""
import csv
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OVERRIDES_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "daily-actual-overrides.csv",
)
FIELDS = ["weekend_of", "movie_title", "day_of_week", "gross_m", "source",
          "status", "as_of_date", "notes"]
# The Numbers publishes a day's chart "by the next morning" (ET). Treat day D
# as fetchable from D+1 13:00 UTC (~9am ET); earlier finalizes skip it and a
# later one picks it up.
PUBLICATION_HOUR_UTC = 13
# Ignore obviously-bogus parses.
MIN_GROSS_M, MAX_GROSS_M = 0.05, 500.0
# Re-append only when the reported number moved by more than this fraction
# (The Numbers revises estimates into finals).
UPSERT_TOLERANCE = 0.02

DAY_OFFSETS = {"Thursday": -1, "Friday": 0, "Saturday": 1, "Sunday": 2}
# Only Saturday/Sunday are emitted as anchors. Tested on the 2026-08-28 ground
# truth: a Saturday anchor improved the Sunday-morning forecast for BOTH films
# (Coyote +42%->+34%, Dog Stars +78%->+65%), while a Friday anchor made both
# WORSE (+46%->+88%, +75%->+97%) for two reasons that auto-fetch cannot fix:
# The Numbers folds Thursday previews into Friday's gross mid-weekend (false
# "model reads low" signal), and Friday's implied AMC share is systematically
# the weekend's low outlier, so transferring it to Sat/Sun amplifies the share
# error. Thursday/Friday anchors stay with the manual process, which knows how
# to split previews from separately-reported numbers.
SAFE_ANCHOR_DAYS = ("Saturday", "Sunday")


def completed_days(weekend_of, now_utc):
    """Opening-weekend day names whose numbers should be published by now."""
    try:
        friday = datetime.strptime(weekend_of, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return []
    out = []
    for day, offset in DAY_OFFSETS.items():
        day_date = friday + timedelta(days=offset)
        publishable_from = day_date + timedelta(days=1, hours=PUBLICATION_HOUR_UTC)
        if now_utc >= publishable_from:
            out.append(day)
    return out


def merge_override_rows(existing_rows, weekend_of, movie, day_gross, as_of_date):
    """Return NEW rows to append (upsert semantics; pure — unit-tested).

    The loader keeps the latest row per (movie, day) by as_of_date/order, so
    appending is an upsert. Skip appending when the latest existing value is
    within UPSERT_TOLERANCE of the fetched one, so repeated finalizes do not
    grow the file with identical rows.
    """
    latest = {}
    for row in existing_rows:
        if (row.get("weekend_of") or "").strip() != weekend_of:
            continue
        key = ((row.get("movie_title") or "").strip().lower(),
               (row.get("day_of_week") or "").strip())
        try:
            latest[key] = float(row.get("gross_m") or 0)
        except (TypeError, ValueError):
            continue
    new_rows = []
    for day, gross in sorted(day_gross.items()):
        if not (MIN_GROSS_M <= gross <= MAX_GROSS_M):
            continue
        prev = latest.get((movie.strip().lower(), day))
        if prev and prev > 0 and abs(gross - prev) / prev <= UPSERT_TOLERANCE:
            continue
        new_rows.append({
            "weekend_of": weekend_of,
            "movie_title": movie,
            "day_of_week": day,
            "gross_m": round(gross, 3),
            "source": "The Numbers auto-fetch",
            "status": "reported",
            "as_of_date": as_of_date,
            "notes": "auto-fetched daily gross (revisions re-append)",
        })
    return new_rows


def main():
    import calibrate
    from predict import load_seat_data

    now_utc = datetime.now(timezone.utc)
    weekend_of = calibrate._last_friday()
    days = completed_days(weekend_of, now_utc)
    if not days:
        print(f"daily-actuals fetch: no completed days yet for weekend {weekend_of}")
        return 0

    seat = load_seat_data(weekend_of=weekend_of)
    movies = sorted(seat or {})
    if not movies:
        print(f"daily-actuals fetch: no tracked films with seat data for {weekend_of}")
        return 0

    existing = []
    if os.path.exists(OVERRIDES_CSV):
        with open(OVERRIDES_CSV, newline="") as f:
            existing = list(csv.DictReader(f))

    appended = []
    for movie in movies:
        try:
            fetched = calibrate.fetch_opening_weekend_daily(movie, weekend_of) or {}
        except Exception as e:
            print(f"  ⚠️  fetch failed for {movie}: {e}")
            continue
        day_gross = {d: g for d, g in fetched.items()
                     if d in days and d in SAFE_ANCHOR_DAYS}
        if not day_gross:
            print(f"  {movie}: no published days yet ({', '.join(days)} expected)")
            continue
        rows = merge_override_rows(existing, weekend_of, movie,
                                   day_gross, now_utc.strftime("%Y-%m-%d"))
        appended.extend(rows)
        kept = {r["day_of_week"]: r["gross_m"] for r in rows}
        print(f"  {movie}: fetched {day_gross} -> appending {kept or 'nothing (unchanged)'}")

    if not appended:
        print("daily-actuals fetch: nothing new to record")
        return 0

    file_exists = os.path.exists(OVERRIDES_CSV)
    with open(OVERRIDES_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(appended)
    print(f"daily-actuals fetch: appended {len(appended)} row(s) for weekend "
          f"{weekend_of} — same-week anchors will engage on the next prediction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
