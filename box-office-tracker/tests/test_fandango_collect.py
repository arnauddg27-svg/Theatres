import csv
import sys
import tempfile
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
        self.assertEqual(
            fc.slugify_title("Star Wars: The Mandalorian & Grogu"),
            "star-wars-the-mandalorian-grogu",
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

    def test_header_written_to_target_path(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "sub" / "fandango.csv"
            fc.append_unique_fandango_rows([_row()], csv_path=path)
            with open(path) as f:
                header = f.readline().strip().split(",")
            self.assertEqual(header, fc.FANDANGO_PRE_RESERVATION_FIELDS)


if __name__ == "__main__":
    unittest.main()
