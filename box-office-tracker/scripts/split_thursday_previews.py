#!/usr/bin/env python3
"""Make recorded actuals mean the same thing for every film.

The Numbers folds Thursday previews into Friday. 22 of 34 recorded films had a
separate Thursday line and 12 did not, so the Thursday-to-weekend shape was
learned from two definitions at once (the step that missed on Resident Evil).
For films whose previews were reported by the trades, this moves the preview
gross out of Friday into Thursday (weekend total unchanged) and appends the
same split to daily-actual-overrides.csv. Films with no reported previews are
flagged previews_folded_into_friday=True, which the fits treat as "Thursday
unknown, Friday not a clean Friday". Idempotent.

  python3 scripts/split_thursday_previews.py [--dry-run]
"""
import csv, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import calibrate as C  # noqa: E402

# movie -> (Thursday previews $M, source). Reported by the studio via the
# trades the Friday morning after previews; Coyote's figure includes ~$0.45M
# of prior-weekend sneaks the studio folded into "previews".
PREVIEWS = {
    "The Devil Wears Prada 2": (10.0, "Variety 2026-05-01 https://variety.com/2026/film/box-office/box-office-devil-wears-prada-2-previews-1236734300/"),
    "The Mandalorian and Grogu": (12.0, "Variety 2026-05-22 https://variety.com/2026/film/box-office/box-office-mandalorian-grogu-previews-1236756178/"),
    "The Breadwinner": (0.75, "trade reports 2026-05-29 (Yahoo/ComingSoon: ~$750K previews)"),
    "The Odyssey": (17.6, "Variety/THR 2026-07-17 https://variety.com/2026/film/box-office/box-office-the-odyssey-previews-1236812480/"),
    "The End of Oak Street": (2.5, "Variety 2026-08-14 https://variety.com/2026/film/box-office/box-office-end-of-oak-street-previews-1236833323/"),
    "Coyote vs. Acme": (1.7, "Deadline 2026-08-28 (incl. ~$446K prior-weekend sneaks) https://www.worldofreel.com/blog/2026/8/28/box-office-coyote-vs-acme-eyes-17m-opening-after-17m-thursday-the-dog-stars-bombs-with-850k"),
    "The Dog Stars": (0.85, "Deadline 2026-08-28 https://www.worldofreel.com/blog/2026/8/28/box-office-coyote-vs-acme-eyes-17m-opening-after-17m-thursday-the-dog-stars-bombs-with-850k"),
}
OVERRIDES = ROOT / "data" / "daily-actual-overrides.csv"


def split_entry(entry, previews_m, source):
    """Pure: move previews from Friday to Thursday. Returns True if changed."""
    da = dict(entry.get("daily_actuals") or {})
    if da.get("Thursday"):
        return False
    fri = float(da.get("Friday") or 0)
    if fri <= previews_m:
        return False
    da["Thursday"] = round(previews_m, 3)
    da["Friday"] = round(fri - previews_m, 3)
    entry["daily_actuals"] = da
    entry["previews_split_source"] = source
    entry.pop("previews_folded_into_friday", None)
    return True


def flag_entry(entry):
    """Pure: mark an entry whose Friday still carries unreported previews."""
    da = entry.get("daily_actuals") or {}
    if da.get("Thursday") or entry.get("previews_folded_into_friday"):
        return False
    entry["previews_folded_into_friday"] = True
    return True


def main(argv):
    dry = "--dry-run" in argv
    cal = C.load_calibration()
    changed, flagged, override_rows = [], [], []
    for entry in cal.get("history", []):
        movie = entry.get("movie", "")
        if movie in PREVIEWS:
            prev, src = PREVIEWS[movie]
            if split_entry(entry, prev, src):
                changed.append(movie)
                da = entry["daily_actuals"]
                for day, note in (("Thursday", f"Thursday previews per {src.split(' http')[0]}"),
                                  ("Friday", f"Reported Friday incl previews minus Thursday previews {prev}M")):
                    override_rows.append({"weekend_of": entry["weekend_of"], "movie_title": movie, "day_of_week": day,
                                          "gross_m": da[day], "source": "trade report split", "status": "reported",
                                          "as_of_date": time.strftime("%Y-%m-%d"), "notes": note})
        elif flag_entry(entry):
            flagged.append(movie)
    print("split  :", changed)
    print("flagged:", flagged)
    if dry:
        print("(dry run)"); return 0
    C.save_calibration(cal)
    if override_rows:
        with open(OVERRIDES, newline="") as f:
            r = csv.DictReader(f); fields = r.fieldnames; existing = [(x["weekend_of"], x["movie_title"], x["day_of_week"], x["source"]) for x in r]
        with open(OVERRIDES, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            for row in override_rows:
                if (row["weekend_of"], row["movie_title"], row["day_of_week"], row["source"]) not in existing:
                    w.writerow({k: row.get(k, "") for k in fields})
    print(f"saved calibration.json; appended {len(override_rows)} override rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
