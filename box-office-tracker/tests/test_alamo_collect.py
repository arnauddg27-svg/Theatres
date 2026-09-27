import csv
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import alamo_collect as A  # noqa: E402
import fandango_collect as F  # noqa: E402


def _seat(status, price=1500):
    return {"seatStatus": status, "defaultPriceInCents": price}


SEATING = {"areas": [{"rows": [{"seats": [_seat("SOLD"), _seat("SOLD", -1), _seat("EMPTY"), _seat("NONE"), _seat("BROKEN")]}]}]}
SCHEDULE = {
    "market": [{"cinemas": [{"id": "0007", "name": "Lakeline", "city": "Austin", "timeZoneName": "America/Chicago"}]}],
    "presentations": [{"slug": "primetime", "show": {"title": "Primetime"}},
                      {"slug": "other", "show": {"title": "Other Film"}}],
    "sessions": [
        {"cinemaId": "0007", "sessionId": "1", "presentationSlug": "primetime", "businessDateClt": "2026-09-26",
         "showTimeClt": "2026-09-26T19:00:00", "showTimeUtc": "2026-09-27T00:00:00", "reservedSeating": True,
         "cinemaTimeZoneName": "America/Chicago", "screenNumber": "7", "formatSlug": "2d-digital"},
        {"cinemaId": "0007", "sessionId": "2", "presentationSlug": "primetime", "businessDateClt": "2026-09-26",
         "showTimeClt": "2026-09-26T12:00:00", "showTimeUtc": "2026-09-26T17:00:00", "reservedSeating": True},
        {"cinemaId": "0007", "sessionId": "3", "presentationSlug": "other", "businessDateClt": "2026-09-26",
         "showTimeClt": "2026-09-26T19:00:00", "showTimeUtc": "2026-09-27T00:00:00", "reservedSeating": True},
        {"cinemaId": "0007", "sessionId": "4", "presentationSlug": "primetime", "businessDateClt": "2026-10-03",
         "showTimeClt": "2026-10-03T19:00:00", "showTimeUtc": "2026-10-04T00:00:00", "reservedSeating": True},
    ],
}
NOW = datetime(2026, 9, 26, 20, 0, tzinfo=timezone.utc)


class AlamoLaneTest(unittest.TestCase):
    def test_seat_counts_skip_aisles_and_broken_and_bad_prices(self):
        c = A.seat_counts(SEATING)
        self.assertEqual({"total": 3, "sold": 2, "available": 1, "broken": 1, "price_cents": 1500}, c)

    def test_pre_selects_upcoming_tracked_in_window_only(self):
        picks = A.select_sessions(SCHEDULE, {"primetime": "Primetime"}, A.window_dates("2026-09-25"), NOW, "pre")
        self.assertEqual(["1"], [s["sessionId"] for s, _, _ in picks])      # 2 started, 3 untracked, 4 next week

    def test_rows_keep_zero_counts_and_post_rows_are_tagged(self):
        s, cinema, title = A.select_sessions(SCHEDULE, {"primetime": "Primetime"}, A.window_dates("2026-09-25"), NOW)[0]
        zero = {"total": 100, "sold": 0, "available": 100, "broken": 0, "price_cents": None}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "a.csv"
            pre = A.build_row(s, cinema, title, zero, "2026-09-25", "r1", NOW)
            post = A.build_row(s, cinema, title, zero, "2026-09-25", "r2", NOW.replace(hour=23), post=True)
            F.append_unique_fandango_rows([pre, post], csv_path=path)
            rows = list(csv.DictReader(open(path)))
            self.assertEqual(["0", "0"], [r["reserved_seats"] for r in rows])       # 0 is not blanked
            self.assertEqual(["0.0", "0.0"], [r["occupancy_pct"] for r in rows])
            self.assertEqual(["alamo-api", "post-show-census"], [r["row_kind"] for r in rows])
            self.assertEqual("ALMO", rows[0]["chain"])
            self.assertEqual("Alamo Drafthouse Lakeline", rows[0]["theatre_name"])

    def test_post_pass_revisits_stored_sessions_that_just_started(self):
        s, cinema, title = A.select_sessions(SCHEDULE, {"primetime": "Primetime"}, A.window_dates("2026-09-25"), NOW)[0]
        counts = {"total": 10, "sold": 5, "available": 5, "broken": 0, "price_cents": None}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "a.csv"
            F.append_unique_fandango_rows([A.build_row(s, cinema, title, counts, "2026-09-25", "r", NOW)], csv_path=path)
            at = datetime(2026, 9, 27, 0, 30, tzinfo=timezone.utc)                  # 30 min after the 19:00 CT start
            got = A.stored_post_sessions("2026-09-25", at, path=path)
            self.assertEqual(["1"], [x[0]["sessionId"] for x in got])
            self.assertEqual([], A.stored_post_sessions("2026-09-25", datetime(2026, 9, 26, 23, 0, tzinfo=timezone.utc), path=path))  # not started
            self.assertEqual([], A.stored_post_sessions("2026-09-25", datetime(2026, 9, 27, 3, 0, tzinfo=timezone.utc), path=path))   # window passed


if __name__ == "__main__":
    unittest.main()
