import asyncio
import csv
import json
import tempfile
import unittest
import os
import importlib
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

    def test_polymarket_fetch_uses_public_search_for_low_volume_opening_markets(self):
        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self.payload

        def event(title, slug, end_date, *, closed=False):
            return {
                "id": slug,
                "title": title,
                "slug": slug,
                "active": True,
                "closed": closed,
                "archived": False,
                "endDate": end_date,
                "volume24hr": 500,
                "markets": [
                    {
                        "id": f"{slug}-1",
                        "question": f"Will {title} be less than 20m?",
                        "volume": "500",
                        "outcomePrices": "[\"0.5\", \"0.5\"]",
                    }
                ],
            }

        old_get = getattr(scraper.requests, "get", None)

        def fake_get(url, params=None, timeout=None):
            if url.endswith("/events"):
                return FakeResponse([])
            if url.endswith("/public-search"):
                return FakeResponse({
                    "events": [
                        event(
                            '"Obsession" Opening Weekend Box Office',
                            "obsession-opening-weekend-box-office",
                            "2026-05-18T12:00:00Z",
                        ),
                        event(
                            '"Mortal Kombat II" 2nd Weekend Box Office',
                            "mortal-kombat-ii-2nd-weekend-box-office",
                            "2026-05-18T12:00:00Z",
                        ),
                        event(
                            '"Backrooms" Opening Weekend Box Office',
                            "backrooms-opening-weekend-box-office",
                            "2026-06-01T12:00:00Z",
                        ),
                        event(
                            '"Old Movie" Opening Weekend Box Office',
                            "old-movie-opening-weekend-box-office",
                            "2026-05-18T12:00:00Z",
                            closed=True,
                        ),
                    ]
                })
            raise AssertionError(url)

        try:
            scraper.requests.get = fake_get
            markets = scraper.fetch_polymarket_box_office()
        finally:
            if old_get is None:
                del scraper.requests.get
            else:
                scraper.requests.get = old_get

        titles = [m["movie_title"] for m in markets]
        self.assertIn("Obsession", titles)
        self.assertIn("Backrooms", titles)
        self.assertNotIn("Mortal Kombat II", titles)
        self.assertNotIn("Old Movie", titles)

        current_weekend = scraper.filter_live_markets_for_weekend(
            markets,
            "2026-05-15",
            "Phase 1",
        )
        self.assertEqual(["Obsession"], [m["movie_title"] for m in current_weekend])

    def test_saturday_sunday_collection_window_starts_at_10am(self):
        self.assertTrue(scraper.showtime_in_collection_window("10:00am", "2026-05-09"))
        self.assertTrue(scraper.showtime_in_collection_window("12:00pm", "2026-05-09"))
        self.assertTrue(scraper.showtime_in_collection_window("11:00pm", "2026-05-10"))
        self.assertFalse(scraper.showtime_in_collection_window("9:55am", "2026-05-09"))
        self.assertFalse(scraper.showtime_in_collection_window("11:30pm", "2026-05-10"))

    def test_weekday_collection_window_keeps_existing_5pm_start(self):
        self.assertFalse(scraper.showtime_in_collection_window("10:00am", "2026-05-08"))
        self.assertTrue(scraper.showtime_in_collection_window("5:00pm", "2026-05-08"))
        self.assertTrue(scraper.showtime_in_collection_window("11:00pm", "2026-05-08"))

    def test_phase2_saved_entries_use_same_showtime_window(self):
        entries = [
            {"showtime": "9:55am", "showtime_id": "too-early"},
            {"showtime": "10:00am", "showtime_id": "morning"},
            {"showtime": "4:30pm", "showtime_id": "daytime"},
            {"showtime": "11:00pm", "showtime_id": "late"},
            {"showtime": "11:30pm", "showtime_id": "too-late"},
        ]

        kept = scraper.filter_showtime_entries_for_collection_window(entries, "2026-05-09")

        self.assertEqual(
            ["morning", "daytime", "late"],
            [entry["showtime_id"] for entry in kept],
        )

    def test_phase1_cache_requires_current_showtime_window_before_merge(self):
        old_window_cache = {
            "weekend_of": "2026-05-08",
            "theatres": {
                "AMC Old": {
                    "tz": "ET",
                    "dates": {
                        "2026-05-09": {
                            "movies": {
                                "The Sheep Detectives": [
                                    {"showtime": "7:00pm", "showtime_id": "old"}
                                ],
                            },
                        },
                    },
                },
            },
        }
        current_window_cache = {
            **old_window_cache,
            "showtime_window_version": scraper.SHOWTIME_WINDOW_VERSION,
        }

        self.assertFalse(
            scraper.phase1_cache_is_mergeable(old_window_cache, "2026-05-08")
        )
        self.assertTrue(
            scraper.phase1_cache_is_mergeable(current_window_cache, "2026-05-08")
        )
        self.assertFalse(
            scraper.phase1_cache_is_mergeable(current_window_cache, "2026-05-15")
        )

    def test_phase1_cache_sanitizer_drops_unversioned_date_entries(self):
        saved_links = {
            "AMC Mixed": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-09": {
                        "movies": {
                            "The Sheep Detectives": [
                                {"showtime": "7:00pm", "showtime_id": "old-window"}
                            ],
                        },
                    },
                    "2026-05-10": {
                        "showtime_window_version": scraper.SHOWTIME_WINDOW_VERSION,
                        "movies": {
                            "The Sheep Detectives": [
                                {"showtime": "10:00am", "showtime_id": "new-window"}
                            ],
                        },
                    },
                },
            },
        }

        sanitized = scraper.sanitize_phase1_links_for_current_window(saved_links)

        self.assertEqual(["2026-05-10"], list(sanitized["AMC Mixed"]["dates"]))
        self.assertNotIn(
            "2026-05-09",
            sanitized["AMC Mixed"]["dates"],
        )

    def test_seat_row_notes_include_showtime_window_version(self):
        note = scraper.add_showtime_window_note("Standard @ 7:00 PM")

        self.assertIn(f"showtime_window={scraper.SHOWTIME_WINDOW_VERSION}", note)

    def test_duplicate_seat_row_updates_showtime_window_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_csv = scraper.SEAT_CSV
            scraper.SEAT_CSV = Path(tmp) / "seat-counts.csv"
            row = {field: "" for field in scraper.SEAT_FIELDS}
            row.update({
                "weekend_of": "2026-05-08",
                "run_id": "old-run",
                "date": "2026-05-09",
                "day_of_week": "Saturday",
                "theatre_name": "AMC Existing",
                "timezone": "ET",
                "movie_title": "Movie A",
                "showtime": "7:00pm",
                "auditorium_type": "Standard",
                "total_seats": "100",
                "seats_sold": "50",
                "seats_available": "50",
                "notes": "Standard @ 7:00 PM",
            })
            updated = dict(row)
            updated["run_id"] = "new-run"
            updated["notes"] = scraper.add_showtime_window_note(updated["notes"])
            try:
                scraper.ensure_csv_header()
                with scraper.SEAT_CSV.open("a", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=scraper.SEAT_FIELDS)
                    writer.writerow(row)

                written, skipped = scraper.append_unique_seat_rows([
                    [updated.get(field, "") for field in scraper.SEAT_FIELDS]
                ])
                with scraper.SEAT_CSV.open(newline="") as f:
                    rows = list(csv.DictReader(f))
            finally:
                scraper.SEAT_CSV = old_csv

        self.assertEqual(0, written)
        self.assertEqual(1, skipped)
        self.assertEqual(1, len(rows))
        self.assertIn(f"showtime_window={scraper.SHOWTIME_WINDOW_VERSION}", rows[0]["notes"])

    def test_append_unique_seat_rows_fills_inferable_blank_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_csv = scraper.SEAT_CSV
            scraper.SEAT_CSV = Path(tmp) / "seat-counts.csv"
            zero_sold = {field: "" for field in scraper.SEAT_FIELDS}
            zero_sold.update({
                "weekend_of": "2026-05-08",
                "run_id": "run-1",
                "date": "2026-05-10",
                "day_of_week": "Sunday",
                "theatre_name": "AMC Empty",
                "timezone": "ET",
                "movie_title": "Movie A",
                "showtime": "9:00pm",
                "auditorium_type": "Standard",
                "total_seats": "53",
                "seats_sold": "",
                "seats_available": "53",
                "occupancy_pct": "",
                "amc_seat_map_url": "https://example.test/empty",
            })
            sold_out = dict(zero_sold)
            sold_out.update({
                "run_id": "run-2",
                "theatre_name": "AMC Full",
                "total_seats": "107",
                "seats_sold": "107",
                "seats_available": "",
                "amc_seat_map_url": "https://example.test/full",
            })
            try:
                written, skipped = scraper.append_unique_seat_rows([
                    [zero_sold.get(field, "") for field in scraper.SEAT_FIELDS],
                    [sold_out.get(field, "") for field in scraper.SEAT_FIELDS],
                ])
                with scraper.SEAT_CSV.open(newline="") as f:
                    rows = list(csv.DictReader(f))
            finally:
                scraper.SEAT_CSV = old_csv

        self.assertEqual(2, written)
        self.assertEqual(0, skipped)
        self.assertEqual("0", rows[0]["seats_sold"])
        self.assertEqual("53", rows[0]["seats_available"])
        self.assertEqual("0", rows[0]["occupancy_pct"])
        self.assertEqual("107", rows[1]["seats_sold"])
        self.assertEqual("0", rows[1]["seats_available"])
        self.assertEqual("100", rows[1]["occupancy_pct"])

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

    def test_snapshot_only_phase2_uses_remaining_weekend_window(self):
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

            scraper.local_now = lambda tz: datetime(2026, 5, 8, 22, 30)
            self.assertEqual(
                {"ET": ["2026-05-08", "2026-05-09", "2026-05-10"]},
                scraper.phase2_collection_dates_by_group(["ET"], snapshots_only=True),
            )

            scraper.local_now = lambda tz: datetime(2026, 5, 10, 22, 30)
            self.assertEqual(
                {"ET": ["2026-05-10"]},
                scraper.phase2_collection_dates_by_group(["ET"], snapshots_only=True),
            )
        finally:
            scraper.local_now = old_local_now

    def test_snapshot_keeps_date_when_at_least_one_active_movie_has_links(self):
        saved_links = {
            "AMC PT 1": {
                "tz": "PT",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-08": {
                        "movies": {
                            "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "mk-fri"}],
                            "The Sheep Detectives": [{"showtime": "7:00pm", "showtime_id": "sheep-fri"}],
                        }
                    },
                    "2026-05-09": {
                        "movies": {
                            "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "mk-sat"}],
                        }
                    },
                },
            },
        }
        poly_markets = [
            {"movie_title": "Mortal Kombat II"},
            {"movie_title": "The Sheep Detectives"},
        ]

        usable, skipped = scraper.snapshot_usable_date_sets(
            poly_markets,
            saved_links,
            ["PT"],
            {"PT": ["2026-05-08", "2026-05-09"]},
            min_theatres=1,
        )

        self.assertEqual({"PT": ["2026-05-08", "2026-05-09"]}, usable)
        self.assertEqual(1, len(skipped))
        self.assertEqual("PT", skipped[0]["timezone"])
        self.assertEqual("2026-05-09", skipped[0]["show_date"])
        self.assertEqual(["The Sheep Detectives"], skipped[0]["missing_movies"])
        self.assertFalse(skipped[0]["date_skipped"])

    def test_snapshot_link_validation_uses_selected_theatre_subset(self):
        saved_links = {
            "AMC Selected": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-08": {
                        "movies": {
                            "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "mk"}],
                        }
                    }
                },
            },
            "AMC Not Selected": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-08": {
                        "movies": {
                            "The Sheep Detectives": [{"showtime": "7:00pm", "showtime_id": "sheep"}],
                        }
                    }
                },
            },
        }

        selected_links = scraper.filter_saved_links_by_names(saved_links, {"AMC Selected"})
        usable, skipped = scraper.snapshot_usable_date_sets(
            [{"movie_title": "Mortal Kombat II"}, {"movie_title": "The Sheep Detectives"}],
            selected_links,
            ["ET"],
            {"ET": ["2026-05-08"]},
            min_theatres=1,
        )

        self.assertEqual({"ET": ["2026-05-08"]}, usable)
        self.assertEqual(["The Sheep Detectives"], skipped[0]["missing_movies"])
        self.assertFalse(skipped[0]["date_skipped"])

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

    def test_live_market_selection_keeps_only_current_weekend_events(self):
        old_tracked = scraper.tracked_movie_titles_from_state
        try:
            scraper.tracked_movie_titles_from_state = lambda weekend: []
            markets = scraper.select_collection_markets(
                [
                    {
                        "movie_title": "Mortal Kombat II",
                        "market_url": "https://example.test/mk",
                        "end_date": "2026-05-11T12:00:00Z",
                    },
                    {
                        "movie_title": "Future Movie",
                        "market_url": "https://example.test/future",
                        "end_date": "2026-05-18T12:00:00Z",
                    },
                ],
                datetime(2026, 5, 6, 18, 0),
                "Phase 1",
                weekend_override="2026-05-08",
                prefer_live_markets=True,
            )
        finally:
            scraper.tracked_movie_titles_from_state = old_tracked

        self.assertEqual(["Mortal Kombat II"], [m["movie_title"] for m in markets])

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

    def test_active_market_guard_flags_missing_timezone_movie_links(self):
        saved_links = {
            "AMC East": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-08": {
                        "movies": {
                            "The Sheep Detectives": [
                                {"showtime": "7:00pm", "showtime_id": "east-1"}
                            ]
                        }
                    }
                },
            },
            "AMC West": {
                "tz": "PT",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-08": {
                        "movies": {
                            "Mortal Kombat II": [
                                {"showtime": "7:00pm", "showtime_id": "west-1"}
                            ]
                        }
                    }
                },
            },
        }
        markets = [
            {"movie_title": "The Sheep Detectives"},
            {"movie_title": "Mortal Kombat II"},
        ]

        missing = scraper.active_market_phase1_link_gaps(
            markets,
            saved_links,
            ["PT"],
            {"PT": ["2026-05-08"]},
        )

        self.assertEqual(
            [
                {
                    "movie_title": "The Sheep Detectives",
                    "timezone": "PT",
                    "show_date": "2026-05-08",
                    "fresh_theatres": 0,
                    "required_theatres": 1,
                }
            ],
            missing,
        )
        with self.assertRaises(SystemExit):
            scraper.require_active_market_phase1_links(
                markets,
                saved_links,
                ["PT"],
                {"PT": ["2026-05-08"]},
                "Phase 1 scrape preflight for PT",
            )

    def test_ensure_links_repairs_active_movie_gaps_even_when_coverage_is_high(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_links_json = scraper.LINKS_JSON
            old_load_theatres = scraper.load_theatres
            old_phase1_expected_date = scraper.phase1_expected_date
            old_fetch = scraper.fetch_polymarket_box_office
            old_select = scraper.select_collection_markets
            old_run_collect = scraper.run_collect_links_async
            tmp_links = Path(tmp) / "showtime-links.json"
            tmp_links.write_text(json.dumps({
                "weekend_of": "2026-05-08",
                "theatres": {
                    "AMC West": {
                        "tz": "PT",
                        "cohort": scraper.CORE_COHORT,
                        "dates": {
                            "2026-05-08": {
                                "movies": {
                                    "Mortal Kombat II": [
                                        {"showtime": "7:00pm", "showtime_id": "west-1"}
                                    ]
                                }
                            }
                        },
                    }
                },
            }))
            calls = []

            async def fake_collect(tz_group, target_date=None, full_weekend=None):
                calls.append((tz_group, target_date, full_weekend))
                repaired = json.loads(tmp_links.read_text())
                repaired["theatres"]["AMC West"]["dates"]["2026-05-08"]["movies"][
                    "The Sheep Detectives"
                ] = [{"showtime": "8:00pm", "showtime_id": "west-sheep-1"}]
                tmp_links.write_text(json.dumps(repaired))

            try:
                scraper.LINKS_JSON = tmp_links
                scraper.load_theatres = lambda: {
                    "PT": [
                        {
                            "name": "AMC West",
                            "slug": "amc-west",
                            "cohort": scraper.CORE_COHORT,
                        }
                    ]
                }
                scraper.phase1_expected_date = lambda tz: "2026-05-08"
                scraper.fetch_polymarket_box_office = lambda: [
                    {"movie_title": "Mortal Kombat II"},
                    {"movie_title": "The Sheep Detectives"},
                ]
                scraper.select_collection_markets = (
                    lambda live_markets, ref_dt, phase_label,
                    weekend_override=None, prefer_live_markets=False: live_markets
                )
                scraper.run_collect_links_async = fake_collect

                asyncio.run(scraper.ensure_phase1_links_async("PT"))
            finally:
                scraper.LINKS_JSON = old_links_json
                scraper.load_theatres = old_load_theatres
                scraper.phase1_expected_date = old_phase1_expected_date
                scraper.fetch_polymarket_box_office = old_fetch
                scraper.select_collection_markets = old_select
                scraper.run_collect_links_async = old_run_collect

            self.assertEqual([("PT", "2026-05-08", False)], calls)

    def test_snapshot_repair_attempts_missing_movie_links_and_keeps_partial_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_links_json = scraper.LINKS_JSON
            old_run_collect = scraper.run_collect_links_async
            tmp_links = Path(tmp) / "showtime-links.json"
            saved_links = {
                "AMC PT 1": {
                    "tz": "PT",
                    "cohort": scraper.CORE_COHORT,
                    "dates": {
                        "2026-05-08": {
                            "showtime_window_version": scraper.SHOWTIME_WINDOW_VERSION,
                            "movies": {
                                "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "mk-fri"}],
                                "The Sheep Detectives": [{"showtime": "7:00pm", "showtime_id": "sheep-fri"}],
                            },
                        },
                        "2026-05-09": {
                            "showtime_window_version": scraper.SHOWTIME_WINDOW_VERSION,
                            "movies": {
                                "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "mk-sat"}],
                            },
                        },
                    },
                },
            }
            tmp_links.write_text(json.dumps({
                "weekend_of": "2026-05-08",
                "showtime_window_version": scraper.SHOWTIME_WINDOW_VERSION,
                "theatres": saved_links,
            }))
            calls = []

            async def fake_collect(tz_group, target_date=None, full_weekend=None):
                calls.append((tz_group, target_date, full_weekend))

            try:
                scraper.LINKS_JSON = tmp_links
                scraper.run_collect_links_async = fake_collect
                repaired_links, usable, skipped = asyncio.run(
                    scraper.repair_snapshot_phase1_links_async(
                        [
                            {"movie_title": "Mortal Kombat II"},
                            {"movie_title": "The Sheep Detectives"},
                        ],
                        saved_links,
                        ["PT"],
                        {"PT": ["2026-05-08", "2026-05-09"]},
                    )
                )
            finally:
                scraper.LINKS_JSON = old_links_json
                scraper.run_collect_links_async = old_run_collect

            self.assertEqual([("PT", "2026-05-09", False)], calls)
            self.assertEqual(saved_links, repaired_links)
            self.assertEqual({"PT": ["2026-05-08", "2026-05-09"]}, usable)
            self.assertEqual(1, len(skipped))
            self.assertEqual(["The Sheep Detectives"], skipped[0]["missing_movies"])
            self.assertFalse(skipped[0]["date_skipped"])

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

    def test_snapshot_theatre_cap_selects_top_signal_theatres_across_timezones(self):
        theatres_map = {
            "ET": [
                {"name": "ET A", "dma": "NY", "cohort": scraper.CORE_COHORT},
                {"name": "ET B", "dma": "NY", "cohort": scraper.CORE_COHORT},
                {"name": "ET C", "dma": "NY", "cohort": scraper.CORE_COHORT},
                {"name": "ET D", "dma": "NY", "cohort": scraper.CORE_COHORT},
            ],
            "CT": [
                {"name": "CT A", "dma": "Chicago", "cohort": scraper.CORE_COHORT},
                {"name": "CT B", "dma": "Chicago", "cohort": scraper.CORE_COHORT},
                {"name": "CT C", "dma": "Chicago", "cohort": scraper.CORE_COHORT},
            ],
            "PT": [
                {"name": "PT A", "dma": "LA", "cohort": scraper.CORE_COHORT},
                {"name": "PT B", "dma": "LA", "cohort": scraper.CORE_COHORT},
                {"name": "PT C", "dma": "LA", "cohort": scraper.CORE_COHORT},
            ],
        }
        signal_scores = {
            "ET A": 40, "ET B": 30, "ET C": 20, "ET D": 10,
            "CT A": 80, "CT B": 70, "CT C": 60,
            "PT A": 100, "PT B": 90, "PT C": 1,
        }

        selected = scraper.select_snapshot_theatre_names(
            theatres_map,
            cap=5,
            signal_scores=signal_scores,
        )

        self.assertEqual({"ET A", "ET B", "CT A", "CT B", "PT A"}, selected)

    def test_snapshot_signal_scores_reward_distinct_regular_seat_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            seat_csv = Path(tmp) / "seat-counts.csv"
            with open(seat_csv, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=scraper.SEAT_FIELDS)
                writer.writeheader()
                for date_str in ("2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"):
                    writer.writerow({
                        "weekend_of": "2026-05-08",
                        "date": date_str,
                        "theatre_name": "AMC Multi Day",
                        "movie_title": "Mortal Kombat II",
                        "total_seats": "100",
                        "seats_sold": "0",
                    })

            scores = scraper.snapshot_theatre_signal_scores(seat_csv)

        # Four distinct regular seat-count dates should count as four samples:
        # 4 * (100 seats * 0.03) + 4 * sample_bonus(5) = 32.
        self.assertAlmostEqual(32.0, scores["AMC Multi Day"])

    def test_snapshot_phase2_work_expands_remaining_weekend_only_for_selected_theatres(self):
        theatres_map = {
            "ET": [
                {"name": "AMC Keep", "dma": "NY", "cohort": scraper.CORE_COHORT},
                {"name": "AMC Drop", "dma": "NY", "cohort": scraper.CORE_COHORT},
            ]
        }
        collection_dates = {
            "ET": ["2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"]
        }

        work = scraper.build_phase2_theatre_work(
            theatres_map,
            ["ET"],
            collection_dates,
            snapshots_only=True,
            snapshot_theatre_names={"AMC Keep"},
        )

        self.assertEqual(4, len(work))
        self.assertEqual({"AMC Keep"}, {row["name"] for row in work})
        self.assertEqual(
            ["2026-05-07", "2026-05-08", "2026-05-09", "2026-05-10"],
            [row["_date"] for row in work],
        )

    def test_snapshot_phase2_work_never_falls_back_to_all_theatres_when_selection_empty(self):
        theatres_map = {
            "ET": [
                {"name": "AMC A", "dma": "NY", "cohort": scraper.CORE_COHORT},
                {"name": "AMC B", "dma": "NY", "cohort": scraper.CORE_COHORT},
            ]
        }

        work = scraper.build_phase2_theatre_work(
            theatres_map,
            ["ET"],
            {"ET": ["2026-05-08"]},
            snapshots_only=True,
            snapshot_theatre_names=set(),
        )

        self.assertEqual([], work)

    def test_snapshot_theatre_selection_uses_link_available_theatres_first(self):
        theatres_map = {
            "ET": [
                {"name": "AMC High No Links", "dma": "NY", "cohort": scraper.CORE_COHORT},
                {"name": "AMC Lower With Links", "dma": "NY", "cohort": scraper.CORE_COHORT},
            ],
            "CT": [],
            "PT": [],
        }
        saved_links = {
            "AMC Lower With Links": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-08": {
                        "movies": {
                            "Mortal Kombat II": [
                                {"showtime": "7:00pm", "showtime_id": "mk"}
                            ],
                        }
                    }
                },
            },
        }

        selected = scraper.select_snapshot_theatre_names(
            theatres_map,
            groups=["ET"],
            cap=1,
            signal_scores={"AMC High No Links": 999, "AMC Lower With Links": 1},
            saved_links=saved_links,
            requested_date_sets={"ET": ["2026-05-08"]},
            movie_titles=["Mortal Kombat II"],
        )

        self.assertEqual({"AMC Lower With Links"}, selected)

    def test_snapshot_theatre_selection_keeps_partial_active_movie_links(self):
        theatres_map = {
            "PT": [
                {"name": "AMC Partial", "dma": "LA", "cohort": scraper.CORE_COHORT},
            ],
        }
        saved_links = {
            "AMC Partial": {
                "tz": "PT",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-09": {
                        "movies": {
                            "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "mk"}],
                        },
                    },
                },
            },
        }

        selected = scraper.select_snapshot_theatre_names(
            theatres_map,
            groups=["PT"],
            cap=1,
            signal_scores={"AMC Partial": 1},
            saved_links=saved_links,
            requested_date_sets={"PT": ["2026-05-09"]},
            movie_titles=["Mortal Kombat II", "The Sheep Detectives"],
        )

        self.assertEqual({"AMC Partial"}, selected)

    def test_snapshot_theatre_selection_prefers_fuller_weekend_link_coverage(self):
        theatres_map = {
            "ET": [
                {"name": "AMC High Partial", "dma": "NY", "cohort": scraper.CORE_COHORT},
                {"name": "AMC Lower Full", "dma": "NY", "cohort": scraper.CORE_COHORT},
            ],
        }
        saved_links = {
            "AMC High Partial": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-08": {
                        "movies": {
                            "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "partial-fri"}],
                        },
                    },
                },
            },
            "AMC Lower Full": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-08": {
                        "movies": {
                            "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "full-fri"}],
                        },
                    },
                    "2026-05-09": {
                        "movies": {
                            "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "full-sat"}],
                        },
                    },
                    "2026-05-10": {
                        "movies": {
                            "Mortal Kombat II": [{"showtime": "7:00pm", "showtime_id": "full-sun"}],
                        },
                    },
                },
            },
        }

        selected = scraper.select_snapshot_theatre_names(
            theatres_map,
            groups=["ET"],
            cap=1,
            signal_scores={"AMC High Partial": 999, "AMC Lower Full": 1},
            saved_links=saved_links,
            requested_date_sets={"ET": ["2026-05-08", "2026-05-09", "2026-05-10"]},
            movie_titles=["Mortal Kombat II"],
        )

        self.assertEqual({"AMC Lower Full"}, selected)

    def test_snapshot_global_selection_uses_all_timezones_for_matrix_leg_cap(self):
        theatres_map = {
            "ET": [
                {"name": "ET A", "dma": "NY", "cohort": scraper.CORE_COHORT},
                {"name": "ET B", "dma": "NY", "cohort": scraper.CORE_COHORT},
            ],
            "CT": [
                {"name": "CT A", "dma": "Chicago", "cohort": scraper.CORE_COHORT},
                {"name": "CT B", "dma": "Chicago", "cohort": scraper.CORE_COHORT},
            ],
            "PT": [
                {"name": "PT A", "dma": "LA", "cohort": scraper.CORE_COHORT},
                {"name": "PT B", "dma": "LA", "cohort": scraper.CORE_COHORT},
            ],
        }

        groups, date_sets = scraper.snapshot_global_selection_inputs(theatres_map)

        self.assertEqual(["ET", "CT", "PT"], groups)
        self.assertEqual({"ET", "CT", "PT"}, set(date_sets))
        self.assertTrue(all(date_sets[group] for group in groups))

    def test_snapshot_link_aware_selection_keeps_global_cap_across_timezones(self):
        theatres_map = {
            "ET": [
                {"name": "ET A", "dma": "NY", "cohort": scraper.CORE_COHORT},
                {"name": "ET B", "dma": "NY", "cohort": scraper.CORE_COHORT},
            ],
            "CT": [
                {"name": "CT A", "dma": "Chicago", "cohort": scraper.CORE_COHORT},
                {"name": "CT B", "dma": "Chicago", "cohort": scraper.CORE_COHORT},
            ],
            "PT": [
                {"name": "PT A", "dma": "LA", "cohort": scraper.CORE_COHORT},
                {"name": "PT B", "dma": "LA", "cohort": scraper.CORE_COHORT},
            ],
        }
        groups, date_sets = scraper.snapshot_global_selection_inputs(theatres_map)
        saved_links = {}
        for group, theatres in theatres_map.items():
            date_str = date_sets[group][0]
            for theatre in theatres:
                saved_links[theatre["name"]] = {
                    "tz": group,
                    "cohort": scraper.CORE_COHORT,
                    "dates": {
                        date_str: {
                            "movies": {
                                "Mortal Kombat II": [
                                    {"showtime": "7:00pm", "showtime_id": theatre["name"]}
                                ],
                            },
                        },
                    },
                }

        selected = scraper.select_snapshot_theatre_names(
            theatres_map,
            groups=groups,
            cap=3,
            signal_scores={
                "ET A": 100, "ET B": 90,
                "CT A": 80, "CT B": 70,
                "PT A": 60, "PT B": 50,
            },
            saved_links=saved_links,
            requested_date_sets=date_sets,
            movie_titles=["Mortal Kombat II"],
        )

        self.assertEqual(3, len(selected))
        self.assertEqual({"ET", "CT", "PT"}, {saved_links[name]["tz"] for name in selected})

    def test_snapshot_market_filter_keeps_movie_with_future_date_links(self):
        saved_links = {
            "AMC Future": {
                "tz": "ET",
                "cohort": scraper.CORE_COHORT,
                "dates": {
                    "2026-05-09": {
                        "movies": {
                            "Future Only": [{"showtime": "7:00pm", "showtime_id": "future"}],
                        },
                    },
                },
            }
        }

        filtered = scraper.filter_markets_with_phase1_links_for_date_sets(
            [
                {"movie_title": "Missing"},
                {"movie_title": "Future Only"},
            ],
            saved_links,
            groups=["ET"],
            expected_date_sets={"ET": ["2026-05-08", "2026-05-09"]},
            min_theatres=1,
        )

        self.assertEqual(["Future Only"], [market["movie_title"] for market in filtered])

    def test_snapshot_theatre_coverage_flags_thin_theatre_date_sample(self):
        expected_theatres = [
            {"name": "AMC A", "_tz": "ET", "_date": "2026-05-07"},
            {"name": "AMC B", "_tz": "ET", "_date": "2026-05-07"},
            {"name": "AMC C", "_tz": "ET", "_date": "2026-05-08"},
        ]
        snapshot_rows = [
            {"theatre_name": "AMC A", "timezone": "ET", "show_date": "2026-05-07"},
        ]

        report = scraper.snapshot_theatre_coverage(expected_theatres, snapshot_rows)
        failures = scraper.snapshot_coverage_failures(report, min_ratio=0.8)

        self.assertEqual(3, report["expected_total"])
        self.assertEqual(1, report["observed_total"])
        self.assertAlmostEqual(1 / 3, report["ratio"])
        self.assertIn("overall 1/3 theatre-date slices", failures[0])
        self.assertTrue(any("2026-05-08 ET 0/1 theatres" in failure for failure in failures))

    def test_partial_snapshot_coverage_is_warning_when_rows_were_captured(self):
        report = {
            "expected_total": 10,
            "observed_total": 4,
            "ratio": 0.4,
            "by_slice": {},
        }

        self.assertFalse(
            scraper.snapshot_coverage_failure_is_fatal(report, snapshot_rows_written=12)
        )

    def test_empty_snapshot_coverage_is_fatal(self):
        report = {
            "expected_total": 10,
            "observed_total": 0,
            "ratio": 0.0,
            "by_slice": {},
        }

        self.assertTrue(
            scraper.snapshot_coverage_failure_is_fatal(report, snapshot_rows_written=0)
        )

    def test_partial_snapshot_phase1_coverage_is_warning_when_some_links_exist(self):
        report = {
            "expected_total": 10,
            "fresh_count": 3,
            "ratio": 0.3,
        }

        self.assertFalse(scraper.snapshot_phase1_coverage_failure_is_fatal(report))

    def test_empty_snapshot_phase1_coverage_is_fatal(self):
        report = {
            "expected_total": 10,
            "fresh_count": 0,
            "ratio": 0.0,
        }

        self.assertTrue(scraper.snapshot_phase1_coverage_failure_is_fatal(report))

    def test_pre_reservation_snapshot_only_records_future_showtimes(self):
        self.assertTrue(scraper.should_record_pre_reservation_snapshot(-90))
        self.assertTrue(scraper.should_record_pre_reservation_snapshot(0))
        self.assertFalse(scraper.should_record_pre_reservation_snapshot(1))
        self.assertFalse(scraper.should_record_pre_reservation_snapshot(75))

    def test_phase2_deadline_is_env_configurable_for_snapshot_workflow(self):
        old_value = os.environ.get("PHASE2_DEADLINE_SEC")
        os.environ["PHASE2_DEADLINE_SEC"] = "8100"
        try:
            reloaded = importlib.reload(scraper)
            self.assertEqual(8100, reloaded.PHASE2_DEADLINE_SEC)
        finally:
            if old_value is None:
                os.environ.pop("PHASE2_DEADLINE_SEC", None)
            else:
                os.environ["PHASE2_DEADLINE_SEC"] = old_value
            importlib.reload(scraper)

    def test_phase2_theatre_timeout_is_env_configurable_for_daytime_window(self):
        old_value = os.environ.get("PHASE2_THEATRE_TIMEOUT_SEC")
        os.environ["PHASE2_THEATRE_TIMEOUT_SEC"] = "300"
        try:
            reloaded = importlib.reload(scraper)
            self.assertEqual(300, reloaded.PHASE2_THEATRE_TIMEOUT_SEC)
        finally:
            if old_value is None:
                os.environ.pop("PHASE2_THEATRE_TIMEOUT_SEC", None)
            else:
                os.environ["PHASE2_THEATRE_TIMEOUT_SEC"] = old_value
            importlib.reload(scraper)

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
