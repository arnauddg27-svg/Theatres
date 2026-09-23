#!/usr/bin/env python3
"""Chronological calibration-layer evaluation using stored raw seat features.

Refit on earlier, already-recorded weekends only. Hold out all films opening
the same weekend together. This evaluates calibration, NOT archived live
headlines: raw features may have been reconstructed after the opening. It
does not validate the presale, Friday-anchor or review adjustments.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_regression as sr
from actuals_quality import actuals_as_of


def valid_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def earlier_history(history, weekend):
    """Require release AND actual-recording dates before the test weekend."""
    cutoff = valid_date(weekend)
    return [actuals_as_of(e, weekend) for e in history if cutoff and valid_date(e.get("weekend_of"))
            and valid_date(e.get("date"))
            and valid_date(e["weekend_of"]) < cutoff
            and valid_date(e["date"]) < cutoff]


def summarize(rows):
    scored = [r for r in rows if r.get("predicted_m") is not None]
    if not scored:
        return {"n": 0, "mape_pct": None, "interval_coverage_pct": None}
    errors = [(r["predicted_m"] - r["actual_m"]) / r["actual_m"] for r in scored]
    return {
        "n": len(scored),
        "mape_pct": round(statistics.mean(abs(e) for e in errors) * 100, 2),
        "median_ape_pct": round(statistics.median(abs(e) for e in errors) * 100, 2),
        "bias_pct": round(statistics.mean(errors) * 100, 2),
        "mae_m": round(statistics.mean(abs(r["predicted_m"] - r["actual_m"]) for r in scored), 3),
        "interval_coverage_pct": round(100 * statistics.mean(
            r["low_m"] <= r["actual_m"] <= r["high_m"] for r in scored), 2),
        "mean_relative_width_pct": round(100 * statistics.mean(
            (r["high_m"] - r["low_m"]) / r["predicted_m"] for r in scored), 2),
    }


def evaluate(history, min_training_movies=8):
    rows = []
    for weekend in sorted({e.get("weekend_of") for e in history
                           if valid_date(e.get("weekend_of"))}):
        train = earlier_history(history, weekend)
        n_train = len(set(sr.weekend_cv_movies(sr.fitting_history(train))))
        block = sr.fit_regression_calibration(train) if n_train >= min_training_movies else None
        for e in (e for e in history if e.get("weekend_of") == weekend):
            actual = sr._f(e.get("actual_total"))
            row = {"movie": e.get("movie"), "weekend_of": weekend,
                   "actual_m": actual, "training_movies": n_train,
                   "data_outage": sr.is_data_outage_entry(e)}
            if not actual or actual <= 0:
                row["status"] = "invalid actual"
            elif block is None:
                row["status"] = "insufficient earlier training history"
            else:
                pred = sr.predict_weekend(
                    block, e.get("raw_daily_predictions") or e.get("daily_predictions") or {},
                    e.get("daily_coverage_ratios") or {}, {}, {},
                    daily_sellout=e.get("daily_sellout_fractions") or {})
                if pred["mid_m"] > 0:
                    row.update(predicted_m=pred["mid_m"], low_m=pred["low_m"],
                               high_m=pred["high_m"], tier=pred["tier"], status="scored")
                else:
                    row["status"] = "no admissible seat days"
            rows.append(row)
    return {
        "scope": "Chronological calibration-layer replay of stored raw features; not live forecast accuracy.",
        "min_training_movies": min_training_movies,
        "all_scored": summarize(rows),
        "non_outage": summarize([r for r in rows if not r["data_outage"]]),
        "unscored": sum(r["status"] != "scored" for r in rows),
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", type=Path, default=Path(__file__).resolve().parents[1] / "data/calibration.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(json.loads(args.calibration.read_text())["history"])
    print(report["scope"])
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
