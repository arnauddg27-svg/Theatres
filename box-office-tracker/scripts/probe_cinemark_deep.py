#!/usr/bin/env python3
"""Focused, hardened Cinemark seat-flow probe (direct-collector go/no-go).

Robustness lessons from the timed-out run: ONE theatre only, short per-step
timeouts, popup/new-tab handling for the ticketing flow, and a hard wall so
the whole probe finishes in ~3 min. Run with `python -u` so output survives a
kill. Read-only; artifact only.
"""
import json
import os
import re
import time

REPORT_DIR = os.environ.get("PROBE_REPORT_DIR", "../chain-probe")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
THEATRE_PAGE = "https://www.cinemark.com/theatres/tx-dallas/cinemark-17-and-imax"
INTERESTING = re.compile(
    r"showtime|session|seat|performance|screening|occupanc|availab|"
    r"vista|graphql|/api/|ticketing|booking", re.I)
BORING = ("image/", "font/", "text/css", "video/", "/rokt", "google", "bing",
          "tealium", "analytics", "doubleclick", "facebook")
DEADLINE = None


def _over(): return DEADLINE is not None and time.monotonic() > DEADLINE


def main():
    global DEADLINE
    from playwright.sync_api import sync_playwright
    os.makedirs(REPORT_DIR, exist_ok=True)
    DEADLINE = time.monotonic() + 170  # hard ~3-min wall
    report = {"captured": [], "pages": [], "theatre_page": THEATRE_PAGE}
    seen = set()

    def on_response(resp):
        try:
            url = resp.url
            if any(b in url.lower() for b in BORING) or not INTERESTING.search(url):
                return
            key = re.sub(r"\d{2,}", "N", url.split("?")[0])
            if key in seen:
                return
            seen.add(key)
            ctype = (resp.headers or {}).get("content-type", "")
            row = {"url": url[:260], "status": resp.status, "ctype": ctype[:50]}
            if "json" in ctype and resp.status == 200:
                try:
                    body = resp.text()
                    row["bytes"] = len(body)
                    low = body.lower()
                    row["mentions"] = sorted({w for w in (
                        "seat", "showtime", "session", "performance", "sold",
                        "available", "occupanc", "auditorium", "area") if w in low})
                    if row["mentions"]:
                        row["body_head"] = body[:800]
                except Exception:
                    pass
            report["captured"].append(row)
            print(f"  XHR {resp.status} {ctype[:22]:22s} {url[:95]}"
                  f"{' SEATS:'+','.join(row['mentions']) if row.get('mentions') else ''}",
                  flush=True)
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
        ctx.on("response", on_response)   # context-level: also catches popup tabs
        page = ctx.new_page()
        note = {"page": THEATRE_PAGE}
        try:
            page.goto(THEATRE_PAGE, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(7000)
            note["title"] = page.title()[:120]
            body = (page.inner_text("body") or "").lower()
            note["blocked"] = "sorry" in body and "blocked" in body
            note["time_buttons"] = page.locator(
                "a:has-text('PM'), button:has-text('PM'), "
                "a:has-text('AM'), button:has-text('AM')").count()
            links = page.eval_on_selector_all(
                "a[href]", "els=>els.map(e=>e.getAttribute('href'))") or []
            note["ticket_link_sample"] = [h for h in links if h and re.search(
                r"seat|ticket|showtime|session|booking", h, re.I)][:6]
        except Exception as e:
            note["error"] = str(e)[:200]
        report["pages"].append(note)
        print(f"[page] title={note.get('title','?')!r} blocked={note.get('blocked')} "
              f"time_buttons={note.get('time_buttons')} "
              f"ticket_links={note.get('ticket_link_sample')}", flush=True)

        if note.get("time_buttons", 0) > 0 and not note.get("blocked") and not _over():
            try:
                btn = page.locator(
                    "a:has-text('PM'), button:has-text('PM'), "
                    "a:has-text('AM'), button:has-text('AM')").first
                href = None
                try:
                    href = btn.get_attribute("href")
                except Exception:
                    pass
                report["showtime_href"] = href
                # The click may open a popup/new tab (ticketing subdomain).
                target = page
                try:
                    with ctx.expect_page(timeout=8000) as pop:
                        btn.click(timeout=8000)
                    target = pop.value
                    print("[seat-flow] opened a NEW TAB", flush=True)
                except Exception:
                    print("[seat-flow] same-tab navigation", flush=True)
                target.wait_for_timeout(9000)
                after = {"stage": "after-click", "final_url": target.url[:250],
                         "title": (target.title() or "")[:120]}
                seaty = target.locator(
                    "[class*='seat' i], [id*='seat' i], [data-seat], "
                    "[aria-label*='seat' i], svg [class*='seat' i]").count()
                txt = (target.inner_text("body") or "").lower()[:4000]
                after["seat_elements"] = seaty
                after["mentions_seat"] = "seat" in txt
                after["needs_login"] = "sign in" in txt or "create account" in txt
                after["blocked"] = "sorry" in txt and "blocked" in txt
                report["pages"].append(after)
                print(f"[seat-flow] -> {after['final_url'][:90]}\n"
                      f"            seat_elements={seaty} mentions_seat={after['mentions_seat']} "
                      f"needs_login={after['needs_login']} blocked={after['blocked']}", flush=True)
            except Exception as e:
                report["seat_flow_error"] = str(e)[:200]
                print(f"[seat-flow] failed: {e}", flush=True)
        browser.close()

    path = os.path.join(REPORT_DIR, "cinemark-deep.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    seaty = [x for x in report["captured"] if "seat" in (x.get("mentions") or [])]
    print(f"\nVERDICT INPUTS: {len(report['captured'])} interesting XHRs; "
          f"{len(seaty)} JSON responses mention seats; "
          f"seat-flow reached: {'seat-flow-error' not in report and any(p.get('stage')=='after-click' for p in report['pages'])}",
          flush=True)
    print(f"report -> {path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
