"""2nd/3rd-weekend (holdover) collection + forecast (2026-10-31)."""
import csv
import os
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import holdover as H  # noqa: E402
import holdover_backtest as B  # noqa: E402
import holdover_forecast as F  # noqa: E402

NOW = datetime(2026, 10, 31, 16, 0, tzinfo=timezone.utc)
EVENTS = [
    {"title": '"Clayface" 2nd Weekend Box Office', "slug": "clayface-2nd", "endDate": "2026-11-01T12:00:00Z",
     "volume": "34181"},
    {"title": "“Wildwood” 2nd Weekend Box Office", "slug": "wildwood-2nd",
     "endDate": "2026-11-01T12:00:00Z", "volume": "20869"},
    {"title": '"You Can See Everything" 3rd Weekend Box Office', "slug": "ycse-3rd",
     "endDate": "2026-11-01T12:00:00Z", "volume": "18770"},
    {"title": '"Old" 4th Weekend Box Office', "slug": "old-4th", "endDate": "2026-11-01T12:00:00Z"},
    {"title": '"Gone" 2nd Weekend Box Office', "slug": "gone", "endDate": "2026-11-01T12:00:00Z", "closed": True},
    {"title": '"Godzilla Minus Zero" Opening Weekend Box Office', "slug": "gmz",
     "endDate": "2026-11-08T12:00:00Z"},
]
SHAPE = {"drop": 0.5, "u_saturday": 1.2, "u_sunday": 1.1, "v_sunday": 0.95,
         "band_q10_q90": {"prior": [0.7, 1.3], "fri_known": [0.9, 1.15], "fri_sat_known": [0.95, 1.07]}}


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.reg = os.path.join(self.tmp.name, "holdover-titles.csv")
        self.act = os.path.join(self.tmp.name, "daily.csv")

    def tearDown(self):
        self.tmp.cleanup()

    def test_parse_event_title(self):
        self.assertEqual(H.parse_event_title('"Wildwood" 2nd Weekend Box Office'), ("Wildwood", 2))
        self.assertEqual(H.parse_event_title("“X: Y” 3rd weekend box office"), ("X: Y", 3))
        self.assertIsNone(H.parse_event_title('"Wildwood" Opening Weekend Box Office'))
        self.assertIsNone(H.parse_event_title('"A" vs "B" 2nd Weekend Box Office'))

    def test_entries_weekend_opening_and_caps(self):
        rows = {r["movie"]: r for r in H.entries_from_events(EVENTS, NOW)}
        self.assertEqual(set(rows), {"Clayface", "Wildwood", "You Can See Everything"})  # 4th wk + closed out
        self.assertEqual(rows["Wildwood"]["weekend_of"], "2026-10-30")
        self.assertEqual(rows["Wildwood"]["opening_weekend_of"], "2026-10-23")
        self.assertEqual(rows["You Can See Everything"]["opening_weekend_of"], "2026-10-16")

    def test_register_is_append_only_and_deduped(self):
        new = H.register(H.entries_from_events(EVENTS, NOW), self.reg)
        self.assertEqual(len(new), 3)
        self.assertEqual(H.register(H.entries_from_events(EVENTS, NOW), self.reg), [])
        self.assertEqual([r["movie"] for r in H.entries("2026-10-30", self.reg)],
                         ["Clayface", "Wildwood", "You Can See Everything"])   # by volume

    def test_collection_titles_fill_room_after_openers(self):
        H.register(H.entries_from_events(EVENTS, NOW), self.reg)
        with mock.patch.dict(os.environ, {"HOLDOVER_COLLECTION": "1", "HOLDOVER_MAX_TRACKED_TITLES": "4"}):
            self.assertEqual(H.collection_titles("2026-10-30", ["A", "B"], self.reg, live=False),
                             ["Clayface", "Wildwood"])
            self.assertEqual(H.collection_titles("2026-10-30", [], self.reg, live=False),
                             ["Clayface", "Wildwood", "You Can See Everything"])
            self.assertEqual(H.collection_titles("2026-10-23", [], self.reg, live=False), [])
        with mock.patch.dict(os.environ, {"HOLDOVER_COLLECTION": "0"}):
            self.assertEqual(H.collection_titles("2026-10-30", [], self.reg, live=False), [])

    def test_is_holdover_registry_or_opened_earlier(self):
        H.register(H.entries_from_events(EVENTS, NOW), self.reg)
        with open(self.act, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["weekend_of", "movie_title", "day_of_week", "gross_m"])
            w.writerow(["2026-10-16", "Whalefall", "Friday", "3.1"])
            w.writerow(["2026-10-30", "Everest", "Thursday", "0.4"])
        self.assertTrue(H.is_holdover("The Clayface", "2026-10-30", self.reg, self.act))
        self.assertTrue(H.is_holdover("Whalefall", "2026-10-30", self.reg, self.act))   # opened 10-16
        self.assertFalse(H.is_holdover("Whalefall", "2026-10-16", self.reg, self.act))  # its own opening
        self.assertFalse(H.is_holdover("Everest", "2026-10-30", self.reg, self.act))
        self.assertFalse(H.is_holdover("Clayface", "2026-10-23", self.reg, self.act))
        self.assertEqual(H.without_holdovers(["Everest", "Wildwood"], "2026-10-30", path=self.reg,
                                             actuals_path=self.act), ["Everest"])


class TrackedTitlesTest(unittest.TestCase):
    def test_scraper_appends_holdovers_after_gate(self):
        import scraper
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(scraper, "LINKS_JSON", scraper.Path(os.path.join(td, "x.json"))), \
                mock.patch.object(scraper, "THEATRE_COUNTS_JSON", scraper.Path(os.path.join(td, "y.json"))), \
                mock.patch.object(scraper, "calendar_titles_for_weekend", return_value=["Everest"]), \
                mock.patch.object(scraper.holdover, "collection_titles", return_value=["Wildwood"]) as ct:
            self.assertEqual(scraper.tracked_movie_titles_from_state("2026-10-30"), ["Everest", "Wildwood"])
            ct.assert_called_with("2026-10-30", ["Everest"])


class DedupGuardTest(unittest.TestCase):
    def test_guard_demands_holdover_links(self):
        import collect_links_dedup_guard as G
        with tempfile.TemporaryDirectory() as td:
            root = os.path.join(td, "repo")
            os.makedirs(os.path.join(root, "box-office-tracker", "data"))
            H.register(H.entries_from_events(EVENTS, NOW), os.path.join(root, G.HOLDOVER_TITLES_PATH))
            with mock.patch.dict(os.environ, {"HOLDOVER_COLLECTION": "1"}), \
                    mock.patch.object(H, "refresh", return_value=[]), \
                    mock.patch.object(G, "_calendar_titles_to_demand", return_value=["Everest"]), \
                    mock.patch.object(G, "_csv_market_titles", return_value=[]):
                active = G._active_movie_titles(G.Path(root), "2026-10-30", "2026-10-27")
            self.assertEqual(active, ["Everest", "Clayface", "Wildwood", "You Can See Everything"])


class CensusCoverageTest(unittest.TestCase):
    def test_holdover_days_before_registration_are_skipped(self):
        import census_coverage as CC
        with tempfile.TemporaryDirectory() as td:
            reg = os.path.join(td, "holdover-titles.csv")
            H.register(H.entries_from_events(EVENTS, NOW), reg)          # first_seen 2026-10-31
            with open(os.path.join(td, "daily-actual-overrides.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["weekend_of", "movie_title", "day_of_week", "gross_m"])
                for day in ("Thursday", "Friday", "Saturday"):
                    w.writerow(["2026-10-30", "Clayface", day, "3.0"])
                    w.writerow(["2026-10-30", "Everest", day, "0.5"])
            with mock.patch.object(CC, "DATA", td):
                rep = CC.reported("2026-10-30", registry=reg)
        self.assertEqual(sorted(d for (m, d) in rep if m == "Clayface"), ["Saturday"])
        self.assertEqual(sorted(d for (m, d) in rep if m == "Everest"), ["Friday", "Saturday", "Thursday"])


class ForecastTest(unittest.TestCase):
    O = {"Thursday": 1.32, "Friday": 3.03, "Saturday": 4.2, "Sunday": 3.71}

    def test_prior_uses_whole_base_weekend(self):
        mid, low, high, stage, _ = F.forecast(self.O, {}, SHAPE)
        self.assertEqual(stage, "prior")
        self.assertAlmostEqual(mid, (1.32 + 3.03 + 4.2 + 3.71) * 0.5)
        self.assertAlmostEqual(low, mid * 0.7)

    def test_friday_known_shapes_the_weekend(self):
        mid, low, high, stage, day = F.forecast(self.O, {"Friday": 2.4}, SHAPE)
        r = 2.4 / 3.03
        self.assertEqual(stage, "fri_known")
        self.assertAlmostEqual(day["Saturday"], 4.2 * r * 1.2)
        self.assertAlmostEqual(day["Sunday"], 3.71 * r * 1.1)
        self.assertAlmostEqual(mid, 2.4 + day["Saturday"] + day["Sunday"])
        self.assertAlmostEqual(high, mid * 1.15)

    def test_saturday_anchors_sunday_and_band_follows_reported_days(self):
        mid, low, high, stage, day = F.forecast(self.O, {"Friday": 2.4, "Saturday": 3.6}, SHAPE,
                                                band_days={"Friday": 2.4})
        self.assertEqual(stage, "fri_sat_known")
        self.assertAlmostEqual(day["Sunday"], 3.71 * (3.6 / 4.2) * 0.95)
        self.assertAlmostEqual(low, mid * 0.9)          # Saturday from census: fri_known band
        _, low2, high2, stage2, _ = F.forecast(self.O, {"Friday": 1, "Saturday": 1, "Sunday": 1}, SHAPE)
        self.assertEqual((stage2, low2, high2), ("all_known", 3, 3))

    def test_missing_base_day_gives_no_forecast(self):
        self.assertIsNone(F.forecast({"Friday": 1, "Saturday": 1}, {"Friday": 1}, SHAPE))

    def test_table_days_split_previews_only_on_openings(self):
        daily = {date(2026, 10, 22): ("P", 1.32), date(2026, 10, 23): ("3", 4.35),
                 date(2026, 10, 24): ("3", 4.2), date(2026, 10, 25): ("3", 3.71),
                 date(2026, 10, 29): ("3", 1.4), date(2026, 10, 30): ("3", 2.39)}
        self.assertEqual(F.table_days(daily, "2026-10-23", opening=True),
                         {"Thursday": 1.32, "Friday": 3.03, "Saturday": 4.2, "Sunday": 3.71})
        self.assertEqual(F.table_days(daily, "2026-10-30"), {"Friday": 2.39})

    def test_census_ratio_needs_matched_theatres(self):
        base = {"Saturday": {("CNMK", f"t{i}"): 100.0 for i in range(150)}}
        cur = {"Saturday": {("CNMK", f"t{i}"): 40.0 for i in range(120)} | {("AMC", "new"): 999.0}}
        ratio, chains, n = F.census_ratios(base, cur)["Saturday"]
        self.assertAlmostEqual(ratio, 0.4)
        self.assertEqual((chains, n), (["CNMK"], 120))
        few = {"Saturday": {("CNMK", f"t{i}"): 40.0 for i in range(F.MIN_CENSUS_THEATRES - 1)}}
        self.assertEqual(F.census_ratios(base, few), {})

    def test_log_skips_unchanged_rows(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "log.csv")
            row = {"logged_at": "t1", "weekend_of": "2026-10-30", "movie": "Wildwood", "headline_mid_m": 9.8,
                   "forecast_stage": "fri_known", "days_actual": "Friday", "days_census": ""}
            self.assertEqual(F.append_log([row], path), 1)
            self.assertEqual(F.append_log([dict(row, logged_at="t2")], path), 0)
            self.assertEqual(F.append_log([dict(row, logged_at="t3", headline_mid_m=9.1)], path), 1)


class BacktestShapeTest(unittest.TestCase):
    def test_film_weekends_and_estimates(self):
        daily = {date(2026, 10, 22): ("P", 1.0), date(2026, 10, 23): ("1", 5.0),
                 date(2026, 10, 24): ("1", 4.0), date(2026, 10, 25): ("1", 3.0),
                 date(2026, 10, 30): ("1", 2.0), date(2026, 10, 31): ("1", 3.0),
                 date(2026, 11, 1): ("1", 2.0)}
        w = B.film_weekends(daily, opening_m=13.0)
        self.assertEqual(w[1], {"Friday": 4.0, "Saturday": 4.0, "Sunday": 3.0, "previews": 1.0})
        self.assertNotIn(3, w)
        self.assertIsNone(B.film_weekends(daily, opening_m=30.0))          # disagrees with comps
        est = B.estimates(w[1], w[2], dict(SHAPE))
        self.assertAlmostEqual(est["prior"], 12.0 * 0.5)
        self.assertAlmostEqual(est["fri_known"], 2.0 + 4.0 * 0.5 * 1.2 + 3.0 * 0.5 * 1.1)
        self.assertAlmostEqual(est["fri_sat_known"], 5.0 + 3.0 * 0.75 * 0.95)


if __name__ == "__main__":
    unittest.main()


class CensusBaseTest(unittest.TestCase):
    """2026-11-01: You Can See Everything (wk 3, 855 -> 3,243 theatres) was
    census-read against its OPENING weekend: $7.0M vs a $10-12M market."""

    def _actuals(self, td):
        path = os.path.join(td, "actuals.csv")
        with open(path, "w") as f:
            f.write("weekend_of,movie_title,day,gross_m\n")
        return path

    def test_census_is_read_against_the_base_weekend(self):
        from unittest.mock import patch
        daily = {date(2026, 10, 15): ("P", 1.75), date(2026, 10, 16): ("1", 5.54),
                 date(2026, 10, 17): ("1", 5.21), date(2026, 10, 18): ("1", 4.85),
                 date(2026, 10, 23): ("1", 5.5), date(2026, 10, 24): ("1", 7.0),
                 date(2026, 10, 25): ("1", 6.2), date(2026, 10, 30): ("2", 3.57)}
        calls = []

        def census(weekend_of, movie):
            calls.append(weekend_of)
            per = {"2026-10-23": 100.0, "2026-10-30": 60.0}.get(weekend_of, 300.0)
            return {"Saturday": {("CNMK", f"t{i}"): per for i in range(150)}}

        entry = {"weekend_of": "2026-10-30", "movie": "Film", "weekend_num": "3",
                 "opening_weekend_of": "2026-10-16"}
        with tempfile.TemporaryDirectory() as td, \
                patch.object(F, "fetch_daily", return_value=daily), \
                patch.object(F, "census_by_theatre", census), \
                patch.object(F, "theatre_counts", return_value=None):
            row = F.film_forecast(entry, {"1-3": SHAPE, "2-3": SHAPE}, actuals_path=self._actuals(td))
        self.assertEqual((row["base"], row["days_census"]), ("wk2", "Saturday"))
        self.assertIn("Sat=4.200", row["day_m"])          # weekend-2 Saturday 7.0 x 0.6
        self.assertEqual(sorted(set(calls)), ["2026-10-23", "2026-10-30"])

    def test_expansion_voids_the_census(self):
        from unittest.mock import patch
        daily = {date(2026, 10, 22): ("P", 1.0), date(2026, 10, 23): ("1", 5.0),
                 date(2026, 10, 24): ("1", 6.0), date(2026, 10, 25): ("1", 4.0),
                 date(2026, 10, 30): ("2", 3.0)}
        entry = {"weekend_of": "2026-10-30", "movie": "Film", "weekend_num": "2",
                 "opening_weekend_of": "2026-10-23"}
        with tempfile.TemporaryDirectory() as td, \
                patch.object(F, "fetch_daily", return_value=daily), \
                patch.object(F, "census_by_theatre", side_effect=AssertionError("must not read")), \
                patch.object(F, "theatre_counts", return_value=(855.0, 3243.0)):
            row = F.film_forecast(entry, {"1-2": SHAPE}, actuals_path=self._actuals(td))
        self.assertEqual((row["base"], row["days_census"], row["forecast_stage"]), ("opening", "", "fri_known"))

    def test_theatre_counts_reads_metadata_and_counts_file(self):
        import json
        with tempfile.TemporaryDirectory() as td:
            meta = os.path.join(td, "meta.csv")
            with open(meta, "w") as f:
                f.write("movie,weekend_of,national_theatre_count\nThe Film,2026-10-16,855\nThe Film,2026-10-23,\n")
            counts = os.path.join(td, "counts.json")
            with open(counts, "w") as f:
                json.dump({"Film": 3243, "_updated": "x"}, f)
            self.assertEqual(F.theatre_counts("film", "2026-10-16", meta, counts), (855.0, 3243.0))
            self.assertIsNone(F.theatre_counts("film", "2026-10-23", meta, counts))
            self.assertIsNone(F.theatre_counts("other", "2026-10-16", meta, counts))
