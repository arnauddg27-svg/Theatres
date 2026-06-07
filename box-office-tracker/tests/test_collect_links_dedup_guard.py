import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
import json
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.collect_links_dedup_guard import default_since_date, should_skip  # noqa: E402


def run(cmd, cwd):
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=True,
    )


def write_active_markets(repo, titles, date="2026-06-03"):
    markets = repo / "box-office-tracker" / "data" / "polymarket-markets.csv"
    markets.parent.mkdir(parents=True, exist_ok=True)
    lines = ["date,movie_title,market_url,market_question,outcome_prices,volume,market_id,notes\n"]
    for idx, title in enumerate(titles, 1):
        lines.append(
            f'{date},{title},https://example.test/{idx},"Will ""{title}"" Opening Weekend Box Office be over 1m?",'
            f'"[""0.5"", ""0.5""]",1000,market-{idx},\n'
        )
    markets.write_text("".join(lines))


def append_active_markets(repo, titles, date):
    markets = repo / "box-office-tracker" / "data" / "polymarket-markets.csv"
    with markets.open("a", encoding="utf-8") as f:
        for idx, title in enumerate(titles, 1):
            f.write(
                f'{date},{title},https://example.test/{date}/{idx},'
                f'"Will ""{title}"" Opening Weekend Box Office be over 1m?",'
                f'"[""0.5"", ""0.5""]",1000,market-{date}-{idx},\n'
            )


def write_showtime_links(repo, tz, titles_by_date, weekend_of="2026-06-05"):
    dates = {
        date: {
            "movies": {
                title: [{"showtime": "7:00 PM", "showtime_id": f"{date}-{title}"}]
                for title in titles
            }
        }
        for date, titles in titles_by_date.items()
    }
    payload = {
        "date": weekend_of,
        "weekend_of": weekend_of,
        "theatres": {
            "AMC Test 1": {
                "tz": tz,
                "dates": dates,
            }
        },
    }
    links = repo / "box-office-tracker" / "data" / "showtime-links.json"
    links.parent.mkdir(parents=True, exist_ok=True)
    links.write_text(json.dumps(payload))


def write_theatres(repo, tz, names):
    theatres = repo / "box-office-tracker" / "data" / "theatres-all.json"
    theatres.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        tz: [
            {"name": name, "slug": name.lower().replace(" ", "-")}
            for name in names
        ]
    }
    theatres.write_text(json.dumps(payload))


class CollectLinksDedupGuardTest(unittest.TestCase):
    def test_marker_only_commit_does_not_skip_but_link_data_commit_does(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)

            data_dir = repo / "box-office-tracker" / "data"
            data_dir.mkdir(parents=True)
            (repo / "README.md").write_text("init\n")
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "init"], repo)

            (repo / "marker-only.txt").write_text("marker\n")
            run(["git", "add", "marker-only.txt"], repo)
            run(["git", "commit", "-m", "data: box office ET collect-links"], repo)

            self.assertFalse(should_skip(repo, "ET", False, "2000-01-01"))

            write_active_markets(repo, ["Scary Movie"])
            write_showtime_links(
                repo,
                "ET",
                {
                    "2026-06-04": ["Scary Movie"],
                    "2026-06-05": ["Scary Movie"],
                    "2026-06-06": ["Scary Movie"],
                    "2026-06-07": ["Scary Movie"],
                },
            )
            run(["git", "add", "box-office-tracker/data/showtime-links.json"], repo)
            run(["git", "commit", "-m", "data: box office ET collect-links"], repo)

            self.assertTrue(
                should_skip(
                    repo,
                    "ET",
                    False,
                    "2000-01-01",
                    now=datetime(2026, 6, 3, 18, 0, tzinfo=timezone.utc),
                )
            )

    def test_link_marker_does_not_skip_when_active_movie_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)

            (repo / "README.md").write_text("init\n")
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "init"], repo)

            write_active_markets(repo, ["Scary Movie", "Masters of the Universe"])
            write_showtime_links(
                repo,
                "PT",
                {
                    "2026-06-04": ["Scary Movie"],
                    "2026-06-05": ["Scary Movie"],
                    "2026-06-06": ["Scary Movie"],
                    "2026-06-07": ["Scary Movie"],
                },
            )
            run(["git", "add", "box-office-tracker/data/showtime-links.json"], repo)
            run(["git", "commit", "-m", "data: box office PT collect-links"], repo)

            self.assertFalse(
                should_skip(
                    repo,
                    "PT",
                    False,
                    "2000-01-01",
                    now=datetime(2026, 6, 3, 18, 0, tzinfo=timezone.utc),
                )
            )

    def test_link_marker_does_not_skip_when_theatre_coverage_is_too_low(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)

            (repo / "README.md").write_text("init\n")
            data_dir = repo / "box-office-tracker" / "data"
            data_dir.mkdir(parents=True)
            write_theatres(repo, "PT", ["AMC Test 1", "AMC Test 2"])
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "init"], repo)

            active_titles = ["Scary Movie"]
            write_active_markets(repo, active_titles)
            write_showtime_links(
                repo,
                "PT",
                {
                    "2026-06-04": active_titles,
                    "2026-06-05": active_titles,
                    "2026-06-06": active_titles,
                    "2026-06-07": active_titles,
                },
            )
            run(["git", "add", "box-office-tracker/data/showtime-links.json"], repo)
            run(["git", "commit", "-m", "data: box office PT collect-links"], repo)

            self.assertFalse(
                should_skip(
                    repo,
                    "PT",
                    False,
                    "2000-01-01",
                    now=datetime(2026, 6, 3, 18, 0, tzinfo=timezone.utc),
                )
            )

    def test_link_marker_skips_when_all_active_movies_have_weekend_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)

            (repo / "README.md").write_text("init\n")
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "init"], repo)

            active_titles = ["Scary Movie", "Masters of the Universe"]
            write_active_markets(repo, active_titles)
            write_showtime_links(
                repo,
                "PT",
                {
                    "2026-06-04": active_titles,
                    "2026-06-05": active_titles,
                    "2026-06-06": active_titles,
                    "2026-06-07": active_titles,
                },
            )
            run(["git", "add", "box-office-tracker/data/showtime-links.json"], repo)
            run(["git", "commit", "-m", "data: box office PT collect-links"], repo)

            self.assertTrue(
                should_skip(
                    repo,
                    "PT",
                    False,
                    "2000-01-01",
                    now=datetime(2026, 6, 3, 18, 0, tzinfo=timezone.utc),
                )
            )

    def test_active_slate_uses_opening_week_not_only_latest_market_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            run(["git", "config", "user.name", "Test"], repo)
            run(["git", "config", "user.email", "test@example.com"], repo)

            (repo / "README.md").write_text("init\n")
            run(["git", "add", "."], repo)
            run(["git", "commit", "-m", "init"], repo)

            write_active_markets(repo, ["Scary Movie", "Masters of the Universe"], date="2026-06-06")
            append_active_markets(repo, ["Scary Movie"], date="2026-06-07")
            write_showtime_links(
                repo,
                "PT",
                {
                    "2026-06-07": ["Scary Movie"],
                },
            )
            run(["git", "add", "box-office-tracker/data/showtime-links.json"], repo)
            run(["git", "commit", "-m", "data: box office PT collect-links"], repo)

            self.assertFalse(
                should_skip(
                    repo,
                    "PT",
                    False,
                    "2026-06-07",
                    now=datetime(2026, 6, 7, 18, 0, tzinfo=timezone.utc),
                )
            )

    def test_force_bypasses_collect_links_dedup(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            self.assertFalse(should_skip(repo, "ET", True, "2000-01-01"))

    def test_wednesday_default_since_checks_tuesday_warm_cache(self):
        self.assertEqual(
            "2026-05-12",
            default_since_date(datetime(2026, 5, 13, 12, 0, tzinfo=timezone.utc)),
        )
        self.assertEqual(
            "2026-05-14",
            default_since_date(datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)),
        )


if __name__ == "__main__":
    unittest.main()
