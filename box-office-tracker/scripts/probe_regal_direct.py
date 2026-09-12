"""Read-only probe (no AMC lock, hard byte ceiling): can regmovies.com be read
through the residential proxy?

August's verdict was "Regal is behind Cloudflare Turnstile" — measured from a
DATA-CENTRE address, which is what those checks punish. Residential exits may
pass. Regal is a Next.js site, so if it passes, the AMC treatment (RSC data
endpoint + segment diff) may apply and Regal escapes Fandango's shared budget.

Budget: stops after PROBE_MAX_MB of proxy traffic (default 30 MB).
Prints no credentials.
"""
import os, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
MAX_BYTES = int(float(os.environ.get("PROBE_MAX_MB", "30")) * 1024 * 1024)
spent = 0
sess = sfh.make_session()


def get(url, tag, headers=None, note=""):
    global spent
    if spent >= MAX_BYTES:
        print(f"{tag}: SKIPPED — probe byte budget spent ({spent/1048576:.1f} MB)", flush=True)
        return None, b""
    kw = {"stream": True, "timeout": 30,
          "headers": headers or {"Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                                 "Accept-Language": "en-US,en;q=0.9"}}
    if proxy:
        kw["proxies"] = {"http": proxy, "https": proxy}
    try:
        r = sess.get(url, **kw)
    except Exception as e:
        print(f"{tag}: ERROR {type(e).__name__}: {str(e)[:100]}", flush=True)
        return None, b""
    raw = 0; out = bytearray()
    inf = sfh._Inflater(r.headers.get("content-encoding", ""))
    for ch in r.iter_content(chunk_size=16384):
        raw += len(ch); out += inf.feed(ch)
        if raw > 3 * 1024 * 1024:
            break
    r.close()
    spent += raw
    b = bytes(out)
    low = b[:6000].lower()
    turnstile = b"turnstile" in b.lower() or b"challenge-platform" in low or b"cf-chl" in low
    title = re.search(rb"<title[^>]*>(.*?)</title>", b, re.I | re.S)
    print(f"{tag}: status={r.status_code} raw={raw} decoded={len(b)} "
          f"ctype={str(r.headers.get('content-type'))[:28]} turnstile={turnstile} "
          f"nextjs={b'/_next/' in b} title={(title.group(1)[:60].decode('utf-8','ignore').strip() if title else '')!r} "
          f"cf={r.headers.get('cf-mitigated')} {note} [spent {spent/1048576:.1f} MB]", flush=True)
    return r, b


RSC_HDRS = {"RSC": "1", "Accept": "text/x-component,*/*", "Accept-Language": "en-US,en;q=0.9"}
print(f"proxy={'ON' if proxy else 'off'} budget={MAX_BYTES/1048576:.0f} MB", flush=True)

# The theatre list hydrates client-side, so discover routes from the sitemap.
r, sm = get("https://www.regmovies.com/sitemap.xml", "SITEMAP")
import collections
locs = [m.decode() for m in re.findall(rb"<loc>\s*([^<\s]+)\s*</loc>", sm or b"")]
shapes = collections.Counter(re.sub(r"[0-9]+", "N", u.replace("https://www.regmovies.com", "")).rsplit("/", 1)[0] or "/" for u in locs)
print(f"sitemap: {len(locs)} urls | top shapes: {shapes.most_common(10)}", flush=True)
theatre_url = next((u for u in locs if "/theatres/" in u), None)
movie_url = next((u for u in locs if "/movies/" in u), None)
print(f"sample theatre={theatre_url}  sample movie={movie_url}", flush=True)

if theatre_url:
    time.sleep(1)
    r, detail = get(theatre_url, "THEATRE PAGE")
    for key in (b'"seats"', b'"seatingLayout"', b'"available"', b'seatMap', b'"sessionId"',
                b'"showtimes"', b'"performances"', b'"SeatsAvailable"'):
        if detail and key in detail:
            i2 = detail.find(key)
            print(f"  has {key.decode()} @{i2}: {detail[max(0,i2-60):i2+200].decode('utf-8','ignore')!r}", flush=True)
    hrefs = sorted({m.decode('utf-8','ignore') for m in re.findall(rb'href="([^"]{2,140})"', detail or b"")})
    tick = [h for h in hrefs if re.search(r"ticket|seat|session|showtime|book", h, re.I)][:8]
    print(f"  ticket-ish hrefs: {tick}", flush=True)
    print(f"  all href shapes: {sorted({re.sub(r'[0-9]+','N',h)[:48] for h in hrefs})[:12]}", flush=True)
    time.sleep(1)
    r, rsc = get(theatre_url, "RSC theatre", headers=RSC_HDRS)
    if rsc:
        print(f"  rsc is_flight={rsc[:40]!r} has_seat_keys={any(k in rsc for k in (b'seatingLayout', b'"seats"', b'"available"'))}", flush=True)
