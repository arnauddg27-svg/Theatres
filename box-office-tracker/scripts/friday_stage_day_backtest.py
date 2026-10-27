#!/usr/bin/env python3
"""Per-DAY companion to friday_stage_backtest.py: replay each film as of the
end of its opening Friday and grade Friday / Saturday / Sunday separately
against calibration.json's daily_actuals, plus the weekend headline.

Why: the weekend headline can look unbiased while its days cancel — on the
2026-09-25..10-16 films the recorded Friday day ran -13% (8 of 9 under) and
Sat/Sun ran high. A lever that lifts Friday is only right if Sat/Sun do not
follow it up. Read-only. SINCE=YYYY-MM-DD limits the replay (default all).

    SINCE=2026-09-25 python3 scripts/friday_stage_day_backtest.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402
import chain_census as _CC  # noqa: E402


DAYS = ["Friday", "Saturday", "Sunday"]


def main():
    since = os.environ.get("SINCE") or ""
    # THROUGH_OFFSET=1 replays as of the end of SATURDAY (after-saturday stage).
    offset = int(os.environ.get("THROUGH_OFFSET") or 0)
    from datetime import datetime, timedelta
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    load_md = getattr(P, "load_movie_metadata", None)
    out = []
    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        da = h.get("daily_actuals") or {}
        if w < since or h.get("data_outage") or not all(da.get(d) for d in DAYS):
            continue
        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)
        except Exception:
            continue
        thru = (datetime.strptime(w, "%Y-%m-%d") + timedelta(days=offset)).strftime("%Y-%m-%d")
        seat_data = P.filter_seat_data_through(P.load_seat_data(weekend_of=w), thru)
        sd = P.movie_mapping_get(seat_data, movie, None)
        if not sd or w not in sd:
            continue
        P._CROSS_CHAIN_CACHE.clear()
        md = load_md() if load_md else None
        tc = P.load_theatre_counts()
        try:
            pred = P.predict_movie(
                movie, sd, P.movie_mapping_get(P.load_polymarket_data(weekend_of=w, through_date=thru), movie, []), cal,
                national_theatre_count=P.national_theatre_count_for_movie(movie, tc, metadata=md),
                snapshot_data=P.movie_mapping_get(P.load_pre_reservation_data(weekend_of=w, through_date=thru), movie, {}),
                social_data=P.load_social_signal_data(weekend_of=w, through_date=thru),
                daily_actual_overrides=P.load_daily_actual_overrides(weekend_of=w, through_date=thru),
                showtime_link_profiles=P.movie_mapping_get(P.load_showtime_link_daypart_profiles(weekend_of=w), movie, {}),
                cross_chain_data=P.load_cross_chain_occupancy(weekend_of=w, through_date=thru),
                census_daypart_data=P.load_census_daypart_seats(weekend_of=w, through_date=thru),
                chain_census_data=_CC.dollars_for(w, thru) if P.CHAIN_CENSUS_MODE == 'on' else None,
            )
        except Exception as e:
            print(f"{movie}: err {e}")
            continue
        if not pred:
            continue
        dp = P.daily_calibration_fields_from_prediction(pred)[0] or {}
        out.append((movie, w, actual, pred.get("regression_mid_m"), dp, da))

    print(f"{'movie':24} {'wknd':>6}  " + "".join(f"{d[:3]+' p/a':>14}" for d in DAYS) + f"{'weekend':>10}")
    errs = {d: [] for d in DAYS + ["weekend"]}
    for movie, w, actual, head, dp, da in out:
        cells = []
        for d in DAYS:
            if dp.get(d):
                r = dp[d] / da[d] - 1
                errs[d].append(r)
                cells.append(f"{dp[d]:5.1f}/{da[d]:<4.1f}{r:+4.0%}")
            else:
                cells.append(f"{'-':>14}")
        hr = head / actual - 1 if head else None
        if hr is not None:
            errs["weekend"].append(hr)
        print(f"{movie[:24]:24} {w[5:]:>6}  " + "".join(f"{c:>14}" for c in cells) + f"{(f'{hr:+.0%}' if hr is not None else '-'):>10}")
    import statistics as st
    print()
    for d, xs in errs.items():
        if xs:
            print(f"  {d:8} n={len(xs):2d}  median {st.median(xs):+5.1%}  mean {st.mean(xs):+5.1%}  "
                  f"MAE {st.mean(abs(x) for x in xs):5.1%}  under {sum(1 for x in xs if x < 0)}/{len(xs)}")


if __name__ == "__main__":
    main()
