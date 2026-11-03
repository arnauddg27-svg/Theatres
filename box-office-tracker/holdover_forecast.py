#!/usr/bin/env python3
"""Forecast the 3-day (Fri-Sun) gross of 2nd/3rd-weekend films with a market.

For a film in data/holdover-titles.csv (holdover.py) the forecast is built
from its own earlier weekends, day by day. The BASE is the previous weekend
when The Numbers has its dailies (You Can See Everything grew from $15.6M to
$18.7M in weekend 2: an opening base said $3.9M for weekend 3, the market
$10-12M), else the opening with Friday excluding previews.

  known day      the reported gross (The Numbers daily table, falling back to
                 daily-actual-overrides.csv); otherwise our post-show seat
                 census: BASE-day gross x (this weekend's counted dollars /
                 the base day's) over the SAME theatres (AMC finals,
                 Cinemark/Alamo/Harkins/Webedia post census). The census is
                 only read against the base weekend, and not at all when the
                 film's theatre count grew since then (You Can See Everything
                 went 855 -> 3,243 theatres after opening: its weekend-3
                 Saturday at the original theatres was 0.36x the opening while
                 the national Friday was 0.94x — a $7.0M call against a
                 $10-12M market, 2026-11-01).
  unknown day    base day x the latest known day's ratio x the fitted day
                 shape (data/holdover-day-shape.json, scripts/holdover_
                 backtest.py, 185 films leave-one-out: Friday known -> 3-day
                 9.4% mean |error| vs 13.1% for a flat ratio; Fri+Sat 3.6%).
  nothing known  base weekend x the median drop (1->2 21%, 2->3 24% error).

The band is the backtest's 10th-90th percentile of truth/estimate for the
stage the REPORTED days reach: census-derived days move the mid but have no
graded record yet, so they are labelled (days_census) and the log grades
them against the reported days.

Each run appends one row per film to data/holdover-prediction-log.csv; the
odds logger (scripts/log_polymarket_odds.py) fills its poly_* columns.

    python3 holdover_forecast.py [--weekend YYYY-MM-DD] [--no-log]
"""
import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import holdover

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SHAPE_JSON = os.path.join(DATA_DIR, "holdover-day-shape.json")
LOG_CSV = os.path.join(DATA_DIR, "holdover-prediction-log.csv")
DAILY_CSV = os.path.join(DATA_DIR, "daily-actual-overrides.csv")
MODEL_VERSION = "holdover-v1"
DAYS = ("Friday", "Saturday", "Sunday")
OFFSET = {"Thursday": -1, "Friday": 0, "Saturday": 1, "Sunday": 2}
CENSUS_CHAINS = ("AMC", "CNMK", "ALMO", "HARK", "WEBD")
# Matched theatres (all chains) for a census day. 2026-10-31 check on the
# openers since 10-02: census Sat/Fri and Sun/Fri ratios ran +16% vs reported
# on average, and the 20-104-theatre films (Klara, Sense and Sensibility) were
# off by 47-99%; the 600+ theatre films since 10-16 by 3-15%.
MIN_CENSUS_THEATRES = 100
# A per-theatre census ratio scales a national day only while the film plays
# in (about) the same theatres as the base weekend. Growth beyond this since
# the base weekend (an expansion) voids the census for that film.
MAX_CENSUS_THEATRE_GROWTH = 1.15
METADATA_CSV = os.path.join(DATA_DIR, "movie-metadata.csv")
THEATRE_COUNTS_JSON = os.path.join(DATA_DIR, "theatre-counts.json")
GRADES_CSV = os.path.join(DATA_DIR, "holdover-grades.csv")
GRADE_FIELDS = ["weekend_of", "movie", "weekend_num", "forecast_stage", "days_census", "logged_at",
                "forecast_m", "low_m", "high_m", "actual_m", "error_pct", "in_band",
                "poly_favorite", "poly_favorite_prob", "poly_favorite_hit", "model_version", "graded_at"]
LOG_FIELDS = ["logged_at", "weekend_of", "movie", "weekend_num", "opening_weekend_of",
              "opening_m", "base", "base_m", "headline_mid_m", "headline_low_m", "headline_high_m",
              "forecast_stage", "days_actual", "days_census", "day_m", "latest_ratio",
              "census_chains", "census_theatres", "model_version"]


def load_shape(path=SHAPE_JSON):
    with open(path) as f:
        return json.load(f)["weekends"]


def reported_days(weekend_of, movie, path=DAILY_CSV):
    """{day: gross_m} for one film-weekend, latest as_of per day."""
    latest = {}
    key = holdover.title_key(movie)
    try:
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                if r.get("weekend_of") != weekend_of or holdover.title_key(r.get("movie_title")) != key:
                    continue
                if (r.get("status") or "reported") != "reported":
                    continue
                try:
                    g = float(r.get("gross_m"))
                except (TypeError, ValueError):
                    continue
                day = r.get("day_of_week")
                if r.get("as_of_date", "") >= latest.get(day, ("", 0))[0]:
                    latest[day] = (r.get("as_of_date", ""), g)
    except OSError:
        return {}
    return {d: g for d, (_, g) in latest.items() if g > 0}


def fetch_daily(movie, weekend_of):
    """The film's whole daily table from The Numbers ({date: (rank, gross_m)})."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
        import import_thenumbers_daily as N
        return N.fetch_daily_table(movie, int(weekend_of[:4]), weekend_of=weekend_of) or {}
    except Exception as exc:
        print(f"  ⚠️  {movie}: daily table fetch failed ({type(exc).__name__})")
        return {}


def table_days(daily, weekend_of, opening=False):
    """{Thursday?, Friday, Saturday, Sunday} $M for one weekend of a daily
    table; an opening's Friday excludes the previews (import_thenumbers_daily
    convention), a later weekend's Thursday is a weekday and is left out."""
    fri = datetime.strptime(weekend_of, "%Y-%m-%d").date()
    out = {}
    for day in (("Thursday",) if opening else ()) + DAYS:
        got = daily.get(fri + timedelta(days=OFFSET[day]))
        if got:
            out[day] = round(float(got[1]), 4)
    thu = daily.get(fri - timedelta(days=1))
    if opening and "Friday" in out:
        if thu and thu[0] == "P":
            out["Friday"] = round(out["Friday"] - float(thu[1]), 4)
        else:
            out.pop("Thursday", None)
    return out


def census_by_theatre(weekend_of, movie):
    """{day: {(chain, theatre): dollars}} from post-show reads of one film."""
    import chain_census as C
    import predict as P
    dates = {(datetime.strptime(weekend_of, "%Y-%m-%d") + timedelta(days=OFFSET[d])).strftime("%Y-%m-%d"): d
             for d in DAYS}
    key = holdover.title_key(movie)
    out = defaultdict(lambda: defaultdict(float))
    seat = P.movie_mapping_get(P.load_seat_data(weekend_of=weekend_of) or {}, movie, None) or {}
    for date, rows in seat.items():
        if date not in dates:
            continue
        for r in P._latest_seat_showtime_rows(rows).values():
            try:
                sold = float(r.get("seats_sold") or 0)
            except ValueError:
                continue
            if sold >= 0:
                out[dates[date]][("AMC", r.get("theatre_name"))] += sold * C._price(r, weekend_of)
    for chain in ("CNMK", "ALMO", "HARK", "WEBD"):
        latest = {}
        for r in C._lane_rows(chain, weekend_of):
            if (r.get("row_kind") != "post-show-census" or r.get("show_date") not in dates
                    or holdover.title_key(r.get("movie_title")) != key):
                continue
            k = (r.get("show_date"), r.get("theatre_name"), r.get("showtime_id"))
            if k not in latest or (r.get("snapshot_time") or "") > (latest[k].get("snapshot_time") or ""):
                latest[k] = r
        for (date, theatre, _sid), r in latest.items():
            try:
                sold = (float(r.get("occupancy_pct") or 0) / 100.0 * C.WEBEDIA_EST_SEATS if chain == "WEBD"
                        else float(r.get("reserved_seats") or 0))
            except ValueError:
                continue
            out[dates[date]][(chain, theatre)] += sold * C._price(r, weekend_of)
    return out


def census_ratios(opening, current):
    """{day: (ratio, chains, theatres)} over theatres counted on both weekends."""
    out = {}
    for day in DAYS:
        cur, base = current.get(day) or {}, opening.get(day) or {}
        matched = [k for k in cur if base.get(k, 0) > 0]
        if len(matched) < MIN_CENSUS_THEATRES:
            continue
        num = sum(cur[k] for k in matched)
        den = sum(base[k] for k in matched)
        if den > 0 and num > 0:
            out[day] = (num / den, sorted({c for c, _ in matched}), len(matched))
    return out


def theatre_counts(movie, base_weekend, metadata_path=METADATA_CSV, counts_path=THEATRE_COUNTS_JSON):
    """(base-weekend count, current count) or None. The base count is the
    opening-weekend national_theatre_count in movie-metadata.csv, so it is
    only known when the base IS the opening; the current count is the AMC
    movie-page count the lanes save to theatre-counts.json."""
    key = holdover.title_key(movie)
    base = current = None
    try:
        with open(metadata_path, newline="") as f:
            for r in csv.DictReader(f):
                if r.get("weekend_of") == base_weekend and holdover.title_key(r.get("movie")) == key:
                    base = float(r.get("national_theatre_count") or 0) or None
        with open(counts_path) as f:
            for name, n in (json.load(f) or {}).items():
                if not str(name).startswith("_") and holdover.title_key(name) == key:
                    current = float(n or 0) or None
    except (OSError, ValueError, TypeError):
        return None
    return (base, current) if base and current else None


def census_void_reason(movie, base_weekend):
    """Why the census must not be read for this film, or None."""
    counts = theatre_counts(movie, base_weekend)
    if counts and counts[1] / counts[0] > MAX_CENSUS_THEATRE_GROWTH:
        return (f"theatre count grew {counts[0]:,.0f} -> {counts[1]:,.0f} since {base_weekend}; "
                "per-theatre ratios do not scale an expansion")
    return None


def _stage(days):
    return ("all_known" if all(d in days for d in DAYS)
            else "fri_sat_known" if "Saturday" in days
            else "fri_known" if days else "prior")


def forecast(base_days, known, shape, band_days=None):
    """Pure. base_days: the base weekend {Thursday previews?, Friday (ex
    previews), Saturday, Sunday} in $M; known: {day: gross_m} for this
    weekend; shape: the base->target fit; band_days: the known days the band
    is set by (default all; census days are not graded yet, so callers pass
    the reported ones). Returns (mid, low, high, stage, {day: gross_m}) or None."""
    if not all(base_days.get(d) for d in DAYS):
        return None
    o = base_days
    if not known:
        mid = (sum(o[d] for d in DAYS) + (o.get("Thursday") or 0)) * shape["drop"]
        stage, day_m = "prior", {}
    else:
        day_m = dict(known)
        r = {d: known[d] / o[d] for d in known}
        u = {"Friday": 1.0, "Saturday": shape["u_saturday"], "Sunday": shape["u_sunday"]}
        if "Saturday" in r:
            # Saturday anchors Sunday (v); Friday, if unknown, backs out of it.
            day_m.setdefault("Sunday", o["Sunday"] * r["Saturday"] * shape["v_sunday"])
            day_m.setdefault("Friday", o["Friday"] * r["Saturday"] / shape["u_saturday"])
        else:
            anchor = "Friday" if "Friday" in r else "Sunday"
            base = r[anchor] / u[anchor]
            for d in DAYS:
                day_m.setdefault(d, o[d] * base * u[d])
        mid = sum(day_m[d] for d in DAYS)
        stage = _stage(known)
    band = _stage(known if band_days is None else [d for d in known if d in band_days])
    if band == "all_known":
        low = high = mid
    else:
        q10, q90 = shape["band_q10_q90"][band]
        low, high = mid * q10, mid * q90
    return mid, low, high, stage, day_m


def film_forecast(entry, shape_by_pair, actuals_path=DAILY_CSV, census=True, fetch=True):
    weekend, movie = entry["weekend_of"], entry["movie"]
    n, opening = int(entry["weekend_num"]), entry["opening_weekend_of"]
    daily = fetch_daily(movie, weekend) if fetch else {}
    o = {**reported_days(opening, movie, actuals_path), **table_days(daily, opening, opening=True)}
    actual = {**{d: g for d, g in reported_days(weekend, movie, actuals_path).items() if d in DAYS},
              **table_days(daily, weekend)}
    prev = (datetime.strptime(weekend, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
    prev_days = table_days(daily, prev) if n >= 3 else {}
    if n >= 3 and all(prev_days.get(d) for d in DAYS) and f"{n - 1}-{n}" in shape_by_pair:
        base, shape, base_label = prev_days, shape_by_pair[f"{n - 1}-{n}"], f"wk{n - 1}"
    else:
        base, shape, base_label = o, shape_by_pair.get(f"1-{n}"), "opening"
    if not shape:
        return None
    # The census is read against the BASE weekend (the one whose days it
    # scales): a weekend-3 film with a weekend-2 base needs a weekend-2 census.
    base_weekend = opening if base_label == "opening" else prev
    ratios = {}
    void = census_void_reason(movie, base_weekend) if census else None
    if void:
        print(f"  ↷ {movie}: census not read — {void}")
    elif census:
        try:
            ratios = census_ratios(census_by_theatre(base_weekend, movie), census_by_theatre(weekend, movie))
        except Exception as exc:
            print(f"  ⚠️  {movie}: census read failed ({type(exc).__name__}: {exc})")
    known = dict(actual)
    via_census = []
    for d, (ratio, _chains, _n) in ratios.items():
        if d not in known and base.get(d):
            known[d] = base[d] * ratio
            via_census.append(d)
    res = forecast(base, known, shape, band_days=actual)
    if not res:
        return None
    mid, low, high, stage, day_m = res
    latest = max((d for d in known), key=DAYS.index, default=None)
    return {"weekend_of": weekend, "movie": movie, "weekend_num": n, "opening_weekend_of": opening,
            "opening_m": (round(sum(o[d] for d in DAYS) + (o.get("Thursday") or 0), 3)
                          if all(o.get(d) for d in DAYS) else ""),
            "base": base_label, "base_m": round(sum(base[d] for d in DAYS) + (base.get("Thursday") or 0), 3),
            "headline_mid_m": round(mid, 3), "headline_low_m": round(low, 3),
            "headline_high_m": round(high, 3), "forecast_stage": stage,
            "days_actual": ",".join(d for d in DAYS if d in actual),
            "days_census": ",".join(d for d in DAYS if d in via_census),
            "day_m": ";".join(f"{d[:3]}={day_m[d]:.3f}" for d in DAYS if d in day_m),
            "latest_ratio": round(known[latest] / base[latest], 4) if latest else "",
            "census_chains": ",".join(sorted({c for d in via_census for c in ratios[d][1]})),
            "census_theatres": ";".join(f"{d[:3]}={ratios[d][2]}" for d in via_census),
            "model_version": MODEL_VERSION}


def append_log(rows, path=LOG_CSV):
    """Append, skipping a film whose last row has the same numbers (a settled
    weekend keeps being re-forecast by every finalize until the next one)."""
    fresh = not os.path.exists(path) or os.path.getsize(path) == 0
    fields = LOG_FIELDS
    last = {}
    if not fresh:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            fields = list(reader.fieldnames or LOG_FIELDS)
            for r in reader:
                last[(r.get("weekend_of"), holdover.title_key(r.get("movie")))] = r
        fields += [c for c in LOG_FIELDS if c not in fields]
    same = ("headline_mid_m", "forecast_stage", "days_actual", "days_census")
    rows = [r for r in rows
            if not (prev := last.get((r["weekend_of"], holdover.title_key(r["movie"]))))
            or any(str(prev.get(k, "")) != str(r.get(k, "")) for k in same)]
    if not rows:
        return 0
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if fresh:
            w.writeheader()
        w.writerows(rows)
    return len(rows)


def bracket_bounds(label):
    """('10m-12m' | '10-12M' | '<5M' | '20M+') -> (low, high) in $M, or None."""
    import re
    text = (label or "").strip().lower()
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", text)]
    if not nums:
        return None
    if text.startswith("<") or "under" in text or "less" in text:
        return (0.0, nums[0])
    if text.startswith(">") or text.endswith("+") or "over" in text or "more" in text:
        return (nums[0], float("inf"))
    return (nums[0], nums[1]) if len(nums) >= 2 else None


def grade_log(log_path=LOG_CSV, actuals_path=DAILY_CSV, out_path=GRADES_CSV, now=None):
    """Rewrite data/holdover-grades.csv: for every film-weekend in the log
    whose three days are reported, the LAST forecast of each stage against the
    actual 3-day. Idempotent (the file is regenerated); returns the rows."""
    try:
        with open(log_path, newline="") as f:
            log = list(csv.DictReader(f))
    except OSError:
        return []
    last = {}
    for r in sorted(log, key=lambda r: r.get("logged_at") or ""):
        last[(r.get("weekend_of"), holdover.title_key(r.get("movie")),
              r.get("forecast_stage"), r.get("days_census") or "")] = r
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    actual_cache, rows = {}, []
    for (weekend, key, stage, census), r in sorted(last.items()):
        if (weekend, key) not in actual_cache:
            days = reported_days(weekend, r.get("movie"), actuals_path)
            actual_cache[(weekend, key)] = sum(days[d] for d in DAYS) if all(days.get(d) for d in DAYS) else None
        actual = actual_cache[(weekend, key)]
        if actual is None:
            continue
        try:
            mid, low, high = (float(r.get(k)) for k in ("headline_mid_m", "headline_low_m", "headline_high_m"))
        except (TypeError, ValueError):
            continue
        fav = bracket_bounds(r.get("poly_favorite"))
        rows.append({
            "weekend_of": weekend, "movie": r.get("movie"), "weekend_num": r.get("weekend_num"),
            "forecast_stage": stage, "days_census": census, "logged_at": r.get("logged_at"),
            "forecast_m": round(mid, 3), "low_m": round(low, 3), "high_m": round(high, 3),
            "actual_m": round(actual, 3), "error_pct": round((mid / actual - 1) * 100, 1),
            # all_known is the reported weekend itself, not a forecast: its band is a point.
            "in_band": "" if stage == "all_known" else ("yes" if low <= actual <= high else "no"),
            "poly_favorite": r.get("poly_favorite") or "",
            "poly_favorite_prob": r.get("poly_favorite_prob") or "",
            "poly_favorite_hit": ("" if not fav else "yes" if fav[0] <= actual < fav[1] else "no"),
            "model_version": r.get("model_version") or "", "graded_at": stamp,
        })
    if rows:
        with open(out_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=GRADE_FIELDS)
            w.writeheader()
            w.writerows(rows)
        by_stage = defaultdict(list)
        for g in rows:
            by_stage[(g["forecast_stage"], g["days_census"])].append(abs(g["error_pct"]))
        print(f"holdover grades: {len(rows)} stage rows over "
              f"{len({(g['weekend_of'], g['movie']) for g in rows})} film-weekend(s) → {os.path.relpath(out_path)}")
        for (stage, census), errs in sorted(by_stage.items()):
            print(f"  {stage:14s} census={census or '-':9s} mean |err| {sum(errs) / len(errs):5.1f}%  n={len(errs)}")
    else:
        print("holdover grades: no film-weekend with a reported Fri-Sun yet")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weekend", help="Friday of the holdover weekend (default: this weekend)")
    ap.add_argument("--no-log", action="store_true")
    ap.add_argument("--grade", action="store_true",
                    help="grade the log against reported weekends into data/holdover-grades.csv and exit")
    args = ap.parse_args(argv)
    if args.grade:
        grade_log()
        return 0
    now = datetime.now(timezone.utc)
    weekend = args.weekend or (now - timedelta(hours=8) - timedelta(
        days=((now - timedelta(hours=8)).weekday() - 4) % 7)).strftime("%Y-%m-%d")
    entries = holdover.entries(weekend)
    if not entries:
        print(f"holdover forecast: no holdover markets for weekend {weekend}")
        return 0
    shape = load_shape()
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    print(f"\n{'=' * 70}\n  Holdover Weekend Forecasts — weekend of {weekend}\n{'=' * 70}")
    for e in entries:
        try:
            row = film_forecast(e, shape)
        except Exception as exc:
            print(f"  ⚠️  {e['movie']}: forecast failed ({type(exc).__name__}: {exc})")
            continue
        if not row:
            print(f"  {e['movie']} (wk {e['weekend_num']}): no forecast — base weekend dailies unknown")
            continue
        row["logged_at"] = stamp
        rows.append(row)
        print(f"  {row['movie']} (wk {row['weekend_num']}, base {row['base']} ${row['base_m']:.1f}M): "
              f"${row['headline_mid_m']:.2f}M [{row['headline_low_m']:.2f}-{row['headline_high_m']:.2f}] "
              f"stage={row['forecast_stage']} actual={row['days_actual'] or '-'} "
              f"census={row['days_census'] or '-'} {row['day_m']}")
    if rows and not args.no_log:
        append_log(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
