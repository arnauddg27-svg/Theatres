#!/usr/bin/env python3
"""Re-probe every AMC CLASSIC theatre on file for a readable (reserved) seat map
and rewrite data/amc-classic-reserved.json. Automated weekly (collect-links ET,
Mondays) so theatres that convert to reserved seating join the census without a
manual step. Through AMC_SEAT_PROXY_URL when set (never printed).

A theatre is 'reserved' when any of its first two listed showtimes returns a
parsed seat map; 'no-seat-map' (general admission) and 'no-showtimes' stay out.
A probe that reaches fewer than half the theatres leaves the file untouched.
"""
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import amc_classic  # noqa: E402
import seat_fetch_http as H  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def classic_theatres():
    out = []
    for fn in ("theatres-all.json", "theatres-expansion.json"):
        with open(os.path.join(DATA, fn)) as f:
            d = json.load(f)
        for g, v in d.items():
            if g.startswith("_") or not isinstance(v, list):
                continue
            out += [t for t in v if amc_classic.is_classic(t.get("name"), t.get("slug"))]
    return out


def verdict_for(slug, date, proxy, session):
    res = H.fetch_listing_page(f"https://www.amctheatres.com/showtimes/all/{date}/{slug}/all", proxy, session=session)
    if res.get("kind") != "listing":
        return "unreachable"
    ids = [s.get("showtime_id") for s in H.parse_listing_showtimes(res.get("html", "")) if s.get("showtime_id")][:2]
    if not ids:
        return "no-showtimes"
    for sid in ids:
        r = H.fetch_rsc_seat_page(f"https://www.amctheatres.com/showtimes/{sid}/seats", proxy, session=session)
        if r.get("kind") == "seats":
            return "reserved"
    return "no-seat-map"


def main():
    proxy = os.environ.get("AMC_SEAT_PROXY_URL") or None
    session = H.make_session()
    date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    verdicts = {}
    for t in classic_theatres():
        try:
            verdicts[t["name"]] = verdict_for(t["slug"], date, proxy, session)
        except Exception as e:
            verdicts[t["name"]] = f"error:{type(e).__name__}"
        time.sleep(0.3)
    counts = Counter(verdicts.values())
    reached = sum(n for k, n in counts.items() if k in ("reserved", "no-seat-map", "no-showtimes"))
    print(f"AMC CLASSIC probe: {dict(counts)}")
    if reached < len(verdicts) / 2:
        print("::warning::AMC CLASSIC probe reached too few theatres — keeping the existing list")
        return 0
    out = {"_description": amc_classic.__doc__.strip().splitlines()[0],
           "_probed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
           "_counts": dict(counts),
           "reserved": sorted(n for n, v in verdicts.items() if v == "reserved"),
           "verdicts": dict(sorted(verdicts.items()))}
    with open(amc_classic.ALLOWLIST_JSON, "w") as f:
        json.dump(out, f, indent=1)
    print(f"reserved-seating AMC CLASSIC theatres: {len(out['reserved'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
