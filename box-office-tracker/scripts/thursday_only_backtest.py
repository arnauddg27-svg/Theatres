#!/usr/bin/env python3
"""Thursday-only backtest: for each historical film, replay its forecast AS OF
its opening Thursday (only Thursday seat data + snapshots captured by Thursday,
using that weekend's frozen — leak-free — calibration) and compare the two
candidate headlines against the actual:

  * seat-only  = Thursday seat fill extrapolated to the weekend via the average
                 day-shape (pred['seat_mid_m']).
  * snapshot   = Thursday seat + Fri/Sat/Sun reservation snapshots, the daily
                 evidence (pred['snapshot_mid_m']).

Goal: learn WHEN the snapshot beats the seat-extrapolation (and by how much), so
the Thursday-only headline rule is data-driven instead of a blunt wholesale
switch. Read-only; does not touch production data.

Run:  python3 scripts/thursday_only_backtest.py
"""
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402


def thursday_of(weekend_of):
    return (datetime.strptime(weekend_of, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")


def ape(est, actual):
    """Absolute percentage error."""
    if est is None or not actual:
        return None
    return abs(est - actual) / actual * 100.0


def main():
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    load_md = getattr(P, "load_movie_metadata", None)

    rows = []
    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        thu = thursday_of(w)
        da = h.get("daily_actuals") or {}
        thu_actual = da.get("Thursday")
        # frontloading proxy: Thursday's share of the actual weekend (higher = more frontloaded)
        frontload = (thu_actual / actual) if (thu_actual and actual) else None

        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)   # leak-free: pre-actual freeze
        except Exception:
            rows.append((movie, w, actual, None, None, None, frontload, "no-freeze"))
            continue

        seat_data = P.filter_seat_data_through(P.load_seat_data(weekend_of=w), thu)
        sd = P.movie_mapping_get(seat_data, movie, None)
        if not sd:
            rows.append((movie, w, actual, None, None, None, frontload, "no-thu-seat"))
            continue

        snap = P.load_pre_reservation_data(weekend_of=w, through_date=thu)
        poly = P.load_polymarket_data(weekend_of=w, through_date=thu)
        social = P.load_social_signal_data(weekend_of=w, through_date=thu)
        dao = P.load_daily_actual_overrides(weekend_of=w, through_date=thu)
        slp = P.load_showtime_link_daypart_profiles(weekend_of=w)
        ccd = P.load_cross_chain_occupancy(weekend_of=w, through_date=thu)
        tc = P.load_theatre_counts()
        md = load_md() if load_md else None
        nat = P.national_theatre_count_for_movie(movie, tc, metadata=md)

        try:
            pred = P.predict_movie(
                movie, sd, P.movie_mapping_get(poly, movie, []), cal,
                national_theatre_count=nat,
                snapshot_data=P.movie_mapping_get(snap, movie, {}),
                social_data=social,
                daily_actual_overrides=dao,
                showtime_link_profiles=P.movie_mapping_get(slp, movie, {}),
                cross_chain_data=ccd,
            )
        except Exception as e:
            rows.append((movie, w, actual, None, None, None, frontload, f"err:{str(e)[:40]}"))
            continue
        if not pred:
            rows.append((movie, w, actual, None, None, None, frontload, "no-pred"))
            continue

        seat_est = pred.get("seat_mid_m")
        snap_est = pred.get("snapshot_mid_m")
        fires = P.complete_snapshot_covers_missing_days(pred)
        rows.append((movie, w, actual, seat_est, snap_est, fires, frontload, "ok"))

    # ── report ────────────────────────────────────────────────────────────
    print(f"{'movie':26} {'actual':>7} {'seat':>7} {'snap':>7} "
          f"{'seatAPE':>8} {'snapAPE':>8} {'gate':>5} {'frontld':>7} note")
    seat_apes, snap_apes, both = [], [], []
    for movie, w, actual, seat, snap, fires, frontload, note in rows:
        sape, npe = ape(seat, actual), ape(snap, actual)
        fl = f"{frontload:.0%}" if frontload is not None else "  ?"
        print(f"{movie[:26]:26} {actual:>7.1f} "
              f"{(f'{seat:.1f}' if seat is not None else '-'):>7} "
              f"{(f'{snap:.1f}' if snap is not None else '-'):>7} "
              f"{(f'{sape:.0f}%' if sape is not None else '-'):>8} "
              f"{(f'{npe:.0f}%' if npe is not None else '-'):>8} "
              f"{str(fires) if fires is not None else '-':>5} {fl:>7} {note}")
        if sape is not None and npe is not None:
            seat_apes.append(sape); snap_apes.append(npe)
            both.append((movie, actual, seat, snap, sape, npe, frontload))

    def mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")
    def median(xs):
        s = sorted(xs); n = len(s)
        return float("nan") if not n else (s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2)

    print(f"\n=== Thursday-only forecast accuracy (n={len(both)} films with both signals) ===")
    print(f"  seat-extrapolation : MAE {mean(seat_apes):.1f}%   median {median(seat_apes):.1f}%")
    print(f"  snapshot           : MAE {mean(snap_apes):.1f}%   median {median(snap_apes):.1f}%")
    snap_wins = sum(1 for _,_,_,_,s,n,_ in both if n < s)
    print(f"  snapshot beats seat: {snap_wins}/{len(both)} films")

    # does snapshot win more when the film is frontloaded?
    fl_both = [b for b in both if b[6] is not None]
    if fl_both:
        med_fl = median([b[6] for b in fl_both])
        hi = [b for b in fl_both if b[6] >= med_fl]   # more frontloaded
        lo = [b for b in fl_both if b[6] < med_fl]
        def grp(g):
            return (mean([b[4] for b in g]), mean([b[5] for b in g]))  # seat MAE, snap MAE
        if hi:
            s, n = grp(hi); print(f"  frontloaded (Thu≥{med_fl:.0%}): seat MAE {s:.0f}%  vs  snap MAE {n:.0f}%  (n={len(hi)})")
        if lo:
            s, n = grp(lo); print(f"  leggier     (Thu<{med_fl:.0%}): seat MAE {s:.0f}%  vs  snap MAE {n:.0f}%  (n={len(lo)})")


if __name__ == "__main__":
    main()
