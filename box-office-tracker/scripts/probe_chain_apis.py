#!/usr/bin/env python3
"""Phase A probe: what do Regal and Cinemark's OWN sites expose, and from where?

Feasibility question for the direct-chain census (Phase C scaling): the
Fandango lane is capped by a per-Azure-range seat-backend budget, so scaling
past ~260 theatres/weekend needs the chains' own sites, each an independent
rate-limit domain. This probe answers, from a US GitHub runner:

  1. Do plain HTTPS requests reach each chain (bot-wall posture)?
  2. What JSON/XHR endpoints do their theatre pages actually call
     (discovered by Playwright network capture, not guessed)?
  3. Is showtime data present? Is per-showtime SEAT state reachable
     pre-purchase without a login/session?

Read-only reconnaissance: a handful of page loads per chain, standard
browser UA, no purchases, no logins, no fan-out. Writes a JSON report to
../chain-probe/report.json (uploaded as a workflow artifact) and prints a
human summary. Modeled on fandango_probe.py, which answered the same
questions for Fandango before its collector was built.
"""
import json
import os
import re
import sys
import time

REPORT_DIR = os.environ.get("PROBE_REPORT_DIR", "../chain-probe")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

CHAINS = {
    "cinemark": {
        "requests_candidates": [
            "https://www.cinemark.com/",
            "https://www.cinemark.com/theatres/tx-dallas",
            "https://www.cinemark.com/api/vista/data/theatres",
        ],
        "browser_pages": [
            "https://www.cinemark.com/theatres/tx-dallas",
        ],
    },
    "regal": {
        "requests_candidates": [
            "https://www.regmovies.com/",
            "https://www.regmovies.com/theatres",
            "https://api.regmovies.com/v1/theatres",
        ],
        "browser_pages": [
            "https://www.regmovies.com/theatres",
        ],
    },
}

INTERESTING = re.compile(
    r"showtime|session|seat|performance|screening|occupancy|availab|"
    r"theatre|theater|film|movie|graphql|api", re.I)
BORING_TYPES = ("image/", "font/", "text/css", "video/")


def probe_requests(chain, urls, report):
    import requests
    out = []
    for url in urls:
        row = {"url": url}
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=25)
            row["status"] = r.status_code
            ctype = r.headers.get("content-type", "")
            row["content_type"] = ctype
            body = r.text or ""
            row["bytes"] = len(body)
            row["cloudflare_block"] = ("you have been blocked" in body.lower()
                                       or "cf-chl" in body.lower()
                                       or r.status_code in (403, 503))
            if "json" in ctype:
                row["body_head"] = body[:400]
        except Exception as e:
            row["error"] = str(e)[:200]
        out.append(row)
        print(f"  [requests] {chain} {url} -> {row.get('status', row.get('error'))}"
              f"{' BLOCKED' if row.get('cloudflare_block') else ''}")
        time.sleep(2)
    report[chain]["requests"] = out


def probe_browser(chain, pages, report):
    from playwright.sync_api import sync_playwright
    captured = []
    seen = set()

    def on_response(resp):
        try:
            url = resp.url
            ctype = (resp.headers or {}).get("content-type", "")
            if any(ctype.startswith(b) for b in BORING_TYPES):
                return
            if not INTERESTING.search(url):
                return
            key = re.sub(r"\d+", "N", url.split("?")[0])
            if key in seen:
                return
            seen.add(key)
            row = {"url": url[:300], "status": resp.status, "content_type": ctype[:80]}
            if "json" in ctype and resp.status == 200:
                try:
                    body = resp.text()
                    row["bytes"] = len(body)
                    row["body_head"] = body[:600]
                    low = body.lower()
                    row["mentions"] = sorted({w for w in (
                        "showtime", "seat", "session", "performance", "sold",
                        "available", "auditorium", "occupancy") if w in low})
                except Exception:
                    pass
            captured.append(row)
        except Exception:
            pass

    page_notes = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.on("response", on_response)

        def visit(url, wait_ms=8000):
            note = {"page": url[:200]}
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(wait_ms)
                note["title"] = page.title()[:120]
                body_text = (page.inner_text("body") or "")[:2000].lower()
                note["blocked"] = ("blocked" in body_text and "sorry" in body_text) or \
                                  "verify you are a human" in body_text
                note["time_buttons"] = page.locator(
                    "a:has-text('PM'), a:has-text('AM'), "
                    "button:has-text('PM'), button:has-text('AM')").count()
            except Exception as e:
                note["error"] = str(e)[:200]
            page_notes.append(note)
            print(f"  [browser] {chain} {url[:90]} -> title={note.get('title','?')!r} "
                  f"blocked={note.get('blocked')} time_buttons={note.get('time_buttons')}")
            return note

        for url in pages:
            visit(url)

        # DEEPEN: harvest a real theatre-detail link from the locator page,
        # visit it, then follow ONE showtime toward seat selection (pre-
        # payment, same depth the Fandango collector uses). Read-only.
        try:
            hrefs = page.eval_on_selector_all(
                "a[href*='/theatres/']",
                "els => els.map(e => e.getAttribute('href'))")
            detail = [h for h in hrefs or []
                      if h and h.count('/') >= 3 and 'theatres' in h][:3]
            report[chain]["theatre_links_sample"] = detail
            if detail:
                base = pages[0].split('/theatres')[0]
                turl = detail[0] if detail[0].startswith('http') else base + detail[0]
                tnote = visit(turl, wait_ms=9000)
                if tnote.get("time_buttons", 0) > 0 and not tnote.get("blocked"):
                    st = page.locator(
                        "a:has-text('PM'), button:has-text('PM'), "
                        "a:has-text('AM'), button:has-text('AM')").first
                    st_href = None
                    try:
                        st_href = st.get_attribute("href")
                    except Exception:
                        pass
                    report[chain]["showtime_href_sample"] = (st_href or "")[:300]
                    try:
                        st.click(timeout=10000)
                        page.wait_for_timeout(12000)
                        note2 = {"page": "after-showtime-click",
                                 "final_url": page.url[:250],
                                 "title": page.title()[:120]}
                        seaty = page.locator(
                            "[class*='seat' i], [id*='seat' i], "
                            "svg [class*='seat' i], [data-seat], "
                            "[aria-label*='seat' i]").count()
                        note2["seat_elements"] = seaty
                        body_text = (page.inner_text("body") or "")[:3000].lower()
                        note2["mentions_login"] = ("sign in" in body_text
                                                  or "log in" in body_text)
                        note2["mentions_seat"] = "seat" in body_text
                        page_notes.append(note2)
                        print(f"  [browser] {chain} after-click -> {note2['final_url'][:80]} "
                              f"seat_elements={seaty} mentions_seat={note2['mentions_seat']}")
                    except Exception as e:
                        report[chain]["showtime_click_error"] = str(e)[:200]
        except Exception as e:
            report[chain]["deepen_error"] = str(e)[:250]
        browser.close()
    report[chain]["browser_pages"] = page_notes
    report[chain]["xhr_endpoints"] = captured


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)
    report = {chain: {} for chain in CHAINS}
    try:
        import requests  # noqa: F401
        egress = None
        try:
            import requests as rq
            egress = rq.get("https://api.ipify.org", timeout=10).text.strip()
        except Exception:
            pass
        report["egress_ip"] = egress
        print(f"egress IP: {egress}")
    except ImportError:
        print("requests not installed; skipping requests probes")

    for chain, cfg in CHAINS.items():
        print(f"\n== {chain.upper()} ==")
        try:
            probe_requests(chain, cfg["requests_candidates"], report)
        except Exception as e:
            report[chain]["requests_error"] = str(e)[:200]
        try:
            probe_browser(chain, cfg["browser_pages"], report)
        except Exception as e:
            report[chain]["browser_error"] = str(e)[:300]
            print(f"  [browser] {chain} probe failed: {e}")

    path = os.path.join(REPORT_DIR, "report.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nreport written to {path}")

    # Human summary
    for chain in CHAINS:
        xhr = report[chain].get("xhr_endpoints") or []
        json_hits = [x for x in xhr if x.get("body_head")]
        seaty = [x for x in xhr if "seat" in (x.get("url", "").lower())
                 or "seat" in (x.get("mentions") or [])]
        print(f"{chain}: {len(xhr)} interesting endpoints, "
              f"{len(json_hits)} JSON bodies captured, "
              f"{len(seaty)} mention seats")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
