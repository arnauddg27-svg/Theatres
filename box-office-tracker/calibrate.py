#!/usr/bin/env python3
"""
Auto-Calibration — fetches actual daily box office results and calibrates
predictions day-by-day for continuous accuracy improvement.

Runs every Tuesday (after opening weekend numbers are public on The Numbers).
Compares our Thursday/Friday/Saturday/Sunday predictions against actuals,
updates day weights, scale factors, and feeds accuracy into trading confidence.

Usage:
    python3 calibrate.py                          # Auto-calibrate last weekend
    python3 calibrate.py --actual "Movie" 85.3    # Manual total override
    python3 calibrate.py --actual "Movie" 85.3 --daily-actuals Thursday=10,Friday=22,Saturday=26,Sunday=27
    python3 calibrate.py --history                 # Show past predictions vs actuals
"""

import html
import json
import os
import re
import statistics
import sys
from datetime import datetime, timedelta

try:
    import requests
except ModuleNotFoundError:
    requests = None
from calibration_freeze import (calibration_has_weekend,
                                load_calibration_freeze,
                                save_calibration_freeze)
from model_calibration import (MIN_DAILY_CALIBRATION_COVERAGE,
                               SNAPSHOT_LEAD_BUCKETS,
                               excluded_calibration_days,
                               sanitize_calibration, recalibrate_scale_factor,
                               recalibrate_day_scale_factors,
                               recalibrate_snapshot_day_scale_factors,
                               recalibrate_snapshot_lead_scale_factors,
                               snapshot_calibration_support)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CALIBRATION_JSON = os.path.join(DATA_DIR, "calibration.json")

DEFAULT_CALIBRATION = {
    "history": [],
    "calibration_factors": {
        "amc_market_share": 0.25,
        "overall_scale_factor": 1.0,
        "day_weights": {
            "Thursday": 0.12,
            "Friday": 0.32,
            "Saturday": 0.33,
            "Sunday": 0.23,
        },
        "snapshot_to_day_scale_factors": {
            "Thursday": 1.0,
            "Friday": 1.0,
            "Saturday": 1.0,
            "Sunday": 1.0,
        },
        "snapshot_to_lead_scale_factors": {
            "same_day": 1.0,
            "next_day": 1.0,
            "multi_day": 1.0,
            "long_lead": 1.0,
        },
        "snapshot_calibration_support": {
            "days": {
                "Thursday": {"n": 0, "support": 0.0},
                "Friday": {"n": 0, "support": 0.0},
                "Saturday": {"n": 0, "support": 0.0},
                "Sunday": {"n": 0, "support": 0.0},
            },
            "leads": {
                "same_day": {"n": 0, "support": 0.0},
                "next_day": {"n": 0, "support": 0.0},
                "multi_day": {"n": 0, "support": 0.0},
                "long_lead": {"n": 0, "support": 0.0},
            },
        },
        "format_scale_factors": {},
        "historical_accuracy": [],
        "last_updated": None,
    },
}

OPENING_WEEKEND_DAYS = ("Thursday", "Friday", "Saturday", "Sunday")


def _positive_float(value):
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if f > 0 else None


def _normalize_model_cohort_key(cohorts):
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


def parse_daily_actuals_arg(raw):
    """Parse --daily-actuals values like Thursday=10.0,Friday=22.5."""
    if not raw:
        return {}

    canonical = {day.lower(): day for day in OPENING_WEEKEND_DAYS}
    parsed = {}
    for chunk in raw.split(","):
        part = chunk.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"Daily actual must be Day=value, got {part!r}")
        day_raw, value_raw = part.split("=", 1)
        day_key = day_raw.strip().lower()
        if day_key not in canonical:
            raise ValueError(f"Unknown opening-weekend day {day_raw!r}")
        day = canonical[day_key]
        if day in parsed:
            raise ValueError(f"Duplicate daily actual for {day}")
        try:
            value = float(value_raw.strip())
        except ValueError as exc:
            raise ValueError(f"Invalid gross for {day}: {value_raw!r}") from exc
        if value <= 0:
            raise ValueError(f"Gross for {day} must be positive")
        parsed[day] = value

    return {day: parsed[day] for day in OPENING_WEEKEND_DAYS if day in parsed}


def daily_actuals_from_reported_total(movie, actual_total, daily_actual_overrides,
                                      daily_actual_override_for):
    """Use known daily reports plus an unlabeled weekend remainder.

    A manual total often arrives before the final daily table is available.
    If we already have reported Thursday/Friday overrides, keep those real
    daily actuals for calibration and put the unresolved balance in a
    non-day bucket. That preserves the true weekend total without inventing a
    Saturday/Sunday split.
    """
    known = {}
    for day in OPENING_WEEKEND_DAYS:
        override = daily_actual_override_for(movie, day, daily_actual_overrides)
        if not override:
            continue
        gross = _positive_float(override.get("gross_m"))
        if gross is None:
            continue
        known[day] = gross

    known_total = sum(known.values())
    if not known or known_total <= 0 or known_total >= actual_total:
        return {"Weekend": actual_total}

    remainder = actual_total - known_total
    if remainder <= max(0.05, actual_total * 0.005):
        return known

    known["WeekendRemainder"] = remainder
    return known


def actual_status_is_final(entry):
    """Legacy calibration rows without status are treated as final actuals."""
    return (entry.get("actual_status") or "final") != "provisional"


def final_calibrated_movies(cal, weekend_of):
    """Movies with final actuals already recorded for a weekend."""
    return {
        h["movie"] for h in cal.get("history", [])
        if h.get("weekend_of") == weekend_of
        and h.get("movie")
        and actual_status_is_final(h)
    }


def _remember_reference_amc_theatres(cal, reference_amc_theatres, model_cohort_key=None):
    reference = _positive_float(reference_amc_theatres)
    if not reference:
        return None

    ref = int(round(reference))
    factors = cal.setdefault("calibration_factors", {})
    cohort_key = _normalize_model_cohort_key(model_cohort_key)
    if cohort_key:
        factors.setdefault("reference_amc_theatres_by_cohort", {})[cohort_key] = ref
        if cohort_key == "core":
            factors.setdefault("reference_amc_theatres", ref)
    else:
        factors.setdefault("reference_amc_theatres", ref)
    return ref


def load_calibration():
    if os.path.exists(CALIBRATION_JSON):
        with open(CALIBRATION_JSON, "r") as f:
            cal = json.load(f)
    else:
        cal = json.loads(json.dumps(DEFAULT_CALIBRATION))
    return sanitize_calibration(
        cal,
        day_weights_default=DEFAULT_CALIBRATION["calibration_factors"]["day_weights"],
        default_market_share=DEFAULT_CALIBRATION["calibration_factors"]["amc_market_share"],
    )


def load_prediction_calibration(weekend_of, fallback_cal, require_freeze=False):
    """Use the pre-actual freeze when recording/replacing actuals for a weekend."""
    try:
        frozen = load_calibration_freeze(DATA_DIR, weekend_of)
    except FileNotFoundError:
        if require_freeze:
            raise FileNotFoundError(
                f"Missing pre-actual calibration freeze for {weekend_of}; "
                "refusing to record actuals from live calibration."
            )
        return fallback_cal
    return sanitize_calibration(
        frozen,
        day_weights_default=DEFAULT_CALIBRATION["calibration_factors"]["day_weights"],
        default_market_share=DEFAULT_CALIBRATION["calibration_factors"]["amc_market_share"],
    )


def reset_calibration_factors_to_prediction_baseline(cal, prediction_cal):
    """Anchor actual recording to the clean pre-actual calibration baseline."""
    factors = prediction_cal.get("calibration_factors")
    if isinstance(factors, dict):
        cal["calibration_factors"] = json.loads(json.dumps(factors))
        cal["calibration_factors"].setdefault("historical_accuracy", [])


def accuracy_entry_from_history(entry):
    """Build the historical_accuracy row implied by one calibration history row."""
    total_actual = _positive_float(entry.get("actual_total", entry.get("actual")))
    total_predicted = _positive_float(entry.get("predicted_mid"))
    if not total_actual or not total_predicted:
        return None

    daily_actuals = entry.get("daily_actuals", {}) or {}
    daily_predictions = entry.get("daily_predictions", {}) or {}
    accuracy_entry = {
        "movie": entry.get("movie"),
        "weekend_of": entry.get("weekend_of"),
        "abs_error_pct": round(abs(total_predicted - total_actual) / total_actual * 100, 1),
        "n_theatres": entry.get("n_theatres", 0),
        "n_days": entry.get("n_days", entry.get("days_collected", 0)),
        "coverage_ratio": entry.get("coverage_ratio"),
        "daily_coverage_ratios": entry.get("daily_coverage_ratios", {}),
        "daily_errors": {
            day: round(abs(daily_predictions.get(day, 0) - daily_actuals.get(day, 0))
                       / daily_actuals[day] * 100, 1)
            for day in daily_actuals
            if daily_actuals[day] > 0 and day in daily_predictions
        },
    }
    if entry.get("model_cohort_key"):
        accuracy_entry["model_cohort_key"] = entry["model_cohort_key"]
    if entry.get("reference_amc_theatres"):
        accuracy_entry["reference_amc_theatres"] = entry["reference_amc_theatres"]
    return accuracy_entry


def snapshot_calibration_fields_from_prediction(pred):
    """Extract per-day snapshot predictions for future snapshot calibration."""
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


def rebuild_historical_accuracy(cal):
    """Recreate confidence-tracking accuracy rows from retained history."""
    factors = cal.setdefault("calibration_factors", {})
    rebuilt = [
        accuracy
        for accuracy in (
            accuracy_entry_from_history(entry)
            for entry in cal.get("history", [])[-20:]
        )
        if accuracy
    ]
    factors["historical_accuracy"] = rebuilt[-20:]
    return factors["historical_accuracy"]


def save_calibration(cal):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CALIBRATION_JSON, "w") as f:
        json.dump(cal, f, indent=2)
        f.write("\n")


# ── Fetch Daily Actuals from The Numbers ────────────────────────────────────

def fetch_daily_chart(date_str):
    """Fetch daily domestic box office chart from The Numbers.

    Returns dict of {movie_title: gross_in_millions}.
    The Numbers publishes daily data by the next morning — reliable by Tuesday.
    """
    if requests is None:
        print(f"  ⚠️  requests is not installed; cannot fetch The Numbers for {date_str}")
        return {}

    url = f"https://www.the-numbers.com/box-office-chart/daily/{date_str.replace('-', '/')}"
    # The Numbers can be slow on cold cache hits; the previous 10s timeout
    # caused intermittent day drops that silently understated weekend totals
    # (e.g. weekend of 2026-04-24 lost Friday's $39.5M, recording $57.5M
    # instead of $97M). 30s + one retry covers the common case.
    resp = None
    for attempt in range(2):
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 BoxOfficeTracker/1.0"}, timeout=30)
            if resp.status_code != 200:
                print(f"  ⚠️  The Numbers returned HTTP {resp.status_code} for {date_str}")
                return {}
            break
        except Exception as e:
            if attempt == 0:
                continue
            print(f"  ⚠️  The Numbers fetch failed for {date_str} after retry: {e}")
            return {}
    if resp is None:
        return {}

    results = {}
    table = re.search(r'<table[^>]*>(.*?)</table>', resp.text, re.DOTALL)
    if not table:
        return {}

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table.group(1), re.DOTALL)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        clean = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        if len(clean) >= 4:
            movie = clean[2]
            gross_str = clean[3].replace('$', '').replace(',', '')
            try:
                results[movie] = float(gross_str) / 1_000_000
            except ValueError:
                pass
    return results


def fetch_opening_weekend_daily(movie_title, friday_date):
    """Fetch daily actuals for a movie's opening weekend (Thu-Sun).

    Args:
        movie_title: Movie name to match (fuzzy)
        friday_date: The Friday of opening weekend (YYYY-MM-DD)

    Returns dict of {day_name: gross_in_millions} or None.

    Strategy: try the per-movie page first because it separates Thursday
    PREVIEWS (rank "P", not in the regular daily top-chart) from Friday's
    pure opening-day gross. The Numbers' top-chart endpoint hides preview
    rows, which silently zeros Thursday for any wide-release with previews
    and inflates Friday's apparent share of the weekend in our day_weights
    calibration. If the movie page lookup fails, fall back to the daily
    chart for each date (legacy behavior).
    """
    movie_daily = fetch_movie_daily_history(movie_title, friday_date)
    if movie_daily:
        return movie_daily

    friday = datetime.strptime(friday_date, "%Y-%m-%d")
    dates = [
        ("Thursday", (friday - timedelta(days=1)).strftime("%Y-%m-%d")),
        ("Friday", friday.strftime("%Y-%m-%d")),
        ("Saturday", (friday + timedelta(days=1)).strftime("%Y-%m-%d")),
        ("Sunday", (friday + timedelta(days=2)).strftime("%Y-%m-%d")),
    ]

    movie_lower = movie_title.lower()
    movie_words = set(re.sub(r'[^a-z0-9\s]', '', movie_lower).split())
    daily = {}

    for day_name, date_str in dates:
        chart = fetch_daily_chart(date_str)
        best_gross = None
        best_score = 0.0
        for title, gross in chart.items():
            title_words = set(re.sub(r'[^a-z0-9\s]', '', title.lower()).split())
            if not title_words:
                continue
            overlap = len(movie_words & title_words) / max(len(movie_words), len(title_words))
            # Require at least 60% word overlap to avoid false matches
            if overlap > best_score and overlap >= 0.6:
                best_score = overlap
                best_gross = gross
        if best_gross is not None:
            daily[day_name] = best_gross

    return daily if daily else None


def fetch_movie_daily_history(movie_title, friday_date):
    """Scrape the per-movie daily-history table from The Numbers.

    Unlike the daily top-chart, this table includes a separate Thursday
    PREVIEWS row (rank "P") so we can distinguish preview revenue from
    pure-Friday gross. Preview rows have rank "P" and theatre count 0;
    they're returned under the "Thursday" key as preview-only revenue.

    Returns dict of {day_name: gross_in_millions} or None on failure.
    """
    if requests is None:
        return None

    friday = datetime.strptime(friday_date, "%Y-%m-%d")
    year = friday.year

    # Try common URL patterns with year suffix to disambiguate remakes
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', movie_title).strip().replace(' ', '-')
    candidates = [
        f"https://www.the-numbers.com/movie/{slug}-({year})",
        f"https://www.the-numbers.com/movie/{slug}-({year - 1})",
        f"https://www.the-numbers.com/movie/{slug}",
    ]

    for url in candidates:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 BoxOfficeTracker/1.0"},
                                timeout=30, allow_redirects=True)
            if resp.status_code != 200:
                continue
        except Exception:
            continue

        # Locate the Daily Box Office Performance section
        section_match = re.search(r'Daily Box Office Performance.*?</table>', resp.text, re.DOTALL)
        if not section_match:
            continue

        # Build {date_str -> (rank, gross_millions)} from the daily rows
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', section_match.group(0), re.DOTALL)
        date_grosses = {}
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            # Decode HTML entities (&nbsp; etc.) BEFORE collapsing whitespace,
            # otherwise the date column ends up as 'Apr&nbsp;23,&nbsp;2026'
            # and strptime silently fails for every row.
            clean = [html.unescape(re.sub(r'<[^>]+>', ' ', c)).replace('\xa0', ' ').strip() for c in cells]
            clean = [re.sub(r'\s+', ' ', c) for c in clean]
            if len(clean) < 3:
                continue
            date_raw = clean[0]
            rank = clean[1]
            gross_str = clean[2].replace('$', '').replace(',', '')
            try:
                date_dt = datetime.strptime(date_raw, "%b %d, %Y")
            except ValueError:
                continue
            try:
                gross_m = float(gross_str) / 1_000_000
            except ValueError:
                continue
            date_grosses[date_dt.strftime("%Y-%m-%d")] = (rank, gross_m)

        if not date_grosses:
            continue

        # Map to weekend day labels. Thursday picks up the Preview row even
        # though "regular" daily-chart Thursday would be 0 for this movie.
        # The release-day Friday row may already include those previews as
        # part of the industry "opening day" figure. When a preview row is
        # present, subtract it so our Thursday + Friday day-by-day model does
        # not double-count previews.
        thursday = (friday - timedelta(days=1)).strftime("%Y-%m-%d")
        daily = {}
        for day_name, days_offset in [
            ("Thursday", -1), ("Friday", 0), ("Saturday", 1), ("Sunday", 2)
        ]:
            d = (friday + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            if d in date_grosses:
                rank, gross = date_grosses[d]
                daily[day_name] = gross
        thursday_rank = date_grosses.get(thursday, ("", 0))[0]
        if (
            str(thursday_rank).strip().upper() == "P"
            and daily.get("Thursday", 0) > 0
            and daily.get("Friday", 0) > daily.get("Thursday", 0)
        ):
            daily["Friday"] = max(0.0, daily["Friday"] - daily["Thursday"])
        return daily if daily else None

    return None


# ── Calibration Logic ───────────────────────────────────────────────────────

def record_result(cal, movie, weekend_of, predicted_mid, predicted_low,
                  predicted_high, daily_actuals, daily_predictions,
                  n_theatres, n_days, daily_theatre_counts=None,
                  daily_coverage_ratios=None, raw_daily_predictions=None,
                  snapshot_daily_predictions=None,
                  snapshot_daily_coverage_ratios=None,
                  snapshot_daily_lead_buckets=None,
                  reference_amc_theatres=None, model_cohort_key=None,
                  social_signal=None, model_version=None,
                  actual_source=None, actual_status="final",
                  replace_existing=False):
    """Record daily predicted-vs-actual and update all calibration factors."""
    total_actual = sum(daily_actuals.values())
    total_predicted = predicted_mid

    error_pct = ((total_predicted - total_actual) / total_actual * 100
                 if total_actual > 0 else None)

    entry = {
        "movie": movie,
        "weekend_of": weekend_of,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "predicted_mid": round(total_predicted, 2),
        "predicted_low": round(predicted_low, 2),
        "predicted_high": round(predicted_high, 2),
        "actual_total": round(total_actual, 2),
        "daily_actuals": {k: round(v, 2) for k, v in daily_actuals.items()},
        "daily_predictions": {k: round(v, 2) for k, v in daily_predictions.items()},
        "error_pct": round(error_pct, 1) if error_pct is not None else None,
        "n_theatres": n_theatres,
        "n_days": n_days,
    }
    if model_version:
        entry["model_version"] = model_version
    cohort_key = _normalize_model_cohort_key(model_cohort_key)
    if cohort_key:
        entry["model_cohort_key"] = cohort_key
    reference = _remember_reference_amc_theatres(
        cal,
        reference_amc_theatres,
        model_cohort_key=cohort_key,
    )
    if reference:
        entry["reference_amc_theatres"] = reference
    if actual_source:
        entry["actual_source"] = actual_source
    if actual_status:
        entry["actual_status"] = actual_status
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
    factors = cal["calibration_factors"]
    if replace_existing:
        movie_key = movie.strip().lower()
        cal["history"] = [
            h for h in cal["history"]
            if not (
                (h.get("movie") or "").strip().lower() == movie_key
                and h.get("weekend_of") == weekend_of
            )
        ]
        factors["historical_accuracy"] = [
            h for h in factors.get("historical_accuracy", [])
            if not (
                (h.get("movie") or "").strip().lower() == movie_key
                and h.get("weekend_of") == weekend_of
            )
        ]

    cal["history"].append(entry)

    # 1a. Update overall scale factor (EMA) — kept as a fallback for movies
    #     with no per-day history yet, but predict.py now prefers the per-day
    #     scale factors below for Thu/Fri/Sat/Sun.
    factors["overall_scale_factor"] = recalibrate_scale_factor(
        cal["history"],
        default=1.0,
    )

    # 1b. Per-day scale factors (EMA) — calibration adds up to a total
    #     day-by-day rather than scaling the weekend sum once. Each day's
    #     bias (Thursday previews-only, Saturday partial-scrape, etc.) gets
    #     learned independently. Deterministic: always EMAs from 1.0 over
    #     history, so re-running this on the same history is a no-op.
    factors["day_scale_factors"] = recalibrate_day_scale_factors(cal["history"])
    factors["snapshot_to_day_scale_factors"] = recalibrate_snapshot_day_scale_factors(
        cal["history"]
    )
    factors["snapshot_to_lead_scale_factors"] = recalibrate_snapshot_lead_scale_factors(
        cal["history"],
        day_scales=factors["snapshot_to_day_scale_factors"],
    )
    factors["snapshot_calibration_support"] = snapshot_calibration_support(
        cal["history"]
    )

    # 2. Update day weights from actual daily proportions
    #    Average the actual day splits across all movies with daily data
    all_day_weights = []
    for h in cal["history"]:
        da = h.get("daily_actuals", {})
        opening_da = {
            day: _positive_float(da.get(day))
            for day in OPENING_WEEKEND_DAYS
            if _positive_float(da.get(day)) is not None
        }
        total = sum(opening_da.values())
        if total > 0 and len(opening_da) >= 3:
            all_day_weights.append({d: g / total for d, g in opening_da.items()})

    if all_day_weights:
        new_weights = {}
        for day in ["Thursday", "Friday", "Saturday", "Sunday"]:
            vals = [w.get(day, 0) for w in all_day_weights]
            new_weights[day] = round(statistics.mean(vals), 4) if vals else 0
        # Normalize to sum to 1.0
        total_w = sum(new_weights.values())
        if total_w > 0:
            factors["day_weights"] = {d: round(v / total_w, 4) for d, v in new_weights.items()}

    # 3. Update per-day accuracy (predicted vs actual for each day)
    day_errors = {}
    for h in cal["history"]:
        da = h.get("daily_actuals", {})
        dp = h.get("daily_predictions", {})
        for day in da:
            if day in dp and dp[day] > 0 and da[day] > 0:
                err = abs(dp[day] - da[day]) / da[day]
                day_errors.setdefault(day, []).append(err)

    # 4. Update AMC market share
    share_estimates = []
    for h in cal["history"]:
        if h.get("actual_total", 0) > 0 and h.get("predicted_mid", 0) > 0:
            share = factors.get("amc_market_share", 0.25)
            implied = (h["predicted_mid"] * share) / h["actual_total"]
            if 0.15 < implied < 0.40:
                share_estimates.append(implied)
    if share_estimates:
        factors["amc_market_share"] = round(statistics.median(share_estimates), 4)

    # 5. Update historical accuracy (drives trading confidence)
    if total_actual > 0 and total_predicted > 0:
        abs_error = abs(total_predicted - total_actual) / total_actual
        accuracy_entry = {
            "movie": movie,
            "weekend_of": weekend_of,
            "abs_error_pct": round(abs_error * 100, 1),
            "n_theatres": n_theatres,
            "n_days": n_days,
            "coverage_ratio": entry.get("coverage_ratio"),
            "daily_coverage_ratios": entry.get("daily_coverage_ratios", {}),
            "daily_errors": {
                day: round(abs(daily_predictions.get(day, 0) - daily_actuals.get(day, 0))
                           / daily_actuals[day] * 100, 1)
                for day in daily_actuals
                if daily_actuals[day] > 0 and day in daily_predictions
            },
        }
        if entry.get("model_cohort_key"):
            accuracy_entry["model_cohort_key"] = entry["model_cohort_key"]
        if entry.get("reference_amc_theatres"):
            accuracy_entry["reference_amc_theatres"] = entry["reference_amc_theatres"]
        factors["historical_accuracy"].append(accuracy_entry)
        factors["historical_accuracy"] = factors["historical_accuracy"][-20:]

    factors["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_calibration(cal)
    return entry


def _movie_weekend_key(movie, weekend_of):
    return ((movie or "").strip().lower(), weekend_of)


def _drop_existing_pending_entries(cal, weekend_of, pending):
    """Remove provisional/final rows that this pending batch will replace."""
    keys = {
        _movie_weekend_key(item.get("movie"), weekend_of)
        for item in pending
        if item.get("movie")
    }
    if not keys:
        return

    cal["history"] = [
        h for h in cal.get("history", [])
        if _movie_weekend_key(h.get("movie"), h.get("weekend_of")) not in keys
    ]

    factors = cal.setdefault("calibration_factors", {})
    factors["historical_accuracy"] = [
        h for h in factors.get("historical_accuracy", [])
        if _movie_weekend_key(h.get("movie"), h.get("weekend_of")) not in keys
    ]


def record_pending_calibrations(cal, prediction_cal, weekend_of, pending,
                                actual_source="The Numbers auto-calibrate",
                                actual_status="final"):
    """Record a batch of actuals against one clean pre-actual baseline."""
    if not pending:
        return []

    _drop_existing_pending_entries(cal, weekend_of, pending)
    reset_calibration_factors_to_prediction_baseline(cal, prediction_cal)
    rebuild_historical_accuracy(cal)

    entries = []
    for item in pending:
        pred = item["pred"]
        predicted, predicted_low, predicted_high = item["regression_prediction"]
        entry = record_result(
            cal, item["movie"], weekend_of,
            predicted_mid=predicted,
            predicted_low=predicted_low,
            predicted_high=predicted_high,
            daily_actuals=item["daily_actuals"],
            daily_predictions=item["daily_predictions"],
            n_theatres=pred["n_theatres_total"],
            n_days=pred["n_days"],
            daily_theatre_counts=item.get("daily_theatre_counts"),
            daily_coverage_ratios=item.get("daily_coverage_ratios"),
            raw_daily_predictions=item.get("raw_daily_predictions"),
            snapshot_daily_predictions=item.get("snapshot_daily_predictions"),
            snapshot_daily_coverage_ratios=item.get("snapshot_daily_coverage_ratios"),
            snapshot_daily_lead_buckets=item.get("snapshot_daily_lead_buckets"),
            reference_amc_theatres=pred.get("reference_amc_theatres"),
            model_cohort_key=pred.get("model_cohort_key"),
            social_signal=item.get("social_signal"),
            model_version=pred.get("model_version"),
            actual_source=actual_source,
            actual_status=actual_status,
            replace_existing=True,
        )
        entries.append(entry)

    return entries


def predict_pre_actual_movie(predict_movie_fn, movie, seat_data, poly_data, cal,
                             **kwargs):
    """Replay a forecast without letting reported actual override CSV leak in."""
    kwargs = dict(kwargs)
    kwargs["daily_actual_overrides"] = {}
    return predict_movie_fn(movie, seat_data, poly_data, cal, **kwargs)


# ── Auto-Calibration Pipeline ──────────────────────────────────────────────

def _last_friday():
    today = datetime.now()
    days_since_friday = (today.weekday() - 4) % 7
    return (today - timedelta(days=days_since_friday)).strftime("%Y-%m-%d")


def auto_calibrate():
    """Fetch actual daily results and calibrate against our predictions."""
    from predict import (regression_prediction_values, load_seat_data,
                         load_polymarket_data, load_theatre_counts,
                         load_pre_reservation_data,
                         load_social_signal_data,
                         load_movie_metadata,
                         daily_calibration_fields_from_prediction,
                         national_theatre_count_for_movie,
                         predict_movie)

    cal = load_calibration()
    last_fri = _last_friday()

    print(f"{'='*60}")
    print(f"  Auto-Calibration — weekend of {last_fri}")
    print(f"{'='*60}")

    already_done = final_calibrated_movies(cal, last_fri)

    seat_data = load_seat_data(weekend_of=last_fri)
    poly_data = load_polymarket_data(weekend_of=last_fri)
    snapshot_data = load_pre_reservation_data(weekend_of=last_fri)
    social_data = load_social_signal_data(weekend_of=last_fri)
    # National theatre counts feed the AMC-share / national-count blend in
    # predict_movie. Skipping them here makes calibrate.py's "predicted" number
    # disagree with `predict.py --movie X` output and trains the EMA scale
    # factor against the wrong baseline.
    theatre_counts = load_theatre_counts()
    metadata = load_movie_metadata()

    if not seat_data:
        print(f"\n  No seat data for weekend {last_fri}. Nothing to calibrate.")
        return

    eligible_movies = [movie for movie in seat_data if movie not in already_done]
    if eligible_movies:
        freeze_path = save_calibration_freeze(
            DATA_DIR,
            last_fri,
            cal,
            source="calibrate.py auto_calibrate",
            movies=eligible_movies,
        )
        if freeze_path:
            print(f"\n  Pre-actual calibration freeze: {os.path.relpath(freeze_path, os.getcwd())}")
        elif calibration_has_weekend(cal, last_fri):
            print("\n  ⚠️  Calibration already contains this weekend; not freezing contaminated state.")
    prediction_cal = load_prediction_calibration(
        last_fri,
        cal,
        require_freeze=bool(eligible_movies),
    )

    # Predict everything from a frozen pre-calibration state so later movies do
    # not benefit from actuals recorded earlier in the same Tuesday run.
    pending = []
    for movie in seat_data:
        if movie in already_done:
            print(f"\n  {movie}: already calibrated, skipping")
            continue

        print(f"\n  {movie}:")

        nat_count = national_theatre_count_for_movie(
            movie,
            theatre_counts,
            metadata=metadata,
        )

        # Our prediction
        pred = predict_pre_actual_movie(
            predict_movie,
            movie,
            seat_data[movie],
            poly_data.get(movie, []),
            prediction_cal,
            national_theatre_count=nat_count,
            snapshot_data=snapshot_data.get(movie, {}),
            social_data=social_data,
        )
        if not pred:
            print(f"    No prediction possible")
            continue

        predicted, predicted_low, predicted_high = regression_prediction_values(pred)
        print(f"    Our regression prediction: ${predicted:.1f}M")

        # Fetch actual daily breakdown
        daily_actuals = fetch_opening_weekend_daily(movie, last_fri)
        if not daily_actuals:
            print(f"    No actual daily data available yet")
            continue

        total_actual = sum(daily_actuals.values())
        print(f"    Actual total: ${total_actual:.1f}M")
        for day, gross in sorted(daily_actuals.items(),
                                  key=lambda x: ["Thursday","Friday","Saturday","Sunday"].index(x[0])):
            pct = gross / total_actual * 100 if total_actual > 0 else 0
            print(f"      {day}: ${gross:.1f}M ({pct:.1f}%)")

        # Extract our pre-actual per-day seat predictions for calibration.
        # If a reported daily override was used in prediction, the helper keeps
        # the seat-implied value so the model learns the miss.
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

        pending.append({
            "movie": movie,
            "pred": pred,
            "regression_prediction": (predicted, predicted_low, predicted_high),
            "daily_actuals": daily_actuals,
            "daily_predictions": daily_predictions,
            "raw_daily_predictions": raw_daily_predictions,
            "daily_theatre_counts": daily_theatre_counts,
            "daily_coverage_ratios": daily_coverage_ratios,
            "snapshot_daily_predictions": snapshot_daily_predictions,
            "snapshot_daily_coverage_ratios": snapshot_daily_coverage_ratios,
            "snapshot_daily_lead_buckets": snapshot_daily_lead_buckets,
            "social_signal": pred.get("social_signal"),
        })

    entries = record_pending_calibrations(cal, prediction_cal, last_fri, pending)

    for item, entry in zip(pending, entries):
        movie = item["movie"]

        print(f"\n  Recording calibration for {movie}:")

        error = entry["error_pct"]
        direction = "over" if error and error > 0 else "under"
        print(f"    Error: {abs(error):.1f}% ({direction}-predicted)")

        # Show day weight + per-day scale-factor update
        new_weights = cal["calibration_factors"]["day_weights"]
        new_scales = cal["calibration_factors"].get("day_scale_factors", {})
        print(f"    Updated day weights / scales:")
        for day in ["Thursday", "Friday", "Saturday", "Sunday"]:
            w = new_weights.get(day, 0)
            s = new_scales.get(day, 1.0)
            print(f"      {day}: weight={w:.1%}  scale={s:.3f}")

    # Summary
    factors = cal["calibration_factors"]
    acc = factors.get("historical_accuracy", [])
    if acc:
        mean_err = statistics.mean(a["abs_error_pct"] for a in acc)
        print(f"\n  Overall: scale={factors['overall_scale_factor']:.3f}, "
              f"mean error={mean_err:.1f}%, "
              f"movies calibrated={len(cal['history'])}")

    print(f"\n{'='*60}")


def show_history():
    cal = load_calibration()
    history = cal.get("history", [])
    if not history:
        print("No calibration history yet.")
        return

    print(f"\n{'='*70}")
    print(f"  Calibration History")
    print(f"{'='*70}")
    print(f"  {'Movie':<25} {'Weekend':<12} {'Predicted':>10} {'Actual':>10} {'Error':>8}")
    print(f"  {'─'*25} {'─'*12} {'─'*10} {'─'*10} {'─'*8}")
    for h in history:
        pred = f"${h['predicted_mid']:.1f}M"
        actual = f"${h['actual_total']:.1f}M" if h.get("actual_total") else "—"
        err = f"{h['error_pct']:+.1f}%" if h.get("error_pct") is not None else "—"
        print(f"  {h['movie'][:25]:<25} {h.get('weekend_of','?'):<12} {pred:>10} {actual:>10} {err:>8}")

        # Show daily breakdown if available
        da = h.get("daily_actuals", {})
        dp = h.get("daily_predictions", {})
        dc = h.get("daily_theatre_counts", {}) or {}
        dr = h.get("daily_coverage_ratios", {}) or {}
        excluded_days = excluded_calibration_days(h)
        if da:
            for day in ["Thursday", "Friday", "Saturday", "Sunday"]:
                a = da.get(day)
                p = dp.get(day)
                if a is not None:
                    a_str = f"${a:.1f}M"
                    p_str = f"${p:.1f}M" if p else "—"
                    err_d = f"{abs(p-a)/a*100:.0f}%" if p and a > 0 else "—"
                    coverage = ""
                    if day in dc or day in dr:
                        coverage = (
                            f"  coverage={dc.get(day, '?')} theatres"
                            f"{f' ({dr[day]:.0%})' if day in dr else ''}"
                        )
                    if day in excluded_days:
                        coverage = f"{coverage}  excluded-from-calibration"
                    print(f"    {day:<12} pred={p_str:>8}  actual={a_str:>8}  err={err_d}{coverage}")

    factors = cal.get("calibration_factors", {})
    print(f"\n  Scale: {factors.get('overall_scale_factor', 1.0):.4f}")
    print(f"  AMC share: {factors.get('amc_market_share', 0.25):.2%}")
    print(f"  Day weights: {factors.get('day_weights', {})}")
    print(f"  Day scales: {factors.get('day_scale_factors', {})}")


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if "--history" in args:
        show_history()
    elif "--actual" in args:
        idx = args.index("--actual")
        if idx + 2 >= len(args):
            print("Usage: --actual \"Movie Name\" 85.3 [--daily-actuals Thursday=10,Friday=22,Saturday=26,Sunday=27]")
            sys.exit(1)
        movie_name = args[idx + 1]
        try:
            actual_val = float(args[idx + 2])
        except ValueError:
            print("Usage: --actual \"Movie Name\" 85.3 [--daily-actuals Thursday=10,Friday=22,Saturday=26,Sunday=27]")
            sys.exit(1)

        manual_daily_actuals = None
        if "--daily-actuals" in args:
            daily_idx = args.index("--daily-actuals")
            if daily_idx + 1 >= len(args):
                print("Usage: --daily-actuals Thursday=10,Friday=22,Saturday=26,Sunday=27")
                sys.exit(1)
            try:
                manual_daily_actuals = parse_daily_actuals_arg(args[daily_idx + 1])
            except ValueError as exc:
                print(f"Invalid --daily-actuals: {exc}")
                sys.exit(1)
            manual_total = sum(manual_daily_actuals.values())
            tolerance = max(0.1, actual_val * 0.01)
            if abs(manual_total - actual_val) > tolerance:
                print(
                    f"--daily-actuals sum ${manual_total:.1f}M does not match "
                    f"--actual ${actual_val:.1f}M"
                )
                sys.exit(1)

        actual_source = None
        if "--actual-source" in args:
            source_idx = args.index("--actual-source")
            if source_idx + 1 >= len(args):
                print("Usage: --actual-source \"Source note\"")
                sys.exit(1)
            actual_source = args[source_idx + 1]

        from predict import (regression_prediction_values, load_seat_data,
                             load_polymarket_data, load_theatre_counts,
                             load_pre_reservation_data,
                             load_social_signal_data,
                             load_movie_metadata,
                             load_daily_actual_overrides,
                             daily_actual_override_for,
                             daily_calibration_fields_from_prediction,
                             national_theatre_count_for_movie,
                             predict_movie)
        cal = load_calibration()
        weekend_of = _last_friday()
        seat_data = load_seat_data(weekend_of=weekend_of)
        poly_data = load_polymarket_data(weekend_of=weekend_of)
        snapshot_data = load_pre_reservation_data(weekend_of=weekend_of)
        social_data = load_social_signal_data(weekend_of=weekend_of)
        theatre_counts = load_theatre_counts()
        metadata = load_movie_metadata()

        matched_movie = None
        nat_count = None
        for m in seat_data:
            if movie_name.lower() in m.lower():
                matched_movie = m
                nat_count = national_theatre_count_for_movie(
                    m,
                    theatre_counts,
                    metadata=metadata,
                )
                break

        if not matched_movie:
            print(f"No seat-count prediction found for {movie_name!r}; not recording actual.")
            sys.exit(1)

        freeze_path = save_calibration_freeze(
            DATA_DIR,
            weekend_of,
            cal,
            source="calibrate.py --actual",
            movies=[matched_movie],
        )
        if freeze_path:
            print(f"Pre-actual calibration freeze: {os.path.relpath(freeze_path, os.getcwd())}")
        elif calibration_has_weekend(cal, weekend_of):
            print("Calibration already contains this weekend; not freezing contaminated state.")

        prediction_cal = load_prediction_calibration(
            weekend_of,
            cal,
            require_freeze=True,
        )
        pred = predict_pre_actual_movie(
            predict_movie,
            matched_movie,
            seat_data[matched_movie],
            poly_data.get(matched_movie, []),
            prediction_cal,
            national_theatre_count=nat_count,
            snapshot_data=snapshot_data.get(matched_movie, {}),
            social_data=social_data,
        )
        if not pred:
            print(f"No prediction found for {matched_movie!r}; not recording actual.")
            sys.exit(1)

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

        if manual_daily_actuals:
            daily_actuals = manual_daily_actuals
            if not actual_source:
                actual_source = "manual daily actuals"
            actual_status = "provisional"
        else:
            # Try fetching daily breakdown, fall back to total-only
            daily_actuals = fetch_opening_weekend_daily(matched_movie, _last_friday())
            if not daily_actuals:
                daily_actuals = daily_actuals_from_reported_total(
                    matched_movie,
                    actual_val,
                    load_daily_actual_overrides(weekend_of=_last_friday()),
                    daily_actual_override_for,
                )
                actual_status = "provisional"
            else:
                actual_status = "final"

        predicted_mid, predicted_low, predicted_high = regression_prediction_values(pred)
        reset_calibration_factors_to_prediction_baseline(cal, prediction_cal)
        rebuild_historical_accuracy(cal)

        record_result(
            cal, matched_movie, weekend_of,
            predicted_mid=predicted_mid,
            predicted_low=predicted_low,
            predicted_high=predicted_high,
            daily_actuals=daily_actuals,
            daily_predictions=daily_predictions,
            n_theatres=pred["n_theatres_total"],
            n_days=pred["n_days"],
            daily_theatre_counts=daily_theatre_counts,
            daily_coverage_ratios=daily_coverage_ratios,
            raw_daily_predictions=raw_daily_predictions,
            snapshot_daily_predictions=snapshot_daily_predictions,
            snapshot_daily_coverage_ratios=snapshot_daily_coverage_ratios,
            snapshot_daily_lead_buckets=snapshot_daily_lead_buckets,
            reference_amc_theatres=pred.get("reference_amc_theatres"),
            model_cohort_key=pred.get("model_cohort_key"),
            social_signal=pred.get("social_signal"),
            model_version=pred.get("model_version"),
            actual_source=actual_source,
            actual_status=actual_status,
            replace_existing=True,
        )
        print(f"Recorded: {matched_movie} actual=${actual_val}M")
    else:
        auto_calibrate()
