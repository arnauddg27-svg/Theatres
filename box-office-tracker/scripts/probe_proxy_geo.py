"""Read-only: what country do the residential proxy's exits land in?
Fandango geo-blocks non-US traffic, so a US-targeted endpoint matters for the
Regal lane (AMC does not geo-block, which is why this went unnoticed).
Prints countries only — never the proxy URL or credentials."""
import os, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
N = max(1, min(20, int(os.environ.get("PROBE_N", "8") or 8)))
sess = sfh.make_session()
seen = collections.Counter()
for i in range(N):
    kw = {"timeout": 20, "headers": {"Accept": "application/json"}}
    if proxy:
        kw["proxies"] = {"http": proxy, "https": proxy}
    try:
        r = sess.get("https://ipinfo.io/json", **kw)
        d = r.json()
        cc = d.get("country", "?")
        seen[cc] += 1
        print(f"draw {i+1}: country={cc} region={d.get('region','?')}", flush=True)
    except Exception as e:
        seen["ERR"] += 1
        print(f"draw {i+1}: ERROR {type(e).__name__}", flush=True)
print(f"SUMMARY: {dict(seen)} — US share {seen.get('US',0)}/{sum(seen.values())}", flush=True)
