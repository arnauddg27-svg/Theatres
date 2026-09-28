#!/usr/bin/env python3
"""Webedia chains lane — per-showing OCCUPANCY % from the chains' own open JSON.

Probed 2026-09-27: Landmark, Showcase, MJR, Flix Brewhouse, Epic and Marquee run the Webedia
"Movies Pro" site platform, whose public schedule endpoint

    GET {site}/api/gatsby-source-boxofficeapi/schedule
        ?from=YYYY-MM-DDT03:00:00&to=...&theaters={"id":"X0KAO","timeZone":"..."}

returns every showtime with `occupancy.rate` (integer % of seats sold),
`screen.name`, `startsAt` (local) and ticketing URLs. No login, no bot wall, no
browser, no proxy, no token. Today's started showings stay listed (the day
drops off at the business-day rollover), so a late-evening pass reads each
showing's final occupancy — walk-ins included, since the box office sells from
the same system. B&B shares the platform but publishes no rate (null) — its
showings are discovered and skipped row-by-row. First pass (Sun 09-27 18:50Z):
139 theatres, 1,007 tracked showings with a rate at 88 of them.

Theatre list (id, name, timeZone, screens) comes from the site's Gatsby static
query data (/page-data/index/page-data.json -> staticQueryHashes ->
/page-data/sq/d/<hash>.json).

SEATS ARE NOT PUBLISHED — only the percentage. Rows carry occupancy_pct and
leave total/reserved seats blank; the census scorecard converts with an
assumed auditorium size (WEBEDIA_EST_SEATS). The seat maps that would give
capacity sit behind the booking engine's session token (not used).

Each run: every theatre, today + the upcoming opening-window dates. A showing
that has started is written as row_kind=post-show-census (the latest read of
the evening is the final count); the rest as webedia-api (pre).
Rows: Fandango superset schema, data/webedia-pre-reservation-snapshots.csv.
Not wired into the model yet.
"""
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fandango_collect import append_unique_fandango_rows, slugify_title  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"
WEBEDIA_CSV = DATA_DIR / "webedia-pre-reservation-snapshots.csv"
# chain code -> (display name, site). Chains without a published rate are
# harmless (their showings are skipped), so the platform's other US sites
# can sit here and start counting the day they switch the field on.
CHAINS = {
    "LMRK": ("Landmark", "https://www.landmarktheatres.com"),
    "SHOW": ("Showcase", "https://www.showcasecinemas.com"),
    "MJRT": ("MJR", "https://www.mjrtheatres.com"),
    "FLIX": ("Flix Brewhouse", "https://flixbrewhouse.com"),
    "BBTH": ("B&B", "https://www.bbtheatres.com"),
    "EPIC": ("Epic", "https://www.epictheatres.com"),
    "MARQ": ("Marquee", "https://www.marqueecinemas.com"),
}
API = "/api/gatsby-source-boxofficeapi"
SLEEP = float(os.environ.get("WEBEDIA_SLEEP_SEC", "0.3"))
ONLY = {c.strip().upper() for c in (os.environ.get("WEBEDIA_CHAINS") or "").split(",") if c.strip()}


def _session():
    from curl_cffi import requests as cr
    return cr.Session(impersonate="chrome")


def theatres_from_static(obj):
    """Pure: walk Gatsby static-query JSON -> [{id,name,timeZone,screens}]."""
    out = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get("__typename") == "Theater" and o.get("id") and o.get("timeZone") and o.get("name"):
                out[o["id"]] = {"id": o["id"], "name": o["name"], "timeZone": o["timeZone"],
                                "screens": len(o.get("screens") or [])}
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return list(out.values())


THEATRES_CACHE = DATA_DIR / "theatres-webedia.json"


def _load_cache():
    try:
        return json.load(open(THEATRES_CACHE))
    except Exception:
        return {}


def _save_cache(chain, theatres):
    cache = _load_cache()
    cache[chain] = theatres
    tmp = str(THEATRES_CACHE) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cache, f, indent=0, sort_keys=True)
    os.replace(tmp, THEATRES_CACHE)


def discover_theatres(s, base, chain=None):
    """Theatre list from the site's Gatsby static-query data; on a miss (the
    sites rebuild daily and 2026-09-28 14:15Z found nothing at any of the 7
    chains for ~15 min) fall back to the list cached from the last success."""
    found = {}
    try:
        pd = s.get(f"{base}/page-data/index/page-data.json", timeout=30).json()
        for h in pd.get("staticQueryHashes") or []:
            try:
                for t in theatres_from_static(s.get(f"{base}/page-data/sq/d/{h}.json", timeout=30).json()):
                    found[t["id"]] = t
            except Exception:
                continue
    except Exception:
        pass
    theatres = list(found.values())
    if theatres:
        if chain:
            try:
                _save_cache(chain, theatres)
            except Exception:
                pass
        return theatres
    cached = _load_cache().get(chain or "", []) if chain else []
    if cached:
        print(f"  {chain}: discovery found nothing — using {len(cached)} cached theatres", flush=True)
    return cached


def schedule_url(base, theatre, day_from, day_to):
    q = urlencode({"from": f"{day_from}T03:00:00", "to": f"{day_to}T03:00:00",
                   "theaters": json.dumps({"id": theatre["id"], "timeZone": theatre["timeZone"]},
                                          separators=(",", ":"))})
    return f"{base}{API}/schedule?{q}"


def movie_titles(s, base, ids):
    out = {}
    ids = sorted(ids)
    for i in range(0, len(ids), 40):
        q = "&".join(f"ids={m}" for m in ids[i:i + 40])
        try:
            for mv in s.get(f"{base}{API}/movies?basic=true&{q}", timeout=30).json() or []:
                out[str(mv.get("id"))] = mv.get("title") or ""
        except Exception:
            continue
    return out


def window_dates(weekend_of):
    fri = datetime.strptime(weekend_of, "%Y-%m-%d")
    return sorted((fri + timedelta(days=o)).strftime("%Y-%m-%d") for o in (-1, 0, 1, 2))


def showings(schedule_json, theatre_id):
    """Pure: schedule response -> [(movie_id, business_date, showtime dict)]."""
    sched = ((schedule_json or {}).get(theatre_id) or {}).get("schedule") or {}
    return [(str(mid), d, st) for mid, by_date in sched.items()
            for d, lst in (by_date or {}).items() for st in (lst or [])]


def build_row(chain, theatre, title, day, st, weekend_of, run_id, now_utc):
    """One snapshot row, or None when the showing publishes no rate."""
    rate = (st.get("occupancy") or {}).get("rate")
    if rate is None:
        return None
    tz = ZoneInfo(theatre["timeZone"])
    local = datetime.fromisoformat(st["startsAt"]).replace(tzinfo=tz)
    start = local.astimezone(timezone.utc)
    started = start <= now_utc
    tags = st.get("tags") or []
    fmt = ",".join(t.split(".")[-1] for t in tags if t.startswith("Format."))
    screen = ((st.get("screen") or {}).get("name") or "").strip()
    from scraper import snapshot_bucket
    return {
        "weekend_of": weekend_of, "run_id": run_id,
        "snapshot_time": now_utc.isoformat(), "snapshot_bucket": snapshot_bucket(now_utc),
        "show_date": day, "day_of_week": local.strftime("%A"),
        "theatre_name": theatre["name"], "theatre_city": "", "timezone": theatre["timeZone"],
        "movie_title": title, "showtime": local.strftime("%H:%M"),
        "showtime_id": f"{theatre['id']}:{st['startsAt']}:{screen}",
        "minutes_until_showtime": max(0, int((start - now_utc).total_seconds() // 60)),
        "auditorium_name": f"Screen {screen}".strip(), "auditorium_type": fmt,
        "total_seats": "", "reserved_seats": "", "available_seats": "",
        "occupancy_pct": float(rate),
        "delta_reserved_since_previous": "",
        "amc_seat_map_url": ((st.get("data") or {}).get("ticketing") or [{}])[0].get("urls", [""])[0],
        "notes": (f"webedia-api; {'post-show-census; ' if started else ''}occupancy_rate={rate}; "
                  f"reserved={'y' if any('ReservedSeating' in t for t in tags) else 'n'}"),
        "chain": chain, "unavailable_seats": "",
        "row_kind": "post-show-census" if started else "webedia-api",
    }


def collect(weekend_of=None, titles=None, now_utc=None, session=None):
    from scraper import opening_weekend_friday, phase1_weekend_anchor, tracked_movie_titles_from_state
    now_utc = now_utc or datetime.now(timezone.utc)
    if not weekend_of:
        # Thu-Sun: this weekend; Mon-Wed: anchor forward like the other lanes,
        # except in the early-UTC hours of Monday when Sunday's evening is
        # still the day being read.
        weekend_of = (opening_weekend_friday(datetime.now()) if now_utc.weekday() == 0 and now_utc.hour < 12
                      else phase1_weekend_anchor(datetime.now(), full_weekend=True))
    titles = titles or tracked_movie_titles_from_state(weekend_of)
    totals = Counter()
    if not titles:
        print(f"⚠️  No tracked titles for weekend_of={weekend_of}; nothing to collect.")
        return totals
    target = {slugify_title(t): t for t in titles}
    wdates = window_dates(weekend_of)
    run_id = f"webedia-{now_utc.strftime('%Y-%m-%dT%H:%MZ')}"
    s = session or _session()
    print(f"Webedia collect • weekend_of={weekend_of} • titles={titles}", flush=True)
    rows = []
    for chain, (label, base) in CHAINS.items():
        if ONLY and chain not in ONLY:
            continue
        try:
            theatres = discover_theatres(s, base, chain=chain)
        except Exception as e:
            print(f"  {label}: discovery ERROR {type(e).__name__}", flush=True)
            totals["chain_errors"] += 1
            continue
        chain_rows, pending, movie_ids = 0, [], set()
        for th in theatres:
            local_today = now_utc.astimezone(ZoneInfo(th["timeZone"]))
            # before the 03:00 rollover the business day is still yesterday
            biz_today = (local_today - timedelta(hours=3)).strftime("%Y-%m-%d")
            days = [d for d in wdates if d >= biz_today]
            if not days:
                continue
            end = (datetime.strptime(days[-1], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            try:
                r = s.get(schedule_url(base, th, days[0], end), timeout=30)
                sched = r.json() if r.status_code == 200 else {}
                if r.status_code != 200:
                    totals["schedule_errors"] += 1
            except Exception:
                totals["schedule_errors"] += 1
                continue
            for mid, day, st in showings(sched, th["id"]):
                if day in days:
                    pending.append((th, mid, day, st))
                    movie_ids.add(mid)
            totals["theatres"] += 1
            time.sleep(SLEEP)
        names = movie_titles(s, base, movie_ids)
        for th, mid, day, st in pending:
            title = target.get(slugify_title(names.get(mid, "")))
            if not title:
                continue
            totals["matched"] += 1
            row = build_row(chain, th, title, day, st, weekend_of, run_id, now_utc)
            if row is None:
                totals["no_rate"] += 1
                continue
            totals["post" if row["row_kind"] == "post-show-census" else "pre"] += 1
            rows.append(row)
            chain_rows += 1
        print(f"  {label}: {len(theatres)} theatres, {chain_rows} rows", flush=True)
    written, deduped = append_unique_fandango_rows(rows, csv_path=WEBEDIA_CSV)
    totals["captured"], totals["written"], totals["deduped"] = len(rows), written, deduped
    print("=== Webedia collect summary === " + " ".join(f"{k}={v}" for k, v in sorted(totals.items())), flush=True)
    return totals


def main():
    t = collect()
    if t.get("theatres", 0) >= 20 and t.get("matched", 0) == 0:
        print("::warning::Webedia pass matched no tracked showings (titles not playing, or a title mismatch)")
    if t.get("theatres", 0) == 0:
        print("❌ Webedia: no theatre schedule read at all — failing loudly.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
