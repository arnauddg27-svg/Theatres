"""Regular-scrape top-up: skip captured showings, fail a leg that captured too few."""
import csv
import tempfile
import unittest
from pathlib import Path

import scraper


def _links(ids_by_movie, date="2026-11-14", tz="CT"):
    return {
        "tz": tz,
        "dates": {date: {"movies": {
            movie: [{"showtime": "7:00pm", "showtime_id": sid, "format": "Laser at AMC"}
                    for sid in ids]
            for movie, ids in ids_by_movie.items()
        }}},
    }


class CapturedShowtimeIdsTest(unittest.TestCase):
    def _write(self, rows):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        writer = csv.DictWriter(tmp, fieldnames=["date", "amc_seat_map_url"])
        writer.writeheader()
        writer.writerows(rows)
        tmp.close()
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return tmp.name

    def test_reads_ids_for_the_requested_dates_only(self):
        path = self._write([
            {"date": "2026-11-14", "amc_seat_map_url": "https://www.amctheatres.com/showtimes/111/seats"},
            {"date": "2026-11-14", "amc_seat_map_url": "https://www.amctheatres.com/showtimes/222/seats"},
            {"date": "2026-11-13", "amc_seat_map_url": "https://www.amctheatres.com/showtimes/333/seats"},
            {"date": "2026-11-14", "amc_seat_map_url": ""},
        ])
        self.assertEqual(
            scraper.captured_showtime_ids({"2026-11-14"}, path=path),
            {"2026-11-14": {"111", "222"}},
        )

    def test_missing_file_means_nothing_captured(self):
        self.assertEqual(
            scraper.captured_showtime_ids({"2026-11-14"}, path="/nonexistent/seat-counts.csv"),
            {"2026-11-14": set()},
        )


class DropCapturedShowtimesTest(unittest.TestCase):
    def test_drops_only_captured_showings(self):
        movies = {
            "Ebenezer": [{"showtime_id": "1"}, {"showtime_id": "2"}],
            "Ghost Soldier": [{"showtime_id": "3"}],
        }
        remaining, skipped = scraper.drop_captured_showtimes(movies, {"1", "3"})
        self.assertEqual(skipped, 2)
        self.assertEqual(remaining, {"Ebenezer": [{"showtime_id": "2"}], "Ghost Soldier": []})

    def test_first_pass_reads_everything(self):
        movies = {"Ebenezer": [{"showtime_id": "1"}]}
        remaining, skipped = scraper.drop_captured_showtimes(movies, set())
        self.assertIs(remaining, movies)
        self.assertEqual(skipped, 0)


class RegularShowingCaptureTest(unittest.TestCase):
    def setUp(self):
        self.theatres = [{"name": "AMC A", "_tz": "CT"}, {"name": "AMC B", "_tz": "CT"}]
        self.saved = {
            "AMC A": _links({"Ebenezer": ["1", "2"], "Untracked": ["9"]}),
            "AMC B": _links({"Ebenezer": ["3", "4"]}),
        }
        self.expected = {"CT": "2026-11-14"}
        # The collection-window filter is date/time dependent; this test is
        # about counting, so let every saved showing through.
        original = scraper.filter_showtime_entries_for_collection_window
        scraper.filter_showtime_entries_for_collection_window = lambda shows, date: list(shows)
        self.addCleanup(setattr, scraper, "filter_showtime_entries_for_collection_window", original)

    def test_counts_tracked_titles_only(self):
        captured, linked = scraper.regular_showing_capture(
            self.theatres, self.saved, ["Ebenezer"], self.expected,
            {"2026-11-14": {"1", "3", "9"}})
        self.assertEqual((captured, linked), (2, 4))

    def test_other_dates_do_not_count(self):
        captured, linked = scraper.regular_showing_capture(
            self.theatres, self.saved, ["Ebenezer"], self.expected,
            {"2026-11-13": {"1", "2", "3", "4"}})
        self.assertEqual((captured, linked), (0, 4))


class RegularCaptureShortfallTest(unittest.TestCase):
    def test_saturday_1114_central_and_mountain_fail(self):
        # 2026-11-14 post-show scrape: CT 2157/3330 linked, MT 222/450.
        self.assertIn("minimum 85%", scraper.regular_capture_shortfall(2157, 3330))
        self.assertIsNotNone(scraper.regular_capture_shortfall(222, 450))

    def test_normal_nights_pass(self):
        # Lowest normal leg seen 11-08..11-15: ET 3877/4110 (94.3%).
        self.assertIsNone(scraper.regular_capture_shortfall(3877, 4110))
        self.assertIsNone(scraper.regular_capture_shortfall(5213, 5248))

    def test_nothing_linked_is_not_a_shortfall(self):
        self.assertIsNone(scraper.regular_capture_shortfall(0, 0))

    def test_floor_can_be_switched_off(self):
        self.assertIsNone(scraper.regular_capture_shortfall(1, 100, min_ratio=0.0))


class WavePauseStreakTest(unittest.TestCase):
    """2026-11-15: in-flight theatres burned the next pause 7 s into the last one."""

    def test_blocks_during_a_pause_do_not_advance_the_streak(self):
        self.assertEqual(scraper._hold_streak_during_pause(0, 1, None, paused=True), (0, None))
        self.assertEqual(scraper._hold_streak_during_pause(5, 6, "why", paused=True), (5, None))

    def test_blocks_outside_a_pause_count(self):
        self.assertEqual(scraper._hold_streak_during_pause(5, 6, None, paused=False), (6, None))
        self.assertEqual(scraper._hold_streak_during_pause(11, 12, "why", paused=False), (12, "why"))

    def test_real_data_resets_the_streak_even_during_a_pause(self):
        self.assertEqual(scraper._hold_streak_during_pause(4, 0, None, paused=True), (0, None))


class SnapshotCaptureShortfallTest(unittest.TestCase):
    """Theatre-slice coverage passed the 2026-11-19 02:30Z Central leg at
    94.2% while it read 53.9% of its linked showings."""

    def test_quiet_legs_pass(self):
        for read, linked in ((7672, 7753), (2652, 2741), (13650, 16008)):
            self.assertIsNone(scraper.snapshot_capture_shortfall(read, linked), (read, linked))

    def test_walled_legs_fail_with_the_numbers(self):
        msg = scraper.snapshot_capture_shortfall(4517, 8385)
        self.assertIn("4517/8385", msg)
        self.assertIn("53.9%", msg)
        self.assertIsNotNone(scraper.snapshot_capture_shortfall(241, 1274))
        self.assertIsNotNone(scraper.snapshot_capture_shortfall(2241, 2741))

    def test_tiny_or_empty_legs_are_not_judged(self):
        self.assertIsNone(scraper.snapshot_capture_shortfall(0, 0))
        self.assertIsNone(scraper.snapshot_capture_shortfall(10, 49))
        self.assertIsNotNone(scraper.snapshot_capture_shortfall(10, 50))

    def test_zero_ratio_disables(self):
        self.assertIsNone(scraper.snapshot_capture_shortfall(1, 1000, min_ratio=0))

    def test_defaults(self):
        self.assertEqual(0.85, scraper.SNAPSHOT_MIN_SHOWING_CAPTURE_RATIO)
        self.assertEqual(50, scraper.SNAPSHOT_MIN_SHOWING_CAPTURE_LINKS)

    def test_failed_snapshot_leg_keeps_its_rows_in_the_merge(self):
        # the red leg writes no fatal marker; the merge keeps snapshot-only
        # sources whatever the job status
        src = (Path(scraper.__file__).parent / "scripts" / "merge_scrape_artifacts.py").read_text()
        self.assertIn("if writes_snapshots and not successful and not snapshots_only:", src)
        body = Path(scraper.__file__).read_text()
        tail = body[body.index("if snapshot_shortfall:\n        # No fatal marker"):][:400]
        self.assertNotIn("snapshot-fatal.marker", tail)


class WaveRateTest(unittest.TestCase):
    """2026-11-19: the Eastern snapshot leg was walled on 30-80% of its seat
    requests for 65 minutes and never paused, because the consecutive-theatre
    streak kept resetting on the reads that still landed."""

    def test_defaults(self):
        self.assertEqual(900, scraper.CF_BLOCK_PAUSE_SEC)
        self.assertEqual((120, 60, 0.15), (scraper.CF_WAVE_WINDOW_SEC, scraper.CF_WAVE_MIN_WALLS,
                                           scraper.CF_WAVE_SHARE))

    def test_quiet_reading_is_not_a_wave(self):
        # 11-19 03:10Z: 1,939 reads and 6 walls in ten minutes
        self.assertFalse(scraper.wave_in_window([(0, 0, 0), (60, 190, 1), (120, 388, 2)]))

    def test_cold_start_burst_is_not_a_wave(self):
        # 11-19 02:44-02:50Z: 805 reads, 56 walls (6.5%) while threads find an exit
        self.assertFalse(scraper.wave_in_window([(0, 0, 0), (60, 130, 25), (120, 270, 40)]))

    def test_mild_wave_trips(self):
        # 11-18 04:00Z Central: 1,403 reads / 374 walls per ten minutes (21%)
        self.assertTrue(scraper.wave_in_window([(0, 5000, 100), (60, 5140, 137), (120, 5281, 175)]))

    def test_deep_wave_trips(self):
        # 11-19 04:20Z Eastern: 306 reads / 1,186 walls per ten minutes
        self.assertTrue(scraper.wave_in_window([(0, 9000, 500), (120, 9061, 737)]))

    def test_only_the_window_counts(self):
        old_walls = [(0, 0, 0), (100, 50, 400), (1000, 3000, 405), (1100, 3300, 410)]
        self.assertFalse(scraper.wave_in_window(old_walls))

    def test_a_few_walls_with_no_reads_is_not_yet_a_wave(self):
        self.assertFalse(scraper.wave_in_window([(0, 0, 0), (30, 0, 59)]))
        self.assertTrue(scraper.wave_in_window([(0, 0, 0), (30, 0, 60)]))

    def test_needs_two_readings_and_can_be_switched_off(self):
        self.assertFalse(scraper.wave_in_window([]))
        self.assertFalse(scraper.wave_in_window([(0, 0, 500)]))
        self.assertFalse(scraper.wave_in_window([(0, 0, 0), (30, 0, 500)], share=0))

    def test_totals_come_from_the_http_lane_counters(self):
        # a data-endpoint read bumps BOTH _RSC_STATE["ok"] and http_ok, so only
        # http_ok is counted (summing them halved the measured wall share)
        saved = (scraper._RSC_STATE["ok"], scraper._HTTP_STATE["http_ok"], scraper._HTTP_STATE["http_blocked"])
        try:
            scraper._RSC_STATE["ok"], scraper._HTTP_STATE["http_ok"], scraper._HTTP_STATE["http_blocked"] = 281, 281, 75
            self.assertEqual((281, 75), scraper.seat_request_totals())
            ok, walls = scraper.seat_request_totals()
            self.assertTrue(scraper.wave_in_window([(0, 0, 0), (120, ok, walls)]))   # the 21% wave trips
        finally:
            scraper._RSC_STATE["ok"], scraper._HTTP_STATE["http_ok"], scraper._HTTP_STATE["http_blocked"] = saved

    def test_snapshot_floor_counts_showings_read_not_rows_written(self):
        body = Path(scraper.__file__).read_text()
        block = body[body.index("snapshot_shortfall = None\n    if snapshots_only and not test_max:"):][:900]
        self.assertIn("snapshot_read = len(cf_read_ids)", block)
        self.assertNotIn("snapshot_rows_written + snapshot_rows_skipped", block)


class WaveRetryTest(unittest.TestCase):
    def test_each_show_date_visit_is_its_own_retry(self):
        a = {"name": "AMC Test 12", "_date": "2026-11-20"}
        b = {"name": "AMC Test 12", "_date": "2026-11-21"}
        self.assertNotEqual(scraper.cf_retry_key(a), scraper.cf_retry_key(b))
        self.assertEqual(("AMC Test 12", ""), scraper.cf_retry_key({"name": "AMC Test 12"}))

    def test_ids_from_seat_rows_and_snapshot_rows(self):
        seat_row = ["2026-11-20", "run", "AMC Test 12", "7:00pm",
                    "https://www.amctheatres.com/showtimes/148037756/seats", "note"]
        snap_row = {"showtime_id": 148096033, "amc_seat_map_url": "https://www.amctheatres.com/showtimes/148096033/seats"}
        url_only = {"showtime_id": "", "amc_seat_map_url": "https://www.amctheatres.com/showtimes/147929262/seats"}
        self.assertEqual({"148037756", "148096033", "147929262"},
                         scraper.read_showtime_ids([seat_row, snap_row, url_only]))
        self.assertEqual(set(), scraper.read_showtime_ids(None))

    def test_retry_reads_only_the_showings_still_missing(self):
        saved = {"Film": [{"showtime_id": "1"}, {"showtime_id": "2"}, {"showtime_id": "3"}]}
        remaining, skipped = scraper.drop_captured_showtimes(saved, {"1", "3"})
        self.assertEqual(([{"showtime_id": "2"}], 2), (remaining["Film"], skipped))

    def test_the_retry_pass_never_pauses(self):
        body = Path(scraper.__file__).read_text()
        block = body[body.index("if ((cf_block_streak >= CF_BLOCK_PAUSE_AFTER or wave)"):][:260]
        self.assertIn("and not cf_retry_pass", block)

    def test_partly_read_theatres_join_the_retry(self):
        body = Path(scraper.__file__).read_text()
        block = body[body.index("cf_read_ids.update(read_showtime_ids(csv_rows))"):][:900]
        self.assertIn("any(CF_BLOCK_ISSUE in i for i in issues)", block)
        self.assertNotIn("not results and not snapshot_rows", block)


class PreShowRowsAreNotFinalsTest(unittest.TestCase):
    """Review 2026-11-19: a seat row read before its showing started counted
    as captured, so a later top-up would skip that showing for good."""

    def _write(self, td, rows):
        path = Path(td) / "seat.csv"
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["date", "amc_seat_map_url", "minutes_after_showtime"])
            w.writeheader()
            w.writerows(rows)
        return path

    def test_negative_minutes_do_not_count(self):
        url = "https://www.amctheatres.com/showtimes/{}/seats"
        with tempfile.TemporaryDirectory() as td:
            path = self._write(td, [
                {"date": "2026-11-14", "amc_seat_map_url": url.format(1), "minutes_after_showtime": "95"},
                {"date": "2026-11-14", "amc_seat_map_url": url.format(2), "minutes_after_showtime": "-400"},
                {"date": "2026-11-14", "amc_seat_map_url": url.format(3), "minutes_after_showtime": "0"},
                {"date": "2026-11-14", "amc_seat_map_url": url.format(4), "minutes_after_showtime": ""},
            ])
            self.assertEqual({"1", "3", "4"}, scraper.captured_showtime_ids({"2026-11-14"}, path=path)["2026-11-14"])

    def test_afternoon_regular_leg_has_no_finals_to_read(self):
        from datetime import datetime
        for hour, unplayed in ((2, False), (9, False), (11, False), (12, True), (15, True), (20, True),
                               (21, False), (23, False)):
            self.assertEqual(unplayed, scraper.regular_leg_targets_unplayed_day(datetime(2026, 11, 15, hour, 30)), hour)
        self.assertFalse(scraper.REGULAR_ALLOW_SAME_DAY)


if __name__ == "__main__":
    unittest.main()
