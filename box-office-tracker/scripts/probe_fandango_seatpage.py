"""Read-only: is Fandango's seat state in the seat page's HTML, or only after
the browser hydrates it? If it is server-rendered, Regal costs ~1 page instead
of a ~7 MB browser render and the whole pool becomes affordable.
Uses seat URLs the lane already stored. Prints no credentials."""
import csv, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
N = max(1, min(6, int(os.environ.get("PROBE_N", "3") or 3)))
csv_path = Path(__file__).resolve().parents[1] / "data" / "fandango-pre-reservation-snapshots.csv"
# FUTURE showtimes only: a started show legitimately returns an empty seat
# list, which would look identical to "the handshake is missing".
import datetime as _dt
_today = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
rows = [r for r in csv.DictReader(open(csv_path))
        if r.get("chain") == "REGL" and r.get("amc_seat_map_url", "").startswith("http")]
future = [r for r in rows if (r.get("show_date") or "") > _today]
picked = (future or rows)[-N:]
print(f"today={_today} rows={len(rows)} future={len(future)} using={'future' if future else 'ANY (no future rows)'}", flush=True)
for r in picked[:1]:
    print(f"  sample: show_date={r.get('show_date')} showtime={r.get('showtime')}", flush=True)
urls = [r["amc_seat_map_url"] for r in picked]
print(f"proxy={'ON' if proxy else 'off'} testing {len(urls)} stored Regal seat URLs", flush=True)
sess = sfh.make_session()
for u in urls:
    try:
        res = sfh.fetch_seat_page(u, proxy, session=sess)
    except Exception as e:
        print(f"ERROR {type(e).__name__}: {str(e)[:110]}", flush=True); continue
    h = res["html"]
    marks = {k: h.count(k) for k in ("seat-map__seat", "availableSeat", "reservedSeat",
                                     "seatPickerAvailabilityUrl", "__NEXT_DATA__", "seatsAvailable")}
    title = re.search(r"<title[^>]*>(.*?)</title>", h, re.S)
    print(f"raw={res['raw_bytes']} html={len(h)} kind={res['kind']} "
          f"title={(title.group(1).strip()[:40] if title else '')!r} marks={marks}", flush=True)
    # What does the page's own script have to work with? (session/order ids,
    # tokens, other endpoints) — this is what the availability call is missing.
    varz = re.findall(r"var\s+([A-Za-z_][\w]*)\s*=\s*'([^']{0,160})'", h)
    interesting = [(k, v) for k, v in varz if v and not v.isdigit() and len(v) > 1]
    print(f"   page vars ({len(varz)}): {interesting[:22]}", flush=True)
    for key in ("Set-Cookie", "orderid", "order_id", "sessionid", "token", "csrf", "guid"):
        i = h.lower().find(key.lower())
        if i != -1:
            print(f"      [{key}] {h[max(0,i-80):i+160]!r}", flush=True)
    m = re.search(r"seatPickerAvailabilityUrl\s*=\s*'([^']+)'", h)
    if not m:
        print("   no availability url", flush=True); continue
    from html import unescape
    avail_url = unescape(m.group(1))
    print(f"   availability url: {avail_url[:200]}", flush=True)
    # cookies the seat page set on this session (names only)
    try:
        jar = getattr(sess, "cookies", None)
        names = sorted({c.name for c in jar}) if jar is not None else []
        print(f"   session cookies: {names[:14]}", flush=True)
    except Exception as e:
        print(f"   cookie read failed: {type(e).__name__}", flush=True)
    try:
        res2 = sfh.fetch_seat_page(avail_url, proxy, session=sess)
    except Exception as e:
        print(f"   AVAIL ERROR {type(e).__name__}: {str(e)[:110]}", flush=True); continue
    body = res2["html"]
    print(f"   AVAIL raw={res2['raw_bytes']} len={len(body)} head={body[:400]!r}", flush=True)
    for k in ("available", "reserved", "seat", "Status", "rows"):
        print(f"      {k!r} x{body.lower().count(k.lower())}", flush=True)
