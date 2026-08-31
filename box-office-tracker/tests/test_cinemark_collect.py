import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cinemark_collect as cc  # noqa: E402


class CinemarkCollectTest(unittest.TestCase):
    def test_selftest_passes(self):
        # The module's offline selftest covers href parsing, slug matching,
        # sitemap URL parsing, showtime selection, and row schema.
        cc._selftest()

    def test_schema_is_the_fandango_superset(self):
        from fandango_collect import FANDANGO_PRE_RESERVATION_FIELDS
        self.assertEqual(FANDANGO_PRE_RESERVATION_FIELDS, cc.CINEMARK_FIELDS)

    def test_append_rows_dedupes_and_writes_header_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "cinemark.csv"
            os.environ["CINEMARK_OUTPUT"] = str(out)
            try:
                row = {f: "" for f in cc.CINEMARK_FIELDS}
                row.update({"weekend_of": "2026-08-28", "movie_title": "X",
                            "theatre_name": "T", "showtime_id": "2026-08-28 19:00",
                            "show_date": "2026-08-28", "snapshot_bucket": "B",
                            "chain": "CNMK", "reserved_seats": "5"})
                w1, d1 = cc.append_rows([row, dict(row)])
                self.assertEqual((1, 1), (w1, d1))
                w2, d2 = cc.append_rows([dict(row)])
                self.assertEqual((0, 1), (w2, d2))
                rows = list(csv.DictReader(open(out)))
                self.assertEqual(1, len(rows))
                self.assertEqual("CNMK", rows[0]["chain"])
            finally:
                os.environ.pop("CINEMARK_OUTPUT", None)

    def test_scheduler_slots_implement_the_three_read_design(self):
        # Deliberately ENABLED 2026-08-31 after scale (zero blocks, run
        # 33426873143) and upcoming-day (run 33430418143) validation.
        # Structure pinned: pre passes EVERY day; post census only on UTC
        # Fri/Sat/Sun/Mon early hours (= Thu-Sun evenings locally); before
        # Thursday, pre-reservation only.
        import importlib.util
        sched_path = (Path(__file__).resolve().parents[1] /
                      "scripts" / "schedule_box_office_pipeline.py")
        spec = importlib.util.spec_from_file_location("sched_cin_test", sched_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cin = [s for s in mod.SLOTS if s.inputs.get("phase") == "scrape-cinemark"]
        self.assertEqual(3, len(cin))
        pre = [s for s in cin if s.inputs.get("cinemark_mode") != "post"]
        post = [s for s in cin if s.inputs.get("cinemark_mode") == "post"]
        self.assertEqual(2, len(pre))
        self.assertEqual(1, len(post))
        for s in pre:
            self.assertEqual(frozenset(range(7)), s.cron_days, s.name)
        self.assertEqual(frozenset({0, 1, 5, 6}), post[0].cron_days)


if __name__ == "__main__":
    unittest.main()


class PostModeAnchorTest(unittest.TestCase):
    def test_post_window_covers_full_show_day(self):
        # 18h window: the Monday/weekend 06:20Z pass must census matinees
        # too, not only evening shows.
        self.assertGreaterEqual(cc.CINEMARK_POST_SHOW_WINDOW_MIN, 1000)

    def test_post_mode_selects_started_shows_newest_first(self):
        from datetime import datetime, timezone
        targets = {"the-dog-stars": "The Dog Stars"}
        now = datetime(2026, 8, 31, 6, 20, tzinfo=timezone.utc)  # Mon 06:20Z
        entries = [
            {"href": "/TicketSeatMap/?TheaterId=1&ShowtimeId=10&Showtime=2026-08-30T19:30:00",
             "movie_href": "/movies/the-dog-stars"},   # Sun 19:30 CT, started ~5h ago
            {"href": "/TicketSeatMap/?TheaterId=1&ShowtimeId=11&Showtime=2026-08-30T13:00:00",
             "movie_href": "/movies/the-dog-stars"},   # Sun matinee, ~11.5h ago
            {"href": "/TicketSeatMap/?TheaterId=1&ShowtimeId=12&Showtime=2026-08-31T19:00:00",
             "movie_href": "/movies/the-dog-stars"},   # future -> excluded in post
        ]
        picks = cc.select_showtimes(entries, targets, {"2026-08-30", "2026-08-31"},
                                    "America/Chicago", now, cap=5, mode="post")
        self.assertEqual(["10", "11"],
                         [p["showtime_id"] for p in picks])  # newest started first
        self.assertTrue(all(p["post_show"] for p in picks))
