#!/usr/bin/env python3
"""Phase A validation prototype — Fandango non-AMC seat-availability probe.

ISOLATED: writes ONLY to data/fandango-probe.csv (gitignored). Imports nothing
that touches the production seat-counts / pre-reservation CSVs. Its job is to
answer the three Phase A gate questions before any pipeline integration:

  A1 (discovery)   — can we resolve {zip} -> theatre -> showtime -> seat page,
                     tagged by chain, filtering OUT AMC (we already scrape AMC)?
  A2 (completeness)— does the seat DOM render the FULL auditorium (not a
                     virtualized/section subset)? Signal: the seat-map container
                     is not scrollable (zoom-to-fit) AND rows form a complete
                     A.. sequence.
  A3 (anti-bot)    — what is the throttle/block rate at realistic cadence?
                     (Local run is indicative; the real test is a GH-hosted
                     dry-run on the pipeline's IPs.)

Validated live (2026-06-22) across REGL/CNMK/CPLS, houses 50–98 seats: every
seat page rendered the complete auditorium in a non-scrollable container.

Run:  python3 fandango_probe.py            # default zips, 3 showtimes/theatre
      python3 fandango_probe.py --selftest # offline unit checks (no network)
"""
import csv
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

import requests

DATA_DIR = Path(__file__).resolve().parent / "data"
PROBE_CSV = DATA_DIR / "fandango-probe.csv"

# Chains we WANT (suburban, family-skewing — the AMC blind spot). AMC is
# excluded because the production lane already scrapes it directly.
WANTED_CHAINS = {"REGL", "CNMK"}          # Regal, Cinemark
EXCLUDED_CHAINS = {"AMC"}

# A few metro ZIPs likely to host Regal + Cinemark.
DEFAULT_ZIPS = ["75201", "85004", "30303", "63101", "92101"]

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
CHROMIUM_ARGS = ["--no-sandbox", "--disable-blink-features=AutomationControlled"]

PROBE_FIELDS = [
    "probed_at", "zip", "chain", "theatre_slug", "tid", "mid", "sdate",
    "total_seats", "reserved_seats", "available_seats", "occupancy_pct",
    "row_count", "rows_span", "container_fits", "complete", "status",
]


# ── Pure logic (offline-testable) ────────────────────────────────────────────

def theater_page_links(movietimes_html):
    """Extract (slug, chain_guess) theater-page links from a movietimes SSR page.

    Theatre identity (the `aaid`, == the seat page's `tid`) is the slug suffix.
    Chain is inferred from the slug prefix (regal-* / cinemark-*).
    """
    out = []
    for slug in re.findall(r'/([a-z0-9\-]+-[a-z]{4,6})/theater-page', movietimes_html):
        low = slug.lower()
        if low.startswith("regal-"):
            chain = "REGL"
        elif low.startswith("cinemark-"):
            chain = "CNMK"
        else:
            continue
        out.append((slug, chain))
    # de-dup, preserve order
    seen, uniq = set(), []
    for s, c in out:
        if s not in seen:
            seen.add(s)
            uniq.append((s, c))
    return uniq


def seat_url_params(seat_url):
    """Pull chainCode/tid/mid/sdate from a seatselection URL (final, post-jump)."""
    q = parse_qs(urlparse(seat_url).query)
    return {
        "chain": (q.get("chainCode") or [""])[0].upper(),
        "tid": (q.get("tid") or [""])[0],
        "mid": (q.get("mid") or [""])[0],
        "sdate": unquote((q.get("sdate") or [""])[0]),
        "is_seat_page": "seatselection" in urlparse(seat_url).path.lower(),
    }


def is_wanted_chain(chain):
    return chain in WANTED_CHAINS and chain not in EXCLUDED_CHAINS


def assess_completeness(total, rows_span, container_fits):
    """A2 verdict for one seat page: full auditorium rendered, not virtualized."""
    # complete row sequence A.. with no gaps, plausible seat count, and the
    # map fits its container (zoom-to-fit ⇒ all seats are in the DOM).
    contiguous = bool(rows_span) and rows_span[0] == "A"
    return bool(container_fits and contiguous and total >= 10)


# ── Browser I/O (mirrors scraper.py's stealth launch) ────────────────────────

SEAT_COUNT_JS = """() => {
  const seats = [...document.querySelectorAll('.seat-map__seat')];
  const rows = new Set();
  seats.forEach(s => { const l=(s.getAttribute('aria-label')||s.id||'');
    const m=l.match(/row\\s*([A-Z]+)/i)||l.match(/\\b([A-Z])\\d/); if(m) rows.add(m[1].toUpperCase()); });
  const cont = document.querySelector('[class*="seat-map"]');
  const sorted = [...rows].sort();
  return {
    total: seats.length,
    available: document.querySelectorAll('.availableSeat').length,
    reserved: document.querySelectorAll('.reservedSeat').length,
    rowSpan: sorted.length ? sorted[0] + '-' + sorted[sorted.length-1] : '',
    rowFirst: sorted[0] || '',
    containerFits: cont ? (cont.scrollHeight <= cont.clientHeight + 1 &&
                           cont.scrollWidth  <= cont.clientWidth + 1) : null,
  };
}"""


def looks_blocked(page):
    """A3 sentinel: Akamai / access-denied / queue interstitial."""
    title = (page.title() or "").lower()
    url = page.url.lower()
    if any(s in title for s in ("access denied", "pardon", "reference #", "just a moment")):
        return True
    if "errors.edgesuite" in url or "/_sec/" in url:
        return True
    return False


def showtime_jump_hrefs(page):
    """Hydrated jump.aspx hrefs behind the time buttons on a theater page."""
    return page.eval_on_selector_all(
        "a",
        """els => els.filter(a => /^\\d{1,2}:\\d{2}\\s*[ap]/i.test((a.textContent||'').trim())
                                   && /jump\\.aspx/i.test(a.href)).map(a => a.href)"""
    )


def probe(zips, per_theatre=3, max_theatres=8):
    from playwright.sync_api import sync_playwright

    # A1 discovery via requests (theater-page links are in the movietimes SSR).
    theatres = []
    for z in zips:
        try:
            html = requests.get(f"https://www.fandango.com/{z}_movietimes",
                                 headers={"User-Agent": UA}, timeout=20).text
            for slug, chain in theater_page_links(html):
                if is_wanted_chain(chain):
                    theatres.append((z, slug, chain))
        except Exception as e:
            print(f"  discover {z}: ERROR {e}")
    # de-dup by slug, cap
    seen, picked = set(), []
    for z, slug, chain in theatres:
        if slug not in seen:
            seen.add(slug)
            picked.append((z, slug, chain))
    picked = picked[:max_theatres]
    print(f"A1 discovery: {len(picked)} Regal/Cinemark theatres across {len(zips)} zips")

    rows, blocks, renders = [], 0, 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        for z, slug, chain in picked:
            try:
                page.goto(f"https://www.fandango.com/{slug}/theater-page",
                          wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1500)
                if looks_blocked(page):
                    blocks += 1
                    print(f"  {slug}: BLOCKED on theater-page")
                    continue
                hrefs = showtime_jump_hrefs(page)[:per_theatre]
                for href in hrefs:
                    time.sleep(random.uniform(1.0, 2.5))   # polite cadence
                    renders += 1
                    page.goto(href, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1200)
                    if looks_blocked(page):
                        blocks += 1
                        rows.append(_row(z, slug, {}, {}, "blocked"))
                        continue
                    params = seat_url_params(page.url)
                    if not params["is_seat_page"] or not is_wanted_chain(params["chain"]):
                        rows.append(_row(z, slug, params, {}, "no_seat_map"))
                        continue
                    try:
                        page.wait_for_selector(".seat-map__seat", timeout=8000)
                    except Exception:
                        rows.append(_row(z, slug, params, {}, "no_seats_rendered"))
                        continue
                    s = page.evaluate(SEAT_COUNT_JS)
                    rows.append(_row(z, slug, params, s, "ok"))
            except Exception as e:
                print(f"  {slug}: ERROR {str(e)[:80]}")
        browser.close()

    _write(rows)
    _verdict(rows, blocks, renders, len(picked))
    return rows


def _row(zip_code, slug, params, seats, status):
    total = seats.get("total", 0)
    reserved = seats.get("reserved", 0)
    occ = round(reserved / total * 100, 1) if total else 0.0
    span = seats.get("rowSpan", "")
    fits = seats.get("containerFits")
    return {
        "probed_at": datetime.now(timezone.utc).isoformat(),
        "zip": zip_code, "chain": params.get("chain", ""), "theatre_slug": slug,
        "tid": params.get("tid", ""), "mid": params.get("mid", ""),
        "sdate": params.get("sdate", ""),
        "total_seats": total, "reserved_seats": reserved,
        "available_seats": seats.get("available", 0), "occupancy_pct": occ,
        "row_count": (span.count("-") and len(_expand(span))) or 0,
        "rows_span": span, "container_fits": fits,
        "complete": assess_completeness(total, seats.get("rowFirst", ""), fits) if status == "ok" else False,
        "status": status,
    }


def _expand(span):
    a, _, b = span.partition("-")
    if len(a) == 1 and len(b) == 1:
        return [chr(c) for c in range(ord(a), ord(b) + 1)]
    return [a]


def _write(rows):
    DATA_DIR.mkdir(exist_ok=True)
    with open(PROBE_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PROBE_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {len(rows)} probe rows -> {PROBE_CSV}")


def _verdict(rows, blocks, renders, n_theatres):
    ok = [r for r in rows if r["status"] == "ok"]
    complete = [r for r in ok if r["complete"]]
    chains = sorted({r["chain"] for r in ok})
    print("\n=== PHASE A VERDICT ===")
    print(f"  A1 discovery : {n_theatres} theatres, {renders} seat renders, chains={chains}")
    print(f"  A2 complete  : {len(complete)}/{len(ok)} seat pages render a full auditorium "
          f"(non-virtualized) {'PASS' if ok and len(complete)==len(ok) else 'CHECK'}")
    if ok:
        szs = sorted(r["total_seats"] for r in ok)
        print(f"               house sizes: min={szs[0]} max={szs[-1]} (n={len(ok)})")
    print(f"  A3 anti-bot  : {blocks} blocks / {renders} renders "
          f"({(blocks/renders*100 if renders else 0):.0f}%) — full stress needs a GH-hosted run")


def _selftest():
    html = ('x /regal-uptown-aaqzk/theater-page y /cinemark-lancaster-movies-14-aacbs/theater-page '
            'z /amc-northpark-15-aande/theater-page /landmark-inwood-theatre-aaddm/theater-page')
    links = theater_page_links(html)
    assert ("regal-uptown-aaqzk", "REGL") in links, links
    assert ("cinemark-lancaster-movies-14-aacbs", "CNMK") in links, links
    assert all(c in WANTED_CHAINS for _, c in links), links  # AMC + landmark excluded
    p = seat_url_params("https://tickets.fandango.com/mobileexpress/seatselection"
                        "?row_count=552181552&mid=244348&chainCode=CNMK&sdate=2026-06-22+19%3A55"
                        "&tid=AACBS&route=map-seat-map")
    assert p == {"chain": "CNMK", "tid": "AACBS", "mid": "244348",
                 "sdate": "2026-06-22 19:55", "is_seat_page": True}, p
    assert is_wanted_chain("CNMK") and not is_wanted_chain("AMC")
    assert assess_completeness(98, "A", True) and not assess_completeness(98, "A", False)
    assert not assess_completeness(98, "C", True)   # rows must start at A (no gap)
    print("selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        probe(DEFAULT_ZIPS)
