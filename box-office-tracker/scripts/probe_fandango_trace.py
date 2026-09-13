"""Read-only: watch ONE real browser load a Fandango seat map and record every
request, so we can see which call actually returns the seat states and whether
it is replayable over plain HTTP (the lane currently pays ~7 MB per theatre for
a full render). Prints URLs and sizes only — no credentials."""
import os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import proxy_egress  # noqa: E402
from fandango_probe import UA, CHROMIUM_ARGS, SEAT_COUNT_JS  # noqa: E402
from fandango_collect import SHOWTIME_ENTRIES_JS, load_fandango_theatres  # noqa: E402

SLUG = os.environ.get("PROBE_SLUG", "")
from playwright.sync_api import sync_playwright

theatres = [t for t in load_fandango_theatres() if not SLUG or t["slug"] == SLUG]
th = theatres[0]
print(f"tracing {th['slug']}", flush=True)
calls = []
with sync_playwright() as p:
    browser = p.chromium.launch(**proxy_egress.launch_kwargs({"headless": True, "args": CHROMIUM_ARGS}))
    ctx = browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 1600})
    page = ctx.new_page()

    def on_response(r):
        try:
            calls.append((r.request.resource_type, r.status, r.url))
        except Exception:
            pass
    page.on("response", on_response)

    # A dated visit: an undated theatre page serves only today's REMAINING
    # showtimes, and a started show renders no seat map at all — which is what
    # made the previous two probes inconclusive.
    import datetime as _dt
    when = os.environ.get("PROBE_DATE") or (_dt.date.today() + _dt.timedelta(days=1)).isoformat()
    print(f"visiting theatre page for {when}", flush=True)
    page.goto(f"https://www.fandango.com/{th['slug']}/theater-page?date={when}",
              wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3000)
    entries = page.evaluate(SHOWTIME_ENTRIES_JS)
    print(f"showtime buttons: {len(entries)}", flush=True)
    if not entries:
        print("no showtimes — cannot trace", flush=True); raise SystemExit(0)
    # pick a showtime on the requested date (the page can still carry others)
    dated = [e for e in entries if when.replace("-", "-") in (e.get("href") or "")] or entries
    href = dated[len(dated) // 2]["href"]
    calls.clear()
    page.goto(href, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)
    print(f"seat url: {page.url[:200]}", flush=True)
    try:
        page.wait_for_selector(".seat-map__seat", timeout=15000)
    except Exception:
        print("seat map never rendered", flush=True)
    try:
        seats = page.evaluate(SEAT_COUNT_JS)
        print(f"seats from DOM: {seats}", flush=True)
    except Exception as e:
        print(f"seat count failed: {type(e).__name__}", flush=True)

    # which response carried the seat states?
    print(f"--- {len(calls)} responses on the seat page ---", flush=True)
    for rt, status, url in calls:
        host_ok = any(d in url for d in ("fandango.com", "seatpicker", "availab"))
        if host_ok and (rt in ("xhr", "fetch", "document") or "seatpicker" in url.lower()):
            print(f"  {rt:6s} {status} {url[:230]}", flush=True)
    browser.close()
