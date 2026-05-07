#!/usr/bin/env python3
"""Local dashboard for box-office tracker data.

Run:
    python3 dashboard.py

Then open http://127.0.0.1:8765. The dashboard reads the canonical data files
on every refresh and can fast-forward local data from origin/main when the
worktree is clean.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ROOT_DIR = BASE_DIR.parent
TZ_ORDER = ("ET", "CT", "PT")

SEAT_FIELDS = [
    "weekend_of", "run_id", "date", "day_of_week", "theatre_name",
    "theatre_city", "timezone", "movie_title", "polymarket_market",
    "showtime", "check_time", "minutes_after_showtime", "auditorium_name",
    "auditorium_type", "total_seats", "seats_sold", "seats_available",
    "occupancy_pct", "amc_seat_map_url", "notes",
]

PRE_RESERVATION_FIELDS = [
    "weekend_of", "run_id", "snapshot_time", "snapshot_bucket",
    "show_date", "day_of_week", "theatre_name", "theatre_city",
    "timezone", "movie_title", "showtime", "showtime_id",
    "minutes_until_showtime", "auditorium_name", "auditorium_type",
    "total_seats", "reserved_seats", "available_seats", "occupancy_pct",
    "delta_reserved_since_previous", "amc_seat_map_url", "notes",
]

POLY_FIELDS = [
    "date", "movie_title", "market_url", "market_question",
    "outcome_prices", "volume", "market_id", "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def to_int(value, default=0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def to_float(value, default=0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def iso_or_blank(value: str | None) -> str:
    return value or ""


def weekend_friday_for_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except (TypeError, ValueError):
        return ""
    wd = dt.weekday()
    if wd == 3:
        friday = dt.replace(day=dt.day)  # Thursday -> next day below
        from datetime import timedelta
        return (friday + timedelta(days=1)).strftime("%Y-%m-%d")
    from datetime import timedelta
    if wd == 4:
        friday = dt
    elif wd == 5:
        friday = dt - timedelta(days=1)
    elif wd == 6:
        friday = dt - timedelta(days=2)
    elif wd == 0:
        friday = dt - timedelta(days=3)
    elif wd == 1:
        friday = dt - timedelta(days=4)
    else:
        friday = dt - timedelta(days=5)
    return friday.strftime("%Y-%m-%d")


def opening_weekend_show_dates(weekend_of: str) -> list[str]:
    try:
        friday = datetime.strptime(weekend_of, "%Y-%m-%d")
    except (TypeError, ValueError):
        return []
    from datetime import timedelta
    return [
        (friday + timedelta(days=offset)).strftime("%Y-%m-%d")
        for offset in (-1, 0, 1, 2)
    ]


def row_weekend(row: dict[str, str], date_field: str) -> str:
    return row.get("weekend_of") or weekend_friday_for_date(row.get(date_field, ""))


def latest_weekend(seat_rows, snapshot_rows, poly_rows) -> str:
    weekends = set()
    weekends.update(row.get("weekend_of", "") for row in seat_rows if row.get("weekend_of"))
    weekends.update(row.get("weekend_of", "") for row in snapshot_rows if row.get("weekend_of"))
    weekends.update(weekend_friday_for_date(row.get("date", "")) for row in poly_rows)
    weekends.discard("")
    return max(weekends) if weekends else weekend_friday_for_date(datetime.now().strftime("%Y-%m-%d"))


def timezone_counts(rows) -> dict[str, int]:
    counts = Counter(row.get("timezone", "") for row in rows if row.get("timezone"))
    return {tz: counts.get(tz, 0) for tz in TZ_ORDER if counts.get(tz, 0)}


def missing_timezones(rows) -> list[str]:
    counts = timezone_counts(rows)
    return [tz for tz in TZ_ORDER if counts.get(tz, 0) == 0]


def missing_date_timezones(rows, show_dates) -> dict[str, list[str]]:
    missing = {}
    for show_date in show_dates:
        counts = Counter(
            row.get("timezone", "")
            for row in rows
            if row.get("show_date") == show_date and row.get("timezone")
        )
        missing_tz = [tz for tz in TZ_ORDER if counts.get(tz, 0) == 0]
        if missing_tz:
            missing[show_date] = missing_tz
    return missing


def weighted_pct(rows, sold_field) -> float | None:
    sold = 0
    total = 0
    for row in rows:
        row_total = to_int(row.get("total_seats"))
        row_sold = to_int(row.get(sold_field))
        if row_total > 0 and row_sold >= 0:
            total += row_total
            sold += row_sold
    if not total:
        return None
    return round(sold / total * 100, 1)


def latest_value(rows, field) -> str:
    values = [row.get(field, "") for row in rows if row.get(field)]
    return max(values) if values else ""


def run_ids(rows) -> list[str]:
    return sorted({row.get("run_id", "") for row in rows if row.get("run_id")})


def summarize_seat_rows(rows) -> dict:
    dates = sorted({row.get("date", "") for row in rows if row.get("date")})
    return {
        "rows": len(rows),
        "theatres": len({row.get("theatre_name", "") for row in rows if row.get("theatre_name")}),
        "showtimes": len({row.get("amc_seat_map_url", "") or (row.get("theatre_name", "") + row.get("showtime", "")) for row in rows}),
        "dates": dates,
        "timezone_rows": timezone_counts(rows),
        "missing_timezones": missing_timezones(rows) if rows else TZ_ORDER,
        "latest_check_time": iso_or_blank(latest_value(rows, "check_time")),
        "latest_run_ids": run_ids(rows)[-6:],
        "weighted_occupancy_pct": weighted_pct(rows, "seats_sold"),
    }


def summarize_snapshot_rows(rows) -> dict:
    show_dates = sorted({row.get("show_date", "") for row in rows if row.get("show_date")})
    return {
        "rows": len(rows),
        "theatres": len({row.get("theatre_name", "") for row in rows if row.get("theatre_name")}),
        "showtimes": len({row.get("showtime_id", "") or (row.get("theatre_name", "") + row.get("showtime", "")) for row in rows}),
        "show_dates": show_dates,
        "timezone_rows": timezone_counts(rows),
        "missing_timezones": missing_timezones(rows) if rows else TZ_ORDER,
        "latest_snapshot_time": iso_or_blank(latest_value(rows, "snapshot_time")),
        "latest_run_ids": run_ids(rows)[-6:],
        "weighted_reserved_pct": weighted_pct(rows, "reserved_seats"),
    }


def summarize_poly_rows(rows) -> dict:
    latest_date = latest_value(rows, "date")
    latest_rows = [row for row in rows if row.get("date") == latest_date] if latest_date else rows
    return {
        "rows": len(rows),
        "latest_date": latest_date,
        "market_url": next((row.get("market_url", "") for row in latest_rows if row.get("market_url")), ""),
        "volume": round(sum(to_float(row.get("volume")) for row in latest_rows), 0),
        "brackets": len(latest_rows),
    }


def load_run_log_summaries(data_dir: Path) -> dict[str, dict]:
    log_dir = data_dir / "run-logs"
    summaries = {}
    if not log_dir.exists():
        return summaries
    files = sorted(log_dir.glob("*/*.md"))[-250:]
    for path in files:
        text = path.read_text(errors="ignore")
        run_id = re.search(r"\*\*Run ID:\*\*\s*([^\n]+)", text)
        if not run_id:
            continue
        rows = re.search(r"\*\*Rows:\*\*\s*(\d+)", text)
        issues = re.search(r"\*\*Issues:\*\*\s*(\d+)", text)
        title = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        summaries[run_id.group(1).strip()] = {
            "path": str(path),
            "title": title.group(1).strip() if title else path.stem,
            "rows": to_int(rows.group(1)) if rows else None,
            "issues": to_int(issues.group(1)) if issues else None,
        }
    return summaries


def build_prediction_map(current_weekend: str, data_dir: Path) -> dict[str, dict]:
    if data_dir.resolve() != DATA_DIR.resolve():
        return {}
    try:
        import predict
    except Exception as exc:
        return {"_error": {"message": str(exc)}}
    try:
        cal = predict.load_calibration()
        seat_data = predict.load_seat_data(weekend_of=current_weekend)
        poly_data = predict.load_polymarket_data(weekend_of=current_weekend)
        theatre_counts = predict.load_theatre_counts()
    except Exception as exc:
        return {"_error": {"message": str(exc)}}

    predictions = {}
    for movie, movie_seat_data in seat_data.items():
        try:
            nat_count = predict.national_theatre_count_for_movie(movie, theatre_counts)
            pred = predict.predict_movie(
                movie,
                movie_seat_data,
                poly_data.get(movie, []),
                cal,
                national_theatre_count=nat_count,
            )
            if not pred:
                continue
            mid, low, high = predict.regression_prediction_values(pred)
            predictions[movie] = {
                "mid_m": round(mid, 1),
                "low_m": round(low, 1),
                "high_m": round(high, 1),
                "source": pred.get("regression_source", ""),
                "basis": pred.get("regression_basis", ""),
                "uses_polymarket": bool(pred.get("regression_uses_polymarket")),
                "seat_only_m": round(pred.get("seat_mid_m", 0), 1),
                "seat_comp_m": round(pred["seat_comp_mid_m"], 1) if pred.get("seat_comp_mid_m") is not None else None,
                "seat_primary_m": round(pred["seat_primary_mid_m"], 1) if pred.get("seat_primary_mid_m") is not None else None,
                "n_days": pred.get("n_days"),
                "n_theatres": pred.get("n_theatres_total"),
                "coverage_ratio": pred.get("coverage_ratio"),
                "quality": pred.get("seat_data_quality"),
                "daily": [
                    {
                        "day": day,
                        "date": details.get("date", ""),
                        "mid_m": round(details.get("domestic_mid", 0) / 1_000_000, 1),
                        "theatres": details.get("n_theatres"),
                        "missing_timezones": details.get("missing_timezones") or [],
                    }
                    for day, details in sorted(
                        pred.get("daily_details", {}).items(),
                        key=lambda item: item[1].get("date", ""),
                    )
                ],
            }
        except Exception as exc:
            predictions[movie] = {"error": str(exc)}
    return predictions


def git_command(args: list[str], cwd: Path, timeout=30) -> dict:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return {"ok": False, "output": str(exc)}
    output = (proc.stdout + proc.stderr).strip()
    return {"ok": proc.returncode == 0, "output": output}


def git_snapshot(repo_dir: Path) -> dict:
    branch = git_command(["branch", "--show-current"], repo_dir)
    head = git_command(["rev-parse", "--short", "HEAD"], repo_dir)
    status = git_command(["status", "--short"], repo_dir)
    return {
        "branch": branch["output"],
        "head": head["output"],
        "dirty": bool(status["output"]),
        "status": status["output"],
    }


def maybe_git_pull(repo_dir: Path, auto_pull: bool) -> dict:
    if not auto_pull:
        return {"attempted": False, "ok": None, "output": "auto-pull disabled"}
    status = git_command(["status", "--short"], repo_dir)
    if status["output"]:
        return {
            "attempted": False,
            "ok": None,
            "output": "worktree dirty; skipped git pull",
        }
    pull = git_command(["pull", "--ff-only", "origin", "main"], repo_dir, timeout=60)
    return {"attempted": True, **pull}


def run_status(rows, current_weekend, row_type) -> dict:
    if row_type == "snapshot":
        current = [row for row in rows if row.get("weekend_of") == current_weekend]
        latest_time = latest_value(current, "snapshot_time")
        observed_show_dates = sorted({
            row.get("show_date", "")
            for row in current
            if row.get("show_date")
        })
        expected_show_dates = opening_weekend_show_dates(current_weekend)
        missing_show_dates = [
            date_str for date_str in expected_show_dates
            if date_str not in observed_show_dates
        ]
        missing_date_tz = missing_date_timezones(current, expected_show_dates)
    else:
        current = [row for row in rows if row.get("weekend_of") == current_weekend]
        latest_time = latest_value(current, "check_time")
        observed_show_dates = []
        expected_show_dates = []
        missing_show_dates = []
        missing_date_tz = {}

    if not current:
        return {
            "status": "pending",
            "label": "Pending",
            "rows": 0,
            "latest_time": "",
            "timezone_rows": {},
            "missing_timezones": list(TZ_ORDER),
            "missing_date_timezones": {},
        }

    missing = missing_timezones(current)
    status = "partial" if missing or missing_show_dates or missing_date_tz else "ok"
    return {
        "status": status,
        "label": "OK" if status == "ok" else "Partial",
        "rows": len(current),
        "latest_time": latest_time,
        "timezone_rows": timezone_counts(current),
        "missing_timezones": missing,
        "show_dates": observed_show_dates,
        "missing_show_dates": missing_show_dates,
        "missing_date_timezones": missing_date_tz,
        "run_ids": run_ids(current)[-6:],
    }


def phase1_status(showtime_links: dict, current_weekend: str) -> dict:
    weekend = showtime_links.get("weekend_of") or showtime_links.get("date", "")
    theatres = showtime_links.get("theatres") or {}
    status = "ok" if weekend == current_weekend and theatres else "stale"
    return {
        "status": status,
        "label": "OK" if status == "ok" else "Stale",
        "weekend_of": weekend,
        "collected_at": showtime_links.get("collected_at", ""),
        "theatres": len(theatres),
        "movies": showtime_links.get("_requested_movies") or [],
    }


def build_dashboard_data(data_dir: Path = DATA_DIR, auto_pull=False,
                         include_predictions=True) -> dict:
    data_dir = Path(data_dir)
    pull = maybe_git_pull(ROOT_DIR, auto_pull) if data_dir.resolve() == DATA_DIR.resolve() else {
        "attempted": False,
        "ok": None,
        "output": "custom data dir; skipped git pull",
    }

    seat_rows = read_csv(data_dir / "seat-counts.csv")
    snapshot_rows = read_csv(data_dir / "pre-reservation-snapshots.csv")
    poly_rows = read_csv(data_dir / "polymarket-markets.csv")
    showtime_links = read_json(data_dir / "showtime-links.json")
    run_logs = load_run_log_summaries(data_dir)
    current_weekend = latest_weekend(seat_rows, snapshot_rows, poly_rows)

    current_seat_rows = [row for row in seat_rows if row_weekend(row, "date") == current_weekend]
    current_snapshot_rows = [
        row for row in snapshot_rows
        if row_weekend(row, "show_date") == current_weekend
    ]
    current_poly_rows = [
        row for row in poly_rows
        if weekend_friday_for_date(row.get("date", "")) == current_weekend
    ]

    predictions = build_prediction_map(current_weekend, data_dir) if include_predictions else {}
    movies = sorted({
        row.get("movie_title", "")
        for row in current_seat_rows + current_snapshot_rows + current_poly_rows
        if row.get("movie_title")
    })
    if not movies:
        movies = sorted(predictions.keys())

    movie_cards = []
    for movie in movies:
        movie_seat = [row for row in current_seat_rows if row.get("movie_title") == movie]
        movie_snapshot = [row for row in current_snapshot_rows if row.get("movie_title") == movie]
        movie_poly = [row for row in current_poly_rows if row.get("movie_title") == movie]
        latest_run_ids = set(run_ids(movie_seat) + run_ids(movie_snapshot))
        movie_cards.append({
            "movie": movie,
            "weekend_of": current_weekend,
            "prediction": predictions.get(movie),
            "seat_data": summarize_seat_rows(movie_seat),
            "snapshot": summarize_snapshot_rows(movie_snapshot),
            "market": summarize_poly_rows(movie_poly),
            "run_logs": [
                {"run_id": run_id, **run_logs[run_id]}
                for run_id in sorted(latest_run_ids)
                if run_id in run_logs
            ],
        })

    movie_cards.sort(
        key=lambda card: (
            card["prediction"] is None,
            -(card["snapshot"]["rows"] + card["seat_data"]["rows"]),
            card["movie"],
        )
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_weekend": current_weekend,
        "git": git_snapshot(ROOT_DIR),
        "pull": pull,
        "runs": {
            "phase1": phase1_status(showtime_links, current_weekend),
            "snapshot": run_status(snapshot_rows, current_weekend, "snapshot"),
            "regular": run_status(seat_rows, current_weekend, "regular"),
        },
        "movies": movie_cards,
        "totals": {
            "seat_rows": len(seat_rows),
            "snapshot_rows": len(snapshot_rows),
            "polymarket_rows": len(poly_rows),
        },
    }


HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Box Office Tracker Dashboard</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --ink: #18212f;
      --muted: #647084;
      --line: #dfe4eb;
      --ok: #15803d;
      --warn: #b45309;
      --bad: #b91c1c;
      --accent: #0f766e;
      --blue: #1d4ed8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    header {
      padding: 18px 24px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      position: sticky;
      top: 0;
      z-index: 10;
    }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }
    h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.2;
      font-weight: 750;
    }
    .subline {
      margin-top: 5px;
      color: var(--muted);
      font-size: 13px;
    }
    button {
      border: 1px solid #0f766e;
      background: var(--accent);
      color: white;
      border-radius: 6px;
      padding: 9px 13px;
      font-weight: 700;
      cursor: pointer;
    }
    button.secondary {
      background: white;
      color: var(--ink);
      border-color: var(--line);
    }
    main {
      max-width: 1440px;
      margin: 0 auto;
      padding: 18px 20px 36px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    .panel, .movie {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    .panel {
      padding: 14px;
      min-height: 108px;
    }
    .label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .value {
      margin-top: 6px;
      font-size: 25px;
      font-weight: 780;
      line-height: 1.15;
    }
    .detail {
      margin-top: 6px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }
    .status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      font-weight: 750;
      border: 1px solid var(--line);
    }
    .ok { color: var(--ok); background: #ecfdf3; border-color: #bbf7d0; }
    .partial, .pending { color: var(--warn); background: #fffbeb; border-color: #fde68a; }
    .stale, .error { color: var(--bad); background: #fef2f2; border-color: #fecaca; }
    .movies {
      display: grid;
      gap: 12px;
    }
    .movie {
      padding: 0;
      overflow: hidden;
    }
    .movie-header {
      display: grid;
      grid-template-columns: minmax(220px, 1.25fr) repeat(4, minmax(150px, 1fr));
      gap: 0;
      border-bottom: 1px solid var(--line);
      background: #fbfcfd;
    }
    .cell {
      padding: 13px 14px;
      border-right: 1px solid var(--line);
      min-width: 0;
    }
    .cell:last-child { border-right: 0; }
    .movie-title {
      font-size: 18px;
      font-weight: 780;
      overflow-wrap: anywhere;
    }
    .metric {
      font-size: 18px;
      font-weight: 780;
      margin-top: 3px;
    }
    .small {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
      margin-top: 4px;
    }
    .movie-body {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0;
    }
    .section {
      padding: 12px 14px;
      border-right: 1px solid var(--line);
    }
    .section:last-child { border-right: 0; }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    th, td {
      text-align: left;
      padding: 8px 7px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }
    th {
      color: var(--muted);
      font-size: 12px;
      font-weight: 750;
    }
    a { color: var(--blue); text-decoration: none; }
    .empty {
      padding: 22px;
      color: var(--muted);
      background: var(--panel);
      border: 1px dashed var(--line);
      border-radius: 8px;
    }
    @media (max-width: 1020px) {
      .grid { grid-template-columns: repeat(2, minmax(160px, 1fr)); }
      .movie-header { grid-template-columns: 1fr 1fr; }
      .movie-body { grid-template-columns: 1fr; }
      .section { border-right: 0; border-bottom: 1px solid var(--line); }
    }
    @media (max-width: 640px) {
      header { padding: 14px; }
      main { padding: 12px; }
      .grid { grid-template-columns: 1fr; }
      .movie-header { grid-template-columns: 1fr; }
      .cell { border-right: 0; border-bottom: 1px solid var(--line); }
    }
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <div>
        <h1>Box Office Tracker</h1>
        <div class="subline" id="subtitle">Loading local data...</div>
      </div>
      <div>
        <button id="refresh">Refresh</button>
        <button class="secondary" id="json">JSON</button>
      </div>
    </div>
  </header>
  <main>
    <div class="grid" id="runGrid"></div>
    <div class="movies" id="movies"></div>
  </main>
  <script>
    const fmtMoney = v => v == null ? "Pending" : `$${Number(v).toFixed(1)}M`;
    const fmtPct = v => v == null ? "-" : `${Math.round(Number(v) * 100)}%`;
    const fmtTime = value => {
      if (!value) return "-";
      const d = new Date(value);
      if (Number.isNaN(d.getTime())) return value;
      return d.toLocaleString();
    };
    const esc = value => String(value ?? "").replace(/[&<>"']/g, ch => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[ch]));
    const statusClass = status => ["ok", "partial", "pending", "stale", "error"].includes(status) ? status : "pending";
    const tzText = obj => ["ET", "CT", "PT"].map(tz => `${tz} ${obj?.[tz] ?? 0}`).join(" / ");

    let lastData = null;

    function panel(label, value, detail, status) {
      return `<div class="panel">
        <div class="label">${esc(label)} ${status ? `<span class="status ${statusClass(status.status)}">${esc(status.label || status.status)}</span>` : ""}</div>
        <div class="value">${value}</div>
        <div class="detail">${detail}</div>
      </div>`;
    }

    function render(data) {
      lastData = data;
      document.getElementById("subtitle").textContent =
        `Weekend ${data.current_weekend} | updated ${fmtTime(data.generated_at)} | ${data.git.branch}@${data.git.head}`;
      const phase1 = data.runs.phase1;
      const snapshot = data.runs.snapshot;
      const regular = data.runs.regular;
      const snapshotDates = snapshot.missing_show_dates?.length
        ? `missing ${snapshot.missing_show_dates.join(", ")}`
        : `dates ${(snapshot.show_dates || []).join(", ") || "-"}`;
      const snapshotMissingSlices = snapshot.missing_date_timezones && Object.keys(snapshot.missing_date_timezones).length
        ? ` | incomplete ${Object.entries(snapshot.missing_date_timezones).map(([date, tz]) => `${date}:${tz.join("/")}`).join(", ")}`
        : "";
      document.getElementById("runGrid").innerHTML = [
        panel("Phase 1 links", `${phase1.theatres || 0} theatres`, `${fmtTime(phase1.collected_at)} | ${esc((phase1.movies || []).join(", ") || "-")}`, phase1),
        panel("Snapshot", `${snapshot.rows || 0} rows`, `${fmtTime(snapshot.latest_time)} | ${tzText(snapshot.timezone_rows)} | ${snapshotDates}${snapshotMissingSlices}`, snapshot),
        panel("Regular scrape", `${regular.rows || 0} rows`, `${fmtTime(regular.latest_time)} | ${tzText(regular.timezone_rows)}`, regular),
        panel("Local data", `${data.totals.seat_rows.toLocaleString()} seat rows`, `${data.totals.snapshot_rows.toLocaleString()} snapshot rows | pull: ${esc(data.pull.output || "-")}`, {status: data.git.dirty ? "partial" : "ok", label: data.git.dirty ? "Dirty" : "Clean"}),
      ].join("");

      const movies = data.movies || [];
      document.getElementById("movies").innerHTML = movies.length ? movies.map(renderMovie).join("") :
        `<div class="empty">No movie data found for this weekend.</div>`;
    }

    function renderMovie(movie) {
      const p = movie.prediction;
      const estimate = p && !p.error ? fmtMoney(p.mid_m) : "Pending";
      const range = p && !p.error ? `${fmtMoney(p.low_m)} - ${fmtMoney(p.high_m)}` : "No seat-count model yet";
      const marketUrl = movie.market.market_url;
      const dailyRows = p && p.daily ? p.daily.map(row => `<tr>
        <td>${esc(row.day)}<div class="small">${esc(row.date)}</div></td>
        <td>${fmtMoney(row.mid_m)}</td>
        <td>${esc(row.theatres ?? "-")}</td>
        <td>${esc((row.missing_timezones || []).join("/") || "-")}</td>
      </tr>`).join("") : `<tr><td colspan="4">Estimate appears after regular seat collection.</td></tr>`;
      const runLogRows = (movie.run_logs || []).map(log => `<tr>
        <td>${esc(log.run_id)}</td>
        <td>${esc(log.rows ?? "-")}</td>
        <td>${esc(log.issues ?? "-")}</td>
      </tr>`).join("") || `<tr><td colspan="3">No run-log summary attached.</td></tr>`;
      return `<article class="movie">
        <div class="movie-header">
          <div class="cell">
            <div class="movie-title">${esc(movie.movie)}</div>
            <div class="small">Weekend ${esc(movie.weekend_of)} ${marketUrl ? `| <a href="${esc(marketUrl)}" target="_blank" rel="noreferrer">market</a>` : ""}</div>
          </div>
          <div class="cell">
            <div class="label">Model estimate</div>
            <div class="metric">${estimate}</div>
            <div class="small">${range}<br>${p && !p.error ? esc(p.source) : ""}</div>
          </div>
          <div class="cell">
            <div class="label">Seat data</div>
            <div class="metric">${movie.seat_data.rows.toLocaleString()} rows</div>
            <div class="small">${movie.seat_data.theatres} theatres | ${tzText(movie.seat_data.timezone_rows)}<br>${fmtTime(movie.seat_data.latest_check_time)}</div>
          </div>
          <div class="cell">
            <div class="label">Snapshot</div>
            <div class="metric">${movie.snapshot.rows.toLocaleString()} rows</div>
            <div class="small">${movie.snapshot.theatres} theatres | ${tzText(movie.snapshot.timezone_rows)}<br>${esc((movie.snapshot.show_dates || []).join(", ") || "-")}<br>${fmtTime(movie.snapshot.latest_snapshot_time)}</div>
          </div>
          <div class="cell">
            <div class="label">Market</div>
            <div class="metric">${movie.market.brackets || 0} brackets</div>
            <div class="small">${movie.market.latest_date || "-"} | volume $${Number(movie.market.volume || 0).toLocaleString()}</div>
          </div>
        </div>
        <div class="movie-body">
          <section class="section">
            <table>
              <thead><tr><th>Day</th><th>Model</th><th>Theatres</th><th>Missing TZ</th></tr></thead>
              <tbody>${dailyRows}</tbody>
            </table>
          </section>
          <section class="section">
            <table>
              <thead><tr><th>Run ID</th><th>Rows</th><th>Issues</th></tr></thead>
              <tbody>${runLogRows}</tbody>
            </table>
          </section>
        </div>
      </article>`;
    }

    async function load() {
      const res = await fetch("/api/status");
      if (!res.ok) throw new Error(await res.text());
      render(await res.json());
    }

    document.getElementById("refresh").addEventListener("click", () => load().catch(err => alert(err.message)));
    document.getElementById("json").addEventListener("click", () => {
      const blob = new Blob([JSON.stringify(lastData, null, 2)], {type: "application/json"});
      window.open(URL.createObjectURL(blob), "_blank");
    });
    load().catch(err => {
      document.getElementById("movies").innerHTML = `<div class="empty">${esc(err.message)}</div>`;
    });
    setInterval(() => load().catch(console.error), 60000);
  </script>
</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "BoxOfficeDashboard/1.0"

    def do_HEAD(self):  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.write_response(200, HTML_PAGE, "text/html; charset=utf-8")
            return
        if parsed.path == "/api/status":
            qs = parse_qs(parsed.query)
            auto_pull = getattr(self.server, "auto_pull", False)
            if "pull" in qs:
                auto_pull = qs.get("pull", ["1"])[0] not in ("0", "false", "no")
            data = build_dashboard_data(auto_pull=auto_pull)
            self.write_response(200, json.dumps(data), "application/json")
            return
        self.write_response(404, "Not found", "text/plain; charset=utf-8")

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def write_response(self, code, body, content_type):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-auto-pull", action="store_true")
    args = parser.parse_args()

    os.chdir(BASE_DIR)
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    server.auto_pull = not args.no_auto_pull
    print(f"Dashboard: http://{args.host}:{args.port}")
    print(f"Auto-pull: {'off' if args.no_auto_pull else 'on'}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard.")


if __name__ == "__main__":
    main()
