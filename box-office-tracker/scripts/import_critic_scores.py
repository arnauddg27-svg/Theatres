#!/usr/bin/env python3
"""Backfill rt_critic_score into historical-comps.csv so the critic signal can be
TESTED for incremental predictive value over the audience score (which is already
populated 217/217). Pulls the Tomatometer straight from each comp's resolved
rt_url via the proven rt_scorecard helper. Cached + throttled; resumable.

Run:  python3 scripts/import_critic_scores.py
      python3 scripts/import_critic_scores.py --dry-run
"""
import argparse
import csv
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import predict as P  # noqa: E402
import import_audience_scores as RT  # noqa: E402

COMPS = os.path.join(P.DATA_DIR, "historical-comps.csv")
CACHE = os.path.join(P.DATA_DIR, ".rt-critic-cache.json")


def _critic_from_url(url):
    sc = RT.rt_scorecard(url)
    for key in ("criticsScore", "criticsAll"):
        block = sc.get(key) or {}
        s = str(block.get("score") or "").strip()
        if s:
            return s
    overlay = sc.get("overlay") or {}
    return str((overlay.get("criticsAll") or {}).get("score") or "").strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--throttle", type=float, default=0.3)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(COMPS)))
    fields = list(rows[0].keys())
    if "rt_critic_score" not in fields:
        # place it right after rt_audience_score_type for tidiness if present
        if "rt_audience_score_type" in fields:
            fields.insert(fields.index("rt_audience_score_type") + 1, "rt_critic_score")
        else:
            fields.append("rt_critic_score")

    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    filled = 0
    for r in rows:
        url = (r.get("rt_url") or "").strip()
        if not url:
            r["rt_critic_score"] = r.get("rt_critic_score", "")
            continue
        if url in cache:
            critic = cache[url]
        else:
            try:
                critic = _critic_from_url(url)
            except Exception as e:  # noqa: BLE001
                critic = ""
                print(f"  {r['movie'][:30]:30} ERROR {str(e)[:50]}")
            cache[url] = critic
            json.dump(cache, open(CACHE, "w"))
            time.sleep(args.throttle)
        r["rt_critic_score"] = critic
        if critic:
            filled += 1
        print(f"  {r['movie'][:30]:30} audience={r.get('rt_audience_score') or '-':>3}  critic={critic or '-':>3}")

    print(f"\ncritic scores resolved: {filled}/{len(rows)}")
    if args.dry_run:
        print("[dry-run] historical-comps.csv NOT written")
        return 0
    with open(COMPS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {COMPS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
