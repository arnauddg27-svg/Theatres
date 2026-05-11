#!/usr/bin/env python3
"""
Opening Weekend Box Office Predictor
=====================================
Predicts North American opening-weekend gross from AMC seat occupancy data.
Polymarket odds are parsed for market context only, not forecast math.

Pipeline:
  A. Per-theatre daily revenue (occupancy × seats × showings × price)
  B. Sum all AMC theatres
  C. AMC → total domestic (÷ market share)
  D. Partial days → full weekend (day weights)
  E. Polymarket expected value (bracket parsing)
  F. Model prediction (seat + historical comps)
  G. Polymarket market context, excluded from model calculations

Usage:
    python3 predict.py                              # All movies this weekend
    python3 predict.py --movie "Project Hail Mary"  # Single movie
    python3 predict.py --actual "Movie Name" 125.3  # Record actual result
    python3 predict.py --history                    # Past predictions vs actuals
    python3 predict.py --verbose                    # Full calculation breakdown
"""

import json, csv, os, sys, re, statistics
from datetime import datetime, timedelta, timezone
from math import exp, log, sqrt
from calibration_freeze import (calibration_has_weekend,
                                load_calibration_freeze,
                                save_calibration_freeze)
from historical_comps import (estimate_from_prediction,
                              load_historical_comps,
                              load_movie_metadata,
                              metadata_for_movie)
from model_calibration import (MIN_DAILY_CALIBRATION_COVERAGE,
                               sanitize_calibration, recalibrate_scale_factor,
                               recalibrate_snapshot_day_scale_factors)

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR            = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SEAT_CSV            = os.path.join(DATA_DIR, "seat-counts.csv")
PRE_RESERVATION_CSV = os.path.join(DATA_DIR, "pre-reservation-snapshots.csv")
POLY_CSV            = os.path.join(DATA_DIR, "polymarket-markets.csv")
CALIBRATION_JSON    = os.path.join(DATA_DIR, "calibration.json")
THEATRE_COUNTS_JSON = os.path.join(DATA_DIR, "theatre-counts.json")
THEATRES_JSON       = os.path.join(DATA_DIR, "theatres-all.json")
THEATRES_EXPANSION_JSON = os.path.join(DATA_DIR, "theatres-expansion.json")

# ── Default Constants ────────────────────────────────────────────────────────
DEFAULT_AMC_MARKET_SHARE = 0.25
CORE_COHORT = "core"
EXPANSION_COHORT = "expansion"
DEFAULT_MODEL_COHORTS = (CORE_COHORT, EXPANSION_COHORT)
KNOWN_THEATRE_COHORTS = {CORE_COHORT, EXPANSION_COHORT}
MODEL_TIMEZONE_GROUPS = ("ET", "CT", "PT")
URL_SHOWTIME_IDENTITY_VALUES = {"url", "seat-map", "seat_map", "amc_url", "amc-url"}
LOCAL_THURSDAY_SHARE_PRIOR_SAMPLES = 8.0
MAX_LOCAL_THURSDAY_SHARE_WEIGHT = 0.50
MODEL_VERSION = "seat-regression-v5"
SNAPSHOT_LAYER_MAX_WEIGHT = 0.45
RESIDUAL_REGRESSION_MIN_OBS = 2
RESIDUAL_REGRESSION_PRIOR_WEIGHT = 6.0
RESIDUAL_REGRESSION_MAX_STRENGTH = 0.35
RESIDUAL_REGRESSION_RATIO_MIN = 0.60
RESIDUAL_REGRESSION_RATIO_MAX = 1.60
RESIDUAL_REGRESSION_FACTOR_MIN = 0.85
RESIDUAL_REGRESSION_FACTOR_MAX = 1.15
SNAPSHOT_MAX_SLICE_AGE_HOURS = 8
SNAPSHOT_SAME_WEEK_SCALE_MIN = 0.50
SNAPSHOT_SAME_WEEK_SCALE_MAX = 3.00
SNAPSHOT_MAX_LEAD_MINUTES = 96 * 60
SNAPSHOT_DAY_SHAPE_MAX_SIGNAL_WEIGHT = 0.50

# Samples more than six hours before showtime are outside the intended
# collection window and usually indicate stale link/date metadata.
MAX_REASONABLE_PRE_SHOW_MINUTES = 360

# Per-format AMC evening ticket prices (2026 dollars). Premium formats charge a
# real surcharge — averaging them away with one DEFAULT_TICKET_PRICE × discount
# throws away signal we already have in `auditorium_type`. These are realized
# evening prices (not advertised), already net of typical loyalty discounts,
# which is why they're a touch below AMC's headline rates.
FORMAT_TICKET_PRICES = {
    8: 19.00, 7: 19.00,   # IMAX with Laser
    6: 18.00,             # IMAX / IMAX 3D
    5: 17.00,             # Dolby Cinema
    4: 15.00, 3: 14.00,   # Prime / XL
    2: 14.00,             # Laser
    1: 13.00, 0: 13.00,   # Standard / Digital
}

# Partial-day sample → full-day revenue multipliers, *per day of week*.
# Friday still collects 5pm–11pm, so 1.7× extrapolates captured late-day
# showings to a full day. Saturday/Sunday are intended to collect 10am–11pm;
# when those rows are present, daypart_adjusted_evening_to_daily() removes the
# uplift and treats the sample as full-day coverage.
#
# Thursday is structurally different: a wide release that opens Friday has NO
# Thursday daytime showings — only evening preview screenings. What we capture
# IS the full Thursday business, so the multiplier is 1.0. Using 1.7× on
# Thursday inflates our preview-night estimate by ~70%, which is what was
# producing Thursday over-predictions on calibration runs.
#
# Industry convention complicates this: trades often roll Thursday previews
# into "Friday opening" totals. The Numbers' per-movie page (which calibrate.py
# uses) keeps them separate via the rank-"P" preview row. Make sure both sides
# of the comparison use the same convention.
DEFAULT_EVENING_TO_DAILY = 1.70   # Fri/Sat/Sun fallback
DAY_EVENING_TO_DAILY_DEFAULT = {
    "Thursday":  1.00,   # preview-only, no matinee
    "Friday":    1.70,
    "Saturday":  1.70,
    "Sunday":    1.70,
}
FAMILY_DAYPART_REFERENCE_SHOWINGS = 4.5
FAMILY_DAYPART_MIN_SHOWINGS = 1.5
FAMILY_DAYPART_MAX_EVENING_TO_DAILY = 3.8
WEEKEND_FULL_DAY_START_HOUR = 10.0
WEEKEND_FULL_DAY_LATEST_EARLY_HOUR = WEEKEND_FULL_DAY_START_HOUR + 4.0
WEEKEND_FULL_DAY_MIN_THEATRE_COVERAGE = 0.60
FULL_DAY_SHOWTIME_WINDOW_NOTE = "showtime_window=sat-sun-10-23-v1"

# Opening weekend = Thu-Sun. Weights MUST sum to 1.0 across these four days
# only — adding Mon-Wed entries here would silently shrink Thu-Sun weights when
# `normalize_day_weights` re-normalizes, causing `days_to_weekend` to overshoot
# by 1/(Thu+Fri+Sat+Sun). The model only predicts opening weekend, so Mon-Wed
# don't belong in this distribution. Defaults match calibrate.py's DEFAULT_CALIBRATION
# so a fresh install agrees with a freshly calibrated install.
DAY_WEIGHTS_DEFAULT = {
    "Thursday":  0.12,
    "Friday":    0.32,
    "Saturday":  0.33,
    "Sunday":    0.23,
}


def get_evening_to_daily_multiplier(cal, day_name=None):
    """Read the per-day evening→daily multiplier from calibration.

    Falls through, in order:
      1. calibration_factors.day_evening_to_daily[day_name]
      2. calibration_factors.evening_to_daily_multiplier (legacy global)
      3. DAY_EVENING_TO_DAILY_DEFAULT[day_name]
      4. DEFAULT_EVENING_TO_DAILY (1.70)
    """
    factors = (cal or {}).get("calibration_factors", {}) if cal else {}
    if day_name:
        per_day = factors.get("day_evening_to_daily") if cal else None
        if isinstance(per_day, dict) and day_name in per_day:
            try:
                return float(per_day[day_name])
            except (TypeError, ValueError):
                pass
    legacy_global = factors.get("evening_to_daily_multiplier") if cal else None
    if legacy_global is not None:
        try:
            return float(legacy_global)
        except (TypeError, ValueError):
            pass
    if day_name and day_name in DAY_EVENING_TO_DAILY_DEFAULT:
        return DAY_EVENING_TO_DAILY_DEFAULT[day_name]
    return DEFAULT_EVENING_TO_DAILY


def _parse_showtime_hour(time_str):
    """Parse a showtime like '7:30pm' into local decimal hour."""
    if not time_str:
        return None
    match = re.search(r"(\d{1,2}):(\d{2})\s*(AM|PM)", str(time_str).strip(), re.I)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    ampm = match.group(3).upper()
    if ampm == "PM" and hour != 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    return hour + minute / 60


def _row_has_full_day_showtime_window(row):
    return FULL_DAY_SHOWTIME_WINDOW_NOTE in str((row or {}).get("notes", ""))


def daypart_adjusted_evening_to_daily(base_multiplier, day_name, avg_showings,
                                      target_metadata=None,
                                      earliest_showtime_hour=None,
                                      full_day_window_coverage_ratio=None):
    """Adjust partial-day scaling when showtime mix misses matinee demand.

    Saturday/Sunday are meant to collect 10am-11pm. When actual theatre-level
    daytime rows prove that the full-day window landed, no evening-to-day uplift
    should be applied. The showtime-window marker only describes the intended
    link window; it is not enough by itself because AMC can drop earlier seat
    maps before the post-show scrape runs.
    """
    if day_name not in {"Friday", "Saturday", "Sunday"}:
        return base_multiplier
    try:
        full_day_coverage = float(full_day_window_coverage_ratio)
    except (TypeError, ValueError):
        full_day_coverage = 0.0
    if (
        day_name in {"Saturday", "Sunday"}
        and full_day_coverage >= WEEKEND_FULL_DAY_MIN_THEATRE_COVERAGE
    ):
        return 1.0
    if target_metadata is None:
        return base_multiplier

    audience_type = (getattr(target_metadata, "audience_type", "") or "").lower()
    rating = (getattr(target_metadata, "rating", "") or "").upper()
    is_family_title = "family" in audience_type or rating in {"G", "PG"}
    if not is_family_title:
        return base_multiplier

    try:
        base = float(base_multiplier)
        show_count = float(avg_showings)
    except (TypeError, ValueError):
        return base_multiplier

    if show_count <= 0 or base <= 0:
        return base_multiplier

    effective_show_count = max(FAMILY_DAYPART_MIN_SHOWINGS, show_count)
    daypart_factor = max(1.0, FAMILY_DAYPART_REFERENCE_SHOWINGS / effective_show_count)
    adjusted = base * daypart_factor
    return min(FAMILY_DAYPART_MAX_EVENING_TO_DAILY, max(base, adjusted))


def get_day_scale(cal, day_name):
    """Per-day calibration scale factor (default 1.0).

    Calibration trains one scale per day from EMA over historical
    actual/predicted ratios for that day. The total weekend prediction is the
    sum of (raw_daily × day_scale[day]) — no global scale factor applied on
    top, so calibration adds up to a total day-by-day instead of inflating a
    single number.
    """
    factors = (cal or {}).get("calibration_factors", {}) if cal else {}
    per_day = factors.get("day_scale_factors") if cal else None
    if isinstance(per_day, dict) and day_name in per_day:
        try:
            return float(per_day[day_name])
        except (TypeError, ValueError):
            pass
    # Fall back to legacy overall_scale_factor only when no per-day calibration
    # exists — keeps a fresh install or an old calibration.json working.
    legacy = factors.get("overall_scale_factor", 1.0) if cal else 1.0
    try:
        return float(legacy)
    except (TypeError, ValueError):
        return 1.0


def get_snapshot_to_day_scale(cal, day_name):
    """Calibrated scale for pre-reservation snapshot → final day gross."""
    factors = (cal or {}).get("calibration_factors", {}) if cal else {}
    per_day = factors.get("snapshot_to_day_scale_factors") if cal else None
    if isinstance(per_day, dict) and day_name in per_day:
        try:
            return float(per_day[day_name])
        except (TypeError, ValueError):
            pass
    return 1.0


def get_day_weights(cal):
    """Get day weights from calibration, falling back to defaults.

    Calibrate.py updates these weights every Tuesday from actual daily
    box office splits. Over time they converge on the true distribution.
    """
    if cal:
        return cal.get("calibration_factors", {}).get("day_weights", DAY_WEIGHTS_DEFAULT)
    return DAY_WEIGHTS_DEFAULT

DAY_CONFIDENCE = {
    1: (0.70, 1.40),   # 1 day collected
    2: (0.85, 1.20),   # 2 days
    3: (0.92, 1.10),   # 3 days
    4: (0.96, 1.05),   # 4 days (full opening weekend)
    5: (0.97, 1.04),   # 5 days
    6: (0.98, 1.03),   # 6 days
    7: (0.99, 1.02),   # full week
}
OPENING_WEEKEND_DAYS = ("Thursday", "Friday", "Saturday", "Sunday")

DEFAULT_TICKET_PRICE = 14.50
PRICE_DISCOUNT_FACTOR = 0.85   # avg effective price vs adult price
DEFAULT_SEATS_PER_SHOW = 200   # when no seat map available


# ── Data Loading ─────────────────────────────────────────────────────────────

def _current_weekend_friday():
    """Return the Friday that anchors the current opening weekend (Thu-Mon).

    Delegates to scraper.opening_weekend_friday() so both files always agree.
    Falls back to inline logic if scraper is unavailable (e.g. import cycle).
    """
    try:
        from scraper import opening_weekend_friday
        return opening_weekend_friday()
    except ImportError:
        pass
    now = datetime.now()
    wd = now.weekday()  # Mon=0 ... Sun=6
    if wd == 3:
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    if wd == 4:
        return now.strftime("%Y-%m-%d")
    if wd == 5:
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    if wd == 6:
        return (now - timedelta(days=2)).strftime("%Y-%m-%d")
    if wd == 0:
        return (now - timedelta(days=3)).strftime("%Y-%m-%d")
    if wd == 1:
        return (now - timedelta(days=4)).strftime("%Y-%m-%d")
    return (now - timedelta(days=5)).strftime("%Y-%m-%d")


def _opening_weekend_for_date(date_str):
    """Map a YYYY-MM-DD row date to its opening-weekend Friday anchor."""
    try:
        row_dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return ""

    try:
        from scraper import opening_weekend_friday
        return opening_weekend_friday(row_dt)
    except ImportError:
        wd = row_dt.weekday()
        if wd == 3:
            return (row_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        if wd == 4:
            return row_dt.strftime("%Y-%m-%d")
        if wd == 5:
            return (row_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        if wd == 6:
            return (row_dt - timedelta(days=2)).strftime("%Y-%m-%d")
        if wd == 0:
            return (row_dt - timedelta(days=3)).strftime("%Y-%m-%d")
        if wd == 1:
            return (row_dt - timedelta(days=4)).strftime("%Y-%m-%d")
        return (row_dt - timedelta(days=5)).strftime("%Y-%m-%d")


def _parse_cohorts(raw, default=DEFAULT_MODEL_COHORTS):
    value = raw if raw is not None else ",".join(default)
    cohorts = [part.strip().lower() for part in value.split(",") if part.strip()]
    if not cohorts:
        return set(default)
    if "all" in cohorts or "*" in cohorts:
        return set(KNOWN_THEATRE_COHORTS)
    selected = set(cohorts) & KNOWN_THEATRE_COHORTS
    return selected or set(default)


def active_model_cohorts():
    """Theatre cohorts allowed to feed prediction/calibration."""
    return _parse_cohorts(os.getenv("THEATRE_MODEL_COHORTS"), DEFAULT_MODEL_COHORTS)


def normalize_model_cohort_key(cohorts):
    """Stable identity for the theatre cohort set behind a prediction."""
    if cohorts is None:
        return ""
    if isinstance(cohorts, str):
        raw = cohorts.split(",")
    else:
        raw = cohorts
    normalized = []
    for cohort in raw:
        value = str(cohort).strip().lower()
        if value:
            normalized.append(value)
    return ",".join(sorted(set(normalized)))


def active_model_cohort_key():
    return normalize_model_cohort_key(active_model_cohorts())


def use_url_showtime_identity():
    """Opt in to URL-level screen identity without changing the default model."""
    return os.getenv("THEATRE_MODEL_SHOWTIME_IDENTITY", "").strip().lower() in URL_SHOWTIME_IDENTITY_VALUES


def _add_theatre_cohorts(cohort_sets, path, default_cohort):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except Exception:
        return
    for group, theatres in data.items():
        if group.startswith("_"):
            continue
        for theatre in theatres:
            name = (theatre.get("name") or "").strip()
            if not name:
                continue
            cohort = (theatre.get("cohort") or default_cohort).strip().lower()
            cohort_sets.setdefault(cohort, set()).add(name)


def _theatre_cohort(theatre, default_cohort):
    return (theatre.get("cohort") or default_cohort).strip().lower()


def _add_theatre_timezone_reference(name_to_tz, tz_counts, path, default_cohort,
                                    allowed_cohorts):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except Exception:
        return
    for group, theatres in data.items():
        if group not in MODEL_TIMEZONE_GROUPS:
            continue
        for theatre in theatres:
            name = (theatre.get("name") or "").strip()
            if not name:
                continue
            cohort = _theatre_cohort(theatre, default_cohort)
            if cohort not in allowed_cohorts:
                continue
            # Core wins over expansion when the same AMC appears twice.
            if name in name_to_tz:
                continue
            name_to_tz[name] = group
            tz_counts[group] = tz_counts.get(group, 0) + 1


def load_theatre_cohort_sets():
    """Return {cohort: theatre_names} from core + expansion config files."""
    cohort_sets = {CORE_COHORT: set(), EXPANSION_COHORT: set()}
    _add_theatre_cohorts(cohort_sets, THEATRES_JSON, CORE_COHORT)
    _add_theatre_cohorts(cohort_sets, THEATRES_EXPANSION_JSON, EXPANSION_COHORT)
    cohort_sets[EXPANSION_COHORT] -= cohort_sets[CORE_COHORT]
    return cohort_sets


def load_theatre_timezone_reference(model_cohorts=None):
    """Return ({theatre_name: tz_group}, {tz_group: configured_count}).

    MT is intentionally omitted because the production workflow currently
    schedules ET/CT/PT only. The output is used for model confidence and sample
    normalization, not for scraping.
    """
    allowed = model_cohorts if model_cohorts is not None else active_model_cohorts()
    name_to_tz = {}
    tz_counts = {}
    _add_theatre_timezone_reference(
        name_to_tz,
        tz_counts,
        THEATRES_JSON,
        CORE_COHORT,
        allowed,
    )
    _add_theatre_timezone_reference(
        name_to_tz,
        tz_counts,
        THEATRES_EXPANSION_JSON,
        EXPANSION_COHORT,
        allowed,
    )
    return name_to_tz, tz_counts


def model_allows_theatre(theatre_name, cohort_sets=None, model_cohorts=None):
    """True when a row's theatre belongs to an enabled model cohort.

    Unknown theatres are allowed so old/manual rows do not disappear just
    because the theatre config changed. Core and expansion theatres are included
    by default; THEATRE_MODEL_COHORTS can still narrow the active cohorts.
    """
    name = (theatre_name or "").strip()
    if not name:
        return True
    cohort_sets = cohort_sets if cohort_sets is not None else load_theatre_cohort_sets()
    model_cohorts = model_cohorts if model_cohorts is not None else active_model_cohorts()
    known_names = set().union(*cohort_sets.values()) if cohort_sets else set()
    if name not in known_names:
        return True
    allowed_names = set()
    for cohort in model_cohorts:
        allowed_names.update(cohort_sets.get(cohort, set()))
    return name in allowed_names


def load_seat_data(weekend_of=None):
    """Load seat-counts.csv and group by movie → date → list of theatre rows.

    If weekend_of is set, only loads rows from that opening weekend.
    If not set, uses the current weekend (Thu-Sun → Friday anchor).
    Falls back to loading all rows if weekend_of column is absent (old data).
    """
    if not os.path.exists(SEAT_CSV):
        return {}

    if weekend_of is None:
        # Use the most recent weekend_of found in the CSV rather than
        # computing from today's date — avoids day-of-week arithmetic mismatches.
        with open(SEAT_CSV, "r") as f:
            weekends = [r.get("weekend_of", "") for r in csv.DictReader(f) if r.get("weekend_of")]
        weekend_of = max(weekends) if weekends else _current_weekend_friday()

    data = {}
    rows = []
    cohort_sets = load_theatre_cohort_sets()
    model_cohorts = active_model_cohorts()
    with open(SEAT_CSV, "r") as f:
        for row in csv.DictReader(f):
            movie = row.get("movie_title", "")
            date = row.get("date", "")
            if not movie or not date:
                continue
            if not model_allows_theatre(
                row.get("theatre_name", ""),
                cohort_sets=cohort_sets,
                model_cohorts=model_cohorts,
            ):
                continue
            rows.append(row)

    # Determine whether ANY row in this file has weekend_of set.
    # If yes, filter strictly by weekend_of; if no (pure old-format CSV),
    # include all rows so we don't accidentally drop everything.
    has_weekend_col = any(r.get("weekend_of", "") for r in rows)
    for row in rows:
        row_weekend = row.get("weekend_of", "")
        if has_weekend_col and row_weekend != weekend_of:
            continue
        data.setdefault(row["movie_title"], {}).setdefault(row["date"], []).append(row)
    return data


def load_pre_reservation_data(weekend_of=None, through_date=None):
    """Load pre-reservation snapshots grouped by movie → show_date.

    These rows are a separate early-demand signal. They are not mixed into
    regular post-show seat counts; prediction code decides when to use them.
    """
    if not os.path.exists(PRE_RESERVATION_CSV):
        return {}

    if weekend_of is None:
        with open(PRE_RESERVATION_CSV, "r") as f:
            weekends = [
                r.get("weekend_of", "")
                for r in csv.DictReader(f)
                if r.get("weekend_of")
            ]
        weekend_of = max(weekends) if weekends else _current_weekend_friday()

    data = {}
    cohort_sets = load_theatre_cohort_sets()
    model_cohorts = active_model_cohorts()
    with open(PRE_RESERVATION_CSV, "r") as f:
        reader = csv.DictReader(f)
        has_weekend_col = "weekend_of" in (reader.fieldnames or [])
        for row in reader:
            movie = row.get("movie_title", "")
            show_date = row.get("show_date", "")
            if not movie or not show_date:
                continue
            if has_weekend_col and row.get("weekend_of", "") != weekend_of:
                continue
            snapshot_date = (row.get("snapshot_time", "") or "")[:10]
            if through_date:
                if not snapshot_date or snapshot_date > through_date:
                    continue
            if not model_allows_theatre(
                row.get("theatre_name", ""),
                cohort_sets=cohort_sets,
                model_cohorts=model_cohorts,
            ):
                continue
            data.setdefault(movie, {}).setdefault(show_date, []).append(row)
    return data


def seat_data_weekend_of(movie_seat_data):
    """Infer the opening-weekend key from one movie's loaded seat rows."""
    weekends = sorted({
        row.get("weekend_of", "")
        for rows in movie_seat_data.values()
        for row in rows
        if row.get("weekend_of")
    })
    return weekends[-1] if weekends else _current_weekend_friday()


def filter_seat_data_through(seat_data, through_date=None):
    """Drop seat rows after through_date for clean historical replay."""
    if not through_date:
        return seat_data
    filtered = {}
    for movie, dates in seat_data.items():
        kept_dates = {
            date: rows
            for date, rows in dates.items()
            if date <= through_date
        }
        if kept_dates:
            filtered[movie] = kept_dates
    return filtered


def load_polymarket_data(weekend_of=None, through_date=None):
    """Load Polymarket bracket rows for one opening weekend, deduped by market.

    The CSV is append-only and may contain multiple snapshots of the same
    bracket market across several days. For prediction we want the latest
    snapshot per market for the target weekend, not every historical row.
    If through_date is set, ignore snapshots after that date for replay.
    """
    if not os.path.exists(POLY_CSV):
        return {}

    rows = []
    with open(POLY_CSV, "r") as f:
        for idx, row in enumerate(csv.DictReader(f)):
            movie = row.get("movie_title", "")
            if not movie:
                continue
            date_str = row.get("date", "").strip()
            if through_date and date_str and date_str > through_date:
                continue
            row_weekend = _opening_weekend_for_date(date_str) if date_str else ""
            rows.append((idx, row, row_weekend, date_str))

    if weekend_of is None:
        weekends = [row_weekend for _, _, row_weekend, _ in rows if row_weekend]
        weekend_of = max(weekends) if weekends else _current_weekend_friday()

    latest_rows = {}
    for idx, row, row_weekend, date_str in rows:
        if row_weekend and row_weekend != weekend_of:
            continue
        movie = row.get("movie_title", "")
        market_key = row.get("market_id", "") or row.get("market_question", "")
        if not movie or not market_key:
            continue
        dedupe_key = (movie, market_key)
        sort_key = (date_str, idx)
        prev = latest_rows.get(dedupe_key)
        if not prev or sort_key >= prev[0]:
            latest_rows[dedupe_key] = (sort_key, row)

    event_groups = {}
    for sort_key, row in latest_rows.values():
        movie = row["movie_title"]
        event_url = row.get("market_url", "")
        event_groups.setdefault(movie, {}).setdefault(event_url, []).append((sort_key, row))

    data = {}
    for movie, groups in event_groups.items():
        # Polymarket can replace an event with a new strike ladder mid-weekend
        # (for example, a higher-strikes event after the first ladder gets blown
        # through). Use one coherent event set per movie: latest snapshot wins,
        # with bracket count and volume as tie-breakers.
        def group_score(item):
            _, group_rows = item
            latest_sort = max(sort_key for sort_key, _ in group_rows)
            total_volume = sum(float(row.get("volume", 0) or 0) for _, row in group_rows)
            return latest_sort, len(group_rows), total_volume

        _, best_rows = max(groups.items(), key=group_score)
        data[movie] = [row for _, row in sorted(best_rows)]
    return data


def load_calibration():
    """Load calibration.json or return defaults."""
    if os.path.exists(CALIBRATION_JSON):
        with open(CALIBRATION_JSON, "r") as f:
            cal = json.load(f)
    else:
        cal = {
        "history": [],
        "calibration_factors": {
            "amc_market_share": DEFAULT_AMC_MARKET_SHARE,
            "overall_scale_factor": 1.0,
            "day_weights": DAY_WEIGHTS_DEFAULT,
            "format_scale_factors": {},
            "historical_accuracy": [],
            "last_updated": None,
        }
        }
    return sanitize_calibration(
        cal,
        day_weights_default=DAY_WEIGHTS_DEFAULT,
        default_market_share=DEFAULT_AMC_MARKET_SHARE,
    )


def load_frozen_calibration(weekend_of):
    """Load a pre-actual calibration freeze for live-model replay."""
    cal = load_calibration_freeze(DATA_DIR, weekend_of)
    return sanitize_calibration(
        cal,
        day_weights_default=DAY_WEIGHTS_DEFAULT,
        default_market_share=DEFAULT_AMC_MARKET_SHARE,
    )


def save_calibration(cal):
    """Save calibration.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CALIBRATION_JSON, "w") as f:
        json.dump(cal, f, indent=2)


def load_theatre_counts():
    """Load national theatre counts from theatre-counts.json (scraped from BOM)."""
    if os.path.exists(THEATRE_COUNTS_JSON):
        with open(THEATRE_COUNTS_JSON) as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if not k.startswith("_")}
    return {}


def national_theatre_count_for_movie(movie, theatre_counts):
    """Find the BOM theatre count for a movie, allowing simple fuzzy matches."""
    nat_count = theatre_counts.get(movie)
    if nat_count:
        return nat_count
    for tc_movie, count in theatre_counts.items():
        if tc_movie.lower() in movie.lower() or movie.lower() in tc_movie.lower():
            return count
    return None


# ── Stage A: Per-Theatre Daily Revenue ───────────────────────────────────────

def time_multiplier(row):
    """Estimate multiplier based on minutes_after_showtime from the CSV.

    Negative = scraped before show started (still selling tickets).
    Zero or positive = scraped after show started (occupancy is near-final).
    """
    # Use _parse_numeric so float-formatted cells (e.g. "96.0" from Excel
    # edits) don't silently fall back to delta=0 and misroute the row into
    # the post-showtime bucket.
    delta = _parse_numeric(row.get("minutes_after_showtime", 0), default=0)

    if delta < -MAX_REASONABLE_PRE_SHOW_MINUTES:
        return 1.0
    elif delta < -120:
        return 1.6   # >2h before showtime — occupancy will grow significantly
    elif delta < -60:
        return 1.3
    elif delta < 0:
        return 1.1   # <1h before — nearly final
    else:
        return 1.0   # after showtime — actual attendance


def infer_format_rank(row):
    """Infer format_rank from format string or auditorium_type if not present."""
    if row.get("format_rank"):
        try:
            return int(row["format_rank"])
        except (ValueError, TypeError):
            pass
    # Fall back to auditorium_type or format field
    fmt = (row.get("format") or row.get("auditorium_type") or
           row.get("auditorium_name") or "").lower()
    if "imax with laser" in fmt:
        return 7
    elif "imax" in fmt:
        return 6
    elif "dolby" in fmt:
        return 5
    elif "prime" in fmt:
        return 4
    elif "xl" in fmt:
        return 3
    elif "laser" in fmt:
        return 2
    return 1  # standard/digital


def _parse_numeric(value, default=0):
    """Coerce CSV cells like '96.0' or '' to ints without crashing on floats."""
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def estimate_theatre_daily_revenue(row, cal):
    """Stage A: revenue for ONE captured evening showtime (one CSV row).

    A CSV row = a single (theatre, movie, format, showtime) snapshot. This
    returns the *actual* revenue of THAT specific show:

        revenue = projected_occupancy × auditorium_seats × format_ticket_price

    No deflators. The row is real data — observed seats sold at observed
    showtime — so we don't deflate it toward a hypothetical day-average.
    `time_multiplier` projects pre-showtime occupancy forward to showtime,
    which IS legitimate (tickets keep selling until lights down).

    The caller (predict_movie) sums these per-row revenues per theatre/day.
    Friday's late-day sample is scaled to full-day; Saturday/Sunday 10am-11pm
    samples are treated as full-day coverage.
    """
    total_seats = _parse_numeric(row.get("total_seats", 0))
    seats_sold = _parse_numeric(row.get("seats_sold", 0))

    # Detect data format: new collect.py vs old scraper
    has_seat_map_field = row.get("has_seat_map", "")
    has_seat_map = has_seat_map_field.lower() in ("true", "1", "yes") if has_seat_map_field else (total_seats > 0)

    is_sold_out = row.get("is_sold_out", "").lower() in ("true", "1", "yes")
    is_almost_sold = row.get("is_almost_sold_out", "").lower() in ("true", "1", "yes")
    format_rank = infer_format_rank(row)

    # Ticket price — explicit per-row override wins; otherwise format-aware.
    raw_price = row.get("adult_ticket_price", "") or row.get("ticket_price_estimate", "")
    try:
        ticket_price = float(raw_price) if raw_price else None
    except (ValueError, TypeError):
        ticket_price = None
    if ticket_price is None:
        ticket_price = FORMAT_TICKET_PRICES.get(format_rank, FORMAT_TICKET_PRICES.get(0))

    # Occupancy
    if has_seat_map and total_seats > 0:
        observed_occ = seats_sold / total_seats
    elif is_sold_out:
        observed_occ = 0.95
        total_seats = DEFAULT_SEATS_PER_SHOW
    elif is_almost_sold:
        observed_occ = 0.80
        total_seats = DEFAULT_SEATS_PER_SHOW
    elif total_seats > 0 and seats_sold >= 0:
        # Old format: has seat data even without explicit has_seat_map flag
        observed_occ = seats_sold / total_seats
    else:
        return None  # can't estimate without data

    # Project pre-showtime occupancy forward to showtime (tickets keep
    # selling). Negative delta = scraped before show; positive = after.
    time_mult = time_multiplier(row)
    projected_occ = min(1.0, observed_occ * time_mult)

    revenue_per_showtime = projected_occ * total_seats * ticket_price

    return {
        "revenue": revenue_per_showtime,
        "projected_occ": projected_occ,
        "observed_occ": observed_occ,
        "time_mult": time_mult,
        "total_seats": total_seats,
        "ticket_price": ticket_price,
        "format_rank": format_rank,
        "theatre_name": row.get("theatre_name", "?"),
        "format": row.get("format", "") or row.get("auditorium_type", "") or row.get("auditorium_name", "") or "?",
        "has_seat_map": has_seat_map,
    }


# ── Stage B: Sum All AMC Theatres ────────────────────────────────────────────

def sum_amc_theatres(theatre_results):
    """Stage B: sum all theatre revenues. Returns (total, stats)."""
    revenues = [t["revenue"] for t in theatre_results if t is not None]
    if not revenues:
        return 0, {}
    total = sum(revenues)
    mean_rev = statistics.mean(revenues)
    median_rev = statistics.median(revenues)
    stdev = statistics.stdev(revenues) if len(revenues) > 1 else mean_rev * 0.3
    return total, {
        "n_theatres": len(revenues),
        "mean_revenue": mean_rev,
        "median_revenue": median_rev,
        "stdev": stdev,
        "total": total,
    }


def snapshot_reservation_multiplier(minutes_until_showtime):
    """Project pre-reserved seats forward to final attendance.

    This is deliberately conservative and separately calibrated by
    snapshot_to_day_scale_factors once actuals are available.
    """
    minutes = _parse_numeric(minutes_until_showtime, default=0)
    if minutes <= 0:
        return 1.0
    if minutes <= 60:
        return 1.15
    if minutes <= 180:
        return 1.35
    if minutes <= 360:
        return 1.60
    if minutes <= 24 * 60:
        return 2.20
    if minutes <= 48 * 60:
        return 3.00
    return 4.00


def estimate_snapshot_showtime_revenue(row):
    """Estimate final showtime revenue from one pre-reservation row."""
    total_seats = _parse_numeric(row.get("total_seats", 0))
    reserved = _parse_numeric(row.get("reserved_seats", 0))
    if total_seats <= 0 or reserved < 0:
        return None

    fmt = (row.get("auditorium_type") or row.get("auditorium_name") or "").lower()
    format_rank = 1
    if "imax with laser" in fmt:
        format_rank = 7
    elif "imax" in fmt:
        format_rank = 6
    elif "dolby" in fmt:
        format_rank = 5
    elif "prime" in fmt:
        format_rank = 4
    elif "xl" in fmt:
        format_rank = 3
    elif "laser" in fmt:
        format_rank = 2

    multiplier = snapshot_reservation_multiplier(row.get("minutes_until_showtime", 0))
    projected_reserved = min(total_seats, reserved * multiplier)
    ticket_price = FORMAT_TICKET_PRICES.get(format_rank, FORMAT_TICKET_PRICES.get(1))
    revenue = projected_reserved * ticket_price
    return {
        "revenue": revenue,
        "projected_occ": projected_reserved / total_seats if total_seats else 0.0,
        "reserved_occ": reserved / total_seats if total_seats else 0.0,
        "reservation_mult": multiplier,
        "total_seats": total_seats,
        "ticket_price": ticket_price,
        "format_rank": format_rank,
        "theatre_name": row.get("theatre_name", "?"),
        "format": row.get("auditorium_type") or row.get("auditorium_name") or "?",
    }


def snapshot_within_remaining_weekend_window(row):
    """Keep pre-reservation rows inside the remaining-weekend signal window."""
    minutes = _parse_numeric(row.get("minutes_until_showtime", ""), default=None)
    if minutes is None:
        return True
    return minutes <= SNAPSHOT_MAX_LEAD_MINUTES


def _positive_float(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _clamp(value, low, high):
    return max(low, min(high, value))


def _coverage_average(daily_coverage_ratios):
    if not daily_coverage_ratios:
        return None
    values = []
    for value in daily_coverage_ratios.values():
        if value is None:
            continue
        try:
            values.append(_clamp(float(value), 0.0, 1.0))
        except (TypeError, ValueError):
            continue
    return sum(values) / len(values) if values else None


def _coverage_value(value, default=0.0):
    try:
        return _clamp(float(value), 0.0, 1.0)
    except (TypeError, ValueError):
        return default


def weighted_weekend_coverage_ratio(day_coverage_ratios, cal):
    """Coverage over the full opening weekend, counting missing days as zero."""
    if not day_coverage_ratios:
        return None
    day_weights = get_day_weights(cal)
    total_weight = sum(
        day_weights.get(day, 0)
        for day in OPENING_WEEKEND_DAYS
    )
    if total_weight <= 0:
        return _coverage_average(day_coverage_ratios)
    weighted = 0.0
    for day in OPENING_WEEKEND_DAYS:
        weight = day_weights.get(day, 0)
        if weight <= 0:
            continue
        weighted += weight * _coverage_value(
            day_coverage_ratios.get(day),
            default=0.0,
        )
    return _clamp(weighted / total_weight, 0.0, 1.0)


def missing_data_profile(daily_details, cal, snapshot_layer=None):
    """Summarize missing/partial data using weekend day weights."""
    day_weights = get_day_weights(cal)
    expected_days = [
        day for day in OPENING_WEEKEND_DAYS
        if day_weights.get(day, 0) > 0
    ]
    total_weight = sum(day_weights.get(day, 0) for day in expected_days) or 1.0
    observed_days = [
        day for day in expected_days
        if day in (daily_details or {})
    ]
    missing_days = [
        day for day in expected_days
        if day not in (daily_details or {})
    ]
    day_coverages = {}
    missing_timezone_days = []
    for day, details in (daily_details or {}).items():
        coverage = details.get(
            "effective_coverage_ratio",
            details.get("coverage_ratio"),
        )
        day_coverages[day] = coverage
        if details.get("missing_timezones"):
            missing_timezone_days.append(day)

    observed_day_share = sum(day_weights.get(day, 0) for day in observed_days) / total_weight
    missing_day_share = sum(day_weights.get(day, 0) for day in missing_days) / total_weight
    weighted_coverage = weighted_weekend_coverage_ratio(day_coverages, cal)
    snapshot_days = []
    snapshot_coverage = None
    if snapshot_layer:
        snapshot_days = snapshot_layer.get("snapshot_days", [])
        snapshot_coverage = snapshot_layer.get("snapshot_coverage_ratio")

    return {
        "observed_days": observed_days,
        "missing_days": missing_days,
        "observed_day_share": _clamp(observed_day_share, 0.0, 1.0),
        "missing_day_share": _clamp(missing_day_share, 0.0, 1.0),
        "seat_weighted_coverage_ratio": weighted_coverage,
        "missing_timezone_days": sorted(set(missing_timezone_days)),
        "snapshot_days": snapshot_days,
        "snapshot_coverage_ratio": snapshot_coverage,
    }


def reference_amc_theatre_count(cal, fallback=0, model_cohort_key=None):
    """The stable sample size that AMC-share calibration was trained against."""
    factors = (cal or {}).get("calibration_factors", {}) if cal else {}
    cohort_key = normalize_model_cohort_key(model_cohort_key)
    refs_by_cohort = factors.get("reference_amc_theatres_by_cohort") or {}
    if cohort_key and isinstance(refs_by_cohort, dict):
        for key, value in refs_by_cohort.items():
            if normalize_model_cohort_key(key) != cohort_key:
                continue
            explicit_cohort = _positive_float(value)
            if explicit_cohort:
                return int(round(explicit_cohort))

    explicit = _positive_float(factors.get("reference_amc_theatres"))
    if explicit and (not cohort_key or cohort_key == CORE_COHORT):
        return int(round(explicit))

    reference_candidates = []
    observed_candidates = []
    for entry in (cal or {}).get("history", []):
        entry_key = normalize_model_cohort_key(entry.get("model_cohort_key"))
        if cohort_key:
            if entry_key and entry_key != cohort_key:
                continue
            if not entry_key and cohort_key != CORE_COHORT:
                continue
        ref = _positive_float(entry.get("reference_amc_theatres"))
        if ref:
            reference_candidates.append(ref)
            continue
        daily_counts = entry.get("daily_theatre_counts") or {}
        daily_coverage = entry.get("daily_coverage_ratios") or {}
        for day, count in daily_counts.items():
            n_theatres = _positive_float(count)
            if not n_theatres:
                continue
            coverage = _positive_float(daily_coverage.get(day))
            if coverage is None or coverage >= MIN_DAILY_CALIBRATION_COVERAGE:
                observed_candidates.append(n_theatres)
        if not daily_counts:
            n_theatres = _positive_float(entry.get("n_theatres"))
            if n_theatres:
                observed_candidates.append(n_theatres)

    if reference_candidates:
        return int(round(statistics.median(reference_candidates)))
    if observed_candidates:
        return int(round(statistics.median(observed_candidates)))

    fallback_count = _positive_float(fallback)
    return int(round(fallback_count)) if fallback_count else 0


def remember_reference_amc_theatres(cal, reference_amc_theatres, model_cohort_key=None):
    """Persist the denominator used for a prediction without moving other cohorts."""
    reference = _positive_float(reference_amc_theatres)
    if not reference:
        return None

    ref = int(round(reference))
    factors = cal.setdefault("calibration_factors", {})
    cohort_key = normalize_model_cohort_key(model_cohort_key)
    if cohort_key:
        factors.setdefault("reference_amc_theatres_by_cohort", {})[cohort_key] = ref
        if cohort_key == CORE_COHORT:
            factors.setdefault("reference_amc_theatres", ref)
    else:
        factors.setdefault("reference_amc_theatres", ref)
    return ref


def normalize_amc_sample(amc_total, observed_theatres, reference_theatres,
                         representativeness=1.0):
    """Normalize sampled AMC revenue to the calibration reference sample size."""
    observed = _positive_float(observed_theatres)
    reference = _positive_float(reference_theatres)
    if not observed or not reference:
        return amc_total, 1.0
    factor = reference / observed
    if factor > 1.0:
        rep_value = _positive_float(representativeness)
        rep = 1.0 if rep_value is None else _clamp(rep_value, 0.0, 1.0)
        factor = 1.0 + (factor - 1.0) * rep
    return amc_total * factor, factor


def _row_timezone(row, theatre_timezone_map=None):
    raw = (row.get("timezone") or "").strip().upper()
    if raw in MODEL_TIMEZONE_GROUPS:
        return raw
    theatre_name = (row.get("theatre_name") or "").strip()
    if theatre_name and theatre_timezone_map:
        return theatre_timezone_map.get(theatre_name)
    return None


def timezone_coverage_profile(rows, expected_timezone_counts=None,
                              theatre_timezone_map=None):
    """Measure whether a day is missing an entire expected TZ bucket.

    Missing a whole timezone is not the same as randomly missing theatres. When
    a bucket is absent, only part of the sample-size normalization is trusted.
    """
    observed = sorted({
        tz for tz in (
            _row_timezone(row, theatre_timezone_map=theatre_timezone_map)
            for row in rows
        )
        if tz in MODEL_TIMEZONE_GROUPS
    })
    if not observed:
        return {
            "observed_timezones": [],
            "expected_timezones": [],
            "missing_timezones": [],
            "coverage_factor": 1.0,
        }

    expected_counts = {
        tz: count for tz, count in (expected_timezone_counts or {}).items()
        if tz in MODEL_TIMEZONE_GROUPS and _positive_float(count)
    }
    if not expected_counts:
        expected_counts = {tz: 1 for tz in observed}

    expected = sorted(expected_counts)
    missing = sorted(set(expected) - set(observed))
    if not missing:
        factor = 1.0
    else:
        total_weight = sum(expected_counts.values())
        observed_weight = sum(
            expected_counts.get(tz, 0)
            for tz in observed
            if tz in expected_counts
        )
        factor = observed_weight / total_weight if total_weight else 1.0
        factor = _clamp(factor, 0.0, 1.0)

    return {
        "observed_timezones": observed,
        "expected_timezones": expected,
        "missing_timezones": missing,
        "coverage_factor": factor,
    }


def seat_data_quality(n_theatres, n_days, coverage_ratio=None):
    """0-1 quality score for how much the seat model should influence blends."""
    if coverage_ratio is None:
        return min(1.0, (n_theatres / 100) * 0.6 + (n_days / 3) * 0.4)
    theatre_component = _coverage_value(coverage_ratio)
    day_component = _clamp(n_days / len(OPENING_WEEKEND_DAYS), 0.0, 1.0)
    return _clamp(0.70 * theatre_component + 0.30 * day_component, 0.0, 1.0)


def confidence_interval_factors(n_days, coverage_ratio=None):
    """Low/high multipliers for seat-only intervals, adjusted for coverage."""
    low, high = DAY_CONFIDENCE.get(n_days, (0.70, 1.40))
    if coverage_ratio is None:
        return low, high
    coverage = _coverage_value(coverage_ratio)
    missing = 1.0 - coverage
    low *= 1.0 - 0.35 * missing
    high *= 1.0 + 0.55 * missing
    return max(0.25, low), max(high, low)


def comp_component_weight(n_days):
    """How much the comp-translated seat signal should affect the seat model."""
    if n_days <= 1:
        return 0.70
    if n_days == 2:
        return 0.45
    if n_days == 3:
        return 0.25
    return 0.10


def seat_primary_ensemble(pred):
    """Blend direct seat totals with the comp-translated seat signal."""
    comp_mid = pred.get("seat_comp_adjusted_mid_m", pred.get("seat_comp_mid_m"))
    if comp_mid is None:
        return None

    w_comp = comp_component_weight(pred.get("n_days", 0))
    w_direct = 1.0 - w_comp
    direct_mid = pred["seat_mid_m"]
    direct_low = pred["seat_low_m"]
    direct_high = pred["seat_high_m"]
    comp_low = pred.get("seat_comp_adjusted_low_m", pred["seat_comp_low_m"])
    comp_high = pred.get("seat_comp_adjusted_high_m", pred["seat_comp_high_m"])

    mid = direct_mid * w_direct + comp_mid * w_comp
    low = direct_low * w_direct + comp_low * w_comp
    high = direct_high * w_direct + comp_high * w_comp

    # If direct day-weight extrapolation and comp shape disagree, widen the
    # band instead of hiding model disagreement in a precise-looking midpoint.
    disagreement = abs(comp_mid - direct_mid)
    low = max(0.0, low - disagreement * 0.25)
    high = high + disagreement * 0.25
    return {
        "mid_m": mid,
        "low_m": min(low, high),
        "high_m": max(low, high),
        "w_direct": w_direct,
        "w_comp": w_comp,
        "disagreement_m": disagreement,
    }


def has_missing_timezone_bucket(pred):
    """Whether any collected day is missing a full expected timezone bucket."""
    for details in (pred.get("daily_details") or {}).values():
        if details.get("missing_timezones"):
            return True
    return False


def missing_data_prior_weight(pred):
    """Historical-prior weight for incomplete seat samples.

    The observed seat count remains the anchor, but one-day reads with weak
    coverage should not be treated as a full AMC census. Missing an entire
    timezone bucket is especially important because it is systematic, not
    random noise.
    """
    n_days = int(pred.get("n_days") or 0)
    if n_days <= 0:
        return 0.0

    profile = pred.get("missing_data_profile") or {}
    quality = _coverage_value(pred.get("seat_data_quality"), default=1.0)
    weight = 1.0 - quality
    missing_day_share = _coverage_value(
        profile.get("missing_day_share"),
        default=0.0,
    )
    weight = max(weight, missing_day_share * 0.60)
    if has_missing_timezone_bucket(pred) and n_days <= 1:
        weight = max(weight, 0.55)
    elif has_missing_timezone_bucket(pred):
        weight = max(weight, 0.15)

    if n_days <= 1:
        cap = 0.65
    elif n_days == 2:
        cap = 0.45
    elif n_days == 3:
        cap = 0.25
    else:
        cap = 0.10
    return _clamp(weight, 0.0, cap)


def coverage_adjusted_comp_model(pred, model, estimate):
    """Blend sparse seat+comp output with a metadata-only historical prior."""
    prior_mid = _positive_float(getattr(estimate, "prior_weekend_mid_m", 0))
    if not prior_mid:
        return None

    prior_low = _positive_float(getattr(estimate, "prior_weekend_low_m", 0)) or prior_mid
    prior_high = _positive_float(getattr(estimate, "prior_weekend_high_m", 0)) or prior_mid
    prior_low, prior_high = min(prior_low, prior_high), max(prior_low, prior_high)
    weight = missing_data_prior_weight(pred)
    if weight <= 0:
        return None

    seat_weight = 1.0 - weight
    mid = model["mid_m"] * seat_weight + prior_mid * weight
    low = model["low_m"] * seat_weight + prior_low * weight
    high = model["high_m"] * seat_weight + prior_high * weight
    disagreement = abs(model["mid_m"] - prior_mid)

    # Make the interval honestly reflect disagreement between the observed
    # seat signal and the metadata prior.
    low = max(0.0, low - disagreement * weight * 0.15)
    high = high + disagreement * weight * 0.15
    return {
        "mid_m": mid,
        "low_m": min(low, high),
        "high_m": max(low, high),
        "prior_mid_m": prior_mid,
        "prior_low_m": prior_low,
        "prior_high_m": prior_high,
        "prior_weight": weight,
        "seat_weight": seat_weight,
        "disagreement_m": disagreement,
    }


def _actual_status_is_final(entry):
    return (entry.get("actual_status") or "final") != "provisional"


def _historical_residual_weight(pred, entry):
    current_quality = _coverage_value(pred.get("seat_data_quality"), default=1.0)
    current_days = int(_positive_float(pred.get("n_days")) or 0)
    current_coverage = _coverage_value(
        pred.get("seat_weighted_coverage_ratio", pred.get("coverage_ratio")),
        default=current_quality,
    )

    entry_days = int(_positive_float(entry.get("n_days", entry.get("days_collected"))) or 0)
    entry_coverage = entry.get("coverage_ratio")
    if entry_coverage is None:
        entry_coverage = _coverage_average(entry.get("daily_coverage_ratios") or {})
    entry_coverage = _coverage_value(entry_coverage, default=0.0)
    entry_quality = seat_data_quality(
        _positive_float(entry.get("n_theatres")) or 0,
        entry_days,
        coverage_ratio=entry_coverage,
    )

    current_cohort = normalize_model_cohort_key(pred.get("model_cohort_key"))
    entry_cohort = normalize_model_cohort_key(entry.get("model_cohort_key"))
    if current_cohort and entry_cohort:
        cohort_weight = 1.0 if current_cohort == entry_cohort else 0.45
    else:
        cohort_weight = 0.65

    day_similarity = 1.0 - min(1.0, abs(current_days - entry_days) / 4.0) * 0.45
    coverage_similarity = 1.0 - abs(current_coverage - entry_coverage) * 0.45
    return max(
        0.0,
        entry_quality * cohort_weight * day_similarity * coverage_similarity,
    )


def historical_residual_regression(pred, cal):
    """Estimate a shrunken actual/predicted residual from settled history.

    This is a guardrail on top of the seat forecast, not a replacement for it:
    the current seat count remains the driver and the learned residual is capped
    heavily until there are many same-quality settled movies.
    """
    if not cal:
        return None

    values = []
    for entry in (cal or {}).get("history", [])[-20:]:
        if not _actual_status_is_final(entry):
            continue
        if _movie_matches(pred.get("movie", ""), entry.get("movie", "")):
            continue
        predicted = _positive_float(entry.get("predicted_mid"))
        actual = _positive_float(entry.get("actual_total", entry.get("actual")))
        if not predicted or not actual:
            continue
        weight = _historical_residual_weight(pred, entry)
        if weight <= 0:
            continue
        ratio = _clamp(
            actual / predicted,
            RESIDUAL_REGRESSION_RATIO_MIN,
            RESIDUAL_REGRESSION_RATIO_MAX,
        )
        values.append((ratio, weight, entry))

    if len(values) < RESIDUAL_REGRESSION_MIN_OBS:
        return None

    total_weight = sum(weight for _, weight, _ in values)
    if total_weight <= 0:
        return None

    log_ratio = sum(log(ratio) * weight for ratio, weight, _ in values) / total_weight
    raw_factor = exp(log_ratio)
    strength = min(
        RESIDUAL_REGRESSION_MAX_STRENGTH,
        total_weight / (total_weight + RESIDUAL_REGRESSION_PRIOR_WEIGHT),
    )
    factor = 1.0 + (raw_factor - 1.0) * strength
    factor = _clamp(
        factor,
        RESIDUAL_REGRESSION_FACTOR_MIN,
        RESIDUAL_REGRESSION_FACTOR_MAX,
    )
    return {
        "factor": factor,
        "raw_factor": raw_factor,
        "strength": strength,
        "n": len(values),
        "effective_weight": total_weight,
        "examples": [
            {
                "movie": entry.get("movie"),
                "weekend_of": entry.get("weekend_of"),
                "ratio": ratio,
                "weight": weight,
            }
            for ratio, weight, entry in sorted(
                values,
                key=lambda item: item[1],
                reverse=True,
            )[:5]
        ],
    }


def select_regression_prediction(pred, cal=None):
    """Attach the model-driven regression forecast.

    Polymarket and published trade estimates remain context only. Calibration,
    strategy, and reporting use the actual-predictive regression line. Prefer
    the seat+comp regression when available; fall back to the direct seat model.
    """
    if pred.get("seat_comp_adjusted_mid_m") is not None:
        source = "seat+comp-coverage-adjusted-regression"
        mid = pred["seat_comp_adjusted_mid_m"]
        low = pred["seat_comp_adjusted_low_m"]
        high = pred["seat_comp_adjusted_high_m"]
        basis = pred.get("seat_comp_adjusted_basis")
    elif pred.get("seat_comp_mid_m") is not None:
        source = "seat+comp-regression"
        mid = pred["seat_comp_mid_m"]
        low = pred["seat_comp_low_m"]
        high = pred["seat_comp_high_m"]
        basis = pred.get("seat_comp_basis")
    else:
        source = "seat-only-regression"
        mid = pred["seat_mid_m"]
        low = pred["seat_low_m"]
        high = pred["seat_high_m"]
        basis = "seat-only"

    snapshot_mid = pred.get("snapshot_mid_m")
    snapshot_weight = _coverage_value(pred.get("snapshot_model_weight"), default=0.0)
    if snapshot_mid is not None and snapshot_weight > 0:
        seat_weight = 1.0 - snapshot_weight
        snapshot_low = pred.get("snapshot_low_m", snapshot_mid)
        snapshot_high = pred.get("snapshot_high_m", snapshot_mid)
        base_mid = mid
        mid = base_mid * seat_weight + snapshot_mid * snapshot_weight
        low = low * seat_weight + snapshot_low * snapshot_weight
        high = high * seat_weight + snapshot_high * snapshot_weight
        disagreement = abs(snapshot_mid - base_mid)
        low = max(0.0, low - disagreement * snapshot_weight * 0.20)
        high = high + disagreement * snapshot_weight * 0.20
        pred["snapshot_blended_base_mid_m"] = base_mid
        pred["snapshot_blended_disagreement_m"] = disagreement
        pred["snapshot_blended_weight"] = snapshot_weight
        if source == "seat-only-regression":
            source = "seat+snapshot-regression"
        elif "seat+comp" in source:
            source = "seat+comp+snapshot-regression"
        else:
            source = f"{source}+snapshot"
        basis = f"{basis} + snapshot future days"

    residual = historical_residual_regression(pred, cal)
    if residual:
        base_mid = mid
        mid = mid * residual["factor"]
        low = low * residual["factor"]
        high = high * residual["factor"]
        pred["historical_residual_base_mid_m"] = base_mid
        pred["historical_residual_factor"] = round(residual["factor"], 4)
        pred["historical_residual_raw_factor"] = round(residual["raw_factor"], 4)
        pred["historical_residual_strength"] = round(residual["strength"], 4)
        pred["historical_residual_n"] = residual["n"]
        pred["historical_residual_effective_weight"] = round(
            residual["effective_weight"],
            3,
        )
        pred["historical_residual_examples"] = [
            {
                "movie": item["movie"],
                "weekend_of": item["weekend_of"],
                "ratio": round(item["ratio"], 4),
                "weight": round(item["weight"], 3),
            }
            for item in residual["examples"]
        ]
        source = f"{source}+historical-residual"
        basis = f"{basis} + settled residuals"

    pred["regression_mid_m"] = mid
    pred["regression_low_m"] = low
    pred["regression_high_m"] = high
    pred["regression_source"] = source
    pred["regression_basis"] = basis
    pred["regression_uses_polymarket"] = False
    pred["model_forecast_mid_m"] = mid
    pred["model_forecast_low_m"] = low
    pred["model_forecast_high_m"] = high
    pred["model_forecast_source"] = source
    pred["model_forecast_basis"] = basis
    pred["model_forecast_uses_polymarket"] = False
    return pred


def regression_prediction_values(pred):
    """Return the point/range used for actual-focused model reporting."""
    if pred.get("regression_mid_m") is None:
        select_regression_prediction(pred)
    return pred["regression_mid_m"], pred["regression_low_m"], pred["regression_high_m"]


# ── Stage C: AMC → Total Domestic ────────────────────────────────────────────

def amc_to_domestic(amc_revenue, cal):
    """Stage C: scale AMC revenue to total domestic market."""
    share = cal["calibration_factors"].get("amc_market_share", DEFAULT_AMC_MARKET_SHARE)
    share = max(0.10, min(0.50, share))   # clamp to sane range
    mid = amc_revenue / share
    # Uncertainty in market share: ±3 points, both bounds clamped away from 0
    low  = amc_revenue / min(0.50, share + 0.03)   # higher share → lower gross
    high = amc_revenue / max(0.10, share - 0.03)   # lower share  → higher gross
    # Sanity guard: ensure low ≤ mid ≤ high
    low  = min(low, mid)
    high = max(high, mid)
    return mid, low, high


# ── Stage D: Partial Days → Full Weekend ─────────────────────────────────────

def calibrated_daily_estimates(daily_estimates, cal):
    """Return per-day calibrated estimates from raw daily domestic estimates."""
    return {
        day: {
            "raw_mid": est,
            "scale": get_day_scale(cal, day),
            "mid": est * get_day_scale(cal, day),
        }
        for day, est in daily_estimates.items()
    }


def days_to_weekend(daily_estimates, cal, daily_coverage_ratios=None):
    """Stage D: per-day calibrated daily estimates summed to a weekend total.

    daily_estimates: dict of {day_name: raw_domestic_daily_mid}
    Each captured day is multiplied by its own calibration scale factor
    (`day_scale_factors[day]`, default 1.0). The weekend total is the SUM of
    those calibrated daily values, so calibration adds up to a total
    day-by-day instead of being applied as one global multiplier on the sum.

    For partial-weekend coverage (e.g. only Thu+Fri scraped so far), the
    missing Thu-Sun days are extrapolated from the calibrated days using the
    learned `day_weights` distribution: total = collected_sum / collected_share.

    Returns (mid, low, high, calibrated_daily).
    """
    if not daily_estimates:
        return 0, 0, 0, {}

    day_weights = get_day_weights(cal)

    # Apply per-day scale factors first; the sum is the calibrated subtotal
    # of the days we actually have.
    calibrated_daily = calibrated_daily_estimates(daily_estimates, cal)
    collected_sum = sum(d["mid"] for d in calibrated_daily.values())
    collected_share = sum(day_weights.get(day, 0) for day in calibrated_daily)

    # If we have substantially the full weekend (Thu-Sun ≈ 1.0), the sum IS
    # the prediction — no extrapolation needed. The 0.99 threshold leaves a
    # rounding cushion for day_weights that sum to e.g. 0.9999.
    if collected_share >= 0.99:
        weekend_mid = collected_sum
    elif collected_share > 0:
        # Partial weekend: scale collected_sum up to the full weekend share.
        # E.g. Thu+Fri share = 0.12+0.32=0.44, so weekend ≈ collected/0.44.
        weekend_mid = collected_sum / collected_share
    else:
        # Day_weights misconfigured for this set of days — fall back to a
        # wide bracket around the raw sum so we never silently zero out.
        return collected_sum, collected_sum * 0.5, collected_sum * 2.0, calibrated_daily

    # Confidence based on how many days and how complete the scraped sample was.
    n_days = len(daily_estimates)
    coverage_ratio = _coverage_average(daily_coverage_ratios)
    weighted_coverage_ratio = weighted_weekend_coverage_ratio(
        daily_coverage_ratios,
        cal,
    )
    conf_low, conf_high = confidence_interval_factors(
        n_days,
        coverage_ratio=weighted_coverage_ratio,
    )
    weekend_low = weekend_mid * conf_low
    weekend_high = weekend_mid * conf_high

    return weekend_mid, weekend_low, weekend_high, calibrated_daily


def _snapshot_day_name(date_str, rows):
    csv_day = rows[0].get("day_of_week", "") if rows else ""
    if csv_day:
        return csv_day
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")


def _parse_snapshot_time(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def latest_snapshot_window_rows(rows, max_slice_age_hours=SNAPSHOT_MAX_SLICE_AGE_HOURS):
    """Keep one coherent recent snapshot run per show-date/timezone slice."""
    parsed_rows = []
    for idx, row in enumerate(rows):
        parsed = _parse_snapshot_time(row.get("snapshot_time", ""))
        parsed_rows.append((idx, row, parsed))

    latest_overall = max((parsed for _, _, parsed in parsed_rows if parsed), default=None)
    if latest_overall is None:
        return list(rows)

    by_slice = {}
    for item in parsed_rows:
        _, row, _ = item
        key = (row.get("show_date", ""), row.get("timezone", ""))
        by_slice.setdefault(key, []).append(item)

    keep_indexes = set()
    max_age_seconds = max_slice_age_hours * 3600
    for items in by_slice.values():
        timed = [item for item in items if item[2]]
        if not timed:
            keep_indexes.update(idx for idx, _, _ in items)
            continue
        latest_slice_time = max(parsed for _, _, parsed in timed)
        if (latest_overall - latest_slice_time).total_seconds() > max_age_seconds:
            continue
        latest_item = max(
            timed,
            key=lambda item: (
                item[2],
                item[1].get("snapshot_bucket", ""),
                item[1].get("run_id", ""),
            ),
        )
        latest_run_id = latest_item[1].get("run_id", "")
        latest_bucket = latest_item[1].get("snapshot_bucket", "")
        for idx, row, _ in items:
            if latest_run_id and row.get("run_id", "") == latest_run_id:
                keep_indexes.add(idx)
            elif not latest_run_id and row.get("snapshot_bucket", "") == latest_bucket:
                keep_indexes.add(idx)

    return [row for idx, row, _ in parsed_rows if idx in keep_indexes]


def _latest_snapshot_showtime_rows(rows):
    latest = {}
    for row in rows:
        t_name = row.get("theatre_name", "")
        showtime_key = (
            row.get("showtime_id")
            or row.get("amc_seat_map_url")
            or f"{row.get('auditorium_type') or row.get('auditorium_name')}|{row.get('showtime')}"
        )
        key = f"{t_name}|{showtime_key}"
        sort_key = (
            row.get("snapshot_bucket", ""),
            row.get("snapshot_time", ""),
            row.get("run_id", ""),
        )
        prev = latest.get(key)
        if not prev or sort_key > prev[0]:
            latest[key] = (sort_key, row)
    return [row for _, row in latest.values()]


def estimate_snapshot_day(rows, date_str, cal, expected_amc_theatres,
                          expected_timezone_counts=None,
                          theatre_timezone_map=None,
                          national_theatre_count=None):
    """Estimate one future day from pre-reservation snapshots only."""
    day_name = _snapshot_day_name(date_str, rows)
    latest_rows = _latest_snapshot_showtime_rows(latest_snapshot_window_rows(rows))
    lead_window_rows = [
        row for row in latest_rows
        if snapshot_within_remaining_weekend_window(row)
    ]
    lead_window_ignored = len(latest_rows) - len(lead_window_rows)
    latest_rows = lead_window_rows
    per_showtime_results = []
    captured_by_theatre = {}
    no_data_count = 0
    for row in latest_rows:
        result = estimate_snapshot_showtime_revenue(row)
        if not result:
            no_data_count += 1
            continue
        per_showtime_results.append(result)
        captured_by_theatre.setdefault(result["theatre_name"], []).append(result)

    if not per_showtime_results:
        return None

    theatre_results = []
    showings_by_theatre = {}
    for t_name, captured_rows in captured_by_theatre.items():
        revenue = sum(r["revenue"] for r in captured_rows)
        theatre_results.append({
            "revenue": revenue,
            "theatre_name": t_name,
            "n_snapshot_showings": len(captured_rows),
        })
        showings_by_theatre[t_name] = len(captured_rows)

    sampled_amc_total, amc_stats = sum_amc_theatres(theatre_results)
    n_amc_theatres = amc_stats.get("n_theatres", 0)
    tz_profile = timezone_coverage_profile(
        latest_rows,
        expected_timezone_counts=expected_timezone_counts,
        theatre_timezone_map=theatre_timezone_map,
    )
    amc_total, sample_norm_factor = normalize_amc_sample(
        sampled_amc_total,
        n_amc_theatres,
        expected_amc_theatres,
        representativeness=tz_profile["coverage_factor"],
    )
    coverage_ratio = (
        min(1.0, n_amc_theatres / expected_amc_theatres)
        if expected_amc_theatres else None
    )
    effective_coverage_ratio = coverage_ratio
    if coverage_ratio is not None and tz_profile["missing_timezones"]:
        effective_coverage_ratio = coverage_ratio * tz_profile["coverage_factor"]

    domestic_mid, domestic_low, domestic_high = amc_to_domestic(amc_total, cal)
    if national_theatre_count and n_amc_theatres > 0:
        mean_rev = amc_stats.get("mean_revenue", 0)
        nat_est = mean_rev * national_theatre_count
        domestic_mid = domestic_mid * 0.6 + nat_est * 0.4
        domestic_low = domestic_low * 0.6 + nat_est * 0.4 * 0.85
        domestic_high = domestic_high * 0.6 + nat_est * 0.4 * 1.15

    snapshot_scale = get_snapshot_to_day_scale(cal, day_name)
    avg_showings = (
        sum(showings_by_theatre.values()) / len(showings_by_theatre)
        if showings_by_theatre else 0
    )
    return {
        "date": date_str,
        "day": day_name,
        "source": "pre-reservation-snapshot",
        "amc_total": amc_total,
        "sampled_amc_total": sampled_amc_total,
        "sample_normalization_factor": sample_norm_factor,
        "raw_domestic_mid": domestic_mid,
        "raw_domestic_low": domestic_low,
        "raw_domestic_high": domestic_high,
        "domestic_mid": domestic_mid * snapshot_scale,
        "domestic_low": domestic_low * snapshot_scale,
        "domestic_high": domestic_high * snapshot_scale,
        "snapshot_scale": snapshot_scale,
        "n_theatres": n_amc_theatres,
        "expected_theatres": expected_amc_theatres,
        "coverage_ratio": coverage_ratio,
        "effective_coverage_ratio": effective_coverage_ratio,
        "observed_timezones": tz_profile["observed_timezones"],
        "expected_timezones": tz_profile["expected_timezones"],
        "missing_timezones": tz_profile["missing_timezones"],
        "timezone_coverage_factor": tz_profile["coverage_factor"],
        "n_no_data": no_data_count,
        "n_lead_window_ignored": lead_window_ignored,
        "avg_showings_per_cinema": round(avg_showings, 1),
        "theatre_results": theatre_results,
    }


def same_week_snapshot_scale(snapshot_details, regular_daily_details):
    """Calibrate pre-reservation snapshots to same-week observed seat days."""
    anchors = []
    for day_name, details in snapshot_details.items():
        regular = regular_daily_details.get(day_name)
        if not regular:
            continue
        snapshot_mid = _positive_float(details.get("domestic_mid"))
        regular_mid = _positive_float(regular.get("domestic_mid"))
        if not snapshot_mid or not regular_mid:
            continue
        coverage = _coverage_value(
            details.get("effective_coverage_ratio", details.get("coverage_ratio")),
            default=0.0,
        )
        if coverage <= 0:
            continue
        raw_ratio = regular_mid / snapshot_mid
        ratio = _clamp(
            raw_ratio,
            SNAPSHOT_SAME_WEEK_SCALE_MIN,
            SNAPSHOT_SAME_WEEK_SCALE_MAX,
        )
        anchors.append({
            "day": day_name,
            "scale": ratio,
            "raw_scale": raw_ratio,
            "weight": coverage,
            "snapshot_mid": snapshot_mid,
            "regular_mid": regular_mid,
        })

    if not anchors:
        return 1.0, []

    total_weight = sum(anchor["weight"] for anchor in anchors)
    if total_weight <= 0:
        return 1.0, []
    scale = sum(anchor["scale"] * anchor["weight"] for anchor in anchors) / total_weight
    return scale, anchors


def apply_same_week_snapshot_scale(details, scale):
    if not details or abs(scale - 1.0) < 1e-9:
        return details
    adjusted = dict(details)
    adjusted["same_week_snapshot_scale"] = scale
    for key in ("domestic_mid", "domestic_low", "domestic_high"):
        adjusted[f"pre_same_week_{key}"] = adjusted.get(key)
        adjusted[key] = adjusted.get(key, 0) * scale
    return adjusted


def regular_day_shape_priors(regular_daily_details, cal):
    """Daily priors implied by the observed seat days and learned day shape."""
    if not regular_daily_details:
        return {}
    day_weights = get_day_weights(cal)
    collected_sum = sum(
        _positive_float(details.get("domestic_mid")) or 0
        for details in regular_daily_details.values()
    )
    collected_share = sum(
        day_weights.get(day, 0)
        for day in regular_daily_details
    )
    if collected_sum <= 0 or collected_share <= 0:
        return {}
    weekend_mid = collected_sum / collected_share
    return {
        day: weekend_mid * weight
        for day, weight in day_weights.items()
        if weight > 0
    }


def apply_snapshot_day_shape_prior(details, day_shape_prior):
    """Anchor partial pre-reservation reads to the seat-derived day shape."""
    prior_mid = _positive_float(day_shape_prior)
    if not details or not prior_mid:
        return details

    coverage = _coverage_value(
        details.get("effective_coverage_ratio", details.get("coverage_ratio")),
        default=0.0,
    )
    signal_weight = _clamp(
        coverage * SNAPSHOT_DAY_SHAPE_MAX_SIGNAL_WEIGHT,
        0.0,
        SNAPSHOT_DAY_SHAPE_MAX_SIGNAL_WEIGHT,
    )
    prior_weight = 1.0 - signal_weight
    if signal_weight >= 1.0:
        return details

    adjusted = dict(details)
    adjusted["day_shape_prior_domestic_mid"] = prior_mid
    adjusted["snapshot_day_shape_signal_weight"] = round(signal_weight, 4)
    adjusted["snapshot_day_shape_prior_weight"] = round(prior_weight, 4)

    prior_bounds = {
        "domestic_mid": prior_mid,
        "domestic_low": prior_mid * 0.85,
        "domestic_high": prior_mid * 1.15,
    }
    for key, prior_value in prior_bounds.items():
        adjusted[f"pre_day_shape_{key}"] = adjusted.get(key)
        adjusted[key] = (
            (adjusted.get(key, 0) * signal_weight) +
            (prior_value * prior_weight)
        )
    return adjusted


def build_snapshot_future_layer(snapshot_data, regular_daily_details, cal,
                                expected_amc_theatres, expected_timezone_counts=None,
                                theatre_timezone_map=None,
                                national_theatre_count=None):
    """Use snapshots only for opening-weekend days without seat-count actuals."""
    if not snapshot_data:
        return None

    all_snapshot_details = {}
    ignored_days = []
    for date_str, rows in sorted(snapshot_data.items()):
        if not rows:
            continue
        day_name = _snapshot_day_name(date_str, rows)
        if day_name not in OPENING_WEEKEND_DAYS:
            continue
        details = estimate_snapshot_day(
            rows,
            date_str,
            cal,
            expected_amc_theatres,
            expected_timezone_counts=expected_timezone_counts,
            theatre_timezone_map=theatre_timezone_map,
            national_theatre_count=national_theatre_count,
        )
        if details:
            all_snapshot_details[day_name] = details

    same_week_scale, same_week_anchors = same_week_snapshot_scale(
        all_snapshot_details,
        regular_daily_details,
    )

    snapshot_details = {}
    day_shape_priors = regular_day_shape_priors(regular_daily_details, cal)
    for day_name, details in all_snapshot_details.items():
        if day_name in regular_daily_details:
            ignored_days.append(day_name)
            continue
        scaled_details = apply_same_week_snapshot_scale(
            details,
            same_week_scale,
        )
        snapshot_details[day_name] = apply_snapshot_day_shape_prior(
            scaled_details,
            day_shape_priors.get(day_name),
        )

    if not snapshot_details:
        return {
            "snapshot_daily_details": {},
            "snapshot_ignored_days": sorted(set(ignored_days)),
            "snapshot_same_week_scale": round(same_week_scale, 4),
            "snapshot_same_week_anchors": same_week_anchors,
        }

    day_weights = get_day_weights(cal)
    combined_days = {}
    coverage = {}
    for day, details in regular_daily_details.items():
        combined_days[day] = details.get("domestic_mid", 0)
        if details.get("coverage_ratio") is not None:
            coverage[day] = details.get(
                "effective_coverage_ratio",
                details["coverage_ratio"],
            )
    for day, details in snapshot_details.items():
        combined_days[day] = details.get("domestic_mid", 0)
        if details.get("coverage_ratio") is not None:
            coverage[day] = details.get(
                "effective_coverage_ratio",
                details["coverage_ratio"],
            )

    collected_sum = sum(combined_days.values())
    collected_share = sum(day_weights.get(day, 0) for day in combined_days)
    if collected_share >= 0.99:
        mid = collected_sum
    elif collected_share > 0:
        mid = collected_sum / collected_share
    else:
        mid = collected_sum

    n_days = len(combined_days)
    avg_coverage = _coverage_average(coverage)
    low_factor, high_factor = confidence_interval_factors(
        n_days,
        coverage_ratio=avg_coverage,
    )
    snapshot_missing_share = sum(day_weights.get(day, 0) for day in snapshot_details)
    snapshot_coverage = _coverage_average({
        day: details.get("effective_coverage_ratio", details.get("coverage_ratio"))
        for day, details in snapshot_details.items()
    })
    model_weight = SNAPSHOT_LAYER_MAX_WEIGHT
    model_weight *= _coverage_value(snapshot_coverage)
    model_weight *= _clamp(snapshot_missing_share, 0.0, 1.0)

    return {
        "snapshot_daily_details": snapshot_details,
        "snapshot_ignored_days": sorted(set(ignored_days)),
        "snapshot_mid_m": mid / 1_000_000,
        "snapshot_low_m": (mid * low_factor) / 1_000_000,
        "snapshot_high_m": (mid * high_factor) / 1_000_000,
        "snapshot_model_weight": round(_clamp(model_weight, 0.0, SNAPSHOT_LAYER_MAX_WEIGHT), 4),
        "snapshot_coverage_ratio": round(snapshot_coverage, 3) if snapshot_coverage is not None else None,
        "snapshot_days": sorted(snapshot_details),
        "snapshot_same_week_scale": round(same_week_scale, 4),
        "snapshot_same_week_anchors": same_week_anchors,
    }


# ── Stage E: Polymarket Expected Value ───────────────────────────────────────

def extract_bracket_range(question):
    """Parse dollar ranges from Polymarket bracket questions."""
    q = question.lower()

    # Match "$100M" or "$100 million" patterns
    amounts = re.findall(r'\$(\d+(?:\.\d+)?)\s*[Mm]', question)
    if not amounts:
        # Try without M suffix (some use "million")
        amounts = re.findall(r'\$(\d+(?:\.\d+)?)\s*(?:million|mil)', q)
    if not amounts:
        # Try bare numbers after $
        amounts = re.findall(r'\$(\d+(?:\.\d+)?)', question)
        # Filter to likely millions (> 10)
        amounts = [a for a in amounts if float(a) >= 10]
    if not amounts:
        # Polymarket often writes brackets as "between 75m and 80m" without "$".
        amounts = re.findall(r'(?<![\w.])(\d+(?:\.\d+)?)\s*(?:m|million|mil)\b', q)
        amounts = [a for a in amounts if float(a) >= 10]

    if len(amounts) >= 2:
        return float(amounts[0]), float(amounts[1])
    elif len(amounts) == 1:
        val = float(amounts[0])
        if any(w in q for w in ["over", "above", "more than", "higher than", "greater than", "exceed"]):
            return val, val + 30
        elif any(w in q for w in ["under", "below", "less than", "lower than"]):
            return max(0, val - 30), val
        else:
            return max(0, val - 10), val + 10
    return None, None


def polymarket_expected_value(markets_for_movie):
    """Stage E: compute expected value from Polymarket bracket markets."""
    brackets = []
    total_volume = 0

    for mkt in markets_for_movie:
        question = mkt.get("market_question", "") or mkt.get("question", "")
        prices_raw = mkt.get("outcome_prices", "")
        vol = float(mkt.get("total_volume", 0) or mkt.get("volume", 0) or 0)

        low, high = extract_bracket_range(question)
        if low is None:
            continue

        # Parse probability
        try:
            if prices_raw.startswith("["):
                prices = json.loads(prices_raw)
                p_yes = _clamp(float(prices[0]), 0.0, 1.0)
            else:
                p_yes = _clamp(float(prices_raw), 0.0, 1.0) if prices_raw else 0
        except (json.JSONDecodeError, ValueError, IndexError):
            continue

        midpoint = (low + high) / 2
        brackets.append({
            "low": low, "high": high, "midpoint": midpoint,
            "p_yes": p_yes, "question": question,
        })
        total_volume += vol

    if not brackets:
        return None

    raw_probability_sum = sum(b["p_yes"] for b in brackets)
    if raw_probability_sum > 0:
        for bracket in brackets:
            bracket["p_norm"] = bracket["p_yes"] / raw_probability_sum
    else:
        uniform = 1.0 / len(brackets)
        for bracket in brackets:
            bracket["p_norm"] = uniform

    # Expected value from no-vig normalized interval probabilities.
    ev = sum(b["midpoint"] * b["p_norm"] for b in brackets)

    # Weighted standard deviation
    if ev > 0:
        variance = sum(b["p_norm"] * (b["midpoint"] - ev) ** 2 for b in brackets)
        std = sqrt(variance) if variance > 0 else ev * 0.2
    else:
        std = 0

    # Highest probability bracket
    best_bracket = max(brackets, key=lambda b: b["p_norm"])

    return {
        "ev": ev,
        "std": std,
        "low": max(0, ev - std),
        "high": ev + std,
        "brackets": brackets,
        "best_bracket": best_bracket,
        "total_volume": total_volume,
        "raw_probability_sum": raw_probability_sum,
    }


# ── Calibration ──────────────────────────────────────────────────────────────

def record_actual(cal, movie, predicted_mid, predicted_low, predicted_high,
                  seat_raw, poly_ev, actual, n_theatres, days_collected,
                  daily_theatre_counts=None, daily_coverage_ratios=None,
                  daily_predictions=None, raw_daily_predictions=None,
                  snapshot_daily_predictions=None,
                  snapshot_daily_coverage_ratios=None,
                  weekend_of=None, reference_amc_theatres=None,
                  model_cohort_key=None):
    """Record a predicted-vs-actual result and update calibration factors."""
    if isinstance(days_collected, (list, tuple, set, dict)):
        n_days = len(days_collected)
    else:
        n_days = int(_positive_float(days_collected) or 0)
    entry = {
        "movie": movie,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "predicted_mid": round(predicted_mid, 1),
        "predicted_low": round(predicted_low, 1),
        "predicted_high": round(predicted_high, 1),
        "seat_raw_estimate": round(seat_raw, 1) if seat_raw else None,
        "polymarket_ev": round(poly_ev, 1) if poly_ev else None,
        "actual": actual,
        "n_theatres": n_theatres,
        "days_collected": n_days,
        "n_days": n_days,
        "model_version": MODEL_VERSION,
    }
    cohort_key = normalize_model_cohort_key(model_cohort_key)
    if cohort_key:
        entry["model_cohort_key"] = cohort_key
    if weekend_of:
        entry["weekend_of"] = weekend_of
    reference = remember_reference_amc_theatres(
        cal,
        reference_amc_theatres,
        model_cohort_key=cohort_key,
    )
    if reference:
        entry["reference_amc_theatres"] = reference
    if daily_predictions:
        entry["daily_predictions"] = {
            k: round(v, 2) for k, v in daily_predictions.items()
        }
    if raw_daily_predictions:
        entry["raw_daily_predictions"] = {
            k: round(v, 2) for k, v in raw_daily_predictions.items()
        }
    if snapshot_daily_predictions:
        entry["snapshot_daily_predictions"] = {
            k: round(v, 2) for k, v in snapshot_daily_predictions.items()
            if v is not None
        }
    if snapshot_daily_coverage_ratios:
        entry["snapshot_daily_coverage_ratios"] = {
            k: round(min(1.0, max(0.0, float(v))), 3)
            for k, v in snapshot_daily_coverage_ratios.items()
            if v is not None
        }
    if daily_theatre_counts:
        entry["daily_theatre_counts"] = daily_theatre_counts
    if daily_coverage_ratios:
        entry["daily_coverage_ratios"] = daily_coverage_ratios
        vals = [v for v in daily_coverage_ratios.values() if v is not None]
        if vals:
            entry["coverage_ratio"] = round(sum(vals) / len(vals), 3)
        excluded_days = [
            day for day, ratio in daily_coverage_ratios.items()
            if ratio < MIN_DAILY_CALIBRATION_COVERAGE
        ]
        if excluded_days:
            entry["calibration_excluded_days"] = sorted(excluded_days)
    cal["history"].append(entry)

    # Update scale factor using the same bounded logic as calibrate.py.
    history = cal["history"]
    if history:
        cal["calibration_factors"]["overall_scale_factor"] = recalibrate_scale_factor(
            history,
            default=1.0,
        )
        cal["calibration_factors"]["snapshot_to_day_scale_factors"] = (
            recalibrate_snapshot_day_scale_factors(history)
        )

    # Refine AMC market share from seat-based estimates
    share_estimates = []
    for h in history:
        if h.get("seat_raw_estimate") and h.get("actual") and h["actual"] > 0:
            implied = h["seat_raw_estimate"] / h["actual"]
            if 0.15 < implied < 0.40:
                share_estimates.append(implied)
    if share_estimates:
        cal["calibration_factors"]["amc_market_share"] = round(
            statistics.median(share_estimates), 4
        )

    cal["calibration_factors"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_calibration(cal)


def snapshot_calibration_fields_from_prediction(pred):
    """Extract raw snapshot day estimates for calibration history."""
    snapshot_predictions = {}
    snapshot_coverage = {}
    for day_name, details in pred.get("snapshot_daily_details", {}).items():
        mid = _positive_float(
            details.get("raw_domestic_mid", details.get("domestic_mid"))
        )
        if not mid:
            continue
        snapshot_predictions[day_name] = mid / 1_000_000
        coverage = details.get("effective_coverage_ratio", details.get("coverage_ratio"))
        cov = _positive_float(coverage)
        if cov is not None:
            snapshot_coverage[day_name] = round(min(1.0, cov), 3)
    return snapshot_predictions, snapshot_coverage


# ── Main Prediction Pipeline ─────────────────────────────────────────────────

def predict_movie(movie, seat_data, poly_data, cal, verbose=False,
                  national_theatre_count=None, snapshot_data=None):
    """Run full prediction pipeline for a single movie."""
    # Identify opening weekend dates. The scraper may continue collecting
    # Mon-Wed rows for calibration research, but Polymarket brackets settle on
    # the opening weekend only, so prediction totals must stay Thu-Sun.
    all_dates = sorted(seat_data.keys())
    if not all_dates:
        return None
    opening_dates = []
    ignored_dates = {}
    for date_str in all_dates:
        rows = seat_data[date_str]
        csv_day = rows[0].get("day_of_week", "") if rows else ""
        day_name = csv_day if csv_day else datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        if day_name in OPENING_WEEKEND_DAYS:
            opening_dates.append(date_str)
        else:
            ignored_dates[date_str] = day_name

    if not opening_dates:
        return None

    model_cohorts = active_model_cohorts()
    model_cohort_key = normalize_model_cohort_key(model_cohorts)
    theatre_timezone_map, expected_timezone_counts = load_theatre_timezone_reference(
        model_cohorts=model_cohorts,
    )

    # Group by day of week
    daily_estimates = {}
    daily_details = {}
    observed_max_theatres = max(
        (
            len({
                row.get("theatre_name", "")
                for row in rows
                if row.get("theatre_name", "")
            })
            for date_str, rows in seat_data.items()
            if date_str in opening_dates
        ),
        default=0,
    )
    expected_amc_theatres = reference_amc_theatre_count(
        cal,
        fallback=observed_max_theatres,
        model_cohort_key=model_cohort_key,
    )
    movie_metadata = metadata_for_movie(movie, load_movie_metadata())

    for date_str in opening_dates:
        rows = seat_data[date_str]
        # Use day_of_week from CSV if available, else compute from date
        csv_day = rows[0].get("day_of_week", "") if rows else ""
        day_name = csv_day if csv_day else datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")

        # Group by (theatre, format): collect all showtime rows per pair.
        # Each row is one showtime — revenue = sum across all captured showings.
        # Use latest run_id to pick the freshest occupancy reading per showtime.
        rows_by_theatre_fmt_show = {}
        for row in rows:
            t_id = row.get("theatre_name", "")
            fmt = (row.get("auditorium_type", "") or row.get("auditorium_name", "") or "Standard")
            showtime = row.get("showtime", "")
            showtime_identity = ""
            if use_url_showtime_identity():
                showtime_identity = row.get("amc_seat_map_url", "").strip()
            key = f"{t_id}|{showtime_identity or f'{fmt}|{showtime}'}"
            sort_key = row.get("run_id", "") or row.get("check_time", "")
            prev = rows_by_theatre_fmt_show.get(key)
            if not prev or sort_key > prev.get("_sort_key", ""):
                rows_by_theatre_fmt_show[key] = {**row, "_sort_key": sort_key}

        # Stage A: per-showtime revenue (one row = one captured showtime).
        # Aggregate per theatre, then scale partial-day samples to a full-day
        # estimate via the calibrated daypart multiplier.
        per_showtime_results = []
        no_data_count = 0
        captured_by_theatre = {}        # {theatre: [per_showtime_result, ...]}
        showtime_hours_by_theatre = {}
        showtime_window_tagged_theatre_names = set()
        full_day_window_theatre_names = set()
        for row in rows_by_theatre_fmt_show.values():
            result = estimate_theatre_daily_revenue(row, cal)
            if result:
                per_showtime_results.append(result)
                t_name = result["theatre_name"]
                captured_by_theatre.setdefault(t_name, []).append(result)
                parsed_hour = _parse_showtime_hour(row.get("showtime", ""))
                if parsed_hour is not None:
                    showtime_hours_by_theatre.setdefault(t_name, []).append(parsed_hour)
                if _row_has_full_day_showtime_window(row):
                    showtime_window_tagged_theatre_names.add(t_name)
            else:
                no_data_count += 1

        if not per_showtime_results:
            continue

        showings_by_theatre = {
            t_name: len(captured_rows)
            for t_name, captured_rows in captured_by_theatre.items()
        }
        avg_showings = (sum(showings_by_theatre.values()) / len(showings_by_theatre)
                        if showings_by_theatre else 0)
        showtime_hours = [
            hour
            for theatre_hours in showtime_hours_by_theatre.values()
            for hour in theatre_hours
        ]
        earliest_showtime_hour = min(showtime_hours) if showtime_hours else None
        full_day_window_theatre_names.update(
            t_name
            for t_name, theatre_hours in showtime_hours_by_theatre.items()
            if theatre_hours
            and min(theatre_hours) <= WEEKEND_FULL_DAY_LATEST_EARLY_HOUR
        )
        full_day_window_coverage_ratio = (
            len(full_day_window_theatre_names) / len(captured_by_theatre)
            if captured_by_theatre else 0.0
        )
        showtime_window_tagged_coverage_ratio = (
            len(showtime_window_tagged_theatre_names) / len(captured_by_theatre)
            if captured_by_theatre else 0.0
        )

        # Per-theatre full-day revenue:
        #   captured_revenue  = sum of per-showtime revenues across captured
        #                       evening shows at this theatre
        #   theatre_day_rev   = captured_revenue × evening_to_daily_multiplier
        #
        # The multiplier defaults to 1.7 for Fri/Sat/Sun (we capture ~6 of
        # ~10 daily showings; matinees fill at roughly 60% of evening
        # occupancy) and 1.0 for Thursday (preview-only night, no matinees
        # exist for this movie that day, so what we scrape IS the full day).
        # Calibration EMA can tune this per day from actuals over time.
        base_ev_to_daily = get_evening_to_daily_multiplier(cal, day_name=day_name)
        ev_to_daily = daypart_adjusted_evening_to_daily(
            base_ev_to_daily,
            day_name,
            avg_showings,
            target_metadata=movie_metadata,
            earliest_showtime_hour=earliest_showtime_hour,
            full_day_window_coverage_ratio=full_day_window_coverage_ratio,
        )
        theatre_results = []
        for t_name, captured_rows in captured_by_theatre.items():
            captured_rev = sum(r["revenue"] for r in captured_rows)
            theatre_day_rev = captured_rev * ev_to_daily
            theatre_results.append({
                "revenue": theatre_day_rev,
                "theatre_name": t_name,
                "n_captured_showings": len(captured_rows),
                "captured_revenue": captured_rev,
                "evening_to_daily": ev_to_daily,
                "base_evening_to_daily": base_ev_to_daily,
            })

        # Stage B: sum all AMC
        sampled_amc_total, amc_stats = sum_amc_theatres(theatre_results)
        n_amc_theatres = amc_stats.get("n_theatres", 0)
        tz_profile = timezone_coverage_profile(
            rows,
            expected_timezone_counts=expected_timezone_counts,
            theatre_timezone_map=theatre_timezone_map,
        )
        amc_total, sample_norm_factor = normalize_amc_sample(
            sampled_amc_total,
            n_amc_theatres,
            expected_amc_theatres,
            representativeness=tz_profile["coverage_factor"],
        )
        coverage_ratio = (
            min(1.0, n_amc_theatres / expected_amc_theatres)
            if expected_amc_theatres else None
        )
        effective_coverage_ratio = coverage_ratio
        if coverage_ratio is not None and tz_profile["missing_timezones"]:
            effective_coverage_ratio = coverage_ratio * tz_profile["coverage_factor"]

        # Stage C: AMC → domestic
        # If we have a national theatre count, use it to cross-check our scaling.
        # Per-theatre revenue from our sample × national theatre count gives an
        # independent estimate — we blend it 50/50 with the market-share approach.
        domestic_mid, domestic_low, domestic_high = amc_to_domestic(amc_total, cal)
        if national_theatre_count and n_amc_theatres > 0:
            mean_rev = amc_stats.get("mean_revenue", 0)
            nat_est = mean_rev * national_theatre_count
            # Blend: 60% market-share, 40% national-count extrapolation
            domestic_mid  = domestic_mid  * 0.6 + nat_est * 0.4
            domestic_low  = domestic_low  * 0.6 + nat_est * 0.4 * 0.85
            domestic_high = domestic_high * 0.6 + nat_est * 0.4 * 1.15

        daily_estimates[day_name] = domestic_mid
        daily_details[day_name] = {
            "date": date_str,
            "amc_total": amc_total,
            "sampled_amc_total": sampled_amc_total,
            "sample_normalization_factor": sample_norm_factor,
            "domestic_mid": domestic_mid,
            "domestic_low": domestic_low,
            "domestic_high": domestic_high,
            "n_theatres": n_amc_theatres,
            "expected_theatres": expected_amc_theatres,
            "coverage_ratio": coverage_ratio,
            "effective_coverage_ratio": effective_coverage_ratio,
            "observed_timezones": tz_profile["observed_timezones"],
            "expected_timezones": tz_profile["expected_timezones"],
            "missing_timezones": tz_profile["missing_timezones"],
            "timezone_coverage_factor": tz_profile["coverage_factor"],
            "n_no_data": no_data_count,
            "avg_showings_per_cinema": round(avg_showings, 1),
            "earliest_showtime_hour": earliest_showtime_hour,
            "full_day_window_coverage_ratio": full_day_window_coverage_ratio,
            "showtime_window_tagged_coverage_ratio": showtime_window_tagged_coverage_ratio,
            "evening_to_daily": ev_to_daily,
            "base_evening_to_daily": base_ev_to_daily,
            "daypart_adjusted_evening_to_daily": abs(ev_to_daily - base_ev_to_daily) > 0.001,
            "daypart_adjustment_factor": (
                ev_to_daily / base_ev_to_daily if base_ev_to_daily else 1.0
            ),
            "mean_revenue": amc_stats.get("mean_revenue", 0),
            "median_revenue": amc_stats.get("median_revenue", 0),
            "theatre_results": theatre_results if verbose else [],
        }

    if not daily_estimates:
        return None

    daily_raw_coverage_ratios = {
        day: details["coverage_ratio"]
        for day, details in daily_details.items()
        if details.get("coverage_ratio") is not None
    }
    daily_coverage_ratios = {
        day: details.get("effective_coverage_ratio", details["coverage_ratio"])
        for day, details in daily_details.items()
        if details.get("coverage_ratio") is not None
    }
    coverage_ratio = _coverage_average(daily_coverage_ratios)
    weighted_coverage_ratio = weighted_weekend_coverage_ratio(
        daily_coverage_ratios,
        cal,
    )
    raw_coverage_ratio = _coverage_average(daily_raw_coverage_ratios)

    # Stage D: day-by-day calibration → weekend sum.
    seat_mid, seat_low, seat_high, calibrated_daily = days_to_weekend(
        daily_estimates,
        cal,
        daily_coverage_ratios=daily_coverage_ratios,
    )
    for day_name, calibrated in calibrated_daily.items():
        details = daily_details.get(day_name)
        if not details:
            continue
        raw_mid = details["domestic_mid"]
        raw_low = details["domestic_low"]
        raw_high = details["domestic_high"]
        day_scale = calibrated["scale"]
        details["raw_domestic_mid"] = raw_mid
        details["raw_domestic_low"] = raw_low
        details["raw_domestic_high"] = raw_high
        details["day_scale"] = day_scale
        details["domestic_mid"] = calibrated["mid"]
        details["domestic_low"] = raw_low * day_scale
        details["domestic_high"] = raw_high * day_scale

    # Convert to millions for display
    seat_mid_m = seat_mid / 1_000_000
    seat_low_m = seat_low / 1_000_000
    seat_high_m = seat_high / 1_000_000

    snapshot_layer = build_snapshot_future_layer(
        snapshot_data,
        daily_details,
        cal,
        expected_amc_theatres,
        expected_timezone_counts=expected_timezone_counts,
        theatre_timezone_map=theatre_timezone_map,
        national_theatre_count=national_theatre_count,
    )
    data_profile = missing_data_profile(
        daily_details,
        cal,
        snapshot_layer=snapshot_layer,
    )

    # Stage E: Polymarket
    poly_result = None
    if poly_data:
        poly_result = polymarket_expected_value(poly_data)

    # Stage F: model forecast. Polymarket is retained as market context only;
    # it must never pull the seat/comp forecast up or down.
    # Count unique theatres across all days (a theatre that appears on both
    # Thursday and Friday should count as 1, not 2).
    all_theatre_names: set[str] = set()
    for date_str in opening_dates:
        rows = seat_data[date_str]
        for row in rows:
            t_name = row.get("theatre_name", "")
            if t_name:
                all_theatre_names.add(t_name)
    n_theatres_total = len(all_theatre_names) if all_theatre_names else sum(
        d["n_theatres"] for d in daily_details.values()
    )
    n_days = len(daily_estimates)

    blended_m = seat_mid_m
    blend_low_m = seat_low_m
    blend_high_m = seat_high_m
    w_seat, w_poly = 1.0, 0.0

    avg_showings_total = (
        sum(d.get("avg_showings_per_cinema", 0) for d in daily_details.values()) /
        len(daily_details) if daily_details else 0
    )

    result = {
        "movie": movie,
        "model_version": MODEL_VERSION,
        "model_cohorts": sorted(model_cohorts),
        "model_cohort_key": model_cohort_key,
        "seat_mid_m": seat_mid_m,
        "seat_low_m": seat_low_m,
        "seat_high_m": seat_high_m,
        "poly_result": poly_result,
        "blended_m": blended_m,
        "blend_low_m": blend_low_m,
        "blend_high_m": blend_high_m,
        "w_seat": w_seat,
        "w_poly": w_poly,
        "daily_details": daily_details,
        "daily_estimates": {
            day: details["domestic_mid"]
            for day, details in daily_details.items()
        },
        "raw_daily_estimates": daily_estimates,
        "snapshot_daily_details": (
            snapshot_layer.get("snapshot_daily_details", {})
            if snapshot_layer else {}
        ),
        "snapshot_ignored_days": (
            snapshot_layer.get("snapshot_ignored_days", [])
            if snapshot_layer else []
        ),
        "snapshot_mid_m": (
            snapshot_layer.get("snapshot_mid_m")
            if snapshot_layer and snapshot_layer.get("snapshot_mid_m") is not None else None
        ),
        "snapshot_low_m": (
            snapshot_layer.get("snapshot_low_m")
            if snapshot_layer and snapshot_layer.get("snapshot_low_m") is not None else None
        ),
        "snapshot_high_m": (
            snapshot_layer.get("snapshot_high_m")
            if snapshot_layer and snapshot_layer.get("snapshot_high_m") is not None else None
        ),
        "snapshot_model_weight": (
            snapshot_layer.get("snapshot_model_weight", 0.0)
            if snapshot_layer else 0.0
        ),
        "snapshot_coverage_ratio": (
            snapshot_layer.get("snapshot_coverage_ratio")
            if snapshot_layer else None
        ),
        "snapshot_days": (
            snapshot_layer.get("snapshot_days", [])
            if snapshot_layer else []
        ),
        "snapshot_same_week_scale": (
            snapshot_layer.get("snapshot_same_week_scale")
            if snapshot_layer else None
        ),
        "snapshot_same_week_anchors": (
            snapshot_layer.get("snapshot_same_week_anchors", [])
            if snapshot_layer else []
        ),
        "n_days": n_days,
        "n_theatres_total": n_theatres_total,
        "expected_amc_theatres": expected_amc_theatres,
        "reference_amc_theatres": expected_amc_theatres,
        "ignored_post_weekend_dates": ignored_dates,
        "coverage_ratio": round(coverage_ratio, 3) if coverage_ratio is not None else None,
        "seat_observed_day_share": data_profile["observed_day_share"],
        "seat_missing_day_share": data_profile["missing_day_share"],
        "seat_weighted_coverage_ratio": weighted_coverage_ratio,
        "missing_data_profile": data_profile,
        "raw_coverage_ratio": (
            round(raw_coverage_ratio, 3)
            if raw_coverage_ratio is not None else None
        ),
        "seat_data_quality": round(
            seat_data_quality(
                n_theatres_total,
                n_days,
                coverage_ratio=weighted_coverage_ratio,
            ),
            3,
        ),
        "seat_confidence_low_factor": confidence_interval_factors(
            n_days,
            coverage_ratio=weighted_coverage_ratio,
        )[0],
        "seat_confidence_high_factor": confidence_interval_factors(
            n_days,
            coverage_ratio=weighted_coverage_ratio,
        )[1],
        "national_theatre_count": national_theatre_count,
        "avg_showings_per_cinema": round(avg_showings_total, 1),
        "amc_total_weekend": sum(d.get("amc_total", 0) for d in daily_details.values()),
    }
    attach_comp_model_prediction(result, cal)
    select_regression_prediction(result, cal)
    return result


# ── Output ───────────────────────────────────────────────────────────────────

def fmt_m(val):
    """Format millions as $XXX.XM or $X.XM."""
    if val >= 1:
        return f"${val:,.1f}M"
    elif val > 0:
        return f"${val * 1000:,.0f}K"
    return "$0"


def attach_comp_model_prediction(pred, cal, metadata=None, comps=None):
    """Attach the automated seat+historical-comp model to a prediction.

    This is intentionally additive: if metadata or comps are missing, the
    seat-only and Polymarket paths continue unchanged.
    """
    metadata = metadata if metadata is not None else load_movie_metadata()
    comps = comps if comps is not None else load_historical_comps()
    target = metadata_for_movie(pred.get("movie", ""), metadata)
    if not target or not comps:
        return None

    try:
        day_weights = get_day_weights(cal)
        baseline_thursday_share = float(day_weights.get("Thursday", 0) or 0)
        estimate = estimate_from_prediction(
            pred,
            target,
            comps,
            baseline_thursday_share=baseline_thursday_share,
        )
    except (KeyError, TypeError, ValueError):
        return None

    local_share = learned_local_thursday_share(
        cal,
        exclude_movie=pred.get("movie", ""),
        target_metadata=target,
        metadata=metadata,
    )
    external_thursday_share = (
        estimate.audience_adjusted_thursday_share
        or estimate.weighted_thursday_share
    )
    thursday_share = external_thursday_share
    local_weight = 0.0
    if local_share:
        local_weight = min(
            MAX_LOCAL_THURSDAY_SHARE_WEIGHT,
            local_share["n"] / (local_share["n"] + LOCAL_THURSDAY_SHARE_PRIOR_SAMPLES),
        )
        thursday_share = (
            external_thursday_share * (1 - local_weight)
            + local_share["share"] * local_weight
        )

    model = _seat_comp_model_from_available_days(
        pred,
        estimate,
        thursday_share=thursday_share,
        audience_factor=estimate.audience_regression_factor,
    )

    pred["seat_comp_mid_m"] = model["mid_m"]
    pred["seat_comp_low_m"] = model["low_m"]
    pred["seat_comp_high_m"] = model["high_m"]
    pred["seat_comp_basis"] = model["basis"]
    pred["seat_comp_evidence_m"] = model["evidence_m"]
    pred["seat_comp_evidence_share"] = model["evidence_share"]
    pred["seat_comp_thursday_gross_m"] = estimate.thursday_gross_m
    pred["seat_comp_thursday_share"] = thursday_share
    pred["seat_comp_external_thursday_share"] = external_thursday_share
    pred["seat_comp_raw_external_thursday_share"] = estimate.weighted_thursday_share
    if estimate.audience_regression_n:
        features = estimate.audience_regression_features or {}
        feature_parts = []
        if features.get("imdb_rating"):
            feature_parts.append(f"IMDb {features['imdb_rating']:.1f}")
        if features.get("rt_audience_score"):
            feature_parts.append(f"RT audience {features['rt_audience_score']:.0f}%")
        pred["seat_comp_audience_factor"] = estimate.audience_regression_factor
        pred["seat_comp_audience_regression_n"] = estimate.audience_regression_n
        pred["seat_comp_audience_regression_r2"] = estimate.audience_regression_r2
        pred["seat_comp_audience_features"] = ", ".join(feature_parts)
    if local_share:
        pred["seat_comp_local_thursday_share"] = local_share["share"]
        pred["seat_comp_local_thursday_n"] = local_share["n"]
        pred["seat_comp_local_thursday_weight"] = local_weight
    pred["seat_comp_daily_shares"] = estimate.daily_shares
    pred["seat_comp_daily_m"] = {
        day: model["mid_m"] * share
        for day, share in estimate.daily_shares.items()
    }
    pred["seat_comp_top_comps"] = [
        {
            "movie": comp.movie,
            "thursday_share": comp.thursday_share,
            "has_daily_breakdown": comp.has_daily_breakdown,
            "weight": estimate.weights.get(comp.movie, 0),
        }
        for comp in estimate.comps[:5]
    ]

    adjusted = coverage_adjusted_comp_model(pred, model, estimate)
    if adjusted:
        pred["seat_comp_prior_mid_m"] = adjusted["prior_mid_m"]
        pred["seat_comp_prior_low_m"] = adjusted["prior_low_m"]
        pred["seat_comp_prior_high_m"] = adjusted["prior_high_m"]
        pred["seat_comp_prior_weight"] = adjusted["prior_weight"]
        pred["seat_comp_observed_weight"] = adjusted["seat_weight"]
        pred["seat_comp_prior_disagreement_m"] = adjusted["disagreement_m"]
        pred["seat_comp_adjusted_mid_m"] = adjusted["mid_m"]
        pred["seat_comp_adjusted_low_m"] = adjusted["low_m"]
        pred["seat_comp_adjusted_high_m"] = adjusted["high_m"]
        pred["seat_comp_adjusted_basis"] = f"{model['basis']} + coverage prior"

    pred["comp_blended_m"] = pred.get("seat_comp_adjusted_mid_m", pred["seat_comp_mid_m"])
    pred["comp_blend_low_m"] = pred.get("seat_comp_adjusted_low_m", pred["seat_comp_low_m"])
    pred["comp_blend_high_m"] = pred.get("seat_comp_adjusted_high_m", pred["seat_comp_high_m"])
    pred["comp_w_model"] = 1.0
    pred["comp_w_poly"] = 0.0

    primary = seat_primary_ensemble(pred)
    if primary:
        pred["seat_primary_mid_m"] = primary["mid_m"]
        pred["seat_primary_low_m"] = primary["low_m"]
        pred["seat_primary_high_m"] = primary["high_m"]
        pred["seat_primary_w_direct"] = primary["w_direct"]
        pred["seat_primary_w_comp"] = primary["w_comp"]
        pred["seat_primary_disagreement_m"] = primary["disagreement_m"]
        pred["blended_m"] = primary["mid_m"]
        pred["blend_low_m"] = primary["low_m"]
        pred["blend_high_m"] = primary["high_m"]
        w_seat, w_poly = 1.0, 0.0
        pred["w_seat"] = w_seat
        pred["w_poly"] = w_poly
    select_regression_prediction(pred, cal)
    return estimate


def _movie_matches(a, b):
    a = (a or "").strip().lower()
    b = (b or "").strip().lower()
    if not a or not b:
        return False
    return a in b or b in a


def _metadata_matches_local_share(target_metadata, entry_metadata):
    if not target_metadata or not entry_metadata:
        return False
    return bool(
        target_metadata.audience_type
        and target_metadata.audience_type == entry_metadata.audience_type
    )


def learned_local_thursday_share(cal, exclude_movie="", target_metadata=None,
                                 metadata=None):
    """Estimate Thursday/weekend share from settled local seat predictions.

    Uses our own recorded Thursday seat-implied grosses divided by the settled
    actual opening weekend. The target movie is excluded to prevent replay
    leakage after actuals have been recorded.
    """
    all_values = []
    matched_values = []
    saw_entry_metadata = False
    for item in (cal or {}).get("history", []):
        entry_movie = item.get("movie", "")
        if _movie_matches(exclude_movie, entry_movie):
            continue
        entry_metadata = None
        if target_metadata is not None and metadata:
            entry_metadata = metadata_for_movie(entry_movie, metadata)
            if entry_metadata:
                saw_entry_metadata = True
        actual = item.get("actual_total") or item.get("actual")
        daily_predictions = item.get("daily_predictions") or {}
        thursday = daily_predictions.get("Thursday")
        if not thursday:
            raw_daily = item.get("raw_daily_predictions") or {}
            thursday = raw_daily.get("Thursday")
        try:
            actual = float(actual or 0)
            thursday = float(thursday or 0)
        except (TypeError, ValueError):
            continue
        if actual <= 0 or thursday <= 0:
            continue
        share = thursday / actual
        if 0.02 <= share <= 0.35:
            all_values.append(share)
            if _metadata_matches_local_share(target_metadata, entry_metadata):
                matched_values.append(share)

    values = matched_values if saw_entry_metadata else all_values
    if not values:
        return None
    return {
        "share": statistics.median(values),
        "n": len(values),
    }


def _weighted_quantile_pairs(values, quantile):
    if not values:
        return 0.0
    ordered = sorted(values, key=lambda item: item[0])
    total_weight = sum(weight for _, weight in ordered)
    if total_weight <= 0:
        return ordered[len(ordered) // 2][0]
    threshold = total_weight * quantile
    running = 0.0
    for value, weight in ordered:
        running += weight
        if running >= threshold:
            return value
    return ordered[-1][0]


def _seat_comp_model_from_available_days(pred, estimate, thursday_share=None, audience_factor=1.0):
    """Project weekend from the latest observed seat data plus comp shape.

    Public daily grosses report Friday as Friday+previews, so once Friday seat
    data exists this uses (Thursday + Friday) against the comp's reported
    Friday share. Saturday and Sunday are added as they become available.
    """
    details = pred.get("daily_details", {})
    if "Thursday" not in details:
        return {
            "mid_m": estimate.audience_adjusted_mid_m or estimate.mid_m,
            "low_m": estimate.low_m * audience_factor,
            "high_m": estimate.high_m * audience_factor,
            "basis": "Thursday",
            "evidence_m": estimate.thursday_gross_m,
            "evidence_share": thursday_share or estimate.weighted_thursday_share,
        }

    evidence_m = details["Thursday"]["domestic_mid"] / 1_000_000
    basis = "Thursday"
    share_values = [
        (comp.thursday_share, estimate.weights.get(comp.movie, 0))
        for comp in estimate.comps
        if comp.thursday_share > 0
    ]
    evidence_share = thursday_share or estimate.weighted_thursday_share

    if "Friday" in details and estimate.daily_shares.get("Friday"):
        evidence_m = (
            details["Thursday"]["domestic_mid"]
            + details["Friday"]["domestic_mid"]
        ) / 1_000_000
        basis = "reported Friday"
        share_values = [
            (comp.daily_shares["Friday"], estimate.weights.get(comp.movie, 0))
            for comp in estimate.comps
            if comp.daily_shares.get("Friday")
        ]
        evidence_share = estimate.daily_shares["Friday"]

    if "Saturday" in details and estimate.daily_shares.get("Saturday"):
        evidence_m = (
            details["Thursday"]["domestic_mid"]
            + details.get("Friday", {}).get("domestic_mid", 0)
            + details["Saturday"]["domestic_mid"]
        ) / 1_000_000
        basis = "reported Friday+Saturday"
        share_values = [
            (
                comp.daily_shares["Friday"] + comp.daily_shares["Saturday"],
                estimate.weights.get(comp.movie, 0),
            )
            for comp in estimate.comps
            if comp.daily_shares.get("Friday") and comp.daily_shares.get("Saturday")
        ]
        evidence_share = estimate.daily_shares["Friday"] + estimate.daily_shares["Saturday"]

    if "Sunday" in details and estimate.daily_shares.get("Sunday"):
        evidence_m = (
            details["Thursday"]["domestic_mid"]
            + details.get("Friday", {}).get("domestic_mid", 0)
            + details.get("Saturday", {}).get("domestic_mid", 0)
            + details["Sunday"]["domestic_mid"]
        ) / 1_000_000
        basis = "reported full weekend"
        share_values = [
            (sum(comp.daily_shares.values()), estimate.weights.get(comp.movie, 0))
            for comp in estimate.comps
            if comp.has_daily_breakdown
        ]
        evidence_share = sum(estimate.daily_shares.values())

    if not share_values or evidence_share <= 0:
        return {
            "mid_m": estimate.mid_m,
            "low_m": estimate.low_m,
            "high_m": estimate.high_m,
            "basis": "Thursday",
            "evidence_m": estimate.thursday_gross_m,
            "evidence_share": thursday_share or estimate.weighted_thursday_share,
        }

    mid_m = evidence_m / evidence_share
    low_share = _weighted_quantile_pairs(share_values, 0.75)
    high_share = _weighted_quantile_pairs(share_values, 0.25)
    low_m = (evidence_m / low_share) * audience_factor if low_share else mid_m
    high_m = (evidence_m / high_share) * audience_factor if high_share else mid_m
    return {
        "mid_m": mid_m,
        "low_m": min(low_m, high_m),
        "high_m": max(low_m, high_m),
        "basis": basis,
        "evidence_m": evidence_m,
        "evidence_share": evidence_share,
    }


def print_prediction(pred, verbose=False):
    """Pretty-print a movie prediction."""
    movie = pred["movie"]
    print(f"\n  {movie.upper()}")
    print(f"  {'─' * len(movie)}")

    # Seat-based
    days_str = ", ".join(
        day for day in OPENING_WEEKEND_DAYS
        if day in pred["daily_estimates"]
    )
    n_th = pred["n_theatres_total"]
    nat = pred.get("national_theatre_count")
    nat_str = f", {nat:,} national" if nat else ""
    ref = pred.get("expected_amc_theatres")
    quality = pred.get("seat_data_quality")
    model_quality_str = (
        f" (ref {ref}, quality {quality:.0%})"
        if ref and quality is not None else ""
    )
    shows_str = f", ~{pred.get('avg_showings_per_cinema', 0):.1f} showings/cinema" if pred.get('avg_showings_per_cinema') else ""
    print(f"  Model 1 seat-only: {fmt_m(pred['seat_mid_m']):>7}  "
          f"({fmt_m(pred['seat_low_m'])} - {fmt_m(pred['seat_high_m'])})")
    print(f"    Data: {n_th} AMC theatres{model_quality_str}{nat_str}, "
          f"{pred['n_days']} day(s) [{days_str}]{shows_str}")
    profile = pred.get("missing_data_profile") or {}
    missing_days = profile.get("missing_days") or []
    missing_tz_days = profile.get("missing_timezone_days") or []
    if missing_days or missing_tz_days:
        coverage = pred.get("seat_weighted_coverage_ratio")
        coverage_str = f"{coverage:.0%}" if coverage is not None else "n/a"
        print(f"    Completeness: {profile.get('observed_day_share', 0):.0%} day-share, "
              f"{coverage_str} weighted seat coverage"
              f"{'; missing ' + '/'.join(missing_days) if missing_days else ''}"
              f"{'; missing TZ on ' + '/'.join(missing_tz_days) if missing_tz_days else ''}")

    # Per-day breakdown
    for day, details in sorted(pred["daily_details"].items(),
                                key=lambda x: x[1]["date"]):
        amc_m = details["amc_total"] / 1_000_000
        sampled_amc_m = details.get("sampled_amc_total", details["amc_total"]) / 1_000_000
        sample_norm = details.get("sample_normalization_factor", 1.0)
        raw_dom_m = details.get("raw_domestic_mid", details["domestic_mid"]) / 1_000_000
        dom_m = details["domestic_mid"] / 1_000_000
        day_scale = details.get("day_scale", 1.0)
        spd = details.get("avg_showings_per_cinema", 0)
        coverage = details.get("coverage_ratio")
        effective_coverage = details.get("effective_coverage_ratio")
        coverage_str = (
            f", {coverage:.0%} sample coverage"
            if coverage is not None and coverage < 0.95 else ""
        )
        if (
            effective_coverage is not None
            and coverage is not None
            and effective_coverage < coverage - 0.005
        ):
            coverage_str += f", {effective_coverage:.0%} effective"
        missing_tz = details.get("missing_timezones") or []
        missing_tz_str = f", missing TZ {'/'.join(missing_tz)}" if missing_tz else ""
        day_model = fmt_m(dom_m)
        if abs(day_scale - 1.0) >= 0.005:
            day_model = f"{fmt_m(raw_dom_m)} × {day_scale:.3f} = {fmt_m(dom_m)}"
        daypart_str = ""
        if details.get("daypart_adjusted_evening_to_daily"):
            base_ev = details.get("base_evening_to_daily", details.get("evening_to_daily", 1.0))
            adj_ev = details.get("evening_to_daily", base_ev)
            daypart_str = f", daypart {base_ev:.1f}x→{adj_ev:.1f}x"
        full_day_window_coverage = details.get("full_day_window_coverage_ratio")
        full_day_window_str = ""
        if day in {"Saturday", "Sunday"} and full_day_window_coverage is not None:
            full_day_window_str = f", full-window theatres {full_day_window_coverage:.0%}"
        amc_input = f"AMC {fmt_m(amc_m)}"
        if abs(sample_norm - 1.0) >= 0.005:
            amc_input = (
                f"sample AMC {fmt_m(sampled_amc_m)} × {sample_norm:.3f} "
                f"= AMC {fmt_m(amc_m)}"
            )
        print(f"    {day} ({details['date']}): "
              f"{amc_input} → day {day_model} "
              f"[{details['n_theatres']} theatres{coverage_str}, {spd:.1f} showings/cinema"
              f"{full_day_window_str}"
              f"{daypart_str}"
              f"{missing_tz_str}"
              f"{', ' + str(details['n_no_data']) + ' no data' if details['n_no_data'] else ''}]")

    # Seat + historical comps
    if pred.get("seat_comp_mid_m") is not None:
        print(f"  Model 2 seat+comp: {fmt_m(pred['seat_comp_mid_m']):>7}  "
              f"({fmt_m(pred['seat_comp_low_m'])} - {fmt_m(pred['seat_comp_high_m'])})")
        print(f"    Basis: {pred['seat_comp_basis']} "
              f"{fmt_m(pred['seat_comp_evidence_m'])} / {pred['seat_comp_evidence_share']:.1%}")
        share_bits = [f"external comps {pred['seat_comp_external_thursday_share']:.1%}"]
        if pred.get("seat_comp_local_thursday_share") is not None:
            share_bits.append(
                f"local seat history {pred['seat_comp_local_thursday_share']:.1%} "
                f"n={pred['seat_comp_local_thursday_n']} "
                f"w={pred['seat_comp_local_thursday_weight']:.0%}"
            )
        print(f"    Seat-implied Thu: {fmt_m(pred['seat_comp_thursday_gross_m'])}; "
              f"Thu share used: {pred['seat_comp_thursday_share']:.1%} "
              f"({'; '.join(share_bits)})")
        if pred.get("seat_comp_audience_factor"):
            r2 = pred.get("seat_comp_audience_regression_r2")
            r2_str = f", R2 {r2:.2f}" if r2 is not None else ""
            print(f"    Audience regression: x{pred['seat_comp_audience_factor']:.3f} "
                  f"from {pred.get('seat_comp_audience_features', 'audience scores')} "
                  f"(n={pred['seat_comp_audience_regression_n']}{r2_str})")
        daily = pred.get("seat_comp_daily_m") or {}
        shares = pred.get("seat_comp_daily_shares") or {}
        if daily:
            parts = []
            for day in ("Friday", "Saturday", "Sunday"):
                if day in daily and day in shares:
                    parts.append(f"{day[:3]} {fmt_m(daily[day])} ({shares[day]:.0%})")
            if parts:
                print(f"    Comp F/S/S shape: {', '.join(parts)}")
        top_comps = pred.get("seat_comp_top_comps") or []
        if top_comps:
            print("    Top comps: " + ", ".join(comp["movie"] for comp in top_comps))

        if pred.get("seat_comp_adjusted_mid_m") is not None:
            print(f"  Coverage-adjusted: {fmt_m(pred['seat_comp_adjusted_mid_m']):>7}  "
                  f"({fmt_m(pred['seat_comp_adjusted_low_m'])} - "
                  f"{fmt_m(pred['seat_comp_adjusted_high_m'])})")
            print(f"    Weights: {pred['seat_comp_observed_weight']:.0%} observed seat+comp / "
                  f"{pred['seat_comp_prior_weight']:.0%} historical prior; "
                  f"prior {fmt_m(pred['seat_comp_prior_mid_m'])}")

        if pred.get("comp_blended_m") is not None:
            print(f"  Seat+comp model:  {fmt_m(pred['comp_blended_m']):>7}  "
                  f"({fmt_m(pred['comp_blend_low_m'])} - {fmt_m(pred['comp_blend_high_m'])})")

        if pred.get("seat_primary_mid_m") is not None:
            print(f"  Seat primary:     {fmt_m(pred['seat_primary_mid_m']):>7}  "
                  f"({fmt_m(pred['seat_primary_low_m'])} - {fmt_m(pred['seat_primary_high_m'])})")
            print(f"    Weights: {pred['seat_primary_w_direct']:.0%} direct seats / "
                  f"{pred['seat_primary_w_comp']:.0%} seat+comp")

    if pred.get("snapshot_mid_m") is not None:
        days = ", ".join(pred.get("snapshot_days") or [])
        print(f"  Snapshot layer:   {fmt_m(pred['snapshot_mid_m']):>7}  "
              f"({fmt_m(pred['snapshot_low_m'])} - {fmt_m(pred['snapshot_high_m'])})")
        print(f"    Future days: {days or '-'}; "
              f"coverage {pred.get('snapshot_coverage_ratio') or 0:.0%}; "
              f"model weight {pred.get('snapshot_model_weight', 0):.0%}")
        snapshot_scale = pred.get("snapshot_same_week_scale")
        if snapshot_scale and abs(snapshot_scale - 1.0) >= 0.01:
            anchors = ", ".join(
                anchor.get("day", "?")
                for anchor in pred.get("snapshot_same_week_anchors", [])
            )
            print(f"    Same-week calibration: x{snapshot_scale:.2f}"
                  f"{f' from {anchors}' if anchors else ''}")
        for day, details in sorted(
            pred.get("snapshot_daily_details", {}).items(),
            key=lambda item: item[1].get("date", ""),
        ):
            prior = details.get("day_shape_prior_domestic_mid")
            signal_weight = details.get("snapshot_day_shape_signal_weight")
            raw_mid = details.get(
                "pre_day_shape_domestic_mid",
                details.get("domestic_mid", 0),
            )
            if prior is None or signal_weight is None:
                continue
            print(f"    {day}: {fmt_m(details['domestic_mid'] / 1_000_000)} "
                  f"(snapshot {fmt_m(raw_mid / 1_000_000)}, "
                  f"day-shape prior {fmt_m(prior / 1_000_000)}, "
                  f"{signal_weight:.0%} snapshot signal)")

    # Polymarket
    poly = pred["poly_result"]
    if poly:
        print(f"  Polymarket ctx:{fmt_m(poly['ev']):>10}  "
              f"({fmt_m(poly['low'])} - {fmt_m(poly['high'])})")
        bb = poly["best_bracket"]
        vol_str = f"${poly['total_volume']:,.0f}" if poly['total_volume'] else "—"
        print(f"    Brackets: {len(poly['brackets'])}, vol {vol_str}")
        if poly.get("raw_probability_sum") is not None:
            print(f"    No-vig normalized from raw sum {poly['raw_probability_sum']:.1%}")
        print(f"    Highest-prob: ${bb['low']:.0f}M-${bb['high']:.0f}M "
              f"({bb.get('p_norm', bb['p_yes']):.0%})")

    # Headline model prediction
    regression_mid, regression_low, regression_high = regression_prediction_values(pred)
    print(f"  PREDICTION:    {fmt_m(regression_mid):>10}  "
          f"({fmt_m(regression_low)} - {fmt_m(regression_high)})")
    source = pred.get("regression_source")
    basis = pred.get("regression_basis")
    if source:
        label = source.replace("-", " ")
        basis_str = f", basis {basis}" if basis else ""
        print(f"    Source: {label}{basis_str}; Polymarket excluded from model")
    if pred.get("historical_residual_factor") is not None:
        print(f"    Historical residual: x{pred['historical_residual_factor']:.3f} "
              f"(raw x{pred['historical_residual_raw_factor']:.3f}, "
              f"strength {pred['historical_residual_strength']:.0%}, "
              f"n={pred['historical_residual_n']})")
    if poly:
        diff = regression_mid - poly["ev"]
        direction = "higher" if diff > 0 else "lower"
        print(f"    vs Polymarket: {'+' if diff > 0 else ''}{diff:,.1f}M {direction}")

    # Verbose: top theatres
    if verbose:
        print(f"\n  Top theatres by estimated revenue:")
        all_theatres = []
        for day, details in pred["daily_details"].items():
            for t in details.get("theatre_results", []):
                all_theatres.append({**t, "day": day})
        all_theatres.sort(key=lambda t: t["revenue"], reverse=True)
        for t in all_theatres[:20]:
            rev_k = t["revenue"] / 1000
            if "n_captured_showings" in t:
                captured_k = t.get("captured_revenue", 0) / 1000
                print(f"    {t['theatre_name'][:35]:<35} {t['day']:<10} "
                      f"${rev_k:,.0f}K daily  "
                      f"({t['n_captured_showings']} captured, ${captured_k:,.0f}K evening)")
            else:
                print(f"    {t['theatre_name'][:35]:<35} {t['day']:<10} "
                      f"{t.get('format', '?'):<15} "
                      f"occ:{t.get('observed_occ', 0):.0%}→{t.get('avg_occupancy', 0):.0%} "
                      f"${rev_k:,.0f}K  ({t.get('total_showings', 0)} shows)")


def print_history(cal):
    """Print historical predictions vs actuals."""
    history = cal.get("history", [])
    if not history:
        print("\nNo historical predictions yet. Use --actual to record results.")
        return

    print(f"\n{'='*70}")
    print(f"  Prediction History")
    print(f"{'='*70}")
    print(f"  {'Movie':<30} {'Predicted':>10} {'Actual':>10} {'Error':>8}")
    print(f"  {'─'*30} {'─'*10} {'─'*10} {'─'*8}")
    for h in history:
        predicted = h.get("predicted_mid", 0)
        actual = h.get("actual", h.get("actual_total"))
        pred_str = fmt_m(predicted)
        actual_str = fmt_m(actual) if actual else "—"
        if h.get("error_pct") is not None:
            err_str = f"{h['error_pct']:+.1f}%"
        elif actual and predicted > 0:
            err = (actual - predicted) / predicted
            err_str = f"{err:+.0%}"
        else:
            err_str = "—"
        print(f"  {h['movie'][:30]:<30} {pred_str:>10} {actual_str:>10} {err_str:>8}")

    factors = cal.get("calibration_factors", {})
    print(f"\n  Calibration: scale={factors.get('overall_scale_factor', 1.0):.4f}, "
          f"AMC share={factors.get('amc_market_share', DEFAULT_AMC_MARKET_SHARE):.2%}")


def print_usage():
    """Print CLI usage without running a prediction."""
    print("""Usage:
  python3 predict.py
  python3 predict.py --movie "Movie Name"
  python3 predict.py --actual "Movie Name" 125.3
  python3 predict.py --history
  python3 predict.py --verbose
  python3 predict.py --movie "Movie Name" --calibration-freeze 2026-04-24 --through-date 2026-04-23

Options:
  --movie NAME       Predict one movie from the loaded seat-count data
  --actual NAME GROSS_M
                     Record an actual opening-weekend result in millions
  --history          Show stored prediction-vs-actual history
  --calibration-freeze WEEKEND_OF
                     Use a pre-actual calibration snapshot for live replay
  --through-date YYYY-MM-DD
                     Ignore seat/Polymarket rows after this date for replay
  --include-expansion
                     Kept for compatibility; expansion is now on by default
  --verbose, -v      Include per-theatre prediction details
  --help, -h         Show this help text
""")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print_usage()
        return

    verbose = "--verbose" in args or "-v" in args
    calibration_freeze_weekend = None
    through_date = None
    if "--calibration-freeze" in args:
        idx = args.index("--calibration-freeze")
        if idx + 1 >= len(args) or args[idx + 1].startswith("--"):
            print_usage()
            return
        calibration_freeze_weekend = args[idx + 1]
        args = args[:idx] + args[idx + 2:]
    if "--through-date" in args:
        idx = args.index("--through-date")
        if idx + 1 >= len(args) or args[idx + 1].startswith("--"):
            print_usage()
            return
        through_date = args[idx + 1]
        try:
            datetime.strptime(through_date, "%Y-%m-%d")
        except ValueError:
            print_usage()
            return
        args = args[:idx] + args[idx + 2:]
    if "--include-expansion" in args:
        os.environ["THEATRE_MODEL_COHORTS"] = "core,expansion"
        args = [arg for arg in args if arg != "--include-expansion"]
    if calibration_freeze_weekend:
        try:
            cal = load_frozen_calibration(calibration_freeze_weekend)
        except FileNotFoundError:
            print(f"No calibration freeze found for {calibration_freeze_weekend}.")
            return
    else:
        cal = load_calibration()

    # --history
    if "--history" in args:
        print_history(cal)
        return

    # --actual "Movie Name" 125.3
    if "--actual" in args:
        if calibration_freeze_weekend:
            print("--actual cannot be combined with --calibration-freeze.")
            return
        if through_date:
            print("--actual cannot be combined with --through-date.")
            return
        idx = args.index("--actual")
        if idx + 2 >= len(args):
            print_usage()
            return
        if args[idx + 1].startswith("--") or args[idx + 2].startswith("--"):
            print_usage()
            return
        movie_name = args[idx + 1]
        try:
            actual_val = float(args[idx + 2])
        except ValueError:
            print_usage()
            return

        # Try to find the last prediction for this movie
        seat_data = load_seat_data()
        poly_data = load_polymarket_data()
        snapshot_data = load_pre_reservation_data()
        theatre_counts = load_theatre_counts()
        movie_match = None
        for m in seat_data:
            if movie_name.lower() in m.lower():
                movie_match = m
                break

        if not movie_match:
            print(f"No seat-count prediction found for {movie_name!r}; not recording actual.")
            return

        nat_count = national_theatre_count_for_movie(movie_match, theatre_counts)
        pred = predict_movie(movie_match, seat_data[movie_match],
                            poly_data.get(movie_match, []), cal,
                            national_theatre_count=nat_count,
                            snapshot_data=snapshot_data.get(movie_match, {}))
        if not pred:
            print(f"Could not build a prediction for {movie_match!r}; not recording actual.")
            return
        weekend_of = seat_data_weekend_of(seat_data[movie_match])
        freeze_path = save_calibration_freeze(
            DATA_DIR,
            weekend_of,
            cal,
            source="predict.py --actual",
            movies=[movie_match],
        )
        if freeze_path:
            print(f"Pre-actual calibration freeze: {os.path.relpath(freeze_path, os.getcwd())}")
        elif calibration_has_weekend(cal, weekend_of):
            print("Calibration already contains this weekend; not freezing contaminated state.")

        pred_mid, pred_low, pred_high = regression_prediction_values(pred)
        seat_raw = pred["amc_total_weekend"] / 1_000_000
        poly_ev = pred["poly_result"]["ev"] if pred["poly_result"] else 0
        n_th = pred["n_theatres_total"]
        days = list(pred["daily_estimates"].keys())
        daily_predictions = {
            day: details.get("domestic_mid", 0) / 1_000_000
            for day, details in pred.get("daily_details", {}).items()
        }
        raw_daily_predictions = {
            day: details.get(
                "raw_domestic_mid",
                details.get("domestic_mid", 0),
            ) / 1_000_000
            for day, details in pred.get("daily_details", {}).items()
        }
        daily_theatre_counts = {
            day: details.get("n_theatres", 0)
            for day, details in pred.get("daily_details", {}).items()
        }
        daily_coverage_ratios = {
            day: round(
                details.get("effective_coverage_ratio", details["coverage_ratio"]),
                3,
            )
            for day, details in pred.get("daily_details", {}).items()
            if details.get("coverage_ratio") is not None
        }
        snapshot_daily_predictions, snapshot_daily_coverage_ratios = (
            snapshot_calibration_fields_from_prediction(pred)
        )

        record_actual(cal, movie_match, pred_mid, pred_low, pred_high,
                     seat_raw, poly_ev, actual_val, n_th, days,
                     daily_theatre_counts=daily_theatre_counts,
                     daily_coverage_ratios=daily_coverage_ratios,
                     daily_predictions=daily_predictions,
                     raw_daily_predictions=raw_daily_predictions,
                     snapshot_daily_predictions=snapshot_daily_predictions,
                     snapshot_daily_coverage_ratios=snapshot_daily_coverage_ratios,
                     weekend_of=weekend_of,
                     reference_amc_theatres=pred.get("reference_amc_theatres"),
                     model_cohort_key=pred.get("model_cohort_key"))
        print(f"Recorded: {movie_match} actual = ${actual_val}M")
        print(f"Calibration updated → scale={cal['calibration_factors']['overall_scale_factor']:.4f}, "
              f"AMC share={cal['calibration_factors']['amc_market_share']:.2%}")
        return

    # Default: predict all movies. When replaying against a calibration freeze,
    # use the same opening-weekend key for seat and market data so future CSV
    # rows do not make older freezes point at the newest weekend.
    replay_weekend = calibration_freeze_weekend
    seat_data = load_seat_data(weekend_of=replay_weekend)
    seat_data = filter_seat_data_through(seat_data, through_date)
    poly_data = load_polymarket_data(weekend_of=replay_weekend, through_date=through_date)
    snapshot_data = load_pre_reservation_data(
        weekend_of=replay_weekend,
        through_date=through_date,
    )
    theatre_counts = load_theatre_counts()

    if not seat_data:
        print("No seat data found. Run: python3 scraper.py --collect-links, then python3 scraper.py")
        return

    # Filter to a specific movie if requested
    movie_filter = None
    if "--movie" in args:
        idx = args.index("--movie")
        if idx + 1 >= len(args) or args[idx + 1].startswith("--"):
            print_usage()
            return
        movie_filter = args[idx + 1].lower()
    movies_to_predict = [
        movie for movie in sorted(seat_data.keys())
        if not movie_filter or movie_filter in movie.lower()
    ]

    print(f"\n{'='*70}")
    print(f"  Opening Weekend Box Office Predictions")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    factors = cal["calibration_factors"]
    print(f"  Calibration: scale={factors.get('overall_scale_factor', 1.0):.3f}, "
          f"AMC share={factors.get('amc_market_share', DEFAULT_AMC_MARKET_SHARE):.1%}")
    if calibration_freeze_weekend:
        print(f"  Calibration freeze: {calibration_freeze_weekend}")
    if through_date:
        print(f"  Data through: {through_date}")
    print(f"  Theatre cohorts: {', '.join(sorted(active_model_cohorts()))}")
    if theatre_counts:
        relevant_counts = {
            movie: national_theatre_count_for_movie(movie, theatre_counts)
            for movie in movies_to_predict
        }
        relevant_counts = {m: c for m, c in relevant_counts.items() if c}
        if relevant_counts:
            print("  National theatre counts: "
                  f"{', '.join(f'{m}: {c:,}' for m, c in relevant_counts.items())}")
    print(f"{'='*70}")

    for movie in movies_to_predict:
        nat_count = national_theatre_count_for_movie(movie, theatre_counts)
        pred = predict_movie(movie, seat_data[movie],
                            poly_data.get(movie, []), cal, verbose=verbose,
                            national_theatre_count=nat_count,
                            snapshot_data=snapshot_data.get(movie, {}))
        if pred:
            print_prediction(pred, verbose=verbose)

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
