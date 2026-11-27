#!/usr/bin/env python3
"""Fetch published trade forecasts (Box Office Theory) into data/trade-forecasts.csv.

Why: a 2026-11-27 study of 59 openings found the published Wednesday forecast
misses the 3-day opening by ~21% as of Thursday afternoon, against ~34% for our
own pre-sales call, and it is the best fallback when a film has no Polymarket
market. The file is an INPUT to scripts/ensemble_forecast.py, never to
predict.py's seat model.

Source: the site's public WordPress REST feed (no login, no key). Two post
kinds are parsed:
  * weekend forecast (Wednesday): one row per film, 3-day forecast, optional
    holiday frame column (4-/5-day), "NEW" marks an opener; plus the opener
    range text ("BOT Domestic Opening Weekend Forecast Range: $40 — 50 million").
  * tracking (Friday): release date, low / high / pinpoint for the next weeks.

Append-only; a row is identified by (post_id, kind, film). Every row keeps the
post's publish time so a consumer can enforce "published before the cutoff".
Exit code is always 0: a missing forecast must never fail the finalize job.
"""
import csv
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(HERE), "data")
OUT_CSV = os.path.join(DATA_DIR, "trade-forecasts.csv")
API = "https://boxofficetheory.com/wp-json/wp/v2/posts"
USER_AGENT = "box-office-tracker/1.0"
FIELDS = [
    "fetched_at", "source", "post_id", "published_gmt", "modified_gmt", "url",
    "kind", "film", "release_date", "is_opener", "three_day_m", "multi_day_m",
    "multi_day_frame", "low_m", "high_m", "point_m", "locations",
]


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _text(cell):
    return html.unescape(re.sub(r"<[^>]+>", " ", cell or "")).replace("\xa0", " ").strip()


def money_m(value):
    """'$83,700,000' -> 83.7 ; '$750K' -> 0.75 ; '' / words -> None. First number wins."""
    if not value:
        return None
    m = re.search(r"\$?\s*([\d][\d,]*(?:\.\d+)?)\s*([KkMm](?:illion)?)?", value)
    if not m:
        return None
    try:
        num = float(m.group(1).replace(",", ""))
    except ValueError:
        return None
    unit = (m.group(2) or "").lower()
    if unit.startswith("k"):
        return round(num / 1000.0, 4)
    if unit.startswith("m"):
        return round(num, 4)
    if num >= 10000:          # a full dollar figure
        return round(num / 1e6, 4)
    return None               # a bare small number is not a gross


def clean_title(title):
    t = _text(title)
    t = re.sub(r"^(Disney|Pixar|Marvel|DreamWorks|Illumination)[’']s\s+", "", t)
    return t.strip()


def parse_tables(content):
    """Yield {header: text} dicts for every data row of every mtr table."""
    for row in re.findall(r"<tr.*?</tr>", content, flags=re.S):
        cells = re.findall(r'data-mtr-content="([^"]*)"[^>]*>(.*?)</td>', row, flags=re.S)
        if not cells:
            continue
        rec = {re.sub(r"\s+", " ", html.unescape(h)).strip(): _text(v) for h, v in cells}
        if any(k == v for k, v in rec.items()):      # header row repeats its own labels
            continue
        yield rec


def _col(rec, *needles):
    for key, value in rec.items():
        low = key.lower()
        if all(n in low for n in needles):
            return key, value
    return None, None


def rows_from_post(post):
    content = (post.get("content") or {}).get("rendered") or ""
    base = {
        "source": "boxofficetheory",
        "post_id": str(post.get("id") or ""),
        "published_gmt": post.get("date_gmt") or "",
        "modified_gmt": post.get("modified_gmt") or "",
        "url": post.get("link") or "",
    }
    out = []
    for rec in parse_tables(content):
        _, pin = _col(rec, "pinpoint", "3-day")
        if pin is not None or _col(rec, "low-end", "3-day")[0]:
            film = clean_title(rec.get("Title") or "")
            if not film:
                continue
            _, low = _col(rec, "3-day", "low-end")
            _, high = _col(rec, "3-day", "high-end")
            low_m, high_m, point_m = money_m(low), money_m(high), money_m(pin)
            if low_m is None and high_m is None and point_m is None:
                continue
            release = ""
            try:
                release = datetime.strptime((rec.get("Release Date") or "").strip(), "%m/%d/%Y").strftime("%Y-%m-%d")
            except ValueError:
                pass
            out.append(dict(base, kind="tracking", film=film, release_date=release, is_opener="1",
                            three_day_m="", multi_day_m="", multi_day_frame="",
                            low_m=low_m if low_m is not None else "",
                            high_m=high_m if high_m is not None else "",
                            point_m=point_m if point_m is not None else "", locations=""))
            continue
        film = clean_title(rec.get("Film") or "")
        key3, v3 = _col(rec, "3-day", "forecast")
        if not film or key3 is None:
            continue
        three = money_m(v3)
        multi, frame = None, ""
        for key, value in rec.items():
            m = re.match(r"\s*([45])-day", key, flags=re.I)
            if m and "forecast" in key.lower():
                multi, frame = money_m(value), f"{m.group(1)}-day"
        if three is None and multi is None:
            continue
        _, change = _col(rec, "change")
        _, loc = _col(rec, "location")
        out.append(dict(base, kind="weekend", film=film, release_date="",
                        is_opener="1" if (change or "").strip().upper() == "NEW" else "0",
                        three_day_m=three if three is not None else "",
                        multi_day_m=multi if multi is not None else "", multi_day_frame=frame,
                        low_m="", high_m="", point_m="",
                        locations=re.sub(r"[^\d]", "", loc or "")))
    out.extend(range_rows(content, base))
    return out


RANGE_PATTERN = re.compile(
    r"\|\s*([^|]{2,90}?)\s*\|[\s|]*\(([^)|]{2,40})\)[\s|]*BOT Domestic (?:Opening )?Weekend Forecast Range:"
    r"\s*\$?([\d.]+)\s*([KkMm])?\s*(?:[—–-]\s*\$?([\d.]+))?\s*(million|[KkMm])?\+?\s*(?:\(\s*(\d)-day[^)]*\))?",
    flags=re.I)


def range_rows(content, base):
    """Opener range text ("<Film> (<Distributor>) BOT Domestic Opening Weekend
    Forecast Range: $40 — 50 million (5-day)") — present even in the weeks whose
    table is a chart image, and in the Substack copy of every weekend post."""
    out = []
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " | ", content or "")))
    for m in RANGE_PATTERN.finditer(text):
        film = clean_title(m.group(1))
        unit_hi = (m.group(6) or "").lower()
        scale_hi = 0.001 if unit_hi.startswith("k") else 1.0
        unit_lo = (m.group(4) or "").lower()
        scale_lo = 0.001 if unit_lo.startswith("k") else (1.0 if unit_lo.startswith("m") else scale_hi)
        try:
            low = float(m.group(3)) * scale_lo
            high = float(m.group(5)) * scale_hi if m.group(5) else None
        except ValueError:
            continue
        frame = f"{m.group(7)}-day" if m.group(7) else ""
        out.append(dict(base, kind="range", film=film, release_date="", is_opener="1",
                        three_day_m="", multi_day_m="", multi_day_frame=frame,
                        low_m=round(low, 4), high_m=round(high, 4) if high is not None else "",
                        point_m="", locations=""))
    return out


SUBSTACK = "https://boxofficetheory.substack.com/api/v1"


def fetch_substack_rows(limit=12):
    """The newsletter copy of the recent free posts — the fallback for weeks the
    site copy carries its numbers only as an image. Range text only."""
    listing = _get(f"{SUBSTACK}/archive?sort=new&limit={int(limit)}")
    posts = listing.get("posts") if isinstance(listing, dict) else listing
    rows = []
    for meta in posts or []:
        if (meta.get("audience") or "") != "everyone" or not meta.get("slug"):
            continue
        try:
            post = _get(f"{SUBSTACK}/posts/{urllib.parse.quote(meta['slug'])}")
        except Exception:
            continue
        published = (post.get("post_date") or "")[:19]
        base = {"source": "boxofficetheory-substack", "post_id": f"s{post.get('id')}",
                "published_gmt": published, "modified_gmt": "",
                "url": post.get("canonical_url") or ""}
        rows.extend(range_rows(post.get("body_html") or "", base))
    return rows


def fetch_posts(days=21, per_page=50, max_pages=20):
    """Every post of the last `days` days (paged; the feed caps a page at 100)."""
    after = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    posts = []
    for page in range(1, max_pages + 1):
        query = urllib.parse.urlencode({
            "per_page": per_page, "page": page, "after": after,
            "_fields": "id,date_gmt,modified_gmt,link,title,content",
        })
        try:
            batch = _get(f"{API}?{query}")
        except Exception:
            if page == 1:
                raise
            break                      # past the last page the feed answers 400
        if not isinstance(batch, list) or not batch:
            break
        posts.extend(batch)
        if len(batch) < per_page:
            break
    return posts


def load_existing(path=OUT_CSV):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def merge(existing, new_rows, fetched_at):
    seen = {(r.get("post_id"), r.get("kind"), r.get("film")) for r in existing}
    added = 0
    for row in new_rows:
        key = (row["post_id"], row["kind"], row["film"])
        if key in seen:
            continue
        seen.add(key)
        existing.append(dict(row, fetched_at=fetched_at))
        added += 1
    return added


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    days = 21
    if "--days" in argv:
        days = int(argv[argv.index("--days") + 1])
    try:
        posts = fetch_posts(days=days)
    except Exception as exc:                       # network / format: never fail the job
        print(f"⚠️  trade forecasts: fetch failed ({type(exc).__name__}: {exc}); file unchanged")
        return 0
    rows = []
    for post in posts if isinstance(posts, list) else []:
        try:
            rows.extend(rows_from_post(post))
        except Exception as exc:                   # one odd post must not drop the rest
            print(f"⚠️  trade forecasts: post {post.get('id')} unparsed ({type(exc).__name__})")
    try:
        rows.extend(fetch_substack_rows())
    except Exception as exc:
        print(f"⚠️  trade forecasts: newsletter copy unavailable ({type(exc).__name__}); site copy only")
    existing = load_existing()
    added = merge(existing, rows, datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    if added:
        existing.sort(key=lambda r: (r.get("published_gmt") or "", r.get("kind") or "", r.get("film") or ""))
        with open(OUT_CSV, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(existing)
    print(f"trade forecasts: {len(posts) if isinstance(posts, list) else 0} posts, "
          f"{len(rows)} rows parsed, {added} new → {os.path.relpath(OUT_CSV)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
