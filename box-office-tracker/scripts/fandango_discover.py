#!/usr/bin/env python3
"""Expand theatres-fandango.json toward Regal's full ~420-theatre US footprint.

The June pool (188 REGL) had two gaps this discovery closes:
  1. Chain detection matched only `regal-` slugs — Regal's EDWARDS and
     UNITED ARTISTS brands were silently skipped.
  2. The zip list covered ~90 metros; this one is a ~350-zip national grid.

Method (proven June 2026): GET https://www.fandango.com/{zip}_movietimes —
the SSR page lists nearby theatres as /{slug}/theater-page links. requests
first; Playwright fallback per zip if the plain fetch is blocked. Runs on a
US runner (Fandango geo-blocks elsewhere). ADD-ONLY merge: existing entries
are preserved verbatim (their curated tz/city stand); the script aborts
rather than ever shrinking the pool. Output is written to the report dir as
an artifact for review + local commit — this script never touches git.

Bigger pool does NOT raise render pressure: renders per slot stay capped;
more theatres just broadens the shuffled rotation across nights.
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPORT_DIR = os.environ.get("PROBE_REPORT_DIR", "../chain-probe")
POOL = Path(__file__).resolve().parents[1] / "data" / "theatres-fandango.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

STATE_TZ = {
    "CT": "America/New_York", "DE": "America/New_York", "FL": "America/New_York",
    "GA": "America/New_York", "MA": "America/New_York", "MD": "America/New_York",
    "ME": "America/New_York", "MI": "America/New_York", "NC": "America/New_York",
    "NH": "America/New_York", "NJ": "America/New_York", "NY": "America/New_York",
    "OH": "America/New_York", "PA": "America/New_York", "RI": "America/New_York",
    "SC": "America/New_York", "VA": "America/New_York", "VT": "America/New_York",
    "WV": "America/New_York", "IN": "America/New_York", "KY": "America/New_York",
    "DC": "America/New_York",
    "AL": "America/Chicago", "AR": "America/Chicago", "IA": "America/Chicago",
    "IL": "America/Chicago", "KS": "America/Chicago", "LA": "America/Chicago",
    "MN": "America/Chicago", "MO": "America/Chicago", "MS": "America/Chicago",
    "ND": "America/Chicago", "NE": "America/Chicago", "OK": "America/Chicago",
    "SD": "America/Chicago", "TN": "America/Chicago", "TX": "America/Chicago",
    "WI": "America/Chicago",
    "AZ": "America/Phoenix", "CO": "America/Denver", "ID": "America/Denver",
    "MT": "America/Denver", "NM": "America/Denver", "UT": "America/Denver",
    "WY": "America/Denver",
    "CA": "America/Los_Angeles", "NV": "America/Los_Angeles",
    "OR": "America/Los_Angeles", "WA": "America/Los_Angeles",
    "AK": "America/Anchorage", "HI": "Pacific/Honolulu",
}

# (zip, "City, ST") — national grid: every state's major metros plus secondary
# cities, weighted toward Regal/Edwards/UA territory (NE corridor, FL, CA, TX,
# PNW, mountain states). ~350 probes; the movietimes page covers a 10-25 mile
# radius, so adjacent grid points overlap deliberately.
ZIP_GRID = [
    # Northeast
    ("10001", "New York, NY"), ("10314", "Staten Island, NY"), ("11201", "Brooklyn, NY"),
    ("11375", "Queens, NY"), ("10467", "Bronx, NY"), ("11550", "Hempstead, NY"),
    ("11746", "Huntington, NY"), ("11901", "Riverhead, NY"), ("10601", "White Plains, NY"),
    ("12207", "Albany, NY"), ("13202", "Syracuse, NY"), ("14604", "Rochester, NY"),
    ("14202", "Buffalo, NY"), ("13501", "Utica, NY"), ("12601", "Poughkeepsie, NY"),
    ("07102", "Newark, NJ"), ("07030", "Hoboken, NJ"), ("07601", "Hackensack, NJ"),
    ("08540", "Princeton, NJ"), ("08701", "Lakewood, NJ"), ("08052", "Cherry Hill, NJ"),
    ("07728", "Freehold, NJ"), ("08234", "Atlantic City, NJ"), ("07960", "Morristown, NJ"),
    ("06103", "Hartford, CT"), ("06510", "New Haven, CT"), ("06604", "Bridgeport, CT"),
    ("06901", "Stamford, CT"), ("06360", "Norwich, CT"), ("06790", "Torrington, CT"),
    ("02108", "Boston, MA"), ("02138", "Cambridge, MA"), ("01608", "Worcester, MA"),
    ("01103", "Springfield, MA"), ("02740", "New Bedford, MA"), ("01960", "Peabody, MA"),
    ("02184", "Braintree, MA"), ("02601", "Hyannis, MA"),
    ("02903", "Providence, RI"), ("02886", "Warwick, RI"),
    ("03101", "Manchester, NH"), ("03060", "Nashua, NH"), ("03801", "Portsmouth, NH"),
    ("04101", "Portland, ME"), ("04401", "Bangor, ME"),
    ("05401", "Burlington, VT"),
    # Mid-Atlantic
    ("19103", "Philadelphia, PA"), ("19401", "Norristown, PA"), ("19013", "Chester, PA"),
    ("18101", "Allentown, PA"), ("18503", "Scranton, PA"), ("17101", "Harrisburg, PA"),
    ("17601", "Lancaster, PA"), ("15222", "Pittsburgh, PA"), ("16501", "Erie, PA"),
    ("16801", "State College, PA"), ("19610", "Reading, PA"),
    ("19801", "Wilmington, DE"), ("19901", "Dover, DE"),
    ("21201", "Baltimore, MD"), ("20850", "Rockville, MD"), ("21401", "Annapolis, MD"),
    ("21740", "Hagerstown, MD"), ("20601", "Waldorf, MD"), ("21801", "Salisbury, MD"),
    ("20001", "Washington, DC"),
    ("22314", "Alexandria, VA"), ("22030", "Fairfax, VA"), ("23219", "Richmond, VA"),
    ("23510", "Norfolk, VA"), ("23451", "Virginia Beach, VA"), ("24016", "Roanoke, VA"),
    ("22901", "Charlottesville, VA"), ("22401", "Fredericksburg, VA"),
    ("25301", "Charleston, WV"), ("26501", "Morgantown, WV"),
    # Southeast
    ("28202", "Charlotte, NC"), ("27601", "Raleigh, NC"), ("27401", "Greensboro, NC"),
    ("28801", "Asheville, NC"), ("28401", "Wilmington, NC"), ("27858", "Greenville, NC"),
    ("29201", "Columbia, SC"), ("29401", "Charleston, SC"), ("29601", "Greenville, SC"),
    ("29577", "Myrtle Beach, SC"),
    ("30303", "Atlanta, GA"), ("30060", "Marietta, GA"), ("31401", "Savannah, GA"),
    ("31901", "Columbus, GA"), ("30901", "Augusta, GA"), ("31201", "Macon, GA"),
    ("32202", "Jacksonville, FL"), ("32801", "Orlando, FL"), ("33602", "Tampa, FL"),
    ("33701", "St Petersburg, FL"), ("33131", "Miami, FL"), ("33301", "Fort Lauderdale, FL"),
    ("33401", "West Palm Beach, FL"), ("34236", "Sarasota, FL"), ("33901", "Fort Myers, FL"),
    ("34102", "Naples, FL"), ("32501", "Pensacola, FL"), ("32301", "Tallahassee, FL"),
    ("32601", "Gainesville, FL"), ("32114", "Daytona Beach, FL"), ("34741", "Kissimmee, FL"),
    ("33952", "Port Charlotte, FL"), ("32960", "Vero Beach, FL"), ("34952", "Port St Lucie, FL"),
    ("33020", "Hollywood, FL"), ("33544", "Wesley Chapel, FL"), ("32174", "Ormond Beach, FL"),
    ("35203", "Birmingham, AL"), ("36104", "Montgomery, AL"), ("36602", "Mobile, AL"),
    ("35801", "Huntsville, AL"),
    ("39201", "Jackson, MS"), ("39530", "Biloxi, MS"),
    ("37203", "Nashville, TN"), ("37902", "Knoxville, TN"), ("38103", "Memphis, TN"),
    ("37402", "Chattanooga, TN"), ("37601", "Johnson City, TN"),
    ("40202", "Louisville, KY"), ("40507", "Lexington, KY"), ("42101", "Bowling Green, KY"),
    # Midwest
    ("60601", "Chicago, IL"), ("60563", "Naperville, IL"), ("60173", "Schaumburg, IL"),
    ("61602", "Peoria, IL"), ("62701", "Springfield, IL"), ("61820", "Champaign, IL"),
    ("61101", "Rockford, IL"),
    ("46204", "Indianapolis, IN"), ("46802", "Fort Wayne, IN"), ("47708", "Evansville, IN"),
    ("46601", "South Bend, IN"),
    ("43215", "Columbus, OH"), ("45202", "Cincinnati, OH"), ("44113", "Cleveland, OH"),
    ("43604", "Toledo, OH"), ("45402", "Dayton, OH"), ("44308", "Akron, OH"),
    ("44503", "Youngstown, OH"),
    ("48226", "Detroit, MI"), ("48104", "Ann Arbor, MI"), ("49503", "Grand Rapids, MI"),
    ("48601", "Saginaw, MI"), ("49001", "Kalamazoo, MI"), ("48912", "Lansing, MI"),
    ("53202", "Milwaukee, WI"), ("53703", "Madison, WI"), ("54301", "Green Bay, WI"),
    ("55401", "Minneapolis, MN"), ("55101", "St Paul, MN"), ("55901", "Rochester, MN"),
    ("55802", "Duluth, MN"),
    ("50309", "Des Moines, IA"), ("52401", "Cedar Rapids, IA"), ("52240", "Iowa City, IA"),
    ("63101", "St Louis, MO"), ("64106", "Kansas City, MO"), ("65806", "Springfield, MO"),
    ("65201", "Columbia, MO"),
    ("66603", "Topeka, KS"), ("67202", "Wichita, KS"), ("66210", "Overland Park, KS"),
    ("68102", "Omaha, NE"), ("68508", "Lincoln, NE"),
    ("57104", "Sioux Falls, SD"), ("58102", "Fargo, ND"),
    # South Central
    ("73102", "Oklahoma City, OK"), ("74103", "Tulsa, OK"),
    ("72201", "Little Rock, AR"), ("72701", "Fayetteville, AR"),
    ("70112", "New Orleans, LA"), ("70801", "Baton Rouge, LA"), ("71101", "Shreveport, LA"),
    ("70501", "Lafayette, LA"),
    ("75201", "Dallas, TX"), ("76102", "Fort Worth, TX"), ("77002", "Houston, TX"),
    ("78205", "San Antonio, TX"), ("78701", "Austin, TX"), ("79901", "El Paso, TX"),
    ("79401", "Lubbock, TX"), ("76701", "Waco, TX"), ("78401", "Corpus Christi, TX"),
    ("78501", "McAllen, TX"), ("77550", "Galveston, TX"), ("75701", "Tyler, TX"),
    ("79101", "Amarillo, TX"), ("76901", "San Angelo, TX"), ("77840", "College Station, TX"),
    # Mountain
    ("80202", "Denver, CO"), ("80903", "Colorado Springs, CO"), ("80521", "Fort Collins, CO"),
    ("81501", "Grand Junction, CO"), ("80301", "Boulder, CO"),
    ("84101", "Salt Lake City, UT"), ("84604", "Provo, UT"), ("84401", "Ogden, UT"),
    ("84770", "St George, UT"),
    ("85003", "Phoenix, AZ"), ("85701", "Tucson, AZ"), ("86301", "Prescott, AZ"),
    ("86001", "Flagstaff, AZ"), ("85201", "Mesa, AZ"),
    ("87102", "Albuquerque, NM"), ("87501", "Santa Fe, NM"), ("88001", "Las Cruces, NM"),
    ("59101", "Billings, MT"), ("59718", "Bozeman, MT"), ("59801", "Missoula, MT"),
    ("83702", "Boise, ID"), ("83201", "Pocatello, ID"), ("83814", "Coeur d'Alene, ID"),
    ("82001", "Cheyenne, WY"), ("82601", "Casper, WY"),
    # West
    ("89101", "Las Vegas, NV"), ("89501", "Reno, NV"), ("89701", "Carson City, NV"),
    ("90012", "Los Angeles, CA"), ("90802", "Long Beach, CA"), ("91101", "Pasadena, CA"),
    ("91367", "Woodland Hills, CA"), ("91730", "Rancho Cucamonga, CA"),
    ("92501", "Riverside, CA"), ("92401", "San Bernardino, CA"), ("92626", "Costa Mesa, CA"),
    ("92618", "Irvine, CA"), ("92101", "San Diego, CA"), ("92024", "Encinitas, CA"),
    ("92860", "Norco, CA"), ("93003", "Ventura, CA"), ("93101", "Santa Barbara, CA"),
    ("93301", "Bakersfield, CA"), ("93710", "Fresno, CA"), ("95202", "Stockton, CA"),
    ("95814", "Sacramento, CA"), ("95678", "Roseville, CA"), ("94102", "San Francisco, CA"),
    ("94612", "Oakland, CA"), ("94538", "Fremont, CA"), ("95112", "San Jose, CA"),
    ("94010", "Burlingame, CA"), ("94903", "San Rafael, CA"), ("95401", "Santa Rosa, CA"),
    ("95003", "Aptos, CA"), ("93940", "Monterey, CA"), ("96001", "Redding, CA"),
    ("95926", "Chico, CA"), ("95531", "Crescent City, CA"), ("92243", "El Centro, CA"),
    ("92392", "Victorville, CA"), ("93534", "Lancaster, CA"), ("92028", "Fallbrook, CA"),
    ("97201", "Portland, OR"), ("97301", "Salem, OR"), ("97401", "Eugene, OR"),
    ("97701", "Bend, OR"), ("97501", "Medford, OR"), ("97330", "Corvallis, OR"),
    ("98101", "Seattle, WA"), ("98402", "Tacoma, WA"), ("98501", "Olympia, WA"),
    ("99201", "Spokane, WA"), ("98225", "Bellingham, WA"), ("98901", "Yakima, WA"),
    ("99301", "Pasco, WA"), ("98661", "Vancouver, WA"), ("98052", "Redmond, WA"),
    ("99501", "Anchorage, AK"), ("96813", "Honolulu, HI"),
]

# Widened chain detection: Regal operates under the Edwards and United
# Artists brands too — the June discovery matched only `regal-` and left
# them out of the pool entirely.
CHAIN_PREFIXES = (
    ("regal-", "REGL"), ("edwards-", "REGL"), ("united-artists-", "REGL"),
    ("ua-", "REGL"),
    ("cinemark-", "CNMK"), ("century-", "CNMK"), ("cinearts-", "CNMK"),
    ("tinseltown-", "CNMK"),
)


def chain_for_slug(slug):
    low = slug.lower()
    for prefix, chain in CHAIN_PREFIXES:
        if low.startswith(prefix):
            return chain
    return None


def parse_theatres(html):
    out = {}
    for slug in re.findall(r'/([a-z0-9\-]+)/theater-page', html or ""):
        chain = chain_for_slug(slug)
        if chain:
            out[slug] = chain
    return out


def name_from_slug(slug):
    # "{words}-{aaid}" — the trailing 4-6 char token is the theatre id.
    parts = slug.split("-")
    if len(parts) > 1 and 4 <= len(parts[-1]) <= 6:
        parts = parts[:-1]
    return " ".join(p.capitalize() for p in parts)


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)
    existing = json.load(open(POOL)) if POOL.exists() else {"theatres": []}
    known = {t["slug"]: t for t in existing.get("theatres", [])}
    print(f"existing pool: {len(known)} theatres", flush=True)

    import requests
    session = requests.Session()
    session.headers["User-Agent"] = UA

    browser = page = None
    use_browser = False
    found = {}   # slug -> entry
    stats = {"zips": 0, "http_ok": 0, "blocked": 0, "browser_ok": 0}

    def fetch(zipc):
        nonlocal use_browser, browser, page
        url = f"https://www.fandango.com/{zipc}_movietimes"
        if not use_browser:
            try:
                r = session.get(url, timeout=20)
                if r.status_code == 200 and "theater-page" in r.text:
                    stats["http_ok"] += 1
                    return r.text
                stats["blocked"] += 1
            except Exception:
                stats["blocked"] += 1
            # requests path failing consistently -> switch to browser for the rest
            if stats["blocked"] >= 3 and stats["http_ok"] == 0:
                use_browser = True
                print("  switching to Playwright fallback", flush=True)
        if use_browser:
            if page is None:
                from playwright.sync_api import sync_playwright
                pw = sync_playwright().start()
                browser = pw.chromium.launch(
                    args=["--disable-blink-features=AutomationControlled"])
                page = browser.new_context(user_agent=UA).new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1500)
                stats["browser_ok"] += 1
                return page.content()
            except Exception:
                return ""
        return ""

    for zipc, city in ZIP_GRID:
        stats["zips"] += 1
        html = fetch(zipc)
        if not html:
            continue
        state = city.rsplit(",", 1)[-1].strip()
        for slug, chain in parse_theatres(html).items():
            if slug in known or slug in found:
                continue
            found[slug] = {
                "name": name_from_slug(slug),
                "slug": slug,
                "chain": chain,
                "city": city,
                "dma": city,
                "timezone": STATE_TZ.get(state, "America/Chicago"),
                "zip": zipc,
                "discovered": "2026-08-31-expansion",
            }
        if stats["zips"] % 40 == 0:
            print(f"  {stats['zips']}/{len(ZIP_GRID)} zips, "
                  f"+{len(found)} new theatres so far", flush=True)
        time.sleep(0.8)

    if browser:
        browser.close()

    merged = list(known.values()) + sorted(found.values(), key=lambda t: t["slug"])
    assert len(merged) >= len(known), "pool must never shrink"
    out = dict(existing)
    out["theatres"] = merged
    out["_updated"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(REPORT_DIR, "theatres-fandango-expanded.json"), "w") as f:
        json.dump(out, f, indent=1)

    from collections import Counter
    by_chain_new = Counter(t["chain"] for t in found.values())
    by_chain_all = Counter(t["chain"] for t in merged)
    print(f"\nDISCOVERY: {stats} | new theatres: {dict(by_chain_new)} "
          f"| merged pool: {dict(by_chain_all)} ({len(merged)} total)", flush=True)
    print("report -> theatres-fandango-expanded.json (review + commit locally)",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
