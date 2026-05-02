import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from strategy import analyze_distribution, prediction_confidence


class StrategyConfidenceTest(unittest.TestCase):
    def test_prediction_confidence_uses_seat_data_quality_when_available(self):
        base_prediction = {
            "n_days": 1,
            "n_theatres_total": 400,
            "w_seat": 0.70,
            "blended_m": 80.0,
            "blend_low_m": 60.0,
            "blend_high_m": 100.0,
        }
        high_quality = {**base_prediction, "seat_data_quality": 0.90}
        low_quality = {**base_prediction, "seat_data_quality": 0.25}

        self.assertLess(
            prediction_confidence(low_quality),
            prediction_confidence(high_quality),
        )

    def test_distribution_uses_regression_forecast_not_headline_or_market_blend(self):
        prediction = {
            "n_days": 2,
            "n_theatres_total": 425,
            "seat_data_quality": 0.75,
            "w_seat": 0.75,
            "blended_m": 75.0,
            "blend_low_m": 60.0,
            "blend_high_m": 90.0,
            "headline_mid_m": 60.0,
            "headline_low_m": 55.0,
            "headline_high_m": 65.0,
            "headline_source": "seat+comp-regression",
            "headline_uses_polymarket": False,
            "regression_mid_m": 85.0,
            "regression_low_m": 80.0,
            "regression_high_m": 90.0,
            "regression_source": "seat+comp-regression",
            "regression_uses_polymarket": False,
        }
        markets = [
            {
                "question": "Will Sample opening weekend box office be between $80M and $90M?",
                "outcomePrices": "[0.5, 0.5]",
                "clobTokenIds": "[\"yes-token\", \"no-token\"]",
                "conditionId": "condition",
                "id": "market",
            },
        ]

        dist = analyze_distribution("Sample", prediction, markets)

        self.assertAlmostEqual(85.0, dist.our_mean, places=6)
        self.assertGreater(dist.brackets[0].our_prob, 0.90)


if __name__ == "__main__":
    unittest.main()
