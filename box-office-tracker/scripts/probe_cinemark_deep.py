#!/usr/bin/env python3
"""Focused Phase-A probe: reach a Cinemark theatre's showtimes, follow one
showtime toward seat selection, capture the Vista backend calls.

Go/no-go for a Cinemark-DIRECT collector (the split-lane plan: Cinemark direct,
Regal via Fandango). The generic probe confirmed Cinemark renders clean with no
Cloudflare wall but never reached a theatre-detail page. This one navigates
known theatre showtime URLs, records every XHR the seat flow makes, and reports
whether pre-purchase seat state is readable. Read-only; artifact only.
"""
import json
import os
import re
import time

REPORT_DIR = os.environ.get("PROBE_REPORT_DIR", "../chain-probe")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# A few real Cinemark theatre pages (high-volume metros). The probe tries each
# until one exposes showtimes, then follows a showtime.
THEATRE_PAGES = [
    "https://www.cinemark.com/theatres/tx-dallas/cinemark-17-and-imax",
    "https://www.cinemark.com/theatres/ca-los-angeles/cinemark-baldwin-hills-and-xd",
    "https://www.cinemark.com/theatres/tx-plano/cinemark-west-plano-and-xd",
]
INTERESTING = re.compile(
    r"showtime|session|seat|performance|screening|occupanc|availab|"
    r"vista|graphql|/api/|ticketing|booking", re.I)
BORING = ("image/", "font/", "text/css", "video/", "/rokt", "google", "bing",
          "tealium", "analytics")


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(REPORT_DIR, exist_ok=True)
    report = {"captured": [], "pages": []}
    seen = set()

    def on_response(resp):
        try:
            url = resp.url
            if any(b in url.lower() for b in BORING):
                return
            ctype = (resp.headers or {}).get("content-type", "")
            if not INTERESTING.search(url):
                return
            key = re.sub(r"\d{2,}", "N", url.split("?")[0])
            if key in seen:
                return
            seen.add(key)
            row = {"url": url[:280], "status": resp.status, "ctype": ctype[:60]}
            if "json" in ctype and resp.status == 200:
                try:
                    body = resp.text()
                    row["bytes"] = len(body)
                    low = body.lower()
                    row["mentions"] = sorted({w for w in (
                        "seat", "showtime", "session", "performance", "sold",
                        "available", "occupanc", "auditorium", "area", "row")
                        if w in low})
                    row["body_head"] = body[:700]
                except Exception:
                    pass
            report["captured"].append(row)
            print(f"  XHR {resp.status} {ctype[:24]:24s} {url[:100]}"
                  f"{' seats:'+','.join(row.get('mentions',[])) if row.get('mentions') else ''}")
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.on("response", on_response)

        showtime_link = None
        for turl in THEATRE_PAGES:
            note = {"page": turl}
            try:
                page.goto(turl, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(9000)
                note["title"] = page.title()[:120]
                body = (page.inner_text("body") or "").lower()
                note["blocked"] = "sorry" in body and "blocked" in body
                # Cinemark showtime buttons link to a seat/ticketing flow.
                links = page.eval_on_selector_all(
                    "a[href]", "els => els.map(e => e.getAttribute('href'))") or []
                show_links = [h for h in links if h and re.search(
                    r"showtime|seat|ticket|session|/booking|/movies/", h, re.I)]
                note["showtime_link_count"] = len(show_links)
                note["showtime_link_sample"] = show_links[:6]
                # Count on-screen time buttons.
                note["time_buttons"] = page.locator(
                    "a:has-text('PM'), a:has-text('AM'), "
                    "button:has-text('PM'), button:has-text('AM')").count()
            except Exception as e:
                note["error"] = str(e)[:200]
            report["pages"].append(note)
            print(f"[page] {turl.split('/')[-1]} title={note.get('title','?')!r} "
                  f"blocked={note.get('blocked')} time_buttons={note.get('time_buttons')} "
                  f"showtime_links={note.get('showtime_link_count')}")
            if note.get("time_buttons", 0) > 0 and not note.get("blocked"):
                # Click the first time button and capture the seat flow.
                try:
                    btn = page.locator(
                        "a:has-text('PM'), button:has-text('PM'), "
                        "a:has-text('AM'), button:has-text('AM')").first
                    try:
                        showtime_link = btn.get_attribute("href")
                    except Exception:
                        pass
                    btn.click(timeout=10000)
                    page.wait_for_timeout(12000)
                    after = {"stage": "after-showtime-click",
                             "final_url": page.url[:250], "title": page.title()[:120]}
                    seaty = page.locator(
                        "[class*='seat' i], [id*='seat' i], [data-seat], "
                        "[aria-label*='seat' i], svg [class*='seat' i]").count()
                    txt = (page.inner_text("body") or "").lower()[:4000]
                    after["seat_elements"] = seaty
                    after["mentions_seat"] = "seat" in txt
                    after["needs_login"] = "sign in" in txt or "create account" in txt
                    report["pages"].append(after)
                    print(f"[seat-flow] -> {after['final_url'][:80]} "
                          f"seat_elements={seaty} mentions_seat={after['mentions_seat']} "
                          f"needs_login={after['needs_login']}")
                    break
                except Exception as e:
                    report["seat_flow_error"] = str(e)[:200]
                    print(f"[seat-flow] click failed: {e}")
        report["showtime_link_sample"] = showtime_link
        browser.close()

    path = os.path.join(REPORT_DIR, "cinemark-deep.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    seaty = [x for x in report["captured"] if "seat" in (x.get("mentions") or [])]
    print(f"\nverdict inputs: {len(report['captured'])} interesting XHRs, "
          f"{len(seaty)} JSON responses mention seats")
    print(f"report -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
