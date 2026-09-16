"""Plain curl vs our curl_cffi client through the proxy, SAME runner, interleaved.
Decides whether a tunnel stall is the gateway's or the client's. Prints status
and timing only; the proxy URL and credential are never printed."""
import os, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

proxy = (os.environ.get("AMC_SEAT_PROXY_URL") or "").strip()
if not proxy:
    print("no proxy configured"); raise SystemExit(0)
TARGET = "https://ipinfo.io/ip"
region = subprocess.run(["bash", "-c", "curl -s -m 8 https://ipinfo.io/ip"], capture_output=True, text=True).stdout.strip()
print(f"runner egress ip: {region or '?'}", flush=True)


def plain_curl(tag):
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-m", "20", "-x", proxy,
                        "-w", "%{http_code} %{time_total}", TARGET], capture_output=True, text=True)
    out = (r.stdout or "").split()
    code = out[0] if out else "000"
    secs = out[1] if len(out) > 1 else "?"
    print(f"{tag} plain curl        : HTTP {code} total={secs}s (exit {r.returncode})", flush=True)


def cffi(tag, impersonate):
    from curl_cffi import requests as cr
    from curl_cffi.const import CurlOpt
    t0 = time.monotonic()
    try:
        sess = cr.Session(impersonate=impersonate, curl_options={CurlOpt.HTTP_CONTENT_DECODING: 0}) \
            if impersonate else cr.Session()
        r = sess.get(TARGET, proxies={"http": proxy, "https": proxy}, timeout=20)
        print(f"{tag} curl_cffi {str(impersonate or 'plain'):7s}: HTTP {r.status_code} "
              f"total={time.monotonic() - t0:.2f}s", flush=True)
    except Exception as e:
        print(f"{tag} curl_cffi {str(impersonate or 'plain'):7s}: {type(e).__name__} after "
              f"{time.monotonic() - t0:.1f}s", flush=True)


for i in (1, 2, 3):
    plain_curl(f"round {i}")
    cffi(f"round {i}", "chrome")
    cffi(f"round {i}", None)
