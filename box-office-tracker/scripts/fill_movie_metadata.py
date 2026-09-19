#!/usr/bin/env python3
"""Fill data/movie-metadata.csv from Box Office Mojo for tracked films.

Half the recorded films had no metadata row (14/34 on 2026-09-19), so the
footprint factor, audience gates and genre lift ran on defaults. This looks
each film up on Box Office Mojo (search -> title -> current release page),
reads MPAA rating, genres and widest release, maps genres onto the model's
controlled vocabulary, and writes/completes rows. Never overwrites a value
someone typed; only fills blanks. Review the printed rows.

  python3 scripts/fill_movie_metadata.py --from-history [--write]
  python3 scripts/fill_movie_metadata.py "Resident Evil" 2026-09-18 [--write]
"""
import csv, html, json, os, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "movie-metadata.csv"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
FIELDS = ["movie", "weekend_of", "genre", "audience_type", "franchise_type", "rating", "notes",
          "imdb_rating", "imdb_votes", "rt_audience_score", "rt_audience_score_type",
          "national_theatre_count", "amc_market_share_override"]

# Box Office Mojo genre -> (model genre, default audience_type). First match in
# the film's genre list wins; order below is the priority.
GENRE_MAP = [
    ("Horror", ("horror", "horror_fan")),
    ("Animation", ("animation", "broad_family")),
    ("Superhero", ("superhero", "fan_driven")),
    ("Musical", ("music_biopic", "female_skewing")),
    ("Music", ("music_biopic", "adult_drama")),
    ("Biography", ("drama", "adult_drama")),
    ("Comedy", ("comedy", "broad_legacy")),
    ("Sci-Fi", ("action", "fan_driven")),
    ("Action", ("action", "young_male")),
    ("Adventure", ("action", "fan_driven")),
    ("Thriller", ("drama", "adult_drama")),
    ("Drama", ("drama", "adult_drama")),
    ("Romance", ("drama", "female_skewing")),
    ("Fantasy", ("action", "fan_driven")),
]


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def _strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def bom_lookup(title, year_hint=None):
    """(rating, genres, widest_release, bom_title, release_url) or None."""
    base_title = re.sub(r"\s*\((19|20)\d\d\)\s*$", "", title).strip()   # "Moana (2026)" -> "Moana"
    q = urllib.parse.quote(base_title)
    page = _get(f"https://www.boxofficemojo.com/search/?q={q}")
    # text link followed by the year span: <a href="/title/tt…">Title</a><span> (2026)</span>
    hits = re.findall(r'href="(/title/tt\d+/)[^"]*"[^>]*>([^<]{1,120})</a>\s*<span[^>]*>\s*\((\d{4})\)', page)
    want = re.sub(r"[^a-z0-9]", "", base_title.lower())
    pick = None
    for href, name, yr in hits:
        if re.sub(r"[^a-z0-9]", "", _strip(name).lower()) != want:
            continue
        if year_hint and yr != str(year_hint):
            continue
        pick = href; break
    if not pick:
        return None                       # exact title (and year) or nothing: no guessing
    tpage = _get("https://www.boxofficemojo.com" + pick)
    rel = re.search(r'href="(/release/rl\d+/)', tpage)
    rpage = _get("https://www.boxofficemojo.com" + rel.group(1)) if rel else tpage
    def field(name):
        m = re.search(name + r"</span><span[^>]*>(.*?)</span>", rpage, re.S)
        return _strip(m.group(1)) if m else ""
    rating = field("MPAA")
    genres = [g.strip() for g in re.split(r"\s{2,}|\n", field("Genres")) if g.strip()]
    widest = re.sub(r"[^\d]", "", field("Widest Release") or "")
    bom_title = _strip(re.search(r"<title>(.*?)</title>", tpage, re.S).group(1)).split(" - ")[0] if "<title>" in tpage else title
    return {"rating": rating if rating in ("G", "PG", "PG-13", "R", "NC-17") else "",
            "genres": genres, "widest": int(widest) if widest else None,
            "bom_title": bom_title, "url": "https://www.boxofficemojo.com" + (rel.group(1) if rel else pick)}


def map_genre(genres):
    for key, out in GENRE_MAP:
        if any(key.lower() in g.lower() for g in genres):
            return out
    return ("", "")


def load_rows():
    if not META.exists():
        return []
    with open(META, newline="") as f:
        return list(csv.DictReader(f))


def history_films():
    cal = json.loads((ROOT / "data" / "calibration.json").read_text())
    return sorted({(h["movie"], h.get("weekend_of", "")) for h in cal.get("history", [])})


def fill(rows, movie, weekend_of, info):
    key = movie.strip().lower()
    row = next((r for r in rows if r["movie"].strip().lower() == key), None)
    created = row is None
    if created:
        row = {k: "" for k in FIELDS}; row["movie"] = movie; row["weekend_of"] = weekend_of
        rows.append(row)
    genre, aud = map_genre(info["genres"]) if info else ("", "")
    changes = []
    for k, v in (("genre", genre), ("audience_type", aud), ("rating", info["rating"] if info else ""),
                 ("national_theatre_count", str(info["widest"]) if info and info["widest"] else "")):
        if v and not (row.get(k) or "").strip():
            row[k] = v; changes.append(f"{k}={v}")
    if changes and info:
        tag = f"BOM auto-fill {time.strftime('%Y-%m-%d')}: {', '.join(info['genres'][:3])} ({info['url']})"
        row["notes"] = (row.get("notes") or "").strip()
        row["notes"] = f"{row['notes']}; {tag}" if row["notes"] else tag
    return created, changes


def main(argv):
    write = "--write" in argv
    args = [a for a in argv if not a.startswith("--")]
    rows = load_rows()
    targets = history_films() if "--from-history" in argv else ([(args[0], args[1] if len(args) > 1 else "")] if args else [])
    if not targets:
        print(__doc__); return 1
    for movie, weekend_of in targets:
        existing = next((r for r in rows if r["movie"].strip().lower() == movie.strip().lower()), None)
        if existing and all((existing.get(k) or "").strip() for k in ("genre", "audience_type", "rating", "national_theatre_count")):
            continue
        try:
            info = bom_lookup(movie, (weekend_of or "")[:4] or None)
        except Exception as e:
            print(f"  {movie}: lookup failed ({type(e).__name__})"); info = None
        created, changes = fill(rows, movie, weekend_of, info)
        print(f"  {movie:32s} {'NEW ' if created else 'fill'} {', '.join(changes) or '(nothing to fill)'}"
              f"{'  <- BOM: ' + info['bom_title'] + ' ' + '/'.join(info['genres'][:3]) if info else '  <- not found'}")
        time.sleep(1.0)
    if write:
        with open(META, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
            for r in rows: w.writerow({k: r.get(k, "") for k in FIELDS})
        print(f"wrote {len(rows)} rows -> {META}")
    else:
        print("(dry run; add --write to save)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
