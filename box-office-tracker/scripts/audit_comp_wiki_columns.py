#!/usr/bin/env python3
"""Check historical-comps.csv `wiki_opening_friday` and `wiki_article` against
records that cannot point at another weekend or another film. Read-only.

  * Opening Friday: the Friday in the row's own Box Office Mojo daily table
    whose Friday/Saturday/Sunday grosses are the row's friday_m / saturday_m /
    sunday_m. It is the weekend the comp's numbers describe, so a limited run
    before the wide release, a re-release or an awards-season traffic spike
    cannot move it.
  * Article: the English Wikipedia page of the Wikidata item that holds the
    row's IMDb id (wiki_film_article).

On 2026-11-27 this found 31 wrong or blank Fridays and 9 wrong articles in 217
rows. Exit status 1 when any row disagrees, so it can gate a refill.

Usage:
  python3 scripts/audit_comp_wiki_columns.py
  python3 scripts/audit_comp_wiki_columns.py --pages-dir /tmp/bom   # keep the pages
  python3 scripts/audit_comp_wiki_columns.py --skip-articles
"""
import argparse
import csv
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bom_release_page as B  # noqa: E402
import wiki_film_article as A  # noqa: E402

COMPS_CSV = os.path.join(os.path.dirname(HERE), "data", "historical-comps.csv")
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")


def _page(rl, pages_dir, throttle):
    path = os.path.join(pages_dir, rl + ".html") if pages_dir else ""
    if path and os.path.exists(path) and os.path.getsize(path) > 50000:
        return open(path, encoding="utf-8", errors="ignore").read()
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(f"https://www.boxofficemojo.com/release/{rl}/",
                                         headers={"User-Agent": BROWSER_UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "ignore")
            if path:
                os.makedirs(pages_dir, exist_ok=True)
                open(path, "w", encoding="utf-8").write(body)
            time.sleep(throttle)
            return body
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (attempt + 1))
    print(f"  could not read {rl}: {last}")
    return ""


def audit(rows, pages_dir="", throttle=0.8, skip_articles=False):
    """[(movie, column, value on file, value found)] for every disagreement."""
    wrong = []
    facts = {} if skip_articles else A.facts_for_imdb_ids(
        [A.imdb_id(r.get("imdb_url")) for r in rows])
    for r in rows:
        rl = B.release_id(r.get("daily_source_url"))
        friday = B.opening_friday_for_row(r, _page(rl, pages_dir, throttle)) if rl else None
        if friday is None:
            wrong.append((r["movie"], "wiki_opening_friday", r.get("wiki_opening_friday", ""),
                          "no weekend in the daily table matches the row's grosses"))
        elif friday != r.get("wiki_opening_friday", ""):
            wrong.append((r["movie"], "wiki_opening_friday", r.get("wiki_opening_friday", ""), friday))
        if skip_articles:
            continue
        article = A.article_for_imdb(A.imdb_id(r.get("imdb_url")), facts)
        on_file = r.get("wiki_article", "")
        # The page's name today. A page moved since the last refill ("The Menu
        # (2022 film)" -> "The Menu") shows here too: its old name is only a
        # redirect now, and the refill counts a page under all its names.
        if article and on_file != article:
            wrong.append((r["movie"], "wiki_article", on_file, article))
    return wrong


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--comps", default=COMPS_CSV)
    ap.add_argument("--pages-dir", default="", help="keep/reuse the release pages here")
    ap.add_argument("--skip-articles", action="store_true")
    args = ap.parse_args()
    rows = list(csv.DictReader(open(args.comps)))
    wrong = audit(rows, args.pages_dir, skip_articles=args.skip_articles)
    for movie, column, on_file, found in wrong:
        print(f"  {movie[:44]:44} {column:20} on file: {on_file or '(blank)'}  ->  {found}")
    dates = sum(1 for w in wrong if w[1] == "wiki_opening_friday")
    print(f"\n{len(rows)} rows: {dates} opening Friday(s) and {len(wrong) - dates} article(s) disagree")
    return 1 if wrong else 0


if __name__ == "__main__":
    raise SystemExit(main())
