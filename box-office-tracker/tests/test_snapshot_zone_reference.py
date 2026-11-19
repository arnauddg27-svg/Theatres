"""latest_snapshot_window_rows: staleness per zone, walled visits skipped.

2026-11-19: AMC refused 92-99% of seat requests from 14:48Z on. A Central-only
re-read at 14:00Z made every Eastern theatre (read 02:44-04:41Z) "stale" against
the show date's newest row, and the blocked legs that followed left a few rows
per theatre as each theatre's "latest run". Coverage fell under the 50% gate and
Hunger Games had no forecast from 08:14Z on, on its opening Thursday.
"""
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import predict  # noqa: E402

DAY = datetime(2026, 11, 19, tzinfo=timezone.utc)
SHOW_DATE = "2026-11-20"


def at(hours):
    return DAY + timedelta(hours=hours)


def row(run_id, read_at, showtime_id, starts_at, theatre="AMC One 1", tz="ET",
        show_date=SHOW_DATE, with_run_id=True):
    stamp = read_at.isoformat()
    return {
        "show_date": show_date, "timezone": tz, "theatre_name": theatre,
        "run_id": run_id if with_run_id else "",
        "snapshot_time": stamp,
        "snapshot_bucket": run_id if not with_run_id else stamp[:13] + ":00Z",
        "showtime_id": f"{theatre}-{showtime_id}", "showtime": "x",
        "minutes_until_showtime": str(int((starts_at - read_at).total_seconds() // 60)),
        "reserved_seats": "10", "total_seats": "100",
    }


def visit(run_id, read_at, showtime_ids, theatre="AMC One 1", tz="ET", **kw):
    """One theatre visit: every showtime starts the next evening, well ahead."""
    return [row(run_id, read_at, sid, at(48 + sid), theatre=theatre, tz=tz, **kw)
            for sid in showtime_ids]


def window(rows, **kw):
    """The outage-fallback rule ("rescue") unless a mode is named."""
    kw.setdefault("zone_reference", "rescue")
    return predict.latest_snapshot_window_rows(rows, **kw)


def kept_ids(rows, **kw):
    return sorted((r["theatre_name"], r["run_id"] or r["snapshot_bucket"],
                   r["showtime_id"].rsplit("-", 1)[1])
                  for r in window(rows, **kw))


def theatres(rows, **kw):
    return sorted({r["theatre_name"] for r in window(rows, **kw)})


class ZoneReferenceTest(unittest.TestCase):
    def test_rereading_one_zone_does_not_age_out_another(self):
        rows = (visit("night", at(3), range(5), theatre="AMC East 1", tz="ET")
                + visit("night", at(5), range(5), theatre="AMC Central 1", tz="CT")
                + visit("reread", at(14), range(5), theatre="AMC Central 1", tz="CT"))
        self.assertEqual(theatres(rows), ["AMC Central 1", "AMC East 1"])
        # The rule this replaces dropped the Eastern theatre: 11 hours behind.
        self.assertEqual(theatres(rows, zone_reference="date"), ["AMC Central 1"])

    def test_a_few_theatres_read_in_a_block_do_not_age_out_their_zone(self):
        rows = []
        for n in range(10):
            rows += visit("morning", at(8), range(4), theatre=f"AMC West {n}", tz="PT")
        for n in range(2):                                   # two got through, 13 hours later
            rows += visit("blocked", at(21), range(4), theatre=f"AMC West {n}", tz="PT")
        self.assertEqual(len(theatres(rows)), 10)
        self.assertEqual(len(theatres(rows, zone_reference="date")), 2)

    def test_theatre_missed_by_a_real_rerun_still_goes_stale(self):
        rows = []
        for n in range(10):
            rows += visit("morning", at(8), range(4), theatre=f"AMC West {n}", tz="PT")
        for n in range(8):                                   # most of the zone re-read
            rows += visit("evening", at(21), range(4), theatre=f"AMC West {n}", tz="PT")
        self.assertEqual(theatres(rows), [f"AMC West {n}" for n in range(8)])

    def test_theatre_missed_by_a_rerun_within_the_window_is_kept(self):
        rows = []
        for n in range(10):
            rows += visit("evening", at(22), range(4), theatre=f"AMC East {n}", tz="ET")
        for n in range(8):
            rows += visit("night", at(27), range(4), theatre=f"AMC East {n}", tz="ET")
        self.assertEqual(len(theatres(rows)), 10)

    def test_zone_unread_for_two_days_is_dropped(self):
        east_old = visit("old", at(-60), range(4), theatre="AMC East 1", tz="ET")
        east_lagging = visit("lag", at(-30), range(4), theatre="AMC East 1", tz="ET")
        central = visit("now", at(3), range(4), theatre="AMC Central 1", tz="CT")
        self.assertEqual(theatres(east_old + central), ["AMC Central 1"])
        self.assertEqual(theatres(east_lagging + central), ["AMC Central 1", "AMC East 1"])
        self.assertEqual(theatres(east_old + central, max_zone_lag_hours=0),
                         ["AMC Central 1", "AMC East 1"])

    def test_each_show_date_is_judged_on_its_own(self):
        rows = (visit("night", at(3), range(4), theatre="AMC East 1", show_date="2026-11-21")
                + visit("night", at(3), range(4), theatre="AMC East 1", show_date="2026-11-20")
                + visit("day", at(15), range(4), theatre="AMC East 1", show_date="2026-11-20"))
        kept = window(rows)
        self.assertEqual({(r["show_date"], r["run_id"]) for r in kept},
                         {("2026-11-21", "night"), ("2026-11-20", "day")})


class WalledVisitTest(unittest.TestCase):
    def test_walled_visit_is_skipped_for_the_one_before(self):
        rows = visit("morning", at(8), range(10)) + visit("blocked", at(21), [3])
        self.assertEqual({run for _, run, _ in kept_ids(rows)}, {"morning"})
        self.assertEqual(len(kept_ids(rows)), 10)

    def test_two_walled_visits_in_a_row_fall_back_to_the_full_one(self):
        rows = (visit("morning", at(8), range(10)) + visit("blocked-1", at(17), [3])
                + visit("blocked-2", at(21), [5, 6]))
        self.assertEqual({run for _, run, _ in kept_ids(rows)}, {"morning"})

    def test_visit_that_read_half_is_kept_and_nothing_is_resurrected(self):
        rows = visit("morning", at(8), range(10)) + visit("evening", at(13), range(5))
        self.assertEqual(kept_ids(rows), [("AMC One 1", "evening", str(n)) for n in range(5)])

    def test_evening_visit_is_not_walled_because_matinees_have_played(self):
        night = at(3)
        evening = at(22.5)
        rows = [row("night", night, n, at(13 + n)) for n in range(7)]        # played by 22:30Z
        rows += [row("night", night, n, at(23 + n)) for n in (7, 8, 9)]       # still ahead
        rows += [row("evening", evening, n, at(23 + n)) for n in (7, 8, 9)]
        kept = kept_ids(rows, max_slice_age_hours=48)
        self.assertEqual([k for k in kept if k[1] == "evening"],
                         [("AMC One 1", "evening", str(n)) for n in (7, 8, 9)])
        self.assertEqual(len([k for k in kept if k[1] == "night"]), 7)        # carried forward

    def test_walled_visit_rows_are_not_carried_forward_later(self):
        # The blocked visit read a showtime that has since started; the theatre
        # stands on the morning visit, so only the morning's row for it is used.
        rows = [row("morning", at(8), n, at(30 + n)) for n in range(10)]
        rows += [row("blocked", at(21), 0, at(30))]
        kept = kept_ids(rows, max_slice_age_hours=48)
        self.assertEqual({run for _, run, _ in kept}, {"morning"})

    def test_schedule_cut_is_believed_once_the_full_read_is_two_days_old(self):
        rows = visit("old", at(-60), range(10)) + visit("now", at(3), [3])
        self.assertEqual({run for _, run, _ in kept_ids(rows)}, {"now"})

    def test_first_visit_is_never_walled(self):
        rows = visit("only", at(21), [3])
        self.assertEqual(len(kept_ids(rows)), 1)

    def test_rows_without_a_run_id_group_by_bucket(self):
        rows = (visit("bucket-a", at(8), range(10), with_run_id=False)
                + visit("bucket-b", at(21), [3], with_run_id=False))
        self.assertEqual({run for _, run, _ in kept_ids(rows)}, {"bucket-a"})

    def test_sparse_rule_can_be_turned_off(self):
        rows = visit("morning", at(8), range(10)) + visit("blocked", at(13), [3])
        self.assertEqual({run for _, run, _ in kept_ids(rows, sparse_ratio=0)}, {"blocked"})

    def test_old_rule_takes_the_newest_visit_as_before(self):
        rows = visit("morning", at(8), range(10)) + visit("blocked", at(13), [3])
        self.assertEqual({run for _, run, _ in kept_ids(rows, zone_reference="date")}, {"blocked"})


class RescueOnlyTest(unittest.TestCase):
    """The default touches a zone only when the date rule has left it with
    under half the showtimes its own last full reads hold."""

    def mild_wave(self):
        rows = []
        for n in range(10):
            rows += visit("evening", at(22), range(4), theatre=f"AMC East {n}", tz="ET")
        for n in range(4):                                   # 4 theatres walled at night
            rows += visit("night", at(27), [0], theatre=f"AMC East {n}", tz="ET")
        return rows

    def test_a_zone_that_kept_most_of_its_showtimes_is_left_alone(self):
        rows = self.mild_wave()
        default = kept_ids(rows)
        self.assertEqual(default, kept_ids(rows, zone_reference="date"))
        self.assertEqual(6 * 4 + 4, len(default))            # walled visits stand, as before
        self.assertEqual(40, len(kept_ids(rows, zone_reference="zone")))

    def test_only_the_zone_in_outage_is_taken_from_its_own_reads(self):
        rows = self.mild_wave()                               # Eastern: mild, left alone
        for n in range(5):                                    # Pacific: read 13 hours earlier
            rows += visit("morning", at(14), range(4), theatre=f"AMC West {n}", tz="PT")
        default = window(rows)
        east = [r for r in default if r["timezone"] == "ET"]
        west = [r for r in default if r["timezone"] == "PT"]
        self.assertEqual(28, len(east))
        self.assertEqual(20, len(west))
        self.assertEqual([], [r for r in window(rows, zone_reference="date")
                              if r["timezone"] == "PT"])

    def test_rescue_threshold(self):
        rows = self.mild_wave()
        self.assertEqual(40, len(kept_ids(rows, rescue_ratio=0.75)))   # 28 < 0.75 x 40
        self.assertEqual(28, len(kept_ids(rows, rescue_ratio=0.7)))    # 28 >= 0.7 x 40

    def test_bridge_rows_with_iana_zone_names_join_their_zone(self):
        rows = []
        for n in range(6):
            rows += visit("night", at(27), range(4), theatre=f"AMC Central {n}", tz="CT")
        rows += visit("bridge", at(-10), range(4), theatre="AMC Bridge 1", tz="America/Chicago")
        self.assertNotIn("AMC Bridge 1", theatres(rows, zone_reference="zone"))


class DefaultIsTheOldRuleTest(unittest.TestCase):
    """The model is fitted and graded on the date rule; nothing here moves it."""

    def test_default_mode(self):
        self.assertEqual("date", predict.SNAPSHOT_ZONE_REFERENCE)
        self.assertEqual(0.5, predict.SNAPSHOT_ZONE_RESCUE_RATIO)
        self.assertTrue(predict.SNAPSHOT_OUTAGE_FALLBACK)

    def test_default_call_is_the_date_rule(self):
        rows = ThursdayOutageReplayTest().build()
        default = predict.latest_snapshot_window_rows(rows)
        self.assertEqual(default, window(rows, zone_reference="date"))
        self.assertNotEqual(default, window(rows))

    def test_mode_override_applies_inside_the_block_only(self):
        rows = ThursdayOutageReplayTest().build()
        with predict.snapshot_zone_mode("rescue"):
            inside = predict.latest_snapshot_window_rows(rows)
        self.assertEqual(inside, window(rows))
        self.assertEqual(predict.latest_snapshot_window_rows(rows), window(rows, zone_reference="date"))
        self.assertEqual([], predict._SNAPSHOT_ZONE_OVERRIDE)

    def test_override_is_cleared_when_the_forecast_raises(self):
        with self.assertRaises(RuntimeError):
            with predict.snapshot_zone_mode("rescue"):
                raise RuntimeError("boom")
        self.assertEqual([], predict._SNAPSHOT_ZONE_OVERRIDE)


class OutageFallbackTest(unittest.TestCase):
    def forecaster(self, by_mode):
        calls = []

        def forecast(movie, cal, **kw):
            mode = predict._SNAPSHOT_ZONE_OVERRIDE[-1] if predict._SNAPSHOT_ZONE_OVERRIDE else "date"
            calls.append(mode)
            cal["touched"] = cal.get("touched", 0) + 1
            value = by_mode.get(mode)
            return dict(value) if value else None
        return forecast, calls

    def test_a_forecast_the_model_can_make_is_never_touched(self):
        forecast, calls = self.forecaster({"date": {"domestic_mid": 88.2}, "rescue": {"domestic_mid": 98.9}})
        pred = predict.predict_with_outage_fallback(forecast, "Film", {"calibration_factors": {}})
        self.assertEqual(["date"], calls)
        self.assertEqual({"domestic_mid": 88.2}, pred)

    def test_no_forecast_falls_back_and_is_flagged(self):
        forecast, calls = self.forecaster({"rescue": {"domestic_mid": 98.9, "data_outage": False}})
        cal = {"calibration_factors": {}}
        pred = predict.predict_with_outage_fallback(forecast, "Film", cal)
        self.assertEqual(["date", "rescue"], calls)
        self.assertEqual(98.9, pred["domestic_mid"])
        self.assertTrue(pred["snapshot_outage_fallback"])
        self.assertTrue(pred["data_outage"])
        self.assertEqual(1, cal["touched"])                 # the retry ran on a copy
        self.assertEqual([], predict._SNAPSHOT_ZONE_OVERRIDE)

    def walled_snapshot(self, walled_theatres):
        rows = []
        for n in range(12):
            rows += visit("night", at(27), range(6), theatre=f"AMC Central {n}", tz="CT")
        for n in range(walled_theatres):
            rows += visit("evening", at(22), range(6), theatre=f"AMC West {n}", tz="PT")
            rows += visit("blocked", at(28), [0], theatre=f"AMC West {n}", tz="PT")
        return {SHOW_DATE: rows}

    def test_walled_share_counts_theatres_standing_on_a_walled_visit(self):
        self.assertEqual(0.0, predict.snapshot_walled_share(self.walled_snapshot(0)[SHOW_DATE]))
        self.assertAlmostEqual(6 / 18, predict.snapshot_walled_share(self.walled_snapshot(6)[SHOW_DATE]))
        self.assertEqual(0.0, predict.snapshot_walled_share([]))

    def test_a_forecast_standing_on_walled_reads_is_replaced_and_flagged(self):
        forecast, calls = self.forecaster({"date": {"domestic_mid": 64.6}, "rescue": {"domestic_mid": 98.9}})
        pred = predict.predict_with_outage_fallback(
            forecast, "Film", {"calibration_factors": {}}, snapshot_data=self.walled_snapshot(6))
        self.assertEqual(["date", "rescue"], calls)
        self.assertEqual(98.9, pred["domestic_mid"])
        self.assertTrue(pred["snapshot_outage_fallback"] and pred["data_outage"])
        self.assertAlmostEqual(0.333, pred["snapshot_outage_walled_share"])

    def test_a_few_walled_theatres_leave_the_forecast_alone(self):
        forecast, calls = self.forecaster({"date": {"domestic_mid": 88.2}, "rescue": {"domestic_mid": 98.9}})
        pred = predict.predict_with_outage_fallback(
            forecast, "Film", {"calibration_factors": {}}, snapshot_data=self.walled_snapshot(3))
        self.assertEqual(["date"], calls)                    # 3 of 15 = 20%, under the bar
        self.assertEqual({"domestic_mid": 88.2}, pred)

    def test_walled_forecast_is_kept_when_the_rescue_gives_none(self):
        forecast, calls = self.forecaster({"date": {"domestic_mid": 64.6}})
        pred = predict.predict_with_outage_fallback(
            forecast, "Film", {"calibration_factors": {}}, snapshot_data=self.walled_snapshot(6))
        self.assertEqual(["date", "rescue"], calls)
        self.assertEqual({"domestic_mid": 64.6}, pred)

    def test_no_forecast_either_way_stays_none(self):
        forecast, calls = self.forecaster({})
        self.assertIsNone(predict.predict_with_outage_fallback(forecast, "Film", {"calibration_factors": {}}))
        self.assertEqual(["date", "rescue"], calls)

    def test_switch_off(self):
        forecast, calls = self.forecaster({"rescue": {"domestic_mid": 98.9}})
        old = predict.SNAPSHOT_OUTAGE_FALLBACK
        predict.SNAPSHOT_OUTAGE_FALLBACK = False
        try:
            self.assertIsNone(predict.predict_with_outage_fallback(forecast, "Film", {"calibration_factors": {}}))
        finally:
            predict.SNAPSHOT_OUTAGE_FALLBACK = old
        self.assertEqual(["date"], calls)

    def test_the_live_loop_uses_it_and_replays_do_not(self):
        body = open(predict.__file__).read()
        loop = body[body.index("for movie in movies_to_predict:\n        nat_count"):][:900]
        self.assertIn("forecast = predict_movie if through_date else functools.partial(", loop)
        self.assertIn("predict_with_outage_fallback, predict_movie)", loop)
        self.assertIn("pred = forecast(movie,", loop)

    def test_an_outage_forecast_is_logged_as_an_outage(self):
        body = open(predict.__file__).read()
        self.assertIn('"data_outage": "1" if pred.get("data_outage") else "",', body)


class ThursdayOutageReplayTest(unittest.TestCase):
    """The shape of 2026-11-19 at 21:30Z, one show date."""

    def build(self):
        rows = []
        for n in range(20):                                   # Eastern: last night only
            rows += visit("night", at(3 + n / 20), range(12), theatre=f"AMC East {n}", tz="ET")
        for n in range(12):                                   # Central: night + 14:00Z re-read
            rows += visit("night", at(5), range(12), theatre=f"AMC Central {n}", tz="CT")
            rows += visit("reread", at(14), range(12), theatre=f"AMC Central {n}", tz="CT")
        for n in range(8):                                    # Pacific: morning, then the block
            rows += visit("morning", at(8), range(12), theatre=f"AMC West {n}", tz="PT")
        for n in range(6):
            rows += visit("blocked", at(21), [n % 12], theatre=f"AMC West {n}", tz="PT")
        return rows

    def test_every_zone_keeps_its_last_full_read(self):
        kept = window(self.build())
        by_zone = {}
        for r in kept:
            by_zone.setdefault(r["timezone"], set()).add((r["theatre_name"], r["run_id"]))
        self.assertEqual(len(by_zone["ET"]), 20)
        self.assertEqual({run for _, run in by_zone["CT"]}, {"reread"})
        self.assertEqual(len(by_zone["PT"]), 8)
        self.assertEqual({run for _, run in by_zone["PT"]}, {"morning"})
        self.assertEqual(len(kept), (20 + 12 + 8) * 12)

    def test_old_rule_loses_the_eastern_zone_and_most_pacific_showings(self):
        kept = window(self.build(), zone_reference="date")
        zones = {r["timezone"] for r in kept}
        self.assertNotIn("ET", zones)
        self.assertEqual(len([r for r in kept if r["timezone"] == "PT"]), 6)


if __name__ == "__main__":
    unittest.main()
