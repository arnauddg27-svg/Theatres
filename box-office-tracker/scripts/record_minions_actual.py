#!/usr/bin/env python3
"""Record Minions & Monsters actual (the-numbers.com daily grosses).

Honest: predicts with daily_actual_overrides={} (no outcome leakage), records the
REAL daily split directly, and flags it out of the day-weight fit (July-4th Sat
crater would corrupt the normal Thu/Fri/Sat/Sun shape). Thu-Sun span to match the
model's prediction convention.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402
import calibrate as C  # noqa: E402

W = "2026-07-03"
MOVIE = "Minions & Monsters"
# the-numbers.com reported daily grosses ($M)
DAILY_ACTUALS = {"Thursday": 10.81, "Friday": 16.51, "Saturday": 9.47, "Sunday": 10.42}
CAL_PATH = os.path.join(P.DATA_DIR, "calibration.json")

cal = json.load(open(CAL_PATH))
dw_before = dict(cal["calibration_factors"]["day_weights"])
share_before = cal["calibration_factors"]["amc_market_share"]

sd = P.movie_mapping_get(P.load_seat_data(weekend_of=W), MOVIE, None)
if not sd:
    sys.exit("no Minions seat data")
pred = P.predict_movie(
    MOVIE, sd, [], cal,
    national_theatre_count=P.national_theatre_count_for_movie(
        MOVIE, P.load_theatre_counts(), metadata=P.load_movie_metadata()),
    snapshot_data=P.movie_mapping_get(P.load_pre_reservation_data(weekend_of=W), MOVIE, {}),
    daily_actual_overrides={},   # no leakage
    cross_chain_data=P.load_cross_chain_occupancy(weekend_of=W))

pmid, plow, phigh = P.regression_prediction_values(pred)
dp, rdp, dtc, dcr = P.daily_calibration_fields_from_prediction(pred)
sdp, sdcr, sdlb = P.snapshot_calibration_fields_from_prediction(pred)

C.record_result(
    cal, MOVIE, W, pmid, plow, phigh, DAILY_ACTUALS, dp,
    pred["n_theatres_total"], len(pred["daily_estimates"]),
    daily_theatre_counts=dtc, daily_coverage_ratios=dcr, raw_daily_predictions=rdp,
    snapshot_daily_predictions=sdp, snapshot_daily_coverage_ratios=sdcr,
    snapshot_daily_lead_buckets=sdlb,
    reference_amc_theatres=pred.get("reference_amc_theatres"),
    model_cohort_key=pred.get("model_cohort_key"),
    social_signal=pred.get("social_signal"),
    actual_source="the-numbers.com",
    exclude_from_day_weights=True)

for e in cal["history"]:
    if e["movie"] == MOVIE and e["weekend_of"] == W:
        e["notes"] = ("Wed 2026-07-01 opener into July-4th weekend; reported 3-day "
                      "(Fri-Sun) $36.4M, 5-day $61.4M; recorded Thu-Sun to match model "
                      "span. July-4th Sat crater ($9.47M, -43%) -> excluded from "
                      "day-weight fit. Live pre-revert model over-read ~$62M (Thursday "
                      "anchor over-scale); reverted commit 89ed09b.")
        break

json.dump(cal, open(CAL_PATH, "w"), indent=2)
dw_after = cal["calibration_factors"]["day_weights"]
actual = sum(DAILY_ACTUALS.values())
print(f"recorded Minions: predicted ${pmid:.1f}M vs actual (Thu-Sun) ${actual:.2f}M "
      f"= {(pmid-actual)/actual*100:+.0f}%")
print(f"day_weights BEFORE: {dw_before}")
print(f"day_weights AFTER : {dw_after}   ({'UNCHANGED' if dw_before==dw_after else 'CHANGED!'})")
print(f"amc_market_share: {share_before:.4f} -> {cal['calibration_factors']['amc_market_share']:.4f}")
print(f"history now: {len(cal['history'])} films")
