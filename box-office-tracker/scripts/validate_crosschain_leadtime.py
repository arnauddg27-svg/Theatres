#!/usr/bin/env python3
"""Does projecting Fandango pre-show reads to FINAL fix the cross-chain share?

AMC occupancy is captured AFTER showtime (final fill). Fandango is captured
BEFORE (incomplete, and at wildly varying lead — Regal 15h out shows ~2%,
Cinemark 1h out shows ~27%). Comparing raw occupancy is apples-to-oranges.

Fix under test: keep only Fandango rows within LEAD_CAP of showtime, project each
to final via snapshot_reservation_multiplier(lead), then compare projected-final
Regal/Cinemark occupancy to AMC final occupancy. Validate against the known
truth: Minions under-indexes AMC (~0.14 from its Thursday actual), Supergirl ~0.26,
Jackass ~0.33. Read-only.
"""
import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

LEAD_CAP = 360.0   # minutes; only trust Fandango reads within 6h of showtime
FLEET = 0.219


def num(x):
    try:
        return float(str(x).replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def main():
    films = {"inion": "Minions", "upergirl": "Supergirl", "ackass": "Jackass"}
    # AMC final occupancy per film
    amc = defaultdict(list)
    for r in csv.DictReader(open(os.path.join(P.DATA_DIR, "seat-counts.csv"))):
        m = r.get("movie_title", "")
        key = next((v for k, v in films.items() if k in m), None)
        if key and r.get("weekend_of", "") >= "2026-06-26":
            o = num(r.get("occupancy_pct"))
            if o is not None:
                amc[key].append(o)
    # Fandango: raw vs lead-capped-projected occupancy
    raw = defaultdict(list)
    proj = defaultdict(list)
    for r in csv.DictReader(open(os.path.join(P.DATA_DIR, "fandango-pre-reservation-snapshots.csv"))):
        m = r.get("movie_title", "")
        key = next((v for k, v in films.items() if k in m), None)
        if not key or r.get("weekend_of", "") < "2026-06-26":
            continue
        o = num(r.get("occupancy_pct"))
        lead = num(r.get("minutes_until_showtime"))
        if o is None or lead is None:
            continue
        raw[key].append(o)
        if 0 <= lead <= LEAD_CAP:
            mult = P.snapshot_reservation_multiplier(lead)
            proj[key].append(min(100.0, o * mult))

    def share(occ_a, occ_rc, k=P.CROSS_CHAIN_WALKUP_K):
        a = FLEET * occ_a
        b = (1 - FLEET) * k * occ_rc
        return a / (a + b) if (a + b) else None

    print(f"{'film':10}{'AMC occ':>9}{'RC raw':>8}{'RC proj':>9}{'share raw':>11}{'share proj':>12}")
    truth = {"Minions": 0.14, "Supergirl": 0.26, "Jackass": 0.33}
    for key in ("Minions", "Supergirl", "Jackass"):
        if not amc[key] or not raw[key]:
            continue
        aocc = sum(amc[key]) / len(amc[key])
        rraw = sum(raw[key]) / len(raw[key])
        rproj = sum(proj[key]) / len(proj[key]) if proj[key] else None
        s_raw = share(aocc, rraw)
        s_proj = share(aocc, rproj) if rproj else None
        print(f"{key:10}{aocc:>8.1f}%{rraw:>7.1f}%"
              f"{(f'{rproj:.1f}%' if rproj else '-'):>9}"
              f"{s_raw:>11.3f}{(f'{s_proj:.3f}' if s_proj else '-'):>12}"
              f"   (truth ~{truth[key]}, n_proj={len(proj[key])})")


if __name__ == "__main__":
    main()
