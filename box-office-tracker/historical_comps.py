#!/usr/bin/env python3
"""Historical-comp helpers for opening-weekend model research.

This module is intentionally read-only. It does not touch scraping, workflow
scheduling, seat-count collection, or live prediction defaults. It estimates an
opening weekend from a Thursday-preview gross by comparing the target movie to
historical films with similar genre/audience metadata.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_COMPS_CSV = DATA_DIR / "historical-comps.csv"
DEFAULT_METADATA_CSV = DATA_DIR / "movie-metadata.csv"


@dataclass(frozen=True)
class HistoricalComp:
    movie: str
    genre: str
    audience_type: str
    franchise_type: str
    rating: str
    thursday_preview_m: float
    opening_weekend_m: float
    source_url: str = ""
    notes: str = ""

    @property
    def thursday_share(self) -> float:
        if self.opening_weekend_m <= 0:
            return 0.0
        return self.thursday_preview_m / self.opening_weekend_m


@dataclass(frozen=True)
class TargetMetadata:
    movie: str
    genre: str
    audience_type: str
    franchise_type: str
    rating: str
    weekend_of: str = ""
    notes: str = ""


@dataclass(frozen=True)
class CompEstimate:
    movie: str
    thursday_gross_m: float
    mid_m: float
    low_m: float
    high_m: float
    weighted_thursday_share: float
    low_share: float
    high_share: float
    comps: list[HistoricalComp]
    weights: dict[str, float]
    baseline_thursday_share: float | None = None
    adjusted_thursday_share: float | None = None
    adjusted_mid_m: float | None = None
    comp_influence: float = 1.0


def _clean(value: str | None) -> str:
    return (value or "").strip().lower().replace(" ", "_")


def _float(row: dict, key: str) -> float:
    raw = (row.get(key) or "").strip()
    return float(raw) if raw else 0.0


def load_historical_comps(path: Path | str = DEFAULT_COMPS_CSV) -> list[HistoricalComp]:
    path = Path(path)
    if not path.exists():
        return []
    comps = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            comp = HistoricalComp(
                movie=(row.get("movie") or "").strip(),
                genre=_clean(row.get("genre")),
                audience_type=_clean(row.get("audience_type")),
                franchise_type=_clean(row.get("franchise_type")),
                rating=(row.get("rating") or "").strip().upper(),
                thursday_preview_m=_float(row, "thursday_preview_m"),
                opening_weekend_m=_float(row, "opening_weekend_m"),
                source_url=(row.get("source_url") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            )
            if comp.movie and comp.thursday_share > 0:
                comps.append(comp)
    return comps


def load_movie_metadata(path: Path | str = DEFAULT_METADATA_CSV) -> dict[str, TargetMetadata]:
    path = Path(path)
    if not path.exists():
        return {}
    metadata = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            movie = (row.get("movie") or "").strip()
            if not movie:
                continue
            item = TargetMetadata(
                movie=movie,
                weekend_of=(row.get("weekend_of") or "").strip(),
                genre=_clean(row.get("genre")),
                audience_type=_clean(row.get("audience_type")),
                franchise_type=_clean(row.get("franchise_type")),
                rating=(row.get("rating") or "").strip().upper(),
                notes=(row.get("notes") or "").strip(),
            )
            metadata[movie.lower()] = item
    return metadata


def metadata_for_movie(movie: str,
                       metadata: dict[str, TargetMetadata]) -> TargetMetadata | None:
    needle = movie.lower()
    if needle in metadata:
        return metadata[needle]
    for key, item in metadata.items():
        if needle in key or key in needle:
            return item
    return None


def score_comp(target: TargetMetadata, comp: HistoricalComp) -> float:
    """Score a comp by metadata similarity.

    The base weight keeps imperfect comps in the distribution, while exact
    genre/audience/franchise/rating matches dominate the estimate.
    """
    score = 0.25
    if target.genre and target.genre == comp.genre:
        score += 4.0
    elif target.genre and comp.genre and target.genre.split("_")[0] == comp.genre.split("_")[0]:
        score += 1.0
    if target.audience_type and target.audience_type == comp.audience_type:
        score += 2.0
    if target.franchise_type and target.franchise_type == comp.franchise_type:
        score += 1.25
    if target.rating and target.rating == comp.rating:
        score += 0.75
    return score


def _weighted_average(values: list[tuple[float, float]]) -> float:
    total_weight = sum(weight for _, weight in values)
    if total_weight <= 0:
        return 0.0
    return sum(value * weight for value, weight in values) / total_weight


def _weighted_quantile(values: list[tuple[float, float]], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values, key=lambda item: item[0])
    total_weight = sum(weight for _, weight in ordered)
    if total_weight <= 0:
        return ordered[len(ordered) // 2][0]
    threshold = total_weight * quantile
    running = 0.0
    for value, weight in ordered:
        running += weight
        if running >= threshold:
            return value
    return ordered[-1][0]


def estimate_opening_weekend_from_thursday(
    thursday_gross_m: float,
    target: TargetMetadata,
    comps: list[HistoricalComp],
    *,
    max_comps: int = 8,
    baseline_thursday_share: float | None = None,
    baseline_prior_comps: float = 20.0,
) -> CompEstimate:
    """Estimate opening weekend from Thursday gross and historical comps."""
    eligible = [
        (comp, score_comp(target, comp))
        for comp in comps
        if comp.thursday_share > 0
    ]
    eligible.sort(key=lambda item: item[1], reverse=True)
    selected = eligible[:max_comps]
    if not selected:
        raise ValueError("No valid historical comps available")

    share_values = [(comp.thursday_share, weight) for comp, weight in selected]
    weighted_share = _weighted_average(share_values)
    low_share = _weighted_quantile(share_values, 0.75)
    high_share = _weighted_quantile(share_values, 0.25)

    mid = thursday_gross_m / weighted_share if weighted_share else 0.0
    low = thursday_gross_m / low_share if low_share else mid
    high = thursday_gross_m / high_share if high_share else mid

    adjusted_share = None
    adjusted_mid = None
    comp_influence = 1.0
    if baseline_thursday_share and baseline_thursday_share > 0:
        comp_influence = len(selected) / (len(selected) + baseline_prior_comps)
        adjusted_share = (
            weighted_share * comp_influence
            + baseline_thursday_share * (1 - comp_influence)
        )
        adjusted_mid = thursday_gross_m / adjusted_share if adjusted_share else None

    return CompEstimate(
        movie=target.movie,
        thursday_gross_m=thursday_gross_m,
        mid_m=mid,
        low_m=min(low, high),
        high_m=max(low, high),
        weighted_thursday_share=weighted_share,
        low_share=min(low_share, high_share),
        high_share=max(low_share, high_share),
        comps=[comp for comp, _ in selected],
        weights={comp.movie: weight for comp, weight in selected},
        baseline_thursday_share=baseline_thursday_share,
        adjusted_thursday_share=adjusted_share,
        adjusted_mid_m=adjusted_mid,
        comp_influence=comp_influence,
    )


def estimate_from_prediction(
    prediction: dict,
    target: TargetMetadata,
    comps: list[HistoricalComp],
    *,
    baseline_thursday_share: float | None = None,
    baseline_prior_comps: float = 20.0,
) -> CompEstimate:
    """Build a comp estimate from predict.py output.

    Uses the predicted Thursday daily gross, not the model's full-weekend
    projection, so the comp layer answers the Thursday-preview question.
    """
    details = prediction.get("daily_details", {}).get("Thursday")
    if not details:
        raise ValueError("Prediction does not contain Thursday daily details")
    thursday_gross_m = float(details.get("domestic_mid", 0) or 0) / 1_000_000
    return estimate_opening_weekend_from_thursday(
        thursday_gross_m,
        target,
        comps,
        baseline_thursday_share=baseline_thursday_share,
        baseline_prior_comps=baseline_prior_comps,
    )
