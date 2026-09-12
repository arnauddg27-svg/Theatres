"""Read-only probe (hard byte ceiling): can Fandango seat availability be read
over plain HTTP through the residential proxy, i.e. WITHOUT a browser?

If yes, Regal escapes Fandango's per-network ~30 renders/hour budget (each
request leaves from a different residential address) and its seat coverage
stops being the bottleneck. Prints no credentials."""
import csv, os, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
MAX_BYTES = int(float(os.environ.get("PROBE_MAX_MB", "20")) * 1024 * 1024)
spent = 0
sess = sfh.make_session()
DATA = Path(__file__).resolve().parents[1] / "data" / "fandango-pre-reservation-snapshots.csv"


def get(url, tag, headers=None):
    global spent
    if spent >= MAX_BYTES:
        print(f"{tag}: SKIPPED (budget spent)", flush=True); return None, b""
    kw = {"stream": True, "timeout": 30,
          "headers": headers or {"Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                                 "Accept-Language": "en-US,en;q=0.9"}}
    if proxy:
        kw["proxies"] = {"http": proxy, "https": proxy}
    try:
        r = sess.get(url, **kw)
    except Exception as e:
        print(f"{tag}: ERROR {type(e).__name__}: {str(e)[:110]}", flush=True); return None, b""
    raw = 0; out = bytearray()
    inf = sfh._Inflater(r.headers.get("content-encoding", ""))
    for ch in r.iter_content(chunk_size=16384):
        raw += len(ch); out += inf.feed(ch)
        if raw > 2 * 1024 * 1024:
            break
    r.close(); spent += raw
    b = bytes(out)
    title = re.search(rb"<title[^>]*>(.*?)</title>", b, re.I | re.S)
    print(f"{tag}: status={r.status_code} raw={raw} decoded={len(b)} "
          f"ctype={str(r.headers.get('content-type'))[:26]} "
          f"title={(title.group(1)[:50].decode('utf-8','ignore').strip() if title else '')!r} "
          f"[spent {spent/1048576:.1f} MB]", flush=True)
    return r, b


urls = []
with open(DATA, newline="") as f:
    for row in csv.DictReader(f):
        if row.get("chain") == "REGL" and (row.get("snapshot_bucket") or "")[:10] >= "2026-09-11":
            u = row.get("amc_seat_map_url") or ""
            if "seatselection" in u:
                urls.append(u)
print(f"proxy={'ON' if proxy else 'off'} budget={MAX_BYTES/1048576:.0f} MB | {len(urls)} candidate seat urls", flush=True)

for u in urls[-2:]:
    r, b = get(u, f"SEATPAGE {u[-40:]}")
    if not b:
        continue
    # Are seat states already in the HTML the server sent?
    for key in (b"seat-map__seat", b"availableSeat", b"reservedSeat", b"seatPickerAvailabilityUrl",
                b'"seats"', b"SeatsAvailable", b"__NEXT_DATA__", b"seatData"):
        n = b.count(key)
        if n:
            j = b.find(key)
            print(f"  {key.decode()} x{n} @{j}: {b[max(0,j-120):j+200].decode('utf-8','ignore')!r}", flush=True)
    # the availability endpoint the page would call
    m = re.search(rb"seatPickerAvailabilityUrl['\"]?\s*[:=]\s*['\"]([^'\"]+)", b)
    if m:
        av = m.group(1).decode("utf-8", "ignore").replace("&amp;", "&")
        print(f"  availability url: {av[:220]}", flush=True)
        time.sleep(1)
        full = av if av.startswith("http") else "https://tickets.fandango.com" + av
        r2, ab = get(full, "AVAILABILITY",
                     headers={"Accept": "application/json,text/plain,*/*", "X-Requested-With": "XMLHttpRequest"})
        print(f"  AVAIL BODY ({len(ab)} B): {ab[:1500].decode('utf-8','ignore')!r}", flush=True)
        # the API names its own required parameters: tid, mid, sdate, t, quantity
        time.sleep(1)
        withq = full + "&quantity=1"
        r3, sb = get(withq, "AVAIL+quantity",
                     headers={"Accept": "application/json,text/plain,*/*", "X-Requested-With": "XMLHttpRequest"})
        if sb:
            print(f"  +quantity BODY ({len(sb)} B) head: {sb[:900].decode('utf-8','ignore')!r}", flush=True)
            for key in (b'"seats"', b'"available"', b'"status"', b'"rows"', b'"seat_status"',
                        b'"unavailable"', b'"sold"', b'"total"'):
                n = sb.count(key)
                if n:
                    j = sb.find(key)
                    print(f"    {key.decode()} x{n}: {sb[max(0,j-80):j+260].decode('utf-8','ignore')!r}", flush=True)
    time.sleep(1)
