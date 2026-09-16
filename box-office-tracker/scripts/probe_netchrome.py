"""Which Chromium launch flags get a page through the proxy from THIS runner?
Chrome's post-quantum key share hangs the proxy's tunnels from Azure
East/Central US (see seat_fetch_http.TLS_CURVES). Tries flag variants, prints
outcome and timing only; the proxy URL and credential are never printed."""
import os, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scraper  # noqa: E402  (parses the proxy the way the lanes do)
from playwright.sync_api import sync_playwright  # noqa: E402

proxy = scraper._SEAT_PROXY
if not proxy:
    print("no proxy configured"); raise SystemExit(0)
print("runner egress ip:", subprocess.run(["curl", "-s", "-m", "8", "https://ipinfo.io/ip"],
                                          capture_output=True, text=True).stdout.strip() or "?", flush=True)
BASE = list(scraper._CHROMIUM_ARGS)
VARIANTS = [
    ("default flags              ", []),
    ("--disable-features=UseMLKEM,PostQuantumKyber", ["--disable-features=UseMLKEM,PostQuantumKyber"]),
    ("--disable-features=PostQuantumKeyAgreement  ", ["--disable-features=PostQuantumKeyAgreement"]),
]
with sync_playwright() as p:
    for rnd in (1, 2):
        for tag, extra in VARIANTS:
            t0 = time.monotonic()
            try:
                b = p.chromium.launch(headless=True, args=BASE + extra, proxy=proxy)
                pg = b.new_page()
                r = pg.goto("https://ipinfo.io/ip", wait_until="domcontentloaded", timeout=20000)
                print(f"round {rnd} {tag}: HTTP {r.status if r else '?'} total={time.monotonic()-t0:.2f}s", flush=True)
                b.close()
            except Exception as e:
                print(f"round {rnd} {tag}: {type(e).__name__} after {time.monotonic()-t0:.1f}s", flush=True)
                try: b.close()
                except Exception: pass
