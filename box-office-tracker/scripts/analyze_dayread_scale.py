#!/usr/bin/env python3
"""Measure the model's per-film DAY-READ scale bias against daily actuals.

For each history film, replay as-of-Sunday (all weekend days observed, leak-free
freeze) and compare each observed seat-day's domestic_mid against the recorded
daily actual. scale_f = sum(day reads)/sum(daily actuals) is the film's
end-to-end seat->dollar bias (share, ticket price, coverage — everything).

Question: does scale_f group by audience_type (AMC-demographic skew)? If the
between-group separation is real, a history-calibrated per-type correction is
the fix for both the chronic broad-film under-reads and the Jackass-style
over-reads. Read-only.
"""
import csv
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


def main():
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    md = P.load_movie_metadata()
    rows = []
    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        da = h.get("daily_actuals") or {}
        if not da:
            continue
        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)
        except Exception:
            continue
        thru = (datetime.strptime(w, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
        sd = P.movie_mapping_get(P.filter_seat_data_through(P.load_seat_data(weekend_of=w), thru), movie, None)
        if not sd:
            continue
        try:
            pred = P.predict_movie(
                movie, sd, [], cal,
                national_theatre_count=P.national_theatre_count_for_movie(
                    movie, P.load_theatre_counts(), metadata=md),
                snapshot_data=P.movie_mapping_get(
                    P.load_pre_reservation_data(weekend_of=w, through_date=thru), movie, {}),
            )
        except Exception:
            continue
        if not pred:
            continue
        dd = pred.get("daily_details") or {}
        read = act = 0.0
        nd = 0
        for day, det in dd.items():
            a = _f(da.get(day))
            r = _f(det.get("domestic_mid"))
            if a and a > 0 and r and r > 0:
                read += r / 1e6
                act += a
                nd += 1
        if nd < 2:
            continue
        meta = P.metadata_for_movie(movie, md)
        atype = getattr(meta, "audience_type", "") or ""
        rows.append((movie, w, nd, read, act, read / act, atype))

    rows.sort(key=lambda r: r[5])
    print(f"{'movie':28}{'wknd':>11}{'days':>5}{'read':>8}{'actual':>8}{'scale':>7}  audience")
    for m, w, nd, r, a, s, at in rows:
        print(f"{m[:28]:28}{w:>11}{nd:>5}{r:>8.1f}{a:>8.1f}{s:>7.2f}  {at}")
    scales = [r[5] for r in rows]
    print(f"\nn={len(rows)}  mean scale {sum(scales)/len(scales):.2f}  "
          f"(1.0 = unbiased; <1 under-read, >1 over-read)")
    by = {}
    for m, w, nd, r, a, s, at in rows:
        if at:
            by.setdefault(at, []).append(s)
    print("\nby audience_type (tagged films only):")
    for at, v in sorted(by.items(), key=lambda x: sum(x[1]) / len(x[1])):
        print(f"  {at:16} n={len(v)}  mean {sum(v)/len(v):.2f}  {['%.2f' % x for x in v]}")


if __name__ == "__main__":
    main()
