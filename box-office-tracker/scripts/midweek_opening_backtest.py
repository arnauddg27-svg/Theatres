#!/usr/bin/env python3
"""Backtest: reported days of a pre-Friday opening as actuals vs as previews.

For every finished pre-Friday opening in data/midweek-opening-dailies.csv, at
each point of its run (after the opening day, after the second day, ...):

  AFTER   midweek_opening.project(): reported days + the remaining days from
          the day shape of the OTHER openings in the same frame (leave one
          out; --prospective uses earlier weekends only).
  BEFORE  what predict.py served until 2026-11-28 once Thursday was reported:
          the reported Thursday treated as previews -- the geometric 50/50
          blend of the one-day seat regression scaled to the reported gross
          (days_to_weekend) and Thursday x the class previews multiplier
          (class_opening_multiplier). On the three live 2026-11-27 rows this
          replay gives 57.9 / 39.1 / 24.3 against 57.73 / 39.14 / 24.32 logged
          (the remainder is the review factor). Today's calibration is used
          for every film, so BEFORE is the current model, not the model of
          the film's year. Shown only at the stage where Thursday is the
          newest reported day and Friday is not.

Both are scored on the model's own window, Thursday-Sunday, and AFTER also on
opening day through Sunday (the 5-day frame of a Wednesday opener).

    python3 scripts/midweek_opening_backtest.py [--prospective] [--films]
"""
import contextlib
import io
import json
import os
import statistics
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import midweek_opening as M  # noqa: E402

# Audience class for the BEFORE replay's previews multiplier only.
FAMILY = {"encanto", "strangeworld", "wish", "moana2", "zootopia2", "sing2", "pussinbootsthelastwish",
          "despicableme4", "minionsmonsters", "thesupermariobrosmovie"}
LEGACY = {"houseofgucci", "napoleon", "acompleteunknown", "thecolorpurple", "theboysintheboat", "ferrari",
          "air", "bobmarleyonelove", "songsungblue", "devotion"}
FAN = {"residentevilwelcometoraccooncity", "thematrixresurrections", "thekingsman", "madameweb",
       "missionimpossibledeadreckoningpartone", "jurassicworldrebirth", "theamazingdigitalcircusthelastact"}


def audience(title):
    key = M.movie_key(title)
    return ("broad_family" if key in FAMILY else "broad_legacy" if key in LEGACY
            else "fan_driven" if key in FAN else "broad_adult")


def before_replay(P, cal, title, weekend, thursday_m):
    with contextlib.redirect_stdout(io.StringIO()):
        seat_mid, _, _, _ = P.days_to_weekend({"Thursday": thursday_m * 1e6 / P.get_day_scale(cal, "Thursday")}, cal)
        mult = P.class_opening_multiplier(cal, audience(title), "previews", exclude=(weekend, title), weekend_of=None)
    if not mult or seat_mid <= 0:
        return None
    return (seat_mid / 1e6 * thursday_m * mult["multiplier"]) ** 0.5


def truncated(days, run_dates, k):
    keep = set(run_dates[:k])
    return {d: v for d, v in days.items() if v[0] == M.PREVIEW or d.isoformat() in keep}


def run_backtest(data, prospective=False, with_before=True):
    P = cal = None
    if with_before:
        import predict as P  # noqa: N812
        with open(os.path.join(ROOT, "data", "calibration.json")) as f:
            cal = json.load(f)
    rows = []
    for (weekend, key), film in sorted(data.items()):
        full = M.opening_run(film["days"], weekend)
        if not full or full["remaining_dates"] or full["position"] != len(full["reported_dates"]):
            continue
        friday = M._date(weekend)
        thursday, sunday = friday - timedelta(days=1), friday + timedelta(days=2)
        gross = [full["reported_m"][d] for d in full["reported_dates"]]
        actual_thu_sun = sum(g for d, g in full["reported_m"].items() if d >= thursday.isoformat())
        actual_run = sum(gross)
        comps = M.complete_runs(data, before_weekend=weekend if prospective else None,
                                exclude=(weekend, film["movie"]))
        for k in range(1, len(gross)):
            run = M.opening_run(truncated(film["days"], full["reported_dates"], k), weekend,
                                known_opening=full["opening_date"])
            projection = M.project(run, comps)
            if not projection:
                continue
            thu_sun = M.frame_total(run, projection, thursday, sunday)
            whole = M.frame_total(run, projection, full["opening_date"], sunday)
            last = M._date(run["reported_dates"][-1])
            before = None
            if with_before and last == thursday:
                before = before_replay(P, cal, film["movie"], weekend, run["last_m"])
            rows.append({
                "movie": film["movie"], "weekend_of": weekend, "frame": full["frame"], "offset": full["offset"],
                "stage": M.stage_name(run), "pool": projection["pool"], "n_comps": projection["n_comps"],
                "actual_thu_sun": actual_thu_sun, "after_thu_sun": thu_sun[0],
                "in_band": thu_sun[1] <= actual_thu_sun <= thu_sun[2],
                "actual_run": actual_run, "after_run": whole[0] if whole else None,
                "before_thu_sun": before,
            })
    return rows


def pct(values):
    return f"{100 * statistics.mean(values):5.1f}%" if values else "    —"


def summarize(rows, out=sys.stdout):
    groups = {}
    for r in rows:
        groups.setdefault((r["frame"], r["offset"], r["stage"]), []).append(r)
    print(f"{'frame':13s} {'opens':5s} {'stage':26s} {'n':>2s}  {'before':>7s} {'after':>7s}  "
          f"{'after, run':>10s}  {'in band':>7s}", file=out)
    for (frame, offset, stage), group in sorted(groups.items()):
        after = [abs(r["after_thu_sun"] / r["actual_thu_sun"] - 1) for r in group]
        before = [abs(r["before_thu_sun"] / r["actual_thu_sun"] - 1) for r in group if r["before_thu_sun"]]
        whole = [abs(r["after_run"] / r["actual_run"] - 1) for r in group if r["after_run"]]
        opens = M.DAY_NAMES[(4 - offset) % 7][:3]
        print(f"{frame:13s} {opens:5s} {stage:26s} {len(group):2d}  {pct(before):>7s} {pct(after):>7s}  "
              f"{pct(whole):>10s}  {sum(r['in_band'] for r in group):3d}/{len(group)}", file=out)
    paired = [r for r in rows if r["before_thu_sun"]]
    if paired:
        b = [abs(r["before_thu_sun"] / r["actual_thu_sun"] - 1) for r in paired]
        a = [abs(r["after_thu_sun"] / r["actual_thu_sun"] - 1) for r in paired]
        signed = statistics.mean(r["before_thu_sun"] / r["actual_thu_sun"] - 1 for r in paired)
        better = sum(1 for x, y in zip(b, a) if y < x)
        print(f"\nThursday reported, Friday not (n={len(paired)}), Thursday-Sunday: before {pct(b).strip()} "
              f"mean miss (signed {100 * signed:+.1f}%), after {pct(a).strip()}; closer on {better} of {len(paired)}.",
              file=out)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    data = M.load_rows()
    rows = run_backtest(data, prospective="--prospective" in argv)
    if "--films" in argv:
        for r in rows:
            if r["before_thu_sun"]:
                print(f"{r['weekend_of']} {r['movie'][:38]:38s} {r['frame']:12s} actual {r['actual_thu_sun']:7.2f}  "
                      f"before {r['before_thu_sun']:7.2f} ({100 * (r['before_thu_sun'] / r['actual_thu_sun'] - 1):+4.0f}%)  "
                      f"after {r['after_thu_sun']:7.2f} ({100 * (r['after_thu_sun'] / r['actual_thu_sun'] - 1):+4.0f}%)")
        print()
    summarize(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
