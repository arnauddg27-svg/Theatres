"""Read-only probe (no AMC lock): can the data endpoint be made smaller?
For N showtimes: RSC payload with (a) default encoding, (b) explicit brotli,
(c) Next-Router-Prefetch: 1. Prints sizes + whether the seat list is present."""
import os, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

N = int(os.environ.get("PROBE_N", "2"))
proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
links = (Path(__file__).resolve().parents[1] / "data" / "showtime-links.json").read_text()
ids = re.findall(r'"showtime_id":\s*"(\d+)"', links)
picks = ids[len(ids) // 3::max(1, len(ids) // (3 * N))][:N]
sess = sfh.make_session()


def get(url, headers, tag):
    kw = {"stream": True, "timeout": 30, "headers": headers}
    if proxy:
        kw["proxies"] = {"http": proxy, "https": proxy}
    r = sess.get(url, **kw)
    raw = 0; out = bytearray()
    inf = sfh._Inflater(r.headers.get("content-encoding", ""))
    for ch in r.iter_content(chunk_size=16384):
        raw += len(ch); out += inf.feed(ch)
    r.close()
    b = bytes(out)
    print(f"{tag}: status={r.status_code} enc={r.headers.get('content-encoding')} ctype={str(r.headers.get('content-type'))[:30]} "
          f"raw={raw} decoded={len(b)} layout={b.find(b'seatingLayout')} counts={sfh.parse_rsc_seats(b)}", flush=True)


for sid in picks:
    url = f"https://www.amctheatres.com/showtimes/{sid}/seats"
    base = {"RSC": "1", "Accept": "text/x-component,*/*", "Accept-Language": "en-US,en;q=0.9"}
    for tag, extra in (("RSC-default", {}), ("RSC-br", {"Accept-Encoding": "br"}),
                       ("RSC-prefetch", {"Next-Router-Prefetch": "1"}),
                       ("RSC-segment", {"Next-Router-Segment-Prefetch": "/_tree"})):
        try:
            get(url, {**base, **extra}, f"{tag} {sid}")
        except Exception as e:
            print(f"{tag} {sid}: ERROR {type(e).__name__}: {str(e)[:120]}", flush=True)
