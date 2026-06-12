#!/usr/bin/env python3
"""Validate the "disabled seat input == sold seat" assumption.

The whole seat model rests on COUNT_SEATS_JS treating a disabled seat input as
a sold seat. Disabled can also mean house-held, broken, or mid-checkout seats.
This diagnostic estimates the held-seat baseline per auditorium format: for
each showtime, take its EARLIEST long-lead snapshot (>= MIN_LEAD_MINUTES before
showtime) — almost nothing is genuinely sold that early, so the "reserved"
count at first observation approximates the non-sold disabled floor.

Interpretation:
  - small + stable median  -> assumption fine; calibration absorbs the constant
  - large or format-varying -> a per-format bias worth a correction constant

Usage:
    python3 scripts/seat_hold_baseline.py [--min-lead-minutes 1440]
"""
from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRE_RESERVATION_CSV = ROOT / "data" / "pre-reservation-snapshots.csv"

MIN_LEAD_MINUTES = 1440  # >= 1 day before showtime


def main(argv):
    min_lead = MIN_LEAD_MINUTES
    if "--min-lead-minutes" in argv:
        min_lead = int(argv[argv.index("--min-lead-minutes") + 1])

    earliest = {}  # showtime identity -> (minutes_until, occ, format)
    with open(PRE_RESERVATION_CSV, newline="") as f:
        for row in csv.DictReader(f):
            try:
                total = float(row.get("total_seats") or 0)
                reserved = float(row.get("reserved_seats") or 0)
                minutes = int(float(row.get("minutes_until_showtime") or 0))
            except (TypeError, ValueError):
                continue
            if total <= 0 or minutes < min_lead:
                continue
            key = (
                row.get("theatre_name", ""),
                row.get("showtime_id", "") or row.get("showtime", ""),
                row.get("show_date", ""),
            )
            prev = earliest.get(key)
            if prev is None or minutes > prev[0]:
                fmt = row.get("auditorium_type", "") or "Standard"
                earliest[key] = (minutes, reserved / total, fmt)

    by_format = defaultdict(list)
    for minutes, occ, fmt in earliest.values():
        by_format[fmt].append(occ)

    if not by_format:
        print(f"no snapshots with lead >= {min_lead} minutes — lower --min-lead-minutes")
        return 1

    print(f"Held-seat baseline at first long-lead observation (lead >= {min_lead} min)")
    print(f"{'format':<44}{'n':>6}{'median':>9}{'p90':>8}")
    overall = []
    for fmt, occs in sorted(by_format.items(), key=lambda kv: -len(kv[1])):
        overall.extend(occs)
        occs.sort()
        p90 = occs[int(0.9 * (len(occs) - 1))]
        print(f"{fmt[:43]:<44}{len(occs):>6}{statistics.median(occs):>9.1%}{p90:>8.1%}")
    overall.sort()
    p90 = overall[int(0.9 * (len(overall) - 1))]
    print(f"{'ALL':<44}{len(overall):>6}{statistics.median(overall):>9.1%}{p90:>8.1%}")
    print(
        "\nIf the ALL median is small (<~5%) and formats are similar, the\n"
        "disabled==sold assumption is sound; calibration absorbs the constant.\n"
        "Large per-format gaps would justify a per-format correction."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
