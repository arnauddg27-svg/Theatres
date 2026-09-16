"""Read-only: are AMC showtime LISTINGS readable over HTTP (no browser)?
For a few theatres, fetch the listing page as HTML and as the RSC flight
payload through the proxy and report what each contains: Cloudflare verdict,
sizes, how many "Showtimes for" sections and /showtimes/<id> links, and a
short snippet around the first showtime id so a parser can be designed.
Prints no credentials."""
import datetime as dt, json, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import seat_fetch_http as sfh

proxy = (os.environ.get("AMC_SEAT_PROXY_URL") or "").strip() or None
N = max(1, min(6, int(os.environ.get("PROBE_N", "3") or 3)))
slugs = [t["slug"] for t in json.loads((ROOT / "data" / "theatres-all.json").read_text())["ET"]][:N]
date = (dt.date.today() + dt.timedelta(days=(4 - dt.date.today().weekday()) % 7 or 7)).isoformat()  # next Friday
sess = sfh.make_session()
ID_RE = re.compile(rb'/showtimes/(\d{6,})(?!/seats)')


def get(url, rsc):
    hdr = ({"RSC": "1", "Accept": "text/x-component,*/*"} if rsc
           else {"Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    hdr["Accept-Language"] = "en-US,en;q=0.9"
    kw = {"stream": True, "timeout": 30, "accept_encoding": sfh.ACCEPT_ENCODING, "headers": hdr}
    if proxy:
        kw["proxies"] = {"http": proxy, "https": proxy}
    r = sess.get(url, **kw)
    inf = sfh._Inflater(r.headers.get("content-encoding", ""))
    raw = 0; out = bytearray()
    for ch in r.iter_content(chunk_size=16384):
        raw += len(ch); out += inf.feed(ch)
        if raw > 3_000_000: break
    return r.status_code, str(r.headers.get("content-type", ""))[:40], raw, bytes(out)


for slug in slugs:
    url = f"https://www.amctheatres.com/showtimes/all/{date}/{slug}/all"
    for rsc in (False, True):
        tag = f"{slug[:28]:28s} {'RSC ' if rsc else 'HTML'}"
        try:
            st, ct, raw, body = get(url, rsc)
        except Exception as e:
            print(f"{tag}: ERROR {type(e).__name__}", flush=True); continue
        text = body.decode("utf-8", "ignore")
        kind = sfh.classify_page(text) if not rsc else ("component" if "x-component" in ct else sfh.classify_page(text))
        ids = ID_RE.findall(body)
        sections = text.count("Showtimes for")
        print(f"{tag}: HTTP {st} {ct} raw={raw//1024}KB dec={len(body)//1024}KB kind={kind} "
              f"sections={sections} showtime_ids={len(set(ids))} seats_links={body.count(b'/seats')}", flush=True)
        m = ID_RE.search(body)
        if m and (rsc or sections):
            a = max(0, m.start() - 400); print("   ...", text[a:m.end() + 250].replace("\n", " ")[:650], flush=True)
