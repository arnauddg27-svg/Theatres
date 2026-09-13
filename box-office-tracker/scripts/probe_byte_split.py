"""Read-only: where do a Regal (Fandango) / Cinemark seat render's megabytes
actually go? Sums wire bytes per host so the blocklist can be precise instead
of type-based (type-based trimming tripped cinemark.com's bot check).
PROBE_KIND=fandango|cinemark. Prints hosts and sizes only."""
import collections, os, sys
from urllib.parse import urlparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import proxy_egress  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

WHICH = (os.environ.get("PROBE_SITE") or "fandango").strip().lower()
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")


def measure(page, label):
    by_host = collections.Counter()
    by_type = collections.Counter()
    n = collections.Counter()

    def on_done(r):
        try:
            host = urlparse(r.url).netloc
            size = 0
            try:
                size = int(r.headers.get("content-length") or 0)
            except Exception:
                size = 0
            if not size:
                try:
                    size = len(r.body())
                except Exception:
                    size = 0
            by_host[host] += size
            by_type[r.request.resource_type] += size
            n[host] += 1
        except Exception:
            pass
    page.on("response", on_done)
    return by_host, by_type, n


def report(label, by_host, by_type, n, first_party):
    total = sum(by_host.values())
    fp = sum(v for h, v in by_host.items() if any(d in h for d in first_party))
    print(f"\n=== {label}: {total/1048576:.2f} MB over {sum(n.values())} responses ===", flush=True)
    print(f"  first-party {fp/1048576:.2f} MB ({fp/total:.0%})  third-party {(total-fp)/1048576:.2f} MB ({(total-fp)/total:.0%})", flush=True)
    print("  by resource type: " + ", ".join(f"{k}={v/1024:.0f}KB" for k, v in by_type.most_common(8)), flush=True)
    print("  top hosts:", flush=True)
    for h, v in by_host.most_common(14):
        tag = "FIRST" if any(d in h for d in first_party) else "third"
        print(f"    {tag} {v/1024:8.0f} KB  x{n[h]:3d}  {h}", flush=True)


with sync_playwright() as p:
    browser = p.chromium.launch(**proxy_egress.launch_kwargs(
        {"headless": True, "args": ["--disable-blink-features=AutomationControlled"]}))
    ctx = browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 1600})
    page = ctx.new_page()
    by_host, by_type, n = measure(page, WHICH)
    if WHICH == "cinemark":
        first_party = ("cinemark.com",)
        page.goto("https://www.cinemark.com/theatres", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)
        report("cinemark theatres page", by_host, by_type, n, first_party)
    else:
        first_party = ("fandango.com",)
        import datetime as _dt
        when = (_dt.date.today() + _dt.timedelta(days=1)).isoformat()
        page.goto(f"https://www.fandango.com/regal-atlas-park-aatzo/theater-page?date={when}",
                  wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)
        report("fandango theatre page", by_host, by_type, n, first_party)
        by_host.clear(); by_type.clear(); n.clear()
        from fandango_collect import SHOWTIME_ENTRIES_JS
        entries = page.evaluate(SHOWTIME_ENTRIES_JS)
        if entries:
            page.goto(entries[len(entries)//2]["href"], wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(5000)
            report("fandango SEAT page", by_host, by_type, n, first_party)
    browser.close()
