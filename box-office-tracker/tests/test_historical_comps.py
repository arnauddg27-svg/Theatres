import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from historical_comps import (
    DEFAULT_COMPS_CSV,
    HistoricalComp,
    TargetMetadata,
    estimate_from_prediction,
    estimate_opening_weekend_from_thursday,
    load_historical_comps,
)
from predict import attach_comp_model_prediction


class HistoricalCompsTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
