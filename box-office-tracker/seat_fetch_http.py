"""Streaming HTTP seat-map fetch — same data as the browser path, a fraction of
the bytes (2026-09-10, proxy-cost efficiency without dropping collection).

The AMC seat page is server-rendered: every seat is an `<input aria-label=
"Seat A1" … disabled>` in the HTML shell, and the bulk of the page (the
React-Server-Components payload the browser would hydrate from) trails AFTER
the markup. The browser path downloads and parses all of it. This path:

  1. GETs the page with a Chrome-impersonating TLS/HTTP2 client (curl_cffi),
     through the same residential proxy, with normal Accept-Encoding;
  2. receives the RAW compressed bytes (so what we count is what the proxy
     bills), decompressing incrementally;
  3. STOPS READING as soon as the seat block has passed — a stop marker after
     the last seat input — and closes the connection;
  4. counts seats with the same rules as COUNT_SEATS_JS.

Cloudflare block / challenge pages are recognised from the HTML so the caller
can apply its usual sentinels. Anything unexpected returns None and the caller
falls back to the browser for that showtime — completeness is never traded.
"""
from __future__ import annotations

import re
import zlib
from html import unescape

SEAT_LABEL_RE = re.compile(r"[a-z]\d+")
INPUT_TAG_RE = re.compile(r"<input\b[^>]*>", re.I)
ARIA_LABEL_RE = re.compile(r"""aria-label\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
DISABLED_RE = re.compile(r"""(?:^|\s)disabled(?:\s*=\s*(?:""|''|"disabled"|'disabled'|disabled|"true"|'true'|true))?(?=\s|/|>|$)""", re.I)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)

# Once at least one seat input has been seen, any of these means the seat
# block is behind us (the RSC payload / closing markup follows).
STOP_MARKERS = (b"self.__next_f.push", b"</main>", b"</body>", b'id="__NEXT_DATA__"')
# Hard ceiling regardless of markers (a full page is ~180 KB raw).
MAX_RAW_BYTES = 2 * 1024 * 1024
CHUNK = 16 * 1024

CF_BLOCK_TITLES = ("attention required", "access denied")
CF_CHALLENGE_TITLES = ("just a moment",)


def is_seat_label(label: str) -> bool:
    """Mirror of COUNT_SEATS_JS's filter (lower-cased label)."""
    l = (label or "").lower()
    if not (SEAT_LABEL_RE.search(l) or "recliner" in l or "seat" in l or "club rocker" in l):
        return False
    if "wheelchair" in l or "companion" in l:
        return False
    return True


def parse_seat_counts(html: str) -> dict | None:
    """{'total_seats','seats_sold','seats_available','occupancy_pct'} or None
    when no seat inputs exist — identical semantics to COUNT_SEATS_JS."""
    total = sold = 0
    for tag in INPUT_TAG_RE.findall(html or ""):
        m = ARIA_LABEL_RE.search(tag)
        if not m:
            continue
        label = unescape(m.group(1) if m.group(1) is not None else (m.group(2) or ""))
        if not is_seat_label(label):
            continue
        total += 1
        if DISABLED_RE.search(tag):
            sold += 1
    if total == 0:
        return None
    return {
        "total_seats": total,
        "seats_sold": sold,
        "seats_available": total - sold,
        "occupancy_pct": round(sold / total * 1000) / 10,
    }


def classify_page(html: str) -> str:
    """'seats' | 'blocked' | 'challenge' | 'other' from title/body."""
    m = TITLE_RE.search(html or "")
    title = unescape(m.group(1)).strip().lower() if m else ""
    if any(t in title for t in CF_BLOCK_TITLES) or "you have been blocked" in (html or "").lower()[:4000]:
        return "blocked"
    if any(t in title for t in CF_CHALLENGE_TITLES):
        return "challenge"
    if INPUT_TAG_RE.search(html or "") and parse_seat_counts(html):
        return "seats"
    return "other"


def should_stop(buffer: bytes, seen_seat_input: bool) -> bool:
    """Pure early-stop rule: after the first seat input, stop at the first
    marker that can only follow the seat block."""
    if not seen_seat_input:
        return False
    return any(marker in buffer for marker in STOP_MARKERS)


class _Inflater:
    """Incremental decoder for identity / gzip / deflate / br bodies."""

    def __init__(self, encoding: str):
        enc = (encoding or "").lower().strip()
        self.kind = enc
        if enc == "br":
            import brotli
            self._d = brotli.Decompressor()
            self.feed = self._d.process
        elif enc in ("gzip", "deflate", "x-gzip"):
            self._d = zlib.decompressobj(47 if "gzip" in enc else 15)
            self.feed = self._d.decompress
        else:
            self.feed = lambda b: b


def fetch_seat_page(url: str, proxy_url: str | None, *, timeout: float = 30.0,
                    impersonate: str = "chrome", session=None) -> dict:
    """Stream the seat page and stop early. Returns
    {'html': str, 'raw_bytes': int, 'status': int, 'kind': str, 'stopped_early': bool}.
    Never raises for HTTP-level trouble; network errors propagate to the caller.
    """
    from curl_cffi import requests as cffi_requests
    from curl_cffi.const import CurlOpt

    sess = session or cffi_requests.Session(impersonate=impersonate)
    kwargs = {"stream": True, "timeout": timeout,
              "headers": {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                          "Accept-Language": "en-US,en;q=0.9"}}
    if proxy_url:
        kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
    # Receive the body as sent on the wire (compressed) so raw_bytes == billed bytes.
    kwargs["curl_options"] = {CurlOpt.HTTP_CONTENT_DECODING: 0}
    resp = sess.get(url, **kwargs)
    raw = 0
    out = bytearray()
    seen_seat = False
    stopped = False
    try:
        inflater = _Inflater(resp.headers.get("content-encoding", ""))
        for chunk in resp.iter_content(chunk_size=CHUNK):
            if not chunk:
                continue
            raw += len(chunk)
            try:
                out += inflater.feed(chunk)
            except Exception:
                # decoder confusion: keep what we have, stop reading
                stopped = True
                break
            if not seen_seat:
                tail = bytes(out[-CHUNK * 4:])
                seen_seat = b"aria-label" in tail and INPUT_TAG_RE.search(tail.decode("utf-8", "ignore")) is not None
            if should_stop(bytes(out[-CHUNK * 3:]), seen_seat) or raw >= MAX_RAW_BYTES:
                stopped = True
                break
    finally:
        try:
            resp.close()
        except Exception:
            pass
    html = out.decode("utf-8", "ignore")
    return {"html": html, "raw_bytes": raw, "status": int(getattr(resp, "status_code", 0) or 0),
            "kind": classify_page(html), "stopped_early": stopped}
