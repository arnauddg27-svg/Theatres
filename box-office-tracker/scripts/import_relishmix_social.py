#!/usr/bin/env python3
"""Backfill RelishMix social-buzz references for historical comps.

This enriches data/historical-comps.csv only. It never touches live scraping,
workflow scheduling, calibration, or current-weekend social inputs.
"""

from __future__ import annotations

import csv
import html
import re
import time
import unicodedata
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
COMPS_CSV = BASE_DIR / "data" / "historical-comps.csv"
RELISHMIX_SITEMAP_URL = "https://www.relishmix.com/sitemap.xml"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

SOCIAL_FIELDS = [
    "social_media_universe_m",
    "social_sentiment_score",
    "social_buzz_score",
    "social_source_url",
    "social_notes",
]

TITLE_OVERRIDES = {
    "Alien: Romulus": "Alien Romulus",
    "A Quiet Place: Day One": "A Quiet Place Day One",
    "Bad Boys: Ride or Die": "Bad Boys Ride or Die",
    "Beetlejuice Beetlejuice": "Beetlejuice 2",
    "Demon Slayer -Kimetsu no Yaiba- The Movie: Infinity Castle": "Demon Slayer",
    "Dungeons & Dragons: Honor Among Thieves": "Dungeons & Dragons Honor Among Thieves",
    "Five Nights at Freddy's": "Five Nights at Freddys",
    "Godzilla x Kong: The New Empire": "Godzilla x Kong The New Empire",
    "Guardians of the Galaxy Vol 3": "Guardians of the Galaxy Vol. 3",
    "M3GAN": "Megan",
    "Mission: Impossible - Dead Reckoning Part One": "Mission Impossible Dead Reckoning",
    "Spider-Man: Across the Spider-Verse": "Spider Man Across the Spider Verse",
    "Spider-Man: No Way Home": "Spider Man No Way Home",
    "The Super Mario Bros. Movie": "Super Mario Bros",
    "Venom: Let There be Carnage": "Venom Let There Be Carnage",
}


def norm(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def tokens(value: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if token not in {"the", "a", "an", "of", "and", "part", "movie", "film"}
    ]


def source_title(title: str) -> str:
    return TITLE_OVERRIDES.get(title, title)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", errors="replace")


def text_from_html(page: str) -> str:
    page = re.sub(r"<script[\s\S]*?</script>", " ", page, flags=re.I)
    page = re.sub(r"<style[\s\S]*?</style>", " ", page, flags=re.I)
    page = re.sub(r"<[^>]+>", " ", page)
    page = html.unescape(page)
    return re.sub(r"\s+", " ", page).strip()


def sitemap_urls() -> list[str]:
    page = fetch(RELISHMIX_SITEMAP_URL)
    urls = re.findall(r"<loc>(.*?)</loc>", page)
    return [
        url
        for url in urls
        if "/news/" in url
        or url.rstrip("/").split("/")[-1]
        in {
            "alien-romulous",
            "beetlejuice2",
            "challengers",
            "dune-2",
            "furiosa",
            "last-breath-focus",
            "nosferatu",
            "the-monkey1",
        }
    ]


def page_title(page: str) -> str:
    match = re.search(r"<title>(.*?)</title>", page, flags=re.S | re.I)
    if not match:
        return ""
    return html.unescape(re.sub(r"\s+", " ", match.group(1))).replace("— RelishMix", "").strip()


def title_match_score(movie: str, url: str, title: str, text: str) -> float:
    source = source_title(movie)
    source_norm = norm(source)
    title_norm = norm(title)
    slug = url.rstrip("/").split("/")[-1].replace("-", " ")
    slug_norm = norm(slug)
    text_prefix_norm = norm(text[:5000])

    score = 0.0
    if source_norm and source_norm in title_norm:
        score += 8.0
    if source_norm and source_norm in slug_norm:
        score += 6.0
    if source_norm and source_norm in text_prefix_norm:
        score += 3.0

    movie_tokens = set(tokens(source))
    title_tokens = set(tokens(title))
    slug_tokens = set(tokens(slug))
    if movie_tokens:
        score += len(movie_tokens & title_tokens) / len(movie_tokens) * 3.0
        score += len(movie_tokens & slug_tokens) / len(movie_tokens) * 2.0
    return score


def parse_number(raw: str, suffix: str) -> float:
    value = float(raw.replace(",", ""))
    suffix = suffix.upper()
    if suffix == "B":
        return value * 1000.0
    if suffix == "K":
        return value / 1000.0
    return value


def smu_candidates(text: str) -> list[tuple[int, float]]:
    candidates = []
    for pattern in (
        r"(?:social media across|social awareness|total reach across)[^.]{0,260}?"
        r"(?:is|at|stood at|running at|stands at|of)\s*"
        r"\$?([0-9][0-9,]*(?:\.[0-9]+)?)\s*([KMB])\b",
        r"social media universe stats[^.]{0,260}?"
        r"(?:is|at|stood at|running at|stands at|of)\s*"
        r"\$?([0-9][0-9,]*(?:\.[0-9]+)?)\s*([KMB])\b",
    ):
        for match in re.finditer(pattern, text, flags=re.I):
            candidates.append((match.start(), parse_number(match.group(1), match.group(2))))
    for keyword in ("social media universe", "SMU"):
        for match in re.finditer(keyword, text, flags=re.I):
            window = text[match.start():match.start() + 900]
            total = re.search(
                r"total\s+social\s+media\s+universe\s+(?:of|at|is|stands at|sits at)\s*"
                r"\$?([0-9][0-9,]*(?:\.[0-9]+)?)\s*([KMB])\b",
                window,
                flags=re.I,
            )
            if total:
                candidates.append((match.start(), parse_number(total.group(1), total.group(2))))
                continue
            number = re.search(
                r"(?:at|to|of|with|running at|sits at|stands at|is at|was at)\s*"
                r"\$?([0-9][0-9,]*(?:\.[0-9]+)?)\s*([KMB])\b",
                window,
                flags=re.I,
            )
            if number:
                nearby_values = [
                    parse_number(item.group(1), item.group(2))
                    for item in re.finditer(
                        r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*([KMB])\b",
                        window[:450],
                        flags=re.I,
                    )
                ]
                candidates.append((
                    match.start(),
                    max(nearby_values) if nearby_values else parse_number(number.group(1), number.group(2)),
                ))
                continue
            fallback = re.search(r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*([KMB])\b", window, flags=re.I)
            if fallback:
                candidates.append((match.start(), parse_number(fallback.group(1), fallback.group(2))))
    return candidates


def extract_smu_m(text: str) -> float:
    candidates = smu_candidates(text)
    return candidates[0][1] if candidates else 0.0


def extract_sentiment_score(text: str) -> float:
    match = re.search(
        r"Combined Index Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*10",
        text,
        flags=re.I,
    )
    if match:
        score = float(match.group(1))
        return max(-1.0, min(1.0, (score - 5.0) / 5.0))

    convo_match = re.search(r"Convo:\s*(POS|NEG|MIXED)", text, flags=re.I)
    if convo_match:
        label = convo_match.group(1).lower()
        if label == "pos":
            return 0.45
        if label == "neg":
            return -0.45
    return 0.0


def load_pages() -> list[dict[str, str]]:
    pages = []
    for url in sitemap_urls():
        try:
            page = fetch(url)
        except Exception as exc:  # pragma: no cover - network diagnostic script
            print(f"skip {url}: {exc}")
            continue
        text = text_from_html(page)
        smu_m = extract_smu_m(text)
        sentiment = extract_sentiment_score(text)
        if smu_m <= 0 and sentiment == 0:
            continue
        pages.append({
            "url": url,
            "title": page_title(page),
            "text": text,
            "smu_m": f"{smu_m:.3f}" if smu_m > 0 else "",
            "sentiment": f"{sentiment:.4f}" if sentiment else "",
        })
        time.sleep(0.1)
    return pages


def title_positions(movie: str, text: str) -> list[int]:
    source = source_title(movie)
    lowered = text.lower()
    phrases = {source.lower()}
    compact_tokens = tokens(source)
    if compact_tokens:
        phrases.add(" ".join(compact_tokens))
    positions = []
    for phrase in phrases:
        if not phrase:
            continue
        start = 0
        while True:
            idx = lowered.find(phrase, start)
            if idx < 0:
                break
            positions.append(idx)
            start = idx + max(1, len(phrase))
    return positions


def metric_for_movie(movie: str, page: dict[str, str]) -> tuple[float, float]:
    """Return (smu_m, proximity_score) for the movie on this page.

    Multi-title box-office articles often mention several movies. The SMU value
    has to live near the target title, otherwise short/generic titles like "IF"
    or "Drop" can steal a different movie's social metric.
    """
    candidates = smu_candidates(page["text"])
    if not candidates:
        return 0.0, 0.0

    positions = title_positions(movie, page["text"])
    if not positions:
        return 0.0, 0.0

    best_value = 0.0
    best_score = 0.0
    for metric_pos, value in candidates:
        distance = min(abs(metric_pos - title_pos) for title_pos in positions)
        if distance <= 650:
            score = 4.0
        elif distance <= 1400:
            score = 2.0
        elif distance <= 2600:
            score = 0.75
        else:
            score = 0.0
        if score > best_score:
            best_value = value
            best_score = score
    return best_value, best_score


def is_unsafe_short_match(movie: str, url: str, title: str) -> bool:
    movie_tokens = tokens(source_title(movie))
    if len(movie_tokens) > 1 and len(norm(source_title(movie))) > 4:
        return False
    source_norm = norm(source_title(movie))
    if not source_norm:
        return True
    title_norm = norm(title)
    slug_norm = norm(url.rstrip("/").split("/")[-1])
    return not (title_norm.startswith(source_norm) or slug_norm.startswith(source_norm))


def choose_page(movie: str, pages: list[dict[str, str]]) -> dict[str, str] | None:
    source_norm = norm(source_title(movie))
    best = None
    best_score = 0.0
    for page in pages:
        if is_unsafe_short_match(movie, page["url"], page["title"]):
            continue
        title_norm = norm(page["title"])
        slug_norm = norm(page["url"].rstrip("/").split("/")[-1])
        if source_norm not in title_norm and source_norm not in slug_norm:
            continue
        smu_m, proximity_score = metric_for_movie(movie, page)
        if smu_m <= 0 or proximity_score < 2.0:
            continue
        score = title_match_score(movie, page["url"], page["title"], page["text"])
        score += proximity_score
        if slug_norm.startswith(source_norm):
            score += 5.0
        elif source_norm in slug_norm:
            score += 1.0
        if title_norm.startswith(source_norm):
            score += 3.0
        if score > best_score:
            best = {**page, "smu_m": f"{smu_m:.3f}"}
            best_score = score
    if not best or best_score < 6.0:
        return None
    return best


def main() -> None:
    with COMPS_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = list(reader.fieldnames or [])

    for field in SOCIAL_FIELDS:
        if field not in fields:
            fields.append(field)

    pages = load_pages()
    updated = 0
    matched = 0
    for row in rows:
        for field in SOCIAL_FIELDS:
            row[field] = ""
        movie = (row.get("movie") or "").strip()
        if not movie:
            continue
        page = choose_page(movie, pages)
        if not page:
            continue
        matched += 1
        if page.get("smu_m"):
            row["social_media_universe_m"] = page["smu_m"]
        if page.get("sentiment"):
            row["social_sentiment_score"] = page["sentiment"]
        row["social_source_url"] = page["url"]
        row["social_notes"] = f"RelishMix public social metrics matched from {page['title']}"
        updated += 1
        print(f"{movie}: SMU={row.get('social_media_universe_m') or '-'}M "
              f"sentiment={row.get('social_sentiment_score') or '-'} url={page['url']}")

    with COMPS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"RelishMix pages with metrics: {len(pages)}")
    print(f"Matched comps: {matched}")
    print(f"Updated comps: {updated}")


if __name__ == "__main__":
    main()
