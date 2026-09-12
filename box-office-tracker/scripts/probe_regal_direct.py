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


print(f"proxy={'ON' if proxy else 'off'} budget={MAX_BYTES/1048576:.0f} MB", flush=True)
r, home = get("https://www.regmovies.com/", "HOME")
if home:
    slugs = sorted(set(re.findall(rb"/theatres/([a-z0-9\-]+)/(\d+)", home)))[:3]
    print(f"HOME theatre links: {[(s.decode(), i.decode()) for s, i in slugs][:3]}", flush=True)
    apis = sorted(set(re.findall(rb'"(/api/[a-z0-9\-/]+)"', home)))[:8]
    print(f"HOME api paths: {[a.decode() for a in apis]}", flush=True)
for path, tag in (("/theatres", "THEATRES"), ("/movies", "MOVIES")):
    time.sleep(1)
    get("https://www.regmovies.com" + path, tag)
