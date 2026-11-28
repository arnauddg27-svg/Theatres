"""Pre-release estimate from the other chains' pre-sales (chain_presales.py)
and its place in the combined forecast."""
import csv
import math
import os
import sys
from datetime import datetime, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import chain_presales as CP  # noqa: E402
import ensemble_forecast as E  # noqa: E402

LANE_FIELDS = ["weekend_of", "run_id", "snapshot_time", "show_date", "theatre_name", "movie_title",
               "showtime_id", "total_seats", "reserved_seats", "chain", "discovered_showtimes", "row_kind"]


def _lane(tmp_path, chain, rows):
    path = tmp_path / (CP.LANES[chain][0] + ".csv")
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LANE_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(dict({"weekend_of": "2026-12-04", "movie_title": "Film A", "chain": chain,
                                  "total_seats": "100", "discovered_showtimes": "", "row_kind": ""}, **r))


def test_cutoffs_are_16_et_monday_to_thursday():
    assert CP.cutoff_time("2026-12-04", "thu") == datetime(2026, 12, 3, 21, 0, tzinfo=timezone.utc)
    assert CP.cutoff_at("2026-12-04", "2026-11-30T20:59:00Z") is None
    assert CP.cutoff_at("2026-12-04", "2026-11-30T21:00:00Z") == "mon"
    assert CP.cutoff_at("2026-12-04", "2026-12-03T12:00:00Z") == "wed"
    assert CP.cutoff_at("2026-12-04", "2026-12-05T12:00:00Z") == "thu"


def test_features_take_each_theatres_last_run_before_the_cutoff(tmp_path):
    _lane(tmp_path, "HARK", [
        # theatre 1: an early run and a later one; only the later counts at the Thursday cutoff
        {"run_id": "r1", "snapshot_time": "2026-12-01T10:00:00Z", "show_date": "2026-12-04", "theatre_name": "T1", "showtime_id": "a", "reserved_seats": "10"},
        {"run_id": "r2", "snapshot_time": "2026-12-03T10:00:00Z", "show_date": "2026-12-04", "theatre_name": "T1", "showtime_id": "a", "reserved_seats": "40"},
        {"run_id": "r2", "snapshot_time": "2026-12-03T10:00:00Z", "show_date": "2026-12-05", "theatre_name": "T1", "showtime_id": "b", "reserved_seats": "20"},
        # theatre 2: read after the cutoff -> not in the Thursday features
        {"run_id": "r3", "snapshot_time": "2026-12-03T22:00:00Z", "show_date": "2026-12-04", "theatre_name": "T2", "showtime_id": "c", "reserved_seats": "90"},
        # a Monday showing is outside the opening weekend
        {"run_id": "r2", "snapshot_time": "2026-12-03T10:00:00Z", "show_date": "2026-12-07", "theatre_name": "T1", "showtime_id": "d", "reserved_seats": "99"},
    ])
    feats = CP.lane_features("2026-12-04", ["tue", "thu"], data_dir=str(tmp_path))
    thu = feats[("filma", "HARK", "thu")]
    assert (thu["theatres"], thu["showings"], thu["reserved"], thu["res_per_theatre"]) == (1, 2, 60, 60.0)
    assert feats[("filma", "HARK", "tue")]["reserved"] == 10


def test_a_sampled_run_is_scaled_to_the_showings_the_theatre_listed(tmp_path):
    _lane(tmp_path, "CNMK", [
        {"run_id": "r1", "snapshot_time": "2026-12-03T10:00:00Z", "show_date": "2026-12-04", "theatre_name": "T1",
         "showtime_id": "a", "reserved_seats": "30", "discovered_showtimes": "6"},
    ])
    feat = CP.lane_features("2026-12-04", ["thu"], data_dir=str(tmp_path))[("filma", "CNMK", "thu")]
    assert feat["reserved"] == 30 and feat["scaled_reserved"] == 180


def test_amc_bridge_rows_in_the_fandango_file_are_not_regal(tmp_path):
    _lane(tmp_path, "REGL", [
        {"run_id": "r1", "snapshot_time": "2026-12-03T10:00:00Z", "show_date": "2026-12-04", "theatre_name": "AMC 1",
         "showtime_id": "a", "reserved_seats": "50", "chain": "AMC"},
    ])
    assert CP.lane_features("2026-12-04", ["thu"], data_dir=str(tmp_path)) == {}


def test_update_table_appends_each_passed_cutoff_once(tmp_path):
    _lane(tmp_path, "HARK", [
        {"run_id": "r1", "snapshot_time": "2026-11-30T10:00:00Z", "show_date": "2026-12-04", "theatre_name": "T1", "showtime_id": "a", "reserved_seats": "10"},
    ])
    table = str(tmp_path / "features.csv")
    now = datetime(2026, 12, 2, 12, 0, tzinfo=timezone.utc)          # Monday and Tuesday cutoffs passed
    assert CP.update_table("2026-12-04", now=now, national={"filma": 3000}, path=table, data_dir=str(tmp_path)) == 2
    assert CP.update_table("2026-12-04", now=now, national={"filma": 3000}, path=table, data_dir=str(tmp_path)) == 0
    rows = CP.load_table(table)
    assert {r["cutoff"] for r in rows} == {"mon", "tue"} and rows[0]["national_theatres"] == "3000"


def _table(target_rpt):
    rows = []
    for i in range(14):                       # earlier openings: opening = 0.01 x rpt x (national / 3000)
        rpt, national = 100.0 * (i + 2), 2500 + 100 * i
        actual = 0.01 * rpt * national / 3000
        for chain, noise in (("HARK", 1.0), ("CNMK", 1.6 if i % 2 else 0.6)):
            rows.append({"weekend_of": f"2026-0{1 + i // 4}-{10 + i:02d}", "movie": f"Film {i}", "chain": chain,
                         "cutoff": "thu", "theatres": "30", "res_per_theatre": str(rpt * noise),
                         "national_theatres": str(national), "_actual": actual})
    for chain in ("HARK", "CNMK"):
        rows.append({"weekend_of": "2026-12-04", "movie": "Film A", "chain": chain, "cutoff": "thu",
                     "theatres": "30", "res_per_theatre": str(target_rpt), "national_theatres": "3000"})
    actuals = {(r["weekend_of"], CP.movie_key(r["movie"])): r["_actual"] for r in rows if "_actual" in r}
    return rows, actuals


def test_estimate_recovers_the_relation_and_leans_on_the_tighter_chain():
    table, actuals = _table(1000.0)
    est = CP.estimate("Film A", "2026-12-04", "thu", table, actuals)
    assert est["chains"] == "CNMK+HARK" and est["n_train"] == 14
    assert est["mid_m"] == pytest.approx(10.0, rel=0.08)      # Harkins is exact, Cinemark is noisy
    assert CP.estimate("Film A", "2026-12-04", "wed", table, actuals) is None


def test_estimate_needs_enough_earlier_openings_and_theatres():
    table, actuals = _table(1000.0)
    assert CP.estimate("Film A", "2026-12-04", "thu", table[:12] + table[-2:], actuals) is None
    for r in table[-2:]:
        r["theatres"] = "3"
    assert CP.estimate("Film A", "2026-12-04", "thu", table, actuals) is None


def _pred(**kw):
    row = {"logged_at": "2026-12-03T22:00:00Z", "weekend_of": "2026-12-04", "movie": "Film A",
           "headline_mid_m": "30", "forecast_stage": "presales", "market_window_compatible": "1",
           "poly_implied_mid_m": ""}
    row.update(kw)
    return row


def _presales():
    table, actuals = _table(1000.0)
    return CP, table, actuals


def test_presale_estimate_is_logged_but_does_not_move_the_number():
    # 2026-11-28: tested, not adopted (walk-forward it made the mix worse).
    assert E.W_SEATS_WITH_MARKET == 0 and E.W_SEATS_WITH_TRADE == 0
    with_market = E.ensemble_row(_pred(poly_implied_mid_m="20"), [], presales=_presales())
    assert with_market["ensemble_source"] == "market" and with_market["ensemble_mid_m"] == 20.0
    assert with_market["seats_chains"] == "CNMK+HARK @thu" and float(with_market["seats_mid_m"]) > 0
    alone = E.ensemble_row(_pred(), [], presales=_presales())
    assert alone["ensemble_source"] == "model" and alone["ensemble_mid_m"] == 30.0


def test_a_positive_weight_mixes_the_presale_estimate_in_log_space(monkeypatch):
    monkeypatch.setattr(E, "W_SEATS_WITH_MARKET", 0.2)
    seats = CP.estimate("Film A", "2026-12-04", "thu", *_presales()[1:])["mid_m"]
    row = E.ensemble_row(_pred(poly_implied_mid_m="20"), [], presales=_presales())
    assert row["ensemble_source"] == "market+seats"
    assert row["ensemble_mid_m"] == pytest.approx(math.exp(0.2 * math.log(seats) + 0.8 * math.log(20)), abs=0.01)


def test_presale_estimate_stays_out_after_release_and_for_pre_friday_openers():
    played = E.ensemble_row(_pred(poly_implied_mid_m="20", forecast_stage="after-friday"), [], presales=_presales())
    assert played["seats_mid_m"] == "" and played["ensemble_source"] == "market+model"
    midweek = E.ensemble_row(_pred(market_window_compatible="0"), [], presales=_presales())
    assert midweek["seats_mid_m"] == ""
    early = E.ensemble_row(_pred(logged_at="2026-11-29T12:00:00Z"), [], presales=_presales())
    assert early["seats_mid_m"] == "" and early["ensemble_source"] == "model"
    late = E.ensemble_row(_pred(), [], presales=_presales())
    assert late["seats_mid_m"] != ""
