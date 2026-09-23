# Box-office model v30 — accuracy work

Applied locally on September 19, 2026. The attached spreadsheet is an export; the executable prediction model and its data were updated in the Theatre 2.0 project. No publication or deployment was performed.

**The model is better protected against bad data, but this round does not establish another substantial accuracy gain.** Across 65 comparable forecasts, mean absolute percentage error fell from 27.21% to 26.69%. On the later 24 forecasts it stayed essentially flat, 31.53% to 31.56%. Experiments that worsened full-forecast performance remain disabled.

## Changes now active

- Corrected nine historical records against reported grosses, preserved their prior versions and verification dates, and refreshed calibration. Separately reported previews are subtracted from Friday so they are not counted twice. New corrections cannot silently enter an earlier replay's training set.
- Fixed duplicate metadata erasing populated fields, an incorrect release date, missing film classifications, and several release-type/theatre-count fields. A preview-derived AMC-share override is usable only after its dated availability.
- Improved source URL resolution, title/entity matching and wrong-year fallback. Unknown preview splits remain excluded instead of estimated from seats. Non-Friday openings with regular Thursday revenue cannot teach the model a false preview pattern.
- Added provisional forecasts for films with presale data but no observed-day seat data. They require all four days, at least 50% coverage, sufficient calibration support and at least eight admissible prior films. They receive a conservative range of at least 0.5–2.5 times the central estimate. This range is a safeguard, not a demonstrated 90% interval.
- Added forecast-window checks. A Thursday–Sunday subtotal cannot generate market-comparison signals against a Wednesday–Sunday or Friday–Monday settlement target. The dashboard and forecast log expose the mismatch.
- Added read-only data audits and repeatable comparisons using capture-time cutoffs. Unsupported or missing forecasts remain visible in the exported evaluation.
- Added Resident Evil's reported preview and Friday numbers as provisional current inputs, with preview subtraction. No unreported weekend outcome was invented.

## Measured results

Lower error is better. MAPE is the average absolute percentage error; multiple checkpoints for one film are correlated.

| Comparable regular forecasts | Forecasts / films | v29 error | v30 error |
|---|---:|---:|---:|
| Development, before August | 41 / 14 | 24.67% | 23.84% |
| Later weekends, August–September | 24 / 10 | 31.53% | 31.56% |
| Combined | 65 / 24 | 27.21% | 26.69% |

The film-level bootstrap's 95% interval for the combined improvement is **−0.12 to +1.55 percentage points**, which includes no improvement. This does not establish a statistically reliable gain. Median absolute error fell from 26.49% to 22.85% across the combined set.

There are 136 reconstructed checkpoints covering 34 films, including missing forecasts. Each replay uses only captures available by its Thursday/Friday/Saturday/Sunday noon Eastern cutoff and training films from earlier weekends. Actual revisions and publication dates are respected. Metadata and ticket prices remain current reference inputs, so these are reconstructions, not historical live forecasts. The later period has already informed earlier work and is not an untouched holdout. All headline v29/v30 comparisons use the same corrected outcome totals.

New eligible presale-only forecasts have 31.73% error on 11 development films and 29.06% on just three later films. The sample is too small to establish reliable accuracy or interval coverage. Regular-forecast ranges cover 51.22% of development outcomes and 91.67% of later outcomes; they should not be described as universally calibrated 90% intervals.

## Experiment not activated

Theatre-specific revenue weights account for the fact that sampled theatres differ in size. They improved a component test: later-film sample expansion error fell from 22.97% to 5.63%. However, the full forecast did not improve: regular later forecasts were unchanged and later presale error worsened from 29.06% to 29.59%. **The production setting remains off.** Research data and the replay script are retained for future verification.

## Corrected outcome records

Totals below are the model's Thursday–Sunday target, with previews counted once. Each linked source was checked September 19, 2026. Previous values are retained in calibration history.

| Film / source | Corrected model total | Treatment |
|---|---:|---|
| [Michael](https://www.the-numbers.com/movie/Michael-(2026)) | $97.207M | Independent reported split; previews separated from Friday. |
| [The Sheep Detectives](https://www.the-numbers.com/movie/Sheep-Detectives-The-(2026)) | $15.088M | Independent reported split; previews separated from Friday. |
| [In the Grey](https://www.the-numbers.com/movie/In-the-Grey-(2026)) | $2.927M | Unknown previews remain excluded from daily fitting. |
| [The Mandalorian and Grogu](https://www.the-numbers.com/movie/Star-Wars-The-Mandalorian-and-Grogu-(2026)) | $81.670M | Independent reported split; previews separated from Friday. |
| [Toy Story 5](https://www.the-numbers.com/movie/Toy-Story-5-(2026)) | $159.678M | Independent reported split; previews separated from Friday. |
| [Minions & Monsters](https://www.the-numbers.com/movie/Minions-and-Monsters-(2026)) | $47.814M | Thu–Sun subtotal only; Wednesday opener excluded from standard calibration. |
| [Young Washington](https://www.the-numbers.com/movie/Young-Washington-(2026)) | $19.372M | Unknown previews remain excluded from daily fitting. |
| [Mutiny](https://www.the-numbers.com/movie/Mutiny-(2026-United-Kingdom)) | $7.710M | Independent reported split; previews separated from Friday. |
| [Runner](https://www.the-numbers.com/movie/Runner-(2026-Dir-Scott-Waugh)) | $6.462M | Unknown previews remain excluded from daily fitting. |

[The Devil Wears Prada 2's official release date](https://www.20thcenturystudios.com/movies/the-devil-wears-prada-2) is May 1, not the September date previously in metadata. Additional metadata references: [Spider-Man](https://www.the-numbers.com/movie/Spider-Man-Brand-New-Day-(2026)), [The Breadwinner](https://www.the-numbers.com/movie/Breadwinner-The-(2026)), and [Moana](https://www.the-numbers.com/movie/Moana-(2026)).

The [Minions market](https://polymarket.com/event/minions-monsters-opening-weekend-box-office/will-minions-monsters-opening-weekend-box-office-be-between-68m-and-77m) covers July 1–5; its Wednesday–Sunday reported total is $62.044900M, while this model's Thursday–Sunday subtotal is $47.813790M. The [Mandalorian market](https://polymarket.com/event/the-mandalorian-and-grogu-4-day-opening-weekend-box-office) includes Monday, May 25. These missing-day forecasts have not been implemented; comparisons are blocked until targets match.

## Current example

With [Resident Evil's reported grosses](https://www.the-numbers.com/movie/Resident-Evil-(2026)), the local after-Friday forecast is **$59.14M**, with a model range of **$43.77M–$69.47M**. Inputs are $8.8M previews plus $17.5M pure Friday ($26.3M reported Friday including previews, less $8.8M). These inputs remain marked provisional. This is a live estimate, not a validated outcome or guaranteed range.

## Verification and remaining limits

**798 tests pass across 46 separately run test modules.** Changed Python files compile. The current forecast runs successfully. The audit finds 30 complete independent daily splits among 34 films, two flagged data outages, three unknown preview splits and one nonstandard Thursday that is excluded from preview fitting. It finds no remaining duplicate metadata, release-week mismatch or independently complete daily-total mismatch.

Source parsing and URL fallback have fixture tests. Direct automated requests to The Numbers returned HTTP 403 in this environment; the manual verification used accessible web pages. The code does not bypass that restriction, and automated source availability is not claimed to be solved.

The largest remaining constraint is data: more independent completed films, consistent capture coverage, trustworthy advance booking trajectories and reliable non-AMC representation. Another algorithm cannot be assumed to solve those gaps. Future changes should be judged on newly logged forecasts whose outcomes were not used to design them.

Reproduction from `box-office-tracker`:

```
python scripts/audit_prediction_data.py --output audit.json
python scripts/accuracy_backtest.py --output accuracy-replays.json
python predict.py --movie "Resident Evil"
```

The evaluation CSV includes every checkpoint, forecast status, eligibility, stage, range, target window and available v29 prediction. Validation JSON contains the metric summaries, audit and original/corrected data values. The v30 patch is incremental from checkpoint `ced9620`; earlier v28/v29 work is retained.
