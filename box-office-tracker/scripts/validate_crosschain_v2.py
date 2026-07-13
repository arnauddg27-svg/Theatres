#!/usr/bin/env python3
"""Design validation for cross-chain share v2.

Changes under test, against every film with cross-chain data + an actual:
  A. wA pinned to a fixed AMC capacity constant (0.24) instead of the drifting
     calibrated fleet share (formula output must not move when the fleet prior
     drifts 0.244 -> 0.196).
  B. Near-showtime RC occupancy: use rows with lead <= 360 min when >= 30 exist
     (like-for-like vs AMC's post-show reads; long-lead rows read ~0 and
     confound family films).
  C. Weight/clamp grid: w in {0.5 (current), 0.75, 0.9, 1.0}; absolute share
     clamp [0.10, 0.40].

Scores: what the recorded prediction WOULD have been (pred scales ~1/share) vs
the actual. Read-only.
"""
import csv
import gzip
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

K = 1.15
CAP_SHARE = 0.24

# film -> (weekend, share_used_at_record, recorded_pred, actual, cc_applied_at_record)
FILMS = {
    "Supergirl":              ("2026-06-26", 0.244, 39.54, 37.1, False),
    "Jackass: Best and Last": ("2026-06-26", 0.244, 11.55, 8.46, False),
    "Young Washington":       ("2026-07-03", 0.262, 8.3, 19.37, True),   # cc fired pre-gate
    "Evil Dead Burn":         ("2026-07-10", None, 24.7, 13.7, None),    # resolve below
    "Minions & Monsters":     ("2026-07-03", 0.209, 33.2, 47.2, False),  # family-gated
}


def num(x):
    try:
        return float(str(x).replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def seat_rows(w):
    p = f"data/seat-archive/seat-counts-{w}.csv.gz"
    if os.path.exists(p):
        with gzip.open(p, "rt") as f:
            return list(csv.DictReader(f))
    return [r for r in csv.DictReader(open("data/seat-counts.csv"))
            if r.get("weekend_of") == w]


def occupancies(movie, w):
    A = [num(r["occupancy_pct"]) for r in seat_rows(w)
         if r["movie_title"] == movie and num(r["occupancy_pct"]) is not None]
    fan = [r for r in csv.DictReader(open("data/fandango-pre-reservation-snapshots.csv"))
           if r.get("weekend_of") == w and r["movie_title"] == movie]
    rc_all = [num(r["occupancy_pct"]) for r in fan if num(r["occupancy_pct"]) is not None]
    rc_near = [num(r["occupancy_pct"]) for r in fan
               if num(r["occupancy_pct"]) is not None
               and (num(r.get("minutes_until_showtime")) or 1e9) <= 360]
    return (sum(A) / len(A) if A else None,
            sum(rc_all) / len(rc_all) if rc_all else None,
            (sum(rc_near) / len(rc_near), len(rc_near)) if rc_near else (None, 0))


def formula(a, rc, wa=CAP_SHARE, k=K):
    x = wa * a
    y = (1 - wa) * k * rc
    return x / (x + y)


def main():
    # resolve EDB's share_used (did the supply gate block cc at record time?)
    edb_spc = None
    sd = P.movie_mapping_get(P.load_seat_data(weekend_of="2026-07-10"), "Evil Dead Burn", None)
    if sd:
        edb_spc = P._seat_showings_per_cinema_day(sd)
    print(f"EDB showings/cinema-day = {edb_spc:.2f} -> supply gate "
          f"{'BLOCKED cc (share=fleet 0.1955)' if edb_spc and edb_spc < 4.5 else 'passed (cc fired ~0.24)'}")
    FILMS["Evil Dead Burn"] = ("2026-07-10",
                               0.1955 if (edb_spc and edb_spc < 4.5) else 0.246,
                               24.7, 13.7, not (edb_spc and edb_spc < 4.5))

    print(f"\n{'film':24}{'AMCocc':>7}{'RCall':>7}{'RCnear':>8}{'n':>4}"
          f"{'trueShare':>10}{'f(all)':>8}{'f(near)':>8}")
    rows = []
    for movie, (w, share_used, pred, actual, _cc) in FILMS.items():
        a, rc_all, (rc_near, n_near) = occupancies(movie, w)
        if a is None or rc_all is None:
            print(f"{movie[:24]:24} missing")
            continue
        true_share = share_used * pred / actual
        f_all = formula(a, rc_all)
        f_near = formula(a, rc_near) if rc_near and n_near >= 30 else None
        rows.append((movie, share_used, pred, actual, true_share, f_all, f_near))
        print(f"{movie[:24]:24}{a:>6.1f}%{rc_all:>6.1f}%"
              f"{(f'{rc_near:.1f}%' if rc_near else '-'):>8}{n_near:>4}"
              f"{true_share:>10.3f}{f_all:>8.3f}"
              f"{(f'{f_near:.3f}' if f_near else '-'):>8}")

    print(f"\n{'film':24}", end="")
    weights = (0.5, 0.75, 0.9, 1.0)
    for wt in weights:
        print(f"{'err w=' + str(wt):>12}", end="")
    print(f"{'(recorded)':>12}")
    for movie, share_used, pred, actual, true_share, f_all, f_near in rows:
        f_use = f_near if f_near else f_all
        base_pred = pred * (share_used / share_used)  # recorded pred at share_used
        print(f"{movie[:24]:24}", end="")
        for wt in weights:
            s = share_used + wt * (f_use - share_used)
            s = max(0.10, min(0.40, s))
            new_pred = pred * share_used / s
            print(f"{(new_pred - actual) / actual * 100:>+11.0f}%", end="")
        print(f"{(pred - actual) / actual * 100:>+11.0f}%")


if __name__ == "__main__":
    main()
