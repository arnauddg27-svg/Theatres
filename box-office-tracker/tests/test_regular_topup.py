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


if __name__ == "__main__":
    unittest.main()
