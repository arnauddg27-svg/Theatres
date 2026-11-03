"""Tiny-release rule of the small-film gate (2026-11-03): a calendar-seeded
title with a metadata theatre count under the floor AND no AMC listing for the
weekend is not collected. Queen at Sea (1 theatre) cost every snapshot leg a
900 s link repair."""
import csv
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import small_film_gate as G  # noqa: E402

W = "2026-11-06"


def write_metadata(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["movie", "weekend_of", "genre", "national_theatre_count"])
        w.writeheader()
        for movie, weekend, count in rows:
            w.writerow({"movie": movie, "weekend_of": weekend, "genre": "drama", "national_theatre_count": count})


def write_links(path, weekend, movies_by_theatre):
    theatres = {name: {"tz": "ET", "dates": {weekend: {"movies": {m: [{"showtime_id": "1"}] for m in movies}}}}
                for name, movies in movies_by_theatre.items()}
    with open(path, "w") as f:
        json.dump({"weekend_of": weekend, "date": weekend, "theatres": theatres}, f)


class TinyReleaseGateTest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.meta = os.path.join(self.td.name, "movie-metadata.csv")
        self.links = os.path.join(self.td.name, "showtime-links.json")
        self.log = os.path.join(self.td.name, "prediction-log.csv")
        with open(self.log, "w", newline="") as f:
            f.write("logged_at,weekend_of,movie,headline_mid_m,forecast_stage\n")
        write_metadata(self.meta, [("Queen at Sea", W, "1"), ("Godzilla Minus Zero", W, ""),
                                   ("Jimmy", W, "2400"), ("Old Platform Film", "2026-10-30", "3")])
        G._REPORTED.clear()

    def tearDown(self):
        self.td.cleanup()

    def _wide_links(self, extra=()):
        booked = {f"AMC Theatre {i}": ["Godzilla Minus Zero", "Jimmy", *extra] for i in range(60)}
        write_links(self.links, W, booked)

    def test_tiny_unlisted_title_is_gated(self):
        self._wide_links()
        gated = G.dropped_titles(W, path=self.log, metadata_path=self.meta, links_path=self.links)
        self.assertEqual(set(gated), {"queen at sea"})
        self.assertIn("1 theatre(s)", gated["queen at sea"])
        kept = G.filter_titles(["Godzilla Minus Zero", "Queen at Sea", "Jimmy"], W, "snapshot", path=self.log)
        # filter_titles reads the real data files; assert through dropped_titles with explicit paths instead
        self.assertIn("Jimmy", kept)

    def test_placeholder_count_on_a_listed_film_is_kept(self):
        self._wide_links(extra=["Queen at Sea"])
        self.assertEqual(G.tiny_release_titles(W, metadata_path=self.meta, links_path=self.links), {})

    def test_no_links_evidence_keeps_the_film(self):
        # no links file at all
        self.assertEqual(G.tiny_release_titles(W, metadata_path=self.meta, links_path=self.links + ".missing"), {})
        # links for another weekend
        write_links(self.links, "2026-10-30", {f"AMC {i}": ["Clayface"] for i in range(60)})
        self.assertEqual(G.tiny_release_titles(W, metadata_path=self.meta, links_path=self.links), {})
        # too few theatres covered yet
        write_links(self.links, W, {f"AMC {i}": ["Jimmy"] for i in range(10)})
        self.assertEqual(G.tiny_release_titles(W, metadata_path=self.meta, links_path=self.links), {})

    def test_floor_is_configurable_and_gate_can_be_disabled(self):
        self._wide_links()
        with mock.patch.dict(os.environ, {"SMALL_FILM_MIN_THEATRES": "1"}):
            self.assertEqual(G.tiny_release_titles(W, metadata_path=self.meta, links_path=self.links), {})
        with mock.patch.dict(os.environ, {"SMALL_FILM_GATE": "0"}):
            self.assertEqual(G.tiny_release_titles(W, metadata_path=self.meta, links_path=self.links), {})

    def test_forecast_rule_still_merges(self):
        self._wide_links()
        with open(self.log, "a", newline="") as f:
            f.write(f"2026-11-04T01:00:00Z,{W},Jimmy,0.8,presales\n2026-11-04T02:00:00Z,{W},Jimmy,0.9,presales\n")
        gated = G.dropped_titles(W, path=self.log, metadata_path=self.meta, links_path=self.links)
        self.assertEqual(set(gated), {"queen at sea", "jimmy"})
        self.assertEqual(gated["jimmy"], 0.9)


if __name__ == "__main__":
    unittest.main()
