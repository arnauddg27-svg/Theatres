"""Films that open before Friday (2026-11-27 Thanksgiving audit)."""
import csv
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import midweek_opening as M  # noqa: E402
import forecast_windows as FW  # noqa: E402
import stage_forecasting as S  # noqa: E402
import predict as P  # noqa: E402
import ensemble_forecast as E  # noqa: E402
import paper_trade as T  # noqa: E402

spec = importlib.util.spec_from_file_location("fetch_daily_actuals_midweek", ROOT / "scripts" / "fetch_daily_actuals.py")
FDA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FDA)

W = "2026-11-27"
RULES_5DAY = ('weekend_of=2026-11-27; settlement_rules=This market will resolve according to how much "Hexed" '
              "will gross domestically on its 5-day Thanksgiving opening weekend (Wednesday, November 25 - "
              "Sunday, November 29).")
# (weekend, [Wed incl. previews, Thu, Fri, Sat, Sun]) -- the-numbers.com, $M
THANKSGIVING = {
    "Encanto": ("2021-11-26", [7.5532, 5.8076, 11.0751, 9.781, 6.3504]),
    "House of Gucci": ("2021-11-26", [4.2045, 3.386, 5.7327, 5.2938, 3.3973]),
    "Strange World": ("2022-11-25", [4.1926, 2.5112, 4.9688, 4.3974, 2.7852]),
    "Wish": ("2023-11-24", [8.1174, 3.7937, 8.0956, 7.1319, 4.4708]),
    "Moana 2": ("2024-11-29", [57.8698, 27.7846, 54.3618, 50.6041, 34.8215]),
    "Zootopia 2": ("2025-11-28", [38.4977, 20.0438, 39.0603, 36.2243, 24.9779]),
}


def days_from(weekend, gross, opening_offset=2):
    friday = M._date(weekend)
    return {friday.fromordinal(friday.toordinal() - opening_offset + i): (M.REGULAR, g) for i, g in enumerate(gross)}


def history():
    return {(w, M.movie_key(t)): {"movie": t, "days": days_from(w, g)} for t, (w, g) in THANKSGIVING.items()}


class OpeningRunTest(unittest.TestCase):
    def test_holiday_frames(self):
        self.assertEqual("thanksgiving", M.holiday_frame("2026-11-27", "2026-11-25"))
        self.assertEqual("july4", M.holiday_frame("2026-07-03", "2026-07-01"))
        self.assertEqual("christmas", M.holiday_frame("2025-12-26", "2025-12-25"))
        self.assertEqual("none", M.holiday_frame("2023-04-07", "2023-04-05"))

    def test_wednesday_opener_with_tuesday_previews(self):
        days = {date(2026, 11, 24): (M.PREVIEW, 2.1), date(2026, 11, 25): (M.REGULAR, 7.6),
                date(2026, 11, 26): (M.REGULAR, 4.4)}
        run = M.opening_run(days, W)
        self.assertEqual(("2026-11-25", 2, "thanksgiving", 2), (run["opening_date"], run["offset"], run["frame"], run["position"]))
        self.assertAlmostEqual(12.0, run["to_date_m"])
        self.assertEqual(["2026-11-27", "2026-11-28", "2026-11-29"], run["remaining_dates"])
        self.assertTrue(run["last_is_single_day"])
        self.assertEqual("midweek-after-thursday", M.stage_name(run))

    def test_friday_opener_with_thursday_previews_is_not_midweek(self):
        days = {date(2026, 11, 19): (M.PREVIEW, 21.0), date(2026, 11, 20): (M.REGULAR, 55.6)}
        self.assertIsNone(M.opening_run(days, "2026-11-20"))

    def test_first_row_after_the_known_opening_is_a_gross_to_date(self):
        # Hershey: the market names Wednesday, the table starts on Thursday.
        run = M.opening_run({date(2026, 11, 26): (M.REGULAR, 2.9452)}, W, known_opening="2026-11-25")
        self.assertEqual(("2026-11-25", 2), (run["opening_date"], run["position"]))
        self.assertFalse(run["last_is_single_day"])
        later = M.opening_run({date(2026, 11, 26): (M.REGULAR, 2.9452), date(2026, 11, 27): (M.REGULAR, 2.0)},
                              W, known_opening="2026-11-25")
        self.assertTrue(later["last_is_single_day"])

    def test_platform_days_before_the_wide_opening_are_dropped(self):
        days = {date(2025, 12, 22): (M.REGULAR, 0.142), date(2025, 12, 23): (M.REGULAR, 0.129),
                date(2025, 12, 24): (M.REGULAR, 2.0129), date(2025, 12, 25): (M.REGULAR, 9.5357),
                date(2025, 12, 26): (M.REGULAR, 6.7343)}
        run = M.opening_run(days, "2025-12-26")
        self.assertEqual(("2025-12-25", 1), (run["opening_date"], run["offset"]))


class ProjectionTest(unittest.TestCase):
    def setUp(self):
        self.comps = M.complete_runs(history(), before_weekend=W)

    def test_complete_runs_exclude_the_film_and_later_weekends(self):
        self.assertEqual(6, len(self.comps))
        self.assertEqual(5, len(M.complete_runs(history(), before_weekend=W, exclude=("2021-11-26", "Encanto"))))
        self.assertEqual(2, len(M.complete_runs(history(), before_weekend="2022-11-25")))

    def test_two_reported_days_blend_last_day_and_to_date(self):
        run = M.opening_run(days_from(W, [7.6, 4.4]), W)
        out = M.project(run, self.comps)
        self.assertEqual((6, "thanksgiving", "last day x to date"), (out["n_comps"], out["pool"], out["estimator"]))
        self.assertAlmostEqual((out["by_last_m"] * out["by_cum_m"]) ** 0.5, out["remaining_m"])
        self.assertTrue(18.0 < out["remaining_m"] < 23.0)          # Fri-Sun of a $12M Wed+Thu
        self.assertTrue(out["low_m"] < out["remaining_m"] < out["high_m"])
        self.assertAlmostEqual(out["remaining_m"], sum(out["per_day_m"].values()))
        self.assertLess(out["loo_mae"], 0.05)

    def test_readings_that_disagree_widen_the_band(self):
        # Thursday above Wednesday (no comp did that): reach halfway to each reading.
        out = M.project(M.opening_run(days_from(W, [5.3, 7.7]), W), self.comps)
        self.assertGreater(out["by_last_m"], 1.5 * out["by_cum_m"])
        self.assertLessEqual(out["low_m"], (out["remaining_m"] + out["by_cum_m"]) / 2 + 1e-9)
        self.assertGreaterEqual(out["high_m"], (out["remaining_m"] + out["by_last_m"]) / 2 - 1e-9)

    def test_gross_to_date_row_uses_the_running_total_only(self):
        run = M.opening_run({date(2026, 11, 26): (M.REGULAR, 2.9452)}, W, known_opening="2026-11-25")
        out = M.project(run, self.comps)
        self.assertIsNone(out["r_last"])
        self.assertAlmostEqual(out["r_cum"] * 2.9452, out["remaining_m"])

    def test_other_frames_are_pooled_when_the_frame_is_thin_and_none_without_comps(self):
        run = M.opening_run(days_from("2027-03-12", [3.0, 2.0]), "2027-03-12")       # no holiday
        out = M.project(run, self.comps)
        self.assertEqual("all frames", out["pool"])
        self.assertLessEqual(out["low_m"], out["remaining_m"] * (1 - M.POOLED_HALF_BAND) + 1e-9)
        self.assertIsNone(M.project(run, self.comps[:2]))
        thursday_opener = M.opening_run(days_from("2027-03-12", [3.0], opening_offset=1), "2027-03-12")
        self.assertIsNone(M.project(thursday_opener, self.comps))                    # no Thursday-opening comps

    def test_frame_totals(self):
        run = M.opening_run(days_from(W, [7.6, 4.4]), W)
        out = M.project(run, self.comps)
        five = M.frame_total(run, out, "2026-11-25", "2026-11-29")
        thu_sun = M.frame_total(run, out, "2026-11-26", "2026-11-29")
        three = M.frame_total(run, out, "2026-11-27", "2026-11-29")
        self.assertAlmostEqual(12.0 + out["remaining_m"], five[0])
        self.assertAlmostEqual(4.4 + out["remaining_m"], thu_sun[0])
        self.assertAlmostEqual(out["remaining_m"], three[0])
        self.assertTrue(five[1] < five[0] < five[2])
        self.assertIsNone(M.frame_total(run, out, "2026-11-27", "2026-11-30"))        # a Monday we cannot project
        self.assertEqual("Wednesday-Sunday (5 days)", M.window_label("2026-11-25", "2026-11-29"))


class StorageTest(unittest.TestCase):
    def test_load_keeps_the_last_row_and_honours_through_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "midweek.csv")
            rows = [
                {"weekend_of": "2025-11-28", "movie_title": "Zootopia 2", "show_date": "2025-11-26", "day_kind": "regular",
                 "gross_m": 38.5, "source": "x", "as_of_date": "2026-11-28"},
                {"weekend_of": W, "movie_title": "Hexed", "show_date": "2026-11-25", "day_kind": "regular",
                 "gross_m": 7.0, "source": "x", "as_of_date": "2026-11-26"},
                {"weekend_of": W, "movie_title": "Hexed", "show_date": "2026-11-25", "day_kind": "regular",
                 "gross_m": 7.6, "source": "x", "as_of_date": "2026-11-27"},
                {"weekend_of": W, "movie_title": "Hexed", "show_date": "2026-11-26", "day_kind": "regular",
                 "gross_m": 4.4, "source": "x", "as_of_date": "2026-11-27"},
            ]
            self.assertEqual(4, M.append_csv(rows, path))
            data = M.load_rows(path)
            self.assertEqual((M.REGULAR, 7.6), M.film_days(data, "hexed", W)[date(2026, 11, 25)])
            replay = M.load_rows(path, through_date="2026-11-26")
            # A finished opening is history whatever day it was recorded; the
            # live film shows only what was known by the replay date.
            self.assertIn(("2025-11-28", "zootopia2"), replay)
            self.assertEqual({date(2026, 11, 25): (M.REGULAR, 7.0)}, M.film_days(replay, "Hexed", W))

    def test_merge_rows_writes_new_and_revised_days_only(self):
        table = {date(2026, 11, 24): ("P", 2.1), date(2026, 11, 25): ("2", 7.6), date(2026, 11, 26): ("3", 4.4)}
        rows = M.week_rows(table, W)
        self.assertEqual([M.PREVIEW, M.REGULAR, M.REGULAR], [kind for _, kind, _ in rows])
        self.assertTrue(M.opens_before_friday(rows, W))
        first = M.merge_rows([], W, "Hexed", rows, "2026-11-27")
        self.assertEqual(3, len(first))
        self.assertEqual([], M.merge_rows(first, W, "Hexed", rows, "2026-11-28"))
        revised = M.week_rows({**table, date(2026, 11, 26): ("3", 4.9)}, W)
        self.assertEqual(["2026-11-26"], [r["show_date"] for r in M.merge_rows(first, W, "hexed", revised, "2026-11-28")])

    def test_repo_history_supports_a_thanksgiving_projection(self):
        comps = [c for c in M.complete_runs(M.load_rows(), before_weekend=W)
                 if c["frame"] == "thanksgiving" and c["offset"] == 2]
        self.assertGreaterEqual(len(comps), 10)


class FetcherTest(unittest.TestCase):
    def test_friday_opener_writes_no_midweek_rows(self):
        table = {date(2026, 11, 19): ("P", 21.0), date(2026, 11, 20): ("1", 55.6)}
        self.assertEqual([], FDA.midweek_rows_for("The Hunger Games", "2026-11-20", table, [], "2026-11-21"))

    def test_wednesday_opener_rows_and_upcoming_friday(self):
        table = {date(2026, 11, 25): ("3", 5.3), date(2026, 11, 26): ("2", 7.7)}
        rows = FDA.midweek_rows_for("Focker In-Law", W, table, [], "2026-11-27")
        self.assertEqual([("2026-11-25", "regular"), ("2026-11-26", "regular")],
                         [(r["show_date"], r["day_kind"]) for r in rows])
        self.assertEqual(W, FDA.upcoming_friday(datetime(2026, 11, 26, 14, tzinfo=timezone.utc)))   # Thursday
        self.assertIsNone(FDA.upcoming_friday(datetime(2026, 11, 27, 14, tzinfo=timezone.utc)))     # Friday
        self.assertIsNone(FDA.upcoming_friday(datetime(2026, 11, 29, 14, tzinfo=timezone.utc)))     # Sunday

    def test_split_days_accepts_an_already_fetched_table(self):
        table = {date(2026, 11, 26): ("2", 7.7), date(2026, 11, 27): ("2", 12.0)}
        self.assertEqual({"Thursday": 7.7, "Friday": 12.0},
                         FDA.fetch_split_opening_days("Focker In-Law", W, daily=table))


class MarketFrameTest(unittest.TestCase):
    def test_stated_dates_are_read(self):
        self.assertEqual(("2026-11-25", "2026-11-29"), FW.market_frame("Hexed", W, [{"notes": RULES_5DAY}]))
        three = [{"notes": 'on its 3-day opening weekend (November 13 - 15).  This market'}]
        self.assertEqual(("2026-11-13", "2026-11-15"), FW.market_frame("Ghost Soldier", "2026-11-13", three))
        wrap = [{"rules": "4-day opening (Thursday, December 31 - Sunday, January 3)"}]
        self.assertEqual(("2026-12-31", "2027-01-03"), FW.market_frame("X", "2027-01-01", wrap))
        self.assertIsNone(FW.market_frame("X", W, [{"notes": "opening weekend (see rules)"}]))
        self.assertIsNone(FW.market_frame("X", W, [{"notes": "resolves (March 3 - 5)"}]))   # not this weekend

    def test_window_profile_keeps_standard_weekends_compatible(self):
        three = FW.window_profile("Ghost Soldier", "2026-11-13", [{"notes": "3-day opening weekend (November 13 - 15)"}])
        self.assertTrue(three["market_window_compatible"])
        self.assertEqual("2026-11-13", three["market_frame_start"])
        five = FW.window_profile("Hexed", W, [{"notes": RULES_5DAY}])
        self.assertFalse(five["market_window_compatible"])
        self.assertEqual(("2026-11-25", "2026-11-29"), (five["market_frame_start"], five["market_frame_end"]))
        self.assertEqual("", FW.window_profile("Film", "2026-09-18")["market_frame_start"])


def opening_week(film_days):
    data = history()
    data[(W, M.movie_key("Hexed"))] = {"movie": "Hexed", "days": film_days}
    return data


def thursday_pred(thursday_m=4.4):
    return {"movie": "Hexed", "weekend_of": W, "audience_type": "broad_family",
            "seat_mid_m": 37.9, "seat_low_m": 9.4, "seat_high_m": 151.8,
            "daily_details": {"Thursday": {"domestic_mid": thursday_m * 1e6, "actual_override": True,
                                           "actual_override_m": thursday_m, "n_theatres": 24,
                                           "expected_theatres": 425, "coverage_ratio": 1.0,
                                           "effective_coverage_ratio": 1.0}}}


class PredictIntegrationTest(unittest.TestCase):
    def test_reported_wednesday_and_thursday_are_actuals_not_previews(self):
        pred = thursday_pred()
        data = opening_week(days_from(W, [7.6, 4.4]))
        info = P.attach_midweek_opening(pred, "Hexed", W, data, [{"notes": RULES_5DAY}])
        self.assertEqual("midweek-after-thursday", info["stage"])
        self.assertEqual("midweek-after-thursday", S.forecast_stage(pred))
        self.assertIsNone(P.comp_multiplier_estimate({"history": []}, pred))
        P.select_regression_prediction(pred, {"history": [], "calibration_factors": {}})
        remaining = info["projection"]["remaining_m"]
        self.assertEqual("midweek-reported-days", pred["regression_source"])
        self.assertAlmostEqual(4.4 + remaining, pred["regression_mid_m"])
        self.assertLess(pred["regression_mid_m"], 30)              # was $39.1M as "previews"
        self.assertIn("not previews", pred["regression_basis"])
        pred.update(FW.window_profile("Hexed", W, [{"notes": RULES_5DAY}]))
        P.apply_market_frame(pred)
        self.assertAlmostEqual(12.0 + remaining, pred["market_frame_mid_m"])
        self.assertEqual("Wednesday-Sunday (5 days)", pred["market_frame_window"])
        row = P.prediction_log_row(pred, logged_at=datetime(2026, 11, 28, 5, tzinfo=timezone.utc), weekend_of=W)
        self.assertEqual(("midweek-after-thursday", "Thursday-Sunday", "0", "Wednesday-Sunday (5 days)"),
                         (row["forecast_stage"], row["model_gross_window"], row["market_window_compatible"],
                          row["market_frame_window"]))
        self.assertAlmostEqual(12.0 + remaining, row["market_frame_mid_m"], places=2)

    def test_full_thursday_outside_a_three_day_market(self):
        pred = thursday_pred()
        three_day = [{"notes": "3-day opening weekend (November 27 - 29)"}]
        info = P.attach_midweek_opening(pred, "Hexed", W, opening_week(days_from(W, [7.6, 4.4])), three_day)
        P.select_regression_prediction(pred, {"history": [], "calibration_factors": {}})
        pred.update(FW.window_profile("Hexed", W, three_day))
        self.assertTrue(pred["market_window_compatible"])
        P.apply_market_frame(pred)
        self.assertFalse(pred["market_window_compatible"])
        self.assertAlmostEqual(info["projection"]["remaining_m"], pred["market_frame_mid_m"])

    def test_friday_opener_and_replays_are_untouched(self):
        pred = thursday_pred()
        previews = {date(2026, 11, 26): (M.PREVIEW, 4.4)}
        self.assertIsNone(P.attach_midweek_opening(pred, "Hexed", W, opening_week(previews)))
        self.assertIsNone(P.attach_midweek_opening(pred, "Hexed", W, {}))       # a replay hands in no reported days
        self.assertNotIn("midweek_opening", pred)
        self.assertEqual("after-previews", S.forecast_stage(pred))
        pred.update(FW.window_profile("Hexed", W, [{"notes": RULES_5DAY}]))
        self.assertIsNone(P.apply_market_frame(pred))
        self.assertEqual("", P.prediction_log_row(pred, weekend_of=W)["market_frame_mid_m"])

    def test_reported_day_does_not_hide_a_dark_seat_panel(self):
        cal = {"calibration_factors": {}}
        details = thursday_pred()["daily_details"]
        panel = P.seat_panel_coverage_ratio(details, cal)
        self.assertLess(panel, 0.05)                                # 24 of 425 theatres on one day
        starved = {"seat_weighted_coverage_ratio": 0.133, "seat_data_quality": 0.168,
                   "snapshot_model_weight": 0.01}
        self.assertFalse(P.detect_data_outage(dict(starved)))       # the 2026-11-27 rows
        self.assertTrue(P.detect_data_outage({**starved, "seat_panel_coverage_ratio": panel}))
        healthy = {"Thursday": {**details["Thursday"], "n_theatres": 400}}
        self.assertFalse(P.detect_data_outage({**starved, "seat_weighted_coverage_ratio": 0.133,
                                               "seat_panel_coverage_ratio": 0.9}))
        self.assertGreater(P.seat_panel_coverage_ratio(healthy, cal), panel)
        self.assertIsNone(P.seat_panel_coverage_ratio({}, cal))


class ConsumersTest(unittest.TestCase):
    def pred_row(self, **over):
        row = {"logged_at": "2026-11-28T05:00:00Z", "weekend_of": W, "movie": "Hexed", "headline_mid_m": "25.47",
               "forecast_stage": "midweek-after-thursday", "market_window_compatible": "0",
               "poly_implied_mid_m": "33.92", "market_frame_window": "Wednesday-Sunday (5 days)",
               "market_frame_mid_m": "33.07"}
        row.update(over)
        return row

    def trade(self, **over):
        row = {"published_gmt": "2026-11-25T17:52:07", "kind": "weekend", "film": "Hexed", "release_date": "",
               "is_opener": "1", "three_day_m": "20.6", "multi_day_m": "33.0", "multi_day_frame": "5-day",
               "low_m": "", "high_m": "", "point_m": ""}
        row.update(over)
        return row

    def test_ensemble_compares_on_the_market_dates(self):
        row = E.ensemble_row(self.pred_row(), [self.trade()])
        self.assertEqual((33.07, 33.92, 33.0), (row["model_mid_m"], row["market_mid_m"], row["trade_mid_m"]))
        # 2026-11-28: an opener stage carries the weight of the regular stage
        # with as many reported days (it used to have none: market alone).
        stage = E.STAGE_ALIAS[self.pred_row()["forecast_stage"]]
        w = E.W_MODEL_WITH_MARKET[stage]
        self.assertEqual("Wednesday-Sunday (5 days)", row["frame"])
        self.assertEqual("market+model" if 0 < w < 1 else ("model" if w >= 1 else "market"), row["ensemble_source"])
        self.assertAlmostEqual(33.07 ** w * 33.92 ** (1 - w), row["ensemble_mid_m"], places=2)
        no_market = E.ensemble_row(self.pred_row(poly_implied_mid_m=""), [self.trade()])
        self.assertEqual(33.0, no_market["trade_mid_m"])
        self.assertEqual(3, E._frame_days("Friday-Sunday (3 days)"))
        self.assertEqual(20.6, E._frame_row_value(self.trade(), 3))
        self.assertIsNone(E._frame_row_value(self.trade(multi_day_frame="4-day"), 5))
        self.assertAlmostEqual((28 * 37) ** 0.5, E._frame_row_value(
            self.trade(kind="range", low_m="28", high_m="37", multi_day_m=""), 5))

    def test_ensemble_without_a_frame_number_stays_model_only(self):
        row = E.ensemble_row(self.pred_row(market_frame_mid_m="", market_frame_window=""), [self.trade()])
        self.assertEqual(("model", "", ""), (row["ensemble_source"], row["market_mid_m"], row["frame"]))
        self.assertEqual(25.47, row["model_mid_m"])

    def test_report_skips_rows_on_the_market_dates(self):
        rows = [E.ensemble_row(self.pred_row(), [])]
        out = io.StringIO()
        self.assertEqual([], E.report(rows, {("Hexed", W): 25.0}, out=out))

    def test_no_paper_bet_against_a_market_on_other_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            pred, odds = os.path.join(tmp, "pred.csv"), os.path.join(tmp, "odds.csv")
            fields = ["logged_at", "weekend_of", "movie", "headline_mid_m", "forecast_stage",
                      "poly_logged_at", "poly_event", "market_window_compatible"]
            base = {"logged_at": "2026-11-27T17:17:15Z", "weekend_of": W, "movie": "Hexed", "headline_mid_m": "39.14",
                    "forecast_stage": "after-friday", "poly_logged_at": "2026-11-27T17:17:15Z",
                    "poly_event": "hexed-5-day"}
            prices = [("<28m", 0.05), ("28m-32m", 0.25), ("32m-36m", 0.60), ("36m+", 0.10)]
            with open(odds, "w", newline="") as f:
                rows = [{"logged_at": base["logged_at"], "weekend_of": W, "movie": "Hexed", "event_slug": "hexed-5-day",
                         "bracket": b, "yes_price": p, "best_bid": p - 0.01, "best_ask": p + 0.01,
                         "last_trade": p, "volume": 100, "market_id": i} for i, (b, p) in enumerate(prices)]
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
            ratios = {"after-friday": [("2026-09-%02d" % d, "m%d" % d, v) for d, v in
                                       enumerate([0.1, -0.1, 0.05, -0.05, 0.0, 0.08, -0.08, 0.02], start=1)]}

            def bets(flag):
                with open(pred, "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=fields)
                    w.writeheader()
                    w.writerow({**base, "market_window_compatible": flag})
                return T.place_bets(pred, odds, trades={}, ratios=ratios)[1]

            self.assertTrue(bets("1"))
            self.assertEqual([], bets("0"))


if __name__ == "__main__":
    unittest.main()
