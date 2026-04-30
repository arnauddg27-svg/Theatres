#!/usr/bin/env python3
"""Read-only historical-comp backtest runner.

This script compares the current seat/Polymarket prediction with a separate
Thursday-preview historical-comp estimate. It does not write data and does not
touch the scraper.
"""

from __future__ import annotations

import argparse
import sys

from historical_comps import (
    DEFAULT_COMPS_CSV,
    DEFAULT_METADATA_CSV,
    estimate_from_prediction,
    load_historical_comps,
    load_movie_metadata,
    metadata_for_movie,
)
from predict import (
    active_model_cohorts,
    filter_seat_data_through,
    get_day_weights,
    load_calibration,
    load_frozen_calibration,
    load_polymarket_data,
    load_seat_data,
    load_theatre_counts,
    national_theatre_count_for_movie,
    predict_movie,
)


def _fmt_m(value: float) -> str:
    return f"${value:.1f}M"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare live prediction output with a historical-comp Thursday estimate.",
    )
    parser.add_argument("--movie", required=True, help="Movie title to backtest")
    parser.add_argument(
        "--calibration-freeze",
        help="Pre-actual calibration freeze weekend, e.g. 2026-04-24",
    )
    parser.add_argument(
        "--through-date",
        help="Ignore seat and Polymarket rows after YYYY-MM-DD",
    )
    parser.add_argument(
        "--actual",
        type=float,
        help="Optional actual opening weekend gross in millions for error display",
    )
    parser.add_argument("--comps", default=str(DEFAULT_COMPS_CSV))
    parser.add_argument("--metadata", default=str(DEFAULT_METADATA_CSV))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    metadata = load_movie_metadata(args.metadata)
    target = metadata_for_movie(args.movie, metadata)
    if not target:
        print(f"No metadata found for {args.movie!r}. Add it to {args.metadata}.")
        return 1

    comps = load_historical_comps(args.comps)
    if not comps:
        print(f"No historical comps found in {args.comps}.")
        return 1

    weekend_of = args.calibration_freeze or target.weekend_of or None
    cal = load_frozen_calibration(args.calibration_freeze) if args.calibration_freeze else load_calibration()
    seat_data = load_seat_data(weekend_of=weekend_of)
    seat_data = filter_seat_data_through(seat_data, args.through_date)
    poly_data = load_polymarket_data(weekend_of=weekend_of, through_date=args.through_date)
    theatre_counts = load_theatre_counts()

    movie_match = None
    for movie in seat_data:
        if args.movie.lower() in movie.lower():
            movie_match = movie
            break
    if not movie_match:
        print(f"No seat data found for {args.movie!r}.")
        return 1

    nat_count = national_theatre_count_for_movie(movie_match, theatre_counts)
    prediction = predict_movie(
        movie_match,
        seat_data[movie_match],
        poly_data.get(movie_match, []),
        cal,
        national_theatre_count=nat_count,
    )
    if not prediction:
        print(f"Could not build prediction for {movie_match!r}.")
        return 1

    day_weights = get_day_weights(cal)
    baseline_thursday_share = float(day_weights.get("Thursday", 0) or 0)
    comp_estimate = estimate_from_prediction(
        prediction,
        target,
        comps,
        baseline_thursday_share=baseline_thursday_share,
    )

    print("\nHistorical Comp Backtest")
    print("=" * 70)
    print(f"Movie: {movie_match}")
    if weekend_of:
        print(f"Weekend: {weekend_of}")
    if args.calibration_freeze:
        print(f"Calibration freeze: {args.calibration_freeze}")
    if args.through_date:
        print(f"Data through: {args.through_date}")
    print(f"Theatre cohorts: {', '.join(sorted(active_model_cohorts()))}")
    print()
    print(f"Current model:     {_fmt_m(prediction['blended_m'])}")
    print(f"Seat-only model:   {_fmt_m(prediction['seat_mid_m'])}")
    print(
        f"Comp-only model:   {_fmt_m(comp_estimate.mid_m)} "
        f"({_fmt_m(comp_estimate.low_m)} - {_fmt_m(comp_estimate.high_m)})"
    )
    if comp_estimate.adjusted_mid_m is not None:
        print(
            f"Comp-adjusted:     {_fmt_m(comp_estimate.adjusted_mid_m)} "
            f"(baseline Thu share {comp_estimate.baseline_thursday_share:.1%}, "
            f"comp influence {comp_estimate.comp_influence:.0%})"
        )
    print(f"Thursday gross:    {_fmt_m(comp_estimate.thursday_gross_m)}")
    print(f"Comp Thu share:    {comp_estimate.weighted_thursday_share:.1%}")
    if args.actual:
        adjusted_mid = (
            comp_estimate.adjusted_mid_m
            if comp_estimate.adjusted_mid_m is not None
            else comp_estimate.mid_m
        )
        print(f"Actual:            {_fmt_m(args.actual)}")
        print(f"Current error:     {prediction['blended_m'] - args.actual:+.1f}M")
        print(f"Comp-only error:   {comp_estimate.mid_m - args.actual:+.1f}M")
        print(f"Adjusted error:    {adjusted_mid - args.actual:+.1f}M")
    print()
    print("Top comps:")
    for comp in comp_estimate.comps[:5]:
        weight = comp_estimate.weights.get(comp.movie, 0)
        print(
            f"  {comp.movie:<32} "
            f"Thu share={comp.thursday_share:>5.1%} "
            f"weight={weight:>4.2f}"
        )
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
