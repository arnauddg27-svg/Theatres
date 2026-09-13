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

    page.goto(f"https://www.fandango.com/{th['slug']}/theater-page", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3000)
    entries = page.evaluate(SHOWTIME_ENTRIES_JS)
    print(f"showtime buttons: {len(entries)}", flush=True)
    if not entries:
        print("no showtimes — cannot trace", flush=True); raise SystemExit(0)
    href = entries[len(entries) // 2]["href"]
    calls.clear()
    page.goto(href, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)
    print(f"seat url: {page.url[:200]}", flush=True)
    try:
        seats = page.evaluate(SEAT_COUNT_JS)
        print(f"seats from DOM: {seats}", flush=True)
    except Exception as e:
        print(f"seat count failed: {type(e).__name__}", flush=True)

    # which response carried the seat states?
    print(f"--- {len(calls)} responses on the seat page ---", flush=True)
    for rt, status, url in calls:
        if rt in ("xhr", "fetch") or "seatpicker" in url.lower() or "availab" in url.lower():
            print(f"  {rt:6s} {status} {url[:230]}", flush=True)
    browser.close()
