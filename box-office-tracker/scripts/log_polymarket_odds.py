#!/usr/bin/env python3
"""Append a timestamped snapshot of every live opening-weekend Polymarket
bracket to data/polymarket-odds-log.csv.

2026-10-24: polymarket-markets.csv keeps one row per bracket per DAY (the first
observation), so intraday moves were lost — Wildwood's $12-14M favourite at
Friday 15Z had flipped to $10-12M by Saturday and only one of the two prices
was on disk. This runs in finalize right after predict.py, so every logged
forecast has the market odds of the same moment next to it.

Standalone (stdlib only): finalize does not install playwright, which
scraper.py imports. Advisory: any error prints a ::warning:: and exits 0.

It then fills the poly_* columns of the prediction-log rows written within
ODDS_MATCH_MINUTES of a logged snapshot: which bracket our headline lands in
and the market's probability for it, the market favourite, and the market's
implied median (2026-10-24: "predictions should also have equivalent poly odds
recorded"). Films without a market keep the columns blank.

    python3 scripts/log_polymarket_odds.py               # snapshot + annotate
    python3 scripts/log_polymarket_odds.py --annotate-only
"""
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ODDS_LOG = os.path.join(DATA_DIR, "polymarket-odds-log.csv")
PREDICTION_LOG = os.path.join(DATA_DIR, "prediction-log.csv")
ODDS_MATCH_MINUTES = 90
POLY_FIELDS = ["poly_logged_at", "poly_event", "poly_bracket", "poly_bracket_prob",
               "poly_favorite", "poly_favorite_prob", "poly_implied_mid_m"]
SEARCH_URL = "https://gamma-api.polymarket.com/public-search"
FIELDS = ["logged_at", "weekend_of", "movie", "event_slug", "bracket", "yes_price",
          "best_bid", "best_ask", "last_trade", "volume", "market_id"]


def opening_weekend_friday(now):
    """Fri-Sun -> that Friday; Mon-Thu -> the coming Friday."""
    if now.weekday() >= 4:
        return (now - timedelta(days=now.weekday() - 4)).strftime("%Y-%m-%d")
    return (now + timedelta(days=4 - now.weekday())).strftime("%Y-%m-%d")


def event_weekend(ev, now):
    """The Friday on or before the market's end date (markets end Sun/Mon of
    the opening weekend); falls back to the calendar weekend of `now`."""
    try:
        end = datetime.fromisoformat(str(ev.get("endDate")).replace("Z", "+00:00"))
        return (end - timedelta(days=(end.weekday() - 4) % 7)).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return opening_weekend_friday(now)


def _get(url, params):
    req = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params)}",
                                 headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def fetch_events():
    # limit_per_type, not limit: the plain `limit` param returns 5 events, which
    # missed Ali G and Klara and the Sun on 2026-10-24.
    data = _get(SEARCH_URL, {"q": "opening weekend box office", "limit_per_type": 50,
                             "events_status": "active"})
    return data.get("events", []) if isinstance(data, dict) else (data or [])


def movie_name(title):
    title = (title or "").replace("“", '"').replace("”", '"')
    m = re.search(r'"([^"]+)"', title)
    return m.group(1).strip() if m else None


def _f(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return ""


def odds_rows(events, now):
    logged_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for ev in events:
        title = str(ev.get("title") or "")
        tl = title.lower()
        if ev.get("closed") or "opening weekend" not in tl or "box office" not in tl:
            continue
        movie = movie_name(title)
        if not movie:
            continue
        weekend = event_weekend(ev, now)
        for m in ev.get("markets") or []:
            if m.get("closed"):
                continue
            try:
                prices = json.loads(m.get("outcomePrices") or "[]")
            except ValueError:
                prices = []
            rows.append({
                "logged_at": logged_at, "weekend_of": weekend, "movie": movie,
                "event_slug": ev.get("slug", ""),
                "bracket": m.get("groupItemTitle") or m.get("question", ""),
                "yes_price": _f(prices[0]) if prices else "",
                "best_bid": _f(m.get("bestBid")), "best_ask": _f(m.get("bestAsk")),
                "last_trade": _f(m.get("lastTradePrice")), "volume": _f(m.get("volume")),
                "market_id": str(m.get("id", "")),
            })
    return rows


def append(rows, path=ODDS_LOG):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def title_key(title):
    text = re.sub(r"[^a-z0-9 ]", " ", (title or "").lower())
    text = re.sub(r"^(the|a|an)\s+", "", text.strip())
    return re.sub(r"\s+", " ", text).strip()


def bracket_range(label):
    """'<22m' -> (None, 22), '22m-25m' / '2-3M' -> (22, 25), '37m+' -> (37, None)."""
    text = (label or "").lower().replace("$", "").replace(" ", "")
    num = r"(\d+(?:\.\d+)?)m?"
    m = re.fullmatch(r"<" + num, text)
    if m:
        return None, float(m.group(1))
    m = re.fullmatch(num + r"-" + num, text)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.fullmatch(num + r"\+", text)
    if m:
        return float(m.group(1)), None
    return None


def market_summary(brackets, mid_m):
    """brackets: [(label, yes_price)] for one event at one moment."""
    parsed = []
    for label, price in brackets:
        rng = bracket_range(label)
        if rng is None or price in ("", None):
            continue
        parsed.append((rng[0] if rng[0] is not None else float("-inf"), rng, label, float(price)))
    if not parsed:
        return {}
    parsed.sort()
    total = sum(p for *_, p in parsed) or 1.0
    fav = max(parsed, key=lambda b: b[3])
    out = {"poly_favorite": fav[2], "poly_favorite_prob": round(fav[3], 4)}
    for _, (lo, hi), label, price in parsed:
        if (lo is None or mid_m >= lo) and (hi is None or mid_m < hi):
            out.update(poly_bracket=label, poly_bracket_prob=round(price, 4))
    # Implied median: walk the normalised CDF, interpolate inside the bracket;
    # open-ended ends borrow the width of their neighbour.
    widths = [hi - lo for _, (lo, hi), _, _ in parsed if lo is not None and hi is not None]
    width = widths[0] if widths else 1.0
    cum = 0.0
    for _, (lo, hi), _, price in parsed:
        share = price / total
        lo = max(0.0, hi - width) if lo is None else lo
        hi = lo + width if hi is None else hi
        if cum + share >= 0.5 and share > 0:
            out["poly_implied_mid_m"] = round(lo + (0.5 - cum) / share * (hi - lo), 2)
            break
        cum += share
    return out


def _ts(text):
    try:
        return datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None


def annotate_prediction_log(pred_path=PREDICTION_LOG, odds_path=ODDS_LOG):
    """Fill blank poly_* columns from the nearest odds snapshot (same film and
    weekend, within ODDS_MATCH_MINUTES). Returns the number of rows filled."""
    if not (os.path.exists(pred_path) and os.path.exists(odds_path)):
        return 0
    snaps = {}  # (weekend, film key) -> {logged_at: {slug: [(bracket, price, volume)]}}
    with open(odds_path, newline="") as f:
        for r in csv.DictReader(f):
            snaps.setdefault((r["weekend_of"], title_key(r["movie"])), {}) \
                 .setdefault(r["logged_at"], {}).setdefault(r["event_slug"], []) \
                 .append((r["bracket"], r["yes_price"], r.get("volume") or ""))
    with open(pred_path, newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    fields += [c for c in POLY_FIELDS if c not in fields]
    filled = 0
    for row in rows:
        if row.get("poly_logged_at"):
            continue
        by_time = snaps.get((row.get("weekend_of", ""), title_key(row.get("movie"))))
        when = _ts(row.get("logged_at"))
        try:
            mid = float(row.get("headline_mid_m") or 0)
        except ValueError:
            mid = 0
        if not by_time or when is None or mid <= 0:
            continue
        near = [(abs((_ts(t) - when).total_seconds()), t) for t in by_time if _ts(t)]
        near = [x for x in near if x[0] <= ODDS_MATCH_MINUTES * 60]
        if not near:
            continue
        at = min(near)[1]
        events = by_time[at]

        def weight(item):
            slug, brackets = item
            vol = sum(float(v) for _, _, v in brackets if v not in ("", None))
            return (vol, -len(slug))  # main event: most volume, else shortest slug
        slug, brackets = max(events.items(), key=weight)
        summary = market_summary([(b, p) for b, p, _ in brackets], mid)
        if not summary:
            continue
        row.update({k: "" for k in POLY_FIELDS})
        row.update(summary, poly_logged_at=at, poly_event=slug)
        filled += 1
    if filled:
        tmp = pred_path + ".tmp"
        with open(tmp, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, pred_path)
    return filled


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    now = datetime.now(timezone.utc)
    if "--annotate-only" not in argv:
        try:
            rows = odds_rows(fetch_events(), now)
        except Exception as exc:  # advisory
            print(f"::warning::Polymarket odds snapshot failed: {type(exc).__name__}: {exc}")
            rows = []
        if rows:
            append(rows)
            films = sorted({r["movie"] for r in rows})
            print(f"Polymarket odds: logged {len(rows)} brackets for {len(films)} film(s): {', '.join(films)}")
        else:
            print("Polymarket odds: no live opening-weekend brackets")
    try:
        n = annotate_prediction_log()
        print(f"Polymarket odds: filled poly_* on {n} prediction-log row(s)")
    except Exception as exc:  # advisory
        print(f"::warning::prediction-log poly annotation failed: {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
