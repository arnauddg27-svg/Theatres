#!/usr/bin/env python3
"""Read-only regression audit and training-data export command.

Examples:
    python3 box-office-tracker/model_audit.py --as-of-grid
    python3 box-office-tracker/model_audit.py --replay-weekend 2026-05-15
    python3 box-office-tracker/model_audit.py --export-training-data
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import model_pipeline


DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_OUTPUT_DIR = DATA_DIR / "model-audits"


def _float(value, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def _day_weights(calibration: dict) -> dict[str, float]:
    factors = calibration.get("calibration_factors", {}) or {}
    weights = factors.get("day_weights", {}) or {}
    clean = {
        day: _float(weights.get(day), 0.0)
        for day in model_pipeline.OPENING_WEEKEND_DAYS
    }
    total = sum(clean.values())
    if total <= 0:
        return {
            "Thursday": 0.12,
            "Friday": 0.32,
            "Saturday": 0.33,
            "Sunday": 0.23,
        }
    return {day: value / total for day, value in clean.items()}


def _included_days_for_cut(cut_name: str) -> list[str]:
    return {
        "thursday_morning": [],
        "thursday_night": ["Thursday"],
        "friday_morning": ["Thursday"],
        "saturday_morning": ["Thursday", "Friday"],
        "sunday_morning": ["Thursday", "Friday", "Saturday"],
        "final_pre_estimate": ["Thursday", "Friday", "Saturday", "Sunday"],
    }.get(cut_name, [])


def _prediction_from_daily(entry: dict, cut_name: str, weights: dict[str, float]) -> float:
    daily_predictions = (
        entry.get("raw_daily_predictions")
        or entry.get("daily_predictions", {})
        or {}
    )
    included = [
        day for day in _included_days_for_cut(cut_name)
        if _float(daily_predictions.get(day), 0.0) > 0
    ]
    if not included:
        if cut_name != "final_pre_estimate":
            return 0.0
        return _float(entry.get("predicted_mid"), 0.0)
    observed = sum(_float(daily_predictions.get(day), 0.0) for day in included)
    observed_share = sum(weights.get(day, 0.0) for day in included)
    if cut_name == "final_pre_estimate":
        return observed if observed > 0 else _float(entry.get("predicted_mid"), 0.0)
    if observed_share <= 0:
        return _float(entry.get("predicted_mid"), 0.0)
    return observed / observed_share


def _coverage_tier(value: float) -> str:
    if value >= 0.85:
        return "high"
    if value >= 0.60:
        return "medium"
    return "low"


def history_replay_rows(calibration: dict,
                        weekend_of: str | None = None) -> list[dict]:
    """Replay settled movies at standard forecast cuts.

    The row's interval is calibrated only from prior settled actuals. This is
    intentionally conservative and prevents the common audit mistake where a
    movie's own actual tightens its interval.
    """
    weights = _day_weights(calibration)
    history = sorted(
        calibration.get("history", []) or [],
        key=lambda row: (row.get("weekend_of", ""), row.get("movie", "")),
    )
    prior_errors: list[float] = []
    rows = []
    for entry in history:
        if weekend_of and entry.get("weekend_of") != weekend_of:
            continue
        actual = _float(entry.get("actual_total", entry.get("actual")), 0.0)
        if actual <= 0:
            continue
        coverage = _float(entry.get("coverage_ratio"), 0.0)
        missing_profile = {
            "missing_days": [
                day for day in model_pipeline.OPENING_WEEKEND_DAYS
                if _float((entry.get("daily_predictions") or {}).get(day), 0.0) <= 0
            ],
            "missing_timezone_days": [],
            "partial_daypart_days": entry.get("calibration_excluded_days", []) or [],
        }
        for cut_name, _, _ in model_pipeline.FORECAST_CUTS:
            predicted = _prediction_from_daily(entry, cut_name, weights)
            if predicted <= 0:
                continue
            intervals = model_pipeline.calibrated_intervals(
                predicted,
                residual_errors=prior_errors,
                coverage_ratio=coverage,
                missing_risk_count=len(model_pipeline.missing_data_risks(missing_profile)),
            )
            low80 = intervals["80"]["low_m"]
            high80 = intervals["80"]["high_m"]
            rows.append({
                "movie": entry.get("movie", ""),
                "weekend_of": entry.get("weekend_of", ""),
                "forecast_cut": cut_name,
                "predicted_m": round(predicted, 3),
                "actual_m": round(actual, 3),
                "error_m": round(predicted - actual, 3),
                "ape": round(abs(predicted - actual) / actual, 4),
                "bias_pct": round((predicted - actual) / actual, 4),
                "coverage_ratio": round(coverage, 4),
                "coverage_tier": _coverage_tier(coverage),
                "interval80_low_m": low80,
                "interval80_high_m": high80,
                "interval80_hit": int(low80 <= actual <= high80),
                "prior_actual_count": len(prior_errors),
                "calibration_source": "history",
                "excluded_day_count": len(entry.get("calibration_excluded_days", []) or []),
            })
        final_pred = _float(entry.get("predicted_mid"), 0.0)
        if final_pred <= 0:
            final_pred = _prediction_from_daily(entry, "final_pre_estimate", weights)
        if final_pred > 0:
            prior_errors.append((final_pred - actual) / actual)
    return rows


def summarize_replay(rows: list[dict]) -> dict:
    by_cut: dict[str, list[dict]] = defaultdict(list)
    by_coverage: dict[str, list[dict]] = defaultdict(list)
    by_movie: dict[str, list[dict]] = defaultdict(list)
    segments: dict[str, list[dict]] = defaultdict(list)
    excluded_reasons: dict[str, int] = defaultdict(int)
    warning_reasons: dict[str, int] = defaultdict(int)
    for row in rows:
        by_cut[row["forecast_cut"]].append(row)
        by_coverage[row["coverage_tier"]].append(row)
        by_movie[row["movie"]].append(row)
        actual = _float(row.get("actual_m"))
        coverage = _float(row.get("coverage_ratio"))
        if _float(row.get("headline_eligible"), 0.0) >= 1:
            segments["headline_clean"].append(row)
        else:
            for reason in str(row.get("quality_reasons") or "").split(";"):
                if reason:
                    excluded_reasons[reason] += 1
        for warning in str(row.get("quality_warnings") or "").split(";"):
            if warning:
                warning_reasons[warning] += 1
        if actual >= 10:
            segments["wide_or_material"].append(row)
        else:
            segments["low_gross"].append(row)
        if coverage >= 0.80:
            segments["high_coverage"].append(row)
        if actual >= 10 and coverage >= 0.60:
            segments["material_medium_plus_coverage"].append(row)
    return {
        "overall": model_pipeline.summarize_backtest_rows(rows),
        "by_forecast_cut": {
            key: model_pipeline.summarize_backtest_rows(value)
            for key, value in sorted(by_cut.items())
        },
        "by_coverage_tier": {
            key: model_pipeline.summarize_backtest_rows(value)
            for key, value in sorted(by_coverage.items())
        },
        "by_movie": {
            key: model_pipeline.summarize_backtest_rows(value)
            for key, value in sorted(by_movie.items())
        },
        "by_segment": {
            key: model_pipeline.summarize_backtest_rows(value)
            for key, value in sorted(segments.items())
        },
        "headline_clean": model_pipeline.summarize_backtest_rows(
            segments.get("headline_clean", [])
        ),
        "excluded_reasons": dict(sorted(excluded_reasons.items())),
        "warning_reasons": dict(sorted(warning_reasons.items())),
    }


def _filter_movie_date_rows_as_of(data: dict, field: str, as_of: datetime) -> dict:
    filtered = {}
    for movie, dates in (data or {}).items():
        kept_dates = {}
        for date_str, rows in (dates or {}).items():
            kept = model_pipeline.filter_rows_as_of(rows, field, as_of)
            if kept:
                kept_dates[date_str] = kept
        if kept_dates:
            filtered[movie] = kept_dates
    return filtered


def _safe_frozen_calibration(predict_module, weekend_of: str):
    try:
        return predict_module.load_frozen_calibration(weekend_of), "freeze"
    except Exception:
        return predict_module.load_calibration(), "live-fallback"


def current_model_replay_rows(calibration: dict,
                              weekend_of: str | None = None) -> list[dict]:
    """Replay current production predictor at standard as-of cuts.

    This path is intentionally read-only. It uses the frozen pre-actual
    calibration for each weekend when available, filters seat rows by
    ``check_time`` and snapshot rows by ``snapshot_time``, and records the model
    card interval produced at that timestamp.
    """
    import predict  # Imported lazily to keep model_pipeline independent.

    history = sorted(
        calibration.get("history", []) or [],
        key=lambda row: (row.get("weekend_of", ""), row.get("movie", "")),
    )
    theatre_counts = predict.load_theatre_counts()
    metadata = predict.load_movie_metadata()
    all_rows = []
    for entry in history:
        entry_weekend = entry.get("weekend_of", "")
        movie = entry.get("movie", "")
        actual = _float(entry.get("actual_total", entry.get("actual")), 0.0)
        if not entry_weekend or not movie or actual <= 0:
            continue
        if weekend_of and entry_weekend != weekend_of:
            continue

        try:
            cal, cal_source = _safe_frozen_calibration(predict, entry_weekend)
            seat_data_all = predict.load_seat_data(weekend_of=entry_weekend)
            snapshot_data_all = predict.load_pre_reservation_data(weekend_of=entry_weekend)
            showtime_link_profiles = predict.load_showtime_link_daypart_profiles(
                weekend_of=entry_weekend,
            )
        except Exception:
            continue

        for cut in model_pipeline.weekend_forecast_cuts(entry_weekend):
            cut_name = cut["cut"]
            as_of = model_pipeline.parse_datetime(cut["as_of"])
            if as_of is None:
                continue
            filtered_seats = _filter_movie_date_rows_as_of(
                seat_data_all,
                "check_time",
                as_of,
            )
            movie_seats = predict.movie_mapping_get(filtered_seats, movie, {})
            if not movie_seats:
                continue
            filtered_snapshots = _filter_movie_date_rows_as_of(
                snapshot_data_all,
                "snapshot_time",
                as_of,
            )
            through_date = as_of.date().isoformat()
            poly_data = predict.load_polymarket_data(
                weekend_of=entry_weekend,
                through_date=through_date,
            )
            daily_actual_overrides = predict.load_daily_actual_overrides(
                weekend_of=entry_weekend,
                through_date=through_date,
            )
            social_data = predict.load_social_signal_data(
                weekend_of=entry_weekend,
                through_date=through_date,
            )
            nat_count = predict.national_theatre_count_for_movie(
                movie,
                theatre_counts,
                metadata=metadata,
            )
            try:
                pred = predict.predict_movie(
                    movie,
                    movie_seats,
                    predict.movie_mapping_get(poly_data, movie, []),
                    cal,
                    national_theatre_count=nat_count,
                    snapshot_data=predict.movie_mapping_get(filtered_snapshots, movie, {}),
                    social_data=social_data,
                    daily_actual_overrides=daily_actual_overrides,
                    showtime_link_profiles=predict.movie_mapping_get(
                        showtime_link_profiles,
                        movie,
                        {},
                    ),
                )
            except Exception:
                continue
            if not pred:
                continue
            mid, _, _ = predict.regression_prediction_values(pred)
            card = pred.get("model_card") or {}
            interval80 = (card.get("intervals") or {}).get("80") or {}
            low80 = _float(interval80.get("low_m"))
            high80 = _float(interval80.get("high_m"))
            all_rows.append({
                "movie": movie,
                "weekend_of": entry_weekend,
                "forecast_cut": cut_name,
                "as_of": cut["as_of"],
                "replay_mode": "current_model",
                "calibration_source": cal_source,
                "predicted_m": round(mid, 3),
                "actual_m": round(actual, 3),
                "error_m": round(mid - actual, 3),
                "ape": round(abs(mid - actual) / actual, 4),
                "bias_pct": round((mid - actual) / actual, 4),
                "coverage_ratio": pred.get("seat_weighted_coverage_ratio") or pred.get("coverage_ratio"),
                "coverage_tier": card.get("coverage_grade") or _coverage_tier(_float(pred.get("coverage_ratio"))),
                "interval80_low_m": low80,
                "interval80_high_m": high80,
                "interval80_hit": int(low80 <= actual <= high80) if low80 and high80 else "",
                "model_source": pred.get("model_forecast_source") or pred.get("regression_source", ""),
                "snapshot_weight": pred.get("snapshot_model_weight", 0.0),
                "seat_days": pred.get("n_days", 0),
                "seat_theatres": pred.get("n_theatres_total", 0),
                "excluded_day_count": len(entry.get("calibration_excluded_days", []) or []),
            })
    return all_rows


def _write_rows(path: Path, rows: list[dict]) -> None:
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


def write_replay_outputs(rows: list[dict], summary: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows_path = output_dir / "as-of-grid.csv"
    summary_path = output_dir / "as-of-grid-summary.json"
    _write_rows(rows_path, rows)
    summary_path.write_text(json.dumps(summary, indent=2))
    return {
        "rows_path": str(rows_path),
        "summary_path": str(summary_path),
        "rows": len(rows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit box-office regression model data.")
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--as-of-grid", action="store_true")
    parser.add_argument("--replay-weekend")
    parser.add_argument("--export-training-data", action="store_true")
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(output_dir),
    }
    if args.export_training_data:
        results["training_tables"] = model_pipeline.export_training_tables(
            data_dir,
            output_dir,
        )
    if args.as_of_grid or args.replay_weekend:
        calibration = _load_json(data_dir / "calibration.json")
        rows = current_model_replay_rows(calibration, weekend_of=args.replay_weekend)
        if not rows:
            rows = history_replay_rows(calibration, weekend_of=args.replay_weekend)
        rows = model_pipeline.apply_precision_quality(rows)
        summary = summarize_replay(rows)
        results["replay"] = write_replay_outputs(rows, summary, output_dir)
        results["summary"] = summary
    if not (args.export_training_data or args.as_of_grid or args.replay_weekend):
        parser.print_help()
        return 2

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
