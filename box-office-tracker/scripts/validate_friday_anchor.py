#!/usr/bin/env python3
"""Gate for the post-Friday layer.

Once Friday is an observed (seat) day, is it better to estimate the weekend from
the OBSERVED front-half x a (front-load-aware) Friday->weekend multiplier than to
keep reading Saturday/Sunday from pre-weekend reservations (what the model does
now)? A soft Friday should drag Sat/Sun down; reservations don't know that.

Replays each history film AS-OF-SATURDAY (seat data filtered through the Friday =
weekend_of, leak-free frozen calibration), then compares three weekend estimates
against the actual:
  * snapshot     = the model's current headline (Thu+Fri seat + Sat/Sun reservations)
  * fri-anchor   = (observed Thu+Fri) x GLOBAL Friday->weekend multiplier
  * fri-anchor+A = (observed Thu+Fri) x audience-aware multiplier (front-loaded)

Read-only. Ships only if fri-anchor materially beats snapshot.
"""
import csv
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def friday_multipliers():
    """weekend / friday_m (friday already incl previews) from comps."""
    by, allv = defaultdict(list), []
    for r in csv.DictReader(open(os.path.join(P.DATA_DIR, "historical-comps.csv"))):
        fr, sa, su = _f(r.get("friday_m")), _f(r.get("saturday_m")), _f(r.get("sunday_m"))
        a = (r.get("audience_type") or "").strip()
        if fr and fr > 0 and sa and su:
            mult = (fr + sa + su) / fr
            allv.append(mult)
            if a:
                by[a].append(mult)
    glob = sum(allv) / len(allv)
    per = {a: (sum(v) / len(v), len(v)) for a, v in by.items()}
    return glob, per


def aud_mult(atype, glob, per, min_n=6, shrink=8.0):
    info = per.get((atype or "").strip())
    if not info:
        return glob
    m, n = info
    if n < min_n:
        return glob
    return glob + (n / (n + shrink)) * (m - glob)


def audience_lookup():
    look = {}
    for path in ("movie-metadata.csv", "historical-comps.csv"):
        try:
            for r in csv.DictReader(open(os.path.join(P.DATA_DIR, path))):
                m = (r.get("movie") or "").strip().lower()
                a = (r.get("audience_type") or "").strip()
                if m and a and m not in look:
                    look[m] = a
        except OSError:
            pass
    return look


def main():
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    glob, per = friday_multipliers()
    look = audience_lookup()
    load_md = getattr(P, "load_movie_metadata", None)
    print(f"global Friday->weekend multiplier: {glob:.2f}x")

    rows = []
    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)
        except Exception:
            continue
        # as-of-Saturday: keep Thursday + Friday seat rows (through the Friday = weekend_of)
        seat = P.filter_seat_data_through(P.load_seat_data(weekend_of=w), w)
        sd = P.movie_mapping_get(seat, movie, None)
        if not sd:
            continue
        try:
            pred = P.predict_movie(
                movie, sd, [], cal,
                national_theatre_count=P.national_theatre_count_for_movie(
                    movie, P.load_theatre_counts(), metadata=(load_md() if load_md else None)),
                snapshot_data=P.movie_mapping_get(
                    P.load_pre_reservation_data(weekend_of=w, through_date=w), movie, {}),
            )
        except Exception:
            continue
        if not pred:
            continue
        dd = pred.get("daily_details") or {}
        thu = _f((dd.get("Thursday") or {}).get("domestic_mid"))
        fri = _f((dd.get("Friday") or {}).get("domestic_mid"))
        if not (thu and fri):       # Friday must be observed for this layer to apply
            continue
        front = (thu + fri) / 1_000_000.0   # domestic_mid is in dollars; actuals are in $M
        snap = _f(pred.get("snapshot_mid_m")) or _f(pred.get("seat_mid_m"))
        atype = look.get(movie.strip().lower(), "")
        rows.append((movie, actual, snap, front * glob, front * aud_mult(atype, glob, per),
                     atype, front))

    # blends of snapshot (idx 2) and fri-anchor+audience (idx 4)
    def mae_blend(wf):
        es = sorted(abs((1 - wf) * r[2] + wf * r[4] - r[1]) / r[1] * 100 for r in rows if r[2] and r[4])
        n = len(es)
        return (sum(es) / n, es[n // 2] if n % 2 else (es[n // 2 - 1] + es[n // 2]) / 2) if es else (0, 0)

    def mae(idx):
        es = sorted(abs(r[idx] - r[1]) / r[1] * 100 for r in rows if r[idx])
        n = len(es)
        return (sum(es) / n, es[n // 2] if n % 2 else (es[n // 2 - 1] + es[n // 2]) / 2) if es else (0, 0)

    print(f"\n{'movie':26}{'actual':>8}{'snap':>8}{'friAnc':>8}{'friAnc+A':>9}{'aud':>14}")
    for m, a, s, fg, fa, at, fr in rows:
        print(f"{m[:26]:26}{a:>8.1f}{(s or 0):>8.1f}{fg:>8.1f}{fa:>9.1f}{at[:13]:>14}")
    sm, smd = mae(2); fgm, fgmd = mae(3); fam, famd = mae(4)
    print(f"\n(n={len(rows)} films with Friday observed)")
    print(f"  snapshot (current)   : MAE {sm:5.1f}%   median {smd:5.1f}%")
    print(f"  fri-anchor (global)  : MAE {fgm:5.1f}%   median {fgmd:5.1f}%   ({sm - fgm:+.1f} vs snapshot)")
    print(f"  fri-anchor + audience: MAE {fam:5.1f}%   median {famd:5.1f}%   ({sm - fam:+.1f} vs snapshot)")
    print("  --- blends of snapshot x fri-anchor(audience) ---")
    blends = []
    for wf in (0.33, 0.5, 0.67):
        bm, bmd = mae_blend(wf)
        blends.append((bm, wf))
        print(f"  blend {int((1-wf)*100)}/{int(wf*100)} snap/fri : MAE {bm:5.1f}%   median {bmd:5.1f}%   ({sm - bm:+.1f} vs snapshot)")
    best_blend = min(blends)
    gain = sm - best_blend[0]
    print(f"\n>>> {'SHIP a blend (fri weight ' + str(best_blend[1]) + ', ' + f'{gain:+.1f} pts)' if gain > 1.0 else 'no combination beats snapshot by >1pt — do not ship as a general layer'}")


if __name__ == "__main__":
    main()
