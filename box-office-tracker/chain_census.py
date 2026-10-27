"""Phase C — every chain's counted seats priced into dollars, individually
and pooled.

Until 2026-10-27 the headline turned ONLY AMC seats into dollars (AMC $ ÷
AMC share) and used the other chains just to estimate that share. The
census now counts ~40-50% of all US seats sold on a played day (AMC ~22%,
Cinemark ~16%, Alamo ~1%, Harkins ~2%, plus thin Regal / Webedia reads), so
each chain can carry its own dollar estimate and the pool can replace the
4x AMC scale-up with a ~2.3x one.

Per chain c on a played show date:
    dollars_c = sum over counted showings of seats_sold x price(format, daypart)
    national_c = dollars_c / s_c           (the chain's INDIVIDUAL read)
    pooled     = sum_c dollars_c / sum_c s_c over the chains present
where s_c is the chain's fitted dollar share — median of dollars_c / reported
daily gross over graded films, by day of week (Thursday previews are a
premium-format mix). A chain's absolute price level cancels inside s_c, so
only the format/daypart RELATIVE pricing matters (AMC rows carry formats;
Cinemark/Harkins rows do not and price as standard).

Sources (all post-show, i.e. walk-ins included): AMC seat-counts finals,
Cinemark post-show census (every showing), Alamo and Harkins post census.
Regal (Fandango near-show lower bound) and Webedia (occupancy % x assumed
room) are reported but never pooled. Archive-aware like every canonical
reader (data/<lane>-archive, data/seat-archive).
"""
import csv
import gzip
import os
import re
import statistics
from collections import defaultdict
from datetime import datetime, timedelta

import predict as P

DATA_DIR = P.DATA_DIR
POOLED_CHAINS = ("AMC", "CNMK", "ALMO", "HARK")
REPORT_CHAINS = POOLED_CHAINS + ("REGL", "WEBD")
LANES = {"RINV": "regal-showings.csv",
         "CNMK": "cinemark-pre-reservation-snapshots.csv",
         "ALMO": "alamo-pre-reservation-snapshots.csv",
         "HARK": "harkins-pre-reservation-snapshots.csv",
         "REGL": "fandango-pre-reservation-snapshots.csv",
         "WEBD": "webedia-pre-reservation-snapshots.csv"}
ARCHIVE_DIR = {"RINV": "regal-archive", "CNMK": "cinemark-archive", "ALMO": "alamo-archive", "HARK": "harkins-archive",
               "REGL": "fandango-archive", "WEBD": "webedia-archive"}
REGAL_NEAR_MIN = float(os.environ.get("CENSUS_REGAL_NEAR_MIN", "60"))
WEBEDIA_EST_SEATS = float(os.environ.get("WEBEDIA_EST_SEATS", "120"))
MIN_SHOWINGS = {"AMC": 50, "CNMK": 50, "ALMO": 10, "HARK": 10, "REGL": 50}   # below: not "present"
# REGAL (2026-10-27): Fandango's seat throttle allows ~2% of Regal showings, so
# Regal is a SAMPLE, not a census: near-showtime reads (sample=census, or a
# random read <= REGAL_MAX_LEAD_MIN before start) give mean $ per showing by
# daypart, regal_inventory.py gives every showing; dollars = sum over dayparts
# of mean x count. Pooled only once regal_pool_ok() says its graded record
# beats the pool without it.
REGAL_MAX_LEAD_MIN = 60
REGAL_MIN_READS = 30
REGAL_POOL_MIN_N = 8
DAYPARTS = ((0, 16), (16, 20), (20, 30))    # local start hour: matinee / evening / late
# Regime starts — a chain's count on a date before these is a partial read,
# not a census, and is neither pooled nor used to fit shares:
#   Cinemark: first every-showing post census was Mon 2026-09-28 (Sunday 09-27).
#   AMC Thu/Fri: links were a 5pm-11pm window until 2026-10-11 (10am since).
COMPLETE_FROM = {"CNMK": "2026-09-27", "AMC_THU_FRI": "2026-10-15"}
# First weekend the overlay prices at all: auto-fetched dailies and the
# multi-chain post lanes both start here; earlier weekends are AMC-only
# replays with hand-entered actuals and would only add noise to the shares.
CENSUS_FROM = "2026-09-25"
# AMC day with far fewer theatres than the film's best day = a late or partial
# link set (Sense and Sensibility's Friday: 116 rows after a Saturday market).
AMC_MIN_THEATRE_FRACTION = 0.6
SHARE_SHRINK_K = 3          # films of prior weight toward the all-day median
MIN_SHARE_N = 3
DAYS = ("Thursday", "Friday", "Saturday", "Sunday")


def movie_key(title):
    return re.sub(r"[^a-z0-9]", "", (title or "").lower())


def weekend_from_dates(dates):
    """Opening Friday for any Thu-Sun show date (None if no parseable date)."""
    for d in dates or ():
        try:
            dt = datetime.strptime(str(d)[:10], "%Y-%m-%d")
        except ValueError:
            continue
        return (dt + timedelta(days=(4 - dt.weekday()) if dt.weekday() <= 4 else -(dt.weekday() - 4))).strftime("%Y-%m-%d")
    return None


def weekend_dates(weekend_of):
    fri = datetime.strptime(weekend_of, "%Y-%m-%d")
    return {(fri + timedelta(days=o)).strftime("%Y-%m-%d"): d for d, o in zip(DAYS, (-1, 0, 1, 2))}


def _lane_rows(chain, weekend_of):
    fn = LANES[chain]
    paths = [os.path.join(DATA_DIR, ARCHIVE_DIR[chain], f"{fn[:-4]}-{weekend_of}.csv.gz"), os.path.join(DATA_DIR, fn)]
    for path in paths:
        if not os.path.exists(path):
            continue
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt", errors="replace", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("weekend_of") == weekend_of:
                    yield r


def _price(row, weekend_of, rank=None):
    rank = P.infer_format_rank(row) if rank is None else rank
    return P.price_for_row(row, rank, weekend_of, base="seat")


def chain_day_dollars(weekend_of, through_date=None):
    """{movie_title: {show_date: {chain: {seats, dollars, showings, theatres}}}}
    for played show dates (<= through_date when given)."""
    dates = weekend_dates(weekend_of)
    out = defaultdict(lambda: defaultdict(dict))

    def put(movie, date, chain, seats, dollars, showings, theatres):
        if through_date and date > through_date:
            return
        out[movie][date][chain] = {"seats": int(seats), "dollars": float(dollars),
                                   "showings": int(showings), "theatres": int(theatres)}

    # AMC: post-show finals, format-priced.
    seat_data = P.load_seat_data(weekend_of=weekend_of)
    for movie, by_date in (seat_data or {}).items():
        for date, rows in by_date.items():
            if date not in dates:
                continue
            seats = dollars = 0.0
            theatres, shows = set(), 0
            for r in rows:
                try:
                    sold = float(r.get("seats_sold") or 0)
                except ValueError:
                    continue
                if sold < 0:
                    continue
                seats += sold
                dollars += sold * _price(r, weekend_of)
                theatres.add(r.get("theatre_name"))
                shows += 1
            if shows:
                put(movie, date, "AMC", seats, dollars, shows, len(theatres))

    # Post-show census lanes: latest read per (theatre, showtime) wins.
    for chain in ("CNMK", "ALMO", "HARK"):
        latest = {}
        for r in _lane_rows(chain, weekend_of):
            if r.get("row_kind") != "post-show-census" or r.get("show_date") not in dates:
                continue
            k = (r.get("movie_title"), r.get("show_date"), r.get("theatre_name"), r.get("showtime_id"))
            if k not in latest or (r.get("snapshot_time") or "") > (latest[k].get("snapshot_time") or ""):
                latest[k] = r
        agg = defaultdict(lambda: [0.0, 0.0, 0, set()])
        for (movie, date, th, _sid), r in latest.items():
            try:
                sold = float(r.get("reserved_seats") or 0)
            except ValueError:
                continue
            a = agg[(movie, date)]
            a[0] += sold
            a[1] += sold * _price(r, weekend_of, rank=P.infer_format_rank(r))
            a[2] += 1
            a[3].add(th)
        for (movie, date), (seats, dollars, shows, ths) in agg.items():
            put(movie, date, chain, seats, dollars, shows, len(ths))

    # Regal, estimated: near-showtime sample x full showing inventory.
    est = regal_day_dollars(weekend_of, dates, through_date)
    for (movie, date), cell in est.items():
        put(movie, date, "REGL", cell["seats"], cell["dollars"], cell["showings"], cell["theatres"])
        if "REGL" in out[movie].get(date, {}):
            out[movie][date]["REGL"]["sampled"] = cell["sampled"]
    # Regal without an inventory for the day: the old lower bound (latest read
    # within REGAL_NEAR_MIN of showtime), reported only.
    near = {}
    for r in _lane_rows("REGL", weekend_of):
        if (r.get("chain") or "").upper() != "REGL" or r.get("show_date") not in dates:
            continue
        try:
            if float(r.get("minutes_until_showtime") or 1e9) > REGAL_NEAR_MIN:
                continue
        except ValueError:
            continue
        k = (r.get("movie_title"), r.get("show_date"), r.get("theatre_name"), r.get("showtime_id"))
        if k not in near or (r.get("snapshot_time") or "") > (near[k].get("snapshot_time") or ""):
            near[k] = r
    agg = defaultdict(lambda: [0.0, 0.0, 0, set()])
    for (movie, date, th, _sid), r in near.items():
        try:
            sold = float(r.get("reserved_seats") or 0)
        except ValueError:
            continue
        a = agg[(movie, date)]
        a[0] += sold; a[1] += sold * _price(r, weekend_of); a[2] += 1; a[3].add(th)
    for (movie, date), (seats, dollars, shows, ths) in agg.items():
        if (movie, date) not in est:
            put(movie, date, "REGL", seats, dollars, shows, len(ths))
            if "REGL" in out[movie].get(date, {}):
                out[movie][date]["REGL"]["lower_bound"] = True

    # Webedia: occupancy % only -> assumed room size. Reported, not pooled.
    wl = {}
    for r in _lane_rows("WEBD", weekend_of):
        if r.get("row_kind") != "post-show-census" or r.get("show_date") not in dates:
            continue
        k = (r.get("movie_title"), r.get("show_date"), r.get("showtime_id"))
        if k not in wl or (r.get("snapshot_time") or "") > (wl[k].get("snapshot_time") or ""):
            wl[k] = r
    agg = defaultdict(lambda: [0.0, 0.0, 0, set()])
    for (movie, date, _sid), r in wl.items():
        try:
            sold = float(r.get("occupancy_pct") or 0) / 100.0 * WEBEDIA_EST_SEATS
        except ValueError:
            continue
        a = agg[(movie, date)]
        a[0] += sold; a[1] += sold * _price(r, weekend_of); a[2] += 1; a[3].add(r.get("theatre_name"))
    for (movie, date), (seats, dollars, shows, ths) in agg.items():
        put(movie, date, "WEBD", seats, dollars, shows, len(ths))
    for movie in out:
        mark_complete(out[movie])
    return out


def present(chain, cell):
    if chain == "REGL" and (not cell or cell.get("lower_bound") or cell.get("sampled", 0) < REGAL_MIN_READS):
        return False
    return bool(cell) and cell.get("complete", True) and cell.get("showings", 0) >= MIN_SHOWINGS.get(chain, 10)


def _hour(label):
    try:
        h, m = str(label or "").strip()[:5].split(":")
        return int(h) + int(m) / 60.0
    except ValueError:
        return None


def _daypart(hour):
    for i, (lo, hi) in enumerate(DAYPARTS):
        if hour is not None and lo <= hour < hi:
            return i
    return None


def regal_day_dollars(weekend_of, dates, through_date=None):
    """{(movie, date): {seats, dollars, showings, theatres, sampled}} for film-
    days with a Regal inventory. Pure over the two lane files."""
    inv = {}
    for r in _lane_rows("RINV", weekend_of):
        date = r.get("show_date")
        if date not in dates or (through_date and date > through_date):
            continue
        k = (r.get("movie_title"), date)
        inv.setdefault(k, {})[(r.get("theatre_name"), r.get("showtime_id"))] = _daypart(_hour(r.get("showtime")))
    if not inv:
        return {}
    reads = {}
    for r in _lane_rows("REGL", weekend_of):
        if (r.get("chain") or "").upper() != "REGL" or r.get("row_kind") == "regal-inventory":
            continue
        note = r.get("notes") or ""
        if "sample=priority" in note or "sample=bridge" in note:
            continue
        try:
            lead = float(r.get("minutes_until_showtime") or 1e9)
            sold = float(r.get("reserved_seats") or 0)
        except ValueError:
            continue
        if "sample=census" not in note and lead > REGAL_MAX_LEAD_MIN:
            continue
        k = (r.get("movie_title"), r.get("show_date"), r.get("theatre_name"), r.get("showtime_id"))
        if k not in reads or (r.get("snapshot_time") or "") > (reads[k][0].get("snapshot_time") or ""):
            reads[k] = (r, sold)
    by = {}
    for (movie, date, _th, _sid), (r, sold) in reads.items():
        if (movie, date) not in inv:
            continue
        part = _daypart(_hour(r.get("showtime")))
        cell = by.setdefault((movie, date), {})
        cell.setdefault(part, []).append((sold, sold * _price(r, weekend_of)))
    out = {}
    for k, perfs in inv.items():
        sample = by.get(k) or {}
        allr = [x for xs in sample.values() for x in xs]
        if not allr:
            continue
        mean_all_s = sum(a for a, _ in allr) / len(allr)
        mean_all_d = sum(b for _, b in allr) / len(allr)
        counts = {}
        for part in perfs.values():
            counts[part] = counts.get(part, 0) + 1
        seats = dollars = 0.0
        for part, n in counts.items():
            xs = sample.get(part) or []
            if len(xs) >= 3:
                seats += n * sum(a for a, _ in xs) / len(xs)
                dollars += n * sum(b for _, b in xs) / len(xs)
            else:
                seats += n * mean_all_s
                dollars += n * mean_all_d
        out[k] = {"seats": seats, "dollars": dollars, "showings": len(perfs),
                  "theatres": len({th for th, _ in perfs}), "sampled": len(allr)}
    return out


def mark_complete(by_date):
    """Flag each (date, chain) cell complete/partial per COMPLETE_FROM and the
    AMC theatre-fraction rule. Mutates and returns `by_date` for one film."""
    amc_max = max((c.get("AMC", {}).get("theatres", 0) for c in by_date.values()), default=0)
    for date, chains in by_date.items():
        dow = datetime.strptime(date, "%Y-%m-%d").weekday()   # Thu=3, Fri=4
        for chain, cell in chains.items():
            ok = True
            if chain == "CNMK" and date < COMPLETE_FROM["CNMK"]:
                ok = False
            if chain == "AMC":
                if dow in (3, 4) and date < COMPLETE_FROM["AMC_THU_FRI"]:
                    ok = False
                if amc_max and cell.get("theatres", 0) < AMC_MIN_THEATRE_FRACTION * amc_max:
                    ok = False
            cell["complete"] = ok
    return by_date


def reported_daily(weekends=None):
    """{(weekend_of, movie_key): {day: gross_m}} from daily-actual-overrides
    (latest as_of per day), folding nothing: The Numbers splits previews."""
    out = defaultdict(dict)
    latest = {}
    path = os.path.join(DATA_DIR, "daily-actual-overrides.csv")
    if not os.path.exists(path):
        return out
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if weekends and r.get("weekend_of") not in weekends:
                continue
            if (r.get("status") or "reported") != "reported":
                continue
            try:
                g = float(r.get("gross_m"))
            except (TypeError, ValueError):
                continue
            k = (r["weekend_of"], movie_key(r["movie_title"]), r["day_of_week"])
            if r.get("as_of_date", "") >= latest.get(k, ("", 0))[0]:
                latest[k] = (r.get("as_of_date", ""), g)
    for (w, mk, d), (_, g) in latest.items():
        out[(w, mk)][d] = g
    return out


def share_samples(weekends, dollars_by_weekend=None, actuals=None):
    """[(weekend, movie_key, day, chain, dollars_c / gross)] over graded film-days."""
    actuals = reported_daily(weekends) if actuals is None else actuals
    samples = []
    for w in weekends:
        cd = (dollars_by_weekend or {}).get(w) or chain_day_dollars(w)
        dates = weekend_dates(w)
        for movie, by_date in cd.items():
            mk = movie_key(movie)
            for date, chains in by_date.items():
                day = dates[date]
                gross = (actuals.get((w, mk)) or {}).get(day)
                if not gross or gross <= 0:
                    continue
                for chain, cell in chains.items():
                    if chain in POOLED_CHAINS + ("REGL",) and present(chain, cell):
                        samples.append((w, mk, day, chain, cell["dollars"] / (gross * 1e6)))
    return samples


def fit_shares(samples, exclude=None):
    """{chain: {day: share}} — median by (chain, day), shrunk toward the
    chain's all-day median with SHARE_SHRINK_K films of weight; films in
    `exclude` ({(weekend, movie_key)}) are left out (leave-one-out)."""
    exclude = exclude or set()
    by = defaultdict(list)
    allday = defaultdict(list)
    for w, mk, day, chain, s in samples:
        if (w, mk) in exclude:
            continue
        by[(chain, day)].append(s)
        allday[chain].append(s)
    out = defaultdict(dict)
    for chain, xs in allday.items():
        prior = statistics.median(xs) if xs else None
        if prior is None:
            continue
        for day in DAYS:
            ys = by.get((chain, day), [])
            n = len(ys)
            med = statistics.median(ys) if n else prior
            out[chain][day] = (n * med + SHARE_SHRINK_K * prior) / (n + SHARE_SHRINK_K) if n >= MIN_SHARE_N else prior
    return out


def estimates(chains_cell, day, shares, pooled=POOLED_CHAINS):
    """Per-chain implied national ($M) and the pooled estimate for one film-day."""
    out = {"chains": {}, "pooled_m": None, "pooled_share": None, "pooled_chains": []}
    num = den = 0.0
    for chain, cell in (chains_cell or {}).items():
        s = (shares.get(chain) or {}).get(day)
        if not s:
            continue
        national = cell["dollars"] / s / 1e6
        out["chains"][chain] = {"dollars_m": cell["dollars"] / 1e6, "seats": cell["seats"],
                               "share": s, "national_m": national, "present": present(chain, cell)}
        if chain in pooled and present(chain, cell):
            num += cell["dollars"]
            den += s
            out["pooled_chains"].append(chain)
    if den > 0:
        out["pooled_m"] = num / den / 1e6
        out["pooled_share"] = den
    return out


# ─── Forecast layer ─────────────────────────────────────────────────────────
_DOLLARS_CACHE = {}
_SAMPLES_CACHE = {}
FACTOR_CLAMP = (0.6, 1.6)


def dollars_for(weekend_of, through_date=None):
    key = (weekend_of, through_date)
    if key not in _DOLLARS_CACHE:
        _DOLLARS_CACHE[key] = chain_day_dollars(weekend_of, through_date=through_date)
    return _DOLLARS_CACHE[key]


def shares_for(weekend_of, exclude_movie=None):
    """Per-chain day shares fitted on reported weekends strictly BEFORE
    `weekend_of` (leak-free for live and replay alike), minus the film."""
    if weekend_of not in _SAMPLES_CACHE:
        actuals = reported_daily()
        weekends = sorted({w for (w, _mk) in actuals if CENSUS_FROM <= w < weekend_of})
        _SAMPLES_CACHE[weekend_of] = share_samples(weekends, {w: dollars_for(w) for w in weekends}, actuals)
    samples = _SAMPLES_CACHE[weekend_of]
    excl = {(w, mk) for (w, mk, *_r) in samples if mk == movie_key(exclude_movie)} if exclude_movie else set()
    return fit_shares(samples, exclude=excl)


_REGAL_GATE_CACHE = {}


def regal_pool_ok(weekend_of):
    """True when, over graded film-days BEFORE `weekend_of`, adding Regal's
    estimate to the pool lowered the mean |log error| vs the 4-chain pool
    (shares leave-one-film-out), on at least REGAL_POOL_MIN_N film-days. The
    backtest gate runs in code, so Regal joins the forecast on its own
    record — no manual switch."""
    if weekend_of in _REGAL_GATE_CACHE:
        return _REGAL_GATE_CACHE[weekend_of]
    import math
    actuals = reported_daily()
    weekends = sorted({w for (w, _mk) in actuals if CENSUS_FROM <= w < (weekend_of or "")})
    samples = share_samples(weekends, {w: dollars_for(w) for w in weekends}, actuals)
    e4, e5 = [], []
    for w in weekends:
        dates = weekend_dates(w)
        for movie, by_date in dollars_for(w).items():
            mk = movie_key(movie)
            shares = fit_shares(samples, exclude={(w, mk)})
            for date, chains in by_date.items():
                gross = (actuals.get((w, mk)) or {}).get(dates[date])
                if not gross or not present("REGL", chains.get("REGL")):
                    continue
                a = estimates(chains, dates[date], shares)
                b = estimates(chains, dates[date], shares, pooled=POOLED_CHAINS + ("REGL",))
                if a["pooled_m"] and b["pooled_m"] and "REGL" in b["pooled_chains"]:
                    e4.append(abs(math.log(a["pooled_m"] / gross)))
                    e5.append(abs(math.log(b["pooled_m"] / gross)))
    ok = len(e5) >= REGAL_POOL_MIN_N and sum(e5) < sum(e4)
    _REGAL_GATE_CACHE[weekend_of] = ok
    return ok


def layer_for_movie(movie, weekend_of, chain_data=None, through_date=None):
    """{day_name: {date, pooled_m, pooled_share, chains, n_fit}} for the
    film's played dates with a pooled census estimate, or {}."""
    if not weekend_of or weekend_of < CENSUS_FROM:
        return {}
    chain_data = dollars_for(weekend_of, through_date) if chain_data is None else chain_data
    by_date = P.movie_mapping_get(chain_data or {}, movie, None)
    if not by_date:
        return {}
    shares = shares_for(weekend_of, exclude_movie=movie)
    if not shares:
        return {}
    dates = weekend_dates(weekend_of)
    pooled = POOLED_CHAINS + (("REGL",) if regal_pool_ok(weekend_of) else ())
    out = {}
    for date, chains in by_date.items():
        day = dates.get(date)
        if not day or (through_date and date > through_date):
            continue
        est = estimates(chains, day, shares, pooled=pooled)
        if est["pooled_m"]:
            est["date"] = date
            out[day] = est
    return out


def apply_to_prediction(pred, layer, weight, carry, clamp=FACTOR_CLAMP):
    """Pure: for each played, unreported day, the factor that moves the model
    day toward the pooled census estimate in log space (weight = share of the
    move). Returns (delta_played_m, carry_factor, per_day_info). Nothing in
    `pred` is mutated — the assembly may run more than once per film and the
    LAST run's headline is the one served, so the overlay must be re-derivable
    from the untouched day details every time. The carry factor (geometric
    mean of the day factors) is for the still-projected remainder: the chain
    mix a film shows on its played days is the mix it keeps all weekend."""
    import math
    details = pred.get("daily_details") or {}
    info, delta, logs = {}, 0.0, []
    for day, est in (layer or {}).items():
        d = details.get(day)
        if not d or d.get("actual_override"):
            continue
        model_m = (float(d.get("domestic_mid") or 0)) / 1e6
        pooled_m = est.get("pooled_m")
        if model_m <= 0 or not pooled_m:
            continue
        raw = pooled_m / model_m
        f = max(clamp[0], min(clamp[1], math.exp(weight * math.log(raw))))
        delta += model_m * (f - 1.0)
        logs.append(math.log(f))
        info[day] = {"model_m": model_m, "pooled_m": pooled_m, "blended_m": model_m * f, "factor": f,
                     "raw_ratio": raw, "pooled_share": est.get("pooled_share"),
                     "pooled_chains": est.get("pooled_chains"), "chains": est.get("chains")}
    # Carry from the regular days only: a preview night's audience (fans,
    # premium formats) is not the weekend's chain mix. Thursday carries only
    # when it is the sole played day.
    carry_logs = [math.log(v["factor"]) for d, v in info.items() if d != "Thursday"] or logs
    carry_f = math.exp(sum(carry_logs) / len(carry_logs)) if (carry_logs and carry) else 1.0
    return delta, carry_f, info
