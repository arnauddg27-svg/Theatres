"""AMC CLASSIC exclusion with a reserved-seating allow-list.

Most AMC CLASSIC (ex-Carmike) locations are general admission: no seat map, so
nothing to count, and the pipeline has excluded the brand since 2026-05-31.
A probe on 2026-09-26 found 7 of 49 that DO sell reserved seats; those are
collected like any other AMC theatre. data/amc-classic-reserved.json is
rewritten by scripts/probe_amc_classic.py.
"""
import json
import os

ALLOWLIST_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "amc-classic-reserved.json")
_CACHE = {}


def reserved_names(path=None):
    path = path or ALLOWLIST_JSON
    if path not in _CACHE:
        try:
            with open(path) as f:
                _CACHE[path] = {n.strip().upper() for n in json.load(f).get("reserved", [])}
        except (OSError, ValueError):
            _CACHE[path] = set()
    return _CACHE[path]


def is_classic(name="", slug=""):
    n = (name or "").strip().lower()
    s = (slug or "").strip().lower()
    return n.startswith("amc classic ") or s.startswith("amc-classic-")


def excluded(name="", slug="", path=None):
    """True for an AMC CLASSIC theatre that is NOT on the reserved-seating list."""
    return is_classic(name, slug) and (name or "").strip().upper() not in reserved_names(path)
