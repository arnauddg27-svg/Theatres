#!/usr/bin/env python3
"""Isolate how much each 2026-07 change contributed to the Minions over-read.

Actual Minions 3-day (Fri-Sun) = $36.4M. The model predicts Thu+Fri+Sat+Sun, so
compare the model's Fri+Sat+Sun against $36.4M. Toggle each change off:
  * Thursday reported-actual anchor (daily_actual_overrides)  -> x1.98 seat scale
  * family walk-up boost (FAMILY_WALKUP_SNAPSHOT_BOOST)
  * Friday anchor blend (friday_anchored_weekend_m)
Read-only (monkeypatch; does not edit predict.py).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

W = "2026-07-03"
MOVIE = "Minions & Monsters"
ACTUAL_3DAY = 36.4


def run(thursday_anchor, family_boost, friday_anchor):
    orig_boost = getattr(P, "FAMILY_WALKUP_SNAPSHOT_BOOST", 1.0)  # reverted 2026-07-06; guarded
    orig_fa = P.friday_anchored_weekend_m
    if hasattr(P, "FAMILY_WALKUP_SNAPSHOT_BOOST"):
        P.FAMILY_WALKUP_SNAPSHOT_BOOST = orig_boost if family_boost else 1.0
    if not friday_anchor:
        P.friday_anchored_weekend_m = lambda pred: None
    try:
        cal = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))
        md = P.load_movie_metadata()
        sd = P.movie_mapping_get(P.load_seat_data(weekend_of=W), MOVIE, None)
        snap = P.movie_mapping_get(P.load_pre_reservation_data(weekend_of=W), MOVIE, {})
        dao = P.load_daily_actual_overrides(weekend_of=W) if thursday_anchor else {}
        pred = P.predict_movie(
            MOVIE, sd, [], cal,
            national_theatre_count=P.national_theatre_count_for_movie(MOVIE, P.load_theatre_counts(), metadata=md),
            snapshot_data=snap, daily_actual_overrides=dao)
    finally:
        if hasattr(P, "FAMILY_WALKUP_SNAPSHOT_BOOST"):
            P.FAMILY_WALKUP_SNAPSHOT_BOOST = orig_boost
        P.friday_anchored_weekend_m = orig_fa
    if not pred:
        return None
    dd = pred.get("daily_details") or {}
    fri_sun = sum((dd.get(d, {}).get("domestic_mid") or 0) for d in ("Friday", "Saturday", "Sunday")) / 1e6
    return pred.get("regression_mid_m"), fri_sun


configs = [
    ("ALL ON (shipped)",            True,  True,  True),
    ("- family boost",              True,  False, True),
    ("- Friday anchor",             True,  True,  False),
    ("- Thursday anchor",           False, True,  True),
    ("- family & Friday",           True,  False, False),
    ("- ALL THREE",                 False, False, False),
]
print(f"actual 3-day (Fri-Sun) = ${ACTUAL_3DAY}M\n")
print(f"{'config':22}{'headline':>10}{'Fri-Sun':>9}{'vs actual':>11}")
for name, ta, fb, fa in configs:
    r = run(ta, fb, fa)
    if not r:
        print(f"{name:22} (no pred)")
        continue
    head, fs = r
    err = (fs - ACTUAL_3DAY) / ACTUAL_3DAY * 100
    print(f"{name:22}{head:>9.1f}{fs:>9.1f}{err:>+10.0f}%")
