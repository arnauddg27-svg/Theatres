import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict as P  # noqa: E402


def _base_pred(audience_type, observed_days, mid=30.0):
    """Minimal pred that takes the snapshot-daily-evidence branch."""
    dd = {d: {"domestic_mid": 5_000_000} for d in observed_days}
    return {
        "movie": "Test", "audience_type": audience_type,
        "daily_details": dd,
        "snapshot_mid_m": mid, "snapshot_low_m": mid * 0.9, "snapshot_high_m": mid * 1.1,
        "seat_mid_m": mid, "seat_low_m": mid * 0.9, "seat_high_m": mid * 1.1,
        # force the snapshot branch of select_regression_prediction
        "snapshot_effective_model_weight": 1.0,
        "snapshot_calibration_support_factor": 1.0,
        "snapshot_model_coverage_ratio": 1.0,
        "snapshot_days": [d for d in observed_days if d != "Thursday"],
    }


class FamilyWalkupConstantTests(unittest.TestCase):
    def test_boost_is_a_bounded_prior(self):
        self.assertEqual(P.FAMILY_WALKUP_AUDIENCE, "broad_family")
        self.assertTrue(1.0 < P.FAMILY_WALKUP_SNAPSHOT_BOOST <= 1.5)


class FamilyWalkupBehaviorTests(unittest.TestCase):
    """Force the snapshot-daily-evidence branch so the boost logic is exercised."""

    def setUp(self):
        self._orig = P.complete_snapshot_covers_missing_days
        P.complete_snapshot_covers_missing_days = lambda pred: True

    def tearDown(self):
        P.complete_snapshot_covers_missing_days = self._orig

    def _headline(self, pred):
        P.select_regression_prediction(pred, cal=None)
        return pred["regression_mid_m"], pred.get("family_walkup_boost")

    def test_non_family_is_untouched(self):
        for atype in ("fan_driven", "horror_fan", "", None):
            pred = _base_pred(atype, ["Thursday"], mid=30.0)
            mid, boost = self._headline(pred)
            self.assertIsNone(boost)
            self.assertAlmostEqual(mid, 30.0, places=6)   # unchanged

    def test_family_thursday_only_gets_near_full_boost(self):
        pred = _base_pred("broad_family", ["Thursday"], mid=30.0)
        mid, boost = self._headline(pred)
        # Thursday observed (~12% weight) -> ~88% reservation-projected
        self.assertIsNotNone(boost)
        self.assertGreater(boost, 1.15)
        self.assertLessEqual(boost, P.FAMILY_WALKUP_SNAPSHOT_BOOST + 1e-9)
        self.assertAlmostEqual(mid, 30.0 * boost, places=5)

    def test_boost_scales_with_reservation_share(self):
        _, b_few = self._headline(_base_pred("broad_family", ["Thursday"]))
        _, b_many = self._headline(
            _base_pred("broad_family", ["Thursday", "Friday", "Saturday"]))
        # more observed seat days -> smaller reservation share -> smaller boost
        self.assertGreater(b_few, b_many)

    def test_fully_observed_family_gets_no_boost(self):
        # all four days observed -> 0% reservation-projected -> no boost
        _, boost = self._headline(
            _base_pred("broad_family", ["Thursday", "Friday", "Saturday", "Sunday"]))
        self.assertIsNone(boost)


if __name__ == "__main__":
    unittest.main()
