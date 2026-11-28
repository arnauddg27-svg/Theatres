"""Friday from the film's own pre-sales pace (chain_pace.py)."""
import math
import os
import sys
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chain_pace as CP  # noqa: E402


def _row(show_date, sid, seats, stamp, kind="", movie="Film A", theatre="T1"):
    return {"show_date": show_date, "showtime_id": sid, "reserved_seats": str(seats), "snapshot_time": stamp,
            "row_kind": kind, "movie_title": movie, "theatre_name": theatre}


def test_build_takes_friday_presales_and_thursday_finals_at_the_cutoff():
    rows = [
        _row("2026-12-04", "f1", 40, "2026-12-03T20:00:00Z"),
        _row("2026-12-04", "f1", 55, "2026-12-04T09:00:00Z"),            # the later read before the cutoff wins
        _row("2026-12-04", "f1", 90, "2026-12-04T12:00:00Z"),            # after Friday 10:00Z: not seen
        _row("2026-12-04", "f2", 70, "2026-12-04T08:00:00Z", kind="post-show-census"),   # never a pre-sale read
        _row("2026-12-03", "t1", 30, "2026-12-03T22:00:00Z"),
        _row("2026-12-03", "t1", 80, "2026-12-04T02:00:00Z", kind="post-show-census"),
        _row("2026-12-03", "t1", 35, "2026-12-04T03:00:00Z"),            # a later pre row does not beat the count
        _row("2026-12-05", "s1", 99, "2026-12-04T08:00:00Z"),            # Saturday: not part of the pace
    ]
    built = CP.build("2026-12-04", lane_rows=lambda chain, weekend: rows if chain == "HARK" else [])
    assert built == {("Film A", "HARK"): {"fri_pre": 55.0, "fri_pre_n": 1.0, "thu_final": 80.0, "thu_n": 1.0}}


def test_update_table_waits_for_the_cutoff_and_writes_once(tmp_path):
    rows = [_row("2026-12-04", "f1", 55, "2026-12-04T09:00:00Z"), _row("2026-12-03", "t1", 80, "2026-12-04T02:00:00Z")]
    lanes = lambda chain, weekend: rows if chain == "ALMO" else []
    table = str(tmp_path / "pace.csv")
    early = datetime(2026, 12, 4, 9, 59, tzinfo=timezone.utc)
    late = datetime(2026, 12, 4, 15, 0, tzinfo=timezone.utc)
    assert CP.update_table("2026-12-04", now=early, path=table, lane_rows=lanes) == 0
    assert CP.update_table("2026-12-04", now=late, path=table, lane_rows=lanes) == 1
    assert CP.update_table("2026-12-04", now=late, path=table, lane_rows=lanes) == 0
    assert CP.load_table(table)[0]["fri_pre"] == "55"


def _history():
    table, reported, openers = [], {}, set()
    for i in range(6):                         # earlier openings: Friday / previews = 1.5 x pace
        w, movie, p = f"2026-10-{2 + 7 * (i % 4):02d}", f"Film {i}", 1.0 + 0.2 * i
        table.append({"weekend_of": w, "movie": movie, "chain": "HARK", "fri_pre": str(1000 * p),
                      "fri_pre_n": "40", "thu_final": "1000", "thu_n": "20"})
        reported[(w, CP.movie_key(movie))] = {"Thursday": 2.0, "Friday": 2.0 * 1.5 * p}
        openers.add((w, CP.movie_key(movie)))
    table.append({"weekend_of": "2026-12-04", "movie": "Film A", "chain": "HARK", "fri_pre": "3000",
                  "fri_pre_n": "50", "thu_final": "1500", "thu_n": "25"})
    return table, reported, openers


def test_friday_estimate_applies_the_earlier_openings_multiple():
    table, reported, openers = _history()
    est = CP.friday_estimate("Film A", "2026-12-04", 3.0, table, reported, openers)
    assert est["chains"] == "HARK" and est["n_train"] == 6
    assert est["friday_m"] == pytest.approx(3.0 * 2.0 * 1.5)          # previews x pace 2.0 x k 1.5


def test_holdovers_and_thin_reads_do_not_train_or_estimate():
    table, reported, openers = _history()
    assert CP.friday_estimate("Film A", "2026-12-04", 3.0, table, reported, set()) is None      # no graded opener
    assert CP.friday_estimate("Film A", "2026-12-04", 0, table, reported, openers) is None      # no previews
    table[-1]["fri_pre_n"] = "3"
    assert CP.friday_estimate("Film A", "2026-12-04", 3.0, table, reported, openers) is None
    assert CP.pace({"fri_pre": "150", "fri_pre_n": "40", "thu_final": "1000", "thu_n": "20"}) is None
    assert math.isclose(CP.pace({"fri_pre": "500", "fri_pre_n": "40", "thu_final": "1000", "thu_n": "20"}), 0.5)
