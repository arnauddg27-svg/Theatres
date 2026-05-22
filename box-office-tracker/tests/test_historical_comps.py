import unittest
from pathlib import Path
import contextlib
import io
import os
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import comp_backtest
from historical_comps import (
    DEFAULT_COMPS_CSV,
    HistoricalComp,
    TargetMetadata,
    _fit_weighted_regression_factor,
    estimate_from_prediction,
    estimate_opening_weekend_from_thursday,
    load_historical_comps,
    load_movie_metadata,
    metadata_for_movie,
)
from predict import (
    CORE_COHORT,
    EXPANSION_COHORT,
    active_model_cohorts,
    attach_comp_model_prediction,
    learned_local_thursday_share,
)


class HistoricalCompsTest(unittest.TestCase):
    def test_feature_regression_shrinks_low_fit_adjustments(self):
        weak_factor, weak_weight = _fit_weighted_regression_factor(
            raw_factor=0.85,
            r2=0.01,
        )
        strong_factor, strong_weight = _fit_weighted_regression_factor(
            raw_factor=1.20,
            r2=0.81,
        )

        self.assertGreater(weak_factor, 0.98)
        self.assertLess(weak_weight, 0.20)
        self.assertGreater(strong_factor, 1.15)
        self.assertGreater(strong_weight, 0.85)

    def test_backtest_labels_seat_primary_instead_of_market_blend(self):
        line = comp_backtest.model_context_line({
            "poly_result": {"ev": 70.0},
            "blended_m": 76.5,
            "seat_primary_mid_m": 76.5,
        })

        self.assertEqual(("Seat primary", 76.5), line)

    def test_backtest_passes_as_of_side_inputs_to_current_model(self):
        target = types.SimpleNamespace(
            movie="Target Movie",
            weekend_of="2026-05-15",
        )
        comp = types.SimpleNamespace(
            movie="Comp Movie",
            thursday_share=0.10,
            has_daily_breakdown=True,
        )
        estimate = types.SimpleNamespace(
            mid_m=10.0,
            low_m=8.0,
            high_m=12.0,
            adjusted_mid_m=None,
            thursday_gross_m=1.0,
            weighted_thursday_share=0.10,
            daily_projection_m={},
            daily_shares={},
            comps=[comp],
            weights={"Comp Movie": 1.0},
        )
        captured = {}
        patches = {
            "load_movie_metadata": lambda _path: {"Target Movie": target},
            "metadata_for_movie": lambda movie, metadata: target,
            "load_historical_comps": lambda _path: [comp],
            "load_frozen_calibration": lambda _weekend: {"calibration_factors": {}},
            "load_seat_data": lambda weekend_of=None: {
                "Target Movie": {
                    "2026-05-15": [{
                        "movie_title": "Target Movie",
                        "weekend_of": "2026-05-15",
                        "day_of_week": "Friday",
                    }],
                },
            },
            "filter_seat_data_through": lambda data, through_date=None: data,
            "load_polymarket_data": lambda weekend_of=None, through_date=None: {},
            "load_pre_reservation_data": lambda weekend_of=None, through_date=None: (
                captured.__setitem__("snapshot_loader", (weekend_of, through_date))
                or {"Target Movie": {"2026-05-16": []}}
            ),
            "load_social_signal_data": lambda weekend_of=None, through_date=None: (
                captured.__setitem__("social_loader", (weekend_of, through_date))
                or {"Target Movie": {"factor": 1.0}}
            ),
            "load_daily_actual_overrides": lambda weekend_of=None, through_date=None: (
                captured.__setitem__("actual_loader", (weekend_of, through_date))
                or {"Target Movie": {"Friday": {"gross_m": 6.6}}}
            ),
            "load_showtime_link_daypart_profiles": lambda weekend_of=None: (
                captured.__setitem__("links_loader", weekend_of)
                or {"Target Movie": {"2026-05-16": {}}}
            ),
            "load_theatre_counts": lambda: {},
            "national_theatre_count_for_movie": lambda movie, counts, metadata=None: 2615,
            "get_day_weights": lambda cal: {"Thursday": 0.1},
            "estimate_from_prediction": lambda prediction, target, comps, baseline_thursday_share=0.0: estimate,
            "regression_prediction_values": lambda prediction: (10.0, 8.0, 12.0),
            "active_model_cohorts": lambda: {"core"},
        }

        def fake_predict_movie(movie, seat_data, poly_data, cal, **kwargs):
            captured["predict_kwargs"] = kwargs
            return {
                "seat_mid_m": 9.0,
                "blended_m": 9.0,
                "daily_details": {},
            }

        patches["predict_movie"] = fake_predict_movie
        originals = {
            name: getattr(comp_backtest, name)
            for name in patches
        }
        for name, value in patches.items():
            setattr(comp_backtest, name, value)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = comp_backtest.main([
                    "--movie",
                    "Target",
                    "--calibration-freeze",
                    "2026-05-15",
                    "--through-date",
                    "2026-05-16",
                ])
        finally:
            for name, value in originals.items():
                setattr(comp_backtest, name, value)

        self.assertEqual(0, rc)
        self.assertEqual(("2026-05-15", "2026-05-16"), captured["snapshot_loader"])
        self.assertEqual(("2026-05-15", "2026-05-16"), captured["social_loader"])
        self.assertEqual(("2026-05-15", "2026-05-16"), captured["actual_loader"])
        self.assertEqual("2026-05-15", captured["links_loader"])
        self.assertEqual({"2026-05-16": []}, captured["predict_kwargs"]["snapshot_data"])
        self.assertEqual(
            {"Target Movie": {"Friday": {"gross_m": 6.6}}},
            captured["predict_kwargs"]["daily_actual_overrides"],
        )
        self.assertEqual(
            {"2026-05-16": {}},
            captured["predict_kwargs"]["showtime_link_profiles"],
        )

    def test_estimate_weights_matching_music_biopic_comps(self):
        target = TargetMetadata(
            movie="Michael",
            genre="music_biopic",
            audience_type="broad_legacy",
            franchise_type="biopic",
            rating="PG-13",
        )
        comps = [
            HistoricalComp("Close Match", "music_biopic", "broad_legacy", "biopic", "PG-13", 4.0, 40.0),
            HistoricalComp("Weak Match", "horror", "fan_driven", "original", "R", 4.0, 80.0),
        ]

        estimate = estimate_opening_weekend_from_thursday(10.0, target, comps)

        self.assertEqual(["Close Match", "Weak Match"], [c.movie for c in estimate.comps])
        self.assertGreater(estimate.weights["Close Match"], estimate.weights["Weak Match"])
        self.assertLess(estimate.mid_m, 125.0)
        self.assertGreater(estimate.mid_m, 90.0)

    def test_estimate_excludes_target_movie_from_its_own_comps(self):
        target = TargetMetadata(
            movie="The Devil Wears Prada 2",
            genre="comedy",
            audience_type="female_skewing",
            franchise_type="sequel",
            rating="PG-13",
        )
        comps = [
            HistoricalComp(
                "The Devil Wears Prada 2",
                "comedy",
                "female_skewing",
                "sequel",
                "PG-13",
                10.0,
                77.0,
            ),
            HistoricalComp(
                "Independent Comp",
                "comedy",
                "female_skewing",
                "sequel",
                "PG-13",
                5.0,
                50.0,
            ),
        ]

        estimate = estimate_opening_weekend_from_thursday(10.0, target, comps)

        self.assertEqual(["Independent Comp"], [comp.movie for comp in estimate.comps])
        self.assertAlmostEqual(100.0, estimate.mid_m, places=6)

    def test_estimate_from_prediction_uses_thursday_daily_gross(self):
        target = TargetMetadata(
            movie="Michael",
            genre="music_biopic",
            audience_type="broad_legacy",
            franchise_type="biopic",
            rating="PG-13",
        )
        comps = [
            HistoricalComp("Comp", "music_biopic", "broad_legacy", "biopic", "PG-13", 5.0, 50.0),
        ]
        prediction = {
            "daily_details": {
                "Thursday": {
                    "domestic_mid": 12_000_000,
                }
            },
            "blended_m": 90.0,
        }

        estimate = estimate_from_prediction(prediction, target, comps)

        self.assertAlmostEqual(120.0, estimate.mid_m, places=6)

    def test_estimate_projects_reported_opening_weekend_daily_shape(self):
        target = TargetMetadata(
            movie="Michael",
            genre="music_biopic",
            audience_type="broad_legacy",
            franchise_type="biopic",
            rating="PG-13",
        )
        comps = [
            HistoricalComp(
                "Daily Comp",
                "music_biopic",
                "broad_legacy",
                "biopic",
                "PG-13",
                10.0,
                100.0,
                friday_m=45.0,
                saturday_m=35.0,
                sunday_m=20.0,
            ),
        ]

        estimate = estimate_opening_weekend_from_thursday(12.0, target, comps)

        self.assertAlmostEqual(120.0, estimate.mid_m, places=6)
        self.assertAlmostEqual(0.45, estimate.daily_shares["Friday"], places=6)
        self.assertAlmostEqual(54.0, estimate.daily_projection_m["Friday"], places=6)
        self.assertAlmostEqual(42.0, estimate.daily_projection_m["Saturday"], places=6)
        self.assertAlmostEqual(24.0, estimate.daily_projection_m["Sunday"], places=6)

    def test_baseline_share_shrinks_sparse_comp_estimate(self):
        target = TargetMetadata(
            movie="Michael",
            genre="music_biopic",
            audience_type="broad_legacy",
            franchise_type="biopic",
            rating="PG-13",
        )
        comps = [
            HistoricalComp("Low Share Comp", "music_biopic", "broad_legacy", "biopic", "PG-13", 5.0, 100.0),
        ]

        estimate = estimate_opening_weekend_from_thursday(
            12.0,
            target,
            comps,
            baseline_thursday_share=0.12,
        )

        self.assertAlmostEqual(240.0, estimate.mid_m, places=6)
        self.assertIsNotNone(estimate.adjusted_mid_m)
        self.assertLess(estimate.adjusted_mid_m, estimate.mid_m)
        self.assertAlmostEqual(1 / 21, estimate.comp_influence, places=6)

    def test_default_database_has_post_covid_depth_without_michael_leakage(self):
        comps = load_historical_comps(DEFAULT_COMPS_CSV)
        names = {comp.movie.lower() for comp in comps}
        post_covid = [comp for comp in comps if comp.is_post_covid]

        self.assertGreaterEqual(len(comps), 70)
        self.assertGreaterEqual(len(post_covid), 60)
        self.assertGreaterEqual(
            sum(1 for comp in comps if comp.has_daily_breakdown),
            5,
        )
        self.assertNotIn("michael", names)
        self.assertTrue(all(comp.thursday_preview_m > 0 for comp in comps))
        self.assertTrue(all(comp.opening_weekend_m > 0 for comp in comps))

    def test_post_covid_comp_database_has_daily_breakdowns(self):
        comps = load_historical_comps(DEFAULT_COMPS_CSV)
        self.assertTrue(comps)
        self.assertTrue(all(comp.is_post_covid for comp in comps))
        missing = [
            comp.movie
            for comp in comps
            if not comp.has_daily_breakdown
        ]
        self.assertEqual([], missing)

    def test_comp_database_has_audience_score_references(self):
        comps = load_historical_comps(DEFAULT_COMPS_CSV)
        self.assertTrue(comps)
        missing = [
            comp.movie
            for comp in comps
            if (
                comp.imdb_rating <= 0
                or comp.imdb_votes <= 0
                or not comp.imdb_url.startswith("https://www.imdb.com/title/tt")
                or comp.rt_audience_score <= 0
                or not comp.rt_url.startswith("https://www.rottentomatoes.com/m/")
            )
        ]
        self.assertEqual([], missing)

    def test_comp_database_has_relishmix_social_references(self):
        comps = load_historical_comps(DEFAULT_COMPS_CSV)
        social_comps = [
            comp
            for comp in comps
            if comp.social_media_universe_m > 0
            and comp.social_source_url.startswith("https://www.relishmix.com/")
        ]

        self.assertGreaterEqual(len(social_comps), 15)

    def test_relishmix_social_backfill_uses_specific_movie_pages(self):
        comps = {
            comp.movie: comp
            for comp in load_historical_comps(DEFAULT_COMPS_CSV)
        }

        self.assertAlmostEqual(575.5, comps["Dune: Part Two"].social_media_universe_m)
        self.assertEqual(
            "https://www.relishmix.com/dune-2",
            comps["Dune: Part Two"].social_source_url,
        )
        self.assertAlmostEqual(246.8, comps["Alien: Romulus"].social_media_universe_m)
        self.assertEqual(
            "",
            comps[
                "Demon Slayer -Kimetsu no Yaiba- The Movie: Infinity Castle"
            ].social_source_url,
        )

    def test_audience_regression_uses_imdb_and_rt_audience_scores(self):
        target = TargetMetadata(
            movie="High Audience Sequel",
            genre="comedy",
            audience_type="female_skewing",
            franchise_type="sequel",
            rating="PG-13",
            imdb_rating=8.0,
            rt_audience_score=95,
        )
        comps = [
            HistoricalComp("Low 1", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 70.0,
                           imdb_rating=5.5, imdb_votes=20_000, rt_audience_score=50),
            HistoricalComp("Low 2", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 75.0,
                           imdb_rating=5.8, imdb_votes=25_000, rt_audience_score=58),
            HistoricalComp("Mid 1", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 100.0,
                           imdb_rating=6.6, imdb_votes=35_000, rt_audience_score=76),
            HistoricalComp("Mid 2", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 105.0,
                           imdb_rating=6.8, imdb_votes=40_000, rt_audience_score=80),
            HistoricalComp("High 1", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 130.0,
                           imdb_rating=8.0, imdb_votes=50_000, rt_audience_score=94),
            HistoricalComp("High 2", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 135.0,
                           imdb_rating=8.2, imdb_votes=55_000, rt_audience_score=97),
        ]

        estimate = estimate_opening_weekend_from_thursday(10.0, target, comps, max_comps=6)

        self.assertGreater(estimate.audience_regression_factor, 1.05)
        self.assertGreater(estimate.audience_adjusted_mid_m, estimate.mid_m)
        self.assertLess(estimate.audience_adjusted_thursday_share, estimate.weighted_thursday_share)
        self.assertEqual(6, estimate.audience_regression_n)
        self.assertGreaterEqual(estimate.audience_regression_r2, 0.0)
        self.assertIn("imdb_rating", estimate.audience_regression_features)
        self.assertIn("rt_audience_score", estimate.audience_regression_features)

    def test_movie_metadata_loads_national_theatre_count(self):
        path = Path(__file__).with_name("tmp-metadata-theatres.csv")
        try:
            path.write_text(
                "movie,weekend_of,genre,audience_type,franchise_type,rating,notes,"
                "imdb_rating,imdb_votes,rt_audience_score,rt_audience_score_type,"
                "national_theatre_count\n"
                "Future Movie,2026-05-15,horror,horror_fan,original,R,,"
                "6.1,1000,74,VERIFIED,2615\n"
            )

            metadata = load_movie_metadata(path)
        finally:
            path.unlink(missing_ok=True)

        target = metadata["future movie"]
        self.assertEqual(2615, target.national_theatre_count)

    def test_historical_comps_load_national_theatre_count(self):
        path = Path(__file__).with_name("tmp-comps-theatres.csv")
        try:
            path.write_text(
                "movie,release_year,genre,audience_type,franchise_type,rating,"
                "thursday_preview_m,opening_weekend_m,friday_m,saturday_m,sunday_m,"
                "national_theatre_count\n"
                "Comp Movie,2024,horror,horror_fan,original,R,"
                "4.0,28.0,12.0,9.0,7.0,2615\n"
            )

            comps = load_historical_comps(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertEqual(1, len(comps))
        self.assertEqual(2615, comps[0].national_theatre_count)

    def test_theatre_count_regression_uses_release_footprint(self):
        target = TargetMetadata(
            movie="Sub-Wide Horror",
            genre="horror",
            audience_type="horror_fan",
            franchise_type="original",
            rating="R",
            national_theatre_count=2000,
        )
        comps = [
            HistoricalComp(
                f"Comp {idx}",
                "horror",
                "horror_fan",
                "original",
                "R",
                5.0,
                weekend,
                national_theatre_count=theatres,
            )
            for idx, (theatres, weekend) in enumerate([
                (1800, 28.0),
                (2200, 33.0),
                (2600, 39.0),
                (3200, 48.0),
                (3800, 58.0),
                (4200, 66.0),
            ])
        ]

        estimate = estimate_opening_weekend_from_thursday(
            5.0,
            target,
            comps,
            max_comps=6,
        )

        self.assertLess(estimate.audience_regression_factor, 1.0)
        self.assertLess(estimate.audience_adjusted_mid_m, estimate.mid_m)
        self.assertIn(
            "release_footprint_factor",
            estimate.audience_regression_features["model_features"],
        )
        self.assertEqual(
            2000,
            estimate.audience_regression_features["national_theatre_count"],
        )
        self.assertAlmostEqual(
            0.90,
            estimate.audience_regression_features["release_footprint_factor"],
            places=6,
        )

    def test_theatre_count_normalizes_sparse_historical_prior(self):
        target = TargetMetadata(
            movie="Sub-Wide Horror",
            genre="horror",
            audience_type="horror_fan",
            franchise_type="original",
            rating="R",
            national_theatre_count=2000,
        )
        comps = [
            HistoricalComp(
                f"Wide Comp {idx}",
                "horror",
                "horror_fan",
                "original",
                "R",
                8.0,
                80.0,
                national_theatre_count=4000,
            )
            for idx in range(6)
        ]

        estimate = estimate_opening_weekend_from_thursday(
            8.0,
            target,
            comps,
            max_comps=6,
        )

        self.assertLess(estimate.prior_weekend_mid_m, 80.0)
        self.assertGreater(estimate.prior_weekend_mid_m, 70.0)
        self.assertLess(estimate.prior_footprint_factor, 1.0)
        self.assertGreater(estimate.prior_footprint_factor, 0.88)
        self.assertAlmostEqual(80.0, estimate.raw_prior_weekend_mid_m, places=6)

    def test_social_regression_uses_historical_smu_when_available(self):
        target = TargetMetadata(
            movie="High Buzz Sequel",
            genre="action",
            audience_type="fan_driven",
            franchise_type="sequel",
            rating="PG-13",
            social_media_universe_m=600.0,
        )
        comps = [
            HistoricalComp(
                f"Comp {idx}",
                "action",
                "fan_driven",
                "sequel",
                "PG-13",
                10.0,
                weekend,
                social_media_universe_m=smu,
            )
            for idx, (smu, weekend) in enumerate([
                (30.0, 70.0),
                (60.0, 76.0),
                (90.0, 82.0),
                (130.0, 90.0),
                (190.0, 100.0),
                (260.0, 112.0),
                (390.0, 125.0),
                (520.0, 140.0),
            ])
        ]

        estimate = estimate_opening_weekend_from_thursday(10.0, target, comps, max_comps=8)

        self.assertGreater(estimate.audience_regression_factor, 1.02)
        self.assertEqual(8, estimate.audience_regression_n)
        self.assertIn(
            "log_social_media_universe_m",
            estimate.audience_regression_features["model_features"],
        )
        self.assertEqual(
            600.0,
            estimate.audience_regression_features["social_media_universe_m"],
        )

    def test_movie_metadata_loads_optional_audience_scores(self):
        with self.subTest("temporary metadata csv"):
            path = Path(__file__).with_name("tmp-metadata-audience.csv")
            try:
                path.write_text(
                    "movie,weekend_of,genre,audience_type,franchise_type,rating,notes,"
                    "imdb_rating,imdb_votes,rt_audience_score,rt_audience_score_type\n"
                    "Future Movie,2026-05-08,comedy,female_skewing,sequel,PG-13,,"
                    "7.8,1000,94,VERIFIED\n"
                )

                metadata = load_movie_metadata(path)
            finally:
                path.unlink(missing_ok=True)

        target = metadata["future movie"]
        self.assertAlmostEqual(7.8, target.imdb_rating)
        self.assertEqual(1000, target.imdb_votes)
        self.assertEqual(94, target.rt_audience_score)
        self.assertEqual("VERIFIED", target.rt_audience_score_type)

    def test_prediction_can_attach_seat_comp_model(self):
        prediction = {
            "movie": "Michael",
            "seat_mid_m": 88.6,
            "seat_low_m": 84.0,
            "seat_high_m": 93.0,
            "daily_details": {
                "Thursday": {
                    "domestic_mid": 10_600_000,
                }
            },
        }
        metadata = {
            "michael": TargetMetadata(
                movie="Michael",
                genre="music_biopic",
                audience_type="broad_legacy",
                franchise_type="biopic",
                rating="PG-13",
            )
        }
        comps = [
            HistoricalComp(
                "Comp",
                "music_biopic",
                "broad_legacy",
                "biopic",
                "PG-13",
                11.0,
                100.0,
                friday_m=40.0,
                saturday_m=30.0,
                sunday_m=30.0,
            ),
        ]

        attach_comp_model_prediction(prediction, {}, metadata=metadata, comps=comps)

        self.assertAlmostEqual(96.363636, prediction["seat_comp_mid_m"], places=6)
        self.assertEqual("Thursday", prediction["seat_comp_basis"])
        self.assertEqual("Comp", prediction["seat_comp_top_comps"][0]["movie"])
        self.assertAlmostEqual(38.545454545, prediction["seat_comp_daily_m"]["Friday"], places=6)

    def test_prediction_uses_inferred_metadata_for_obvious_franchise_title(self):
        prediction = {
            "movie": "The Mandalorian and Grogu",
            "seat_mid_m": 120.0,
            "seat_low_m": 90.0,
            "seat_high_m": 150.0,
            "n_theatres_total": 426,
            "n_days": 1,
            "coverage_ratio": 0.25,
            "seat_data_quality": 0.12,
            "daily_details": {
                "Thursday": {
                    "domestic_mid": 8_000_000,
                }
            },
        }
        comps = [
            HistoricalComp(
                "Space Franchise",
                "sci_fi",
                "fan_driven",
                "franchise",
                "PG-13",
                10.0,
                100.0,
                friday_m=45.0,
                saturday_m=32.0,
                sunday_m=23.0,
            ),
            HistoricalComp(
                "Small Horror",
                "horror",
                "horror_fan",
                "original",
                "R",
                2.0,
                20.0,
                friday_m=9.0,
                saturday_m=6.0,
                sunday_m=5.0,
            ),
        ]

        attach_comp_model_prediction(prediction, {}, metadata={}, comps=comps)

        self.assertEqual("title_inferred", prediction["seat_comp_metadata_source"])
        self.assertEqual(
            "Space Franchise",
            prediction["seat_comp_top_comps"][0]["movie"],
        )
        self.assertLess(prediction["seat_primary_w_comp"], 0.80)
        self.assertGreater(prediction["seat_primary_w_direct"], 0.20)
        self.assertIn("seat-primary", prediction["regression_source"])

    def test_prediction_does_not_blend_polymarket_into_comp_model(self):
        prediction = {
            "movie": "Michael",
            "seat_mid_m": 88.6,
            "seat_low_m": 84.0,
            "seat_high_m": 93.0,
            "n_theatres_total": 100,
            "n_days": 1,
            "poly_result": {
                "ev": 80.0,
                "low": 70.0,
                "high": 90.0,
                "total_volume": 500_000,
            },
            "daily_details": {
                "Thursday": {
                    "domestic_mid": 10_000_000,
                }
            },
        }
        metadata = {
            "michael": TargetMetadata(
                movie="Michael",
                genre="music_biopic",
                audience_type="broad_legacy",
                franchise_type="biopic",
                rating="PG-13",
            )
        }
        comps = [
            HistoricalComp(
                "Comp",
                "music_biopic",
                "broad_legacy",
                "biopic",
                "PG-13",
                10.0,
                100.0,
            ),
        ]

        attach_comp_model_prediction(prediction, {}, metadata=metadata, comps=comps)

        self.assertAlmostEqual(100.0, prediction["seat_comp_mid_m"], places=6)
        self.assertAlmostEqual(100.0, prediction["comp_blended_m"], places=6)
        self.assertAlmostEqual(1.0, prediction["comp_w_model"], places=6)
        self.assertAlmostEqual(0.0, prediction["comp_w_poly"], places=6)
        self.assertAlmostEqual(100.0, prediction["comp_blend_low_m"], places=6)
        self.assertAlmostEqual(100.0, prediction["comp_blend_high_m"], places=6)

    def test_model_prediction_uses_regression_not_market_blend(self):
        prediction = {
            "movie": "Michael",
            "seat_mid_m": 88.6,
            "seat_low_m": 84.0,
            "seat_high_m": 93.0,
            "n_theatres_total": 400,
            "n_days": 1,
            "coverage_ratio": 1.0,
            "poly_result": {
                "ev": 60.0,
                "low": 50.0,
                "high": 70.0,
                "total_volume": 1_000_000,
            },
            "daily_details": {
                "Thursday": {
                    "domestic_mid": 10_000_000,
                }
            },
        }
        metadata = {
            "michael": TargetMetadata(
                movie="Michael",
                genre="music_biopic",
                audience_type="broad_legacy",
                franchise_type="biopic",
                rating="PG-13",
            )
        }
        comps = [
            HistoricalComp(
                "Comp",
                "music_biopic",
                "broad_legacy",
                "biopic",
                "PG-13",
                10.0,
                100.0,
            ),
        ]

        attach_comp_model_prediction(prediction, {}, metadata=metadata, comps=comps)

        self.assertAlmostEqual(96.58, prediction["regression_mid_m"], places=6)
        self.assertAlmostEqual(96.58, prediction["model_forecast_mid_m"], places=6)
        self.assertEqual("seat-primary-regression", prediction["regression_source"])
        self.assertFalse(prediction["regression_uses_polymarket"])
        self.assertNotIn("headline_mid_m", prediction)
        self.assertAlmostEqual(
            prediction["model_forecast_mid_m"],
            prediction["seat_primary_mid_m"],
            places=6,
        )

    def test_comp_model_reanchors_final_prediction_as_seat_primary(self):
        prediction = {
            "movie": "Michael",
            "seat_mid_m": 60.0,
            "seat_low_m": 50.0,
            "seat_high_m": 70.0,
            "blended_m": 55.0,
            "blend_low_m": 40.0,
            "blend_high_m": 80.0,
            "n_theatres_total": 400,
            "n_days": 1,
            "coverage_ratio": 1.0,
            "poly_result": {
                "ev": 40.0,
                "low": 35.0,
                "high": 45.0,
                "total_volume": 1_000_000,
            },
            "daily_details": {
                "Thursday": {
                    "domestic_mid": 10_000_000,
                }
            },
        }
        metadata = {
            "michael": TargetMetadata(
                movie="Michael",
                genre="music_biopic",
                audience_type="broad_legacy",
                franchise_type="biopic",
                rating="PG-13",
            )
        }
        comps = [
            HistoricalComp(
                "Comp",
                "music_biopic",
                "broad_legacy",
                "biopic",
                "PG-13",
                10.0,
                100.0,
            ),
        ]

        attach_comp_model_prediction(prediction, {}, metadata=metadata, comps=comps)

        self.assertAlmostEqual(88.0, prediction["seat_primary_mid_m"], places=6)
        self.assertAlmostEqual(0.70, prediction["seat_primary_w_comp"], places=6)
        self.assertAlmostEqual(88.0, prediction["blended_m"], places=6)
        self.assertAlmostEqual(1.0, prediction["w_seat"], places=6)
        self.assertAlmostEqual(0.0, prediction["w_poly"], places=6)

    def test_comp_model_uses_friday_only_when_thursday_is_missing(self):
        prediction = {
            "movie": "Partial Horror",
            "seat_mid_m": 9.0,
            "seat_low_m": 7.0,
            "seat_high_m": 12.0,
            "n_days": 1,
            "seat_data_quality": 0.45,
            "daily_details": {
                "Friday": {
                    "domestic_mid": 4_000_000,
                },
            },
        }
        metadata = {
            "partial horror": TargetMetadata(
                movie="Partial Horror",
                genre="horror",
                audience_type="horror_fan",
                franchise_type="original",
                rating="R",
            )
        }
        comps = [
            HistoricalComp(
                "Comp A",
                "horror",
                "horror_fan",
                "original",
                "R",
                2.0,
                20.0,
                friday_m=10.0,
                saturday_m=6.0,
                sunday_m=4.0,
            ),
            HistoricalComp(
                "Comp B",
                "horror",
                "horror_fan",
                "original",
                "R",
                3.0,
                30.0,
                friday_m=15.0,
                saturday_m=9.0,
                sunday_m=6.0,
            ),
        ]

        attach_comp_model_prediction(prediction, {}, metadata=metadata, comps=comps)

        self.assertEqual("Friday only", prediction["seat_comp_basis"])
        self.assertFalse(prediction["seat_comp_has_thursday_evidence"])
        self.assertAlmostEqual(10.0, prediction["seat_comp_mid_m"], places=6)
        self.assertAlmostEqual(0.40, prediction["seat_comp_evidence_share"], places=6)
        self.assertEqual("seat-primary-regression", prediction["regression_source"])

    def test_non_thursday_comp_model_applies_feature_adjustment_to_midpoint(self):
        def prediction():
            return {
                "movie": "High Audience Sequel",
                "seat_mid_m": 10.0,
                "seat_low_m": 9.0,
                "seat_high_m": 11.0,
                "daily_details": {
                    "Friday": {"domestic_mid": 4_000_000},
                },
            }

        base_metadata = {
            "high audience sequel": TargetMetadata(
                movie="High Audience Sequel",
                genre="comedy",
                audience_type="female_skewing",
                franchise_type="sequel",
                rating="PG-13",
            )
        }
        high_metadata = {
            "high audience sequel": TargetMetadata(
                movie="High Audience Sequel",
                genre="comedy",
                audience_type="female_skewing",
                franchise_type="sequel",
                rating="PG-13",
                imdb_rating=8.0,
                rt_audience_score=95,
            )
        }
        comps = [
            HistoricalComp("Low 1", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 70.0,
                           friday_m=35.0, saturday_m=20.0, sunday_m=15.0,
                           imdb_rating=5.5, imdb_votes=20_000, rt_audience_score=50),
            HistoricalComp("Low 2", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 75.0,
                           friday_m=37.5, saturday_m=22.5, sunday_m=15.0,
                           imdb_rating=5.8, imdb_votes=25_000, rt_audience_score=58),
            HistoricalComp("Mid 1", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 100.0,
                           friday_m=50.0, saturday_m=30.0, sunday_m=20.0,
                           imdb_rating=6.6, imdb_votes=35_000, rt_audience_score=76),
            HistoricalComp("Mid 2", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 105.0,
                           friday_m=52.5, saturday_m=31.5, sunday_m=21.0,
                           imdb_rating=6.8, imdb_votes=40_000, rt_audience_score=80),
            HistoricalComp("High 1", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 130.0,
                           friday_m=65.0, saturday_m=39.0, sunday_m=26.0,
                           imdb_rating=8.0, imdb_votes=50_000, rt_audience_score=94),
            HistoricalComp("High 2", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 135.0,
                           friday_m=67.5, saturday_m=40.5, sunday_m=27.0,
                           imdb_rating=8.2, imdb_votes=55_000, rt_audience_score=97),
        ]
        base_prediction = prediction()
        high_prediction = prediction()

        attach_comp_model_prediction(base_prediction, {}, metadata=base_metadata, comps=comps)
        attach_comp_model_prediction(high_prediction, {}, metadata=high_metadata, comps=comps)

        self.assertEqual("Friday only", high_prediction["seat_comp_basis"])
        self.assertGreater(high_prediction["seat_comp_audience_factor"], 1.05)
        self.assertGreater(
            high_prediction["seat_comp_mid_m"],
            base_prediction["seat_comp_mid_m"],
        )

    def test_default_metadata_includes_current_prada_release(self):
        metadata = load_movie_metadata()

        self.assertIn("the devil wears prada 2", metadata)
        target = metadata["the devil wears prada 2"]
        self.assertEqual("comedy", target.genre)
        self.assertEqual("female_skewing", target.audience_type)
        self.assertEqual("sequel", target.franchise_type)

    def test_default_metadata_includes_current_collection_movies(self):
        metadata = load_movie_metadata()

        mk = metadata_for_movie("Mortal Kombat II", metadata)
        sheep = metadata_for_movie("The Sheep Detectives", metadata)
        obsession = metadata_for_movie("Obsession", metadata)
        animal_farm = metadata_for_movie("Animal Farm", metadata)
        hokum = metadata_for_movie("Hokum", metadata)

        self.assertIsNotNone(mk)
        self.assertEqual("action", mk.genre)
        self.assertEqual("fan_driven", mk.audience_type)
        self.assertEqual("video_game", mk.franchise_type)
        self.assertEqual(3503, mk.national_theatre_count)

        self.assertIsNotNone(sheep)
        self.assertEqual("comedy", sheep.genre)
        self.assertEqual("broad_family", sheep.audience_type)
        self.assertEqual("original", sheep.franchise_type)
        self.assertEqual(3457, sheep.national_theatre_count)

        self.assertIsNotNone(obsession)
        self.assertEqual("horror", obsession.genre)
        self.assertEqual("horror_fan", obsession.audience_type)
        self.assertEqual(2615, obsession.national_theatre_count)

        self.assertIsNotNone(animal_farm)
        self.assertEqual(2600, animal_farm.national_theatre_count)

        self.assertIsNotNone(hokum)
        self.assertEqual(1885, hokum.national_theatre_count)

    def test_prediction_seat_comp_model_uses_latest_available_daily_basis(self):
        prediction = {
            "movie": "Michael",
            "seat_mid_m": 80.0,
            "seat_low_m": 76.0,
            "seat_high_m": 84.0,
            "daily_details": {
                "Thursday": {"domestic_mid": 20_000_000},
                "Friday": {"domestic_mid": 30_000_000},
                "Saturday": {"domestic_mid": 20_000_000},
                "Sunday": {"domestic_mid": 10_000_000},
            },
        }
        metadata = {
            "michael": TargetMetadata(
                movie="Michael",
                genre="music_biopic",
                audience_type="broad_legacy",
                franchise_type="biopic",
                rating="PG-13",
            )
        }
        comps = [
            HistoricalComp(
                "Comp",
                "music_biopic",
                "broad_legacy",
                "biopic",
                "PG-13",
                10.0,
                100.0,
                friday_m=50.0,
                saturday_m=30.0,
                sunday_m=20.0,
            ),
        ]

        attach_comp_model_prediction(prediction, {}, metadata=metadata, comps=comps)

        self.assertEqual("reported full weekend", prediction["seat_comp_basis"])
        self.assertAlmostEqual(80.0, prediction["seat_comp_evidence_m"], places=6)
        self.assertAlmostEqual(80.0, prediction["seat_comp_mid_m"], places=6)

    def test_learned_local_thursday_share_excludes_target_movie(self):
        cal = {
            "history": [
                {
                    "movie": "Michael",
                    "actual_total": 100.0,
                    "daily_predictions": {"Thursday": 20.0},
                },
                {
                    "movie": "Other Movie",
                    "actual_total": 80.0,
                    "daily_predictions": {"Thursday": 8.0},
                },
            ],
        }

        learned = learned_local_thursday_share(cal, exclude_movie="Michael")

        self.assertEqual(1, learned["n"])
        self.assertAlmostEqual(0.10, learned["share"], places=6)

    def test_prediction_blends_external_comps_with_local_seat_history(self):
        prediction = {
            "movie": "Future Biopic",
            "seat_mid_m": 90.0,
            "seat_low_m": 85.0,
            "seat_high_m": 95.0,
            "daily_details": {
                "Thursday": {"domestic_mid": 10_000_000},
            },
        }
        metadata = {
            "future biopic": TargetMetadata(
                movie="Future Biopic",
                genre="music_biopic",
                audience_type="broad_legacy",
                franchise_type="biopic",
                rating="PG-13",
            )
        }
        comps = [
            HistoricalComp(
                "Comp",
                "music_biopic",
                "broad_legacy",
                "biopic",
                "PG-13",
                10.0,
                100.0,
            ),
        ]
        cal = {
            "history": [
                {
                    "movie": "Settled Movie 1",
                    "actual_total": 100.0,
                    "daily_predictions": {"Thursday": 20.0},
                },
                {
                    "movie": "Settled Movie 2",
                    "actual_total": 100.0,
                    "daily_predictions": {"Thursday": 10.0},
                },
            ],
        }

        attach_comp_model_prediction(prediction, cal, metadata=metadata, comps=comps)

        self.assertAlmostEqual(0.11, prediction["seat_comp_thursday_share"], places=6)
        self.assertAlmostEqual(90.909090909, prediction["seat_comp_mid_m"], places=6)
        self.assertEqual(2, prediction["seat_comp_local_thursday_n"])
        self.assertAlmostEqual(0.20, prediction["seat_comp_local_thursday_weight"], places=6)

    def test_local_thursday_share_ignores_unmatched_metadata_when_available(self):
        target = TargetMetadata(
            movie="Family Movie",
            genre="comedy",
            audience_type="broad_family",
            franchise_type="original",
            rating="PG",
        )
        metadata = {
            "family movie": target,
            "adult event": TargetMetadata(
                movie="Adult Event",
                genre="comedy",
                audience_type="female_skewing",
                franchise_type="sequel",
                rating="PG-13",
            ),
        }
        cal = {
            "history": [
                {
                    "movie": "Adult Event",
                    "actual_total": 100.0,
                    "daily_predictions": {"Thursday": 20.0},
                },
            ],
        }

        learned = learned_local_thursday_share(
            cal,
            exclude_movie="Family Movie",
            target_metadata=target,
            metadata=metadata,
        )

        self.assertIsNone(learned)

    def test_sparse_seat_comp_prediction_uses_historical_prior(self):
        prediction = {
            "movie": "Family Movie",
            "seat_mid_m": 6.0,
            "seat_low_m": 4.0,
            "seat_high_m": 8.0,
            "n_days": 1,
            "seat_data_quality": 0.40,
            "daily_details": {
                "Thursday": {
                    "domestic_mid": 500_000,
                    "missing_timezones": ["PT"],
                },
            },
        }
        metadata = {
            "family movie": TargetMetadata(
                movie="Family Movie",
                genre="comedy",
                audience_type="broad_family",
                franchise_type="original",
                rating="PG",
            )
        }
        comps = [
            HistoricalComp("Comp A", "comedy", "broad_family", "original", "PG", 1.0, 20.0),
            HistoricalComp("Comp B", "comedy", "broad_family", "original", "PG", 1.2, 24.0),
        ]

        attach_comp_model_prediction(prediction, {}, metadata=metadata, comps=comps)

        self.assertIn("seat_comp_adjusted_mid_m", prediction)
        self.assertGreater(
            prediction["seat_comp_adjusted_mid_m"],
            prediction["seat_comp_mid_m"],
        )
        self.assertLess(
            prediction["seat_comp_adjusted_mid_m"],
            prediction["seat_comp_prior_mid_m"],
        )
        self.assertEqual("seat-primary-regression", prediction["regression_source"])
        self.assertAlmostEqual(
            prediction["seat_primary_mid_m"],
            prediction["regression_mid_m"],
            places=6,
        )
        self.assertAlmostEqual(
            prediction["seat_mid_m"] * prediction["seat_primary_w_direct"]
            + prediction["seat_comp_adjusted_mid_m"] * prediction["seat_primary_w_comp"],
            prediction["seat_primary_mid_m"],
            places=6,
        )

    def test_prediction_exposes_audience_regression_adjustment(self):
        prediction = {
            "movie": "High Audience Sequel",
            "seat_mid_m": 100.0,
            "seat_low_m": 95.0,
            "seat_high_m": 105.0,
            "daily_details": {
                "Thursday": {"domestic_mid": 10_000_000},
            },
        }
        metadata = {
            "high audience sequel": TargetMetadata(
                movie="High Audience Sequel",
                genre="comedy",
                audience_type="female_skewing",
                franchise_type="sequel",
                rating="PG-13",
                imdb_rating=8.0,
                rt_audience_score=95,
            )
        }
        comps = [
            HistoricalComp("Low 1", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 70.0,
                           imdb_rating=5.5, imdb_votes=20_000, rt_audience_score=50),
            HistoricalComp("Low 2", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 75.0,
                           imdb_rating=5.8, imdb_votes=25_000, rt_audience_score=58),
            HistoricalComp("Mid 1", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 100.0,
                           imdb_rating=6.6, imdb_votes=35_000, rt_audience_score=76),
            HistoricalComp("Mid 2", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 105.0,
                           imdb_rating=6.8, imdb_votes=40_000, rt_audience_score=80),
            HistoricalComp("High 1", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 130.0,
                           imdb_rating=8.0, imdb_votes=50_000, rt_audience_score=94),
            HistoricalComp("High 2", "comedy", "female_skewing", "sequel", "PG-13", 10.0, 135.0,
                           imdb_rating=8.2, imdb_votes=55_000, rt_audience_score=97),
        ]

        attach_comp_model_prediction(prediction, {}, metadata=metadata, comps=comps)

        self.assertGreater(prediction["seat_comp_audience_factor"], 1.05)
        self.assertGreater(prediction["seat_comp_mid_m"], 102.5)
        self.assertEqual(6, prediction["seat_comp_audience_regression_n"])
        self.assertIn("RT audience", prediction["seat_comp_audience_features"])

    def test_prediction_integrates_current_social_signal_into_comp_regression(self):
        prediction = {
            "movie": "High Buzz Sequel",
            "seat_mid_m": 100.0,
            "seat_low_m": 95.0,
            "seat_high_m": 105.0,
            "social_signal": {
                "factor": 1.08,
                "sentiment_score": 0.2,
                "buzz_score": 0.5,
                "signal_quality": 1.0,
                "reach": 600_000,
                "social_media_universe_m": 600.0,
            },
            "daily_details": {
                "Thursday": {"domestic_mid": 10_000_000},
            },
        }
        metadata = {
            "high buzz sequel": TargetMetadata(
                movie="High Buzz Sequel",
                genre="action",
                audience_type="fan_driven",
                franchise_type="sequel",
                rating="PG-13",
            )
        }
        comps = [
            HistoricalComp(
                f"Comp {idx}",
                "action",
                "fan_driven",
                "sequel",
                "PG-13",
                10.0,
                weekend,
                social_media_universe_m=smu,
            )
            for idx, (smu, weekend) in enumerate([
                (30.0, 70.0),
                (60.0, 76.0),
                (90.0, 82.0),
                (130.0, 90.0),
                (190.0, 100.0),
                (260.0, 112.0),
                (390.0, 125.0),
                (520.0, 140.0),
            ])
        ]

        attach_comp_model_prediction(prediction, {}, metadata=metadata, comps=comps)

        self.assertTrue(prediction["social_signal_model_integrated"])
        self.assertIn("RelishMix SMU 600M", prediction["seat_comp_audience_features"])
        self.assertEqual(0.0, prediction["social_adjustment_m"])
        self.assertNotIn("+social", prediction["regression_source"])

    def test_default_model_cohorts_include_expansion_data(self):
        old_value = os.environ.pop("THEATRE_MODEL_COHORTS", None)
        try:
            self.assertEqual(
                {CORE_COHORT, EXPANSION_COHORT},
                active_model_cohorts(),
            )
        finally:
            if old_value is not None:
                os.environ["THEATRE_MODEL_COHORTS"] = old_value

    def test_model_cohorts_can_still_force_core_only(self):
        old_value = os.environ.get("THEATRE_MODEL_COHORTS")
        os.environ["THEATRE_MODEL_COHORTS"] = CORE_COHORT
        try:
            self.assertEqual({CORE_COHORT}, active_model_cohorts())
        finally:
            if old_value is None:
                os.environ.pop("THEATRE_MODEL_COHORTS", None)
            else:
                os.environ["THEATRE_MODEL_COHORTS"] = old_value


if __name__ == "__main__":
    unittest.main()
