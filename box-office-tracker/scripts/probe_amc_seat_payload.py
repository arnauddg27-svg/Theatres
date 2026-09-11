"""Read-only probe (no AMC lock): page-variant repeatability through the proxy.
Fetch the same seat page 3x on one warm session, then once on a fresh session,
printing raw (billed) bytes, whether the flight-data scripts are present, and
cache/vary headers. Prints no credentials or cookie values."""
import os, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

N = int(os.environ.get("PROBE_N", "2"))
proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
links = (Path(__file__).resolve().parents[1] / "data" / "showtime-links.json").read_text()
ids = re.findall(r'"showtime_id":\s*"(\d+)"', links)
picks = ids[len(ids) // 3::max(1, len(ids) // (3 * N))][:N]


def one(sess, url, tag):
    kw = {"stream": True, "timeout": 30,
          "headers": {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                      "Accept-Language": "en-US,en;q=0.9"}}
    if proxy:
        kw["proxies"] = {"http": proxy, "https": proxy}
    r = sess.get(url, **kw)
    raw = 0
    out = bytearray()
    inf = sfh._Inflater(r.headers.get("content-encoding", ""))
    for ch in r.iter_content(chunk_size=16384):
        raw += len(ch); out += inf.feed(ch)
    r.close()
    b = bytes(out)
    hdr = {k: r.headers.get(k) for k in ("cf-cache-status", "vary", "x-nextjs-cache", "x-vercel-cache", "age", "content-type")}
    cookies = sorted({c.split("=", 1)[0] for c in (r.headers.get_list("set-cookie") if hasattr(r.headers, "get_list") else [])})
    print(f"{tag}: status={r.status_code} raw={raw} decoded={len(b)} next_f={b.count(b'self.__next_f.push')} "
          f"seats={sfh.parse_seat_counts(b.decode('utf-8','ignore'))} first_seat@{sfh.last_seat_input_pos(b[:200000]) if False else b.find(b'aria-label=\"Seat') if b.find(b'aria-label=\"Seat')!=-1 else b.find(b'aria-label=\"Recliner')} "
          f"hdr={hdr} set_cookie_names={cookies}", flush=True)


for sid in picks:
    url = f"https://www.amctheatres.com/showtimes/{sid}/seats"
    warm = sfh.make_session()
    for i in range(3):
        try:
            one(warm, url, f"WARM{i+1} {sid}")
        except Exception as e:
            print(f"WARM{i+1} {sid}: ERROR {type(e).__name__}: {str(e)[:120]}", flush=True)
    try:
        one(sfh.make_session(), url, f"FRESH {sid}")
    except Exception as e:
        print(f"FRESH {sid}: ERROR {type(e).__name__}: {str(e)[:120]}", flush=True)
