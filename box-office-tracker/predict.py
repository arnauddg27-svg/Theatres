#!/usr/bin/env python3
"""
Opening Weekend Box Office Predictor
=====================================
Predicts North American opening-weekend gross from AMC seat occupancy data
and Polymarket betting odds.

Pipeline:
  A. Per-theatre daily revenue (occupancy × seats × showings × price)
  B. Sum all AMC theatres
  C. AMC → total domestic (÷ market share)
  D. Partial days → full weekend (day weights)
  E. Polymarket expected value (bracket parsing)
  F. Blended prediction (seat + Polymarket weighted)

Usage:
    python3 predict.py                              # All movies this weekend
    python3 predict.py --movie "Project Hail Mary"  # Single movie
    python3 predict.py --actual "Movie Name" 125.3  # Record actual result
    python3 predict.py --history                    # Past predictions vs actuals
    python3 predict.py --verbose                    # Full calculation breakdown
"""

import json, csv, os, sys, re, statistics
from datetime import datetime, timedelta
from math import sqrt
from calibration_freeze import (calibration_has_weekend,
                                load_calibration_freeze,
                                save_calibration_freeze)
from model_calibration import (MIN_DAILY_CALIBRATION_COVERAGE,
                               sanitize_calibration, recalibrate_scale_factor)

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR            = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SEAT_CSV            = os.path.join(DATA_DIR, "seat-counts.csv")
POLY_CSV            = os.path.join(DATA_DIR, "polymarket-markets.csv")
CALIBRATION_JSON    = os.path.join(DATA_DIR, "calibration.json")
THEATRE_COUNTS_JSON = os.path.join(DATA_DIR, "theatre-counts.json")
THEATRES_JSON       = os.path.join(DATA_DIR, "theatres-all.json")
THEATRES_EXPANSION_JSON = os.path.join(DATA_DIR, "theatres-expansion.json")

# ── Default Constants ────────────────────────────────────────────────────────
DEFAULT_AMC_MARKET_SHARE = 0.25
CORE_COHORT = "core"
EXPANSION_COHORT = "expansion"
DEFAULT_MODEL_COHORTS = (CORE_COHORT,)
KNOWN_THEATRE_COHORTS = {CORE_COHORT, EXPANSION_COHORT}
URL_SHOWTIME_IDENTITY_VALUES = {"url", "seat-map", "seat_map", "amc_url", "amc-url"}

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

# Evening-sample (5pm–11pm) → full-day revenue multipliers, *per day of week*.
# Most days have full daytime business (matinees) we don't scrape, so 1.7×
# extrapolates 6 captured evening showings to ~10–14 full-day showings.
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


def load_theatre_cohort_sets():
    """Return {cohort: theatre_names} from core + expansion config files."""
    cohort_sets = {CORE_COHORT: set(), EXPANSION_COHORT: set()}
    _add_theatre_cohorts(cohort_sets, THEATRES_JSON, CORE_COHORT)
    _add_theatre_cohorts(cohort_sets, THEATRES_EXPANSION_JSON, EXPANSION_COHORT)
    cohort_sets[EXPANSION_COHORT] -= cohort_sets[CORE_COHORT]
    return cohort_sets


def model_allows_theatre(theatre_name, cohort_sets=None, model_cohorts=None):
    """True when a row's theatre belongs to an enabled model cohort.

    Unknown theatres are allowed so old/manual rows do not disappear just
    because the theatre config changed. Expansion theatres are known and are
    therefore excluded unless explicitly enabled.
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

    The caller (predict_movie) sums these per-row revenues per (theatre,
    day), then multiplies by the evening→daily multiplier to extrapolate
    from our 5pm–11pm sample to a full-day theatre estimate.
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


def days_to_weekend(daily_estimates, cal):
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

    # Confidence based on how many days we have
    n_days = len(daily_estimates)
    conf_low, conf_high = DAY_CONFIDENCE.get(n_days, (0.70, 1.40))
    weekend_low = weekend_mid * conf_low
    weekend_high = weekend_mid * conf_high

    return weekend_mid, weekend_low, weekend_high, calibrated_daily


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
                p_yes = float(prices[0])
            else:
                p_yes = float(prices_raw) if prices_raw else 0
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

    # Expected value
    ev = sum(b["midpoint"] * b["p_yes"] for b in brackets)

    # Weighted standard deviation
    if ev > 0:
        variance = sum(b["p_yes"] * (b["midpoint"] - ev) ** 2 for b in brackets)
        std = sqrt(variance) if variance > 0 else ev * 0.2
    else:
        std = 0

    # Highest probability bracket
    best_bracket = max(brackets, key=lambda b: b["p_yes"])

    return {
        "ev": ev,
        "std": std,
        "low": max(0, ev - std),
        "high": ev + std,
        "brackets": brackets,
        "best_bracket": best_bracket,
        "total_volume": total_volume,
    }


# ── Stage F: Blended Prediction ──────────────────────────────────────────────

def blend_predictions(seat_est, seat_low, seat_high,
                      poly_result, n_theatres, n_days):
    """Stage F: weighted blend of seat-based and Polymarket estimates."""
    if poly_result is None:
        return seat_est, seat_low, seat_high, 1.0, 0.0

    poly_ev = poly_result["ev"]
    poly_volume = poly_result["total_volume"]

    # Seat data quality (0-1)
    seat_quality = min(1.0, (n_theatres / 100) * 0.6 + (n_days / 3) * 0.4)

    # Polymarket quality (0-1)
    poly_quality = min(1.0, poly_volume / 500_000)

    # Weights
    w_seat = seat_quality * 0.6
    w_poly = poly_quality * 0.4
    total_w = w_seat + w_poly

    if total_w == 0:
        return seat_est, seat_low, seat_high, 1.0, 0.0

    w_seat_norm = w_seat / total_w
    w_poly_norm = w_poly / total_w

    blended = seat_est * w_seat_norm + poly_ev * w_poly_norm
    blended_low = min(seat_low, poly_result["low"])
    blended_high = max(seat_high, poly_result["high"])

    return blended, blended_low, blended_high, w_seat_norm, w_poly_norm


# ── Calibration ──────────────────────────────────────────────────────────────

def record_actual(cal, movie, predicted_mid, predicted_low, predicted_high,
                  seat_raw, poly_ev, actual, n_theatres, days_collected,
                  daily_theatre_counts=None, daily_coverage_ratios=None,
                  daily_predictions=None, raw_daily_predictions=None,
                  weekend_of=None):
    """Record a predicted-vs-actual result and update calibration factors."""
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
        "days_collected": days_collected,
    }
    if weekend_of:
        entry["weekend_of"] = weekend_of
    if daily_predictions:
        entry["daily_predictions"] = {
            k: round(v, 2) for k, v in daily_predictions.items()
        }
    if raw_daily_predictions:
        entry["raw_daily_predictions"] = {
            k: round(v, 2) for k, v in raw_daily_predictions.items()
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


# ── Main Prediction Pipeline ─────────────────────────────────────────────────

def predict_movie(movie, seat_data, poly_data, cal, verbose=False, national_theatre_count=None):
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

    # Group by day of week
    daily_estimates = {}
    daily_details = {}
    expected_amc_theatres = max(
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

        # Stage A: per-showtime revenue (one row = one captured evening
        # showing). Aggregate per theatre, then scale the evening sample to
        # a full-day estimate via the calibrated evening→daily multiplier.
        per_showtime_results = []
        no_data_count = 0
        captured_by_theatre = {}        # {theatre: [per_showtime_result, ...]}
        for row in rows_by_theatre_fmt_show.values():
            result = estimate_theatre_daily_revenue(row, cal)
            if result:
                per_showtime_results.append(result)
                t_name = result["theatre_name"]
                captured_by_theatre.setdefault(t_name, []).append(result)
            else:
                no_data_count += 1

        if not per_showtime_results:
            continue

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
        ev_to_daily = get_evening_to_daily_multiplier(cal, day_name=day_name)
        theatre_results = []
        showings_by_theatre = {}
        for t_name, captured_rows in captured_by_theatre.items():
            captured_rev = sum(r["revenue"] for r in captured_rows)
            theatre_day_rev = captured_rev * ev_to_daily
            theatre_results.append({
                "revenue": theatre_day_rev,
                "theatre_name": t_name,
                "n_captured_showings": len(captured_rows),
                "captured_revenue": captured_rev,
                "evening_to_daily": ev_to_daily,
            })
            showings_by_theatre[t_name] = len(captured_rows)

        # Stage B: sum all AMC
        amc_total, amc_stats = sum_amc_theatres(theatre_results)
        n_amc_theatres = amc_stats.get("n_theatres", 0)
        coverage_ratio = (
            min(1.0, n_amc_theatres / expected_amc_theatres)
            if expected_amc_theatres else None
        )
        avg_showings = (sum(showings_by_theatre.values()) / len(showings_by_theatre)
                        if showings_by_theatre else 0)

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
            "domestic_mid": domestic_mid,
            "domestic_low": domestic_low,
            "domestic_high": domestic_high,
            "n_theatres": n_amc_theatres,
            "expected_theatres": expected_amc_theatres,
            "coverage_ratio": coverage_ratio,
            "n_no_data": no_data_count,
            "avg_showings_per_cinema": round(avg_showings, 1),
            "evening_to_daily": ev_to_daily,
            "mean_revenue": amc_stats.get("mean_revenue", 0),
            "median_revenue": amc_stats.get("median_revenue", 0),
            "theatre_results": theatre_results if verbose else [],
        }

    if not daily_estimates:
        return None

    # Stage D: day-by-day calibration → weekend sum.
    seat_mid, seat_low, seat_high, calibrated_daily = days_to_weekend(daily_estimates, cal)
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

    # Stage E: Polymarket
    poly_result = None
    if poly_data:
        poly_result = polymarket_expected_value(poly_data)

    # Stage F: blend
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

    if poly_result:
        # Polymarket EV is already in millions
        blended_m, blend_low_m, blend_high_m, w_seat, w_poly = blend_predictions(
            seat_mid_m, seat_low_m, seat_high_m,
            poly_result, n_theatres_total, n_days
        )
    else:
        blended_m = seat_mid_m
        blend_low_m = seat_low_m
        blend_high_m = seat_high_m
        w_seat, w_poly = 1.0, 0.0

    avg_showings_total = (
        sum(d.get("avg_showings_per_cinema", 0) for d in daily_details.values()) /
        len(daily_details) if daily_details else 0
    )

    return {
        "movie": movie,
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
        "n_days": n_days,
        "n_theatres_total": n_theatres_total,
        "expected_amc_theatres": expected_amc_theatres,
        "ignored_post_weekend_dates": ignored_dates,
        "coverage_ratio": round(
            sum(
                d.get("coverage_ratio", 0)
                for d in daily_details.values()
                if d.get("coverage_ratio") is not None
            ) / len([
                d for d in daily_details.values()
                if d.get("coverage_ratio") is not None
            ]),
            3,
        ) if any(d.get("coverage_ratio") is not None for d in daily_details.values()) else None,
        "national_theatre_count": national_theatre_count,
        "avg_showings_per_cinema": round(avg_showings_total, 1),
        "amc_total_weekend": sum(d.get("amc_total", 0) for d in daily_details.values()),
    }


# ── Output ───────────────────────────────────────────────────────────────────

def fmt_m(val):
    """Format millions as $XXX.XM or $X.XM."""
    if val >= 1:
        return f"${val:,.1f}M"
    elif val > 0:
        return f"${val * 1000:,.0f}K"
    return "$0"


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
    shows_str = f", ~{pred.get('avg_showings_per_cinema', 0):.1f} showings/cinema" if pred.get('avg_showings_per_cinema') else ""
    print(f"  Seat-based:    {fmt_m(pred['seat_mid_m']):>10}  "
          f"({fmt_m(pred['seat_low_m'])} - {fmt_m(pred['seat_high_m'])})")
    print(f"    Data: {n_th} AMC theatres{nat_str}, {pred['n_days']} day(s) [{days_str}]{shows_str}")

    # Per-day breakdown
    for day, details in sorted(pred["daily_details"].items(),
                                key=lambda x: x[1]["date"]):
        amc_m = details["amc_total"] / 1_000_000
        raw_dom_m = details.get("raw_domestic_mid", details["domestic_mid"]) / 1_000_000
        dom_m = details["domestic_mid"] / 1_000_000
        day_scale = details.get("day_scale", 1.0)
        spd = details.get("avg_showings_per_cinema", 0)
        coverage = details.get("coverage_ratio")
        coverage_str = (
            f", {coverage:.0%} sample coverage"
            if coverage is not None and coverage < 0.95 else ""
        )
        day_model = fmt_m(dom_m)
        if abs(day_scale - 1.0) >= 0.005:
            day_model = f"{fmt_m(raw_dom_m)} × {day_scale:.3f} = {fmt_m(dom_m)}"
        print(f"    {day} ({details['date']}): "
              f"AMC {fmt_m(amc_m)} → day {day_model} "
              f"[{details['n_theatres']} theatres{coverage_str}, {spd:.1f} showings/cinema"
              f"{', ' + str(details['n_no_data']) + ' no data' if details['n_no_data'] else ''}]")

    # Polymarket
    poly = pred["poly_result"]
    if poly:
        print(f"  Polymarket:    {fmt_m(poly['ev']):>10}  "
              f"({fmt_m(poly['low'])} - {fmt_m(poly['high'])})")
        bb = poly["best_bracket"]
        vol_str = f"${poly['total_volume']:,.0f}" if poly['total_volume'] else "—"
        print(f"    Brackets: {len(poly['brackets'])}, vol {vol_str}")
        print(f"    Highest-prob: ${bb['low']:.0f}M-${bb['high']:.0f}M "
              f"({bb['p_yes']:.0%})")

    # Blended
    print(f"  PREDICTION:    {fmt_m(pred['blended_m']):>10}  "
          f"({fmt_m(pred['blend_low_m'])} - {fmt_m(pred['blend_high_m'])})")
    if poly:
        w_s = pred["w_seat"]
        w_p = pred["w_poly"]
        print(f"    Weights: {w_s:.0%} seat / {w_p:.0%} Polymarket")
        diff = pred["blended_m"] - poly["ev"]
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
                     Include best-effort expansion theatres in prediction
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
                            national_theatre_count=nat_count)
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

        pred_mid = pred["blended_m"]
        pred_low = pred["blend_low_m"]
        pred_high = pred["blend_high_m"]
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
            day: round(details["coverage_ratio"], 3)
            for day, details in pred.get("daily_details", {}).items()
            if details.get("coverage_ratio") is not None
        }

        record_actual(cal, movie_match, pred_mid, pred_low, pred_high,
                     seat_raw, poly_ev, actual_val, n_th, days,
                     daily_theatre_counts=daily_theatre_counts,
                     daily_coverage_ratios=daily_coverage_ratios,
                     daily_predictions=daily_predictions,
                     raw_daily_predictions=raw_daily_predictions,
                     weekend_of=weekend_of)
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
                            national_theatre_count=nat_count)
        if pred:
            print_prediction(pred, verbose=verbose)

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
