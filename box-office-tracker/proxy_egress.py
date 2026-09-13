"""Shared residential-proxy egress for the Regal (Fandango) and Cinemark lanes
(2026-09-12).

Both lanes are limited by PER-NETWORK throttles rather than by policy:
  * Fandango allows ~30 seat renders/hour across the whole GitHub (Azure)
    range, which is why the Regal lane reaches ~12 theatres per hourly slot;
  * cinemark.com answers sustained load from one address with its "Performing
    security verification" interstitial, which is why its per-theatre cap sits
    at 1 (raising it to 3 produced 305 incomplete renders out of 462).
Through a rotating residential pool each request leaves from a different
address, so neither ceiling applies. The cost is that these lanes become
METERED, hence the byte budget below: a lane stops cleanly when it has spent
its allowance, so a runaway can never eat the month's data.

The AMC seat lane has its own (much cheaper) HTTP path and does not use this.
"""
from __future__ import annotations

import os
import threading


def _env_int(name: str, default: int, minimum: int = 0) -> int:
    try:
        return max(minimum, int(os.environ.get(name, "") or default))
    except ValueError:
        return default


def proxy_settings():
    """Playwright proxy dict from AMC_SEAT_PROXY_URL, or None to run direct.

    Parsing is the seat lane's, so a malformed secret behaves identically in
    every lane: logged once, then direct.
    """
    try:
        import scraper
        return scraper._SEAT_PROXY
    except Exception:
        return None


def launch_kwargs(base: dict | None = None) -> dict:
    """chromium.launch(**kwargs) with the proxy attached when configured."""
    kwargs = dict(base or {})
    settings = proxy_settings()
    if settings:
        kwargs["proxy"] = settings
    return kwargs


class ByteBudget:
    """Counts wire bytes across threads and says when a lane should stop.

    Wire bytes (encodedDataLength) are what the proxy bills. `limit_mb` of 0
    disables the ceiling (direct egress, where bytes are free).
    """

    def __init__(self, limit_mb: int, label: str = "lane"):
        self.limit = int(limit_mb) * 1024 * 1024
        self.label = label
        self.bytes = 0
        self.responses = 0
        self.documents = 0
        self._lock = threading.Lock()
        self._announced = False

    @property
    def metered(self) -> bool:
        return self.limit > 0

    def add(self, n: int, is_document: bool = False) -> None:
        with self._lock:
            self.bytes += int(n or 0)
            self.responses += 1
            if is_document:
                self.documents += 1

    def exhausted(self) -> bool:
        if not self.metered:
            return False
        with self._lock:
            spent = self.bytes >= self.limit
            if spent and not self._announced:
                self._announced = True
                print(f"::warning::{self.label} stopped early — spent its "
                      f"{self.limit / 1048576:.0f} MB data budget for this run", flush=True)
            return spent

    def summary(self) -> str:
        mb = self.bytes / 1048576
        per = (self.bytes / self.documents / 1024) if self.documents else 0.0
        cap = f"/{self.limit / 1048576:.0f} MB" if self.metered else " (unmetered)"
        return (f"📶 {self.label} egress: {mb:.1f} MB{cap} over {self.responses} responses, "
                f"{self.documents} page loads (~{per:.0f} KB/page)")


def attach_meter(context, page, budget: ByteBudget) -> None:
    """Count what this page pulls. Best-effort: a CDP hiccup must never break
    scraping, and direct-egress runs skip the listener entirely."""
    if not budget.metered:
        return
    try:
        cdp = context.new_cdp_session(page)
        cdp.send("Network.enable")
        types: dict[str, str] = {}

        def _sent(ev):
            types[ev.get("requestId")] = ev.get("type", "")

        def _done(ev):
            budget.add(ev.get("encodedDataLength", 0),
                       is_document=types.get(ev.get("requestId")) == "Document")

        cdp.on("Network.requestWillBeSent", _sent)
        cdp.on("Network.loadingFinished", _done)
    except Exception:
        pass


def egress_banner(label: str, budget: ByteBudget) -> str:
    on = proxy_settings() is not None
    return (f"🌐 {label} egress: proxy={'ON' if on else 'off'} "
            f"budget={budget.limit / 1048576:.0f} MB" if budget.metered
            else f"🌐 {label} egress: proxy={'ON' if on else 'off'} (unmetered)")


# ── Request trimming ─────────────────────────────────────────────────────────
# Measured 2026-09-12: a proxied Cinemark theatre cost 6.3 MB (481 KB per page
# load) because the browser pulls every image, font and media file. Seat state
# lives in the DOM these lanes already read, so those bytes buy nothing. Scripts
# and stylesheets STAY: both sites build their seat maps client-side, unlike
# AMC's server-rendered page.
TRIM_RESOURCE_TYPES = frozenset({"image", "media", "font"})


def should_block(resource_type: str) -> bool:
    """Pure: is this sub-request pure decoration? (unit-tested)"""
    return (resource_type or "") in TRIM_RESOURCE_TYPES


def trim_page(page, budget: "ByteBudget") -> None:
    """Drop decorative sub-requests on a metered page. Best-effort; a routing
    hiccup must never break scraping, and unmetered (direct) runs are left
    exactly as they were."""
    if not budget.metered:
        return
    try:
        def _route(route):
            try:
                if should_block(route.request.resource_type):
                    route.abort()
                else:
                    route.continue_()
            except Exception:
                pass
        page.route("**/*", _route)
    except Exception:
        pass
