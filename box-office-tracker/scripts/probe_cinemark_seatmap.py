#!/usr/bin/env python3
"""Final Cinemark validation: seat map without login? + DOM shape + date nav.

Three go/no-go unknowns for cinemark_collect.py, answered in one ~3-min run:
  1. Does /TicketSeatMap/?TheaterId=..&ShowtimeId=.. render seat state
     WITHOUT a login? (harvest a future showtime from the theatre page,
     navigate straight to its seat URL)
  2. What does the seat DOM look like (selector census + HTML sample for the
     collector's seat-counting JS)?
  3. Does the showtimes page take a date parameter (?showDate=YYYY-MM-DD)
     for pre-opening/dated collection?
Read-only, self-capped, artifact-only.
"""
import json
import os
import re
import time
from datetime import datetime, timedelta

REPORT_DIR = os.environ.get("PROBE_REPORT_DIR", "../chain-probe")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
THEATRE = "https://www.cinemark.com/theatres/tx-dallas/cinemark-17-and-imax"
BASE = "https://www.cinemark.com"


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(REPORT_DIR, exist_ok=True)
    deadline = time.monotonic() + 170
    report = {}
    seat_json = []

    def on_response(resp):
        try:
            url = resp.url
            ctype = (resp.headers or {}).get("content-type", "")
            if "json" in ctype and re.search(r"seat|ticket|showtime|session", url, re.I):
                row = {"url": url[:250], "status": resp.status}
                try:
                    row["body_head"] = resp.text()[:800]
                except Exception:
                    pass
                seat_json.append(row)
                print(f"  seatish JSON {resp.status} {url[:100]}", flush=True)
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
        ctx.on("response", on_response)
        page = ctx.new_page()

        # 1+2: theatre page -> harvest a FUTURE TicketSeatMap link -> visit it.
        page.goto(THEATRE, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(6000)
        links = page.eval_on_selector_all(
            "a[href*='TicketSeatMap']", "els=>els.map(e=>e.getAttribute('href'))") or []
        report["seatmap_links_found"] = len(links)
        future = None
        now = datetime.utcnow()
        for h in links:
            m = re.search(r"Showtime=([\dT:\-]+)", h or "")
            if not m:
                continue
            try:
                st = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                continue
            if st > now + timedelta(hours=3):   # local-vs-utc slack; want clearly future
                future = h
                break
        report["future_seatmap_href"] = (future or "")[:250]
        print(f"[harvest] {len(links)} seat links; future pick: {future}", flush=True)

        if future and time.monotonic() < deadline:
            url = future if future.startswith("http") else BASE + future
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(9000)
            res = {"final_url": page.url[:250], "title": page.title()[:120]}
            txt = (page.inner_text("body") or "")[:5000]
            low = txt.lower()
            res["needs_login"] = ("sign in" in low or "log in" in low) and "seat" not in low
            res["mentions_seat"] = "seat" in low
            counts = {}
            for sel in ("[class*='seat' i]", "[data-seat]", "[aria-label*='seat' i]",
                        "svg circle", "svg rect", "button[class*='seat' i]",
                        "[class*='available' i]", "[class*='occupied' i]",
                        "[class*='sold' i]", "[class*='unavailable' i]"):
                try:
                    counts[sel] = page.locator(sel).count()
                except Exception:
                    counts[sel] = -1
            res["selector_census"] = counts
            # HTML sample around the densest seat-ish container for selector work.
            try:
                sample = page.evaluate(
                    "() => { const el = document.querySelector(\"[class*='seat' i]\");"
                    " if (!el) return null; const c = el.closest('div,section,main') || el;"
                    " return c.outerHTML.slice(0, 4000); }")
                res["seat_container_html"] = sample
            except Exception:
                pass
            report["seatmap_visit"] = res
            print(f"[seatmap] {res['final_url'][:90]}\n"
                  f"  needs_login={res['needs_login']} mentions_seat={res['mentions_seat']}\n"
                  f"  census={counts}", flush=True)

        # 3: date navigation on the showtimes page.
        if time.monotonic() < deadline:
            tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
            for param in ("showDate", "date"):
                try:
                    page.goto(f"{THEATRE}?{param}={tomorrow}",
                              wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(6000)
                    n = page.locator("a[href*='TicketSeatMap']").count()
                    stamps = page.eval_on_selector_all(
                        "a[href*='TicketSeatMap']",
                        "els=>els.slice(0,3).map(e=>e.getAttribute('href'))") or []
                    dates = sorted({(re.search(r"Showtime=(\d{4}-\d{2}-\d{2})", h or "") or [None, None])[1]
                                    for h in stamps if h})
                    report[f"date_param_{param}"] = {"seatmap_links": n, "dates_seen": [d for d in dates if d]}
                    print(f"[date-nav] ?{param}={tomorrow} -> {n} seat links, dates {dates}", flush=True)
                except Exception as e:
                    report[f"date_param_{param}"] = {"error": str(e)[:150]}
        browser.close()

    report["seat_json_endpoints"] = seat_json
    with open(os.path.join(REPORT_DIR, "cinemark-seatmap.json"), "w") as f:
        json.dump(report, f, indent=2)
    print("report -> cinemark-seatmap.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
