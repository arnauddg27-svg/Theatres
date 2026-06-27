#!/usr/bin/env python3
"""Does adding GENRE (or franchise/audience type) to the Thursday->weekend
regression improve out-of-sample accuracy, or just fit noise?

The Thursday->weekend multiple splits hard by genre (superhero ~6.5, comedy
~11.4), so genre clearly matters descriptively. The question for the model is
whether a one-hot genre term cuts leave-one-out error on log(opening) beyond the
Thursday preview alone — i.e. whether it GENERALIZES on 217 comps.

  baseline : log(opening) ~ log(thursday)
  +genre   : log(opening) ~ log(thursday) + onehot(genre)
  (also franchise_type, audience_type)

Read-only.
"""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predict as P  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from validate_wiki_signal import ols, predict_one  # noqa: E402

COMPS = os.path.join(P.DATA_DIR, "historical-comps.csv")


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_rows():
    rows = []
    for r in csv.DictReader(open(COMPS)):
        thu = _f(r.get("thursday_preview_m"))
        ow = _f(r.get("opening_weekend_m"))
        if thu and thu > 0 and ow and ow > 0:
            rows.append({
                "log_thu": math.log(thu), "log_open": math.log(ow), "open": ow,
                "genre": (r.get("genre") or "?").strip(),
                "franchise_type": (r.get("franchise_type") or "?").strip(),
                "audience_type": (r.get("audience_type") or "?").strip(),
            })
    return rows


def onehot_levels(rows, field, min_n=6):
    """Levels with >= min_n examples (rare levels collapse into the reference)."""
    from collections import Counter
    c = Counter(r[field] for r in rows)
    levels = sorted(l for l, n in c.items() if n >= min_n)
    return levels[1:]  # drop one as reference (intercept carries it)


def feat_row(r, fields_levels):
    x = [r["log_thu"]]
    for field, levels in fields_levels:
        x.extend(1.0 if r[field] == lv else 0.0 for lv in levels)
    return x


def loo_mae(rows, fields_levels):
    errs = []
    for i in range(len(rows)):
        train = [r for j, r in enumerate(rows) if j != i]
        X = [feat_row(r, fields_levels) for r in train]
        y = [r["log_open"] for r in train]
        b = ols(X, y)
        pred = math.exp(predict_one(b, feat_row(rows[i], fields_levels)))
        errs.append(abs(pred - rows[i]["open"]) / rows[i]["open"] * 100.0)
    errs.sort()
    n = len(errs)
    return sum(errs) / n, (errs[n // 2] if n % 2 else (errs[n // 2 - 1] + errs[n // 2]) / 2)


def main():
    rows = load_rows()
    print(f"comps with Thursday + opening: {len(rows)}\n")
    configs = [
        ("thursday only", []),
        ("thursday + genre", [("genre", onehot_levels(rows, "genre"))]),
        ("thursday + franchise_type", [("franchise_type", onehot_levels(rows, "franchise_type"))]),
        ("thursday + audience_type", [("audience_type", onehot_levels(rows, "audience_type"))]),
        ("thursday + genre + franchise", [("genre", onehot_levels(rows, "genre")),
                                          ("franchise_type", onehot_levels(rows, "franchise_type"))]),
    ]
    base = None
    print("-- leave-one-out opening-weekend MAE --")
    for label, fl in configs:
        mae, med = loo_mae(rows, fl)
        if base is None:
            base = mae
        tag = "" if label == "thursday only" else f"  ({base - mae:+.2f} pts vs baseline)"
        print(f"  {label:30}: MAE {mae:5.2f}%   median {med:5.2f}%{tag}")
    print("\n(>+1 pt = genre generalizes and is worth adding; ~0 or negative = in-sample only)")


if __name__ == "__main__":
    main()
