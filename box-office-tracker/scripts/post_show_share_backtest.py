#!/usr/bin/env python3
"""Backtest: AMC share from POST-show volume vs the pre-sale volume ratio.

The 2026-10-10 Other Mommy audit found the cross-chain volume share is
pre-sale biased for fan-driven horror: fans pre-book at AMC (A-List), so the
pre-reservation ratio q overstates AMC's share of the weekend. Post-show
finals (AMC seat-counts vs the Cinemark post-show census) include walk-ins
on both sides, so q_post should track the truth share more closely.

For every film with Cinemark census rows AND a recorded actual, print the
truth share (AMC seats per national dollar, panel-normalized like
share_truth_audit.py), the live pre-sale share, and the post-show share from
Thursday+Friday finals (what the after-Friday stage would see), plus the
|log err| summary. Informational — exits 0.

    python3 scripts/post_show_share_backtest.py
    python3 scripts/post_show_share_backtest.py --k-post 1.0
"""
import argparse
import csv
import gzip
import json
import math
import os
import statistics
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import predict as P  # noqa: E402

MIN_SOLD_SEATS = 15000


def _rows(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", newline="") as f:
        yield from csv.DictReader(f)


def cinemark_census(weekend_of):
    """movie -> show_date -> {"seats": int, "theatres": set}."""
    out = {}
    paths = [P.CINEMARK_SNAPSHOTS_CSV]
    stem = os.path.splitext(os.path.basename(P.CINEMARK_SNAPSHOTS_CSV))[0]
    paths.append(os.path.join(P.DATA_DIR, "cinemark-archive", f"{stem}-{weekend_of}.csv.gz"))
    seen = set()
    for p in paths:
        if not os.path.exists(p):
            continue
        for r in _rows(p):
            if (r.get("weekend_of") or "").strip() != weekend_of:
                continue
            if (r.get("row_kind") or "").strip() != "post-show-census":
                continue
            key = (r.get("theatre_name"), r.get("show_date"), r.get("showtime"), r.get("movie_title"))
            if key in seen:
                continue
            seen.add(key)
            try:
                sold = int(float(r.get("reserved_seats") or 0))
            except ValueError:
                continue
            d = out.setdefault(r["movie_title"].strip(), {}).setdefault(
                r.get("show_date", ""), {"seats": 0, "theatres": set()})
            d["seats"] += sold
            d["theatres"].add(r.get("theatre_name"))
    return out


def amc_finals(weekend_of):
    """movie -> date -> {"seats": int, "theatres": set} from post-show seat counts."""
    out = {}
    seen = set()
    for reader in P._seat_row_sources(weekend_of):
        for r in reader:
            if (r.get("weekend_of") or "").strip() != weekend_of:
                continue
            key = (r.get("theatre_name"), r.get("date"), r.get("showtime"), r.get("movie_title"))
            if key in seen:
                continue
            seen.add(key)
            try:
                sold = int(float(r.get("seats_sold") or 0))
            except ValueError:
                continue
            d = out.setdefault(r["movie_title"].strip(), {}).setdefault(
                r.get("date", ""), {"seats": 0, "theatres": set()})
            d["seats"] += sold
            d["theatres"].add(r.get("theatre_name"))
    return out


def share_from_q(q, k, cal):
    wa = P.CROSS_CHAIN_CAPACITY_SHARE
    formula = wa * q / (wa * q + (1.0 - wa) * k)
    base = P.calibrated_amc_market_share(cal)
    shrunk = base + P.CROSS_CHAIN_SHARE_WEIGHT * (formula - base)
    lo, hi = P.CROSS_CHAIN_SHARE_CLAMP_ABS
    return max(lo, min(hi, shrunk))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k-post", type=float, default=None,
                    help="walk-up constant for the post-show formula (default: fit)")
    ap.add_argument("--through", default="friday", choices=["thursday", "friday"],
                    help="which show dates feed q_post (stage)")
    args = ap.parse_args(argv)

    import calibrate
    cal = calibrate.load_calibration()
    fleet = P.calibrated_amc_market_share(cal)
    hist = cal.get("history", [])

    # panel truth (same construction as share_truth_audit)
    panel = []
    films = []
    for h in hist:
        movie, w, actual = h.get("movie"), h.get("weekend_of"), h.get("actual_total")
        if not movie or not w or not actual or h.get("data_outage"):
            continue
        seat = P.load_seat_data(weekend_of=w).get(movie)
        if not seat:
            continue
        sold = sum(int(float(r.get("seats_sold") or 0)) for rows in seat.values() for r in rows)
        if sold < MIN_SOLD_SEATS:
            continue
        spd = sold / actual / 1000.0
        panel.append(spd)
        films.append((movie, w, actual, spd))
    median_spd = statistics.median(panel)

    rows = []
    for movie, w, actual, spd in films:
        truth = spd / median_spd * fleet
        cen = cinemark_census(w)
        c = P.movie_mapping_get(cen, movie, None)
        if not c:
            continue
        a = P.movie_mapping_get(amc_finals(w), movie, None) or {}
        thu = (datetime.strptime(w, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        dates = [thu, w] if args.through == "friday" else [thu]
        qs = []
        for d in dates:
            ca, cc = a.get(d), c.get(d)
            if not ca or not cc or not ca["theatres"] or not cc["theatres"] or cc["seats"] <= 0:
                continue
            spt_a = ca["seats"] / len(ca["theatres"])
            spt_c = cc["seats"] / len(cc["theatres"])
            qs.append(spt_a / spt_c)
        if not qs:
            continue
        q_post = statistics.median(qs)
        P._CROSS_CHAIN_CACHE.clear()
        ccd = P.load_cross_chain_occupancy(weekend_of=w, through_date=w)
        info = P.movie_mapping_get(ccd, movie, None) or {}
        q_pre = info.get("volume_ratio")
        pre_share = P.cross_chain_volume_share(movie, ccd, cal)
        rows.append({"movie": movie, "w": w, "actual": actual, "truth": truth,
                     "q_pre": q_pre, "pre_share": pre_share, "q_post": q_post,
                     "n_post_days": len(qs)})

    if not rows:
        print("no films with census + actuals")
        return 0

    # fit K_post (LOO) unless given
    def loss(k, subset):
        return sum(abs(math.log(share_from_q(r["q_post"], k, cal) / r["truth"])) for r in subset)

    grid = [x / 100 for x in range(50, 301, 5)]
    if args.k_post is None:
        k_fit = min(grid, key=lambda k: loss(k, rows))
    else:
        k_fit = args.k_post

    print(f"post-show share backtest — {len(rows)} films, fleet {fleet:.1%}, "
          f"K_pre {P.CROSS_CHAIN_WALKUP_K:.2f}, K_post {'fit' if args.k_post is None else 'given'} {k_fit:.2f}")
    print(f"{'movie':24} {'weekend':10} {'truth':>6} {'pre':>6} {'post':>6} {'postLOO':>7} "
          f"{'fleet':>6} {'q_pre':>6} {'q_post':>6}  err_pre err_post err_fleet")
    e_pre, e_post, e_post_loo, e_fleet = [], [], [], []
    for r in rows:
        pre = r["pre_share"] if r["pre_share"] else fleet
        post = share_from_q(r["q_post"], k_fit, cal)
        others = [x for x in rows if x is not r]
        k_loo = min(grid, key=lambda k: loss(k, others)) if args.k_post is None else k_fit
        post_loo = share_from_q(r["q_post"], k_loo, cal)
        le_pre = math.log(pre / r["truth"])
        le_post = math.log(post / r["truth"])
        le_post_loo = math.log(post_loo / r["truth"])
        le_fleet = math.log(fleet / r["truth"])
        e_pre.append(abs(le_pre)); e_post.append(abs(le_post))
        e_post_loo.append(abs(le_post_loo)); e_fleet.append(abs(le_fleet))
        print(f"{r['movie'][:24]:24} {r['w']:10} {r['truth']:6.1%} {pre:6.1%} {post:6.1%} {post_loo:7.1%} "
              f"{fleet:6.1%} {(r['q_pre'] or 0):6.2f} {r['q_post']:6.2f}  "
              f"{le_pre:+7.2f} {le_post:+8.2f} {le_fleet:+9.2f}")
    n = len(rows)
    print(f"mean |log err|: pre-sale {sum(e_pre)/n:.3f}  post-show {sum(e_post)/n:.3f}  "
          f"post-show LOO {sum(e_post_loo)/n:.3f}  fleet prior {sum(e_fleet)/n:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
