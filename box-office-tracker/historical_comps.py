#!/usr/bin/env python3
"""Historical-comp helpers for opening-weekend model research.

This module is intentionally read-only. It does not touch scraping, workflow
scheduling, seat-count collection, or live prediction defaults. It estimates an
opening weekend from a Thursday-preview gross by comparing the target movie to
historical films with similar genre/audience metadata.
"""

from __future__ import annotations

import csv
import math
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
    friday_m: float = 0.0
    saturday_m: float = 0.0
    sunday_m: float = 0.0
    source_url: str = ""
    notes: str = ""
    release_year: int | None = None
    daily_source_url: str = ""
    daily_notes: str = ""
    imdb_rating: float = 0.0
    imdb_votes: int = 0
    imdb_url: str = ""
    rt_audience_score: int = 0
    rt_audience_score_type: str = ""
    rt_url: str = ""

    @property
    def thursday_share(self) -> float:
        if self.opening_weekend_m <= 0:
            return 0.0
        return self.thursday_preview_m / self.opening_weekend_m

    @property
    def is_post_covid(self) -> bool:
        return self.release_year is not None and self.release_year >= 2021

    @property
    def has_daily_breakdown(self) -> bool:
        return self.friday_m > 0 and self.saturday_m > 0 and self.sunday_m > 0

    @property
    def daily_shares(self) -> dict[str, float]:
        if self.opening_weekend_m <= 0 or not self.has_daily_breakdown:
            return {}
        return {
            "Friday": self.friday_m / self.opening_weekend_m,
            "Saturday": self.saturday_m / self.opening_weekend_m,
            "Sunday": self.sunday_m / self.opening_weekend_m,
        }


@dataclass(frozen=True)
class TargetMetadata:
    movie: str
    genre: str
    audience_type: str
    franchise_type: str
    rating: str
    weekend_of: str = ""
    notes: str = ""
    imdb_rating: float = 0.0
    imdb_votes: int = 0
    rt_audience_score: int = 0
    rt_audience_score_type: str = ""


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
    daily_shares: dict[str, float]
    daily_projection_m: dict[str, float]
    comps: list[HistoricalComp]
    weights: dict[str, float]
    baseline_thursday_share: float | None = None
    adjusted_thursday_share: float | None = None
    adjusted_mid_m: float | None = None
    comp_influence: float = 1.0
    audience_adjusted_thursday_share: float | None = None
    audience_adjusted_mid_m: float | None = None
    audience_regression_factor: float = 1.0
    audience_regression_n: int = 0
    audience_regression_r2: float | None = None
    audience_regression_features: dict[str, float] | None = None


def _clean(value: str | None) -> str:
    return (value or "").strip().lower().replace(" ", "_")


def _movie_key(value: str | None) -> str:
    return "".join(ch for ch in (value or "").lower() if ch.isalnum())


def _float(row: dict, key: str) -> float:
    raw = (row.get(key) or "").strip()
    return float(raw) if raw else 0.0


def _int(row: dict, key: str) -> int | None:
    raw = (row.get(key) or "").strip()
    return int(raw) if raw else None


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
                friday_m=_float(row, "friday_m"),
                saturday_m=_float(row, "saturday_m"),
                sunday_m=_float(row, "sunday_m"),
                source_url=(row.get("source_url") or "").strip(),
                notes=(row.get("notes") or "").strip(),
                release_year=_int(row, "release_year"),
                daily_source_url=(row.get("daily_source_url") or "").strip(),
                daily_notes=(row.get("daily_notes") or "").strip(),
                imdb_rating=_float(row, "imdb_rating"),
                imdb_votes=_int(row, "imdb_votes") or 0,
                imdb_url=(row.get("imdb_url") or "").strip(),
                rt_audience_score=_int(row, "rt_audience_score") or 0,
                rt_audience_score_type=(row.get("rt_audience_score_type") or "").strip(),
                rt_url=(row.get("rt_url") or "").strip(),
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
                imdb_rating=_float(row, "imdb_rating"),
                imdb_votes=_int(row, "imdb_votes") or 0,
                rt_audience_score=_int(row, "rt_audience_score") or 0,
                rt_audience_score_type=(row.get("rt_audience_score_type") or "").strip(),
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


def _audience_feature_values(item) -> dict[str, float]:
    values = {}
    imdb_rating = float(getattr(item, "imdb_rating", 0) or 0)
    rt_audience_score = int(getattr(item, "rt_audience_score", 0) or 0)
    if imdb_rating > 0:
        values["imdb_rating"] = imdb_rating
    if rt_audience_score > 0:
        # RT critic scores are intentionally not modeled; this is audience only.
        values["rt_audience_score"] = rt_audience_score / 10.0
    return values


def _solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float] | None:
    n = len(vector)
    aug = [row[:] + [vector[idx]] for idx, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) < 1e-12:
            return None
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        pivot_val = aug[col][col]
        aug[col] = [value / pivot_val for value in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor:
                aug[row] = [
                    aug[row][idx] - factor * aug[col][idx]
                    for idx in range(n + 1)
                ]
    return [aug[row][-1] for row in range(n)]


def _weighted_ridge_regression(rows, feature_names, ridge=1.0):
    if len(rows) < max(5, len(feature_names) + 3):
        return None

    raw_features = [
        [features[name] for name in feature_names]
        for features, _, _ in rows
    ]
    means = [
        sum(values[col] for values in raw_features) / len(raw_features)
        for col in range(len(feature_names))
    ]
    stds = []
    for col, mean in enumerate(means):
        var = sum((values[col] - mean) ** 2 for values in raw_features) / len(raw_features)
        stds.append(math.sqrt(var) or 1.0)

    design = []
    y_values = []
    weights = []
    for features, y, weight in rows:
        design.append(
            [1.0]
            + [
                (features[name] - means[idx]) / stds[idx]
                for idx, name in enumerate(feature_names)
            ]
        )
        y_values.append(y)
        weights.append(max(float(weight or 0), 0.01))

    n_features = len(feature_names) + 1
    xtwx = [[0.0 for _ in range(n_features)] for _ in range(n_features)]
    xtwy = [0.0 for _ in range(n_features)]
    for row, y, weight in zip(design, y_values, weights):
        for i in range(n_features):
            xtwy[i] += row[i] * y * weight
            for j in range(n_features):
                xtwx[i][j] += row[i] * row[j] * weight

    # Penalize score coefficients, not the intercept.
    for idx in range(1, n_features):
        xtwx[idx][idx] += ridge

    coefficients = _solve_linear_system(xtwx, xtwy)
    if coefficients is None:
        return None

    def predict(features):
        return coefficients[0] + sum(
            coefficients[idx + 1] * ((features[name] - means[idx]) / stds[idx])
            for idx, name in enumerate(feature_names)
        )

    y_mean = _weighted_average(list(zip(y_values, weights)))
    ss_tot = sum(weight * (y - y_mean) ** 2 for y, weight in zip(y_values, weights))
    ss_res = sum(
        weight * (y - predict(features)) ** 2
        for features, y, weight in rows
    )
    r2 = 0.0 if ss_tot <= 0 else max(0.0, min(1.0, 1 - ss_res / ss_tot))
    return predict, r2


def _audience_regression_adjustment(
    target: TargetMetadata,
    eligible: list[tuple[HistoricalComp, float]],
    selected: list[tuple[HistoricalComp, float]],
):
    target_features = _audience_feature_values(target)
    if not target_features:
        return None

    feature_names = [
        name for name in ("imdb_rating", "rt_audience_score")
        if name in target_features
    ]
    rows = []
    for comp, weight in eligible:
        comp_features = _audience_feature_values(comp)
        if not all(name in comp_features for name in feature_names):
            continue
        if comp.thursday_preview_m <= 0 or comp.opening_weekend_m <= 0:
            continue
        weekend_multiple = comp.opening_weekend_m / comp.thursday_preview_m
        if weekend_multiple <= 0:
            continue
        rows.append((comp_features, math.log(weekend_multiple), weight))

    model = _weighted_ridge_regression(rows, feature_names, ridge=1.0)
    if model is None:
        return None
    predict, r2 = model
    selected_predictions = []
    for comp, weight in selected:
        comp_features = _audience_feature_values(comp)
        if all(name in comp_features for name in feature_names):
            selected_predictions.append((predict(comp_features), weight))
    if not selected_predictions:
        return None

    target_log_multiple = predict(target_features)
    baseline_log_multiple = _weighted_average(selected_predictions)
    raw_factor = math.exp(target_log_multiple - baseline_log_multiple)
    factor = max(0.85, min(1.20, raw_factor))
    return {
        "factor": factor,
        "raw_factor": raw_factor,
        "n": len(rows),
        "r2": r2,
        "features": {
            "imdb_rating": float(getattr(target, "imdb_rating", 0) or 0),
            "rt_audience_score": float(getattr(target, "rt_audience_score", 0) or 0),
        },
    }


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


def _weighted_daily_shares(selected: list[tuple[HistoricalComp, float]]) -> dict[str, float]:
    daily_values = {"Friday": [], "Saturday": [], "Sunday": []}
    for comp, weight in selected:
        for day, share in comp.daily_shares.items():
            daily_values[day].append((share, weight))
    return {
        day: _weighted_average(values)
        for day, values in daily_values.items()
        if values
    }


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
    target_key = _movie_key(target.movie)
    eligible = [
        (comp, score_comp(target, comp))
        for comp in comps
        if comp.thursday_share > 0
        and _movie_key(comp.movie) != target_key
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
    daily_shares = _weighted_daily_shares(selected)
    daily_projection = {
        day: mid * share
        for day, share in daily_shares.items()
    }

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

    audience_adjustment = _audience_regression_adjustment(target, eligible, selected)
    audience_adjusted_share = None
    audience_adjusted_mid = None
    audience_factor = 1.0
    audience_n = 0
    audience_r2 = None
    audience_features = None
    if audience_adjustment:
        audience_factor = audience_adjustment["factor"]
        audience_adjusted_share = weighted_share / audience_factor if weighted_share else None
        audience_adjusted_mid = (
            thursday_gross_m / audience_adjusted_share
            if audience_adjusted_share else None
        )
        audience_n = audience_adjustment["n"]
        audience_r2 = audience_adjustment["r2"]
        audience_features = audience_adjustment["features"]

    return CompEstimate(
        movie=target.movie,
        thursday_gross_m=thursday_gross_m,
        mid_m=mid,
        low_m=min(low, high),
        high_m=max(low, high),
        weighted_thursday_share=weighted_share,
        low_share=min(low_share, high_share),
        high_share=max(low_share, high_share),
        daily_shares=daily_shares,
        daily_projection_m=daily_projection,
        comps=[comp for comp, _ in selected],
        weights={comp.movie: weight for comp, weight in selected},
        baseline_thursday_share=baseline_thursday_share,
        adjusted_thursday_share=adjusted_share,
        adjusted_mid_m=adjusted_mid,
        comp_influence=comp_influence,
        audience_adjusted_thursday_share=audience_adjusted_share,
        audience_adjusted_mid_m=audience_adjusted_mid,
        audience_regression_factor=audience_factor,
        audience_regression_n=audience_n,
        audience_regression_r2=audience_r2,
        audience_regression_features=audience_features,
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
