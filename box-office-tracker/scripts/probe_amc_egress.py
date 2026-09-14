"""Read-only: does amctheatres.com answer THROUGH the residential proxy right
now, and how fast? Built 2026-09-14 after the seat and listing lanes timed out
for hours while the proxy itself still answered ipinfo.io. For each draw it
prints status, elapsed seconds, raw bytes, and on failure only the exception
CLASS — never the proxy URL, credentials or response bodies. A couple of
direct draws follow for contrast (direct is Cloudflare-walled; a fast 403
there is expected)."""
import csv, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
N = max(1, min(10, int(os.environ.get("PROBE_N", "4") or 4)))
MAX_BYTES = int(float(os.environ.get("PROBE_MAX_MB", "30")) * 1024 * 1024)
spent = 0

seat_urls = []
with open(ROOT / "data" / "pre-reservation-snapshots.csv", newline="") as fh:
    for row in csv.DictReader(fh):
        u = row.get("amc_seat_map_url") or ""
        if u.startswith("https://www.amctheatres.com/showtimes/"):
            seat_urls.append(u)
seat_urls = seat_urls[-N:]
import json
slugs = [t["slug"] for t in json.loads((ROOT / "data" / "theatres-all.json").read_text()).get("ET", [])][:N]
import datetime as _dt
day = (_dt.date.today() + _dt.timedelta(days=3)).isoformat()
listing_urls = [f"https://www.amctheatres.com/showtimes/all/{day}/{s}/all" for s in slugs]
sess = sfh.make_session()
HDR = {"Accept": "text/html,*/*", "Accept-Language": "en-US,en;q=0.9"}


def draw(url, via_proxy, tag):
    global spent
    if spent >= MAX_BYTES:
        print(f"{tag}: SKIPPED — probe byte budget spent", flush=True)
        return
    kw = {"timeout": 25, "headers": HDR, "stream": True}
    if via_proxy and proxy:
        kw["proxies"] = {"http": proxy, "https": proxy}
    t0 = time.monotonic()
    try:
        r = sess.get(url, **kw)
        raw = 0
        for ch in r.iter_content(chunk_size=16384):
            raw += len(ch)
            if raw > 1024 * 1024:
                break
        spent += raw
        print(f"{tag}: status={r.status_code} {time.monotonic()-t0:5.1f}s {raw/1024:7.1f} KB "
              f"cf-ray={'yes' if r.headers.get('cf-ray') else 'no'}", flush=True)
    except Exception as e:
        print(f"{tag}: ERROR {type(e).__name__} after {time.monotonic()-t0:5.1f}s", flush=True)


print(f"proxy configured: {'yes' if proxy else 'NO'}; {len(listing_urls)} listings, "
      f"{len(seat_urls)} seat pages", flush=True)
for i, u in enumerate(listing_urls):
    draw(u, True, f"proxy listing {i+1}")
for i, u in enumerate(seat_urls):
    draw(u, True, f"proxy seat    {i+1}")
draw("https://ipinfo.io/json", True, "proxy ipinfo  ")
for i, u in enumerate(seat_urls[:2]):
    draw(u, False, f"direct seat   {i+1}")
for i, u in enumerate(listing_urls[:2]):
    draw(u, False, f"direct listing{i+1}")
# A 200 is not proof of data (a challenge page can be a 200): classify direct
# seat pages with the production reader and print its verdict and seat total.
for i, u in enumerate(seat_urls[-4:]):
    t0 = time.monotonic()
    try:
        res = sfh.fetch_seat_page(u, None, session=sess)
        seats = sfh.parse_seat_counts(res["html"]) if res.get("kind") == "seats" else None
        total = (seats or {}).get("total_seats")
        print(f"direct parse  {i+1}: kind={res.get('kind')} total_seats={total} "
              f"{time.monotonic()-t0:4.1f}s", flush=True)
    except Exception as e:
        print(f"direct parse  {i+1}: ERROR {type(e).__name__}", flush=True)
print(f"TOTAL {spent/1048576:.2f} MB", flush=True)
