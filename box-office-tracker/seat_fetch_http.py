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


SEAT_INPUT_RE_B = re.compile(rb"""<input\b[^>]*aria-label\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)


def last_seat_input_pos(buffer, search_from: int = 0) -> int:
    """Byte offset just past the LAST seat input (`<input … aria-label=` whose
    label passes is_seat_label) at or after search_from, else -1. Accepts
    bytes or bytearray without copying."""
    pos = -1
    for m in SEAT_INPUT_RE_B.finditer(buffer, max(0, search_from)):
        raw = m.group(1) if m.group(1) is not None else (m.group(2) or b"")
        if is_seat_label(unescape(raw.decode("utf-8", "ignore"))):
            pos = m.end()
    return pos


def should_stop(buffer: bytes, last_input_end: int) -> bool:
    """Pure early-stop rule: stop only at a marker that appears AFTER the last
    seat input seen so far. Next.js streams flight-data scripts interleaved
    with markup, so a marker BEFORE the seat block must never end the read
    (that would truncate the seats); a marker after it means the block is
    behind us."""
    if last_input_end < 0:
        return False
    tail = memoryview(buffer)[last_input_end:]
    return any(buffer.find(marker, last_input_end) != -1 for marker in STOP_MARKERS) if tail else False


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


def make_session(impersonate: str = "chrome"):
    """curl_cffi session that hands us the body AS SENT ON THE WIRE (compressed),
    so raw_bytes == what the proxy bills; we inflate incrementally ourselves.
    curl_cffi keeps one curl handle per THREAD inside a Session, so one shared
    session is safe across asyncio.to_thread workers."""
    from curl_cffi import requests as cffi_requests
    from curl_cffi.const import CurlOpt
    return cffi_requests.Session(impersonate=impersonate,
                                 curl_options={CurlOpt.HTTP_CONTENT_DECODING: 0})


def fetch_seat_page(url: str, proxy_url: str | None, *, timeout: float = 30.0,
                    impersonate: str = "chrome", session=None) -> dict:
    """Stream the seat page and stop early. Returns
    {'html': str, 'raw_bytes': int, 'status': int, 'kind': str, 'stopped_early': bool}.
    Never raises for HTTP-level trouble; network errors propagate to the caller.
    """
    sess = session or make_session(impersonate)
    kwargs = {"stream": True, "timeout": timeout,
              "headers": {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                          "Accept-Language": "en-US,en;q=0.9"}}
    if proxy_url:
        kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
    resp = sess.get(url, **kwargs)
    raw = 0
    out = bytearray()
    last_input_end = -1
    stopped = False
    try:
        inflater = _Inflater(resp.headers.get("content-encoding", ""))
        for chunk in resp.iter_content(chunk_size=CHUNK):
            if not chunk:
                continue
            raw += len(chunk)
            before = len(out)
            try:
                out += inflater.feed(chunk)
            except Exception:
                # decoder confusion: keep what we have, stop reading
                stopped = True
                break
            # an <input …aria-label may straddle the chunk boundary: rescan a
            # little before the new bytes
            pos = last_seat_input_pos(out, search_from=max(0, before - 512))
            if pos > last_input_end:
                last_input_end = pos
            if should_stop(out, last_input_end) or raw >= MAX_RAW_BYTES:
                stopped = True
                break
    finally:
        try:
            resp.close()
        except Exception:
            pass
    html = out.decode("utf-8", "ignore")
    res = {"html": html, "raw_bytes": raw, "status": int(getattr(resp, "status_code", 0) or 0),
           "url": str(getattr(resp, "url", "") or url),
           "kind": classify_page(html), "stopped_early": stopped,
           "decoded_bytes": len(out), "encoding": getattr(inflater, "kind", "?") if 'inflater' in dir() else "?"}
    # Diagnostics for placing the early stop: where the seat block sits and
    # where each marker first appears in the decoded document.
    b = bytes(out)
    first_in = -1
    m = SEAT_INPUT_RE_B.search(b)
    while m:
        raw_label = m.group(1) if m.group(1) is not None else (m.group(2) or b"")
        if is_seat_label(unescape(raw_label.decode("utf-8", "ignore"))):
            first_in = m.start(); break
        m = SEAT_INPUT_RE_B.search(b, m.end())
    res["first_seat_input"] = first_in
    res["last_seat_input"] = last_input_end
    res["markers"] = {mk.decode(): b.find(mk) for mk in STOP_MARKERS}
    return res


# ── Diagnostics: where else do the seat states live? ─────────────────────────
_PROBE_KEYS = (b'"isAvailable"', b'"available"', b'"status"', b'"seatType"', b'"seatNumber"',
               b'"row"', b'"seats"', b'"seatingLayout"', b'Wheelchair', b'Recliner')


def _snippet(b: bytes, pos: int, width: int = 240) -> str:
    return b[max(0, pos - 40): pos + width].decode("utf-8", "ignore").replace("\n", " ")


def diagnose_seat_payload(html_bytes: bytes, first_seat_input: int) -> dict:
    """Counts/positions of JSON-ish seat keys in the flight data BEFORE the
    seat markup, plus one snippet — to design a JSON-based reader."""
    head = html_bytes[:first_seat_input] if first_seat_input > 0 else html_bytes
    out = {"head_bytes": len(head), "keys": {}}
    for k in _PROBE_KEYS:
        n = head.count(k)
        if n:
            out["keys"][k.decode()] = {"count": n, "first": head.find(k)}
    for k in (b'"isAvailable"', b'"status"', b'"seatNumber"', b'"seatType"'):
        i = head.find(k)
        if i != -1:
            out["snippet"] = _snippet(head, i)
            break
    return out


def probe_rsc_endpoint(url: str, proxy_url: str | None, session=None, timeout: float = 30.0) -> dict:
    """Ask the same URL for its flight payload (Next.js app router honours the
    RSC:1 header) and report size, content-type and seat-key counts."""
    sess = session or make_session()
    kwargs = {"stream": True, "timeout": timeout,
              "headers": {"RSC": "1", "Accept": "text/x-component,*/*"}}
    if proxy_url:
        kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
    resp = sess.get(url, **kwargs)
    raw = 0
    out = bytearray()
    try:
        inflater = _Inflater(resp.headers.get("content-encoding", ""))
        for chunk in resp.iter_content(chunk_size=CHUNK):
            raw += len(chunk)
            out += inflater.feed(chunk)
            if raw >= MAX_RAW_BYTES:
                break
    finally:
        try:
            resp.close()
        except Exception:
            pass
    b = bytes(out)
    res = {"status": int(getattr(resp, "status_code", 0) or 0), "raw_bytes": raw, "decoded_bytes": len(b),
           "content_type": str(resp.headers.get("content-type", "")), "keys": {}}
    for k in _PROBE_KEYS:
        n = b.count(k)
        if n:
            res["keys"][k.decode()] = n
    i = next((b.find(k) for k in (b'"isAvailable"', b'"status"', b'"seatNumber"') if b.find(k) != -1), -1)
    res["snippet"] = _snippet(b, i) if i != -1 else b[:240].decode("utf-8", "ignore")
    return res
