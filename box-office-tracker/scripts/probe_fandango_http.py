"""Read-only probe: replicate Fandango's ticket flow over plain HTTP through the
residential proxy — theater page -> jump.aspx (establishes the order context)
-> seatpicker availability JSON. If this works, Regal seat data costs ~1 KB per
showtime instead of a browser render, and escapes the per-network render budget."""
import json, os, re, sys, time
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
MAX_BYTES = int(float(os.environ.get("PROBE_MAX_MB", "20")) * 1024 * 1024)
spent = 0
sess = sfh.make_session()
UA_HDRS = {"Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"}


def get(url, tag, headers=None, quiet=False):
    global spent
    if spent >= MAX_BYTES:
        print(f"{tag}: SKIPPED (budget)", flush=True); return None, b""
    kw = {"stream": True, "timeout": 30, "headers": headers or UA_HDRS}
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
    if not quiet:
        print(f"{tag}: status={r.status_code} raw={raw} final={str(getattr(r,'url','' ))[:110]} [spent {spent/1048576:.2f} MB]", flush=True)
    return r, b


print(f"proxy={'ON' if proxy else 'off'} budget={MAX_BYTES/1048576:.0f} MB", flush=True)

# 1. a Regal theatre page on Fandango (the collector already loads these)
pool = json.load(open(Path(__file__).resolve().parents[1] / "data" / "theatres-fandango.json"))["theatres"]
slug = next(t["slug"] for t in pool if t["chain"] == "REGL")
r, page = get(f"https://www.fandango.com/{slug}/theater-page", f"THEATREPAGE {slug}")
jumps = sorted({m.decode("utf-8", "ignore").replace("&amp;", "&")
                for m in re.findall(rb'href="([^"]*jump\.aspx[^"]*)"', page or b"")})
print(f"  jump links: {len(jumps)} e.g. {jumps[:1]}", flush=True)

# 2. follow one jump (sets the order context) and read where it lands
if jumps:
    j = jumps[0]
    j = j if j.startswith("http") else "https://www.fandango.com" + j
    time.sleep(1)
    r2, land = get(j, "JUMP")
    final = str(getattr(r2, "url", "") or "")
    q = parse_qs(urlparse(final).query)
    print(f"  landed params: { {k: v[0] for k, v in q.items() if k in ('tid','mid','sdate','chainCode','row_count')} }", flush=True)
    print(f"  cookies now: {sorted(sess.cookies.keys()) if hasattr(sess, 'cookies') else 'n/a'}", flush=True)

    # 3. the availability JSON with the params from the landing URL
    tid, mid = q.get("tid", [""])[0], q.get("mid", [""])[0]
    sdate_raw = unquote(q.get("sdate", [""])[0])
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[ T+]*(\d{2}):(\d{2})", sdate_raw)
    if tid and mid and m:
        y, mo, d, hh, mm = m.groups()
        api = ("https://tickets.fandango.com/transaction/ticketing/seatpicker/Default.aspx"
               f"?tid={tid}&t={hh}:{mm}&best_availability=1&mid={mid}&sdate={int(mo)}/{int(d)}/{y}"
               "&action=availability&quantity=1")
        time.sleep(1)
        r3, ab = get(api, "AVAILABILITY")
        print(f"  AVAIL ({len(ab)} B): {ab[:1400].decode('utf-8','ignore')!r}", flush=True)
        try:
            js = json.loads(ab)
            resp = js.get("response", {})
            print(f"  status={resp.get('status')} manifest_areas={len(resp.get('manifest',{}).get('areas',[]))}", flush=True)
        except Exception:
            pass
