#!/usr/bin/env python3
"""Sample real AMC ticket prices: one showtime per theatre × format per weekend.

Reads the Phase 1 link file, picks for every (theatre, format) one showtime
(Friday evening when there is one), fetches the tickets route through the
proxy, and appends to data/ticket-prices.csv. Pairs already sampled for this
weekend_of are skipped, so the daily link slots converge on full coverage
without re-spending. Budgets: TICKET_PRICE_MAX_MB (default 40) and
TICKET_PRICE_MAX_SEC (default 600). Never prints the proxy credential.

The model does not use these prices yet (AMC_USE_SAMPLED_PRICES=0): the
calibration was fitted against the assumed prices, so the switch happens
with a recalibration once a few weekends are sampled. predict.py prints the
sampled-vs-assumed gap meanwhile.
"""
import csv, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import seat_fetch_http as sfh  # noqa: E402
import scraper  # noqa: E402  (proxy settings, exactly as the seat lane)

LINKS = ROOT / "data" / "showtime-links.json"
OUT = ROOT / "data" / "ticket-prices.csv"
FIELDS = ["weekend_of", "sampled_at", "theatre_name", "tz", "show_date", "day_of_week", "showtime",
          "showtime_id", "auditorium_type", "adult_price", "child_price", "senior_price",
          "convenience_fee", "all_prices", "raw_bytes"]
MAX_MB = float(os.environ.get("TICKET_PRICE_MAX_MB") or 40)
MAX_SEC = float(os.environ.get("TICKET_PRICE_MAX_SEC") or 600)


def pick_samples(links: dict, weekend_of: str, already: set) -> list:
    """Pure: one (theatre, format) -> showtime per pair not yet sampled.
    Prefers the weekend Friday, then Saturday, then any date; within a date
    the middle showtime (an evening slot rather than a matinee)."""
    try:
        fri = datetime.strptime(weekend_of, "%Y-%m-%d")
    except (TypeError, ValueError):
        return []
    from datetime import timedelta
    order = [fri.strftime("%Y-%m-%d"), (fri + timedelta(days=1)).strftime("%Y-%m-%d"),
             (fri - timedelta(days=1)).strftime("%Y-%m-%d"), (fri + timedelta(days=2)).strftime("%Y-%m-%d")]
    out = []
    for theatre, entry in (links.get("theatres") or {}).items():
        dates = entry.get("dates") or {}
        by_fmt = {}
        for d in order + sorted(set(dates) - set(order)):
            movies = (dates.get(d) or {}).get("movies") or {}
            for shows in movies.values():
                for s in shows:
                    fmt = s.get("format") or "Standard"
                    by_fmt.setdefault(fmt, []).append((d, s))
        for fmt, shows in by_fmt.items():
            if (theatre, fmt) in already:
                continue
            # keep the first date in preference order; take its middle showtime
            first_date = shows[0][0]
            same = [s for d, s in shows if d == first_date]
            s = same[len(same) // 2]
            if s.get("showtime_id"):
                out.append({"theatre_name": theatre, "tz": entry.get("tz", ""), "show_date": first_date,
                            "showtime": s.get("showtime", ""), "showtime_id": str(s["showtime_id"]),
                            "auditorium_type": fmt})
    return out


def load_already(weekend_of: str) -> set:
    if not OUT.exists():
        return set()
    with open(OUT, newline="") as f:
        return {(r["theatre_name"], r["auditorium_type"]) for r in csv.DictReader(f) if r.get("weekend_of") == weekend_of}


def main() -> int:
    links = json.loads(LINKS.read_text())
    weekend_of = links.get("weekend_of") or ""
    if not weekend_of:
        print("ticket prices: link file has no weekend_of — nothing to do"); return 0
    todo = pick_samples(links, weekend_of, load_already(weekend_of))
    print(f"ticket prices: weekend {weekend_of}, {len(todo)} (theatre, format) pairs to sample, "
          f"budget {MAX_MB:.0f} MB / {MAX_SEC:.0f} s", flush=True)
    if not todo:
        return 0
    proxy = scraper._http_proxy_url()
    sess = sfh.make_session()
    tree = None
    spent = 0; t0 = time.monotonic(); ok = walls = other = errs = diff_ok = 0
    new = not OUT.exists()
    with open(OUT, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        last_id = None
        for item in todo:
            if spent >= MAX_MB * 1048576 or time.monotonic() - t0 >= MAX_SEC:
                print(f"ticket prices: budget reached after {ok} samples", flush=True); break
            url = sfh.tickets_url(item["showtime_id"])
            res = None
            try:
                if tree and last_id and last_id != item["showtime_id"]:
                    res = sfh.fetch_rsc_tickets(url, proxy, tree_header=sfh.router_tree_header(tree, last_id), session=sess)
                    if res["kind"] == "prices":
                        diff_ok += 1
                    else:
                        res = None
                if res is None:
                    res = sfh.fetch_rsc_tickets(url, proxy, session=sess)
                    if res["kind"] == "prices" and tree is None:
                        tree = sfh.extract_router_tree(res["payload"])
                        if tree:
                            print("ticket prices: learned the tickets route tree — using segment diffs", flush=True)
            except Exception as e:
                errs += 1
                if errs <= 3:
                    print(f"  fetch failed ({type(e).__name__}) for {item['theatre_name']}", flush=True)
                continue
            spent += res["raw_bytes"]
            if res["kind"] == "prices":
                p = res["prices"]; ok += 1; last_id = item["showtime_id"]
                w.writerow({**{k: item.get(k, "") for k in FIELDS}, "weekend_of": weekend_of,
                            "sampled_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "day_of_week": datetime.strptime(item["show_date"], "%Y-%m-%d").strftime("%A"),
                            "adult_price": p.get("adult") or "", "child_price": p.get("child") or "",
                            "senior_price": p.get("senior") or "", "convenience_fee": p.get("fee") or "",
                            "all_prices": json.dumps(p.get("all") or {}, separators=(",", ":")),
                            "raw_bytes": res["raw_bytes"]})
                f.flush()
            elif res["kind"] in ("blocked", "challenge"):
                walls += 1
            else:
                other += 1
    print(f"ticket prices: sampled={ok} (diff={diff_ok}) walls={walls} other={other} errors={errs} "
          f"bytes={spent / 1048576:.1f} MB in {time.monotonic() - t0:.0f}s -> {OUT.name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
