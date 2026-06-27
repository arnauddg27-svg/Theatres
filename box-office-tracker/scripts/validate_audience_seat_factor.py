#!/usr/bin/env python3
"""Gate for the audience-type seat correction: does applying
audience_frontload_seat_factor to the seat-only extrapolation REDUCE the
Thursday-as-of seat backtest error on the calibration history, or does it hurt
under-predictors (e.g. Mortal Kombat II under-shot at $26.7M vs $38.5M)?

Replays each history film as-of its Thursday (leak-free frozen calibration),
takes the seat-only estimate, looks up its audience_type, applies the bounded
factor, and compares seat MAE before/after. Read-only — does NOT wire anything.
"""
import csv
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

# Comp-calibrated audience-type Thursday-share factor (self-contained — this is
# a research gate, intentionally NOT wired into predict.py).
FLOOR, CAP = 0.78, 1.25
_SHARES = None


def _audience_thursday_shares():
    global _SHARES
    if _SHARES is not None:
        return _SHARES
    by_type, allv = {}, []
    with open(os.path.join(P.DATA_DIR, "historical-comps.csv")) as f:
        for r in csv.DictReader(f):
            try:
                thu = float(r.get("thursday_preview_m") or 0)
                wknd = sum(float(r.get(k) or 0) for k in ("friday_m", "saturday_m", "sunday_m"))
            except (TypeError, ValueError):
                continue
            if thu > 0 and wknd > 0:
                allv.append(thu / wknd)
                a = (r.get("audience_type") or "").strip()
                if a:
                    by_type.setdefault(a, []).append(thu / wknd)
    g = sum(allv) / len(allv) if allv else 0.0
    _SHARES = (g, {a: (sum(v) / len(v), len(v)) for a, v in by_type.items()})
    return _SHARES


def audience_frontload_seat_factor(audience_type, min_n=6, shrink=8.0):
    if not audience_type:
        return 1.0
    g, shares = _audience_thursday_shares()
    info = shares.get(audience_type.strip())
    if not g or not info:
        return 1.0
    share, n = info
    if n < min_n or share <= 0:
        return 1.0
    weight = n / (n + shrink)
    factor = 1.0 + weight * (g / share - 1.0)
    return max(FLOOR, min(CAP, factor))


def _audience_lookup():
    """movie (lowercased) -> audience_type, from metadata then comps."""
    look = {}
    for path in ("movie-metadata.csv", "historical-comps.csv"):
        try:
            with open(os.path.join(P.DATA_DIR, path)) as f:
                for r in csv.DictReader(f):
                    m = (r.get("movie") or "").strip().lower()
                    a = (r.get("audience_type") or "").strip()
                    if m and a and m not in look:
                        look[m] = a
        except OSError:
            pass
    return look


def _thu(weekend):
    return (datetime.strptime(weekend, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")


def main():
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    look = _audience_lookup()
    load_md = getattr(P, "load_movie_metadata", None)

    rows = []
    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        thu = _thu(w)
        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)
        except Exception:
            continue
        seat_data = P.filter_seat_data_through(P.load_seat_data(weekend_of=w), thu)
        sd = P.movie_mapping_get(seat_data, movie, None)
        if not sd:
            continue
        snap = P.load_pre_reservation_data(weekend_of=w, through_date=thu)
        try:
            pred = P.predict_movie(
                movie, sd, P.movie_mapping_get(P.load_polymarket_data(weekend_of=w, through_date=thu), movie, []),
                cal, national_theatre_count=P.national_theatre_count_for_movie(
                    movie, P.load_theatre_counts(), metadata=(load_md() if load_md else None)),
                snapshot_data=P.movie_mapping_get(snap, movie, {}),
                social_data=P.load_social_signal_data(weekend_of=w, through_date=thu),
            )
        except Exception:
            continue
        seat = pred.get("seat_mid_m") if pred else None
        if not seat:
            continue
        atype = look.get(movie.strip().lower(), "")
        factor = audience_frontload_seat_factor(atype)
        rows.append((movie, actual, seat, seat * factor, atype, factor))

    def mae(pairs):
        es = [abs(e - a) / a * 100 for a, e in pairs if a]
        es.sort()
        n = len(es)
        return (sum(es) / n, es[n // 2] if n % 2 else (es[n // 2 - 1] + es[n // 2]) / 2) if es else (0, 0)

    print(f"{'movie':26}{'actual':>8}{'seat':>8}{'seat*f':>8}{'audience':>14}{'factor':>7}")
    for m, a, s, sf, at, f in rows:
        print(f"{m[:26]:26}{a:>8.1f}{s:>8.1f}{sf:>8.1f}{at[:14]:>14}{f:>7.3f}")
    base = mae([(a, s) for _, a, s, _, _, _ in rows])
    adj = mae([(a, sf) for _, a, _, sf, _, _ in rows])
    print(f"\nseat-only MAE  : {base[0]:6.1f}%   median {base[1]:5.1f}%   (n={len(rows)})")
    print(f"+audience factor: {adj[0]:6.1f}%   median {adj[1]:5.1f}%")
    print(f"\n>>> audience factor changes seat MAE by {base[0] - adj[0]:+.1f} pts "
          f"({'WIRE IT' if base[0] - adj[0] > 1.0 else 'NO — does not help the noisy seat layer'})")


if __name__ == "__main__":
    main()
