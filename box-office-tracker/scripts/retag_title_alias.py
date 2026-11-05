#!/usr/bin/env python3
"""Fold a film tracked under two spellings onto its canonical title.

    python3 scripts/retag_title_alias.py --weekend 2026-11-06 \
        --alias "Ramayana" --canonical "Ramayana: Rise of A Legend" [--write]

Why (2026-11-05): Polymarket listed "Ramayana", the Box Office Mojo calendar
"Ramayana: Rise of A Legend". Tracked side by side for a day they became two
films — 5,094 AMC rows, Cinemark and the metadata under the full title; the
live market, Regal, Fandango, 35 AMC rows and 106 Webedia rows under the
short one; every AMC theatre-date linked twice. scraper.py now treats the
short spelling as an alias (data/title-aliases.json); this script repairs the
data already written, then records the alias so every lane keeps matching
both spellings:

  * every data/*.csv with a movie_title or movie column: rows for the alias in
    the weekend are retagged (weekend_of column, else a weekend_of=... note,
    else every row); rows that become exact duplicates are dropped
  * movie-metadata.csv: the alias row's non-empty fields fill blanks in the
    canonical row, then the alias row goes
  * showtime-links.json: alias entries merge into the canonical film per
    theatre-date (union of showtime_ids)
  * theatre-counts.json: alias count/request folded into the canonical

Dry run by default; --write rewrites atomically.
"""
import csv
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"
TITLE_COLUMNS = ("movie_title", "movie")
SKIP_CSV = {"test-run-2026-04-05.csv"}


def _row_weekend(row):
    wk = (row.get("weekend_of") or "").strip()
    if wk:
        return wk
    m = re.search(r"weekend_of=(\d{4}-\d{2}-\d{2})", row.get("notes") or "")
    return m.group(1) if m else ""


def retag_csv(path, weekend, alias, canonical):
    """(rows, fieldnames, retagged, dropped_duplicates); rows unchanged when 0."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    col = next((c for c in TITLE_COLUMNS if c in fields), None)
    if not col:
        return rows, fields, 0, 0
    seen = set()
    out, retagged, dropped = [], 0, 0
    for row in rows:
        if (row.get(col) or "").strip() == alias and _row_weekend(row) in ("", weekend):
            row = dict(row, **{col: canonical})
            retagged += 1
        key = tuple(row.get(c, "") for c in fields)
        if retagged and key in seen:
            dropped += 1
            continue
        seen.add(key)
        out.append(row)
    return out, fields, retagged, dropped


def merge_metadata_rows(rows, weekend, alias, canonical):
    """Alias row -> canonical row for the weekend (filling blanks); returns rows, changed."""
    canon = [r for r in rows if (r.get("movie") or "").strip() == canonical
             and (r.get("weekend_of") or "").strip() == weekend]
    al = [r for r in rows if (r.get("movie") or "").strip() == alias
          and (r.get("weekend_of") or "").strip() == weekend]
    if not al:
        return rows, False
    if not canon:
        for r in al:
            r["movie"] = canonical
        return rows, True
    target = canon[0]
    for r in al:
        for k, v in r.items():
            if k != "movie" and (v or "").strip() and not (target.get(k) or "").strip():
                target[k] = v
    return [r for r in rows if r not in al], True


def merge_link_movies(movies, alias, canonical):
    """Fold movies[alias] into movies[canonical] (union by showtime_id)."""
    if not isinstance(movies, dict) or alias not in movies:
        return movies, False
    alias_shows = movies.pop(alias) or []
    kept = list(movies.get(canonical) or [])
    ids = {s.get("showtime_id") for s in kept if isinstance(s, dict)}
    for s in alias_shows:
        if isinstance(s, dict) and s.get("showtime_id") not in ids:
            kept.append(s)
            ids.add(s.get("showtime_id"))
    if kept or canonical in movies:
        movies[canonical] = kept
    return movies, True


def retag_links(data, weekend, alias, canonical):
    """(data, theatre-dates merged)."""
    if not isinstance(data, dict) or (data.get("weekend_of") or data.get("date")) != weekend:
        return data, 0
    merged = 0
    for entry in (data.get("theatres") or {}).values():
        _, changed = merge_link_movies(entry.get("movies"), alias, canonical)
        merged += int(changed)
        for date_entry in (entry.get("dates") or {}).values():
            movies, changed = merge_link_movies(date_entry.get("movies"), alias, canonical)
            if changed:
                merged += 1
                date_entry["empty"] = not any(movies.values()) if isinstance(movies, dict) else True
    return data, merged


def retag_theatre_counts(data, alias, canonical):
    if not isinstance(data, dict):
        return data, False
    changed = False
    if alias in data:
        if canonical not in data or not data.get(canonical):
            data[canonical] = data[alias]
        del data[alias]
        changed = True
    req = data.get("_requested_movies")
    if isinstance(req, list) and alias in req:
        data["_requested_movies"] = [canonical if t == alias else t for t in req]
        seen, uniq = set(), []
        for t in data["_requested_movies"]:
            if t not in seen:
                seen.add(t)
                uniq.append(t)
        data["_requested_movies"] = uniq
        changed = True
    return data, changed


def _write_csv(path, rows, fields):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def _write_json(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def retag(weekend, alias, canonical, data_dir=DATA_DIR, write=False, log=print):
    """Apply every repair; returns {file: (retagged, dropped)}."""
    data_dir = Path(data_dir)
    report = {}
    for path in sorted(data_dir.glob("*.csv")):
        if path.name in SKIP_CSV:
            continue
        rows, fields, retagged, dropped = retag_csv(path, weekend, alias, canonical)
        changed = retagged > 0
        if path.name == "movie-metadata.csv" and changed:
            rows, _ = merge_metadata_rows(rows, weekend, alias, canonical)
            # rows retagged above already carry the canonical name; merge
            # collapses duplicates produced for the weekend
            canon_rows = [r for r in rows if (r.get("movie") or "").strip() == canonical
                          and (r.get("weekend_of") or "").strip() == weekend]
            if len(canon_rows) > 1:
                keep = canon_rows[0]
                for extra in canon_rows[1:]:
                    for k, v in extra.items():
                        if (v or "").strip() and not (keep.get(k) or "").strip():
                            keep[k] = v
                    rows.remove(extra)
                    dropped += 1
        if changed:
            report[path.name] = (retagged, dropped)
            log(f"  {path.name}: {retagged} row(s) -> '{canonical}'"
                + (f", {dropped} duplicate(s) dropped" if dropped else ""))
            if write:
                _write_csv(path, rows, fields)

    links = data_dir / "showtime-links.json"
    if links.exists():
        try:
            data = json.loads(links.read_text())
        except ValueError:
            data = None
        data, merged = retag_links(data, weekend, alias, canonical)
        if merged:
            report[links.name] = (merged, 0)
            log(f"  {links.name}: {merged} theatre-date(s) folded into '{canonical}'")
            if write:
                _write_json(links, data)

    counts = data_dir / "theatre-counts.json"
    if counts.exists():
        try:
            data = json.loads(counts.read_text())
        except ValueError:
            data = None
        data, changed = retag_theatre_counts(data, alias, canonical)
        if changed:
            report[counts.name] = (1, 0)
            log(f"  {counts.name}: '{alias}' folded into '{canonical}'")
            if write:
                _write_json(counts, data)

    if write:
        from scraper import record_title_alias
        if record_title_alias(weekend, canonical, alias, path=data_dir / "title-aliases.json"):
            log(f"  title-aliases.json: recorded '{alias}' -> '{canonical}' ({weekend})")
    return report


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    write = "--write" in argv
    opts = {}
    for flag in ("--weekend", "--alias", "--canonical"):
        if flag not in argv or argv.index(flag) + 1 >= len(argv):
            print(__doc__)
            return 2
        opts[flag] = argv[argv.index(flag) + 1]
    weekend, alias, canonical = opts["--weekend"], opts["--alias"], opts["--canonical"]
    if alias == canonical:
        print("alias and canonical title are identical; nothing to do")
        return 2
    print(f"retag_title_alias: '{alias}' -> '{canonical}' for weekend {weekend}"
          + ("" if write else " (dry run; pass --write)"))
    report = retag(weekend, alias, canonical, write=write)
    if not report:
        print("  nothing to retag")
    return 0


if __name__ == "__main__":
    sys.exit(main())
