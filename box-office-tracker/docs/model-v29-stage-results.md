# Stage-aware box-office model — September 19, 2026

Implemented `seat-regression-v29-stage-daily-evidence` in the local Theatre project. The strongest measured benefit is in forecasts made after Friday.

## What changed

The model now uses the combined observed-day and reservation-day estimate when reservation coverage and calibration support are sufficient. Previously, a generic Friday-to-weekend multiplier could pull that estimate back toward an average opening pattern. Partial reservation coverage can now contribute even when it does not cover every missing day.

Sparse or unsupported reservations and completed weekends retain the existing model. The previous forecast's uncertainty range remains a minimum. Reviews are applied once. Each future live log records both the old and new forecast from the same run; fixed-time checkpoint grading compares their errors once actual results are available. Existing log rows and custom columns are preserved when comparison columns are added.

## Historical results

The stage rule was checked on April–July development data before being evaluated on August–September releases. At least eight earlier historical records were required for the principal comparison; flagged outages were excluded from that comparison and included in a separate all-data result.

| Evaluation | Sample | Previous average error | Updated average error |
|---|---|---:|---:|
| Development | 41 forecasts, 14 films | 26.86% | 24.63% |
| Later weekends | 24 forecasts, 10 films, 5 weekends | 34.38% | 31.53% |
| Later weekends, Saturday noon | 9 films | 39.68% | 32.67% |
| Later weekends, Sunday noon | 10 films | 36.04% | 35.52% |
| All available, including outages and early history | 89 forecasts, 33 films | 29.89% | 28.54% |

Later-weekend median error fell from **33.65% to 31.10%**. Giving each film equal weight, average error fell from **33.79% to 30.70%**. Friday-noon results were unchanged.

These are reconstructed forecasts, not verified live results. Capture timestamps are limited to noon Eastern at each checkpoint. Training actuals must predate the release being predicted; date-only side inputs must predate the checkpoint day. Current corrected metadata and historical ticket-price references are retained. Reviews, market odds, social signals, and cross-chain inputs were disabled consistently for this controlled comparison. Historical comparison films all predate 2026.

The later-weekend sample is small and several checkpoints belong to the same film. A film-level bootstrap puts the 95% improvement interval at **−1.05 to +9.69 percentage points**, so a durable accuracy gain is not yet established. Some films get worse. The all-data improvement interval also includes zero. These results are not directly comparable with the earlier 26.24% calibration-only result, which used different inputs and prediction stages.

47 of 136 film/checkpoint combinations lacked an existing forecast, including every Thursday-noon checkpoint. This update does not claim accuracy for those missing forecasts or introduce a pure-presale forecast without regular seat data.

## Alternatives tested and rejected

- **Extra missing-coverage expansion:** multiplying by inverse square-root coverage improved development error to 25.20%, but later-weekend error rose to **59.01%**. It is not applied.
- **Historical-film prior for coverage gaps:** development error worsened to **29.35%**. It is not applied.
- **Residual regression using stage, coverage and pickup features:** the tested shrinkage variants did not beat the development baseline. They are not applied.
- **Learned presale growth:** matched the same shows' earlier reservations to later seat counts; learned lead-time multipliers using earlier films only. Later-film seat-volume weighted error was **16.98% before and after**, while average film/bucket percentage error worsened from **14.51% to 15.01%**. This is a seat-count experiment, not a box-office accuracy result. The candidate remains a research script and is not applied to forecasts.

## Validation and reproduction

**775 tests across 45 modules passed**, including 13 new stage, timing, interval and logging tests. Test modules ran in separate processes; affected modules were rerun after the final changes. Historical source data and the supplied Excel export are unchanged. The change has not been published.

From `box-office-tracker`, using its Python environment:

```sh
python scripts/stage_backtest.py --output stage-baseline.json
python scripts/stage_backtest.py --evaluate stage-baseline.json --output stage-results.json
python scripts/reservation_growth_backtest.py --pairs reservation-pairs.json --output reservation-growth-results.json
```

The first command explicitly disables the new stage selector while generating the baseline. The second applies the production selector to those identical inputs. Reports retain per-film results, missing forecasts, and the broader all-data comparison.
