#!/usr/bin/env python3
"""Measure the family/walk-up gap in the snapshot layer.

The snapshot layer turns pre-reservation seats into a day gross with an
'empirical' walk-up uplift that is GENRE-BLIND. Kids/family films sell mostly at
the door, so their pre-reservations are a small fraction of the final gross and
the uplift is far too small.

For each history film, replay as-of-Thursday (leak-free freeze) and record:
  raw   = pre_empirical_snapshot_mid_m   (reservations, pre-uplift)
  applied_uplift = snapshot_mid_m / raw  (what the model applied)
  required_uplift = actual_total / raw   (what would have been correct)
The ratio required/applied is how badly the snapshot under/over-reads. Grouped by
audience_type to see if `broad_family` needs a systematically bigger uplift.
Read-only.
"""
import csv
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    hist = json.load(open(os.path.join(P.DATA_DIR, "calibration.json")))["history"]
    md = P.load_movie_metadata()
    tags = {r["movie"]: (r.get("audience_type") or "").strip()
            for r in csv.DictReader(open(os.path.join(P.DATA_DIR, "movie-metadata.csv")))}
    rows = []
    for h in hist:
        movie, w, actual = h["movie"], h["weekend_of"], h["actual_total"]
        thu = (datetime.strptime(w, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            cal = P.load_calibration_freeze(P.DATA_DIR, w)
        except Exception:
            continue
        sd = P.movie_mapping_get(P.filter_seat_data_through(P.load_seat_data(weekend_of=w), thu), movie, None)
        if not sd:
            continue
        try:
            pred = P.predict_movie(
                movie, sd, [], cal,
                national_theatre_count=P.national_theatre_count_for_movie(movie, P.load_theatre_counts(), metadata=md),
                snapshot_data=P.movie_mapping_get(P.load_pre_reservation_data(weekend_of=w, through_date=thu), movie, {}))
        except Exception:
            continue
        if not pred:
            continue
        raw = _f(pred.get("pre_empirical_snapshot_mid_m"))
        post = _f(pred.get("snapshot_mid_m"))
        if not raw or raw <= 0 or not post:
            continue
        rows.append((movie, tags.get(movie, ""), raw, post / raw, actual / raw))

    rows.sort(key=lambda r: -r[4])
    print(f"{'movie':26}{'audience':16}{'raw$M':>7}{'applied':>9}{'required':>10}{'gap':>7}")
    for m, at, raw, ap, req in rows:
        print(f"{m[:26]:26}{at[:16]:16}{raw:>7.1f}{ap:>9.2f}{req:>10.2f}{req/ap:>7.2f}")
    fam = [r for r in rows if r[1] == "broad_family"]
    non = [r for r in rows if r[1] and r[1] != "broad_family"]
    if fam:
        print(f"\nbroad_family (n={len(fam)}): mean required uplift "
              f"{sum(r[4] for r in fam)/len(fam):.2f}  vs applied {sum(r[3] for r in fam)/len(fam):.2f}")
    if non:
        print(f"other tagged (n={len(non)}): mean required uplift "
              f"{sum(r[4] for r in non)/len(non):.2f}  vs applied {sum(r[3] for r in non)/len(non):.2f}")


if __name__ == "__main__":
    main()
