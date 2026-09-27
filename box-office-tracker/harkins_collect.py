#!/usr/bin/env python3
"""Harkins Theatres lane — a full census of every tracked showing (2026-09-27).

Harkins' own services answer plain HTTPS (no bot wall, no browser, no proxy):
  webservice.harkins.com/v2/theatres                               32 theatres
  webservice.harkins.com/v2/theatres/<id>/schedules/<date>/movies  sessions
  cmsservice.harkins.com/api/v1/movies/HO<8-digit id>              title
  ticketingservice.harkins.com/api/Theatre/GetTheatreShowtime/harkinsid/<id>/sessionid/<s>
                                                                   -> Vista cinema id
  ticketingservice.harkins.com/api/Theatre/GetSeatPlan/cinemaid/<vista>/sessionId/<s>
                                                                   -> numberOfSeats, openSeats
Sold = numberOfSeats - openSeats. Same pre/post design and row schema as
alamo_collect (chain=HARK). Not wired into the model yet.
"""
import json
import os
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fandango_collect import append_unique_fandango_rows, slugify_title  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"
HARKINS_CSV = DATA_DIR / "harkins-pre-reservation-snapshots.csv"
WEB = "https://webservice.harkins.com/v2"
CMS = "https://cmsservice.harkins.com/api/v1"
TIX = "https://ticketingservice.harkins.com/api/Theatre"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
           "Accept": "application/json", "Origin": "https://www.harkins.com",
           "Referer": "https://www.harkins.com/"}
SLEEP = float(os.environ.get("HARKINS_SLEEP_SEC", "0.25"))
POST_WINDOW_MIN = int(os.environ.get("HARKINS_POST_WINDOW_MIN", "90"))


def _get(url, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=timeout) as r:
        return json.load(r)


WINDOWS_TZ = {"US Mountain Standard Time": "America/Phoenix", "Mountain Standard Time": "America/Denver",
              "Pacific Standard Time": "America/Los_Angeles", "Central Standard Time": "America/Chicago",
              "Eastern Standard Time": "America/New_York"}


def theatre_tz(theatre):
    """IANA zone from the theatre's Windows time-zone id (Harkins runs AZ, CA,
    CO, OK and TX theatres; Arizona has no daylight saving)."""
    tzid = ((theatre.get("timeZone") or {}).get("id") or "").strip()
    return WINDOWS_TZ.get(tzid, "America/Phoenix" if theatre.get("state") == "AZ" else "America/Denver")


def vista_movie_id(movie_id):
    return f"HO{int(movie_id):08d}"


def seat_counts(plan):
    """Pure: GetSeatPlan data -> counts. Sold = capacity - open seats."""
    total = int(plan.get("numberOfSeats") or 0)
    open_ = int(plan.get("openSeats") or 0)
    return {"total": total, "sold": max(0, total - open_), "available": open_, "broken": 0, "price_cents": None}


def window_dates(weekend_of):
    fri = datetime.strptime(weekend_of, "%Y-%m-%d")
    return sorted((fri + timedelta(days=o)).strftime("%Y-%m-%d") for o in (-1, 0, 1, 2))


def normalize_performance(p):
    """The day-schedule endpoint carries 'showtimeUtc' ('9/27/2026 5:40:00 PM'),
    'showtime' ('September 27, 2026 10:40 AM') and a ticketing url holding the
    session id; the per-movie endpoint uses ISO fields. Return ISO fields."""
    if "showtimeUTCDate" in p and "sessionId" in p:
        return p
    import re
    utc = datetime.strptime(p["showtimeUtc"], "%m/%d/%Y %I:%M:%S %p")
    local = datetime.strptime(p["showtime"], "%B %d, %Y %I:%M %p")
    m = re.search(r"/session/(\d+)/date/(\d{4}-\d{2}-\d{2})", p.get("url") or p.get("desktopUrl") or "")
    return {**p, "showtimeUTCDate": utc.strftime("%Y-%m-%dT%H:%M:%SZ"), "showtimeDate": local.strftime("%Y-%m-%dT%H:%M:%S"),
            "sessionId": m.group(1) if m else "", "businessDate": m.group(2) if m else local.strftime("%Y-%m-%d"),
            "ticketingUrl": p.get("url", "")}


def pick_performances(day, titles_by_id, target_slugs, now_utc, mode="pre"):
    """Pure: one theatre-day schedule -> [(performance, title)] to read."""
    out = []
    for mv in day.get("movies") or []:
        title = titles_by_id.get(int(mv.get("movieId") or mv.get("id") or 0))
        if not title or slugify_title(title) not in target_slugs:
            continue
        for p in mv.get("performances") or []:
            p = normalize_performance(p)
            if not p.get("sessionId"):
                continue
            start = datetime.fromisoformat(p["showtimeUTCDate"].replace("Z", "+00:00"))
            mins_after = (now_utc - start).total_seconds() / 60
            if mode == "pre" and mins_after >= 0:
                continue
            if mode == "post" and not (0 <= mins_after <= POST_WINDOW_MIN):
                continue
            out.append((p, target_slugs[slugify_title(title)]))
    return out


def build_row(theatre, perf, title, counts, weekend_of, run_id, now_utc, post=False):
    from scraper import snapshot_bucket
    local = datetime.fromisoformat(perf["showtimeDate"])
    start = datetime.fromisoformat(perf["showtimeUTCDate"].replace("Z", "+00:00"))
    occ = round(counts["sold"] * 100.0 / counts["total"], 1) if counts["total"] else 0.0
    tz = theatre_tz(theatre)
    return {
        "weekend_of": weekend_of, "run_id": run_id, "snapshot_time": now_utc.isoformat(),
        "snapshot_bucket": snapshot_bucket(now_utc), "show_date": (perf.get("businessDate") or perf["showtimeDate"])[:10],
        "day_of_week": local.strftime("%A"), "theatre_name": f"Harkins {theatre['name']}",
        "theatre_city": theatre.get("city", ""), "timezone": tz, "movie_title": title,
        "showtime": local.strftime("%H:%M"), "showtime_id": f"{theatre['id']}:{perf['sessionId']}",
        "minutes_until_showtime": max(0, int((start - now_utc).total_seconds() // 60)),
        "auditorium_name": "", "auditorium_type": perf.get("format", ""),
        "total_seats": counts["total"], "reserved_seats": counts["sold"], "available_seats": counts["available"],
        "occupancy_pct": occ, "delta_reserved_since_previous": "",
        "amc_seat_map_url": perf.get("ticketingUrl", ""),
        "notes": f"harkins-api; {'post-show-census; ' if post else ''}sold_out={int(bool(perf.get('soldOut')))}",
        "chain": "HARK", "row_kind": "post-show-census" if post else "harkins-api",
    }


def stored_post_performances(weekend_of, now_utc, path=None, window_min=None):
    """Sessions from stored pre rows that started 0..window minutes ago.
    Harkins' schedule drops started showings, so the post-show (walk-in)
    read must come from session ids stored by pre passes. Seat plans stay
    readable after start (2026-09-27: a 7:35pm showing read 32 sold before
    start, 61 sold 16 min after). Returns [(theatre_id, perf, title)]."""
    import csv
    from zoneinfo import ZoneInfo
    path = Path(path or HARKINS_CSV)
    window_min = POST_WINDOW_MIN if window_min is None else window_min
    if not path.exists():
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
            local = datetime.strptime(f"{r['show_date']} {r['showtime']}", "%Y-%m-%d %H:%M")
            start = local.replace(tzinfo=ZoneInfo(r.get("timezone") or "America/Phoenix")).astimezone(timezone.utc)
            if start > now_utc + timedelta(hours=12):
                start -= timedelta(days=1)          # after-midnight show on the prior business date
            mins = (now_utc - start).total_seconds() / 60
            if not (0 <= mins <= window_min):
                continue
            tid, sess = sid.split(":", 1)
            out.append((int(tid), {"sessionId": sess, "showtimeUTCDate": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                   "showtimeDate": local.strftime("%Y-%m-%dT%H:%M:%S"), "businessDate": r["show_date"],
                                   "format": r.get("auditorium_type", ""), "ticketingUrl": r.get("amc_seat_map_url", "")},
                        r["movie_title"]))
    return out


def collect(weekend_of=None, titles=None, mode="pre", now_utc=None):
    from scraper import opening_weekend_friday, phase1_weekend_anchor, tracked_movie_titles_from_state
    now_utc = now_utc or datetime.now(timezone.utc)
    if not weekend_of:
        weekend_of = (opening_weekend_friday(datetime.now()) if mode == "post"
                      else phase1_weekend_anchor(datetime.now(), full_weekend=True))
    titles = titles or tracked_movie_titles_from_state(weekend_of)
    totals = Counter()
    if not titles:
        print(f"⚠️  No tracked titles for weekend_of={weekend_of}; nothing to collect.")
        return totals
    target = {slugify_title(t): t for t in titles}
    today = now_utc.strftime("%Y-%m-%d")
    dates = [d for d in window_dates(weekend_of)
             if d >= (now_utc - timedelta(days=1)).strftime("%Y-%m-%d")]
    if mode == "post":
        dates = [d for d in dates if d <= today]
    run_id = f"harkins-{now_utc.strftime('%Y-%m-%dT%H:%MZ')}"
    print(f"Harkins collect [{mode}] • weekend_of={weekend_of} • dates={dates} • titles={titles}", flush=True)
    theatres = [t for r in _get(f"{WEB}/theatres")["data"]["regions"] for t in (r.get("theatres") or [])]
    titles_by_id, vista_ids, rows = {}, {}, []
    if mode == "post":
        by_id = {int(t["id"]): t for t in theatres}
        for tid, perf, title in stored_post_performances(weekend_of, now_utc):
            th = by_id.get(tid)
            if not th:
                continue
            totals["matched"] += 1
            try:
                if tid not in vista_ids:
                    info = _get(f"{TIX}/GetTheatreShowtime/harkinsid/{tid}/sessionid/{perf['sessionId']}")
                    vista_ids[tid] = info["data"]["theatre"]["value"][0]["id"]
                plan = _get(f"{TIX}/GetSeatPlan/cinemaid/{vista_ids[tid]}/sessionId/{perf['sessionId']}")["data"]
                counts = seat_counts(plan)
            except Exception:
                totals["errors"] += 1
                continue
            if counts["total"]:
                rows.append(build_row(th, perf, title, counts, weekend_of, run_id, now_utc, post=True))
                totals["captured"] += 1
            time.sleep(SLEEP)
        theatres = []          # the schedule walk below is the pre pass only
    for th in theatres:
        totals["theatres"] += 1
        for d in dates:
            try:
                day = _get(f"{WEB}/theatres/{th['id']}/schedules/{d}/movies")["data"] or {}
            except Exception:
                totals["schedule_errors"] += 1
                continue
            for mv in day.get("movies") or []:
                mid = int(mv.get("movieId") or mv.get("id") or 0)
                if mid and mid not in titles_by_id:
                    try:
                        resp = _get(f"{CMS}/movies/{vista_movie_id(mid)}")
                        titles_by_id[mid] = ((resp.get("data") if isinstance(resp.get("data"), dict) else resp) or {}).get("title", "")
                    except Exception:
                        titles_by_id[mid] = ""
            for perf, title in pick_performances(day, titles_by_id, target, now_utc, mode):
                totals["matched"] += 1
                try:
                    if th["id"] not in vista_ids:
                        info = _get(f"{TIX}/GetTheatreShowtime/harkinsid/{th['id']}/sessionid/{perf['sessionId']}")
                        vista_ids[th["id"]] = info["data"]["theatre"]["value"][0]["id"]
                    plan = _get(f"{TIX}/GetSeatPlan/cinemaid/{vista_ids[th['id']]}/sessionId/{perf['sessionId']}")["data"]
                    counts = seat_counts(plan)
                except Exception:
                    totals["errors"] += 1
                    continue
                if not counts["total"]:
                    totals["empty"] += 1
                    continue
                rows.append(build_row(th, perf, title, counts, weekend_of, run_id, now_utc, post=(mode == "post")))
                totals["captured"] += 1
                time.sleep(SLEEP)
            time.sleep(SLEEP)
    written, deduped = append_unique_fandango_rows(rows, csv_path=HARKINS_CSV)
    totals["written"], totals["deduped"] = written, deduped
    print(f"=== Harkins collect summary [{mode}] === " + " ".join(f"{k}={v}" for k, v in sorted(totals.items())), flush=True)
    return totals


def main():
    mode = "post" if os.environ.get("HARKINS_MODE") == "post" else "pre"
    t = collect(mode=mode)
    if t.get("matched", 0) and not t.get("captured", 0):
        print("❌ Harkins: every seat read failed — failing loudly.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
