"""Which TLS fingerprint gets a tunnel through the proxy from THIS runner, and
does it still read AMC past Cloudflare? Same runner, interleaved variants.
Status/timing/kind only; the proxy URL and credential are never printed.
2026-09-16: chrome impersonation hung from Azure East/Central US while plain
curl and non-impersonated curl_cffi passed, on the same runner."""
import csv, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import seat_fetch_http as sfh
from curl_cffi import requests as cr
from curl_cffi.const import CurlOpt

proxy = (os.environ.get("AMC_SEAT_PROXY_URL") or "").strip()
if not proxy:
    print("no proxy configured"); raise SystemExit(0)
print("runner egress ip:", subprocess.run(["curl", "-s", "-m", "8", "https://ipinfo.io/ip"],
                                          capture_output=True, text=True).stdout.strip() or "?", flush=True)
print("CurlOpt curve options:", [n for n in dir(CurlOpt) if "CURVE" in n.upper()], flush=True)
CURVES = getattr(CurlOpt, "SSL_EC_CURVES", None)
NO_PQ = "X25519:P-256:P-384"

seat_url = ""
with open(ROOT / "data" / "pre-reservation-snapshots.csv", newline="") as fh:
    for row in csv.DictReader(fh):
        u = row.get("amc_seat_map_url") or ""
        if u.startswith("https://www.amctheatres.com/showtimes/"):
            seat_url = u
VARIANTS = [
    ("chrome (as today)     ", dict(impersonate="chrome"), {}),
    ("chrome, no PQ curves  ", dict(impersonate="chrome"), {CURVES: NO_PQ} if CURVES else None),
    ("chrome120 (pre-Kyber) ", dict(impersonate="chrome120"), {}),
    ("no impersonation      ", dict(), {}),
]


def run(tag, kw, extra, url, classify):
    if extra is None:
        print(f"{tag}: SKIPPED (no curve option in this curl_cffi)", flush=True); return
    opts = {CurlOpt.HTTP_CONTENT_DECODING: 0}; opts.update(extra)
    t0 = time.monotonic()
    try:
        sess = cr.Session(curl_options=opts, **kw)
        r = sess.get(url, proxies={"http": proxy, "https": proxy}, timeout=20,
                     accept_encoding=sfh.ACCEPT_ENCODING, stream=True)
        body = b""
        for ch in r.iter_content(chunk_size=16384):
            body += ch
            if len(body) > 600_000: break
        extra_s = ""
        if classify:
            html = sfh._Inflater(r.headers.get("content-encoding", "")).feed(body).decode("utf-8", "ignore")
            kind = "seats" if "seatingLayout" in html or 'aria-label="Seat' in html or "Recliner" in html else \
                   ("blocked" if "Attention Required" in html else ("challenge" if "Just a moment" in html else "other"))
            extra_s = f" kind={kind} raw={len(body)//1024}KB"
        print(f"{tag}: HTTP {r.status_code} total={time.monotonic()-t0:.2f}s{extra_s}", flush=True)
    except Exception as e:
        print(f"{tag}: {type(e).__name__} after {time.monotonic()-t0:.1f}s", flush=True)


for rnd in (1, 2):
    for tag, kw, extra in VARIANTS:
        run(f"round {rnd} ipinfo  {tag}", kw, extra, "https://ipinfo.io/ip", False)
for tag, kw, extra in VARIANTS[1:]:
    run(f"AMC seat page   {tag}", kw, extra, seat_url, True)
