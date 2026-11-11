#!/usr/bin/env python3
"""After-previews HEADLINE backtest: replay each historical film as of the end
of its opening Thursday (Thursday seats, snapshots and side inputs captured by
Thursday, that weekend's frozen leak-free calibration) and grade the served
headline — not the seat/snapshot candidates thursday_only_backtest.py compares.

Two questions (2026-11-10 audit):

  1. Snapshot coverage floor. stage_forecasting falls back to the one-day seat
     regression when model coverage is under the floor. Each film is graded
     with the floor at 0.50 and at the after-previews 0.30.
  2. Previews x class multiplier. Reported previews (calibration.json
     daily_actuals, i.e. what the daily table shows on opening Friday) blended
     geometrically into the headline at weights 0 / 0.3 / 0.5. The multiplier
     comes from the frozen calibration, so only earlier weekends inform it.

The chain census overlay is not passed (as in thursday_only_backtest.py), so
the numbers isolate the two questions. Read-only.

    SINCE=2026-09-25 python3 scripts/after_previews_headline_backtest.py
"""
import copy
import json
import os
import statistics
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402
import stage_forecasting as S  # noqa: E402

WEIGHTS = (0.0, 0.3, 0.4, 0.5)


def headline(pred, cal, floor, previews_m, weight):
    p = copy.deepcopy(pred)
    p["reported_previews_withheld_m"] = previews_m if weight > 0 else None
    old_floor = dict(S.MIN_SNAPSHOT_COVERAGE_BY_STAGE)
    old_weight = P.COMP_MULTIPLIER_PREVIEWS_WEIGHT
    try:
        S.MIN_SNAPSHOT_COVERAGE_BY_STAGE["after-previews"] = floor
        P.COMP_MULTIPLIER_PREVIEWS_WEIGHT = weight
        P.select_regression_prediction(p, cal)
    finally:
        S.MIN_SNAPSHOT_COVERAGE_BY_STAGE.clear()
        S.MIN_SNAPSHOT_COVERAGE_BY_STAGE.update(old_floor)
        P.COMP_MULTIPLIER_PREVIEWS_WEIGHT = old_weight
    return p.get("regression_mid_m"), p.get("regression_source")


def main():
    since = os.environ.get("SINCE") or ""
    until = os.environ.get("UNTIL") or ""
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    load_md = getattr(P, "load_movie_metadata", None)
    rows = []
    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        if (since and w < since) or (until and w > until):
            continue
        thu = (datetime.strptime(w, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        previews = (h.get("daily_actuals") or {}).get("Thursday")
        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)
        except Exception:
            continue
        sd = P.movie_mapping_get(P.filter_seat_data_through(P.load_seat_data(weekend_of=w), thu), movie, None)
        if not sd:
            continue
        snap = P.load_pre_reservation_data(weekend_of=w, through_date=thu)
        md = load_md() if load_md else None
        try:
            pred = P.predict_movie(
                movie, sd, P.movie_mapping_get(P.load_polymarket_data(weekend_of=w, through_date=thu), movie, []), cal,
                national_theatre_count=P.national_theatre_count_for_movie(movie, P.load_theatre_counts(), metadata=md),
                snapshot_data=P.movie_mapping_get(snap, movie, {}),
                social_data=P.load_social_signal_data(weekend_of=w, through_date=thu),
                daily_actual_overrides=P.load_daily_actual_overrides(weekend_of=w, through_date=thu),
                showtime_link_profiles=P.movie_mapping_get(P.load_showtime_link_daypart_profiles(weekend_of=w), movie, {}),
                cross_chain_data=P.load_cross_chain_occupancy(weekend_of=w, through_date=thu),
            )
        except Exception as exc:
            print(f"{movie}: replay failed ({type(exc).__name__}: {exc})")
            continue
        if not pred or S.forecast_stage(pred) != "after-previews":
            continue
        cov = pred.get("snapshot_model_coverage_ratio")
        out = {"movie": movie, "weekend": w, "actual": actual, "coverage": cov, "previews": previews}
        # Third arm (2026-11-10): what production does once previews are in the
        # daily table — the gate open, so the reported Thursday is an override
        # (seat scale / same-week anchor) AND the comp multiplier blends at 0.5.
        out["open_gate"] = None
        if previews and os.environ.get("GATE_ARM", "1") == "1":
            dao = P.load_daily_actual_overrides(weekend_of=w, through_date=thu)
            dao = {**dao, movie: {**(dao.get(movie) or {}), "Thursday": {
                "gross_m": float(previews), "source": "history daily_actuals", "status": "reported",
                "as_of_date": w, "notes": ""}}}
            old_mode = P.PREVIEWS_GATE_MODE
            try:
                P.PREVIEWS_GATE_MODE = "dates"
                og = P.predict_movie(
                    movie, sd, P.movie_mapping_get(P.load_polymarket_data(weekend_of=w, through_date=thu), movie, []), cal,
                    national_theatre_count=P.national_theatre_count_for_movie(movie, P.load_theatre_counts(), metadata=md),
                    snapshot_data=P.movie_mapping_get(snap, movie, {}),
                    social_data=P.load_social_signal_data(weekend_of=w, through_date=thu),
                    daily_actual_overrides=dao,
                    showtime_link_profiles=P.movie_mapping_get(P.load_showtime_link_daypart_profiles(weekend_of=w), movie, {}),
                    cross_chain_data=P.load_cross_chain_occupancy(weekend_of=w, through_date=thu),
                )
                out["open_gate"] = (og or {}).get("regression_mid_m")
            except Exception as exc:
                print(f"{movie}: open-gate replay failed ({type(exc).__name__}: {exc})")
            finally:
                P.PREVIEWS_GATE_MODE = old_mode
        for floor in (0.5, 0.3):
            out[f"floor{floor}"] = headline(pred, cal, floor, None, 0.0)
        for wgt in WEIGHTS:
            out[f"w{wgt}"] = headline(pred, cal, 0.3, previews, wgt)[0] if previews else None
        rows.append(out)

    def err(v, a):
        return (v / a - 1) * 100 if v and a else None

    print(f"{'movie':26} {'wknd':10} {'actual':>6} {'cov':>5} | {'floor .50':>18} {'floor .30':>18} | "
          + " ".join(f"{'w=' + str(w):>7}" for w in WEIGHTS))
    for r in rows:
        f5, f3 = r["floor0.5"], r["floor0.3"]
        e5, e3 = err(f5[0], r["actual"]), err(f3[0], r["actual"])
        print(f"{r['movie'][:26]:26} {r['weekend']} {r['actual']:6.1f} "
              f"{(format(r['coverage'], '.2f') if r['coverage'] is not None else '-'):>5} | "
              f"{(f'{e5:+.0f}% {str(f5[1])[:11]}' if e5 is not None else '-'):>18} "
              f"{(f'{e3:+.0f}% {str(f3[1])[:11]}' if e3 is not None else '-'):>18} | "
              + " ".join(format(format(err(r["w%s" % w], r["actual"]), "+.0f") + "%" if r["w%s" % w] else "-", ">7") for w in WEIGHTS)
              + " | open gate " + format(format(err(r["open_gate"], r["actual"]), "+.0f") + "%" if r.get("open_gate") else "-", ">6"))

    def stats(label, errs):
        errs = [e for e in errs if e is not None]
        if errs:
            print(f"  {label:34} n={len(errs):2d}  MAE {statistics.mean(abs(e) for e in errs):5.1f}%  "
                  f"median {statistics.median(abs(e) for e in errs):5.1f}%  signed {statistics.mean(errs):+5.1f}%")

    print("\n=== coverage floor (all replayed films) ===")
    stats("floor 0.50", [err(r["floor0.5"][0], r["actual"]) for r in rows])
    stats("floor 0.30", [err(r["floor0.3"][0], r["actual"]) for r in rows])
    moved = [r for r in rows if r["floor0.5"][1] != r["floor0.3"][1]]
    print(f"  films whose path changes: {len(moved)}")
    stats("  those films, floor 0.50", [err(r["floor0.5"][0], r["actual"]) for r in moved])
    stats("  those films, floor 0.30", [err(r["floor0.3"][0], r["actual"]) for r in moved])
    print("\n=== previews x class multiplier blend (films with reported previews) ===")
    withp = [r for r in rows if r["previews"]]
    for w in WEIGHTS:
        stats(f"weight {w}", [err(r[f"w{w}"], r["actual"]) for r in withp])
    og = [r for r in withp if r.get("open_gate")]
    if og:
        print(f"  -- same films with the gate OPEN (reported previews as override + comp 0.5), n={len(og)}")
        stats("   open gate (production today)", [err(r["open_gate"], r["actual"]) for r in og])
        for w in WEIGHTS:
            stats(f"   closed gate, weight {w}", [err(r[f"w{w}"], r["actual"]) for r in og])
        print("RAW " + json.dumps([{k: (v if not isinstance(v, tuple) else list(v)) for k, v in r.items()} for r in rows]))
    for label, sel in (("since 2026-09-25", lambda r: r["weekend"] >= "2026-09-25"),
                       ("before 2026-09-25", lambda r: r["weekend"] < "2026-09-25")):
        sub = [r for r in withp if sel(r)]
        if sub:
            print(f"  -- {label}")
            for w in WEIGHTS:
                stats(f"   weight {w}", [err(r[f"w{w}"], r["actual"]) for r in sub])
    return 0


if __name__ == "__main__":
    sys.exit(main())
