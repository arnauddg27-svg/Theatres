#!/usr/bin/env python3
"""Auditable feature engineering and model reporting helpers.

This module is deliberately independent from ``predict.py`` so the regression
pipeline can be inspected, exported, and tested without running the production
forecast entrypoint. It turns raw scraper artifacts into supervised examples:

* snapshot reservations -> final showtime attendance
* seat-count rows -> AMC daily demand features
* settled calibration rows -> movie/weekend actual features

The functions here do not scrape, mutate canonical data, or write calibration.
Only explicit export helpers write derived audit artifacts.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_AUDIT_DIR = DATA_DIR / "model-audits"
OPENING_WEEKEND_DAYS = ("Thursday", "Friday", "Saturday", "Sunday")
TIMEZONE_GROUPS = ("ET", "CT", "PT")
EXCLUDED_THEATRE_NAME_PREFIXES = ("AMC CLASSIC",)
FORECAST_CUTS = (
    ("thursday_morning", -1, "10:00"),
    ("thursday_night", -1, "23:59"),
    ("friday_morning", 0, "10:00"),
    ("saturday_morning", 1, "10:00"),
    ("sunday_morning", 2, "10:00"),
    ("final_pre_estimate", 2, "23:59"),
)
WIDE_RELEASE_BASELINE_THEATRES = 4000
FOOTPRINT_EXPONENT = 0.18
MIN_FOOTPRINT_FACTOR = 0.55
MAX_FOOTPRINT_FACTOR = 1.08
HEADLINE_MIN_ACTUAL_M = 10.0
HEADLINE_MIN_COVERAGE_RATIO = 0.60
HEADLINE_MIN_STAGE_COVERAGE_RATIO = 0.80


def _clean_key(value: str | None) -> str:
    return "".join(ch for ch in (value or "").lower() if ch.isalnum())


def _float(value, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def parse_showtime_hour(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    match = re.search(r"(\d{1,2}):(\d{2})\s*(AM|PM)", str(value).strip(), re.I)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    ampm = match.group(3).upper()
    if ampm == "PM" and hour != 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    return hour, minute


def showtime_datetime(show_date: str | None, showtime: str | None) -> datetime | None:
    parsed_time = parse_showtime_hour(showtime)
    if not show_date or parsed_time is None:
        return None
    try:
        base = datetime.strptime(show_date, "%Y-%m-%d")
    except ValueError:
        return None
    hour, minute = parsed_time
    return base.replace(hour=hour, minute=minute, tzinfo=timezone.utc)


def read_csv_rows(path: Path | str) -> list[dict[str, str]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path | str, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def filter_rows_as_of(rows: Iterable[dict], field: str, as_of: datetime | str | None) -> list[dict]:
    """Keep rows whose timestamp field exists and is <= the forecast cut."""
    if as_of is None:
        return list(rows)
    if isinstance(as_of, str):
        parsed = parse_datetime(as_of)
        if parsed is None:
            parsed = datetime.strptime(as_of, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        as_of_dt = parsed
    else:
        as_of_dt = as_of if as_of.tzinfo else as_of.replace(tzinfo=timezone.utc)

    kept = []
    for row in rows:
        row_dt = parse_datetime(row.get(field, ""))
        if row_dt is not None and row_dt <= as_of_dt:
            kept.append(row)
    return kept


def _showtime_id_from_url(value: str | None) -> str:
    if not value:
        return ""
    match = re.search(r"/showtimes/([^/?#]+)/seats", value)
    return match.group(1) if match else ""


def showtime_match_key(row: dict, *, snapshot: bool = False) -> tuple:
    """Stable showtime identity for joining snapshot rows to final seat rows."""
    show_date = row.get("show_date") if snapshot else row.get("date")
    showtime_id = (
        row.get("showtime_id")
        or _showtime_id_from_url(row.get("amc_seat_map_url"))
        or ""
    )
    fallback = (
        row.get("auditorium_name", ""),
        row.get("auditorium_type", ""),
        row.get("showtime", ""),
    )
    identity = ("id", showtime_id) if showtime_id else ("fallback", fallback)
    return (
        row.get("weekend_of", ""),
        _clean_key(row.get("movie_title", "")),
        show_date or "",
        (row.get("theatre_name") or "").strip().lower(),
        row.get("timezone", ""),
        identity,
    )


def _day_name(row: dict, date_field: str = "date") -> str:
    value = row.get("day_of_week") or ""
    if value:
        return value
    date_value = row.get(date_field) or row.get("show_date") or ""
    try:
        return datetime.strptime(date_value, "%Y-%m-%d").strftime("%A")
    except ValueError:
        return ""


def build_snapshot_to_final_showtime_rows(snapshot_rows: Iterable[dict],
                                          seat_rows: Iterable[dict],
                                          as_of: datetime | str | None = None
                                          ) -> list[dict]:
    """Build supervised rows from pre-reservation snapshots to final attendance."""
    snapshots = filter_rows_as_of(snapshot_rows, "snapshot_time", as_of)
    seats = filter_rows_as_of(seat_rows, "check_time", as_of)

    latest_seats: dict[tuple, dict] = {}
    for row in seats:
        key = showtime_match_key(row, snapshot=False)
        sort_key = row.get("check_time", "") or row.get("run_id", "")
        current = latest_seats.get(key)
        if current is None or sort_key > current.get("_sort_key", ""):
            latest_seats[key] = {**row, "_sort_key": sort_key}

    training = []
    for snap in snapshots:
        key = showtime_match_key(snap, snapshot=True)
        final = latest_seats.get(key)
        if not final:
            continue
        snapshot_time = parse_datetime(snap.get("snapshot_time", ""))
        final_time = parse_datetime(final.get("check_time", ""))
        if snapshot_time is None or final_time is None or final_time <= snapshot_time:
            continue
        show_dt = showtime_datetime(snap.get("show_date"), snap.get("showtime"))
        minutes_to_showtime = None
        if show_dt is not None:
            minutes_to_showtime = (show_dt - snapshot_time).total_seconds() / 60
        reserved = _int(snap.get("reserved_seats"))
        final_sold = _int(final.get("seats_sold"))
        capacity = max(_int(snap.get("total_seats")), _int(final.get("total_seats")))
        if capacity <= 0:
            continue
        training.append({
            "weekend_of": snap.get("weekend_of", ""),
            "movie_title": snap.get("movie_title", ""),
            "show_date": snap.get("show_date", ""),
            "day_of_week": _day_name(snap, date_field="show_date"),
            "theatre_name": snap.get("theatre_name", ""),
            "timezone": snap.get("timezone", ""),
            "showtime": snap.get("showtime", ""),
            "showtime_id": snap.get("showtime_id") or _showtime_id_from_url(snap.get("amc_seat_map_url")),
            "snapshot_time": snap.get("snapshot_time", ""),
            "final_check_time": final.get("check_time", ""),
            "minutes_to_showtime": round(minutes_to_showtime or 0, 2),
            "capacity": capacity,
            "snapshot_reserved_seats": reserved,
            "snapshot_occupancy": round(reserved / capacity, 4),
            "final_seats_sold": final_sold,
            "final_occupancy": round(final_sold / capacity, 4),
            "pickup_seats": max(0, final_sold - reserved),
            "pickup_ratio": round(final_sold / reserved, 4) if reserved > 0 else None,
        })
    return training


def _coverage_tier(value: float) -> str:
    if value >= 0.85:
        return "high"
    if value >= 0.50:
        return "medium"
    return "low"


def _daypart_flags(hours: list[float]) -> dict[str, int]:
    return {
        "has_morning": int(any(hour < 12 for hour in hours)),
        "has_afternoon": int(any(12 <= hour < 17 for hour in hours)),
        "has_evening": int(any(17 <= hour < 22 for hour in hours)),
        "has_late": int(any(hour >= 22 for hour in hours)),
    }


def build_seat_to_amc_day_rows(seat_rows: Iterable[dict],
                               expected_timezone_counts: dict[str, int] | None = None
                               ) -> list[dict]:
    """Aggregate scraper seat rows into movie/day AMC-demand examples."""
    expected_timezone_counts = expected_timezone_counts or {}
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in seat_rows:
        movie = row.get("movie_title", "")
        date = row.get("date", "")
        if not movie or not date:
            continue
        groups[(row.get("weekend_of", ""), movie, date, _day_name(row))].append(row)

    expected_total = sum(expected_timezone_counts.values()) or None
    table = []
    for (weekend_of, movie, date, day_name), rows in sorted(groups.items()):
        theatres_by_tz: dict[str, set[str]] = defaultdict(set)
        theatres = set()
        hours = []
        capacity = 0
        sold = 0
        for row in rows:
            theatre = (row.get("theatre_name") or "").strip()
            tz = row.get("timezone", "")
            if theatre:
                theatres.add(theatre)
                if tz:
                    theatres_by_tz[tz].add(theatre)
            capacity += _int(row.get("total_seats"))
            sold += _int(row.get("seats_sold"))
            parsed_time = parse_showtime_hour(row.get("showtime"))
            if parsed_time:
                hours.append(parsed_time[0] + parsed_time[1] / 60)
        expected_count = expected_total or max(len(theatres), 1)
        coverage = min(1.0, len(theatres) / expected_count) if expected_count else 0.0
        timezone_coverage = (
            sum(min(len(theatres_by_tz.get(tz, set())), expected_timezone_counts.get(tz, 0))
                for tz in TIMEZONE_GROUPS)
            / expected_total
            if expected_total else coverage
        )
        row = {
            "weekend_of": weekend_of,
            "movie_title": movie,
            "date": date,
            "day_of_week": day_name,
            "n_showings": len(rows),
            "n_theatres": len(theatres),
            "sample_capacity": capacity,
            "sample_seats_sold": sold,
            "sample_occupancy": round(sold / capacity, 4) if capacity else 0.0,
            "timezone_coverage_ratio": round(timezone_coverage, 4),
            "theatre_coverage_ratio": round(coverage, 4),
            "coverage_tier": _coverage_tier(min(coverage, timezone_coverage)),
            "avg_showings_per_theatre": round(len(rows) / len(theatres), 3) if theatres else 0.0,
            "earliest_showtime_hour": round(min(hours), 2) if hours else None,
            "latest_showtime_hour": round(max(hours), 2) if hours else None,
        }
        row.update(_daypart_flags(hours))
        for tz in TIMEZONE_GROUPS:
            row[f"{tz}_theatres"] = len(theatres_by_tz.get(tz, set()))
            row[f"missing_timezone_{tz}"] = int(
                bool(expected_timezone_counts)
                and expected_timezone_counts.get(tz, 0) > 0
                and len(theatres_by_tz.get(tz, set())) == 0
            )
        table.append(row)
    return table


def release_footprint_features(theatre_count: int | float | None) -> dict:
    """Non-linear national footprint features for AMC-to-national conversion."""
    count = max(0.0, _float(theatre_count, 0.0))
    if count <= 0:
        return {
            "national_theatre_count": 0,
            "log_theatre_count": 0.0,
            "footprint_factor": 1.0,
            "wide_release_ratio": 1.0,
        }
    ratio = count / WIDE_RELEASE_BASELINE_THEATRES
    # A 2,600-theatre release is not 65% of a 4,000-theatre release in gross
    # potential because those theatres skew toward larger chains and stronger
    # markets. Use a gentle exponent and bounds instead of direct scaling.
    factor = ratio ** FOOTPRINT_EXPONENT
    factor = max(MIN_FOOTPRINT_FACTOR, min(MAX_FOOTPRINT_FACTOR, factor))
    return {
        "national_theatre_count": int(round(count)),
        "log_theatre_count": round(math.log1p(count), 5),
        "footprint_factor": round(factor, 5),
        "wide_release_ratio": round(ratio, 5),
    }


def _metadata_by_movie(rows: Iterable[dict]) -> dict[str, dict]:
    return {_clean_key(row.get("movie", "")): row for row in rows if row.get("movie")}


def _social_by_movie(rows: Iterable[dict]) -> dict[str, dict]:
    return {_clean_key(row.get("movie_title", "") or row.get("movie", "")): row for row in rows}


def build_movie_weekend_actual_rows(calibration: dict,
                                    metadata_rows: Iterable[dict] | None = None,
                                    social_rows: Iterable[dict] | None = None
                                    ) -> list[dict]:
    metadata = _metadata_by_movie(metadata_rows or [])
    social = _social_by_movie(social_rows or [])
    rows = []
    for entry in calibration.get("history", []) or []:
        movie = entry.get("movie", "")
        if not movie:
            continue
        meta = metadata.get(_clean_key(movie), {})
        social_row = social.get(_clean_key(movie), {})
        theatre_count = (
            entry.get("national_theatre_count")
            or meta.get("national_theatre_count")
            or entry.get("theatre_count")
        )
        row = {
            "movie_title": movie,
            "weekend_of": entry.get("weekend_of", ""),
            "actual_total_m": _float(entry.get("actual_total", entry.get("actual"))),
            "predicted_mid_m": _float(entry.get("predicted_mid")),
            "error_pct": _float(entry.get("error_pct")),
            "coverage_ratio": _float(entry.get("coverage_ratio")),
            "genre": meta.get("genre", ""),
            "audience_type": meta.get("audience_type", ""),
            "franchise_type": meta.get("franchise_type", ""),
            "rating": meta.get("rating", ""),
            "imdb_rating": _float(meta.get("imdb_rating")),
            "rt_audience_score": _float(meta.get("rt_audience_score")),
            "social_buzz_score": _float(social_row.get("buzz_score", meta.get("social_buzz_score"))),
            "social_sentiment_score": _float(social_row.get("sentiment_score", meta.get("social_sentiment_score"))),
        }
        row.update(release_footprint_features(theatre_count))
        daily_actuals = entry.get("daily_actuals", {}) or {}
        daily_predictions = (
            entry.get("raw_daily_predictions")
            or entry.get("daily_predictions", {})
            or {}
        )
        for day in OPENING_WEEKEND_DAYS:
            row[f"{day.lower()}_actual_m"] = _float(daily_actuals.get(day))
            row[f"{day.lower()}_predicted_m"] = _float(daily_predictions.get(day))
        rows.append(row)
    return rows


def residual_errors_from_history(calibration: dict) -> list[float]:
    errors = []
    for entry in calibration.get("history", []) or []:
        actual = _float(entry.get("actual_total", entry.get("actual")))
        pred = _float(entry.get("predicted_mid"))
        if actual > 0 and pred > 0:
            errors.append((pred - actual) / actual)
    return errors


def calibrated_intervals(point_m: float,
                         residual_errors: Iterable[float] | None = None,
                         coverage_ratio: float | None = None,
                         missing_risk_count: int = 0) -> dict[str, dict]:
    """Return simple conformal-style absolute percentage intervals."""
    point = max(0.0, _float(point_m))
    errors = [abs(_float(err)) for err in (residual_errors or []) if err is not None]
    if errors:
        base = max(0.08, median(errors))
    else:
        base = 0.20
    coverage = max(0.0, min(1.0, _float(coverage_ratio, 0.5)))
    coverage_penalty = (1.0 - coverage) * 0.45
    risk_penalty = min(0.35, missing_risk_count * 0.08)
    p50 = base * 0.75 + coverage_penalty * 0.50 + risk_penalty * 0.35
    p80 = base * 1.35 + coverage_penalty + risk_penalty
    p90 = base * 1.80 + coverage_penalty * 1.25 + risk_penalty * 1.25

    intervals = {}
    for label, pct in (("50", p50), ("80", p80), ("90", p90)):
        low = max(0.0, point * (1.0 - pct))
        high = point * (1.0 + pct)
        intervals[label] = {
            "low_m": round(low, 2),
            "mid_m": round(point, 2),
            "high_m": round(high, 2),
            "width_m": round(high - low, 2),
            "pct_half_width": round(pct, 4),
        }
    return intervals


def coverage_grade(coverage_ratio: float | None) -> str:
    coverage = _float(coverage_ratio, 0.0)
    if coverage >= 0.85:
        return "high"
    if coverage >= 0.60:
        return "medium"
    return "low"


def stage_expected_days(forecast_cut: str | None) -> tuple[str, ...]:
    """Days that should be available for a forecast cut."""
    return {
        "thursday_night": ("Thursday",),
        "friday_morning": ("Thursday",),
        "saturday_morning": ("Thursday", "Friday"),
        "sunday_morning": ("Thursday", "Friday", "Saturday"),
        "final_pre_estimate": ("Thursday", "Friday", "Saturday", "Sunday"),
    }.get(str(forecast_cut or ""), ())


def stage_coverage_ratio(daily_details: dict | None,
                         expected_days: Iterable[str]) -> float:
    """Average coverage for only the days expected at this forecast stage.

    Missing expected days count as zero. This prevents Friday-morning audits
    from being penalized for not having Saturday/Sunday while still penalizing a
    final-pre-estimate replay that lacks Sunday.
    """
    expected = [day for day in expected_days if day]
    if not expected:
        return 0.0
    details = daily_details or {}
    coverages = []
    for day in expected:
        detail = details.get(day) or {}
        coverage = detail.get("effective_coverage_ratio")
        if coverage is None:
            coverage = detail.get("coverage_ratio")
        coverages.append(max(0.0, min(1.0, _float(coverage))))
    return round(sum(coverages) / len(coverages), 4)


def missing_data_risks(profile: dict | None) -> list[str]:
    profile = profile or {}
    risks = []
    for day in profile.get("missing_days") or []:
        risks.append(f"missing {day}")
    for day in profile.get("missing_timezone_days") or []:
        risks.append(f"missing timezone coverage on {day}")
    for day in profile.get("partial_daypart_days") or []:
        risks.append(f"partial daypart coverage on {day}")
    snapshot_days = profile.get("snapshot_days") or []
    if snapshot_days and _float(profile.get("snapshot_coverage_ratio"), 1.0) < 0.60:
        risks.append("thin snapshot theatre coverage")
    return risks


def build_model_card(prediction: dict,
                     residual_errors: Iterable[float] | None = None,
                     audit_summary: dict | None = None) -> dict:
    """Create a structured model card for one forecast."""
    point = (
        prediction.get("model_forecast_mid_m")
        or prediction.get("regression_mid_m")
        or prediction.get("blended_m")
        or prediction.get("seat_mid_m")
        or 0.0
    )
    coverage = prediction.get("seat_weighted_coverage_ratio")
    if coverage is None:
        coverage = prediction.get("coverage_ratio")
    profile = prediction.get("missing_data_profile") or {}
    risks = missing_data_risks(profile)
    intervals = calibrated_intervals(
        point,
        residual_errors=residual_errors,
        coverage_ratio=coverage,
        missing_risk_count=len(risks),
    )
    grade = coverage_grade(coverage)
    components = {
        "seat_weight": round(_float(prediction.get("seat_primary_w_direct"), 1.0), 4),
        "comp_weight": round(_float(prediction.get("seat_primary_w_comp"), 0.0), 4),
        "snapshot_weight": round(_float(prediction.get("snapshot_model_weight"), 0.0), 4),
        "social_factor": round(_float(prediction.get("social_factor"), 1.0), 5),
        "theatre_count": _int(prediction.get("national_theatre_count")),
        "coverage_ratio": round(_float(coverage), 4),
    }
    card = {
        "movie": prediction.get("movie", ""),
        "model_version": prediction.get("model_version", ""),
        "point_estimate_m": round(_float(point), 2),
        "intervals": intervals,
        "coverage_grade": grade,
        "high_confidence": grade == "high" and not risks,
        "components": components,
        "biggest_missing_data_risks": risks,
        "source": prediction.get("model_forecast_source") or prediction.get("regression_source", ""),
        "basis": prediction.get("model_forecast_basis") or prediction.get("regression_basis", ""),
        "uses_polymarket": bool(prediction.get("model_forecast_uses_polymarket")),
    }
    if audit_summary:
        card["backtest"] = audit_summary
    return card


def precision_quality(row: dict) -> dict:
    """Classify whether a replay row belongs in headline precision metrics.

    Raw rows remain exported for transparency. The headline slice excludes rows
    that are not comparable to the current trading target: very low-gross films,
    very thin data coverage, missing pre-actual freezes, or known partial-day
    calibration exclusions.
    """
    actual = _float(row.get("actual_m"))
    predicted = _float(row.get("predicted_m"))
    coverage = _float(row.get("coverage_ratio"))
    stage_coverage = _float(row.get("stage_coverage_ratio"), -1.0)
    coverage_basis = stage_coverage if stage_coverage >= 0 else coverage
    min_coverage = (
        HEADLINE_MIN_STAGE_COVERAGE_RATIO
        if stage_coverage >= 0
        else HEADLINE_MIN_COVERAGE_RATIO
    )
    excluded_day_count = _int(row.get("excluded_day_count"))
    calibration_source = str(row.get("calibration_source") or "")
    reasons = []
    warnings = []
    if actual <= 0 or predicted <= 0:
        reasons.append("missing_prediction_or_actual")
    if 0 < actual < HEADLINE_MIN_ACTUAL_M:
        reasons.append("low_gross")
    if coverage_basis < min_coverage:
        reasons.append("low_coverage")
    if calibration_source == "live-fallback":
        reasons.append("missing_pre_actual_freeze")
    if excluded_day_count > 0:
        warnings.append("known_partial_day_exclusions")
    return {
        "headline_eligible": int(not reasons),
        "quality_segment": "headline_clean" if not reasons else "excluded",
        "quality_reasons": ";".join(reasons),
        "quality_warnings": ";".join(warnings),
        "quality_basis": "stage" if stage_coverage >= 0 else "weekend",
    }


def apply_precision_quality(rows: Iterable[dict]) -> list[dict]:
    return [{**row, **precision_quality(row)} for row in rows]


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def theatre_name_is_excluded(name: str) -> bool:
    normalized = (name or "").strip().upper()
    return any(normalized.startswith(prefix) for prefix in EXCLUDED_THEATRE_NAME_PREFIXES)


def expected_timezone_counts_from_theatres(data_dir: Path | str = DATA_DIR) -> dict[str, int]:
    """Count configured AMC theatres by timezone from core + expansion files."""
    data_dir = Path(data_dir)
    counts = {tz: 0 for tz in TIMEZONE_GROUPS}
    seen = {tz: set() for tz in TIMEZONE_GROUPS}
    for filename in ("theatres-all.json", "theatres-expansion.json"):
        data = _read_json(data_dir / filename)
        for tz in TIMEZONE_GROUPS:
            for item in data.get(tz, []) or []:
                if not isinstance(item, dict):
                    continue
                name = (item.get("name") or "").strip()
                if name and not theatre_name_is_excluded(name):
                    seen[tz].add(name)
    for tz in TIMEZONE_GROUPS:
        counts[tz] = len(seen[tz])
    return {tz: count for tz, count in counts.items() if count > 0}


def export_training_tables(data_dir: Path | str = DATA_DIR,
                           output_dir: Path | str = MODEL_AUDIT_DIR,
                           as_of: datetime | str | None = None) -> dict:
    """Export all supervised tables and return a manifest."""
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    seat_rows = read_csv_rows(data_dir / "seat-counts.csv")
    snapshot_rows = read_csv_rows(data_dir / "pre-reservation-snapshots.csv")
    metadata_rows = read_csv_rows(data_dir / "movie-metadata.csv")
    social_rows = read_csv_rows(data_dir / "social-signals.csv")
    calibration = _read_json(data_dir / "calibration.json")

    snapshot_table = build_snapshot_to_final_showtime_rows(
        snapshot_rows,
        seat_rows,
        as_of=as_of,
    )
    seat_day_table = build_seat_to_amc_day_rows(
        seat_rows,
        expected_timezone_counts=expected_timezone_counts_from_theatres(data_dir),
    )
    movie_actual_table = build_movie_weekend_actual_rows(
        calibration,
        metadata_rows=metadata_rows,
        social_rows=social_rows,
    )

    tables = {
        "snapshot_to_final_showtimes": snapshot_table,
        "seat_to_amc_day": seat_day_table,
        "movie_weekend_actuals": movie_actual_table,
    }
    manifest = {}
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        path = output_dir / f"{name}.csv"
        write_csv_rows(path, rows)
        manifest[name] = {
            "path": str(path),
            "rows": len(rows),
        }
    manifest_path = output_dir / "training-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest


def summarize_backtest_rows(rows: list[dict]) -> dict:
    """Summarize replay/backtest rows with MAPE, MAE, bias, and coverage."""
    if not rows:
        return {
            "n": 0,
            "mae_m": 0.0,
            "mape": 0.0,
            "bias_m": 0.0,
            "interval_80_coverage": None,
        }
    errors = []
    ape = []
    inside_80 = []
    for row in rows:
        actual = _float(row.get("actual_m"))
        pred = _float(row.get("predicted_m"))
        if actual <= 0 or pred <= 0:
            continue
        err = pred - actual
        errors.append(err)
        ape.append(abs(err) / actual)
        low = _float(row.get("interval80_low_m"))
        high = _float(row.get("interval80_high_m"))
        if low > 0 and high > 0:
            inside_80.append(1 if low <= actual <= high else 0)
    if not errors:
        return {
            "n": 0,
            "mae_m": 0.0,
            "mape": 0.0,
            "bias_m": 0.0,
            "interval_80_coverage": None,
        }
    return {
        "n": len(errors),
        "mae_m": round(sum(abs(err) for err in errors) / len(errors), 3),
        "mape": round(sum(ape) / len(ape), 4),
        "bias_m": round(sum(errors) / len(errors), 3),
        "interval_80_coverage": (
            round(sum(inside_80) / len(inside_80), 4) if inside_80 else None
        ),
    }


def weekend_forecast_cuts(weekend_of: str) -> list[dict]:
    """Forecast-cut timestamps for one opening weekend.

    ``weekend_of`` is the Friday anchor. Thursday is one day earlier.
    """
    try:
        friday = datetime.strptime(weekend_of, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return []
    cuts = []
    for name, offset, clock in FORECAST_CUTS:
        hour, minute = [int(part) for part in clock.split(":", 1)]
        ts = friday + timedelta(days=offset)
        ts = ts.replace(hour=hour, minute=minute)
        cuts.append({"cut": name, "as_of": ts.isoformat()})
    return cuts
