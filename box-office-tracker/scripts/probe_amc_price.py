"""Read-only: does AMC expose TICKET PRICES anywhere we already read (or one
hop away)? Fetches one showtime's seat page HTML and RSC payload, plus the
candidate ticket-selection routes, through the proxy, and prints where
price-like tokens occur with short snippets. No credentials printed."""
import csv, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import seat_fetch_http as sfh

proxy = (os.environ.get("AMC_SEAT_PROXY_URL") or "").strip() or None
urls = []
with open(ROOT / "data" / "pre-reservation-snapshots.csv", newline="") as fh:
    for r in csv.DictReader(fh):
        u = r.get("amc_seat_map_url") or ""
        if u.startswith("https://www.amctheatres.com/showtimes/"):
            urls.append(u)
seat = urls[-1]
sid = seat.rsplit("/showtimes/", 1)[1].split("/")[0]
print("showtime", sid, flush=True)
sess = sfh.make_session()
PRICE_RE = re.compile(rb'(?i)("price[a-z_]*"\s*:\s*[^,}]{1,40}|\$\d{1,3}\.\d{2}|"ticketType[a-z_]*"\s*:\s*"[^"]{1,40}"|"adult[a-z_]*"\s*:\s*[^,}]{1,40})')


def fetch(url, rsc=False):
    hdr = {"Accept": "text/x-component,*/*" if rsc else "text/html,*/*", "Accept-Language": "en-US,en;q=0.9"}
    if rsc: hdr["RSC"] = "1"
    kw = {"stream": True, "timeout": 30, "accept_encoding": sfh.ACCEPT_ENCODING, "headers": hdr}
    if proxy: kw["proxies"] = {"http": proxy, "https": proxy}
    r = sess.get(url, **kw)
    inf = sfh._Inflater(r.headers.get("content-encoding", "")); raw = 0; out = bytearray()
    for ch in r.iter_content(chunk_size=16384):
        raw += len(ch); out += inf.feed(ch)
        if raw > 3_000_000: break
    return r.status_code, str(r.headers.get("content-type", ""))[:30], raw, bytes(out)


for label, url, rsc in (("seat page HTML", seat, False), ("seat page RSC", seat, True),
                        ("tickets route HTML", f"https://www.amctheatres.com/showtimes/{sid}/tickets", False),
                        ("tickets route RSC", f"https://www.amctheatres.com/showtimes/{sid}/tickets", True),
                        ("showtime root HTML", f"https://www.amctheatres.com/showtimes/{sid}", False)):
    try:
        st, ct, raw, body = fetch(url, rsc)
    except Exception as e:
        print(f"{label:20s}: ERROR {type(e).__name__}", flush=True); continue
    hits = PRICE_RE.findall(body)
    uniq = []
    for h in hits:
        t = h.decode("utf-8", "ignore")
        if t not in uniq: uniq.append(t)
    kind = sfh.classify_page(body.decode("utf-8", "ignore")) if b"x-component" not in ct.encode() else "component"
    print(f"{label:20s}: HTTP {st} {ct} raw={raw//1024}KB kind={kind} price-like hits={len(hits)} distinct={len(uniq)}", flush=True)
    for t in uniq[:12]: print("     ", t[:120], flush=True)
    m = re.search(rb'(?i).{0,200}"price".{0,300}', body)
    if m: print("   ctx:", m.group(0).decode("utf-8", "ignore").replace("\n", " ")[:500], flush=True)
