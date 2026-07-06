#!/usr/bin/env python3
"""Backfill REAL reported daily grosses from the-numbers.com into calibration.json.

Only ~4/18 calibration films had real reported daily splits; the rest were
seat-derived. the-numbers.com publishes the true daily table for every film, so
this replaces the derived splits with reported grosses and rebuilds the day-weight
calibration on real data.

Per film: construct the movie URL, parse 'Daily Box Office Performance', pull the
grosses for Thursday(weekend_of-1) .. Sunday(weekend_of+2). Flags a weekend as
day-weight-anomalous when Saturday < Friday (e.g. a July-4th Saturday crater).

  python3 scripts/import_thenumbers_daily.py --test "Minions & Monsters" 2026-07-03
  python3 scripts/import_thenumbers_daily.py --backfill [--dry-run]
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
DAYS = ("Thursday", "Friday", "Saturday", "Sunday")


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def slug_candidates(title, year):
    base = title.replace("&", "and")
    base = re.sub(r"[^A-Za-z0-9 ]", " ", base)      # drop :, ', etc.
    base = re.sub(r"\s+", "-", base.strip())
    return [f"https://www.the-numbers.com/movie/{base}-({year})",
            f"https://www.the-numbers.com/movie/{base}"]


def fetch_daily_table(title, year):
    """Return {date_obj: gross_m} from the Daily Box Office Performance table."""
    page = None
    for url in slug_candidates(title, year):
        try:
            page = _get(url)
            break
        except Exception:
            continue
    if not page:
        return None
    i = page.find("Daily Box Office Performance")
    if i < 0:
        return None
    tbl = re.search(r"<table.*?</table>", page[i:], re.S)   # ONLY the daily table
    if not tbl:
        return None
    seg = tbl.group(0)
    out = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", seg, re.S):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).replace("\xa0", " ").strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) < 3:
            continue
        try:
            d = datetime.strptime(cells[0].replace(" ,", ","), "%b %d, %Y")
        except ValueError:
            continue
        m = re.search(r"\$([\d,]+)", cells[2])
        if m:
            out[d.date()] = (cells[1].strip(), int(m.group(1).replace(",", "")) / 1e6)
    return out or None


def opening_days(daily, weekend_of):
    """Model convention: Thursday=preview, Friday=Friday EXCLUDING previews.

    the-numbers rolls Thursday previews into the reported opening-Friday gross
    (the Thursday row is ranked 'P' and is a SUBSET of Friday). So when Thursday
    is a preview, subtract it from Friday. For a Wednesday opener (Thursday is a
    ranked regular day, not 'P'), both stand alone.
    """
    fri = datetime.strptime(weekend_of, "%Y-%m-%d").date()
    wanted = {"Thursday": fri - timedelta(days=1), "Friday": fri,
              "Saturday": fri + timedelta(days=1), "Sunday": fri + timedelta(days=2)}
    od = {day: round(daily[dt][1], 2) for day, dt in wanted.items() if dt in daily}
    thu_dt = wanted["Thursday"]
    if (thu_dt in daily and daily[thu_dt][0] == "P"
            and "Thursday" in od and "Friday" in od):
        od["Friday"] = round(od["Friday"] - od["Thursday"], 2)
    return od


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", nargs=2, metavar=("TITLE", "WEEKEND"))
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.test:
        title, w = args.test
        daily = fetch_daily_table(title, int(w[:4]))
        if not daily:
            print("no daily table found")
            return
        od = opening_days(daily, w)
        print(f"{title} ({w}): {od}  sum(Thu-Sun)=${sum(od.values()):.2f}M")
        return

    cal_path = os.path.join(P.DATA_DIR, "calibration.json")
    cal = json.load(open(cal_path))
    updated = 0
    for e in cal["history"]:
        movie, w = e["movie"], e["weekend_of"]
        daily = fetch_daily_table(movie, int(w[:4]))
        time.sleep(0.4)
        od = daily and opening_days(daily, w)
        if not od or len(od) < 3:
            print(f"  {movie[:30]:30} {w}  MISS ({'no table' if not daily else 'few days'})")
            continue
        # A holiday crater (e.g. July 4th) inverts the weekend: Saturday, normally
        # the biggest day, falls BELOW Sunday. Normal frontloading (Sat<Fri but
        # Sat>Sun, e.g. horror/tentpoles) is a real day-shape and must stay in.
        anomalous = ("Saturday" in od and "Sunday" in od and od["Saturday"] < od["Sunday"])
        print(f"  {movie[:30]:30} {w}  {od}  sum=${sum(od.values()):.1f}M"
              f"{'  [Sat<Fri -> day-weight-excluded]' if anomalous else ''}")
        if not args.dry_run:
            e["daily_actuals"] = od
            e["daily_actuals_source"] = "the-numbers.com"
            if anomalous:
                e["exclude_from_day_weights"] = True
            updated += 1
    if not args.dry_run:
        json.dump(cal, open(cal_path, "w"), indent=2)
        print(f"\nupdated {updated} films with real daily grosses -> {cal_path}")


if __name__ == "__main__":
    main()
