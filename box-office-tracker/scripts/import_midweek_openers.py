#!/usr/bin/env python3
"""Seed data/midweek-opening-dailies.csv with past pre-Friday openings.

The file is the comp set midweek_opening.py projects from. Live weekends add
themselves (scripts/fetch_daily_actuals.py); this script backfills history from
The Numbers' daily tables: the wide releases of 2021-2026 that opened on a
Monday-Thursday. historical-comps.csv holds none of them (it was built as a
Thursday-previews comp set) and calibration.json five (Minions & Monsters, The
Amazing Digital Circus, Hope, Ramayana, Ghost Soldier).

    python3 scripts/import_midweek_openers.py            # fetch + append what is new
    python3 scripts/import_midweek_openers.py --dry-run
    python3 scripts/import_midweek_openers.py --film "Title" 2027-11-26
"""
import argparse
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import midweek_opening as M  # noqa: E402

# (title on The Numbers, opening-weekend Friday)
SEED = [
    # Thanksgiving, Wednesday
    ("Encanto", "2021-11-26"), ("House of Gucci", "2021-11-26"),
    ("Resident Evil: Welcome to Raccoon City", "2021-11-26"),
    ("Strange World", "2022-11-25"), ("Devotion", "2022-11-25"),
    ("Wish", "2023-11-24"), ("Napoleon", "2023-11-24"),
    ("Moana 2", "2024-11-29"), ("Zootopia 2", "2025-11-28"), ("Eternity", "2025-11-28"),
    # Christmas week
    ("Sing 2", "2021-12-24"), ("The Matrix Resurrections", "2021-12-24"), ("The King's Man", "2021-12-24"),
    ("Puss in Boots: The Last Wish", "2022-12-23"),
    ("The Color Purple", "2023-12-29"), ("The Boys in the Boat", "2023-12-29"), ("Ferrari", "2023-12-29"),
    ("Nosferatu", "2024-12-27"), ("A Complete Unknown", "2024-12-27"), ("Babygirl", "2024-12-27"),
    ("Marty Supreme", "2025-12-26"), ("Anaconda", "2025-12-26"), ("Song Sung Blue", "2025-12-26"),
    # Independence Day week
    ("Sound of Freedom", "2023-07-07"), ("Despicable Me 4", "2024-07-05"),
    ("Jurassic World Rebirth", "2025-07-04"), ("Minions & Monsters", "2026-07-03"),
    # no holiday in the run
    ("The Super Mario Bros. Movie", "2023-04-07"), ("Air", "2023-04-07"),
    ("Mission: Impossible - Dead Reckoning Part One", "2023-07-14"),
    ("Bob Marley: One Love", "2024-02-16"), ("Madame Web", "2024-02-16"),
    ("The Amazing Digital Circus: The Last Act", "2026-06-05"), ("Hope", "2026-09-11"),
    ("Ramayana: Rise of A Legend", "2026-11-06"), ("Ghost Soldier", "2026-11-13"),
]


def main():
    import import_thenumbers_daily as N
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--film", nargs=2, action="append", metavar=("TITLE", "WEEKEND_OF"))
    args = ap.parse_args()
    as_of = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    existing = M.read_csv()
    appended = []
    for title, weekend in ([tuple(f) for f in args.film] if args.film else SEED):
        try:
            daily = N.fetch_daily_table(title, int(weekend[:4]), weekend_of=weekend) or {}
        except Exception as e:
            print(f"  {title} ({weekend}): fetch failed: {e}")
            continue
        rows = M.week_rows(daily, weekend)
        if not M.opens_before_friday(rows, weekend):
            print(f"  {title} ({weekend}): no regular day before Friday -- skipped")
            continue
        new = M.merge_rows(existing + appended, weekend, title, rows, as_of)
        appended.extend(new)
        print(f"  {title} ({weekend}): {len(rows)} day(s), {len(new)} new")
        time.sleep(1.0)
    if args.dry_run:
        print(f"dry run: {len(appended)} row(s) not written")
        return 0
    M.append_csv(appended)
    print(f"appended {len(appended)} row(s) -> {M.DATA_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
