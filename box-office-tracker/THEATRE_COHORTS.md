# Theatre Cohorts

The scraper now has two theatre cohorts:

- `core`: the existing model sample in `data/theatres-all.json`.
- `expansion`: best-effort extra AMC theatres in `data/theatres-expansion.json`.

The collection pipeline loads both cohorts by default, but Phase 1 and Phase 2
run core theatres before expansion theatres. If a runtime deadline is close,
expansion work is the first work left uncollected.

Prediction, calibration, and trading stay core-only by default. Expansion rows
are written to `seat-counts.csv` and tagged in `notes` with
`cohort=expansion`, but `predict.py` excludes known expansion theatre names
unless explicitly enabled.

To compare the expanded sample without changing the default model path:

```bash
THEATRE_MODEL_COHORTS=core,expansion python3 predict.py
python3 predict.py --include-expansion
```

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
