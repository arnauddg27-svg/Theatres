#!/usr/bin/env python3
"""Build time-cutoff-controlled stage replays for model development.

Historical capture timestamps are enforced, actual labels are held out by
opening weekend, and date-only side inputs must predate the checkpoint day.
Metadata and historical ticket prices are current corrected reference data;
these are reconstructed forecasts, not immutable live predictions.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, time, timedelta, timezone
import json
from pathlib import Path
import random
import statistics
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import predict as P
from forecast_evaluation import utc_timestamp
from calibration_backtest import earlier_history

ET = ZoneInfo("America/New_York")
CHECKPOINTS = {"thursday_noon": -1, "friday_noon": 0,
               "saturday_noon": 1, "sunday_noon": 2}


def filter_captured(data, cutoff, field):
    result = {}
    for movie, dates in data.items():
        for day, rows in dates.items():
            usable = [r for r in rows if (stamp := utc_timestamp(r.get(field))) and stamp <= cutoff]
            if usable:
                result.setdefault(movie, {})[day] = usable
    return result


def checkpoint_time(weekend, offset):
    friday = datetime.strptime(weekend, "%Y-%m-%d").date()
    return datetime.combine(friday + timedelta(days=offset), time(12), tzinfo=ET).astimezone(timezone.utc)


def build(output):
    history = json.loads((Path(P.DATA_DIR) / "calibration.json").read_text())["history"]
    metadata = P.load_movie_metadata()
    counts = P.load_theatre_counts()
    result = []
    for weekend in sorted({h["weekend_of"] for h in history}):
        films = [h for h in history if h["weekend_of"] == weekend]
        try:
            frozen = P.load_calibration_freeze(P.DATA_DIR, weekend)
        except FileNotFoundError:
            frozen = {"history": [], "calibration_factors": {}}
        # Today's clean calibration implementation, fitted to strictly earlier
        # labels. A historical freeze supplies reference settings, not outcomes.
        frozen["history"] = earlier_history(history, (datetime.fromisoformat(weekend) - timedelta(days=1)).date().isoformat())
        cal = P.sanitize_calibration(frozen, P.DAY_WEIGHTS_DEFAULT, P.DEFAULT_AMC_MARKET_SHARE)
        seats = P.load_seat_data(weekend_of=weekend)
        snapshots = P.load_pre_reservation_data(weekend_of=weekend)
        for name, offset in CHECKPOINTS.items():
            cutoff = checkpoint_time(weekend, offset)
            prior_day = (cutoff.astimezone(ET).date() - timedelta(days=1)).isoformat()
            seat_now = filter_captured(seats, cutoff, "check_time")
            snap_now = filter_captured(snapshots, cutoff, "snapshot_time")
            overrides = P.load_daily_actual_overrides(weekend, through_date=prior_day)
            # Unknown publication dates cannot establish availability.
            overrides = {m: {d: v for d, v in days.items() if v.get("as_of_date")}
                         for m, days in overrides.items()}
            for h in films:
                movie = h["movie"]
                sd = P.movie_mapping_get(seat_now, movie, {})
                sn = P.movie_mapping_get(snap_now, movie, {})
                row = {"movie": movie, "weekend_of": weekend, "actual_m": h["actual_total"],
                       "actual_recorded": h.get("date"), "checkpoint": name,
                       "cutoff": cutoff.isoformat(), "data_outage": bool(h.get("data_outage")),
                       "training_movies": len(cal["history"])}
                try:
                    pred = P.predict_movie(
                        movie, sd, [], copy.deepcopy(cal),
                        national_theatre_count=P.national_theatre_count_for_movie(movie, counts, metadata=metadata),
                        snapshot_data=sn, social_data={}, daily_actual_overrides=overrides,
                        showtime_link_profiles={}, reviews_data={}, cross_chain_data={},
                        apply_stage_model=False) if sd else None
                    if pred:
                        row["pred"] = pred
                        row["baseline_m"] = pred.get("regression_mid_m")
                    row["status"] = "ok" if pred else "no regular seats at cutoff"
                except Exception as exc:
                    row["status"] = f"error: {type(exc).__name__}: {exc}"
                result.append(row)
                print(weekend, name, movie, row.get("baseline_m"), row["status"], flush=True)
        output.write_text(json.dumps({"schema": 1, "scope": __doc__, "rows": result}, default=str) + "\n")
    return result


def summarize(rows):
    if not rows:
        return {"forecasts": 0}
    out = {"forecasts": len(rows), "films": len({r["movie"] for r in rows}),
           "weekends": len({r["weekend_of"] for r in rows})}
    for name, key in (("baseline", "baseline_m"), ("updated", "updated_m")):
        errors = [abs(r[key] / r["actual_m"] - 1) * 100 for r in rows]
        by_movie = {}
        for r, error in zip(rows, errors):
            by_movie.setdefault(r["movie"], []).append(error)
        out[name] = {"mape_pct": round(statistics.mean(errors), 2),
                     "median_ape_pct": round(statistics.median(errors), 2),
                     "film_balanced_mape_pct": round(statistics.mean(
                         statistics.mean(values) for values in by_movie.values()), 2)}
    # Resample whole films, not correlated checkpoints from the same release.
    improvements = {}
    for r in rows:
        improvements.setdefault(r["movie"], []).append(
            100 * (abs(r["baseline_m"] / r["actual_m"] - 1)
                   - abs(r["updated_m"] / r["actual_m"] - 1)))
    values = [statistics.mean(v) for v in improvements.values()]
    rng = random.Random(20260919)
    bootstrap = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(2000))
    out["film_bootstrap_improvement_pp_95pct"] = [round(bootstrap[49], 2), round(bootstrap[1949], 2)]
    return out


def evaluate(cache, split="2026-08-01"):
    rows = json.loads(cache.read_text())["rows"]
    scored = []
    for row in rows:
        if not row.get("baseline_m") or row["baseline_m"] <= 0:
            continue
        pred = copy.deepcopy(row["pred"])
        # Re-run the exact production headline selection on identical inputs.
        P.select_regression_prediction(pred)
        scored.append({k: row.get(k) for k in
                       ("movie", "weekend_of", "checkpoint", "baseline_m", "actual_m",
                        "training_movies", "data_outage")} | {
                            "updated_m": pred["regression_mid_m"],
                            "applied": pred["stage_daily_evidence_applied"]})
    eligible = [r for r in scored if r["training_movies"] >= 8 and not r["data_outage"]]
    heldout = [r for r in eligible if r["weekend_of"] >= split]
    return {"scope": __doc__, "development_before": split,
            "all_available_including_outages": summarize(scored),
            "development": summarize([r for r in eligible if r["weekend_of"] < split]),
            "later_weekends": summarize(heldout),
            "later_weekends_by_checkpoint": {name: summarize([r for r in heldout if r["checkpoint"] == name])
                                             for name in CHECKPOINTS},
            "missing_baseline": len(rows) - len(scored), "rows": scored}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evaluate", type=Path, help="Evaluate an existing baseline replay cache without rereading captures")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.evaluate:
        report = evaluate(args.evaluate)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))
    else:
        build(args.output)


if __name__ == "__main__":
    main()
