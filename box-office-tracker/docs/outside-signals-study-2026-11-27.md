# Outside-signals study — 2026-11-27

Question: with AMC's seat maps blocked since 2026-11-19, what public data predicts an
opening weekend, and does it combine with the seat data we still collect?

"Miss" below is the mean absolute percentage error against the final 3-day opening
(Friday–Sunday, Thursday previews included). Every signal is measured as of a cutoff
before the result is known.

## What was tested

| Signal | Films | Result |
|---|---|---|
| Polymarket implied median, Thursday 4pm ET | 101 (2025–26) | 14.2% miss (median 10.1%). Wednesday 4pm 16.6%, Friday noon 9.5%, Saturday noon 7.5%. Films under $10M: 25%; over $30M: 8%. |
| Box Office Theory published forecast, as of Thursday | 85 | 18.8% miss (2026 only: 21.2%, n=56). Wednesday 20.8%. |
| Variety / Deadline / THR week-of numbers | 44 | 24% miss; Deadline runs ~48% high on small films. Prose numbers, not machine-readable. |
| Our seat model, pre-sales call | 23 | 34% miss. |
| Per-chain pre-sales at Thursday 4pm (reserved seats per theatre + theatre count) | 17–46 | AMC 30%, Regal 33%, Harkins 28%, Cinemark 55%, Regal+Cinemark 34%. |
| Wikipedia views, Google Trends, YouTube trailer views, RT score, theatre count | 17–101 | Each tracks the opening (correlation 0.45–0.63) but none explains the market's or the trade forecast's remaining error (partial correlation −0.14 to +0.21, none significant). Adding Wikipedia to the market: 14.7% → 14.9%. |
| Kalshi | — | No opening-weekend box-office markets exist. |

Not obtainable: Boxoffice Pro and r/boxoffice refuse automated reads; Google Trends
rate-limits after ~34 films; YouTube exposes no view history (current counts include
post-release views).

## Does anything add to the market?

Matched-time comparison on 2026 films (our latest logged call before the time shown):

| Time (ET) | Ours | Market | 80/20 market/ours | n |
|---|---|---|---|---|
| Wed 4pm | 36% | 24% | 23% | 9 |
| Thu 4pm | 36% | 17% | 17% | 20 |
| Fri noon | 21% | 7.5% | 9% | 21 |
| Sat noon | 18.5% | 9% | 10% | 22 |

Before Saturday is reported nothing we have improves on the market: not our model, not
the trade forecast (ridge market+trade 13.3% vs market 13.0%, n=78), not seat counts
(market + AMC seats 14.5% vs 13.9%, n=40), not attention signals. Once Saturday is
reported our model wins (2.5% vs 8%, n=10); the market's bracket width is its floor.

Weak leads, not acted on: the market's error correlates +0.27 with (trade − market)
and +0.26 with log volume (n=78–101); YouTube trailer views correlate +0.56 with the
trade forecast's error (n=20, leak risk).

## When there is no market

Trade forecast and our model make different errors, so mixing them helps
(log-space, weight on ours):

| Stage | Ours | Trade | Mix | n |
|---|---|---|---|---|
| Pre-sales | 34% | 23% | 19% (0.25–0.5) | 23 |
| After previews | 24% | 23% | 16–17% (0.5) | 24 |
| After Friday | 11–17% | 23% | 10–15% (0.75) | 24 |

## More sources and the literature

Second sweep (2026 films; correlation of each signal with the market's / the trade
forecast's remaining error after removing its level):

| Signal | n | vs market | vs trade | Notes |
|---|---|---|---|---|
| Greenlight (ex-Quorum) theatrical intent % | 16–17 | +0.17 | +0.40 | Strongest raw signal (ρ 0.87 with the opening) but published as table screenshots, about one film a week, none since 2026-10-20. |
| TMDB daily-export popularity | 34–36 | +0.09 | +0.28 | No key, scriptable; files kept ~120 days. |
| Bluesky posts, prior 7 days | 52–56 | −0.13 | +0.30 | Exact history; noisy on ambiguous titles. |
| Wikipedia edits, prior 30 days | 52–55 | +0.15 | +0.19 | |
| RT critic review count, Letterboxd rating count (Wayback) | 24–39 | −0.16 / −0.08 | +0.15 / +0.04 | |

None explains the market's error. A few lean the right way against the trade forecast
(films without a market), on samples too small to build on.

Blocked or login-gated: IMDb MOVIEmeter, Trakt, Letterboxd watchlists, TikTok,
Instagram/X, Spotify, GDELT (429). No public metric: Fandango, Atom, EntTelligence,
Comscore.

Literature: trade forecasts miss by a median 19.9% and are no better on opening day
than three weeks out (Follows, 1,184 films); a forward-tested public-signal model
misses by 32% a week out (Meiler, 2025 holdout); search adds nothing once a prediction
market is in the model (Goel et al.) — the same result as here. The famous high
figures (Asur & Huberman R² 0.97, Google 94%) are in-sample fits. No published study
measures pre-sale ticketing against openings.

## Shipped

- `scripts/fetch_trade_forecasts.py` → `data/trade-forecasts.csv` (weekly forecast,
  timestamped, fetched every finalize; history backfilled to 2024-12).
- `scripts/ensemble_forecast.py` → `data/ensemble-log.csv`: market when one exists,
  trade + model when not, shifting to the model after Friday. `--report` grades it.
  On the 24 graded films, with each stage's weight picked on the other weekends:
  pre-sales 34% → 17–22%, after-previews 24% → 12–15%, after-Friday 10.7% → 8.6%,
  after-Saturday unchanged. predict.py's headline is untouched.
- Holiday weekends (midweek openers) are left to the model: the market and the trade
  forecast quote 3-day and 5-day windows, the model Thursday–Sunday.

## AMC theatre panel (tested, not shipped)

A small panel of AMC theatres chosen by correlation with past openings carries the
fleet's signal (Thursday pre-sales, 46 films, panel picked without the test film):
all ~320 theatres 33%, top 10 29%, top 25 31%; random panels 51–55% and the biggest
theatres 52–79% in a walk-forward test.

Under the Fandango bridge's budget (~60 reads per film per day): today's design
(biggest theatres, one showing each) 49%, or 40% if scaled by each theatre's showing
count; 15 panel theatres × 4 showings, scaled by showing count, 31%.

Top 15 (all readable through the bridge): Hawthorn 12, DINE-IN Holly Springs 9,
Huntington Square 12, Woodlands Square 20, Ontario Mills 30, DINE-IN Shops at
Riverside 9, Marquis 16, Woodhaven 10, Thousand Oaks 14, Rio Cinemas 18, Edinburg 18,
Town Square 18, Gulf Pointe 30, Ridgefield Park 12, Highlands Ranch 24.

Not shipped because predict.py's AMC snapshot layer is scaled for the bridge's current
theatre set; a 15-theatre panel would fall under its coverage floors. It needs its own
estimator, and before opening AMC pre-sales add about one point to the combined
forecast for films without a market.

## Data issues found

- `films`/calibration actuals that disagree with how the market settled (The Numbers
  final): Ramayana $12.45M vs $8–9M, Primetime $19.2M vs $16–19M, The Amazing Digital
  Circus $20.27M vs under $19M (ours is probably the 4-day figure).
- historical-comps `wiki_opening_friday` is wrong for Demon Slayer, One Battle After
  Another, Nobody 2, The Accountant 2, The Monkey, Black Bag, Last Breath, King of Kings.
