"""The recorded opening is the 3-day figure markets settle on (2026-11-27).

Ramayana (2026-11-06) and The Amazing Digital Circus (2026-06-05) opened on a
Thursday and were recorded with that full Thursday summed in ($12.45M vs the
$8.94M weekend; $20.27M vs $12.39M). Primetime (2026-09-25) kept a Sunday
estimate that was never re-read ($19.2M vs $18.83M).
"""
import csv
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import actuals_quality as AQ  # noqa: E402
import calibrate as C  # noqa: E402
import forecast_windows as FW  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


RAMAYANA = {"Thursday": 3.505682, "Friday": 2.417783, "Saturday": 3.825743, "Sunday": 2.695979}


class StandardOpeningTotalTest(unittest.TestCase):
    def test_previews_are_part_of_the_opening(self):
        daily = {"Thursday": 2.7, "Friday": 5.79, "Saturday": 6.12, "Sunday": 4.22}
        self.assertAlmostEqual(18.83, AQ.standard_opening_total(daily), places=2)

    def test_a_regular_thursday_is_not(self):
        self.assertAlmostEqual(8.94, AQ.standard_opening_total(RAMAYANA, True), places=2)

    def test_model_window_actual_prefers_the_thu_sun_total(self):
        self.assertEqual(12.45, AQ.model_window_actual({"actual_total": 8.94, "actual_thu_sun_total": 12.45}))
        self.assertEqual(8.94, AQ.model_window_actual({"actual_total": 8.94}))
        self.assertEqual(7.0, AQ.model_window_actual({"actual": 7.0}))
        self.assertIsNone(AQ.model_window_actual({}))


class ReviseTest(unittest.TestCase):
    def _entry(self):
        return {"movie": "Ramayana: Rise of A Legend", "weekend_of": "2026-11-06", "date": "2026-11-11",
                "predicted_mid": 15.43, "actual_total": 12.45, "error_pct": 23.9,
                "daily_actuals": {"Thursday": 3.51, "Friday": 2.42, "Saturday": 3.83, "Sunday": 2.7},
                "live_headline": {"mid_m": 12.35, "checkpoints": {
                    "sunday_noon_et": {"mid_m": 12.03, "low_m": 9.7, "high_m": 13.83}}},
                "live_error_pct": -0.8}

    def test_thursday_opener_records_the_three_day_opening(self):
        entry = self._entry()
        daily = AQ.ReportedDailyGrosses(RAMAYANA, source_url="u", non_preview_thursday=True)
        self.assertTrue(AQ.revise_reported_daily_actuals(entry, daily, "u", "2026-11-27"))
        self.assertAlmostEqual(8.939505, entry["actual_total"], places=5)
        self.assertAlmostEqual(12.445187, entry["actual_thu_sun_total"], places=5)
        self.assertTrue(entry["non_preview_thursday"] and entry["exclude_from_calibration"])
        # The Thu-Sun prediction is graded on the Thu-Sun actual, not the 3-day.
        self.assertAlmostEqual(100 * (15.43 / 12.445187 - 1), entry["error_pct"], places=1)
        self.assertAlmostEqual(100 * (12.35 / 12.445187 - 1), entry["live_error_pct"], places=1)
        self.assertEqual(12.45, entry["actuals_revision"]["previous"]["actual_total"])
        self.assertFalse(AQ.revise_reported_daily_actuals(entry, daily, "u", "2026-11-28"))

    def test_revision_regrades_the_live_headline_and_checkpoints(self):
        entry = {"movie": "Primetime", "weekend_of": "2026-09-25", "predicted_mid": 21.92,
                 "actual_total": 19.2, "error_pct": 14.2, "live_error_pct": 5.7,
                 "daily_actuals": {"Thursday": 2.7, "Friday": 5.79, "Saturday": 6.12, "Sunday": 4.59},
                 "live_headline": {"mid_m": 20.3, "checkpoints": {
                     "friday_noon_et": {"mid_m": 19.06, "low_m": 10.55, "high_m": 43.1, "error_pct": -0.72}}}}
        daily = AQ.ReportedDailyGrosses(
            {"Thursday": 2.7, "Friday": 5.794586, "Saturday": 6.116102, "Sunday": 4.22011}, source_url="u")
        AQ.revise_reported_daily_actuals(entry, daily, "u", "2026-11-27")
        self.assertAlmostEqual(18.830798, entry["actual_total"], places=5)
        self.assertNotIn("actual_thu_sun_total", entry)
        self.assertEqual(7.8, entry["live_error_pct"])
        self.assertEqual(1.22, entry["live_headline"]["checkpoints"]["friday_noon_et"]["error_pct"])


class RecordResultTest(unittest.TestCase):
    def _record(self, daily):
        cal = json.loads(json.dumps(C.DEFAULT_CALIBRATION))
        with mock.patch.object(C, "save_calibration"), \
                mock.patch.object(C.seat_regression, "fit_regression_calibration", return_value={}), \
                mock.patch.object(C.seat_regression, "learn_day_shares", return_value={}):
            return C.record_result(cal, "Film", "2026-11-06", 15.43, 13.0, 17.0, daily,
                                   {"Thursday": 1.35, "Friday": 3.85, "Saturday": 6.19, "Sunday": 4.48},
                                   n_theatres=300, n_days=4,
                                   live_headline={"mid_m": 12.35, "checkpoints": {}}), cal

    def test_thursday_opener(self):
        entry, cal = self._record(AQ.ReportedDailyGrosses(RAMAYANA, non_preview_thursday=True))
        self.assertEqual(8.94, entry["actual_total"])
        self.assertEqual(12.45, entry["actual_thu_sun_total"])
        self.assertEqual(24.0, entry["error_pct"])          # 15.43 vs the Thu-Sun 12.45
        self.assertEqual(-0.8, entry["live_error_pct"])
        # Rebuilt from the stored (rounded) Thu-Sun total: 15.43 / 12.45.
        self.assertEqual(23.9, C.accuracy_entry_from_history(entry)["abs_error_pct"])
        self.assertEqual(24.0, cal["calibration_factors"]["historical_accuracy"][-1]["abs_error_pct"])

    def test_preview_thursday_is_unchanged(self):
        entry, _ = self._record(AQ.ReportedDailyGrosses(
            {"Thursday": 2.7, "Friday": 5.79, "Saturday": 6.12, "Sunday": 4.22}))
        self.assertEqual(18.83, entry["actual_total"])
        self.assertNotIn("actual_thu_sun_total", entry)


class ReverifyTest(unittest.TestCase):
    def _primetime(self):
        return {"movie": "Primetime", "weekend_of": "2026-09-25", "date": "2026-09-29",
                "predicted_mid": 21.92, "actual_total": 19.2, "actual_status": "final",
                "daily_actuals": {"Thursday": 2.7, "Friday": 5.79, "Saturday": 6.12, "Sunday": 4.59}}

    FINAL = {"Thursday": 2.7, "Friday": 5.794586, "Saturday": 6.116102, "Sunday": 4.22011}

    def test_rounding_is_not_a_revision(self):
        entry = dict(self._primetime(), actual_total=18.83,
                     daily_actuals={"Thursday": 2.7, "Friday": 5.79, "Saturday": 6.12, "Sunday": 4.22})
        self.assertFalse(C.reported_actuals_differ(entry, AQ.ReportedDailyGrosses(self.FINAL)))

    def test_a_moved_sunday_is(self):
        self.assertTrue(C.reported_actuals_differ(self._primetime(), AQ.ReportedDailyGrosses(self.FINAL)))

    def test_a_newly_ranked_thursday_is(self):
        entry = dict(self._primetime(), actual_total=18.83,
                     daily_actuals={"Thursday": 2.7, "Friday": 5.79, "Saturday": 6.12, "Sunday": 4.22})
        self.assertTrue(C.reported_actuals_differ(
            entry, AQ.ReportedDailyGrosses(self.FINAL, non_preview_thursday=True)))

    def test_recent_weekends_are_reread_and_revised(self):
        old = dict(self._primetime(), movie="Old", weekend_of="2026-06-05")
        current = dict(self._primetime(), movie="Now", weekend_of="2026-10-16")
        cal = {"history": [old, self._primetime(), current], "calibration_factors": {}}
        seen = []

        def fetch(movie, weekend):
            seen.append(movie)
            return AQ.ReportedDailyGrosses(self.FINAL, source_url="u")

        with mock.patch.object(C, "refresh_fitted_factors") as refit:
            revised = C.reverify_recent_actuals(cal, today="2026-10-21", fetch=fetch,
                                                skip_weekends=("2026-10-16",))
        self.assertEqual(["Primetime"], seen)        # 6-week window, current weekend skipped
        self.assertEqual([("Primetime", "2026-09-25", 19.2, 18.830798)], revised)
        refit.assert_called_once()
        self.assertEqual("2026-10-21", cal["history"][1]["actuals_revision"]["as_of_date"])
        # A replay dated before the revision still sees the record as it stood.
        self.assertEqual(19.2, AQ.actuals_as_of(cal["history"][1], "2026-10-16")["actual_total"])

    def test_unchanged_film_is_stamped_not_revised(self):
        entry = dict(self._primetime(), actual_total=18.83,
                     daily_actuals={"Thursday": 2.7, "Friday": 5.79, "Saturday": 6.12, "Sunday": 4.22})
        cal = {"history": [entry], "calibration_factors": {}}
        fetch = lambda m, w: AQ.ReportedDailyGrosses(self.FINAL, source_url="u")  # noqa: E731
        self.assertEqual([], C.reverify_recent_actuals(cal, today="2026-10-21", fetch=fetch))
        self.assertEqual("2026-10-21", entry["actuals_verified_at"])
        self.assertNotIn("actuals_revision", entry)

    def test_a_fetch_failure_changes_nothing(self):
        cal = {"history": [self._primetime()], "calibration_factors": {}}

        def boom(movie, weekend):
            raise RuntimeError("the-numbers down")

        self.assertEqual([], C.reverify_recent_actuals(cal, today="2026-10-21", fetch=boom))
        self.assertEqual(19.2, cal["history"][0]["actual_total"])


class ChartTitleMatchTest(unittest.TestCase):
    def _urls(self, html_text, title):
        response = mock.Mock(status_code=200, text=html_text)
        with mock.patch.object(C, "requests", mock.Mock(get=mock.Mock(return_value=response))):
            return C.numbers_chart_movie_urls(title, "2026-05-22")

    def test_unique_franchise_prefix_is_accepted(self):
        page = ('<a href="/movie/Star-Wars-The-Mandalorian-and-Grogu-(2026)#tab=box-office">'
                'Star Wars: The Mandalorian and Grogu</a><a href="/movie/Passenger-(2026)">Passenger</a>')
        self.assertEqual(["https://www.the-numbers.com/movie/Star-Wars-The-Mandalorian-and-Grogu-(2026)"],
                         self._urls(page, "The Mandalorian and Grogu"))

    def test_exact_match_wins_and_one_word_titles_never_prefix_match(self):
        page = ('<a href="/movie/Hope-(2026-South-Korea)">Hope</a>'
                '<a href="/movie/Last-Hope-(2026)">Last Hope</a>')
        self.assertEqual(["https://www.the-numbers.com/movie/Hope-(2026-South-Korea)"], self._urls(page, "Hope"))
        self.assertEqual([], self._urls('<a href="/movie/Last-Hope-(2026)">Last Hope</a>', "Hope"))


class WindowProfileTest(unittest.TestCase):
    def test_early_opener_is_not_market_compatible(self):
        profile = FW.window_profile("Ramayana: Rise of A Legend", "2026-11-06", early_opening=True)
        self.assertFalse(profile["market_window_compatible"])
        self.assertIn("Friday-Sunday", profile["market_gross_window"])
        self.assertTrue(FW.window_profile("Film", "2026-09-18")["market_window_compatible"])

    def test_detected_from_a_marked_thursday_override(self):
        note = f"auto-fetched; {AQ.REGULAR_THURSDAY_NOTE}: film opened before Friday"
        overrides = {"Ghost Soldier": {"Thursday": {"gross_m": 0.8, "notes": note}},
                     "Wildwood": {"Thursday": {"gross_m": 1.3, "notes": "auto-fetched daily gross"}}}
        self.assertTrue(FW.opened_before_friday("Ghost Soldier", "2026-11-13", overrides, calendar_path="/nonexistent"))
        self.assertFalse(FW.opened_before_friday("Wildwood", "2026-11-13", overrides, calendar_path="/nonexistent"))
        self.assertFalse(FW.opened_before_friday("Wildwood", "2026-11-13", None, calendar_path="/nonexistent"))

    def test_detected_from_the_release_calendar(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "release-calendar.json")
            with open(path, "w") as f:
                json.dump({"weekend_of": "2026-11-27", "titles": [
                    {"title": "Hershey", "date": "November 25, 2026"},
                    {"title": "The Focker In-Law", "date": "November 27, 2026"}]}, f)
            self.assertTrue(FW.opened_before_friday("Hershey", "2026-11-27", calendar_path=path))
            self.assertFalse(FW.opened_before_friday("Focker In-Law", "2026-11-27", calendar_path=path))
            # The file describes another weekend: no evidence either way.
            self.assertFalse(FW.opened_before_friday("Hershey", "2026-12-04", calendar_path=path))


class RegularThursdayFetchTest(unittest.TestCase):
    def setUp(self):
        self.fetch = _load("fetch_daily_actuals")
        self.numbers = _load("import_thenumbers_daily")

    def test_ranked_thursday_of_an_opener_is_regular(self):
        opener = {date(2026, 11, 5): ("1", 3.51), date(2026, 11, 6): ("6", 2.42)}
        previews = {date(2026, 11, 5): ("P", 1.3), date(2026, 11, 6): ("3", 4.36)}
        holdover = {date(2026, 10, 23): ("3", 4.36), date(2026, 11, 5): ("5", 0.6), date(2026, 11, 6): ("6", 1.2)}
        self.assertTrue(self.numbers.thursday_is_regular(opener, "2026-11-06"))
        self.assertFalse(self.numbers.thursday_is_regular(previews, "2026-11-06"))
        self.assertFalse(self.numbers.thursday_is_regular(holdover, "2026-11-06"))
        self.assertFalse(self.numbers.thursday_is_regular({}, "2026-11-06"))

    def test_split_days_carry_the_flag(self):
        table = {date(2026, 11, 5): ("1", 3.51), date(2026, 11, 6): ("6", 2.42), date(2026, 11, 7): ("3", 3.83)}
        days = self.fetch.fetch_split_opening_days("Ramayana", "2026-11-06", fetch_table=lambda t, y: table)
        self.assertTrue(days.non_preview_thursday)
        self.assertEqual({"Thursday": 3.51, "Friday": 2.42, "Saturday": 3.83}, dict(days))

    def test_regular_thursday_row_is_marked_and_an_unmarked_one_rewritten(self):
        existing = [{"weekend_of": "2026-11-27", "movie_title": "Hershey", "day_of_week": "Thursday",
                     "gross_m": "2.95", "notes": "auto-fetched daily gross (revisions re-append)"}]
        gross = AQ.ReportedDailyGrosses({"Thursday": 2.95}, non_preview_thursday=True)
        rows = self.fetch.merge_override_rows(existing, "2026-11-27", "Hershey", gross, "2026-11-28")
        self.assertEqual(1, len(rows))
        self.assertIn(AQ.REGULAR_THURSDAY_NOTE, rows[0]["notes"])
        self.assertEqual([], self.fetch.merge_override_rows(existing + rows, "2026-11-27", "Hershey",
                                                            gross, "2026-11-29"))

    def test_preview_rows_keep_the_plain_note(self):
        rows = self.fetch.merge_override_rows([], "2026-10-23", "Wildwood", {"Thursday": 1.33}, "2026-10-24")
        self.assertNotIn(AQ.REGULAR_THURSDAY_NOTE, rows[0]["notes"])


class PaperTradeWindowTest(unittest.TestCase):
    def setUp(self):
        self.T = _load("paper_trade")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _path(self, name):
        return os.path.join(self.tmp.name, name)

    def test_provisional_total_leaves_out_a_regular_thursday(self):
        path = self._path("overrides.csv")
        note = f"auto; {AQ.REGULAR_THURSDAY_NOTE}: film opened before Friday"
        rows = [("2026-11-06", "Ramayana", "Thursday", 3.51, note), ("2026-11-06", "Ramayana", "Friday", 2.42, ""),
                ("2026-11-06", "Ramayana", "Saturday", 3.83, ""), ("2026-11-06", "Ramayana", "Sunday", 2.70, ""),
                ("2026-10-23", "Wildwood", "Thursday", 1.33, "auto"), ("2026-10-23", "Wildwood", "Friday", 3.03, ""),
                ("2026-10-23", "Wildwood", "Saturday", 4.22, ""), ("2026-10-23", "Wildwood", "Sunday", 3.72, "")]
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["weekend_of", "movie_title", "day_of_week", "gross_m", "source", "status", "as_of_date", "notes"])
            for weekend, movie, day, gross, notes in rows:
                w.writerow([weekend, movie, day, gross, "The Numbers auto-fetch", "reported", "2026-11-09", notes])
        totals = self.T.provisional_actuals(path)
        self.assertAlmostEqual(8.95, totals[("2026-11-06", "ramayana")], places=2)
        self.assertAlmostEqual(12.30, totals[("2026-10-23", "wildwood")], places=2)

    def _off_window_inputs(self):
        pred, cal = self._path("pred.csv"), self._path("cal.json")
        with open(pred, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["weekend_of", "movie", "market_window_compatible"])
            w.writerows([["2026-11-27", "Hershey", "0"], ["2026-10-23", "Wildwood", "1"]])
        with open(cal, "w") as f:
            json.dump({"history": [
                {"movie": "Ramayana: Rise of A Legend", "weekend_of": "2026-11-06", "non_preview_thursday": True},
                {"movie": "Wildwood", "weekend_of": "2026-10-23"}]}, f)
        return pred, cal

    def test_off_window_films(self):
        pred, cal = self._off_window_inputs()
        self.assertEqual({("2026-11-27", "hershey"), ("2026-11-06", "ramayanariseofalegend")},
                         self.T.off_window_films(pred, cal))

    def test_off_window_bets_are_void_and_stay_void(self):
        trades = {
            "a": {"weekend_of": "2026-11-06", "movie": "Ramayana: Rise of A Legend", "status": "settled",
                  "pnl": "21.7273", "actual_m": "12.45", "outcome_bracket": "9m+", "event_slug": "e",
                  "bracket": "9m+", "side": "YES", "cost": "0.044", "forecast_stage": "complete"},
            "b": {"weekend_of": "2026-10-23", "movie": "Wildwood", "status": "settled", "pnl": "0.5000",
                  "actual_m": "12.27", "outcome_bracket": "12m-13m", "event_slug": "e",
                  "bracket": "12m-13m", "side": "YES", "cost": "0.5", "forecast_stage": "complete"}}
        off = {("2026-11-06", "ramayanariseofalegend")}
        self.assertEqual(1, self.T.void_off_window(trades, off, now="2026-11-27T00:00:00Z"))
        self.assertEqual(("void", "0.0000"), (trades["a"]["status"], trades["a"]["pnl"]))
        self.assertEqual("settled", trades["b"]["status"])
        self.assertEqual(0, self.T.void_off_window(trades, off))
        self.T.settle(trades, snaps={}, finals={("2026-11-06", "ramayanariseofalegend"): 8.94}, provisionals={})
        self.assertEqual("void", trades["a"]["status"])
        self.assertIn("void", self.T.report(trades))


if __name__ == "__main__":
    unittest.main()
