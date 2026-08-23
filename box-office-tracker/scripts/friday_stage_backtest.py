#!/usr/bin/env python3
"""Friday-stage backtest: replay each historical film AS OF the end of its
opening Friday (Thursday+Friday seat data, snapshots/side inputs captured
through Friday, that weekend's frozen leak-free calibration) and grade the
HEADLINE — regression mid including the Friday-anchor blend — against the
actual.

WHY THIS EXISTS: every model change was validated at the Thursday stage only
(scripts/thursday_only_backtest.py). The in-weekend update path — the Friday
anchor, same-week calibration, drifting cross-chain shares — had NO gate, which
is how PAW Patrol's nowcast walked from +23% at Thursday to -36% recorded with
nothing measuring the deterioration. This harness makes in-weekend behaviour
testable the same way: run it before and after any change that touches
post-Thursday machinery.

Read-only; does not touch production data.

INTERPRETING THE SIGNED MEAN: the composite signed mean mixes eras. Films
replayed with immature freezes (<10 history entries, before the regression
tier had substance) carry a large under-bias that says nothing about the
current model; the mature-freeze cohort is the live-model read. A uniform
in-weekend debias multiplier was LOO-tested 2026-08-23 and REFUTED — it
worsened MAE fit on all films (20.0->22.7), fit on the mature era (->21.7),
and applied to mature films only (16.5->19.8); mature-era signed mean was
-5.2% +/- 5.7 SE, indistinguishable from zero. Do not retry a flat
multiplier; only a *conditional* lever with new evidence should be attempted.

Run:  python3 scripts/friday_stage_backtest.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402


def ape(est, actual):
    if est is None or not actual:
        return None
    return abs(est - actual) / actual * 100.0


def spe(est, actual):
    """Signed percentage error (negative = under-prediction)."""
    if est is None or not actual:
        return None
    return (est - actual) / actual * 100.0


def main():
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    load_md = getattr(P, "load_movie_metadata", None)

    rows = []
    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        friday = w   # weekend_of IS the opening Friday; data through Friday
        if h.get("data_outage"):
            rows.append((movie, w, actual, None, None, "outage-excluded", None))
            continue
        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)
        except Exception:
            rows.append((movie, w, actual, None, None, "no-freeze", None))
            continue
        freeze_n = len(cal.get("history", []) or [])

        seat_data = P.filter_seat_data_through(P.load_seat_data(weekend_of=w), friday)
        sd = P.movie_mapping_get(seat_data, movie, None)
        if not sd:
            rows.append((movie, w, actual, None, None, "no-seat-data", freeze_n))
            continue
        observed_days = sorted(sd.keys())
        if friday not in observed_days:
            # Friday's post-showtime fill arrives in the Saturday-morning
            # regular scrape; a film missing it can only be graded Thursday-stage.
            rows.append((movie, w, actual, None, None, "no-fri-seat", freeze_n))
            continue

        snap = P.load_pre_reservation_data(weekend_of=w, through_date=friday)
        poly = P.load_polymarket_data(weekend_of=w, through_date=friday)
        social = P.load_social_signal_data(weekend_of=w, through_date=friday)
        dao = P.load_daily_actual_overrides(weekend_of=w, through_date=friday)
        slp = P.load_showtime_link_daypart_profiles(weekend_of=w)
        P._CROSS_CHAIN_CACHE.clear()
        ccd = P.load_cross_chain_occupancy(weekend_of=w, through_date=friday)
        tc = P.load_theatre_counts()
        md = load_md() if load_md else None
        nat = P.national_theatre_count_for_movie(movie, tc, metadata=md)

        try:
            pred = P.predict_movie(
                movie, sd, P.movie_mapping_get(poly, movie, []), cal,
                national_theatre_count=nat,
                snapshot_data=P.movie_mapping_get(snap, movie, {}),
                social_data=social,
                daily_actual_overrides=dao,
                showtime_link_profiles=P.movie_mapping_get(slp, movie, {}),
                cross_chain_data=ccd,
            )
        except Exception as e:
            rows.append((movie, w, actual, None, None, f"err:{str(e)[:36]}", freeze_n))
            continue
        if not pred:
            rows.append((movie, w, actual, None, None, "no-pred", freeze_n))
            continue
        headline = pred.get("regression_mid_m")
        anchored = pred.get("friday_anchored_mid_m")
        rows.append((movie, w, actual, headline, anchored, "ok", freeze_n))

    MATURE_FREEZE_N = 10   # regression tier has substance from ~10 entries
    print(f"{'movie':26} {'actual':>7} {'headline':>9} {'FriAnch':>8} "
          f"{'APE':>7} {'signed':>8} {'frz_n':>5} note")
    apes, spes = [], []
    mature, early = [], []
    for movie, w, actual, headline, anchored, note, freeze_n in rows:
        a, s = ape(headline, actual), spe(headline, actual)
        print(f"{movie[:26]:26} {actual:>7.1f} "
              f"{(f'{headline:.1f}' if headline is not None else '-'):>9} "
              f"{(f'{anchored:.1f}' if anchored is not None else '-'):>8} "
              f"{(f'{a:.0f}%' if a is not None else '-'):>7} "
              f"{(f'{s:+.0f}%' if s is not None else '-'):>8} "
              f"{(str(freeze_n) if freeze_n is not None else '-'):>5} {note}")
        if a is not None:
            apes.append(a)
            spes.append(s)
            (mature if (freeze_n or 0) >= MATURE_FREEZE_N else early).append((a, s))

    def mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")
    def median(xs):
        srt = sorted(xs); n = len(srt)
        return float("nan") if not n else (srt[n // 2] if n % 2 else (srt[n // 2 - 1] + srt[n // 2]) / 2)

    print(f"\n=== Friday-stage headline accuracy (n={len(apes)}) ===")
    print(f"  MAE {mean(apes):.1f}%   median {median(apes):.1f}%   "
          f"signed mean {mean(spes):+.1f}% (negative = under-prediction)")
    if mature and early:
        ma, ms = [x[0] for x in mature], [x[1] for x in mature]
        ea, es = [x[0] for x in early], [x[1] for x in early]
        print(f"  mature freezes (n>={MATURE_FREEZE_N} history, the live-model read): "
              f"n={len(ma)}  MAE {mean(ma):.1f}%  signed {mean(ms):+.1f}%")
        print(f"  immature freezes (early era, not the live model):        "
              f"n={len(ea)}  MAE {mean(ea):.1f}%  signed {mean(es):+.1f}%")
        print("  NOTE: the composite signed mean mixes eras — a flat debias was "
              "LOO-refuted 2026-08-23 (see module docstring).")


if __name__ == "__main__":
    main()
