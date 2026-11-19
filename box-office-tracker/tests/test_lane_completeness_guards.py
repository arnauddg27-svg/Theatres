"""Green-but-partial passes in the direct lanes (audit 2026-11-19): every
lane's only floor was "nothing captured at all", so a pass that read a third
of its theatres stayed green and was never retried."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import alamo_collect as A  # noqa: E402
import harkins_collect as H  # noqa: E402
import regal_inventory as R  # noqa: E402
import webedia_collect as W  # noqa: E402


class RegalInventoryFloorTest(unittest.TestCase):
    def test_full_and_near_full_passes_are_fine(self):
        for read in (402, 401, 362):
            self.assertIsNone(R.inventory_shortfall(read, 402), read)

    def test_the_three_partial_passes_fail(self):
        for read in (254, 314, 135):                      # 11-14, 11-15, 11-19
            self.assertIn(f"{read}/402", R.inventory_shortfall(read, 402))

    def test_unknown_directory_or_switch_off(self):
        self.assertIsNone(R.inventory_shortfall(0, 0))
        self.assertIsNone(R.inventory_shortfall(10, 402, min_share=0))

    def test_main_goes_red_on_a_partial_pass(self):
        totals = {"theatres": 135, "directory": 402, "rows": 900, "walls": 548}
        with mock.patch.object(R, "collect", return_value=totals):
            self.assertEqual(1, R.main([]))
        with mock.patch.object(R, "collect", return_value={**totals, "theatres": 401}):
            self.assertEqual(0, R.main([]))


class HarkinsDeadlineTest(unittest.TestCase):
    def _main(self, totals):
        with mock.patch.object(H, "collect", return_value=totals), mock.patch.dict(os.environ, {"HARKINS_MODE": "pre"}):
            return H.main()

    def test_a_few_unread_theatres_warn_but_stay_green(self):
        self.assertEqual(0, self._main({"matched": 900, "captured": 880, "deadline_skipped": 4, "theatre_total": 32}))

    def test_many_unread_theatres_go_red(self):
        self.assertEqual(1, self._main({"matched": 900, "captured": 500, "deadline_skipped": 12, "theatre_total": 32}))

    def test_complete_pass_is_green(self):
        self.assertEqual(0, self._main({"matched": 900, "captured": 900, "theatre_total": 32}))


class AlamoBudgetTest(unittest.TestCase):
    def _main(self, totals, mode="pre"):
        env = {"ALAMO_MODE": mode}
        with mock.patch.object(A, "collect", return_value=totals), mock.patch.dict(os.environ, env), \
                mock.patch.object(A, "ALAMO_LOOP_MIN", 0):
            return A.main()

    def test_the_11_18_pass_goes_red(self):
        self.assertEqual(1, self._main({"markets": 22, "matched": 2027, "captured": 736, "budget_skipped": 1291}))

    def test_small_skips_and_full_passes_stay_green(self):
        self.assertEqual(0, self._main({"markets": 22, "matched": 2027, "captured": 1900, "budget_skipped": 100}))
        self.assertEqual(0, self._main({"markets": 22, "matched": 2027, "captured": 2027}))


class WebediaOutageTest(unittest.TestCase):
    def _main(self, totals):
        with mock.patch.object(W, "collect", return_value=totals):
            return W.main()

    def test_errors_with_nothing_captured_is_red(self):
        self.assertEqual(1, self._main({"theatres": 53, "matched": 0, "captured": 0, "schedule_errors": 86}))
        self.assertEqual(1, self._main({"theatres": 53, "matched": 0, "captured": 0, "chain_errors": 6}))

    def test_nothing_playing_is_not_an_outage(self):
        self.assertEqual(0, self._main({"theatres": 140, "matched": 0, "captured": 0}))
        self.assertEqual(0, self._main({"no_titles": 1}))

    def test_normal_pass_with_a_few_errors_is_green(self):
        self.assertEqual(0, self._main({"theatres": 140, "matched": 900, "captured": 880, "schedule_errors": 3}))


if __name__ == "__main__":
    unittest.main()
