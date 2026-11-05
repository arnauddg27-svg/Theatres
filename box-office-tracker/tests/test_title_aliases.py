"""Short Polymarket title vs full calendar title = one film (2026-11-05)."""
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scraper  # noqa: E402

spec = importlib.util.spec_from_file_location("retag", ROOT / "scripts" / "retag_title_alias.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
spec2 = importlib.util.spec_from_file_location("odds", ROOT / "scripts" / "log_polymarket_odds.py")
O = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(O)

LONG = "Ramayana: Rise of A Legend"
SHORT = "Ramayana"


class CanonicalMapTest(unittest.TestCase):
    def test_short_whole_word_prefix_maps_to_longest(self):
        amap = scraper.canonical_title_map([SHORT, LONG, "Jimmy"], aliases={})
        self.assertEqual(amap, {SHORT: LONG})

    def test_partial_word_and_tiny_prefixes_do_not_merge(self):
        self.assertEqual(scraper.canonical_title_map(["Scream", "Screamers"], aliases={}), {})
        self.assertEqual(scraper.canonical_title_map(["It", "It Ends With Us"], aliases={}), {})

    def test_sequel_numbers_do_merge(self):
        self.assertEqual(scraper.canonical_title_map(["Scream", "Scream 7"], aliases={}), {"Scream": "Scream 7"})

    def test_recorded_alias_wins_without_prefix(self):
        amap = scraper.canonical_title_map(["Chainsaw Man", "Other"], aliases={"Chainsaw Man - The Movie": ["Chainsaw Man"]})
        self.assertEqual(amap, {"Chainsaw Man": "Chainsaw Man - The Movie"})

    def test_dedupe_keeps_order_and_collapses(self):
        with mock.patch.object(scraper, "load_title_aliases", return_value={}):
            self.assertEqual(scraper.dedupe_title_aliases(["Godzilla", SHORT, "Jimmy", LONG]),
                             ["Godzilla", LONG, "Jimmy"])


class RegistryTest(unittest.TestCase):
    def test_record_and_load_roundtrip_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "title-aliases.json"
            self.assertTrue(scraper.record_title_alias("2026-11-06", LONG, SHORT, path=p))
            self.assertFalse(scraper.record_title_alias("2026-11-06", LONG, SHORT, path=p))
            self.assertEqual(scraper.load_title_aliases("2026-11-06", path=p), {LONG: [SHORT]})
            self.assertEqual(scraper.load_title_aliases("2026-11-13", path=p), {})
            self.assertEqual(scraper.load_title_aliases(path=p), {LONG: [SHORT]})
            self.assertEqual(scraper.title_aliases_for(LONG, aliases={LONG: [SHORT]}), [SHORT])
            self.assertEqual(scraper.title_aliases_for("Jimmy", aliases={LONG: [SHORT]}), [])

    def test_match_targets_cover_aliases_with_canonical_precedence(self):
        with mock.patch.object(scraper, "load_title_aliases", return_value={LONG: [SHORT]}):
            targets = scraper.title_match_targets([LONG, "Jimmy"], str.lower)
        self.assertEqual(targets, {LONG.lower(): LONG, SHORT.lower(): LONG, "jimmy": "Jimmy"})


class MarketCanonicalisationTest(unittest.TestCase):
    def test_live_market_is_renamed_and_alias_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "title-aliases.json"
            with mock.patch.object(scraper, "TITLE_ALIASES_JSON", p), \
                 mock.patch.object(scraper, "calendar_titles_for_weekend", return_value=[LONG, "Jimmy"]), \
                 mock.patch.object(scraper, "market_matches_collection_weekend", return_value=True):
                out = scraper.canonicalise_market_titles(
                    [{"movie_title": SHORT, "market_url": "u"}, {"movie_title": "Godzilla Minus Zero"}],
                    "2026-11-06", "Phase 2")
            self.assertEqual([m["movie_title"] for m in out], [LONG, "Godzilla Minus Zero"])
            self.assertEqual(out[0]["market_title"], SHORT)
            self.assertEqual(json.loads(p.read_text()), {"2026-11-06": {LONG: [SHORT]}})

    def test_other_weekend_market_is_left_alone(self):
        with mock.patch.object(scraper, "load_title_aliases", return_value={}), \
             mock.patch.object(scraper, "calendar_titles_for_weekend", return_value=[LONG]), \
             mock.patch.object(scraper, "market_matches_collection_weekend", return_value=False):
            out = scraper.canonicalise_market_titles([{"movie_title": SHORT}], "2026-11-06", "Phase 2")
        self.assertEqual(out[0]["movie_title"], SHORT)

    def test_calendar_merge_does_not_add_the_twin(self):
        with mock.patch.object(scraper, "load_title_aliases", return_value={}), \
             mock.patch.object(scraper, "calendar_titles_for_weekend", return_value=[LONG, "Jimmy"]):
            out = scraper.merge_calendar_titles([{"movie_title": SHORT}], "2026-11-06", "Phase 2")
            self.assertEqual([m["movie_title"] for m in out], [SHORT, "Jimmy"])
            out = scraper.merge_calendar_titles([{"movie_title": LONG}], "2026-11-06", "Phase 2")
            self.assertEqual([m["movie_title"] for m in out], [LONG, "Jimmy"])

    def test_select_collection_markets_tracks_full_title_once(self):
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(scraper, "TITLE_ALIASES_JSON", Path(td) / "a.json"), \
                 mock.patch.object(scraper, "calendar_titles_for_weekend", return_value=[LONG]), \
                 mock.patch.object(scraper, "market_matches_collection_weekend", return_value=True), \
                 mock.patch.object(scraper, "tracked_movie_titles_from_state", return_value=[]), \
                 mock.patch.object(scraper.small_film_gate, "filter_titles", side_effect=lambda t, w, p: list(t)):
                out = scraper.select_collection_markets([{"movie_title": SHORT, "bracket_markets": []}],
                                                        None, "Phase 2", weekend_override="2026-11-06",
                                                        prefer_live_markets=True)
        self.assertEqual([m["movie_title"] for m in out], [LONG])


class StateAndListingsTest(unittest.TestCase):
    def test_tracked_titles_from_links_collapse(self):
        with tempfile.TemporaryDirectory() as td:
            links = Path(td) / "links.json"
            links.write_text(json.dumps({"weekend_of": "2026-11-06", "theatres": {
                "AMC X": {"dates": {"2026-11-06": {"movies": {SHORT: [], LONG: [], "Jimmy": []}}}}}}))
            with mock.patch.object(scraper, "LINKS_JSON", links), \
                 mock.patch.object(scraper, "THEATRE_COUNTS_JSON", Path(td) / "none.json"), \
                 mock.patch.object(scraper, "load_title_aliases", return_value={}), \
                 mock.patch.object(scraper, "calendar_titles_for_weekend", return_value=[]), \
                 mock.patch.object(scraper.small_film_gate, "filter_titles", side_effect=lambda t, w, p: list(t)), \
                 mock.patch.object(scraper.holdover, "collection_titles", return_value=[]):
                titles = scraper.tracked_movie_titles_from_state("2026-11-06")
        self.assertEqual(titles, [LONG, "Jimmy"])

    def test_phase1_matches_a_listing_under_the_alias(self):
        shows = [{"movie": "Ramayana", "showtime": "7:00pm", "showtime_id": "1"},
                 {"movie": "Jimmy", "showtime": "7:30pm", "showtime_id": "2"}]
        with mock.patch.object(scraper, "load_title_aliases", return_value={LONG: [SHORT]}), \
             mock.patch.object(scraper, "filter_showtime_entries_for_collection_window", side_effect=lambda m, d: m):
            got = scraper._phase1_collect(shows, [LONG], "2026-11-06")
        self.assertEqual(list(got), [LONG])
        self.assertEqual(got[LONG][0]["showtime_id"], "1")

    def test_every_lane_builds_alias_aware_targets(self):
        for name in ("regal_inventory.py", "fandango_collect.py", "cinemark_collect.py",
                     "webedia_collect.py", "alamo_collect.py", "harkins_collect.py"):
            self.assertIn("title_match_targets(titles,", (ROOT / name).read_text(), name)

    def test_odds_logger_files_the_market_under_the_canonical_title(self):
        with mock.patch.object(scraper, "calendar_titles_for_weekend", return_value=[LONG]), \
             mock.patch.object(scraper, "load_title_aliases", return_value={}):
            self.assertEqual(O.canonical_movie(SHORT, "2026-11-06"), LONG)
            self.assertEqual(O.canonical_movie("Jimmy", "2026-11-06"), "Jimmy")


class RetagScriptTest(unittest.TestCase):
    def make_data(self, td):
        d = Path(td)
        with open(d / "pre-reservation-snapshots.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["weekend_of", "theatre_name", "movie_title", "showtime_id", "snapshot_time"])
            w.writerow(["2026-11-06", "AMC X", SHORT, "1", "t1"])
            w.writerow(["2026-11-06", "AMC X", LONG, "1", "t1"])      # becomes a duplicate
            w.writerow(["2026-11-06", "AMC Y", SHORT, "2", "t1"])
            w.writerow(["2026-10-30", "AMC Y", SHORT, "9", "t0"])      # other weekend: untouched
        with open(d / "polymarket-markets.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "movie_title", "market_id", "notes"])
            w.writerow(["2026-11-05", SHORT, "m1", "weekend_of=2026-11-06"])
            w.writerow(["2026-10-01", SHORT, "m0", "weekend_of=2026-10-30"])
        with open(d / "movie-metadata.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["movie", "weekend_of", "genre", "notes", "national_theatre_count"])
            w.writerow([LONG, "2026-11-06", "action", "BOM", ""])
            w.writerow([SHORT, "2026-11-06", "", "", "1800"])
        (d / "showtime-links.json").write_text(json.dumps({"weekend_of": "2026-11-06", "theatres": {
            "AMC X": {"movies": {SHORT: [{"showtime_id": "1"}]},
                      "dates": {"2026-11-06": {"movies": {SHORT: [{"showtime_id": "1"}, {"showtime_id": "3"}],
                                                          LONG: [{"showtime_id": "1"}]}, "empty": False}}}}}))
        (d / "theatre-counts.json").write_text(json.dumps({SHORT: 1500, "_requested_movies": [SHORT, LONG, "Jimmy"]}))
        return d

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            d = self.make_data(td)
            before = {p.name: p.read_text() for p in d.iterdir()}
            report = R.retag("2026-11-06", SHORT, LONG, data_dir=d, write=False, log=lambda *_: None)
            self.assertEqual(set(report), {"pre-reservation-snapshots.csv", "polymarket-markets.csv",
                                           "movie-metadata.csv", "showtime-links.json", "theatre-counts.json"})
            self.assertEqual({p.name: p.read_text() for p in d.iterdir()}, before)

    def test_write_folds_everything_onto_the_canonical_title(self):
        with tempfile.TemporaryDirectory() as td:
            d = self.make_data(td)
            R.retag("2026-11-06", SHORT, LONG, data_dir=d, write=True, log=lambda *_: None)
            snaps = list(csv.DictReader(open(d / "pre-reservation-snapshots.csv")))
            self.assertEqual([(r["movie_title"], r["showtime_id"]) for r in snaps],
                             [(LONG, "1"), (LONG, "2"), (SHORT, "9")])
            poly = list(csv.DictReader(open(d / "polymarket-markets.csv")))
            self.assertEqual([r["movie_title"] for r in poly], [LONG, SHORT])
            meta = list(csv.DictReader(open(d / "movie-metadata.csv")))
            self.assertEqual(len(meta), 1)
            self.assertEqual((meta[0]["movie"], meta[0]["genre"], meta[0]["national_theatre_count"]),
                             (LONG, "action", "1800"))
            links = json.loads((d / "showtime-links.json").read_text())
            movies = links["theatres"]["AMC X"]["dates"]["2026-11-06"]["movies"]
            self.assertEqual(list(movies), [LONG])
            self.assertEqual([s["showtime_id"] for s in movies[LONG]], ["1", "3"])
            self.assertEqual(list(links["theatres"]["AMC X"]["movies"]), [LONG])
            counts = json.loads((d / "theatre-counts.json").read_text())
            self.assertEqual(counts, {LONG: 1500, "_requested_movies": [LONG, "Jimmy"]})
            self.assertEqual(json.loads((d / "title-aliases.json").read_text()), {"2026-11-06": {LONG: [SHORT]}})


if __name__ == "__main__":
    unittest.main()
