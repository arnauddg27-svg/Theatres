"""Census-measured evening->day ratio replaces the generic 1.7x uplift.

2026-10-11 (Other Mommy): AMC's Friday capture is an evening window, the
generic 1.7x printed a $9.8M Friday against a $9.0M actual, and the x0.92
residual was transferred to a full-day Saturday. The Cinemark post-show
census reads every showing of the same film-day, so the real ratio
(Fri 1.21, Sat 1.36 — AMC's own full-day Saturday count agreed at 1.37) is
measurable and should drive the uplift instead.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import predict  # noqa: E402


def _entry(hour_seats, showings=None):
    return {"hours": dict(hour_seats), "showings": showings or 200}


class CensusDaypartRatioTest(unittest.TestCase):
    def test_ratio_is_full_day_over_captured_window(self):
        entry = _entry({13.0: 100, 16.0: 100, 19.0: 400, 21.5: 400})
        self.assertAlmostEqual(1000 / 800, predict.census_evening_to_daily(entry, 17.0), places=6)
        # window starting earlier includes the 4pm show
        self.assertAlmostEqual(1000 / 900, predict.census_evening_to_daily(entry, 16.0), places=6)

    def test_too_few_showings_returns_none(self):
        entry = _entry({13.0: 100, 19.0: 400}, showings=20)
        self.assertIsNone(predict.census_evening_to_daily(entry, 17.0))
        self.assertIsNone(predict.census_evening_to_daily(None, 17.0))
        self.assertIsNone(predict.census_evening_to_daily(_entry({13.0: 100}), 17.0))  # nothing in window
        # window holding <25% of the day is not the captured window
        self.assertIsNone(predict.census_evening_to_daily(_entry({13.0: 900, 19.0: 100}), 17.0))

    def test_ratio_never_below_one(self):
        entry = _entry({19.0: 400, 21.5: 400})
        self.assertEqual(1.0, predict.census_evening_to_daily(entry, 17.0))

    def test_showtime_hour_parsing(self):
        self.assertEqual(14.0, predict._census_showtime_hour("14:00"))
        self.assertEqual(19.5, predict._census_showtime_hour("7:30pm"))
        self.assertIsNone(predict._census_showtime_hour(""))

    def test_default_mode_is_census(self):
        if not os.environ.get("CENSUS_DAYPART_MODE"):
            self.assertEqual("census", predict.CENSUS_DAYPART_MODE)


if __name__ == "__main__":
    unittest.main()
