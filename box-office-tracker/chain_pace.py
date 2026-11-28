"""Opening Friday from each film's own pre-sales pace at the other chains.

Why (2026-11-28): once Thursday previews are reported, Friday was previews x
the median Friday/previews multiple of earlier openings. That multiple is the
most film-dependent number of the weekend (a fan-driven opening is 1.7, a
family one 4+), and the previews-reported forecast missed by 21%.

The lanes already hold a film-specific read of it. On Friday morning, per
chain:

    pace = seats reserved for Friday's showings / seats counted on Thursday

and over earlier openings the reported Friday / previews runs at a stable
multiple k of that pace, so

    Friday = reported previews x pace x k(chain)        (chains geo-averaged)

Alone it is no better than the median multiple (Friday miss 23% against 24%),
but its errors are different ones: averaged with it, the weekend miss at the
previews-reported stage falls from 21.0% to 17.3% leaving one weekend out
(17 openings 2026-10-02..11-20, better on 12), and from 28.3% to 20.5% when k
comes from earlier weekends only (the 10 later films, better on 7).
chain_forecast.py does that averaging.

The table (data/chain-pace.csv) gets one row per film and chain, appended by
the first forecast run after Friday 10:00 UTC; nothing is entered by hand.
"""
import csv
import math
import os
import re
import statistics
from collections import defaultdict
from datetime import datetime, time, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
TABLE_CSV = os.path.join(DATA_DIR, "chain-pace.csv")
FIELDS = ["weekend_of", "movie", "chain", "fri_pre", "fri_pre_n", "thu_final", "thu_n", "built_at"]
CHAINS = ("CNMK", "ALMO", "HARK")
CUTOFF_UTC = time(10, 0)             # Friday 05:00 ET: Thursday's shows are over everywhere
MIN_FRI_PRE, MIN_FRI_SHOWINGS = 200, 10
MIN_THU_FINAL, MIN_THU_SHOWINGS = 100, 5
MIN_TRAIN = 5


def movie_key(title):
    return re.sub(r"[^a-z0-9]", "", (title or "").lower())


def _f(value):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def cutoff_time(weekend_of):
    friday = datetime.strptime(str(weekend_of), "%Y-%m-%d").date()
    return datetime.combine(friday, CUTOFF_UTC, tzinfo=timezone.utc)


def build(weekend_of, lane_rows=None):
    """{(movie_title, chain): {fri_pre, fri_pre_n, thu_final, thu_n}}.

    Friday: each showing's last pre-sale read at or before the cutoff.
    Thursday: each showing's last read at or before the cutoff, the post-show
    count when there is one. `lane_rows(chain, weekend_of)` yields lane rows
    (default: chain_census's reader, live file plus archives)."""
    if lane_rows is None:
        import chain_census
        lane_rows = chain_census._lane_rows
    friday = datetime.strptime(str(weekend_of), "%Y-%m-%d").date()
    thu, fri = (friday - timedelta(days=1)).isoformat(), friday.isoformat()
    cut = cutoff_time(weekend_of).strftime("%Y-%m-%dT%H:%M:%S")
    out = {}
    for chain in CHAINS:
        fri_pre, thu_last = {}, {}
        for r in lane_rows(chain, weekend_of):
            show_date = r.get("show_date")
            if show_date not in (thu, fri):
                continue
            stamp = (r.get("snapshot_time") or "")[:19]
            if not stamp or stamp > cut:
                continue
            post = (r.get("row_kind") or "") == "post-show-census"
            key = (r.get("movie_title"), r.get("theatre_name"), r.get("showtime_id"))
            if show_date == fri:
                if not post and (key not in fri_pre or stamp > fri_pre[key][0]):
                    fri_pre[key] = (stamp, r)
            else:
                held = thu_last.get(key)
                held_post = bool(held) and (held[1].get("row_kind") or "") == "post-show-census"
                if not held or (post and not held_post) or (post == held_post and stamp > held[0]):
                    thu_last[key] = (stamp, r)
        for store, field, count in ((fri_pre, "fri_pre", "fri_pre_n"), (thu_last, "thu_final", "thu_n")):
            for (movie, _theatre, _sid), (_stamp, r) in store.items():
                seats = _f(r.get("reserved_seats"))
                if seats is None or seats < 0 or not movie:
                    continue
                cell = out.setdefault((movie, chain), defaultdict(float))
                cell[field] += seats
                cell[count] += 1
    return {k: dict(v) for k, v in out.items()}


def load_table(path=None):
    path = path or TABLE_CSV
    if not os.path.exists(path):
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def update_table(weekend_of, now=None, path=None, lane_rows=None):
    """Append this weekend's rows once the cutoff has passed and none are on
    file. Returns the number of rows added."""
    path = path or TABLE_CSV
    now = now or datetime.now(timezone.utc)
    if not weekend_of or now < cutoff_time(weekend_of):
        return 0
    if any(r.get("weekend_of") == weekend_of for r in load_table(path)):
        return 0
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = [dict(weekend_of=weekend_of, movie=movie, chain=chain, built_at=stamp,
                 fri_pre=round(cell.get("fri_pre", 0)), fri_pre_n=int(cell.get("fri_pre_n", 0)),
                 thu_final=round(cell.get("thu_final", 0)), thu_n=int(cell.get("thu_n", 0)))
            for (movie, chain), cell in sorted(build(weekend_of, lane_rows).items())]
    if not rows:
        return 0
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def pace(row):
    """Friday reserved / Thursday counted for one table row, or None when
    either side is too thin to mean anything."""
    fri, thu = _f(row.get("fri_pre")), _f(row.get("thu_final"))
    if (not fri or not thu or fri < MIN_FRI_PRE or thu < MIN_THU_FINAL
            or (_f(row.get("fri_pre_n")) or 0) < MIN_FRI_SHOWINGS
            or (_f(row.get("thu_n")) or 0) < MIN_THU_SHOWINGS):
        return None
    return fri / thu


def friday_estimate(movie, weekend_of, previews_m, table, reported, openers, exclude_weekends=None):
    """{friday_m, chains, n_train} or None.

    reported: {(weekend_of, movie_key): {day: $M}} (chain_census.reported_daily).
    openers: keys of graded standard openings, so holdovers and films that
    opened before Friday never train the multiple. Trains on weekends strictly
    before `weekend_of` (a backtest passes `exclude_weekends` instead)."""
    if not previews_m or previews_m <= 0:
        return None
    mk = movie_key(movie)
    mine = {r["chain"]: pace(r) for r in table
            if r.get("weekend_of") == weekend_of and movie_key(r.get("movie")) == mk}
    estimates, used, n_train = [], [], []
    for chain in CHAINS:
        if not mine.get(chain):
            continue
        logs = []
        for r in table:
            w = r.get("weekend_of") or ""
            if r.get("chain") != chain:
                continue
            if (w in exclude_weekends) if exclude_weekends is not None else not (w < weekend_of):
                continue
            key = (w, movie_key(r.get("movie")))
            days = reported.get(key) or {}
            p = pace(r)
            if key in openers and p and _f(days.get("Thursday")) and _f(days.get("Friday")):
                logs.append(math.log(days["Friday"] / days["Thursday"] / p))
        if len(logs) < MIN_TRAIN:
            continue
        estimates.append(previews_m * mine[chain] * math.exp(statistics.median(logs)))
        used.append(chain)
        n_train.append(len(logs))
    if not estimates:
        return None
    return {"friday_m": math.exp(sum(math.log(e) for e in estimates) / len(estimates)),
            "chains": "+".join(used), "n_train": min(n_train)}
