#!/usr/bin/env python3
"""Auto-fetch Rotten Tomatoes audience (word-of-mouth) + critic scores for the
films being predicted this weekend, and append them to data/reviews.csv (the
input to predict.py's review/WOM layer).

Reuses the proven RT-scrape helpers from import_audience_scores.py. Each run
writes a dated snapshot per film (as_of_date = today, UTC); load_reviews_data
keeps the latest per movie and is leak-safe via through_date in replay. Films
not found on RT (no page / no score yet) are skipped → the review layer stays
neutral for them.

Run:  python3 scripts/import_reviews.py            # current weekend's films
      python3 scripts/import_reviews.py --movies "Supergirl" "Jackass: Best and Last"
      python3 scripts/import_reviews.py --dry-run   # print, don't write
"""
import argparse
import csv
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)               # scripts/  (import_audience_scores)
sys.path.insert(0, os.path.dirname(HERE))  # box-office-tracker/ (predict)

import predict as P  # noqa: E402
import import_audience_scores as RT  # noqa: E402

REVIEWS_FIELDS = ["weekend_of", "as_of_date", "movie_title", "rt_audience_score",
                  "rt_critic_score", "imdb_rating", "source", "notes"]


def _rt_retry(fn, *args, tries=3, base_sleep=10):
    """RT rate-limits CI IPs in bursts (403s all weekend 2026-07-10); one or two
    spaced retries usually clear it. Best effort — the caller treats a final
    failure as 'no RT this run' and IMDb (the primary signal) carries on."""
    import time
    last = None
    for attempt in range(tries):
        try:
            return fn(*args)
        except Exception as exc:  # noqa: BLE001
            last = exc
            if attempt < tries - 1:
                time.sleep(base_sleep * (attempt + 1))
    raise last


def fetch_rt_scores(title, release_year):
    """Return {rt_audience_score, rt_critic_score, rt_url} or None if not found."""
    candidate = RT.choose_rt_candidate(
        title, release_year, _rt_retry(RT.rt_search_candidates, title))
    if not candidate:
        return None
    scorecard = _rt_retry(RT.rt_scorecard, candidate["url"])

    def _score(block_keys):
        for k in block_keys:
            block = scorecard.get(k) or {}
            s = str(block.get("score") or "").strip()
            if s:
                return s
        # fall back to the overlay block RT sometimes uses
        overlay = scorecard.get("overlay") or {}
        for k in ("audienceAll", "criticsAll"):
            s = str((overlay.get(k) or {}).get("score") or "").strip()
            if s and k.startswith(block_keys[0][:4].lower().replace("audi", "audi")):
                return s
        return ""

    audience = str((scorecard.get("audienceScore") or {}).get("score") or "").strip()
    if not audience:
        audience = str(((scorecard.get("overlay") or {}).get("audienceAll") or {}).get("score") or "").strip()
    critic = str((scorecard.get("criticsScore") or {}).get("score") or "").strip()
    if not audience and not critic:
        return None
    return {"rt_audience_score": audience, "rt_critic_score": critic, "rt_url": candidate["url"]}


def fetch_imdb_rating(title, release_year, ratings):
    """Return {imdb_rating, imdb_votes, imdb_url} or None (best effort)."""
    if not ratings:
        return None
    try:
        rating, votes, url = RT.imdb_reference(title, release_year, ratings)
        return {"imdb_rating": rating, "imdb_votes": votes, "imdb_url": url}
    except Exception:  # noqa: BLE001
        return None


def current_weekend_and_films(args):
    weekend = args.weekend or P._current_weekend_friday()
    if args.movies:
        return weekend, list(args.movies)
    seat = P.load_seat_data(weekend_of=weekend)
    return weekend, sorted(seat.keys())


def append_reviews(rows, csv_path):
    """Append rows; create with header if needed. Dedupe identical (movie,as_of)."""
    existing = set()
    if os.path.exists(csv_path):
        with open(csv_path, newline="") as f:
            for r in csv.DictReader(f):
                existing.add((r.get("movie_title", ""), r.get("as_of_date", "")))
    new = [r for r in rows if (r["movie_title"], r["as_of_date"]) not in existing]
    write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
    with open(csv_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REVIEWS_FIELDS)
        if write_header:
            w.writeheader()
        w.writerows(new)
    return len(new)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weekend", help="weekend_of (YYYY-MM-DD); default = current")
    ap.add_argument("--movies", nargs="*", help="explicit film titles to fetch")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    weekend, films = current_weekend_and_films(args)
    if not films:
        print("No films to fetch (no seat data and no --movies).")
        return 0
    year = int(weekend[:4])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Fetching review scores (IMDb primary, RT fallback) for weekend {weekend}: {films}")

    imdb_ratings = {}
    try:
        imdb_ratings = RT.load_imdb_ratings()
    except Exception as e:  # noqa: BLE001
        print(f"  (IMDb dataset unavailable: {str(e)[:60]} — IMDb scores skipped)")

    rows = []
    for title in films:
        try:
            scores = fetch_rt_scores(title, year)
        except Exception as e:  # noqa: BLE001
            scores = None
            print(f"  {title}: RT error {str(e)[:60]}")
        imdb = fetch_imdb_rating(title, year, imdb_ratings)
        if not scores and not imdb:
            print(f"  {title}: no IMDb or RT match — skipped (review layer neutral)")
            continue
        rt_aud = (scores or {}).get("rt_audience_score", "")
        rt_crit = (scores or {}).get("rt_critic_score", "")
        imdb_rating = (imdb or {}).get("imdb_rating", "")
        print(f"  {title}: IMDb={imdb_rating or '-'}  RT audience={rt_aud or '-'} critic={rt_crit or '-'}")
        rows.append({
            "weekend_of": weekend, "as_of_date": today, "movie_title": title,
            "rt_audience_score": rt_aud, "rt_critic_score": rt_crit,
            "imdb_rating": imdb_rating,
            "source": "imdb+rottentomatoes",
            "notes": (imdb or {}).get("imdb_url", "") or (scores or {}).get("rt_url", ""),
        })

    if args.dry_run:
        print(f"\n[dry-run] would write {len(rows)} row(s) to {P.REVIEWS_CSV}")
        return 0
    if rows:
        n = append_reviews(rows, P.REVIEWS_CSV)
        print(f"\nwrote {n} new review row(s) → {P.REVIEWS_CSV}")
    else:
        print("\nNo scores found — reviews.csv unchanged (review layer stays neutral).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
