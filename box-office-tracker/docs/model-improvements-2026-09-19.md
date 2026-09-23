# Box-office model update — September 19, 2026

Updated the local model to `seat-regression-v28-independent-actuals`.

## Changes

- **Clean training labels:** exclude daily grosses identified as seat/model estimates. Preserve independently reported days and original records. Stop inventing missing daily grosses from the model's own snapshot proportions.
- **Consistent day weights:** learn normal weekend proportions from complete reported splits, excluding flagged holiday patterns, outages, and combined Thursday/Friday figures. Refresh both prediction paths from the same eligible history.
- **Sellout correction:** fix training to use the sellout feature that prediction already expected.
- **Forecast tracking:** retain the last logged forecast at or before noon Eastern on Tuesday, Thursday, Friday, Saturday, and Sunday. Missing or more-than-24-hour-old forecasts remain missing; later runs cannot substitute for earlier checkpoints. Grade each available checkpoint when results are recorded.
- **Uncertainty and evaluation:** prevent collapsed or negative historical-error bands; exclude later results when building dated historical bands. Add a chronological calibration test that trains only on earlier weekends whose actuals were already recorded.

## Validation

All **762 tests across 44 modules passed**, running modules in separate processes. This includes 18 new tests for the changes.

The same chronological calibration comparison was run against the original code at `fcf5873` and the updated code:

| Measure | Before | After |
|---|---:|---:|
| Films scored | 18 | 18 |
| Mean absolute percentage error | 26.35% | 26.24% |
| Median absolute percentage error | 17.32% | 17.63% |
| Mean signed error | +7.07% | +7.31% |
| Mean absolute dollar error | $6.342M | $6.276M |
| Actual inside prediction interval | 16/18 | 16/18 |
| Mean interval width / prediction | 105.98% | 125.56% |

The average-error gain is small, median error is slightly worse, and intervals are wider. This does **not** establish improved live forecasting accuracy.

Of 34 historical films, 13 lack the required eight earlier training films and three lack admissible seat inputs. All are retained in the evaluation report. The comparison evaluates the calibration layer on stored raw features, which may have been reconstructed later; it does not independently validate live headlines, presale adjustments, reviews, or Friday anchors. The new fixed-time checkpoints support prospective evaluation.

Reproduce the calibration report from `box-office-tracker`:

```sh
python scripts/calibration_backtest.py --output calibration-evaluation.json
```

Changes are local and have not been published. The supplied Excel export and historical data files are unchanged.
