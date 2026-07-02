#!/usr/bin/env python3
"""Gate: should empirical residual examples be RECENCY-weighted?

The day-read scale audit (analyze_dayread_scale.py) showed the model's day reads
were ~0.53-0.70x actual in the April/early-May era (immature calibration) but
~0.96x by June — the global bias got fixed by ongoing recalibration. The
empirical residual layer, however, trains on ALL history equally, so those stale
under-read examples still teach big upward corrections that now DOUBLE-correct
recent films (Jackass snapshot days got x1.14-1.20 -> +37% miss).

Fix candidate: multiply each example's weight by 0.5**(age_weeks/half_life),
age = current weekend - example weekend. Tested via the canonical Thursday-only
replay (leak-free freezes), scored on ALL films and on the RECENT half (June+).
Monkeypatch only — predict.py untouched. Ships only on a clear win.
"""
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

_orig_weight = P._empirical_example_weight
_CURRENT_WEEKEND = {"w": None}


def _make_weight(half_life_weeks):
    def weight(current, example):
        w = _orig_weight(current, example)
        if w <= 0 or half_life_weeks is None:
            return w
        cur = _CURRENT_WEEKEND["w"]
        ex = example.get("weekend_of") or ""
        if not cur or not ex:
            return w
        try:
            age_days = (datetime.strptime(cur, "%Y-%m-%d") - datetime.strptime(ex, "%Y-%m-%d")).days
        except ValueError:
            return w
        if age_days <= 0:
            return w
        return w * (0.5 ** (age_days / 7.0 / half_life_weeks))
    return weight


def replay_all(hist, md):
    out = []
    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        thu = (datetime.strptime(w, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        _CURRENT_WEEKEND["w"] = w
        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)
        except Exception:
            continue
        sd = P.movie_mapping_get(P.filter_seat_data_through(P.load_seat_data(weekend_of=w), thu), movie, None)
        if not sd:
            continue
        try:
            pred = P.predict_movie(
                movie, sd, [], cal,
                national_theatre_count=P.national_theatre_count_for_movie(
                    movie, P.load_theatre_counts(), metadata=md),
                snapshot_data=P.movie_mapping_get(
                    P.load_pre_reservation_data(weekend_of=w, through_date=thu), movie, {}),
            )
        except Exception:
            continue
        if not pred:
            continue
        mid = pred.get("regression_mid_m") or pred.get("snapshot_mid_m") or pred.get("seat_mid_m")
        if mid:
            out.append((movie, w, mid, actual))
    return out


def mae(rows):
    es = sorted(abs(p - a) / a * 100 for _, _, p, a in rows if a)
    n = len(es)
    return (sum(es) / n, es[n // 2] if n % 2 else (es[n // 2 - 1] + es[n // 2]) / 2) if es else (0, 0)


def main():
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    md = P.load_movie_metadata()
    for label, hl in (("baseline (no decay)", None), ("half-life 8w", 8.0),
                      ("half-life 6w", 6.0), ("half-life 4w", 4.0)):
        P._empirical_example_weight = _make_weight(hl)
        rows = replay_all(hist, md)
        recent = [r for r in rows if r[1] >= "2026-06-01"]
        am, amd = mae(rows)
        rm, rmd = mae(recent)
        print(f"{label:20}: ALL n={len(rows)} MAE {am:5.1f}% (med {amd:.1f}%)   "
              f"JUNE+ n={len(recent)} MAE {rm:5.1f}% (med {rmd:.1f}%)")
        if hl is None:
            for m, w, p, a in rows:
                print(f"    {m[:26]:26} {w} pred {p:6.1f} actual {a:6.1f}  {(p-a)/a*100:+.0f}%")
    P._empirical_example_weight = _orig_weight


if __name__ == "__main__":
    main()
