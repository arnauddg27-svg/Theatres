"""Read-only probe (no AMC lock): (1) conditional requests (ETag / If-None-Match
/ Last-Modified) on the data endpoint; (2) Next-Router-State-Tree diffing —
send showtime A's router tree when asking for showtime B, measure the payload.
Prints headers of interest (no cookie values, no credentials) and the first
1200 chars of the flight payload so the tree row can be located."""
import json, os, re, sys, urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

try:
    N = max(1, min(20, int(os.environ.get("PROBE_N", "2") or 2)))
except ValueError:
    N = 2
MAX_BYTES = int(float(os.environ.get("PROBE_MAX_MB", "30")) * 1024 * 1024)
spent = 0
proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
links = (Path(__file__).resolve().parents[1] / "data" / "showtime-links.json").read_text()
ids = re.findall(r'"showtime_id":\s*"(\d+)"', links)
picks = ids[len(ids) // 3::max(1, len(ids) // (3 * N))][:N]
sess = sfh.make_session()
BASE = {"RSC": "1", "Accept": "text/x-component,*/*", "Accept-Language": "en-US,en;q=0.9"}


def get(url, headers, tag, show_head=False):
    global spent
    if spent >= MAX_BYTES:
        print(f"{tag}: SKIPPED — probe byte budget spent ({spent/1048576:.1f} MB)", flush=True)
        return None, b""
    kw = {"stream": True, "timeout": 30, "headers": headers}
    if proxy:
        kw["proxies"] = {"http": proxy, "https": proxy}
    r = sess.get(url, **kw)
    raw = 0; out = bytearray()
    inf = sfh._Inflater(r.headers.get("content-encoding", ""))
    for ch in r.iter_content(chunk_size=16384):
        raw += len(ch); out += inf.feed(ch)
        if raw > 2 * 1024 * 1024:
            break
    r.close()
    spent += raw
    b = bytes(out)
    hdr = {k: r.headers.get(k) for k in ("etag", "last-modified", "cache-control", "cf-cache-status", "age", "x-nextjs-postponed", "content-length")}
    print(f"{tag}: status={r.status_code} raw={raw} decoded={len(b)} layout={b.find(b'seatingLayout')} "
          f"counts={sfh.parse_rsc_seats(b)} hdr={hdr}", flush=True)
    if show_head:
        print(f"{tag} HEAD: {b[:1200].decode('utf-8', 'ignore')!r}", flush=True)
    return r, b


def extract_tree(payload: bytes):
    """Best effort: the flight row that starts with the router tree."""
    txt = payload.decode("utf-8", "ignore")
    for line in txt.splitlines():
        m = re.match(r"^(\d+):(.*)$", line)
        if not m:
            continue
        body = m.group(2)
        if '"__PAGE__' in body:
            try:
                obj = json.loads(body)
            except Exception:
                continue
            # flight envelope {"f":[[tree, seed, head, ...]]} -> the router tree is f[0][0]
            if isinstance(obj, dict) and "f" in obj:
                try:
                    return obj["f"][0][0]
                except Exception:
                    return None
            return obj
    return None


for i, sid in enumerate(picks):
    url = f"https://www.amctheatres.com/showtimes/{sid}/seats"
    r, b = get(url, BASE, f"RSC {sid}", show_head=(i == 0))
    etag = r.headers.get("etag"); lm = r.headers.get("last-modified")
    cond = dict(BASE)
    if etag: cond["If-None-Match"] = etag
    if lm: cond["If-Modified-Since"] = lm
    tree = extract_tree(b)
    print(f"TREE {sid}: {'found' if tree else 'not found'} {json.dumps(tree)[:400] if tree else ''}", flush=True)
    if tree and i + 1 < len(picks):
        nxt = f"https://www.amctheatres.com/showtimes/{picks[i+1]}/seats"
        def sanitize(node, trim):
            # flight encoding -> what the browser router holds: "$undefined" -> null,
            # and (trim) nodes cut to [segment, parallelRoutes, url, refresh]
            if isinstance(node, list):
                out = [sanitize(x, trim) for x in node]
                if trim and len(out) >= 2 and isinstance(out[1], dict):
                    out = out[:4]
                return out
            if isinstance(node, dict):
                return {k: sanitize(v, trim) for k, v in node.items()}
            return None if node == "$undefined" else node
        variants = {
            "DIFF-null": sanitize(tree, False),
            "DIFF-trim": sanitize(tree, True),
        }
        for tag, t in variants.items():
            enc = urllib.parse.quote(json.dumps(t, separators=(",", ":")))
            print(f"{tag} tree: {json.dumps(t, separators=(',', ':'))[:300]}", flush=True)
            extra = {"Next-Router-State-Tree": enc}
            hdrs = dict(BASE); hdrs.update(extra)
            try:
                _, body = get(nxt, hdrs, f"{tag} {picks[i+1]} (tree from {sid})")
                if len(body) < 400:
                    print(f"{tag} BODY: {body[:400]!r}", flush=True)
            except Exception as e:
                print(f"{tag}: ERROR {type(e).__name__}: {str(e)[:120]}", flush=True)
