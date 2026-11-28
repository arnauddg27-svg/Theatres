"""Opening-weekend forecast that does not need AMC.

Why (2026-11-28): AMC's seat maps have been unreadable since 2026-11-19, and
every layer of predict.py's headline starts from AMC rows. The other chains'
counted seats (chain_census.py: Cinemark, Alamo, Harkins, Regal once its gate
passes) only nudged an AMC-based day, so with AMC dark they reached no
forecast at all while the lanes kept collecting.

What this does, per day of the weekend, with the best evidence available:

    reported gross              -> the actual
    played, not yet reported    -> the chains' counted seats
    not played yet              -> the day shape of earlier openings

and, for a Friday whose previews are reported, the film's own pre-sales pace
at those chains (chain_pace.py), averaged with the other Friday reads.

Seat counts are used two ways. Where the day before is already reported, the
count is carried: reported(day-1) x pooled(day) / pooled(day-1) over the same
chains, which cancels the film's own chain mix. That carry is only trusted
when the same chains' count of the reported day lands within CONSISTENCY of
the truth; a lane that lost a day (2026-11-06) fails that test and the day
falls back to the day-shape ratio. Where nothing before it is reported, the
pooled count stands on its national-share estimate.

Backtest (scripts/chain_forecast_backtest.py, openings 2026-09-25..11-20,
AMC left out of the pool, shares from the other weekends): see STAGE_SIGMA.

Nothing here reads a market price or a trade forecast: those are mixed in
afterwards by scripts/ensemble_forecast.py, so the paper-trading edge is
still measured against a number the market did not write.
"""
import csv
import json
import math
import os
import statistics

from datetime import datetime, timedelta, timezone

import chain_census as CC

DATA_DIR = CC.DATA_DIR
DAYS = ("Thursday", "Friday", "Saturday", "Sunday")
POOL = ("CNMK", "ALMO", "HARK")
# The chains' count of a day we already know must land within this band of the
# reported gross before the same chains are trusted for the next day (the
# census overlay's own factor clamp).
CONSISTENCY = (0.6, 1.6)
# A carried day further than this from the day-shape ratio is a data gap, not a film.
CARRY_VS_SHAPE = (0.5, 2.0)
# Log-weight of the carried seat read against the day-shape read on Saturday.
# Swept 2026-11-28 (0.5 / 0.67 / 0.8 / 1.0): 7.4 / 7.1 / 7.0 / 7.0% over all
# 26 films, and seats alone beat the even blend on the 13 films that have the
# carry (3.4% against 3.9%). Friday's reads are averaged with equal weights
# (0.3 / 0.5 / 0.7 / 1.0 on the seat read: flat within half a point).
SATURDAY_CARRY_WEIGHT = 0.75
CARRY_POOL_EXTRA = ()
# A chain's count of the day being carried must hold at least this share of
# the showings it counted the day before: a lane that missed part of the day
# reads low without failing the reference-day test. Saturday and Sunday list
# as many showings as the day before (The Hunger Games: 6,495 / 6,524).
MIN_TARGET_SHOWINGS = 0.85
# A show date counts as played once the last West-coast show has started and
# been read: 10:00 UTC the next morning. Before that the post-show lanes hold
# only the showings that already ended (matinees at 22:30Z), which the pooled
# estimate would read as the whole day.
DAY_COMPLETE_UTC_HOUR = 10
# Alamo and Harkins together sell about 3% of US tickets: too thin to stand
# for the country on their own (Cinemark alone is about 13%).
MIN_POOLED_SHARE = 0.08
MIN_LIBRARY = 20
MIN_GROUP_N = 8
GROUP_SHRINK_K = 10

# Evidence stage -> log-sd of (forecast / actual) in the backtest, n in the
# comment. Used for the band only; refit with scripts/chain_forecast_backtest.py.
STAGE_SIGMA = {
    "previews-reported": 0.25,     # n=24, mean miss 18.5% (live AMC-era headline 24%)
    "friday-seats": 0.24,          # n=24, mean miss 17%
    "friday-reported": 0.11,       # n=26, mean miss 8% (live 10%)
    "saturday-seats": 0.10,        # n=26, mean miss 7%
    "saturday-reported": 0.05,     # n=26, mean miss 3% (live 4%)
    "sunday-seats": 0.045,         # n=26, mean miss 2%
}


def _f(value):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _geo(values):
    values = [v for v in values if v and v > 0]
    if not values:
        return None
    return math.exp(sum(math.log(v) for v in values) / len(values))


# ─── Day shape of earlier openings ──────────────────────────────────────────
def load_library(comps_path=None, calibration_path=None, metadata=None):
    """[(sort_key, previews, friday, saturday, sunday, audience_type)] in $M.
    Friday excludes previews. Comps (2021+) sort before every tracked weekend."""
    rows = []
    try:
        with open(comps_path or os.path.join(DATA_DIR, "historical-comps.csv"), newline="") as fh:
            for r in csv.DictReader(fh):
                pv = _f(r.get("thursday_preview_m")) or 0.0
                fri, sat, sun = _f(r.get("friday_m")), _f(r.get("saturday_m")), _f(r.get("sunday_m"))
                if fri and sat and sun and fri - pv > 0:      # the comps' Friday includes previews
                    rows.append(("0000-" + str(r.get("release_year") or ""), pv, fri - pv, sat, sun,
                                 (r.get("audience_type") or "").strip()))
    except OSError:
        pass
    try:
        with open(calibration_path or os.path.join(DATA_DIR, "calibration.json")) as fh:
            history = json.load(fh).get("history") or []
    except (OSError, ValueError):
        history = []
    if metadata is None:
        try:
            metadata = CC.P.load_movie_metadata()
        except Exception:
            metadata = {}
    for e in history:
        d = e.get("daily_actuals") or {}
        if e.get("non_preview_thursday") or not all(_f(d.get(k)) for k in ("Friday", "Saturday", "Sunday")):
            continue
        meta = CC.P.movie_mapping_get(metadata or {}, e.get("movie") or "", None)
        rows.append((str(e.get("weekend_of") or ""), _f(d.get("Thursday")) or 0.0,
                     _f(d["Friday"]), _f(d["Saturday"]), _f(d["Sunday"]),
                     (getattr(meta, "audience_type", "") or "").strip()))
    return rows


def _shrunk(rows, group_rows, value, k=GROUP_SHRINK_K):
    """Group median pulled toward the all-film median with k films of weight."""
    overall = statistics.median(value(r) for r in rows)
    if len(group_rows) < MIN_GROUP_N:
        return overall
    n = len(group_rows)
    return (n * statistics.median(value(r) for r in group_rows) + k * overall) / (n + k)


def shape_ratios(weekend_of, library=None, audience_type=None):
    """Median day ratios over openings strictly before `weekend_of`, or None.
    With an audience type that has enough earlier openings, each ratio is that
    group's median shrunk toward the all-film median (a fan-driven opening is
    front-loaded: Friday / previews 1.7 against 2.4 overall)."""
    library = load_library() if library is None else library
    rows = [r for r in library if r[0] < str(weekend_of)]
    if len(rows) < MIN_LIBRARY:
        return None
    group = [r for r in rows if audience_type and r[5] == audience_type]
    with_previews = [r for r in rows if r[1] > 0]
    out = {
        "n": len(rows), "group_n": len(group) if len(group) >= MIN_GROUP_N else 0,
        "group": audience_type if len(group) >= MIN_GROUP_N else "",
        "sat_per_fri": _shrunk(rows, group, lambda r: r[3] / r[2]),
        "sun_per_sat": _shrunk(rows, group, lambda r: r[4] / r[3]),
    }
    if len(with_previews) >= MIN_LIBRARY:
        out["fri_per_previews"] = _shrunk(with_previews, [r for r in group if r[1] > 0], lambda r: r[2] / r[1])
    return out


# ─── Seat counts ────────────────────────────────────────────────────────────
def _usable(cells, day, shares, pool):
    return [c for c in pool
            if CC.present(c, (cells or {}).get(c)) and (shares.get(c) or {}).get(day)]


def pooled(cells, day, shares, pool=POOL, chains=None):
    """National $M implied by the pooled chains' counted seats on one day."""
    chains = _usable(cells, day, shares, pool) if chains is None else chains
    den = sum(shares[c][day] for c in chains)
    if not chains or den < MIN_POOLED_SHARE:
        return None, []
    return sum(cells[c]["dollars"] for c in chains) / den / 1e6, list(chains)


def carried(cells_by_day, shares, day, prev, prev_reported, pool=POOL):
    """reported(prev) x pooled(day) / pooled(prev) over the chains counted on
    both days, or (None, reason) when the counts cannot be trusted."""
    a, b = cells_by_day.get(day) or {}, cells_by_day.get(prev) or {}
    pool = tuple(pool) + tuple(c for c in CARRY_POOL_EXTRA if c not in pool)
    chains = [c for c in _usable(a, day, shares, pool) if c in _usable(b, prev, shares, pool)
              and a[c].get("showings", 0) >= MIN_TARGET_SHOWINGS * b[c].get("showings", 0)]
    if not chains or not prev_reported or prev_reported <= 0:
        return None, "no chain counted on both days"
    now, _ = pooled(a, day, shares, chains=chains)
    before, _ = pooled(b, prev, shares, chains=chains)
    if not now or not before:
        return None, "no chain counted on both days"
    check = before / prev_reported
    if not CONSISTENCY[0] <= check <= CONSISTENCY[1]:
        return None, (f"{prev} seat count is {check:.2f}x its reported gross "
                      f"(outside {CONSISTENCY[0]:g}-{CONSISTENCY[1]:g}): lane gap")
    return prev_reported * now / before, "+".join(chains)


# ─── The forecast ───────────────────────────────────────────────────────────
def weekend_forecast(reported, cells_by_day, shares, ratios, pool=POOL, pace_friday=None):
    """{mid_m, low_m, high_m, stage, days, basis} or None when no day is
    reported or counted (pre-release: not this module's stage).

    reported: {day: $M}; a Friday reported without a Thursday row holds its
    previews. cells_by_day: {day: {chain: cell}} from chain_census.
    pace_friday: chain_pace.friday_estimate() -- Friday from the film's own
    pre-sales pace, averaged with the other Friday reads."""
    reported = {d: v for d, v in ((d, _f((reported or {}).get(d))) for d in DAYS) if v is not None and v >= 0}
    cells_by_day = cells_by_day or {}
    shares = shares or {}
    if not ratios:
        return None
    seats = {d: pooled(cells_by_day.get(d), d, shares, pool) for d in DAYS}
    if not reported and not any(v for v, _ in seats.values()):
        return None
    days, stage = {}, None

    # Thursday previews
    if "Thursday" in reported:
        days["Thursday"] = (reported["Thursday"], "reported")
    elif "Friday" in reported:
        days["Thursday"] = (0.0, "inside Friday")
    elif seats["Thursday"][0]:
        days["Thursday"] = (seats["Thursday"][0], "seats " + "+".join(seats["Thursday"][1]))
    previews = days.get("Thursday", (None,))[0]

    # Friday
    if "Friday" in reported:
        days["Friday"] = (reported["Friday"], "reported")
        stage = "friday-reported"
    else:
        candidates, how = [], []
        count, chains = seats["Friday"]
        if count:
            thu_count = seats["Thursday"][0]
            thu = reported.get("Thursday")
            if thu and thu_count and CONSISTENCY[0] <= thu_count / thu <= CONSISTENCY[1]:
                # Half the film's Thursday chain skew carries to Friday: the
                # preview crowd is not the Friday crowd (full carry was worse).
                count *= math.sqrt(thu / thu_count)
                how.append("seats " + "+".join(chains) + " half-corrected by Thursday")
            else:
                how.append("seats " + "+".join(chains))
            candidates.append(count)
            stage = "friday-seats"
        if previews and previews > 0 and ratios.get("fri_per_previews"):
            candidates.append(previews * ratios["fri_per_previews"])
            how.append(f"previews x{ratios['fri_per_previews']:.2f}")
            stage = stage or "previews-reported"
        if pace_friday and pace_friday.get("friday_m") and reported.get("Thursday"):
            candidates.append(pace_friday["friday_m"])
            how.append(f"pre-sales pace {pace_friday.get('chains', '')}")
        friday = _geo(candidates)             # equal log-weights (swept: flat)
        if not friday:
            return None
        days["Friday"] = (friday, " and ".join(how))
    friday = days["Friday"][0]

    # Saturday
    shape_sat = friday * ratios["sat_per_fri"]
    if "Saturday" in reported:
        days["Saturday"] = (reported["Saturday"], "reported")
        stage = "saturday-reported"
    else:
        value, how = shape_sat, f"Friday x{ratios['sat_per_fri']:.2f}"
        if "Friday" in reported:
            est, note = carried(cells_by_day, shares, "Saturday", "Friday", reported["Friday"], pool)
            if est and CARRY_VS_SHAPE[0] <= est / shape_sat <= CARRY_VS_SHAPE[1]:
                value = math.exp(SATURDAY_CARRY_WEIGHT * math.log(est)
                                 + (1 - SATURDAY_CARRY_WEIGHT) * math.log(shape_sat))
                how = f"seats {note} carried from Friday, averaged with {how}"
                stage = "saturday-seats"
        elif seats["Saturday"][0] and stage == "friday-seats":
            value = math.sqrt(seats["Saturday"][0] * shape_sat)
            how = "seats " + "+".join(seats["Saturday"][1]) + f", averaged with {how}"
        days["Saturday"] = (value, how)
    saturday = days["Saturday"][0]

    # Sunday
    shape_sun = saturday * ratios["sun_per_sat"]
    if "Sunday" in reported:
        days["Sunday"] = (reported["Sunday"], "reported")
        stage = "complete" if {"Friday", "Saturday"} <= set(reported) else stage
    else:
        value, how = shape_sun, f"Saturday x{ratios['sun_per_sat']:.2f}"
        if "Saturday" in reported:
            est, note = carried(cells_by_day, shares, "Sunday", "Saturday", reported["Saturday"], pool)
            if est and CARRY_VS_SHAPE[0] <= est / shape_sun <= CARRY_VS_SHAPE[1]:
                value, how = est, f"seats {note} carried from Saturday"
                stage = "sunday-seats"
        days["Sunday"] = (value, how)

    mid = sum(v for v, _ in days.values())
    known = sum(v for d, (v, how) in days.items() if how in ("reported", "inside Friday"))
    sigma = STAGE_SIGMA.get(stage, 0.30)
    # The stage sd is on the weekend total; reported dollars are a floor.
    low = max(known, mid * math.exp(-1.2816 * sigma))
    high = max(mid, mid * math.exp(1.2816 * sigma)) if mid > known else mid
    basis = "; ".join(f"{d[:3]} ${v:.2f}M ({how})" for d, (v, how) in days.items())
    return {"mid_m": mid, "low_m": low, "high_m": high, "stage": stage or "previews-reported",
            "days": {d: {"value_m": v, "how": how} for d, (v, how) in days.items()},
            "reported_m": known, "basis": basis, "library_n": ratios.get("n"),
            "shape_group": ratios.get("group") or "", "shape_group_n": ratios.get("group_n") or 0}


def cells_for_movie(movie, weekend_of, chain_data=None, through_date=None):
    """{day: {chain: cell}} for the film's played dates."""
    chain_data = CC.dollars_for(weekend_of, through_date) if chain_data is None else chain_data
    by_date = CC.P.movie_mapping_get(chain_data or {}, movie, None) or {}
    dates = CC.weekend_dates(weekend_of)
    return {dates[date]: cells for date, cells in by_date.items()
            if date in dates and not (through_date and date > through_date)}


def last_complete_date(now=None):
    """Latest show date whose seat counts are final (see DAY_COMPLETE_UTC_HOUR)."""
    now = now or datetime.now(timezone.utc)
    return (now - timedelta(hours=DAY_COMPLETE_UTC_HOUR) - timedelta(days=1)).date().isoformat()


def for_movie(movie, weekend_of, reported, chain_data=None, through_date=None, library=None,
              audience_type=None, now=None):
    """Live entry point: shares from weekends strictly before this one. Seat
    counts of a day still in progress are left out (a dated replay passes
    `through_date` and keeps every date up to it)."""
    if not weekend_of or weekend_of < CC.CENSUS_FROM:
        return None
    through_date = through_date or last_complete_date(now)
    ratios = shape_ratios(weekend_of, library, audience_type)
    cells = cells_for_movie(movie, weekend_of, chain_data, through_date)
    shares = CC.shares_for(weekend_of, exclude_movie=movie) if cells else {}
    pool = POOL + (("REGL",) if cells and CC.regal_pool_ok(weekend_of) else ())
    return weekend_forecast(reported, cells, shares, ratios, pool=pool,
                            pace_friday=pace_for_movie(movie, weekend_of, reported))


_PACE_CACHE = {}


def pace_for_movie(movie, weekend_of, reported):
    """chain_pace.friday_estimate() for a film whose previews are reported and
    whose Friday is not, or None. Never raises: the pace read is an extra."""
    reported = reported or {}
    previews = _f(reported.get("Thursday"))
    if not previews or _f(reported.get("Friday")) is not None:
        return None
    try:
        import chain_pace
        import chain_presales
        if "inputs" not in _PACE_CACHE:
            _PACE_CACHE["inputs"] = (chain_pace.load_table(), CC.reported_daily(),
                                     set(chain_presales.load_actuals()))
        table, history, openers = _PACE_CACHE["inputs"]
        return chain_pace.friday_estimate(movie, weekend_of, previews, table, history, openers)
    except Exception:
        return None
