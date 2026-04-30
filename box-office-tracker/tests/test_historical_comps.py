import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from historical_comps import (
    HistoricalComp,
    TargetMetadata,
    estimate_from_prediction,
    estimate_opening_weekend_from_thursday,
)


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


if __name__ == "__main__":
    unittest.main()
