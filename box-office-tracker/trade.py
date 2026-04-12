#!/usr/bin/env python3
"""
Box Office Polymarket Trading Bot
===================================
Compares our seat-based box office prediction against Polymarket bracket
market prices and places trades where we have edge.

Uses a normal-distribution model of our confidence interval to calculate
implied probability for each bracket, then buys brackets where our
implied probability exceeds the market price by more than MIN_EDGE.

Pipeline:
  1. Load credentials from .env (same as SwissTony)
  2. Connect to Polymarket (CLOB + Gamma API)
  3. Find active opening-weekend box office bracket events
  4. For each movie: run prediction, calculate edge, place trades
  5. Log everything to SQLite

Usage:
    python3 trade.py                  # Dry run (default)
    DRY_RUN=false python3 trade.py    # Live trading
    python3 trade.py --status         # Show open trades and PnL
    python3 trade.py --movie "X"      # Single movie only
"""

import json
import logging
import os
import sys
from datetime import datetime
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from polymarket_client import PolymarketClient  # noqa: E402

# Local imports
from strategy import (  # noqa: E402
    find_edge_brackets, size_trades, parse_bracket_range,
    analyze_distribution, format_distribution,
)
from trade_log import TradeLog  # noqa: E402
from predict import (  # noqa: E402
    load_seat_data, load_polymarket_data, load_calibration, predict_movie, fmt_m,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

GAMMA_HOST = "https://gamma-api.polymarket.com"
CLOB_HOST = "https://clob.polymarket.com"


# ── Config ──────────────────────────────────────────────────────────────────

def load_trade_config() -> dict:
    """Load trading config from env vars."""
    load_dotenv()
    # Check .env files in order: script dir, parent dir, then VPS persistent store
    for env_path in [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.expanduser("~/.polymarket.env"),   # persistent on EU VPS, survives GHA checkout
        "/home/gha/.polymarket.env",               # when running as root/other user on VPS
    ]:
        if os.path.exists(env_path):
            load_dotenv(env_path)

    private_key = os.environ.get("POLYMARKET_PRIVATE_KEY", "").strip() or None
    funder = os.environ.get("POLYMARKET_FUNDER_ADDRESS", "").strip() or None
    dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"

    if not dry_run and (not private_key or not funder):
        raise ValueError(
            "POLYMARKET_PRIVATE_KEY and POLYMARKET_FUNDER_ADDRESS required "
            "when DRY_RUN=false"
        )

    return {
        "private_key": private_key,
        "funder": funder,
        "dry_run": dry_run,
        "box_office_pct": float(os.environ.get("BOX_OFFICE_PCT", "0.20")),
        "min_edge": float(os.environ.get("BOX_OFFICE_MIN_EDGE", "0.05")),
        "chain_id": int(os.environ.get("CHAIN_ID", "137")),
        "signature_type": int(os.environ.get("SIGNATURE_TYPE", "1")),
    }


# ── Polymarket Discovery ───────────────────────────────────────────────────

def fetch_box_office_events() -> list[dict]:
    """Find active opening-weekend box office events on Polymarket Gamma API.

    Returns raw event dicts with full market data including clobTokenIds.
    """
    url = (
        f"{GAMMA_HOST}/events?active=true&closed=false&limit=500"
        "&order=volume24hr&ascending=false"
    )
    req = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 BoxOfficeTracker/1.0",
    })
    resp = urlopen(req, timeout=15)
    events = json.loads(resp.read().decode())

    box_office = []
    for e in events:
        title_lower = (e.get("title") or "").lower()
        if "opening weekend" not in title_lower or "box office" not in title_lower:
            continue

        # Extract movie name from quoted title
        raw_title = e.get("title", "").replace("\u201c", '"').replace("\u201d", '"')
        movie_name = None
        if '"' in raw_title:
            parts = raw_title.split('"')
            if len(parts) >= 3:
                movie_name = parts[1]

        box_office.append({
            "event_id": str(e.get("id", "")),
            "title": movie_name or raw_title,
            "slug": e.get("slug", ""),
            "markets": e.get("markets", []),
            "total_volume": sum(
                float(m.get("volume", 0) or 0)
                for m in e.get("markets", [])
            ),
        })

    return box_office


def enrich_with_orderbook(poly_client: PolymarketClient,
                          markets: list[dict]) -> list[dict]:
    """Fetch CLOB orderbook prices for each market's outcomes.

    Updates each market dict in-place with live best_ask prices.
    Returns markets that have valid orderbook data.
    """
    enriched = []
    for mkt in markets:
        token_ids_raw = mkt.get("clobTokenIds", "")
        if isinstance(token_ids_raw, str):
            try:
                token_ids = json.loads(token_ids_raw)
            except (json.JSONDecodeError, TypeError):
                continue
        elif isinstance(token_ids_raw, list):
            token_ids = token_ids_raw
        else:
            continue

        if not token_ids:
            continue

        # Fetch orderbook for YES token
        yes_token = token_ids[0]
        try:
            book = poly_client.clob.get_order_book(yes_token)
            if book.asks:
                live_ask = float(book.asks[0].price)
                ask_size = float(book.asks[0].size)
                # Store live prices on the market dict
                mkt["_live_ask"] = live_ask
                mkt["_live_ask_size"] = ask_size
                enriched.append(mkt)
                logger.info(
                    f"  Orderbook: {mkt.get('question', '')[:60]} "
                    f"ask={live_ask:.3f} size={ask_size:.0f}"
                )
            else:
                # Try midpoint fallback
                mid_result = poly_client.clob.get_midpoint(yes_token)
                mid = float(mid_result.get("mid", 0))
                if mid > 0:
                    mkt["_live_ask"] = min(round(mid + 0.005, 3), 0.99)
                    mkt["_live_ask_size"] = None
                    enriched.append(mkt)
        except Exception as e:
            logger.warning(f"  Orderbook failed for {yes_token[:16]}...: {e}")

    return enriched


# ── Main Pipeline ──────────────────────────────────────────────────────────

def match_movie_to_prediction(movie_title: str,
                              seat_data: dict, poly_data: dict,
                              cal: dict) -> dict | None:
    """Try to match a Polymarket movie title to our prediction data."""
    title_lower = movie_title.lower()

    # Direct match
    for movie_key in seat_data:
        if title_lower in movie_key.lower() or movie_key.lower() in title_lower:
            pred = predict_movie(
                movie_key, seat_data[movie_key],
                poly_data.get(movie_key, []), cal
            )
            if pred:
                return pred

    # No seat data — can still use Polymarket-only prediction
    if poly_data:
        for movie_key in poly_data:
            if title_lower in movie_key.lower() or movie_key.lower() in title_lower:
                pred = predict_movie(
                    movie_key, {},
                    poly_data[movie_key], cal
                )
                if pred:
                    return pred

    return None


def run_trading(config: dict, movie_filter: str | None = None):
    """Main trading pipeline."""
    trade_log = TradeLog()

    # Connect to Polymarket
    logger.info("Connecting to Polymarket...")
    poly = PolymarketClient(
        host=CLOB_HOST,
        gamma_host=GAMMA_HOST,
        private_key=config["private_key"],
        chain_id=config["chain_id"],
        signature_type=config["signature_type"],
        funder=config.get("funder"),
    )

    # Fetch balance
    balance = None
    if config["private_key"]:
        balance = poly.fetch_balance()
        if balance is not None:
            logger.info(f"Polymarket balance: ${balance:.2f} USDC")
        elif not config["dry_run"]:
            # In live mode a failed balance fetch means credentials are broken or
            # the API is down — abort rather than trade against a fake number.
            logger.error("Could not fetch balance in live mode — aborting to avoid phantom trades")
            poly.close()
            trade_log.close()
            return
        else:
            logger.warning("Could not fetch balance (dry run), using $100 notional")
            balance = 100.0
    else:
        logger.info("No private key — dry run mode, using $100 notional balance")
        balance = 100.0

    # Find box office events
    logger.info("Searching for box office bracket markets...")
    events = fetch_box_office_events()
    if not events:
        logger.info("No active box office bracket markets found.")
        poly.close()
        trade_log.close()
        return

    logger.info(f"Found {len(events)} box office events:")
    for ev in events:
        logger.info(f"  {ev['title']} — {len(ev['markets'])} brackets, "
                     f"vol=${ev['total_volume']:,.0f}")

    # Load prediction data
    seat_data = load_seat_data()
    poly_data = load_polymarket_data()
    cal = load_calibration()

    # Budget per movie
    n_movies = len(events)
    if movie_filter:
        events = [e for e in events
                  if movie_filter.lower() in e["title"].lower()]
        if not events:
            logger.info(f"No events matching '{movie_filter}'")
            poly.close()
            trade_log.close()
            return
        n_movies = len(events)

    budget_per_movie = balance * config["box_office_pct"] / max(n_movies, 1)
    logger.info(f"\nBudget: ${balance:.2f} × {config['box_office_pct']:.0%} "
                f"= ${balance * config['box_office_pct']:.2f} total "
                f"→ ${budget_per_movie:.2f}/movie ({n_movies} movies)")

    total_trades = 0
    total_cost = 0.0
    consecutive_order_errors = 0
    MAX_CONSECUTIVE_ERRORS = 3   # abort after this many back-to-back failures

    for event in events:
        movie = event["title"]
        print(f"\n{'='*60}")
        print(f"  {movie.upper()}")
        print(f"{'='*60}")

        # Skip if already traded this week
        if trade_log.has_traded_movie(movie):
            logger.info(f"  Already traded this week, skipping.")
            continue

        # Get prediction
        pred = match_movie_to_prediction(movie, seat_data, poly_data, cal)
        if pred:
            print(f"  Prediction: {fmt_m(pred['blended_m'])} "
                  f"({fmt_m(pred['blend_low_m'])} - {fmt_m(pred['blend_high_m'])})")
            print(f"  Data: {pred['n_theatres_total']} theatres, "
                  f"{pred['n_days']} day(s)")
        else:
            logger.warning(f"  No prediction data for {movie}")
            # Without seat data, we can't meaningfully predict
            # Could use Polymarket-only EV but that's not edge
            continue

        # Enrich markets with live orderbook
        logger.info(f"  Fetching orderbooks for {len(event['markets'])} brackets...")
        enriched = enrich_with_orderbook(poly, event["markets"])
        if not enriched:
            logger.warning(f"  No orderbook data available")
            continue

        # Override market prices with live orderbook data
        for mkt in enriched:
            if "_live_ask" in mkt:
                mkt["outcomePrices"] = json.dumps([mkt["_live_ask"]])

        # Full distribution analysis — compare ours vs market across ALL brackets
        # Pass calibration so historical accuracy influences confidence + scaling
        dist = analyze_distribution(movie, pred, enriched, calibration=cal)
        print(f"\n{format_distribution(dist)}")

        # Find edge brackets using confidence-aware Kelly sizing
        signals = find_edge_brackets(
            movie, pred, enriched,
            min_edge=config["min_edge"],
            calibration=cal,
        )

        if not signals:
            print(f"\n  No tradeable edge (min_edge={config['min_edge']:.0%}, "
                  f"confidence={dist.confidence:.0%})")
            continue

        # Size trades with fractional Kelly × confidence
        trades = size_trades(signals, budget_per_movie)
        if not trades:
            print(f"\n  Edge found but Kelly sizing too small for budget")
            continue

        kelly_pct = 0.25 + 0.25 * dist.confidence
        print(f"\n  TRADES ({len(trades)} brackets, "
              f"{kelly_pct:.0%} Kelly @ {dist.confidence:.0%} confidence):")
        print(f"  {'Bracket':<40} {'Our%':>5} {'Mkt%':>5} {'Edge':>5} "
              f"{'Kelly':>6} {'Size':>5} {'Cost':>7} {'Bgt%':>5}")
        print(f"  {'─'*40} {'─'*5} {'─'*5} {'─'*5} "
              f"{'─'*6} {'─'*5} {'─'*7} {'─'*5}")

        for trade in trades:
            s = trade.signal
            print(f"  {s.bracket_question[:40]:<40} "
                  f"{s.our_prob:5.1%} {s.market_price:5.1%} "
                  f"{s.edge:+5.1%} {s.kelly_fraction:5.1%} "
                  f"{trade.size:5.0f} ${trade.cost:6.2f} "
                  f"{trade.pct_of_budget:4.0%}")

            # Place order
            order_id = ""
            status = "dry_run"

            if not config["dry_run"]:
                try:
                    result = poly.place_limit_buy(
                        token_id=s.token_id,
                        price=s.market_price,
                        size=trade.size,
                    )
                    order_id = result.get("orderID") or result.get("id") or ""
                    status = "placed"
                    consecutive_order_errors = 0
                    logger.info(f"  ORDER PLACED: {order_id}")
                except Exception as e:
                    logger.error(f"  ORDER FAILED: {e}")
                    status = "error"
                    consecutive_order_errors += 1
                    if consecutive_order_errors >= MAX_CONSECUTIVE_ERRORS:
                        logger.error(
                            f"  {consecutive_order_errors} consecutive order failures — "
                            f"aborting (likely credential or connectivity issue)"
                        )
                        trade_log.close()
                        poly.close()
                        return
            else:
                logger.info(f"  DRY RUN — would buy {trade.size} shares "
                            f"@ {s.market_price:.3f}")

            # Log trade
            trade_log.record_trade(
                movie=s.movie,
                bracket_question=s.bracket_question,
                bracket_low=s.bracket_low,
                bracket_high=s.bracket_high,
                our_prob=s.our_prob,
                market_price=s.market_price,
                edge=s.edge,
                token_id=s.token_id,
                market_id=s.market_id,
                size=trade.size,
                price=s.market_price,
                cost=trade.cost,
                order_id=order_id,
                status=status,
                pred_mid=pred["blended_m"],
                pred_low=pred["blend_low_m"],
                pred_high=pred["blend_high_m"],
            )

            total_trades += 1
            total_cost += trade.cost

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    mode = "DRY RUN" if config["dry_run"] else "LIVE"
    print(f"  Mode: {mode}")
    print(f"  Trades: {total_trades}")
    print(f"  Total cost: ${total_cost:.2f}")
    print(f"  Balance after: ${balance - total_cost:.2f}")

    # Show recent trade history
    recent = trade_log.recent_trades(5)
    if recent:
        pnl = trade_log.total_pnl()
        print(f"  Historical PnL: ${pnl:.2f}")

    poly.close()
    trade_log.close()


def show_status():
    """Show current open trades and historical PnL."""
    trade_log = TradeLog()
    open_trades = trade_log.get_open_trades()
    recent = trade_log.recent_trades(20)

    print(f"\n{'='*60}")
    print(f"  BOX OFFICE TRADE STATUS")
    print(f"{'='*60}")

    if open_trades:
        print(f"\n  Open trades ({len(open_trades)}):")
        for t in open_trades:
            print(f"    {t['movie']}: {t['bracket_question'][:40]} "
                  f"size={t['order_size']:.0f} @ {t['order_price']:.3f} "
                  f"edge={t['edge']:+.1%}")
    else:
        print(f"\n  No open trades.")

    if recent:
        print(f"\n  Recent trades:")
        for t in recent:
            pnl_str = f"${t['pnl']:.2f}" if t['pnl'] is not None else "pending"
            print(f"    [{t['created_at'][:10]}] {t['movie']}: "
                  f"{t['bracket_question'][:35]} "
                  f"status={t['status']} pnl={pnl_str}")

    pnl = trade_log.total_pnl()
    print(f"\n  Total settled PnL: ${pnl:.2f}")
    trade_log.close()


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--status" in args:
        show_status()
        return

    movie_filter = None
    if "--movie" in args:
        idx = args.index("--movie")
        if idx + 1 < len(args):
            movie_filter = args[idx + 1]

    config = load_trade_config()
    run_trading(config, movie_filter)


if __name__ == "__main__":
    main()
