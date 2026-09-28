#!/usr/bin/env python3
"""Alamo Drafthouse lane — a full census of every tracked showing.

Alamo's own site API is open JSON (probed 2026-09-27): no bot wall, no browser,
no proxy. Per market, /s/mother/v2/schedule/market/<slug> lists every session;
/s/mother/v1/app/seats/<cinemaId>/<sessionId> returns every seat with its
status (SOLD / EMPTY / BROKEN / NONE = aisle) and price, ~40-60 KB. 22 markets,
39 cinemas; the 2026-09-25 weekend had ~600 tracked showings left on Saturday.

mode 'pre'  : every upcoming tracked session in the opening window.
mode 'post' : sessions that STARTED 0..ALAMO_POST_WINDOW_MIN ago, from session
              ids stored by pre passes (the schedule drops started sessions) —
              the at/after-showtime read that includes walk-ins.

Rows use the Fandango superset schema (chain=ALMO) in
data/alamo-pre-reservation-snapshots.csv, deduped/deltaed by
fandango_collect.append_unique_fandango_rows. Not wired into the model yet.
"""
import csv
import json
import os
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fandango_collect import (  # noqa: E402
    FANDANGO_PRE_RESERVATION_FIELDS, append_unique_fandango_rows, slugify_title)

DATA_DIR = Path(__file__).resolve().parent / "data"
ALAMO_CSV = DATA_DIR / "alamo-pre-reservation-snapshots.csv"
API = "https://drafthouse.com/s/mother"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "application/json"}
# Alamo's seat endpoint 404s ~30-50 min after showtime (measured 2026-09-27:
# ok at 21 min, 404 from 51 min on), so the walk-in read must land in the
# first half hour: a 30-min window, polled every ALAMO_LOOP_EVERY_MIN by a
# long-running loop job (ALAMO_LOOP_MIN > 0) instead of hourly one-shots.
ALAMO_POST_WINDOW_MIN = int(os.environ.get("ALAMO_POST_WINDOW_MIN", "30"))
ALAMO_LOOP_MIN = int(os.environ.get("ALAMO_LOOP_MIN", "0") or 0)
ALAMO_LOOP_EVERY_MIN = int(os.environ.get("ALAMO_LOOP_EVERY_MIN", "15") or 15)
ALAMO_SLEEP_SEC = float(os.environ.get("ALAMO_SLEEP_SEC", "0.25"))
ALAMO_MAX_SESSIONS = int(os.environ.get("ALAMO_MAX_SESSIONS", "0") or 0)


def _get(path, timeout=30):
    req = urllib.request.Request(f"{API}{path}", headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def seat_counts(seating):
    """Pure: seatingData -> {'total','sold','available','broken','price_cents'}.
    NONE cells are aisles/gaps, not seats. BROKEN seats exist but cannot be
    sold; they are left out of capacity so occupancy = sold / sellable."""
    c = Counter(); prices = []
    for area in seating.get("areas") or []:
        for row in area.get("rows") or []:
            for s in row.get("seats") or []:
                st = (s.get("seatStatus") or "").upper()
                c[st] += 1
                price = s.get("defaultPriceInCents")
                if st in ("SOLD", "EMPTY") and isinstance(price, (int, float)) and price > 0:
                    prices.append(int(price))
    sold, avail = c.get("SOLD", 0), c.get("EMPTY", 0)
    prices.sort()
    return {"total": sold + avail, "sold": sold, "available": avail, "broken": c.get("BROKEN", 0),
            "price_cents": prices[len(prices) // 2] if prices else None}


def window_dates(weekend_of):
    fri = datetime.strptime(weekend_of, "%Y-%m-%d")
    return {(fri + timedelta(days=o)).strftime("%Y-%m-%d") for o in (-1, 0, 1, 2)}


def select_sessions(schedule, target_slugs, dates, now_utc, mode="pre"):
    """Pure: market schedule -> [(session, cinema, title)] to read."""
    cinemas = {c["id"]: c for m in (schedule.get("market") or []) for c in (m.get("cinemas") or [])}
    titles = {}
    for p in schedule.get("presentations") or []:
        show = p.get("show") or {}
        slug = slugify_title(show.get("title") or p.get("slug") or "")
        if slug in target_slugs:
            titles[p["slug"]] = target_slugs[slug]
    out = []
    for s in schedule.get("sessions") or []:
        title = titles.get(s.get("presentationSlug"))
        if not title or s.get("businessDateClt") not in dates or not s.get("reservedSeating", True):
            continue
        start = datetime.fromisoformat(s["showTimeUtc"]).replace(tzinfo=timezone.utc)
        if mode == "pre" and start <= now_utc:
            continue
        out.append((s, cinemas.get(s.get("cinemaId"), {}), title))
    return out


def build_row(session, cinema, title, counts, weekend_of, run_id, now_utc, post=False):
    tz = session.get("cinemaTimeZoneName") or cinema.get("timeZoneName") or "America/Chicago"
    start = datetime.fromisoformat(session["showTimeUtc"]).replace(tzinfo=timezone.utc)
    local = datetime.fromisoformat(session["showTimeClt"])
    minutes_until = max(0, int((start - now_utc).total_seconds() // 60))
    occ = round(counts["sold"] * 100.0 / counts["total"], 1) if counts["total"] else 0.0
    from scraper import snapshot_bucket
    note = (f"alamo-api; {'post-show-census; ' if post else ''}unavailable={counts['broken']}"
            + (f"; price_cents={counts['price_cents']}" if counts["price_cents"] else ""))
    return {
        "weekend_of": weekend_of, "run_id": run_id,
        "snapshot_time": now_utc.isoformat(), "snapshot_bucket": snapshot_bucket(now_utc),
        "show_date": session.get("businessDateClt", ""), "day_of_week": local.strftime("%A"),
        "theatre_name": f"Alamo Drafthouse {cinema.get('name', session.get('cinemaId'))}",
        "theatre_city": cinema.get("city", ""), "timezone": tz, "movie_title": title,
        "showtime": local.strftime("%H:%M"),
        "showtime_id": f"{session.get('cinemaId')}:{session.get('sessionId')}",
        "minutes_until_showtime": minutes_until,
        "auditorium_name": f"Screen {session.get('screenNumber', '')}".strip(),
        "auditorium_type": session.get("formatSlug", ""),
        "total_seats": counts["total"], "reserved_seats": counts["sold"],
        "available_seats": counts["available"], "occupancy_pct": occ,
        "delta_reserved_since_previous": "",
        "amc_seat_map_url": f"{API}/v1/app/seats/{session.get('cinemaId')}/{session.get('sessionId')}",
        "notes": note, "chain": "ALMO", "unavailable_seats": counts["broken"],
        "row_kind": "post-show-census" if post else "alamo-api",
    }


def stored_post_sessions(weekend_of, now_utc, path=ALAMO_CSV):
    """Sessions from stored pre rows that started 0..window minutes ago."""
    if not Path(path).exists():
        return []
    seen, out = set(), []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r.get("weekend_of") != weekend_of or r.get("row_kind") == "post-show-census":
                continue
            sid = r.get("showtime_id") or ""
            if sid in seen or ":" not in sid:
                continue
            seen.add(sid)
            tz = ZoneInfo(r.get("timezone") or "America/Chicago")
            local = datetime.strptime(f"{r['show_date']} {r['showtime']}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)
            start = local.astimezone(timezone.utc)
            # a show after midnight belongs to the previous business date
            if start > now_utc + timedelta(hours=12):
                start -= timedelta(days=1)
            mins = (now_utc - start).total_seconds() / 60
            if 0 <= mins <= ALAMO_POST_WINDOW_MIN:
                cid, sess = sid.split(":", 1)
                out.append(({"cinemaId": cid, "sessionId": sess, "businessDateClt": r["show_date"],
                             "showTimeClt": local.replace(tzinfo=None).isoformat(),
                             "showTimeUtc": start.replace(tzinfo=None).isoformat(),
                             "cinemaTimeZoneName": r.get("timezone"), "screenNumber": (r.get("auditorium_name") or "").replace("Screen ", ""),
                             "formatSlug": r.get("auditorium_type", "")},
                            {"name": r["theatre_name"].replace("Alamo Drafthouse ", ""), "city": r.get("theatre_city", "")},
                            r["movie_title"]))
    return out


def pre_pass_weekend(now_utc):
    """Weekend a PRE pass reads: anchored forward Mon-Wed (upcoming opening),
    EXCEPT the early UTC hours of Monday — Sunday evening in the US — when the
    weekend still playing is the one to read. 2026-09-28 00:40Z: the pass
    anchored to 10-02, found no tracked titles and left Sunday's CT/MT/PT
    shows unread before showtime (same rule as the Webedia lane)."""
    from scraper import opening_weekend_friday, phase1_weekend_anchor
    local = now_utc.replace(tzinfo=None)      # GitHub runners are UTC: same clock as datetime.now()
    if now_utc.weekday() == 0 and now_utc.hour < 12:
        return opening_weekend_friday(local)
    return phase1_weekend_anchor(local, full_weekend=True)


def collect(weekend_of=None, titles=None, mode="pre", now_utc=None):
    from scraper import (opening_weekend_friday, phase1_weekend_anchor,
                         tracked_movie_titles_from_state)
    now_utc = now_utc or datetime.now(timezone.utc)
    if not weekend_of:
        weekend_of = (opening_weekend_friday(datetime.now()) if mode == "post"
                      else pre_pass_weekend(now_utc))
    titles = titles or tracked_movie_titles_from_state(weekend_of)
    totals = Counter()
    if not titles:
        print(f"⚠️  No tracked titles for weekend_of={weekend_of}; nothing to collect.")
        return totals
    target = {slugify_title(t): t for t in titles}
    dates = window_dates(weekend_of)
    run_id = f"alamo-{now_utc.strftime('%Y-%m-%dT%H:%MZ')}"
    print(f"Alamo collect [{mode}] • weekend_of={weekend_of} • titles={titles}", flush=True)
    if mode == "post":
        picks = stored_post_sessions(weekend_of, now_utc)
    else:
        picks = []
        markets = _get("/v1/page/cclamp?useUnifiedSchedule=true")["data"]["marketSummaries"]
        for m in markets:
            try:
                sched = _get(f"/v2/schedule/market/{m['slug']}")["data"]
                totals["markets"] += 1
            except Exception as e:
                totals["market_errors"] += 1
                print(f"  {m['slug']}: schedule ERROR {type(e).__name__}", flush=True)
                continue
            picks += select_sessions(sched, target, dates, now_utc, mode)
            time.sleep(ALAMO_SLEEP_SEC)
    if ALAMO_MAX_SESSIONS:
        picks = picks[:ALAMO_MAX_SESSIONS]
    totals["matched"] = len(picks)
    rows = []
    for session, cinema, title in picks:
        try:
            seating = _get(f"/v1/app/seats/{session['cinemaId']}/{session['sessionId']}")["data"]["seatingData"]
            counts = seat_counts(seating)
        except Exception as e:
            totals["errors"] += 1
            continue
        if not counts["total"]:
            totals["empty"] += 1
            continue
        rows.append(build_row(session, cinema, title, counts, weekend_of, run_id, now_utc, post=(mode == "post")))
        totals["captured"] += 1
        time.sleep(ALAMO_SLEEP_SEC)
    written, deduped = append_unique_fandango_rows(rows, csv_path=ALAMO_CSV)
    totals["written"], totals["deduped"] = written, deduped
    print(f"=== Alamo collect summary [{mode}] === " + " ".join(f"{k}={v}" for k, v in sorted(totals.items())), flush=True)
    return totals


def main():
    mode = "post" if os.environ.get("ALAMO_MODE") == "post" else "pre"
    if mode == "post" and ALAMO_LOOP_MIN > 0:
        end = time.monotonic() + ALAMO_LOOP_MIN * 60
        total = Counter()
        while True:
            total.update(collect(mode=mode))
            if time.monotonic() + ALAMO_LOOP_EVERY_MIN * 60 > end:
                break
            time.sleep(ALAMO_LOOP_EVERY_MIN * 60)
        print("=== Alamo post loop total === " + " ".join(f"{k}={v}" for k, v in sorted(total.items())), flush=True)
        return 0
    t = collect(mode=mode)
    if mode == "pre" and t.get("markets", 0) >= 5 and t.get("matched", 0) == 0 and t.get("market_errors", 0) == 0:
        print("::warning::Alamo pre pass matched no tracked showings (titles not playing, or a slug mismatch)")
    if t.get("matched", 0) and not t.get("captured", 0):
        print("❌ Alamo: every seat read failed — failing loudly.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
