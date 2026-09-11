"""Read-only probe (no AMC lock): fetch N seat pages through the residential
proxy via the RSC data endpoint and the HTML path, print sizes + the
seatingLayout schema. Used to design a JSON seat reader that reads a
fraction of the page. Prints no credentials."""
import json, os, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seat_fetch_http as sfh  # noqa: E402

N = int(os.environ.get("PROBE_N", "2"))
proxy = os.environ.get("AMC_SEAT_PROXY_URL", "").strip() or None
links = (Path(__file__).resolve().parents[1] / "data" / "showtime-links.json").read_text()
ids = re.findall(r'"showtime_id":\s*"(\d+)"', links)
picks = ids[len(ids) // 3::max(1, len(ids) // (3 * N))][:N]
sess = sfh.make_session()
for sid in picks:
    url = f"https://www.amctheatres.com/showtimes/{sid}/seats"
    try:
        rsc = sfh.probe_rsc_endpoint(url, proxy, session=sess)
        for k in ("layout_snippet", "seat_snippet"):
            rsc[k] = (rsc.get(k) or "")[:1200]
        print(f"RSC {sid}: " + json.dumps(rsc)[:3000], flush=True)
    except Exception as e:
        print(f"RSC {sid}: ERROR {type(e).__name__}: {str(e)[:120]}", flush=True)
    try:
        page = sfh.fetch_seat_page(url, proxy, session=sess)
        print(f"HTML {sid}: raw={page['raw_bytes']} decoded={page.get('decoded_bytes')} kind={page['kind']} "
              f"parse={sfh.parse_seat_counts(page['html'])} first_seat@{page.get('first_seat_input')} "
              f"last_seat@{page.get('last_seat_input')} markers={page.get('markers')}", flush=True)
    except Exception as e:
        print(f"HTML {sid}: ERROR {type(e).__name__}: {str(e)[:120]}", flush=True)
