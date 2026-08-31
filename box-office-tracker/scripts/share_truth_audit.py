#!/usr/bin/env python3
"""Post-weekend AMC-share truth audit: measure per-film share error weekly.

The single largest error source in the 2026-08-28 post-mortem was the
AMC-to-national share divisor: both films' ground-truth share (AMC seats sold
per national dollar, normalized to the panel median) ran ~27% while the model
divided by 16.9%/20.2% — a +40%/+79% miss with no monitor watching the share
dimension at all. Per-film truth spans ~3x (10%-30%) across the recorded
history, so this is a standing error channel, not a one-off.

This script recomputes the ground truth for any weekend with recorded actuals
and prints each film's implied share against the fleet prior, flagging films
whose share error exceeds the warning threshold. Informational by design —
always exits 0 (a watchdog that can brick finalize would repeat the
clean_canonical_data incident). Run it after actuals land (Wednesday's
calibrate, or manually):

    python3 scripts/share_truth_audit.py                 # latest recorded weekend
    python3 scripts/share_truth_audit.py --weekend 2026-08-21
    python3 scripts/share_truth_audit.py --all           # every recorded weekend
"""
import argparse
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WARN_LOG_ERROR = 0.22   # |log(truth/fleet)| above this -> flag (~25% share miss)
MIN_SOLD_SEATS = 15000  # below this the seats/$ ratio is too noisy to score


def film_rows(history, seat_loader):
    """(movie, weekend, seats_per_national_dollar_k, actual_total) rows."""
    rows = []
    seen = set()
    for h in history:
        movie = h.get("movie")
        weekend = h.get("weekend_of") or h.get("date")
        actual = h.get("actual_total") or h.get("actual")
        if not movie or not weekend or not actual or h.get("data_outage"):
            continue
        if (movie, weekend) in seen:
            continue
        seen.add((movie, weekend))
        seat = seat_loader(weekend_of=weekend).get(movie)
        if not seat:
            continue
        sold = sum(
            int(float(r.get("seats_sold") or 0))
            for day_rows in seat.values()
            for r in day_rows
        )
        if sold < MIN_SOLD_SEATS:
            continue
        rows.append((movie, weekend, sold / actual / 1000.0, actual))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weekend", help="audit one weekend (YYYY-MM-DD Friday)")
    parser.add_argument("--all", action="store_true", help="audit every recorded weekend")
    args = parser.parse_args(argv)

    from predict import load_seat_data, calibrated_amc_market_share
    import calibrate

    cal = calibrate.load_calibration()
    fleet = calibrated_amc_market_share(cal)
    rows = film_rows(cal.get("history", []), load_seat_data)
    if not rows:
        print("share-truth audit: no scorable film-weekends in calibration history")
        return 0

    median_spd = statistics.median(r[2] for r in rows)
    if args.weekend:
        targets = [r for r in rows if r[1] == args.weekend]
    elif args.all:
        targets = rows
    else:
        latest = max(r[1] for r in rows)
        targets = [r for r in rows if r[1] == latest]

    if not targets:
        print(f"share-truth audit: no scorable films for {args.weekend}")
        return 0

    print(f"share-truth audit — panel median {median_spd:.2f} AMC seats/$k "
          f"across {len(rows)} film-weekends; fleet share {fleet:.1%}")
    print(f"{'movie':30s}{'weekend':12s}{'seats/$k':>9s}{'truth':>8s}{'vs fleet':>9s}")
    for movie, weekend, spd, actual in sorted(targets, key=lambda r: r[1]):
        truth = spd / median_spd * fleet
        log_err = math.log(truth / fleet)
        flag = "  <-- SHARE OUTLIER" if abs(log_err) > WARN_LOG_ERROR else ""
        print(f"{movie[:30]:30s}{weekend:12s}{spd:9.2f}{truth:8.1%}{log_err:+9.2f}{flag}")
        if abs(log_err) > WARN_LOG_ERROR:
            print(f"::warning::share truth for {movie} ({weekend}) is {truth:.1%} "
                  f"vs fleet prior {fleet:.1%} — the AMC-to-national divisor "
                  f"missed by {abs(math.expm1(log_err)):.0%}; per-film share "
                  f"remains the model's largest open error channel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
