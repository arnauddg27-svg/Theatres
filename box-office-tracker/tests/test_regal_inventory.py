"""Regal showing inventory parser (2026-10-27)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import regal_inventory as R  # noqa: E402

PAGE = {"showtimes": [{"AdvertiseShowDate": "2026-10-30T00:00:00", "Film": [
    {"Title": "Clayface", "Performances": [
        {"Auditorium": 9, "PerformanceId": 1, "PerformanceAttributes": ["2D", "Laser"],
         "CalendarShowTime": "2026-10-30T13:30:00", "UtcShowTime": "2026-10-30T17:30:00.000Z", "StopSales": False},
        {"Auditorium": 2, "PerformanceId": 2, "PerformanceAttributes": ["IMAX"],
         "CalendarShowTime": "2026-10-30T19:00:00", "UtcShowTime": "2026-10-30T23:00:00.000Z", "StopSales": False}]},
    {"Title": "Clayface: The IMAX Experience", "Performances": [
        {"Auditorium": 1, "PerformanceId": 3, "PerformanceAttributes": ["IMAX"],
         "CalendarShowTime": "2026-10-30T21:00:00", "UtcShowTime": "2026-10-31T01:00:00.000Z", "StopSales": False}]},
    {"Title": "Some Other Film", "Performances": [{"PerformanceId": 9, "CalendarShowTime": "2026-10-30T12:00:00"}]},
]}]}
THEATRE = {"name": "Regal Aviation Mall", "city": "Queensbury", "state": "NY", "theatre_code": "1731"}


class InventoryParseTest(unittest.TestCase):
    def test_rows_for_tracked_films_in_window(self):
        rows = R.performance_rows(PAGE, THEATRE, {"clayface": "Clayface"}, {"2026-10-30"}, "2026-10-30", "t")
        self.assertEqual([(r["movie_title"], r["showtime"], r["showtime_id"]) for r in rows],
                         [("Clayface", "13:30", "1"), ("Clayface", "19:00", "2"), ("Clayface", "21:00", "3")])
        self.assertTrue(all(r["chain"] == "REGL" and r["row_kind"] == "regal-inventory" for r in rows))
        self.assertEqual(rows[1]["auditorium_type"], "IMAX")
        self.assertIn("theatre_code=1731", rows[0]["notes"])

    def test_out_of_window_dates_dropped(self):
        self.assertEqual(R.performance_rows(PAGE, THEATRE, {"clayface": "Clayface"}, {"2026-10-31"}, "w", "t"), [])

    def test_walls_detected(self):
        self.assertTrue(R.looks_walled(403, ""))
        self.assertTrue(R.looks_walled(200, "<title>Just a moment...</title>"))
        self.assertFalse(R.looks_walled(200, "<html>ok</html>"))

    def test_next_data(self):
        html = '<script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"x":1}}}</script>'
        self.assertEqual(R.next_data(html)["props"]["pageProps"]["x"], 1)
        self.assertIsNone(R.next_data("<html></html>"))


if __name__ == "__main__":
    unittest.main()
