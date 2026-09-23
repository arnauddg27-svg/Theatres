"""Estimate a theatre subset's revenue importance from strictly earlier films.

Only used when no same-film measured expansion is available. Shrink toward an
equal-theatre sample and abstain when the reference or training support is weak.
"""
from collections import defaultdict
from datetime import date, timedelta
from functools import lru_cache
import json
from math import isfinite
from pathlib import Path
from statistics import mean, median

MIN_FILMS = 8
SHRINK_FILMS = 5


def make_profile(movie, weekend, available_date, daily_revenues):
    values = defaultdict(list)
    for revenues in daily_revenues:
        clean = {t: float(v) for t, v in revenues.items() if isfinite(float(v)) and float(v) >= 0}
        if len(clean) < 250 or sum(clean.values()) <= 0:
            continue
        avg = mean(clean.values())
        for name, revenue in clean.items():
            values[name].append(revenue / avg)
    if not values:
        return None
    return {"movie": movie, "weekend_of": weekend, "available_date": available_date,
            "weights": {name: round(mean(vs), 6) for name, vs in values.items()}}


def fit(profiles, cutoff):
    values = defaultdict(list)
    movies = set()
    for profile in profiles:
        if (not profile.get("weekend_of") or not profile.get("available_date")
                or profile["weekend_of"] >= cutoff or profile["available_date"] >= cutoff
                or profile.get("movie") in movies):
            continue
        movies.add(profile["movie"])
        for name, value in profile.get("weights", {}).items():
            if isinstance(value, (int, float)) and isfinite(value) and value >= 0:
                values[name].append(value)
    if len(movies) < MIN_FILMS:
        return {}, len(movies)
    weights = {name: (len(vs) * median(vs) + SHRINK_FILMS) / (len(vs) + SHRINK_FILMS)
               for name, vs in values.items() if len(vs) >= 3}
    return weights, len(movies)


@lru_cache(maxsize=128)
def _load_fit(path, mtime_ns, cutoff):
    return fit(json.loads(Path(path).read_text()).get("profiles", []), cutoff)


def expansion(sample_names, reference_names, expected_count, date_str, profile_path):
    """Return (expansion, support) or None; unknown theatres get neutral weight."""
    sample, reference = set(sample_names), set(reference_names)
    if not sample or not reference or expected_count <= 0:
        return None
    try:
        day = date.fromisoformat(date_str)
        friday = day + timedelta(days=4 - day.weekday())
        path = Path(profile_path)
        weights, n = _load_fit(str(path), path.stat().st_mtime_ns, friday.isoformat())
    except (OSError, ValueError, TypeError):
        return None
    if not weights or len(sample & weights.keys()) / len(sample) < .8:
        return None
    # Config can contain newly added venues beyond the calibrated reference
    # fleet. Prefer the known historical cohort when it matches that fleet.
    known_reference = reference & weights.keys()
    if .9 <= len(known_reference) / expected_count <= 1.1:
        reference = known_reference
    elif not .9 <= len(reference) / expected_count <= 1.1:
        return None
    mass = sum(weights.get(t, 1.0) for t in sample)
    total = sum(weights.get(t, 1.0) for t in reference) * expected_count / len(reference)
    if mass <= 0:
        return None
    return max(1.0, total / mass), n
