import math
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chain_forecast as CF  # noqa: E402
import predict as P  # noqa: E402

SHARES = {c: {d: s for d in CF.DAYS} for c, s in (("CNMK", 0.14), ("ALMO", 0.013), ("HARK", 0.016), ("REGL", 0.17))}
RATIOS = {"n": 100, "sat_per_fri": 1.2, "sun_per_sat": 0.75, "fri_per_previews": 2.4}


def cell(dollars_m, showings=200):
    return {"dollars": dollars_m * 1e6, "seats": int(dollars_m * 8e4), "showings": showings, "theatres": 50}


def cells(national_m, chains=("CNMK", "ALMO", "HARK"), skew=1.0):
    """Chain cells that imply `national_m` (times `skew`: the film's chain mix)."""
    return {c: cell(national_m * SHARES[c]["Friday"] * skew) for c in chains}


class WeekendForecastTest(unittest.TestCase):
    def test_nothing_reported_or_counted_is_not_this_modules_stage(self):
        self.assertIsNone(CF.weekend_forecast({}, {}, SHARES, RATIOS))

    def test_previews_only_uses_the_day_shape(self):
        fc = CF.weekend_forecast({"Thursday": 2.0}, {}, SHARES, RATIOS)
        friday = 2.0 * 2.4
        self.assertEqual(fc["stage"], "previews-reported")
        self.assertAlmostEqual(fc["mid_m"], 2.0 + friday + friday * 1.2 + friday * 1.2 * 0.75)

    def test_friday_seats_are_averaged_with_the_previews_read(self):
        fc = CF.weekend_forecast({"Thursday": 2.0}, {"Friday": cells(6.0)}, SHARES, RATIOS)
        self.assertEqual(fc["stage"], "friday-seats")
        self.assertAlmostEqual(fc["days"]["Friday"]["value_m"], math.sqrt(6.0 * 4.8), places=6)

    def test_friday_reported_without_a_thursday_row_holds_its_previews(self):
        fc = CF.weekend_forecast({"Friday": 3.8}, {}, SHARES, RATIOS)
        self.assertEqual(fc["days"]["Thursday"], {"value_m": 0.0, "how": "inside Friday"})
        self.assertAlmostEqual(fc["mid_m"], 3.8 * (1 + 1.2 + 1.2 * 0.75))
        self.assertEqual(fc["stage"], "friday-reported")

    def test_saturday_seats_carry_from_the_reported_friday_and_cancel_the_chain_mix(self):
        # The film over-indexes 1.3x at these chains on both days: a raw read
        # of Saturday would say 9.1; the carry says 7.0.
        by_day = {"Friday": cells(5.0, skew=1.3), "Saturday": cells(7.0, skew=1.3)}
        est, note = CF.carried(by_day, SHARES, "Saturday", "Friday", 5.0)
        self.assertAlmostEqual(est, 7.0, places=6)
        self.assertEqual(note, "CNMK+ALMO+HARK")
        fc = CF.weekend_forecast({"Thursday": 1.0, "Friday": 5.0}, by_day, SHARES, RATIOS)
        self.assertEqual(fc["stage"], "saturday-seats")
        w = CF.SATURDAY_CARRY_WEIGHT
        self.assertAlmostEqual(fc["days"]["Saturday"]["value_m"], 7.0 ** w * (5.0 * 1.2) ** (1 - w), places=6)

    def test_a_lane_gap_on_the_reference_day_drops_the_carry(self):
        # 2026-11-06: Friday's reads were lost, so Friday counted 30% of its
        # reported gross and the carry tripled Saturday (The Cat in the Hat +73%).
        by_day = {"Friday": cells(5.0, skew=0.3), "Saturday": cells(7.0)}
        est, note = CF.carried(by_day, SHARES, "Saturday", "Friday", 5.0)
        self.assertIsNone(est)
        self.assertIn("lane gap", note)
        fc = CF.weekend_forecast({"Thursday": 1.0, "Friday": 5.0}, by_day, SHARES, RATIOS)
        self.assertEqual(fc["stage"], "friday-reported")
        self.assertAlmostEqual(fc["days"]["Saturday"]["value_m"], 6.0)

    def test_sunday_seats_carry_from_the_reported_saturday(self):
        by_day = {"Saturday": cells(6.0, skew=0.8), "Sunday": cells(4.2, skew=0.8)}
        fc = CF.weekend_forecast({"Thursday": 1.0, "Friday": 5.0, "Saturday": 6.0}, by_day, SHARES, RATIOS)
        self.assertEqual(fc["stage"], "sunday-seats")
        self.assertAlmostEqual(fc["mid_m"], 1.0 + 5.0 + 6.0 + 4.2, places=6)
        self.assertGreaterEqual(fc["low_m"], 12.0)          # reported dollars are a floor
        self.assertLessEqual(fc["low_m"], fc["mid_m"])
        self.assertGreaterEqual(fc["high_m"], fc["mid_m"])

    def test_two_small_chains_cannot_stand_for_the_country(self):
        fc = CF.weekend_forecast({}, {"Thursday": cells(1.0, chains=("ALMO", "HARK")),
                                      "Friday": cells(3.0, chains=("ALMO", "HARK"))}, SHARES, RATIOS)
        self.assertIsNone(fc)

    def test_amc_is_never_in_the_pool(self):
        self.assertNotIn("AMC", CF.POOL)
        by_day = {"Friday": dict(cells(6.0), AMC=cell(50.0))}
        value, chains = CF.pooled(by_day["Friday"], "Friday", dict(SHARES, AMC={d: 0.24 for d in CF.DAYS}))
        self.assertAlmostEqual(value, 6.0, places=6)
        self.assertNotIn("AMC", chains)


class ShapeRatiosTest(unittest.TestCase):
    LIB = ([("0000-2024", 2.0, 5.0, 6.0, 4.5, "broad_adult")] * 30
           + [("0000-2025", 4.0, 6.0, 6.0, 4.2, "fan_driven")] * 10
           + [("2026-12-25", 1.0, 9.0, 9.0, 9.0, "broad_adult")])

    def test_only_earlier_openings_are_used(self):
        r = CF.shape_ratios("2026-11-27", self.LIB)
        self.assertEqual(r["n"], 40)
        self.assertAlmostEqual(r["sat_per_fri"], 1.2)

    def test_an_audience_group_pulls_its_ratio_toward_its_own_median(self):
        base = CF.shape_ratios("2026-11-27", self.LIB)
        fan = CF.shape_ratios("2026-11-27", self.LIB, "fan_driven")
        self.assertEqual(fan["group"], "fan_driven")
        self.assertLess(fan["fri_per_previews"], base["fri_per_previews"])     # front-loaded
        self.assertGreater(fan["fri_per_previews"], 1.5)                        # shrunk, not replaced
        self.assertEqual(CF.shape_ratios("2026-11-27", self.LIB, "young_male")["group"], "")

    def test_too_small_a_library_gives_no_forecast(self):
        self.assertIsNone(CF.shape_ratios("2026-11-27", self.LIB[:5]))


class HeadlineGateTest(unittest.TestCase):
    """predict.chain_evidence_forecast: only when AMC was not read."""
    DETAILS_DARK = {"Friday": {"actual_override": True, "expected_theatres": 425, "n_theatres": 2}}
    DETAILS_OK = {"Thursday": {"effective_coverage_ratio": 0.9}, "Friday": {"effective_coverage_ratio": 0.8}}

    def test_played_day_coverage_does_not_fall_because_the_weekend_is_young(self):
        self.assertAlmostEqual(P.amc_played_day_coverage(self.DETAILS_OK), 0.85)
        self.assertLess(P.amc_played_day_coverage(self.DETAILS_DARK), 0.01)
        self.assertIsNone(P.amc_played_day_coverage({}))

    def _call(self, details, mode="outage", data=()):
        fake = {"mid_m": 10.0, "low_m": 9.0, "high_m": 11.0, "stage": "friday-reported", "basis": "b", "library_n": 99}
        pred = {"movie": "X", "weekend_of": "2026-11-20", "daily_details": details}
        with mock.patch.object(P, "CHAIN_FORECAST_MODE", mode), \
                mock.patch.object(P, "_CHAIN_CENSUS_DATA", data), \
                mock.patch.object(CF, "for_movie", return_value=fake) as call:
            return P.chain_evidence_forecast(pred, {}, {"Friday": 3.8}), call, pred

    def test_engages_when_amc_is_dark(self):
        out, call, pred = self._call(self.DETAILS_DARK, data={})
        self.assertEqual(out["mid_m"], 10.0)
        self.assertEqual(pred["chain_forecast"]["stage"], "friday-reported")
        self.assertEqual(call.call_args.args[2], {"Friday": 3.8})

    def test_stays_out_when_amc_was_read(self):
        out, call, _ = self._call(self.DETAILS_OK, data={})
        self.assertIsNone(out)
        call.assert_not_called()

    def test_stays_out_of_replays_that_pass_no_chain_data(self):
        out, call, _ = self._call(self.DETAILS_DARK, data=None)
        self.assertIsNone(out)
        call.assert_not_called()

    def test_switch_off(self):
        self.assertIsNone(self._call(self.DETAILS_DARK, mode="off", data={})[0])
        self.assertIsNotNone(self._call(self.DETAILS_OK, mode="always", data={})[0])


if __name__ == "__main__":
    unittest.main()


class AuditFixesTest(unittest.TestCase):
    """2026-11-28 audit of the first version."""

    def test_a_day_still_in_progress_is_not_a_counted_day(self):
        from datetime import datetime, timezone
        # Saturday 22:30Z: Friday is complete, Saturday holds only its matinees.
        self.assertEqual(CF.last_complete_date(datetime(2026, 12, 5, 22, 30, tzinfo=timezone.utc)), "2026-12-04")
        # Sunday 09:59Z: the last West-coast shows are not read yet; 10:00Z they are.
        self.assertEqual(CF.last_complete_date(datetime(2026, 12, 6, 9, 59, tzinfo=timezone.utc)), "2026-12-04")
        self.assertEqual(CF.last_complete_date(datetime(2026, 12, 6, 10, 0, tzinfo=timezone.utc)), "2026-12-05")

    def test_for_movie_drops_the_in_progress_day(self):
        from datetime import datetime, timezone
        chain_data = {"Film A": {"2026-12-04": cells(5.0), "2026-12-05": cells(7.0)}}
        with mock.patch.object(CF.CC, "shares_for", return_value=SHARES), \
                mock.patch.object(CF.CC, "regal_pool_ok", return_value=False), \
                mock.patch.object(CF, "shape_ratios", return_value=RATIOS), \
                mock.patch.object(CF, "pace_for_movie", return_value=None):
            live = CF.for_movie("Film A", "2026-12-04", {"Thursday": 1.0, "Friday": 5.0}, chain_data=chain_data,
                                now=datetime(2026, 12, 5, 22, 30, tzinfo=timezone.utc))
            later = CF.for_movie("Film A", "2026-12-04", {"Thursday": 1.0, "Friday": 5.0}, chain_data=chain_data,
                                 now=datetime(2026, 12, 6, 11, 0, tzinfo=timezone.utc))
        self.assertEqual(live["stage"], "friday-reported")
        self.assertAlmostEqual(live["days"]["Saturday"]["value_m"], 6.0)
        self.assertEqual(later["stage"], "saturday-seats")

    def test_a_carry_needs_most_of_the_days_showings(self):
        by_day = {"Friday": cells(5.0), "Saturday": {c: dict(v, showings=100) for c, v in cells(7.0).items()}}
        est, note = CF.carried(by_day, SHARES, "Saturday", "Friday", 5.0)        # 100 of 200 showings read
        self.assertIsNone(est)

    def test_pace_read_joins_the_friday_average_only_with_reported_previews(self):
        pace = {"friday_m": 3.0, "chains": "CNMK+HARK"}
        fc = CF.weekend_forecast({"Thursday": 2.0}, {}, SHARES, RATIOS, pace_friday=pace)
        self.assertAlmostEqual(fc["days"]["Friday"]["value_m"], math.sqrt(4.8 * 3.0), places=6)
        self.assertIn("pre-sales pace CNMK+HARK", fc["days"]["Friday"]["how"])
        with_seats = CF.weekend_forecast({"Thursday": 2.0}, {"Friday": cells(6.0)}, SHARES, RATIOS, pace_friday=pace)
        self.assertAlmostEqual(with_seats["days"]["Friday"]["value_m"], (6.0 * 4.8 * 3.0) ** (1 / 3), places=6)
        reported = CF.weekend_forecast({"Thursday": 2.0, "Friday": 5.0}, {}, SHARES, RATIOS, pace_friday=pace)
        self.assertEqual(reported["days"]["Friday"]["value_m"], 5.0)

    def test_a_pre_friday_opener_never_takes_the_chain_headline(self):
        pred = {"movie": "X", "weekend_of": "2026-11-27", "midweek_opening": {"run": {"opening_date": "2026-11-25"}},
                "daily_details": HeadlineGateTest.DETAILS_DARK}
        with mock.patch.object(P, "_CHAIN_CENSUS_DATA", {}), mock.patch.object(CF, "for_movie") as call:
            self.assertIsNone(P.chain_evidence_forecast(pred, {}, {"Thursday": 7.7}))
        call.assert_not_called()
