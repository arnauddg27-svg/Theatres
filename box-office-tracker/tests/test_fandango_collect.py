import csv
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fandango_collect as fc  # noqa: E402
from scraper import PRE_RESERVATION_FIELDS, PRE_RESERVATION_DEDUPE_FIELDS  # noqa: E402


NOW = datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc)


def _row(**over):
    theatre = {"name": "Regal Test", "city": "Dallas, TX",
               "timezone": "America/Chicago", "chain": "REGL"}
    params = {"chain": "REGL", "tid": "AACAW", "mid": "244348",
              "sdate": "2026-06-20 19:55", "is_seat_page": True}
    seats = {"total": 200, "reserved": 50, "available": 150,
             "rowFirst": "A", "containerFits": True}
    base = dict(
        theatre=theatre, movie_title="Toy Story 5", sdate="2026-06-20 19:55",
        seat_url="https://tickets.fandango.com/mobileexpress/seatselection?chainCode=REGL&tid=AACAW&mid=244348",
        params=params, seats=seats, weekend_of="2026-06-19", run_id="run-x",
        check_time=NOW.isoformat(), minutes_until=475, show_date="2026-06-20",
        day_of_week="Saturday",
    )
    base.update(over)
    return fc.build_fandango_row(**base)


class SchemaTests(unittest.TestCase):
    def test_schema_is_amc_superset_plus_chain(self):
        self.assertEqual(fc.FANDANGO_PRE_RESERVATION_FIELDS[:-1], list(PRE_RESERVATION_FIELDS))
        self.assertEqual(fc.FANDANGO_PRE_RESERVATION_FIELDS[-1], "chain")
        self.assertEqual(
            fc.FANDANGO_PRE_RESERVATION_DEDUPE_FIELDS,
            tuple(PRE_RESERVATION_DEDUPE_FIELDS) + ("chain",),
        )

    def test_row_has_exactly_the_schema_fields(self):
        row = _row()
        self.assertEqual(set(row), set(fc.FANDANGO_PRE_RESERVATION_FIELDS))
        self.assertEqual(row["chain"], "REGL")
        # showtime_id is the showtime datetime — Fandango's mid is the movie id
        self.assertEqual(row["showtime_id"], "2026-06-20 19:55")
        self.assertEqual(row["occupancy_pct"], "25.0")
        # legacy-named column holds the Fandango seat-map URL
        self.assertIn("seatselection", row["amc_seat_map_url"])


class DiscoveryLogicTests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(fc.slugify_title("Toy Story 5"), "toy-story-5")
        # '&' -> 'and' to match Fandango slugs (regression 2026-07-03:
        # 'Minions & Monsters' was silently dropped when '&' was stripped)
        self.assertEqual(
            fc.slugify_title("Star Wars: The Mandalorian & Grogu"),
            "star-wars-the-mandalorian-and-grogu",
        )
        self.assertEqual(fc.slugify_title("Minions & Monsters"), "minions-and-monsters")
        self.assertEqual(fc.slugify_title("Fast & Furious 11"), "fast-and-furious-11")

    def test_ampersand_title_matches_fandango_slug(self):
        targets = {fc.slugify_title("Minions & Monsters"): "Minions & Monsters"}
        self.assertEqual(
            fc.match_target_title(
                "/minions-and-monsters-2026-241234/movie-overview", targets),
            "Minions & Monsters",
        )

    def test_overview_core_slug_strips_year_and_id(self):
        self.assertEqual(
            fc.overview_core_slug("/toy-story-5-2026-243393/movie-overview"), "toy-story-5")
        self.assertEqual(
            fc.overview_core_slug(
                "https://www.fandango.com/backrooms-2026-244954/movie-overview"), "backrooms")

    def test_title_match_is_exact_no_prefix_bleed(self):
        targets = {fc.slugify_title(t): t for t in ["Toy Story 5", "Backrooms"]}
        self.assertEqual(
            fc.match_target_title("/toy-story-5-2026-243393/movie-overview", targets),
            "Toy Story 5")
        # 'Toy Story' (different film) must not match 'Toy Story 5'
        self.assertIsNone(
            fc.match_target_title("/toy-story-1995-1234/movie-overview", targets))
        self.assertIsNone(
            fc.match_target_title("/unrelated-2026-9/movie-overview", targets))

    def test_sdate_extracted_from_jump_href(self):
        href = ("https://tickets.fandango.com/transaction/ticketing/mobile/jump.aspx"
                "?row_count=1&sdate=2026-06-20+19%3A55&mid=244348")
        self.assertEqual(fc.sdate_from_jump_href(href), "2026-06-20 19:55")

    def test_select_wanted_showtimes_filters_and_prioritizes_primetime(self):
        def href(sd):
            q = sd.replace(" ", "+").replace(":", "%3A")
            return f"https://tickets.fandango.com/transaction/ticketing/mobile/jump.aspx?sdate={q}&mid=1"

        TS5 = "/toy-story-5-2026-243393/movie-overview"
        entries = [
            {"movieOverview": TS5, "href": href("2026-06-20 11:00")},   # matinee (future)
            {"movieOverview": TS5, "href": href("2026-06-20 19:30")},   # prime
            {"movieOverview": TS5, "href": href("2026-06-20 22:00")},   # late
            {"movieOverview": "/other-2026-9/movie-overview", "href": href("2026-06-20 19:00")},  # not tracked
            {"movieOverview": TS5, "href": href("2026-06-25 19:00")},   # out of window
            {"movieOverview": TS5, "href": href("2026-06-20 06:00")},   # already started (past)
        ]
        targets = {fc.slugify_title("Toy Story 5"): "Toy Story 5"}
        window = set()
        for d in ("2026-06-18", "2026-06-19", "2026-06-20", "2026-06-21"):
            window.add(d)
        now = dt = datetime(2026, 6, 20, 8, 0, tzinfo=timezone.utc)

        # cap=2 → the two most prime-time shows, in prime order
        top2 = fc.select_wanted_showtimes(entries, targets, window, "UTC", now, cap=2)
        self.assertEqual([w["sdate"] for w in top2],
                         ["2026-06-20 19:30", "2026-06-20 22:00"])
        self.assertTrue(all(w["title"] == "Toy Story 5" for w in top2))

        # cap=0 → all 3 valid (matinee included), still prime-ordered
        allv = fc.select_wanted_showtimes(entries, targets, window, "UTC", now, cap=0)
        self.assertEqual([w["sdate"] for w in allv],
                         ["2026-06-20 19:30", "2026-06-20 22:00", "2026-06-20 11:00"])

    def test_timing_pre_show_vs_past(self):
        m_after, m_until, sd, dow = fc.showtime_timing("2026-06-20 19:55", "UTC", NOW)
        self.assertLess(m_after, 0)          # show is in the future
        self.assertGreater(m_until, 0)
        self.assertEqual((sd, dow), ("2026-06-20", "Saturday"))
        m_past, _, _, _ = fc.showtime_timing("2026-06-20 08:00", "UTC", NOW)
        self.assertGreaterEqual(m_past, 0)   # show already started → not recorded


class DedupeAndWriteTests(unittest.TestCase):
    def test_chain_in_dedupe_key(self):
        regl = _row()
        cnmk = _row(theatre={"name": "Cinemark T", "city": "X",
                             "timezone": "America/Chicago", "chain": "CNMK"},
                    params={"chain": "CNMK", "tid": "T", "mid": "244348",
                            "sdate": "2026-06-20 19:55", "is_seat_page": True})
        self.assertNotEqual(fc.fandango_row_key(regl), fc.fandango_row_key(cnmk))

    def test_distinct_showtimes_same_theatre_do_not_collapse(self):
        # Regression: Fandango's `mid` is the movie id (same for every showtime of
        # a film), so showtime_id must be the datetime or distinct times collapse.
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fandango.csv"
            evening = _row(sdate="2026-06-20 19:30")
            late = _row(sdate="2026-06-20 22:15")
            self.assertNotEqual(fc.fandango_row_key(evening), fc.fandango_row_key(late))
            written, skipped = fc.append_unique_fandango_rows([evening, late], csv_path=path)
            self.assertEqual((written, skipped), (2, 0))

    def test_append_dedupes_and_computes_delta(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fandango.csv"
            r1 = _row(seats={"total": 200, "reserved": 50, "available": 150,
                             "rowFirst": "A", "containerFits": True},
                      check_time="2026-06-20T10:00:00+00:00")
            written, skipped = fc.append_unique_fandango_rows([r1], csv_path=path)
            self.assertEqual((written, skipped), (1, 0))

            # same showtime, same bucket → deduped
            _, skipped2 = fc.append_unique_fandango_rows([r1], csv_path=path)
            self.assertEqual(skipped2, 1)

            # same showtime, LATER bucket, more reserved → new row + delta
            r2 = _row(seats={"total": 200, "reserved": 80, "available": 120,
                             "rowFirst": "A", "containerFits": True},
                      check_time="2026-06-20T11:00:00+00:00")
            written3, _ = fc.append_unique_fandango_rows([r2], csv_path=path)
            self.assertEqual(written3, 1)

            with open(path) as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0].keys() | set(),
                             set(fc.FANDANGO_PRE_RESERVATION_FIELDS))
            later = [r for r in rows if r["snapshot_bucket"].endswith("11:00Z")][0]
            self.assertEqual(later["delta_reserved_since_previous"], "30")

    def test_delta_is_vs_latest_prior_bucket_not_max_reserved(self):
        # Regression: a reservation dip (50→80→60) then a new reading (70) must
        # delta against the LATEST prior bucket (60 → +10), not the max (80 → -10).
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fandango.csv"

            def at(reserved, hh):
                return _row(seats={"total": 200, "reserved": reserved,
                                   "available": 200 - reserved,
                                   "rowFirst": "A", "containerFits": True},
                            check_time=f"2026-06-20T{hh}:00:00+00:00")

            fc.append_unique_fandango_rows([at(50, "08"), at(80, "09"), at(60, "10")],
                                           csv_path=path)
            fc.append_unique_fandango_rows([at(70, "11")], csv_path=path)
            rows = list(csv.DictReader(open(path)))
            last = [r for r in rows if r["snapshot_bucket"].endswith("11:00Z")][0]
            self.assertEqual(last["delta_reserved_since_previous"], "10")

    def test_header_written_to_target_path(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "sub" / "fandango.csv"
            fc.append_unique_fandango_rows([_row()], csv_path=path)
            with open(path) as f:
                header = f.readline().strip().split(",")
            self.assertEqual(header, fc.FANDANGO_PRE_RESERVATION_FIELDS)


class ThrottleBackoffTests(unittest.TestCase):
    def _shared(self, **over):
        s = {"lock": threading.Lock(), "stop": threading.Event(),
             "consec_fail": 0, "backoff_extra": 0.0,
             "backoff_after": 4, "stop_after": 12,
             "backoff_step": 6.0, "backoff_max": 30.0,
             "paused_until": 0.0, "resume_count": 0, "max_resumes": 0,
             "pause_sec": 600.0, "deadline": time.monotonic() + 10_000}
        s.update(over)
        return s

    def test_backoff_kicks_in_then_success_resets(self):
        s = self._shared()
        for _ in range(3):                       # below backoff threshold
            self.assertFalse(fc._note_seat_failure(s))
        self.assertEqual(s["backoff_extra"], 0.0)
        fc._note_seat_failure(s)                 # 4th → backoff
        self.assertGreater(s["backoff_extra"], 0.0)
        self.assertFalse(s["stop"].is_set())
        fc._note_seat_success(s)                 # a render succeeds → reset
        self.assertEqual(s["consec_fail"], 0)
        self.assertEqual(s["backoff_extra"], 0.0)

    def test_persistent_failures_stop_when_no_resumes_left(self):
        s = self._shared(max_resumes=0)          # no pause budget → hard stop
        stop = False
        for _ in range(12):
            stop = fc._note_seat_failure(s)
        self.assertTrue(stop)
        self.assertTrue(s["stop"].is_set())

    def test_throttle_pauses_then_resumes_before_stopping(self):
        s = self._shared(max_resumes=2)
        # first sustained stall → pause #1 (not a stop), counter reset
        stop = False
        for _ in range(12):
            stop = fc._note_seat_failure(s)
        self.assertFalse(stop)
        self.assertFalse(s["stop"].is_set())
        self.assertEqual(s["resume_count"], 1)
        self.assertGreater(s["paused_until"], time.monotonic())
        self.assertEqual(s["consec_fail"], 0)
        # simulate the pause window elapsing, then stall again → pause #2
        s["paused_until"] = 0.0
        for _ in range(12):
            stop = fc._note_seat_failure(s)
        self.assertFalse(stop)
        self.assertEqual(s["resume_count"], 2)
        # third stall: resume budget exhausted → stop
        s["paused_until"] = 0.0
        for _ in range(12):
            stop = fc._note_seat_failure(s)
        self.assertTrue(stop)
        self.assertTrue(s["stop"].is_set())

    def test_no_pause_when_it_would_overrun_the_deadline(self):
        # plenty of resume budget, but the pause wouldn't fit before the deadline
        s = self._shared(max_resumes=5, pause_sec=600.0, deadline=time.monotonic() + 1)
        stop = False
        for _ in range(12):
            stop = fc._note_seat_failure(s)
        self.assertTrue(stop)
        self.assertEqual(s["resume_count"], 0)

    def test_backoff_is_capped(self):
        s = self._shared(backoff_after=1, stop_after=1000, backoff_step=10.0, backoff_max=25.0)
        for _ in range(10):
            fc._note_seat_failure(s)
        self.assertLessEqual(s["backoff_extra"], 25.0)


class ShardingAndMergeTests(unittest.TestCase):
    def test_shards_are_disjoint_and_cover_the_whole_pool(self):
        pool = [{"slug": f"t{i}"} for i in range(320)]
        N = 8
        shards = [fc.shard_theatres(pool, i, N) for i in range(N)]
        seen = [t["slug"] for s in shards for t in s]
        self.assertEqual(sorted(seen), sorted(t["slug"] for t in pool))  # complete
        self.assertEqual(len(seen), len(set(seen)))                      # disjoint
        sizes = [len(s) for s in shards]
        self.assertLessEqual(max(sizes) - min(sizes), 1)                 # balanced

    def test_no_sharding_returns_whole_pool(self):
        pool = [{"slug": f"t{i}"} for i in range(10)]
        self.assertEqual(fc.shard_theatres(pool, 0, 0), pool)
        self.assertEqual(fc.shard_theatres(pool, 0, 1), pool)


if __name__ == "__main__":
    unittest.main()


class RobustSlugMatchTest(unittest.TestCase):
    def test_roman_numeral_variant_matches(self):
        # tracked 'Mortal Kombat 2' must match a fandango 'mortal-kombat-ii' slug
        targets = {fc.slugify_title("Mortal Kombat 2"): "Mortal Kombat 2"}
        self.assertEqual(
            fc.match_target_title("/mortal-kombat-ii-2026-241111/movie-overview", targets),
            "Mortal Kombat 2")

    def test_number_word_variant_matches(self):
        targets = {fc.slugify_title("Scream Seven"): "Scream Seven"}
        self.assertEqual(
            fc.match_target_title("/scream-7-2026-241112/movie-overview", targets),
            "Scream Seven")

    def test_different_films_do_not_cross_match(self):
        # exact-first + token equality: 'toy-story' never swallows 'toy-story-5'
        targets = {fc.slugify_title("Toy Story 5"): "Toy Story 5"}
        self.assertIsNone(
            fc.match_target_title("/toy-story-2026-241113/movie-overview", targets))

    def test_near_miss_is_logged_not_matched(self):
        import io, contextlib
        fc._NEAR_MISS_LOGGED.clear()
        targets = {fc.slugify_title("Moana (2026)"): "Moana (2026)"}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            got = fc.match_target_title("/moana-2-2027-241114/movie-overview", targets)
        self.assertIsNone(got)                      # not silently matched
        self.assertIn("NEAR-MISS", buf.getvalue())  # but LOUD in run logs


class NearestOrderTest(unittest.TestCase):
    def test_nearest_order_picks_soonest_showtime(self):
        def href(sd):
            q = sd.replace(" ", "+").replace(":", "%3A")
            return f"https://tickets.fandango.com/transaction/ticketing/mobile/jump.aspx?sdate={q}&mid=1"
        TS5 = "/toy-story-5-2026-243393/movie-overview"
        entries = [
            {"movieOverview": TS5, "href": href("2026-06-20 19:30")},   # prime, 11.5h out
            {"movieOverview": TS5, "href": href("2026-06-20 11:00")},   # matinee, 3h out
        ]
        targets = {fc.slugify_title("Toy Story 5"): "Toy Story 5"}
        window = {"2026-06-20"}
        now = datetime(2026, 6, 20, 8, 0, tzinfo=timezone.utc)
        # prime order (default): the 19:30 show wins the cap
        prime = fc.select_wanted_showtimes(entries, targets, window, "UTC", now, cap=1)
        self.assertEqual(prime[0]["sdate"], "2026-06-20 19:30")
        # nearest order (afternoon near-showtime slots): the 3h-out matinee wins
        near = fc.select_wanted_showtimes(entries, targets, window, "UTC", now,
                                          cap=1, order="nearest")
        self.assertEqual(near[0]["sdate"], "2026-06-20 11:00")
        # discovered count attached either way (volume signal for cross-chain)
        self.assertEqual(near[0]["discovered"], 2)


class LiveTitleFallbackTests(unittest.TestCase):
    """When Phase-1 state has no titles, discover them live by Polymarket.

    2026-08-21: markets listed late, Tue-Thu Phase 1 skipped, showtime-links
    stayed on the prior weekend, and every Thursday/Friday Fandango slot said
    "No tracked titles" on a green run — the weekend's first two days of
    Regal/Cinemark capture (incl. the preview-day volume q) were lost. The
    collector discovers showtimes by TITLE, so links were never required.
    """

    def test_fallback_present_and_ordered_after_state(self):
        src = open(Path(__file__).resolve().parents[1] / "fandango_collect.py").read()
        i_state = src.index("tracked_movie_titles_from_state(weekend_of)")
        i_live = src.index("live Polymarket discovery", i_state)
        i_giveup = src.index("No tracked titles for weekend_of=", i_live)
        self.assertTrue(i_state < i_live < i_giveup,
                        "fallback must sit between state lookup and the give-up")

    def test_fallback_failure_cannot_crash_collection(self):
        src = open(Path(__file__).resolve().parents[1] / "fandango_collect.py").read()
        i = src.index("Fandango title fallback")
        block = src[i - 600:i + 900]
        self.assertIn("except Exception", block)
