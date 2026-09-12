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

# 1. a theatre page -> its showtime links
r, th = get("https://www.regmovies.com/theatres", "THEATRES")
import collections
hrefs = [m.decode("utf-8", "ignore") for m in re.findall(rb'href="(/[^"]{2,80})"', th or b"")]
shapes = collections.Counter("/".join(re.sub(r"[0-9]+", "N", p).split("/")[:3]) for p in hrefs)
print(f"THEATRES hrefs: {len(hrefs)} | top shapes: {shapes.most_common(8)}", flush=True)
print(f"  samples: {hrefs[:8]}", flush=True)
paths = sorted({p for p in hrefs if p.startswith("/theatres/") and p.count("/") >= 2})
print(f"theatre paths: {len(paths)} e.g. {paths[:3]}", flush=True)
detail = b""
if paths:
    time.sleep(1)
    r, detail = get("https://www.regmovies.com" + paths[0], f"THEATRE {paths[0]}")

# 2. showtime / ticketing links on a theatre page
dh = [m.decode("utf-8", "ignore") for m in re.findall(rb'href="([^"]{2,120})"', detail or b"")]
dshapes = collections.Counter("/".join(re.sub(r"[0-9]+", "N", p).split("/")[:4]) for p in dh)
print(f"THEATRE-PAGE hrefs: {len(dh)} | top shapes: {dshapes.most_common(8)}", flush=True)
cands = sorted({p for p in dh if re.search(r"showtime|ticket|seat|session", p, re.I)})[:8]
print(f"showtime-ish paths: {cands}", flush=True)
sess_ids = sorted({m.decode() for m in re.findall(rb'"(?:sessionId|showtimeId|sessionID)"\s*:\s*"?([A-Za-z0-9\-]{4,})"?', detail or b"")})[:5]
print(f"session ids in page: {sess_ids}", flush=True)
for key in (b'"seats"', b'"seatingLayout"', b'"available"', b'seatMap', b'"SeatsAvailable"', b'"occupancy"'):
    if detail and key in detail:
        i = detail.find(key)
        print(f"  theatre page has {key.decode()} @{i}: {detail[max(0,i-80):i+220].decode('utf-8','ignore')!r}", flush=True)

# 3. does the site answer RSC on a deep page? (the AMC trick's precondition)
if paths:
    time.sleep(1)
    r, rsc = get("https://www.regmovies.com" + paths[0], "RSC theatre", headers=RSC_HDRS,
                 note=f"is_flight={bool(rsc_ct) if (rsc_ct := (r.headers.get('content-type') if r else '')) else False}")

# 4. any obvious data API the page calls
apis = sorted({m.decode() for m in re.findall(rb'"(/api/[a-z0-9\-/]+)"', (th or b"") + (detail or b""))})[:10]
print(f"api paths seen: {apis}", flush=True)
