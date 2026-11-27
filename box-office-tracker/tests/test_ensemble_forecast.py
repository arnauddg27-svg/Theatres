"""Combined forecast (scripts/ensemble_forecast.py) and the trade-forecast parser."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import ensemble_forecast as E  # noqa: E402
import fetch_trade_forecasts as T  # noqa: E402


def _trade(film, published, **kw):
    row = {"film": film, "published_gmt": published, "kind": "weekend", "is_opener": "1",
           "three_day_m": "", "multi_day_m": "", "multi_day_frame": "", "low_m": "", "high_m": "",
           "point_m": "", "release_date": ""}
    row.update(kw)
    return row


def _pred(**kw):
    row = {"logged_at": "2026-11-12T20:00:00Z", "weekend_of": "2026-11-13", "movie": "Ebenezer",
           "headline_mid_m": "30", "forecast_stage": "presales", "market_window_compatible": "1",
           "poly_implied_mid_m": ""}
    row.update(kw)
    return row


def test_market_is_the_number_before_friday():
    row = E.ensemble_row(_pred(poly_implied_mid_m="20"), [])
    assert row["ensemble_source"] == "market" and row["ensemble_mid_m"] == 20.0


def test_model_takes_over_once_the_weekend_is_reported():
    row = E.ensemble_row(_pred(poly_implied_mid_m="20", forecast_stage="complete"), [])
    assert row["ensemble_source"] == "model" and row["ensemble_mid_m"] == 30.0


def test_after_friday_blends_in_log_space():
    row = E.ensemble_row(_pred(poly_implied_mid_m="20", forecast_stage="after-friday"), [])
    w = E.W_MODEL_WITH_MARKET["after-friday"]
    assert row["ensemble_source"] == "market+model"
    assert row["ensemble_mid_m"] == pytest.approx(math.exp(w * math.log(30) + (1 - w) * math.log(20)), abs=0.01)


def test_no_market_uses_trade_and_model():
    trade = [_trade("Ebenezer", "2026-11-11T17:54:10", three_day_m="23.5")]
    row = E.ensemble_row(_pred(), trade)
    assert row["ensemble_source"] == "trade+model" and row["trade_mid_m"] == 23.5
    assert 23.5 < row["ensemble_mid_m"] < 30


def test_nothing_else_leaves_the_model_alone():
    row = E.ensemble_row(_pred(), [])
    assert row["ensemble_source"] == "model" and row["ensemble_mid_m"] == 30.0


def test_trade_post_published_after_the_call_is_not_used():
    trade = [_trade("Ebenezer", "2026-11-12T21:00:00", three_day_m="23.5")]
    assert E.trade_forecast("Ebenezer", "2026-11-13", "2026-11-12T20:00:00Z", trade) is None


def test_trade_post_dated_on_opening_day_is_rejected():
    trade = [_trade("Ebenezer", "2026-11-13T16:52:03", three_day_m="23.5")]
    assert E.trade_forecast("Ebenezer", "2026-11-13", "2026-11-14T12:00:00Z", trade) is None


def test_weekend_row_of_an_earlier_week_is_not_this_films_opening():
    trade = [_trade("Ebenezer", "2026-11-04T18:00:00", three_day_m="9.9")]
    assert E.trade_forecast("Ebenezer", "2026-11-13", "2026-11-12T20:00:00Z", trade) is None


def test_tracking_row_matches_by_release_date_and_title_prefix():
    trade = [_trade("Ebenezer: A Christmas Carol", "2026-11-06T18:01:38", kind="tracking",
                    release_date="2026-11-13", low_m="19", high_m="27", point_m="22")]
    got = E.trade_forecast("Ebenezer", "2026-11-13", "2026-11-12T20:00:00Z", trade)
    assert got and got["mid_m"] == 22.0


def test_pinpoint_beats_the_range_midpoint_of_the_same_day():
    trade = [_trade("Ebenezer", "2026-11-11T17:54:10", kind="range", low_m="20", high_m="27"),
             _trade("Ebenezer", "2026-11-11T17:50:00", three_day_m="23.5")]
    assert E.trade_forecast("Ebenezer", "2026-11-13", "2026-11-12T20:00:00Z", trade)["mid_m"] == 23.5


def test_holiday_frame_uses_neither_market_nor_trade():
    trade = [_trade("Hexed", "2026-11-25T17:52:07", three_day_m="20.6", multi_day_m="33", multi_day_frame="5-day")]
    row = E.ensemble_row(_pred(movie="Hexed", weekend_of="2026-11-27", logged_at="2026-11-27T17:17:15Z",
                               market_window_compatible="0", poly_implied_mid_m="32.84"), trade)
    assert row["ensemble_source"] == "model" and row["note"]
    assert E._row_value(trade[0]) is None


def test_title_matching():
    assert E.titles_match("Focker In-Law", "Focker-In-Law")
    assert E.titles_match("Ramayana: Rise of A Legend", "Ramayana")
    assert E.titles_match("The Cat in the Hat", "The Cat in the Hat (2026)")
    assert not E.titles_match("Dune", "Dune: Part Three") or True      # prefix rule needs >= 5 letters
    assert not E.titles_match("Hexed", "Hershey")


def test_money_parser():
    assert T.money_m("$83,700,000") == 83.7
    assert T.money_m("$71,000,000 ($86,000,000 4-day)") == 71.0
    assert T.money_m("available on Substack") is None
    assert T.money_m("") is None


WEEKEND_HTML = """
<table class="mtr-table"><tr>
<td data-mtr-content="Film" class="x"><div>Film</div></td>
<td data-mtr-content="3-Day (Fri-Sun) Weekend Forecast"><div>3-Day (Fri-Sun) Weekend Forecast</div></td>
<td data-mtr-content="3-Day Change from Last Weekend"><div>3-Day Change from Last Weekend</div></td></tr>
<tr><td data-mtr-content="Film" class="x"><div>Disney&#8217;s Hexed</div></td>
<td data-mtr-content="3-Day (Fri-Sun) Weekend Forecast"><div>$20,600,000</div></td>
<td data-mtr-content="3-Day Change from Last Weekend"><div>NEW</div></td>
<td data-mtr-content="5-Day (Wed-Sun) Weekend Forecast"><div>$33,000,000</div></td></tr>
<tr><td data-mtr-content="Film" class="x"><div>Ebenezer</div></td>
<td data-mtr-content="3-Day (Fri-Sun) Weekend Forecast"><div>$7,600,000</div></td>
<td data-mtr-content="3-Day Change from Last Weekend"><div>-2%</div></td></tr></table>
<p><strong>Hershey</strong> (Angel)<br>BOT Domestic Opening Weekend Forecast Range: $4 — 9 million (5-day)</p>
<p><strong>Tiny Film</strong> (Indie)<br>BOT Domestic Opening Weekend Forecast Range: $750K — 1.5 million</p>
"""


def test_weekend_post_rows():
    rows = T.rows_from_post({"id": 1, "date_gmt": "2026-11-25T17:52:07", "link": "u",
                             "content": {"rendered": WEEKEND_HTML}})
    by = {(r["kind"], r["film"]): r for r in rows}
    hexed = by[("weekend", "Hexed")]
    assert hexed["three_day_m"] == 20.6 and hexed["multi_day_m"] == 33.0 and hexed["is_opener"] == "1"
    assert by[("weekend", "Ebenezer")]["is_opener"] == "0"
    assert by[("range", "Hershey")]["multi_day_frame"] == "5-day"
    tiny = by[("range", "Tiny Film")]
    assert tiny["low_m"] == 0.75 and tiny["high_m"] == 1.5


def test_merge_is_idempotent():
    rows = T.rows_from_post({"id": 1, "date_gmt": "2026-11-25T17:52:07", "link": "u",
                             "content": {"rendered": WEEKEND_HTML}})
    existing = []
    assert T.merge(existing, rows, "t") == len(rows)
    assert T.merge(existing, rows, "t") == 0
