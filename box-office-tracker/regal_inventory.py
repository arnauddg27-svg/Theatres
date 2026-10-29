#!/usr/bin/env python3
"""Regal showing inventory — every Regal showing of the tracked films, per day.

Regal's own theatre pages (regmovies.com/theatres/<slug>-<code>) are server-
rendered Next.js: `__NEXT_DATA__.props.pageProps.showtimes` lists TODAY's
complete showtime inventory per film (PerformanceId, local start, auditorium,
format attributes), and `fullTheatreData` carries the whole 402-theatre
directory. Probed 2026-10-27: one plain HTTPS request per theatre, ~110 KB on
the wire, no login, no challenge. Only today's date is server-rendered (other
dates load client-side from an API that is Cloudflare-gated — not used), so
the lane runs once each show-day morning (12:10Z = 8am ET / 5am PT, every
theatre still on its local "today").

Why: Fandango's seat-map throttle caps Regal at ~700 seat reads a day, ~2% of
its showings. The census slots (fandango_collect order="census") read a random
sample of showings within an hour of start; this inventory is the denominator
that scales that sample to the whole chain (chain_census.regal_day_dollars).

Polite by construction: REGAL_INVENTORY_WORKERS (3) threads, a small delay,
REGAL_MAX_MB byte ceiling through the residential proxy (REGAL_HTTP_PROXY_URL;
direct first — GitHub's addresses get a 403). Through the rotating pool a
challenge page is a bad exit draw (~40% of draws on the 2026-10-27 test, the
same pattern as the AMC listings lane), so a walled page is re-requested on a
fresh tunnel up to REGAL_WALL_RETRIES times; the run STOPS after
REGAL_WALL_STOP consecutive theatres that stayed walled. A challenge is never
solved.

Rows (Fandango superset schema, chain=REGL, row_kind=regal-inventory, seat
fields blank) go to data/regal-showings.csv; one row per performance.

    python3 regal_inventory.py [--max-theatres N] [--dry-run]
"""
import argparse
import csv
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fandango_collect import FANDANGO_PRE_RESERVATION_FIELDS, slugify_title  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"
OUT_CSV = DATA_DIR / "regal-showings.csv"
BASE = "https://www.regmovies.com"
SEED_THEATRE = "regal-aviation-mall-1731"
WORKERS = int(os.environ.get("REGAL_INVENTORY_WORKERS") or 3)
MAX_MB = float(os.environ.get("REGAL_MAX_MB") or 120)
WALL_STOP = int(os.environ.get("REGAL_WALL_STOP") or 5)
WALL_RETRIES = int(os.environ.get("REGAL_WALL_RETRIES") or 2)
DEADLINE_SEC = int(os.environ.get("REGAL_DEADLINE_SEC") or 1500)
NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)


def next_data(html):
    m = NEXT_DATA_RE.search(html or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def looks_walled(status, html):
    low = (html or "")[:20000].lower()
    return status in (403, 429, 503) or "just a moment" in low or "cf-chl" in low or "one more step" in low


def title_key(title):
    return slugify_title(title)


def match_title(regal_title, targets):
    """Tracked title for a Regal film title, else None. Exact slug first,
    then the Regal title starting with the tracked slug as whole words
    ('clayface-the-imax-experience' -> Clayface)."""
    k = title_key(regal_title)
    if k in targets:
        return targets[k]
    for tk, t in targets.items():
        if k.startswith(tk + "-"):
            return t
    return None


def performance_rows(page_props, theatre, targets, weekend_dates, weekend_of, collected_at):
    """Pure: inventory rows for one theatre page's server-rendered showtimes."""
    rows = []
    for day in page_props.get("showtimes") or []:
        show_date = str(day.get("AdvertiseShowDate") or "")[:10]
        if show_date not in weekend_dates:
            continue
        for film in day.get("Film") or []:
            title = match_title(film.get("Title"), targets)
            if not title:
                continue
            for perf in film.get("Performances") or []:
                local = str(perf.get("CalendarShowTime") or "")
                attrs = [str(a) for a in (perf.get("PerformanceAttributes") or [])]
                row = {k: "" for k in FANDANGO_PRE_RESERVATION_FIELDS}
                row.update({
                    "weekend_of": weekend_of, "run_id": f"regal-inventory-{collected_at[:13]}",
                    "snapshot_time": collected_at, "snapshot_bucket": show_date,
                    "show_date": show_date,
                    "day_of_week": datetime.strptime(show_date, "%Y-%m-%d").strftime("%A"),
                    "theatre_name": theatre.get("name", ""), "theatre_city": theatre.get("city", ""),
                    "timezone": theatre.get("state", ""),
                    "movie_title": title, "showtime": local[11:16],
                    "showtime_id": str(perf.get("PerformanceId", "")),
                    "auditorium_name": str(perf.get("Auditorium", "")),
                    "auditorium_type": "|".join(attrs),
                    "chain": "REGL", "row_kind": "regal-inventory",
                    "notes": (f"regal-inventory; theatre_code={theatre.get('theatre_code', '')}; "
                              f"utc={perf.get('UtcShowTime', '')}; stop_sales={int(bool(perf.get('StopSales')))}"),
                })
                rows.append(row)
    return rows


def weekend_window(now=None):
    from scraper import opening_weekend_friday
    now = now or datetime.now()
    weekend_of = opening_weekend_friday(now)
    fri = datetime.strptime(weekend_of, "%Y-%m-%d")
    dates = {(fri + timedelta(days=o)).strftime("%Y-%m-%d") for o in (-1, 0, 1, 2)}
    return weekend_of, dates


class Fetcher:
    def __init__(self):
        import seat_fetch_http as sfh
        self.sfh = sfh
        self.session = sfh.make_session()
        self.proxy = (os.environ.get("REGAL_HTTP_PROXY_URL") or "").strip() or None
        self.bytes = 0
        self.lock = threading.Lock()

    def fresh_tunnel(self):
        try:
            self.sfh.drop_thread_connection(self.session)
        except Exception:
            pass

    def get(self, url):
        kw = {"stream": True, "timeout": 30,
              "headers": {"Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"}}
        if self.proxy:
            kw["proxies"] = {"http": self.proxy, "https": self.proxy}
        r = self.session.get(url, **kw)
        inf = self.sfh._Inflater(r.headers.get("content-encoding", ""))
        raw, out = 0, bytearray()
        for ch in r.iter_content(chunk_size=32768):
            raw += len(ch)
            out += inf.feed(ch)
        r.close()
        with self.lock:
            self.bytes += raw
        return r.status_code, bytes(out).decode("utf-8", "replace")


def collect(max_theatres=0, dry_run=False):
    from scraper import tracked_movie_titles_from_state
    weekend_of, dates = weekend_window()
    titles = tracked_movie_titles_from_state(weekend_of)
    test = bool(os.environ.get("REGAL_TEST_TODAY"))
    if test:
        # Ad-hoc yield test: today's showings of last weekend's films (still
        # playing mid-week), written to a throwaway file, never canonical.
        from zoneinfo import ZoneInfo
        dates = {datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")}
        titles = sorted(set(titles) | set(os.environ.get("REGAL_TEST_TITLES", "").split("|")) - {""})
        dry_run = True
    if not titles:
        print(f"⚠️  No tracked titles for weekend_of={weekend_of}; nothing to collect.")
        return {"theatres": 0, "rows": 0}
    targets = {title_key(t): t for t in titles}
    f = Fetcher()
    proxy, f.proxy = f.proxy, None      # direct first: the proxy is metered
    status, html = f.get(f"{BASE}/theatres/{SEED_THEATRE}")
    if looks_walled(status, html) and proxy:
        print(f"  direct egress refused (status {status}); using the residential proxy", flush=True)
        f.proxy = proxy
        # The seed page is one draw from a rotating pool, ~40% of which are
        # walled: retry it on fresh exits like every other page (2026-10-29:
        # the first scheduled run died here on a single walled draw).
        for attempt in range(1 + 2 * WALL_RETRIES):
            status, html = f.get(f"{BASE}/theatres/{SEED_THEATRE}")
            if not looks_walled(status, html):
                break
            f.fresh_tunnel()
    nd = next_data(html)
    if looks_walled(status, html) or not nd:
        print(f"::error::Regal seed page unreadable (status {status}); stopping — never solving a wall")
        return {"theatres": 0, "rows": 0, "walled": True}
    directory = nd["props"]["pageProps"].get("fullTheatreData") or []
    theatres = [t for t in directory if t.get("path_name")]
    random.shuffle(theatres)
    if max_theatres:
        theatres = theatres[:max_theatres]
    collected_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Regal inventory • weekend_of={weekend_of} • dates={sorted(dates)} • {len(theatres)} theatres "
          f"• titles={titles} • proxy={'ON' if f.proxy else 'off'} • ceiling {MAX_MB:.0f} MB", flush=True)
    stop = threading.Event()
    walls = {"streak": 0, "total": 0, "draws": 0}
    totals = {"theatres": 0, "errors": 0, "rows": 0, "skipped_budget": 0}
    rows, lock = [], threading.Lock()
    deadline = time.monotonic() + DEADLINE_SEC

    def one(t):
        if stop.is_set() or time.monotonic() > deadline or f.bytes > MAX_MB * 1048576:
            with lock:
                totals["skipped_budget"] += 1
            return
        status, page = None, ""
        for attempt in range(1 + (WALL_RETRIES if f.proxy else 0)):
            time.sleep(random.uniform(0.3, 0.9))
            try:
                status, page = f.get(f"{BASE}/theatres/{t['path_name']}")
            except Exception as exc:
                with lock:
                    totals["errors"] += 1
                print(f"  {t['path_name']}: {type(exc).__name__}", flush=True)
                return
            if not looks_walled(status, page):
                break
            with lock:
                walls["draws"] += 1
            f.fresh_tunnel()      # next draw leaves from another exit
        if looks_walled(status, page):
            with lock:
                walls["streak"] += 1
                walls["total"] += 1
                if walls["streak"] >= WALL_STOP:
                    stop.set()
                    print(f"⛔ {WALL_STOP} walled pages in a row — stopping (walls are never solved)", flush=True)
            return
        data = next_data(page)
        if not data:
            with lock:
                totals["errors"] += 1
            return
        got = performance_rows(data["props"]["pageProps"], t, targets, dates, weekend_of, collected_at)
        with lock:
            walls["streak"] = 0
            totals["theatres"] += 1
            rows.extend(got)

    with ThreadPoolExecutor(max_workers=max(1, WORKERS)) as ex:
        list(ex.map(one, theatres))
    totals["rows"] = len(rows)
    totals["walls"] = walls["total"]
    totals["walled_draws"] = walls["draws"]
    totals["mb"] = round(f.bytes / 1048576, 1)
    by = {}
    for r in rows:
        by[(r["movie_title"], r["show_date"])] = by.get((r["movie_title"], r["show_date"]), 0) + 1
    print(f"Regal inventory done: {totals}  per film-day: " +
          ", ".join(f"{m} {d[5:]} {n}" for (m, d), n in sorted(by.items())), flush=True)
    if not dry_run and rows:
        new = not OUT_CSV.exists() or OUT_CSV.stat().st_size == 0
        with open(OUT_CSV, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FANDANGO_PRE_RESERVATION_FIELDS)
            if new:
                w.writeheader()
            w.writerows(rows)
    if totals["theatres"] >= 50 and not rows:
        print("::warning::Regal inventory read 50+ theatres and matched no tracked showing "
              "(title mismatch or the films are not playing today)")
    return totals


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-theatres", type=int, default=int(os.environ.get("REGAL_MAX_THEATRES") or 0))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    totals = collect(args.max_theatres, args.dry_run)
    # Loud failure when the lane is dark: the seed page walled, or most pages did.
    if totals.get("walled") or (totals.get("walls", 0) >= WALL_STOP and totals.get("theatres", 0) < 50):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
