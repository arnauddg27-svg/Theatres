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

Leak safety (audited 2026-08-31): calibrate.py's recording replay
(predict_pre_actual_movie) hard-injects daily_actual_overrides={}, so NO
override row — in-weekend or post-weekend — ever touches a recorded
predicted_mid. That is a blanket exclusion, deliberately stronger than an
as_of/through_date filter: the recorded error measures the raw model, not
the anchor-corrected number production served. Anchors improve LIVE
forecasts only. Rows still carry as_of_date for provenance and revision
upserts. Informational by design: the workflow step runs with
continue-on-error, so a fetch hiccup cannot brick finalize (the next
finalize retries).
"""
import csv
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
# Every opening day is recorded (2026-09-26: Thursday/Friday were left to a
# manual step that never ran, and the Heart of the Beast share error went
# uncorrected all weekend). Grosses come from The Numbers' daily table with
# Thursday previews SPLIT OUT of opening Friday (import_thenumbers_daily.
# opening_days); a Friday is only emitted once its Thursday row is known, so a
# folded Friday can never be recorded. WHEN the model uses each day is decided
# in predict.stage_gated_overrides (Thu/Fri wait for Friday seats), not here.
SAFE_ANCHOR_DAYS = ("Thursday", "Friday", "Saturday", "Sunday")


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


PREDICTION_LOG_CSV = os.path.join(os.path.dirname(OVERRIDES_CSV), "prediction-log.csv")


def logged_movies(weekend_of, path=PREDICTION_LOG_CSV):
    """Distinct films with a logged forecast for weekend_of, in log order."""
    if not os.path.exists(path):
        return []
    out = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            m = (r.get("movie") or "").strip()
            if r.get("weekend_of") == str(weekend_of) and m and m not in out:
                out.append(m)
    return out


CALENDAR_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "release-calendar.json",
)


def calendar_movies(weekend_of, path=CALENDAR_JSON):
    """Release-calendar titles for weekend_of. 2026-11-27 audit: with the AMC
    lane blocked, the Thanksgiving openers had no seat rows and no logged
    forecast, so their reported days were never fetched."""
    try:
        import json
        with open(path) as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    if str(data.get("weekend_of")) != str(weekend_of):
        return []
    out = []
    for t in data.get("titles") or []:
        title = (t.get("title") if isinstance(t, dict) else str(t or "")).strip()
        if title and title not in out:
            out.append(title)
    return out


def fetch_split_opening_days(movie, weekend_of, fetch_table=None, daily=None):
    """{day: gross_m} for the opening Thu-Sun, previews split out of Friday.
    Friday is dropped unless Thursday is known (otherwise it may still carry
    the previews) -- or unless Saturday is already published with still no
    Thursday row: by then the film simply had no previews (2026-11-03 audit:
    Everest: The Other Side / Christmas at the Kringles, no-preview openers,
    never got a Friday row)."""
    import import_thenumbers_daily as N
    if daily is None:
        fetch_table = fetch_table or (lambda t, y: N.fetch_daily_table(t, y, weekend_of=weekend_of))
        daily = fetch_table(movie, int(str(weekend_of)[:4])) or {}
    days = N.opening_days(daily, weekend_of) if daily else {}
    if "Friday" in days and "Thursday" not in days and "Saturday" not in days:
        days.pop("Friday")
    return {d: g for d, g in days.items() if MIN_GROSS_M <= g <= MAX_GROSS_M}


# PRE-FRIDAY OPENINGS (2026-11-27 audit). A film that opens on Wednesday has
# two full days on the books before the opening Friday, and this script only
# kept Thursday-Sunday, with nothing saying whether a Thursday row was
# previews or a regular day. Every day of the opening week of such a film
# (previews flagged) now also goes to data/midweek-opening-dailies.csv, which
# predict.py reads through midweek_opening.py. The file doubles as the comp
# set: a finished opening becomes history for the next one.
def midweek_rows_for(movie, weekend_of, daily, existing, as_of_date):
    """Rows to append for this film's opening week, [] for a Friday opener."""
    import midweek_opening as M
    rows = M.week_rows(daily, weekend_of)
    if not M.opens_before_friday(rows, weekend_of):
        return []
    return M.merge_rows(existing, weekend_of, movie, rows, as_of_date)


def upcoming_friday(now_utc):
    """The Friday of the weekend that has not started yet (Monday-Thursday),
    or None from Friday to Sunday, when last Friday is the live weekend."""
    days_ahead = (4 - now_utc.weekday()) % 7
    if days_ahead == 0 or now_utc.weekday() > 4:
        return None
    return (now_utc + timedelta(days=days_ahead)).strftime("%Y-%m-%d")


def early_openers(weekend_of):
    """Titles the release calendar or a market's stated dates put before Friday."""
    out = []
    try:
        import json
        with open(CALENDAR_JSON) as f:
            data = json.load(f)
        if str(data.get("weekend_of")) == str(weekend_of):
            for t in data.get("titles") or []:
                if not isinstance(t, dict):
                    continue
                try:
                    opens = datetime.strptime(t.get("date") or "", "%B %d, %Y").strftime("%Y-%m-%d")
                except ValueError:
                    continue
                if opens < str(weekend_of) and (t.get("title") or "").strip():
                    out.append(t["title"].strip())
    except (OSError, ValueError):
        pass
    try:
        from forecast_windows import market_frame
        from predict import load_polymarket_data
        for movie, markets in (load_polymarket_data(weekend_of=weekend_of) or {}).items():
            frame = market_frame(movie, weekend_of, markets)
            if frame and frame[0] < str(weekend_of):
                out.append(movie)
    except Exception as e:
        print(f"  (markets not read for early openers: {type(e).__name__})")
    seen, unique = set(), []
    for title in out:
        key = "".join(ch for ch in title.lower() if ch.isalnum())
        if key not in seen:
            seen.add(key)
            unique.append(title)
    return unique


def fetch_upcoming_midweek(now_utc, fetch_table=None):
    """Wednesday/Thursday of a pre-Friday opening are published before the
    weekend this script tracks has begun: fetch them as they appear."""
    import import_thenumbers_daily as N
    import midweek_opening as M
    weekend_of = upcoming_friday(now_utc)
    if not weekend_of:
        return 0
    existing = M.read_csv()
    appended = []
    for movie in early_openers(weekend_of):
        try:
            daily = (fetch_table or (lambda t, y: N.fetch_daily_table(t, y, weekend_of=weekend_of)))(
                movie, int(weekend_of[:4])) or {}
        except Exception as e:
            print(f"  ⚠️  fetch failed for {movie}: {e}")
            continue
        rows = midweek_rows_for(movie, weekend_of, daily, existing + appended,
                                now_utc.strftime("%Y-%m-%d"))
        appended.extend(rows)
        if rows:
            print(f"  {movie}: opening week {[(r['show_date'], r['day_kind'], r['gross_m']) for r in rows]}")
    M.append_csv(appended)
    if appended:
        print(f"daily-actuals fetch: {len(appended)} opening-week row(s) for the weekend of {weekend_of}")
    return len(appended)


def main():
    import calibrate
    import midweek_opening as M
    from predict import load_seat_data

    now_utc = datetime.now(timezone.utc)
    try:
        fetch_upcoming_midweek(now_utc)
    except Exception as e:      # informational, like the rest of this script
        print(f"  (upcoming pre-Friday openings not fetched: {type(e).__name__}: {e})")
    weekend_of = calibrate._last_friday()
    days = completed_days(weekend_of, now_utc)
    if not days:
        print(f"daily-actuals fetch: no completed days yet for weekend {weekend_of}")
        return 0

    seat = load_seat_data(weekend_of=weekend_of)
    movies = sorted(seat or {})
    # 2nd/3rd-weekend films with a market: holdover_forecast.py anchors on
    # their reported days the same way (2026-10-31).
    import holdover
    have = {holdover.title_key(m) for m in movies}
    movies += [r["movie"] for r in holdover.entries(weekend_of)
               if holdover.title_key(r["movie"]) not in have]
    # Films forecast from presales/comps without seat rows (2026-11-03 audit:
    # Fjord, Christmas at the Kringles, The Only Living Pickpocket were in the
    # prediction log but never got actuals).
    have = {holdover.title_key(m) for m in movies}
    movies += [m for m in logged_movies(weekend_of) if holdover.title_key(m) not in have]
    have = {holdover.title_key(m) for m in movies}
    movies += [m for m in calendar_movies(weekend_of) if holdover.title_key(m) not in have]
    if not movies:
        print(f"daily-actuals fetch: no tracked films with seat data for {weekend_of}")
        return 0

    existing = []
    if os.path.exists(OVERRIDES_CSV):
        with open(OVERRIDES_CSV, newline="") as f:
            existing = list(csv.DictReader(f))

    import import_thenumbers_daily as N
    midweek_existing = M.read_csv()
    midweek_appended = []
    appended = []
    for movie in movies:
        try:
            daily = N.fetch_daily_table(movie, int(str(weekend_of)[:4]), weekend_of=weekend_of) or {}
            fetched = fetch_split_opening_days(movie, weekend_of, daily=daily)
        except Exception as e:
            print(f"  ⚠️  fetch failed for {movie}: {e}")
            continue
        midweek_appended.extend(midweek_rows_for(
            movie, weekend_of, daily, midweek_existing + midweek_appended,
            now_utc.strftime("%Y-%m-%d")))
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

    if M.append_csv(midweek_appended):
        print(f"daily-actuals fetch: {len(midweek_appended)} opening-week row(s) for films that "
              f"opened before Friday {weekend_of}")
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
