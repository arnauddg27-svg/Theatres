import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import harkins_collect as H  # noqa: E402

DAY = {"movies": [
    {"movieId": 16093, "performances": [
        {"showtimeUtc": "9/27/2026 2:35:00 AM", "showtime": "September 26, 2026 7:35 PM",
         "url": "https://harkins.com/ticketing/theatre/16/movie/HO00016093/session/573969/date/2026-09-26 19:35"},
        {"showtimeUtc": "9/26/2026 6:15:00 PM", "showtime": "September 26, 2026 11:15 AM",
         "url": "https://harkins.com/ticketing/theatre/16/movie/HO00016093/session/576394/date/2026-09-26 11:15"}]},
    {"movieId": 16074, "performances": [
        {"showtimeUtc": "9/27/2026 2:00:00 AM", "showtime": "September 26, 2026 7:00 PM",
         "url": "https://harkins.com/ticketing/theatre/16/movie/HO00016074/session/1/date/2026-09-26 19:00"}]},
]}
TITLES = {16093: "Heart of the Beast", 16074: "Some Other Film"}
TARGET = {"heart-of-the-beast": "Heart of the Beast"}


class HarkinsLaneTest(unittest.TestCase):
    def test_sold_is_capacity_minus_open(self):
        self.assertEqual({"total": 119, "sold": 32, "available": 87, "broken": 0, "price_cents": None},
                         H.seat_counts({"numberOfSeats": 119, "openSeats": 87}))

    def test_day_schedule_format_is_normalized(self):
        p = H.normalize_performance(DAY["movies"][0]["performances"][0])
        self.assertEqual(("573969", "2026-09-26", "2026-09-27T02:35:00Z", "2026-09-26T19:35:00"),
                         (p["sessionId"], p["businessDate"], p["showtimeUTCDate"], p["showtimeDate"]))

    def test_pre_and_post_windows(self):
        now = datetime(2026, 9, 27, 2, 0, tzinfo=timezone.utc)
        pre = H.pick_performances(DAY, TITLES, TARGET, now, "pre")
        self.assertEqual(["573969"], [p["sessionId"] for p, _ in pre])            # 11:15 started, other film untracked
        post = H.pick_performances(DAY, TITLES, TARGET, datetime(2026, 9, 27, 3, 0, tzinfo=timezone.utc), "post")
        self.assertEqual(["573969"], [p["sessionId"] for p, _ in post])           # 25 min after start

    def test_theatre_time_zones(self):
        self.assertEqual("America/Phoenix", H.theatre_tz({"state": "AZ", "timeZone": {"id": "US Mountain Standard Time"}}))
        self.assertEqual("America/Los_Angeles", H.theatre_tz({"state": "CA", "timeZone": {"id": "Pacific Standard Time"}}))
        self.assertEqual("America/Chicago", H.theatre_tz({"state": "OK", "timeZone": {"id": "Central Standard Time"}}))
        self.assertEqual("America/Denver", H.theatre_tz({"state": "CO", "timeZone": {"id": "Mountain Standard Time"}}))


    def test_post_reads_stored_sessions_after_start(self):
        import tempfile, os
        from fandango_collect import append_unique_fandango_rows
        th = {"id": 16, "name": "Arizona Mills 18", "city": "Tempe", "state": "AZ", "timeZone": {"id": "US Mountain Standard Time"}}
        perf = H.normalize_performance(DAY["movies"][0]["performances"][0])      # 19:35 MST = 02:35Z
        before = datetime(2026, 9, 27, 1, 50, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "h.csv")
            row = H.build_row(th, perf, "Heart of the Beast", H.seat_counts({"numberOfSeats": 119, "openSeats": 87}),
                              "2026-09-25", "r", before, vista_id="0000000002")
            append_unique_fandango_rows([row], csv_path=__import__("pathlib").Path(path))
            got = H.stored_post_performances("2026-09-25", datetime(2026, 9, 27, 2, 51, tzinfo=timezone.utc), path=path)
            self.assertEqual([(16, "573969", "0000000002")], [(t, p["sessionId"], p["vistaId"]) for t, p, _ in got])
            self.assertEqual([], H.stored_post_performances("2026-09-25", before, path=path))


if __name__ == "__main__":
    unittest.main()


class PrePassWeekendTest(unittest.TestCase):
    """2026-09-28: Monday 00:40Z pre passes anchored to the NEXT weekend (no
    titles) and skipped Sunday's remaining shows."""

    def test_early_monday_reads_the_playing_weekend(self):
        from datetime import datetime, timezone
        from scraper import opening_weekend_friday, phase1_weekend_anchor
        import alamo_collect as A
        import harkins_collect as H
        early = datetime(2026, 9, 28, 0, 40, tzinfo=timezone.utc)      # Sunday 8:40pm ET
        noon = datetime(2026, 9, 28, 13, 0, tzinfo=timezone.utc)
        for mod in (A, H):
            self.assertEqual(opening_weekend_friday(early.replace(tzinfo=None)), mod.pre_pass_weekend(early))
            self.assertEqual("2026-09-25", mod.pre_pass_weekend(early))
            self.assertEqual(phase1_weekend_anchor(noon.replace(tzinfo=None), full_weekend=True),
                             mod.pre_pass_weekend(noon))


class LoudFailThresholdTest(unittest.TestCase):
    def test_single_failed_read_is_not_an_outage(self):
        import alamo_collect as A
        import harkins_collect as H
        for mod in (A, H):
            self.assertEqual(5, mod.LOUD_FAIL_MIN_MATCHED)
