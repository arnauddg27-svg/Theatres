#!/usr/bin/env python3
"""Seed the tracked slate from the Box Office Mojo release calendar.

Until 2026-10-18 the pipeline tracked only films with a Polymarket market.
Sense and Sensibility's market appeared on Saturday Oct 17, so Thursday and
most of Friday were never read on any chain, and a wide release Polymarket
never lists is never counted at all. This script reads BOM's calendar page
for an opening weekend, keeps the Wide releases dated Wednesday-Friday of
that weekend, and writes data/release-calendar.json; scraper.py merges those
titles into the collection slate (see calendar_titles_for_weekend).

    python3 scripts/release_calendar.py --weekend 2026-10-23 --write
    python3 scripts/release_calendar.py --weekend 2026-10-23           # print only

Advisory by design: a fetch failure leaves the previous file in place and
exits 0 (Polymarket seeding still works), but prints a ::warning::.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CALENDAR_JSON = os.path.join(DATA_DIR, "release-calendar.json")
BOM_CALENDAR_URL = "https://www.boxofficemojo.com/calendar/{date}/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
MAX_TITLES = 8
# Re-releases and event cinema are not opening weekends the model forecasts.
SKIP_PATTERNS = re.compile(
    r"\b(re-?release|anniversary|\d+th|fathom|concert|in concert|"
    r"restoration|sing-?along|ghibli fest|encore)\b|\blive!", re.I)


def _key(title):
    text = re.sub(r"[^a-z0-9 ]", " ", (title or "").lower())
    text = re.sub(r"^(the|a|an)\s+", "", text.strip())
    return re.sub(r"\s+", " ", text).strip()


def earlier_tracked_titles(weekend_of, metadata_csv=None):
    """Title keys whose metadata weekend_of precedes `weekend_of`."""
    import csv
    path = metadata_csv or os.path.join(DATA_DIR, "movie-metadata.csv")
    keys = set()
    try:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                w = (row.get("weekend_of") or "").strip()
                if w and w < weekend_of:
                    keys.add(_key(row.get("movie")))
    except OSError:
        pass
    return keys


def opening_weekend_friday(ref):
    days_ahead = (4 - ref.weekday()) % 7
    return ref + timedelta(days=days_ahead)


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def _clean(fragment):
    text = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", text).strip()


def _header_date(text):
    """'October 23, 2026' or BOM's live 'Fri Oct 23, 2026' -> 'October 23, 2026'."""
    text = re.sub(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+", "", text.strip())
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%B %-d, %Y")
        except ValueError:
            pass
    return None


def calendar_start_date(weekend_of):
    """BOM's calendar page starts AT the requested date, so ask for the
    Wednesday or a Wed/Thu opener never appears on the page."""
    return (datetime.strptime(weekend_of, "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")


def parse_calendar(page, weekend_of):
    """[{title, distributor, date, scale, genres}] for Wide releases dated
    Wed-Fri of `weekend_of` (Thursday/Wednesday openers belong to the weekend)."""
    friday = datetime.strptime(weekend_of, "%Y-%m-%d")
    window = {(friday - timedelta(days=d)).strftime("%B %-d, %Y") for d in (0, 1, 2)}
    out = []
    current_date = None
    # Walk the rows in order: a header row carrying a date (<th>October 23,
    # 2026</th>) opens that date's block; the rows that follow are its releases.
    for chunk in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        header_dates = [_clean(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", chunk, re.S)]
        header_dates = [d for d in (_header_date(h) for h in header_dates) if d]
        if header_dates:
            current_date = header_dates[0]
            continue
        if current_date not in window:
            continue
        cells = [_clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", chunk, re.S)]
        if len(cells) < 3:
            continue
        release, distributor, scale = cells[0], cells[1], cells[2]
        if scale.strip().lower() != "wide":
            continue
        # "Title Genre Genre With: cast ... 1 hr 48 min Cast, Crew, and Company Info"
        title_match = re.match(r"^(.*?)(?:\s+(?:Action|Adventure|Animation|Biography|Comedy|Crime|"
                               r"Documentary|Drama|Family|Fantasy|History|Horror|Music|Musical|Mystery|"
                               r"Romance|Sci-Fi|Sport|Thriller|War|Western)\b.*)?(?:\s+With:.*)?$",
                               release)
        title = (title_match.group(1) if title_match else release).strip()
        title = re.sub(r"\s+Cast, Crew, and Company Info$", "", title).strip()
        if not title or SKIP_PATTERNS.search(title) or SKIP_PATTERNS.search(release):
            continue
        genres = re.findall(r"\b(Action|Adventure|Animation|Biography|Comedy|Crime|Documentary|Drama|"
                            r"Family|Fantasy|History|Horror|Music|Musical|Mystery|Romance|Sci-Fi|Sport|"
                            r"Thriller|War|Western)\b", release.split("With:")[0])
        out.append({"title": title, "distributor": distributor, "date": current_date,
                    "scale": scale, "genres": sorted(set(genres))})
    # Expansions are not openings: a title already tracked for an EARLIER
    # weekend (You Can See Everything opened Oct 16 on 855 screens and shows
    # as "Wide" again on Oct 23) would be re-forecast as an opener and its
    # second weekend graded as an opening. Skip anything metadata already
    # dates before this weekend.
    earlier = earlier_tracked_titles(weekend_of)
    out = [r for r in out if _key(r["title"]) not in earlier]
    # Majors first so a cap never drops the weekend's biggest opener.
    majors = ("warner", "disney", "universal", "sony", "paramount", "amazon", "lionsgate",
              "20th", "searchlight", "focus", "a24", "neon", "angel", "columbia", "gkids")
    out.sort(key=lambda r: (0 if any(m in r["distributor"].lower() for m in majors) else 1, r["title"]))
    return out[:MAX_TITLES]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weekend", help="opening Friday (YYYY-MM-DD); default: next Friday")
    ap.add_argument("--write", action="store_true", help=f"write {CALENDAR_JSON}")
    args = ap.parse_args(argv)
    weekend = args.weekend or opening_weekend_friday(datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    try:
        page = fetch(BOM_CALENDAR_URL.format(date=calendar_start_date(weekend)))
        titles = parse_calendar(page, weekend)
    except Exception as exc:  # advisory
        print(f"::warning::release calendar fetch failed for {weekend}: {type(exc).__name__}: {exc}")
        return 0
    print(f"release calendar {weekend}: {len(titles)} wide release(s)")
    for t in titles:
        print(f"  {t['title']} — {t['distributor']} ({t['date']}; {', '.join(t['genres'])})")
    if args.write:
        payload = {"weekend_of": weekend, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "source": BOM_CALENDAR_URL.format(date=calendar_start_date(weekend)), "titles": titles}
        with open(CALENDAR_JSON, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"wrote {CALENDAR_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
