# Plan: Requesting AMC Theatres API Access

## The Opportunity

AMC has an official Developer Portal at **https://developers.amctheatres.com/** with documented REST APIs covering showtimes, theatre info, seat maps, and more. Getting API access would replace our current browser-based scraping approach — making the system faster, more reliable, and scalable.

## What the API Offers

AMC's documented endpoints include exactly what we need:

- **Showtimes** — query by theatre and date, with format filtering
- **Theatre information** — location, attributes, auditorium details
- **Seat maps and selection** — seating layout with availability status
- **Embargoed Showtimes** — future-dated online ticket availability

Authentication uses an `X-AMC-Vendor-Key` header — a single API key per vendor.

## Registration Steps

1. Go to https://developers.amctheatres.com/
2. Register as a developer (create account)
3. Submit a "New Vendor Request" describing your use case
4. Wait for API key activation (~10 days based on reports)
5. Start making authenticated REST calls

## What to Say in the Request

Frame it as a research/analytics project, not a competitor or reseller:

> **Project:** Box office analytics research tool
> **Use case:** Querying showtime schedules and seat availability data across select AMC locations to build statistical models correlating real-time attendance patterns with public prediction market data. Read-only access only — no ticket purchasing, no order creation, no customer data needed.
> **Volume:** ~60 API calls per run, 3 runs per week (Thu/Fri/Sat evenings). Total: ~180 calls/week.
> **Theatres:** 10 specific AMC locations across ET/CT/PT timezone groups.

## What Changes with API Access

| Current (Browser Scraping) | With API Access |
|---|---|
| ~25 sec per theatre (navigate + wait + JS) | ~1 sec per theatre (single HTTP call) |
| Requires Chrome browser open | Runs headlessly via Python script |
| Fragile — breaks if AMC changes HTML | Stable — versioned API contract |
| ~5 min for all 10 theatres | ~15 sec for all 10 theatres |
| Can't run in background | Fully automated, no UI needed |

## Fallback: Third-Party APIs

If AMC denies direct access, alternatives exist:

- **ShowtimeAPI.com** (https://showtimeapi.com/chain/amc) — aggregates AMC showtime data
- **Gracenote/TMS API** (https://developer.tmsapi.com/) — movies playing in local theatres
- **Fandango Developer API** (https://developer.fandango.com/) — showtimes + ticketing data

Note: These likely cover showtimes but may not include seat-level availability, which is the core of our occupancy tracking.

## Recommended Next Steps

1. **Now:** Register at https://developers.amctheatres.com/ and submit the vendor request
2. **While waiting (~10 days):** Continue using the browser-based system (already working)
3. **On approval:** Rewrite the scraper as a simple Python script using `requests` — the scheduled tasks would call the script instead of Chrome
4. **If denied:** Evaluate ShowtimeAPI.com for showtimes + keep browser-based seat map counting as a hybrid approach
