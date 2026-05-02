# Theatre Cohorts

The scraper now has two theatre cohorts:

- `core`: the existing model sample in `data/theatres-all.json`.
- `expansion`: best-effort extra AMC theatres in `data/theatres-expansion.json`.

The collection pipeline loads both cohorts by default, but Phase 1 and Phase 2
run core theatres before expansion theatres. If a runtime deadline is close,
expansion work is the first work left uncollected.

Prediction, calibration, and trading include `core,expansion` by default. The
prediction model normalizes the observed AMC sample back to the calibration
reference count for the active cohort key before converting to domestic gross.
That keeps `core` historical replays on the old 376-theatre denominator while
letting the expanded model use the stable 425-theatre denominator instead of
artificially shrinking current preview data.

To force an apples-to-apples core-only replay:

```bash
THEATRE_MODEL_COHORTS=core python3 predict.py
```

`--include-expansion` remains accepted for older runbooks, but expansion is
already part of the default model path:

```bash
THEATRE_MODEL_COHORTS=core,expansion python3 predict.py
python3 predict.py --include-expansion
```

For a different theatre universe, set
`calibration_factors.reference_amc_theatres_by_cohort` in
`data/calibration.json` to the stable reference sample size for that cohort key.
The legacy `reference_amc_theatres` value remains the `core` fallback only. If a
cohort-specific reference is absent, `predict.py` learns from matching
historical calibration entries and falls back to the current observed sample
only when no matching history exists.

The official `PREDICTION` is seat-first:

- direct seat-count model estimates the weekend from observed AMC occupancy
- seat+comp model uses the same seat evidence with historical day-share comps
- the seat-primary model blends those two seat-driven views
- Polymarket intervals are no-vig normalized and capped as a secondary prior

This keeps actual collected seat data as the main driver while still using
market pricing and historical comps as calibration signals.

The collector preserves every AMC showtime ID it finds. The model still uses
the historical theatre/format/showtime identity by default; to research
same-time duplicate screens separately, opt in with:

```bash
THEATRE_MODEL_SHOWTIME_IDENTITY=url python3 predict.py --movie Michael
```

To temporarily collect only the core cohort:

```bash
THEATRE_COLLECTION_COHORTS=core python3 scraper.py --collect-links PT
THEATRE_COLLECTION_COHORTS=core python3 scraper.py --ensure-links PT
```
