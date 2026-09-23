# Further accuracy work — v31

September 19, 2026. Applied locally to the Theatre 2.0 model after v30. No publication or deployment.

This round found additional calculation and input-consistency defects. It does **not** establish a major general improvement in predictive accuracy.

## Fixed

1. **Rejected seat days could re-enter the forecast.** The regression layer excluded days with poor effective coverage, but later empirical recalculation, snapshot anchoring and stage selection reused those same day records. Rejected days now remain diagnostic records and cannot supply those downstream observations. When neither usable seat data nor a sufficiently supported reservation forecast remains, the model declines to forecast and explains why.
2. **Daily ranges could miss their own central estimate.** Calibration moved the midpoint while leaving the range on its old scale. Ranges now retain both the original and rescaled uncertainty, with the midpoint inside them. Across 136 replay checkpoints this removed **58 invalid daily ranges**; none remain in the updated replay.
3. **Reported actuals are protected.** A fitted calibration cannot rewrite an explicitly reported daily gross. A forecast cannot fall below revenue already reported. If all four model days are reported, the headline is their total, without review or regression adjustments. Provisional source status is retained; a reported total can still be revised by its source.
4. **Dashboard and command-line inputs now match.** The dashboard now explicitly passes reviews, cross-chain measurements, reported grosses and showtime profiles for the selected weekend, with consistent film-name matching. It also explains unavailable forecasts and lists excluded days.

## What the evaluation shows

The fair comparison uses only forecasts both versions produce, keeping cases whose stage changed. Lower error is better.

| Same forecast cases | Forecasts / films | v30 mean absolute percentage error | v31 error |
|---|---:|---:|---:|
| Development | 39 / 14 | 23.23% | 23.15% |
| Later weekends | 21 / 9 | 28.13% | 27.05% |
| Combined | 60 / 23 | 24.95% | 24.52% |

The later-film bootstrap's 95% improvement interval is **−0.10 to +2.61 percentage points**. It includes no improvement. Combined film-balanced error slightly worsens, 24.72% to 24.88%, so the result is not a broad statistical victory. The changes are justified by consistent evidence handling and arithmetic correctness.

The model now produces 91 of the 136 reconstructed checkpoints, versus 104 previously. Among the 65 previously eligible regular forecasts, it declines five: The Breadwinner on Friday, Disclosure Day on Saturday, and Hope on Friday/Saturday/Sunday. One retained development forecast is reclassified as reservation-only. **Do not compare the old 31.56% later error on 24 forecasts directly with 27.05% on 21 and call the difference an accuracy gain.** On those same 21 cases the difference is 28.13% to 27.05%.

These are reused historical periods, not new untouched tests. Replays enforce capture cutoffs, earlier-film training and revision availability. Current reference metadata and prices remain a limitation. Reviews, social signals and cross-chain measurements are omitted equally from both versions in this replay; dashboard input parity is a separate integration check.

## Further models tested and rejected

Six sequential corrections were tested using only earlier films' available outcomes, with equal total training weight per film. Every candidate was worse on later regular forecasts, so none was enabled.

| Candidate | Development error | Later error |
|---|---:|---:|
| v30 reference | 23.84% | 31.56% |
| Same-stage historical bias | 24.01% | 32.88% |
| Same-audience historical bias | 23.84% | 32.11% |
| Stage-based shrinkage regression | 23.97% | 33.55% |
| Size and coverage regression | 24.01% | 36.94% |
| Audience, size and coverage regression | 23.52% | 35.90% |
| More strongly restrained audience regression | 23.63% | 34.30% |

These candidates were compared to the frozen v30 replay, before this round's integrity fixes. Small development gains failed to carry into the later period. They should not be enabled by tuning further against the same later movies.

## Validation and deliverables

**808 tests pass across 47 isolated modules**, including ten new tests for evidence rejection, reported-actual protection, range containment and dashboard inputs. Existing small-sample normalization fixtures now isolate normalization from the production admission threshold; separate end-to-end tests enforce that threshold. The stale Resident Evil theatre-count assertion was updated to the verified 3,684 value already in v30 data.

Resident Evil's current command-line forecast remains **$59.14M**, range **$43.77M–$69.47M**. This is an estimate, not a settled result. The dashboard now receives the same current inputs: its displayed estimate changed from $58.6M to $59.1M and matches the command-line result.

The companion CSV retains all 136 checkpoints, including abstentions. The validation JSON includes paired results, forecast coverage, range defects, rejected experiments and test counts. The incremental patch is based on v30 checkpoint `1f584f2`.

Reproduce the research from `box-office-tracker`:

```
python scripts/accuracy_backtest.py --output accuracy-replays.json
python scripts/residual_correction_backtest.py --replays accuracy-replays.json --output experiments.json
```

The six reported research comparisons use the saved v30 replay; running the second command against a new v31 replay evaluates a different baseline. More reliable independent future films are still needed before claiming a substantial accuracy gain.
