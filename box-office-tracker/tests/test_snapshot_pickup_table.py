"""Fitted pickup table (2026-10-11) + the scraper coverage/expected helper."""
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import predict  # noqa: E402
import scraper  # noqa: E402


class FittedPickupTableTest(unittest.TestCase):
    def setUp(self):
        self._old_mode = predict.SNAPSHOT_PICKUP_MODE
        predict.SNAPSHOT_PICKUP_MODE = "fitted"
        predict.set_snapshot_pickup_table({
            "all": {"le_24h": 1.92, "le_48h": 2.55, "gt_96h": 5.08},
            "by_day": {"Thursday": {"le_24h": 1.39}, "Saturday": {"le_24h": 2.03}},
        })

    def tearDown(self):
        predict.SNAPSHOT_PICKUP_MODE = self._old_mode
        predict.set_snapshot_pickup_table(None)
        predict._SNAPSHOT_PICKUP_TABLE_LOADED = False

    def test_day_then_all_then_constant(self):
        self.assertEqual(1.39, predict.snapshot_reservation_multiplier(1000, "Thursday"))
        self.assertEqual(2.03, predict.snapshot_reservation_multiplier(1000, "Saturday"))
        self.assertEqual(1.92, predict.snapshot_reservation_multiplier(1000, "Sunday"))   # no Sunday cell -> all
        self.assertEqual(5.08, predict.snapshot_reservation_multiplier(10000, "Friday"))
        self.assertEqual(1.35, predict.snapshot_reservation_multiplier(120, "Friday"))  # bucket absent -> constant
        self.assertEqual(1.0, predict.snapshot_reservation_multiplier(0, "Friday"))

    def test_table_mode_ignores_fit(self):
        predict.SNAPSHOT_PICKUP_MODE = "table"
        self.assertEqual(2.20, predict.snapshot_reservation_multiplier(1000, "Thursday"))

    def test_row_day_feeds_multiplier(self):
        row = {"total_seats": "100", "reserved_seats": "10", "minutes_until_showtime": "1000",
               "show_date": "2026-10-08", "auditorium_type": "", "weekend_of": "2026-10-09"}
        thu = predict.estimate_snapshot_showtime_revenue(row)
        row_sat = dict(row, show_date="2026-10-10")
        sat = predict.estimate_snapshot_showtime_revenue(row_sat)
        self.assertAlmostEqual(sat["projected_occ"] / thu["projected_occ"], 2.03 / 1.39, places=4)

    def test_buckets(self):
        self.assertEqual("le_1h", predict.snapshot_pickup_lead_bucket(60))
        self.assertEqual("le_3h", predict.snapshot_pickup_lead_bucket(61))
        self.assertEqual("gt_96h", predict.snapshot_pickup_lead_bucket(5761))


class SnapshotExpectedTheatresTest(unittest.TestCase):
    def _links(self, shows):
        return {"AMC X": {"dates": {"2026-10-11": {"movies": {"M": [{"showtime": s} for s in shows]}}}}}

    def test_same_day_slice_with_only_started_shows_is_dropped(self):
        theatres = [{"name": "AMC X", "_tz": "ET", "_date": "2026-10-11"},
                    {"name": "AMC X", "_tz": "ET", "_date": "2026-10-12"}]
        now = {"ET": datetime(2026, 10, 11, 22, 30)}
        kept = scraper.snapshot_expected_theatres(theatres, self._links(["1:00pm", "7:00pm"]), now_by_tz=now)
        self.assertEqual(["2026-10-12"], [t["_date"] for t in kept])

    def test_future_show_keeps_slice(self):
        theatres = [{"name": "AMC X", "_tz": "ET", "_date": "2026-10-11"}]
        now = {"ET": datetime(2026, 10, 11, 18, 30)}
        kept = scraper.snapshot_expected_theatres(theatres, self._links(["1:00pm", "7:00pm"]), now_by_tz=now)
        self.assertEqual(1, len(kept))

    def test_unknown_links_never_hide_a_miss(self):
        theatres = [{"name": "AMC Y", "_tz": "ET", "_date": "2026-10-11"}]
        now = {"ET": datetime(2026, 10, 11, 23, 30)}
        self.assertEqual(1, len(scraper.snapshot_expected_theatres(theatres, self._links(["1:00pm"]), now_by_tz=now)))
        self.assertEqual(1, len(scraper.snapshot_expected_theatres(theatres, None, now_by_tz=now)))


if __name__ == "__main__":
    unittest.main()
