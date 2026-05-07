import tempfile
import unittest
import os
from datetime import datetime
from pathlib import Path
from types import ModuleType
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", ModuleType("requests"))
playwright_mod = ModuleType("playwright")
playwright_async = ModuleType("playwright.async_api")
playwright_async.async_playwright = lambda: None
sys.modules.setdefault("playwright", playwright_mod)
sys.modules.setdefault("playwright.async_api", playwright_async)
import scraper


class ScraperLoggingTest(unittest.TestCase):
    def test_log_run_writes_stable_per_run_file_with_bulleted_issues(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            old_run_log_dir = scraper.RUN_LOG_DIR
            old_run_log = scraper.RUN_LOG
            scraper.RUN_LOG_DIR = tmp_path / "run-logs"
            scraper.RUN_LOG = tmp_path / "run-log.md"
            try:
                log_path = scraper.log_run(
                    "PT",
                    ["Movie A"],
                    [
                        {
                            "theatre": "AMC Test 1",
                            "movie": "Movie A",
                            "format": "Laser at AMC",
                            "showtime": "7:00pm",
                            "occupancy": 42.5,
                            "delta": 15,
                        }
                    ],
                    [
                        "AMC Test 2: No seat map for Movie A @ 8:00pm",
                        "AMC Test 3: timeout after 180s — skipped",
                    ],
                    run_id="20260501-030500-test",
                    now=datetime(2026, 5, 1, 3, 24),
                )
            finally:
                scraper.RUN_LOG_DIR = old_run_log_dir
                scraper.RUN_LOG = old_run_log

            self.assertEqual(
                tmp_path / "run-logs" / "2026-05-01" / "20260501-032400-20260501-030500-test-PT.md",
                log_path,
            )
            content = log_path.read_text()
            self.assertIn("# 2026-05-01 03:24 - PT Group", content)
            self.assertIn("- **Rows:** 1", content)
            self.assertIn("- **Issues:** 2", content)
            self.assertIn("| AMC Test 1 | Movie A | Laser at AMC | 7:00pm | 42.5% | 15 min |", content)
            self.assertIn("- AMC Test 2: No seat map for Movie A @ 8:00pm", content)
            self.assertIn("- AMC Test 3: timeout after 180s — skipped", content)

    def test_phase1_full_weekend_dates_expand_from_thursday(self):
        dates = scraper.phase1_collection_dates(
            "ET",
            ref_dt=datetime(2026, 4, 30, 12, 0),
            full_weekend=True,
        )

        self.assertEqual(
            ["2026-04-30", "2026-05-01", "2026-05-02", "2026-05-03"],
            dates,
        )

    def test_phase1_full_weekend_dates_expand_from_tuesday_warm_cache(self):
        dates = scraper.phase1_collection_dates(
            "ET",
            ref_dt=datetime(2026, 5, 5, 12, 0),
            full_weekend=True,
        )

        self.assertEqual(
            ["2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"],
            dates,
        )
        self.assertEqual(
            "2026-05-01",
            scraper.opening_weekend_friday(datetime(2026, 5, 5, 12, 0)),
        )
        self.assertEqual(
            "2026-05-08",
            scraper.phase1_weekend_anchor(datetime(2026, 5, 5, 12, 0), full_weekend=True),
        )

    def test_phase1_full_weekend_dates_start_from_wednesday_for_preopening_snapshots(self):
        dates = scraper.phase1_collection_dates(
            "ET",
            ref_dt=datetime(2026, 5, 6, 12, 0),
            full_weekend=True,
        )

        self.assertEqual(
            ["2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"],
            dates,
        )
        self.assertEqual(
            "2026-05-01",
            scraper.opening_weekend_friday(datetime(2026, 5, 6, 12, 0)),
        )
        self.assertEqual(
            "2026-05-08",
            scraper.phase1_weekend_anchor(datetime(2026, 5, 6, 12, 0), full_weekend=True),
        )

    def test_snapshot_only_phase2_expects_current_local_date(self):
        old_local_now = scraper.local_now
        try:
            scraper.local_now = lambda tz: datetime(2026, 5, 5, 9, 30)

            self.assertEqual(
                {"ET": "2026-05-04"},
                scraper.phase2_expected_dates(["ET"], snapshots_only=False),
            )
            self.assertEqual(
                {"ET": "2026-05-05"},
                scraper.phase2_expected_dates(["ET"], snapshots_only=True),
            )
        finally:
            scraper.local_now = old_local_now

    def test_snapshot_only_phase2_expects_thursday_links_on_wednesday(self):
        old_local_now = scraper.local_now
        try:
            scraper.local_now = lambda tz: datetime(2026, 5, 6, 22, 30)

            self.assertEqual(
                {"ET": "2026-05-07", "CT": "2026-05-07", "PT": "2026-05-07"},
                scraper.phase2_expected_dates(["ET", "CT", "PT"], snapshots_only=True),
            )
            self.assertEqual(
                {
                    "ET": ["2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"],
                    "CT": ["2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"],
                    "PT": ["2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"],
                },
                scraper.phase2_collection_dates_by_group(
                    ["ET", "CT", "PT"],
                    snapshots_only=True,
                ),
            )
        finally:
            scraper.local_now = old_local_now

    def test_wednesday_preopening_collection_prefers_live_future_markets(self):
        old_tracked = scraper.tracked_movie_titles_from_state
        seen_weekends = []
        try:
            scraper.tracked_movie_titles_from_state = (
                lambda weekend: seen_weekends.append(weekend) or ["Prior Weekend Movie"]
            )
            markets = scraper.select_collection_markets(
                [{"movie_title": "Upcoming Movie", "market_url": "https://example.test"}],
                datetime(2026, 5, 6, 18, 0),
                "Phase 1",
                weekend_override="2026-05-08",
                prefer_live_markets=True,
            )
        finally:
            scraper.tracked_movie_titles_from_state = old_tracked

        self.assertEqual(["2026-05-08"], seen_weekends)
        self.assertEqual(["Upcoming Movie"], [m["movie_title"] for m in markets])

    def test_tuesday_warm_cache_collection_prefers_live_future_markets(self):
        old_tracked = scraper.tracked_movie_titles_from_state
        seen_weekends = []
        try:
            scraper.tracked_movie_titles_from_state = (
                lambda weekend: seen_weekends.append(weekend) or ["Prior Weekend Movie"]
            )
            weekend = scraper.phase1_weekend_anchor(datetime(2026, 5, 5, 18, 0), full_weekend=True)
            markets = scraper.select_collection_markets(
                [{"movie_title": "Upcoming Movie", "market_url": "https://example.test"}],
                datetime(2026, 5, 5, 18, 0),
                "Phase 1",
                weekend_override=weekend,
                prefer_live_markets=True,
            )
        finally:
            scraper.tracked_movie_titles_from_state = old_tracked

        self.assertEqual(["2026-05-08"], seen_weekends)
        self.assertEqual(["Upcoming Movie"], [m["movie_title"] for m in markets])

    def test_snapshot_only_keeps_current_day_phase1_links(self):
        theatres = [{"name": "AMC Snapshot", "_tz": "ET"}]
        saved_links = {
            "AMC Snapshot": {
                "tz": "ET",
                "show_date": "2026-05-05",
                "movies": {
                    "Movie A": [
                        {"showtime": "7:00pm", "showtime_id": "123", "format": "Standard"}
                    ]
                },
            }
        }

        fresh, stale = scraper.filter_fresh_phase2_theatres(
            theatres,
            saved_links,
            {"ET": "2026-05-05"},
        )

        self.assertEqual(theatres, fresh)
        self.assertEqual([], stale)

    def test_snapshot_only_keeps_future_weekend_phase1_links(self):
        theatres = [
            {
                "name": "AMC Snapshot",
                "_tz": "ET",
                "_phase2_expected_date": "2026-05-10",
            }
        ]
        saved_links = {
            "AMC Snapshot": {
                "tz": "ET",
                "dates": {
                    "2026-05-07": {"movies": {}},
                    "2026-05-10": {
                        "movies": {
                            "Movie A": [
                                {"showtime": "7:00pm", "showtime_id": "789", "format": "Standard"}
                            ]
                        }
                    },
                },
            }
        }

        fresh, stale = scraper.filter_fresh_phase2_theatres(
            theatres,
            saved_links,
            {"ET": "2026-05-07"},
        )

        self.assertEqual(theatres, fresh)
        self.assertEqual([], stale)

    def test_regular_phase2_uses_expected_date_not_theatre_local_date(self):
        theatres = [{"name": "AMC Regular", "_tz": "ET", "_date": "2026-05-08"}]
        saved_links = {
            "AMC Regular": {
                "tz": "ET",
                "show_date": "2026-05-07",
                "movies": {
                    "Movie A": [
                        {"showtime": "7:00pm", "showtime_id": "123", "format": "Standard"}
                    ]
                },
            }
        }

        fresh, stale = scraper.filter_fresh_phase2_theatres(
            theatres,
            saved_links,
            {"ET": "2026-05-07"},
        )

        self.assertEqual(theatres, fresh)
        self.assertEqual([], stale)

    def test_phase1_coverage_reads_nested_full_weekend_links(self):
        theatres = {
            "ET": [{"name": "AMC Nested", "slug": "amc-nested", "cohort": scraper.CORE_COHORT}]
        }
        saved_links = {
            "AMC Nested": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-01": {
                        "movies": {
                            "Movie A": [
                                {"showtime": "7:00pm", "showtime_id": "123", "format": "Standard"}
                            ]
                        }
                    }
                },
            }
        }

        coverage = scraper.phase1_link_coverage(
            saved_links,
            theatres,
            ["ET"],
            {"ET": "2026-05-01"},
        )
        counts = scraper.phase1_movie_link_counts(
            saved_links,
            groups=["ET"],
            expected_dates={"ET": "2026-05-01"},
        )

        self.assertEqual(1, coverage["fresh_count"])
        self.assertEqual({"Movie A": 1}, counts)

    def test_forward_cached_links_can_pass_stale_file_guard(self):
        theatres = {
            "ET": [{"name": "AMC Nested", "slug": "amc-nested", "cohort": scraper.CORE_COHORT}]
        }
        saved_links = {
            "AMC Nested": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-02": {
                        "movies": {
                            "Movie A": [
                                {"showtime": "7:00pm", "showtime_id": "123", "format": "Standard"}
                            ]
                        }
                    }
                },
            }
        }

        self.assertTrue(
            scraper.phase1_forward_cache_is_usable(
                saved_links,
                theatres,
                ["ET"],
                {"ET": "2026-05-02"},
            )
        )

    def test_snapshot_full_weekend_coverage_requires_each_show_date(self):
        theatres = {
            "ET": [{"name": "AMC Nested", "slug": "amc-nested", "cohort": scraper.CORE_COHORT}]
        }
        saved_links = {
            "AMC Nested": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-07": {
                        "movies": {
                            "Movie A": [
                                {"showtime": "7:00pm", "showtime_id": "123", "format": "Standard"}
                            ]
                        }
                    }
                },
            }
        }
        date_sets = {"ET": ["2026-05-07", "2026-05-08"]}

        coverage = scraper.phase1_link_coverage_for_date_sets(
            saved_links,
            theatres,
            ["ET"],
            date_sets,
        )

        self.assertEqual(2, coverage["expected_total"])
        self.assertEqual(1, coverage["fresh_count"])
        self.assertEqual(0.5, coverage["ratio"])
        self.assertEqual(
            {"2026-05-07": {"expected": 1, "fresh": 1}, "2026-05-08": {"expected": 1, "fresh": 0}},
            coverage["by_date"],
        )
        self.assertFalse(
            scraper.phase1_forward_cache_is_usable_for_date_sets(
                saved_links,
                theatres,
                ["ET"],
                date_sets,
            )
        )

    def test_phase1_required_coverage_uses_full_weekend_date_set(self):
        theatres = {
            "ET": [{"name": "AMC Nested", "slug": "amc-nested", "cohort": scraper.CORE_COHORT}]
        }
        saved_links = {
            "AMC Nested": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-07": {
                        "movies": {
                            "Movie A": [
                                {"showtime": "7:00pm", "showtime_id": "123", "format": "Standard"}
                            ]
                        }
                    }
                },
            }
        }

        coverage = scraper.phase1_required_link_coverage(
            saved_links,
            theatres,
            ["ET"],
            {"ET": "2026-05-07"},
            {"ET": ["2026-05-07", "2026-05-08"]},
        )

        self.assertEqual(2, coverage["expected_total"])
        self.assertEqual(1, coverage["fresh_count"])
        self.assertEqual(
            {"2026-05-07": {"expected": 1, "fresh": 1}, "2026-05-08": {"expected": 1, "fresh": 0}},
            coverage["by_date"],
        )
        with self.assertRaises(SystemExit):
            scraper.require_phase1_coverage(
                coverage,
                "Phase 1 full-weekend links for ET",
                min_ratio=0.9,
            )

    def test_snapshot_theatre_order_balances_show_dates_before_repeating_theatres(self):
        theatres = []
        for name in ("AMC A", "AMC B", "AMC C", "AMC D"):
            for show_date in ("2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"):
                theatres.append({
                    "name": name,
                    "dma": "NY",
                    "cohort": scraper.CORE_COHORT,
                    "_tz": "ET",
                    "_date": show_date,
                    "_phase2_expected_date": show_date,
                })

        ordered = scraper.order_phase2_theatres_for_collection(theatres, snapshots_only=True)

        self.assertEqual(
            [
                ("AMC A", "2026-05-07"),
                ("AMC B", "2026-05-08"),
                ("AMC C", "2026-05-09"),
                ("AMC D", "2026-05-10"),
            ],
            [(row["name"], row["_date"]) for row in ordered[:4]],
        )
        self.assertEqual(
            len({(row["name"], row["_date"]) for row in theatres}),
            len({(row["name"], row["_date"]) for row in ordered}),
        )

    def test_phase1_batches_current_day_before_future_cache(self):
        theatres = [
            {"name": "Core A", "_tz": "ET", "_date": "2026-04-30", "cohort": scraper.CORE_COHORT},
            {"name": "Core A", "_tz": "ET", "_date": "2026-05-01", "cohort": scraper.CORE_COHORT},
            {"name": "Expansion A", "_tz": "ET", "_date": "2026-04-30", "cohort": scraper.EXPANSION_COHORT},
            {"name": "Core B", "_tz": "ET", "_date": "2026-05-02", "cohort": scraper.CORE_COHORT},
        ]

        batches = scraper.phase1_collection_batches(theatres, {"ET": "2026-04-30"})

        self.assertEqual(
            [
                ("core current-day pass", [("Core A", "2026-04-30")]),
                ("expansion current-day pass", [("Expansion A", "2026-04-30")]),
                ("core forward-cache pass", [("Core A", "2026-05-01"), ("Core B", "2026-05-02")]),
            ],
            [
                (label, [(row["name"], row["_date"]) for row in rows])
                for label, rows in batches
            ],
        )

    def test_pre_reservation_snapshots_are_separate_and_deduped(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_csv = scraper.PRE_RESERVATION_CSV
            scraper.PRE_RESERVATION_CSV = Path(tmp) / "pre-reservation-snapshots.csv"
            try:
                row = {field: "" for field in scraper.PRE_RESERVATION_FIELDS}
                row.update(
                    {
                        "weekend_of": "2026-05-01",
                        "snapshot_bucket": "2026-05-01T18:00Z",
                        "show_date": "2026-05-02",
                        "theatre_name": "AMC Snapshot",
                        "timezone": "ET",
                        "movie_title": "Movie A",
                        "showtime": "7:00pm",
                        "showtime_id": "123",
                        "auditorium_type": "Standard",
                        "reserved_seats": "42",
                        "available_seats": "158",
                    }
                )

                written, skipped = scraper.append_unique_pre_reservation_rows([row, row])
            finally:
                scraper.PRE_RESERVATION_CSV = old_csv

            self.assertEqual(1, written)
            self.assertEqual(1, skipped)

    def test_snapshot_only_phase2_uses_low_impact_tab_limit(self):
        old_regular = os.environ.pop("SCRAPER_MAX_CONCURRENT_TABS", None)
        old_snapshot = os.environ.pop("SNAPSHOT_MAX_CONCURRENT_TABS", None)
        try:
            self.assertEqual(3, scraper.phase2_max_concurrent_tabs(snapshots_only=False))
            self.assertEqual(1, scraper.phase2_max_concurrent_tabs(snapshots_only=True))

            os.environ["SCRAPER_MAX_CONCURRENT_TABS"] = "4"
            os.environ["SNAPSHOT_MAX_CONCURRENT_TABS"] = "2"
            self.assertEqual(4, scraper.phase2_max_concurrent_tabs(snapshots_only=False))
            self.assertEqual(2, scraper.phase2_max_concurrent_tabs(snapshots_only=True))

            os.environ["SNAPSHOT_MAX_CONCURRENT_TABS"] = "0"
            self.assertEqual(1, scraper.phase2_max_concurrent_tabs(snapshots_only=True))
        finally:
            if old_regular is None:
                os.environ.pop("SCRAPER_MAX_CONCURRENT_TABS", None)
            else:
                os.environ["SCRAPER_MAX_CONCURRENT_TABS"] = old_regular
            if old_snapshot is None:
                os.environ.pop("SNAPSHOT_MAX_CONCURRENT_TABS", None)
            else:
                os.environ["SNAPSHOT_MAX_CONCURRENT_TABS"] = old_snapshot


if __name__ == "__main__":
    unittest.main()
