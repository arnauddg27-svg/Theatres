#!/usr/bin/env python3
"""Backfill IMDb and Rotten Tomatoes audience-score references for comps.

This script enriches data/historical-comps.csv only. It does not touch seat
scraping, scheduling, prediction execution, or calibration defaults.
"""

from __future__ import annotations

import csv
import gzip
import html
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
COMPS_CSV = BASE_DIR / "data" / "historical-comps.csv"
IMDB_RATINGS_URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"
IMDB_TITLE_URL = "https://www.imdb.com/title/{imdb_id}/"
IMDB_SUGGEST_URL = "https://v3.sg.media-imdb.com/suggestion/x/{query}.json"
RT_SEARCH_URL = "https://www.rottentomatoes.com/search?search={query}"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


AUDIENCE_FIELDS = [
    "imdb_rating",
    "imdb_votes",
    "imdb_url",
    "rt_audience_score",
    "rt_audience_score_type",
    "rt_url",
]


TITLE_OVERRIDES = {
    "Guardians of the Galaxy Vol 3": "Guardians of the Galaxy Vol. 3",
    "Venom: Let There be Carnage": "Venom: Let There Be Carnage",
    "Demon Slayer -Kimetsu no Yaiba- The Movie: Infinity Castle": (
        "Demon Slayer: Kimetsu no Yaiba Infinity Castle"
    ),
    "Renaissance: A Film by Beyonce": "Renaissance: A Film by Beyoncé",
}


def norm(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def token_score(target: str, candidate: str) -> float:
    target_tokens = set(re.findall(r"[a-z0-9]+", target.lower()))
    candidate_tokens = set(re.findall(r"[a-z0-9]+", candidate.lower()))
    if not target_tokens or not candidate_tokens:
        return 0.0
    return len(target_tokens & candidate_tokens) - len(candidate_tokens - target_tokens) * 0.25


def source_title(title: str) -> str:
    return TITLE_OVERRIDES.get(title, title)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def load_imdb_ratings() -> dict[str, tuple[str, str]]:
    data = gzip.decompress(fetch_bytes(IMDB_RATINGS_URL)).decode("utf-8", errors="replace")
    ratings: dict[str, tuple[str, str]] = {}
    for line in data.splitlines()[1:]:
        imdb_id, rating, votes = line.split("\t")
        ratings[imdb_id] = (rating, votes)
    return ratings


def imdb_candidates(title: str) -> list[dict]:
    query = re.sub(r"[^a-z0-9]+", "_", source_title(title).lower()).strip("_")
    page = fetch(IMDB_SUGGEST_URL.format(query=urllib.parse.quote(query)))
    data = json.loads(page)
    return [
        item
        for item in data.get("d", [])
        if item.get("qid") == "movie" and item.get("id", "").startswith("tt")
    ]


def choose_imdb_candidate(title: str, release_year: int, candidates: list[dict]) -> dict | None:
    target = source_title(title)
    target_norm = norm(target)
    best = None
    best_score = -100.0
    for item in candidates:
        candidate_title = item.get("l", "")
        candidate_year = int(item.get("y") or 0)
        score = token_score(target, candidate_title)
        if norm(candidate_title) == target_norm:
            score += 4.0
        if candidate_year == release_year:
            score += 2.0
        elif abs(candidate_year - release_year) == 1:
            score += 1.0
        elif candidate_year:
            score -= min(abs(candidate_year - release_year), 5)
        rank = item.get("rank")
        if isinstance(rank, int):
            score += max(0.0, 1.0 - min(rank, 50_000) / 50_000)
        if score > best_score:
            best = item
            best_score = score
    return best


def imdb_reference(title: str,
                   release_year: int,
                   ratings: dict[str, tuple[str, str]]) -> tuple[str, str, str]:
    candidate = choose_imdb_candidate(title, release_year, imdb_candidates(title))
    if not candidate:
        raise ValueError("no IMDb title match")
    imdb_id = candidate["id"]
    if imdb_id not in ratings:
        raise ValueError(f"IMDb title {imdb_id} has no rating row")
    rating, votes = ratings[imdb_id]
    return rating, votes, IMDB_TITLE_URL.format(imdb_id=imdb_id)


def rt_search_candidates(title: str) -> list[dict]:
    query = urllib.parse.quote_plus(source_title(title))
    page = fetch(RT_SEARCH_URL.format(query=query))
    candidates = []
    for block in re.findall(r"<search-page-media-row\b(.*?)</search-page-media-row>", page, flags=re.S):
        year_match = re.search(r'release-year="(\d{4})"', block)
        href_match = re.search(r'<a href="(https://www\.rottentomatoes\.com/m/[^"]+)"[^>]*slot="title"', block)
        title_match = re.search(r'slot="title">\s*(.*?)\s*</a>', block, flags=re.S)
        if not href_match or not title_match:
            continue
        candidates.append({
            "title": html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()),
            "url": html.unescape(href_match.group(1)),
            "year": int(year_match.group(1)) if year_match else 0,
        })
    return candidates


def choose_rt_candidate(title: str, release_year: int, candidates: list[dict]) -> dict | None:
    target = source_title(title)
    target_norm = norm(target)
    best = None
    best_score = -100.0
    for item in candidates:
        candidate_title = item["title"]
        candidate_year = item["year"]
        score = token_score(target, candidate_title)
        if norm(candidate_title) == target_norm:
            score += 4.0
        if candidate_year == release_year:
            score += 2.0
        elif abs(candidate_year - release_year) == 1:
            score += 1.0
        elif candidate_year:
            score -= min(abs(candidate_year - release_year), 5)
        if score > best_score:
            best = item
            best_score = score
    return best


def rt_scorecard(url: str) -> dict:
    page = fetch(url)
    match = re.search(
        r'id="media-scorecard-json"[^>]*>\s*(\{.*?\})\s*</script>',
        page,
        flags=re.S,
    )
    if not match:
        raise ValueError("no Rotten Tomatoes scorecard JSON")
    return json.loads(html.unescape(match.group(1)))


def rt_reference(title: str, release_year: int) -> tuple[str, str, str]:
    candidate = choose_rt_candidate(title, release_year, rt_search_candidates(title))
    if not candidate:
        raise ValueError("no Rotten Tomatoes title match")
    scorecard = rt_scorecard(candidate["url"])
    audience = scorecard.get("audienceScore") or {}
    if not audience.get("score"):
        audience = (scorecard.get("overlay") or {}).get("audienceAll") or {}
    score = str(audience.get("score") or "").strip()
    score_type = str(audience.get("scoreType") or "ALL").strip()
    if not score:
        raise ValueError("no Rotten Tomatoes audience score")
    return score, score_type, candidate["url"]


def has_audience_reference(row: dict[str, str]) -> bool:
    return all((row.get(field) or "").strip() for field in AUDIENCE_FIELDS)


def main() -> None:
    with COMPS_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    for field in AUDIENCE_FIELDS:
        if field not in fields:
            fields.append(field)

    ratings = load_imdb_ratings()
    failures = []
    out = []
    for row in rows:
        title = row["movie"]
        release_year = int(row.get("release_year") or 0)
        if has_audience_reference(row):
            out.append(row)
            continue
        try:
            imdb_rating, imdb_votes, imdb_url = imdb_reference(title, release_year, ratings)
            rt_score, rt_score_type, rt_url = rt_reference(title, release_year)
            row["imdb_rating"] = imdb_rating
            row["imdb_votes"] = imdb_votes
            row["imdb_url"] = imdb_url
            row["rt_audience_score"] = rt_score
            row["rt_audience_score_type"] = rt_score_type
            row["rt_url"] = rt_url
            out.append(row)
            print(
                f"ok {title}: IMDb {imdb_rating} ({imdb_votes}), "
                f"RT {rt_score}% {rt_score_type}"
            )
        except Exception as exc:
            failures.append(f"{title}: {exc}")
            print(f"FAIL {title}: {exc}")
        time.sleep(0.25)

    if failures:
        raise SystemExit("\n".join(failures))

    with COMPS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)


if __name__ == "__main__":
    main()
