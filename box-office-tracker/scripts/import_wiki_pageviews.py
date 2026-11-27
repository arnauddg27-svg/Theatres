#!/usr/bin/env python3
"""Wikipedia release-week pageviews as a leak-free word-of-mouth / anticipation
signal for the box-office model.

Why Wikipedia: the Wikimedia pageviews API is official, free, unauthenticated,
and has full daily history back to 2015 — so unlike Twitter/Reddit/Trends it can
be BACKFILLED across the whole comp library and therefore *calibrated* (the same
discipline as the reviews layer). Release-week article traffic is a well-
established opening-weekend predictor.

Leak-free window: the Monday-Thursday immediately before the opening Friday.
  * Live (weekend_of known): window = [Fri-4, Fri-1].
  * Backfill: the opening Friday is read from the comp row's own sources (the
    weekend in its Box Office Mojo daily table that has the row's grosses, else
    the dated the-numbers chart, else the page's release date), then the
    Mon-Thu before it. It was located from the year's biggest pageview spike
    until 2026-11-27, which is the awards or streaming date for many films.

Article: the page of the Wikidata item holding the film's IMDb id; without an
id, a search hit Wikidata confirms as a film of that title and year
(wiki_film_article.py). No article is better than another film's.

Usage:
  python3 scripts/import_wiki_pageviews.py --backfill   # fill historical-comps.csv
  python3 scripts/import_wiki_pageviews.py              # current weekend -> social-signals.csv
  python3 scripts/import_wiki_pageviews.py --movies "Supergirl" --weekend 2026-06-26
  python3 scripts/import_wiki_pageviews.py --dry-run
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import predict as P  # noqa: E402
import bom_release_page as BOM  # noqa: E402
import wiki_film_article as WA  # noqa: E402

# Wikimedia asks automated clients for a contact. It is read from the
# environment (set WIKIMEDIA_CONTACT in the workflow) instead of being
# hard-coded into every request this script sends.
_CONTACT = (os.environ.get("WIKIMEDIA_CONTACT") or "").strip()
UA = "box-office-wom/0.2 (research)" + (f" contact {_CONTACT}" if _CONTACT else "")
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
MAX_REDIRECTS = 25
# Four pre-release days of a wide release never draw this few readers; a lower
# count means the traffic sits under a title that can no longer be traced.
MIN_PLAUSIBLE_VIEWS = 1000
COMPS_CSV = os.path.join(P.DATA_DIR, "historical-comps.csv")
CACHE_PATH = os.path.join(P.DATA_DIR, ".wiki-pageviews-cache.json")
PAGEVIEWS = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
             "en.wikipedia.org/all-access/all-agents/{article}/daily/{start}/{end}")
SOCIAL_FIELDS = ["weekend_of", "as_of_date", "movie_title", "platform", "source",
                 "mentions", "engagement", "views", "social_media_universe_m",
                 "likes", "comments", "shares", "positive_mentions",
                 "negative_mentions", "neutral_mentions", "sentiment_score",
                 "buzz_score", "notes"]


def _get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            last = e
            code = getattr(e, "code", None)
            if code == 404:
                return None
            if code == 429:
                # Rate-limited: wait as told (the pageviews API throttled the
                # 2026-11-27 backfill once redirects were read too).
                try:
                    wait = float((getattr(e, "headers", None) or {}).get("Retry-After") or 0)
                except (TypeError, ValueError):
                    wait = 0
                time.sleep(min(max(wait, 5.0 * (i + 1)), 60.0))
                continue
            time.sleep(0.6 * (i + 1))
    raise last


def _norm(s):
    return "".join(c for c in (s or "").lower() if c.isalnum())


def search_query(title, year):
    """Plain-word search text: punctuation is an operator to the search API
    ("-Kimetsu" EXCLUDES the word, which sent Demon Slayer to "Inuyasha").
    Apostrophes stay: "Don t Worry Darling" finds nothing."""
    words = "".join(c if (c.isalnum() or c in "'’") else " " for c in (title or ""))
    return " ".join(f"{words} {year} film".split())


def article_titles(article):
    """The article plus the redirects that are earlier names of the same page.

    Pageviews are counted under the title a page had on the day. A film's
    article is often moved after release ("Black Bag (film)" -> "Black Bag",
    "Horrorscope (film)" -> "Tarot (2024 American film)"), so reading only
    today's title loses the pre-release week (Black Bag: 16,635 views against
    117,517 with its redirects)."""
    return redirect_titles([article]).get(article) or [article]   # live path: best effort


def former_title(article, redirect):
    """True when a redirect looks like a name the page itself once had: the
    bare title, or any "(... film)" title. Spelling and nickname redirects
    ("TGM", "Sonic 2 Movie") never held the page; asking for their views only
    returns 404s, and a client that draws many 404s is throttled to one
    request every ~20 s (2026-11-27: 80 s per film)."""
    if "(" in redirect:
        return "film" in redirect.split("(", 1)[1].lower()
    return _norm(redirect) == _norm(article.split("(")[0]) and redirect != article


def redirect_titles(articles, batch=20, strict=False):
    """{article: [article, *redirects]} read `batch` articles per request.

    One request per film was throttled to about a minute each on 2026-11-27;
    the API takes many titles at once and pages the answer."""
    out = {a: [a] for a in articles if a}
    names = list(out)
    for start in range(0, len(names), batch):
        chunk, cont = names[start:start + batch], {}
        for _ in range(20):                       # follow rdcontinue, bounded
            url = ("https://en.wikipedia.org/w/api.php?action=query&format=json&prop=redirects"
                   "&rdnamespace=0&rdlimit=500&titles=" + urllib.parse.quote("|".join(chunk))
                   + "".join(f"&{k}={urllib.parse.quote(str(v))}" for k, v in cont.items()))
            try:
                data = _get(url, tries=6) or {}
            except Exception:  # noqa: BLE001
                # Unknown redirects: the caller must not count these articles'
                # views as complete (strict=True) — a silent undercount is the
                # fault this lookup exists to remove.
                for name in chunk:
                    out[name] = None if strict else out[name]
                break
            # The API may hand back a normalized spelling of a requested title.
            renamed = {n.get("to"): n.get("from") for n in data.get("query", {}).get("normalized", []) or []}
            for page in (data.get("query", {}).get("pages", {}) or {}).values():
                key = renamed.get(page.get("title"), page.get("title"))
                if not out.get(key):
                    continue
                for r in page.get("redirects", []) or []:
                    name = r.get("title", "")
                    if (name and name not in out[key] and len(out[key]) <= MAX_REDIRECTS
                            and former_title(key, name)):
                        out[key].append(name)
            cont = data.get("continue") or {}
            if not cont:
                break
            time.sleep(0.3)
        time.sleep(0.3)
    return out


def search_hits(title, year):
    url = ("https://en.wikipedia.org/w/api.php?action=query&list=search&format=json"
           "&srlimit=8&srsearch=" + urllib.parse.quote(search_query(title, year)))
    data = _get(url) or {}
    return [h["title"] for h in data.get("query", {}).get("search", [])]


def resolve_article(title, year, imdb="", facts_by_imdb=None):
    """This film's English Wikipedia article, or None — never another film's.

    With an IMDb id the article is the page of the Wikidata item holding that
    id. Without one (or when Wikidata does not know the id) a search hit is
    taken only if Wikidata says it is a film of this title and year
    (wiki_film_article). Until 2026-11-27 the first hit containing the title
    won: "Beast" read "The Sea Beast", "Longlegs" read "Daddy Longlegs (2009
    film)", and 9 of 217 comps carried another page's traffic.
    `facts_by_imdb`: WA.facts_for_imdb_ids() when already read for many films."""
    imdb = WA.imdb_id(imdb)
    if imdb:
        facts = facts_by_imdb if facts_by_imdb is not None else WA.facts_for_imdb_ids([imdb])
        exact = WA.article_for_imdb(imdb, facts, title, year)
        if exact:
            return exact
    hits = search_hits(title, year)
    return WA.choose_from_hits(title, year, hits, WA.facts_for_titles(hits)) if hits else None


# ── opening Friday of a comp (read, never inferred from traffic) ─────────────
def opening_friday_for_date(day):
    """Friday of the opening weekend a release date belongs to: a Monday-
    Thursday release (previews, midweek openers) opens that week's Friday."""
    wd = day.weekday()  # Mon=0 .. Sun=6
    return day + timedelta(days=4 - wd) if wd <= 4 else day - timedelta(days=wd - 4)


def chart_date(source_url):
    """Date in a the-numbers daily-chart link (the day the comp's preview
    gross was read from), or None."""
    m = re.search(r"/box-office-chart/daily/(\d{4})/(\d{2})/(\d{2})", source_url or "")
    try:
        return datetime(int(m[1]), int(m[2]), int(m[3])) if m else None
    except ValueError:
        return None


def _get_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def release_page(release_url, fetch_text=None):
    """A Box Office Mojo release page's HTML, or "" (no link, or unreadable)."""
    if not BOM.release_id(release_url):
        return ""
    try:
        return (fetch_text or _get_text)(release_url) or ""
    except Exception:  # noqa: BLE001
        return ""


def bom_release_date(release_url, fetch_text=None):
    """Domestic release date from a Box Office Mojo release page, or None."""
    return BOM.release_date(release_page(release_url, fetch_text))


def comp_opening_friday(row, fetch_text=None):
    """(YYYY-MM-DD, basis) for one historical-comps row, or (None, "").

    First the Friday in the row's Box Office Mojo daily table whose Friday /
    Saturday / Sunday grosses are the row's own: the weekend the comp's numbers
    describe, whatever ran before it (a limited opening, previews, a
    re-release). Failing that, the dated chart the row's grosses came from,
    then the release date the page states — the first US date, which for a
    platform release is the limited opening. The old method, the Friday
    nearest the article's biggest traffic day of the year, landed on awards
    season or the streaming debut (One Battle After Another: 2026-01-09
    instead of 2025-09-26); 31 of 217 rows were wrong or blank."""
    page = release_page(row.get("daily_source_url"), fetch_text)
    matched = BOM.opening_friday_for_row(row, page)
    if matched:
        return matched, "bom-daily"
    charted = chart_date(row.get("source_url"))
    if charted:
        return opening_friday_for_date(charted).strftime("%Y-%m-%d"), "numbers-chart"
    released = BOM.release_date(page)
    if released:
        return opening_friday_for_date(released).strftime("%Y-%m-%d"), "bom-release"
    return None, ""


def daily_pageviews(article, start, end):
    a = urllib.parse.quote(article.replace(" ", "_"), safe="")
    data = _get(PAGEVIEWS.format(article=a, start=start, end=end))
    return (data or {}).get("items", []) if data else []


def _window_sum(items, mon, days=4):
    by = {i["timestamp"][:8]: i["views"] for i in items}
    return sum(by.get((mon + timedelta(days=k)).strftime("%Y%m%d"), 0) for k in range(days))


def redirect_last_touched(names, batch=50):
    """{redirect: 'YYYY-MM-DD' of its latest revision}, 50 titles a request.

    A redirect left behind by a page move was written on the day of the move:
    one last touched before a film's release week was already only a redirect
    that week, and asking for its views draws the 404s that get a client
    throttled. Titles the lookup cannot date are simply absent (read anyway)."""
    out = {}
    names = [n for n in dict.fromkeys(names) if n]
    for start in range(0, len(names), batch):
        chunk = names[start:start + batch]
        url = ("https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions"
               "&rvprop=timestamp&titles=" + urllib.parse.quote("|".join(chunk)))
        try:
            data = _get(url, tries=6) or {}
        except Exception:  # noqa: BLE001
            continue
        renamed = {n.get("to"): n.get("from") for n in data.get("query", {}).get("normalized", []) or []}
        for page in (data.get("query", {}).get("pages", {}) or {}).values():
            stamp = ((page.get("revisions") or [{}])[0].get("timestamp") or "")[:10]
            if stamp:
                out[renamed.get(page.get("title"), page.get("title"))] = stamp
        time.sleep(0.3)
    return out


def anticipation_for_weekend(article, weekend_of, titles=None, touched=None):
    """Exact leak-free Mon-Thu anticipation for a known opening Friday.
    `titles`: the article and its redirects when already looked up;
    `touched`: redirect_last_touched() for them, to skip long-settled ones."""
    friday = datetime.strptime(weekend_of, "%Y-%m-%d")
    mon, thu = friday - timedelta(days=4), friday - timedelta(days=1)
    total = 0
    for name in (titles or article_titles(article)):
        if name != article and (touched or {}).get(name, "9999") < mon.strftime("%Y-%m-%d"):
            continue      # already a redirect that week: the page was not there
        items = daily_pageviews(name, mon.strftime("%Y%m%d"), thu.strftime("%Y%m%d"))
        total += _window_sum(items, mon)
        time.sleep(0.15)
    return total, friday.strftime("%Y-%m-%d")


def views_from(items, mon, since="", days=4):
    """Views on the window's days, counting only days on or after `since`
    (YYYY-MM-DD): before that the name belonged to another page."""
    by = {i["timestamp"][:8]: i["views"] for i in items}
    total = 0
    for k in range(days):
        day = mon + timedelta(days=k)
        if day.strftime("%Y-%m-%d") >= (since or ""):
            total += by.get(day.strftime("%Y%m%d"), 0)
    return total


def anticipation_under_past_names(article, weekend_of, fetch_revisions=None):
    """(Mon-Thu views, names) summed over every name the page carried by that
    week, read from the page's move history. The fallback for a page whose
    release-week name was later given to something else."""
    friday = datetime.strptime(weekend_of, "%Y-%m-%d")
    mon, thu = friday - timedelta(days=4), friday - timedelta(days=1)
    try:
        names = WA.past_names(article, thu.strftime("%Y-%m-%d"), fetch_revisions)
    except Exception as e:  # noqa: BLE001 — stays unknown
        print(f"  could not read the move history of '{article}': {e}")
        return 0, {}
    total = 0
    for name, since in names.items():
        items = daily_pageviews(name, mon.strftime("%Y%m%d"), thu.strftime("%Y%m%d"))
        total += views_from(items, mon, since)
        time.sleep(0.15)
    return total, names


def opening_friday_from_peak(d):
    """Map a pageview-peak day to the opening Friday (pure; leak-free anchor).

    The release spike usually lands on opening Fri/Sat/Sun -> that week's Friday.
    A Mon/Tue peak means the weekend just ended -> the previous Friday. A
    mid-week (Wed/Thu) peak (preview-driven) -> that week's upcoming Friday.
    """
    wd = d.weekday()  # Mon=0 .. Sun=6
    if wd in (4, 5, 6):
        return d - timedelta(days=wd - 4)
    if wd in (0, 1):
        return d - timedelta(days=wd + 3)
    return d + timedelta(days=4 - wd)


def detect_opening_and_anticipation(article, year):
    """Locate the opening Friday from the pageview spike, return (friday, antic)."""
    items = daily_pageviews(article, f"{year}0101", f"{int(year) + 1}0228")
    if not items:
        return None, 0, 0
    peak = max(items, key=lambda i: i["views"])
    d = datetime.strptime(peak["timestamp"][:8], "%Y%m%d")
    friday = opening_friday_from_peak(d)
    antic = _window_sum(items, friday - timedelta(days=4))
    return friday.strftime("%Y-%m-%d"), antic, peak["views"]


# ── cache ────────────────────────────────────────────────────────────────────
def _load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            return json.load(open(CACHE_PATH))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def _save_cache(cache):
    json.dump(cache, open(CACHE_PATH, "w"), indent=0)


# ── backfill ─────────────────────────────────────────────────────────────────
def backfill_comps(dry_run=False, throttle=0.25):
    rows = list(csv.DictReader(open(COMPS_CSV)))
    fields = list(rows[0].keys())
    for col in ("wiki_release_week_views", "wiki_article", "wiki_opening_friday"):
        if col not in fields:
            fields.append(col)
    cache = _load_cache()
    filled = failed = 0

    def cache_key(row):                 # v1 entries hold traffic-inferred Fridays
        return f"v2|{row['movie']}|{row.get('release_year', '')}"

    # Articles first: each film's own page by its IMDb id, one Wikidata query
    # for the whole file. A cached row is kept only while it holds that page
    # and a view count; then every article's redirects in a few batched
    # requests. If Wikidata cannot be reached this raises and nothing is
    # written: an article is never guessed.
    facts = WA.facts_for_imdb_ids([WA.imdb_id(r.get("imdb_url")) for r in rows])
    articles = {}
    for r in rows:
        key = cache_key(r)
        title, year = r["movie"], r.get("release_year", "")
        imdb = WA.imdb_id(r.get("imdb_url"))
        exact = WA.article_for_imdb(imdb, facts, title, year)
        cached = cache.get(key)
        if cached and cached.get("views") and (not exact or cached.get("article") == exact):
            continue
        cache.pop(key, None)
        if exact:
            articles[key] = exact
            continue
        try:
            articles[key] = resolve_article(title, year, imdb, facts)
            print(f"  searched: {title} -> {articles[key]}")
        except Exception as e:  # noqa: BLE001
            articles[key] = e
        time.sleep(throttle)
    titles_for = redirect_titles(sorted({a for a in articles.values() if isinstance(a, str)}),
                                 strict=True)
    touched = redirect_last_touched(
        [n for a, names in titles_for.items() for n in (names or []) if n != a])

    for r in rows:
        title, year = r["movie"], r.get("release_year", "")
        key = cache_key(r)
        if key in cache:
            info = cache[key]
        else:
            try:
                art = articles.get(key)
                if isinstance(art, Exception):
                    raise art
                if art and titles_for.get(art) is None:
                    raise RuntimeError("redirect lookup failed")
                info = _resolve_comp(r, title, year, throttle, art, titles_for.get(art), touched)
            except Exception as e:  # noqa: BLE001 — one film must not lose the rest
                failed += 1
                print(f"  ⚠️  {title}: lookup failed ({e}) — row left as it was; "
                      "re-run to resume from the cache")
                continue
            cache[key] = info
            _save_cache(cache)
        r["wiki_release_week_views"] = info["views"] or ""
        r["wiki_article"] = info["article"] or ""
        r["wiki_opening_friday"] = info["friday"] or ""
        if info["views"]:
            filled += 1
        print(f"  {title[:30]:30} {year} -> {str(info['article'])[:34]:34} "
              f"views={info['views'] or 0:>10,}")
    print(f"\nresolved release-week views for {filled}/{len(rows)} comps"
          + (f"; {failed} lookup(s) failed" if failed else ""))
    if dry_run:
        print("[dry-run] historical-comps.csv NOT written")
        return failed
    with open(COMPS_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {COMPS_CSV}")
    return failed


def _resolve_comp(r, title, year, throttle, art, titles=None, touched=None):
    """Opening Friday and release-week views for one comps row's article."""
    friday, basis = comp_opening_friday(r)
    if art and friday:
        antic, _ = anticipation_for_weekend(art, friday, titles=titles, touched=touched)
        peak = 0
        if antic < MIN_PLAUSIBLE_VIEWS:
            # The page had another name that week and that name now points
            # elsewhere, so it is not among the redirects (Tarot 2024: 37
            # views; 68,698 under the names in the page's own move history).
            recovered, names = anticipation_under_past_names(art, friday)
            if recovered >= MIN_PLAUSIBLE_VIEWS:
                print(f"  {title}: {antic} views under '{art}' and its redirects; "
                      f"{recovered:,} under the names it had that week {sorted(names)}")
                antic = recovered
            else:
                # Unknown, not ~0.
                print(f"  ⚠️  {title}: {antic} views in release week under "
                      f"'{art}' — recorded as unknown")
                antic = 0
    elif art:
        # No dated source at all: the traffic spike is the last resort.
        friday, antic, peak = detect_opening_and_anticipation(art, year)
        basis = "pageview-peak"
        print(f"  ⚠️  {title}: no release date on file — opening Friday "
              f"guessed from traffic ({friday})")
    else:
        antic, peak = 0, 0
    time.sleep(throttle)
    return {"article": art, "friday": friday, "views": antic, "peak": peak,
            "basis": basis}


# ── live fetch -> social-signals.csv ─────────────────────────────────────────
def review_imdb_ids(path=None):
    """{movie title: IMDb id} from reviews.csv, whose notes hold the IMDb link
    import_reviews.py matched for each film (the latest row wins)."""
    path = path or P.REVIEWS_CSV
    out = {}
    if os.path.exists(path):
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                found = WA.imdb_id(r.get("notes"))
                if found:
                    out[r.get("movie_title", "")] = found
    return out


def fetch_current(weekend, films, dry_run=False):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    imdb_ids = review_imdb_ids()
    rows = []
    for title in films:
        try:
            art = resolve_article(title, int(weekend[:4]), imdb_ids.get(title, ""))
        except Exception as e:  # noqa: BLE001 — diagnostic signal: skip, never guess
            print(f"  {title}: article lookup failed ({e}) — skipped")
            continue
        if not art:
            print(f"  {title}: no Wikipedia article verified as this film — skipped")
            continue
        views, friday = anticipation_for_weekend(art, weekend)
        print(f"  {title}: {art} release-week (Mon-Thu) views={views:,}")
        rows.append({
            "weekend_of": weekend, "as_of_date": today, "movie_title": title,
            "platform": "wikipedia", "source": "wikimedia-pageviews",
            "mentions": "", "engagement": "", "views": views,
            "social_media_universe_m": "", "likes": "", "comments": "",
            "shares": "", "positive_mentions": "", "negative_mentions": "",
            "neutral_mentions": "", "sentiment_score": "", "buzz_score": "",
            "notes": f"en.wikipedia/{art}; Mon-Thu before {friday}",
        })
    if dry_run:
        print(f"\n[dry-run] would write {len(rows)} row(s) to {P.SOCIAL_SIGNALS_CSV}")
        return
    _append_social(rows)


def _append_social(rows):
    path = P.SOCIAL_SIGNALS_CSV
    existing = set()
    if os.path.exists(path):
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                existing.add((r.get("movie_title", ""), r.get("as_of_date", ""),
                              r.get("platform", "")))
    new = [r for r in rows if (r["movie_title"], r["as_of_date"], r["platform"]) not in existing]
    write_header = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SOCIAL_FIELDS)
        if write_header:
            w.writeheader()
        w.writerows(new)
    print(f"\nwrote {len(new)} new wikipedia social-signal row(s) -> {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backfill", action="store_true", help="fill historical-comps.csv")
    ap.add_argument("--weekend", help="weekend_of (YYYY-MM-DD)")
    ap.add_argument("--movies", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.backfill:
        return 1 if backfill_comps(dry_run=args.dry_run) else 0

    weekend = args.weekend or P._current_weekend_friday()
    films = args.movies or sorted(P.load_seat_data(weekend_of=weekend).keys())
    if not films:
        print("No films to fetch.")
        return 0
    print(f"Fetching Wikipedia anticipation for weekend {weekend}: {films}")
    fetch_current(weekend, films, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
