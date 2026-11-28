import csv
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import alamo_collect as A  # noqa: E402
import fandango_collect as F  # noqa: E402


def _seat(status, price=1500):
    return {"seatStatus": status, "defaultPriceInCents": price}


SEATING = {"areas": [{"rows": [{"seats": [_seat("SOLD"), _seat("SOLD", -1), _seat("EMPTY"), _seat("NONE"), _seat("BROKEN")]}]}]}
SCHEDULE = {
    "market": [{"cinemas": [{"id": "0007", "name": "Lakeline", "city": "Austin", "timeZoneName": "America/Chicago"}]}],
    "presentations": [{"slug": "primetime", "show": {"title": "Primetime"}},
                      {"slug": "other", "show": {"title": "Other Film"}}],
    "sessions": [
        {"cinemaId": "0007", "sessionId": "1", "presentationSlug": "primetime", "businessDateClt": "2026-09-26",
         "showTimeClt": "2026-09-26T19:00:00", "showTimeUtc": "2026-09-27T00:00:00", "reservedSeating": True,
         "cinemaTimeZoneName": "America/Chicago", "screenNumber": "7", "formatSlug": "2d-digital"},
        {"cinemaId": "0007", "sessionId": "2", "presentationSlug": "primetime", "businessDateClt": "2026-09-26",
         "showTimeClt": "2026-09-26T12:00:00", "showTimeUtc": "2026-09-26T17:00:00", "reservedSeating": True},
        {"cinemaId": "0007", "sessionId": "3", "presentationSlug": "other", "businessDateClt": "2026-09-26",
         "showTimeClt": "2026-09-26T19:00:00", "showTimeUtc": "2026-09-27T00:00:00", "reservedSeating": True},
        {"cinemaId": "0007", "sessionId": "4", "presentationSlug": "primetime", "businessDateClt": "2026-10-03",
         "showTimeClt": "2026-10-03T19:00:00", "showTimeUtc": "2026-10-04T00:00:00", "reservedSeating": True},
    ],
}
NOW = datetime(2026, 9, 26, 20, 0, tzinfo=timezone.utc)


class AlamoLaneTest(unittest.TestCase):
    def test_seat_counts_skip_aisles_and_broken_and_bad_prices(self):
        c = A.seat_counts(SEATING)
        self.assertEqual({"total": 3, "sold": 2, "available": 1, "broken": 1, "price_cents": 1500}, c)

    def test_pre_selects_upcoming_tracked_in_window_only(self):
        picks = A.select_sessions(SCHEDULE, {"primetime": "Primetime"}, A.window_dates("2026-09-25"), NOW, "pre")
        self.assertEqual(["1"], [s["sessionId"] for s, _, _ in picks])      # 2 started, 3 untracked, 4 next week

    def test_rows_keep_zero_counts_and_post_rows_are_tagged(self):
        s, cinema, title = A.select_sessions(SCHEDULE, {"primetime": "Primetime"}, A.window_dates("2026-09-25"), NOW)[0]
        zero = {"total": 100, "sold": 0, "available": 100, "broken": 0, "price_cents": None}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "a.csv"
            pre = A.build_row(s, cinema, title, zero, "2026-09-25", "r1", NOW)
            post = A.build_row(s, cinema, title, zero, "2026-09-25", "r2", NOW.replace(hour=23), post=True)
            F.append_unique_fandango_rows([pre, post], csv_path=path)
            rows = list(csv.DictReader(open(path)))
            self.assertEqual(["0", "0"], [r["reserved_seats"] for r in rows])       # 0 is not blanked
            self.assertEqual(["0.0", "0.0"], [r["occupancy_pct"] for r in rows])
            self.assertEqual(["alamo-api", "post-show-census"], [r["row_kind"] for r in rows])
            self.assertEqual("ALMO", rows[0]["chain"])
            self.assertEqual("Alamo Drafthouse Lakeline", rows[0]["theatre_name"])

    def test_post_pass_revisits_stored_sessions_that_just_started(self):
        s, cinema, title = A.select_sessions(SCHEDULE, {"primetime": "Primetime"}, A.window_dates("2026-09-25"), NOW)[0]
        counts = {"total": 10, "sold": 5, "available": 5, "broken": 0, "price_cents": None}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "a.csv"
            F.append_unique_fandango_rows([A.build_row(s, cinema, title, counts, "2026-09-25", "r", NOW)], csv_path=path)
            at = datetime(2026, 9, 27, 0, 30, tzinfo=timezone.utc)                  # 30 min after the 19:00 CT start
            got = A.stored_post_sessions("2026-09-25", at, path=path)
            self.assertEqual(["1"], [x[0]["sessionId"] for x in got])
            self.assertEqual([], A.stored_post_sessions("2026-09-25", datetime(2026, 9, 26, 23, 0, tzinfo=timezone.utc), path=path))  # not started
            self.assertEqual([], A.stored_post_sessions("2026-09-25", datetime(2026, 9, 27, 3, 0, tzinfo=timezone.utc), path=path))   # window passed
            # 2026-11-19: the same clock time one day EARLIER is not "just started"
            day_before = datetime(2026, 9, 26, 0, 30, tzinfo=timezone.utc)
            self.assertEqual([], A.stored_post_sessions("2026-09-25", day_before, path=path))

    def test_after_midnight_show_starts_on_the_next_calendar_date(self):
        row = {"weekend_of": "2026-11-20", "row_kind": "alamo-api", "showtime_id": "0801:9",
               "timezone": "America/Chicago", "show_date": "2026-11-21", "showtime": "00:00",
               "theatre_name": "Alamo Drafthouse Lake Highlands", "theatre_city": "Dallas",
               "movie_title": "Film", "auditorium_name": "Screen 1", "auditorium_type": "x"}
        import io
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=list(row)); w.writeheader(); w.writerow(row)
        missing = Path("/nonexistent/a.csv")
        real = datetime(2026, 11, 22, 6, 10, tzinfo=timezone.utc)       # 10 min after Sunday 00:00 CST
        self.assertEqual(1, len(A.stored_post_sessions("2026-11-20", real, path=missing, extra_text=buf.getvalue())))
        listed = datetime(2026, 11, 21, 6, 10, tzinfo=timezone.utc)     # 10 min after the LISTED date's midnight
        self.assertEqual([], A.stored_post_sessions("2026-11-20", listed, path=missing, extra_text=buf.getvalue()))

    def test_loop_pass_also_reads_sessions_from_origin_main_copy(self):
        """2026-10-31: the 15:10Z loop's checkout predated the holdover pre rows
        on main, so it found no session for 5.5 h. The main copy is merged in,
        deduped by session id, and a missing copy changes nothing."""
        s, cinema, title = A.select_sessions(SCHEDULE, {"primetime": "Primetime"}, A.window_dates("2026-09-25"), NOW)[0]
        counts = {"total": 10, "sold": 5, "available": 5, "broken": 0, "price_cents": None}
        at = datetime(2026, 9, 27, 0, 30, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as td:
            on_main = Path(td) / "main.csv"
            F.append_unique_fandango_rows([A.build_row(s, cinema, title, counts, "2026-09-25", "r", NOW)], csv_path=on_main)
            text = on_main.read_text()
            missing = Path(td) / "checkout.csv"                       # loop checkout: no pre rows at all
            got = A.stored_post_sessions("2026-09-25", at, path=missing, extra_text=text)
            self.assertEqual(["1"], [x[0]["sessionId"] for x in got])
            got = A.stored_post_sessions("2026-09-25", at, path=on_main, extra_text=text)   # same rows twice
            self.assertEqual(["1"], [x[0]["sessionId"] for x in got])
            self.assertEqual([], A.stored_post_sessions("2026-09-25", at, path=missing, extra_text=None))


if __name__ == "__main__":
    unittest.main()


class AlamoBudgetTest(unittest.TestCase):
    def test_slow_pass_stops_at_budget_and_still_writes_rows(self):
        # 2026-10-21 12:40Z: slow seat reads ran past the 30-min step timeout and
        # the pass was killed with nothing written. Past the budget, write what we have.
        from unittest import mock
        sessions = [dict(SCHEDULE["sessions"][0], sessionId=str(i)) for i in range(1, 6)]
        sched = dict(SCHEDULE, sessions=sessions)
        clock = [0.0]

        def fake_get(path, timeout=30):
            if path.startswith("/v1/page/cclamp"):
                return {"data": {"marketSummaries": [{"slug": "austin"}]}}
            if path.startswith("/v2/schedule/market/"):
                return {"data": sched}
            clock[0] += 600                                   # each seat read takes 10 min
            return {"data": {"seatingData": SEATING}}

        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(A, "_get", fake_get), \
                mock.patch.object(A, "ALAMO_CSV", Path(td) / "a.csv"), \
                mock.patch.object(A, "ALAMO_SLEEP_SEC", 0), \
                mock.patch.object(A, "ALAMO_BUDGET_MIN", 25), \
                mock.patch.object(A.time, "monotonic", lambda: clock[0]):
            t = A.collect(weekend_of="2026-09-25", titles=["Primetime"], now_utc=NOW)
            rows = list(csv.DictReader(open(Path(td) / "a.csv")))
        self.assertEqual(5, t["matched"])
        self.assertEqual(3, t["captured"])                    # reads at 0, 10, 20 min; 30 > 25 stops
        self.assertEqual(2, t["budget_skipped"])
        self.assertEqual(3, len(rows))


class AlamoResumeTest(unittest.TestCase):
    """2026-11-28 12:40Z: three attempts read 1,260, 924 and 1,397 of 1,785
    showings, each from zero and in a fresh random order, and each failed on
    its own skips. A retry now reads what the cut pass left before anything
    else, and the slot is judged on what no attempt has read."""

    def _attempt(self, td, now, fail=(), n=10, step_sec=300):
        from unittest import mock
        sessions = [dict(SCHEDULE["sessions"][0], sessionId=str(i)) for i in range(1, n + 1)]
        sched = dict(SCHEDULE, sessions=sessions)
        clock, asked = [0.0], []

        def fake_get(path, timeout=30):
            if path.startswith("/v1/page/cclamp"):
                return {"data": {"marketSummaries": [{"slug": "austin"}]}}
            if path.startswith("/v2/schedule/market/"):
                return {"data": sched}
            sid = path.rsplit("/", 1)[1]
            asked.append(sid)
            clock[0] += step_sec
            if sid in fail:
                raise TimeoutError("timed out")
            return {"data": {"seatingData": SEATING}}

        with mock.patch.object(A, "_get", fake_get), \
                mock.patch.object(A, "ALAMO_CSV", Path(td) / "a.csv"), \
                mock.patch.object(A, "ALAMO_SLEEP_SEC", 0), \
                mock.patch.object(A, "ALAMO_BUDGET_MIN", 25), \
                mock.patch.object(A.time, "monotonic", lambda: clock[0]):
            t = A.collect(weekend_of="2026-09-25", titles=["Primetime"], now_utc=now)
        return t, asked

    def _main(self, totals):
        from unittest import mock
        with mock.patch.object(A, "collect", return_value=totals), mock.patch.dict(os.environ, {"ALAMO_MODE": ""}), \
                mock.patch.object(A, "ALAMO_LOOP_MIN", 0):
            return A.main()

    def _progress(self, td):
        import json
        return json.load(open(Path(td) / A.ALAMO_PROGRESS_NAME))

    def test_retry_reads_the_unread_showings_first_and_turns_the_slot_green(self):
        from datetime import timedelta
        with tempfile.TemporaryDirectory() as td:
            t1, asked1 = self._attempt(td, NOW)
            self.assertEqual((10, 6, 4, 4), (t1["matched"], t1["captured"], t1["budget_skipped"], t1["budget_unread"]))
            self.assertEqual(1, self._main(t1))                       # 4 of 10 unread: retry the slot
            left = {str(i) for i in range(1, 11)} - set(asked1)
            self.assertEqual({f"0007:{s}" for s in asked1}, set(self._progress(td)["read"]))

            t2, asked2 = self._attempt(td, NOW + timedelta(minutes=30))
            self.assertEqual(left, set(asked2[:4]))                   # the cut pass's tail goes first
            self.assertEqual((4, 0), (t2["budget_skipped"], t2["budget_unread"]))
            self.assertEqual(0, self._main(t2))                       # every showing read within the slot
            progress = self._progress(td)
            self.assertEqual(10, len(progress["read"]))
            self.assertEqual(NOW.isoformat(), progress["started"])   # the window runs from the first attempt

    def test_a_retry_that_still_leaves_too_much_unread_stays_red(self):
        from datetime import timedelta
        with tempfile.TemporaryDirectory() as td:
            t1, asked1 = self._attempt(td, NOW, n=20)
            t2, asked2 = self._attempt(td, NOW + timedelta(minutes=30), n=20)
            self.assertFalse(set(asked1) & set(asked2))               # nothing re-read while unread remain
            self.assertEqual((14, 8), (t2["budget_skipped"], t2["budget_unread"]))
            self.assertEqual(1, self._main(t2))                       # 8 of 20 still unread by any attempt
            t3, _ = self._attempt(td, NOW + timedelta(minutes=60), n=20)
            self.assertEqual(2, t3["budget_unread"])
            self.assertEqual(0, self._main(t3))                       # 2 of 20 is under the 20% floor

    def test_failed_reads_are_not_recorded_as_read(self):
        from datetime import timedelta
        odd = {str(i) for i in range(1, 11, 2)}
        with tempfile.TemporaryDirectory() as td:
            t1, asked1 = self._attempt(td, NOW, fail=odd)
            good = {s for s in asked1 if s not in odd}
            self.assertEqual(6 - len(good), t1["errors"])
            self.assertEqual({f"0007:{s}" for s in good}, set(self._progress(td)["read"]))
            _, asked2 = self._attempt(td, NOW + timedelta(minutes=30))
            self.assertFalse(set(asked2[:min(6, 10 - len(good))]) & good)   # timed-out showings are retried first

    def test_progress_from_an_earlier_slot_or_another_weekend_is_ignored(self):
        from datetime import timedelta
        with tempfile.TemporaryDirectory() as td:
            self._attempt(td, NOW)
            later = NOW + timedelta(minutes=A.ALAMO_RESUME_WINDOW_MIN + 1)        # the next slot is 4 h on
            self.assertEqual((None, set()), A.load_progress("2026-09-25", later, Path(td) / A.ALAMO_PROGRESS_NAME))
            self.assertEqual((None, set()), A.load_progress("2026-10-02", NOW, Path(td) / A.ALAMO_PROGRESS_NAME))
            self.assertEqual((None, set()), A.load_progress("2026-09-25", NOW - timedelta(minutes=1),
                                                            Path(td) / A.ALAMO_PROGRESS_NAME))
            t, _ = self._attempt(td, later)
            self.assertEqual((4, 4), (t["budget_skipped"], t["budget_unread"]))   # judged as a first attempt
            self.assertEqual(later.isoformat(), self._progress(td)["started"])
            for junk in ("", "[]", '{"weekend_of": "2026-09-25", "started": "soon", "read": []}',
                         '{"weekend_of": "2026-09-25", "started": "%s"}' % NOW.isoformat()):
                (Path(td) / A.ALAMO_PROGRESS_NAME).write_text(junk)
                self.assertEqual((None, set()), A.load_progress("2026-09-25", NOW, Path(td) / A.ALAMO_PROGRESS_NAME))

    def test_a_pass_that_finishes_leaves_nothing_to_resume(self):
        from datetime import timedelta
        with tempfile.TemporaryDirectory() as td:
            t, _ = self._attempt(td, NOW, step_sec=1)
            self.assertEqual((10, 0), (t["captured"], t["budget_skipped"]))
            self.assertFalse((Path(td) / A.ALAMO_PROGRESS_NAME).exists())         # no file churn on a normal pass
            self._attempt(td, NOW)                                                # cut
            t, _ = self._attempt(td, NOW + timedelta(minutes=30), step_sec=1)     # retry reads all ten
            self.assertEqual((10, 0), (t["captured"], t["budget_skipped"]))
            self.assertEqual([], self._progress(td)["read"])

    def test_first_attempt_order_is_still_shuffled_and_post_mode_is_untouched(self):
        import random
        picks = [({"cinemaId": "0007", "sessionId": str(i)}, {}, "Primetime") for i in range(50)]
        first = [p[0]["sessionId"] for p in A.order_for_resume(list(picks), set(), random.Random(1))]
        self.assertNotEqual([str(i) for i in range(50)], first)
        self.assertEqual(sorted(first, key=int), [str(i) for i in range(50)])
        read = {f"0007:{i}" for i in range(0, 50, 2)}
        again = [p[0]["sessionId"] for p in A.order_for_resume(list(picks), read, random.Random(2))]
        self.assertTrue(all(int(s) % 2 for s in again[:25]))                      # unread half first
        self.assertNotEqual(sorted(again[:25], key=int), again[:25])              # and still shuffled

    def test_the_11_28_third_attempt_would_have_passed(self):
        # 388 skipped at the budget; attempts 1 and 2 had read 1,260 and 924 of the 1,785.
        self.assertEqual(1, self._main({"markets": 22, "matched": 1785, "captured": 1373, "budget_skipped": 388}))
        self.assertEqual(0, self._main({"markets": 22, "matched": 1785, "captured": 1373, "budget_skipped": 388,
                                        "budget_unread": 0}))
        self.assertEqual(1, self._main({"markets": 22, "matched": 1785, "captured": 903, "budget_skipped": 861,
                                        "budget_unread": 400}))

    def test_the_commit_step_carries_the_progress_file(self):
        workflow = (Path(__file__).resolve().parents[2] / ".github/workflows/box-office-pipeline.yml").read_text()
        line = next(l for l in workflow.splitlines() if "commit_lane.sh alamo " in l)
        self.assertTrue(line.rstrip().endswith(f"box-office-tracker/data/{A.ALAMO_PROGRESS_NAME}"), line)
        self.assertEqual(A.ALAMO_CSV.parent / A.ALAMO_PROGRESS_NAME, A.progress_path())
