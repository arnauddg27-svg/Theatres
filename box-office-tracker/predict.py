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
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from math import exp, log, sqrt
from calibration_freeze import (calibration_has_weekend,
                                load_calibration_freeze,
                                save_calibration_freeze)
from historical_comps import (NATIONAL_FOOTPRINT_EXPONENT,
                              NATIONAL_FOOTPRINT_MAX_FACTOR,
                              NATIONAL_FOOTPRINT_MIN_FACTOR,
                              NATIONAL_WIDE_RELEASE_BASELINE_THEATRES,
                              TargetMetadata,
                              estimate_from_prediction,
                              estimate_opening_weekend_from_thursday,
                              load_historical_comps,
                              load_movie_metadata,
                              metadata_for_movie,
                              release_footprint_factor,
                              release_scale_for_item)
from model_calibration import (MIN_DAILY_CALIBRATION_COVERAGE,
                               SNAPSHOT_LEAD_BUCKETS,
                               excluded_calibration_days,
                               sanitize_calibration, recalibrate_scale_factor,
                               recalibrate_day_scale_factors,
                               recalibrate_snapshot_day_scale_factors,
                               recalibrate_snapshot_lead_scale_factors,
                               snapshot_calibration_actual_for_day,
                               snapshot_calibration_support)

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR            = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SEAT_CSV            = os.path.join(DATA_DIR, "seat-counts.csv")
PRE_RESERVATION_CSV = os.path.join(DATA_DIR, "pre-reservation-snapshots.csv")
DAILY_ACTUALS_CSV   = os.path.join(DATA_DIR, "daily-actual-overrides.csv")
POLY_CSV            = os.path.join(DATA_DIR, "polymarket-markets.csv")
SOCIAL_SIGNALS_CSV  = os.path.join(DATA_DIR, "social-signals.csv")
SHOWTIME_LINKS_JSON = os.path.join(DATA_DIR, "showtime-links.json")
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
MODEL_VERSION = "seat-regression-v23-daily-seat-snapshot-no-comps"
COMPS_IN_FORECAST = False
SNAPSHOT_LAYER_MAX_WEIGHT = 0.70
DYNAMIC_AMC_SHARE_MAX_WEIGHT = 0.85
DYNAMIC_AMC_SHARE_MIN_SHARE = 0.10
DYNAMIC_AMC_SHARE_MAX_SHARE = 0.50
RESIDUAL_REGRESSION_MIN_OBS = 2
RESIDUAL_REGRESSION_PRIOR_WEIGHT = 6.0
RESIDUAL_REGRESSION_MAX_STRENGTH = 0.35
RESIDUAL_REGRESSION_RATIO_MIN = 0.60
RESIDUAL_REGRESSION_RATIO_MAX = 1.60
RESIDUAL_REGRESSION_FACTOR_MIN = 0.85
RESIDUAL_REGRESSION_FACTOR_MAX = 1.15
RESIDUAL_SAME_MODEL_VERSION_WEIGHT = 1.0
RESIDUAL_DIFFERENT_MODEL_VERSION_WEIGHT = 0.60
RESIDUAL_LEGACY_MODEL_VERSION_WEIGHT = 0.35
RESIDUAL_METADATA_MIN_WEIGHT = 0.55
RESIDUAL_METADATA_MAX_WEIGHT = 1.15
RESIDUAL_FOOTPRINT_MIN_WEIGHT = 0.65
RESIDUAL_FOOTPRINT_MAX_WEIGHT = 1.10
RESIDUAL_METADATA_COMBINED_MIN_WEIGHT = 0.45
RESIDUAL_METADATA_COMBINED_MAX_WEIGHT = 1.20
EMPIRICAL_DAILY_REGRESSION_MIN_EXAMPLES = 5
EMPIRICAL_SNAPSHOT_REGRESSION_MIN_EXAMPLES = 4
EMPIRICAL_DAILY_REGRESSION_PRIOR_WEIGHT = 5.0
EMPIRICAL_SNAPSHOT_REGRESSION_PRIOR_WEIGHT = 4.0
EMPIRICAL_DAILY_REGRESSION_MAX_STRENGTH = 0.55
EMPIRICAL_SNAPSHOT_REGRESSION_MAX_STRENGTH = 0.65
EMPIRICAL_DAILY_FACTOR_MIN = 0.70
EMPIRICAL_DAILY_FACTOR_MAX = 1.55
EMPIRICAL_SNAPSHOT_FACTOR_MIN = 0.55
EMPIRICAL_SNAPSHOT_FACTOR_MAX = 1.80
EMPIRICAL_DAILY_TRAINING_MIN_COVERAGE = 0.45
EMPIRICAL_SNAPSHOT_TRAINING_MIN_COVERAGE = 0.20
INFERRED_METADATA_MAX_COMP_WEIGHT = 0.70
INFERRED_METADATA_DISAGREE_MAX_COMP_WEIGHT = 0.85
MODEL_DISAGREEMENT_MEDIUM_RATIO = 1.25
MODEL_DISAGREEMENT_HIGH_RATIO = 1.55
MODEL_DISAGREEMENT_SPARSE_QUALITY = 0.35
MODEL_DISAGREEMENT_SNAPSHOT_MEDIUM_MULTIPLIER = 0.80
MODEL_DISAGREEMENT_SNAPSHOT_HIGH_MULTIPLIER = 0.65
PREVIEW_SEAT_RESIDUAL_MIN_OBS = 1
PREVIEW_SEAT_RESIDUAL_PRIOR_WEIGHT = 4.0
PREVIEW_SEAT_RESIDUAL_MAX_STRENGTH = 0.60
PREVIEW_SEAT_RESIDUAL_RATIO_MIN = 0.70
PREVIEW_SEAT_RESIDUAL_RATIO_MAX = 1.80
PREVIEW_SEAT_RESIDUAL_FACTOR_MIN = 0.85
PREVIEW_SEAT_RESIDUAL_FACTOR_MAX = 1.45
SOCIAL_LAYER_MAX_ADJUSTMENT = 0.08
SOCIAL_LAYER_SENTIMENT_WEIGHT = 0.03
SOCIAL_LAYER_BUZZ_WEIGHT = 0.05
SOCIAL_LAYER_MIN_QUALITY_FOR_ADJUSTMENT = 0.05
SNAPSHOT_MAX_SLICE_AGE_HOURS = 8
SNAPSHOT_SAME_WEEK_SCALE_MIN = 0.50
SNAPSHOT_SAME_WEEK_SCALE_MAX = 3.00
SNAPSHOT_MAX_LEAD_MINUTES = 96 * 60
SNAPSHOT_DAY_SHAPE_MAX_SIGNAL_WEIGHT = 0.65
SNAPSHOT_FRONTLOAD_MAX_PRIOR_SHIFT = 0.35
SNAPSHOT_FRONTLOAD_MIN_CONFIDENCE = 0.10
SNAPSHOT_SUPPORT_PRIOR_WEIGHT = 2.0
SNAPSHOT_UNTRAINED_DAY_SUPPORT_FLOOR = 0.20
SNAPSHOT_UNTRAINED_LEAD_SUPPORT_FLOOR = 0.35
SNAPSHOT_ONE_ANCHOR_SUPPORT_FLOOR = 0.55
SNAPSHOT_TWO_ANCHOR_SUPPORT_FLOOR = 0.70
SNAPSHOT_MISSING_SHARE_SIGNAL_FLOOR = 0.50
SNAPSHOT_STRATEGIC_THEATRE_CAP = 100
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
WEEKEND_DAYPART_COVERAGE_FLOOR = 0.45
WEEKEND_LATE_SKEW_DAYPART_COVERAGE_FLOOR = 0.85
WEEKEND_ADULT_DAYPART_COVERAGE_FLOOR = 0.70
WEEKEND_LATE_SKEW_MIN_SHOWINGS = 2.5
WEEKEND_LATE_SKEW_LATEST_START_HOUR = 18.0
WEEKEND_SCHEDULE_PROFILE_MIN_THEATRES = 10
WEEKEND_DAYPART_SNAPSHOT_SUPPORT_THRESHOLD = 0.85
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


def _metadata_text(target_metadata):
    if target_metadata is None:
        return ""
    fields = (
        getattr(target_metadata, "genre", ""),
        getattr(target_metadata, "audience_type", ""),
        getattr(target_metadata, "franchise_type", ""),
        getattr(target_metadata, "rating", ""),
        getattr(target_metadata, "notes", ""),
    )
    return " ".join(str(value or "").lower() for value in fields)


def is_family_title(target_metadata):
    metadata_text = _metadata_text(target_metadata)
    rating = (getattr(target_metadata, "rating", "") or "").upper() if target_metadata else ""
    return "family" in metadata_text or rating in {"G", "PG"}


def is_late_skew_title(target_metadata):
    """Titles where a mid-afternoon/evening-heavy schedule is expected."""
    metadata_text = _metadata_text(target_metadata)
    rating = (getattr(target_metadata, "rating", "") or "").upper() if target_metadata else ""
    late_skew_terms = (
        "horror",
        "thriller",
        "fan",
        "adult",
        "r-rated",
        "r rated",
    )
    return rating in {"R", "NC-17"} or any(term in metadata_text for term in late_skew_terms)


def weekend_daypart_coverage_factor(day_name, full_day_window_coverage_ratio,
                                    target_metadata=None,
                                    earliest_showtime_hour=None,
                                    avg_showings=None,
                                    scheduled_full_day_window_coverage_ratio=None,
                                    scheduled_earliest_showtime_hour=None,
                                    scheduled_avg_showings=None):
    """How complete a Sat/Sun regular scrape is across the 10am-11pm daypart.

    Theatre count alone can look healthy even when every collected seat map is
    late afternoon/evening. For broad/family titles, missing matinees are a real
    gap. For niche horror/adult-skewing titles, a late-heavy schedule can be the
    actual full playable day, so avoid penalizing healthy theatre/showtime
    coverage merely because AMC did not schedule 10am/noon shows.
    """
    if day_name not in {"Saturday", "Sunday"}:
        return 1.0
    try:
        full_day_coverage = float(full_day_window_coverage_ratio)
    except (TypeError, ValueError):
        full_day_coverage = 0.0
    full_day_coverage = _clamp(full_day_coverage, 0.0, 1.0)
    threshold = max(WEEKEND_FULL_DAY_MIN_THEATRE_COVERAGE, 1e-9)
    if full_day_coverage >= threshold:
        return 1.0
    schedule_has_profile = scheduled_full_day_window_coverage_ratio is not None
    if schedule_has_profile:
        try:
            scheduled_full_day_coverage = float(scheduled_full_day_window_coverage_ratio)
        except (TypeError, ValueError):
            scheduled_full_day_coverage = 0.0
        scheduled_full_day_coverage = _clamp(scheduled_full_day_coverage, 0.0, 1.0)
        try:
            scheduled_show_count = float(scheduled_avg_showings)
        except (TypeError, ValueError):
            scheduled_show_count = 0.0
        try:
            scheduled_earliest_hour = float(scheduled_earliest_showtime_hour)
        except (TypeError, ValueError):
            scheduled_earliest_hour = None
        if (
            scheduled_full_day_coverage < threshold
            and scheduled_show_count >= WEEKEND_LATE_SKEW_MIN_SHOWINGS
            and scheduled_earliest_hour is not None
            and scheduled_earliest_hour <= WEEKEND_LATE_SKEW_LATEST_START_HOUR
        ):
            return 1.0
        if scheduled_full_day_coverage >= threshold:
            floor = WEEKEND_DAYPART_COVERAGE_FLOOR
            progress = full_day_coverage / threshold
            return _clamp(
                floor + ((1.0 - floor) * progress),
                floor,
                1.0,
            )
    try:
        show_count = float(avg_showings)
    except (TypeError, ValueError):
        show_count = 0.0
    try:
        earliest_hour = float(earliest_showtime_hour)
    except (TypeError, ValueError):
        earliest_hour = None
    if (
        is_late_skew_title(target_metadata)
        and show_count >= WEEKEND_LATE_SKEW_MIN_SHOWINGS
        and earliest_hour is not None
        and earliest_hour <= WEEKEND_LATE_SKEW_LATEST_START_HOUR
    ):
        return 1.0
    floor = WEEKEND_DAYPART_COVERAGE_FLOOR
    if is_late_skew_title(target_metadata):
        floor = WEEKEND_LATE_SKEW_DAYPART_COVERAGE_FLOOR
    elif target_metadata is not None and not is_family_title(target_metadata):
        floor = WEEKEND_ADULT_DAYPART_COVERAGE_FLOOR
    progress = full_day_coverage / threshold
    return _clamp(
        floor + ((1.0 - floor) * progress),
        floor,
        1.0,
    )


def regular_day_needs_snapshot_support(day_name, details):
    """Whether same-day snapshot demand should support a partial regular day."""
    if day_name not in {"Saturday", "Sunday"} or not details:
        return False
    if details.get("actual_override"):
        return False
    return _coverage_value(
        details.get("daypart_coverage_factor"),
        default=1.0,
    ) < WEEKEND_DAYPART_SNAPSHOT_SUPPORT_THRESHOLD


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

    if not is_family_title(target_metadata):
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


def get_snapshot_lead_scale(cal, lead_bucket):
    """Calibrated residual for a snapshot lead-time bucket."""
    factors = (cal or {}).get("calibration_factors", {}) if cal else {}
    per_lead = factors.get("snapshot_to_lead_scale_factors") if cal else None
    if isinstance(per_lead, dict) and lead_bucket in per_lead:
        try:
            return float(per_lead[lead_bucket])
        except (TypeError, ValueError):
            pass
    return 1.0


def get_snapshot_to_day_scale(cal, day_name, lead_bucket=None):
    """Calibrated scale for pre-reservation snapshot → final day gross."""
    factors = (cal or {}).get("calibration_factors", {}) if cal else {}
    per_day = factors.get("snapshot_to_day_scale_factors") if cal else None
    day_scale = 1.0
    if isinstance(per_day, dict) and day_name in per_day:
        try:
            day_scale = float(per_day[day_name])
        except (TypeError, ValueError):
            pass
    if lead_bucket:
        return day_scale * get_snapshot_lead_scale(cal, lead_bucket)
    return day_scale


def _snapshot_support_entry(cal, section, key):
    factors = (cal or {}).get("calibration_factors", {}) if cal else {}
    support = factors.get("snapshot_calibration_support", {}) or {}
    entry = (support.get(section, {}) or {}).get(key, {}) or {}
    return {
        "n": int(_positive_float(entry.get("n")) or 0),
        "support": _positive_float(entry.get("support")) or 0.0,
    }


def _snapshot_support_strength(weighted_support, floor):
    support = _positive_float(weighted_support) or 0.0
    if support <= 0:
        return _clamp(floor, 0.0, 1.0)
    strength = support / (support + SNAPSHOT_SUPPORT_PRIOR_WEIGHT)
    return _clamp(strength, floor, 1.0)


def snapshot_calibration_support_factor(cal, day_name, lead_bucket):
    """Model-weight cap implied by historical snapshot calibration support."""
    day_entry = _snapshot_support_entry(cal, "days", day_name)
    lead_entry = _snapshot_support_entry(cal, "leads", lead_bucket)
    day_strength = _snapshot_support_strength(
        day_entry["support"],
        SNAPSHOT_UNTRAINED_DAY_SUPPORT_FLOOR,
    )
    lead_strength = _snapshot_support_strength(
        lead_entry["support"],
        SNAPSHOT_UNTRAINED_LEAD_SUPPORT_FLOOR,
    )
    # The snapshot layer needs both a day-specific relationship and a lead-time
    # relationship. Use the weaker of the two so an untrained future-day bucket
    # cannot inherit full same-day confidence.
    factor = min(day_strength, lead_strength)
    return {
        "factor": round(_clamp(factor, 0.0, 1.0), 4),
        "day_support": round(day_entry["support"], 4),
        "day_n": day_entry["n"],
        "lead_support": round(lead_entry["support"], 4),
        "lead_n": lead_entry["n"],
    }


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
OPENING_DAY_ALIASES = {
    "thu": "Thursday",
    "thur": "Thursday",
    "thurs": "Thursday",
    "thursday": "Thursday",
    "preview": "Thursday",
    "previews": "Thursday",
    "friday": "Friday",
    "fri": "Friday",
    "saturday": "Saturday",
    "sat": "Saturday",
    "sunday": "Sunday",
    "sun": "Sunday",
}

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


def daypart_profile_from_rows(rows, *, source=None):
    """Summarize showtime daypart shape from regular or snapshot rows."""
    theatre_hours = {}
    for row in rows or []:
        theatre_name = (row.get("theatre_name") or "").strip()
        if not theatre_name:
            continue
        parsed_hour = _parse_showtime_hour(row.get("showtime", ""))
        if parsed_hour is None:
            continue
        theatre_hours.setdefault(theatre_name, []).append(parsed_hour)
    return daypart_profile_from_theatre_hours(theatre_hours, source=source)


def daypart_profile_from_theatre_hours(theatre_hours, *, source=None):
    """Summarize showtime daypart shape from theatre → hour lists."""
    n_theatres = len(theatre_hours)
    if not n_theatres:
        return {}
    all_hours = [hour for hours in theatre_hours.values() for hour in hours]
    if not all_hours:
        return {}
    full_day_theatres = sum(
        1
        for hours in theatre_hours.values()
        if min(hours) <= WEEKEND_FULL_DAY_LATEST_EARLY_HOUR
    )
    profile = {
        "n_theatres": n_theatres,
        "avg_showings": len(all_hours) / n_theatres,
        "earliest_showtime_hour": min(all_hours),
        "full_day_window_coverage_ratio": full_day_theatres / n_theatres,
    }
    if source:
        profile["source"] = source
    return profile


def combine_daypart_profiles(*profiles):
    """Combine schedule evidence, preserving early-showtime evidence.

    Phase 1 link caches can be rebuilt after early showtimes roll off. Snapshot
    rows preserve the schedule seen before the day started, so any reliable
    profile that proves early showtimes existed should influence daypart
    coverage.
    """
    usable = [
        profile for profile in profiles
        if profile and profile.get("n_theatres", 0) >= WEEKEND_SCHEDULE_PROFILE_MIN_THEATRES
    ]
    if not usable:
        usable = [profile for profile in profiles if profile]
    if not usable:
        return {}
    earliest_values = [
        profile.get("earliest_showtime_hour")
        for profile in usable
        if profile.get("earliest_showtime_hour") is not None
    ]
    combined = {
        "n_theatres": max(profile.get("n_theatres", 0) for profile in usable),
        "avg_showings": max(profile.get("avg_showings", 0) for profile in usable),
        "full_day_window_coverage_ratio": max(
            profile.get("full_day_window_coverage_ratio", 0)
            for profile in usable
        ),
        "source": "+".join(
            sorted({
                str(profile.get("source") or "unknown")
                for profile in usable
            })
        ),
    }
    if earliest_values:
        combined["earliest_showtime_hour"] = min(earliest_values)
    return combined


def load_showtime_link_daypart_profiles(weekend_of=None):
    """Summarize Phase 1 scheduled showtime shape by movie/date.

    The regular scrape can only collect seat maps for showtimes Phase 1 found.
    If Phase 1 itself found no morning/noon Saturday shows for a niche title,
    that is a release schedule signal, not missing regular scrape coverage.
    """
    if not os.path.exists(SHOWTIME_LINKS_JSON):
        return {}
    try:
        with open(SHOWTIME_LINKS_JSON, "r") as f:
            links = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

    links_weekend = links.get("weekend_of") or links.get("date")
    if weekend_of and links_weekend and links_weekend != weekend_of:
        return {}

    cohort_sets = load_theatre_cohort_sets()
    model_cohorts = active_model_cohorts()
    by_movie_date = {}
    for theatre_name, theatre_entry in (links.get("theatres") or {}).items():
        if not model_allows_theatre(
            theatre_name,
            cohort_sets=cohort_sets,
            model_cohorts=model_cohorts,
        ):
            continue
        for date_str, date_entry in (theatre_entry.get("dates") or {}).items():
            movies = date_entry.get("movies") or {}
            for movie, showtimes in movies.items():
                if not movie or not isinstance(showtimes, list):
                    continue
                hours = [
                    hour
                    for hour in (
                        _parse_showtime_hour(show.get("showtime", ""))
                        for show in showtimes
                        if isinstance(show, dict)
                    )
                    if hour is not None
                ]
                if not hours:
                    continue
                key = (movie, date_str)
                profile = by_movie_date.setdefault(
                    key,
                    {
                        "theatres": {},
                    },
                )
                profile["theatres"][theatre_name] = hours

    profiles = {}
    for (movie, date_str), profile in by_movie_date.items():
        daypart_profile = daypart_profile_from_theatre_hours(
            profile.get("theatres") or {},
            source="showtime_links",
        )
        if daypart_profile:
            profiles.setdefault(movie, {})[date_str] = daypart_profile
    return profiles


def normalize_opening_day_name(value):
    """Return canonical opening-weekend day name for manual/report inputs."""
    raw = (value or "").strip().lower()
    raw = re.sub(r"[^a-z]+", "", raw)
    return OPENING_DAY_ALIASES.get(raw)


def _movie_lookup_key(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def movie_mapping_get(mapping, movie, default=None):
    """Fetch a movie-keyed side input with punctuation/case-tolerant matching."""
    if not isinstance(mapping, dict):
        return default
    if movie in mapping:
        return mapping[movie]
    target_key = _movie_lookup_key(movie)
    if not target_key:
        return default
    for title, value in mapping.items():
        if _movie_lookup_key(title) == target_key:
            return value
    return default


def load_daily_actual_overrides(weekend_of=None, through_date=None):
    """Load reported partial actuals, e.g. Thursday previews.

    These are known daily grosses used as forecast inputs. They are not final
    opening-weekend actuals and should not be written into calibration history
    until the full weekend settles.
    """
    if not os.path.exists(DAILY_ACTUALS_CSV):
        return {}

    with open(DAILY_ACTUALS_CSV, "r") as f:
        rows = list(csv.DictReader(f))

    if weekend_of is None:
        weekends = sorted({
            row.get("weekend_of", "")
            for row in rows
            if row.get("weekend_of")
        })
        weekend_of = weekends[-1] if weekends else _current_weekend_friday()

    selected = {}
    for idx, row in enumerate(rows):
        row_weekend = row.get("weekend_of", "")
        if row_weekend and row_weekend != weekend_of:
            continue
        as_of_date = row.get("as_of_date", "") or row.get("reported_date", "")
        if through_date and as_of_date and as_of_date > through_date:
            continue
        movie = (row.get("movie_title", "") or "").strip()
        day_name = normalize_opening_day_name(
            row.get("day_of_week", "") or row.get("day", "")
        )
        gross_m = _positive_float(row.get("gross_m", "") or row.get("gross", ""))
        if not movie or not day_name or gross_m is None:
            continue
        movie_bucket = selected.setdefault(movie, {})
        candidate = {
            "gross_m": gross_m,
            "source": row.get("source", ""),
            "status": row.get("status", ""),
            "as_of_date": as_of_date,
            "notes": row.get("notes", ""),
            "_sort_key": (as_of_date or "", idx),
        }
        existing = movie_bucket.get(day_name)
        if not existing or candidate["_sort_key"] >= existing.get("_sort_key", ("", -1)):
            movie_bucket[day_name] = candidate

    for movie_bucket in selected.values():
        for actual in movie_bucket.values():
            actual.pop("_sort_key", None)
    return selected


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


def _social_float(row, fields, default=0.0):
    for field in fields:
        value = (row.get(field, "") or "").strip()
        if value == "":
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return default


def _social_date(row):
    """Best-effort YYYY-MM-DD timestamp for social signal rows."""
    for field in ("as_of_date", "date", "snapshot_date", "collected_at", "timestamp"):
        value = (row.get(field, "") or "").strip()
        if value:
            return value[:10]
    return ""


def _normalize_social_score(value):
    """Normalize manual sentiment/buzz scores to -1..1.

    Accepted conventions:
      - -1..1: native normalized score
      - 0..100: 50 is neutral
      - -100..100: percentage-style score
    """
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    if -1.0 <= score <= 1.0:
        return _clamp(score, -1.0, 1.0)
    if 0.0 <= score <= 100.0:
        return _clamp((score - 50.0) / 50.0, -1.0, 1.0)
    if -100.0 <= score <= 100.0:
        return _clamp(score / 100.0, -1.0, 1.0)
    return None


def _social_sentiment_from_row(row):
    explicit = (row.get("sentiment_score", "") or "").strip()
    if explicit != "":
        normalized = _normalize_social_score(explicit)
        if normalized is not None:
            return normalized

    positive = _social_float(row, ("positive_mentions", "positive", "pos"), 0.0)
    negative = _social_float(row, ("negative_mentions", "negative", "neg"), 0.0)
    neutral = _social_float(row, ("neutral_mentions", "neutral"), 0.0)
    denom = positive + negative + neutral
    if denom <= 0:
        denom = positive + negative
    if denom <= 0:
        return 0.0
    return _clamp((positive - negative) / denom, -1.0, 1.0)


def _social_reach_from_row(row):
    """Return a weighted activity proxy across common platform fields."""
    mentions = _social_float(row, ("mentions", "posts", "videos", "items"), 0.0)
    engagement = _social_float(row, ("engagement", "interactions"), 0.0)
    views = _social_float(row, ("views", "video_views", "impressions"), 0.0)
    social_media_universe_m = _social_float(
        row,
        ("social_media_universe_m", "smu_m", "social_media_universe"),
        0.0,
    )
    likes = _social_float(row, ("likes",), 0.0)
    comments = _social_float(row, ("comments", "replies"), 0.0)
    shares = _social_float(row, ("shares", "reposts", "retweets"), 0.0)
    return max(
        0.0,
        mentions
        + engagement / 25.0
        + views / 1000.0
        + social_media_universe_m * 1000.0
        + likes / 50.0
        + comments / 10.0
        + shares / 10.0,
    )


def load_social_signal_data(weekend_of=None, through_date=None):
    """Load optional social buzz/sentiment rows grouped by movie.

    `social-signals.csv` is intentionally data-source agnostic. It can hold
    manual or automated platform snapshots from TikTok, X, Reddit, YouTube,
    Google Trends, RelishMix-style exports, etc. Prediction uses the latest row
    per movie/platform/source, then compares total reach against other movies in
    the same file/weekend. If the file is absent or has no usable rows, the
    social layer is neutral and forecast math is unchanged.
    """
    if not os.path.exists(SOCIAL_SIGNALS_CSV):
        return {}

    rows = []
    with open(SOCIAL_SIGNALS_CSV, "r") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            movie = (row.get("movie_title") or row.get("movie") or "").strip()
            if not movie:
                continue
            row_weekend = (row.get("weekend_of") or "").strip()
            if weekend_of and row_weekend and row_weekend != weekend_of:
                continue
            row_date = _social_date(row)
            if through_date:
                if not row_date or row_date > through_date:
                    continue
            row["movie_title"] = movie
            rows.append((idx, row_date, row))

    if weekend_of is None:
        weekends = [
            row.get("weekend_of", "")
            for _, _, row in rows
            if row.get("weekend_of")
        ]
        weekend_of = max(weekends) if weekends else _current_weekend_friday()

    latest_rows = {}
    for idx, row_date, row in rows:
        row_weekend = (row.get("weekend_of") or "").strip()
        if row_weekend and row_weekend != weekend_of:
            continue
        movie = row["movie_title"]
        platform = (row.get("platform") or "unknown").strip().lower()
        source = (row.get("source") or row.get("source_url") or "").strip().lower()
        dedupe_key = (movie.lower(), platform, source)
        sort_key = (row_date, idx)
        prev = latest_rows.get(dedupe_key)
        if not prev or sort_key >= prev[0]:
            latest_rows[dedupe_key] = (sort_key, row)

    grouped = {}
    for _, row in latest_rows.values():
        movie = row["movie_title"]
        reach = _social_reach_from_row(row)
        sentiment = _social_sentiment_from_row(row)
        explicit_buzz = _normalize_social_score((row.get("buzz_score") or "").strip())
        social_media_universe_m = _social_float(
            row,
            ("social_media_universe_m", "smu_m", "social_media_universe"),
            0.0,
        )
        grouped.setdefault(movie, []).append({
            "row": row,
            "reach": reach,
            "sentiment": sentiment,
            "explicit_buzz": explicit_buzz,
            "social_media_universe_m": social_media_universe_m,
            "platform": (row.get("platform") or "unknown").strip() or "unknown",
        })

    aggregates = {}
    reaches = []
    for movie, items in grouped.items():
        reach = sum(item["reach"] for item in items)
        if reach > 0:
            reaches.append(reach)
        weight_total = sum(max(item["reach"], 1.0) for item in items)
        sentiment = (
            sum(item["sentiment"] * max(item["reach"], 1.0) for item in items) / weight_total
            if weight_total > 0 else 0.0
        )
        buzz_scores = [
            (item["explicit_buzz"], max(item["reach"], 1.0))
            for item in items
            if item["explicit_buzz"] is not None
        ]
        explicit_buzz = (
            sum(score * weight for score, weight in buzz_scores) /
            sum(weight for _, weight in buzz_scores)
            if buzz_scores else None
        )
        platforms = sorted({item["platform"] for item in items})
        social_media_universe_m = max(
            float(item.get("social_media_universe_m") or 0.0)
            for item in items
        )
        quality = _clamp(
            (log(1.0 + max(reach, 0.0)) / log(1.0 + 25_000.0) if reach > 0 else 0.0)
            * _clamp(0.50 + 0.20 * len(platforms), 0.50, 1.0),
            0.0,
            1.0,
        )
        aggregates[movie] = {
            "movie": movie,
            "weekend_of": weekend_of,
            "rows": len(items),
            "platforms": platforms,
            "reach": reach,
            "sentiment_score": _clamp(sentiment, -1.0, 1.0),
            "explicit_buzz_score": explicit_buzz,
            "signal_quality": quality,
            "social_media_universe_m": round(social_media_universe_m, 3),
        }

    baseline = statistics.median(reaches) if len(reaches) >= 2 else None
    for signal in aggregates.values():
        if signal["explicit_buzz_score"] is not None:
            buzz = signal["explicit_buzz_score"]
            source = "explicit"
        elif baseline and signal["reach"] > 0:
            buzz = _clamp(log(signal["reach"] / baseline) / log(4.0), -1.0, 1.0)
            source = "relative-volume"
        else:
            buzz = 0.0
            source = "neutral"
        signal["buzz_score"] = round(_clamp(buzz, -1.0, 1.0), 4)
        signal["buzz_source"] = source
        signal["sentiment_score"] = round(signal["sentiment_score"], 4)
        signal["signal_quality"] = round(signal["signal_quality"], 4)
    return aggregates


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
            "snapshot_to_day_scale_factors": {
                day: 1.0 for day in OPENING_WEEKEND_DAYS
            },
            "snapshot_to_lead_scale_factors": {
                bucket: 1.0 for bucket in SNAPSHOT_LEAD_BUCKETS
            },
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


def national_theatre_count_for_movie(movie, theatre_counts, metadata=None):
    """Find the BOM theatre count for a movie, allowing simple fuzzy matches."""
    nat_count = movie_mapping_get(theatre_counts, movie)
    if nat_count:
        return nat_count
    for tc_movie, count in theatre_counts.items():
        if tc_movie.lower() in movie.lower() or movie.lower() in tc_movie.lower():
            return count
    if metadata:
        target = metadata_for_movie(movie, metadata)
        if target and target.national_theatre_count:
            return target.national_theatre_count
    return None


def national_release_footprint_factor(national_theatre_count,
                                      baseline=NATIONAL_WIDE_RELEASE_BASELINE_THEATRES):
    """Capacity modifier from national theatre count.

    The AMC model is calibrated from wide-release outcomes, so a reported
    national count should not become an independent gross extrapolation. Use it
    as a bounded footprint modifier instead: sub-wide releases get a drag
    versus a 3,600-4,200-theatre release, while very wide releases get only a
    small upside because seat occupancy/showtime density already carry demand.
    """
    if baseline == NATIONAL_WIDE_RELEASE_BASELINE_THEATRES:
        return release_footprint_factor(national_theatre_count)

    count = _positive_float(national_theatre_count)
    baseline = _positive_float(baseline)
    if not count or not baseline:
        return 1.0
    baseline_factor = release_footprint_factor(baseline)
    if baseline_factor <= 0:
        return 1.0
    return _clamp(
        release_footprint_factor(count) / baseline_factor,
        NATIONAL_FOOTPRINT_MIN_FACTOR,
        NATIONAL_FOOTPRINT_MAX_FACTOR,
    )


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


def snapshot_lead_bucket(minutes_until_showtime):
    """Bucket snapshot lead time for calibration residuals."""
    minutes = _parse_numeric(minutes_until_showtime, default=None)
    if minutes is None:
        return None
    if minutes <= 24 * 60:
        return "same_day"
    if minutes <= 48 * 60:
        return "next_day"
    if minutes <= SNAPSHOT_MAX_LEAD_MINUTES:
        return "multi_day"
    return "long_lead"


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

    minutes_until_showtime = _parse_numeric(row.get("minutes_until_showtime", 0), default=0)
    multiplier = snapshot_reservation_multiplier(minutes_until_showtime)
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
        "minutes_until_showtime": minutes_until_showtime,
        "theatre_name": row.get("theatre_name", "?"),
        "format": row.get("auditorium_type") or row.get("auditorium_name") or "?",
    }


def snapshot_within_remaining_weekend_window(row):
    """Keep pre-reservation rows inside the remaining-weekend signal window."""
    minutes = _parse_numeric(row.get("minutes_until_showtime", ""), default=None)
    if minutes is None:
        return False
    return 0 <= minutes <= SNAPSHOT_MAX_LEAD_MINUTES


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


def snapshot_strategic_expected_theatres(expected_amc_theatres):
    """Expected theatre denominator for capped top-theatre snapshot probes."""
    expected = int(_positive_float(expected_amc_theatres) or 0)
    cap = int(
        _positive_float(os.environ.get("SNAPSHOT_TOP_THEATRE_CAP"))
        or SNAPSHOT_STRATEGIC_THEATRE_CAP
    )
    cap = max(1, cap)
    if expected <= 0:
        return cap
    return min(expected, cap)


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
    partial_daypart_days = []
    for day, details in (daily_details or {}).items():
        coverage = details.get(
            "effective_coverage_ratio",
            details.get("coverage_ratio"),
        )
        day_coverages[day] = coverage
        if details.get("missing_timezones"):
            missing_timezone_days.append(day)
        if regular_day_needs_snapshot_support(day, details):
            partial_daypart_days.append(day)

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
        "partial_daypart_days": sorted(set(partial_daypart_days)),
        "snapshot_days": snapshot_days,
        "snapshot_coverage_ratio": snapshot_coverage,
    }


def actual_override_day_share(daily_details, cal):
    """Opening-weekend share already replaced by reported daily actuals."""
    if not daily_details:
        return 0.0
    day_weights = get_day_weights(cal)
    expected_days = [
        day for day in OPENING_WEEKEND_DAYS
        if day_weights.get(day, 0) > 0
    ]
    total_weight = sum(day_weights.get(day, 0) for day in expected_days) or 1.0
    actual_weight = sum(
        day_weights.get(day, 0)
        for day, details in daily_details.items()
        if day in expected_days and details.get("actual_override")
    )
    return _clamp(actual_weight / total_weight, 0.0, 1.0)


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


def component_ratio(high_signal, low_signal):
    """Return max/min for two positive model anchors."""
    a = _positive_float(high_signal)
    b = _positive_float(low_signal)
    if not a or not b:
        return None
    return max(a, b) / max(0.001, min(a, b))


def model_component_disagreement_profile(
    pred,
    base_mid=None,
    snapshot_mid=None,
    include_comp=True,
):
    """Describe how far the model's independent anchors are from each other."""
    direct_mid = _positive_float(pred.get("seat_mid_m"))
    comp_mid = (
        _positive_float(
            pred.get("seat_comp_adjusted_mid_m", pred.get("seat_comp_mid_m"))
        )
        if include_comp else None
    )
    base_mid = _positive_float(base_mid or pred.get("seat_primary_mid_m"))
    snapshot_mid = _positive_float(snapshot_mid or pred.get("snapshot_mid_m"))

    ratios = {}
    if direct_mid and comp_mid:
        ratios["seat_vs_comp"] = component_ratio(direct_mid, comp_mid)
    if base_mid and snapshot_mid:
        ratios["snapshot_vs_base"] = component_ratio(snapshot_mid, base_mid)
    if direct_mid and snapshot_mid:
        ratios["seat_vs_snapshot"] = component_ratio(direct_mid, snapshot_mid)

    max_ratio = max((value for value in ratios.values() if value), default=1.0)
    if max_ratio >= MODEL_DISAGREEMENT_HIGH_RATIO:
        severity = "high"
        snapshot_multiplier = MODEL_DISAGREEMENT_SNAPSHOT_HIGH_MULTIPLIER
    elif max_ratio >= MODEL_DISAGREEMENT_MEDIUM_RATIO:
        severity = "medium"
        snapshot_multiplier = MODEL_DISAGREEMENT_SNAPSHOT_MEDIUM_MULTIPLIER
    else:
        severity = "low"
        snapshot_multiplier = 1.0

    anchor_values = [
        value for value in (direct_mid, comp_mid, base_mid, snapshot_mid)
        if value and value > 0
    ]
    spread_m = max(anchor_values) - min(anchor_values) if len(anchor_values) >= 2 else 0.0
    quality = _coverage_value(pred.get("seat_data_quality"), default=1.0)
    sparse_multiplier = _clamp(1.0 - quality, 0.0, 1.0)
    if severity == "high":
        range_buffer_m = spread_m * (0.06 + 0.06 * sparse_multiplier)
    elif severity == "medium":
        range_buffer_m = spread_m * (0.03 + 0.04 * sparse_multiplier)
    else:
        range_buffer_m = 0.0

    return {
        "severity": severity,
        "max_ratio": round(max_ratio, 4),
        "ratios": {
            key: round(value, 4)
            for key, value in ratios.items()
            if value is not None
        },
        "spread_m": round(spread_m, 3),
        "seat_data_quality": round(quality, 4),
        "snapshot_weight_multiplier": round(snapshot_multiplier, 4),
        "range_buffer_m": round(range_buffer_m, 3),
    }


def seat_primary_ensemble(pred):
    """Blend direct seat totals with the comp-translated seat signal."""
    comp_mid = pred.get("seat_comp_adjusted_mid_m", pred.get("seat_comp_mid_m"))
    if comp_mid is None:
        return None
    direct_mid = pred["seat_mid_m"]
    direct_low = pred["seat_low_m"]
    direct_high = pred["seat_high_m"]
    comp_low = pred.get("seat_comp_adjusted_low_m", pred["seat_comp_low_m"])
    comp_high = pred.get("seat_comp_adjusted_high_m", pred["seat_comp_high_m"])

    w_comp = comp_component_weight(pred.get("n_days", 0))
    w_direct = 1.0 - w_comp
    quality_raw = pred.get("seat_data_quality")
    quality = _coverage_value(quality_raw, default=1.0)
    if quality_raw is not None:
        # The base day-count weight says how many days were collected; quality
        # says whether those days represent enough of the weekend/theatre map to
        # trust a direct extrapolation. Keep a small floor so seats remain the
        # anchor, but let sparse partial reads lean on comps/priors.
        w_direct *= 0.35 + 0.65 * quality
        w_comp = 1.0 - w_direct
    actual_share = _coverage_value(pred.get("reported_actual_day_share"), default=0.0)
    if actual_share >= 0.20:
        actual_anchor_floor = min(0.70, 0.25 + 0.60 * actual_share)
        w_direct = max(w_direct, actual_anchor_floor)
        w_comp = 1.0 - w_direct
    inferred_cap = None
    if pred.get("seat_comp_metadata_source") == "title_inferred":
        inferred_cap = INFERRED_METADATA_MAX_COMP_WEIGHT
        ratio = component_ratio(direct_mid, comp_mid) or 1.0
        if (
            ratio >= MODEL_DISAGREEMENT_HIGH_RATIO
            and quality < MODEL_DISAGREEMENT_SPARSE_QUALITY
            and actual_share < 0.20
        ):
            inferred_cap = INFERRED_METADATA_DISAGREE_MAX_COMP_WEIGHT
        w_comp = min(w_comp, inferred_cap)
        w_direct = 1.0 - w_comp

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
        "reported_actual_day_share": actual_share,
        "disagreement_m": disagreement,
        "inferred_metadata_comp_cap": inferred_cap,
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
    actual_share = _coverage_value(pred.get("reported_actual_day_share"), default=0.0)
    if actual_share >= 0.20:
        weight *= 1.0 - min(0.30, actual_share * 0.45)
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
    if actual_share >= 0.20:
        cap *= 1.0 - min(0.25, actual_share * 0.35)
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


def _historical_residual_metadata_weight(pred, entry, metadata):
    if not metadata:
        return 1.0
    target_metadata = metadata_for_movie(pred.get("movie", ""), metadata)
    entry_metadata = metadata_for_movie(entry.get("movie", ""), metadata)
    if not target_metadata or not entry_metadata:
        return 1.0
    similarity = _metadata_preview_similarity(target_metadata, entry_metadata)
    similarity_weight = _clamp(
        RESIDUAL_METADATA_MIN_WEIGHT
        + ((RESIDUAL_METADATA_MAX_WEIGHT - RESIDUAL_METADATA_MIN_WEIGHT) * similarity),
        RESIDUAL_METADATA_MIN_WEIGHT,
        RESIDUAL_METADATA_MAX_WEIGHT,
    )
    target_count = _positive_float(getattr(target_metadata, "national_theatre_count", 0))
    entry_count = _positive_float(getattr(entry_metadata, "national_theatre_count", 0))
    footprint_weight = 1.0
    if target_count and entry_count:
        ratio = min(target_count, entry_count) / max(target_count, entry_count)
        footprint_weight = _clamp(
            0.45 + (0.65 * ratio),
            RESIDUAL_FOOTPRINT_MIN_WEIGHT,
            RESIDUAL_FOOTPRINT_MAX_WEIGHT,
        )
    return _clamp(
        similarity_weight * footprint_weight,
        RESIDUAL_METADATA_COMBINED_MIN_WEIGHT,
        RESIDUAL_METADATA_COMBINED_MAX_WEIGHT,
    )


def _historical_residual_weight(pred, entry, metadata=None):
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

    current_version = pred.get("model_version") or MODEL_VERSION
    entry_version = entry.get("model_version")
    if not entry_version:
        version_weight = RESIDUAL_LEGACY_MODEL_VERSION_WEIGHT
    elif entry_version == current_version:
        version_weight = RESIDUAL_SAME_MODEL_VERSION_WEIGHT
    else:
        version_weight = RESIDUAL_DIFFERENT_MODEL_VERSION_WEIGHT

    day_similarity = 1.0 - min(1.0, abs(current_days - entry_days) / 4.0) * 0.45
    coverage_similarity = 1.0 - abs(current_coverage - entry_coverage) * 0.45
    metadata_weight = _historical_residual_metadata_weight(pred, entry, metadata)
    return max(
        0.0,
        entry_quality
        * cohort_weight
        * version_weight
        * day_similarity
        * coverage_similarity
        * metadata_weight,
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
    metadata = load_movie_metadata()
    for entry in (cal or {}).get("history", [])[-20:]:
        if not _actual_status_is_final(entry):
            continue
        if _movie_matches(pred.get("movie", ""), entry.get("movie", "")):
            continue
        predicted = _positive_float(entry.get("predicted_mid"))
        actual = _positive_float(entry.get("actual_total", entry.get("actual")))
        if not predicted or not actual:
            continue
        weight = _historical_residual_weight(pred, entry, metadata=metadata)
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


EMPIRICAL_DAILY_FEATURES = (
    "intercept",
    "is_snapshot",
    "is_thursday",
    "is_friday",
    "is_saturday",
    "is_sunday",
    "lead_same_day",
    "lead_next_day",
    "lead_multi_day",
    "lead_long_lead",
    "log_predicted_m",
    "log_n_theatres",
    "log_avg_showings_per_cinema",
    "log_national_theatre_count",
    "coverage_ratio",
)


def _empirical_feature_value(row, key):
    if key == "intercept":
        return 1.0
    if key == "is_snapshot":
        return 1.0 if row.get("is_snapshot") else 0.0
    day = row.get("day") or row.get("day_of_week") or ""
    if key == "is_thursday":
        return 1.0 if day == "Thursday" else 0.0
    if key == "is_friday":
        return 1.0 if day == "Friday" else 0.0
    if key == "is_saturday":
        return 1.0 if day == "Saturday" else 0.0
    if key == "is_sunday":
        return 1.0 if day == "Sunday" else 0.0
    lead_bucket = row.get("lead_bucket") or ""
    if key == "lead_same_day":
        return 1.0 if lead_bucket == "same_day" else 0.0
    if key == "lead_next_day":
        return 1.0 if lead_bucket == "next_day" else 0.0
    if key == "lead_multi_day":
        return 1.0 if lead_bucket == "multi_day" else 0.0
    if key == "lead_long_lead":
        return 1.0 if lead_bucket == "long_lead" else 0.0
    if key == "log_predicted_m":
        return log(max(_positive_float(row.get("predicted_m")) or 0.0, 0.05))
    if key == "log_n_theatres":
        return log(max(_positive_float(row.get("n_theatres")) or 1.0, 1.0) / 425.0)
    if key == "log_avg_showings_per_cinema":
        return log(max(_positive_float(row.get("avg_showings_per_cinema")) or 0.5, 0.5) / 4.0)
    if key == "log_national_theatre_count":
        count = _positive_float(row.get("national_theatre_count"))
        return log(max(count or NATIONAL_WIDE_RELEASE_BASELINE_THEATRES, 1000.0) / NATIONAL_WIDE_RELEASE_BASELINE_THEATRES)
    if key == "coverage_ratio":
        return _coverage_value(
            row.get("coverage_ratio", row.get("effective_coverage_ratio")),
            default=0.0,
        )
    return 0.0


def _empirical_feature_vector(row, features=EMPIRICAL_DAILY_FEATURES):
    return [_empirical_feature_value(row, feature) for feature in features]


def _log_similarity(a, b, *, scale=1.0, default=0.70):
    a_value = _positive_float(a)
    b_value = _positive_float(b)
    if not a_value or not b_value:
        return default
    return exp(-abs(log(a_value / b_value)) * scale)


def _empirical_day_similarity(current_day, example_day):
    if current_day == example_day:
        return 1.0
    if current_day not in OPENING_WEEKEND_DAYS or example_day not in OPENING_WEEKEND_DAYS:
        return 0.25
    if {current_day, example_day} <= {"Friday", "Saturday", "Sunday"}:
        return 0.55
    return 0.25


def _empirical_example_weight(current, example):
    coverage = _coverage_value(
        example.get("coverage_ratio", example.get("effective_coverage_ratio")),
        default=0.0,
    )
    if coverage <= 0:
        return 0.0
    day_weight = _empirical_day_similarity(current.get("day"), example.get("day"))
    theatre_weight = _log_similarity(
        current.get("n_theatres"),
        example.get("n_theatres"),
        scale=0.50,
    )
    showings_weight = _log_similarity(
        current.get("avg_showings_per_cinema"),
        example.get("avg_showings_per_cinema"),
        scale=0.80,
    )
    national_weight = _log_similarity(
        current.get("national_theatre_count"),
        example.get("national_theatre_count"),
        scale=0.45,
        default=0.80,
    )
    source_weight = 1.0
    if bool(current.get("is_snapshot")) != bool(example.get("is_snapshot")):
        source_weight = 0.70
    lead_weight = 1.0
    current_lead = current.get("lead_bucket")
    example_lead = example.get("lead_bucket")
    if current_lead or example_lead:
        lead_weight = 1.0 if current_lead == example_lead else 0.65
    return max(
        0.0,
        coverage
        * day_weight
        * theatre_weight
        * showings_weight
        * national_weight
        * source_weight
        * lead_weight,
    )


def _solve_weighted_ridge(features, targets, weights, l2=2.0):
    if not features:
        return None
    n = len(features[0])
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    vector = [0.0 for _ in range(n)]
    for row, target, weight in zip(features, targets, weights):
        if weight <= 0:
            continue
        for i in range(n):
            vector[i] += weight * row[i] * target
            for j in range(n):
                matrix[i][j] += weight * row[i] * row[j]
    for i in range(1, n):
        matrix[i][i] += l2

    for i in range(n):
        pivot = max(range(i, n), key=lambda idx: abs(matrix[idx][i]))
        if abs(matrix[pivot][i]) < 1e-9:
            return None
        if pivot != i:
            matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
            vector[i], vector[pivot] = vector[pivot], vector[i]
        pivot_value = matrix[i][i]
        for j in range(i, n):
            matrix[i][j] /= pivot_value
        vector[i] /= pivot_value
        for k in range(n):
            if k == i:
                continue
            factor = matrix[k][i]
            if abs(factor) < 1e-12:
                continue
            for j in range(i, n):
                matrix[k][j] -= factor * matrix[i][j]
            vector[k] -= factor * vector[i]
    return vector


def empirical_daily_residual_regression(current, examples, *,
                                        min_examples=EMPIRICAL_DAILY_REGRESSION_MIN_EXAMPLES,
                                        prior_weight=EMPIRICAL_DAILY_REGRESSION_PRIOR_WEIGHT,
                                        max_strength=EMPIRICAL_DAILY_REGRESSION_MAX_STRENGTH,
                                        factor_min=EMPIRICAL_DAILY_FACTOR_MIN,
                                        factor_max=EMPIRICAL_DAILY_FACTOR_MAX,
                                        l2=2.0):
    """Current-feature local ridge regression for actual/seat residuals.

    This is deliberately residual-based: the observed seat/snapshot estimate
    remains the main signal, and historical actuals only learn how similar
    theatre/showing/coverage profiles have missed before.
    """
    predicted = _positive_float(current.get("predicted_m"))
    if not predicted:
        return None

    training_rows = []
    for example in examples or []:
        example_pred = _positive_float(example.get("predicted_m"))
        actual = _positive_float(example.get("actual_m"))
        if not example_pred or not actual:
            continue
        weight = _empirical_example_weight(current, example)
        if weight <= 0:
            continue
        ratio = _clamp(actual / example_pred, factor_min, factor_max)
        training_rows.append((example, ratio, weight))

    if len(training_rows) < min_examples:
        return None

    x_rows = [_empirical_feature_vector(example) for example, _, _ in training_rows]
    y_rows = [log(ratio) for _, ratio, _ in training_rows]
    weights = [weight for _, _, weight in training_rows]
    beta = _solve_weighted_ridge(x_rows, y_rows, weights, l2=l2)

    if beta:
        current_x = _empirical_feature_vector(current)
        raw_factor = exp(sum(coef * value for coef, value in zip(beta, current_x)))
    else:
        total_weight = sum(weights)
        if total_weight <= 0:
            return None
        raw_factor = exp(
            sum(log(ratio) * weight for _, ratio, weight in training_rows)
            / total_weight
        )

    raw_factor = _clamp(raw_factor, factor_min, factor_max)
    effective_weight = sum(weights)
    strength = min(
        max_strength,
        effective_weight / (effective_weight + max(0.0, prior_weight)),
    )
    factor = 1.0 + ((raw_factor - 1.0) * strength)
    factor = _clamp(factor, factor_min, factor_max)
    return {
        "factor": factor,
        "raw_factor": raw_factor,
        "strength": strength,
        "n": len(training_rows),
        "effective_weight": effective_weight,
        "features": [
            "predicted_m",
            "day",
            "n_theatres",
            "avg_showings_per_cinema",
            "national_theatre_count",
            "coverage_ratio",
        ],
        "model_features": list(EMPIRICAL_DAILY_FEATURES),
        "examples": [
            {
                "movie": example.get("movie"),
                "weekend_of": example.get("weekend_of"),
                "day": example.get("day"),
                "ratio": ratio,
                "weight": weight,
                "predicted_m": example.get("predicted_m"),
                "actual_m": example.get("actual_m"),
                "avg_showings_per_cinema": example.get("avg_showings_per_cinema"),
                "n_theatres": example.get("n_theatres"),
            }
            for example, ratio, weight in sorted(
                training_rows,
                key=lambda item: item[2],
                reverse=True,
            )[:6]
        ],
    }


def _detail_mid_m(details):
    return (_positive_float((details or {}).get("domestic_mid")) or 0.0) / 1_000_000


def _detail_bound_m(details, key, fallback_m):
    value = _positive_float((details or {}).get(key))
    return (value / 1_000_000) if value is not None else fallback_m


def _recompute_weekend_from_daily_detail_m(daily_details, cal):
    day_weights = get_day_weights(cal)
    values = {
        day: _detail_mid_m(details)
        for day, details in (daily_details or {}).items()
        if day in OPENING_WEEKEND_DAYS and _detail_mid_m(details) > 0
    }
    if not values:
        return None
    low_values = {
        day: _detail_bound_m(daily_details[day], "domestic_low", values[day])
        for day in values
    }
    high_values = {
        day: _detail_bound_m(daily_details[day], "domestic_high", values[day])
        for day in values
    }
    collected_share = sum(day_weights.get(day, 0.0) for day in values)
    scale = 1.0
    if 0 < collected_share < 0.99:
        scale = 1.0 / collected_share
    mid = sum(values.values()) * scale
    low = sum(low_values.values()) * scale
    high = sum(high_values.values()) * scale
    return {
        "mid_m": mid,
        "low_m": min(low, mid),
        "high_m": max(high, mid),
        "collected_share": collected_share,
        "days": sorted(values),
    }


def _empirical_current_from_details(day, details, predicted_m,
                                    national_theatre_count=None):
    coverage = details.get(
        "effective_strategic_coverage_ratio",
        details.get("effective_coverage_ratio", details.get("coverage_ratio")),
    )
    lead_bucket = details.get("lead_bucket")
    is_snapshot = bool(
        details.get("snapshot_calibration_support_factor") is not None
        or lead_bucket in SNAPSHOT_LEAD_BUCKETS
        or details.get("snapshot_source")
    )
    return {
        "day": day,
        "predicted_m": predicted_m,
        "n_theatres": details.get("n_theatres"),
        "avg_showings_per_cinema": details.get("avg_showings_per_cinema"),
        "coverage_ratio": coverage,
        "national_theatre_count": national_theatre_count,
        "lead_bucket": lead_bucket,
        "is_snapshot": is_snapshot,
    }


def _apply_empirical_factor_to_details(details, factor_info, prefix):
    factor = _positive_float((factor_info or {}).get("factor"))
    if not details or not factor:
        return details
    adjusted = dict(details)
    adjusted[f"{prefix}_factor"] = round(factor, 4)
    adjusted[f"{prefix}_raw_factor"] = round(factor_info.get("raw_factor", factor), 4)
    adjusted[f"{prefix}_strength"] = round(factor_info.get("strength", 0.0), 4)
    adjusted[f"{prefix}_n"] = factor_info.get("n", 0)
    for key in ("domestic_mid", "domestic_low", "domestic_high"):
        value = _positive_float(adjusted.get(key))
        if value is None:
            continue
        adjusted[f"pre_{prefix}_{key}"] = value
        adjusted[key] = value * factor
    return adjusted


def _snapshot_empirical_basis_details(details):
    """Use the direct snapshot-to-day estimate as the regression input.

    The old snapshot layer could blend a future-day snapshot with a Thursday
    day-shape prior before the supervised residual model ever saw it. That made
    a single Thursday preview extrapolation dominate Fri/Sat/Sun even when we
    had real future-day reservation rows. Historical snapshot calibration is
    stored from the raw snapshot day estimate, so the empirical layer should
    compare raw snapshot to actual and then recompute the weekend from those
    daily rows.
    """
    if not details:
        return details
    adjusted = dict(details)
    replaced_any = False
    for key in ("domestic_mid", "domestic_low", "domestic_high"):
        raw_key = f"raw_{key}"
        raw_value = _positive_float(adjusted.get(raw_key))
        if raw_value is None:
            continue
        adjusted[f"pre_empirical_snapshot_basis_{key}"] = adjusted.get(key)
        adjusted[key] = raw_value
        replaced_any = True
    if replaced_any:
        adjusted["snapshot_empirical_basis"] = "raw_snapshot_to_actual"
    return adjusted


def apply_empirical_snapshot_regression(pred, examples, cal):
    snapshot_details = pred.get("snapshot_daily_details") or {}
    if not snapshot_details:
        return None

    adjusted_days = {}
    factor_by_day = {}
    for day, details in snapshot_details.items():
        basis_details = _snapshot_empirical_basis_details(details)
        predicted_m = _detail_mid_m(basis_details)
        if predicted_m <= 0:
            continue
        current = _empirical_current_from_details(
            day,
            basis_details,
            predicted_m,
            national_theatre_count=pred.get("national_theatre_count"),
        )
        factor_info = empirical_daily_residual_regression(
            current,
            examples,
            min_examples=EMPIRICAL_SNAPSHOT_REGRESSION_MIN_EXAMPLES,
            prior_weight=EMPIRICAL_SNAPSHOT_REGRESSION_PRIOR_WEIGHT,
            max_strength=EMPIRICAL_SNAPSHOT_REGRESSION_MAX_STRENGTH,
            factor_min=EMPIRICAL_SNAPSHOT_FACTOR_MIN,
            factor_max=EMPIRICAL_SNAPSHOT_FACTOR_MAX,
            l2=2.5,
        )
        if not factor_info:
            continue
        adjusted_days[day] = _apply_empirical_factor_to_details(
            basis_details,
            factor_info,
            "snapshot_empirical_regression",
        )
        factor_by_day[day] = factor_info

    if not adjusted_days:
        return None

    merged_snapshot_details = dict(snapshot_details)
    merged_snapshot_details.update(adjusted_days)
    pred["snapshot_daily_details"] = merged_snapshot_details

    combined_details = {}
    combined_details.update(pred.get("daily_details") or {})
    combined_details.update(merged_snapshot_details)
    recomputed = _recompute_weekend_from_daily_detail_m(combined_details, cal)
    if not recomputed:
        return None

    pred["pre_empirical_snapshot_mid_m"] = pred.get("snapshot_mid_m")
    pred["pre_empirical_snapshot_low_m"] = pred.get("snapshot_low_m")
    pred["pre_empirical_snapshot_high_m"] = pred.get("snapshot_high_m")
    pred["snapshot_mid_m"] = recomputed["mid_m"]
    pred["snapshot_low_m"] = recomputed["low_m"]
    pred["snapshot_high_m"] = recomputed["high_m"]
    pred["snapshot_empirical_regression_applied"] = True
    pred["snapshot_empirical_regression_days"] = sorted(adjusted_days)
    pred["snapshot_empirical_regression_factors"] = {
        day: {
            "factor": round(info["factor"], 4),
            "raw_factor": round(info["raw_factor"], 4),
            "strength": round(info["strength"], 4),
            "n": info["n"],
            "effective_weight": round(info["effective_weight"], 4),
            "examples": info["examples"],
        }
        for day, info in factor_by_day.items()
    }
    return pred["snapshot_empirical_regression_factors"]


_EMPIRICAL_SEAT_EXAMPLES_CACHE = {}
_EMPIRICAL_SNAPSHOT_EXAMPLES_CACHE = {}


def _empirical_file_mtime(path):
    try:
        return round(os.path.getmtime(path), 3)
    except OSError:
        return None


def _empirical_history_signature(cal):
    entries = []
    for entry in (cal or {}).get("history", []) or []:
        daily_actuals = entry.get("daily_actuals", {}) or {}
        snapshot_predictions = entry.get("snapshot_daily_predictions", {}) or {}
        entries.append((
            entry.get("movie", ""),
            entry.get("weekend_of", ""),
            entry.get("actual_total", entry.get("actual")),
            tuple(sorted(daily_actuals.items())),
            tuple(sorted(snapshot_predictions.items())),
            tuple(sorted(excluded_calibration_days(entry))),
        ))
    return tuple(entries)


def _empirical_cache_key(kind, cal):
    return (
        kind,
        MODEL_VERSION,
        _empirical_file_mtime(SEAT_CSV),
        _empirical_file_mtime(PRE_RESERVATION_CSV),
        _empirical_history_signature(cal),
    )


def _empirical_history_prediction(entry, cal):
    movie = (entry.get("movie") or "").strip()
    weekend_of = entry.get("weekend_of") or ""
    if not movie or not weekend_of:
        return None
    historical_seat_data = load_seat_data(weekend_of=weekend_of)
    movie_seat_data = movie_mapping_get(historical_seat_data, movie)
    if not movie_seat_data:
        return None
    return predict_movie(
        movie,
        movie_seat_data,
        [],
        cal,
        verbose=False,
        snapshot_data={},
        social_data={},
        daily_actual_overrides={},
        showtime_link_profiles={},
        apply_empirical_regression=False,
    )


def _history_daily_actuals(entry):
    actuals = {}
    for day, value in (entry.get("daily_actuals", {}) or {}).items():
        day_name = normalize_opening_day_name(day)
        gross_m = _positive_float(value)
        if day_name in OPENING_WEEKEND_DAYS and gross_m and gross_m > 0:
            actuals[day_name] = gross_m
    return actuals


def _empirical_example_from_details(movie, weekend_of, day, details, actual_m,
                                    national_theatre_count=None,
                                    source="seat"):
    predicted_m = _detail_mid_m(details)
    if predicted_m <= 0 or not actual_m or actual_m <= 0:
        return None
    current = _empirical_current_from_details(
        day,
        details,
        predicted_m,
        national_theatre_count=national_theatre_count,
    )
    current.update({
        "movie": movie,
        "weekend_of": weekend_of,
        "actual_m": actual_m,
        "source": source,
        "is_snapshot": source == "snapshot" or current.get("is_snapshot"),
    })
    return current


def empirical_seat_training_examples(cal, exclude_movie=None):
    """Build clean day-level seat→actual examples from settled history."""
    cache_key = _empirical_cache_key("seat", cal)
    if cache_key not in _EMPIRICAL_SEAT_EXAMPLES_CACHE:
        examples = []
        for entry in (cal or {}).get("history", []) or []:
            movie = (entry.get("movie") or "").strip()
            weekend_of = entry.get("weekend_of") or ""
            daily_actuals = _history_daily_actuals(entry)
            if not movie or not weekend_of or not daily_actuals:
                continue
            pred = _empirical_history_prediction(entry, cal)
            if not pred:
                continue
            excluded = excluded_calibration_days(entry)
            for day, actual_m in daily_actuals.items():
                if day in excluded:
                    continue
                details = (pred.get("daily_details") or {}).get(day)
                if not details:
                    continue
                coverage = _coverage_value(
                    details.get("effective_coverage_ratio", details.get("coverage_ratio")),
                    default=0.0,
                )
                if coverage < EMPIRICAL_DAILY_TRAINING_MIN_COVERAGE:
                    continue
                example = _empirical_example_from_details(
                    movie,
                    weekend_of,
                    day,
                    details,
                    actual_m,
                    national_theatre_count=pred.get("national_theatre_count"),
                    source="seat",
                )
                if example:
                    example["training_coverage_ratio"] = round(coverage, 4)
                    examples.append(example)
        _EMPIRICAL_SEAT_EXAMPLES_CACHE[cache_key] = examples

    examples = list(_EMPIRICAL_SEAT_EXAMPLES_CACHE.get(cache_key, []))
    if exclude_movie:
        exclude_key = _movie_lookup_key(exclude_movie)
        examples = [
            example for example in examples
            if _movie_lookup_key(example.get("movie", "")) != exclude_key
        ]
    return examples


def empirical_snapshot_training_examples(cal, exclude_movie=None):
    """Build snapshot→actual day examples from settled history.

    These examples train how much pre-reserved seats usually under/overstate
    the final day, separate from the regular post-show seat-count layer.
    """
    cache_key = _empirical_cache_key("snapshot", cal)
    if cache_key not in _EMPIRICAL_SNAPSHOT_EXAMPLES_CACHE:
        examples = []
        for entry in (cal or {}).get("history", []) or []:
            movie = (entry.get("movie") or "").strip()
            weekend_of = entry.get("weekend_of") or ""
            snapshot_predictions = entry.get("snapshot_daily_predictions", {}) or {}
            snapshot_coverage = entry.get("snapshot_daily_coverage_ratios", {}) or {}
            snapshot_leads = entry.get("snapshot_daily_lead_buckets", {}) or {}
            if not movie or not weekend_of or not snapshot_predictions:
                continue
            for raw_day, predicted_m in snapshot_predictions.items():
                day = normalize_opening_day_name(raw_day)
                if day not in OPENING_WEEKEND_DAYS:
                    continue
                actual_m, actual_confidence = snapshot_calibration_actual_for_day(
                    entry,
                    day,
                )
                predicted = _positive_float(predicted_m)
                coverage = _coverage_value(snapshot_coverage.get(day), default=0.0)
                if coverage <= 0:
                    coverage = _coverage_value(
                        (entry.get("daily_coverage_ratios", {}) or {}).get(day),
                        default=0.0,
                    )
                if (
                    not predicted
                    or not actual_m
                    or actual_m <= 0
                    or actual_confidence <= 0
                ):
                    continue
                effective_training_coverage = coverage * actual_confidence
                if effective_training_coverage < EMPIRICAL_SNAPSHOT_TRAINING_MIN_COVERAGE:
                    continue
                example = {
                    "movie": movie,
                    "weekend_of": weekend_of,
                    "day": day,
                    "predicted_m": predicted,
                    "actual_m": actual_m,
                    "coverage_ratio": effective_training_coverage,
                    "actual_confidence": actual_confidence,
                    "lead_bucket": snapshot_leads.get(day),
                    "n_theatres": (entry.get("daily_theatre_counts", {}) or {}).get(day),
                    "avg_showings_per_cinema": None,
                    "national_theatre_count": None,
                    "source": "snapshot",
                    "is_snapshot": True,
                }
                examples.append(example)
        _EMPIRICAL_SNAPSHOT_EXAMPLES_CACHE[cache_key] = examples

    examples = list(_EMPIRICAL_SNAPSHOT_EXAMPLES_CACHE.get(cache_key, []))
    if exclude_movie:
        exclude_key = _movie_lookup_key(exclude_movie)
        examples = [
            example for example in examples
            if _movie_lookup_key(example.get("movie", "")) != exclude_key
        ]
    return examples


def apply_empirical_seat_regression(pred, examples, cal):
    daily_details = pred.get("daily_details") or {}
    if not daily_details:
        return None

    adjusted_days = {}
    factor_by_day = {}
    for day, details in daily_details.items():
        if details.get("actual_override"):
            continue
        predicted_m = _detail_mid_m(details)
        if predicted_m <= 0:
            continue
        current = _empirical_current_from_details(
            day,
            details,
            predicted_m,
            national_theatre_count=pred.get("national_theatre_count"),
        )
        current["is_snapshot"] = False
        factor_info = empirical_daily_residual_regression(
            current,
            examples,
            min_examples=EMPIRICAL_DAILY_REGRESSION_MIN_EXAMPLES,
            prior_weight=EMPIRICAL_DAILY_REGRESSION_PRIOR_WEIGHT,
            max_strength=EMPIRICAL_DAILY_REGRESSION_MAX_STRENGTH,
            factor_min=EMPIRICAL_DAILY_FACTOR_MIN,
            factor_max=EMPIRICAL_DAILY_FACTOR_MAX,
            l2=2.0,
        )
        if not factor_info:
            continue
        adjusted_days[day] = _apply_empirical_factor_to_details(
            details,
            factor_info,
            "seat_empirical_regression",
        )
        factor_by_day[day] = factor_info

    if not adjusted_days:
        return None

    merged_details = dict(daily_details)
    merged_details.update(adjusted_days)
    recomputed = _recompute_weekend_from_daily_detail_m(merged_details, cal)
    if not recomputed:
        return None

    pred["daily_details"] = merged_details
    pred["daily_estimates"] = {
        day: details.get("domestic_mid", 0)
        for day, details in merged_details.items()
    }
    pred["pre_empirical_seat_mid_m"] = pred.get("seat_mid_m")
    pred["pre_empirical_seat_low_m"] = pred.get("seat_low_m")
    pred["pre_empirical_seat_high_m"] = pred.get("seat_high_m")
    pred["seat_mid_m"] = recomputed["mid_m"]
    pred["seat_low_m"] = recomputed["low_m"]
    pred["seat_high_m"] = recomputed["high_m"]
    pred["blended_m"] = pred["seat_mid_m"]
    pred["blend_low_m"] = pred["seat_low_m"]
    pred["blend_high_m"] = pred["seat_high_m"]
    pred["seat_empirical_regression_applied"] = True
    pred["seat_empirical_regression_days"] = sorted(adjusted_days)
    pred["seat_empirical_regression_factors"] = {
        day: {
            "factor": round(info["factor"], 4),
            "raw_factor": round(info["raw_factor"], 4),
            "strength": round(info["strength"], 4),
            "n": info["n"],
            "effective_weight": round(info["effective_weight"], 4),
            "examples": info["examples"],
        }
        for day, info in factor_by_day.items()
    }
    return pred["seat_empirical_regression_factors"]


def attach_empirical_seat_snapshot_regression(pred, cal):
    """Attach supervised daily residual corrections trained from past actuals."""
    if not pred:
        return None
    seat_examples = empirical_seat_training_examples(
        cal,
        exclude_movie=pred.get("movie"),
    )
    snapshot_examples = empirical_snapshot_training_examples(
        cal,
        exclude_movie=pred.get("movie"),
    )
    pred["empirical_regression_training_counts"] = {
        "seat_daily_examples": len(seat_examples),
        "snapshot_daily_examples": len(snapshot_examples),
    }
    seat_result = apply_empirical_seat_regression(pred, seat_examples, cal)
    snapshot_result = apply_empirical_snapshot_regression(pred, snapshot_examples, cal)
    pred["empirical_regression_applied"] = bool(seat_result or snapshot_result)
    return {
        "seat": seat_result,
        "snapshot": snapshot_result,
    }


def build_social_signal_layer(movie, social_data):
    """Return a capped social buzz/sentiment modifier for one movie.

    Social data is intentionally secondary. The layer can only make a bounded
    multiplicative adjustment to the seat/comp/snapshot forecast, and missing
    social data returns None so the core seat model is unchanged.
    """
    signal = movie_mapping_get(social_data, movie)
    if not signal:
        return None

    try:
        sentiment = _clamp(float(signal.get("sentiment_score", 0.0)), -1.0, 1.0)
    except (TypeError, ValueError):
        sentiment = 0.0
    try:
        buzz = _clamp(float(signal.get("buzz_score", 0.0)), -1.0, 1.0)
    except (TypeError, ValueError):
        buzz = 0.0
    quality = _coverage_value(signal.get("signal_quality"), default=0.0)

    raw_adjustment = (
        SOCIAL_LAYER_SENTIMENT_WEIGHT * sentiment
        + SOCIAL_LAYER_BUZZ_WEIGHT * buzz
    )
    if quality < SOCIAL_LAYER_MIN_QUALITY_FOR_ADJUSTMENT:
        adjustment = 0.0
    else:
        adjustment = raw_adjustment * quality
    adjustment = _clamp(
        adjustment,
        -SOCIAL_LAYER_MAX_ADJUSTMENT,
        SOCIAL_LAYER_MAX_ADJUSTMENT,
    )
    return {
        "movie": movie,
        "weekend_of": signal.get("weekend_of"),
        "factor": round(1.0 + adjustment, 5),
        "adjustment_pct": round(adjustment * 100.0, 2),
        "raw_adjustment_pct": round(raw_adjustment * 100.0, 2),
        "sentiment_score": round(sentiment, 4),
        "buzz_score": round(buzz, 4),
        "buzz_source": signal.get("buzz_source", "neutral"),
        "signal_quality": round(quality, 4),
        "reach": round(float(signal.get("reach") or 0.0), 2),
        "social_media_universe_m": round(
            float(signal.get("social_media_universe_m") or 0.0),
            3,
        ),
        "rows": int(signal.get("rows") or 0),
        "platforms": signal.get("platforms") or [],
        "max_adjustment_pct": round(SOCIAL_LAYER_MAX_ADJUSTMENT * 100.0, 1),
    }


def attach_social_signal_prediction(pred, social_data):
    layer = build_social_signal_layer(pred.get("movie", ""), social_data)
    if not layer:
        return None
    pred["social_signal"] = layer
    return layer


def _importance_driver(rank, driver, importance, evidence, why, basis,
                       available=True, confidence=None, model_impact_m=None):
    confidence_value = importance if confidence is None else confidence
    return {
        "rank": rank,
        "priority_rank": rank,
        "driver": driver,
        "importance": int(round(_clamp(float(importance), 0.0, 100.0))),
        "available": bool(available),
        "confidence": int(round(_clamp(float(confidence_value), 0.0, 100.0))),
        "evidence": evidence,
        "why": why,
        "basis": basis,
        "model_impact_m": model_impact_m,
    }


def forecast_feature_importance(pred):
    """Rank the current forecast's live predictive drivers.

    These are not universal causal coefficients. They are an auditable model
    card for the current forecast: how much each available input is allowed to
    influence this prediction after coverage, calibration support, and missing
    data are considered.
    """
    daily_details = pred.get("daily_details") or {}
    thursday = daily_details.get("Thursday") or {}
    comps_active = bool(COMPS_IN_FORECAST and not pred.get("comp_model_excluded"))

    thursday_amc = _positive_float(
        thursday.get("sampled_amc_total", thursday.get("amc_total"))
    )
    thursday_day = _positive_float(
        thursday.get("domestic_mid") or thursday.get("raw_domestic_mid")
    )
    thursday_coverage = _coverage_value(
        thursday.get("effective_coverage_ratio", thursday.get("coverage_ratio")),
        default=_coverage_value(pred.get("seat_data_quality"), default=0.0),
    )
    if thursday_amc and thursday_day:
        thursday_importance = 90.0 + min(8.0, thursday_coverage * 8.0)
        thursday_available = True
        thursday_confidence = thursday_coverage * 100.0
        thursday_evidence = (
            f"{fmt_m(thursday_amc / 1_000_000)} sampled AMC -> "
            f"{fmt_m(thursday_day / 1_000_000)} Thursday seat gross; "
            f"{int(thursday.get('n_theatres') or 0)} AMC theatres, "
            f"{thursday_coverage:.0%} effective coverage"
        )
        if thursday.get("actual_override"):
            thursday_evidence += " with reported actual override"
    else:
        thursday_importance = 20.0
        thursday_available = False
        thursday_confidence = 0.0
        thursday_evidence = "missing Thursday sampled AMC gross; forecast leans on priors"

    pickup = pred.get("snapshot_pickup_profile") or {}
    reserved = _positive_float(pickup.get("reserved_seats_at_snapshot"))
    snapshot_days = pred.get("snapshot_days") or []
    snapshot_weight = _coverage_value(
        pred.get("snapshot_effective_model_weight", pred.get("snapshot_model_weight")),
        default=0.0,
    )
    snapshot_support = _coverage_value(
        pred.get("snapshot_calibration_support_factor"),
        default=0.0,
    )
    snapshot_coverage = _coverage_value(
        pred.get("snapshot_model_coverage_ratio", pred.get("snapshot_coverage_ratio")),
        default=0.0,
    )
    if pred.get("snapshot_mid_m") is not None and snapshot_days:
        snapshot_importance = 58.0 + snapshot_weight * 45.0 + snapshot_support * 8.0
        snapshot_available = True
        snapshot_confidence = (
            snapshot_weight * 45.0
            + snapshot_support * 35.0
            + snapshot_coverage * 20.0
        )
        reserved_text = (
            f"{int(reserved):,} reserved"
            if reserved is not None else "reserved-seat sample"
        )
        matched = int(pickup.get("n_matched_showtimes") or 0)
        matched_text = f", {matched:,} matched showtimes" if matched else ""
        snapshot_evidence = (
            f"{reserved_text} for {', '.join(snapshot_days)}; "
            f"model coverage {snapshot_coverage:.0%}, support {snapshot_support:.0%}, "
            f"weight {snapshot_weight:.0%}{matched_text}"
        )
    else:
        snapshot_importance = 18.0
        snapshot_available = False
        snapshot_confidence = 0.0
        snapshot_evidence = "no usable future-day snapshot layer in this forecast"

    avg_showings = _positive_float(
        pred.get("seat_comp_avg_showings_per_cinema")
        or pred.get("avg_showings_per_cinema")
    )
    if avg_showings:
        showing_signal = _clamp((avg_showings - 2.0) / 6.0, 0.0, 1.0)
        showing_importance = 55.0 + showing_signal * 22.0
        showing_available = True
        showing_confidence = 70.0 + showing_signal * 20.0
        showing_evidence = (
            f"{avg_showings:.1f} showings per AMC theatre; "
            "screens/room density informs release scale and daily capacity"
        )
    else:
        showing_importance = 24.0
        showing_available = False
        showing_confidence = 0.0
        showing_evidence = "missing showings-per-theatre density"

    release_scale = pred.get("seat_comp_release_scale") or "unknown"
    metadata_source = pred.get("seat_comp_metadata_source") or "missing"
    if release_scale == "tentpole":
        release_importance = 71.0
    elif release_scale == "event":
        release_importance = 64.0
    elif release_scale == "standard":
        release_importance = 50.0
    elif release_scale == "niche":
        release_importance = 42.0
    else:
        release_importance = 25.0
    release_available = release_scale != "unknown"
    if not release_available:
        release_confidence = 0.0
    elif metadata_source == "csv":
        release_confidence = 85.0
    elif metadata_source == "title_inferred":
        release_confidence = 60.0
    else:
        release_confidence = 50.0
    release_evidence = (
        f"{release_scale} release profile"
        if release_scale != "unknown" else "missing release-scale metadata"
    )

    national_count = _positive_float(pred.get("national_theatre_count"))
    if national_count:
        integrated = bool(pred.get("theatre_count_model_integrated") and comps_active)
        footprint = national_release_footprint_factor(national_count)
        national_importance = 55.0 + (8.0 if integrated else 0.0)
        national_available = True
        national_confidence = 80.0 if integrated else 65.0
        national_evidence = (
            f"{int(national_count):,} national theatres; "
            f"non-linear footprint x{footprint:.3f}"
            f"{' integrated in comp regression' if integrated else ''}"
        )
    else:
        national_importance = 22.0
        national_available = False
        national_confidence = 0.0
        national_evidence = "missing national theatre count; model uses release-scale fallback"

    thursday_share = _positive_float(pred.get("seat_comp_thursday_share"))
    external_share = _positive_float(pred.get("seat_comp_external_thursday_share"))
    if not comps_active:
        comp_importance = 10.0
        comp_available = False
        comp_confidence = 0.0
        comp_evidence = "historical comps disabled for production forecast"
        comp_driver = "Historical comp Thursday share"
        comp_why = "Preview-share comps are tracked for diagnostics but excluded from the production forecast."
        comp_basis = "diagnostic weighted comps plus local settled Thursday history"
    elif thursday_share:
        local_share = _positive_float(pred.get("seat_comp_local_thursday_share"))
        local_n = int(pred.get("seat_comp_local_thursday_n") or 0)
        local_weight = _coverage_value(
            pred.get("seat_comp_local_thursday_weight"),
            default=0.0,
        )
        comp_importance = 48.0 + min(10.0, local_n * 2.0) + local_weight * 8.0
        comp_available = True
        comp_confidence = 55.0 + min(20.0, local_n * 3.0) + local_weight * 15.0
        share_bits = [f"used {thursday_share:.1%}"]
        if external_share:
            share_bits.append(f"external {external_share:.1%}")
        if local_share:
            share_bits.append(
                f"local {local_share:.1%} n={local_n} w={local_weight:.0%}"
            )
        comp_evidence = "; ".join(share_bits)
        comp_driver = "Historical comp Thursday share"
        comp_why = "Preview-share history calibrates how much of the weekend is already captured."
        comp_basis = "weighted comps plus local settled Thursday history"
    else:
        comp_importance = 24.0
        comp_available = False
        comp_confidence = 0.0
        comp_evidence = "missing historical comp Thursday share"
        comp_driver = "Historical comp Thursday share"
        comp_why = "Preview-share comps are tracked for diagnostics but excluded from the production forecast."
        comp_basis = "diagnostic weighted comps plus local settled Thursday history"

    top_comps = pred.get("seat_comp_top_comps") or []
    audience_features = pred.get("seat_comp_audience_features") or ""
    if not comps_active:
        metadata_importance = 16.0
        metadata_available = False
        metadata_confidence = 0.0
        metadata_evidence = "comp metadata disabled for production forecast"
    elif top_comps:
        comp_names = ", ".join(comp.get("movie", "") for comp in top_comps[:3])
        metadata_importance = 45.0 + min(8.0, len(top_comps) * 1.5)
        metadata_available = True
        metadata_confidence = 72.0 if metadata_source == "csv" else 56.0
        metadata_evidence = (
            f"{metadata_source} metadata; comps {comp_names}"
            f"{f'; {audience_features}' if audience_features else ''}"
        )
    elif metadata_source != "missing":
        metadata_importance = 34.0
        metadata_available = True
        metadata_confidence = 45.0
        metadata_evidence = f"{metadata_source} metadata, but no weighted comps"
    else:
        metadata_importance = 18.0
        metadata_available = False
        metadata_confidence = 0.0
        metadata_evidence = "missing genre/franchise/audience metadata"

    social = pred.get("social_signal") or {}
    if social:
        quality = _coverage_value(social.get("signal_quality"), default=0.0)
        integrated = bool(pred.get("social_signal_model_integrated") and comps_active)
        social_importance = 24.0 + quality * 25.0 + (5.0 if integrated else 0.0)
        social_available = True
        social_confidence = quality * 100.0
        platforms = ", ".join(social.get("platforms") or [])
        if integrated:
            social_evidence = "integrated into comp regression"
        else:
            social_evidence = f"standalone x{social.get('factor', 1.0):.3f}"
        social_evidence += (
            f"; buzz {social.get('buzz_score', 0):+.2f}, "
            f"sentiment {social.get('sentiment_score', 0):+.2f}, "
            f"quality {quality:.0%}"
            f"{f', {platforms}' if platforms else ''}"
        )
    else:
        social_importance = 12.0
        social_available = False
        social_confidence = 0.0
        social_evidence = "no current social signal; neutral in forecast"

    drivers = [
        _importance_driver(
            1,
            "Thursday sampled AMC gross",
            thursday_importance,
            thursday_evidence,
            "Observed same-week paid-seat demand is the strongest anchor.",
            "seat rows -> sampled AMC gross -> national daily gross",
            available=thursday_available,
            confidence=thursday_confidence,
            model_impact_m=(
                thursday_day / 1_000_000 if thursday_day is not None else None
            ),
        ),
        _importance_driver(
            2,
            "Snapshot reserved seats for Fri/Sat/Sun",
            snapshot_importance,
            snapshot_evidence,
            "Future-day reservations indicate remaining weekend demand before final seat counts.",
            "pre-reservation rows -> pickup/frontload layer",
            available=snapshot_available,
            confidence=snapshot_confidence,
            model_impact_m=pred.get("snapshot_mid_m"),
        ),
        _importance_driver(
            3,
            "Showings per AMC theatre",
            showing_importance,
            showing_evidence,
            "Per-theatre show density captures room allocation and distributor/exhibitor confidence.",
            "captured showtimes divided by sampled AMC theatres",
            available=showing_available,
            confidence=showing_confidence,
        ),
        _importance_driver(
            4,
            "Release scale / tentpole flag",
            release_importance,
            release_evidence,
            "Release class controls footprint and day-shape priors around the seat forecast.",
            "metadata plus observed AMC footprint",
            available=release_available,
            confidence=release_confidence,
        ),
        _importance_driver(
            5,
            "National theatre count",
            national_importance,
            national_evidence,
            "National footprint converts tracked AMC demand to the wider market non-linearly.",
            "reported theatre count -> footprint factor",
            available=national_available,
            confidence=national_confidence,
        ),
        _importance_driver(
            6,
            comp_driver,
            comp_importance,
            comp_evidence,
            comp_why,
            comp_basis,
            available=comp_available,
            confidence=comp_confidence,
        ),
        _importance_driver(
            7,
            "Genre/franchise/audience metadata",
            metadata_importance,
            metadata_evidence,
            "Metadata remains diagnostic when comps are disabled; release scale is handled separately.",
            "genre, franchise, audience, rating, scores, and social metadata",
            available=metadata_available,
            confidence=metadata_confidence,
        ),
        _importance_driver(
            8,
            "Social signal",
            social_importance,
            social_evidence,
            "Social buzz/sentiment is secondary and capped unless trained into comp regression.",
            "social rows -> bounded adjustment or comp-regression feature",
            available=social_available,
            confidence=social_confidence,
        ),
    ]

    strength_order = sorted(
        drivers,
        key=lambda item: (-item["importance"], item["priority_rank"]),
    )
    for strength_rank, driver in enumerate(strength_order, start=1):
        driver["strength_rank"] = strength_rank

    # Keep the user-facing order stable and intentional. `rank` is the model
    # priority stack; `strength_rank` is where the current available evidence
    # sorts by computed driver strength.
    return drivers


def _metadata_with_social_signal(target, social):
    """Return TargetMetadata enriched with current-weekend social fields."""
    if not target or not social:
        return target
    social_media_universe_m = _positive_float(social.get("social_media_universe_m")) or 0.0
    if social_media_universe_m <= 0:
        # For generic platform rows we only have the model's reach proxy. Keep
        # that on the same rough million-user scale so historical RelishMix SMU
        # can still train the comp regression when current social rows exist.
        social_media_universe_m = max(float(social.get("reach") or 0.0), 0.0) / 1000.0
    quality = _coverage_value(social.get("signal_quality"), default=0.0)
    sentiment = float(social.get("sentiment_score") or 0.0)
    buzz = float(social.get("buzz_score") or 0.0)
    if quality < SOCIAL_LAYER_MIN_QUALITY_FOR_ADJUSTMENT:
        sentiment = 0.0
        buzz = 0.0
    return replace(
        target,
        social_media_universe_m=social_media_universe_m,
        social_sentiment_score=sentiment,
        social_buzz_score=buzz,
    )


def complete_snapshot_covers_missing_days(pred):
    """Whether snapshot rows directly fill every missing weekend day.

    If Thursday is the only regular/actual seat day, the seat-only total is a
    day-shape extrapolation. When calibrated snapshots exist for every missing
    Fri/Sat/Sun day, use that daily evidence directly instead of blending it
    down against the extrapolated Thursday total.
    """
    snapshot_mid = _positive_float(pred.get("snapshot_mid_m"))
    if snapshot_mid is None:
        return False
    profile = pred.get("missing_data_profile") or {}
    missing_days = set(profile.get("missing_days") or [])
    if not missing_days:
        return False
    missing_weekend_days = {
        day for day in missing_days
        if day in OPENING_WEEKEND_DAYS
    }
    if not missing_weekend_days:
        return False
    snapshot_days = set(pred.get("snapshot_days") or [])
    if not missing_weekend_days.issubset(snapshot_days):
        return False

    coverage = _coverage_value(
        pred.get("snapshot_model_coverage_ratio", pred.get("snapshot_coverage_ratio")),
        default=0.0,
    )
    support = _coverage_value(
        pred.get("snapshot_calibration_support_factor"),
        default=0.0,
    )
    weight = _coverage_value(pred.get("snapshot_model_weight"), default=0.0)
    if coverage < 0.50:
        return False
    return weight > 0 or support >= 0.20


def select_regression_prediction(pred, cal=None):
    """Attach the model-driven regression forecast.

    Polymarket and published trade estimates remain context only. Calibration,
    strategy, and reporting use the actual-predictive regression line. Historical
    comps are retained as diagnostics, but the production forecast is anchored
    to observed seat demand plus snapshot, theatre-footprint, residual, and
    social layers.
    """
    use_comps = bool(COMPS_IN_FORECAST)
    comp_line_present = any(
        pred.get(key) is not None
        for key in (
            "seat_primary_mid_m",
            "seat_comp_adjusted_mid_m",
            "seat_comp_mid_m",
        )
    )
    if comp_line_present and not use_comps:
        pred["comp_model_excluded"] = True

    if use_comps and pred.get("seat_primary_mid_m") is not None:
        source = "seat-primary-regression"
        mid = pred["seat_primary_mid_m"]
        low = pred["seat_primary_low_m"]
        high = pred["seat_primary_high_m"]
        w_direct = pred.get("seat_primary_w_direct")
        w_comp = pred.get("seat_primary_w_comp")
        if w_direct is not None and w_comp is not None:
            basis = f"direct seats ({w_direct:.0%}) + seat/comp prior ({w_comp:.0%})"
        else:
            basis = "direct seats + seat/comp prior"
        uses_comps = True
    elif use_comps and pred.get("seat_comp_adjusted_mid_m") is not None:
        source = "seat+comp-coverage-adjusted-regression"
        mid = pred["seat_comp_adjusted_mid_m"]
        low = pred["seat_comp_adjusted_low_m"]
        high = pred["seat_comp_adjusted_high_m"]
        basis = pred.get("seat_comp_adjusted_basis")
        uses_comps = True
    elif use_comps and pred.get("seat_comp_mid_m") is not None:
        source = "seat+comp-regression"
        mid = pred["seat_comp_mid_m"]
        low = pred["seat_comp_low_m"]
        high = pred["seat_comp_high_m"]
        basis = pred.get("seat_comp_basis")
        uses_comps = True
    else:
        source = "seat-only-regression"
        mid = pred["seat_mid_m"]
        low = pred["seat_low_m"]
        high = pred["seat_high_m"]
        basis = "seat-only"
        uses_comps = False

    snapshot_mid = pred.get("snapshot_mid_m")
    disagreement_profile = model_component_disagreement_profile(
        pred,
        base_mid=mid,
        snapshot_mid=snapshot_mid,
        include_comp=use_comps,
    )
    pred["model_component_disagreement"] = disagreement_profile
    snapshot_primary = complete_snapshot_covers_missing_days(pred)
    if snapshot_primary:
        pred["snapshot_replaced_partial_seat_extrapolation"] = True
        pred["snapshot_replaced_seat_mid_m"] = mid
        pred["snapshot_replaced_seat_low_m"] = low
        pred["snapshot_replaced_seat_high_m"] = high
        mid = snapshot_mid
        low = pred.get("snapshot_low_m", snapshot_mid)
        high = pred.get("snapshot_high_m", snapshot_mid)
        source = "daily-seat-snapshot-regression"
        basis = "observed seat days + snapshot-filled missing days"
        uses_comps = False
    snapshot_weight = _coverage_value(pred.get("snapshot_model_weight"), default=0.0)
    if snapshot_mid is not None and snapshot_weight > 0 and not snapshot_primary:
        original_snapshot_weight = snapshot_weight
        snapshot_weight = _clamp(
            snapshot_weight * disagreement_profile.get("snapshot_weight_multiplier", 1.0),
            0.0,
            SNAPSHOT_LAYER_MAX_WEIGHT,
        )
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
        pred["snapshot_original_model_weight"] = round(original_snapshot_weight, 4)
        pred["snapshot_effective_model_weight"] = round(snapshot_weight, 4)
        if source == "seat-only-regression":
            source = "seat+snapshot-regression"
        elif "seat+comp" in source:
            source = "seat+comp+snapshot-regression"
        elif source == "seat-primary-regression":
            source = "seat-primary+snapshot-regression"
        else:
            source = f"{source}+snapshot"
        basis = f"{basis} + snapshot future days"

    range_buffer_m = _positive_float(disagreement_profile.get("range_buffer_m")) or 0.0
    if disagreement_profile.get("severity") in {"medium", "high"} and range_buffer_m > 0:
        low = max(0.0, low - range_buffer_m)
        high = high + range_buffer_m
        basis = f"{basis} + component disagreement penalty ({disagreement_profile['severity']})"

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

    social = pred.get("social_signal")
    if social and not pred.get("social_signal_model_integrated"):
        factor = _positive_float(social.get("factor")) or 1.0
        factor = _clamp(
            factor,
            1.0 - SOCIAL_LAYER_MAX_ADJUSTMENT,
            1.0 + SOCIAL_LAYER_MAX_ADJUSTMENT,
        )
        base_mid = mid
        mid = mid * factor
        low = low * factor
        high = high * factor
        social_delta = abs(mid - base_mid)
        low = max(0.0, low - social_delta * 0.20)
        high = high + social_delta * 0.20
        pred["social_base_mid_m"] = base_mid
        pred["social_factor"] = round(factor, 5)
        pred["social_adjustment_m"] = round(mid - base_mid, 3)
        pred["social_adjustment_pct"] = round((factor - 1.0) * 100.0, 2)
        source = f"{source}+social"
        basis = f"{basis} + social buzz/sentiment"
    elif social and pred.get("social_signal_model_integrated"):
        pred["social_factor"] = 1.0
        pred["social_adjustment_m"] = 0.0
        pred["social_adjustment_pct"] = 0.0
        pred["social_model_note"] = "social signal integrated into historical comp regression"

    pred["regression_mid_m"] = mid
    pred["regression_low_m"] = low
    pred["regression_high_m"] = high
    pred["regression_source"] = source
    pred["regression_basis"] = basis
    pred["regression_uses_comps"] = uses_comps
    pred["regression_uses_polymarket"] = False
    pred["model_forecast_mid_m"] = mid
    pred["model_forecast_low_m"] = low
    pred["model_forecast_high_m"] = high
    pred["model_forecast_source"] = source
    pred["model_forecast_basis"] = basis
    pred["model_forecast_uses_comps"] = uses_comps
    pred["model_forecast_uses_polymarket"] = False
    pred["forecast_feature_importance"] = forecast_feature_importance(pred)
    return pred


def regression_prediction_values(pred):
    """Return the point/range used for actual-focused model reporting."""
    if pred.get("regression_mid_m") is None:
        select_regression_prediction(pred)
    return pred["regression_mid_m"], pred["regression_low_m"], pred["regression_high_m"]


# ── Stage C: AMC → Total Domestic ────────────────────────────────────────────

def calibrated_amc_market_share(cal):
    """Current historical AMC/tracked-chain share prior."""
    share = cal["calibration_factors"].get("amc_market_share", DEFAULT_AMC_MARKET_SHARE)
    return max(DYNAMIC_AMC_SHARE_MIN_SHARE, min(DYNAMIC_AMC_SHARE_MAX_SHARE, share))


def amc_to_domestic(amc_revenue, cal, share_override=None):
    """Stage C: scale AMC revenue to total domestic market."""
    if share_override is None:
        share = calibrated_amc_market_share(cal)
    else:
        share = max(
            DYNAMIC_AMC_SHARE_MIN_SHARE,
            min(DYNAMIC_AMC_SHARE_MAX_SHARE, float(share_override)),
        )
    mid = amc_revenue / share
    # Uncertainty in market share: ±3 points, both bounds clamped away from 0
    low  = amc_revenue / min(DYNAMIC_AMC_SHARE_MAX_SHARE, share + 0.03)   # higher share → lower gross
    high = amc_revenue / max(DYNAMIC_AMC_SHARE_MIN_SHARE, share - 0.03)   # lower share  → higher gross
    # Sanity guard: ensure low ≤ mid ≤ high
    low  = min(low, mid)
    high = max(high, mid)
    return mid, low, high


def same_week_amc_share_anchor(day_name, amc_total, actual_gross, cal,
                               footprint_factor=1.0, coverage_ratio=None):
    """Infer this movie's tracked-AMC share from a reported daily actual."""
    if not amc_total or not actual_gross or actual_gross <= 0:
        return None
    day_scale = get_day_scale(cal, day_name)
    implied_raw = (amc_total * footprint_factor * day_scale) / actual_gross
    implied_share = _clamp(
        implied_raw,
        DYNAMIC_AMC_SHARE_MIN_SHARE,
        DYNAMIC_AMC_SHARE_MAX_SHARE,
    )
    prior_share = calibrated_amc_market_share(cal)
    coverage = _clamp(float(coverage_ratio if coverage_ratio is not None else 0.0), 0.0, 1.0)
    anchor_weight = DYNAMIC_AMC_SHARE_MAX_WEIGHT * coverage
    if anchor_weight <= 0:
        return None
    blended_share = (
        implied_share * anchor_weight
        + prior_share * (1.0 - anchor_weight)
    )
    return {
        "day": day_name,
        "prior_share": prior_share,
        "raw_implied_share": implied_raw,
        "implied_share": implied_share,
        "anchor_weight": anchor_weight,
        "blended_share": _clamp(
            blended_share,
            DYNAMIC_AMC_SHARE_MIN_SHARE,
            DYNAMIC_AMC_SHARE_MAX_SHARE,
        ),
        "coverage_ratio": coverage,
    }


def same_week_amc_share_anchor_for_day(anchors, target_day=None):
    """Blend same-week reported-actual AMC share anchors for a target day.

    A single same-week actual should transfer directly, preserving the original
    behavior. Once multiple actuals exist, weight them by weekend-day similarity
    so Friday dominates Saturday/Sunday but Thursday previews still contribute a
    small amount of movie-specific share information.
    """
    if not anchors:
        return None
    if isinstance(anchors, dict):
        anchors = [anchors]

    valid = []
    for anchor in anchors:
        if not isinstance(anchor, dict):
            continue
        blended = _positive_float(anchor.get("blended_share"))
        if blended is None:
            continue
        valid.append(anchor)

    if not valid:
        return None
    if len(valid) == 1:
        anchor = dict(valid[0])
        if target_day:
            anchor["target_day"] = target_day
        return anchor

    weighted = []
    for anchor in valid:
        base_weight = (
            _positive_float(anchor.get("anchor_weight"))
            or _positive_float(anchor.get("coverage_ratio"))
            or 1.0
        )
        similarity = 1.0
        if target_day:
            similarity = snapshot_day_similarity(anchor.get("day"), target_day)
        weight = base_weight * similarity
        if weight > 0:
            weighted.append((anchor, weight))

    if not weighted:
        latest = dict(valid[-1])
        if target_day:
            latest["target_day"] = target_day
        return latest

    total_weight = sum(weight for _, weight in weighted)

    def weighted_average(field, default=None):
        values = []
        for anchor, weight in weighted:
            value = _positive_float(anchor.get(field))
            if value is None:
                continue
            values.append((value, weight))
        if not values:
            return default
        total = sum(weight for _, weight in values)
        return sum(value * weight for value, weight in values) / total

    day_labels = []
    for anchor, _ in weighted:
        day = anchor.get("day")
        if day and day not in day_labels:
            day_labels.append(day)

    blended_share = weighted_average("blended_share")
    if blended_share is None:
        return None

    return {
        "day": "+".join(day_labels),
        "days": day_labels,
        "target_day": target_day,
        "prior_share": weighted_average("prior_share"),
        "raw_implied_share": weighted_average("raw_implied_share"),
        "implied_share": weighted_average("implied_share"),
        "anchor_weight": _clamp(total_weight, 0.0, 1.0),
        "blended_share": _clamp(
            blended_share,
            DYNAMIC_AMC_SHARE_MIN_SHARE,
            DYNAMIC_AMC_SHARE_MAX_SHARE,
        ),
        "coverage_ratio": weighted_average("coverage_ratio", default=0.0),
        "anchors": [
            {
                "day": anchor.get("day"),
                "blended_share": anchor.get("blended_share"),
                "weight": round(weight, 4),
            }
            for anchor, weight in weighted
        ],
    }


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


def _showtime_id_from_url(value):
    match = re.search(r"/showtimes/([^/?#]+)/seats", value or "")
    return match.group(1) if match else ""


def _showtime_match_key(row):
    """Stable identity for joining snapshot rows to later seat-count rows."""
    movie_key = _movie_lookup_key(row.get("movie_title", ""))
    date_str = row.get("show_date") or row.get("date") or ""
    showtime_id = _showtime_id_from_url(row.get("amc_seat_map_url", "")) or row.get("showtime_id")
    if showtime_id:
        return ("id", movie_key, date_str, str(showtime_id))

    theatre = re.sub(r"\s+", " ", (row.get("theatre_name") or "").strip().lower())
    showtime = re.sub(r"\s+", "", (row.get("showtime") or "").strip().lower())
    fmt = re.sub(
        r"\s+",
        " ",
        (
            row.get("auditorium_type")
            or row.get("auditorium_name")
            or row.get("format")
            or ""
        ).strip().lower(),
    )
    total_seats = str(_parse_numeric(row.get("total_seats", ""), default=0))
    return ("fallback", movie_key, date_str, theatre, showtime, fmt, total_seats)


def _latest_seat_showtime_rows(rows):
    latest = {}
    for row in rows or []:
        key = _showtime_match_key(row)
        sort_key = (
            row.get("run_id", ""),
            row.get("check_time", ""),
            row.get("minutes_after_showtime", ""),
        )
        prev = latest.get(key)
        if not prev or sort_key > prev[0]:
            latest[key] = (sort_key, row)
    return {key: row for key, (_, row) in latest.items()}


def snapshot_pickup_profile(snapshot_rows, seat_rows, cal):
    """Compare pre-reservation snapshots to later seat-count rows.

    The delta between reserved seats at snapshot time and final/projected
    seats sold is the combined late-reservation + walk-in pickup signal. We
    use it as a same-week calibration layer before comparing the resulting
    daily estimates to reported box-office actuals.
    """
    # Unlike forward-looking prediction, pickup calibration intentionally uses
    # earlier same-week snapshot slices that now have final seat-count rows.
    latest_snapshots = _latest_snapshot_showtime_rows(snapshot_rows or [])
    latest_seats = _latest_seat_showtime_rows(seat_rows or [])
    if not latest_snapshots or not latest_seats:
        return None

    matched = []
    per_day = {}
    snapshot_candidate_counts = {}
    for snapshot in latest_snapshots:
        day = snapshot.get("day_of_week") or _snapshot_day_name(
            snapshot.get("show_date", ""), [snapshot]
        )
        if day:
            snapshot_candidate_counts[day] = snapshot_candidate_counts.get(day, 0) + 1
        seat = latest_seats.get(_showtime_match_key(snapshot))
        if not seat:
            continue
        snapshot_result = estimate_snapshot_showtime_revenue(snapshot)
        seat_result = estimate_theatre_daily_revenue(seat, cal)
        if not snapshot_result or not seat_result:
            continue
        snapshot_revenue = _positive_float(snapshot_result.get("revenue"))
        final_revenue = _positive_float(seat_result.get("revenue"))
        if not snapshot_revenue or not final_revenue:
            continue

        reserved = _parse_numeric(snapshot.get("reserved_seats", 0), default=0)
        total = _parse_numeric(snapshot.get("total_seats", 0), default=0)
        final_sold_raw = _parse_numeric(seat.get("seats_sold", 0), default=0)
        final_projected_sold = seat_result["projected_occ"] * seat_result["total_seats"]
        projected_reserved = snapshot_result["projected_occ"] * snapshot_result["total_seats"]
        day = day or seat.get("day_of_week", "")
        item = {
            "day": day,
            "snapshot_revenue": snapshot_revenue,
            "final_revenue": final_revenue,
            "reserved": reserved,
            "total_seats": total,
            "projected_reserved": projected_reserved,
            "final_sold_raw": final_sold_raw,
            "final_projected_sold": final_projected_sold,
            "post_snapshot_pickup": max(0.0, final_projected_sold - reserved),
        }
        matched.append(item)
        bucket = per_day.setdefault(day, {
            "snapshot_revenue": 0.0,
            "final_revenue": 0.0,
            "projected_reserved": 0.0,
            "final_projected_sold": 0.0,
            "matched": 0,
        })
        bucket["snapshot_revenue"] += snapshot_revenue
        bucket["final_revenue"] += final_revenue
        bucket["projected_reserved"] += projected_reserved
        bucket["final_projected_sold"] += final_projected_sold
        bucket["matched"] += 1

    if not matched:
        return None

    snapshot_revenue = sum(item["snapshot_revenue"] for item in matched)
    final_revenue = sum(item["final_revenue"] for item in matched)
    reserved_total = sum(item["reserved"] for item in matched)
    final_sold_raw_total = sum(item["final_sold_raw"] for item in matched)
    projected_reserved_total = sum(item["projected_reserved"] for item in matched)
    final_projected_total = sum(item["final_projected_sold"] for item in matched)
    pickup_total = max(0.0, final_projected_total - reserved_total)
    raw_seat_scale = (
        final_projected_total / projected_reserved_total
        if projected_reserved_total > 0 else 1.0
    )
    raw_revenue_scale = final_revenue / snapshot_revenue if snapshot_revenue > 0 else 1.0
    anchors = []
    for day, bucket in sorted(per_day.items()):
        day_snapshot_revenue = bucket["snapshot_revenue"]
        if day_snapshot_revenue <= 0:
            continue
        candidates = max(1, snapshot_candidate_counts.get(day, bucket["matched"]))
        weight = _clamp(bucket["matched"] / candidates, 0.0, 1.0)
        # The pickup layer estimates seat growth after the snapshot. Ticket
        # price and national box-office conversion are calibrated separately.
        day_raw_scale = (
            bucket["final_projected_sold"] / bucket["projected_reserved"]
            if bucket["projected_reserved"] > 0 else raw_seat_scale
        )
        anchors.append({
            "day": day,
            "scale": _clamp(
                day_raw_scale,
                SNAPSHOT_SAME_WEEK_SCALE_MIN,
                SNAPSHOT_SAME_WEEK_SCALE_MAX,
            ),
            "raw_scale": day_raw_scale,
            "weight": weight,
            "matched_showtimes": bucket["matched"],
        })

    return {
        "n_matched_showtimes": len(matched),
        "reserved_seats_at_snapshot": int(round(reserved_total)),
        "projected_reserved_seats": round(projected_reserved_total, 2),
        "final_sold_seats": int(round(final_sold_raw_total)),
        "final_projected_sold_seats": round(final_projected_total, 2),
        "post_snapshot_pickup_seats": int(round(pickup_total)),
        "post_snapshot_pickup_share": (
            pickup_total / final_projected_total if final_projected_total > 0 else 0.0
        ),
        "raw_projected_revenue_scale": raw_seat_scale,
        "raw_revenue_scale": raw_revenue_scale,
        "projected_revenue_scale": _clamp(
            raw_seat_scale,
            SNAPSHOT_SAME_WEEK_SCALE_MIN,
            SNAPSHOT_SAME_WEEK_SCALE_MAX,
        ),
        "reservation_pickup_multiplier": (
            final_projected_total / reserved_total if reserved_total > 0 else None
        ),
        "snapshot_projected_revenue": snapshot_revenue,
        "final_seat_revenue": final_revenue,
        "anchors": anchors,
    }


def snapshot_day_similarity(anchor_day, target_day):
    """How transferable one same-week pickup anchor is to another day."""
    anchor = anchor_day if anchor_day in OPENING_WEEKEND_DAYS else None
    target = target_day if target_day in OPENING_WEEKEND_DAYS else None
    if not anchor or not target:
        return 0.0
    if anchor == target:
        return 1.0
    if anchor == "Thursday":
        return {
            "Friday": 0.45,
            "Saturday": 0.08,
            "Sunday": 0.05,
        }.get(target, 0.0)
    if target == "Thursday":
        return {
            "Friday": 0.35,
            "Saturday": 0.20,
            "Sunday": 0.15,
        }.get(anchor, 0.0)
    pair = frozenset((anchor, target))
    if pair == frozenset(("Friday", "Saturday")):
        return 0.90
    if pair == frozenset(("Saturday", "Sunday")):
        return 0.85
    if pair == frozenset(("Friday", "Sunday")):
        return 0.75
    return 0.35


def snapshot_pickup_scale_for_day(day_name, anchors, fallback_scale=1.0):
    """Day-aware pickup scale for future snapshot rows."""
    weighted = []
    for anchor in anchors or []:
        scale = _positive_float(anchor.get("scale"))
        if not scale:
            continue
        similarity = snapshot_day_similarity(anchor.get("day"), day_name)
        if similarity <= 0:
            continue
        weight = (_positive_float(anchor.get("weight")) or 1.0) * similarity
        if weight > 0:
            weighted.append((scale, weight))
    if not weighted:
        return _clamp(
            _positive_float(fallback_scale) or 1.0,
            SNAPSHOT_SAME_WEEK_SCALE_MIN,
            SNAPSHOT_SAME_WEEK_SCALE_MAX,
        )
    total = sum(weight for _, weight in weighted)
    scale = sum(scale * weight for scale, weight in weighted) / total
    return _clamp(scale, SNAPSHOT_SAME_WEEK_SCALE_MIN, SNAPSHOT_SAME_WEEK_SCALE_MAX)


def estimate_snapshot_day(rows, date_str, cal, expected_amc_theatres,
                          expected_timezone_counts=None,
                          theatre_timezone_map=None,
                          national_theatre_count=None,
                          share_override=None):
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
    strategic_expected_theatres = snapshot_strategic_expected_theatres(
        expected_amc_theatres
    )
    strategic_coverage_ratio = (
        min(1.0, n_amc_theatres / strategic_expected_theatres)
        if strategic_expected_theatres else coverage_ratio
    )
    effective_coverage_ratio = coverage_ratio
    if coverage_ratio is not None and tz_profile["missing_timezones"]:
        effective_coverage_ratio = coverage_ratio * tz_profile["coverage_factor"]
    effective_strategic_coverage_ratio = strategic_coverage_ratio
    if strategic_coverage_ratio is not None and tz_profile["missing_timezones"]:
        effective_strategic_coverage_ratio = (
            strategic_coverage_ratio * tz_profile["coverage_factor"]
        )

    domestic_mid, domestic_low, domestic_high = amc_to_domestic(
        amc_total,
        cal,
        share_override=share_override,
    )
    pre_footprint_mid = domestic_mid
    pre_footprint_low = domestic_low
    pre_footprint_high = domestic_high
    footprint_factor = national_release_footprint_factor(national_theatre_count)
    if national_theatre_count:
        domestic_mid *= footprint_factor
        domestic_low *= footprint_factor
        domestic_high *= footprint_factor

    lead_minutes = [
        result.get("minutes_until_showtime")
        for result in per_showtime_results
        if result.get("minutes_until_showtime") is not None
    ]
    median_lead_minutes = statistics.median(lead_minutes) if lead_minutes else None
    lead_bucket = snapshot_lead_bucket(median_lead_minutes)
    snapshot_day_scale = get_snapshot_to_day_scale(cal, day_name)
    snapshot_lead_scale = get_snapshot_lead_scale(cal, lead_bucket)
    snapshot_scale = get_snapshot_to_day_scale(cal, day_name, lead_bucket)
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
        "pre_footprint_domestic_mid": pre_footprint_mid,
        "pre_footprint_domestic_low": pre_footprint_low,
        "pre_footprint_domestic_high": pre_footprint_high,
        "domestic_mid": domestic_mid * snapshot_scale,
        "domestic_low": domestic_low * snapshot_scale,
        "domestic_high": domestic_high * snapshot_scale,
        "national_footprint_factor": footprint_factor,
        "amc_market_share_used": (
            share_override if share_override else calibrated_amc_market_share(cal)
        ),
        "amc_market_share_source": (
            "same_week_actual_anchor" if share_override else "calibration"
        ),
        "snapshot_scale": snapshot_scale,
        "snapshot_day_scale": snapshot_day_scale,
        "snapshot_lead_scale": snapshot_lead_scale,
        "lead_bucket": lead_bucket,
        "median_minutes_until_showtime": median_lead_minutes,
        "n_theatres": n_amc_theatres,
        "expected_theatres": expected_amc_theatres,
        "coverage_ratio": coverage_ratio,
        "effective_coverage_ratio": effective_coverage_ratio,
        "strategic_expected_theatres": strategic_expected_theatres,
        "strategic_coverage_ratio": strategic_coverage_ratio,
        "effective_strategic_coverage_ratio": effective_strategic_coverage_ratio,
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
        if regular_day_needs_snapshot_support(day_name, regular):
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


def snapshot_same_week_support_floor(same_week_anchors):
    """Same-week actual days make snapshot calibration materially more trusted."""
    anchors_by_day = {}
    for anchor in same_week_anchors or []:
        day = anchor.get("day")
        if day not in OPENING_WEEKEND_DAYS:
            continue
        anchors_by_day[day] = max(
            anchors_by_day.get(day, 0.0),
            _coverage_value(anchor.get("weight"), default=0.0),
        )
    anchor_days = set(anchors_by_day)
    anchor_weight = sum(anchors_by_day.values())
    if len(anchor_days) >= 2:
        confidence = _clamp(anchor_weight / 0.45, 0.0, 1.0)
        return SNAPSHOT_ONE_ANCHOR_SUPPORT_FLOOR + (
            (SNAPSHOT_TWO_ANCHOR_SUPPORT_FLOOR - SNAPSHOT_ONE_ANCHOR_SUPPORT_FLOOR)
            * confidence
        )
    if len(anchor_days) == 1:
        confidence = _clamp(anchor_weight / 0.25, 0.0, 1.0)
        return SNAPSHOT_ONE_ANCHOR_SUPPORT_FLOOR * confidence
    return 0.0


def snapshot_layer_model_weight(snapshot_coverage, snapshot_missing_share,
                                snapshot_support_factor, same_week_anchors):
    """Blend weight for snapshot future-day demand.

    Snapshot runs intentionally sample a smaller high-signal theatre set, so
    linear theatre coverage understates their value. Use sqrt coverage and
    same-week actual anchors to make calibrated future-day snapshots matter.
    """
    coverage = _coverage_value(snapshot_coverage, default=0.0)
    coverage_signal = sqrt(coverage) if coverage > 0 else 0.0
    missing_share = _clamp(snapshot_missing_share, 0.0, 1.0)
    missing_signal = SNAPSHOT_MISSING_SHARE_SIGNAL_FLOOR + (
        (1.0 - SNAPSHOT_MISSING_SHARE_SIGNAL_FLOOR) * missing_share
    )
    same_week_floor = snapshot_same_week_support_floor(same_week_anchors)
    support_signal = max(
        _clamp(snapshot_support_factor, 0.0, 1.0),
        same_week_floor,
    )
    weight = (
        SNAPSHOT_LAYER_MAX_WEIGHT
        * coverage_signal
        * missing_signal
        * support_signal
    )
    return {
        "weight": _clamp(weight, 0.0, SNAPSHOT_LAYER_MAX_WEIGHT),
        "coverage_signal": coverage_signal,
        "missing_share_signal": missing_signal,
        "support_signal": support_signal,
        "same_week_support_floor": same_week_floor,
    }


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


def apply_snapshot_day_shape_prior(details, day_shape_prior,
                                   support_factor=None):
    """Anchor partial pre-reservation reads to the seat-derived day shape."""
    prior_mid = _positive_float(day_shape_prior)
    if not details or not prior_mid:
        return details

    coverage = _coverage_value(
        details.get(
            "effective_strategic_coverage_ratio",
            details.get("effective_coverage_ratio", details.get("coverage_ratio")),
        ),
        default=0.0,
    )
    support = _coverage_value(
        support_factor
        if support_factor is not None
        else details.get("snapshot_calibration_support_factor"),
        default=0.50,
    )
    signal_weight = _clamp(
        sqrt(coverage) * SNAPSHOT_DAY_SHAPE_MAX_SIGNAL_WEIGHT * support,
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


def snapshot_frontload_profile(snapshot_details, day_shape_priors,
                               support_factor=None):
    """Use the snapshot day mix to detect frontloaded/backloaded demand.

    The snapshot layer should not only say "there are seats reserved"; it should
    say where those reservations sit inside the weekend. A Friday-heavy mix is a
    frontload warning, while stronger Saturday/Sunday reservations should pull
    the missing-day priors away from a Friday-heavy shape.
    """
    candidate_days = [
        day for day in ("Friday", "Saturday", "Sunday")
        if day in snapshot_details and day in day_shape_priors
    ]
    snapshot_values = {}
    prior_values = {}
    coverage_values = {}
    for day in candidate_days:
        snapshot_mid = _positive_float(
            (snapshot_details.get(day) or {}).get("domestic_mid")
        )
        prior_mid = _positive_float(day_shape_priors.get(day))
        if not snapshot_mid or not prior_mid:
            continue
        snapshot_values[day] = snapshot_mid
        prior_values[day] = prior_mid
        coverage_values[day] = (
            (snapshot_details.get(day) or {}).get(
                "effective_strategic_coverage_ratio",
                (snapshot_details.get(day) or {}).get(
                    "effective_coverage_ratio",
                    (snapshot_details.get(day) or {}).get("coverage_ratio"),
                ),
            )
        )

    if len(snapshot_values) < 2:
        return {}

    snapshot_total = sum(snapshot_values.values())
    prior_total = sum(prior_values.values())
    if snapshot_total <= 0 or prior_total <= 0:
        return {}

    snapshot_shares = {
        day: value / snapshot_total
        for day, value in snapshot_values.items()
    }
    prior_shares = {
        day: value / prior_total
        for day, value in prior_values.items()
    }
    relative_demand = {
        day: (
            snapshot_shares[day] / prior_shares[day]
            if prior_shares.get(day) else 1.0
        )
        for day in snapshot_values
    }

    friday_snapshot_share = snapshot_shares.get("Friday")
    friday_prior_share = prior_shares.get("Friday")
    rest_days = [
        day for day in ("Saturday", "Sunday")
        if day in snapshot_shares and day in prior_shares
    ]
    if friday_snapshot_share is not None and friday_prior_share and rest_days:
        snapshot_rest_share = sum(snapshot_shares[day] for day in rest_days)
        prior_rest_share = sum(prior_shares[day] for day in rest_days)
        if snapshot_rest_share > 0 and prior_rest_share > 0:
            frontload_ratio = (
                (friday_snapshot_share / snapshot_rest_share)
                / (friday_prior_share / prior_rest_share)
            )
        else:
            frontload_ratio = 1.0
    else:
        frontload_ratio = 1.0

    if frontload_ratio >= 1.12:
        classification = "frontloaded"
    elif frontload_ratio <= 0.88:
        classification = "backloaded"
    else:
        classification = "neutral"

    avg_coverage = _coverage_average(coverage_values) or 0.0
    support = _coverage_value(support_factor, default=0.50)
    day_completeness = len(snapshot_values) / 3.0
    confidence = _clamp(
        sqrt(max(0.0, avg_coverage)) * support * day_completeness,
        0.0,
        1.0,
    )

    effective_confidence = (
        confidence if confidence >= SNAPSHOT_FRONTLOAD_MIN_CONFIDENCE else 0.0
    )
    raw_shift = min(1.0, abs(frontload_ratio - 1.0) / 0.75)
    adjustment_strength = (
        SNAPSHOT_FRONTLOAD_MAX_PRIOR_SHIFT
        * raw_shift
        * effective_confidence
    )
    multipliers = {}
    for day, relative in relative_demand.items():
        multipliers[day] = _clamp(
            1.0 + ((relative - 1.0) * adjustment_strength),
            1.0 - SNAPSHOT_FRONTLOAD_MAX_PRIOR_SHIFT,
            1.0 + SNAPSHOT_FRONTLOAD_MAX_PRIOR_SHIFT,
        )

    adjusted_priors = {
        day: prior_values[day] * multipliers.get(day, 1.0)
        for day in prior_values
    }
    adjusted_total = sum(adjusted_priors.values())
    if adjusted_total > 0:
        normalizer = prior_total / adjusted_total
        adjusted_priors = {
            day: value * normalizer
            for day, value in adjusted_priors.items()
        }

    return {
        "classification": classification,
        "confidence": round(confidence, 4),
        "frontload_ratio": round(frontload_ratio, 4),
        "snapshot_shares": {
            day: round(value, 4)
            for day, value in snapshot_shares.items()
        },
        "prior_shares": {
            day: round(value, 4)
            for day, value in prior_shares.items()
        },
        "relative_demand": {
            day: round(value, 4)
            for day, value in relative_demand.items()
        },
        "day_multipliers": {
            day: round(value, 4)
            for day, value in multipliers.items()
        },
        "adjusted_day_shape_priors": adjusted_priors,
        "average_coverage": round(avg_coverage, 4),
        "support_factor": round(support, 4),
    }


def build_snapshot_future_layer(snapshot_data, regular_daily_details, cal,
                                expected_amc_theatres, expected_timezone_counts=None,
                                theatre_timezone_map=None,
                                national_theatre_count=None,
                                regular_seat_data=None,
                                amc_share_anchor=None,
                                amc_share_anchors=None):
    """Use snapshots only for opening-weekend days without seat-count actuals."""
    if not snapshot_data:
        return None

    all_snapshot_details = {}
    ignored_days = []
    share_anchor_inputs = (
        amc_share_anchors
        if amc_share_anchors is not None
        else ([amc_share_anchor] if isinstance(amc_share_anchor, dict) else [])
    )
    share_anchor_summary = same_week_amc_share_anchor_for_day(share_anchor_inputs)
    for date_str, rows in sorted(snapshot_data.items()):
        if not rows:
            continue
        day_name = _snapshot_day_name(date_str, rows)
        if day_name not in OPENING_WEEKEND_DAYS:
            continue
        share_anchor_for_day = same_week_amc_share_anchor_for_day(
            share_anchor_inputs,
            target_day=day_name,
        )
        share_override = (
            share_anchor_for_day.get("blended_share")
            if share_anchor_for_day else None
        )
        details = estimate_snapshot_day(
            rows,
            date_str,
            cal,
            expected_amc_theatres,
            expected_timezone_counts=expected_timezone_counts,
            theatre_timezone_map=theatre_timezone_map,
            national_theatre_count=national_theatre_count,
            share_override=share_override,
        )
        if details:
            if share_anchor_for_day:
                details["amc_market_share_anchor"] = share_anchor_for_day
            all_snapshot_details[day_name] = details

    aggregate_same_week_scale, aggregate_same_week_anchors = same_week_snapshot_scale(
        all_snapshot_details,
        regular_daily_details,
    )
    pickup_profile = snapshot_pickup_profile(
        [
            row
            for rows in snapshot_data.values()
            for row in rows
        ],
        [
            row
            for rows in (regular_seat_data or {}).values()
            for row in rows
        ],
        cal,
    )
    if pickup_profile and pickup_profile.get("n_matched_showtimes", 0) > 0:
        same_week_scale = pickup_profile["projected_revenue_scale"]
        same_week_anchors = pickup_profile.get("anchors", [])
        same_week_scale_source = "matched_showtime_pickup"
        same_week_day_scales = {
            day: snapshot_pickup_scale_for_day(
                day,
                same_week_anchors,
                fallback_scale=same_week_scale,
            )
            for day in all_snapshot_details
        }
    else:
        same_week_scale = aggregate_same_week_scale
        same_week_anchors = aggregate_same_week_anchors
        same_week_scale_source = "aggregate_day_estimate"
        same_week_day_scales = {
            day: same_week_scale
            for day in all_snapshot_details
        }

    day_shape_priors = regular_day_shape_priors(regular_daily_details, cal)
    same_week_support_floor = snapshot_same_week_support_floor(same_week_anchors)
    pending_snapshot_details = {}
    for day_name, details in all_snapshot_details.items():
        regular_details = regular_daily_details.get(day_name)
        supports_partial_regular_day = regular_day_needs_snapshot_support(
            day_name,
            regular_details,
        )
        if regular_details and not supports_partial_regular_day:
            ignored_days.append(day_name)
            continue
        day_same_week_scale = same_week_day_scales.get(day_name, same_week_scale)
        scaled_details = apply_same_week_snapshot_scale(
            details,
            day_same_week_scale,
        )
        support_info = snapshot_calibration_support_factor(
            cal,
            day_name,
            scaled_details.get("lead_bucket"),
        )
        shape_support = max(
            support_info["factor"],
            same_week_support_floor,
        )
        scaled_details = dict(scaled_details)
        scaled_details["same_week_snapshot_day_scale"] = round(day_same_week_scale, 4)
        pending_snapshot_details[day_name] = {
            "scaled_details": scaled_details,
            "regular_details": regular_details,
            "supports_partial_regular_day": supports_partial_regular_day,
            "shape_support": shape_support,
            "support_info": support_info,
        }

    profile_support_values = []
    day_weights = get_day_weights(cal)
    for day_name, pending in pending_snapshot_details.items():
        weight = _positive_float(day_weights.get(day_name)) or 0.0
        profile_support_values.append((pending["shape_support"], weight))
    positive_profile_support = [
        (factor, weight)
        for factor, weight in profile_support_values
        if factor is not None and weight > 0
    ]
    if positive_profile_support:
        profile_support_factor = (
            sum(factor * weight for factor, weight in positive_profile_support)
            / sum(weight for _, weight in positive_profile_support)
        )
    elif profile_support_values:
        profile_support_factor = (
            sum(factor for factor, _ in profile_support_values if factor is not None)
            / len(profile_support_values)
        )
    else:
        profile_support_factor = same_week_support_floor or 0.0

    frontload_profile = snapshot_frontload_profile(
        {
            day: pending["scaled_details"]
            for day, pending in pending_snapshot_details.items()
        },
        day_shape_priors,
        support_factor=profile_support_factor,
    )
    adjusted_day_shape_priors = (
        frontload_profile.get("adjusted_day_shape_priors")
        if frontload_profile else {}
    )

    snapshot_details = {}
    for day_name, pending in pending_snapshot_details.items():
        scaled_details = pending["scaled_details"]
        regular_details = pending["regular_details"]
        supports_partial_regular_day = pending["supports_partial_regular_day"]
        shape_support = pending["shape_support"]
        support_info = pending["support_info"]
        day_shape_prior = adjusted_day_shape_priors.get(
            day_name,
            day_shape_priors.get(day_name),
        )
        adjusted_details = apply_snapshot_day_shape_prior(
            scaled_details,
            day_shape_prior,
            support_factor=shape_support,
        )
        adjusted_details = dict(adjusted_details)
        adjusted_details["snapshot_day_shape_support_factor"] = round(shape_support, 4)
        original_prior = _positive_float(day_shape_priors.get(day_name))
        adjusted_prior = _positive_float(day_shape_prior)
        if original_prior and adjusted_prior:
            adjusted_details["snapshot_frontload_prior_multiplier"] = round(
                adjusted_prior / original_prior,
                4,
            )
            adjusted_details["snapshot_frontload_classification"] = (
                frontload_profile.get("classification")
                if frontload_profile else "neutral"
            )
            adjusted_details["snapshot_frontload_confidence"] = (
                frontload_profile.get("confidence")
                if frontload_profile else 0.0
            )
        if supports_partial_regular_day:
            adjusted_details["supports_partial_regular_day"] = True
            adjusted_details["regular_daypart_coverage_factor"] = round(
                _coverage_value(
                    regular_details.get("daypart_coverage_factor"),
                    default=1.0,
                ),
                4,
            )
        adjusted_details["snapshot_calibration_support_factor"] = support_info["factor"]
        adjusted_details["snapshot_day_calibration_support"] = support_info["day_support"]
        adjusted_details["snapshot_day_calibration_n"] = support_info["day_n"]
        adjusted_details["snapshot_lead_calibration_support"] = support_info["lead_support"]
        adjusted_details["snapshot_lead_calibration_n"] = support_info["lead_n"]
        snapshot_details[day_name] = adjusted_details

    if not snapshot_details:
        return {
            "snapshot_daily_details": {},
            "snapshot_all_daily_details": all_snapshot_details,
            "snapshot_ignored_days": sorted(set(ignored_days)),
            "snapshot_same_week_scale": round(same_week_scale, 4),
            "snapshot_same_week_anchors": same_week_anchors,
            "snapshot_same_week_day_scales": {
                day: round(scale, 4)
                for day, scale in same_week_day_scales.items()
            },
            "snapshot_same_week_scale_source": same_week_scale_source,
            "snapshot_pickup_profile": pickup_profile or {},
            "snapshot_amc_market_share_anchor": share_anchor_summary or {},
            "snapshot_frontload_profile": frontload_profile or {},
        }

    scale_weight_values = [
        (
            details.get("same_week_snapshot_day_scale", same_week_scale),
            _positive_float(day_weights.get(day)) or 0.0,
        )
        for day, details in snapshot_details.items()
    ]
    positive_scale_weights = [
        (scale, weight) for scale, weight in scale_weight_values
        if weight > 0 and scale
    ]
    if positive_scale_weights:
        same_week_scale = (
            sum(scale * weight for scale, weight in positive_scale_weights)
            / sum(weight for _, weight in positive_scale_weights)
        )
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
    snapshot_model_coverage = _coverage_average({
        day: details.get(
            "effective_strategic_coverage_ratio",
            details.get("effective_coverage_ratio", details.get("coverage_ratio")),
        )
        for day, details in snapshot_details.items()
    })
    support_values = []
    for day, details in snapshot_details.items():
        support_factor = _positive_float(
            details.get("snapshot_calibration_support_factor")
        )
        if support_factor is None:
            continue
        weight = _positive_float(day_weights.get(day)) or 0.0
        support_values.append((support_factor, weight))
    positive_weight_values = [
        (factor, weight) for factor, weight in support_values if weight > 0
    ]
    if positive_weight_values:
        support_weighted_total = sum(
            factor * weight for factor, weight in positive_weight_values
        )
        support_weight_total = sum(weight for _, weight in positive_weight_values)
        snapshot_support_factor = support_weighted_total / support_weight_total
    elif support_values:
        snapshot_support_factor = (
            sum(factor for factor, _ in support_values) / len(support_values)
        )
    else:
        snapshot_support_factor = 1.0
    weight_info = snapshot_layer_model_weight(
        snapshot_model_coverage,
        snapshot_missing_share,
        snapshot_support_factor,
        same_week_anchors,
    )
    model_weight = weight_info["weight"]

    return {
        "snapshot_daily_details": snapshot_details,
        "snapshot_all_daily_details": all_snapshot_details,
        "snapshot_ignored_days": sorted(set(ignored_days)),
        "snapshot_mid_m": mid / 1_000_000,
        "snapshot_low_m": (mid * low_factor) / 1_000_000,
        "snapshot_high_m": (mid * high_factor) / 1_000_000,
        "snapshot_model_weight": round(_clamp(model_weight, 0.0, SNAPSHOT_LAYER_MAX_WEIGHT), 4),
        "snapshot_weight_coverage_signal": round(weight_info["coverage_signal"], 4),
        "snapshot_weight_missing_share_signal": round(weight_info["missing_share_signal"], 4),
        "snapshot_weight_support_signal": round(weight_info["support_signal"], 4),
        "snapshot_same_week_support_floor": round(weight_info["same_week_support_floor"], 4),
        "snapshot_calibration_support_factor": round(snapshot_support_factor, 4),
        "snapshot_coverage_ratio": round(snapshot_coverage, 3) if snapshot_coverage is not None else None,
        "snapshot_model_coverage_ratio": (
            round(snapshot_model_coverage, 3)
            if snapshot_model_coverage is not None else None
        ),
        "snapshot_days": sorted(snapshot_details),
        "snapshot_same_week_scale": round(same_week_scale, 4),
        "snapshot_same_week_anchors": same_week_anchors,
        "snapshot_same_week_day_scales": {
            day: round(scale, 4)
            for day, scale in same_week_day_scales.items()
        },
        "snapshot_same_week_scale_source": same_week_scale_source,
        "snapshot_pickup_profile": pickup_profile or {},
        "snapshot_amc_market_share_anchor": share_anchor_summary or {},
        "snapshot_frontload_profile": frontload_profile or {},
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
                  daily_actuals=None,
                  snapshot_daily_predictions=None,
                  snapshot_daily_coverage_ratios=None,
                  snapshot_daily_lead_buckets=None,
                  weekend_of=None, reference_amc_theatres=None,
                  model_cohort_key=None, social_signal=None):
    """Record a predicted-vs-actual result and update calibration factors."""
    if isinstance(days_collected, (list, tuple, set, dict)):
        n_days = len(days_collected)
    else:
        n_days = int(_positive_float(days_collected) or 0)
    actual_value = _positive_float(actual) or 0.0
    entry = {
        "movie": movie,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "predicted_mid": round(predicted_mid, 1),
        "predicted_low": round(predicted_low, 1),
        "predicted_high": round(predicted_high, 1),
        "seat_raw_estimate": round(seat_raw, 1) if seat_raw else None,
        "polymarket_ev": round(poly_ev, 1) if poly_ev else None,
        "actual": round(actual_value, 2),
        "actual_total": round(actual_value, 2),
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
    if daily_actuals:
        clean_daily_actuals = {}
        for key, value in daily_actuals.items():
            gross_m = _positive_float(value)
            if gross_m is not None and gross_m > 0:
                clean_daily_actuals[key] = round(gross_m, 2)
        if clean_daily_actuals:
            entry["daily_actuals"] = clean_daily_actuals
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
    if snapshot_daily_lead_buckets:
        entry["snapshot_daily_lead_buckets"] = {
            k: v for k, v in snapshot_daily_lead_buckets.items()
            if v in SNAPSHOT_LEAD_BUCKETS
        }
    if social_signal:
        entry["social_signal"] = {
            key: social_signal.get(key)
            for key in (
                "factor",
                "adjustment_pct",
                "sentiment_score",
                "buzz_score",
                "buzz_source",
                "signal_quality",
                "reach",
                "rows",
                "platforms",
            )
            if social_signal.get(key) is not None
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
        cal["calibration_factors"]["day_scale_factors"] = (
            recalibrate_day_scale_factors(history)
        )
        cal["calibration_factors"]["snapshot_to_day_scale_factors"] = (
            recalibrate_snapshot_day_scale_factors(history)
        )
        cal["calibration_factors"]["snapshot_to_lead_scale_factors"] = (
            recalibrate_snapshot_lead_scale_factors(
                history,
                day_scales=cal["calibration_factors"]["snapshot_to_day_scale_factors"],
            )
        )
        cal["calibration_factors"]["snapshot_calibration_support"] = (
            snapshot_calibration_support(history)
        )

    # Refine AMC market share from seat-based estimates
    share_estimates = []
    for h in history:
        actual_total = _positive_float(h.get("actual_total", h.get("actual")))
        seat_raw_estimate = _positive_float(h.get("seat_raw_estimate"))
        if seat_raw_estimate and actual_total and actual_total > 0:
            implied = seat_raw_estimate / actual_total
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
    snapshot_leads = {}
    calibration_details = (
        pred.get("snapshot_all_daily_details")
        or pred.get("snapshot_daily_details", {})
    )
    for day_name, details in calibration_details.items():
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
        lead_bucket = details.get("lead_bucket")
        if lead_bucket in SNAPSHOT_LEAD_BUCKETS:
            snapshot_leads[day_name] = lead_bucket
    return snapshot_predictions, snapshot_coverage, snapshot_leads


def daily_calibration_fields_from_prediction(pred):
    """Extract per-day seat predictions used to train calibration.

    If a reported daily actual override is present, `domestic_mid` is the known
    actual by design. Calibration still needs the pre-actual seat-implied value
    so the miss teaches future runs instead of being recorded as a perfect
    prediction.
    """
    daily_predictions = {}
    raw_daily_predictions = {}
    daily_theatre_counts = {}
    daily_coverage_ratios = {}
    for day_name, details in pred.get("daily_details", {}).items():
        if details.get("actual_override"):
            scaled_mid = details.get(
                "seat_implied_scaled_domestic_mid",
                details.get("seat_implied_domestic_mid", details.get("domestic_mid", 0)),
            )
            raw_mid = details.get(
                "seat_implied_domestic_mid",
                details.get("raw_domestic_mid", details.get("domestic_mid", 0)),
            )
        else:
            scaled_mid = details.get("domestic_mid", 0)
            raw_mid = details.get("raw_domestic_mid", scaled_mid)

        daily_predictions[day_name] = scaled_mid / 1_000_000
        raw_daily_predictions[day_name] = raw_mid / 1_000_000
        daily_theatre_counts[day_name] = details.get("n_theatres", 0)
        if details.get("coverage_ratio") is not None:
            daily_coverage_ratios[day_name] = round(
                details.get("effective_coverage_ratio", details["coverage_ratio"]),
                3,
            )
    return (
        daily_predictions,
        raw_daily_predictions,
        daily_theatre_counts,
        daily_coverage_ratios,
    )


# ── Main Prediction Pipeline ─────────────────────────────────────────────────

def daily_actual_override_for(movie, day_name, daily_actual_overrides):
    """Find a reported daily actual for this movie/day, if one exists."""
    if not isinstance(daily_actual_overrides, dict):
        return None
    direct = daily_actual_overrides.get(movie)
    if isinstance(direct, dict) and direct.get(day_name):
        return direct[day_name]

    target_key = _movie_lookup_key(movie)
    if not target_key:
        return None
    for title, daily_actuals in daily_actual_overrides.items():
        if not isinstance(daily_actuals, dict):
            continue
        if _movie_lookup_key(title) == target_key and daily_actuals.get(day_name):
            return daily_actuals[day_name]
    return None


def daily_actual_override_gross_m_for(movie, day_name, daily_actual_overrides):
    """Return the numeric reported daily gross in millions, if available."""
    override = daily_actual_override_for(movie, day_name, daily_actual_overrides)
    if isinstance(override, dict):
        return _positive_float(override.get("gross_m"))
    return _positive_float(override)


def predict_movie(movie, seat_data, poly_data, cal, verbose=False,
                  national_theatre_count=None, snapshot_data=None,
                  social_data=None, daily_actual_overrides=None,
                  showtime_link_profiles=None,
                  apply_empirical_regression=True):
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

    if daily_actual_overrides is None:
        daily_actual_overrides = load_daily_actual_overrides(
            weekend_of=seat_data_weekend_of(seat_data)
        )

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
    movie_metadata_map = load_movie_metadata()
    movie_metadata = metadata_for_movie(movie, movie_metadata_map)
    if not national_theatre_count and movie_metadata and movie_metadata.national_theatre_count:
        national_theatre_count = movie_metadata.national_theatre_count
    if (
        national_theatre_count
        and movie_metadata
        and movie_metadata.national_theatre_count != int(national_theatre_count)
    ):
        movie_metadata = replace(
            movie_metadata,
            national_theatre_count=int(national_theatre_count),
        )

    snapshot_daypart_profiles = {
        date_str: daypart_profile_from_rows(rows, source="snapshot")
        for date_str, rows in (snapshot_data or {}).items()
    }

    dynamic_amc_share_anchors = []
    dynamic_amc_share_anchor = None
    for date_str in opening_dates:
        rows = seat_data[date_str]
        # Use day_of_week from CSV if available, else compute from date
        csv_day = rows[0].get("day_of_week", "") if rows else ""
        day_name = csv_day if csv_day else datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        actual_override = daily_actual_override_for(
            movie,
            day_name,
            daily_actual_overrides,
        )

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
        schedule_profile = combine_daypart_profiles(
            (showtime_link_profiles or {}).get(date_str, {}),
            snapshot_daypart_profiles.get(date_str, {}),
        )
        scheduled_full_day_window_coverage_ratio = schedule_profile.get(
            "full_day_window_coverage_ratio"
        )
        daypart_coverage_factor = weekend_daypart_coverage_factor(
            day_name,
            full_day_window_coverage_ratio,
            target_metadata=movie_metadata,
            earliest_showtime_hour=earliest_showtime_hour,
            avg_showings=avg_showings,
            scheduled_full_day_window_coverage_ratio=scheduled_full_day_window_coverage_ratio,
            scheduled_earliest_showtime_hour=schedule_profile.get("earliest_showtime_hour"),
            scheduled_avg_showings=schedule_profile.get("avg_showings"),
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
        if effective_coverage_ratio is not None:
            effective_coverage_ratio *= daypart_coverage_factor

        # Stage C: AMC → domestic. Reported actuals should not rewrite this
        # movie's AMC share for future days; a single preview report can reflect
        # release footprint, premium screens, or timing more than actual AMC
        # share. Keep the calibrated share stable and record the actual-vs-seat
        # scale on the seat layer instead.
        share_anchor_for_day = None
        share_override = None
        domestic_mid, domestic_low, domestic_high = amc_to_domestic(
            amc_total,
            cal,
            share_override=share_override,
        )
        pre_footprint_mid = domestic_mid
        pre_footprint_low = domestic_low
        pre_footprint_high = domestic_high
        footprint_factor = national_release_footprint_factor(national_theatre_count)
        if national_theatre_count and n_amc_theatres > 0:
            domestic_mid *= footprint_factor
            domestic_low *= footprint_factor
            domestic_high *= footprint_factor

        preview_residual = learned_preview_seat_residual(
            cal,
            day_name,
            exclude_movie=movie,
            target_metadata=movie_metadata,
            metadata=movie_metadata_map,
        )
        if preview_residual:
            residual_factor = preview_residual["factor"]
            domestic_mid *= residual_factor
            domestic_low *= residual_factor
            domestic_high *= residual_factor

        seat_implied_domestic_mid = domestic_mid
        seat_implied_domestic_low = domestic_low
        seat_implied_domestic_high = domestic_high
        actual_gross_m = None
        seat_model_actual_scale = None
        seat_model_actual_raw_scale = None
        if actual_override:
            actual_gross_m = _positive_float(actual_override.get("gross_m"))
            if actual_gross_m is not None:
                actual_gross = actual_gross_m * 1_000_000
                day_scale = get_day_scale(cal, day_name)
                scaled_seat_implied = seat_implied_domestic_mid * day_scale
                if scaled_seat_implied and scaled_seat_implied > 0:
                    seat_model_actual_scale = actual_gross / scaled_seat_implied
                raw_actual_gross = (
                    actual_gross / day_scale
                    if day_scale and abs(day_scale) > 1e-9 else actual_gross
                )
                if seat_implied_domestic_mid and seat_implied_domestic_mid > 0:
                    seat_model_actual_raw_scale = (
                        raw_actual_gross / seat_implied_domestic_mid
                    )
                domestic_mid = raw_actual_gross
                domestic_low = raw_actual_gross
                domestic_high = raw_actual_gross
                coverage_ratio = 1.0
                effective_coverage_ratio = 1.0

        daily_estimates[day_name] = domestic_mid
        details = {
            "date": date_str,
            "amc_total": amc_total,
            "sampled_amc_total": sampled_amc_total,
            "sample_normalization_factor": sample_norm_factor,
            "domestic_mid": domestic_mid,
            "domestic_low": domestic_low,
            "domestic_high": domestic_high,
            "pre_footprint_domestic_mid": pre_footprint_mid,
            "pre_footprint_domestic_low": pre_footprint_low,
            "pre_footprint_domestic_high": pre_footprint_high,
            "national_footprint_factor": footprint_factor,
            "preview_seat_residual_factor": (
                preview_residual["factor"] if preview_residual else 1.0
            ),
            "preview_seat_residual_raw_factor": (
                preview_residual["raw_factor"] if preview_residual else None
            ),
            "preview_seat_residual_strength": (
                preview_residual["strength"] if preview_residual else 0.0
            ),
            "preview_seat_residual_n": (
                preview_residual["n"] if preview_residual else 0
            ),
            "preview_seat_residual_source": (
                preview_residual["source"] if preview_residual else None
            ),
            "amc_market_share_used": share_override or calibrated_amc_market_share(cal),
            "amc_market_share_source": (
                "same_week_actual_anchor" if share_anchor_for_day else "calibration"
            ),
            "amc_market_share_anchor_day": (
                share_anchor_for_day.get("day") if share_anchor_for_day else None
            ),
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
            "scheduled_theatre_count": schedule_profile.get("n_theatres"),
            "scheduled_avg_showings_per_cinema": schedule_profile.get("avg_showings"),
            "scheduled_earliest_showtime_hour": schedule_profile.get("earliest_showtime_hour"),
            "scheduled_full_day_window_coverage_ratio": (
                scheduled_full_day_window_coverage_ratio
            ),
            "scheduled_daypart_source": schedule_profile.get("source"),
            "daypart_coverage_factor": daypart_coverage_factor,
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
        if actual_override and _positive_float(actual_override.get("gross_m")) is not None:
            details.update({
                "actual_override": True,
                "actual_override_m": _positive_float(actual_override.get("gross_m")),
                "actual_override_source": actual_override.get("source", ""),
                "actual_override_status": actual_override.get("status", ""),
                "actual_override_as_of_date": actual_override.get("as_of_date", ""),
                "actual_override_notes": actual_override.get("notes", ""),
                "seat_implied_domestic_mid": seat_implied_domestic_mid,
                "seat_implied_domestic_low": seat_implied_domestic_low,
                "seat_implied_domestic_high": seat_implied_domestic_high,
                "seat_implied_scaled_domestic_mid": (
                    seat_implied_domestic_mid * get_day_scale(cal, day_name)
                ),
                "seat_model_actual_scale": seat_model_actual_scale,
                "seat_model_actual_raw_scale": seat_model_actual_raw_scale,
                "seat_model_actual_scale_source": (
                    "reported_actual_vs_seat_implied"
                    if seat_model_actual_scale is not None else None
                ),
                "seat_model_actual_showings_per_cinema": round(avg_showings, 1),
                "seat_model_actual_daypart_factor": daypart_coverage_factor,
                "seat_model_actual_evening_to_daily": ev_to_daily,
            })
        else:
            details["actual_override"] = False
        daily_details[day_name] = details

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
        regular_seat_data={
            date_str: seat_data[date_str]
            for date_str in opening_dates
            if date_str in seat_data
        },
        amc_share_anchor=dynamic_amc_share_anchor,
        amc_share_anchors=dynamic_amc_share_anchors,
    )
    data_profile = missing_data_profile(
        daily_details,
        cal,
        snapshot_layer=snapshot_layer,
    )
    reported_actual_share = actual_override_day_share(daily_details, cal)

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
        "snapshot_all_daily_details": (
            snapshot_layer.get("snapshot_all_daily_details", {})
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
        "snapshot_calibration_support_factor": (
            snapshot_layer.get("snapshot_calibration_support_factor")
            if snapshot_layer else None
        ),
        "snapshot_coverage_ratio": (
            snapshot_layer.get("snapshot_coverage_ratio")
            if snapshot_layer else None
        ),
        "snapshot_model_coverage_ratio": (
            snapshot_layer.get("snapshot_model_coverage_ratio")
            if snapshot_layer else None
        ),
        "snapshot_weight_coverage_signal": (
            snapshot_layer.get("snapshot_weight_coverage_signal")
            if snapshot_layer else None
        ),
        "snapshot_weight_missing_share_signal": (
            snapshot_layer.get("snapshot_weight_missing_share_signal")
            if snapshot_layer else None
        ),
        "snapshot_weight_support_signal": (
            snapshot_layer.get("snapshot_weight_support_signal")
            if snapshot_layer else None
        ),
        "snapshot_same_week_support_floor": (
            snapshot_layer.get("snapshot_same_week_support_floor")
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
        "snapshot_same_week_day_scales": (
            snapshot_layer.get("snapshot_same_week_day_scales", {})
            if snapshot_layer else {}
        ),
        "snapshot_same_week_scale_source": (
            snapshot_layer.get("snapshot_same_week_scale_source")
            if snapshot_layer else None
        ),
        "snapshot_pickup_profile": (
            snapshot_layer.get("snapshot_pickup_profile", {})
            if snapshot_layer else {}
        ),
        "snapshot_frontload_profile": (
            snapshot_layer.get("snapshot_frontload_profile", {})
            if snapshot_layer else {}
        ),
        "snapshot_amc_market_share_anchor": (
            snapshot_layer.get("snapshot_amc_market_share_anchor", {})
            if snapshot_layer else {}
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
        "reported_actual_day_share": reported_actual_share,
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
        "dynamic_amc_share_anchor": dynamic_amc_share_anchor,
        "dynamic_amc_share_anchors": dynamic_amc_share_anchors,
        "avg_showings_per_cinema": round(avg_showings_total, 1),
        "amc_total_weekend": sum(d.get("amc_total", 0) for d in daily_details.values()),
    }
    attach_social_signal_prediction(result, social_data)
    if apply_empirical_regression:
        attach_empirical_seat_snapshot_regression(result, cal)
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


def infer_target_metadata_from_title(movie, weekend_of=""):
    """Conservative metadata fallback for obvious franchise titles.

    This keeps the comp/regression layer alive for active markets whose CSV
    metadata has not been entered yet. Only high-confidence title patterns are
    inferred; unknown titles still return None rather than fabricating a genre.
    """
    title = (movie or "").lower()
    rules = [
        (
            ("mandalorian", "grogu", "star wars"),
            {
                "genre": "sci_fi",
                "audience_type": "fan_driven",
                "franchise_type": "franchise",
                "rating": "PG-13",
                "release_scale": "tentpole",
            },
        ),
        (
            ("marvel", "avengers", "spider-man", "spiderman", "x-men"),
            {
                "genre": "superhero",
                "audience_type": "fan_driven",
                "franchise_type": "franchise",
                "rating": "PG-13",
                "release_scale": "tentpole",
            },
        ),
        (
            ("jurassic", "mission: impossible", "mission impossible", "fast furious", "fast & furious"),
            {
                "genre": "action",
                "audience_type": "fan_driven",
                "franchise_type": "franchise",
                "rating": "PG-13",
                "release_scale": "tentpole",
            },
        ),
    ]
    for keywords, fields in rules:
        if any(keyword in title for keyword in keywords):
            return TargetMetadata(
                movie=movie,
                weekend_of=weekend_of or "",
                notes="Title-inferred fallback metadata; replace with verified CSV row.",
                **fields,
            )
    return None


def enrich_target_metadata_with_seat_context(target, pred):
    """Add observed theatre/showing intensity to the comp target metadata."""
    if not target:
        return target
    avg_showings = _positive_float(pred.get("avg_showings_per_cinema")) or 0.0
    release_scale = getattr(target, "release_scale", "") or ""
    if not release_scale:
        n_amc = int(_positive_float(pred.get("n_theatres_total")) or 0)
        if avg_showings >= 6.0 and n_amc >= 350:
            release_scale = "tentpole"
        elif avg_showings >= 4.25 and n_amc >= 300:
            release_scale = "event"
    current_avg_showings = float(getattr(target, "avg_showings_per_cinema", 0) or 0)
    if abs(avg_showings - current_avg_showings) < 0.001 and release_scale == (
        getattr(target, "release_scale", "") or ""
    ):
        return target
    return replace(
        target,
        avg_showings_per_cinema=avg_showings,
        release_scale=release_scale,
    )


def attach_comp_model_prediction(pred, cal, metadata=None, comps=None):
    """Attach the automated seat+historical-comp model to a prediction.

    This is intentionally additive: if metadata or comps are missing, the
    seat-only and Polymarket paths continue unchanged.
    """
    metadata = metadata if metadata is not None else load_movie_metadata()
    comps = comps if comps is not None else load_historical_comps()
    target = metadata_for_movie(pred.get("movie", ""), metadata)
    metadata_source = "csv"
    if not target:
        target = infer_target_metadata_from_title(
            pred.get("movie", ""),
            weekend_of=pred.get("weekend_of", ""),
        )
        metadata_source = "title_inferred" if target else "missing"
    pred["seat_comp_metadata_source"] = metadata_source
    if not target or not comps:
        return None
    target = enrich_target_metadata_with_seat_context(target, pred)
    pred_nat_count = pred.get("national_theatre_count")
    if pred_nat_count and target.national_theatre_count != int(pred_nat_count):
        target = replace(target, national_theatre_count=int(pred_nat_count))
    if pred.get("social_signal"):
        target = _metadata_with_social_signal(target, pred.get("social_signal"))
    pred["seat_comp_release_scale"] = release_scale_for_item(target)
    pred["seat_comp_avg_showings_per_cinema"] = getattr(
        target,
        "avg_showings_per_cinema",
        0.0,
    )

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
        day_weights = get_day_weights(cal)
        baseline_thursday_share = float(day_weights.get("Thursday", 0) or 0)
        has_non_thursday_evidence = any(
            day in (pred.get("daily_details") or {})
            for day in ("Friday", "Saturday", "Sunday")
        )
        if not has_non_thursday_evidence:
            return None
        estimate = estimate_opening_weekend_from_thursday(
            1.0,
            target,
            comps,
            baseline_thursday_share=baseline_thursday_share,
        )

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
    has_thursday_evidence = "Thursday" in (pred.get("daily_details") or {})
    pred["seat_comp_has_thursday_evidence"] = has_thursday_evidence
    pred["seat_comp_thursday_gross_m"] = (
        estimate.thursday_gross_m if has_thursday_evidence else None
    )
    pred["seat_comp_thursday_share"] = thursday_share
    pred["seat_comp_external_thursday_share"] = external_thursday_share
    pred["seat_comp_raw_external_thursday_share"] = estimate.weighted_thursday_share
    pred["seat_comp_target_release_scale"] = estimate.target_release_scale
    if estimate.audience_regression_n:
        features = estimate.audience_regression_features or {}
        model_features = set(
            feature.strip()
            for feature in str(features.get("model_features") or "").split(",")
            if feature.strip()
        )
        feature_parts = []
        if features.get("imdb_rating"):
            feature_parts.append(f"IMDb {features['imdb_rating']:.1f}")
        if features.get("rt_audience_score"):
            feature_parts.append(f"RT audience {features['rt_audience_score']:.0f}%")
        if features.get("social_media_universe_m"):
            feature_parts.append(f"RelishMix SMU {features['social_media_universe_m']:.0f}M")
            if COMPS_IN_FORECAST and "log_social_media_universe_m" in model_features:
                pred["social_signal_model_integrated"] = True
        if features.get("social_sentiment_score"):
            feature_parts.append(f"social sentiment {features['social_sentiment_score']:+.2f}")
            if COMPS_IN_FORECAST and "social_sentiment_score" in model_features:
                pred["social_signal_model_integrated"] = True
        if features.get("social_buzz_score"):
            feature_parts.append(f"social buzz {features['social_buzz_score']:+.2f}")
            if COMPS_IN_FORECAST and "social_buzz_score" in model_features:
                pred["social_signal_model_integrated"] = True
        if features.get("national_theatre_count"):
            feature_parts.append(f"{int(features['national_theatre_count']):,} theatres")
            if COMPS_IN_FORECAST and "release_footprint_factor" in model_features:
                pred["theatre_count_model_integrated"] = True
        pred["seat_comp_audience_factor"] = estimate.audience_regression_factor
        pred["seat_comp_audience_regression_n"] = estimate.audience_regression_n
        pred["seat_comp_audience_regression_r2"] = estimate.audience_regression_r2
        pred["seat_comp_audience_raw_factor"] = features.get("regression_raw_factor")
        pred["seat_comp_audience_fit_weight"] = features.get("regression_fit_weight")
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
        pred["seat_comp_prior_raw_mid_m"] = getattr(
            estimate,
            "raw_prior_weekend_mid_m",
            adjusted["prior_mid_m"],
        )
        pred["seat_comp_prior_footprint_factor"] = getattr(
            estimate,
            "prior_footprint_factor",
            1.0,
        )
        pred["seat_comp_adjusted_mid_m"] = adjusted["mid_m"]
        pred["seat_comp_adjusted_low_m"] = adjusted["low_m"]
        pred["seat_comp_adjusted_high_m"] = adjusted["high_m"]
        pred["seat_comp_adjusted_basis"] = f"{model['basis']} + coverage prior"

    pred["comp_blended_m"] = pred.get("seat_comp_adjusted_mid_m", pred["seat_comp_mid_m"])
    pred["comp_blend_low_m"] = pred.get("seat_comp_adjusted_low_m", pred["seat_comp_low_m"])
    pred["comp_blend_high_m"] = pred.get("seat_comp_adjusted_high_m", pred["seat_comp_high_m"])
    pred["comp_w_model"] = 1.0
    pred["comp_w_poly"] = 0.0

    pred["comp_model_excluded"] = not COMPS_IN_FORECAST
    primary = seat_primary_ensemble(pred) if COMPS_IN_FORECAST else None
    if primary:
        pred["seat_primary_mid_m"] = primary["mid_m"]
        pred["seat_primary_low_m"] = primary["low_m"]
        pred["seat_primary_high_m"] = primary["high_m"]
        pred["seat_primary_w_direct"] = primary["w_direct"]
        pred["seat_primary_w_comp"] = primary["w_comp"]
        pred["seat_primary_disagreement_m"] = primary["disagreement_m"]
        if primary.get("inferred_metadata_comp_cap") is not None:
            pred["seat_primary_inferred_metadata_comp_cap"] = (
                primary["inferred_metadata_comp_cap"]
            )
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


def _weighted_geomean_ratio(values):
    """Weighted geometric mean for bounded multiplicative ratios."""
    if not values:
        return None
    total_weight = sum(weight for _, weight, _ in values)
    if total_weight <= 0:
        return None
    return exp(
        sum(log(max(ratio, 1e-9)) * weight for ratio, weight, _ in values)
        / total_weight
    )


def _metadata_preview_similarity(target_metadata, entry_metadata):
    """0-1 similarity for local preview-seat residuals."""
    if not target_metadata or not entry_metadata:
        return 0.0
    score = 0.0
    total = 0.0
    for attr, weight in (
        ("genre", 0.45),
        ("audience_type", 0.35),
        ("franchise_type", 0.12),
        ("rating", 0.08),
    ):
        total += weight
        target_val = getattr(target_metadata, attr, None)
        entry_val = getattr(entry_metadata, attr, None)
        if target_val and entry_val and target_val == entry_val:
            score += weight
    return score / total if total else 0.0


def learned_preview_seat_residual(cal, day_name, exclude_movie="",
                                  target_metadata=None, metadata=None):
    """Learn a same-day actual/seat residual for Thursday previews.

    Day scale factors already learn broad per-day bias. This layer only learns
    the residual left after the stored day prediction for a settled movie. It is
    applied before reported same-week actual overrides, so a known Thursday
    preview still wins, while future movies can benefit from prior local misses.
    """
    if day_name != "Thursday" or not cal:
        return None

    global_values = []
    similar_values = []
    saw_entry_metadata = False
    for entry in (cal or {}).get("history", [])[-30:]:
        if not _actual_status_is_final(entry):
            continue
        entry_movie = entry.get("movie", "")
        if _movie_matches(exclude_movie, entry_movie):
            continue
        daily_actuals = entry.get("daily_actuals") or {}
        daily_predictions = entry.get("daily_predictions") or {}
        raw_daily_predictions = entry.get("raw_daily_predictions") or {}
        actual = _positive_float(daily_actuals.get(day_name))
        raw_predicted = _positive_float(raw_daily_predictions.get(day_name))
        if raw_predicted:
            predicted = raw_predicted * get_day_scale(cal, day_name)
        else:
            predicted = _positive_float(daily_predictions.get(day_name))
        if not actual or not predicted:
            continue

        coverage = _coverage_value(
            (entry.get("daily_coverage_ratios") or {}).get(day_name),
            default=0.0,
        )
        if coverage < MIN_DAILY_CALIBRATION_COVERAGE:
            continue

        ratio = _clamp(
            actual / predicted,
            PREVIEW_SEAT_RESIDUAL_RATIO_MIN,
            PREVIEW_SEAT_RESIDUAL_RATIO_MAX,
        )
        version = entry.get("model_version")
        if not version:
            version_weight = RESIDUAL_LEGACY_MODEL_VERSION_WEIGHT
        elif version == MODEL_VERSION:
            version_weight = RESIDUAL_SAME_MODEL_VERSION_WEIGHT
        else:
            version_weight = RESIDUAL_DIFFERENT_MODEL_VERSION_WEIGHT
        base_weight = coverage * version_weight
        if base_weight <= 0:
            continue

        global_values.append((ratio, base_weight, entry))

        similarity = 0.0
        if target_metadata is not None and metadata:
            entry_metadata = metadata_for_movie(entry_movie, metadata)
            if entry_metadata:
                saw_entry_metadata = True
                similarity = _metadata_preview_similarity(target_metadata, entry_metadata)
        if similarity > 0:
            similar_values.append((ratio, base_weight * similarity, entry))

    source_values = similar_values if saw_entry_metadata and similar_values else global_values
    if len(source_values) < PREVIEW_SEAT_RESIDUAL_MIN_OBS:
        return None

    raw_factor = _weighted_geomean_ratio(source_values)
    if raw_factor is None:
        return None
    total_weight = sum(weight for _, weight, _ in source_values)
    strength = min(
        PREVIEW_SEAT_RESIDUAL_MAX_STRENGTH,
        total_weight / (total_weight + PREVIEW_SEAT_RESIDUAL_PRIOR_WEIGHT),
    )
    factor = 1.0 + (raw_factor - 1.0) * strength
    factor = _clamp(
        factor,
        PREVIEW_SEAT_RESIDUAL_FACTOR_MIN,
        PREVIEW_SEAT_RESIDUAL_FACTOR_MAX,
    )
    if abs(factor - 1.0) < 0.005:
        return None

    return {
        "day": day_name,
        "factor": factor,
        "raw_factor": raw_factor,
        "strength": strength,
        "n": len(source_values),
        "effective_weight": total_weight,
        "source": "matched-local-preview-history" if source_values is similar_values else "local-preview-history",
        "examples": [
            {
                "movie": entry.get("movie"),
                "ratio": ratio,
                "weight": weight,
            }
            for ratio, weight, entry in sorted(
                source_values,
                key=lambda item: item[1],
                reverse=True,
            )[:5]
        ],
    }


def _seat_comp_model_from_available_days(pred, estimate, thursday_share=None, audience_factor=1.0):
    """Project weekend from the latest observed seat data plus comp shape.

    Public daily grosses report Friday as Friday+previews, so once Friday seat
    data exists this uses (Thursday + Friday) against the comp's reported
    Friday share. If Thursday is missing, Friday seat data is compared against
    pure Friday share by removing previews from the reported Friday comp share.
    Saturday and Sunday are added as they become available.
    """
    details = pred.get("daily_details", {})
    thursday_share = thursday_share or estimate.weighted_thursday_share

    def day_domestic_m(day):
        return (details.get(day, {}).get("domestic_mid", 0) or 0) / 1_000_000

    if "Thursday" in details:
        evidence_m = day_domestic_m("Thursday")
        basis = "Thursday"
        share_adjustment_factor = 1.0
        share_values = [
            (comp.thursday_share, estimate.weights.get(comp.movie, 0))
            for comp in estimate.comps
            if comp.thursday_share > 0
        ]
        evidence_share = thursday_share

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
            share_adjustment_factor = audience_factor

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
            share_adjustment_factor = audience_factor

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
            share_adjustment_factor = 1.0
    else:
        evidence_m = 0.0
        evidence_share = 0.0
        share_adjustment_factor = audience_factor
        basis_days = []
        if "Friday" in details and estimate.daily_shares.get("Friday"):
            friday_share = max(
                0.0,
                estimate.daily_shares["Friday"] - estimate.weighted_thursday_share,
            )
            if friday_share > 0:
                evidence_m += day_domestic_m("Friday")
                evidence_share += friday_share
                basis_days.append("Friday")
        for day in ("Saturday", "Sunday"):
            if day in details and estimate.daily_shares.get(day):
                evidence_m += day_domestic_m(day)
                evidence_share += estimate.daily_shares[day]
                basis_days.append(day)

        share_values = []
        if evidence_m > 0 and evidence_share > 0:
            for comp in estimate.comps:
                share = 0.0
                if "Friday" in details and comp.daily_shares.get("Friday"):
                    share += max(0.0, comp.daily_shares["Friday"] - comp.thursday_share)
                for day in ("Saturday", "Sunday"):
                    if day in details and comp.daily_shares.get(day):
                        share += comp.daily_shares[day]
                if share > 0:
                    share_values.append((share, estimate.weights.get(comp.movie, 0)))
        basis = (
            f"{basis_days[0]} only"
            if len(basis_days) == 1
            else f"{'+'.join(basis_days)} only"
        )

    if not share_values or evidence_share <= 0:
        base_mid = estimate.audience_adjusted_mid_m or estimate.mid_m
        base_low = estimate.low_m * audience_factor
        base_high = estimate.high_m * audience_factor
        return {
            "mid_m": base_mid,
            "low_m": min(base_low, base_high),
            "high_m": max(base_low, base_high),
            "basis": "historical comp prior",
            "evidence_m": estimate.thursday_gross_m,
            "evidence_share": thursday_share,
        }

    if evidence_share >= 0.99:
        share_adjustment_factor = 1.0
    share_adjustment_factor = max(float(share_adjustment_factor or 1.0), 0.01)
    adjusted_evidence_share = evidence_share / share_adjustment_factor
    adjusted_share_values = [
        (share / share_adjustment_factor, weight)
        for share, weight in share_values
    ]

    mid_m = evidence_m / adjusted_evidence_share
    low_share = _weighted_quantile_pairs(adjusted_share_values, 0.75)
    high_share = _weighted_quantile_pairs(adjusted_share_values, 0.25)
    thursday_interval_factor = (
        audience_factor
        if basis == "Thursday" and share_adjustment_factor == 1.0
        else 1.0
    )
    low_m = (evidence_m / low_share) * thursday_interval_factor if low_share else mid_m
    high_m = (evidence_m / high_share) * thursday_interval_factor if high_share else mid_m
    return {
        "mid_m": mid_m,
        "low_m": min(low_m, high_m),
        "high_m": max(low_m, high_m),
        "basis": basis,
        "evidence_m": evidence_m,
        "evidence_share": adjusted_evidence_share,
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
    partial_daypart_days = profile.get("partial_daypart_days") or []
    if missing_days or missing_tz_days or partial_daypart_days:
        coverage = pred.get("seat_weighted_coverage_ratio")
        coverage_str = f"{coverage:.0%}" if coverage is not None else "n/a"
        print(f"    Completeness: {profile.get('observed_day_share', 0):.0%} day-share, "
              f"{coverage_str} weighted seat coverage"
              f"{'; missing ' + '/'.join(missing_days) if missing_days else ''}"
              f"{'; missing TZ on ' + '/'.join(missing_tz_days) if missing_tz_days else ''}"
              f"{'; partial daypart on ' + '/'.join(partial_daypart_days) if partial_daypart_days else ''}")

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
        footprint_factor = details.get("national_footprint_factor", 1.0)
        footprint_note = ""
        preview_factor = details.get("preview_seat_residual_factor", 1.0)
        preview_note = ""
        if abs(preview_factor - 1.0) >= 0.005:
            preview_note = (
                f", preview residual x{preview_factor:.3f}"
                f" n={details.get('preview_seat_residual_n', 0)}"
            )
        if details.get("actual_override"):
            source = details.get("actual_override_source") or "reported"
            day_model = f"reported actual {fmt_m(dom_m)} ({source})"
        elif nat and abs(footprint_factor - 1.0) >= 0.005:
            pre_footprint_m = (
                details.get("pre_footprint_domestic_mid", details["domestic_mid"])
                / 1_000_000
            )
            post_footprint_m = pre_footprint_m * footprint_factor
            if abs(day_scale - 1.0) >= 0.005:
                day_model = (
                    f"{fmt_m(pre_footprint_m)} × footprint {footprint_factor:.3f} "
                    f"= {fmt_m(post_footprint_m)} × {day_scale:.3f} = {fmt_m(dom_m)}"
                )
            else:
                day_model = (
                    f"{fmt_m(pre_footprint_m)} × footprint {footprint_factor:.3f} "
                    f"= {fmt_m(dom_m)}"
                )
            footprint_note = f", footprint {footprint_factor:.3f}"
        full_day_window_coverage = details.get("full_day_window_coverage_ratio")
        full_day_window_str = ""
        if day in {"Saturday", "Sunday"} and full_day_window_coverage is not None:
            full_day_window_str = f", full-window theatres {full_day_window_coverage:.0%}"
            scheduled_full_day = details.get("scheduled_full_day_window_coverage_ratio")
            if scheduled_full_day is not None:
                source = details.get("scheduled_daypart_source")
                source_str = f" via {source}" if source else ""
                full_day_window_str += (
                    f", scheduled early theatres {scheduled_full_day:.0%}{source_str}"
                )
            daypart_factor = details.get("daypart_coverage_factor")
            if daypart_factor is not None and daypart_factor < 0.995:
                full_day_window_str += f", daypart coverage {daypart_factor:.0%}"
            elif (
                scheduled_full_day is not None
                and full_day_window_coverage < WEEKEND_FULL_DAY_MIN_THEATRE_COVERAGE
                and scheduled_full_day < WEEKEND_FULL_DAY_MIN_THEATRE_COVERAGE
            ):
                full_day_window_str += ", schedule-limited"
        share_note = ""
        if details.get("actual_override") and details.get("seat_model_actual_scale"):
            share_note = (
                f", seat scale x{details['seat_model_actual_scale']:.2f} "
                "from reported actual"
            )
        elif details.get("amc_market_share_source") == "same_week_actual_anchor":
            share_note = (
                f", AMC share {details.get('amc_market_share_used', 0):.1%} "
                f"from {details.get('amc_market_share_anchor_day')} actual"
            )
        amc_input = f"AMC {fmt_m(amc_m)}"
        if abs(sample_norm - 1.0) >= 0.005:
            amc_input = (
                f"sample AMC {fmt_m(sampled_amc_m)} × {sample_norm:.3f} "
                f"= AMC {fmt_m(amc_m)}"
            )
        if details.get("actual_override"):
            implied_m = (
                details.get(
                    "seat_implied_scaled_domestic_mid",
                    details.get("seat_implied_domestic_mid", details["domestic_mid"]),
                )
                / 1_000_000
            )
            amc_input = f"seat-implied {fmt_m(implied_m)}"
        print(f"    {day} ({details['date']}): "
              f"{amc_input} → day {day_model} "
              f"[{details['n_theatres']} theatres{coverage_str}, {spd:.1f} showings/cinema"
              f"{full_day_window_str}"
              f"{daypart_str}"
              f"{footprint_note}"
              f"{preview_note}"
              f"{share_note}"
              f"{missing_tz_str}"
              f"{', ' + str(details['n_no_data']) + ' no data' if details['n_no_data'] else ''}]")

    # Seat + historical comps are diagnostics unless COMPS_IN_FORECAST is enabled.
    comps_visible = (
        pred.get("seat_comp_mid_m") is not None
        and not pred.get("comp_model_excluded")
    )
    if pred.get("seat_comp_mid_m") is not None and pred.get("comp_model_excluded") and verbose:
        print(f"  Comp diagnostic excluded from forecast: "
              f"{fmt_m(pred['seat_comp_mid_m'])} "
              f"({fmt_m(pred['seat_comp_low_m'])} - {fmt_m(pred['seat_comp_high_m'])})")
    if comps_visible:
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
        if pred.get("seat_comp_has_thursday_evidence"):
            print(f"    Seat-implied Thu: {fmt_m(pred['seat_comp_thursday_gross_m'])}; "
                  f"Thu share used: {pred['seat_comp_thursday_share']:.1%} "
                  f"({'; '.join(share_bits)})")
        else:
            print(f"    No Thursday seat data; using comp daily-shape shares "
                  f"({'; '.join(share_bits)})")
        if pred.get("seat_comp_release_scale"):
            avg_shows = pred.get("seat_comp_avg_showings_per_cinema") or 0
            print(
                f"    Comp release profile: {pred['seat_comp_release_scale']}"
                f"{f', {avg_shows:.1f} showings/theatre' if avg_shows else ''}"
            )
        if pred.get("seat_comp_audience_factor"):
            r2 = pred.get("seat_comp_audience_regression_r2")
            r2_str = f", R2 {r2:.2f}" if r2 is not None else ""
            raw = pred.get("seat_comp_audience_raw_factor")
            fit_weight = pred.get("seat_comp_audience_fit_weight")
            shrink_bits = []
            if raw:
                shrink_bits.append(f"raw x{raw:.3f}")
            if fit_weight is not None:
                shrink_bits.append(f"fit {fit_weight:.0%}")
            shrink_str = f" ({', '.join(shrink_bits)})" if shrink_bits else ""
            print(f"    Comp feature regression: x{pred['seat_comp_audience_factor']:.3f} "
                  f"from {pred.get('seat_comp_audience_features', 'audience scores')} "
                  f"(n={pred['seat_comp_audience_regression_n']}{r2_str}){shrink_str}")
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
            if pred.get("seat_comp_prior_footprint_factor") not in (None, 1.0):
                print(f"    Prior footprint: x{pred['seat_comp_prior_footprint_factor']:.3f} "
                      f"from raw {fmt_m(pred.get('seat_comp_prior_raw_mid_m', 0))}")

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
        raw_snapshot_cov = pred.get("snapshot_coverage_ratio") or 0
        model_snapshot_cov = pred.get("snapshot_model_coverage_ratio")
        if model_snapshot_cov is None:
            coverage_note = f"coverage {raw_snapshot_cov:.0%}"
        elif abs(model_snapshot_cov - raw_snapshot_cov) >= 0.05:
            coverage_note = (
                f"model coverage {model_snapshot_cov:.0%} "
                f"(raw AMC {raw_snapshot_cov:.0%})"
            )
        else:
            coverage_note = f"coverage {raw_snapshot_cov:.0%}"
        print(f"  Snapshot layer:   {fmt_m(pred['snapshot_mid_m']):>7}  "
              f"({fmt_m(pred['snapshot_low_m'])} - {fmt_m(pred['snapshot_high_m'])})")
        print(f"    Future days: {days or '-'}; "
              f"{coverage_note}; "
              f"calibration support {pred.get('snapshot_calibration_support_factor', 1):.0%}; "
              f"model weight {pred.get('snapshot_model_weight', 0):.0%}")
        snapshot_scale = pred.get("snapshot_same_week_scale")
        if snapshot_scale and abs(snapshot_scale - 1.0) >= 0.01:
            anchors = ", ".join(
                anchor.get("day", "?")
                for anchor in pred.get("snapshot_same_week_anchors", [])
            )
            source = pred.get("snapshot_same_week_scale_source")
            source_note = (
                " matched pickup"
                if source == "matched_showtime_pickup" else " aggregate"
            )
            print(f"    Same-week calibration: x{snapshot_scale:.2f}"
                  f"{source_note}{f' from {anchors}' if anchors else ''}")
            day_scales = pred.get("snapshot_same_week_day_scales") or {}
            scale_bits = [
                f"{day[:3]} x{day_scales[day]:.2f}"
                for day in (pred.get("snapshot_days") or [])
                if day in day_scales and abs(day_scales[day] - snapshot_scale) >= 0.01
            ]
            if scale_bits:
                print(f"    Day-aware pickup scales: {', '.join(scale_bits)}")
        share_anchor = pred.get("snapshot_amc_market_share_anchor") or {}
        if share_anchor.get("blended_share"):
            daily_share_bits = []
            for day, details in sorted(
                pred.get("snapshot_daily_details", {}).items(),
                key=lambda item: OPENING_WEEKEND_DAYS.index(item[0])
                if item[0] in OPENING_WEEKEND_DAYS else 99,
            ):
                target_anchor = details.get("amc_market_share_anchor") or {}
                target_share = target_anchor.get("blended_share")
                if target_share:
                    daily_share_bits.append(f"{day[:3]} {target_share:.1%}")
            if daily_share_bits:
                print(f"    Same-week AMC share: {', '.join(daily_share_bits)} "
                      f"from {share_anchor.get('day', 'reported actual')}")
            else:
                print(f"    Same-week AMC share: {share_anchor['blended_share']:.1%} "
                      f"from {share_anchor.get('day', 'reported actual')}")
        pickup = pred.get("snapshot_pickup_profile") or {}
        if pickup.get("n_matched_showtimes"):
            print(
                f"    Pickup/walk-in anchor: {pickup['n_matched_showtimes']} showtimes, "
                f"{pickup.get('reserved_seats_at_snapshot', 0)} reserved → "
                f"{pickup.get('final_sold_seats', 0)} final seats; "
                f"+{pickup.get('post_snapshot_pickup_seats', 0)} after snapshot"
            )
        frontload = pred.get("snapshot_frontload_profile") or {}
        if frontload.get("classification"):
            ratio = frontload.get("frontload_ratio", 1.0)
            confidence = frontload.get("confidence", 0.0)
            shares = frontload.get("snapshot_shares") or {}
            share_bits = [
                f"{day[:3]} {shares[day]:.0%}"
                for day in ("Friday", "Saturday", "Sunday")
                if day in shares
            ]
            print(
                f"    Snapshot frontload: {frontload['classification']} "
                f"(Fri/rest x{ratio:.2f} vs prior, confidence {confidence:.0%}"
                f"{f'; mix {', '.join(share_bits)}' if share_bits else ''})"
            )
        for day, details in sorted(
            pred.get("snapshot_daily_details", {}).items(),
            key=lambda item: item[1].get("date", ""),
        ):
            empirical_factor = details.get("snapshot_empirical_regression_factor")
            if empirical_factor:
                basis_mid = details.get(
                    "pre_snapshot_empirical_regression_domestic_mid",
                    details.get("raw_domestic_mid", details.get("domestic_mid", 0)),
                )
                print(
                    f"    {day}: {fmt_m(details['domestic_mid'] / 1_000_000)} "
                    f"(raw snapshot {fmt_m(basis_mid / 1_000_000)}, "
                    f"empirical x{empirical_factor:.2f}, "
                    f"{details.get('snapshot_empirical_regression_n', 0)} trained snapshot days)"
                )
                continue
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
                  f"{signal_weight:.0%} snapshot signal, "
                  f"{details.get('snapshot_calibration_support_factor', 1):.0%} calibrated support"
                  f"{', frontload prior x' + format(details['snapshot_frontload_prior_multiplier'], '.2f') if details.get('snapshot_frontload_prior_multiplier') not in (None, 1.0) else ''})")

    social = pred.get("social_signal")
    if social:
        platforms = ", ".join(social.get("platforms") or [])
        print(f"  Social layer:     x{social.get('factor', 1.0):.3f} "
              f"({social.get('adjustment_pct', 0):+.1f}%)")
        print(f"    Buzz {social.get('buzz_score', 0):+.2f} "
              f"({social.get('buzz_source', 'neutral')}), "
              f"sentiment {social.get('sentiment_score', 0):+.2f}, "
              f"quality {social.get('signal_quality', 0):.0%}, "
              f"reach {social.get('reach', 0):,.0f}"
              f"{f', {platforms}' if platforms else ''}")
        if pred.get("social_signal_model_integrated"):
            print("    Integrated into historical comp regression; no separate social overlay applied.")

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
    disagreement = pred.get("model_component_disagreement") or {}
    if disagreement.get("severity") in {"medium", "high"}:
        ratios = disagreement.get("ratios") or {}
        ratio_bits = []
        if ratios.get("seat_vs_comp"):
            ratio_bits.append(f"raw seats vs comps x{ratios['seat_vs_comp']:.2f}")
        if ratios.get("snapshot_vs_base"):
            ratio_bits.append(f"snapshot vs base x{ratios['snapshot_vs_base']:.2f}")
        original_snapshot_weight = pred.get("snapshot_original_model_weight")
        effective_snapshot_weight = pred.get("snapshot_effective_model_weight")
        weight_note = ""
        if (
            original_snapshot_weight is not None
            and effective_snapshot_weight is not None
            and abs(original_snapshot_weight - effective_snapshot_weight) >= 0.005
        ):
            weight_note = (
                f"; snapshot weight {original_snapshot_weight:.0%}"
                f"→{effective_snapshot_weight:.0%}"
            )
        print(
            f"    Model disagreement: {disagreement['severity']} "
            f"({', '.join(ratio_bits) if ratio_bits else 'component spread'}"
            f"{weight_note}); raw seat-only is diagnostic"
        )
    if pred.get("historical_residual_factor") is not None:
        print(f"    Historical residual: x{pred['historical_residual_factor']:.3f} "
              f"(raw x{pred['historical_residual_raw_factor']:.3f}, "
              f"strength {pred['historical_residual_strength']:.0%}, "
              f"n={pred['historical_residual_n']})")
    if poly:
        diff = regression_mid - poly["ev"]
        direction = "higher" if diff > 0 else "lower"
        print(f"    vs Polymarket: {'+' if diff > 0 else ''}{diff:,.1f}M {direction}")
    drivers = pred.get("forecast_feature_importance") or forecast_feature_importance(pred)
    if drivers:
        print("    Feature drivers for current forecast "
              "(model priority; current strength):")
        for driver in drivers[:8]:
            inactive = "" if driver.get("available", True) else ", inactive"
            confidence = driver.get("confidence")
            confidence_note = (
                f", confidence {confidence:.0f}%"
                if confidence is not None else ""
            )
            strength_rank = driver.get("strength_rank")
            strength_note = (
                f", strength #{strength_rank}"
                if strength_rank is not None else ""
            )
            print(
                f"      {driver['rank']}. {driver['driver']} "
                f"({driver['importance']}/100{confidence_note}"
                f"{strength_note}{inactive}): {driver['evidence']}"
            )

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
        actual = h.get("actual_total", h.get("actual"))
        if actual is None:
            actual = h.get("actual")
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
        social_data = load_social_signal_data()
        daily_actual_overrides = load_daily_actual_overrides()
        showtime_link_profiles = load_showtime_link_daypart_profiles()
        theatre_counts = load_theatre_counts()
        metadata = load_movie_metadata()
        movie_match = None
        for m in seat_data:
            if movie_name.lower() in m.lower():
                movie_match = m
                break

        if not movie_match:
            print(f"No seat-count prediction found for {movie_name!r}; not recording actual.")
            return

        nat_count = national_theatre_count_for_movie(movie_match, theatre_counts, metadata=metadata)
        pred = predict_movie(movie_match, seat_data[movie_match],
                            movie_mapping_get(poly_data, movie_match, []), cal,
                            national_theatre_count=nat_count,
                            snapshot_data=movie_mapping_get(snapshot_data, movie_match, {}),
                            social_data=social_data,
                            daily_actual_overrides=daily_actual_overrides,
                            showtime_link_profiles=movie_mapping_get(showtime_link_profiles, movie_match, {}))
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
        (
            daily_predictions,
            raw_daily_predictions,
            daily_theatre_counts,
            daily_coverage_ratios,
        ) = daily_calibration_fields_from_prediction(pred)
        (
            snapshot_daily_predictions,
            snapshot_daily_coverage_ratios,
            snapshot_daily_lead_buckets,
        ) = (
            snapshot_calibration_fields_from_prediction(pred)
        )
        record_daily_actuals = {}
        for day_name in daily_predictions:
            actual_gross_m = daily_actual_override_gross_m_for(
                movie_match,
                day_name,
                daily_actual_overrides,
            )
            if actual_gross_m is not None and actual_gross_m > 0:
                record_daily_actuals[day_name] = actual_gross_m

        record_actual(cal, movie_match, pred_mid, pred_low, pred_high,
                     seat_raw, poly_ev, actual_val, n_th, days,
                     daily_theatre_counts=daily_theatre_counts,
                     daily_coverage_ratios=daily_coverage_ratios,
                     daily_predictions=daily_predictions,
                     raw_daily_predictions=raw_daily_predictions,
                     daily_actuals=record_daily_actuals or None,
                     snapshot_daily_predictions=snapshot_daily_predictions,
                     snapshot_daily_coverage_ratios=snapshot_daily_coverage_ratios,
                     snapshot_daily_lead_buckets=snapshot_daily_lead_buckets,
                     weekend_of=weekend_of,
                     reference_amc_theatres=pred.get("reference_amc_theatres"),
                     model_cohort_key=pred.get("model_cohort_key"),
                     social_signal=pred.get("social_signal"))
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
    social_data = load_social_signal_data(
        weekend_of=replay_weekend,
        through_date=through_date,
    )
    daily_actual_overrides = load_daily_actual_overrides(
        weekend_of=replay_weekend,
        through_date=through_date,
    )
    showtime_link_profiles = load_showtime_link_daypart_profiles(
        weekend_of=replay_weekend,
    )
    theatre_counts = load_theatre_counts()
    metadata = load_movie_metadata()

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
            movie: national_theatre_count_for_movie(movie, theatre_counts, metadata=metadata)
            for movie in movies_to_predict
        }
        relevant_counts = {m: c for m, c in relevant_counts.items() if c}
        if relevant_counts:
            print("  National theatre counts: "
                  f"{', '.join(f'{m}: {c:,}' for m, c in relevant_counts.items())}")
    print(f"{'='*70}")

    for movie in movies_to_predict:
        nat_count = national_theatre_count_for_movie(movie, theatre_counts, metadata=metadata)
        pred = predict_movie(movie, seat_data[movie],
                            movie_mapping_get(poly_data, movie, []), cal, verbose=verbose,
                            national_theatre_count=nat_count,
                            snapshot_data=movie_mapping_get(snapshot_data, movie, {}),
                            social_data=social_data,
                            daily_actual_overrides=daily_actual_overrides,
                            showtime_link_profiles=movie_mapping_get(showtime_link_profiles, movie, {}))
        if pred:
            print_prediction(pred, verbose=verbose)

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
