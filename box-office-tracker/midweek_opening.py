"""Films that open before Friday: reported full days are actuals, not previews.

2026-11-27 audit (Thanksgiving; Focker In-Law, Hexed and Hershey opened on
Wednesday 11-25). The model staged them "after-previews" and ran the reported
Thursday -- a full holiday day, the film's second -- through the previews
multiplier and the one-day seat regression: Thursday-Sunday came out 7.5-8.9x
Thursday, where the ten Thanksgiving-Wednesday openers of 2021-2025 ran
5.3-6.2x. Wednesday itself was dropped (only Thursday-Sunday rows were kept),
so nothing could be compared with the 5-day market.

This module holds the day-by-day record of such openings
(data/midweek-opening-dailies.csv, The Numbers' daily table, written by
scripts/fetch_daily_actuals.py every finalize) and projects the days still to
come from the days already reported:

    remaining = sqrt( r_last x last reported day  *  r_cum x gross to date )

with r_last / r_cum the median ratios of earlier films that opened the same
number of days before Friday in the same holiday frame. The two readings err
in opposite directions (a film that jumps on the holiday over-reads on the
last day and under-reads on the running total); leave-one-out on the ten
Thanksgiving openers, with Wednesday and Thursday reported, Friday-Sunday is
missed by 6.9% (last day), 7.8% (to date) and 2.4% (both). See
scripts/midweek_opening_backtest.py.

Everything here is pure; amounts are $ millions.
"""
import csv
import math
import os
import re
import statistics
from datetime import date, datetime, timedelta

DATA_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "midweek-opening-dailies.csv")
FIELDS = ["weekend_of", "movie_title", "show_date", "day_kind", "gross_m", "source", "as_of_date"]
PREVIEW, REGULAR = "preview", "regular"
MIN_COMPS = 3            # same-frame comps needed before pooling every frame
LEAD_IN_RATIO = 4.0      # a day at least this many times smaller than the next is a platform/early-access day
BAND_MARGIN = 0.05       # widen the leave-one-out min/max by this much each side
MIN_HALF_BAND = 0.05
POOLED_HALF_BAND = 0.25  # floor when the comps come from other holiday frames
DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def movie_key(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def _date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def thanksgiving(year):
    first = date(year, 11, 1)
    return first + timedelta(days=(3 - first.weekday()) % 7 + 21)


def holiday_frame(weekend_of, opening_date):
    """thanksgiving | july4 | christmas | none for an opening run ending Sunday."""
    friday, opening = _date(weekend_of), _date(opening_date)
    if not friday or not opening:
        return "none"
    if thanksgiving(friday.year) == friday - timedelta(days=1):
        return "thanksgiving"
    sunday = friday + timedelta(days=2)
    for year in (friday.year - 1, friday.year):
        for month, day, name in ((7, 4, "july4"), (12, 25, "christmas")):
            if opening - timedelta(days=1) <= date(year, month, day) <= sunday:
                return name
    return "none"


def load_rows(path=None, through_date=None):
    """{(weekend_of, movie_key): {"movie": title, "days": {date: (kind, gross_m)}}}.

    Append-only file, last row per (film, show date) wins (revisions re-append).
    With through_date (a replay), a row counts when it was recorded by then, or
    when its weekend had already ended -- a finished opening is history."""
    path = path or DATA_CSV
    out = {}
    if not os.path.exists(path):
        return out
    cutoff = _date(through_date)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            friday, day = _date(row.get("weekend_of")), _date(row.get("show_date"))
            kind = (row.get("day_kind") or "").strip().lower()
            try:
                gross = float(row.get("gross_m") or "")
            except ValueError:
                continue
            title = (row.get("movie_title") or "").strip()
            if not friday or not day or kind not in (PREVIEW, REGULAR) or gross <= 0 or not title:
                continue
            if cutoff:
                recorded = _date(row.get("as_of_date"))
                if not ((recorded and recorded <= cutoff) or friday + timedelta(days=2) < cutoff):
                    continue
            film = out.setdefault((friday.isoformat(), movie_key(title)), {"movie": title, "days": {}})
            film["days"][day] = (kind, gross)
    return out


def film_days(data, movie, weekend_of):
    return ((data or {}).get((str(weekend_of), movie_key(movie))) or {}).get("days") or {}


def opening_run(days, weekend_of, known_opening=None):
    """Describe a pre-Friday opening from its reported regular days, or None.

    days: {date: (kind, gross_m)}. known_opening: the opening date a market's
    rules or the release calendar state. When it precedes the first reported
    row (Hershey 2026-11-25: the table starts on Thursday with a running total
    equal to that row), the first row is a gross-to-date, not a single day:
    `last_is_single_day` is False until a later day is reported."""
    friday = _date(weekend_of)
    if not friday or not days:
        return None
    sunday = friday + timedelta(days=2)
    regular = sorted(d for d, (kind, gross) in days.items()
                     if kind == REGULAR and friday - timedelta(days=6) <= d <= sunday)
    # Platform / early-access days before the wide opening (Marty Supreme ran
    # six days in a handful of theatres before 2025-12-25): start after the
    # last day-over-day jump of LEAD_IN_RATIO or more.
    jumps = [i for i in range(len(regular) - 1)
             if days[regular[i + 1]][1] >= LEAD_IN_RATIO * days[regular[i]][1]]
    if jumps:
        regular = regular[jumps[-1] + 1:]
    if not regular:
        return None
    first = regular[0]
    opening = first
    known = _date(known_opening)
    if known and friday - timedelta(days=6) <= known < first:
        opening = known
    if opening >= friday:
        return None                         # a Friday opener: Thursday, if any, is previews
    run = [first]
    for d in regular[1:]:
        if d != run[-1] + timedelta(days=1):
            break                           # a hole in the table: stop at the last contiguous day
        run.append(d)
    gross = [days[d][1] for d in run]
    last = run[-1]
    return {
        "opening_date": opening.isoformat(),
        "offset": (friday - opening).days,                 # days before Friday
        "frame": holiday_frame(friday, opening),
        "reported_dates": [d.isoformat() for d in run],
        "reported_m": {d.isoformat(): g for d, g in zip(run, gross)},
        "position": (last - opening).days + 1,             # days of the run reported, counted from opening
        "to_date_m": sum(gross),
        "last_m": gross[-1],
        "last_is_single_day": not (opening < first and len(run) == 1),
        "remaining_dates": [(last + timedelta(days=i)).isoformat()
                            for i in range(1, (sunday - last).days + 1)],
    }


def complete_runs(data, before_weekend=None, exclude=None):
    """[{movie, weekend_of, offset, frame, gross: [opening..Sunday]}] for
    finished openings before `before_weekend`, never the film in `exclude`."""
    out = []
    for (weekend, key), film in sorted((data or {}).items()):
        if before_weekend and weekend >= str(before_weekend):
            continue
        if exclude and (weekend, key) == (str(exclude[0]), movie_key(exclude[1])):
            continue
        run = opening_run(film["days"], weekend)
        if not run or run["remaining_dates"] or run["position"] != len(run["reported_dates"]):
            continue
        out.append({"movie": film["movie"], "weekend_of": weekend, "offset": run["offset"],
                    "frame": run["frame"], "gross": [run["reported_m"][d] for d in run["reported_dates"]]})
    return out


def _estimate(gross_to_position, comps, position, single_day=True):
    """(remaining_m, r_last, r_cum) from comps' median ratios at `position`."""
    last, to_date = gross_to_position
    r_cum = statistics.median(sum(c["gross"][position:]) / sum(c["gross"][:position]) for c in comps)
    by_cum = r_cum * to_date
    if position == 1 or not single_day:
        return by_cum, None, r_cum
    r_last = statistics.median(sum(c["gross"][position:]) / c["gross"][position - 1] for c in comps)
    return math.sqrt(r_last * last * by_cum), r_last, r_cum


def project(run, comps_all):
    """Project the days still to come. Returns None without enough comps.

    {remaining_m, low_m, high_m, per_day_m {date: m}, n_comps, pool,
     r_last, r_cum, loo_mae, estimator}"""
    if not run or not run["remaining_dates"]:
        return None
    position, offset = run["position"], run["offset"]
    same_offset = [c for c in comps_all if c["offset"] == offset and len(c["gross"]) == offset + 3]
    comps = [c for c in same_offset if c["frame"] == run["frame"]]
    pool = run["frame"]
    if len(comps) < MIN_COMPS:
        comps, pool = same_offset, "all frames"
    if len(comps) < MIN_COMPS:
        return None
    single = run["last_is_single_day"]
    remaining, r_last, r_cum = _estimate((run["last_m"], run["to_date_m"]), comps, position, single)
    # Leave-one-out on the comps themselves gives the band.
    ratios = []
    for c in comps:
        others = [o for o in comps if o is not c]
        if len(others) < 2:
            continue
        guess, _, _ = _estimate((c["gross"][position - 1], sum(c["gross"][:position])), others, position, single)
        ratios.append(sum(c["gross"][position:]) / guess)
    floor = MIN_HALF_BAND if pool != "all frames" else POOLED_HALF_BAND
    lo = min(ratios + [1.0]) * (1.0 - BAND_MARGIN)
    hi = max(ratios + [1.0]) * (1.0 + BAND_MARGIN)
    lo, hi = min(lo, 1.0 - floor), max(hi, 1.0 + floor)
    by_last = r_last * run["last_m"] if r_last else None
    by_cum = r_cum * run["to_date_m"]
    if by_last:
        # The two readings rarely disagree on the comps; when they do (Focker
        # In-Law rose 45% on Thanksgiving Day, every comp fell) the film is
        # outside their shape: reach halfway to each reading.
        lo = min(lo, (remaining + min(by_last, by_cum)) / 2.0 / remaining)
        hi = max(hi, (remaining + max(by_last, by_cum)) / 2.0 / remaining)
    n_left = len(run["remaining_dates"])
    shares = [statistics.median(c["gross"][position + i] / sum(c["gross"][position:]) for c in comps)
              for i in range(n_left)]
    total_share = sum(shares) or 1.0
    return {
        "remaining_m": remaining, "low_m": remaining * lo, "high_m": remaining * hi,
        "per_day_m": {d: remaining * s / total_share for d, s in zip(run["remaining_dates"], shares)},
        "n_comps": len(comps), "pool": pool, "r_last": r_last, "r_cum": r_cum,
        "by_last_m": by_last, "by_cum_m": by_cum,
        "loo_mae": (statistics.mean(abs(1.0 / r - 1.0) for r in ratios) if ratios else None),
        "estimator": "last day x to date" if r_last else "to date",
    }


def frame_total(run, projection, start, end):
    """(mid, low, high) for the dates start..end from reported + projected days,
    or None when the frame holds a date that is neither (e.g. a Monday)."""
    start, end = _date(start), _date(end)
    if not run or not start or not end or end < start:
        return None
    opening = _date(run["opening_date"])
    per_day = (projection or {}).get("per_day_m") or {}
    reported = projected = 0.0
    day = start
    while day <= end:
        key = day.isoformat()
        if key in run["reported_m"]:
            reported += run["reported_m"][key]
        elif key in per_day:
            projected += per_day[key]
        elif day >= opening and not (run["reported_dates"] and key < run["reported_dates"][0]):
            return None                     # an in-run day we can neither read nor project
        day += timedelta(days=1)
    if projected <= 0:
        return (reported, reported, reported) if reported > 0 else None
    scale_lo = projection["low_m"] / projection["remaining_m"]
    scale_hi = projection["high_m"] / projection["remaining_m"]
    return reported + projected, reported + projected * scale_lo, reported + projected * scale_hi


def stage_name(run):
    """midweek-after-<last reported weekday>, e.g. midweek-after-thursday."""
    last = _date(run["reported_dates"][-1])
    return "midweek-after-" + DAY_NAMES[last.weekday()].lower()


def window_label(start, end):
    start, end = _date(start), _date(end)
    return f"{DAY_NAMES[start.weekday()]}-{DAY_NAMES[end.weekday()]} ({(end - start).days + 1} days)"


# -- recording (scripts/fetch_daily_actuals.py, scripts/import_midweek_openers.py) --

UPSERT_TOLERANCE = 0.02      # re-append a day only when its gross moved by more than this


def week_rows(daily, weekend_of):
    """[(date, kind, gross_m)] Monday..Sunday of the opening week from a The
    Numbers daily table {date: (rank, gross_m)}; rank "P" marks previews."""
    friday = _date(weekend_of)
    if not friday or not daily:
        return []
    out = []
    for day in sorted(daily):
        if friday - timedelta(days=6) <= day <= friday + timedelta(days=2):
            rank, gross = daily[day]
            if gross and gross > 0:
                out.append((day, PREVIEW if str(rank).strip().upper() == "P" else REGULAR, float(gross)))
    return out


def opens_before_friday(rows, weekend_of):
    """True when the week holds a regular (non-preview) day before Friday."""
    friday = _date(weekend_of)
    return bool(friday) and any(kind == REGULAR and day < friday for day, kind, _ in rows)


def merge_rows(existing, weekend_of, movie, rows, as_of_date, source="The Numbers daily table"):
    """New CSV rows to append (pure): a day is written when it is new, changed
    kind, or moved by more than UPSERT_TOLERANCE."""
    latest = {}
    for row in existing or []:
        if row.get("weekend_of") == str(weekend_of) and movie_key(row.get("movie_title")) == movie_key(movie):
            latest[row.get("show_date")] = row
    out = []
    for day, kind, gross in rows:
        old = latest.get(day.isoformat())
        if old:
            try:
                same = (old.get("day_kind") == kind
                        and abs(float(old.get("gross_m") or 0) - gross) <= UPSERT_TOLERANCE * gross)
            except ValueError:
                same = False
            if same:
                continue
        out.append({"weekend_of": str(weekend_of), "movie_title": movie, "show_date": day.isoformat(),
                    "day_kind": kind, "gross_m": round(gross, 4), "source": source,
                    "as_of_date": as_of_date})
    return out


def read_csv(path=None):
    path = path or DATA_CSV
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def append_csv(rows, path=None):
    path = path or DATA_CSV
    if not rows:
        return 0
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        writer.writerows(rows)
    return len(rows)
