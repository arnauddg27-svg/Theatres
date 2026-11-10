"""Turn a headline forecast into a probability for every Polymarket bracket.

The headline mid at a forecast stage has a graded error history: the live log
(data/prediction-log.csv) against calibration.json actuals gives, per stage,
the distribution of ln(actual / mid). Model it as lognormal:

    ln(actual) ~ Normal(ln(mid) + bias_stage, sigma_stage)

and integrate over each bracket. Both parameters are fitted at forecast time
from graded weekends strictly BEFORE the one being priced and never from the
film itself, so a backtest sees only what a live run would have seen. With
n ~ 10 per stage the fit is shrunk toward a prior (k = 4 on sigma, 6 on bias).

2026-10-26 graded history: sd of ln(actual/mid) presales 0.47, after-previews
0.35, after-friday 0.16, after-saturday 0.06, complete 0.03 (n = 10-11).
Stdlib only (finalize has no numpy).
"""
import csv
import json
import math
import os
import re
import statistics

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PREDICTION_LOG = os.path.join(DATA_DIR, "prediction-log.csv")
CALIBRATION_JSON = os.path.join(DATA_DIR, "calibration.json")

PRIOR_SIGMA = {"presales": 0.45, "after-previews": 0.32, "after-friday": 0.15,
               "after-saturday": 0.07, "after-sunday": 0.04, "complete": 0.03}
SIGMA_SHRINK_K = 4
BIAS_SHRINK_K = 6
MIN_FIT_N = 4


def movie_key(title):
    return re.sub(r"[^a-z0-9]", "", (title or "").lower())


def graded_log_ratios(pred_path=PREDICTION_LOG, cal_path=CALIBRATION_JSON):
    """{stage: [(weekend_of, movie_key, ln(actual/mid))]} using the LAST
    positive headline of each film at each stage."""
    actual = {}
    try:
        with open(cal_path) as f:
            for e in json.load(f).get("history", []) or []:
                if e.get("actual_total") and e.get("weekend_of") and e.get("movie") and not e.get("data_outage"):
                    actual[(e["weekend_of"], movie_key(e["movie"]))] = float(e["actual_total"])
    except (OSError, ValueError):
        return {}
    latest = {}
    try:
        with open(pred_path, newline="") as f:
            for r in csv.DictReader(f):
                try:
                    mid = float(r.get("headline_mid_m") or 0)
                except ValueError:
                    continue
                if mid > 0:
                    latest[(r.get("weekend_of"), movie_key(r.get("movie")), r.get("forecast_stage"))] = mid
    except OSError:
        return {}
    out = {}
    for (w, mk, stage), mid in latest.items():
        a = actual.get((w, mk))
        if a:
            out.setdefault(stage, []).append((w, mk, math.log(a / mid)))
    return out


def fit_stage(stage, weekend_of=None, exclude_movie=None, ratios=None):
    """(bias, sigma, n) for `stage` from graded weekends before `weekend_of`,
    excluding `exclude_movie`; shrunk toward the prior."""
    prior = PRIOR_SIGMA.get(stage, 0.30)
    if ratios is None:
        ratios = graded_log_ratios()
    ex = movie_key(exclude_movie) if exclude_movie else None
    xs = [x for w, mk, x in ratios.get(stage, [])
          if (not weekend_of or not w or w < weekend_of) and mk != ex]
    n = len(xs)
    if n < MIN_FIT_N:
        return 0.0, prior, n
    bias = statistics.median(xs) * n / (n + BIAS_SHRINK_K)
    var = statistics.pvariance(xs)
    sigma = math.sqrt((n * var + SIGMA_SHRINK_K * prior ** 2) / (n + SIGMA_SHRINK_K))
    return bias, max(sigma, 0.5 * prior), n


# ── EVERY-ROW FIT (2026-11-10 audit) ────────────────────────────────────────
# fit_stage() above measures the LAST headline of a stage, but a bet is placed
# on the FIRST headline of a stage that shows an edge — e.g. Sunday 07Z, before
# Saturday's reported gross arrives and the Sunday ratio takes over. Within a
# stage the early headlines err far more than the last one (after-Saturday
# 9.3% vs 4.5% MAE, after-Friday 17.7% vs 10.9%). Standardised by the last-row
# sigma, the 311 graded headlines since 2026-10-02 had sd(z) 1.59 after Friday,
# 1.33 after Saturday, 1.47 complete; 11% of after-Friday headlines fell beyond
# the stated 1% tail, and the 19 paper bets rated 95-100% won 68% of the time.
# fit_headline() uses every graded headline of the stage (one second moment per
# film, so a film logged 9 times counts once), and only headlines served by the
# same source path when at least MIN_FIT_N films have one — "sunday-ratio" and
# "stage-daily-evidence" are different instruments. Same data: sd(z) 0.92 /
# 1.07 / 1.00, tails 7% beyond the 10% mark and 1% beyond the 1% mark.
ROW_FIT_MODE = (os.environ.get("BRACKET_ROW_FIT_MODE") or "on").strip().lower()


def graded_row_ratios(pred_path=PREDICTION_LOG, cal_path=CALIBRATION_JSON, extra_actuals=None):
    """{stage: {(weekend_of, movie_key): [(source, ln(actual/mid)), ...]}} for
    every positive headline row of a graded film."""
    actual = {}
    try:
        with open(cal_path) as f:
            for e in json.load(f).get("history", []) or []:
                if e.get("actual_total") and e.get("weekend_of") and e.get("movie") and not e.get("data_outage"):
                    actual[(e["weekend_of"], movie_key(e["movie"]))] = float(e["actual_total"])
    except (OSError, ValueError):
        return {}
    actual.update(extra_actuals or {})
    out = {}
    try:
        with open(pred_path, newline="") as f:
            for r in csv.DictReader(f):
                try:
                    mid = float(r.get("headline_mid_m") or 0)
                except ValueError:
                    continue
                k = (r.get("weekend_of"), movie_key(r.get("movie")))
                if mid > 0 and k in actual:
                    out.setdefault(r.get("forecast_stage"), {}).setdefault(k, []).append(
                        (r.get("source") or "", math.log(actual[k] / mid)))
    except OSError:
        return {}
    return out


def fit_headline(stage, source=None, weekend_of=None, exclude_movie=None, rows=None):
    """(bias, sigma, n) for one headline at `stage` served by `source`, from
    every graded headline row of weekends before `weekend_of` (never the film
    itself). Bias is 0: the spread is measured about the headline, so a stage's
    systematic lean widens sigma instead of moving the centre on n ~ 20."""
    prior = PRIOR_SIGMA.get(stage, 0.30)
    if rows is None:
        rows = graded_row_ratios()
    ex = movie_key(exclude_movie) if exclude_movie else None
    films = {k: v for k, v in (rows.get(stage) or {}).items()
             if (not weekend_of or not k[0] or k[0] < weekend_of) and k[1] != ex}

    def moments(pick):
        out = []
        for v in films.values():
            xs = [x for src, x in v if pick(src)]
            if xs:
                out.append(sum(x * x for x in xs) / len(xs))
        return out

    ms = moments(lambda src: src == source) if source else []
    if len(ms) < MIN_FIT_N:
        ms = moments(lambda src: True)
    n = len(ms)
    if n < MIN_FIT_N:
        return 0.0, prior, n
    sigma = math.sqrt((sum(ms) + SIGMA_SHRINK_K * prior ** 2) / (n + SIGMA_SHRINK_K))
    return 0.0, max(sigma, 0.5 * prior), n


def _norm_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def bracket_probabilities(mid_m, brackets, bias, sigma):
    """{label: probability} for brackets given as [(label, lo_m, hi_m)] with
    None for an open end. Normalised so the listed brackets sum to 1."""
    if not mid_m or mid_m <= 0 or sigma <= 0:
        return {}
    mu = math.log(mid_m) + bias
    out = {}
    for label, lo, hi in brackets:
        p_lo = _norm_cdf((math.log(lo) - mu) / sigma) if lo and lo > 0 else 0.0
        p_hi = _norm_cdf((math.log(hi) - mu) / sigma) if hi else 1.0
        out[label] = max(0.0, p_hi - p_lo)
    total = sum(out.values())
    return {k: v / total for k, v in out.items()} if total > 0 else {}
