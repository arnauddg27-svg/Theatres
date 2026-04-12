"""
Polymarket API client — local copy from SwissTony.
Handles Gamma API (event discovery) and CLOB API (order placement).
"""

from dataclasses import dataclass, field
import json
import logging
import httpx
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import (
    OrderArgs, OrderType, OpenOrderParams,
    BalanceAllowanceParams, AssetType,
)
from py_clob_client.order_builder.constants import BUY, SELL

logger = logging.getLogger(__name__)


@dataclass
class PolyOutcome:
    token_id: str
    label: str
    best_ask: float | None = None
    best_bid: float | None = None
    ask_size: float | None = None


@dataclass
class PolyMarket:
    market_id: str
    question: str
    condition_id: str
    slug: str
    outcomes: list[PolyOutcome] = field(default_factory=list)

    def spread(self) -> float:
        asks = [o.best_ask for o in self.outcomes if o.best_ask is not None]
        if len(asks) < 2:
            return -1.0
        return 1.0 - sum(asks)

    def min_ask_liquidity(self) -> float:
        sizes = [o.ask_size for o in self.outcomes if o.ask_size is not None]
        return min(sizes) if sizes else 0.0


@dataclass
class PolyEvent:
    event_id: str
    title: str
    slug: str
    markets: list[PolyMarket] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @classmethod
    def _parse_json_field(cls, value) -> list:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return []
        if isinstance(value, list):
            return value
        return []

    @classmethod
    def from_gamma(cls, raw: dict) -> "PolyEvent":
        markets = []
        for m in raw.get("markets", []):
            outcomes = []
            labels = cls._parse_json_field(m.get("outcomes", []))
            token_ids = cls._parse_json_field(m.get("clobTokenIds", []))
            prices = cls._parse_json_field(m.get("outcomePrices", []))
            for i, label in enumerate(labels):
                outcomes.append(PolyOutcome(
                    token_id=token_ids[i] if i < len(token_ids) else "",
                    label=label,
                    best_ask=float(prices[i]) if i < len(prices) else None,
                ))
            markets.append(PolyMarket(
                market_id=str(m.get("id", "")),
                question=m.get("question", ""),
                condition_id=m.get("conditionId", ""),
                slug=m.get("slug", ""),
                outcomes=outcomes,
            ))
        tags_raw = raw.get("tags", [])
        tag_labels = [t["label"] for t in tags_raw if isinstance(t, dict) and "label" in t]
        return cls(
            event_id=str(raw.get("id", "")),
            title=raw.get("title", ""),
            slug=raw.get("slug", ""),
            markets=markets,
            tags=tag_labels,
        )


class PolymarketClient:
    def __init__(self, host: str, gamma_host: str,
                 private_key: str | None = None,
                 chain_id: int = 137, funder: str | None = None,
                 signature_type: int = 1):
        self.gamma_host = gamma_host
        self.http = httpx.Client(timeout=30.0)

        if private_key:
            self.clob = ClobClient(
                host, key=private_key, chain_id=chain_id,
                signature_type=signature_type, funder=funder,
            )
            self.clob.set_api_creds(self.clob.create_or_derive_api_creds())
        else:
            self.clob = ClobClient(host)

    def fetch_events(self, limit: int = 200,
                     tag: str | None = None,
                     offset: int = 0) -> list[PolyEvent]:
        params = {
            "active": "true",
            "closed": "false",
            "limit": limit,
            "offset": offset,
            "order": "volume24hr",
            "ascending": "false",
        }
        if tag:
            params["tag"] = tag
        resp = self.http.get(f"{self.gamma_host}/events", params=params)
        resp.raise_for_status()
        return [PolyEvent.from_gamma(e) for e in resp.json() if e.get("markets")]

    def search_events(self, query: str, limit_per_type: int = 20,
                      page: int = 0) -> list[PolyEvent]:
        params = {
            "q": query,
            "events_status": "active",
            "limit_per_type": limit_per_type,
            "page": page,
        }
        resp = self.http.get(f"{self.gamma_host}/public-search", params=params)
        resp.raise_for_status()
        payload = resp.json()
        return [
            PolyEvent.from_gamma(event)
            for event in (payload.get("events") or [])
            if event.get("markets")
        ]

    def enrich_with_orderbook(self, market: PolyMarket) -> PolyMarket:
        for outcome in market.outcomes:
            self.refresh_outcome_price(outcome)
        return market

    def refresh_outcome_price(self, outcome: PolyOutcome) -> PolyOutcome:
        try:
            book = self.clob.get_order_book(outcome.token_id)
            self._apply_orderbook(outcome, book)
        except Exception as e:
            logger.warning(f"Orderbook FAILED: {outcome.label} "
                           f"(token={outcome.token_id[:16]}...): {e}")
        return outcome

    def _apply_orderbook(self, outcome: PolyOutcome, book) -> None:
        if book.asks:
            ask_price = float(book.asks[0].price)
            if ask_price <= 0.95:
                outcome.best_ask = ask_price
                outcome.ask_size = float(book.asks[0].size)
            else:
                self._enrich_from_midpoint(outcome, ask_price)
        else:
            self._enrich_from_midpoint(outcome, None)
        if book.bids:
            outcome.best_bid = float(book.bids[0].price)

    def _enrich_from_midpoint(self, outcome: PolyOutcome,
                              book_ask: float | None) -> None:
        try:
            result = self.clob.get_midpoint(outcome.token_id)
            mid = float(result.get("mid", 0))
            if mid > 0:
                outcome.best_ask = min(round(mid + 0.005, 3), 0.99)
                outcome.ask_size = None
        except Exception as e:
            logger.warning(f"Midpoint FAILED: {outcome.label} "
                           f"(token={outcome.token_id[:16]}...): {e}")

    def get_midpoint(self, token_id: str) -> float | None:
        try:
            result = self.clob.get_midpoint(token_id)
            return float(result.get("mid", 0))
        except Exception as e:
            logger.warning(f"Midpoint fetch failed for {token_id}: {e}")
            return None

    @staticmethod
    def _normalize_usdc_balance(raw_value) -> float:
        """Convert raw USDC balance to a float in dollars.

        The py-clob-client returns USDC as a plain decimal string (e.g. "42.50")
        representing dollars directly — NOT micro-units. We parse it as-is.
        Integer strings that look like whole-unit token amounts (no decimal point,
        value >= 1_000_000) are assumed to be micro-USDC (6 decimals) per the
        ERC-20 standard. Everything else is treated as already in dollars.
        """
        if raw_value is None:
            return 0.0
        try:
            s = str(raw_value).strip()
            if not s:
                return 0.0
            # If the string has no decimal point and the value is >= 1_000_000,
            # it's micro-USDC (e.g. the raw on-chain integer representation).
            if "." not in s and s.lstrip("-").isdigit():
                micro = int(s)
                if abs(micro) >= 1_000_000:
                    return micro / 1e6
            return float(s)
        except (ValueError, TypeError):
            return 0.0

    def fetch_balance(self) -> float | None:
        try:
            result = self.clob.get_balance_allowance(
                BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
            )
            return self._normalize_usdc_balance(result.get("balance", 0))
        except Exception as e:
            logger.warning(f"Balance fetch failed: {e}")
            return None

    def close(self):
        self.http.close()

    def place_limit_buy(self, token_id: str, price: float, size: float,
                        fill_or_kill: bool = False) -> dict:
        order_type = OrderType.FOK if fill_or_kill else OrderType.GTC
        signed = self.clob.create_order(OrderArgs(
            token_id=token_id, price=price, size=size, side=BUY,
        ))
        return self.clob.post_order(signed, order_type)

    def place_limit_sell(self, token_id: str, price: float, size: float,
                         fill_or_kill: bool = False) -> dict:
        order_type = OrderType.FOK if fill_or_kill else OrderType.GTC
        signed = self.clob.create_order(OrderArgs(
            token_id=token_id, price=price, size=size, side=SELL,
        ))
        return self.clob.post_order(signed, order_type)

    def cancel_order(self, order_id: str) -> dict:
        return self.clob.cancel(order_id)

    def get_open_orders(self) -> list:
        return self.clob.get_orders(OpenOrderParams())
