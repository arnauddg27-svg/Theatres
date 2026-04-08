#!/usr/bin/env python3
"""
Opening Weekend Box Office Predictor
=====================================
Predicts North American opening-weekend gross from AMC seat occupancy data
and Polymarket betting odds.

Pipeline:
  A. Per-theatre daily revenue (occupancy × seats × showings × price)
  B. Sum all AMC theatres
  C. AMC → total domestic (÷ market share)
  D. Partial days → full weekend (day weights)
  E. Polymarket expected value (bracket parsing)
  F. Blended prediction (seat + Polymarket weighted)

Usage:
    python3 predict.py                              # All movies this weekend
    python3 predict.py --movie "Project Hail Mary"  # Single movie
    python3 predict.py --actual "Movie Name" 125.3  # Record actual result
    python3 predict.py --history                    # Past predictions vs actuals
    python3 predict.py --verbose                    # Full calculation breakdown
"""

import json, csv, os, sys, re, statistics
from datetime import datetime, timedelta
from math import sqrt

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR            = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SEAT_CSV            = os.path.join(DATA_DIR, "seat-counts.csv")
POLY_CSV            = os.path.join(DATA_DIR, "polymarket-markets.csv")
CALIBRATION_JSON    = os.path.join(DATA_DIR, "calibration.json")
THEATRE_COUNTS_JSON = os.path.join(DATA_DIR, "theatre-counts.json")

# ── Default Constants ────────────────────────────────────────────────────────
DEFAULT_AMC_MARKET_SHARE = 0.25

FORMAT_DEFLATORS = {
    8: 0.65, 7: 0.65,   # IMAX with Laser
    6: 0.65,             # IMAX / IMAX 3D
    5: 0.70,             # Dolby
    4: 0.80, 3: 0.80,   # Prime / XL
    2: 0.85,             # Laser
    1: 0.90, 0: 0.90,   # Standard / Digital
}

SEAT_DEFLATORS = {
    8: 0.70, 7: 0.70, 6: 0.70,  # IMAX rooms are bigger
    5: 0.70,                      # Dolby rooms are bigger
    4: 0.85, 3: 0.85,            # Prime/XL moderate
    2: 0.90, 1: 1.0, 0: 1.0,    # Standard = baseline
}

DAY_WEIGHTS_DEFAULT = {
    "Thursday":  0.10,
    "Friday":    0.27,
    "Saturday":  0.28,
    "Sunday":    0.19,
    # Mon-Wed are tail days; small weights used for daily revenue estimation
    "Monday":    0.08,
    "Tuesday":   0.05,
    "Wednesday": 0.03,
}


def get_day_weights(cal):
    """Get day weights from calibration, falling back to defaults.

    Calibrate.py updates these weights every Tuesday from actual daily
    box office splits. Over time they converge on the true distribution.
    """
    if cal:
        return cal.get("calibration_factors", {}).get("day_weights", DAY_WEIGHTS_DEFAULT)
    return DAY_WEIGHTS_DEFAULT

DAY_CONFIDENCE = {
    1: (0.70, 1.40),   # 1 day collected
    2: (0.85, 1.20),   # 2 days
    3: (0.92, 1.10),   # 3 days
    4: (0.96, 1.05),   # 4 days (full opening weekend)
    5: (0.97, 1.04),   # 5 days
    6: (0.98, 1.03),   # 6 days
    7: (0.99, 1.02),   # full week
}

DEFAULT_TICKET_PRICE = 14.50
PRICE_DISCOUNT_FACTOR = 0.85   # avg effective price vs adult price
DEFAULT_SEATS_PER_SHOW = 200   # when no seat map available


# ── Data Loading ─────────────────────────────────────────────────────────────

def _current_weekend_friday():
    """Return the Friday that anchors the current opening weekend (Thu-Mon).

    Must match opening_weekend_friday() in scraper.py so weekend_of values
    in the CSV align with what predict.py filters on.
    """
    from datetime import timedelta
    now = datetime.now()
    wd = now.weekday()  # Mon=0 ... Sun=6
    if wd == 3:   # Thursday → next Friday (new opening weekend)
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    if wd == 4:   # Friday
        return now.strftime("%Y-%m-%d")
    if wd == 5:   # Saturday
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    if wd == 6:   # Sunday
        return (now - timedelta(days=2)).strftime("%Y-%m-%d")
    if wd == 0:   # Monday
        return (now - timedelta(days=3)).strftime("%Y-%m-%d")
    if wd == 1:   # Tuesday
        return (now - timedelta(days=4)).strftime("%Y-%m-%d")
    # Wednesday
    return (now - timedelta(days=5)).strftime("%Y-%m-%d")


def load_seat_data(weekend_of=None):
    """Load seat-counts.csv and group by movie → date → list of theatre rows.

    If weekend_of is set, only loads rows from that opening weekend.
    If not set, uses the current weekend (Thu-Sun → Friday anchor).
    Falls back to loading all rows if weekend_of column is absent (old data).
    """
    if not os.path.exists(SEAT_CSV):
        return {}

    if weekend_of is None:
        # Use the most recent weekend_of found in the CSV rather than
        # computing from today's date — avoids day-of-week arithmetic mismatches.
        with open(SEAT_CSV, "r") as f:
            weekends = [r.get("weekend_of", "") for r in csv.DictReader(f) if r.get("weekend_of")]
        weekend_of = max(weekends) if weekends else _current_weekend_friday()

    data = {}
    with open(SEAT_CSV, "r") as f:
        for row in csv.DictReader(f):
            movie = row.get("movie_title", "")
            date = row.get("date", "")
            if not movie or not date:
                continue
            # Filter to this weekend if the column exists
            row_weekend = row.get("weekend_of", "")
            if row_weekend and row_weekend != weekend_of:
                continue
            data.setdefault(movie, {}).setdefault(date, []).append(row)
    return data


def load_polymarket_data():
    """Load polymarket-markets.csv and group by movie title."""
    if not os.path.exists(POLY_CSV):
        return {}
    data = {}
    with open(POLY_CSV, "r") as f:
        for row in csv.DictReader(f):
            movie = row.get("movie_title", "")
            if not movie:
                continue
            data.setdefault(movie, []).append(row)
    return data


def load_calibration():
    """Load calibration.json or return defaults."""
    if os.path.exists(CALIBRATION_JSON):
        with open(CALIBRATION_JSON, "r") as f:
            return json.load(f)
    return {
        "history": [],
        "calibration_factors": {
            "amc_market_share": DEFAULT_AMC_MARKET_SHARE,
            "overall_scale_factor": 1.0,
            "last_updated": None,
        }
    }


def save_calibration(cal):
    """Save calibration.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CALIBRATION_JSON, "w") as f:
        json.dump(cal, f, indent=2)


def load_theatre_counts():
    """Load national theatre counts from theatre-counts.json (scraped from BOM)."""
    if os.path.exists(THEATRE_COUNTS_JSON):
        with open(THEATRE_COUNTS_JSON) as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if not k.startswith("_")}
    return {}


# ── Stage A: Per-Theatre Daily Revenue ───────────────────────────────────────

def time_multiplier(row):
    """Estimate multiplier based on minutes_after_showtime from the CSV.

    Negative = scraped before show started (still selling tickets).
    Zero or positive = scraped after show started (occupancy is near-final).
    """
    try:
        delta = int(row.get("minutes_after_showtime", 0) or 0)
    except (ValueError, TypeError):
        delta = 0

    if delta < -120:
        return 1.6   # >2h before showtime — occupancy will grow significantly
    elif delta < -60:
        return 1.3
    elif delta < 0:
        return 1.1   # <1h before — nearly final
    else:
        return 1.0   # after showtime — actual attendance


def infer_format_rank(row):
    """Infer format_rank from format string or auditorium_type if not present."""
    if row.get("format_rank"):
        try:
            return int(row["format_rank"])
        except (ValueError, TypeError):
            pass
    # Fall back to auditorium_type or format field
    fmt = (row.get("format") or row.get("auditorium_type") or
           row.get("auditorium_name") or "").lower()
    if "imax with laser" in fmt:
        return 7
    elif "imax" in fmt:
        return 6
    elif "dolby" in fmt:
        return 5
    elif "prime" in fmt:
        return 4
    elif "xl" in fmt:
        return 3
    elif "laser" in fmt:
        return 2
    return 1  # standard/digital


def estimate_theatre_daily_revenue(row, cal):
    """Stage A: estimate one theatre's revenue for one day from a single row."""
    total_seats = int(row.get("total_seats", 0) or 0)
    seats_sold = int(row.get("seats_sold", 0) or 0)

    # Detect data format: new collect.py vs old scraper
    has_seat_map_field = row.get("has_seat_map", "")
    has_seat_map = has_seat_map_field.lower() in ("true", "1", "yes") if has_seat_map_field else (total_seats > 0)

    is_sold_out = row.get("is_sold_out", "").lower() in ("true", "1", "yes")
    is_almost_sold = row.get("is_almost_sold_out", "").lower() in ("true", "1", "yes")
    total_showings = int(row.get("total_showings", 1) or 1)
    format_rank = infer_format_rank(row)

    # Ticket price — try multiple field names
    raw_price = row.get("adult_ticket_price", "") or row.get("ticket_price_estimate", "")
    try:
        ticket_price = float(raw_price) if raw_price else DEFAULT_TICKET_PRICE
    except (ValueError, TypeError):
        ticket_price = DEFAULT_TICKET_PRICE
    effective_price = ticket_price * PRICE_DISCOUNT_FACTOR

    # Occupancy
    if has_seat_map and total_seats > 0:
        observed_occ = seats_sold / total_seats
    elif is_sold_out:
        observed_occ = 0.95
        total_seats = DEFAULT_SEATS_PER_SHOW
    elif is_almost_sold:
        observed_occ = 0.80
        total_seats = DEFAULT_SEATS_PER_SHOW
    elif total_seats > 0 and seats_sold >= 0:
        # Old format: has seat data even without explicit has_seat_map flag
        observed_occ = seats_sold / total_seats
    else:
        return None  # can't estimate without data

    # Adjust for time (pre-showtime occupancy will increase)
    time_mult = time_multiplier(row)
    projected_occ = min(1.0, observed_occ * time_mult)

    # Format deflator: premium evening shows fill more than average across all showings
    fmt_deflator = FORMAT_DEFLATORS.get(format_rank, 0.85)
    avg_occupancy = projected_occ * fmt_deflator

    # Seat deflator: premium rooms are bigger than average auditorium
    seat_deflator = SEAT_DEFLATORS.get(format_rank, 1.0)
    avg_seats = total_seats * seat_deflator

    # Revenue = avg occupancy × avg seats × showings × price
    revenue = avg_occupancy * avg_seats * total_showings * effective_price

    return {
        "revenue": revenue,
        "avg_occupancy": avg_occupancy,
        "projected_occ": projected_occ,
        "observed_occ": observed_occ,
        "time_mult": time_mult,
        "fmt_deflator": fmt_deflator,
        "total_seats": total_seats,
        "avg_seats": avg_seats,
        "total_showings": total_showings,
        "effective_price": effective_price,
        "theatre_name": row.get("theatre_name", "?"),
        "format": row.get("format", "") or row.get("auditorium_type", "") or row.get("auditorium_name", "") or "?",
        "has_seat_map": has_seat_map,
    }


# ── Stage B: Sum All AMC Theatres ────────────────────────────────────────────

def sum_amc_theatres(theatre_results):
    """Stage B: sum all theatre revenues. Returns (total, stats)."""
    revenues = [t["revenue"] for t in theatre_results if t is not None]
    if not revenues:
        return 0, {}
    total = sum(revenues)
    mean_rev = statistics.mean(revenues)
    median_rev = statistics.median(revenues)
    stdev = statistics.stdev(revenues) if len(revenues) > 1 else mean_rev * 0.3
    return total, {
        "n_theatres": len(revenues),
        "mean_revenue": mean_rev,
        "median_revenue": median_rev,
        "stdev": stdev,
        "total": total,
    }


# ── Stage C: AMC → Total Domestic ────────────────────────────────────────────

def amc_to_domestic(amc_revenue, cal):
    """Stage C: scale AMC revenue to total domestic market."""
    share = cal["calibration_factors"].get("amc_market_share", DEFAULT_AMC_MARKET_SHARE)
    mid = amc_revenue / share
    # Uncertainty in market share: ±3 points
    low = amc_revenue / (share + 0.03)
    high = amc_revenue / max(0.15, share - 0.03)
    return mid, low, high


# ── Stage D: Partial Days → Full Weekend ─────────────────────────────────────

def days_to_weekend(daily_estimates, cal):
    """Stage D: project partial-weekend data to full weekend.

    daily_estimates: dict of {day_name: domestic_daily_mid}
    Uses calibrated day weights (learned from actual results) to project
    partial data to a full Thu-Sun weekend.
    Returns (mid, low, high).
    """
    if not daily_estimates:
        return 0, 0, 0

    day_weights = get_day_weights(cal)
    collected_sum = sum(daily_estimates.values())
    collected_weight = sum(day_weights.get(day, 0) for day in daily_estimates)

    if collected_weight <= 0:
        return collected_sum, collected_sum * 0.5, collected_sum * 2.0

    weekend_mid = collected_sum / collected_weight

    # Apply calibration scale factor
    scale = cal["calibration_factors"].get("overall_scale_factor", 1.0)
    weekend_mid *= scale

    # Confidence based on how many days we have
    n_days = len(daily_estimates)
    conf_low, conf_high = DAY_CONFIDENCE.get(n_days, (0.70, 1.40))
    weekend_low = weekend_mid * conf_low
    weekend_high = weekend_mid * conf_high

    return weekend_mid, weekend_low, weekend_high


# ── Stage E: Polymarket Expected Value ───────────────────────────────────────

def extract_bracket_range(question):
    """Parse dollar ranges from Polymarket bracket questions."""
    q = question.lower()

    # Match "$100M" or "$100 million" patterns
    amounts = re.findall(r'\$(\d+(?:\.\d+)?)\s*[Mm]', question)
    if not amounts:
        # Try without M suffix (some use "million")
        amounts = re.findall(r'\$(\d+(?:\.\d+)?)\s*(?:million|mil)', q)
    if not amounts:
        # Try bare numbers after $
        amounts = re.findall(r'\$(\d+(?:\.\d+)?)', question)
        # Filter to likely millions (> 10)
        amounts = [a for a in amounts if float(a) >= 10]

    if len(amounts) >= 2:
        return float(amounts[0]), float(amounts[1])
    elif len(amounts) == 1:
        val = float(amounts[0])
        if any(w in q for w in ["over", "above", "more than", "higher than", "exceed"]):
            return val, val + 30
        elif any(w in q for w in ["under", "below", "less than", "lower than"]):
            return max(0, val - 30), val
        else:
            return max(0, val - 10), val + 10
    return None, None


def polymarket_expected_value(markets_for_movie):
    """Stage E: compute expected value from Polymarket bracket markets."""
    brackets = []
    total_volume = 0

    for mkt in markets_for_movie:
        question = mkt.get("market_question", "") or mkt.get("question", "")
        prices_raw = mkt.get("outcome_prices", "")
        vol = float(mkt.get("total_volume", 0) or mkt.get("volume", 0) or 0)

        low, high = extract_bracket_range(question)
        if low is None:
            continue

        # Parse probability
        try:
            if prices_raw.startswith("["):
                prices = json.loads(prices_raw)
                p_yes = float(prices[0])
            else:
                p_yes = float(prices_raw) if prices_raw else 0
        except (json.JSONDecodeError, ValueError, IndexError):
            continue

        midpoint = (low + high) / 2
        brackets.append({
            "low": low, "high": high, "midpoint": midpoint,
            "p_yes": p_yes, "question": question,
        })
        total_volume = max(total_volume, vol)

    if not brackets:
        return None

    # Expected value
    ev = sum(b["midpoint"] * b["p_yes"] for b in brackets)

    # Weighted standard deviation
    if ev > 0:
        variance = sum(b["p_yes"] * (b["midpoint"] - ev) ** 2 for b in brackets)
        std = sqrt(variance) if variance > 0 else ev * 0.2
    else:
        std = 0

    # Highest probability bracket
    best_bracket = max(brackets, key=lambda b: b["p_yes"])

    return {
        "ev": ev,
        "std": std,
        "low": max(0, ev - std),
        "high": ev + std,
        "brackets": brackets,
        "best_bracket": best_bracket,
        "total_volume": total_volume,
    }


# ── Stage F: Blended Prediction ──────────────────────────────────────────────

def blend_predictions(seat_est, seat_low, seat_high,
                      poly_result, n_theatres, n_days):
    """Stage F: weighted blend of seat-based and Polymarket estimates."""
    if poly_result is None:
        return seat_est, seat_low, seat_high, 1.0, 0.0

    poly_ev = poly_result["ev"]
    poly_volume = poly_result["total_volume"]

    # Seat data quality (0-1)
    seat_quality = min(1.0, (n_theatres / 100) * 0.6 + (n_days / 3) * 0.4)

    # Polymarket quality (0-1)
    poly_quality = min(1.0, poly_volume / 500_000)

    # Weights
    w_seat = seat_quality * 0.6
    w_poly = poly_quality * 0.4
    total_w = w_seat + w_poly

    if total_w == 0:
        return seat_est, seat_low, seat_high, 1.0, 0.0

    w_seat_norm = w_seat / total_w
    w_poly_norm = w_poly / total_w

    blended = seat_est * w_seat_norm + poly_ev * w_poly_norm
    blended_low = min(seat_low, poly_result["low"])
    blended_high = max(seat_high, poly_result["high"])

    return blended, blended_low, blended_high, w_seat_norm, w_poly_norm


# ── Calibration ──────────────────────────────────────────────────────────────

def record_actual(cal, movie, predicted_mid, predicted_low, predicted_high,
                  seat_raw, poly_ev, actual, n_theatres, days_collected):
    """Record a predicted-vs-actual result and update calibration factors."""
    entry = {
        "movie": movie,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "predicted_mid": round(predicted_mid, 1),
        "predicted_low": round(predicted_low, 1),
        "predicted_high": round(predicted_high, 1),
        "seat_raw_estimate": round(seat_raw, 1) if seat_raw else None,
        "polymarket_ev": round(poly_ev, 1) if poly_ev else None,
        "actual": actual,
        "n_theatres": n_theatres,
        "days_collected": days_collected,
    }
    cal["history"].append(entry)

    # Update scale factor
    history = cal["history"]
    ratios = [h["actual"] / h["predicted_mid"]
              for h in history
              if h.get("actual") and h["predicted_mid"] > 0]

    if ratios:
        # Exponential moving average
        alpha = 0.4
        ema = ratios[-1]
        for r in reversed(ratios[:-1]):
            ema = alpha * ema + (1 - alpha) * r
        cal["calibration_factors"]["overall_scale_factor"] = round(ema, 4)

    # Refine AMC market share from seat-based estimates
    share_estimates = []
    for h in history:
        if h.get("seat_raw_estimate") and h.get("actual") and h["actual"] > 0:
            implied = h["seat_raw_estimate"] / h["actual"]
            if 0.15 < implied < 0.40:
                share_estimates.append(implied)
    if share_estimates:
        cal["calibration_factors"]["amc_market_share"] = round(
            statistics.median(share_estimates), 4
        )

    cal["calibration_factors"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_calibration(cal)


# ── Main Prediction Pipeline ─────────────────────────────────────────────────

def predict_movie(movie, seat_data, poly_data, cal, verbose=False, national_theatre_count=None):
    """Run full prediction pipeline for a single movie."""
    # Identify opening weekend dates (Thu-Sun)
    all_dates = sorted(seat_data.keys())
    if not all_dates:
        return None

    # Group by day of week
    daily_estimates = {}
    daily_details = {}

    for date_str in all_dates:
        rows = seat_data[date_str]
        # Use day_of_week from CSV if available, else compute from date
        csv_day = rows[0].get("day_of_week", "") if rows else ""
        day_name = csv_day if csv_day else datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")

        # Group by (theatre, format): collect all showtime rows per pair.
        # Each row is one showtime — revenue = sum across all captured showings.
        # Use latest run_id to pick the freshest occupancy reading per showtime.
        rows_by_theatre_fmt_show = {}
        for row in rows:
            t_id = row.get("theatre_name", "")
            fmt = (row.get("auditorium_type", "") or row.get("auditorium_name", "") or "Standard")
            showtime = row.get("showtime", "")
            key = f"{t_id}|{fmt}|{showtime}"
            sort_key = row.get("run_id", "") or row.get("check_time", "")
            prev = rows_by_theatre_fmt_show.get(key)
            if not prev or sort_key > prev.get("_sort_key", ""):
                rows_by_theatre_fmt_show[key] = {**row, "_sort_key": sort_key}

        # Stage A: per-showtime revenue, then sum per theatre-format
        theatre_results = []
        no_data_count = 0
        showings_by_theatre = {}
        for row in rows_by_theatre_fmt_show.values():
            result = estimate_theatre_daily_revenue(row, cal)
            if result:
                theatre_results.append(result)
                t_name = row.get("theatre_name", "?")
                showings_by_theatre[t_name] = showings_by_theatre.get(t_name, 0) + 1
            else:
                no_data_count += 1

        if not theatre_results:
            continue

        # Stage B: sum all AMC
        amc_total, amc_stats = sum_amc_theatres(theatre_results)
        n_amc_theatres = amc_stats.get("n_theatres", 0)
        avg_showings = (sum(showings_by_theatre.values()) / len(showings_by_theatre)
                        if showings_by_theatre else 0)

        # Stage C: AMC → domestic
        # If we have a national theatre count, use it to cross-check our scaling.
        # Per-theatre revenue from our sample × national theatre count gives an
        # independent estimate — we blend it 50/50 with the market-share approach.
        domestic_mid, domestic_low, domestic_high = amc_to_domestic(amc_total, cal)
        if national_theatre_count and n_amc_theatres > 0:
            mean_rev = amc_stats.get("mean_revenue", 0)
            nat_est = mean_rev * national_theatre_count
            # Blend: 60% market-share, 40% national-count extrapolation
            domestic_mid  = domestic_mid  * 0.6 + nat_est * 0.4
            domestic_low  = domestic_low  * 0.6 + nat_est * 0.4 * 0.85
            domestic_high = domestic_high * 0.6 + nat_est * 0.4 * 1.15

        daily_estimates[day_name] = domestic_mid
        daily_details[day_name] = {
            "date": date_str,
            "amc_total": amc_total,
            "domestic_mid": domestic_mid,
            "domestic_low": domestic_low,
            "domestic_high": domestic_high,
            "n_theatres": n_amc_theatres,
            "n_no_data": no_data_count,
            "avg_showings_per_cinema": round(avg_showings, 1),
            "mean_revenue": amc_stats.get("mean_revenue", 0),
            "median_revenue": amc_stats.get("median_revenue", 0),
            "theatre_results": theatre_results if verbose else [],
        }

    if not daily_estimates:
        return None

    # Stage D: partial days → weekend
    seat_mid, seat_low, seat_high = days_to_weekend(daily_estimates, cal)

    # Convert to millions for display
    seat_mid_m = seat_mid / 1_000_000
    seat_low_m = seat_low / 1_000_000
    seat_high_m = seat_high / 1_000_000

    # Stage E: Polymarket
    poly_result = None
    if poly_data:
        poly_result = polymarket_expected_value(poly_data)

    # Stage F: blend
    n_theatres_total = sum(d["n_theatres"] for d in daily_details.values())
    n_days = len(daily_estimates)

    if poly_result:
        # Polymarket EV is already in millions
        blended_m, blend_low_m, blend_high_m, w_seat, w_poly = blend_predictions(
            seat_mid_m, seat_low_m, seat_high_m,
            poly_result, n_theatres_total, n_days
        )
    else:
        blended_m = seat_mid_m
        blend_low_m = seat_low_m
        blend_high_m = seat_high_m
        w_seat, w_poly = 1.0, 0.0

    avg_showings_total = (
        sum(d.get("avg_showings_per_cinema", 0) for d in daily_details.values()) /
        len(daily_details) if daily_details else 0
    )

    return {
        "movie": movie,
        "seat_mid_m": seat_mid_m,
        "seat_low_m": seat_low_m,
        "seat_high_m": seat_high_m,
        "poly_result": poly_result,
        "blended_m": blended_m,
        "blend_low_m": blend_low_m,
        "blend_high_m": blend_high_m,
        "w_seat": w_seat,
        "w_poly": w_poly,
        "daily_details": daily_details,
        "daily_estimates": daily_estimates,
        "n_days": n_days,
        "n_theatres_total": n_theatres_total,
        "national_theatre_count": national_theatre_count,
        "avg_showings_per_cinema": round(avg_showings_total, 1),
        "amc_total_weekend": seat_mid * cal["calibration_factors"].get("amc_market_share", DEFAULT_AMC_MARKET_SHARE),
    }


# ── Output ───────────────────────────────────────────────────────────────────

def fmt_m(val):
    """Format millions as $XXX.XM or $X.XM."""
    if val >= 1:
        return f"${val:,.1f}M"
    elif val > 0:
        return f"${val * 1000:,.0f}K"
    return "$0"


def print_prediction(pred, verbose=False):
    """Pretty-print a movie prediction."""
    movie = pred["movie"]
    print(f"\n  {movie.upper()}")
    print(f"  {'─' * len(movie)}")

    # Seat-based
    days_str = ", ".join(sorted(pred["daily_estimates"].keys()))
    n_th = pred["n_theatres_total"]
    nat = pred.get("national_theatre_count")
    nat_str = f", {nat:,} national" if nat else ""
    shows_str = f", ~{pred.get('avg_showings_per_cinema', 0):.1f} showings/cinema" if pred.get('avg_showings_per_cinema') else ""
    print(f"  Seat-based:    {fmt_m(pred['seat_mid_m']):>10}  "
          f"({fmt_m(pred['seat_low_m'])} - {fmt_m(pred['seat_high_m'])})")
    print(f"    Data: {n_th} AMC theatres{nat_str}, {pred['n_days']} day(s) [{days_str}]{shows_str}")

    # Per-day breakdown
    for day, details in sorted(pred["daily_details"].items(),
                                key=lambda x: x[1]["date"]):
        amc_m = details["amc_total"] / 1_000_000
        dom_m = details["domestic_mid"] / 1_000_000
        spd = details.get("avg_showings_per_cinema", 0)
        print(f"    {day} ({details['date']}): "
              f"AMC {fmt_m(amc_m)} → domestic {fmt_m(dom_m)} "
              f"[{details['n_theatres']} theatres, {spd:.1f} showings/cinema"
              f"{', ' + str(details['n_no_data']) + ' no data' if details['n_no_data'] else ''}]")

    # Polymarket
    poly = pred["poly_result"]
    if poly:
        print(f"  Polymarket:    {fmt_m(poly['ev']):>10}  "
              f"({fmt_m(poly['low'])} - {fmt_m(poly['high'])})")
        bb = poly["best_bracket"]
        vol_str = f"${poly['total_volume']:,.0f}" if poly['total_volume'] else "—"
        print(f"    Brackets: {len(poly['brackets'])}, vol {vol_str}")
        print(f"    Highest-prob: ${bb['low']:.0f}M-${bb['high']:.0f}M "
              f"({bb['p_yes']:.0%})")

    # Blended
    print(f"  PREDICTION:    {fmt_m(pred['blended_m']):>10}  "
          f"({fmt_m(pred['blend_low_m'])} - {fmt_m(pred['blend_high_m'])})")
    if poly:
        w_s = pred["w_seat"]
        w_p = pred["w_poly"]
        print(f"    Weights: {w_s:.0%} seat / {w_p:.0%} Polymarket")
        diff = pred["blended_m"] - poly["ev"]
        direction = "higher" if diff > 0 else "lower"
        print(f"    vs Polymarket: {'+' if diff > 0 else ''}{diff:,.1f}M {direction}")

    # Verbose: top theatres
    if verbose:
        print(f"\n  Top theatres by estimated revenue:")
        all_theatres = []
        for day, details in pred["daily_details"].items():
            for t in details.get("theatre_results", []):
                all_theatres.append({**t, "day": day})
        all_theatres.sort(key=lambda t: t["revenue"], reverse=True)
        for t in all_theatres[:20]:
            rev_k = t["revenue"] / 1000
            print(f"    {t['theatre_name'][:35]:<35} {t['day']:<10} "
                  f"{t['format']:<15} occ:{t['observed_occ']:.0%}→{t['avg_occupancy']:.0%} "
                  f"${rev_k:,.0f}K  ({t['total_showings']} shows)")


def print_history(cal):
    """Print historical predictions vs actuals."""
    history = cal.get("history", [])
    if not history:
        print("\nNo historical predictions yet. Use --actual to record results.")
        return

    print(f"\n{'='*70}")
    print(f"  Prediction History")
    print(f"{'='*70}")
    print(f"  {'Movie':<30} {'Predicted':>10} {'Actual':>10} {'Error':>8}")
    print(f"  {'─'*30} {'─'*10} {'─'*10} {'─'*8}")
    for h in history:
        pred_str = fmt_m(h["predicted_mid"])
        actual_str = fmt_m(h["actual"]) if h.get("actual") else "—"
        if h.get("actual") and h["predicted_mid"] > 0:
            err = (h["actual"] - h["predicted_mid"]) / h["predicted_mid"]
            err_str = f"{err:+.0%}"
        else:
            err_str = "—"
        print(f"  {h['movie'][:30]:<30} {pred_str:>10} {actual_str:>10} {err_str:>8}")

    factors = cal.get("calibration_factors", {})
    print(f"\n  Calibration: scale={factors.get('overall_scale_factor', 1.0):.4f}, "
          f"AMC share={factors.get('amc_market_share', DEFAULT_AMC_MARKET_SHARE):.2%}")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    verbose = "--verbose" in args or "-v" in args
    cal = load_calibration()

    # --history
    if "--history" in args:
        print_history(cal)
        return

    # --actual "Movie Name" 125.3
    if "--actual" in args:
        idx = args.index("--actual")
        if idx + 2 >= len(args):
            print("Usage: --actual \"Movie Name\" 125.3")
            return
        movie_name = args[idx + 1]
        actual_val = float(args[idx + 2])

        # Try to find the last prediction for this movie
        seat_data = load_seat_data()
        poly_data = load_polymarket_data()
        movie_match = None
        for m in seat_data:
            if movie_name.lower() in m.lower():
                movie_match = m
                break

        pred_mid = 0
        pred_low = 0
        pred_high = 0
        seat_raw = 0
        poly_ev = 0
        n_th = 0
        days = []

        if movie_match:
            pred = predict_movie(movie_match, seat_data[movie_match],
                                poly_data.get(movie_match, []), cal)
            if pred:
                pred_mid = pred["blended_m"]
                pred_low = pred["blend_low_m"]
                pred_high = pred["blend_high_m"]
                seat_raw = pred["amc_total_weekend"] / 1_000_000
                poly_ev = pred["poly_result"]["ev"] if pred["poly_result"] else 0
                n_th = pred["n_theatres_total"]
                days = list(pred["daily_estimates"].keys())

        record_actual(cal, movie_name, pred_mid, pred_low, pred_high,
                     seat_raw, poly_ev, actual_val, n_th, days)
        print(f"Recorded: {movie_name} actual = ${actual_val}M")
        print(f"Calibration updated → scale={cal['calibration_factors']['overall_scale_factor']:.4f}, "
              f"AMC share={cal['calibration_factors']['amc_market_share']:.2%}")
        return

    # Default: predict all movies
    seat_data = load_seat_data()
    poly_data = load_polymarket_data()
    theatre_counts = load_theatre_counts()

    if not seat_data:
        print("No seat data found. Run: python3 scraper.py --collect-links, then python3 scraper.py")
        return

    # Filter to a specific movie if requested
    movie_filter = None
    if "--movie" in args:
        idx = args.index("--movie")
        if idx + 1 < len(args):
            movie_filter = args[idx + 1].lower()

    print(f"\n{'='*70}")
    print(f"  Opening Weekend Box Office Predictions")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    factors = cal["calibration_factors"]
    print(f"  Calibration: scale={factors.get('overall_scale_factor', 1.0):.3f}, "
          f"AMC share={factors.get('amc_market_share', DEFAULT_AMC_MARKET_SHARE):.1%}")
    if theatre_counts:
        print(f"  National theatre counts: {', '.join(f'{m}: {c:,}' for m, c in theatre_counts.items())}")
    print(f"{'='*70}")

    for movie in sorted(seat_data.keys()):
        if movie_filter and movie_filter not in movie.lower():
            continue

        # Fuzzy match movie name to theatre_counts keys
        nat_count = theatre_counts.get(movie)
        if not nat_count:
            for tc_movie, count in theatre_counts.items():
                if tc_movie.lower() in movie.lower() or movie.lower() in tc_movie.lower():
                    nat_count = count
                    break

        pred = predict_movie(movie, seat_data[movie],
                            poly_data.get(movie, []), cal, verbose=verbose,
                            national_theatre_count=nat_count)
        if pred:
            print_prediction(pred, verbose=verbose)

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
