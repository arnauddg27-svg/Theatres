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
# No zstd: HTTP_CONTENT_DECODING=0 hands us the raw body and _Inflater has no
# zstd branch, so an undecodable body would burn the whole fallback chain.
ACCEPT_ENCODING = "gzip, deflate, br"

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
    # No zstd: HTTP_CONTENT_DECODING=0 means curl hands us the raw body and
    # _Inflater has no zstd branch — an undecodable body would burn the whole
    # fallback chain silently (audit-15).
    return cffi_requests.Session(impersonate=impersonate,
                                 curl_options={CurlOpt.HTTP_CONTENT_DECODING: 0,
                                               CurlOpt.SSL_EC_CURVES: TLS_CURVES})


# Chrome's post-quantum key share (X25519MLKEM768) makes the TLS ClientHello
# span two packets, and the residential proxy's tunnels from Azure East/Central
# US never answer such a handshake (2026-09-16, runs 35100605194/35100558168:
# the Chrome fingerprint timed out every time, the same fingerprint with these
# curves passed in <1 s and still read a seat map past Cloudflare; older or
# plain fingerprints got a 403). Everything else in the impersonation stays.
TLS_CURVES = "X25519:P-256:P-384"


def fetch_seat_page(url: str, proxy_url: str | None, *, timeout: float = 30.0,
                    impersonate: str = "chrome", session=None, diagnostics: bool = False) -> dict:
    """Stream the seat page and stop early. Returns
    {'html': str, 'raw_bytes': int, 'status': int, 'kind': str, 'stopped_early': bool}.
    Never raises for HTTP-level trouble; network errors propagate to the caller.
    """
    sess = session or make_session(impersonate)
    kwargs = {"stream": True, "timeout": timeout, "accept_encoding": ACCEPT_ENCODING,
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
    if not diagnostics:
        return {"html": html, "raw_bytes": raw, "status": int(getattr(resp, "status_code", 0) or 0),
                "url": str(getattr(resp, "url", "") or url),
                "kind": classify_page(html), "stopped_early": stopped}
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



# ── Data-endpoint (RSC flight payload) seat reader ───────────────────────────
# `RSC: 1` on the same URL returns the flight payload (text/x-component,
# ~119 KB gzip vs ~190 KB for the page). Near its end:
#   "seatingLayout":{"columns":14,"rows":9,"seats":[{"available":true,
#     "column":1,"row":1,"name":"A14","type":"LoveSeatLeft","seatTier":"Regular",
#     "shouldDisplay":true}, …]}
# Field ORDER and set are pinned by this regex, so a seat object that gains or
# loses one key stops matching — parse_rsc_seats turns that into None rather
# than a short count (audit-15).
_SEAT_OBJ_RE = re.compile(
    rb'\{"available":(true|false),"column":\d+,"row":\d+,"name":"([^"]*)","type":"([^"]*)","seatTier":"([^"]*)","shouldDisplay":(true|false)\}')
# Counting marker for the completeness check: present exactly once per seat
# cell whatever the field ORDER (a reordered object no longer starts with
# {"available": and would otherwise slip past the check).
_SEAT_OBJ_MARK = b'"shouldDisplay":'
_SEAT_OBJ_OPEN = b'{"available":'
# Whole-type matches, not substrings: "aisle" as a substring also excluded a
# real "AisleRecliner" seat that the markup rule counts (audit-15).
_NON_SEAT_TYPES = frozenset({"notaseat", "wheelchair", "companion", "aisle", "gap", "empty", "blank"})


def _layout_bounds(payload: bytes) -> tuple[int, int] | None:
    """Byte range of the FIRST seatingLayout's seat array, found by matching
    brackets rather than the first ']' — a single list-valued field on one seat
    would otherwise truncate the window mid-array and make every read fail
    (audit-16). Returns None when no usable array is present."""
    start = payload.find(b'"seatingLayout"')
    if start == -1:
        return None
    nxt = payload.find(b'"seatingLayout"', start + 1)
    limit = nxt if nxt != -1 else len(payload)
    arr = payload.find(b'"seats":[', start, limit)   # never reach into the NEXT layout
    if arr == -1:
        return None
    lo = arr + len(b'"seats":[')
    depth, i, in_str, esc = 1, lo, False, False
    while i < limit and depth:
        c = payload[i:i + 1]
        if in_str:
            if esc:
                esc = False
            elif c == b"\\":
                esc = True
            elif c == b'"':
                in_str = False
        elif c == b'"':
            in_str = True
        elif c in (b"[", b"{"):
            depth += 1 if c == b"[" else 0
        elif c == b"]":
            depth -= 1
        i += 1
    if depth:
        return None                                   # unterminated array
    hi = i - 1
    return (lo, hi) if hi > lo else None


def parse_rsc_seats(payload: bytes) -> dict | None:
    """Seat counts from the flight payload with the SAME exclusions as the
    markup rule (COUNT_SEATS_JS): non-seat cells, wheelchair and companion
    cells are skipped; 'sold' = not available.

    Returns None — never a partial count — when the payload's shape has
    drifted, so the caller falls back to a reader that still understands it.
    """
    bounds = _layout_bounds(payload)
    if bounds is None:
        return None
    lo, hi = bounds
    window = payload[lo:hi]
    matches = list(_SEAT_OBJ_RE.finditer(window))
    # Completeness, checked BOTH ways (audit-16): the number of seat cells is
    # the max of the two independent markers, so drift that ADDS/REORDERS keys
    # (mark present, regex misses) and drift that REMOVES a key (neither
    # present) both fail the check instead of yielding a short count.
    cells = max(window.count(_SEAT_OBJ_MARK), window.count(_SEAT_OBJ_OPEN))
    if len(matches) != cells:
        return None
    total = sold = 0
    for m in matches:
        avail, name, typ, _tier, display = m.groups()
        t = typ.decode("utf-8", "ignore").lower()
        if display == b"false" or not name or t in _NON_SEAT_TYPES:
            continue
        total += 1
        if avail == b"false":
            sold += 1
    if total == 0:
        return None
    return {"total_seats": total, "seats_sold": sold, "seats_available": total - sold,
            "occupancy_pct": round(sold / total * 1000) / 10}


def payload_names_showtime(payload: bytes, showtime_id) -> bool:
    """True when the flight payload actually describes the showtime we asked
    for. The envelope carries the canonical segments — "c":["","showtimes",
    "<id>","seats"] — and the full payload also carries ["showtimeId","<id>".
    A diff response is only trusted when this holds (audit-15)."""
    sid = str(showtime_id or "").encode()
    if not sid:
        return False
    return (b'"' + sid + b'","seats"') in payload or (b'"showtimeId","' + sid + b'"') in payload


def fetch_rsc_seat_page(url: str, proxy_url: str | None, *, timeout: float = 30.0, session=None) -> dict:
    """GET the flight payload (RSC: 1) — ~119 KB vs ~190 KB for the page —
    and read the seat list from it. Returns {'counts': dict|None, 'raw_bytes',
    'status', 'kind', 'url'}; kind mirrors classify_page for block pages."""
    sess = session or make_session()
    kwargs = {"stream": True, "timeout": timeout, "accept_encoding": ACCEPT_ENCODING,
              "headers": {"RSC": "1", "Accept": "text/x-component,*/*", "Accept-Language": "en-US,en;q=0.9"}}
    if proxy_url:
        kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
    resp = sess.get(url, **kwargs)
    raw = 0
    out = bytearray()
    try:
        inflater = _Inflater(resp.headers.get("content-encoding", ""))
        for chunk in resp.iter_content(chunk_size=CHUNK):
            if not chunk:
                continue
            raw += len(chunk)
            out += inflater.feed(chunk)
            if raw >= MAX_RAW_BYTES:
                break
    finally:
        try:
            resp.close()
        except Exception:
            pass
    payload = bytes(out)
    ctype = str(resp.headers.get("content-type", "")).lower()
    counts = parse_rsc_seats(payload) if "x-component" in ctype else None
    if counts:
        kind = "seats"
    elif "x-component" in ctype:
        kind = "other"
    else:
        kind = classify_page(payload.decode("utf-8", "ignore"))   # HTML came back: block/challenge/other
    return {"counts": counts, "raw_bytes": raw, "status": int(getattr(resp, "status_code", 0) or 0),
            "url": str(getattr(resp, "url", "") or url), "kind": kind, "payload": payload}


# ── Segment diff: ask only for what changed (2026-09-11) ─────────────────────
# Next.js's router sends its current tree (Next-Router-State-Tree) on client
# navigations and the server replies with only the segments that differ. A seat
# page's tree differs from another showtime's ONLY in the dynamic
# [showtimeId] segment, so handing the server the tree of any OTHER showtime
# yields just that segment: ~8.7 KB gzip with the full seatingLayout, versus
# ~119 KB for the whole flight payload and ~190 KB for the page. The flight
# encoding writes "$undefined" and trailing flags that a browser never sends
# back (the server 500s on them), hence sanitize().
ROUTER_TREE_TEMPLATE = ["", {"children": ["(headless)", {"children": ["showtimes", {"children": [
    ["showtimeId", "__SHOWTIME__", "d", None],
    {"children": ["seats", {"children": ["__PAGE__", {}]}, None, None]}, None, None]}, None, None]}, None, None]}, None, None]
_TREE_ROW_RE = re.compile(r"^\d+:(\{.*\"__PAGE__\".*\})\s*$", re.M)


def sanitize_router_tree(node):
    if isinstance(node, list):
        out = [sanitize_router_tree(x) for x in node]
        if len(out) >= 2 and isinstance(out[1], dict):
            out = out[:4]                      # [segment, parallelRoutes, url, refresh]
        return out
    if isinstance(node, dict):
        return {k: sanitize_router_tree(v) for k, v in node.items()}
    return None if node == "$undefined" else node


def extract_router_tree(payload: bytes):
    """The sanitised router tree from a FULL flight payload (row {"f":[[tree,…]]}),
    with the showtime id replaced by the __SHOWTIME__ placeholder; None if the
    shape is unrecognised. Lets a leg self-heal if AMC changes its routes."""
    import json
    txt = payload.decode("utf-8", "ignore")
    for m in _TREE_ROW_RE.finditer(txt):
        try:
            obj = json.loads(m.group(1))
            tree = sanitize_router_tree(obj["f"][0][0])
        except Exception:
            continue
        s = json.dumps(tree, separators=(",", ":"))
        s2 = re.sub(r'\["showtimeId","\d+"', '["showtimeId","__SHOWTIME__"', s)
        if "__SHOWTIME__" in s2 and '"__PAGE__"' in s2:
            return json.loads(s2)
    return None


def router_tree_header(template, other_showtime_id: str) -> str:
    """URL-encoded tree for the header, naming a showtime OTHER than the one
    requested (identical trees would diff to nothing)."""
    import json
    from urllib.parse import quote
    s = json.dumps(template, separators=(",", ":")).replace("__SHOWTIME__", str(other_showtime_id))
    return quote(s, safe="")


def fetch_rsc_seat_diff(url: str, proxy_url: str | None, tree_header: str, *,
                        timeout: float = 30.0, session=None) -> dict:
    """Segment-diff request. Same result shape as fetch_rsc_seat_page. Uses a
    non-streaming GET so the per-thread connection (and its proxy tunnel) is
    reused across the tiny responses — the ~6 KB handshake would otherwise
    dominate the ~9 KB body."""
    sess = session or make_session()
    kwargs = {"stream": False, "timeout": timeout, "accept_encoding": ACCEPT_ENCODING,
              "headers": {"RSC": "1", "Accept": "text/x-component,*/*", "Accept-Language": "en-US,en;q=0.9",
                          "Next-Router-State-Tree": tree_header}}
    if proxy_url:
        kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
    resp = sess.get(url, **kwargs)
    body = (resp.content or b"")[:MAX_RAW_BYTES]
    raw = len(body)
    try:
        payload = _Inflater(resp.headers.get("content-encoding", "")).feed(body)
    except Exception:
        payload = body
    ctype = str(resp.headers.get("content-type", "")).lower()
    counts = parse_rsc_seats(payload) if "x-component" in ctype else None
    if counts:
        kind = "seats"
    elif "x-component" in ctype or int(getattr(resp, "status_code", 0) or 0) >= 500:
        kind = "other"
    else:
        kind = classify_page(payload.decode("utf-8", "ignore"))
    return {"counts": counts, "raw_bytes": raw, "status": int(getattr(resp, "status_code", 0) or 0),
            "url": str(getattr(resp, "url", "") or url), "kind": kind, "payload": payload}


# ── Showtime LISTINGS over HTTP (2026-09-16) ─────────────────────────────────
# The listing page is server-rendered, but React STREAMS it: a movie's
# <section aria-label="Showtimes for …"> arrives with <template id="P:n">
# placeholders, and the <ul> of formats/showtimes for it arrives later in a
# <div hidden id="S:n"> chunk that a $RS("S:n","P:n") script splices into
# place. The browser does that splice; here the parser does, so the same
# section → li[aria-label$=" Showtimes"] → a[href=/showtimes/<id>] walk that
# EXTRACT_SHOWTIMES_JS performs works on the raw HTML. Measured 2026-09-16
# (run 35103676240): 213 KB raw for 31 movies / 130 showtimes, same page the
# browser needs ~1.4 MB decoded plus its scripts for.
from html.parser import HTMLParser as _HTMLParser

_SHOWTIME_HREF = re.compile(r"/showtimes/(\d+)$")
_TIME_RE = re.compile(r"(\d{1,2}:\d{2}\s*(?:am|pm))", re.I)
_LISTING_MARK = 'aria-label="Showtimes for '
# The page header, present whether or not any film is listed that day, so a
# rendered-but-empty listing is an authoritative empty and not a browser trip.
_LISTING_HEADER = re.compile(r"<h1[^>]*>\s*Showtimes\s*</h1>")


def is_listing_page(html: str) -> bool:
    return _LISTING_MARK in html or bool(_LISTING_HEADER.search(html or ""))


class _Node:
    __slots__ = ("tag", "attrs", "children", "text")

    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []
        self.text = []


_VOID = frozenset({"img", "br", "hr", "input", "meta", "link", "source", "track", "wbr", "area", "base", "col", "embed", "param"})


class _Tree(_HTMLParser):
    """Minimal DOM: enough structure to walk sections, lists, links and text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", {})
        self.stack = [self.root]
        self.by_id = {}

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs)
        self.stack[-1].children.append(node)
        if node.attrs.get("id"):
            self.by_id.setdefault(node.attrs["id"], node)
        if tag not in _VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = _Node(tag, attrs)
        self.stack[-1].children.append(node)
        if node.attrs.get("id"):
            self.by_id.setdefault(node.attrs["id"], node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if data:
            self.stack[-1].children.append(data)


def _walk(node, by_id, seen):
    """Depth-first over a node's children, following streamed placeholders:
    <template id="P:n"> stands for the content of <div hidden id="S:n">."""
    for child in node.children:
        if isinstance(child, str):
            yield child
            continue
        if child.tag == "template":
            tid = child.attrs.get("id", "")
            if tid.startswith("P:"):
                chunk = by_id.get("S:" + tid[2:])
                if chunk is not None and id(chunk) not in seen:
                    seen.add(id(chunk))
                    yield from _walk(chunk, by_id, seen)
            continue
        yield child
        yield from _walk(child, by_id, seen)


def _text_of(node, by_id):
    return "".join(x for x in _walk(node, by_id, set()) if isinstance(x, str))


def parse_listing_showtimes(html: str) -> list:
    """The listing's showtimes, in EXTRACT_SHOWTIMES_JS's shape:
    [{movie, showtime, showtime_id, format, flags}, ...]. Empty when the page
    lists nothing (or is not a listing page at all)."""
    if _LISTING_MARK not in html:
        return []
    tree = _Tree()
    tree.feed(html)
    results = []
    seen_ids = set()

    def sections(node):
        for x in _walk(node, tree.by_id, set()):
            if not isinstance(x, str) and x.tag == "section" and \
                    x.attrs.get("aria-label", "").startswith("Showtimes for "):
                yield x

    for section in sections(tree.root):
        movie = section.attrs.get("aria-label", "")[len("Showtimes for "):]
        for item in _walk(section, tree.by_id, set()):
            if isinstance(item, str) or item.tag != "li":
                continue
            fmt_label = item.attrs.get("aria-label", "")
            if not fmt_label.endswith("Showtimes"):
                continue
            fmt = fmt_label.replace(" Showtimes", "", 1) if " Showtimes" in fmt_label else fmt_label[:-len("Showtimes")]
            for link in _walk(item, tree.by_id, set()):
                if isinstance(link, str) or link.tag != "a":
                    continue
                m = _SHOWTIME_HREF.search(link.attrs.get("href", ""))
                if not m or m.group(1) in seen_ids:
                    continue
                seen_ids.add(m.group(1))
                text = _text_of(link, tree.by_id).strip()
                tm = _TIME_RE.search(text)
                showtime = tm.group(1) if tm else text.split("\n")[0].strip()
                flags = ("Almost Full" if "Almost Full" in text else
                         "Sold Out" if "Sold Out" in text else
                         "Reserved" if "Reserved" in text else "")
                results.append({"movie": movie, "showtime": showtime, "showtime_id": m.group(1),
                                "format": fmt, "flags": flags})
    return results


def fetch_listing_page(url: str, proxy_url: str | None, *, timeout: float = 30.0, session=None) -> dict:
    """GET a showtime listing (whole page; the sections stream throughout).
    Returns {'html', 'raw_bytes', 'status', 'kind', 'url'} where kind is
    'listing' when the page carries showtime sections, else classify_page's
    verdict (blocked / challenge / other). Network errors propagate."""
    sess = session or make_session()
    kwargs = {"stream": True, "timeout": timeout, "accept_encoding": ACCEPT_ENCODING,
              "headers": {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                          "Accept-Language": "en-US,en;q=0.9"}}
    if proxy_url:
        kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
    resp = sess.get(url, **kwargs)
    raw = 0
    out = bytearray()
    try:
        inflater = _Inflater(resp.headers.get("content-encoding", ""))
        for chunk in resp.iter_content(chunk_size=CHUNK):
            if not chunk:
                continue
            raw += len(chunk)
            out += inflater.feed(chunk)
            if raw >= MAX_RAW_BYTES:
                break
    finally:
        try:
            resp.close()
        except Exception:
            pass
    html = bytes(out).decode("utf-8", "ignore")
    kind = classify_page(html)
    if kind == "other" and is_listing_page(html):
        kind = "listing"
    return {"html": html, "raw_bytes": raw, "status": int(getattr(resp, "status_code", 0) or 0),
            "url": str(getattr(resp, "url", "") or url), "kind": kind}
