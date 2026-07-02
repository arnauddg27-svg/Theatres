#!/usr/bin/env python3
"""Gate: should the Friday-anchor blend weight DECAY as weekend days are observed?

The anchor exists to estimate the UNOBSERVED back half of the weekend from the
observed front half. Once Saturday/Sunday are real seat days, extrapolating them
from Friday is architecturally wrong (Jackass: as-of-Sunday every day was
observed, sum $11.0M, yet the anchor still blended a $12.1M extrapolation at full
weight → headline 11.6 vs actual 8.46).

Policy A (current): w = 0.5 whenever Thu+Fri observed.
Policy B (decay):   w = 0.5 x (day-weight share of Sat+Sun still MISSING)
                    -> as-of-Fri: w=0.5; as-of-Sat: ~0.22; as-of-Sun: 0.

Replays every history film at as-of-Fri / as-of-Sat / as-of-Sun (leak-free
freezes) and compares weekend MAE under both policies. Read-only.
"""
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def replay(movie, w, thru, cal, nat):
    sd = P.movie_mapping_get(P.filter_seat_data_through(P.load_seat_data(weekend_of=w), thru), movie, None)
    if not sd:
        return None
    snap = P.movie_mapping_get(P.load_pre_reservation_data(weekend_of=w, through_date=thru), movie, {})
    try:
        return P.predict_movie(movie, sd, [], cal, national_theatre_count=nat, snapshot_data=snap)
    except Exception:
        return None


def main():
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    load_md = getattr(P, "load_movie_metadata", None)
    md = load_md() if load_md else None
    day_w = P.DAY_WEIGHTS_DEFAULT
    sat_sun_w = day_w.get("Saturday", 0) + day_w.get("Sunday", 0)

    offsets = {"as-of-Fri": 0, "as-of-Sat": 1, "as-of-Sun": 2}
    FLOORS = (0.0, 0.2, 0.3, 0.4)   # 0.0 = pure decay; others = decay with floor
    results = {k: {"fixed": [], **{f"floor{fl:g}": [] for fl in FLOORS}} for k in offsets}

    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)
        except Exception:
            continue
        nat = P.national_theatre_count_for_movie(movie, P.load_theatre_counts(), metadata=md)
        fri = datetime.strptime(w, "%Y-%m-%d")
        for label, off in offsets.items():
            thru = (fri + timedelta(days=off)).strftime("%Y-%m-%d")
            pred = replay(movie, w, thru, cal, nat)
            if not pred:
                continue
            fa = pred.get("friday_anchored_mid_m")
            headline = _f(pred.get("regression_mid_m"))
            if headline is None:
                continue
            if fa is None:
                # anchor never fired: all policies identical
                for k in results[label]:
                    results[label][k].append((movie, headline, actual))
                continue
            # reconstruct the pre-anchor mid: headline = (1-w0)*base + w0*fa, w0=0.5
            w0 = P.FRIDAY_ANCHOR_BLEND_WEIGHT
            # strip the review factor to isolate the blend, then re-apply
            rf = pred.get("review_weekend_factor", 1.0) or 1.0
            headline_nr = headline / rf
            base = (headline_nr - w0 * fa) / (1.0 - w0)
            # decayed weight: scale by the share of Sat+Sun still missing
            dd = pred.get("daily_details") or {}
            missing = sum(day_w.get(d, 0) for d in ("Saturday", "Sunday") if d not in dd)
            frac = missing / sat_sun_w if sat_sun_w else 0.0
            results[label]["fixed"].append((movie, headline, actual))
            for fl in FLOORS:
                w_dec = max(fl, w0 * frac)
                dec = ((1.0 - w_dec) * base + w_dec * fa) * rf
                results[label][f"floor{fl:g}"].append((movie, dec, actual))

    def mae(pairs):
        es = sorted(abs(p - a) / a * 100 for _, p, a in pairs if a)
        n = len(es)
        return (sum(es) / n, es[n // 2] if n % 2 else (es[n // 2 - 1] + es[n // 2]) / 2) if es else (0, 0)

    for label in offsets:
        fm, fmd = mae(results[label]["fixed"])
        line = f"{label} (n={len(results[label]['fixed'])}):  fixed {fm:5.1f}%"
        for fl in FLOORS:
            dm, _dmd = mae(results[label][f"floor{fl:g}"])
            line += f"   floor{fl:g} {dm:5.1f}% [{fm - dm:+.1f}]"
        print(line)
    # combined across horizons (what actually ships is one policy for all)
    print("\ncombined all-horizons MAE:")
    allfix = [p for label in offsets for p in results[label]["fixed"]]
    fm, _ = mae(allfix)
    print(f"  fixed   : {fm:5.1f}%")
    for fl in FLOORS:
        alld = [p for label in offsets for p in results[label][f"floor{fl:g}"]]
        dm, _ = mae(alld)
        print(f"  floor{fl:g} : {dm:5.1f}%  [{fm - dm:+.1f} pts]")


if __name__ == "__main__":
    main()
