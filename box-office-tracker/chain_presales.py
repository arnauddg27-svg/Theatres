"""Pre-release opening estimate from the other chains' pre-sales (no AMC).

Why (2026-11-28): with AMC unreadable the pre-release headline rests on a few
bridge reads, while Regal (through Fandango), Cinemark, Harkins and Alamo keep
selling and their lanes keep reading. This turns those pre-sales into a
number of their own, logged by scripts/ensemble_forecast.py beside the market
and the published trade forecast.

Method. At a fixed point of opening week (16:00 ET on Monday..Thursday) take,
per chain, the reserved seats per theatre read across the Thursday-Sunday
showings. For each chain fit, on earlier openings at the same cutoff,

    log(opening) = a + b * log(reserved per theatre) + c * log(national theatres)

and combine the chains' predictions weighted by 1 / residual variance, so a
noisy chain (Cinemark's sampled reads) counts for little without being
hand-picked out.

Result (2026-11-28): logged, not mixed. Leave-one-weekend-out on 2026 openings
(scripts/chain_presales_backtest.py) it misses by 34% on Thursday (n=31; the
AMC-era pre-sales headline: 34%) and nudges the trade forecast from 21.4% to
19.9%. Graded as it would have run -- trained on earlier weekends only, 22
openings since 2026-09-25 -- it adds nothing: with a market 9.4% -> 10.4%,
without one trade + model 20.0% against trade + seats 25.4%. So
ensemble_forecast.py records the estimate beside each pre-release forecast
(seats_mid_m) with a weight of 0, and the test is re-run as the table grows.

The features table (data/chain-presale-features.csv) is appended by
update_table() on every finalize run; nothing is entered by hand.
"""
import csv
import gzip
import glob
import json
import math
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, time, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
FEATURES_CSV = os.path.join(DATA_DIR, "chain-presale-features.csv")
FIELDS = ["weekend_of", "movie", "chain", "cutoff", "theatres", "showings", "reserved",
          "capacity", "scaled_reserved", "res_per_theatre", "national_theatres", "built_at"]
CHAINS = ("REGL", "CNMK", "HARK", "ALMO")
LANES = {  # chain -> (live file stem, archive directory)
    "REGL": ("fandango-pre-reservation-snapshots", "fandango-archive"),
    "CNMK": ("cinemark-pre-reservation-snapshots", "cinemark-archive"),
    "HARK": ("harkins-pre-reservation-snapshots", "harkins-archive"),
    "ALMO": ("alamo-pre-reservation-snapshots", "alamo-archive"),
}
CUTOFFS = {"mon": -4, "tue": -3, "wed": -2, "thu": -1}     # days from the opening Friday
CUTOFF_UTC = time(21, 0)                                    # 16:00 ET
MIN_THEATRES = 5
MIN_TRAIN = 10
csv.field_size_limit(10 ** 9)


def movie_key(title):
    return re.sub(r"[^a-z0-9]", "", (title or "").lower())


def _f(value):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def cutoff_time(weekend_of, name):
    friday = datetime.strptime(str(weekend_of), "%Y-%m-%d").date()
    return datetime.combine(friday + timedelta(days=CUTOFFS[name]), CUTOFF_UTC, tzinfo=timezone.utc)


def cutoff_at(weekend_of, when):
    """Name of the latest cutoff at or before `when` (aware datetime or ISO
    text), or None before Monday 16:00 ET of opening week."""
    if isinstance(when, str):
        try:
            when = datetime.strptime(when[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    passed = [n for n in CUTOFFS if cutoff_time(weekend_of, n) <= when]
    return max(passed, key=lambda n: CUTOFFS[n]) if passed else None


# ─── Features ───────────────────────────────────────────────────────────────
def _lane_files(chain, data_dir, archives):
    stem, archive = LANES[chain]
    files = [os.path.join(data_dir, stem + ".csv")]
    if archives:
        files += sorted(glob.glob(os.path.join(data_dir, archive, stem + "-*.csv.gz")))
    return [p for p in files if os.path.exists(p)]


def lane_features(weekend_of, cutoff_names=None, data_dir=None, archives=False, aliases=None):
    """{(movie_key, chain, cutoff): {movie, theatres, showings, reserved,
    capacity, scaled_reserved, res_per_theatre}} for one weekend.

    Per (film, chain, theatre) the latest run read at or before the cutoff;
    reserved and capacity summed over its Thursday-Sunday showings; a sampled
    run is scaled to the showings the theatre listed (discovered_showtimes)."""
    data_dir = data_dir or DATA_DIR
    aliases = aliases or {}
    friday = datetime.strptime(str(weekend_of), "%Y-%m-%d").date()
    wanted_dates = {(friday + timedelta(days=d)).isoformat() for d in (-1, 0, 1, 2)}
    cutoffs = {n: cutoff_time(weekend_of, n).strftime("%Y-%m-%dT%H:%M:%S")
               for n in (cutoff_names or CUTOFFS)}
    runs = {}          # (mk, chain, theatre, run_id) -> [latest_time, reserved, capacity, n, {date: discovered}]
    titles, seen = {}, set()
    for chain in CHAINS:
        for path in _lane_files(chain, data_dir, archives):
            opener = gzip.open(path, "rt", newline="") if path.endswith(".gz") else open(path, newline="")
            with opener as fh:
                for r in csv.DictReader(fh):
                    if r.get("weekend_of") != weekend_of or r.get("show_date") not in wanted_dates:
                        continue
                    if (r.get("chain") or "") != chain:
                        continue                      # the Fandango file also carries AMC bridge rows
                    key = (chain, r.get("run_id"), r.get("theatre_name"), r.get("showtime_id"), r.get("show_date"))
                    if key in seen:
                        continue
                    seen.add(key)
                    total, reserved = _f(r.get("total_seats")) or 0.0, _f(r.get("reserved_seats")) or 0.0
                    if total <= 0:
                        continue
                    mk = movie_key(r.get("movie_title"))
                    mk = aliases.get(mk, mk)
                    titles.setdefault(mk, r.get("movie_title"))
                    g = runs.setdefault((mk, chain, r.get("theatre_name"), r.get("run_id")), ["", 0.0, 0.0, 0, {}])
                    g[0] = max(g[0], (r.get("snapshot_time") or "")[:19])
                    g[1] += reserved
                    g[2] += total
                    g[3] += 1
                    try:
                        g[4][r["show_date"]] = max(g[4].get(r["show_date"], 0), int(r.get("discovered_showtimes") or 0))
                    except ValueError:
                        pass
    by_theatre = defaultdict(list)
    for (mk, chain, theatre, _run), g in runs.items():
        by_theatre[(mk, chain, theatre)].append(g)
    agg = defaultdict(lambda: [0.0, 0.0, 0, 0, 0.0])
    for (mk, chain, _theatre), items in by_theatre.items():
        for name, cut in cutoffs.items():
            ok = [g for g in items if g[0] and g[0] <= cut]
            if not ok:
                continue
            g = max(ok, key=lambda x: x[0])
            discovered = sum(g[4].values())
            scale = discovered / g[3] if discovered and discovered > g[3] else 1.0
            a = agg[(mk, chain, name)]
            a[0] += g[1]; a[1] += g[2]; a[2] += 1; a[3] += g[3]; a[4] += g[1] * scale
    out = {}
    for (mk, chain, name), a in agg.items():
        out[(mk, chain, name)] = {
            "movie": titles.get(mk, mk), "theatres": a[2], "showings": a[3], "reserved": round(a[0]),
            "capacity": round(a[1]), "scaled_reserved": round(a[4]),
            "res_per_theatre": round(a[4] / a[2], 2) if a[2] else 0.0}
    return out


def load_aliases(weekend_of, path=None):
    """{alias key: tracked title key} for one weekend (data/title-aliases.json)."""
    try:
        with open(path or os.path.join(DATA_DIR, "title-aliases.json")) as fh:
            films = (json.load(fh) or {}).get(weekend_of) or {}
    except (OSError, ValueError):
        return {}
    return {movie_key(name): movie_key(movie) for movie, names in films.items() if isinstance(names, list)
            for name in names}


def load_table(path=None):
    path = path or FEATURES_CSV
    if not os.path.exists(path):
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def update_table(weekend_of, now=None, national=None, path=None, data_dir=None, aliases=None):
    """Append the features of every cutoff of `weekend_of` that has passed and
    is not on file yet. `national`: {movie_key: national theatre count}.
    Returns the number of rows added."""
    path = path or FEATURES_CSV
    now = now or datetime.now(timezone.utc)
    existing = load_table(path)
    have = {(r["weekend_of"], movie_key(r["movie"]), r["chain"], r["cutoff"]) for r in existing}
    due = [n for n in CUTOFFS if cutoff_time(weekend_of, n) <= now]
    if not due:
        return 0
    rows = []
    aliases = load_aliases(weekend_of) if aliases is None else aliases
    for (mk, chain, name), feat in lane_features(weekend_of, due, data_dir=data_dir, aliases=aliases).items():
        if (weekend_of, mk, chain, name) in have or feat["theatres"] < 1:
            continue
        rows.append(dict(feat, weekend_of=weekend_of, chain=chain, cutoff=name,
                         national_theatres=(national or {}).get(mk) or "",
                         built_at=now.strftime("%Y-%m-%dT%H:%M:%SZ")))
    if not rows:
        return 0
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r["movie"], r["chain"], r["cutoff"])))
    return len(rows)


# ─── Model ──────────────────────────────────────────────────────────────────
def _ols(X, y):
    k = len(X[0])
    A = [[sum(row[i] * row[j] for row in X) + (1e-9 if i == j else 0.0) for j in range(k)] for i in range(k)]
    b = [sum(row[i] * yy for row, yy in zip(X, y)) for i in range(k)]
    for i in range(k):
        pivot = A[i][i]
        A[i] = [v / pivot for v in A[i]]
        b[i] /= pivot
        for r in range(k):
            if r != i and A[r][i]:
                factor = A[r][i]
                A[r] = [v - factor * w for v, w in zip(A[r], A[i])]
                b[r] -= factor * b[i]
    return b


def load_actuals(path=None):
    """{(weekend_of, movie_key): 3-day opening $M} from calibration.json."""
    try:
        with open(path or os.path.join(DATA_DIR, "calibration.json")) as fh:
            history = json.load(fh).get("history") or []
    except (OSError, ValueError):
        return {}
    # A film that opened before Friday sold its Thursday as a full day: its
    # pre-sales do not map to a 3-day opening the way the others' do.
    return {(e.get("weekend_of"), movie_key(e.get("movie"))): _f(e.get("actual_total"))
            for e in history if _f(e.get("actual_total")) and not e.get("non_preview_thursday")}


def _usable(row):
    rpt, theatres, national = _f(row.get("res_per_theatre")), _f(row.get("theatres")), _f(row.get("national_theatres"))
    if not rpt or rpt <= 0 or not theatres or theatres < MIN_THEATRES or not national or national <= 0:
        return None
    return math.log(rpt), math.log(national)


def estimate(movie, weekend_of, cutoff, table, actuals, exclude_weekends=None):
    """{mid_m, sigma, chains, n_train} or None. Trains on openings strictly
    before `weekend_of` (or, for a backtest, on every weekend not in
    `exclude_weekends`)."""
    mk = movie_key(movie)
    target = {r["chain"]: r for r in table
              if r.get("weekend_of") == weekend_of and movie_key(r.get("movie")) == mk and r.get("cutoff") == cutoff}
    parts = []
    for chain in CHAINS:
        x = _usable(target.get(chain) or {})
        if not x:
            continue
        train = []
        for r in table:
            if r.get("chain") != chain or r.get("cutoff") != cutoff:
                continue
            w = r.get("weekend_of") or ""
            if (w in exclude_weekends) if exclude_weekends is not None else not (w < weekend_of):
                continue
            xr, actual = _usable(r), actuals.get((w, movie_key(r.get("movie"))))
            if xr and actual and actual > 0:
                train.append((xr, math.log(actual)))
        if len(train) < MIN_TRAIN:
            continue
        coef = _ols([[1.0, xr[0], xr[1]] for xr, _y in train], [y for _xr, y in train])
        resid = [y - (coef[0] + coef[1] * xr[0] + coef[2] * xr[1]) for xr, y in train]
        var = sum(e * e for e in resid) / max(1, len(train) - 3)
        if var <= 0:
            continue
        parts.append((coef[0] + coef[1] * x[0] + coef[2] * x[1], var, chain, len(train)))
    if not parts:
        return None
    weight = sum(1.0 / v for _p, v, _c, _n in parts)
    return {"mid_m": math.exp(sum(p / v for p, v, _c, _n in parts) / weight),
            "sigma": math.sqrt(max(v for _p, v, _c, _n in parts)) if len(parts) == 1 else math.sqrt(
                sum(v for _p, v, _c, _n in parts) / len(parts)),
            "chains": "+".join(c for _p, _v, c, _n in parts), "n_train": min(n for *_x, n in parts),
            "cutoff": cutoff}
