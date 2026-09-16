#!/usr/bin/env python3
"""Can THIS runner reach the residential proxy? Run before the AMC lock.

2026-09-15/16: on roughly half of GitHub runners every request through the
proxy hung from the very first one, while other runners in the same run used
it fine. Such a leg used to take the lock, time out 40 fetches, fall back to
(Cloudflare-walled) direct egress and die 6-10 minutes later with 0 rows.
Failing here instead costs seconds, holds no lock, and lets the scheduler's
retry land the leg on a fresh runner.

Exit 0: proxy answered (any HTTP status), or no proxy configured.
Exit 1: none of the attempts got a response. Prints exception classes only,
never the proxy URL, credentials or response bodies.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

URL = "https://www.amctheatres.com/robots.txt"
ATTEMPTS = 3
TIMEOUT_SEC = 15


def verdict(outcomes) -> bool:
    """Pure: reachable iff at least one attempt produced a response."""
    return any(o == "response" for o in outcomes)


def main() -> int:
    proxy = (os.environ.get("AMC_SEAT_PROXY_URL") or "").strip()
    if not proxy:
        print("proxy preflight: no proxy configured — direct egress, nothing to check")
        return 0
    import seat_fetch_http as sfh
    sess = sfh.make_session()
    outcomes = []
    for i in range(ATTEMPTS):
        t0 = time.monotonic()
        try:
            r = sess.get(URL, proxies={"http": proxy, "https": proxy}, timeout=TIMEOUT_SEC,
                         headers={"Accept": "text/plain,*/*"})
            print(f"proxy preflight {i + 1}/{ATTEMPTS}: status={r.status_code} "
                  f"{time.monotonic() - t0:.1f}s", flush=True)
            outcomes.append("response")
            break
        except Exception as e:
            print(f"proxy preflight {i + 1}/{ATTEMPTS}: {type(e).__name__} after "
                  f"{time.monotonic() - t0:.1f}s", flush=True)
            outcomes.append("error")
    if verdict(outcomes):
        return 0
    print(f"::error::residential proxy unreachable from this runner ({ATTEMPTS} attempts, "
          f"no response) — failing before the AMC lock so the retry lands on a fresh runner",
          flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
