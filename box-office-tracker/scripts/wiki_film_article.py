#!/usr/bin/env python3
"""Which English Wikipedia article belongs to THIS film.

A text search for "<title> <year> film" returns articles that merely contain
the title, and the old resolver took the first one whose name contained it:
"Beast" became "The Sea Beast (2022 film)", "Longlegs" became "Daddy Longlegs
(2009 film)", "The Accountant 2" became "The Accountant (2016 film)", "No Time
to Die" became the 1958 film, "Smile 2" became "Smile (2022 film)", "M3GAN" the
film-series page and "Killers of the Flower Moon" its accolades list. Nine of
the 217 comps carried another page's traffic.

Two rules replace it, both read from Wikidata (one query per run):

  * IMDb id known (every historical comp has one): the article is the English
    sitelink of the Wikidata item holding that IMDb id. Nothing is guessed.
  * IMDb id unknown: a search hit is accepted only when its name, without the
    disambiguator, IS the film's title, its Wikidata item is a film, and no
    year on the page contradicts the release year. Otherwise there is no
    article — an unknown is recorded, never another film's page.
"""
import json
import os
import re
import unicodedata
import urllib.parse
import urllib.request

WDQS = "https://query.wikidata.org/sparql"
_CONTACT = (os.environ.get("WIKIMEDIA_CONTACT") or "").strip()
UA = "box-office-wom/0.2 (research)" + (f" contact {_CONTACT}" if _CONTACT else "")
BATCH = 80          # ids or titles per query


def imdb_id(text):
    """'tt1234567' found in an IMDb link or note, else ''."""
    m = re.search(r"\btt\d{6,}\b", text or "")
    return m[0] if m else ""


def norm(s):
    """Letters and digits only, accents folded ('Folie à Deux' = 'Folie a Deux')."""
    plain = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in plain.lower() if c.isalnum() and not unicodedata.combining(c))


def title_key(name):
    """A title for comparing: no disambiguator, punctuation, accents or
    leading article ('Runner' = 'The Runner')."""
    words = re.sub(r"^(the|a|an)\s+", "", base_title(name).strip(), flags=re.I)
    return norm(words)


def base_title(name):
    """Article or film name without a trailing disambiguator: 'Beast (2022
    American film)' -> 'Beast', 'Moana (2026)' -> 'Moana'."""
    return re.sub(r"\s*\([^()]*\)\s*$", "", name or "").strip()


def disambiguator_years(name):
    m = re.search(r"\(([^()]*)\)\s*$", name or "")
    return [int(y) for y in re.findall(r"\b(?:18|19|20)\d{2}\b", m[1])] if m else []


# ── Wikidata ─────────────────────────────────────────────────────────────────
def _fetch_bindings(query):
    req = urllib.request.Request(
        WDQS, data=urllib.parse.urlencode({"query": query, "format": "json"}).encode(),
        headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)["results"]["bindings"]


_FACT_BODY = """
  ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> ;
           schema:name ?title .
  BIND(EXISTS { ?item wdt:P31/wdt:P279* wd:Q11424 } AS ?film)
  BIND(EXISTS { ?item wdt:P495 wd:Q30 } AS ?us)
  OPTIONAL { ?item wdt:P577 ?date }
"""


def _facts(bindings):
    """Group query rows into one fact per Wikidata item."""
    by_item = {}
    for b in bindings:
        item = b["item"]["value"].rsplit("/", 1)[-1]
        f = by_item.setdefault(item, {"item": item, "title": b["title"]["value"],
                                      "film": False, "us": False, "years": set(),
                                      "imdb": set()})
        f["film"] = f["film"] or b.get("film", {}).get("value") == "true"
        f["us"] = f["us"] or b.get("us", {}).get("value") == "true"
        if b.get("date", {}).get("value", "")[:4].isdigit():
            f["years"].add(int(b["date"]["value"][:4]))
        if b.get("imdb"):
            f["imdb"].add(b["imdb"]["value"])
    for f in by_item.values():
        f["years"], f["imdb"] = sorted(f["years"]), sorted(f["imdb"])
    return list(by_item.values())


def facts_for_imdb_ids(ids, fetch=None):
    """{imdb id: [fact, ...]} for the items that hold each id and have an
    English article. Two items can share an id (a film and its series page)."""
    fetch = fetch or _fetch_bindings
    out = {}
    ids = sorted({i for i in ids if i})
    for k in range(0, len(ids), BATCH):
        values = " ".join(json.dumps(i) for i in ids[k:k + BATCH])
        query = ("SELECT ?imdb ?item ?title ?film ?us ?date WHERE { VALUES ?imdb { %s } "
                 "?item wdt:P345 ?imdb . %s }" % (values, _FACT_BODY))
        for f in _facts(fetch(query)):
            for i in f["imdb"]:
                out.setdefault(i, []).append(f)
    return out


def facts_for_titles(titles, fetch=None):
    """{article name: fact} for English Wikipedia article names."""
    fetch = fetch or _fetch_bindings
    out = {}
    titles = sorted({t for t in titles if t})
    for k in range(0, len(titles), BATCH):
        values = " ".join(json.dumps(t, ensure_ascii=False) + "@en" for t in titles[k:k + BATCH])
        query = ("SELECT ?imdb ?item ?title ?film ?us ?date WHERE { VALUES ?title { %s } "
                 "%s OPTIONAL { ?item wdt:P345 ?imdb } }" % (values, _FACT_BODY))
        for f in _facts(fetch(query)):
            out[f["title"]] = f
    return out


# ── choosing (pure; unit-tested) ─────────────────────────────────────────────
def year_fits(fact, year, name=""):
    """No year on the page contradicts the release year. A film can premiere
    the year before its US release (Talk to Me: 2022 festival, 2023 release)."""
    year = int(year)
    stated = disambiguator_years(name or fact.get("title", ""))
    if stated and not any(y in (year - 1, year) for y in stated):
        return False
    years = fact.get("years") or []
    return not years or any(y in (year - 1, year) for y in years)


def article_for_imdb(imdb, facts_by_imdb, title="", year=None):
    """The film's article from its IMDb id, or None. Among items sharing the
    id, only a film counts ('Horizon: An American Saga' is the series page).

    An id is only as good as whoever matched it: reviews.csv held another
    film's id for "Ramayana: Rise of A Legend" ("Villeneuve: The Rise of a
    Legend"). So when the film's title and year are given, the article must
    agree with them: one title contains the other ("F9: The Fast Saga" /
    "F9 (film)") and no year contradicts the release year."""
    films = [f for f in facts_by_imdb.get(imdb, []) if f.get("film")]
    if len(films) != 1:
        return None
    found = films[0]
    if title:
        ours, theirs = title_key(title), title_key(found["title"])
        if not ours or not theirs or (ours not in theirs and theirs not in ours):
            return None
    if year and not year_fits(found, year):
        return None
    return found["title"]


def choose_from_hits(title, year, hits, facts_by_title):
    """The search hit that is this film, or None — never a different film.

    Accepted: the name before the disambiguator equals the film's title, the
    Wikidata item is a film, and the years agree. Two films of one title and
    year ('Beast (2022 Indian film)' / 'Beast (2022 American film)'): the
    domestic one, since the comps are US releases; still tied -> None."""
    want = title_key(title)
    ok = []
    for name in hits:
        fact = facts_by_title.get(name)
        if not fact or not fact.get("film"):
            continue
        if title_key(name) != want:
            continue
        if not year_fits(fact, year, name):
            continue
        ok.append((name, fact))
    if len(ok) > 1:
        dated = [c for c in ok if int(year) in disambiguator_years(c[0])
                 or int(year) in (c[1].get("years") or [])]
        ok = dated or ok
    if len(ok) > 1:
        ok = [c for c in ok if c[1].get("us")] or ok
    return ok[0][0] if len(ok) == 1 else None


def resolve(title, year, imdb="", hits=(), fetch=None):
    """(article or None, basis). `hits` are search results, used only when the
    IMDb id is missing or Wikidata does not know it."""
    imdb = imdb_id(imdb)
    if imdb:
        art = article_for_imdb(imdb, facts_for_imdb_ids([imdb], fetch), title, year)
        if art:
            return art, "imdb"
    hits = list(hits)
    if hits:
        art = choose_from_hits(title, year, hits, facts_for_titles(hits, fetch))
        if art:
            return art, "search-verified"
    return None, ""


# ── the names a page has had ─────────────────────────────────────────────────
# Pageviews are filed under the name a page had on the day. Reading a film's
# redirects finds most earlier names, but not one that has since been pointed
# at something else: "Tarot (2024 film)" carried the film through its release
# week (68,661 views) and now leads to a list of films, so the film's page and
# its redirects show 37. The page's own history records every move.
WIKI_API = "https://en.wikipedia.org/w/api.php"
MOVED = re.compile(r"moved (?:page )?\[\[(.+?)\]\] to \[\[(.+?)\]\]")
OTHER_NAMESPACE = re.compile(r"^(Draft|User|Wikipedia|Talk|Draft talk|User talk):", re.I)
MAX_HISTORY_REQUESTS = 60       # 500 revisions each


def title_history(revisions):
    """[(YYYY-MM-DD the name took effect, name)] from a page's revisions, oldest
    first. Each move leaves a revision whose comment names both titles. The
    first entry's date is '' (the name the page was created under). Draft and
    other non-article names are left out: nobody reads a film there."""
    names = []
    for rev in sorted(revisions, key=lambda r: r.get("timestamp", "")):
        m = MOVED.search(rev.get("comment") or "")
        if not m:
            continue
        if not names:
            names.append(("", m[1]))
        names.append((rev.get("timestamp", "")[:10], m[2]))
    return [(since, name) for since, name in names if not OTHER_NAMESPACE.match(name)]


def names_through(history, last_day):
    """{name: first day it counts} for the names the page had on or before
    `last_day` (YYYY-MM-DD). A name's views before the page took it belong to
    whatever was there then."""
    out = {}
    for since, name in history:
        if since <= last_day:
            out.setdefault(name, since)
    return out


def _fetch_revisions(article):
    revisions, cont = [], {}
    for _ in range(MAX_HISTORY_REQUESTS):
        query = {"action": "query", "format": "json", "prop": "revisions",
                 "rvprop": "timestamp|comment", "rvlimit": "500", "rvdir": "newer",
                 "titles": article, **cont}
        req = urllib.request.Request(WIKI_API + "?" + urllib.parse.urlencode(query),
                                     headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        for page in (data.get("query", {}).get("pages", {}) or {}).values():
            revisions.extend(page.get("revisions", []) or [])
        cont = data.get("continue") or {}
        if not cont:
            return revisions
    raise RuntimeError(f"{article}: history longer than {MAX_HISTORY_REQUESTS * 500} revisions")


def past_names(article, last_day, fetch_revisions=None):
    """{name: first day it counts} for every article name the page carried up
    to `last_day`. Today's name is among them unless the page took it later."""
    history = title_history((fetch_revisions or _fetch_revisions)(article))
    names = names_through(history, last_day)
    if article not in {name for _, name in history}:
        names.setdefault(article, "")
    return names
