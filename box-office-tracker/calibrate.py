#!/usr/bin/env python3
"""
Auto-Calibration — fetches actual daily box office results and calibrates
predictions day-by-day for continuous accuracy improvement.

Runs every Tuesday (after opening weekend numbers are public on The Numbers).
Compares our Thursday/Friday/Saturday/Sunday predictions against actuals,
updates day weights, scale factors, and feeds accuracy into trading confidence.

Usage:
    python3 calibrate.py                          # Auto-calibrate last weekend
    python3 calibrate.py --actual "Movie" 85.3    # Manual total override
    python3 calibrate.py --history                 # Show past predictions vs actuals
"""

import html
import json
import os
import re
import statistics
import sys
from datetime import datetime, timedelta

import requests
from calibration_freeze import (calibration_has_weekend,
                                save_calibration_freeze)
from model_calibration import (MIN_DAILY_CALIBRATION_COVERAGE,
                               excluded_calibration_days,
                               sanitize_calibration, recalibrate_scale_factor,
                               recalibrate_day_scale_factors)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CALIBRATION_JSON = os.path.join(DATA_DIR, "calibration.json")

DEFAULT_CALIBRATION = {
    "history": [],
    "calibration_factors": {
        "amc_market_share": 0.25,
        "overall_scale_factor": 1.0,
        "day_weights": {
            "Thursday": 0.12,
            "Friday": 0.32,
            "Saturday": 0.33,
            "Sunday": 0.23,
        },
        "format_scale_factors": {},
        "historical_accuracy": [],
        "last_updated": None,
    },
}


def load_calibration():
    if os.path.exists(CALIBRATION_JSON):
        with open(CALIBRATION_JSON, "r") as f:
            cal = json.load(f)
    else:
        cal = json.loads(json.dumps(DEFAULT_CALIBRATION))
    return sanitize_calibration(
        cal,
        day_weights_default=DEFAULT_CALIBRATION["calibration_factors"]["day_weights"],
        default_market_share=DEFAULT_CALIBRATION["calibration_factors"]["amc_market_share"],
    )


def save_calibration(cal):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CALIBRATION_JSON, "w") as f:
        json.dump(cal, f, indent=2)


# ── Fetch Daily Actuals from The Numbers ────────────────────────────────────

def fetch_daily_chart(date_str):
    """Fetch daily domestic box office chart from The Numbers.

    Returns dict of {movie_title: gross_in_millions}.
    The Numbers publishes daily data by the next morning — reliable by Tuesday.
    """
    url = f"https://www.the-numbers.com/box-office-chart/daily/{date_str.replace('-', '/')}"
    # The Numbers can be slow on cold cache hits; the previous 10s timeout
    # caused intermittent day drops that silently understated weekend totals
    # (e.g. weekend of 2026-04-24 lost Friday's $39.5M, recording $57.5M
    # instead of $97M). 30s + one retry covers the common case.
    resp = None
    for attempt in range(2):
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 BoxOfficeTracker/1.0"}, timeout=30)
            if resp.status_code != 200:
                print(f"  ⚠️  The Numbers returned HTTP {resp.status_code} for {date_str}")
                return {}
            break
        except Exception as e:
            if attempt == 0:
                continue
            print(f"  ⚠️  The Numbers fetch failed for {date_str} after retry: {e}")
            return {}
    if resp is None:
        return {}

    results = {}
    table = re.search(r'<table[^>]*>(.*?)</table>', resp.text, re.DOTALL)
    if not table:
        return {}

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table.group(1), re.DOTALL)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        clean = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        if len(clean) >= 4:
            movie = clean[2]
            gross_str = clean[3].replace('$', '').replace(',', '')
            try:
                results[movie] = float(gross_str) / 1_000_000
            except ValueError:
                pass
    return results


def fetch_opening_weekend_daily(movie_title, friday_date):
    """Fetch daily actuals for a movie's opening weekend (Thu-Sun).

    Args:
        movie_title: Movie name to match (fuzzy)
        friday_date: The Friday of opening weekend (YYYY-MM-DD)

    Returns dict of {day_name: gross_in_millions} or None.

    Strategy: try the per-movie page first because it separates Thursday
    PREVIEWS (rank "P", not in the regular daily top-chart) from Friday's
    pure opening-day gross. The Numbers' top-chart endpoint hides preview
    rows, which silently zeros Thursday for any wide-release with previews
    and inflates Friday's apparent share of the weekend in our day_weights
    calibration. If the movie page lookup fails, fall back to the daily
    chart for each date (legacy behavior).
    """
    movie_daily = fetch_movie_daily_history(movie_title, friday_date)
    if movie_daily:
        return movie_daily

    friday = datetime.strptime(friday_date, "%Y-%m-%d")
    dates = [
        ("Thursday", (friday - timedelta(days=1)).strftime("%Y-%m-%d")),
        ("Friday", friday.strftime("%Y-%m-%d")),
        ("Saturday", (friday + timedelta(days=1)).strftime("%Y-%m-%d")),
        ("Sunday", (friday + timedelta(days=2)).strftime("%Y-%m-%d")),
    ]

    movie_lower = movie_title.lower()
    movie_words = set(re.sub(r'[^a-z0-9\s]', '', movie_lower).split())
    daily = {}

    for day_name, date_str in dates:
        chart = fetch_daily_chart(date_str)
        best_gross = None
        best_score = 0.0
        for title, gross in chart.items():
            title_words = set(re.sub(r'[^a-z0-9\s]', '', title.lower()).split())
            if not title_words:
                continue
            overlap = len(movie_words & title_words) / max(len(movie_words), len(title_words))
            # Require at least 60% word overlap to avoid false matches
            if overlap > best_score and overlap >= 0.6:
                best_score = overlap
                best_gross = gross
        if best_gross is not None:
            daily[day_name] = best_gross

    return daily if daily else None


def fetch_movie_daily_history(movie_title, friday_date):
    """Scrape the per-movie daily-history table from The Numbers.

    Unlike the daily top-chart, this table includes a separate Thursday
    PREVIEWS row (rank "P") so we can distinguish preview revenue from
    pure-Friday gross. Preview rows have rank "P" and theatre count 0;
    they're returned under the "Thursday" key as preview-only revenue.

    Returns dict of {day_name: gross_in_millions} or None on failure.
    """
    friday = datetime.strptime(friday_date, "%Y-%m-%d")
    year = friday.year

    # Try common URL patterns with year suffix to disambiguate remakes
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', movie_title).strip().replace(' ', '-')
    candidates = [
        f"https://www.the-numbers.com/movie/{slug}-({year})",
        f"https://www.the-numbers.com/movie/{slug}-({year - 1})",
        f"https://www.the-numbers.com/movie/{slug}",
    ]

    for url in candidates:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 BoxOfficeTracker/1.0"},
                                timeout=30, allow_redirects=True)
            if resp.status_code != 200:
                continue
        except Exception:
            continue

        # Locate the Daily Box Office Performance section
        section_match = re.search(r'Daily Box Office Performance.*?</table>', resp.text, re.DOTALL)
        if not section_match:
            continue

        # Build {date_str -> (rank, gross_millions)} from the daily rows
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', section_match.group(0), re.DOTALL)
        date_grosses = {}
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            # Decode HTML entities (&nbsp; etc.) BEFORE collapsing whitespace,
            # otherwise the date column ends up as 'Apr&nbsp;23,&nbsp;2026'
            # and strptime silently fails for every row.
            clean = [html.unescape(re.sub(r'<[^>]+>', ' ', c)).replace('\xa0', ' ').strip() for c in cells]
            clean = [re.sub(r'\s+', ' ', c) for c in clean]
            if len(clean) < 3:
                continue
            date_raw = clean[0]
            rank = clean[1]
            gross_str = clean[2].replace('$', '').replace(',', '')
            try:
                date_dt = datetime.strptime(date_raw, "%b %d, %Y")
            except ValueError:
                continue
            try:
                gross_m = float(gross_str) / 1_000_000
            except ValueError:
                continue
            date_grosses[date_dt.strftime("%Y-%m-%d")] = (rank, gross_m)

        if not date_grosses:
            continue

        # Map to weekend day labels. Thursday picks up the Preview row even
        # though "regular" daily-chart Thursday would be 0 for this movie.
        # The release-day Friday row may already include those previews as
        # part of the industry "opening day" figure. When a preview row is
        # present, subtract it so our Thursday + Friday day-by-day model does
        # not double-count previews.
        thursday = (friday - timedelta(days=1)).strftime("%Y-%m-%d")
        daily = {}
        for day_name, days_offset in [
            ("Thursday", -1), ("Friday", 0), ("Saturday", 1), ("Sunday", 2)
        ]:
            d = (friday + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            if d in date_grosses:
                rank, gross = date_grosses[d]
                daily[day_name] = gross
        thursday_rank = date_grosses.get(thursday, ("", 0))[0]
        if (
            str(thursday_rank).strip().upper() == "P"
            and daily.get("Thursday", 0) > 0
            and daily.get("Friday", 0) > daily.get("Thursday", 0)
        ):
            daily["Friday"] = max(0.0, daily["Friday"] - daily["Thursday"])
        return daily if daily else None

    return None


# ── Calibration Logic ───────────────────────────────────────────────────────

def record_result(cal, movie, weekend_of, predicted_mid, predicted_low,
                  predicted_high, daily_actuals, daily_predictions,
                  n_theatres, n_days, daily_theatre_counts=None,
                  daily_coverage_ratios=None, raw_daily_predictions=None):
    """Record daily predicted-vs-actual and update all calibration factors."""
    total_actual = sum(daily_actuals.values())
    total_predicted = predicted_mid

    error_pct = ((total_predicted - total_actual) / total_actual * 100
                 if total_actual > 0 else None)

    entry = {
        "movie": movie,
        "weekend_of": weekend_of,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "predicted_mid": round(total_predicted, 2),
        "predicted_low": round(predicted_low, 2),
        "predicted_high": round(predicted_high, 2),
        "actual_total": round(total_actual, 2),
        "daily_actuals": {k: round(v, 2) for k, v in daily_actuals.items()},
        "daily_predictions": {k: round(v, 2) for k, v in daily_predictions.items()},
        "error_pct": round(error_pct, 1) if error_pct is not None else None,
        "n_theatres": n_theatres,
        "n_days": n_days,
    }
    if raw_daily_predictions:
        entry["raw_daily_predictions"] = {
            k: round(v, 2) for k, v in raw_daily_predictions.items()
        }
    if daily_theatre_counts:
        entry["daily_theatre_counts"] = daily_theatre_counts
    if daily_coverage_ratios:
        entry["daily_coverage_ratios"] = daily_coverage_ratios
        vals = [v for v in daily_coverage_ratios.values() if v is not None]
        if vals:
            entry["coverage_ratio"] = round(sum(vals) / len(vals), 3)
        excluded_days = [
            day for day, ratio in daily_coverage_ratios.items()
            if ratio < MIN_DAILY_CALIBRATION_COVERAGE
        ]
        if excluded_days:
            entry["calibration_excluded_days"] = sorted(excluded_days)
    cal["history"].append(entry)

    factors = cal["calibration_factors"]

    # 1a. Update overall scale factor (EMA) — kept as a fallback for movies
    #     with no per-day history yet, but predict.py now prefers the per-day
    #     scale factors below for Thu/Fri/Sat/Sun.
    factors["overall_scale_factor"] = recalibrate_scale_factor(
        cal["history"],
        default=1.0,
    )

    # 1b. Per-day scale factors (EMA) — calibration adds up to a total
    #     day-by-day rather than scaling the weekend sum once. Each day's
    #     bias (Thursday previews-only, Saturday partial-scrape, etc.) gets
    #     learned independently. Deterministic: always EMAs from 1.0 over
    #     history, so re-running this on the same history is a no-op.
    factors["day_scale_factors"] = recalibrate_day_scale_factors(cal["history"])

    # 2. Update day weights from actual daily proportions
    #    Average the actual day splits across all movies with daily data
    all_day_weights = []
    for h in cal["history"]:
        da = h.get("daily_actuals", {})
        total = sum(da.values())
        if total > 0 and len(da) >= 3:
            all_day_weights.append({d: g / total for d, g in da.items()})

    if all_day_weights:
        new_weights = {}
        for day in ["Thursday", "Friday", "Saturday", "Sunday"]:
            vals = [w.get(day, 0) for w in all_day_weights]
            new_weights[day] = round(statistics.mean(vals), 4) if vals else 0
        # Normalize to sum to 1.0
        total_w = sum(new_weights.values())
        if total_w > 0:
            factors["day_weights"] = {d: round(v / total_w, 4) for d, v in new_weights.items()}

    # 3. Update per-day accuracy (predicted vs actual for each day)
    day_errors = {}
    for h in cal["history"]:
        da = h.get("daily_actuals", {})
        dp = h.get("daily_predictions", {})
        for day in da:
            if day in dp and dp[day] > 0 and da[day] > 0:
                err = abs(dp[day] - da[day]) / da[day]
                day_errors.setdefault(day, []).append(err)

    # 4. Update AMC market share
    share_estimates = []
    for h in cal["history"]:
        if h.get("actual_total", 0) > 0 and h.get("predicted_mid", 0) > 0:
            share = factors.get("amc_market_share", 0.25)
            implied = (h["predicted_mid"] * share) / h["actual_total"]
            if 0.15 < implied < 0.40:
                share_estimates.append(implied)
    if share_estimates:
        factors["amc_market_share"] = round(statistics.median(share_estimates), 4)

    # 5. Update historical accuracy (drives trading confidence)
    if total_actual > 0 and total_predicted > 0:
        abs_error = abs(total_predicted - total_actual) / total_actual
        factors["historical_accuracy"].append({
            "movie": movie,
            "weekend_of": weekend_of,
            "abs_error_pct": round(abs_error * 100, 1),
            "n_theatres": n_theatres,
            "n_days": n_days,
            "coverage_ratio": entry.get("coverage_ratio"),
            "daily_coverage_ratios": entry.get("daily_coverage_ratios", {}),
            "daily_errors": {
                day: round(abs(daily_predictions.get(day, 0) - daily_actuals.get(day, 0))
                           / daily_actuals[day] * 100, 1)
                for day in daily_actuals
                if daily_actuals[day] > 0 and day in daily_predictions
            },
        })
        factors["historical_accuracy"] = factors["historical_accuracy"][-20:]

    factors["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_calibration(cal)
    return entry


# ── Auto-Calibration Pipeline ──────────────────────────────────────────────

def _last_friday():
    today = datetime.now()
    days_since_friday = (today.weekday() - 4) % 7
    return (today - timedelta(days=days_since_friday)).strftime("%Y-%m-%d")


def auto_calibrate():
    """Fetch actual daily results and calibrate against our predictions."""
    from predict import (load_seat_data, load_polymarket_data,
                         load_theatre_counts, predict_movie)

    cal = load_calibration()
    last_fri = _last_friday()

    print(f"{'='*60}")
    print(f"  Auto-Calibration — weekend of {last_fri}")
    print(f"{'='*60}")

    already_done = {h["movie"] for h in cal["history"] if h.get("weekend_of") == last_fri}

    seat_data = load_seat_data(weekend_of=last_fri)
    poly_data = load_polymarket_data(weekend_of=last_fri)
    # National theatre counts feed the AMC-share / national-count blend in
    # predict_movie. Skipping them here makes calibrate.py's "predicted" number
    # disagree with `predict.py --movie X` output and trains the EMA scale
    # factor against the wrong baseline.
    theatre_counts = load_theatre_counts()

    if not seat_data:
        print(f"\n  No seat data for weekend {last_fri}. Nothing to calibrate.")
        return

    eligible_movies = [movie for movie in seat_data if movie not in already_done]
    if eligible_movies:
        freeze_path = save_calibration_freeze(
            DATA_DIR,
            last_fri,
            cal,
            source="calibrate.py auto_calibrate",
            movies=eligible_movies,
        )
        if freeze_path:
            print(f"\n  Pre-actual calibration freeze: {os.path.relpath(freeze_path, os.getcwd())}")
        elif calibration_has_weekend(cal, last_fri):
            print("\n  ⚠️  Calibration already contains this weekend; not freezing contaminated state.")

    # Predict everything from a frozen pre-calibration state so later movies do
    # not benefit from actuals recorded earlier in the same Tuesday run.
    pending = []
    for movie in seat_data:
        if movie in already_done:
            print(f"\n  {movie}: already calibrated, skipping")
            continue

        print(f"\n  {movie}:")

        # Match national theatre count by exact or fuzzy name (same logic as
        # predict.py main loop).
        nat_count = theatre_counts.get(movie)
        if not nat_count:
            for tc_movie, count in theatre_counts.items():
                if tc_movie.lower() in movie.lower() or movie.lower() in tc_movie.lower():
                    nat_count = count
                    break

        # Our prediction
        pred = predict_movie(movie, seat_data[movie], poly_data.get(movie, []), cal,
                             national_theatre_count=nat_count)
        if not pred:
            print(f"    No prediction possible")
            continue

        predicted = pred["blended_m"]
        print(f"    Our prediction: ${predicted:.1f}M")

        # Fetch actual daily breakdown
        daily_actuals = fetch_opening_weekend_daily(movie, last_fri)
        if not daily_actuals:
            print(f"    No actual daily data available yet")
            continue

        total_actual = sum(daily_actuals.values())
        print(f"    Actual total: ${total_actual:.1f}M")
        for day, gross in sorted(daily_actuals.items(),
                                  key=lambda x: ["Thursday","Friday","Saturday","Sunday"].index(x[0])):
            pct = gross / total_actual * 100 if total_actual > 0 else 0
            print(f"      {day}: ${gross:.1f}M ({pct:.1f}%)")

        # Extract our per-day predictions for comparison
        daily_predictions = {}
        raw_daily_predictions = {}
        daily_theatre_counts = {}
        daily_coverage_ratios = {}
        for day_name, details in pred.get("daily_details", {}).items():
            daily_predictions[day_name] = details.get("domestic_mid", 0) / 1_000_000
            raw_daily_predictions[day_name] = details.get(
                "raw_domestic_mid",
                details.get("domestic_mid", 0),
            ) / 1_000_000
            daily_theatre_counts[day_name] = details.get("n_theatres", 0)
            if details.get("coverage_ratio") is not None:
                daily_coverage_ratios[day_name] = round(details["coverage_ratio"], 3)

        pending.append({
            "movie": movie,
            "pred": pred,
            "daily_actuals": daily_actuals,
            "daily_predictions": daily_predictions,
            "raw_daily_predictions": raw_daily_predictions,
            "daily_theatre_counts": daily_theatre_counts,
            "daily_coverage_ratios": daily_coverage_ratios,
        })

    for item in pending:
        movie = item["movie"]
        pred = item["pred"]
        daily_actuals = item["daily_actuals"]
        daily_predictions = item["daily_predictions"]
        raw_daily_predictions = item["raw_daily_predictions"]
        daily_theatre_counts = item["daily_theatre_counts"]
        daily_coverage_ratios = item["daily_coverage_ratios"]

        print(f"\n  Recording calibration for {movie}:")

        entry = record_result(
            cal, movie, last_fri,
            predicted_mid=pred["blended_m"],
            predicted_low=pred["blend_low_m"],
            predicted_high=pred["blend_high_m"],
            daily_actuals=daily_actuals,
            daily_predictions=daily_predictions,
            n_theatres=pred["n_theatres_total"],
            n_days=pred["n_days"],
            daily_theatre_counts=daily_theatre_counts,
            daily_coverage_ratios=daily_coverage_ratios,
            raw_daily_predictions=raw_daily_predictions,
        )

        error = entry["error_pct"]
        direction = "over" if error and error > 0 else "under"
        print(f"    Error: {abs(error):.1f}% ({direction}-predicted)")

        # Show day weight + per-day scale-factor update
        new_weights = cal["calibration_factors"]["day_weights"]
        new_scales = cal["calibration_factors"].get("day_scale_factors", {})
        print(f"    Updated day weights / scales:")
        for day in ["Thursday", "Friday", "Saturday", "Sunday"]:
            w = new_weights.get(day, 0)
            s = new_scales.get(day, 1.0)
            print(f"      {day}: weight={w:.1%}  scale={s:.3f}")

    # Summary
    factors = cal["calibration_factors"]
    acc = factors.get("historical_accuracy", [])
    if acc:
        mean_err = statistics.mean(a["abs_error_pct"] for a in acc)
        print(f"\n  Overall: scale={factors['overall_scale_factor']:.3f}, "
              f"mean error={mean_err:.1f}%, "
              f"movies calibrated={len(cal['history'])}")

    print(f"\n{'='*60}")


def show_history():
    cal = load_calibration()
    history = cal.get("history", [])
    if not history:
        print("No calibration history yet.")
        return

    print(f"\n{'='*70}")
    print(f"  Calibration History")
    print(f"{'='*70}")
    print(f"  {'Movie':<25} {'Weekend':<12} {'Predicted':>10} {'Actual':>10} {'Error':>8}")
    print(f"  {'─'*25} {'─'*12} {'─'*10} {'─'*10} {'─'*8}")
    for h in history:
        pred = f"${h['predicted_mid']:.1f}M"
        actual = f"${h['actual_total']:.1f}M" if h.get("actual_total") else "—"
        err = f"{h['error_pct']:+.1f}%" if h.get("error_pct") is not None else "—"
        print(f"  {h['movie'][:25]:<25} {h.get('weekend_of','?'):<12} {pred:>10} {actual:>10} {err:>8}")

        # Show daily breakdown if available
        da = h.get("daily_actuals", {})
        dp = h.get("daily_predictions", {})
        dc = h.get("daily_theatre_counts", {}) or {}
        dr = h.get("daily_coverage_ratios", {}) or {}
        excluded_days = excluded_calibration_days(h)
        if da:
            for day in ["Thursday", "Friday", "Saturday", "Sunday"]:
                a = da.get(day)
                p = dp.get(day)
                if a is not None:
                    a_str = f"${a:.1f}M"
                    p_str = f"${p:.1f}M" if p else "—"
                    err_d = f"{abs(p-a)/a*100:.0f}%" if p and a > 0 else "—"
                    coverage = ""
                    if day in dc or day in dr:
                        coverage = (
                            f"  coverage={dc.get(day, '?')} theatres"
                            f"{f' ({dr[day]:.0%})' if day in dr else ''}"
                        )
                    if day in excluded_days:
                        coverage = f"{coverage}  excluded-from-calibration"
                    print(f"    {day:<12} pred={p_str:>8}  actual={a_str:>8}  err={err_d}{coverage}")

    factors = cal.get("calibration_factors", {})
    print(f"\n  Scale: {factors.get('overall_scale_factor', 1.0):.4f}")
    print(f"  AMC share: {factors.get('amc_market_share', 0.25):.2%}")
    print(f"  Day weights: {factors.get('day_weights', {})}")
    print(f"  Day scales: {factors.get('day_scale_factors', {})}")


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if "--history" in args:
        show_history()
    elif "--actual" in args:
        idx = args.index("--actual")
        if idx + 2 >= len(args):
            print("Usage: --actual \"Movie Name\" 85.3")
            sys.exit(1)
        movie_name = args[idx + 1]
        try:
            actual_val = float(args[idx + 2])
        except ValueError:
            print("Usage: --actual \"Movie Name\" 85.3")
            sys.exit(1)

        from predict import (load_seat_data, load_polymarket_data,
                             load_theatre_counts, predict_movie)
        cal = load_calibration()
        seat_data = load_seat_data(weekend_of=_last_friday())
        poly_data = load_polymarket_data(weekend_of=_last_friday())
        theatre_counts = load_theatre_counts()

        pred = None
        matched_movie = None
        for m in seat_data:
            if movie_name.lower() in m.lower():
                matched_movie = m
                # Same fuzzy match for national theatre count as auto_calibrate.
                nat_count = theatre_counts.get(m)
                if not nat_count:
                    for tc_movie, count in theatre_counts.items():
                        if tc_movie.lower() in m.lower() or m.lower() in tc_movie.lower():
                            nat_count = count
                            break
                pred = predict_movie(m, seat_data[m], poly_data.get(m, []), cal,
                                     national_theatre_count=nat_count)
                break

        if not matched_movie or not pred:
            print(f"No seat-count prediction found for {movie_name!r}; not recording actual.")
            sys.exit(1)

        weekend_of = _last_friday()
        freeze_path = save_calibration_freeze(
            DATA_DIR,
            weekend_of,
            cal,
            source="calibrate.py --actual",
            movies=[matched_movie],
        )
        if freeze_path:
            print(f"Pre-actual calibration freeze: {os.path.relpath(freeze_path, os.getcwd())}")
        elif calibration_has_weekend(cal, weekend_of):
            print("Calibration already contains this weekend; not freezing contaminated state.")

        daily_predictions = {}
        raw_daily_predictions = {}
        daily_theatre_counts = {}
        daily_coverage_ratios = {}
        for day_name, details in pred.get("daily_details", {}).items():
            daily_predictions[day_name] = details.get("domestic_mid", 0) / 1_000_000
            raw_daily_predictions[day_name] = details.get(
                "raw_domestic_mid",
                details.get("domestic_mid", 0),
            ) / 1_000_000
            daily_theatre_counts[day_name] = details.get("n_theatres", 0)
            if details.get("coverage_ratio") is not None:
                daily_coverage_ratios[day_name] = round(details["coverage_ratio"], 3)

        # Try fetching daily breakdown, fall back to total-only
        daily_actuals = fetch_opening_weekend_daily(matched_movie, _last_friday())
        if not daily_actuals:
            daily_actuals = {"Weekend": actual_val}

        record_result(
            cal, matched_movie, weekend_of,
            predicted_mid=pred["blended_m"],
            predicted_low=pred["blend_low_m"],
            predicted_high=pred["blend_high_m"],
            daily_actuals=daily_actuals,
            daily_predictions=daily_predictions,
            n_theatres=pred["n_theatres_total"],
            n_days=pred["n_days"],
            daily_theatre_counts=daily_theatre_counts,
            daily_coverage_ratios=daily_coverage_ratios,
            raw_daily_predictions=raw_daily_predictions,
        )
        print(f"Recorded: {matched_movie} actual=${actual_val}M")
    else:
        auto_calibrate()
