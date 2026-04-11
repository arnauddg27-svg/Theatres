# Box Office Tracker — Run Log

This log records each automated run of the seat-map tracking system.

---

## 2026-03-23 (Sunday) — Manual Test Run

**Theatre:** AMC The Grove 14 (Los Angeles, PT)
**Polymarket Movies Found:** 2 (Project Hail Mary, Ready or Not 2: Here I Come)

| Movie | Format | Showtime | Seats | Sold | Occupancy |
|-------|--------|----------|-------|------|-----------|
| Project Hail Mary | IMAX | 7:00pm | 215 | 179 | 83.3% |
| Ready or Not 2: Here I Come | Laser at AMC | 7:00pm | 174 | 123 | 70.7% |

**Notes:** End-to-end test. Polymarket API accessed via gamma-api.polymarket.com. AMC showtimes parsed via fetch+regex, seat maps via page navigation. All systems working.

---

## 2026-03-23 (Sunday) — Full 10-Theatre Run

**Polymarket Movies:** Project Hail Mary (10 markets), Ready or Not 2: Here I Come (6 markets)

| Theatre | City | TZ | Movie | Format | Showtime | Seats | Sold | Occ% |
|---------|------|----|-------|--------|----------|-------|------|------|
| AMC The Grove 14 | Los Angeles | PT | Project Hail Mary | IMAX | 7:00pm | 215 | 179 | 83.3% |
| AMC The Grove 14 | Los Angeles | PT | Ready or Not 2 | Laser | 7:00pm | 174 | 123 | 70.7% |
| AMC Aventura 24 | Aventura FL | ET | Project Hail Mary | Laser | 9:15pm | 181 | 23 | 12.7% |
| AMC Neshaminy 24 | Bensalem PA | ET | — | — | — | — | — | No showtimes |
| AMC Veterans 24 | Tampa FL | ET | Project Hail Mary | IMAX | 9:45pm | 282 | 86 | 30.5% |
| AMC Veterans 24 | Tampa FL | ET | Ready or Not 2 | Dolby | 10:30pm | 227 | 10 | 4.4% |
| AMC DINE-IN Mesquite 30 | Mesquite TX | CT | Project Hail Mary | IMAX | 8:25pm | 447 | 41 | 9.2% |
| AMC DINE-IN Mesquite 30 | Mesquite TX | CT | Ready or Not 2 | XL | 10:00pm | 232 | 5 | 2.2% |
| AMC NorthPark 15 | Dallas TX | CT | Project Hail Mary | XL | 9:00pm | 295 | 21 | 7.1% |
| AMC NorthPark 15 | Dallas TX | CT | Ready or Not 2 | Dolby | 10:00pm | 239 | 17 | 7.1% |
| AMC Gulf Pointe 30 | Houston TX | CT | Project Hail Mary | IMAX | 10:15pm | 326 | 11 | 3.4% |
| AMC Gulf Pointe 30 | Houston TX | CT | Ready or Not 2 | Dolby | 10:45pm | 260 | 2 | 0.8% |
| AMC River East 21 | Chicago IL | CT | Project Hail Mary | Dolby | 10:30pm | 184 | 21 | 11.4% |
| AMC River East 21 | Chicago IL | CT | Ready or Not 2 | PRIME | 9:50pm | 173 | 27 | 15.6% |
| AMC DINE-IN Rosemont 12 | Rosemont IL | CT | Project Hail Mary | Dolby | 8:30pm | 233 | 86 | 36.9% |
| AMC DINE-IN Rosemont 12 | Rosemont IL | CT | Ready or Not 2 | Laser | 10:30pm | 127 | 0 | 0.0% |
| AMC Burbank 16 | Burbank CA | PT | Project Hail Mary | IMAX | 9:30pm | 348 | 203 | 58.3% |
| AMC Burbank 16 | Burbank CA | PT | Ready or Not 2 | Laser | 7:30pm | 401 | 141 | 35.2% |

**Summary:**
- Project Hail Mary avg occupancy: 28.3% (9 theatres). LA theatres strongest (58-83%), late CT/ET shows still filling.
- Ready or Not 2 avg occupancy: 15.6% (8 theatres). Burbank Laser standout at 35.2%, many late shows near 0%.
- Note: This is a Sunday evening run — many showtimes hadn't started yet. Thu/Fri/Sat scheduled runs will capture ~20min-after data.
- Neshaminy 24 had no showtimes for either movie today.

---


## 2026-03-30 08:33 — PT Group

**Polymarket movies tracked:** Bitcoin, Crude Oil (CL), Will the price of Bitcoin be above $62,000 on March 30?, Will the price of Bitcoin be above $60,000 on March 30?, Will Bitcoin dip to $60,000 in March?, Crude Oil (CL), Crude Oil (CL), Crude Oil (CL), Crude Oil (CL), Crude Oil (CL)


**Issues:** AMC The Grove 14: 'Bitcoin' not showing; AMC The Grove 14: 'Crude Oil (CL)' not showing; AMC The Grove 14: 'Will the price of Bitcoin be above $62,000 on March 30?' not showing; AMC The Grove 14: 'Will the price of Bitcoin be above $60,000 on March 30?' not showing; AMC The Grove 14: 'Will Bitcoin dip to $60,000 in March?' not showing; AMC The Grove 14: 'Crude Oil (CL)' not showing; AMC The Grove 14: 'Crude Oil (CL)' not showing; AMC The Grove 14: 'Crude Oil (CL)' not showing; AMC The Grove 14: 'Crude Oil (CL)' not showing; AMC The Grove 14: 'Crude Oil (CL)' not showing; AMC Burbank 16: 'Bitcoin' not showing; AMC Burbank 16: 'Crude Oil (CL)' not showing; AMC Burbank 16: 'Will the price of Bitcoin be above $62,000 on March 30?' not showing; AMC Burbank 16: 'Will the price of Bitcoin be above $60,000 on March 30?' not showing; AMC Burbank 16: 'Will Bitcoin dip to $60,000 in March?' not showing; AMC Burbank 16: 'Crude Oil (CL)' not showing; AMC Burbank 16: 'Crude Oil (CL)' not showing; AMC Burbank 16: 'Crude Oil (CL)' not showing; AMC Burbank 16: 'Crude Oil (CL)' not showing; AMC Burbank 16: 'Crude Oil (CL)' not showing

---

## 2026-03-30 09:16 — PT Group

**Polymarket movies tracked:** They Will Kill You, The Super Mario Galaxy Movie


**Issues:** AMC The Grove 14: 'city'; AMC Century City 15: 'city'; AMC Burbank 16: 'city'; AMC The Americana at Brand 18: 'city'; AMC Santa Monica 7: 'city'; AMC The Regency 20: 'city'; AMC Lakewood Mall 12: 'city'; AMC DINE-IN Marina 6: 'city'; AMC Brentwood 14: 'city'; AMC DINE-IN Fullerton 20: 'city'; AMC Orange 30: 'city'; AMC Tustin 14 @ The District: 'city'; AMC Puente Hills 20: 'city'; AMC Norwalk 20: 'city'; AMC Marina Pacifica 12: 'city'; AMC Montebello 10: 'city'; AMC La Mirada 7: 'city'; AMC Metreon 16: 'city'; AMC Bay Street 16: 'city'; AMC Mercado 20: 'city'; AMC Eastridge 15: 'city'; AMC Saratoga 14: 'city'; AMC NewPark 12: 'city'; AMC Sunnyvale 12: 'city'; AMC Kabuki 8: 'They Will Kill You' not showing; AMC Kabuki 8: 'The Super Mario Galaxy Movie' not showing; AMC Mission Valley 20: 'city'; AMC Fashion Valley 18: 'city'; AMC Palm Promenade 24: 'city'; AMC La Jolla 12: 'city'; AMC Chula Vista 10: 'city'; AMC Otay Ranch 12: 'city'; AMC Plaza Bonita 14: 'city'; AMC Poway 10: 'city'; AMC UTC 14: 'city'; AMC Southcenter 16: 'city'; AMC Pacific Place 11: 'city'; AMC Kent Station 14: 'city'; AMC Alderwood Mall 16: 'city'; AMC Factoria 8: 'city'; AMC Woodinville 12: 'city'; AMC Arizona Center 24: 'city'; AMC Desert Ridge 18: 'city'; AMC Deer Valley 17: 'city'; AMC Ahwatukee 24: 'city'; AMC Westgate 20: 'city'; AMC Westminster Promenade 24: 'city'; AMC Flatiron Crossing 14: 'city'; AMC Highlands Ranch 24: 'city'; AMC DINE-IN Southlands 16: 'city'; AMC Arapahoe Crossing 16: 'city'

---

## 2026-03-30 09:18 — PT Group

**Polymarket movies tracked:** They Will Kill You, The Super Mario Galaxy Movie

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC The Grove 14 | They Will Kill You | Laser at AMC | 5:15pm | 6.3% | -478 min |
| AMC Century City 15 | They Will Kill You | Laser at AMC | 8:05pm | 17.1% | -647 min |
| AMC The Americana at Brand 18 | They Will Kill You | XL at AMC | 7:45pm | 3.8% | -628 min |
| AMC Santa Monica 7 | They Will Kill You | Laser at AMC | 8:00pm | 0% | -643 min |
| AMC The Regency 20 | They Will Kill You | Laser at AMC | 8:40pm | 0% | -683 min |
| AMC Lakewood Mall 12 | They Will Kill You | Laser at AMC | 6:45pm | 9.4% | -568 min |
| AMC DINE-IN Marina 6 | They Will Kill You | Dine-In Delivery to Seat | 7:00pm | 31% | -583 min |
| AMC Brentwood 14 | They Will Kill You | Laser at AMC | 6:30pm | 0.7% | -553 min |
| AMC DINE-IN Fullerton 20 | They Will Kill You | Laser at AMC | 7:10pm | 5.2% | -593 min |
| AMC Orange 30 | They Will Kill You | XL at AMC | 7:10pm | 3% | -593 min |
| AMC Tustin 14 @ The District | They Will Kill You | PRIME at AMC | 6:15pm | 8.4% | -538 min |
| AMC Puente Hills 20 | They Will Kill You | Laser at AMC | 9:00pm | 2.7% | -703 min |
| AMC Norwalk 20 | They Will Kill You | Laser at AMC | 7:45pm | 8.2% | -628 min |
| AMC Marina Pacifica 12 | They Will Kill You | Laser at AMC | 7:05pm | 6.9% | -587 min |
| AMC Montebello 10 | They Will Kill You | Laser at AMC | 7:45pm | 3.8% | -628 min |
| AMC La Mirada 7 | They Will Kill You | Laser at AMC | 7:30pm | 4.2% | -613 min |
| AMC Metreon 16 | They Will Kill You | Open Caption (On-screen Subtitles) | 7:15pm | 12.2% | -598 min |
| AMC Bay Street 16 | They Will Kill You | XL at AMC | 7:40pm | 1.7% | -623 min |
| AMC Mercado 20 | They Will Kill You | PRIME at AMC | 6:45pm | 5.6% | -568 min |
| AMC Eastridge 15 | They Will Kill You | Laser at AMC | 6:30pm | 0.8% | -553 min |
| AMC Saratoga 14 | They Will Kill You | XL at AMC | 8:30pm | 0% | -673 min |
| AMC NewPark 12 | They Will Kill You | Laser at AMC | 6:30pm | 3.3% | -553 min |
| AMC Sunnyvale 12 | They Will Kill You | Laser at AMC | 8:00pm | 4.4% | -643 min |
| AMC Mission Valley 20 | They Will Kill You | Laser at AMC | 7:45pm | 1.7% | -628 min |
| AMC Palm Promenade 24 | They Will Kill You | XL at AMC | 7:45pm | 0% | -628 min |
| AMC La Jolla 12 | They Will Kill You | Laser at AMC | 6:45pm | 7.6% | -568 min |
| AMC Chula Vista 10 | They Will Kill You | Laser at AMC | 7:45pm | 2.3% | -628 min |
| AMC Otay Ranch 12 | They Will Kill You | Laser at AMC | 6:00pm | 0% | -523 min |
| AMC Plaza Bonita 14 | They Will Kill You | Laser at AMC | 7:00pm | 2% | -582 min |
| AMC Poway 10 | They Will Kill You | Laser at AMC | 6:00pm | 3% | -522 min |
| AMC UTC 14 | They Will Kill You | Laser at AMC | 7:00pm | 3.8% | -582 min |
| AMC Southcenter 16 | They Will Kill You | Laser at AMC | 7:30pm | 8.2% | -612 min |
| AMC Pacific Place 11 | They Will Kill You | Open Caption (On-screen Subtitles) | 7:15pm | 0% | -597 min |
| AMC Kent Station 14 | They Will Kill You | Laser at AMC | 8:10pm | 0% | -652 min |
| AMC Alderwood Mall 16 | They Will Kill You | Laser at AMC | 8:00pm | 0.9% | -642 min |
| AMC Factoria 8 | They Will Kill You | Laser at AMC | 8:00pm | 1.6% | -642 min |
| AMC Woodinville 12 | They Will Kill You | Laser at AMC | 7:20pm | 7% | -601 min |
| AMC Arizona Center 24 | They Will Kill You | Thrills & Chills | 6:45pm | 0% | -567 min |
| AMC Desert Ridge 18 | They Will Kill You | Laser at AMC | 7:30pm | 2.4% | -612 min |
| AMC Deer Valley 17 | They Will Kill You | Laser at AMC | 7:00pm | 3.7% | -582 min |
| AMC Ahwatukee 24 | They Will Kill You | Laser at AMC | 7:10pm | 7.4% | -592 min |
| AMC Westgate 20 | They Will Kill You | Laser at AMC | 8:00pm | 0% | -642 min |
| AMC Westminster Promenade 24 | They Will Kill You | Laser at AMC | 7:10pm | 2.1% | -592 min |
| AMC Flatiron Crossing 14 | They Will Kill You | Laser at AMC | 6:45pm | 0% | -567 min |
| AMC Highlands Ranch 24 | They Will Kill You | Laser at AMC | 6:50pm | 7.7% | -571 min |
| AMC DINE-IN Southlands 16 | They Will Kill You | Dine-In Delivery to Seat | 8:45pm | 0% | -687 min |
| AMC Arapahoe Crossing 16 | They Will Kill You | Laser at AMC | 7:00pm | 2.1% | -582 min |

**Issues:** AMC The Grove 14: 'The Super Mario Galaxy Movie' not showing; AMC Century City 15: 'The Super Mario Galaxy Movie' not showing; AMC Burbank 16: No seat map for They Will Kill You; AMC Burbank 16: 'The Super Mario Galaxy Movie' not showing; AMC The Americana at Brand 18: 'The Super Mario Galaxy Movie' not showing; AMC Santa Monica 7: 'The Super Mario Galaxy Movie' not showing; AMC The Regency 20: 'The Super Mario Galaxy Movie' not showing; AMC Lakewood Mall 12: 'The Super Mario Galaxy Movie' not showing; AMC DINE-IN Marina 6: 'The Super Mario Galaxy Movie' not showing; AMC Brentwood 14: 'The Super Mario Galaxy Movie' not showing; AMC DINE-IN Fullerton 20: 'The Super Mario Galaxy Movie' not showing; AMC Orange 30: 'The Super Mario Galaxy Movie' not showing; AMC Tustin 14 @ The District: 'The Super Mario Galaxy Movie' not showing; AMC Puente Hills 20: 'The Super Mario Galaxy Movie' not showing; AMC Norwalk 20: 'The Super Mario Galaxy Movie' not showing; AMC Marina Pacifica 12: 'The Super Mario Galaxy Movie' not showing; AMC Montebello 10: 'The Super Mario Galaxy Movie' not showing; AMC La Mirada 7: 'The Super Mario Galaxy Movie' not showing; AMC Metreon 16: 'The Super Mario Galaxy Movie' not showing; AMC Bay Street 16: 'The Super Mario Galaxy Movie' not showing; AMC Mercado 20: 'The Super Mario Galaxy Movie' not showing; AMC Eastridge 15: 'The Super Mario Galaxy Movie' not showing; AMC Saratoga 14: 'The Super Mario Galaxy Movie' not showing; AMC NewPark 12: 'The Super Mario Galaxy Movie' not showing; AMC Sunnyvale 12: 'The Super Mario Galaxy Movie' not showing; AMC Kabuki 8: 'They Will Kill You' not showing; AMC Kabuki 8: 'The Super Mario Galaxy Movie' not showing; AMC Mission Valley 20: 'The Super Mario Galaxy Movie' not showing; AMC Fashion Valley 18: No seat map for They Will Kill You; AMC Fashion Valley 18: 'The Super Mario Galaxy Movie' not showing; AMC Palm Promenade 24: 'The Super Mario Galaxy Movie' not showing; AMC La Jolla 12: 'The Super Mario Galaxy Movie' not showing; AMC Chula Vista 10: 'The Super Mario Galaxy Movie' not showing; AMC Otay Ranch 12: 'The Super Mario Galaxy Movie' not showing; AMC Plaza Bonita 14: 'The Super Mario Galaxy Movie' not showing; AMC Poway 10: 'The Super Mario Galaxy Movie' not showing; AMC UTC 14: 'The Super Mario Galaxy Movie' not showing; AMC Southcenter 16: 'The Super Mario Galaxy Movie' not showing; AMC Pacific Place 11: 'The Super Mario Galaxy Movie' not showing; AMC Kent Station 14: 'The Super Mario Galaxy Movie' not showing; AMC Alderwood Mall 16: 'The Super Mario Galaxy Movie' not showing; AMC Factoria 8: 'The Super Mario Galaxy Movie' not showing; AMC Woodinville 12: 'The Super Mario Galaxy Movie' not showing; AMC Arizona Center 24: 'The Super Mario Galaxy Movie' not showing; AMC Desert Ridge 18: 'The Super Mario Galaxy Movie' not showing; AMC Deer Valley 17: 'The Super Mario Galaxy Movie' not showing; AMC Ahwatukee 24: 'The Super Mario Galaxy Movie' not showing; AMC Westgate 20: 'The Super Mario Galaxy Movie' not showing; AMC Westminster Promenade 24: 'The Super Mario Galaxy Movie' not showing; AMC Flatiron Crossing 14: 'The Super Mario Galaxy Movie' not showing; AMC Highlands Ranch 24: 'The Super Mario Galaxy Movie' not showing; AMC DINE-IN Southlands 16: 'The Super Mario Galaxy Movie' not showing; AMC Arapahoe Crossing 16: 'The Super Mario Galaxy Movie' not showing

---

## 2026-03-30 09:27 — PT Group

**Polymarket movies tracked:** They Will Kill You, The Super Mario Galaxy Movie

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC The Grove 14 | They Will Kill You | Laser at AMC | 5:15pm | 6.3% | -469 min |
| AMC Century City 15 | They Will Kill You | Laser at AMC | 8:05pm | 17.1% | -638 min |
| AMC The Americana at Brand 18 | They Will Kill You | XL at AMC | 7:45pm | 3.8% | -619 min |
| AMC Santa Monica 7 | They Will Kill You | Laser at AMC | 8:00pm | 0% | -634 min |
| AMC The Regency 20 | They Will Kill You | Laser at AMC | 8:40pm | 0% | -674 min |
| AMC Lakewood Mall 12 | They Will Kill You | Laser at AMC | 6:45pm | 9.4% | -559 min |
| AMC DINE-IN Marina 6 | They Will Kill You | Dine-In Delivery to Seat | 7:00pm | 31% | -574 min |
| AMC Brentwood 14 | They Will Kill You | Laser at AMC | 6:30pm | 0.7% | -544 min |
| AMC DINE-IN Fullerton 20 | They Will Kill You | Laser at AMC | 7:10pm | 5.2% | -584 min |
| AMC Orange 30 | They Will Kill You | XL at AMC | 7:10pm | 3% | -584 min |
| AMC Tustin 14 @ The District | They Will Kill You | PRIME at AMC | 6:15pm | 8.4% | -529 min |
| AMC Puente Hills 20 | They Will Kill You | Laser at AMC | 9:00pm | 2.7% | -694 min |
| AMC Norwalk 20 | They Will Kill You | Laser at AMC | 7:45pm | 8.2% | -619 min |
| AMC Marina Pacifica 12 | They Will Kill You | Laser at AMC | 7:05pm | 6.9% | -578 min |
| AMC Montebello 10 | They Will Kill You | Laser at AMC | 7:45pm | 3.8% | -619 min |
| AMC La Mirada 7 | They Will Kill You | Laser at AMC | 7:30pm | 4.2% | -604 min |
| AMC Metreon 16 | They Will Kill You | Open Caption (On-screen Subtitles) | 7:15pm | 12.2% | -589 min |
| AMC Bay Street 16 | They Will Kill You | XL at AMC | 7:40pm | 1.7% | -614 min |
| AMC Mercado 20 | They Will Kill You | PRIME at AMC | 6:45pm | 5.6% | -559 min |
| AMC Eastridge 15 | They Will Kill You | Laser at AMC | 6:30pm | 0.8% | -544 min |
| AMC Saratoga 14 | They Will Kill You | XL at AMC | 8:30pm | 0% | -664 min |
| AMC NewPark 12 | They Will Kill You | Laser at AMC | 6:30pm | 3.3% | -544 min |
| AMC Sunnyvale 12 | They Will Kill You | Laser at AMC | 8:00pm | 4.4% | -634 min |
| AMC Mission Valley 20 | They Will Kill You | Laser at AMC | 7:45pm | 1.7% | -618 min |
| AMC Palm Promenade 24 | They Will Kill You | XL at AMC | 7:45pm | 0% | -618 min |
| AMC La Jolla 12 | They Will Kill You | Laser at AMC | 6:45pm | 7.6% | -558 min |
| AMC Chula Vista 10 | They Will Kill You | Laser at AMC | 7:45pm | 2.3% | -618 min |
| AMC Otay Ranch 12 | They Will Kill You | Laser at AMC | 6:00pm | 0% | -513 min |
| AMC Plaza Bonita 14 | They Will Kill You | Laser at AMC | 7:00pm | 2% | -573 min |
| AMC Poway 10 | They Will Kill You | Laser at AMC | 6:00pm | 3% | -513 min |
| AMC UTC 14 | They Will Kill You | Laser at AMC | 7:00pm | 3.8% | -573 min |
| AMC Southcenter 16 | They Will Kill You | Laser at AMC | 7:30pm | 8.2% | -603 min |
| AMC Pacific Place 11 | They Will Kill You | Open Caption (On-screen Subtitles) | 7:15pm | 0% | -588 min |
| AMC Kent Station 14 | They Will Kill You | Laser at AMC | 8:10pm | 0% | -643 min |
| AMC Alderwood Mall 16 | They Will Kill You | Laser at AMC | 8:00pm | 0.9% | -633 min |
| AMC Factoria 8 | They Will Kill You | Laser at AMC | 8:00pm | 1.6% | -633 min |
| AMC Woodinville 12 | They Will Kill You | Laser at AMC | 7:20pm | 7% | -593 min |
| AMC Arizona Center 24 | They Will Kill You | Thrills & Chills | 6:45pm | 0% | -558 min |
| AMC Desert Ridge 18 | They Will Kill You | Laser at AMC | 7:30pm | 2.4% | -603 min |
| AMC Deer Valley 17 | They Will Kill You | Laser at AMC | 7:00pm | 3.7% | -573 min |
| AMC Ahwatukee 24 | They Will Kill You | Laser at AMC | 7:10pm | 7.4% | -583 min |
| AMC Westgate 20 | They Will Kill You | Laser at AMC | 8:00pm | 0% | -633 min |
| AMC Westminster Promenade 24 | They Will Kill You | Laser at AMC | 7:10pm | 2.1% | -583 min |
| AMC Flatiron Crossing 14 | They Will Kill You | Laser at AMC | 6:45pm | 0% | -558 min |
| AMC Highlands Ranch 24 | They Will Kill You | Laser at AMC | 6:50pm | 7.7% | -563 min |
| AMC DINE-IN Southlands 16 | They Will Kill You | Dine-In Delivery to Seat | 8:45pm | 0% | -678 min |
| AMC Arapahoe Crossing 16 | They Will Kill You | Laser at AMC | 7:00pm | 2.1% | -573 min |

**Issues:** AMC The Grove 14: 'The Super Mario Galaxy Movie' not showing; AMC Century City 15: 'The Super Mario Galaxy Movie' not showing; AMC Burbank 16: No seat map for They Will Kill You; AMC Burbank 16: 'The Super Mario Galaxy Movie' not showing; AMC The Americana at Brand 18: 'The Super Mario Galaxy Movie' not showing; AMC Santa Monica 7: 'The Super Mario Galaxy Movie' not showing; AMC The Regency 20: 'The Super Mario Galaxy Movie' not showing; AMC Lakewood Mall 12: 'The Super Mario Galaxy Movie' not showing; AMC DINE-IN Marina 6: 'The Super Mario Galaxy Movie' not showing; AMC Brentwood 14: 'The Super Mario Galaxy Movie' not showing; AMC DINE-IN Fullerton 20: 'The Super Mario Galaxy Movie' not showing; AMC Orange 30: 'The Super Mario Galaxy Movie' not showing; AMC Tustin 14 @ The District: 'The Super Mario Galaxy Movie' not showing; AMC Puente Hills 20: 'The Super Mario Galaxy Movie' not showing; AMC Norwalk 20: 'The Super Mario Galaxy Movie' not showing; AMC Marina Pacifica 12: 'The Super Mario Galaxy Movie' not showing; AMC Montebello 10: 'The Super Mario Galaxy Movie' not showing; AMC La Mirada 7: 'The Super Mario Galaxy Movie' not showing; AMC Metreon 16: 'The Super Mario Galaxy Movie' not showing; AMC Bay Street 16: 'The Super Mario Galaxy Movie' not showing; AMC Mercado 20: 'The Super Mario Galaxy Movie' not showing; AMC Eastridge 15: 'The Super Mario Galaxy Movie' not showing; AMC Saratoga 14: 'The Super Mario Galaxy Movie' not showing; AMC NewPark 12: 'The Super Mario Galaxy Movie' not showing; AMC Sunnyvale 12: 'The Super Mario Galaxy Movie' not showing; AMC Kabuki 8: 'They Will Kill You' not showing; AMC Kabuki 8: 'The Super Mario Galaxy Movie' not showing; AMC Mission Valley 20: 'The Super Mario Galaxy Movie' not showing; AMC Fashion Valley 18: No seat map for They Will Kill You; AMC Fashion Valley 18: 'The Super Mario Galaxy Movie' not showing; AMC Palm Promenade 24: 'The Super Mario Galaxy Movie' not showing; AMC La Jolla 12: 'The Super Mario Galaxy Movie' not showing; AMC Chula Vista 10: 'The Super Mario Galaxy Movie' not showing; AMC Otay Ranch 12: 'The Super Mario Galaxy Movie' not showing; AMC Plaza Bonita 14: 'The Super Mario Galaxy Movie' not showing; AMC Poway 10: 'The Super Mario Galaxy Movie' not showing; AMC UTC 14: 'The Super Mario Galaxy Movie' not showing; AMC Southcenter 16: 'The Super Mario Galaxy Movie' not showing; AMC Pacific Place 11: 'The Super Mario Galaxy Movie' not showing; AMC Kent Station 14: 'The Super Mario Galaxy Movie' not showing; AMC Alderwood Mall 16: 'The Super Mario Galaxy Movie' not showing; AMC Factoria 8: 'The Super Mario Galaxy Movie' not showing; AMC Woodinville 12: 'The Super Mario Galaxy Movie' not showing; AMC Arizona Center 24: 'The Super Mario Galaxy Movie' not showing; AMC Desert Ridge 18: 'The Super Mario Galaxy Movie' not showing; AMC Deer Valley 17: 'The Super Mario Galaxy Movie' not showing; AMC Ahwatukee 24: 'The Super Mario Galaxy Movie' not showing; AMC Westgate 20: 'The Super Mario Galaxy Movie' not showing; AMC Westminster Promenade 24: 'The Super Mario Galaxy Movie' not showing; AMC Flatiron Crossing 14: 'The Super Mario Galaxy Movie' not showing; AMC Highlands Ranch 24: 'The Super Mario Galaxy Movie' not showing; AMC DINE-IN Southlands 16: 'The Super Mario Galaxy Movie' not showing; AMC Arapahoe Crossing 16: 'The Super Mario Galaxy Movie' not showing

---

## 2026-03-30 09:37 — PT Group

**Polymarket movies tracked:** They Will Kill You, The Super Mario Galaxy Movie

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC The Grove 14 | They Will Kill You | Open Caption (On-screen Subtitles) | 8:00pm | 7% | -625 min |
| AMC Century City 15 | They Will Kill You | Laser at AMC | 8:05pm | 17.1% | -629 min |
| AMC The Americana at Brand 18 | They Will Kill You | XL at AMC | 7:45pm | 3.8% | -610 min |
| AMC Santa Monica 7 | They Will Kill You | Laser at AMC | 8:00pm | 0% | -625 min |
| AMC The Regency 20 | They Will Kill You | Laser at AMC | 8:40pm | 0% | -665 min |
| AMC The Regency 20 | They Will Kill You | Open Caption (On-screen Subtitles) | 6:05pm | 0% | -509 min |
| AMC Lakewood Mall 12 | They Will Kill You | Laser at AMC | 6:45pm | 9.4% | -550 min |
| AMC DINE-IN Marina 6 | They Will Kill You | Dine-In Delivery to Seat | 7:00pm | 31% | -565 min |
| AMC Brentwood 14 | They Will Kill You | Laser at AMC | 6:30pm | 0.7% | -535 min |
| AMC DINE-IN Fullerton 20 | They Will Kill You | Laser at AMC | 7:10pm | 5.2% | -575 min |
| AMC Orange 30 | They Will Kill You | XL at AMC | 7:10pm | 3% | -575 min |
| AMC Orange 30 | They Will Kill You | Laser at AMC | 6:15pm | 0.9% | -520 min |
| AMC Tustin 14 @ The District | They Will Kill You | PRIME at AMC | 6:15pm | 8.4% | -520 min |
| AMC Tustin 14 @ The District | They Will Kill You | Open Caption (On-screen Subtitles) | 7:40pm | 0.8% | -605 min |
| AMC Puente Hills 20 | They Will Kill You | Laser at AMC | 9:00pm | 2.7% | -685 min |
| AMC Puente Hills 20 | They Will Kill You | Open Caption (On-screen Subtitles) | 6:30pm | 0% | -535 min |
| AMC Norwalk 20 | They Will Kill You | Laser at AMC | 7:45pm | 8.2% | -610 min |
| AMC Marina Pacifica 12 | They Will Kill You | Laser at AMC | 7:05pm | 6.9% | -569 min |
| AMC Montebello 10 | They Will Kill You | Laser at AMC | 7:45pm | 3.8% | -610 min |
| AMC La Mirada 7 | They Will Kill You | Laser at AMC | 7:30pm | 4.2% | -595 min |
| AMC Metreon 16 | They Will Kill You | Open Caption (On-screen Subtitles) | 7:15pm | 12.2% | -580 min |
| AMC Bay Street 16 | They Will Kill You | XL at AMC | 7:40pm | 1.7% | -605 min |
| AMC Bay Street 16 | They Will Kill You | Laser at AMC | 9:00pm | 2.8% | -685 min |
| AMC Bay Street 16 | They Will Kill You | Open Caption (On-screen Subtitles) | 6:15pm | 1.4% | -520 min |
| AMC Mercado 20 | They Will Kill You | PRIME at AMC | 6:45pm | 5.6% | -550 min |
| AMC Mercado 20 | They Will Kill You | Laser at AMC | 8:00pm | 1.7% | -625 min |
| AMC Eastridge 15 | They Will Kill You | Laser at AMC | 6:30pm | 0.8% | -535 min |
| AMC Saratoga 14 | They Will Kill You | XL at AMC | 8:30pm | 0% | -655 min |
| AMC Saratoga 14 | They Will Kill You | Laser at AMC | 7:15pm | 1.9% | -580 min |
| AMC NewPark 12 | They Will Kill You | Laser at AMC | 6:30pm | 3.3% | -535 min |
| AMC Sunnyvale 12 | They Will Kill You | Laser at AMC | 8:00pm | 4.4% | -624 min |
| AMC Palm Promenade 24 | They Will Kill You | Laser at AMC | 7:00pm | 0% | -564 min |
| AMC Otay Ranch 12 | They Will Kill You | Open Caption (On-screen Subtitles) | 7:45pm | 0% | -609 min |
| AMC Southcenter 16 | They Will Kill You | Laser at AMC | 7:30pm | 8.2% | -594 min |
| AMC Kent Station 14 | They Will Kill You | Laser at AMC | 8:10pm | 0% | -634 min |
| AMC Arizona Center 24 | They Will Kill You | Thrills & Chills | 6:45pm | 0% | -548 min |
| AMC Desert Ridge 18 | They Will Kill You | Laser at AMC | 7:30pm | 2.4% | -593 min |
| AMC Ahwatukee 24 | They Will Kill You | Laser at AMC | 7:10pm | 7.4% | -573 min |
| AMC Westminster Promenade 24 | They Will Kill You | Laser at AMC | 7:10pm | 2.1% | -573 min |
| AMC Flatiron Crossing 14 | They Will Kill You | Laser at AMC | 6:45pm | 0% | -548 min |
| AMC Flatiron Crossing 14 | They Will Kill You | Open Caption (On-screen Subtitles) | 6:30pm | 3.7% | -533 min |
| AMC DINE-IN Southlands 16 | They Will Kill You | Dine-In Delivery to Seat | 8:45pm | 0% | -668 min |
| AMC Arapahoe Crossing 16 | They Will Kill You | Laser at AMC | 7:00pm | 2.1% | -563 min |

**Issues:** AMC The Grove 14: 'The Super Mario Galaxy Movie' not showing; AMC Century City 15: 'The Super Mario Galaxy Movie' not showing; AMC Burbank 16: No seat map for They Will Kill You XL at AMC; AMC Burbank 16: No seat map for They Will Kill You Open Caption (On-screen Subtitles); AMC Burbank 16: 'The Super Mario Galaxy Movie' not showing; AMC The Americana at Brand 18: 'The Super Mario Galaxy Movie' not showing; AMC Santa Monica 7: 'The Super Mario Galaxy Movie' not showing; AMC The Regency 20: 'The Super Mario Galaxy Movie' not showing; AMC Lakewood Mall 12: 'The Super Mario Galaxy Movie' not showing; AMC DINE-IN Marina 6: 'The Super Mario Galaxy Movie' not showing; AMC Brentwood 14: 'The Super Mario Galaxy Movie' not showing; AMC DINE-IN Fullerton 20: 'The Super Mario Galaxy Movie' not showing; AMC Orange 30: 'The Super Mario Galaxy Movie' not showing; AMC Tustin 14 @ The District: 'The Super Mario Galaxy Movie' not showing; AMC Puente Hills 20: 'The Super Mario Galaxy Movie' not showing; AMC Norwalk 20: 'The Super Mario Galaxy Movie' not showing; AMC Marina Pacifica 12: 'The Super Mario Galaxy Movie' not showing; AMC Montebello 10: 'The Super Mario Galaxy Movie' not showing; AMC La Mirada 7: 'The Super Mario Galaxy Movie' not showing; AMC Metreon 16: 'The Super Mario Galaxy Movie' not showing; AMC Bay Street 16: 'The Super Mario Galaxy Movie' not showing; AMC Mercado 20: 'The Super Mario Galaxy Movie' not showing; AMC Eastridge 15: 'The Super Mario Galaxy Movie' not showing; AMC Saratoga 14: 'The Super Mario Galaxy Movie' not showing; AMC NewPark 12: 'The Super Mario Galaxy Movie' not showing; AMC Sunnyvale 12: 'The Super Mario Galaxy Movie' not showing; AMC Kabuki 8: 'They Will Kill You' not showing; AMC Kabuki 8: 'The Super Mario Galaxy Movie' not showing; AMC Mission Valley 20: No seat map for They Will Kill You Laser at AMC; AMC Mission Valley 20: 'The Super Mario Galaxy Movie' not showing; AMC Fashion Valley 18: No seat map for They Will Kill You Laser at AMC; AMC Fashion Valley 18: 'The Super Mario Galaxy Movie' not showing; AMC Palm Promenade 24: No seat map for They Will Kill You XL at AMC; AMC Palm Promenade 24: 'The Super Mario Galaxy Movie' not showing; AMC La Jolla 12: No seat map for They Will Kill You Laser at AMC; AMC La Jolla 12: 'The Super Mario Galaxy Movie' not showing; AMC Chula Vista 10: No seat map for They Will Kill You Laser at AMC; AMC Chula Vista 10: 'The Super Mario Galaxy Movie' not showing; AMC Otay Ranch 12: No seat map for They Will Kill You Laser at AMC; AMC Otay Ranch 12: 'The Super Mario Galaxy Movie' not showing; AMC Plaza Bonita 14: No seat map for They Will Kill You Laser at AMC; AMC Plaza Bonita 14: 'The Super Mario Galaxy Movie' not showing; AMC Poway 10: No seat map for They Will Kill You Laser at AMC; AMC Poway 10: 'The Super Mario Galaxy Movie' not showing; AMC UTC 14: No seat map for They Will Kill You Laser at AMC; AMC UTC 14: 'The Super Mario Galaxy Movie' not showing; AMC Southcenter 16: 'The Super Mario Galaxy Movie' not showing; AMC Pacific Place 11: No seat map for They Will Kill You Open Caption (On-screen Subtitles); AMC Pacific Place 11: 'The Super Mario Galaxy Movie' not showing; AMC Kent Station 14: 'The Super Mario Galaxy Movie' not showing; AMC Alderwood Mall 16: No seat map for They Will Kill You Laser at AMC; AMC Alderwood Mall 16: 'The Super Mario Galaxy Movie' not showing; AMC Factoria 8: No seat map for They Will Kill You Laser at AMC; AMC Factoria 8: 'The Super Mario Galaxy Movie' not showing; AMC Woodinville 12: No seat map for They Will Kill You Laser at AMC; AMC Woodinville 12: 'The Super Mario Galaxy Movie' not showing; AMC Arizona Center 24: 'The Super Mario Galaxy Movie' not showing; AMC Desert Ridge 18: 'The Super Mario Galaxy Movie' not showing; AMC Deer Valley 17: No seat map for They Will Kill You Laser at AMC; AMC Deer Valley 17: 'The Super Mario Galaxy Movie' not showing; AMC Ahwatukee 24: 'The Super Mario Galaxy Movie' not showing; AMC Westgate 20: No seat map for They Will Kill You Laser at AMC; AMC Westgate 20: 'The Super Mario Galaxy Movie' not showing; AMC Westminster Promenade 24: 'The Super Mario Galaxy Movie' not showing; AMC Flatiron Crossing 14: 'The Super Mario Galaxy Movie' not showing; AMC Highlands Ranch 24: No seat map for They Will Kill You Laser at AMC; AMC Highlands Ranch 24: 'The Super Mario Galaxy Movie' not showing; AMC DINE-IN Southlands 16: 'The Super Mario Galaxy Movie' not showing; AMC Arapahoe Crossing 16: 'The Super Mario Galaxy Movie' not showing

---

## 2026-04-03 07:19 — PT Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC The Grove 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:45pm | 28.6% | -940 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:00pm | 72.9% | -775 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:15pm | 68% | -610 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:30pm | 6.5% | -985 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:45pm | 68.8% | -820 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 58.1% | -655 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 7.8% | -910 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 51.2% | -715 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -880 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 15.1% | -745 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 63.9% | -880 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 79.7% | -715 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 1.1% | -940 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 54.1% | -775 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 5.5% | -610 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 5.7% | -910 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 30% | -745 min |
| AMC Burbank 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:15pm | 10.3% | -970 min |
| AMC Burbank 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:40pm | 76.2% | -815 min |
| AMC Burbank 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 74.3% | -655 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:45pm | 44.4% | -940 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:00pm | 73.3% | -775 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:15pm | 70.4% | -610 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:15pm | 11.4% | -970 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:30pm | 68.2% | -805 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:45pm | 63.6% | -640 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | XL at AMC | 9:00pm | 17.3% | -835 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 5.5% | -910 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 36.9% | -730 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 19.4% | -865 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 21.4% | -760 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 11.9% | -670 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 3.4% | -595 min |
| AMC Santa Monica 7 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 11.1% | -835 min |
| AMC Santa Monica 7 | The Super Mario Galaxy Movie | RealD 3D | 7:40pm | 12.8% | -755 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 3.6% | -894 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:10pm | 43% | -724 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:20pm | 5.9% | -974 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:45pm | 45.6% | -819 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 42.6% | -654 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:55pm | 0% | -949 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:35pm | 0% | -929 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:05pm | 8.3% | -839 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:20pm | 10.9% | -794 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 13.8% | -759 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 5.2% | -624 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 2.2% | -909 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | RealD 3D | 9:25pm | 0.5% | -859 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 1.4% | -744 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | RealD 3D | 6:35pm | 9.2% | -689 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:10pm | 2.8% | -604 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:10pm | 64.8% | -784 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:40pm | 63.9% | -754 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:25pm | 60% | -679 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 61.5% | -624 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 52.8% | -594 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 2.2% | -894 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 8:35pm | 25.8% | -809 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 32.3% | -729 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 9.1% | -654 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 14.9% | -908 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 54.3% | -743 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 11:00pm | 22.4% | -953 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:30pm | 69% | -803 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:00pm | 67.2% | -653 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | IMAX at AMC | 6:00pm | 26.5% | -653 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 14.8% | -893 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 64.8% | -713 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 1.1% | -863 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 2.2% | -848 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 12.4% | -773 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 1.5% | -668 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 7.4% | -593 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 7.1% | -683 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 6.3% | -938 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 22.7% | -908 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 55% | -773 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 71.9% | -743 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 50% | -608 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 11:15pm | 0% | -968 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -893 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 14.6% | -878 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 12.2% | -803 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 9.4% | -728 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 43.8% | -713 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 21.4% | -638 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:15pm | 46.3% | -848 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:30pm | 81.5% | -683 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 48.8% | -863 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 73.7% | -683 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | XL at AMC | 11:00pm | 1% | -953 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 9.9% | -773 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 11:35pm | 2.2% | -987 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 11:20pm | 0% | -972 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 10:50pm | 0% | -942 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 10:25pm | 0% | -918 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 9.2% | -803 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 20.9% | -788 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 7:50pm | 18% | -762 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 8.4% | -698 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 6:10pm | 14.6% | -663 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 16.8% | -623 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 0% | -608 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -893 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 2.6% | -833 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 9.8% | -713 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 3.9% | -653 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 2% | -593 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 8:45pm | 0% | -818 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:15pm | 71.5% | -728 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 65.3% | -773 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 56.7% | -608 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 11.4% | -923 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 60.2% | -743 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 64% | -683 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 4.1% | -833 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 9.6% | -788 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | RealD 3D | 5:35pm | 34.2% | -627 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 16.1% | -982 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 68.9% | -817 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 78.3% | -652 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 22.9% | -907 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 69.2% | -742 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -952 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -937 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 4.4% | -922 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 11.1% | -892 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 31.6% | -847 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 58.1% | -772 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 59.4% | -682 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 24.3% | -622 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 49.5% | -607 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 11:15pm | 0% | -967 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -877 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 17.4% | -802 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 26.6% | -712 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 11% | -637 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 8:15pm | 2.7% | -787 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | IMAX at AMC | 10:45pm | 2.4% | -937 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 59.6% | -772 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | IMAX at AMC | 5:15pm | 36.8% | -607 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 44.7% | -877 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 66.5% | -712 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 35.9% | -892 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 66.3% | -817 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 59.1% | -727 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 61.2% | -652 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 3.4% | -907 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -847 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 32.9% | -787 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 41.6% | -742 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 10.6% | -622 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 38.8% | -682 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:55pm | 20.5% | -887 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 60% | -802 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 77.8% | -712 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:35pm | 57.8% | -627 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | RealD 3D | 10:25pm | 2.2% | -917 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | RealD 3D | 9:25pm | 4.4% | -857 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 44.4% | -742 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 42.9% | -682 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 45.7% | -891 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | Laser at AMC | 8:40pm | 69.2% | -811 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:10pm | 74.1% | -721 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | Laser at AMC | 6:25pm | 67.5% | -676 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 10:45pm | 0% | -936 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 23.1% | -846 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 45.7% | -771 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 5:50pm | 30.8% | -640 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 12.8% | -601 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 7.8% | -876 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 22.1% | -816 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 58.6% | -711 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 3.4% | -921 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 34.5% | -756 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 34% | -681 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 26.5% | -651 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 18.1% | -591 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 9.2% | -906 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 49.7% | -741 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -936 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 3.9% | -681 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 0% | -606 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 8.1% | -636 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 13.6% | -921 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 60.7% | -756 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 24.8% | -591 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -891 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 2.1% | -726 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -876 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 2% | -831 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 5.9% | -741 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 5.6% | -711 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 5.4% | -801 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 8.3% | -636 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:15pm | 0% | -666 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 18.6% | -874 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 71.4% | -709 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -949 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -859 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 15.4% | -844 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 30% | -784 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 14% | -694 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -904 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 21.7% | -739 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 11.5% | -679 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 30.3% | -844 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 44.1% | -679 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0.7% | -874 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0.7% | -814 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 21.8% | -709 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 4% | -649 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0.4% | -784 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 3.8% | -754 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 1.9% | -619 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:00pm | 3.4% | -589 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 7.6% | -844 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 33.8% | -679 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0.9% | -889 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 2.2% | -724 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -829 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 0% | -754 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 0% | -589 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0% | -814 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0.9% | -649 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 24.6% | -829 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 37.9% | -649 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 47.3% | -679 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 25.6% | -589 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 1.2% | -919 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 31.4% | -754 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 9:30pm | 3.3% | -859 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 7:15pm | 10.1% | -724 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 57.8% | -829 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 66.4% | -664 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 19.4% | -889 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 65.8% | -724 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -949 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -919 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 25% | -784 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 33.9% | -754 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 17.9% | -619 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 17.4% | -589 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 10.2% | -859 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 17.6% | -694 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -889 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 12.5% | -829 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 28.9% | -769 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 23.9% | -709 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 19.3% | -649 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 27.3% | -904 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 74.1% | -739 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -874 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 1.1% | -829 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 0% | -784 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 13.9% | -769 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 5.1% | -709 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 5% | -664 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 1% | -619 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 10:45pm | 0% | -934 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -859 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0% | -814 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 5.4% | -694 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0% | -649 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 3.6% | -604 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 12.6% | -918 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 66.7% | -753 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 47% | -588 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | XL at AMC | 8:45pm | 11.4% | -813 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | XL at AMC | 6:00pm | 28.6% | -648 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 6% | -888 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 9.1% | -843 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 32.7% | -723 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 29.5% | -663 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 6.6% | -783 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 4.4% | -618 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -888 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 23.4% | -858 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 3.3% | -798 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 16.1% | -783 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 21.2% | -723 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 10.6% | -693 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 13.4% | -618 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 1.4% | -588 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -918 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 1.2% | -828 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 16.7% | -753 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 17.4% | -663 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 4.6% | -843 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 28.5% | -813 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 66.3% | -738 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 60.9% | -678 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 0% | -618 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | RealD 3D | 10:45pm | 1.2% | -933 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 36% | -768 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 29.2% | -648 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 32.6% | -603 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | undefined | 9:45pm | 9.8% | -873 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | undefined | 7:00pm | 67.5% | -708 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 14.5% | -857 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 65.6% | -692 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -887 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 13.8% | -722 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -917 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 2.7% | -797 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 7.5% | -752 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 8.2% | -632 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 6.1% | -587 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -827 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 4.7% | -662 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:30pm | 4.4% | -857 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:45pm | 19.6% | -692 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:00pm | 7.5% | -947 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:30pm | 60.2% | -797 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:45pm | 57.9% | -632 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -887 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 3.3% | -722 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -932 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 1.6% | -827 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 16% | -767 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 22.2% | -602 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -917 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -752 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 4.2% | -662 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -587 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:40pm | 52.9% | -747 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 63.1% | -722 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 81.6% | -662 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 50% | -587 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 2.6% | -827 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 43.8% | -782 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 69.7% | -692 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 52.1% | -617 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | PRIME at AMC | 10:45pm | 4.9% | -931 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | PRIME at AMC | 8:00pm | 26.8% | -766 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | PRIME at AMC | 5:15pm | 22% | -601 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 2.4% | -901 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 0% | -841 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 11% | -811 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 35.7% | -736 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 8.9% | -676 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 8.8% | -646 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 15% | -886 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 63.9% | -736 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 54.4% | -586 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | XL at AMC | 10:30pm | 1.8% | -916 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | XL at AMC | 5:30pm | 12.3% | -616 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 6% | -871 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -826 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 2.1% | -721 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 8.4% | -676 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:10pm | 2.5% | -656 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 1% | -856 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 2.8% | -766 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 1.5% | -796 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 2.6% | -631 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | undefined | 10:15pm | 4.5% | -901 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | undefined | 7:30pm | 16.2% | -736 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:00pm | 1.1% | -946 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:30pm | 21.1% | -796 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 31.8% | -646 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 16.4% | -856 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -886 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 10.6% | -826 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 28.8% | -751 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 23.6% | -736 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 29.5% | -721 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 41.5% | -676 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 13.6% | -661 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 17.8% | -601 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 11.4% | -586 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -916 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 3.3% | -766 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 32.2% | -616 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 50% | -676 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 9.5% | -766 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | XL at AMC | 5:15pm | 3.2% | -601 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -916 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0.6% | -871 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 4.3% | -706 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0% | -811 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0.9% | -751 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 8.5% | -646 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 10:20pm | 3.2% | -905 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 9:10pm | 25% | -836 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:40pm | 17.3% | -746 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 46.4% | -706 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 30.8% | -586 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | RealD 3D | 9:40pm | 1.4% | -866 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | RealD 3D | 8:10pm | 14.9% | -776 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 29.9% | -616 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 67.2% | -750 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 66.4% | -585 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -885 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 33.3% | -795 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 43.2% | -720 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 43.2% | -630 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 11.7% | -840 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 29.8% | -675 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 3.5% | -900 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -795 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 5.8% | -735 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0% | -930 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -915 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0.2% | -870 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -855 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 8:00pm | 4.8% | -765 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 7:00pm | 4.3% | -705 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 4% | -690 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 6:15pm | 15.9% | -660 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 5:15pm | 6.3% | -600 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 0.7% | -824 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 16.2% | -659 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 3% | -914 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 53.8% | -749 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 50% | -584 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -929 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -884 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 4.4% | -794 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 23.8% | -734 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 27.4% | -719 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 15.6% | -629 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -944 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 7.3% | -854 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -779 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 8.3% | -689 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 1.9% | -614 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 12.9% | -809 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 25.2% | -644 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 2% | -914 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 43.7% | -749 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 11.4% | -584 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -884 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 3.5% | -854 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 26.1% | -719 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 13.9% | -689 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -869 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 7.9% | -779 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 30.4% | -704 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 41.3% | -614 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:15pm | 24.3% | -839 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | PRIME at AMC | 9:45pm | 4.3% | -869 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | PRIME 3D | 7:00pm | 47.3% | -704 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 4.4% | -914 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 6.3% | -899 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 6.6% | -854 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 16.7% | -794 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 13.2% | -779 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 31.9% | -749 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 57.3% | -734 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 49.5% | -689 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 59.4% | -629 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 37.4% | -614 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 17.6% | -584 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 4.4% | -824 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 6.3% | -764 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 3.3% | -659 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 28.1% | -599 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 2.2% | -974 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 11.8% | -809 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 14.8% | -644 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 13.7% | -899 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 34.5% | -734 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -944 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -929 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -824 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 0% | -779 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 6.7% | -764 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 0% | -614 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 0% | -599 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 11:15pm | 0% | -959 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -884 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 1.3% | -794 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 0% | -719 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 1.8% | -629 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | English Spoken with Spanish Subtitles | 6:15pm | 1.3% | -659 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:40pm | 19.4% | -863 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 71% | -703 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:40pm | 0% | -923 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:25pm | 0% | -848 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:40pm | 22.2% | -803 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 29.7% | -763 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 47.9% | -688 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 48.9% | -643 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:50pm | 29.5% | -632 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:20pm | 31% | -602 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 44.6% | -778 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | RealD 3D | 5:35pm | 23.2% | -617 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:15pm | 21% | -838 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:30pm | 62.9% | -673 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 3.1% | -898 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 22.3% | -733 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 22.2% | -808 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 25.8% | -703 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -868 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 2.8% | -778 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 14.1% | -613 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 9.5% | -867 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 73.3% | -702 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -927 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 5.2% | -837 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:50pm | 3.8% | -811 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 40% | -762 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 67.1% | -672 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 71.2% | -657 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:50pm | 42.3% | -631 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 66.5% | -597 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 45.9% | -582 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -792 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -747 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 38.5% | -717 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 24.4% | -687 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 34.1% | -642 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 78.3% | -642 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -912 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 20% | -732 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 36.5% | -597 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 11:15pm | 6.8% | -957 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 11:45pm | 0% | -987 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 10:30pm | 0% | -912 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 10:00pm | 2.2% | -882 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:45pm | 0% | -867 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:15pm | 17.8% | -837 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:15pm | 48.6% | -777 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:45pm | 44.4% | -747 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:15pm | 61.1% | -717 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:45pm | 73.3% | -687 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:15pm | 58.7% | -657 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 1.6% | -912 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 21.8% | -747 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 33% | -582 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 13.2% | -852 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 80.8% | -687 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 12.9% | -822 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 46.3% | -792 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 54.8% | -657 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 63.2% | -627 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 23.2% | -717 min |

**Issues:** AMC Century City 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Century City 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Century City 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie SCREENX at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie SCREENX at AMC; AMC Santa Monica 7: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Santa Monica 7: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Santa Monica 7: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Lakewood Mall 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Lakewood Mall 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Brentwood 14: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Orange 30: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Orange 30: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Tustin 14 @ The District: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Tustin 14 @ The District: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Metreon 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Metreon 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Metreon 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Bay Street 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Bay Street 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mercado 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mercado 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mercado 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Eastridge 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Eastridge 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Saratoga 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Saratoga 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Saratoga 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC NewPark 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC NewPark 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mission Valley 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mission Valley 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Palm Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Palm Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Chula Vista 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Chula Vista 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Chula Vista 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Poway 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Poway 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC UTC 14: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC UTC 14: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Southcenter 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Southcenter 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Southcenter 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Southcenter 16: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Southcenter 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Kent Station 14: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Alderwood Mall 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Alderwood Mall 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Alderwood Mall 16: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Alderwood Mall 16: No seat map for The Super Mario Galaxy Movie XL at AMC; AMC Woodinville 12: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Arizona Center 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Westminster Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Westminster Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Highlands Ranch 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Highlands Ranch 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC DINE-IN Southlands 16: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC

---

## 2026-04-03 08:10 — PT Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC The Grove 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:45pm | 28.6% | -887 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:00pm | 71.9% | -722 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:15pm | 68% | -557 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:30pm | 6.5% | -932 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:45pm | 69.8% | -767 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 58.1% | -602 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 7.8% | -857 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 51.2% | -662 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -827 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 15.1% | -692 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 62.7% | -827 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 79.1% | -662 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 1.1% | -887 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 54.7% | -722 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 5.5% | -557 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 5.7% | -857 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 30% | -692 min |
| AMC Burbank 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:15pm | 10.3% | -917 min |
| AMC Burbank 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:40pm | 76.2% | -762 min |
| AMC Burbank 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 74.3% | -602 min |
| AMC Santa Monica 7 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 10.9% | -542 min |
| AMC Santa Monica 7 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 11.1% | -782 min |
| AMC Santa Monica 7 | The Super Mario Galaxy Movie | RealD 3D | 7:40pm | 12.8% | -702 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:10pm | 43% | -672 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:20pm | 5.9% | -921 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:45pm | 45.6% | -767 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 42.6% | -602 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:55pm | 0% | -897 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:35pm | 0% | -876 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:05pm | 8.3% | -786 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:20pm | 10.9% | -741 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 13.8% | -707 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 5.2% | -572 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 2.2% | -857 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | RealD 3D | 9:25pm | 0.5% | -807 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 1.4% | -692 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | RealD 3D | 6:35pm | 9.2% | -636 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:10pm | 2.8% | -552 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:10pm | 30% | -792 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:10pm | 64.8% | -732 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:40pm | 63.9% | -702 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:25pm | 60% | -627 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 61.5% | -572 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 52.8% | -542 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 2.2% | -842 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 8:35pm | 25.8% | -756 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 32.3% | -677 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 9.1% | -602 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 14.9% | -857 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 54.3% | -692 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 11:00pm | 22.4% | -902 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:30pm | 69% | -752 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:00pm | 67.2% | -602 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | IMAX at AMC | 9:00pm | 2.4% | -781 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | IMAX at AMC | 6:00pm | 26.5% | -601 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 14.8% | -841 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 65.8% | -661 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 1.1% | -811 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 2.2% | -796 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 12.4% | -721 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 1.5% | -616 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 7.4% | -541 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 7.1% | -631 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 6.3% | -886 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 22.7% | -856 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 55% | -721 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 71.9% | -691 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 50% | -556 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 11:15pm | 0% | -916 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -841 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 14.6% | -826 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 12.2% | -751 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 9.4% | -676 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 43.8% | -661 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 25.5% | -586 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:15pm | 46.3% | -796 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:30pm | 83.3% | -631 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 48.8% | -811 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 76.1% | -631 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | XL at AMC | 11:00pm | 1% | -901 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 10.9% | -721 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 11:35pm | 2.2% | -935 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 11:20pm | 0% | -920 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 10:50pm | 0% | -890 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 10:25pm | 0% | -866 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 9.2% | -751 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 20.9% | -736 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 7:50pm | 18% | -710 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 8.4% | -646 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 6:10pm | 14.6% | -611 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 16.8% | -571 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 3.4% | -556 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -841 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 3.9% | -781 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 9.8% | -661 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 3.9% | -601 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 2% | -541 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 8:45pm | 0% | -766 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 56.3% | -841 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:15pm | 71.5% | -676 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 22% | -886 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 65.3% | -721 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 56.7% | -556 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 13.6% | -871 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 60.2% | -691 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 64% | -631 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 4.1% | -781 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 9.6% | -736 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | RealD 3D | 5:35pm | 34.2% | -575 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 16.1% | -931 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 68.9% | -766 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 78.3% | -601 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 22.9% | -856 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 69.2% | -691 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -901 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -886 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 4.4% | -871 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 11.1% | -841 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 33.7% | -796 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 58.1% | -721 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 59.4% | -631 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 24.3% | -571 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 49.5% | -556 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 11:15pm | 0% | -916 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -826 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 17.4% | -751 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 26.6% | -661 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 11% | -586 min |
| AMC Puente Hills 20 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 8:15pm | 2.7% | -736 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | IMAX at AMC | 10:45pm | 2.4% | -885 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 59.6% | -720 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | IMAX at AMC | 5:15pm | 36.8% | -555 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 44.1% | -825 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 66.5% | -660 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 35.9% | -840 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 66.3% | -765 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 59.1% | -675 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 61.2% | -600 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 3.4% | -855 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -795 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 32.9% | -735 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 41.6% | -690 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 10.6% | -570 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 38.8% | -630 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:55pm | 20.5% | -835 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 60% | -750 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 77.8% | -660 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:35pm | 57.8% | -574 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | RealD 3D | 10:25pm | 2.2% | -865 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | RealD 3D | 9:25pm | 4.4% | -805 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 44.4% | -690 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 42.9% | -630 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 45.7% | -840 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | Laser at AMC | 8:40pm | 69.2% | -760 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:10pm | 74.1% | -670 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | Laser at AMC | 6:25pm | 67.5% | -625 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 10:45pm | 0% | -885 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 23.1% | -795 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 45.7% | -720 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 5:50pm | 30.8% | -589 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 12.8% | -550 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 7.8% | -824 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 22.1% | -764 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 60.3% | -659 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 3.4% | -869 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 34.5% | -704 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 34% | -629 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 26.5% | -599 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 18.1% | -539 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 9.2% | -854 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 49.7% | -689 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -884 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 5.3% | -629 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 0% | -554 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 7.3% | -749 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 8.1% | -584 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 13.6% | -869 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 60.7% | -704 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 24.8% | -539 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -839 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 2.1% | -674 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -824 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 2% | -779 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 5.9% | -689 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 5.6% | -659 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 5.4% | -749 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 8.3% | -584 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:15pm | 0% | -614 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 19.5% | -823 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 72.3% | -658 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -898 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -808 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 15.4% | -793 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 30% | -733 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 14% | -643 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -853 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 21.7% | -688 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 13.5% | -628 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 30.3% | -793 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 44.1% | -628 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0.7% | -823 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0.7% | -763 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 21.8% | -658 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 4% | -598 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0.4% | -733 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 3.8% | -703 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 1.9% | -568 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:00pm | 3.4% | -538 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 7.6% | -793 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 33.8% | -628 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0.9% | -838 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 2.2% | -673 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -778 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 0% | -703 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 0% | -538 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0% | -763 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0.9% | -598 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 24.6% | -778 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 37.9% | -598 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 47.3% | -628 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 25.6% | -538 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 3.5% | -868 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 31.4% | -703 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 9:30pm | 3.3% | -808 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 7:15pm | 10.1% | -673 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 57.8% | -777 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 66.4% | -612 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 19.4% | -837 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 65.8% | -672 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -897 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -867 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 25% | -732 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 33.9% | -702 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 17.9% | -567 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 17.4% | -537 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 10.2% | -807 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 17.6% | -642 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -837 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 12.5% | -777 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 28.9% | -717 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 23.9% | -657 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 19.3% | -597 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 27.3% | -852 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 74.1% | -687 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -822 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 1.1% | -777 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 0% | -732 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 13.9% | -717 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 5.1% | -657 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 5% | -612 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 1% | -567 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 10:45pm | 0% | -882 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -807 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0% | -762 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 5.4% | -642 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0% | -597 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 3.6% | -552 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 12.6% | -867 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 66.7% | -702 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 47% | -537 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | XL at AMC | 8:45pm | 11.4% | -762 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | XL at AMC | 6:00pm | 28.6% | -597 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 6% | -837 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 9.1% | -792 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 32.7% | -672 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 29.5% | -612 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 6.6% | -732 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 4.4% | -567 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -836 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 23.4% | -806 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 3.3% | -746 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 16.1% | -731 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 21.2% | -671 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 10.6% | -641 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 13.4% | -566 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 1.4% | -536 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -866 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 1.2% | -776 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 16.7% | -701 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 20.9% | -611 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -896 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 2.3% | -851 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 4.6% | -791 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 28.5% | -761 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 66.3% | -686 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 63.2% | -626 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 0% | -566 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | RealD 3D | 10:45pm | 1.2% | -881 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 36% | -716 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 29.2% | -596 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 32.6% | -551 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | undefined | 9:45pm | 9.8% | -821 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | undefined | 7:00pm | 67.5% | -656 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 14.5% | -805 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 65.6% | -640 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -835 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 13.8% | -670 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -865 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 2.7% | -745 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 7.5% | -700 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 8.2% | -580 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 8% | -535 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -775 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 4.7% | -610 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:30pm | 4.4% | -805 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:45pm | 19.6% | -640 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:00pm | 7.5% | -895 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:30pm | 60.2% | -745 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:45pm | 57.9% | -580 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -835 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 3.3% | -670 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -880 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 1.6% | -775 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 16% | -715 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 22.2% | -550 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -865 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -700 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 4.2% | -610 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -535 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 7.6% | -805 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:40pm | 52.9% | -695 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 63.1% | -670 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 81.6% | -610 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 50% | -535 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 2.6% | -775 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 43.8% | -730 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 69.7% | -640 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 52.1% | -565 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 26.6% | -820 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 71.6% | -655 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | PRIME at AMC | 10:45pm | 4.9% | -880 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | PRIME at AMC | 8:00pm | 26.8% | -715 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | PRIME at AMC | 5:15pm | 22% | -550 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 2.4% | -850 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 0% | -790 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 11% | -760 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 35.7% | -685 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 8.9% | -625 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 8.8% | -595 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 16.3% | -834 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 63.9% | -684 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 54.4% | -534 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | XL at AMC | 10:30pm | 1.8% | -864 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | XL at AMC | 5:30pm | 12.3% | -564 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -879 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 6% | -819 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -774 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 2.1% | -669 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 8.4% | -624 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:10pm | 2.5% | -604 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 1% | -804 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 2.8% | -714 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 2.9% | -654 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 1.5% | -744 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 2.6% | -579 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | undefined | 10:15pm | 4.5% | -849 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | undefined | 7:30pm | 16.2% | -684 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:00pm | 1.1% | -894 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:30pm | 21.1% | -744 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 31.8% | -594 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 16.4% | -804 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 60.3% | -654 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -834 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 10.6% | -774 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 28.8% | -699 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 23.6% | -684 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 29.5% | -669 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 41.5% | -624 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 13.6% | -609 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 17.8% | -549 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 11.4% | -534 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -864 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 3.3% | -714 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 32.2% | -564 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 30.9% | -789 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 52% | -624 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | XL at AMC | 10:45pm | 0% | -879 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 9.5% | -714 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | XL at AMC | 5:15pm | 3.2% | -549 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -864 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0.6% | -819 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 4.3% | -654 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0% | -759 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0.9% | -699 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 8.5% | -594 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 10:20pm | 3.2% | -854 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 9:10pm | 25% | -784 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:40pm | 17.3% | -694 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 46.8% | -654 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 30.8% | -534 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | RealD 3D | 9:40pm | 1.4% | -814 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | RealD 3D | 8:10pm | 14.9% | -724 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 29.9% | -564 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 20.8% | -864 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 67.2% | -699 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 66.4% | -534 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -834 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 33.3% | -744 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 43.2% | -669 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 43.2% | -579 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 11.7% | -789 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 29.8% | -624 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 3.5% | -848 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -743 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 5.8% | -683 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 4.6% | -578 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0% | -878 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -863 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0.2% | -818 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -803 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 8:00pm | 4.8% | -713 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 7:00pm | 4.3% | -653 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 4% | -638 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 6:15pm | 12.5% | -608 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 5:15pm | 6.3% | -548 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 0.7% | -773 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 16.2% | -608 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 3% | -863 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 53.8% | -698 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 50% | -533 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -878 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -833 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 4.4% | -743 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 23.8% | -683 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 27.4% | -668 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 15.6% | -578 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -893 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 7.3% | -803 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -728 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 8.3% | -638 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 1.9% | -563 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 12.9% | -758 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 25.2% | -593 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 2% | -863 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 43.7% | -698 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 12.2% | -533 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -833 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 3.5% | -803 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 26.1% | -668 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 16% | -638 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -818 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 7.9% | -728 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 30.4% | -653 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 41.3% | -563 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:15pm | 24.3% | -788 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | PRIME at AMC | 9:45pm | 4.3% | -817 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | PRIME 3D | 7:00pm | 47.3% | -652 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 4.4% | -862 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 8.3% | -847 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 6.6% | -802 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 16.7% | -742 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 13.2% | -727 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 31.9% | -697 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 57.3% | -682 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 49.5% | -637 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 59.4% | -577 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 37.4% | -562 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 17.6% | -532 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 4.4% | -772 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 6.3% | -712 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 3.3% | -607 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 28.1% | -547 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 2.2% | -922 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 11.8% | -757 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 14.8% | -592 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 13.7% | -847 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 34.5% | -682 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -892 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -877 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -772 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 0% | -727 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 6.7% | -712 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 0% | -562 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 0% | -547 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 11:15pm | 0% | -907 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -832 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 1.3% | -742 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 0% | -667 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 1.8% | -577 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | English Spoken with Spanish Subtitles | 6:15pm | 1.3% | -607 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:40pm | 19.4% | -812 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 71% | -652 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:40pm | 0% | -872 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:25pm | 0% | -797 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:40pm | 22.2% | -752 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 29.7% | -712 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 47.9% | -637 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 48.9% | -592 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:50pm | 29.5% | -582 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:20pm | 31% | -552 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 44.6% | -727 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | RealD 3D | 5:35pm | 23.2% | -567 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:15pm | 21% | -786 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:30pm | 62.9% | -621 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 3.1% | -846 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 22.3% | -681 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 22.2% | -756 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 25.8% | -651 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -816 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 2.8% | -726 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 14.1% | -561 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 9.5% | -816 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 73.3% | -651 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 0% | -876 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 5.2% | -786 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:50pm | 3.8% | -760 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 40% | -711 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 67.1% | -621 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 71.2% | -606 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:50pm | 42.3% | -580 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 66.5% | -546 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 45.9% | -531 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -741 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -696 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 38.5% | -666 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 24.4% | -636 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 34.1% | -591 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 36% | -771 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 78.3% | -591 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -861 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 20% | -681 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 36.5% | -546 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 11:15pm | 6.8% | -906 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 11:45pm | 0% | -936 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 10:30pm | 0% | -861 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 10:00pm | 2.2% | -831 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:45pm | 0% | -816 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:15pm | 17.8% | -786 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:15pm | 48.6% | -726 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:45pm | 44.4% | -696 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:15pm | 61.1% | -666 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:45pm | 73.3% | -636 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:15pm | 58.7% | -606 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 1.6% | -861 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 21.8% | -696 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 33% | -531 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 13.2% | -801 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 80.8% | -636 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 12.9% | -771 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 46.3% | -741 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 54.8% | -606 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 63.2% | -576 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 23.2% | -666 min |

**Issues:** AMC Century City 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Century City 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Century City 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie SCREENX at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie SCREENX at AMC; AMC The Americana at Brand 18: No showtimes retrieved; AMC Santa Monica 7: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Santa Monica 7: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC The Regency 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Lakewood Mall 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Orange 30: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Orange 30: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Metreon 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Metreon 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Bay Street 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Bay Street 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mercado 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mercado 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mercado 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Eastridge 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Eastridge 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Saratoga 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Saratoga 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Saratoga 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC NewPark 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC NewPark 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mission Valley 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mission Valley 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Palm Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Palm Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Chula Vista 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Poway 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Southcenter 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Southcenter 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Southcenter 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Alderwood Mall 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Alderwood Mall 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Westminster Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Westminster Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Highlands Ranch 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Highlands Ranch 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC

---

## 2026-04-04 03:41 — ET Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie, The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 22.8% | -1052 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 57.7% | -872 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 0% | -1147 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 32.6% | -947 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 9:35pm | 0% | -1087 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 9:00pm | 3.7% | -1052 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 7:45pm | 45.6% | -976 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 6:15pm | 18.4% | -887 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 57.9% | -812 min |
| AMC Kips Bay 15 | The Drama | undefined | 11:35pm | 0% | -1207 min |
| AMC Kips Bay 15 | The Drama | undefined | 11:15pm | 0% | -1187 min |
| AMC Kips Bay 15 | The Drama | undefined | 10:30pm | 3.5% | -1142 min |
| AMC Kips Bay 15 | The Drama | undefined | 10:00pm | 4.3% | -1112 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:45pm | 22.1% | -1097 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:15pm | 68.4% | -1067 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:00pm | 73.9% | -991 min |
| AMC Kips Bay 15 | The Drama | undefined | 7:00pm | 66.9% | -932 min |
| AMC Kips Bay 15 | The Drama | undefined | 6:30pm | 77.2% | -902 min |
| AMC Kips Bay 15 | The Drama | undefined | 5:15pm | 69.6% | -827 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:40pm | 26.1% | -1092 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 52.9% | -932 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:25pm | 60.6% | -897 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 43.2% | -976 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 45.9% | -812 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 11:00pm | 1.8% | -1172 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 10:30pm | 10.1% | -1142 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 10:15pm | 4.1% | -1127 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 9:30pm | 15.4% | -1082 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 9:00pm | 56.9% | -1052 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 7:45pm | 75.4% | -976 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:45pm | 68.3% | -917 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:15pm | 52.9% | -887 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:00pm | 65.2% | -812 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 9.4% | -1097 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 58.8% | -932 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 4.3% | -1052 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 41.6% | -872 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:45pm | 0% | -1157 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:00pm | 12.3% | -1112 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 8:00pm | 61.5% | -991 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 7:30pm | 37.4% | -961 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 7:15pm | 76.3% | -947 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 10% | -1112 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 10% | -1037 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 23% | -947 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 52.2% | -872 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 4.1% | -1172 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 9.9% | -1067 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 13.3% | -1006 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 27.5% | -902 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 19.4% | -842 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 10:30pm | 25.7% | -1142 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 9:00pm | 35.4% | -1052 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 7:45pm | 70% | -976 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 6:15pm | 64.6% | -887 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 5:35pm | 34.3% | -846 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 5:00pm | 67.1% | -812 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 8% | -1111 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 60.3% | -946 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 10:30pm | 2.7% | -1141 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 7:45pm | 66.8% | -976 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 5:00pm | 77.5% | -811 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 6.9% | -1171 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 6.5% | -1051 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 37.9% | -1006 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 26.4% | -961 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 34.7% | -886 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 65.5% | -841 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -1096 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 2.2% | -1081 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 26.3% | -931 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 12.2% | -916 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 10:00pm | 0% | -1111 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 10:15pm | 27.1% | -1126 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 9:30pm | 4.2% | -1081 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 7:15pm | 81.4% | -946 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 6:00pm | 19.6% | -871 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 9:45pm | 1.8% | -1095 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 40.5% | -930 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 21.7% | -990 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 30.8% | -960 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 58.5% | -825 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 6.6% | -1145 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 11% | -1035 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 27% | -870 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 10:30pm | 8.9% | -1140 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 7:40pm | 72.2% | -970 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 6.3% | -1140 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 24.6% | -1020 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 36.3% | -960 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 19.7% | -945 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 62.3% | -840 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 1.4% | -1110 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 6.3% | -1080 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 29% | -930 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 36.3% | -900 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 9:45pm | 21.7% | -1095 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 6:45pm | 59.8% | -915 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 1.4% | -1155 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 26.9% | -990 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 65.5% | -810 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 0% | -1125 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 11.1% | -1050 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 58.5% | -870 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0% | -1035 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 32.5% | -960 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 10% | -885 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 9.9% | -840 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 11.1% | -900 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 10:20pm | 4% | -1130 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:30pm | 34.6% | -1080 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:10pm | 32% | -880 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 10:45pm | 0% | -1155 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 10:00pm | 11.1% | -1110 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 9:30pm | 1.2% | -1080 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 8:30pm | 17.3% | -1020 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 7:15pm | 50.6% | -945 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 6:40pm | 12.3% | -910 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 5:45pm | 14.8% | -855 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:15pm | 0% | -1004 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:35pm | 8.6% | -844 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | PRIME at AMC | 9:40pm | 12.3% | -1089 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 10.5% | -929 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:20pm | 0% | -1129 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 5.9% | -974 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 12% | -899 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:10pm | 17.8% | -819 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | RealD 3D | 8:40pm | 0% | -1029 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 6.4% | -869 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 10:20pm | 0% | -1129 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 10:00pm | 12.1% | -1109 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 9:05pm | 0% | -1054 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 7:15pm | 45.5% | -944 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 8% | -1079 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 38.5% | -914 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -1109 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0% | -869 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -1139 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -1049 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:45pm | 1% | -1034 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 8:15pm | 4.5% | -1004 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -974 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 7:15pm | 3.4% | -944 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -839 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 3.1% | -809 min |
| AMC West Shore 14 | The Drama | undefined | 10:00pm | 0% | -1109 min |
| AMC West Shore 14 | The Drama | undefined | 7:15pm | 7% | -944 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:00pm | 32% | -1168 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:15pm | 84.2% | -1003 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:30pm | 86.1% | -838 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 7.2% | -1108 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 4.7% | -1093 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 4.3% | -1078 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 32.3% | -1018 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 40.5% | -928 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 17.8% | -913 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 23.1% | -823 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 10:45pm | 1.4% | -1153 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 32.4% | -1063 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 13% | -943 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 72.5% | -898 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 12.9% | -853 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:00pm | 20.7% | -868 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 10:30pm | 28.4% | -1138 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:00pm | 30.6% | -988 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:45pm | 74.5% | -973 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:45pm | 52.2% | -853 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:00pm | 87.3% | -808 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 11:00pm | 5.7% | -1168 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 9:00pm | 0.9% | -1048 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 8:15pm | 38.5% | -1003 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 5:30pm | 29.5% | -838 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 10:00pm | 73.9% | -1108 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 7:15pm | 88.4% | -943 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:00pm | 1.9% | -1168 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:15pm | 16% | -1003 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:30pm | 26.4% | -838 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 12.2% | -973 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -1138 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 9.1% | -913 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 9.5% | -808 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 10:15pm | 12.2% | -1123 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 10:00pm | 0% | -1108 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 9:30pm | 21.2% | -1078 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 8:30pm | 56.8% | -1018 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 8:10pm | 53.3% | -998 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:30pm | 79.6% | -958 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:15pm | 1.4% | -943 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 5:45pm | 62.2% | -853 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -1138 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 8:10pm | 15.1% | -998 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 36.9% | -913 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 4.8% | -1078 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 10:00pm | 7.8% | -1108 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 7:10pm | 51% | -938 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -1092 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 2.9% | -987 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 13% | -822 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 10:20pm | 0% | -1127 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 9:00pm | 5% | -1047 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -972 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 7:00pm | 1.6% | -927 min |
| AMC Worldgate 9 | The Drama | undefined | 10:15pm | 0% | -1122 min |
| AMC Worldgate 9 | The Drama | undefined | 7:30pm | 4.6% | -957 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 34.1% | -1047 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 50.3% | -867 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 5.1% | -1092 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 22.6% | -927 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -1107 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 0% | -1062 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 0% | -1002 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 0% | -987 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -957 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 0.5% | -942 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 0% | -897 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 0% | -822 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 1% | -807 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 4.5% | -1017 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 2.8% | -837 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 9:30pm | 2% | -1077 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 6:45pm | 7.3% | -912 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 26.9% | -1047 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 42.5% | -882 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 22.2% | -987 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 17.8% | -822 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -1077 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 2.7% | -957 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 0% | -912 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -1062 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0.3% | -1017 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 2.7% | -897 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 1.4% | -852 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:00pm | 33.7% | -807 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 9:15pm | 10.5% | -1062 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 7:30pm | 8.7% | -957 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 8:10pm | 0% | -997 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 1.8% | -837 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 10:10pm | 1.2% | -1117 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -1092 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:25pm | 0% | -1072 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0.2% | -1047 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:30pm | 1.8% | -957 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:05pm | 1.9% | -931 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -912 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:20pm | 3.6% | -886 min |
| AMC Voorhees 16 | The Drama | undefined | 9:50pm | 0% | -1097 min |
| AMC Voorhees 16 | The Drama | undefined | 7:00pm | 2.4% | -927 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:50pm | 11.6% | -1096 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 61.6% | -926 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 10:50pm | 0% | -1156 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 8:00pm | 4% | -986 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 5:10pm | 27.5% | -816 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 6:10pm | 4.7% | -876 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 10:20pm | 38.9% | -1126 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 9:00pm | 3.9% | -1046 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 8:25pm | 51.5% | -1011 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 7:30pm | 0% | -956 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 7:20pm | 77.9% | -946 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 5:20pm | 71.6% | -826 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 0.9% | -1151 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 32.7% | -986 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 21.2% | -821 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 3.3% | -1121 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 6.5% | -1091 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 23.3% | -956 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 8.7% | -926 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 32.3% | -896 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 11:15pm | 0% | -1181 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0% | -1031 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0% | -836 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 10:45pm | 2.2% | -1151 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 9:45pm | 4.8% | -1091 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 8:15pm | 16.5% | -1001 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 7:45pm | 39% | -971 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 6:15pm | 26.5% | -881 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 5:00pm | 12.4% | -806 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 8.2% | -1091 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 23.3% | -926 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 13.3% | -866 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | undefined | 8:45pm | 13.3% | -1031 min |
| AMC Northlake 14 | The Drama | undefined | 10:35pm | 0% | -1141 min |
| AMC Northlake 14 | The Drama | undefined | 7:50pm | 41.8% | -976 min |
| AMC Northlake 14 | The Drama | undefined | 5:05pm | 12.7% | -811 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 1.3% | -1030 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 3.9% | -1000 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 2.4% | -940 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 1.3% | -865 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 6.7% | -835 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 9:30pm | 4.7% | -1075 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 9:00pm | 3.6% | -1045 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 3.6% | -970 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 6:45pm | 4.7% | -910 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 6:15pm | 2.9% | -880 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 5.7% | -805 min |
| AMC Camp Creek 14 | The Drama | undefined | 10:00pm | 0% | -1105 min |
| AMC Camp Creek 14 | The Drama | undefined | 7:15pm | 0% | -940 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:45pm | 0% | -1210 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 4.4% | -1045 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 26.5% | -880 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 3.2% | -1075 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 7.4% | -910 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -805 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 11:00pm | 0% | -1165 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:15pm | 12.6% | -1000 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:45pm | 0% | -970 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:30pm | 6.8% | -835 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 10:45pm | 1.8% | -1150 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 9:45pm | 7.4% | -1090 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 8:30pm | 3.6% | -1015 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 7:00pm | 49.4% | -925 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 5:45pm | 5.4% | -850 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 11:10pm | 1.3% | -1174 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 1.1% | -1134 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 2.7% | -1104 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 9:50pm | 3.4% | -1093 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 17.3% | -1013 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 7:40pm | 1.1% | -964 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 2.3% | -924 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 10:40pm | 3.4% | -1144 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -1074 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:10pm | 15.7% | -1054 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 8:00pm | 11.5% | -983 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 7:20pm | 43.8% | -944 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:40pm | 20% | -904 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:20pm | 32.6% | -884 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 5:40pm | 25.3% | -844 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 5:20pm | 17.2% | -824 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 10:10pm | 0% | -1114 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 9:10pm | 9.6% | -1054 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 7:15pm | 37% | -939 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 6:15pm | 5.5% | -879 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 8.1% | -1044 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 16.7% | -864 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 4.9% | -1134 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 64.2% | -954 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -1164 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 3.4% | -1104 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -983 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 9.4% | -924 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 2.3% | -804 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 17% | -1074 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 8:20pm | 58.3% | -1003 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:10pm | 47.9% | -934 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 6:30pm | 38.9% | -894 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 24.1% | -834 min |
| AMC Concord Mills 24 | The Drama | undefined | 10:15pm | 0% | -1119 min |
| AMC Concord Mills 24 | The Drama | undefined | 9:15pm | 10.5% | -1059 min |
| AMC Concord Mills 24 | The Drama | undefined | 8:15pm | 18% | -998 min |
| AMC Concord Mills 24 | The Drama | undefined | 7:15pm | 38.8% | -939 min |
| AMC Concord Mills 24 | The Drama | undefined | 6:15pm | 7% | -879 min |
| AMC Concord Mills 24 | The Drama | undefined | 5:15pm | 18% | -819 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | IMAX at AMC | 9:45pm | 4.3% | -1089 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 13.2% | -924 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 3.6% | -1119 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 8.2% | -1013 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 3.6% | -954 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 4.5% | -849 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 3.4% | -894 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0.9% | -1149 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 3.4% | -1059 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 8:15pm | 4.5% | -998 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 8:00pm | 1.7% | -983 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 5:30pm | 5.9% | -834 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 5:15pm | 0.9% | -819 min |
| AMC Livonia 20 | The Drama | undefined | 10:45pm | 4.1% | -1149 min |
| AMC Livonia 20 | The Drama | undefined | 7:45pm | 5.5% | -968 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 4.2% | -1104 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 3.4% | -939 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 6.6% | -834 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -1134 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -1074 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 8:45pm | 9.9% | -1029 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -968 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 6:45pm | 2.5% | -909 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0% | -864 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 3.4% | -804 min |
| AMC John R 15 | The Drama | undefined | 10:05pm | 19.3% | -1108 min |
| AMC John R 15 | The Drama | undefined | 7:20pm | 38.6% | -944 min |
| AMC John R 15 | The Drama | undefined | 5:10pm | 0% | -814 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 16.9% | -968 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 8.2% | -803 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 17.2% | -1073 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 60.9% | -908 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 0.5% | -1118 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 41% | -953 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -1088 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0.4% | -998 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0.9% | -833 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:00pm | 1.4% | -863 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 10:30pm | 1.1% | -1133 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 9:15pm | 2.3% | -1058 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:45pm | 3.5% | -1028 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 7:00pm | 2.5% | -923 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 6:30pm | 2.3% | -893 min |
| AMC Perry Crossing 18 | The Drama | undefined | 10:00pm | 0.4% | -1103 min |
| AMC Perry Crossing 18 | The Drama | undefined | 7:45pm | 4.3% | -968 min |
| AMC Perry Crossing 18 | The Drama | undefined | 5:00pm | 0.9% | -803 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0% | -1102 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 34.1% | -952 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 23.9% | -802 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -1012 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 2.3% | -982 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0% | -862 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 2.3% | -832 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -1072 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -1042 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 7:00pm | 6.1% | -922 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 6:30pm | 21.5% | -892 min |
| AMC Bellevue 12 | The Drama | undefined | 9:15pm | 13% | -1057 min |
| AMC Bellevue 12 | The Drama | undefined | 6:15pm | 34.8% | -877 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | IMAX at AMC | 9:45pm | 3.5% | -1087 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 22.1% | -922 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 5.2% | -802 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -1132 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 10:00pm | 0% | -1102 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 9:15pm | 1.3% | -1057 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 8:30pm | 1.7% | -1012 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0.9% | -967 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 7:15pm | 1.9% | -937 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 6:30pm | 6.4% | -892 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 5:45pm | 10% | -847 min |
| AMC Grove City 14 | The Drama | undefined | 10:00pm | 0% | -1102 min |
| AMC Grove City 14 | The Drama | undefined | 7:15pm | 3.7% | -937 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 8.5% | -967 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 1.2% | -802 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0% | -1072 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 7.4% | -907 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 1.7% | -1042 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -997 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 3.9% | -877 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0% | -832 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 10:00pm | 0% | -1102 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 8:30pm | 1.1% | -1012 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 7:15pm | 2.5% | -937 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 5:45pm | 2.2% | -847 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 10:15pm | 3.7% | -1117 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 7:20pm | 42.5% | -942 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 6:10pm | 20.4% | -872 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 11:00pm | 2.7% | -1161 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 8:15pm | 6.4% | -996 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 5:30pm | 19.3% | -831 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 4.6% | -1101 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 50.3% | -936 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 3.8% | -1131 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 6% | -966 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 2.6% | -861 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 12% | -801 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 9:15pm | 19.6% | -1056 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 8:45pm | 11.7% | -1026 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 6:30pm | 65.2% | -891 min |
| AMC West Chester 18 | The Drama | undefined | 10:05pm | 7.9% | -1106 min |
| AMC West Chester 18 | The Drama | undefined | 7:00pm | 56.6% | -921 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | IMAX at AMC | 9:00pm | 0.7% | -1041 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | IMAX at AMC | 6:15pm | 1.4% | -876 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 2.1% | -1101 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 16.6% | -936 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 4.7% | -966 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 7.5% | -801 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -1116 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -1071 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 8:45pm | 7.5% | -1026 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 8:15pm | 0% | -996 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -951 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 6:45pm | 5.9% | -906 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 6:00pm | 15.9% | -861 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 8.7% | -831 min |
| AMC Orange Park 24 | The Drama | undefined | 10:30pm | 0% | -1131 min |
| AMC Orange Park 24 | The Drama | undefined | 9:45pm | 0% | -1086 min |
| AMC Orange Park 24 | The Drama | undefined | 8:45pm | 0% | -1026 min |
| AMC Orange Park 24 | The Drama | undefined | 8:15pm | 4.3% | -996 min |
| AMC Orange Park 24 | The Drama | undefined | 7:00pm | 11.8% | -921 min |
| AMC Orange Park 24 | The Drama | undefined | 6:30pm | 0% | -891 min |
| AMC Orange Park 24 | The Drama | undefined | 5:30pm | 0% | -831 min |

**Issues:** AMC Empire 25: No showtimes retrieved; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Newport Centre 11: No seat map for The Drama Laser at AMC; AMC Magic Johnson Harlem 9: No showtimes retrieved; AMC Boston Common 19: No showtimes retrieved; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Assembly Row 12: No seat map for The Drama Laser at AMC; AMC Assembly Row 12: No seat map for The Drama Laser at AMC; AMC Assembly Row 12: No seat map for The Drama Laser at AMC; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Aventura 24: No showtimes retrieved; AMC Sunset Place 24: No showtimes retrieved; AMC DINE-IN Coral Ridge 10: No showtimes retrieved; AMC Pembroke Lakes 9: No showtimes retrieved; AMC Pompano Beach 18: No showtimes retrieved; AMC Veterans 24: No showtimes retrieved; AMC West Shore 14: No seat map for The Drama undefined; AMC Bradenton 20: No showtimes retrieved; AMC Altamonte Mall 18: No showtimes retrieved; AMC Tysons Corner 16: No showtimes retrieved; AMC Hoffman Center 22: No showtimes retrieved; AMC Georgetown 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Georgetown 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Plymouth Meeting Mall 12: No showtimes retrieved; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Sugarloaf Mills 18: No showtimes retrieved; AMC Barrett Commons 24: No showtimes retrieved; AMC Camp Creek 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN North Point Mall 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC DINE-IN North Point Mall 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Highwoods 20: Page.evaluate: Execution context was destroyed, most likely because of a navigation; AMC Forum 30: Page.evaluate: Execution context was destroyed, most likely because of a navigation; AMC Star Great Lakes 25: No showtimes retrieved; AMC Castleton Square 14: No showtimes retrieved; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie Open Caption (On-screen Subtitles); AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie undefined; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie undefined; AMC Indianapolis 17: No seat map for The Drama undefined; AMC Indianapolis 17: No seat map for The Drama undefined; AMC Indianapolis 17: No seat map for The Drama undefined; AMC Indianapolis 17: No seat map for The Drama undefined; AMC Thoroughbred 20: No showtimes retrieved; AMC CLASSIC Murfreesboro 16: No showtimes retrieved; AMC Easton Town Center 30: No showtimes retrieved; AMC Dublin Village 18: No showtimes retrieved; AMC Newport On The Levee 20: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Waterfront 22: No showtimes retrieved; AMC Regency 24: No showtimes retrieved

---

## 2026-04-05 03:08 — ET Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie, The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:30pm | 13.6% | -1224 min |
| AMC Kips Bay 15 | The Drama | undefined | 11:35pm | 2.5% | -1228 min |
| AMC Kips Bay 15 | The Drama | undefined | 11:15pm | 21.7% | -1209 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 11:00pm | 19.3% | -1194 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:45pm | 5.6% | -1179 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 19.4% | -1194 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 11:10pm | 26.7% | -1204 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 33.6% | -1194 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 4.8% | -1179 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 10:45pm | 4.8% | -1179 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:45pm | 10.6% | -1179 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 56.8% | -1179 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:45pm | 29% | -1179 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:40pm | 11.6% | -1174 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:00pm | 71.1% | -1194 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 10:45pm | 33.3% | -1179 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 11:00pm | 23.8% | -1194 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:00pm | 14.2% | -1194 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 10:50pm | 8.1% | -1183 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 10.6% | -1178 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 11:15pm | 7.1% | -1208 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 10:45pm | 33% | -1178 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 11:00pm | 4.6% | -1193 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 10:45pm | 4.1% | -1178 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 17% | -1223 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 10:45pm | 15.5% | -1178 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 11:30pm | 8.9% | -1223 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 11:15pm | 9.3% | -1208 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:45pm | 2.2% | -1238 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 11:00pm | 16.5% | -1193 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 11:20pm | 12.5% | -1213 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 10:45pm | 14.3% | -1178 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 11:10pm | 4% | -1203 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 10:40pm | 12.6% | -1173 min |
| AMC Concord Mills 24 | The Drama | undefined | 11:15pm | 20.4% | -1208 min |
| AMC Livonia 20 | The Drama | undefined | 10:45pm | 9.1% | -1178 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 8.3% | -1118 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:30pm | 2% | -1223 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 5.4% | -1163 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 8.8% | -1133 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0% | -1178 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 10:15pm | 1.9% | -1148 min |
| AMC Thoroughbred 20 | The Drama | undefined | 10:30pm | 8.8% | -1163 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 10:45pm | 18.3% | -1178 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 11:00pm | 15.3% | -1192 min |

**Issues:** AMC Empire 25: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC Lincoln Square 13: 'The Drama' not showing or no started shows; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 84th Street 6: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC Magic Johnson Harlem 9: No showtimes retrieved; AMC Boston Common 19: No showtimes retrieved; AMC Assembly Row 12: 'The Drama' not showing or no started shows; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Framingham 16: 'The Drama' not showing or no started shows; AMC Braintree 10: No showtimes retrieved; AMC Burlington Cinema 10: No showtimes retrieved; AMC Aventura 24: 'The Drama' not showing or no started shows; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Sunset Place 24: 'The Drama' not showing or no started shows; AMC DINE-IN Coral Ridge 10: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC DINE-IN Coral Ridge 10: 'The Drama' not showing or no started shows; AMC Pembroke Lakes 9: No showtimes retrieved; AMC Pompano Beach 18: No showtimes retrieved; AMC Sundial 12: No showtimes retrieved; AMC West Shore 14: No showtimes retrieved; AMC Bradenton 20: No showtimes retrieved; AMC Altamonte Mall 18: No showtimes retrieved; AMC Tysons Corner 16: 'The Drama' not showing or no started shows; AMC Tysons Corner 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Hoffman Center 22: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC Hoffman Center 22: No seat map for The Drama Laser at AMC; AMC Georgetown 14: 'The Drama' not showing or no started shows; AMC Shirlington 7: No showtimes retrieved; AMC Worldgate 9: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC Worldgate 9: 'The Drama' not showing or no started shows; AMC Neshaminy 24: No showtimes retrieved; AMC Cherry Hill 24: No showtimes retrieved; AMC Voorhees 16: No showtimes retrieved; AMC Plymouth Meeting Mall 12: No showtimes retrieved; AMC DINE-IN Fashion District 8: 'The Drama' not showing or no started shows; AMC Northlake 14: 'The Drama' not showing or no started shows; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Sugarloaf Mills 18: 'The Drama' not showing or no started shows; AMC Camp Creek 14: No showtimes retrieved; AMC Highwoods 20: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Carolina Pavilion 22: 'The Drama' not showing or no started shows; AMC Concord Mills 24: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC Forum 30: No showtimes retrieved; AMC Star Great Lakes 25: No showtimes retrieved; AMC Livonia 20: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC John R 15: No showtimes retrieved; AMC Castleton Square 14: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC Castleton Square 14: 'The Drama' not showing or no started shows; AMC Indianapolis 17: No showtimes retrieved; AMC Perry Crossing 18: No showtimes retrieved; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Drama undefined; AMC Bellevue 12: No showtimes retrieved; AMC Easton Town Center 30: No showtimes retrieved; AMC Dublin Village 18: 'The Drama' not showing or no started shows; AMC Grove City 14: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC Grove City 14: 'The Drama' not showing or no started shows; AMC Newport On The Levee 20: No showtimes retrieved; AMC West Chester 18: 'The Drama' not showing or no started shows; AMC Waterfront 22: No showtimes retrieved; AMC Regency 24: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC Regency 24: 'The Drama' not showing or no started shows; AMC Orange Park 24: No showtimes retrieved

---

## 2026-04-05 03:51 — ET Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie, The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:30pm | 16.7% | -1180 min |
| AMC Kips Bay 15 | The Drama | undefined | 11:35pm | 11% | -1185 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 19% | -1180 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 11:30pm | 15.6% | -1180 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:45pm | 2.9% | -1195 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:30pm | 2% | -1180 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 5.4% | -1120 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0% | -1135 min |
| AMC Thoroughbred 20 | The Drama | undefined | 10:30pm | 17.6% | -1120 min |

**Issues:** AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No showtimes retrieved; AMC Kips Bay 15: 'The Super Mario Galaxy Movie' not showing or no started shows; AMC 34th Street 14: No showtimes retrieved; AMC 84th Street 6: No showtimes retrieved; AMC Newport Centre 11: No showtimes retrieved; AMC Magic Johnson Harlem 9: No showtimes retrieved; AMC Boston Common 19: No showtimes retrieved; AMC Assembly Row 12: 'The Drama' not showing or no started shows; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Framingham 16: No showtimes retrieved; AMC Braintree 10: No showtimes retrieved; AMC Burlington Cinema 10: No showtimes retrieved; AMC Methuen 20: No showtimes retrieved; AMC Aventura 24: No showtimes retrieved; AMC Sunset Place 24: No showtimes retrieved; AMC DINE-IN Coral Ridge 10: No showtimes retrieved; AMC Pembroke Lakes 9: No showtimes retrieved; AMC Pompano Beach 18: No showtimes retrieved; AMC Veterans 24: No showtimes retrieved; AMC Sundial 12: No showtimes retrieved; AMC West Shore 14: No showtimes retrieved; AMC Bradenton 20: No showtimes retrieved; AMC DINE-IN Disney Springs 24: No showtimes retrieved; AMC Altamonte Mall 18: No showtimes retrieved; AMC Tysons Corner 16: No showtimes retrieved; AMC Hoffman Center 22: No showtimes retrieved; AMC Georgetown 14: No showtimes retrieved; AMC Shirlington 7: No showtimes retrieved; AMC Worldgate 9: No showtimes retrieved; AMC Neshaminy 24: No showtimes retrieved; AMC Cherry Hill 24: No showtimes retrieved; AMC Voorhees 16: No showtimes retrieved; AMC Plymouth Meeting Mall 12: No showtimes retrieved; AMC DINE-IN Fashion District 8: No showtimes retrieved; AMC Phipps Plaza 14: No showtimes retrieved; AMC Northlake 14: No showtimes retrieved; AMC Sugarloaf Mills 18: No showtimes retrieved; AMC Camp Creek 14: No showtimes retrieved; AMC DINE-IN North Point Mall 12: 'The Drama' not showing or no started shows; AMC Highwoods 20: No showtimes retrieved; AMC Carolina Pavilion 22: No showtimes retrieved; AMC Concord Mills 24: No showtimes retrieved; AMC Forum 30: No showtimes retrieved; AMC Star Great Lakes 25: No showtimes retrieved; AMC Livonia 20: No showtimes retrieved; AMC John R 15: No showtimes retrieved; AMC Castleton Square 14: No showtimes retrieved; AMC Indianapolis 17: No showtimes retrieved; AMC Perry Crossing 18: No showtimes retrieved; AMC CLASSIC Murfreesboro 16: 'The Drama' not showing or no started shows; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC Bellevue 12: No showtimes retrieved; AMC Easton Town Center 30: No showtimes retrieved; AMC Dublin Village 18: No showtimes retrieved; AMC Grove City 14: No showtimes retrieved; AMC Newport On The Levee 20: No showtimes retrieved; AMC West Chester 18: No showtimes retrieved; AMC Waterfront 22: No showtimes retrieved; AMC Regency 24: No showtimes retrieved; AMC Orange Park 24: No showtimes retrieved

---

## 2026-04-05 11:43 — ET Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie, The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:30pm | 2% | -723 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:45pm | 11.1% | -558 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 63.6% | -393 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 6% | -573 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 33.8% | -393 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -573 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 26.1% | -468 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 10:30pm | 5.3% | -663 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 10:05pm | 0% | -638 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 7:45pm | 15.8% | -498 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 6:15pm | 11.7% | -408 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 57.9% | -333 min |
| AMC Kips Bay 15 | The Drama | undefined | 10:45pm | 5.5% | -678 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:45pm | 7.6% | -618 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:15pm | 12.8% | -588 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:50pm | 35.6% | -563 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:00pm | 69% | -513 min |
| AMC Kips Bay 15 | The Drama | undefined | 7:00pm | 77.2% | -453 min |
| AMC Kips Bay 15 | The Drama | undefined | 6:00pm | 77.2% | -393 min |
| AMC Kips Bay 15 | The Drama | undefined | 5:15pm | 76.6% | -348 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0.8% | -603 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 28.6% | -453 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:25pm | 23.9% | -418 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 2.7% | -663 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | RealD 3D | 7:50pm | 16.2% | -503 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 11:00pm | 0% | -693 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 10:30pm | 18.8% | -663 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 9:30pm | 22.1% | -603 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 8:45pm | 38.2% | -558 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 7:45pm | 60.9% | -498 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:45pm | 60.6% | -438 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:00pm | 57.4% | -393 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:30pm | 73.7% | -363 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:10pm | 56.8% | -343 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:00pm | 68.1% | -333 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 2.4% | -618 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 5.6% | -573 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 39.1% | -393 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 7:00pm | 8.2% | -453 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:45pm | 0% | -678 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:00pm | 0% | -633 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 8:00pm | 61.5% | -513 min |
| AMC 84th Street 6 | The Drama | Open Caption (On-screen Subtitles) | 7:15pm | 62.3% | -468 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 4% | -632 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 7.8% | -557 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 13% | -467 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 43.3% | -392 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 2% | -692 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -587 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 9.2% | -527 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 27.5% | -422 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 14.3% | -362 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 10:30pm | 4.3% | -662 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 9:00pm | 12.7% | -572 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 7:45pm | 55.7% | -497 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 6:15pm | 70.9% | -407 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 5:00pm | 77.1% | -332 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 8.4% | -646 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 23.4% | -481 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 2.3% | -586 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 3.1% | -421 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 2.8% | -541 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 6.7% | -376 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 10:00pm | 2% | -631 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 7:15pm | 14.9% | -466 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 7.9% | -571 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 23.7% | -406 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -631 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 1.3% | -466 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 5.4% | -526 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 0% | -361 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 1% | -346 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 4.3% | -601 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 3.8% | -436 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 10:30pm | 0.7% | -661 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 10:00pm | 3.3% | -631 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:30pm | 28.6% | -481 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:00pm | 43.2% | -451 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 0% | -676 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 11.5% | -511 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 27.6% | -346 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 10:30pm | 0% | -661 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 7:45pm | 23% | -496 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 5:00pm | 59.4% | -331 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -631 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -571 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 6.9% | -526 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 1.9% | -481 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 8.9% | -406 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 17.2% | -361 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -601 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 4.4% | -451 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 8.9% | -436 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 10:15pm | 0% | -646 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 10:15pm | 0% | -646 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 7:15pm | 47.1% | -466 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 9:45pm | 0.6% | -616 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 12.3% | -451 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 12.1% | -481 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 33% | -346 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 0% | -666 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0.6% | -556 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -511 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 11% | -391 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 10:30pm | 7.6% | -661 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 7:40pm | 17.7% | -491 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -660 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 2.9% | -540 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 26.3% | -480 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 34.1% | -360 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0.7% | -630 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 3.8% | -600 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 1.4% | -450 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 17.5% | -420 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 9:45pm | 2.2% | -615 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 6:45pm | 15.2% | -435 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 6.9% | -510 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 21.4% | -330 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 3.7% | -570 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 12.6% | -390 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 16% | -360 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -540 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 2.4% | -480 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 7.8% | -420 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:55pm | 2.4% | -625 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:15pm | 0% | -585 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:45pm | 12.3% | -495 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:15pm | 22.2% | -345 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 10:00pm | 8.6% | -630 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 8:30pm | 0% | -540 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 7:15pm | 18.5% | -465 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 5:45pm | 0% | -375 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 15% | -585 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 24.3% | -420 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0.7% | -555 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:20pm | 0% | -529 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 3.6% | -450 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 0% | -390 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:40pm | 2.4% | -370 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -645 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 5.3% | -480 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 5.9% | -435 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 10:15pm | 0.6% | -645 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 9:00pm | 2.4% | -570 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 7:30pm | 3% | -480 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 6:15pm | 6% | -405 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:45pm | 0.9% | -674 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 6.6% | -508 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 5:15pm | 13.2% | -343 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0.7% | -629 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 39.5% | -463 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -539 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 0% | -373 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -614 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -599 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -569 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -493 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 7:00pm | 0% | -448 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 6:45pm | 3.6% | -433 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 6:15pm | 0% | -403 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -358 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0% | -328 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:30pm | 0.6% | -659 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:05pm | 0% | -633 min |
| AMC Sunset Place 24 | The Drama | undefined | 9:40pm | 0% | -609 min |
| AMC Sunset Place 24 | The Drama | undefined | 8:10pm | 1.4% | -519 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:40pm | 5.3% | -489 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:10pm | 38.8% | -459 min |
| AMC Sunset Place 24 | The Drama | undefined | 6:45pm | 1.6% | -433 min |
| AMC Sunset Place 24 | The Drama | undefined | 5:10pm | 18.6% | -339 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:00pm | 7.1% | -569 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:00pm | 30.4% | -448 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:15pm | 28.6% | -403 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 10:15pm | 2.2% | -644 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 7:30pm | 19.6% | -478 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | PRIME at AMC | 10:00pm | 1.3% | -628 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | PRIME 3D | 7:15pm | 10.4% | -463 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -598 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 7.7% | -523 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 4.1% | -418 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 12.8% | -358 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -568 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -508 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 6.8% | -403 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 6.9% | -343 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 9:45pm | 1% | -613 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 7:00pm | 3.1% | -448 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 6:00pm | 0% | -388 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 4.6% | -598 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 34.6% | -433 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -613 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 1.3% | -568 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 11.6% | -508 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -478 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 14.5% | -463 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 5.9% | -403 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 2.9% | -373 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 2.9% | -343 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:10pm | 0% | -338 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 0% | -662 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 5.8% | -538 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:30pm | 50% | -418 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:40pm | 0% | -668 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:25pm | 5.8% | -653 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:10pm | 2.7% | -638 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 9:15pm | 18.2% | -583 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:35pm | 27.5% | -482 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:00pm | 26% | -448 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 6:30pm | 40% | -418 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:15pm | 2.5% | -523 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:35pm | 9.1% | -362 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | PRIME at AMC | 9:40pm | 1.2% | -608 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 10.5% | -448 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:05pm | 0% | -632 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:10pm | 0% | -578 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -478 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 2% | -418 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 2.4% | -388 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 10:00pm | 6.1% | -628 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 8:45pm | 0% | -553 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 7:15pm | 24.2% | -463 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 1.1% | -598 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 9.6% | -433 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -628 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 1.5% | -553 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:00pm | 0% | -388 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -658 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 8:15pm | 0% | -523 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -493 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 7:15pm | 4.5% | -463 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 5:30pm | 2.8% | -358 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0% | -328 min |
| AMC West Shore 14 | The Drama | undefined | 10:00pm | 0.5% | -628 min |
| AMC West Shore 14 | The Drama | undefined | 7:30pm | 5.1% | -478 min |
| AMC West Shore 14 | The Drama | undefined | 7:15pm | 5% | -463 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -613 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 1.4% | -508 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 1.4% | -448 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -643 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -583 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 7:30pm | 4.1% | -478 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 6:30pm | 1.4% | -418 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 5:15pm | 11% | -343 min |
| AMC Bradenton 20 | The Drama | undefined | 10:00pm | 0% | -628 min |
| AMC Bradenton 20 | The Drama | undefined | 7:15pm | 5.6% | -463 min |
| AMC Bradenton 20 | The Drama | undefined | 6:15pm | 2.8% | -403 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 28.9% | -657 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 76.3% | -491 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 91.4% | -326 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 2.3% | -627 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 1.7% | -597 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 2.7% | -582 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 5.4% | -552 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 6.6% | -431 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 25% | -416 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 44.2% | -386 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 19.6% | -567 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 13.5% | -537 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 2.9% | -461 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 47.1% | -401 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 2.4% | -371 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:45pm | 21.6% | -612 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:00pm | 73.5% | -446 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 70.3% | -356 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 9:00pm | 21.3% | -567 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 6:15pm | 59% | -401 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 10:00pm | 63.8% | -627 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 7:15pm | 87% | -461 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 1.9% | -657 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 33.8% | -491 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 58.4% | -326 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -657 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -567 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 1.1% | -522 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 0% | -506 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 3.6% | -401 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 1.5% | -371 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 5.3% | -341 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -627 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 4.8% | -461 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 6.4% | -356 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 10:10pm | 1.5% | -637 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 9:10pm | 10.1% | -577 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 7:10pm | 11.8% | -457 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 6:10pm | 25.8% | -397 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:20pm | 9.3% | -466 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:55pm | 0% | -622 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 2.9% | -416 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | RealD 3D | 9:10pm | 2.5% | -577 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 10:35pm | 1.8% | -661 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 7:45pm | 12.4% | -491 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 0% | -627 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:10pm | 1.3% | -457 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 3.3% | -567 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:10pm | 12.6% | -397 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -627 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -612 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 0% | -537 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -476 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 0% | -446 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 2.4% | -371 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -642 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 4% | -491 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 4% | -337 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:15pm | 0% | -642 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:00pm | 0% | -627 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 9:00pm | 0% | -567 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 7:30pm | 1.7% | -476 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 6:00pm | 10.4% | -386 min |
| AMC Hoffman Center 22 | The Drama | Open Caption (On-screen Subtitles) | 7:00pm | 0% | -446 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:15pm | 1.9% | -521 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:30pm | 15.1% | -356 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -626 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 2.9% | -491 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 2.7% | -461 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 13.5% | -326 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 3% | -431 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 10:15pm | 5.1% | -641 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 9:30pm | 12.1% | -596 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 8:30pm | 52.7% | -536 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:30pm | 75.5% | -476 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:00pm | 67.1% | -446 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 5:45pm | 67.6% | -371 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -656 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 8:10pm | 1.2% | -516 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 23.8% | -431 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 2.4% | -596 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 10:00pm | 0% | -626 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 7:10pm | 21.6% | -456 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -611 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -506 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 11.6% | -341 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 10:20pm | 0% | -646 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -566 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 7:45pm | 2.8% | -491 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 7:00pm | 3.1% | -446 min |
| AMC Worldgate 9 | The Drama | undefined | 10:15pm | 0% | -641 min |
| AMC Worldgate 9 | The Drama | undefined | 7:30pm | 3.1% | -476 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 2.7% | -566 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 28.6% | -401 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0.4% | -626 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 12% | -461 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 0% | -536 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 0.7% | -521 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 0% | -506 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 0% | -491 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 2.7% | -476 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 0% | -371 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 0% | -356 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 0% | -341 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 2.1% | -326 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -596 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 0% | -431 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 9:15pm | 2% | -581 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 6:30pm | 6.7% | -416 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 3.2% | -611 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 22% | -446 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 4.9% | -506 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 8.1% | -341 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -596 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -476 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 1.4% | -431 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -581 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0.3% | -536 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -416 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 0.3% | -371 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:00pm | 32.6% | -326 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 9:30pm | 0% | -596 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 8:30pm | 0% | -536 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 7:30pm | 2.3% | -476 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 6:30pm | 2.2% | -416 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 9:10pm | 0% | -576 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 5.4% | -416 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -611 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:25pm | 0% | -591 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 8:40pm | 0% | -546 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -476 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:00pm | 0% | -446 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -431 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0.5% | -386 min |
| AMC Voorhees 16 | The Drama | undefined | 9:30pm | 0% | -596 min |
| AMC Voorhees 16 | The Drama | undefined | 6:40pm | 1.8% | -426 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -610 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:05pm | 0% | -569 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0.8% | -550 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 3.1% | -444 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 7.7% | -384 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:25pm | 14.3% | -350 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 3.6% | -655 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -489 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -414 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -324 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 10:00pm | 0% | -625 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 8:45pm | 4.4% | -550 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 8:15pm | 4.8% | -520 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 7:15pm | 12% | -459 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:50pm | 4.3% | -614 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 53.6% | -444 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 10:50pm | 0% | -674 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 8:00pm | 2% | -504 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 5:10pm | 12.8% | -335 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -565 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 6:10pm | 15.5% | -395 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 10:20pm | 18.9% | -644 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 7:20pm | 87.4% | -464 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 2.7% | -670 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 12.4% | -504 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 25.7% | -339 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 0% | -640 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 6.5% | -580 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0% | -550 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -474 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 6.5% | -414 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 0% | -384 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -610 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 4.7% | -354 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 10:45pm | 0% | -670 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 9:15pm | 4.8% | -580 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 8:15pm | 3.5% | -520 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 7:45pm | 17.1% | -489 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 7:00pm | 0% | -444 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 6:30pm | 31.7% | -414 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 5:00pm | 16.2% | -324 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 0.7% | -610 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 13.7% | -444 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 2.2% | -550 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:30pm | 2.9% | -595 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | undefined | 6:00pm | 8.9% | -384 min |
| AMC Northlake 14 | The Drama | undefined | 10:00pm | 0% | -625 min |
| AMC Northlake 14 | The Drama | undefined | 7:15pm | 19% | -459 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 4.1% | -655 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 19.2% | -474 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 10:45pm | 0% | -670 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 0% | -504 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 5:15pm | 0% | -339 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -685 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -565 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 0% | -535 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 1.4% | -399 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 0% | -369 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -625 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 0% | -444 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 10:15pm | 0% | -640 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:30pm | 0% | -595 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:15pm | 0% | -520 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:15pm | 3% | -459 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 0% | -429 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 4.7% | -354 min |
| AMC Sugarloaf Mills 18 | The Drama | Laser at AMC | 10:15pm | 0% | -640 min |
| AMC Sugarloaf Mills 18 | The Drama | Laser at AMC | 7:15pm | 3.5% | -459 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 2.7% | -715 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 18.4% | -550 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 27.2% | -384 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 0% | -580 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 6.3% | -414 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 0.7% | -504 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 4.7% | -444 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 5.6% | -339 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -685 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -640 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -520 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 5.6% | -474 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:30pm | 0% | -354 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 11:10pm | 2.2% | -695 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 8:20pm | 28.9% | -524 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 7:50pm | 27.9% | -494 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 5:30pm | 57.8% | -354 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 2.4% | -625 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 1.3% | -550 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 3.9% | -520 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 2.4% | -459 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 1.3% | -384 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 3.9% | -354 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 9:30pm | 4.7% | -595 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 9:00pm | 2.9% | -565 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 4.6% | -489 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 6:45pm | 4.7% | -429 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 6:15pm | 4.2% | -399 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 3.6% | -324 min |
| AMC Camp Creek 14 | The Drama | undefined | 10:00pm | 0% | -625 min |
| AMC Camp Creek 14 | The Drama | undefined | 7:15pm | 0% | -459 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 2.9% | -564 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 19.1% | -399 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -594 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 0% | -429 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -324 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 11:00pm | 0% | -684 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:15pm | 26.2% | -519 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:30pm | 17.5% | -354 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 9:45pm | 1.2% | -609 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 8:30pm | 12.5% | -534 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 7:00pm | 16% | -444 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 5:45pm | 5.4% | -369 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 11:10pm | 1.3% | -694 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 1.1% | -654 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 4.1% | -624 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 9:50pm | 0% | -614 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 1.3% | -534 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 7:40pm | 1.1% | -484 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 2.3% | -444 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:20pm | 6.9% | -343 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 10:40pm | 3.4% | -664 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -594 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:10pm | 4.5% | -574 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 8:00pm | 3.4% | -504 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 7:20pm | 27.4% | -463 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:40pm | 0% | -424 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:20pm | 14.6% | -403 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 5:40pm | 16% | -364 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 10:10pm | 1.4% | -634 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 9:10pm | 5.5% | -574 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 7:15pm | 11% | -459 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 6:15pm | 6.8% | -399 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 1.9% | -564 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 12% | -384 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 9.8% | -654 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 13.8% | -474 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -684 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 3.4% | -624 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 3.1% | -504 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 8.6% | -444 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 5.4% | -324 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 12.5% | -594 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:50pm | 45.8% | -433 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 6:30pm | 3.8% | -414 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 10.5% | -354 min |
| AMC Concord Mills 24 | The Drama | undefined | 10:15pm | 1.5% | -639 min |
| AMC Concord Mills 24 | The Drama | undefined | 9:15pm | 2.3% | -579 min |
| AMC Concord Mills 24 | The Drama | undefined | 8:15pm | 9.8% | -519 min |
| AMC Concord Mills 24 | The Drama | undefined | 7:15pm | 10.4% | -459 min |
| AMC Concord Mills 24 | The Drama | undefined | 6:15pm | 5.3% | -399 min |
| AMC Concord Mills 24 | The Drama | undefined | 5:15pm | 12.2% | -339 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | IMAX at AMC | 9:00pm | 0.8% | -563 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | IMAX at AMC | 6:15pm | 1.2% | -398 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 1% | -623 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 2.4% | -458 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -578 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 8:35pm | 0% | -537 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -488 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -413 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -323 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:50pm | 0% | -372 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -593 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 8:15pm | 0% | -518 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 8:00pm | 0% | -503 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -428 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -353 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 5:15pm | 0% | -338 min |
| AMC Forum 30 | The Drama | undefined | 9:45pm | 1.5% | -608 min |
| AMC Forum 30 | The Drama | undefined | 7:00pm | 0% | -443 min |
| AMC Forum 30 | The Drama | undefined | 6:00pm | 0% | -383 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | IMAX at AMC | 8:30pm | 0% | -533 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | IMAX at AMC | 5:40pm | 0.6% | -363 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0% | -623 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 0% | -458 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -503 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 0% | -333 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -563 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | undefined | 6:20pm | 0% | -402 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 9:45pm | 0% | -608 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 7:00pm | 0% | -443 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 5.5% | -443 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 3.6% | -638 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 4.5% | -533 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 6.4% | -473 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 4.5% | -368 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 3.4% | -413 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 3.4% | -578 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 8:00pm | 4.5% | -503 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 5:15pm | 14.1% | -338 min |
| AMC Livonia 20 | The Drama | undefined | 10:30pm | 0% | -653 min |
| AMC Livonia 20 | The Drama | undefined | 7:45pm | 1.8% | -488 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -623 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 0% | -458 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 3.3% | -353 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -653 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -593 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 8:45pm | 2.2% | -548 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 7:45pm | 1.7% | -488 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -428 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0% | -383 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0% | -323 min |
| AMC John R 15 | The Drama | undefined | 10:05pm | 0% | -627 min |
| AMC John R 15 | The Drama | undefined | 8:45pm | 0% | -548 min |
| AMC John R 15 | The Drama | undefined | 7:20pm | 8.8% | -462 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | IMAX at AMC | 9:00pm | 1.5% | -562 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | IMAX at AMC | 6:15pm | 14.2% | -397 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:10pm | 6.8% | -632 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 10.3% | -472 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 1.1% | -657 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 1.1% | -502 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 5:20pm | 4.2% | -341 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | undefined | 9:35pm | 0.8% | -597 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | undefined | 7:00pm | 4.1% | -442 min |
| AMC Castleton Square 14 | The Drama | undefined | 10:30pm | 1.4% | -652 min |
| AMC Castleton Square 14 | The Drama | undefined | 7:45pm | 21.4% | -487 min |
| AMC Castleton Square 14 | The Drama | undefined | 5:00pm | 28.6% | -322 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | IMAX at AMC | 10:00pm | 0.6% | -622 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | IMAX at AMC | 7:15pm | 8.2% | -457 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 4.7% | -592 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 20.3% | -427 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 2.3% | -637 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 16.1% | -472 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -517 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 0% | -442 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0% | -352 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 8:45pm | 0% | -547 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -652 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -607 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -577 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 6:30pm | 1.4% | -412 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0% | -382 min |
| AMC Perry Crossing 18 | The Drama | undefined | 10:00pm | 0.8% | -622 min |
| AMC Perry Crossing 18 | The Drama | undefined | 7:45pm | 0% | -487 min |
| AMC Perry Crossing 18 | The Drama | undefined | 5:00pm | 0% | -322 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 2.6% | -607 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 3.5% | -442 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:00pm | 0% | -682 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:30pm | 1.4% | -532 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 13.3% | -382 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -652 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -592 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 1.5% | -562 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -487 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 0% | -427 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 0% | -397 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 6.8% | -322 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0% | -667 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0.2% | -637 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -577 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 8:00pm | 0% | -502 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0.7% | -472 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 6:30pm | 0.9% | -412 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -352 min |
| AMC Thoroughbred 20 | The Drama | undefined | 10:30pm | 0% | -652 min |
| AMC Thoroughbred 20 | The Drama | undefined | 9:15pm | 1.9% | -577 min |
| AMC Thoroughbred 20 | The Drama | undefined | 7:50pm | 22.5% | -491 min |
| AMC Thoroughbred 20 | The Drama | undefined | 6:30pm | 11.3% | -412 min |
| AMC Thoroughbred 20 | The Drama | undefined | 5:00pm | 29.4% | -322 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0.5% | -621 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 5.9% | -471 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 7.8% | -321 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -531 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -501 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0% | -381 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 3.5% | -351 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -591 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -561 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 7:00pm | 0% | -441 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 6:30pm | 10.8% | -411 min |
| AMC Bellevue 12 | The Drama | undefined | 9:15pm | 8.7% | -576 min |
| AMC Bellevue 12 | The Drama | undefined | 6:15pm | 41.3% | -396 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 1.1% | -606 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 3.7% | -441 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 2.6% | -561 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 6.2% | -396 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | PRIME at AMC | 5:00pm | 2.2% | -321 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -636 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 9.3% | -531 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 2.2% | -471 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 5.2% | -366 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -591 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -576 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 8:15pm | 0% | -516 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 8:00pm | 0% | -501 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 63% | -426 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 6:30pm | 2.1% | -411 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -351 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 5:15pm | 0% | -336 min |
| AMC Easton Town Center 30 | The Drama | undefined | 10:00pm | 1.9% | -621 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:30pm | 0% | -591 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:00pm | 2.6% | -561 min |
| AMC Easton Town Center 30 | The Drama | undefined | 8:00pm | 0% | -501 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:30pm | 0% | -471 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:00pm | 16.7% | -441 min |
| AMC Easton Town Center 30 | The Drama | undefined | 6:00pm | 20.8% | -381 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 3.3% | -575 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 1.6% | -470 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 10% | -410 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:00pm | 16.5% | -380 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0% | -665 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -635 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 9:45pm | 4.7% | -605 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 8:00pm | 2.4% | -500 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -485 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 7:00pm | 10.2% | -440 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 6:45pm | 10% | -425 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 6:15pm | 39.7% | -395 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 5:15pm | 15.9% | -335 min |
| AMC Dublin Village 18 | The Drama | undefined | 10:15pm | 1.7% | -635 min |
| AMC Dublin Village 18 | The Drama | undefined | 7:15pm | 31.7% | -455 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | IMAX at AMC | 9:45pm | 0.9% | -605 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 7.4% | -440 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 9:15pm | 1.3% | -575 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 8:30pm | 0% | -530 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -485 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 7:15pm | 0% | -455 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 6:30pm | 1.9% | -410 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 5:45pm | 0.9% | -365 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0% | -320 min |
| AMC Grove City 14 | The Drama | undefined | 9:40pm | 0.7% | -600 min |
| AMC Grove City 14 | The Drama | undefined | 7:15pm | 2.2% | -455 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 0% | -650 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 5.6% | -485 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 0.3% | -320 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0% | -590 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 6.4% | -425 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -560 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -515 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 0% | -395 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0% | -350 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 10:00pm | 2.5% | -620 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 8:30pm | 0% | -530 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 7:15pm | 4.9% | -455 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 5:45pm | 1.7% | -365 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 10:15pm | 1.5% | -635 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 9:00pm | 7.4% | -560 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 7:20pm | 4.5% | -459 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 6:10pm | 16.7% | -390 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 0% | -649 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 1.1% | -484 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 2.9% | -319 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 1% | -604 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 14.7% | -439 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 3.8% | -514 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 17.3% | -349 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 9:45pm | 1.1% | -604 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 9:05pm | 2.9% | -563 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 8:45pm | 2.6% | -544 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 7:00pm | 8.5% | -439 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 6:20pm | 2.9% | -398 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 6:00pm | 7.9% | -379 min |
| AMC West Chester 18 | The Drama | undefined | 10:05pm | 3.9% | -623 min |
| AMC West Chester 18 | The Drama | undefined | 7:00pm | 19.7% | -439 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:30pm | 1.4% | -649 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:45pm | 6.8% | -484 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:00pm | 15.8% | -319 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 3.4% | -589 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 11.2% | -424 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | PRIME at AMC | 5:45pm | 10.7% | -364 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 4.3% | -514 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 6:10pm | 5.6% | -389 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 4.3% | -349 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 4.4% | -619 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 10.2% | -454 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 10:30pm | 1.5% | -649 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 9:55pm | 12.5% | -614 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:45pm | 42.4% | -484 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:05pm | 53.1% | -443 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 0.3% | -649 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 2.7% | -484 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 2.4% | -319 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0.5% | -589 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 5.5% | -424 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -604 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 4.1% | -439 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -634 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 10:00pm | 2.4% | -619 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 8:45pm | 0% | -544 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 8:30pm | 0% | -529 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:00pm | 5.7% | -499 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -469 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 7:15pm | 2.4% | -454 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 6:15pm | 3.7% | -394 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 6:00pm | 2% | -379 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 6% | -349 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:15pm | 0% | -334 min |
| AMC Regency 24 | The Drama | undefined | 10:30pm | 0% | -649 min |
| AMC Regency 24 | The Drama | undefined | 10:00pm | 1.4% | -619 min |
| AMC Regency 24 | The Drama | undefined | 8:30pm | 0% | -529 min |
| AMC Regency 24 | The Drama | undefined | 7:15pm | 9.6% | -454 min |
| AMC Regency 24 | The Drama | undefined | 5:45pm | 4.8% | -364 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:00pm | 0% | -619 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | IMAX at AMC | 7:15pm | 3.9% | -454 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 2.7% | -559 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 9.6% | -394 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 15.7% | -319 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -589 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 8:45pm | 1.9% | -544 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 8:15pm | 1.6% | -514 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:45pm | 0% | -484 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -469 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -424 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0.9% | -379 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 4.7% | -349 min |
| AMC Orange Park 24 | The Drama | undefined | 9:45pm | 4.3% | -604 min |
| AMC Orange Park 24 | The Drama | undefined | 8:15pm | 0% | -514 min |
| AMC Orange Park 24 | The Drama | undefined | 7:00pm | 4.3% | -439 min |
| AMC Orange Park 24 | The Drama | undefined | 5:30pm | 0% | -349 min |

**Issues:** AMC Empire 25: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Empire 25: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Assembly Row 12: No seat map for The Drama Laser at AMC; AMC Assembly Row 12: No seat map for The Drama Laser at AMC; AMC Assembly Row 12: No seat map for The Drama Laser at AMC; AMC Assembly Row 12: No seat map for The Drama Laser at AMC; AMC Assembly Row 12: No seat map for The Drama Laser at AMC; AMC Framingham 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie Dine-In Delivery to Seat; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Altamonte Mall 18: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Altamonte Mall 18: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Tysons Corner 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Tysons Corner 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Tysons Corner 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Georgetown 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Georgetown 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC DINE-IN North Point Mall 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC DINE-IN North Point Mall 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC DINE-IN North Point Mall 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Open Caption (On-screen Subtitles); AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Livonia 20: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie Open Caption (On-screen Subtitles); AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie undefined; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie undefined; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie undefined; AMC Indianapolis 17: No seat map for The Drama undefined; AMC Indianapolis 17: No seat map for The Drama undefined; AMC Indianapolis 17: No seat map for The Drama undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Super Mario Galaxy Movie undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Drama undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Drama undefined; AMC CLASSIC Murfreesboro 16: No seat map for The Drama undefined; AMC Dublin Village 18: No seat map for The Super Mario Galaxy Movie undefined; AMC Waterfront 22: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Waterfront 22: No seat map for The Drama Laser at AMC; AMC Waterfront 22: No seat map for The Drama Laser at AMC

---

## 2026-04-05 12:11 — ET Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie, The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Empire 25 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 0% | -585 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 15.9% | -420 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:30pm | 2% | -690 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:45pm | 12.1% | -525 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 64.6% | -360 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -660 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 0% | -615 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 7.7% | -495 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 3.4% | -450 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 8.4% | -300 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 1.5% | -555 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 10.2% | -390 min |
| AMC Empire 25 | The Drama | Laser at AMC | 11:15pm | 0% | -675 min |
| AMC Empire 25 | The Drama | Laser at AMC | 10:00pm | 1.3% | -600 min |
| AMC Empire 25 | The Drama | Laser at AMC | 9:45pm | 3.1% | -585 min |
| AMC Empire 25 | The Drama | Laser at AMC | 8:30pm | 6.7% | -510 min |
| AMC Empire 25 | The Drama | Laser at AMC | 8:15pm | 0% | -495 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:45pm | 11.4% | -465 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:15pm | 22.2% | -435 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:00pm | 6.4% | -420 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:45pm | 26.3% | -345 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:30pm | 18.8% | -330 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:00pm | 25.3% | -300 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 6.9% | -600 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 57.1% | -420 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 7.1% | -540 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 34.5% | -360 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 38.2% | -300 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 1.8% | -465 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 10:30pm | 7.3% | -630 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 9:30pm | 10.9% | -570 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 8:30pm | 37.7% | -510 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 7:45pm | 55.3% | -465 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 7:30pm | 71.3% | -450 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 6:30pm | 65.3% | -390 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 5:30pm | 64.3% | -330 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:00pm | 0.6% | -660 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:15pm | 13% | -495 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:30pm | 26.4% | -330 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -540 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 26.1% | -435 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 10:30pm | 5.3% | -630 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 10:05pm | 0% | -604 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 7:45pm | 19.3% | -465 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 6:15pm | 11.7% | -375 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 57.9% | -300 min |
| AMC Kips Bay 15 | The Drama | undefined | 10:45pm | 5.5% | -645 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:45pm | 7.6% | -585 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:15pm | 12.8% | -555 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:50pm | 35.6% | -529 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:00pm | 71% | -480 min |
| AMC Kips Bay 15 | The Drama | undefined | 7:00pm | 79.3% | -420 min |
| AMC Kips Bay 15 | The Drama | undefined | 6:00pm | 77.2% | -360 min |
| AMC Kips Bay 15 | The Drama | undefined | 5:15pm | 77.2% | -315 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:00pm | 0% | -660 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:20pm | 9.8% | -499 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:45pm | 49.8% | -345 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0.8% | -570 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 30.3% | -420 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:25pm | 25.7% | -385 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 2.7% | -630 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | RealD 3D | 7:50pm | 16.2% | -469 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 11:00pm | 0% | -660 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 10:30pm | 18.8% | -630 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 9:30pm | 22.1% | -570 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 8:45pm | 39.7% | -525 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 7:45pm | 63.8% | -465 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:45pm | 60.6% | -405 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:00pm | 60.3% | -360 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:30pm | 73.7% | -330 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:10pm | 59.5% | -310 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:00pm | 68.1% | -300 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 3.5% | -585 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 5.6% | -540 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 42.9% | -360 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 7:00pm | 16.5% | -420 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:45pm | 0% | -645 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:00pm | 3.5% | -600 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 8:00pm | 62.9% | -480 min |
| AMC 84th Street 6 | The Drama | Open Caption (On-screen Subtitles) | 7:15pm | 64% | -435 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 4% | -600 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 10% | -525 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 13% | -435 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 45.6% | -360 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 2% | -660 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -555 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 9.2% | -495 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 27.5% | -390 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 18.4% | -330 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 10:30pm | 4.3% | -630 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 9:00pm | 12.7% | -540 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 7:45pm | 61.4% | -465 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 6:15pm | 70.9% | -375 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 5:00pm | 77.1% | -300 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 8.4% | -614 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 21.5% | -448 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 2.3% | -554 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 4.2% | -388 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 2.8% | -508 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 10.6% | -343 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 10:00pm | 2% | -599 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 7:15pm | 16.1% | -433 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:30pm | 0.4% | -629 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:45pm | 6.5% | -463 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:00pm | 13.4% | -298 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 7.9% | -539 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 23.7% | -373 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -599 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 1.3% | -433 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 5.4% | -493 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 0% | -328 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 1% | -313 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 4.3% | -569 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 3.8% | -403 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 10:30pm | 0.7% | -629 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 10:00pm | 4% | -599 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:30pm | 30.7% | -448 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:00pm | 42.9% | -418 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:15pm | 1.6% | -554 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:30pm | 14% | -388 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 0% | -644 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 13.2% | -478 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 29.9% | -313 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 6.3% | -524 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 7.3% | -463 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 16% | -358 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 15.7% | -328 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -659 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -599 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 7.6% | -493 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 9.2% | -433 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 10:30pm | 0% | -629 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 9:30pm | 4.2% | -569 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 8:15pm | 40% | -493 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 7:30pm | 50.5% | -448 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 5:30pm | 20.2% | -328 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 10:30pm | 0% | -629 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 7:45pm | 24.1% | -463 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 5:00pm | 63.1% | -298 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -599 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -539 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 6.9% | -493 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 4.7% | -448 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 8.9% | -373 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 17.2% | -328 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -584 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -569 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 4.4% | -418 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 8.9% | -403 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 10:15pm | 0% | -614 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 10:15pm | 0% | -614 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 7:15pm | 45.7% | -433 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 9:45pm | 0.6% | -584 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 12.3% | -418 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 12.1% | -448 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 28.3% | -313 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 0% | -633 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0.6% | -524 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -478 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 11% | -358 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 10:30pm | 7.6% | -629 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 7:40pm | 17.7% | -459 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -629 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 2.9% | -508 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 25% | -448 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 34.1% | -328 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0.7% | -599 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 3.8% | -569 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 2.9% | -418 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 17.5% | -388 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 9:45pm | 2.2% | -584 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 6:45pm | 15.2% | -403 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 0.5% | -598 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 12.7% | -418 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 6.9% | -478 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 25.5% | -298 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 3.7% | -538 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 12.6% | -358 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 16% | -328 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -508 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 2.4% | -448 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 7.8% | -388 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:55pm | 2.4% | -593 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:15pm | 0% | -553 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:45pm | 12.3% | -463 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:15pm | 22.2% | -313 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 10:00pm | 11.1% | -598 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 8:30pm | 0% | -508 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 7:15pm | 19.8% | -433 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 5:45pm | 0% | -343 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:45pm | 0% | -643 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:00pm | 6.1% | -478 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:15pm | 5.3% | -313 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 15% | -553 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 24.3% | -388 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0% | -523 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:20pm | 0% | -497 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 3.6% | -418 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 0% | -358 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:40pm | 2.4% | -338 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -613 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 5.3% | -448 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 5.9% | -403 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 10:15pm | 0.6% | -613 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 9:00pm | 2.4% | -538 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 7:30pm | 5.4% | -448 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 6:15pm | 5.4% | -373 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:45pm | 0.9% | -643 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 6.6% | -478 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 5:15pm | 13.2% | -313 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0.7% | -598 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 39.5% | -433 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -508 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 0% | -343 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -583 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -568 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -538 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 7:45pm | 1.2% | -463 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 7:00pm | 1.3% | -418 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 6:45pm | 3.6% | -403 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 6:15pm | 0% | -373 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -328 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0% | -298 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:30pm | 0.6% | -628 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:05pm | 0% | -602 min |
| AMC Sunset Place 24 | The Drama | undefined | 9:40pm | 0% | -578 min |
| AMC Sunset Place 24 | The Drama | undefined | 8:10pm | 1.4% | -488 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:40pm | 5.3% | -458 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:10pm | 38.8% | -428 min |
| AMC Sunset Place 24 | The Drama | undefined | 6:45pm | 1.6% | -403 min |
| AMC Sunset Place 24 | The Drama | undefined | 5:10pm | 18.6% | -308 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0.7% | -628 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -508 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 5.7% | -463 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 3.6% | -298 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:00pm | 8.9% | -538 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:00pm | 30.4% | -418 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:15pm | 28.6% | -373 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:45pm | 0% | -343 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 10:15pm | 2.2% | -613 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 7:30pm | 19.6% | -448 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | PRIME at AMC | 10:00pm | 1.3% | -598 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | PRIME 3D | 7:15pm | 8.4% | -433 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -568 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 16.2% | -493 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 4.1% | -388 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 12.8% | -328 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -538 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -478 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 6.8% | -373 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 6.9% | -313 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 9:45pm | 1% | -583 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 7:00pm | 3.1% | -418 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 6:00pm | 5.3% | -358 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:30pm | 0.7% | -627 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:45pm | 13.3% | -461 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:00pm | 23% | -296 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 4.6% | -567 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 33.6% | -401 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -582 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 1.3% | -537 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 11.6% | -476 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -446 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 14.5% | -431 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 5.9% | -371 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 2.9% | -341 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 2.9% | -311 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:10pm | 0% | -307 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 0% | -631 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 5.8% | -506 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:30pm | 68.2% | -386 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:40pm | 0% | -637 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:25pm | 5.8% | -622 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:10pm | 8.1% | -607 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 9:15pm | 20.5% | -552 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:35pm | 27.5% | -451 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:00pm | 27.9% | -416 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 6:30pm | 40% | -386 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:15pm | 2.5% | -491 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:35pm | 9.1% | -331 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | PRIME at AMC | 9:40pm | 1.8% | -577 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 10.5% | -416 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:05pm | 0% | -601 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:10pm | 0% | -547 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -446 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 2% | -386 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 2.4% | -356 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 10:00pm | 6.1% | -597 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 8:45pm | 0% | -522 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 7:15pm | 24.2% | -431 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 1.1% | -567 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 10.7% | -401 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -597 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 1.5% | -522 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:00pm | 0% | -356 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -627 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 8:15pm | 0% | -491 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0.5% | -461 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 7:15pm | 4.5% | -431 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 5:30pm | 2.8% | -326 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0% | -296 min |
| AMC West Shore 14 | The Drama | undefined | 10:00pm | 0.5% | -597 min |
| AMC West Shore 14 | The Drama | undefined | 7:30pm | 5.1% | -446 min |
| AMC West Shore 14 | The Drama | undefined | 7:15pm | 5% | -431 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -582 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 1.4% | -476 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 1.4% | -416 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -612 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -552 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 7:30pm | 4.1% | -446 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 6:30pm | 1.4% | -386 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 5:15pm | 13.8% | -311 min |
| AMC Bradenton 20 | The Drama | undefined | 10:00pm | 0% | -597 min |
| AMC Bradenton 20 | The Drama | undefined | 7:15pm | 5.6% | -431 min |
| AMC Bradenton 20 | The Drama | undefined | 6:15pm | 2.8% | -371 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 28.9% | -627 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 76.7% | -461 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 90.2% | -296 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 2.3% | -597 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 1.7% | -567 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 2.7% | -552 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 2.7% | -522 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 6.6% | -401 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 25% | -386 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 44.2% | -356 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 19.6% | -537 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 13.5% | -506 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 2.9% | -431 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 52% | -371 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 2.4% | -341 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:45pm | 23.5% | -582 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:00pm | 73.5% | -416 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 72.1% | -326 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 9:00pm | 21.3% | -537 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 6:15pm | 59% | -371 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 10:00pm | 63.8% | -597 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 7:15pm | 87% | -431 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:30pm | 0.9% | -566 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:45pm | 29.6% | -401 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 1.9% | -626 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 36.4% | -461 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 57.1% | -296 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -626 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -536 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 1.1% | -491 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 0% | -476 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 3.6% | -371 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 1.5% | -341 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 5.3% | -311 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -596 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 4.8% | -431 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 6.4% | -326 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 10:10pm | 1.5% | -606 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 9:10pm | 10.1% | -546 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 7:10pm | 11.8% | -426 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 6:10pm | 25.8% | -366 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:00pm | 0% | -656 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:20pm | 2.1% | -495 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:40pm | 9.6% | -336 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:20pm | 10.1% | -435 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:55pm | 0% | -591 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 2.9% | -386 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | RealD 3D | 9:10pm | 2.5% | -546 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 10:35pm | 1.8% | -631 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 7:45pm | 12.4% | -461 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 0% | -596 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:10pm | 1.3% | -426 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 3.3% | -536 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:10pm | 12.6% | -366 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -596 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -581 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 0% | -506 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -446 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 0% | -416 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 2.8% | -341 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -611 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 4% | -461 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 4% | -306 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:15pm | 0% | -611 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:00pm | 0% | -596 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 9:00pm | 0% | -536 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 7:30pm | 1.7% | -446 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 6:00pm | 10.4% | -356 min |
| AMC Hoffman Center 22 | The Drama | Open Caption (On-screen Subtitles) | 7:00pm | 0% | -416 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 0.9% | -536 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 3.3% | -371 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:15pm | 1.9% | -491 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:30pm | 15.1% | -326 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -596 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 2.9% | -461 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 2.7% | -431 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 13.5% | -296 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 3% | -401 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 10:15pm | 5.1% | -611 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 9:30pm | 13.6% | -566 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 8:30pm | 52.7% | -506 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:30pm | 75.5% | -446 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:00pm | 67.1% | -416 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 5:45pm | 67.6% | -341 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -626 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 8:10pm | 1.2% | -486 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 23.8% | -401 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 2.4% | -566 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 10:00pm | 0% | -596 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 7:10pm | 29.4% | -426 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -580 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -474 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 11.6% | -309 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 10:20pm | 0% | -614 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -535 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 7:45pm | 9.9% | -459 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 7:00pm | 3.1% | -414 min |
| AMC Worldgate 9 | The Drama | undefined | 10:15pm | 0% | -610 min |
| AMC Worldgate 9 | The Drama | undefined | 7:30pm | 3.1% | -444 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 2.7% | -535 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 35.1% | -369 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0.4% | -595 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 11.1% | -429 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 0% | -504 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 0.7% | -489 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 0% | -474 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 0% | -459 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 2.7% | -444 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 0% | -339 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 0% | -324 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 0% | -309 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 2.1% | -294 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -565 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 0% | -399 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 9:15pm | 2% | -550 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 6:30pm | 6.7% | -384 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 3.2% | -580 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 22% | -414 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 4.9% | -474 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 8.1% | -309 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -565 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -444 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 1.4% | -399 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -550 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0.3% | -504 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -384 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 0.3% | -339 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:00pm | 32.6% | -294 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 9:30pm | 0% | -565 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 8:30pm | 0% | -504 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 7:30pm | 2.3% | -444 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 6:30pm | 3.3% | -384 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 9:10pm | 0% | -545 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 6.5% | -384 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -580 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:25pm | 0% | -560 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 8:40pm | 0% | -515 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -444 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:00pm | 0% | -414 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -399 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0.5% | -354 min |
| AMC Voorhees 16 | The Drama | undefined | 9:30pm | 0% | -565 min |
| AMC Voorhees 16 | The Drama | undefined | 6:40pm | 3% | -395 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -580 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:05pm | 0% | -539 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0.8% | -520 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 4.6% | -414 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 7.7% | -354 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:25pm | 14.3% | -320 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 3.6% | -625 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -459 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -384 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 3.6% | -294 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 10:00pm | 0% | -595 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 8:45pm | 4.4% | -520 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 8:15pm | 4.8% | -489 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 7:15pm | 12% | -429 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:50pm | 4.3% | -584 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 61.6% | -414 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 10:50pm | 0% | -644 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 8:00pm | 2% | -474 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 5:10pm | 12.8% | -305 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -535 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 6:10pm | 15.5% | -365 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 10:20pm | 18.9% | -614 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 7:20pm | 87.4% | -434 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 2.7% | -639 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 12.4% | -474 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 25.7% | -309 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 0% | -609 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 6.5% | -549 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0% | -519 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -444 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 6.5% | -384 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 0% | -354 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -579 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0% | -324 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 10:45pm | 0% | -639 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 9:15pm | 4.8% | -549 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 8:15pm | 3.5% | -489 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 7:45pm | 17.1% | -459 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 7:00pm | 2.2% | -414 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 6:30pm | 31% | -384 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 5:00pm | 16.2% | -294 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 3.6% | -474 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | IMAX at AMC | 5:15pm | 7.2% | -309 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 0.7% | -579 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 13.7% | -414 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 2.2% | -519 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:30pm | 2.9% | -564 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | undefined | 6:00pm | 8.9% | -354 min |
| AMC Northlake 14 | The Drama | undefined | 10:00pm | 0% | -594 min |
| AMC Northlake 14 | The Drama | undefined | 7:15pm | 16.5% | -429 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 4.1% | -624 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 19.2% | -444 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 10:45pm | 0% | -639 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 0% | -474 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 5:15pm | 0% | -309 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -654 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -534 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 0% | -504 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 2.1% | -369 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 0% | -339 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -594 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 2% | -414 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 10:15pm | 0% | -609 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:15pm | 0% | -489 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:15pm | 3% | -429 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 0% | -399 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 11.8% | -324 min |
| AMC Sugarloaf Mills 18 | The Drama | Laser at AMC | 10:15pm | 0% | -609 min |
| AMC Sugarloaf Mills 18 | The Drama | Laser at AMC | 7:15pm | 3.5% | -429 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 0% | -684 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 18.4% | -519 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 27.2% | -354 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 0% | -549 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 7.8% | -384 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 0.7% | -474 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 5.9% | -414 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 5.6% | -309 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -654 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -609 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -489 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 5.6% | -444 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:30pm | 0% | -324 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 11:10pm | 2.2% | -664 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 8:20pm | 33.3% | -493 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 7:50pm | 30.2% | -463 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 5:30pm | 53.3% | -324 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 2.4% | -594 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 1.3% | -519 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 3.9% | -489 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 2.4% | -429 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 1.3% | -354 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 3.9% | -324 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 9:30pm | 4.7% | -564 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 9:00pm | 2.9% | -534 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 4.6% | -459 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 6:45pm | 4.7% | -399 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 6:15pm | 4.2% | -369 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 3.6% | -294 min |
| AMC Camp Creek 14 | The Drama | undefined | 10:00pm | 0% | -594 min |
| AMC Camp Creek 14 | The Drama | undefined | 7:15pm | 0% | -429 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 1.1% | -594 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:15pm | 4.4% | -429 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 2.9% | -534 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 19.1% | -369 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -564 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 5.3% | -459 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 0% | -399 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -294 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 11:00pm | 0% | -654 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:15pm | 26.2% | -489 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:30pm | 17.5% | -324 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 9:45pm | 3.7% | -579 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 8:30pm | 12.5% | -504 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 7:00pm | 16% | -414 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 5:45pm | 5.4% | -339 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 11:10pm | 1.3% | -663 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 1.1% | -623 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 4.1% | -593 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 9:50pm | 0% | -582 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 1.3% | -503 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 7:40pm | 1.1% | -453 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 0% | -413 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:20pm | 11.5% | -312 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 10:40pm | 3.4% | -633 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -563 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:10pm | 4.5% | -543 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 8:00pm | 3.4% | -473 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 7:20pm | 27.4% | -432 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:40pm | 0% | -393 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:20pm | 14.6% | -372 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 5:40pm | 26.7% | -333 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 10:10pm | 1.4% | -603 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 9:10pm | 5.5% | -543 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 7:15pm | 11% | -428 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 6:15pm | 6.8% | -368 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 1.9% | -533 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 13.2% | -353 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 10.6% | -623 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 13.8% | -443 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -653 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 3.4% | -593 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 3.1% | -473 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 8.6% | -413 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 6.9% | -293 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 12.5% | -563 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:50pm | 45.8% | -402 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 6:30pm | 12.2% | -383 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 10.5% | -323 min |
| AMC Concord Mills 24 | The Drama | undefined | 10:15pm | 1.5% | -608 min |
| AMC Concord Mills 24 | The Drama | undefined | 9:15pm | 2.3% | -548 min |
| AMC Concord Mills 24 | The Drama | undefined | 8:15pm | 9.8% | -488 min |
| AMC Concord Mills 24 | The Drama | undefined | 7:15pm | 10.4% | -428 min |
| AMC Concord Mills 24 | The Drama | undefined | 6:15pm | 7% | -368 min |
| AMC Concord Mills 24 | The Drama | undefined | 5:15pm | 16.3% | -308 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | IMAX at AMC | 9:00pm | 0.8% | -533 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | IMAX at AMC | 6:15pm | 1.2% | -368 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 1% | -593 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 2.4% | -428 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -548 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 8:35pm | 0% | -507 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -458 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -383 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -293 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:50pm | 0% | -342 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -563 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 8:15pm | 0% | -488 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 8:00pm | 0% | -473 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -398 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -323 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 5:15pm | 0% | -308 min |
| AMC Forum 30 | The Drama | undefined | 9:45pm | 1.5% | -578 min |
| AMC Forum 30 | The Drama | undefined | 7:00pm | 0% | -413 min |
| AMC Forum 30 | The Drama | undefined | 6:00pm | 0% | -353 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | IMAX at AMC | 8:30pm | 0% | -503 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | IMAX at AMC | 5:40pm | 0.6% | -333 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0% | -593 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 0% | -428 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -473 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 0% | -303 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -533 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | undefined | 6:20pm | 0% | -372 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 9:45pm | 0% | -578 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 7:00pm | 0% | -413 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | IMAX at AMC | 9:45pm | 3.7% | -578 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 5.5% | -413 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 3.6% | -608 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 4.5% | -503 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 6.4% | -443 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 4.5% | -338 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 3.4% | -383 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 3.4% | -548 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 8:00pm | 0% | -473 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 5:15pm | 14.1% | -308 min |
| AMC Livonia 20 | The Drama | undefined | 10:30pm | 0% | -623 min |
| AMC Livonia 20 | The Drama | undefined | 7:45pm | 1.8% | -458 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -592 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 0% | -427 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 3.3% | -322 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -622 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -562 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 8:45pm | 2.2% | -517 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 7:45pm | 1.7% | -457 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -397 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0% | -352 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0% | -292 min |
| AMC John R 15 | The Drama | undefined | 10:05pm | 0% | -597 min |
| AMC John R 15 | The Drama | undefined | 8:45pm | 0% | -517 min |
| AMC John R 15 | The Drama | undefined | 7:20pm | 8.8% | -431 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | IMAX at AMC | 9:00pm | 1.5% | -532 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | IMAX at AMC | 6:15pm | 14.2% | -367 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:10pm | 6.8% | -602 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 10.3% | -442 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 1.1% | -627 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 1.1% | -472 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 5:20pm | 4.2% | -311 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | undefined | 9:35pm | 0.8% | -567 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | undefined | 7:00pm | 4.1% | -412 min |
| AMC Castleton Square 14 | The Drama | undefined | 10:30pm | 1.4% | -622 min |
| AMC Castleton Square 14 | The Drama | undefined | 7:45pm | 21.4% | -457 min |
| AMC Castleton Square 14 | The Drama | undefined | 5:00pm | 28.6% | -292 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 2.3% | -607 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 16.1% | -442 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -487 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 0% | -412 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0% | -322 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 8:45pm | 0% | -517 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -622 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -577 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -547 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 6:30pm | 1.4% | -382 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0% | -352 min |
| AMC Perry Crossing 18 | The Drama | undefined | 10:00pm | 0.8% | -592 min |
| AMC Perry Crossing 18 | The Drama | undefined | 7:45pm | 0% | -457 min |
| AMC Perry Crossing 18 | The Drama | undefined | 5:00pm | 0% | -292 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 2.6% | -577 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 3.5% | -412 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:00pm | 0% | -652 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:30pm | 1.4% | -502 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 13.3% | -352 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -622 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -562 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 1.5% | -532 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -457 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 0% | -397 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 0% | -367 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 6.8% | -292 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0% | -637 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0.2% | -607 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -547 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 8:00pm | 0% | -472 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0.7% | -442 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 6:30pm | 0.9% | -382 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -322 min |
| AMC Thoroughbred 20 | The Drama | undefined | 10:30pm | 0% | -622 min |
| AMC Thoroughbred 20 | The Drama | undefined | 9:15pm | 1.9% | -547 min |
| AMC Thoroughbred 20 | The Drama | undefined | 7:50pm | 26.5% | -461 min |
| AMC Thoroughbred 20 | The Drama | undefined | 6:30pm | 11.3% | -382 min |
| AMC Thoroughbred 20 | The Drama | undefined | 5:00pm | 29.4% | -292 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0.5% | -592 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 5.9% | -442 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -502 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -472 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0% | -352 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 3.5% | -322 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -562 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -532 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 7:00pm | 0% | -412 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 6:30pm | 10.8% | -382 min |
| AMC Bellevue 12 | The Drama | undefined | 9:15pm | 8.7% | -547 min |
| AMC Bellevue 12 | The Drama | undefined | 6:15pm | 41.3% | -367 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 1.1% | -577 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 3.7% | -412 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 2.6% | -532 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 6.2% | -367 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | PRIME at AMC | 5:00pm | 2.2% | -292 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -607 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 9.3% | -502 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 2.2% | -442 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 5.2% | -337 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -562 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -547 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 8:15pm | 0% | -487 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 8:00pm | 0% | -472 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 77.8% | -397 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 6:30pm | 2.1% | -382 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -322 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 5:15pm | 0% | -307 min |
| AMC Easton Town Center 30 | The Drama | undefined | 10:00pm | 1.9% | -592 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:30pm | 0% | -562 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:00pm | 2.6% | -532 min |
| AMC Easton Town Center 30 | The Drama | undefined | 8:00pm | 0% | -472 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:30pm | 0% | -442 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:00pm | 16.7% | -412 min |
| AMC Easton Town Center 30 | The Drama | undefined | 6:00pm | 20.8% | -352 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 3.3% | -546 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 1.6% | -441 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 10% | -381 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:00pm | 16.5% | -351 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0% | -636 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -606 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 9:45pm | 4.7% | -576 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 8:45pm | 0.8% | -516 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 8:00pm | 2.4% | -471 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -456 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 7:00pm | 11.8% | -411 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 6:45pm | 10% | -396 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 6:15pm | 46% | -366 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 5:15pm | 20.6% | -306 min |
| AMC Dublin Village 18 | The Drama | undefined | 10:15pm | 5% | -606 min |
| AMC Dublin Village 18 | The Drama | undefined | 7:15pm | 31.7% | -426 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | IMAX at AMC | 9:45pm | 0.9% | -576 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 6.8% | -411 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 9:15pm | 1.3% | -546 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 8:30pm | 0% | -501 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -456 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 7:15pm | 0% | -426 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 6:30pm | 1.9% | -381 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 5:45pm | 0.9% | -336 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0% | -291 min |
| AMC Grove City 14 | The Drama | undefined | 9:40pm | 0.7% | -571 min |
| AMC Grove City 14 | The Drama | undefined | 7:15pm | 2.2% | -426 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 0% | -621 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 5.6% | -456 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 1.5% | -291 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0% | -561 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 6.4% | -396 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -531 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -486 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 0% | -366 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0% | -321 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 10:00pm | 2.5% | -591 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 8:30pm | 0% | -501 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 7:15pm | 4.9% | -426 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 5:45pm | 1.7% | -336 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 10:15pm | 1.5% | -606 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 9:00pm | 11.1% | -531 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 7:20pm | 4.5% | -430 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 6:10pm | 16.7% | -361 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 0% | -621 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 1.9% | -456 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 2.9% | -291 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 1% | -576 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 14.7% | -411 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 3.8% | -486 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 18.8% | -321 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 9:45pm | 1.1% | -576 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 9:05pm | 2.9% | -535 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 8:45pm | 2.6% | -516 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 7:00pm | 8.5% | -411 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 6:20pm | 2.9% | -370 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 6:00pm | 7.9% | -351 min |
| AMC West Chester 18 | The Drama | undefined | 10:05pm | 3.9% | -595 min |
| AMC West Chester 18 | The Drama | undefined | 7:00pm | 19.7% | -411 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:30pm | 1.4% | -621 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:45pm | 7.7% | -456 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:00pm | 15.8% | -291 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 4.3% | -561 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 11.2% | -396 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | PRIME at AMC | 5:45pm | 10.7% | -336 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 10:05pm | 0% | -595 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 4.3% | -486 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 6:10pm | 5.6% | -361 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 4.3% | -321 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 4.4% | -591 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 10.2% | -426 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 10:30pm | 1.5% | -621 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 9:55pm | 12.5% | -586 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:45pm | 42.4% | -456 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:15pm | 9.7% | -426 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:05pm | 53.1% | -415 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 6:15pm | 2.8% | -366 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 0.3% | -620 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 2.7% | -455 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 2.4% | -290 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0.5% | -560 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 7.1% | -395 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -575 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 4.1% | -410 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -605 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 10:00pm | 2.4% | -590 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 8:45pm | 0% | -515 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 8:30pm | 0% | -500 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:00pm | 5.7% | -470 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -440 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 7:15pm | 2.4% | -425 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 6:15pm | 3.7% | -365 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 6:00pm | 2% | -350 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 6% | -320 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:15pm | 0% | -305 min |
| AMC Regency 24 | The Drama | undefined | 10:30pm | 0% | -620 min |
| AMC Regency 24 | The Drama | undefined | 10:00pm | 1.4% | -590 min |
| AMC Regency 24 | The Drama | undefined | 8:30pm | 0% | -500 min |
| AMC Regency 24 | The Drama | undefined | 7:15pm | 9.6% | -425 min |
| AMC Regency 24 | The Drama | undefined | 5:45pm | 4.8% | -335 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:00pm | 0% | -590 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | IMAX at AMC | 7:15pm | 4.6% | -425 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 2.7% | -530 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 10.7% | -365 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 15.7% | -290 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -560 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 8:45pm | 1.9% | -515 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 8:15pm | 1.6% | -485 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:45pm | 0% | -455 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -440 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -395 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0.9% | -350 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 4.7% | -320 min |
| AMC Orange Park 24 | The Drama | undefined | 9:45pm | 4.3% | -575 min |
| AMC Orange Park 24 | The Drama | undefined | 8:15pm | 0% | -485 min |
| AMC Orange Park 24 | The Drama | undefined | 7:00pm | 4.3% | -410 min |
| AMC Orange Park 24 | The Drama | undefined | 5:30pm | 0% | -320 min |

**Issues:** AMC Sugarloaf Mills 18: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Bellevue 12: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC

---

## 2026-04-05 14:09 — ET Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie, The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 64.1% | -256 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -556 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 7.7% | -391 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 4.2% | -346 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 10.9% | -196 min |
| AMC Empire 25 | The Drama | Laser at AMC | 8:15pm | 8.3% | -391 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:45pm | 12.7% | -361 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:00pm | 9.2% | -316 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:45pm | 29.9% | -241 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:00pm | 29.1% | -196 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 35.9% | -256 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 1.8% | -361 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 10:30pm | 7.3% | -526 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 9:30pm | 13.4% | -466 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 8:30pm | 43.7% | -406 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 7:30pm | 73% | -346 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 6:30pm | 72.3% | -286 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 5:30pm | 66.3% | -226 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 10:30pm | 5.3% | -526 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 7:45pm | 26.3% | -361 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 6:15pm | 10.4% | -271 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 61.4% | -196 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:15pm | 20.5% | -451 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:50pm | 43.6% | -426 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 39.5% | -316 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:25pm | 27.5% | -281 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | RealD 3D | 7:50pm | 24.3% | -366 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 11:00pm | 0% | -556 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 10:30pm | 18.8% | -526 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 9:30pm | 24% | -466 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 8:45pm | 48.5% | -421 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 7:45pm | 66.7% | -361 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:00pm | 63.2% | -256 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 7:00pm | 17.6% | -316 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 8:00pm | 66.4% | -376 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 4% | -493 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 10% | -418 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 26% | -328 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 52.2% | -253 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 25.5% | -223 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 9:00pm | 20.3% | -433 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 36.4% | -343 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 2.3% | -448 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 12.6% | -238 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:30pm | 0.4% | -523 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:45pm | 5.8% | -358 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 9.6% | -433 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -493 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 1% | -208 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:00pm | 45.4% | -313 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:15pm | 4.7% | -446 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:30pm | 15.1% | -281 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 40.2% | -206 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 6.9% | -416 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 9.1% | -356 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 17.4% | -251 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -491 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 7.6% | -386 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 9.2% | -326 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 10:30pm | 0% | -522 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 9:30pm | 4.2% | -461 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 8:15pm | 40% | -386 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 7:30pm | 59.5% | -341 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 7:45pm | 27.8% | -356 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -431 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 6.9% | -386 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 9.7% | -266 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 21.6% | -221 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -461 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 4.4% | -311 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 8.9% | -296 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 9:45pm | 0.6% | -476 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 16% | -311 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 12.1% | -341 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 25.5% | -206 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0.6% | -416 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -371 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 14.1% | -251 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 7:40pm | 25.3% | -352 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 37% | -221 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0.7% | -491 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 3.8% | -461 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 17.5% | -281 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 0.5% | -491 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 16.2% | -311 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 6.9% | -371 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 36% | -221 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 11.8% | -281 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:15pm | 0% | -446 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:15pm | 22.2% | -206 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 10:00pm | 8.6% | -491 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:00pm | 7.8% | -369 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 16.2% | -444 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 25.4% | -279 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0% | -414 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 3.6% | -309 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:40pm | 2.4% | -230 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 5.9% | -294 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 10:15pm | 0.6% | -504 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 7:30pm | 9.5% | -339 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:45pm | 0.9% | -535 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 9.7% | -369 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 5:15pm | 15.8% | -204 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 0.7% | -489 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 40.8% | -324 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 2.5% | -399 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -459 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -429 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -354 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 5.9% | -219 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:30pm | 1.8% | -520 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:05pm | 0% | -494 min |
| AMC Sunset Place 24 | The Drama | undefined | 9:40pm | 0% | -470 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:40pm | 5.3% | -350 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:10pm | 35.3% | -320 min |
| AMC Sunset Place 24 | The Drama | undefined | 6:45pm | 1.6% | -294 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:00pm | 8.9% | -429 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:00pm | 30.4% | -309 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:15pm | 26.8% | -264 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:45pm | 5.7% | -234 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 7:30pm | 19.6% | -339 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -459 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 18.8% | -384 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 12.2% | -279 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 14.5% | -219 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -429 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -369 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 6.9% | -204 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:45pm | 14.8% | -353 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:00pm | 36.7% | -187 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 35.9% | -293 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -473 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 11.6% | -368 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -338 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 11.8% | -263 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 1.9% | -232 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 10.1% | -202 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:10pm | 0% | -198 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 0% | -522 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 5.8% | -398 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:40pm | 1.4% | -528 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:25pm | 5.8% | -513 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:10pm | 8.1% | -498 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 9:15pm | 25% | -443 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:35pm | 30.4% | -342 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:00pm | 29.8% | -308 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 6:30pm | 37.8% | -278 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:15pm | 4.6% | -383 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 10.5% | -308 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 2% | -338 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 5% | -278 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 10:00pm | 6.1% | -488 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 8:45pm | 0% | -413 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 7:15pm | 24.2% | -323 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 2.1% | -457 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 12.3% | -292 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:00pm | 0% | -247 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0.5% | -352 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0% | -187 min |
| AMC West Shore 14 | The Drama | undefined | 10:00pm | 0.5% | -487 min |
| AMC West Shore 14 | The Drama | undefined | 7:30pm | 5.1% | -337 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 1.4% | -307 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -502 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -442 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 7:30pm | 4.1% | -337 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 6:30pm | 3.7% | -277 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 5:15pm | 13.8% | -202 min |
| AMC Bradenton 20 | The Drama | undefined | 10:00pm | 0% | -487 min |
| AMC Bradenton 20 | The Drama | undefined | 7:15pm | 5.6% | -322 min |
| AMC Bradenton 20 | The Drama | undefined | 6:15pm | 2.8% | -262 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 31.6% | -517 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 78.6% | -352 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 93.2% | -187 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 2.3% | -487 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 1.7% | -457 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 9.1% | -292 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 25% | -277 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 44.2% | -247 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 13.5% | -397 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 5.8% | -322 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 58.8% | -262 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 4.8% | -232 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:45pm | 21.6% | -472 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:00pm | 73.5% | -307 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 74.8% | -217 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 6:15pm | 63.1% | -262 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 10:00pm | 63.8% | -487 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 9:30pm | 8.7% | -457 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 7:15pm | 89.9% | -322 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:30pm | 0.9% | -456 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 1.9% | -516 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 42.2% | -351 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 72.7% | -185 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -426 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 2.1% | -381 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 1.1% | -366 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 3.6% | -261 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 5.3% | -200 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 6.4% | -215 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 10:10pm | 2.2% | -496 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 7:10pm | 14% | -316 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:00pm | 0% | -546 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:20pm | 2.1% | -385 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:20pm | 11.7% | -325 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 2.9% | -276 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | RealD 3D | 9:10pm | 2.5% | -436 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 7:45pm | 12.4% | -351 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:10pm | 1.3% | -315 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 3.3% | -425 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:10pm | 19.2% | -255 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -485 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -470 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 0% | -395 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 2.8% | -230 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -500 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 4% | -350 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 4% | -195 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:00pm | 0% | -485 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 9:00pm | 0% | -425 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 7:30pm | 1.7% | -335 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 6:00pm | 13.3% | -245 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 0.9% | -425 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 4.2% | -260 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:30pm | 17% | -215 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -485 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 2.9% | -350 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 4.1% | -320 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 3% | -290 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 10:15pm | 5.1% | -500 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 9:30pm | 27.3% | -455 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 8:30pm | 58.1% | -395 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:30pm | 79.6% | -335 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:00pm | 70% | -305 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 5:45pm | 70.3% | -230 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 34.5% | -290 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 2.4% | -455 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 10:00pm | 0% | -485 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -469 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -364 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 15.9% | -199 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 10:20pm | 0% | -503 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -424 min |
| AMC Worldgate 9 | The Drama | undefined | 10:15pm | 0% | -499 min |
| AMC Worldgate 9 | The Drama | undefined | 7:30pm | 3.8% | -334 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 2.7% | -424 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 38.4% | -259 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 0% | -394 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 0% | -364 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 0% | -349 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 2.7% | -334 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 0% | -229 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 0% | -199 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 2.1% | -184 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -454 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 0% | -289 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 9:15pm | 2% | -439 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 3.2% | -469 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 23.7% | -304 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 4.9% | -364 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 10.8% | -199 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -454 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 3.4% | -289 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -439 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 1% | -394 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -274 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 1.4% | -229 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:00pm | 40.7% | -184 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 9:30pm | 0% | -454 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 8:30pm | 0% | -394 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 7:30pm | 8.1% | -334 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 6:30pm | 4.9% | -274 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 9:10pm | 0% | -434 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 5.4% | -274 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -469 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -334 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -289 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0.5% | -244 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:05pm | 4.8% | -428 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0.8% | -408 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 12.3% | -303 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 7.7% | -243 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:25pm | 23.8% | -208 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -273 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 3.6% | -183 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 8:45pm | 4.4% | -408 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 7:15pm | 12% | -318 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:50pm | 4.3% | -473 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 56.5% | -303 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 10:50pm | 0% | -533 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 8:00pm | 2% | -363 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 5:10pm | 26.2% | -193 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -423 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 6:10pm | 15.5% | -253 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 10:20pm | 18.9% | -503 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 7:20pm | 87.4% | -323 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 2.7% | -528 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 15.9% | -363 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 31% | -198 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 0% | -498 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 10.3% | -408 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 10.3% | -243 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -468 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 9:15pm | 8.7% | -438 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 7:45pm | 19% | -348 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 6:30pm | 32.5% | -273 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 5:00pm | 15.2% | -183 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 3.6% | -362 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 0.7% | -467 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 15.1% | -302 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | undefined | 6:00pm | 8.9% | -242 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:30pm | 4.1% | -512 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 1.1% | -362 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 5:15pm | 0% | -197 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -542 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 0% | -422 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 2% | -392 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 5.3% | -257 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 0% | -227 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -482 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:30pm | 4.3% | -452 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:15pm | 7.1% | -317 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 4.3% | -287 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 20.1% | -212 min |
| AMC Sugarloaf Mills 18 | The Drama | Laser at AMC | 7:15pm | 3.5% | -317 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 0% | -572 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 23.1% | -407 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 14.1% | -272 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 5.6% | -197 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -542 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 2.8% | -497 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -377 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 5.6% | -332 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:30pm | 0% | -212 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 11:10pm | 4.4% | -552 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 9:15pm | 0% | -437 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 8:20pm | 33.3% | -381 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 7:50pm | 37.2% | -351 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 5:30pm | 60% | -212 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 2.4% | -482 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 1.3% | -407 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 2.4% | -317 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 9:30pm | 4.7% | -452 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 9:00pm | 2.9% | -422 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 4.6% | -347 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 6:45pm | 4.7% | -287 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 6:15pm | 4.2% | -257 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 3.6% | -182 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:15pm | 5.6% | -316 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 2.9% | -421 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 22.8% | -256 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 14.7% | -346 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 0% | -286 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -181 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:15pm | 27.2% | -376 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:30pm | 17.5% | -211 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 5:45pm | 10.7% | -226 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 11:10pm | 1.3% | -550 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 1.1% | -510 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 9:50pm | 0% | -469 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:20pm | 14.9% | -199 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -450 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:10pm | 4.5% | -430 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 8:00pm | 3.4% | -360 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 7:20pm | 27.4% | -319 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:40pm | 5.3% | -280 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:20pm | 14.6% | -259 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 7:15pm | 16.4% | -315 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 6:15pm | 6.8% | -255 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:00pm | 1.9% | -420 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 20.9% | -240 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 19.5% | -330 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -540 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 10% | -360 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 10.8% | -180 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 12.5% | -450 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:50pm | 68.8% | -289 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 6:30pm | 13.7% | -270 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 18% | -210 min |
| AMC Concord Mills 24 | The Drama | undefined | 10:15pm | 1.5% | -495 min |
| AMC Concord Mills 24 | The Drama | undefined | 9:15pm | 2.3% | -435 min |
| AMC Concord Mills 24 | The Drama | undefined | 8:15pm | 9.8% | -375 min |
| AMC Concord Mills 24 | The Drama | undefined | 7:15pm | 13.4% | -315 min |
| AMC Concord Mills 24 | The Drama | undefined | 6:15pm | 19.3% | -255 min |
| AMC Concord Mills 24 | The Drama | undefined | 5:15pm | 16.3% | -195 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | IMAX at AMC | 9:00pm | 0.8% | -420 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | IMAX at AMC | 6:15pm | 0% | -255 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 1% | -480 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 0% | -435 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 8:35pm | 0% | -394 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -345 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -270 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0% | -180 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:50pm | 0% | -229 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -450 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 8:15pm | 0% | -375 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -285 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -210 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 5:15pm | 0% | -195 min |
| AMC Forum 30 | The Drama | undefined | 9:45pm | 1.5% | -465 min |
| AMC Forum 30 | The Drama | undefined | 6:00pm | 0% | -240 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | IMAX at AMC | 5:40pm | 0.6% | -219 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 0% | -313 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -358 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 0% | -189 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -418 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 9:45pm | 0% | -463 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 7:00pm | 0% | -298 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | IMAX at AMC | 9:45pm | 3.7% | -463 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 7.1% | -298 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 4.5% | -388 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 6.4% | -328 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 4.5% | -223 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 3.4% | -268 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 3.4% | -433 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 8:00pm | 5.5% | -358 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 5:15pm | 14.1% | -193 min |
| AMC Livonia 20 | The Drama | undefined | 10:30pm | 0% | -508 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0% | -478 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 3.3% | -208 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -508 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 8:45pm | 2.2% | -403 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 7:45pm | 1.7% | -343 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -283 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0% | -238 min |
| AMC John R 15 | The Drama | undefined | 10:05pm | 0% | -482 min |
| AMC John R 15 | The Drama | undefined | 8:45pm | 0% | -403 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | IMAX at AMC | 9:00pm | 1.5% | -418 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | IMAX at AMC | 6:15pm | 14.2% | -253 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 10.3% | -328 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 1.1% | -512 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 1.1% | -358 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 5:20pm | 10.5% | -197 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | undefined | 9:35pm | 2.5% | -452 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | undefined | 7:00pm | 11.5% | -298 min |
| AMC Castleton Square 14 | The Drama | undefined | 10:30pm | 1.4% | -508 min |
| AMC Castleton Square 14 | The Drama | undefined | 5:00pm | 24.3% | -178 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 2.3% | -493 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 26.3% | -328 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 0% | -298 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0% | -208 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 8:45pm | 0% | -403 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -463 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 6:30pm | 1.4% | -268 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0% | -238 min |
| AMC Perry Crossing 18 | The Drama | undefined | 10:00pm | 0.8% | -478 min |
| AMC Perry Crossing 18 | The Drama | undefined | 7:45pm | 0% | -343 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 3.3% | -461 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 3.5% | -296 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:00pm | 0% | -537 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:30pm | 3.1% | -386 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 0% | -506 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 1.5% | -416 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 13.2% | -281 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 0% | -251 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 6.8% | -176 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -431 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 8:00pm | 0% | -356 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0.7% | -326 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 6:30pm | 0.9% | -266 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | -206 min |
| AMC Thoroughbred 20 | The Drama | undefined | 9:15pm | 1.9% | -431 min |
| AMC Thoroughbred 20 | The Drama | undefined | 6:30pm | 11.3% | -266 min |
| AMC Thoroughbred 20 | The Drama | undefined | 5:00pm | 34.3% | -176 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 5.9% | -326 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 11.2% | -176 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -356 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0% | -236 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -446 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -416 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 7:00pm | 0% | -296 min |
| AMC Bellevue 12 | The Drama | undefined | 9:15pm | 8.7% | -431 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 1.1% | -461 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 2.6% | -416 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 14.9% | -251 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | PRIME at AMC | 5:00pm | 2.2% | -176 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -491 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 4.3% | -326 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -446 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -431 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 8:15pm | 0% | -371 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 92.6% | -281 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 6:30pm | 2.1% | -266 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 5:15pm | 0% | -191 min |
| AMC Easton Town Center 30 | The Drama | undefined | 10:30pm | 0% | -506 min |
| AMC Easton Town Center 30 | The Drama | undefined | 8:00pm | 0% | -356 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:30pm | 0% | -326 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:00pm | 20.4% | -296 min |
| AMC Easton Town Center 30 | The Drama | undefined | 6:00pm | 23.4% | -236 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:00pm | 18.1% | -236 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 10:45pm | 0% | -521 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 9:45pm | 4.7% | -461 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 8:45pm | 0.8% | -401 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 8:00pm | 4% | -356 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 7:45pm | 3.3% | -341 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 7:00pm | 11.8% | -296 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 6:45pm | 18% | -281 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 6:15pm | 52.4% | -251 min |
| AMC Dublin Village 18 | The Super Mario Galaxy Movie | undefined | 5:15pm | 31% | -191 min |
| AMC Dublin Village 18 | The Drama | undefined | 7:15pm | 50% | -311 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | IMAX at AMC | 9:45pm | 0.9% | -461 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 8.2% | -296 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 9:15pm | 1.3% | -431 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 8:30pm | 0% | -386 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 7:45pm | 0% | -341 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 6:30pm | 1.9% | -266 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 5:45pm | 0.9% | -221 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 0.4% | -176 min |
| AMC Grove City 14 | The Drama | undefined | 9:40pm | 0.7% | -456 min |
| AMC Grove City 14 | The Drama | undefined | 7:15pm | 2.2% | -311 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 0.6% | -504 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 5.6% | -339 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 1.5% | -174 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0% | -444 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 7.4% | -279 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 1.1% | -414 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -369 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 0% | -249 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 10:00pm | 2.5% | -474 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 8:30pm | 0% | -384 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 7:15pm | 4.9% | -309 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 5:45pm | 1.7% | -219 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 9:00pm | 14.8% | -414 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 6:10pm | 20.4% | -245 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 10:30pm | 0% | -504 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 1.9% | -339 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 5.1% | -174 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 3.8% | -369 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 27.1% | -204 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 9:05pm | 2.9% | -419 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 8:45pm | 2.6% | -399 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 7:00pm | 8.5% | -294 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 6:20pm | 2.9% | -254 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 6:00pm | 15.8% | -234 min |
| AMC West Chester 18 | The Drama | undefined | 10:05pm | 3.9% | -479 min |
| AMC West Chester 18 | The Drama | undefined | 7:00pm | 25% | -294 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:30pm | 1.4% | -504 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:45pm | 10% | -339 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:00pm | 18.1% | -174 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 4.3% | -444 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | PRIME at AMC | 5:45pm | 10.7% | -219 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 4.3% | -369 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 6:10pm | 5.6% | -244 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 6.5% | -204 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 4.4% | -474 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 10.2% | -309 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 10:30pm | 1.5% | -504 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 9:55pm | 12.5% | -469 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:45pm | 51.5% | -339 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:15pm | 9.7% | -309 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:05pm | 53.1% | -298 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 6:15pm | 8.3% | -249 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 2.7% | -339 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 4.9% | -174 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0.5% | -444 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 8.2% | -279 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 4.1% | -294 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -489 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 8:45pm | 0% | -399 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 8:30pm | 0% | -384 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 7:15pm | 2.4% | -309 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 6:15pm | 3.7% | -249 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 6:00pm | 2% | -234 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 6% | -204 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:15pm | 8.6% | -189 min |
| AMC Regency 24 | The Drama | undefined | 10:30pm | 0% | -504 min |
| AMC Regency 24 | The Drama | undefined | 10:00pm | 1.4% | -474 min |
| AMC Regency 24 | The Drama | undefined | 8:30pm | 0% | -384 min |
| AMC Regency 24 | The Drama | undefined | 7:15pm | 9.6% | -309 min |
| AMC Regency 24 | The Drama | undefined | 5:45pm | 6% | -219 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:00pm | 0% | -474 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | IMAX at AMC | 7:15pm | 6.4% | -309 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 2.7% | -414 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 10.7% | -249 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 8:15pm | 3.9% | -369 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:45pm | 0% | -339 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 6:45pm | 3.7% | -279 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 10.2% | -204 min |
| AMC Orange Park 24 | The Drama | undefined | 9:45pm | 4.3% | -459 min |
| AMC Orange Park 24 | The Drama | undefined | 8:15pm | 0% | -369 min |
| AMC Orange Park 24 | The Drama | undefined | 7:00pm | 4.3% | -294 min |

**Issues:** AMC Empire 25: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Empire 25: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Empire 25: No seat map for The Drama Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Lincoln Square 13: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Lincoln Square 13: No seat map for The Drama Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie undefined; AMC Kips Bay 15: No seat map for The Drama undefined; AMC Kips Bay 15: No seat map for The Drama undefined; AMC Kips Bay 15: No seat map for The Drama undefined; AMC Kips Bay 15: No seat map for The Drama undefined; AMC Kips Bay 15: No seat map for The Drama undefined; AMC Kips Bay 15: No seat map for The Drama undefined; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC 34th Street 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC 34th Street 14: No seat map for The Drama Laser at AMC; AMC 34th Street 14: No seat map for The Drama Laser at AMC; AMC 34th Street 14: No seat map for The Drama Laser at AMC; AMC 34th Street 14: No seat map for The Drama Laser at AMC; AMC 84th Street 6: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC 84th Street 6: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC 84th Street 6: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC 84th Street 6: No seat map for The Drama Laser at AMC; AMC 84th Street 6: No seat map for The Drama Laser at AMC; AMC 84th Street 6: No seat map for The Drama Laser at AMC; AMC 84th Street 6: No seat map for The Drama Open Caption (On-screen Subtitles); AMC Newport Centre 11: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Newport Centre 11: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Newport Centre 11: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Newport Centre 11: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Newport Centre 11: No seat map for The Drama Laser at AMC; AMC Newport Centre 11: No seat map for The Drama Laser at AMC; AMC Newport Centre 11: No seat map for The Drama Laser at AMC; AMC Newport Centre 11: No seat map for The Drama Laser at AMC; AMC Magic Johnson Harlem 9: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Magic Johnson Harlem 9: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Magic Johnson Harlem 9: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Magic Johnson Harlem 9: No seat map for The Drama Laser at AMC; AMC Magic Johnson Harlem 9: No seat map for The Drama Laser at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie XL at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Boston Common 19: No seat map for The Drama Laser at AMC; AMC Boston Common 19: No seat map for The Drama Laser at AMC; AMC Boston Common 19: No seat map for The Drama Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Assembly Row 12: No seat map for The Drama Laser at AMC; AMC Framingham 16: No seat map for The Super Mario Galaxy Movie PRIME at AMC; AMC Framingham 16: No seat map for The Super Mario Galaxy Movie PRIME at AMC; AMC Framingham 16: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Framingham 16: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Framingham 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Framingham 16: No seat map for The Super Mario Galaxy Movie English Spoken with Chinese and English Subtitles; AMC Framingham 16: No seat map for The Drama Laser at AMC; AMC Framingham 16: No seat map for The Drama Laser at AMC; AMC Braintree 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Braintree 10: No seat map for The Drama Laser at AMC; AMC Burlington Cinema 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Burlington Cinema 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Burlington Cinema 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Burlington Cinema 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Burlington Cinema 10: No seat map for The Drama Laser at AMC; AMC Burlington Cinema 10: No seat map for The Drama Laser at AMC; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Methuen 20: No seat map for The Drama Laser at AMC; AMC Methuen 20: No seat map for The Drama Laser at AMC; AMC Methuen 20: No seat map for The Drama Laser at AMC; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Aventura 24: No seat map for The Drama Laser at AMC; AMC Aventura 24: No seat map for The Drama Laser at AMC; AMC Sunset Place 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Sunset Place 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Sunset Place 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Sunset Place 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Sunset Place 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Sunset Place 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Sunset Place 24: No seat map for The Drama undefined; AMC Sunset Place 24: No seat map for The Drama undefined; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Coral Ridge 10: No seat map for The Drama Dine-In Delivery to Seat; AMC Pompano Beach 18: No seat map for The Super Mario Galaxy Movie PRIME at AMC; AMC Pompano Beach 18: No seat map for The Super Mario Galaxy Movie PRIME 3D; AMC Pompano Beach 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Pompano Beach 18: No seat map for The Drama Laser at AMC; AMC Pompano Beach 18: No seat map for The Drama Laser at AMC; AMC Pompano Beach 18: No seat map for The Drama Laser at AMC; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Sundial 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Sundial 12: No seat map for The Super Mario Galaxy Movie PRIME at AMC; AMC Sundial 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Sundial 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Sundial 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC West Shore 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC West Shore 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC West Shore 14: No seat map for The Super Mario Galaxy Movie undefined; AMC West Shore 14: No seat map for The Super Mario Galaxy Movie undefined; AMC West Shore 14: No seat map for The Super Mario Galaxy Movie undefined; AMC West Shore 14: No seat map for The Super Mario Galaxy Movie undefined; AMC West Shore 14: No seat map for The Drama undefined; AMC Bradenton 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Bradenton 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Disney Springs 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC DINE-IN Disney Springs 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC DINE-IN Disney Springs 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Disney Springs 24: No seat map for The Drama Laser at AMC; AMC Altamonte Mall 18: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Altamonte Mall 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Altamonte Mall 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Altamonte Mall 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Altamonte Mall 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Altamonte Mall 18: No seat map for The Drama Laser at AMC; AMC Altamonte Mall 18: No seat map for The Drama Laser at AMC; AMC Tysons Corner 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Tysons Corner 16: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Tysons Corner 16: No seat map for The Drama Laser at AMC; AMC Hoffman Center 22: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Hoffman Center 22: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Hoffman Center 22: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Hoffman Center 22: No seat map for The Drama Laser at AMC; AMC Hoffman Center 22: No seat map for The Drama Open Caption (On-screen Subtitles); AMC Georgetown 14: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Georgetown 14: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Shirlington 7: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Shirlington 7: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Shirlington 7: No seat map for The Drama Laser at AMC; AMC Worldgate 9: No seat map for The Super Mario Galaxy Movie undefined; AMC Worldgate 9: No seat map for The Super Mario Galaxy Movie undefined; AMC Neshaminy 24: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Neshaminy 24: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Neshaminy 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Neshaminy 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Neshaminy 24: No seat map for The Drama Laser at AMC; AMC Cherry Hill 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Voorhees 16: No seat map for The Super Mario Galaxy Movie undefined; AMC Voorhees 16: No seat map for The Super Mario Galaxy Movie undefined; AMC Voorhees 16: No seat map for The Super Mario Galaxy Movie undefined; AMC Voorhees 16: No seat map for The Drama undefined; AMC Voorhees 16: No seat map for The Drama undefined; AMC Plymouth Meeting Mall 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Plymouth Meeting Mall 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Plymouth Meeting Mall 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Plymouth Meeting Mall 12: No seat map for The Drama Laser at AMC; AMC Plymouth Meeting Mall 12: No seat map for The Drama Laser at AMC; AMC Phipps Plaza 14: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Phipps Plaza 14: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Phipps Plaza 14: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Phipps Plaza 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Phipps Plaza 14: No seat map for The Drama Laser at AMC; AMC Phipps Plaza 14: No seat map for The Drama Laser at AMC; AMC Phipps Plaza 14: No seat map for The Drama Laser at AMC; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Northlake 14: No seat map for The Drama undefined; AMC Northlake 14: No seat map for The Drama undefined; AMC Sugarloaf Mills 18: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Sugarloaf Mills 18: No seat map for The Super Mario Galaxy Movie XL at AMC; AMC Sugarloaf Mills 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Sugarloaf Mills 18: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Sugarloaf Mills 18: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Sugarloaf Mills 18: No seat map for The Drama Laser at AMC; AMC Barrett Commons 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Barrett Commons 24: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Barrett Commons 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Barrett Commons 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Camp Creek 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Camp Creek 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Camp Creek 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Camp Creek 14: No seat map for The Drama undefined; AMC Camp Creek 14: No seat map for The Drama undefined; AMC DINE-IN North Point Mall 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC DINE-IN North Point Mall 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN North Point Mall 12: No seat map for The Super Mario Galaxy Movie Dine-In Delivery to Seat; AMC DINE-IN North Point Mall 12: No seat map for The Drama Dine-In Delivery to Seat; AMC DINE-IN North Point Mall 12: No seat map for The Drama Dine-In Delivery to Seat; AMC DINE-IN North Point Mall 12: No seat map for The Drama Dine-In Delivery to Seat; AMC Carolina Pavilion 22: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Carolina Pavilion 22: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Carolina Pavilion 22: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Carolina Pavilion 22: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Carolina Pavilion 22: No seat map for The Super Mario Galaxy Movie undefined; AMC Carolina Pavilion 22: No seat map for The Super Mario Galaxy Movie undefined; AMC Carolina Pavilion 22: No seat map for The Drama undefined; AMC Carolina Pavilion 22: No seat map for The Drama undefined; AMC Concord Mills 24: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Concord Mills 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Concord Mills 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Forum 30: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Forum 30: No seat map for The Super Mario Galaxy Movie undefined; AMC Forum 30: No seat map for The Drama undefined; AMC Star Great Lakes 25: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Star Great Lakes 25: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Star Great Lakes 25: No seat map for The Super Mario Galaxy Movie undefined; AMC Livonia 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Livonia 20: No seat map for The Drama undefined; AMC John R 15: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC John R 15: No seat map for The Super Mario Galaxy Movie undefined; AMC John R 15: No seat map for The Super Mario Galaxy Movie undefined; AMC John R 15: No seat map for The Drama undefined; AMC Castleton Square 14: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Castleton Square 14: No seat map for The Drama undefined; AMC Perry Crossing 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Perry Crossing 18: No seat map for The Super Mario Galaxy Movie undefined; AMC Perry Crossing 18: No seat map for The Super Mario Galaxy Movie undefined; AMC Perry Crossing 18: No seat map for The Drama undefined; AMC Thoroughbred 20: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Thoroughbred 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Thoroughbred 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Thoroughbred 20: No seat map for The Super Mario Galaxy Movie undefined; AMC Thoroughbred 20: No seat map for The Super Mario Galaxy Movie undefined; AMC Thoroughbred 20: No seat map for The Drama undefined; AMC Thoroughbred 20: No seat map for The Drama undefined; AMC Bellevue 12: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Bellevue 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Bellevue 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Bellevue 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Bellevue 12: No seat map for The Drama undefined; AMC Easton Town Center 30: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Easton Town Center 30: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Easton Town Center 30: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Easton Town Center 30: No seat map for The Super Mario Galaxy Movie undefined; AMC Easton Town Center 30: No seat map for The Super Mario Galaxy Movie undefined; AMC Easton Town Center 30: No seat map for The Drama undefined; AMC Easton Town Center 30: No seat map for The Drama undefined; AMC Easton Town Center 30: No seat map for The Drama undefined; AMC Easton Town Center 30: No seat map for The Drama undefined; AMC Dublin Village 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Dublin Village 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Dublin Village 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Dublin Village 18: No seat map for The Super Mario Galaxy Movie undefined; AMC Dublin Village 18: No seat map for The Drama undefined; AMC Grove City 14: No seat map for The Super Mario Galaxy Movie undefined; AMC Newport On The Levee 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Newport On The Levee 20: No seat map for The Drama undefined; AMC Newport On The Levee 20: No seat map for The Drama undefined; AMC West Chester 18: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC West Chester 18: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC West Chester 18: No seat map for The Super Mario Galaxy Movie undefined; AMC Waterfront 22: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Waterfront 22: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Regency 24: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Regency 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Regency 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Regency 24: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Regency 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Orange Park 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Orange Park 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Orange Park 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Orange Park 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Orange Park 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Orange Park 24: No seat map for The Drama undefined

---

## 2026-04-05 17:08 — ET Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie, The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Empire 25 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 0.7% | -288 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 24% | -123 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 11:30pm | 3% | -393 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:45pm | 19.7% | -228 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 74.7% | -63 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -363 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 0% | -318 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 11.5% | -198 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 10.1% | -153 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 38.2% | -3 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 1.5% | -258 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 20.9% | -93 min |
| AMC Empire 25 | The Drama | Laser at AMC | 11:15pm | 0% | -378 min |
| AMC Empire 25 | The Drama | Laser at AMC | 10:00pm | 1.7% | -303 min |
| AMC Empire 25 | The Drama | Laser at AMC | 9:45pm | 9.2% | -288 min |
| AMC Empire 25 | The Drama | Laser at AMC | 8:30pm | 14.4% | -213 min |
| AMC Empire 25 | The Drama | Laser at AMC | 8:15pm | 10.4% | -198 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:45pm | 35.4% | -168 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:15pm | 32.1% | -138 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:00pm | 20% | -123 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:45pm | 59.8% | -48 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:30pm | 58.3% | -33 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:00pm | 59.5% | -3 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 13.8% | -303 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 63.1% | -123 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 10% | -243 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 47.3% | -63 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 60.9% | -3 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 5.5% | -168 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 10:30pm | 8.2% | -333 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 9:30pm | 20.3% | -273 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 8:30pm | 60.8% | -213 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 7:45pm | 84% | -168 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 7:30pm | 77.4% | -153 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 6:30pm | 80.7% | -93 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 5:30pm | 80.9% | -33 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:00pm | 0.6% | -363 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:15pm | 15.8% | -198 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:30pm | 35.1% | -33 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -243 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 37% | -138 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 10:30pm | 5.3% | -333 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 10:05pm | 0% | -308 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 7:45pm | 35.1% | -168 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 6:15pm | 21.5% | -78 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 66.7% | -3 min |
| AMC Kips Bay 15 | The Drama | undefined | 10:45pm | 8.3% | -348 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:45pm | 9% | -288 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:15pm | 43.6% | -258 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:50pm | 64.4% | -232 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:00pm | 75.9% | -183 min |
| AMC Kips Bay 15 | The Drama | undefined | 7:00pm | 82.8% | -123 min |
| AMC Kips Bay 15 | The Drama | undefined | 6:00pm | 78.9% | -63 min |
| AMC Kips Bay 15 | The Drama | undefined | 5:15pm | 80% | -18 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:00pm | 0.5% | -363 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:20pm | 18% | -202 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:45pm | 67.8% | -48 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:30pm | 0.8% | -273 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 46.2% | -123 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:25pm | 54.1% | -88 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 2.7% | -333 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | RealD 3D | 7:50pm | 33.8% | -172 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 11:00pm | 0% | -363 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 10:30pm | 23.2% | -333 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 9:30pm | 38.5% | -273 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 8:45pm | 52.9% | -228 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 7:45pm | 68.1% | -168 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:45pm | 66.3% | -108 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:00pm | 76.5% | -63 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:30pm | 71.9% | -33 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:10pm | 71.6% | -13 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:00pm | 75.4% | -3 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 10% | -288 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 10.6% | -243 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 78.9% | -63 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 7:00pm | 49.4% | -123 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:45pm | 0% | -348 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:00pm | 9.6% | -303 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 8:00pm | 67.8% | -183 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 7:30pm | 60.6% | -153 min |
| AMC 84th Street 6 | The Drama | Open Caption (On-screen Subtitles) | 7:15pm | 73.7% | -138 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 6% | -302 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 28.9% | -227 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 64% | -137 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 68.9% | -62 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 3.1% | -362 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 2.2% | -257 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 26.5% | -197 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 82.4% | -92 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 93.9% | -32 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 10:30pm | 8.6% | -332 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 9:00pm | 46.8% | -242 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 7:45pm | 75.7% | -167 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 6:15pm | 91.1% | -77 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 5:00pm | 88.6% | -2 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 13.1% | -317 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 74.8% | -152 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 2.3% | -257 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 13.1% | -92 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 5.1% | -212 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 29.9% | -47 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 10:00pm | 2.8% | -302 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 7:15pm | 33.1% | -137 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:30pm | 0.4% | -332 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:45pm | 10.5% | -167 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:00pm | 31.9% | -2 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 15.8% | -242 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 33.3% | -77 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | XL at AMC | 10:00pm | 0% | -302 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | XL at AMC | 7:15pm | 1.3% | -137 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 5.9% | -197 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 0% | -32 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 2.5% | -17 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 4.8% | -272 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 9.7% | -107 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 10:30pm | 0.7% | -332 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 10:00pm | 7% | -302 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:30pm | 44.7% | -152 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:00pm | 59% | -122 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:15pm | 4.7% | -257 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:30pm | 36% | -92 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 0% | -347 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 22.4% | -182 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 70.7% | -17 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 13.9% | -227 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 13.6% | -167 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 27.1% | -62 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 31.4% | -32 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -362 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 1.5% | -302 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 13.4% | -197 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 14.6% | -137 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 10:30pm | 0% | -332 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 9:30pm | 13.3% | -272 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 8:15pm | 41.4% | -197 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 7:30pm | 60.4% | -152 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 5:30pm | 55.5% | -32 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 10:30pm | 0% | -332 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 7:45pm | 41.2% | -167 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 5:00pm | 80.2% | -2 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -302 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 1.6% | -242 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 10.3% | -197 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 6.6% | -152 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 21% | -77 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 40.5% | -32 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -287 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 0% | -272 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 4.4% | -122 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 8.9% | -107 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 10:15pm | 0% | -317 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 10:15pm | 0% | -317 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 7:15pm | 65.7% | -137 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 9:45pm | 0.6% | -287 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 31.3% | -122 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 15.9% | -152 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 47.2% | -17 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 0% | -337 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 0.6% | -227 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 2.8% | -182 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 32.5% | -62 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 10:30pm | 7.6% | -332 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 7:40pm | 74.7% | -162 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 0% | -332 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 5.8% | -212 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 33.8% | -152 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 48.6% | -32 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 0.7% | -302 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 3.8% | -272 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 1.4% | -122 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 20% | -92 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 9:45pm | 6.5% | -287 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 6:45pm | 32.6% | -107 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 0.5% | -300 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 32.8% | -120 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 9.7% | -180 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 51% | 0 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 9:00pm | 3.7% | -240 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 23.7% | -60 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 64% | -30 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -210 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 12.7% | -150 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 19.6% | -90 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:55pm | 2.4% | -296 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:15pm | 0% | -255 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:45pm | 16% | -165 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:15pm | 43.2% | -15 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 10:00pm | 8.6% | -300 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 8:30pm | 2.5% | -210 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 7:15pm | 22.2% | -135 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 5:45pm | 14.8% | -45 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:45pm | 0% | -345 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:00pm | 17.6% | -180 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:15pm | 51% | -15 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 20.2% | -255 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 43.9% | -90 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0% | -225 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:20pm | 2.4% | -200 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 11.8% | -120 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 7.6% | -60 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:40pm | 9.5% | -41 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -315 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 10.5% | -150 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 20.6% | -105 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 10:15pm | 1.8% | -315 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 9:00pm | 6.5% | -240 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 7:30pm | 28.6% | -150 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 6:15pm | 9.5% | -75 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 10:45pm | 0.9% | -345 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 14.7% | -180 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 5:15pm | 27.9% | -15 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 3.4% | -300 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 62.6% | -135 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -210 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 13.5% | -45 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -285 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -270 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -240 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 7:45pm | 2.4% | -165 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 7:00pm | 3.3% | -120 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 6:45pm | 3.6% | -105 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 6:15pm | 2.6% | -75 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 16.2% | -30 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 5:00pm | 1.2% | 0 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:30pm | 1.8% | -330 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:05pm | 1.2% | -305 min |
| AMC Sunset Place 24 | The Drama | undefined | 9:40pm | 2.4% | -281 min |
| AMC Sunset Place 24 | The Drama | undefined | 8:10pm | 14.3% | -191 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:40pm | 14.6% | -161 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:10pm | 40% | -131 min |
| AMC Sunset Place 24 | The Drama | undefined | 6:45pm | 7.3% | -105 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 2.9% | -330 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -210 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 5.7% | -165 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 20.7% | 0 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:00pm | 7.1% | -240 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:00pm | 39.1% | -120 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:15pm | 42% | -75 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:45pm | 8.6% | -45 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 10:15pm | 2.2% | -315 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 7:30pm | 45.7% | -150 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | PRIME at AMC | 10:00pm | 2.6% | -300 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | PRIME 3D | 7:15pm | 22.7% | -135 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 0% | -270 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 34.2% | -195 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 16.3% | -90 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 35.9% | -30 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 0% | -240 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -180 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 8.5% | -75 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 19.5% | -15 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 9:45pm | 3.1% | -285 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 7:00pm | 8.2% | -120 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 6:00pm | 26.3% | -60 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:00pm | 48.1% | 0 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:40pm | 4.3% | -340 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:25pm | 5.8% | -325 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:10pm | 18.9% | -310 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 9:15pm | 25% | -255 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:35pm | 56.5% | -154 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:00pm | 49% | -120 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:15pm | 8.1% | -195 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:35pm | 17.3% | -34 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | PRIME at AMC | 9:40pm | 2.3% | -280 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | PRIME at AMC | 7:00pm | 11.7% | -120 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 10:05pm | 0% | -304 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 9:10pm | 2% | -250 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 2% | -150 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 6% | -90 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 7.2% | -60 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 10:00pm | 6.1% | -300 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 8:45pm | 0% | -225 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 7:15pm | 40.9% | -135 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 2.1% | 0 min |
| AMC West Shore 14 | The Drama | undefined | 10:00pm | 0.5% | -300 min |
| AMC West Shore 14 | The Drama | undefined | 7:30pm | 5.1% | -150 min |
| AMC West Shore 14 | The Drama | undefined | 7:15pm | 8.5% | -135 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -285 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 1.4% | -180 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 2.3% | -120 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0% | -315 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 0% | -255 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 7:30pm | 8.3% | -150 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 6:30pm | 17% | -90 min |
| AMC Bradenton 20 | The Drama | undefined | 10:00pm | 0% | -300 min |
| AMC Bradenton 20 | The Drama | undefined | 7:15pm | 5.6% | -135 min |
| AMC Bradenton 20 | The Drama | undefined | 6:15pm | 4.6% | -75 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 95.9% | 0 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 9:00pm | 23.8% | -240 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 6:15pm | 63.1% | -75 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 10:00pm | 63.8% | -300 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 9:30pm | 36.2% | -270 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 7:15pm | 88.4% | -135 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 72.1% | 0 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 10:10pm | 4.4% | -309 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 9:10pm | 11.2% | -249 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 7:10pm | 19.9% | -129 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 6:10pm | 50.6% | -69 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:00pm | 0.3% | -359 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:20pm | 4.8% | -199 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:40pm | 32.6% | -39 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:20pm | 15% | -139 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Laser at AMC | 9:55pm | 0% | -294 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 8.4% | -89 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | RealD 3D | 9:10pm | 2.5% | -249 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 10:35pm | 1.8% | -334 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 7:45pm | 19.9% | -164 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 0% | -299 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:10pm | 6.9% | -129 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 4.4% | -239 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:10pm | 36.8% | -69 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 0% | -299 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 0% | -284 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 8:30pm | 0% | -209 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 0% | -149 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 0% | -119 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 4.5% | -44 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 0% | -314 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 4% | -164 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 17.2% | -9 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:15pm | 0% | -314 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:00pm | 0.7% | -299 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 9:00pm | 0% | -239 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 7:30pm | 7.5% | -149 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 6:00pm | 20.2% | -59 min |
| AMC Hoffman Center 22 | The Drama | Open Caption (On-screen Subtitles) | 7:00pm | 0.7% | -119 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 24.3% | 0 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 10:15pm | 11.2% | -314 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 9:30pm | 51.5% | -269 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 8:30pm | 64.9% | -209 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:30pm | 80.6% | -149 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:00pm | 72.9% | -119 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 5:45pm | 79.7% | -44 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 4% | -329 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 8:10pm | 5.8% | -189 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 46.4% | -104 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 2.4% | -269 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 10:00pm | 2% | -299 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 7:10pm | 54.9% | -129 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 0% | -284 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -179 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | RealD 3D | 5:15pm | 27.5% | -14 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 10:20pm | 0% | -319 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -239 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 7:45pm | 15.5% | -164 min |
| AMC Worldgate 9 | The Super Mario Galaxy Movie | undefined | 7:00pm | 3.1% | -119 min |
| AMC Worldgate 9 | The Drama | undefined | 10:15pm | 0% | -314 min |
| AMC Worldgate 9 | The Drama | undefined | 7:30pm | 5.3% | -149 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:00pm | 3.8% | 2 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 9:15pm | 2% | -252 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 6:30pm | 8.7% | -87 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:00pm | 50% | 2 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 9:30pm | 0% | -267 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 8:30pm | 4.8% | -207 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 7:30pm | 11.6% | -147 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 6:30pm | 15.2% | -87 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 9:10pm | 0% | -247 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 7.1% | -87 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -282 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:25pm | 0% | -263 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 8:40pm | 0% | -217 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -147 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:00pm | 1.4% | -117 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -102 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:00pm | 0.5% | -57 min |
| AMC Voorhees 16 | The Drama | undefined | 9:30pm | 1.2% | -267 min |
| AMC Voorhees 16 | The Drama | undefined | 6:40pm | 4.2% | -97 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 27% | 2 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 10:00pm | 1.2% | -297 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 8:45pm | 4.4% | -222 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 8:15pm | 23.8% | -192 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 7:15pm | 24.1% | -132 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:50pm | 8.7% | -287 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 74.6% | -117 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 10:50pm | 2.7% | -347 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 8:00pm | 6.7% | -177 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 5:10pm | 69.1% | -7 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 3.1% | -237 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 6:10pm | 48.1% | -67 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 10:20pm | 27.4% | -317 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 7:20pm | 87.4% | -137 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:45pm | 2.7% | -342 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 18.6% | -177 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:15pm | 60.2% | -12 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 0% | -312 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 9:15pm | 6.5% | -252 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 15.4% | -222 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 3.3% | -147 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 12.9% | -87 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 25.6% | -57 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 9:45pm | 4.4% | -282 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 15.3% | -27 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 5:00pm | 30.5% | 2 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 4.1% | -177 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | IMAX at AMC | 5:15pm | 24.4% | -12 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:45pm | 0.7% | -282 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 21.2% | -117 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 7.8% | -222 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:30pm | 8.6% | -267 min |
| AMC Northlake 14 | The Super Mario Galaxy Movie | undefined | 6:00pm | 34.4% | -57 min |
| AMC Northlake 14 | The Drama | undefined | 10:00pm | 3.8% | -297 min |
| AMC Northlake 14 | The Drama | undefined | 7:15pm | 36.7% | -132 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 11:30pm | 0% | -387 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:45pm | 26.5% | -222 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 63.9% | -57 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:15pm | 0% | -252 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 23.4% | -87 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 6.3% | -177 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 11.2% | -117 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:15pm | 14.8% | -12 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 11:00pm | 0% | -357 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 1.4% | -312 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 4.4% | -192 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 11.3% | -147 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:30pm | 0% | -27 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 11:10pm | 13.3% | -368 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 9:15pm | 8.9% | -252 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 8:20pm | 35.6% | -197 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 7:50pm | 53.5% | -167 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 5:30pm | 73.3% | -27 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 11.3% | 3 min |
| AMC Camp Creek 14 | The Drama | undefined | 10:00pm | 0% | -296 min |
| AMC Camp Creek 14 | The Drama | undefined | 7:15pm | 1% | -131 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 2.7% | 3 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 9:45pm | 3.7% | -281 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 8:30pm | 16.1% | -206 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 7:00pm | 21% | -116 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 5:45pm | 32.1% | -41 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 11:10pm | 1.3% | -367 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 1.1% | -326 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 10:00pm | 4.1% | -296 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 9:50pm | 0% | -286 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 1.3% | -206 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 7:40pm | 8% | -157 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 5.7% | -116 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:20pm | 29.9% | -16 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 10:40pm | 3.4% | -337 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:30pm | 0% | -266 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 9:10pm | 14.6% | -247 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 8:00pm | 9.2% | -176 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 7:20pm | 38.4% | -136 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:40pm | 20% | -97 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:20pm | 25.8% | -76 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 5:40pm | 65.3% | -37 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 10:10pm | 5.5% | -307 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 9:10pm | 5.5% | -247 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 7:15pm | 23.3% | -131 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 6:15pm | 20.5% | -71 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 67.7% | 3 min |
| AMC Concord Mills 24 | The Drama | undefined | 10:15pm | 4.5% | -311 min |
| AMC Concord Mills 24 | The Drama | undefined | 9:15pm | 6.1% | -251 min |
| AMC Concord Mills 24 | The Drama | undefined | 8:15pm | 16.5% | -191 min |
| AMC Concord Mills 24 | The Drama | undefined | 7:15pm | 34.3% | -131 min |
| AMC Concord Mills 24 | The Drama | undefined | 6:15pm | 54.4% | -71 min |
| AMC Concord Mills 24 | The Drama | undefined | 5:15pm | 61.2% | -11 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 1.1% | 3 min |
| AMC Forum 30 | The Drama | undefined | 9:45pm | 1.5% | -281 min |
| AMC Forum 30 | The Drama | undefined | 7:00pm | 2.2% | -116 min |
| AMC Forum 30 | The Drama | undefined | 6:00pm | 0.7% | -56 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | IMAX at AMC | 8:30pm | 0.4% | -206 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | IMAX at AMC | 5:40pm | 3.9% | -37 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 1.2% | -296 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 0.6% | -131 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -176 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | RealD 3D | 5:10pm | 2% | -7 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | undefined | 9:00pm | 0% | -236 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | undefined | 6:20pm | 0% | -76 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 9:45pm | 0% | -281 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 7:00pm | 0% | -116 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | IMAX at AMC | 9:45pm | 4.3% | -281 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 8% | -116 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 10:15pm | 3.6% | -311 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 4.5% | -206 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 10.9% | -146 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 10.9% | -41 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 3.4% | -86 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 9:15pm | 3.4% | -251 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 8:00pm | 5.5% | -176 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | undefined | 5:15pm | 14.1% | -11 min |
| AMC Livonia 20 | The Drama | undefined | 10:30pm | 0% | -326 min |
| AMC Livonia 20 | The Drama | undefined | 7:45pm | 4.5% | -161 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 5% | 3 min |
| AMC John R 15 | The Drama | undefined | 10:05pm | 0% | -300 min |
| AMC John R 15 | The Drama | undefined | 8:45pm | 2.2% | -221 min |
| AMC John R 15 | The Drama | undefined | 7:20pm | 10.5% | -135 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | IMAX at AMC | 9:00pm | 11.9% | -236 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | IMAX at AMC | 6:15pm | 38.8% | -71 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:10pm | 8.2% | -306 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 19.9% | -146 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 10:35pm | 1.1% | -330 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 20% | -176 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 5:20pm | 21.1% | -15 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | undefined | 9:35pm | 4.1% | -270 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | undefined | 7:00pm | 25.4% | -116 min |
| AMC Castleton Square 14 | The Drama | undefined | 5:00pm | 45.7% | 3 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:15pm | 4.6% | -311 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 38.7% | -146 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -191 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 0.7% | -116 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 0.4% | -26 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 8:45pm | 0% | -221 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 10:30pm | 0% | -326 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -281 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 9:15pm | 1.2% | -251 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 6:30pm | 3.2% | -86 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | undefined | 6:00pm | 2.4% | -56 min |
| AMC Perry Crossing 18 | The Drama | undefined | 5:00pm | 4.3% | 3 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 6.8% | 3 min |
| AMC Thoroughbred 20 | The Drama | undefined | 5:00pm | 53.9% | 3 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 18.5% | 3 min |
| AMC Bellevue 12 | The Drama | undefined | 9:15pm | 17.4% | -251 min |
| AMC Bellevue 12 | The Drama | undefined | 6:15pm | 63% | -71 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | PRIME at AMC | 5:00pm | 9.4% | 3 min |
| AMC Easton Town Center 30 | The Drama | undefined | 10:30pm | 0% | -326 min |
| AMC Easton Town Center 30 | The Drama | undefined | 10:15pm | 0% | -311 min |
| AMC Easton Town Center 30 | The Drama | undefined | 10:00pm | 1.9% | -296 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:30pm | 2.6% | -266 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:00pm | 3.9% | -236 min |
| AMC Easton Town Center 30 | The Drama | undefined | 8:00pm | 0% | -176 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:30pm | 7.7% | -146 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:00pm | 33.3% | -116 min |
| AMC Easton Town Center 30 | The Drama | undefined | 6:00pm | 28.6% | -56 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 10.9% | 3 min |
| AMC Grove City 14 | The Drama | undefined | 9:40pm | 0.7% | -276 min |
| AMC Grove City 14 | The Drama | undefined | 7:15pm | 6.7% | -131 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 8.5% | 3 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 10:15pm | 1.5% | -311 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 9:00pm | 14.8% | -236 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 7:20pm | 11.2% | -135 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 6:10pm | 35.2% | -66 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 11% | 4 min |
| AMC West Chester 18 | The Drama | undefined | 10:05pm | 6.6% | -300 min |
| AMC West Chester 18 | The Drama | undefined | 7:00pm | 40.8% | -115 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:00pm | 35.7% | 4 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 10:30pm | 6.1% | -325 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 9:55pm | 15.6% | -290 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:45pm | 54.5% | -160 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:15pm | 15.3% | -130 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:05pm | 59.4% | -120 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 6:15pm | 20.8% | -70 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | IMAX at AMC | 5:00pm | 6.8% | 4 min |
| AMC Regency 24 | The Drama | undefined | 10:30pm | 0% | -325 min |
| AMC Regency 24 | The Drama | undefined | 10:00pm | 1.4% | -295 min |
| AMC Regency 24 | The Drama | undefined | 8:30pm | 2.4% | -205 min |
| AMC Regency 24 | The Drama | undefined | 7:15pm | 15.1% | -130 min |
| AMC Regency 24 | The Drama | undefined | 5:45pm | 9.5% | -40 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 47.1% | 4 min |
| AMC Orange Park 24 | The Drama | undefined | 9:45pm | 4.3% | -280 min |
| AMC Orange Park 24 | The Drama | undefined | 8:15pm | 6.3% | -190 min |
| AMC Orange Park 24 | The Drama | undefined | 7:00pm | 8.5% | -115 min |
| AMC Orange Park 24 | The Drama | undefined | 5:30pm | 9.4% | -25 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 12.5% | 4 min |
| AMC Indianapolis 17 | The Drama | undefined | 10:00pm | 1.9% | -295 min |
| AMC Indianapolis 17 | The Drama | undefined | 8:00pm | 17.3% | -175 min |
| AMC Indianapolis 17 | The Drama | undefined | 5:15pm | 26% | -10 min |

**Issues:** AMC Sunset Place 24: No seat map for The Drama undefined; AMC Veterans 24: No seat map for The Drama Laser at AMC; AMC Bradenton 20: No seat map for The Super Mario Galaxy Movie undefined; AMC Sugarloaf Mills 18: [Errno 32] Broken pipe; AMC Dublin Village 18: [Errno 32] Broken pipe; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Open Caption (On-screen Subtitles); AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Highwoods 20: No seat map for The Drama Laser at AMC

---

## 2026-04-05 18:05 — ET Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie, The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Empire 25 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 9:45pm | 1.4% | -236 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 37.8% | -71 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:45pm | 20.7% | -176 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 75.3% | -11 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 11:00pm | 0% | -311 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 10:15pm | 0.8% | -266 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 8:15pm | 23.1% | -146 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 16.8% | -101 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 1.5% | -206 min |
| AMC Empire 25 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 42.9% | -41 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:45pm | 71.1% | 3 min |
| AMC Empire 25 | The Drama | Laser at AMC | 5:30pm | 72.9% | 18 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 10:00pm | 15.1% | -251 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 65.1% | -71 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 9:00pm | 10.7% | -191 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 52% | -11 min |
| AMC Lincoln Square 13 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 14.5% | -116 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 5:30pm | 86.9% | 18 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:30pm | 38.8% | 18 min |
| AMC 34th Street 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:45pm | 76.1% | 3 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:30pm | 77.2% | 18 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Laser at AMC | 9:45pm | 13.5% | -236 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 9.3% | -191 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 83.9% | -11 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 7:00pm | 61.8% | -71 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:45pm | 0% | -296 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:00pm | 10.5% | -251 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 8:00pm | 67.8% | -131 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 7:30pm | 80.8% | -101 min |
| AMC 84th Street 6 | The Drama | Open Caption (On-screen Subtitles) | 7:15pm | 72.8% | -86 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 95.9% | 18 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 10:30pm | 8.6% | -281 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 9:00pm | 58.2% | -191 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 7:45pm | 72.9% | -116 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 6:15pm | 93.7% | -26 min |
| AMC Magic Johnson Harlem 9 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 39.8% | 3 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 10:00pm | 4% | -251 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 7:15pm | 38.3% | -86 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 7.9% | 18 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 10:30pm | 0.7% | -281 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 10:00pm | 7.7% | -251 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:30pm | 51.8% | -101 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:00pm | 64.8% | -71 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 42.9% | 18 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 5:30pm | 56.3% | 18 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 51.7% | 18 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 10:15pm | 1.4% | -266 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 7:15pm | 62.9% | -86 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 10:30pm | 7.6% | -281 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 7:40pm | 72.2% | -111 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 49.3% | 18 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 9:45pm | 5.4% | -236 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 6:45pm | 41.3% | -56 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 64% | 18 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 5:45pm | 24.7% | 3 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:40pm | 21% | 8 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 10:15pm | 1.8% | -266 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 9:00pm | 6.5% | -191 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 7:30pm | 29.2% | -101 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 6:15pm | 13.7% | -26 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 16% | 3 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 27.9% | 18 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:30pm | 1.8% | -281 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:05pm | 1.2% | -255 min |
| AMC Sunset Place 24 | The Drama | undefined | 9:40pm | 2.4% | -231 min |
| AMC Sunset Place 24 | The Drama | undefined | 8:10pm | 21.4% | -141 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:40pm | 17.9% | -111 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:10pm | 40% | -81 min |
| AMC Sunset Place 24 | The Drama | undefined | 6:45pm | 9.4% | -56 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:45pm | 28.6% | 3 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 10:15pm | 2.2% | -266 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 9:00pm | 11.6% | -191 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 7:30pm | 50% | -101 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 10:00pm | 40.6% | -250 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 8:00pm | 63.2% | -130 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 7:15pm | 66.7% | -85 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 44.4% | 19 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 9:45pm | 5.1% | -235 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 7:00pm | 12.2% | -70 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 6:00pm | 23.7% | -10 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 13.5% | 4 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:40pm | 4.3% | -290 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:25pm | 5.8% | -275 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:10pm | 18.9% | -260 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 9:15pm | 31.8% | -205 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:35pm | 56.5% | -105 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:00pm | 51% | -70 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 6:30pm | 55.6% | -40 min |
| AMC Sundial 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:35pm | 22.3% | 15 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 10:00pm | 6.1% | -250 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 8:45pm | 0% | -175 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 7:15pm | 47% | -85 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 5:30pm | 8.5% | 19 min |
| AMC West Shore 14 | The Drama | undefined | 10:00pm | 0.5% | -250 min |
| AMC West Shore 14 | The Drama | undefined | 7:30pm | 7.6% | -100 min |
| AMC West Shore 14 | The Drama | undefined | 7:15pm | 8% | -85 min |
| AMC Bradenton 20 | The Drama | undefined | 10:00pm | 0% | -250 min |
| AMC Bradenton 20 | The Drama | undefined | 7:15pm | 5.6% | -85 min |
| AMC Bradenton 20 | The Drama | undefined | 6:15pm | 6.5% | -25 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 72.2% | 4 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 87.4% | 19 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 9:00pm | 28.7% | -190 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 6:15pm | 66.4% | -25 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 10:00pm | 60.9% | -250 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 9:30pm | 39.1% | -220 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 7:15pm | 94.2% | -85 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 12.5% | 4 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 16.8% | 19 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 10:10pm | 4.4% | -260 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 9:10pm | 18% | -200 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 7:10pm | 25% | -80 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 6:10pm | 53.9% | -20 min |
| AMC Tysons Corner 16 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 5:40pm | 48.5% | 9 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 10:35pm | 2.7% | -285 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 7:45pm | 21.2% | -115 min |
| AMC Hoffman Center 22 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 6.6% | 4 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:15pm | 0% | -265 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:00pm | 0.7% | -250 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 9:00pm | 1.2% | -190 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 7:30pm | 7.5% | -100 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 6:00pm | 20.8% | -10 min |
| AMC Hoffman Center 22 | The Drama | Open Caption (On-screen Subtitles) | 7:00pm | 2.9% | -70 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:30pm | 25.5% | 21 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 5:45pm | 86.5% | 6 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 8% | -278 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 8:10pm | 4.7% | -139 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 58.3% | -53 min |
| AMC Shirlington 7 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 4.8% | -218 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 10:00pm | 2% | -248 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 7:10pm | 60.8% | -78 min |
| AMC Worldgate 9 | The Drama | undefined | 10:15pm | 0% | -263 min |
| AMC Worldgate 9 | The Drama | undefined | 7:30pm | 5.3% | -98 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 11.2% | 6 min |
| AMC Neshaminy 24 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 2.1% | 21 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 9:15pm | 2% | -203 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 6:30pm | 8.7% | -38 min |
| AMC Cherry Hill 24 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 11.9% | 6 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 9:30pm | 0% | -218 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 8:30pm | 3.8% | -158 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 7:30pm | 14% | -98 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 6:30pm | 17.4% | -38 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 9:10pm | 0% | -199 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 6% | -38 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:45pm | 0% | -233 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 9:25pm | 0% | -214 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 8:40pm | 0% | -169 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:30pm | 0% | -98 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 7:00pm | 0.5% | -68 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -53 min |
| AMC Voorhees 16 | The Super Mario Galaxy Movie | undefined | 6:00pm | 6% | -8 min |
| AMC Voorhees 16 | The Drama | undefined | 9:30pm | 1.2% | -218 min |
| AMC Voorhees 16 | The Drama | undefined | 6:40pm | 5.4% | -48 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:25pm | 88.1% | 26 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 10:00pm | 1.2% | -248 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 8:45pm | 4.4% | -173 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 8:15pm | 26.2% | -143 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 7:15pm | 30.1% | -83 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 10:20pm | 31.6% | -268 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 7:20pm | 90.5% | -88 min |
| AMC Phipps Plaza 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 23.5% | 21 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 10:45pm | 0% | -293 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 9:15pm | 15.1% | -203 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 8:15pm | 16.5% | -143 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 7:45pm | 32.4% | -113 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 7:00pm | 33% | -68 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 6:30pm | 45.2% | -38 min |
| AMC Northlake 14 | The Drama | undefined | 10:00pm | 3.8% | -248 min |
| AMC Northlake 14 | The Drama | undefined | 7:15pm | 43% | -83 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 10.1% | 7 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 69.8% | 22 min |
| AMC Sugarloaf Mills 18 | The Drama | Laser at AMC | 10:15pm | 0% | -263 min |
| AMC Sugarloaf Mills 18 | The Drama | Laser at AMC | 7:15pm | 7.7% | -82 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:30pm | 0% | 22 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 5:30pm | 88.9% | 22 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 17.3% | 22 min |
| AMC Camp Creek 14 | The Drama | undefined | 10:00pm | 0% | -247 min |
| AMC Camp Creek 14 | The Drama | undefined | 7:15pm | 2.9% | -82 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:30pm | 28.2% | 22 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 5:45pm | 44.6% | 7 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 5:40pm | 73.3% | 11 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 10:10pm | 5.5% | -258 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 9:10pm | 5.5% | -198 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 7:15pm | 23.3% | -82 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 6:15pm | 27.4% | -22 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 64.7% | 22 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:50pm | 0% | 2 min |
| AMC Forum 30 | The Super Mario Galaxy Movie | undefined | 5:30pm | 0% | 22 min |
| AMC Forum 30 | The Drama | undefined | 9:45pm | 1.5% | -232 min |
| AMC Forum 30 | The Drama | undefined | 7:00pm | 4.4% | -67 min |
| AMC Forum 30 | The Drama | undefined | 6:00pm | 8% | -7 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | IMAX at AMC | 5:40pm | 8% | 11 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 9:45pm | 0% | -232 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 7:00pm | 0% | -67 min |
| AMC Livonia 20 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 22.7% | 7 min |
| AMC Livonia 20 | The Drama | undefined | 10:30pm | 0% | -278 min |
| AMC Livonia 20 | The Drama | undefined | 7:45pm | 5.5% | -112 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 19.8% | 22 min |
| AMC John R 15 | The Drama | undefined | 10:05pm | 0% | -252 min |
| AMC John R 15 | The Drama | undefined | 8:45pm | 2.2% | -172 min |
| AMC John R 15 | The Drama | undefined | 7:20pm | 26.3% | -87 min |
| AMC Castleton Square 14 | The Drama | undefined | 10:30pm | 1.4% | -278 min |
| AMC Castleton Square 14 | The Drama | undefined | 7:45pm | 28.6% | -112 min |
| AMC Perry Crossing 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 2% | 22 min |
| AMC Perry Crossing 18 | The Drama | undefined | 10:00pm | 0.8% | -247 min |
| AMC Perry Crossing 18 | The Drama | undefined | 7:45pm | 0.9% | -112 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 13.5% | 52 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 5:30pm | 8.5% | 22 min |
| AMC Thoroughbred 20 | The Drama | undefined | 5:00pm | 57.8% | 52 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:00pm | 22.9% | 52 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 3.5% | 22 min |
| AMC Bellevue 12 | The Drama | undefined | 9:15pm | 21.7% | -202 min |
| AMC Bellevue 12 | The Drama | undefined | 6:15pm | 67.4% | -22 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 45.4% | 7 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 5:30pm | 14% | 22 min |
| AMC Easton Town Center 30 | The Drama | undefined | 10:30pm | 0% | -277 min |
| AMC Easton Town Center 30 | The Drama | undefined | 10:15pm | 0% | -262 min |
| AMC Easton Town Center 30 | The Drama | undefined | 10:00pm | 1.9% | -247 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:30pm | 0% | -217 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:00pm | 3.9% | -187 min |
| AMC Easton Town Center 30 | The Drama | undefined | 8:00pm | 4.4% | -127 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:30pm | 12.8% | -97 min |
| AMC Easton Town Center 30 | The Drama | undefined | 7:00pm | 40.7% | -67 min |
| AMC Easton Town Center 30 | The Drama | undefined | 6:00pm | 36.4% | -7 min |
| AMC Dublin Village 18 | The Drama | undefined | 10:15pm | 16.7% | -262 min |
| AMC Dublin Village 18 | The Drama | undefined | 7:15pm | 68.3% | -82 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 5:45pm | 12.2% | 7 min |
| AMC Grove City 14 | The Drama | undefined | 9:40pm | 0.7% | -227 min |
| AMC Grove City 14 | The Drama | undefined | 7:15pm | 6.7% | -82 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 13.7% | 22 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 5:45pm | 10.1% | 7 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 10:15pm | 1.5% | -262 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 9:00pm | 18.5% | -187 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 7:20pm | 11.2% | -86 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 6:10pm | 40.7% | -17 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 47.4% | 22 min |
| AMC West Chester 18 | The Drama | undefined | 10:05pm | 6.6% | -251 min |
| AMC West Chester 18 | The Drama | undefined | 7:00pm | 43.4% | -67 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | PRIME at AMC | 5:45pm | 13% | 7 min |
| AMC Waterfront 22 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 18.5% | 22 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 10:30pm | 7.6% | -277 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 9:55pm | 18.8% | -242 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:45pm | 56.1% | -112 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:15pm | 18.1% | -82 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 7:05pm | 68.8% | -71 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 6:15pm | 19.4% | -22 min |
| AMC Regency 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 48% | 22 min |
| AMC Regency 24 | The Drama | undefined | 5:45pm | 13.1% | 7 min |
| AMC Orange Park 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 24.4% | 22 min |
| AMC Orange Park 24 | The Drama | undefined | 5:30pm | 25% | 22 min |
| AMC Academy 8 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 85.7% | 22 min |
| AMC Academy 8 | The Drama | Laser at AMC | 9:40pm | 2.6% | -227 min |
| AMC Academy 8 | The Drama | Laser at AMC | 7:00pm | 23.1% | -67 min |
| AMC Allegany 8 | The Super Mario Galaxy Movie | undefined | 5:30pm | 26.5% | 22 min |
| AMC Allegany 8 | The Drama | undefined | 10:00pm | 0% | -247 min |
| AMC Allegany 8 | The Drama | undefined | 6:40pm | 0% | -47 min |
| AMC Altoona 12 | The Super Mario Galaxy Movie | undefined | 5:45pm | 6% | 7 min |
| AMC Altoona 12 | The Drama | undefined | 10:00pm | 3.9% | -247 min |
| AMC Altoona 12 | The Drama | undefined | 7:15pm | 3.1% | -82 min |
| AMC Anderson Towne Center 9 | The Drama | undefined | 9:30pm | 1.2% | -217 min |
| AMC Anderson Towne Center 9 | The Drama | undefined | 6:45pm | 7.1% | -52 min |
| AMC Annapolis Mall 11 | The Super Mario Galaxy Movie | undefined | 5:40pm | 36.3% | 12 min |
| AMC Annapolis Mall 11 | The Drama | undefined | 9:30pm | 3.1% | -217 min |
| AMC Annapolis Mall 11 | The Drama | undefined | 8:15pm | 2.2% | -142 min |
| AMC Annapolis Mall 11 | The Drama | undefined | 7:40pm | 32.3% | -107 min |
| AMC Antioch 8 | The Super Mario Galaxy Movie | undefined | 5:30pm | 12.4% | 22 min |
| AMC Antioch 8 | The Drama | undefined | 5:00pm | 6.5% | 52 min |
| AMC Avenue 16 | The Super Mario Galaxy Movie | undefined | 5:30pm | 5.3% | 23 min |
| AMC Avenue 16 | The Drama | undefined | 10:15pm | 0% | -261 min |
| AMC Avenue 16 | The Drama | undefined | 7:35pm | 5.5% | -101 min |
| AMC Avenue Forsyth 12 | The Super Mario Galaxy Movie | IMAX at AMC | 5:35pm | 28.5% | 18 min |
| AMC Avenue Forsyth 12 | The Drama | Laser at AMC | 9:50pm | 1.3% | -236 min |
| AMC Avenue Forsyth 12 | The Drama | Laser at AMC | 7:15pm | 16.7% | -81 min |
| AMC Aviation 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 20.3% | 8 min |
| AMC Aviation 12 | The Drama | Laser at AMC | 10:00pm | 3.2% | -246 min |
| AMC Aviation 12 | The Drama | Laser at AMC | 7:00pm | 25% | -66 min |
| AMC Bay Plaza Cinema 13 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 91.9% | 23 min |
| AMC Bay Plaza Cinema 13 | The Drama | Laser at AMC | 10:40pm | 8.2% | -286 min |
| AMC Bay Plaza Cinema 13 | The Drama | Open Caption (On-screen Subtitles) | 7:45pm | 17.8% | -111 min |
| AMC Bayou 15 | The Super Mario Galaxy Movie | undefined | 5:30pm | 13.4% | 23 min |
| AMC Bayou 15 | The Super Mario Galaxy Movie | undefined | 5:00pm | 22.8% | 53 min |
| AMC Bayou 15 | The Drama | undefined | 9:45pm | 2% | -231 min |
| AMC Bayou 15 | The Drama | undefined | 7:00pm | 3.7% | -66 min |
| AMC Boulevard 10 | The Super Mario Galaxy Movie | BigD at AMC | 5:15pm | 26.5% | 38 min |
| AMC Boulevard 10 | The Drama | undefined | 5:00pm | 8.5% | 53 min |
| AMC Bradley Square 12 | The Super Mario Galaxy Movie | undefined | 5:30pm | 15.6% | 23 min |
| AMC Bradley Square 12 | The Drama | undefined | 10:30pm | 0% | -276 min |
| AMC Bradley Square 12 | The Drama | undefined | 7:45pm | 0.8% | -111 min |
| AMC Brick Plaza 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 44.6% | 23 min |
| AMC Brick Plaza 10 | The Super Mario Galaxy Movie | RealD 3D | 5:40pm | 31.2% | 13 min |
| AMC Brick Plaza 10 | The Drama | Laser at AMC | 9:30pm | 23.2% | -216 min |
| AMC Brick Plaza 10 | The Drama | Laser at AMC | 6:40pm | 44.6% | -46 min |
| AMC Broadstreet 7 | The Super Mario Galaxy Movie | Laser at AMC | 5:40pm | 84.1% | 13 min |
| AMC Broadstreet 7 | The Drama | Laser at AMC | 9:00pm | 7.5% | -186 min |
| AMC Broadstreet 7 | The Drama | Laser at AMC | 7:00pm | 25.5% | -66 min |
| AMC Brunswick Square 13 | The Super Mario Galaxy Movie | undefined | 5:30pm | 22.3% | 23 min |
| AMC Brunswick Square 13 | The Drama | undefined | 9:45pm | 3.5% | -231 min |
| AMC Brunswick Square 13 | The Drama | undefined | 7:00pm | 26.3% | -66 min |
| AMC Camp Hill 12 | The Drama | undefined | 10:00pm | 0.7% | -246 min |
| AMC Camp Hill 12 | The Drama | undefined | 7:15pm | 10.5% | -81 min |
| AMC Chattanooga 18 | The Super Mario Galaxy Movie | undefined | 5:45pm | 9% | 8 min |
| AMC Chattanooga 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 5:30pm | 23.9% | 23 min |
| AMC Chattanooga 18 | The Drama | undefined | 10:15pm | 0.8% | -261 min |
| AMC Chattanooga 18 | The Drama | undefined | 6:55pm | 15.3% | -61 min |
| AMC Cherry Blossom 14 | The Super Mario Galaxy Movie | undefined | 5:50pm | 6.4% | 3 min |
| AMC Cherry Blossom 14 | The Drama | undefined | 9:45pm | 0% | -231 min |
| AMC Cherry Blossom 14 | The Drama | undefined | 7:00pm | 0% | -66 min |
| AMC Clifton Commons 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:30pm | 90.2% | 23 min |
| AMC Clifton Commons 16 | The Drama | Laser at AMC | 11:00pm | 0% | -306 min |
| AMC Clifton Commons 16 | The Drama | Laser at AMC | 10:00pm | 1% | -246 min |
| AMC Clifton Commons 16 | The Drama | Laser at AMC | 8:00pm | 5.4% | -126 min |
| AMC Clifton Commons 16 | The Drama | Laser at AMC | 7:00pm | 5.4% | -66 min |
| AMC Clifton Commons 16 | The Drama | Laser at AMC | 6:00pm | 20.8% | -6 min |
| AMC Colonial 18 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:30pm | 37.5% | 23 min |
| AMC Columbia 14 | The Super Mario Galaxy Movie | undefined | 5:30pm | 31.5% | 25 min |
| AMC Columbia 14 | The Drama | undefined | 9:50pm | 2.5% | -234 min |
| AMC Columbia 14 | The Drama | undefined | 7:00pm | 22.1% | -64 min |
| AMC Columbus 10 | The Super Mario Galaxy Movie | undefined | 5:30pm | 49.2% | 25 min |
| AMC Columbus 10 | The Drama | undefined | 10:00pm | 0% | -244 min |
| AMC Columbus 10 | The Drama | undefined | 7:15pm | 17.6% | -79 min |
| AMC Columbus Park 15 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 3% | 25 min |
| AMC Courthouse Plaza 8 | The Super Mario Galaxy Movie | Laser at AMC | 5:40pm | 37.9% | 15 min |
| AMC Courthouse Plaza 8 | The Drama | Laser at AMC | 9:45pm | 3.9% | -229 min |
| AMC Courthouse Plaza 8 | The Drama | Laser at AMC | 7:00pm | 76.3% | -64 min |
| AMC Crystal Run 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 88.8% | 25 min |
| AMC Crystal Run 16 | The Drama | Laser at AMC | 10:00pm | 8% | -244 min |
| AMC Crystal Run 16 | The Drama | Laser at AMC | 7:15pm | 60% | -79 min |
| AMC DINE-IN Berkshire 8 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:30pm | 66.3% | 25 min |
| AMC DINE-IN Berkshire 8 | The Drama | Dine-In Delivery to Seat | 10:30pm | 3.7% | -274 min |
| AMC DINE-IN Berkshire 8 | The Drama | Dine-In Delivery to Seat | 7:45pm | 9.8% | -109 min |
| AMC DINE-IN Bridgewater 7 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:45pm | 24.4% | 10 min |
| AMC DINE-IN Bridgewater 7 | The Drama | Dine-In Delivery to Seat | 9:30pm | 0% | -214 min |
| AMC DINE-IN Bridgewater 7 | The Drama | Dine-In Delivery to Seat | 6:40pm | 23.4% | -45 min |
| AMC DINE-IN Essex Green 9 | The Drama | Dine-In Delivery to Seat | 5:45pm | 85.2% | 10 min |
| AMC DINE-IN Holly Springs 9 | The Drama | Dine-In Delivery to Seat | 10:30pm | 2.2% | -274 min |
| AMC DINE-IN Holly Springs 9 | The Drama | Dine-In Delivery to Seat | 7:30pm | 44.9% | -94 min |
| AMC DINE-IN Menlo Park 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:30pm | 59% | 25 min |
| AMC DINE-IN Menlo Park 12 | The Drama | Dine-In Delivery to Seat | 10:00pm | 4.1% | -244 min |
| AMC DINE-IN Menlo Park 12 | The Drama | Dine-In Delivery to Seat | 7:15pm | 17.3% | -79 min |
| AMC DINE-IN Midlothian 10 | The Super Mario Galaxy Movie | RealD 3D | 7:20pm | 59% | -84 min |
| AMC DINE-IN Midlothian 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 9:00pm | 6.8% | -184 min |
| AMC DINE-IN Midlothian 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:45pm | 51.1% | -109 min |
| AMC DINE-IN Midlothian 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:15pm | 79.7% | -19 min |
| AMC DINE-IN Midlothian 10 | The Drama | Dine-In Delivery to Seat | 9:00pm | 12.5% | -184 min |
| AMC DINE-IN Midlothian 10 | The Drama | Dine-In Delivery to Seat | 6:00pm | 33.3% | -4 min |
| AMC DINE-IN Painters Crossing 9 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 5:30pm | 52.2% | 25 min |
| AMC DINE-IN Painters Crossing 9 | The Drama | Dine-In Delivery to Seat | 10:20pm | 0% | -264 min |
| AMC DINE-IN Painters Crossing 9 | The Drama | Dine-In Delivery to Seat | 7:00pm | 23.3% | -64 min |
| AMC DINE-IN Shops at Riverside 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 10:00pm | 3.6% | -244 min |
| AMC DINE-IN Shops at Riverside 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 72.7% | -64 min |
| AMC DINE-IN Shops at Riverside 9 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 6% | -184 min |
| AMC DINE-IN Shops at Riverside 9 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 48.7% | -94 min |
| AMC DINE-IN Shops at Riverside 9 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 49% | -4 min |
| AMC DINE-IN Shops at Riverside 9 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:00pm | 42.6% | -124 min |
| AMC DINE-IN Shops at Riverside 9 | The Drama | Dine-In Delivery to Seat | 9:30pm | 47.5% | -214 min |
| AMC DINE-IN Shops at Riverside 9 | The Drama | Dine-In Delivery to Seat | 8:30pm | 75% | -154 min |
| AMC DINE-IN Shops at Riverside 9 | The Drama | Dine-In Delivery to Seat | 6:30pm | 77.5% | -34 min |
| AMC Danbury 16 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 7.2% | 10 min |
| AMC Danbury 16 | The Drama | Laser at AMC | 10:15pm | 0.7% | -259 min |
| AMC Danbury 16 | The Drama | Laser at AMC | 7:30pm | 8% | -94 min |
| AMC Dartmouth Mall 11 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 12% | -169 min |
| AMC Dartmouth Mall 11 | The Super Mario Galaxy Movie | RealD 3D | 6:40pm | 42.6% | -44 min |
| AMC Dartmouth Mall 11 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 74% | -3 min |
| AMC Dartmouth Mall 11 | The Super Mario Galaxy Movie | undefined | 9:15pm | 8.1% | -199 min |
| AMC Dartmouth Mall 11 | The Super Mario Galaxy Movie | undefined | 7:45pm | 48.5% | -108 min |
| AMC Dartmouth Mall 11 | The Super Mario Galaxy Movie | undefined | 7:15pm | 52% | -78 min |
| AMC Dartmouth Mall 11 | The Drama | undefined | 7:00pm | 64% | -63 min |
| AMC Deptford 8 | The Drama | Laser at AMC | 10:00pm | 5.2% | -244 min |
| AMC Deptford 8 | The Drama | Laser at AMC | 7:15pm | 18.1% | -78 min |
| AMC Destin Commons 14 | The Super Mario Galaxy Movie | undefined | 5:00pm | 21% | 56 min |
| AMC Destin Commons 14 | The Drama | undefined | 5:40pm | 13.1% | 15 min |
| AMC East Hanover 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 32.7% | 26 min |
| AMC East Hanover 12 | The Drama | Laser at AMC | 10:00pm | 0% | -244 min |
| AMC East Hanover 12 | The Drama | Laser at AMC | 9:15pm | 5.1% | -199 min |
| AMC East Hanover 12 | The Drama | Laser at AMC | 8:30pm | 1.7% | -154 min |
| AMC East Hanover 12 | The Drama | Laser at AMC | 7:15pm | 21.2% | -78 min |
| AMC East Hanover 12 | The Drama | Laser at AMC | 6:45pm | 42.5% | -48 min |
| AMC Evansville 16 | The Drama | undefined | 9:45pm | 0% | -229 min |
| AMC Fayetteville 14 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:45pm | 9.9% | 11 min |
| AMC Fayetteville 14 | The Drama | undefined | 10:40pm | 0% | -284 min |
| AMC Fayetteville 14 | The Drama | undefined | 7:45pm | 3.1% | -108 min |
| AMC Fiesta Square 12 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 11.9% | 11 min |
| AMC Fiesta Square 12 | The Super Mario Galaxy Movie | undefined | 5:15pm | 32.5% | 41 min |
| AMC Fiesta Square 12 | The Drama | undefined | 10:00pm | 5.4% | -244 min |
| AMC Fiesta Square 12 | The Drama | undefined | 8:30pm | 17.4% | -154 min |
| AMC Fiesta Square 12 | The Drama | undefined | 7:15pm | 40.5% | -78 min |
| AMC Fire Tower 12 | The Drama | undefined | 10:00pm | 3.3% | -244 min |
| AMC Fire Tower 12 | The Drama | undefined | 7:15pm | 21.7% | -78 min |
| AMC Fleming Island 12 | The Super Mario Galaxy Movie | undefined | 5:30pm | 21.7% | 26 min |
| AMC Fleming Island 12 | The Drama | undefined | 10:15pm | 0% | -259 min |
| AMC Fleming Island 12 | The Drama | undefined | 7:30pm | 6.6% | -93 min |
| AMC Foothills 12 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 1.3% | 26 min |
| AMC Foothills 12 | The Drama | undefined | 10:00pm | 0% | -244 min |
| AMC Foothills 12 | The Drama | undefined | 7:05pm | 4.7% | -68 min |
| AMC Freehold 14 | The Drama | Laser at AMC | 9:50pm | 4.8% | -233 min |
| AMC Freehold 14 | The Drama | Laser at AMC | 8:45pm | 11.5% | -169 min |
| AMC Freehold 14 | The Drama | Laser at AMC | 7:00pm | 16.3% | -63 min |
| AMC Garden State Plaza 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:30pm | 63.5% | 26 min |
| AMC Garden State Plaza 16 | The Drama | Laser at AMC | 11:00pm | 0% | -304 min |
| AMC Garden State Plaza 16 | The Drama | Laser at AMC | 9:45pm | 2% | -229 min |
| AMC Garden State Plaza 16 | The Drama | Laser at AMC | 7:00pm | 41% | -63 min |
| AMC Glen Cove 6 | The Drama | Laser at AMC | 10:00pm | 0% | -244 min |
| AMC Glen Cove 6 | The Drama | Laser at AMC | 7:15pm | 9.5% | -78 min |
| AMC Grand Rapids 18 | The Super Mario Galaxy Movie | undefined | 5:30pm | 36% | 26 min |
| AMC Grand Rapids 18 | The Drama | undefined | 9:30pm | 3.9% | -214 min |
| AMC Grand Rapids 18 | The Drama | undefined | 6:45pm | 22.1% | -48 min |
| AMC Hampton Towne Centre 24 | The Super Mario Galaxy Movie | RealD 3D | 5:50pm | 39.5% | 7 min |
| AMC Hampton Towne Centre 24 | The Super Mario Galaxy Movie | undefined | 5:30pm | 29.3% | 26 min |
| AMC Hampton Towne Centre 24 | The Drama | undefined | 10:10pm | 0% | -253 min |
| AMC Hampton Towne Centre 24 | The Drama | undefined | 8:50pm | 20% | -172 min |
| AMC Hampton Towne Centre 24 | The Drama | undefined | 7:20pm | 56.8% | -82 min |
| AMC Hampton Towne Centre 24 | The Drama | undefined | 6:00pm | 53.3% | -3 min |
| AMC Hanes 12 | The Super Mario Galaxy Movie | undefined | 5:30pm | 21.2% | 26 min |
| AMC Hanes 12 | The Drama | undefined | 9:30pm | 13.7% | -213 min |
| AMC Hanes 12 | The Drama | undefined | 6:45pm | 47.1% | -48 min |
| AMC Harbison 14 | The Super Mario Galaxy Movie | undefined | 5:30pm | 29.5% | 26 min |
| AMC Harbison 14 | The Drama | undefined | 10:05pm | 5.4% | -247 min |
| AMC Harbison 14 | The Drama | undefined | 7:35pm | 40.5% | -97 min |
| AMC Harbison 14 | The Drama | undefined | 7:20pm | 40.5% | -82 min |
| AMC Headquarters Plaza 10 | The Drama | Laser at AMC | 10:00pm | 0% | -243 min |
| AMC Headquarters Plaza 10 | The Drama | Laser at AMC | 7:15pm | 23% | -78 min |
| AMC Hialeah 12 | The Super Mario Galaxy Movie | English Spoken with Spanish Subtitles | 5:30pm | 45.1% | 26 min |
| AMC Hialeah 12 | The Drama | undefined | 9:45pm | 0% | -228 min |
| AMC Hialeah 12 | The Drama | English Spoken with Spanish Subtitles | 7:00pm | 2.4% | -63 min |
| AMC Hickory 15 | The Super Mario Galaxy Movie | undefined | 5:30pm | 16.6% | 26 min |
| AMC Hickory 15 | The Drama | undefined | 5:40pm | 30.4% | 16 min |
| AMC High Point 8 | The Super Mario Galaxy Movie | undefined | 5:45pm | 66.2% | 11 min |
| AMC High Point 8 | The Drama | undefined | 9:00pm | 16.2% | -183 min |
| AMC High Point 8 | The Drama | undefined | 6:15pm | 23.5% | -18 min |
| AMC Highland 12 | The Super Mario Galaxy Movie | undefined | 5:15pm | 3.1% | 41 min |
| AMC Highland 12 | The Drama | undefined | 10:30pm | 0% | -273 min |
| AMC Highland 12 | The Drama | undefined | 9:30pm | 0% | -213 min |
| AMC Highland 12 | The Drama | undefined | 7:15pm | 2.2% | -78 min |
| AMC Holland 8 | The Drama | undefined | 9:45pm | 5.5% | -228 min |
| AMC Holland 8 | The Drama | undefined | 7:00pm | 0% | -63 min |
| AMC Huntington Square 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 46.9% | 11 min |
| AMC Huntington Square 12 | The Super Mario Galaxy Movie | Laser at AMC | 5:30pm | 49.2% | 26 min |
| AMC Huntington Square 12 | The Drama | Laser at AMC | 10:00pm | 9.9% | -243 min |
| AMC Huntington Square 12 | The Drama | Laser at AMC | 7:00pm | 46.9% | -63 min |
| AMC Indian Mound 9 | The Super Mario Galaxy Movie | undefined | 5:30pm | 32.2% | 26 min |
| AMC Indian Mound 9 | The Drama | undefined | 9:00pm | 6.2% | -183 min |
| AMC Indian Mound 9 | The Drama | undefined | 6:00pm | 16.9% | -3 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | RealD 3D | 5:50pm | 7.7% | 7 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:30pm | 5.9% | 26 min |
| AMC Jefferson Point 18 | The Super Mario Galaxy Movie | undefined | 5:30pm | 14.5% | 27 min |
| AMC Jefferson Point 18 | The Drama | undefined | 9:50pm | 0.4% | -232 min |
| AMC Jefferson Point 18 | The Drama | undefined | 7:00pm | 0% | -62 min |
| AMC Jersey Gardens 20 | The Drama | Laser at AMC | 10:45pm | 2.8% | -287 min |
| AMC Jersey Gardens 20 | The Drama | Laser at AMC | 7:45pm | 10.1% | -107 min |
| AMC Johnson City 14 | The Drama | undefined | 9:50pm | 0% | -232 min |
| AMC Johnson City 14 | The Drama | undefined | 7:50pm | 33.3% | -112 min |
| AMC Kalli 12 | The Drama | undefined | 10:10pm | 4% | -252 min |
| AMC Kalli 12 | The Drama | undefined | 7:15pm | 10% | -77 min |
| AMC Lake Square 12 | The Super Mario Galaxy Movie | undefined | 5:45pm | 23.2% | 12 min |
| AMC Lake Square 12 | The Drama | undefined | 10:00pm | 5.8% | -242 min |
| AMC Lake Square 12 | The Drama | undefined | 7:15pm | 7.2% | -77 min |
| AMC Lakeshore 8 | The Super Mario Galaxy Movie | undefined | 5:30pm | 39.8% | 27 min |
| AMC Lakeshore 8 | The Drama | undefined | 9:15pm | 4.8% | -197 min |
| AMC Lakeshore 8 | The Drama | undefined | 7:00pm | 2.7% | -62 min |
| AMC Landmark 8 | The Super Mario Galaxy Movie | undefined | 5:30pm | 41.7% | 27 min |
| AMC Loudoun Station 11 | The Super Mario Galaxy Movie | RealD 3D | 8:40pm | 13.2% | -162 min |
| AMC Loudoun Station 11 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 26.5% | -2 min |
| AMC Loudoun Station 11 | The Super Mario Galaxy Movie | undefined | 10:00pm | 0.5% | -242 min |
| AMC Loudoun Station 11 | The Super Mario Galaxy Movie | undefined | 9:20pm | 0% | -202 min |
| AMC Loudoun Station 11 | The Super Mario Galaxy Movie | undefined | 7:20pm | 7.7% | -82 min |
| AMC Loudoun Station 11 | The Super Mario Galaxy Movie | undefined | 6:40pm | 28.3% | -42 min |
| AMC Loudoun Station 11 | The Drama | undefined | 9:45pm | 7.4% | -227 min |
| AMC Loudoun Station 11 | The Drama | undefined | 7:00pm | 5.6% | -62 min |
| AMC Lynnhaven 18 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 2.6% | 12 min |
| AMC Lynnhaven 18 | The Drama | undefined | 5:40pm | 24.7% | 17 min |
| AMC Madison Yards 8 | The Drama | Laser at AMC | 5:50pm | 74.4% | 7 min |
| AMC Majestic 12 | The Super Mario Galaxy Movie | undefined | 5:45pm | 3.8% | 12 min |
| AMC Majestic 12 | The Drama | undefined | 10:15pm | 0% | -257 min |
| AMC Majestic 12 | The Drama | undefined | 9:30pm | 4% | -212 min |
| AMC Majestic 12 | The Drama | undefined | 7:30pm | 1.8% | -92 min |
| AMC Majestic 6 | The Super Mario Galaxy Movie | PRIME at AMC | 10:30pm | 0% | -272 min |
| AMC Majestic 6 | The Super Mario Galaxy Movie | PRIME at AMC | 7:45pm | 18.3% | -107 min |
| AMC Majestic 6 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 6.7% | -167 min |
| AMC Majestic 6 | The Super Mario Galaxy Movie | undefined | 11:00pm | 0% | -302 min |
| AMC Majestic 6 | The Super Mario Galaxy Movie | undefined | 7:00pm | 12.4% | -62 min |
| AMC Majestic 6 | The Super Mario Galaxy Movie | undefined | 6:00pm | 34.4% | -2 min |
| AMC Majestic 6 | The Drama | undefined | 10:50pm | 2% | -292 min |
| AMC Majestic 6 | The Drama | undefined | 7:30pm | 28.9% | -92 min |
| AMC Maple Ridge 8 | The Drama | undefined | 10:30pm | 6.7% | -270 min |
| AMC Maple Ridge 8 | The Drama | undefined | 6:30pm | 17.2% | -30 min |
| AMC Market Fair 15 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 19.4% | 14 min |
| AMC Market Fair 15 | The Super Mario Galaxy Movie | undefined | 5:30pm | 54.5% | 29 min |
| AMC Market Fair 15 | The Drama | undefined | 9:40pm | 13% | -221 min |
| AMC Market Fair 15 | The Drama | undefined | 6:50pm | 58.7% | -50 min |
| AMC MarketFair 10 | The Drama | undefined | 10:30pm | 0% | -270 min |
| AMC MarketFair 10 | The Drama | undefined | 9:30pm | 30% | -210 min |
| AMC MarketFair 10 | The Drama | undefined | 6:45pm | 72% | -45 min |
| AMC Marlton 8 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 54.5% | 14 min |
| AMC Marlton 8 | The Drama | Laser at AMC | 9:30pm | 6.7% | -210 min |
| AMC Marlton 8 | The Drama | Laser at AMC | 7:00pm | 52.9% | -60 min |
| AMC Marple 10 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 66.1% | 14 min |
| AMC Marple 10 | The Drama | Laser at AMC | 10:00pm | 3.4% | -240 min |
| AMC Marple 10 | The Drama | Laser at AMC | 7:15pm | 28.4% | -75 min |
| AMC Marquis 16 | The Super Mario Galaxy Movie | undefined | 5:45pm | 44.3% | 14 min |
| AMC Marquis 16 | The Drama | undefined | 10:30pm | 0% | -270 min |
| AMC Marquis 16 | The Drama | undefined | 9:30pm | 3.1% | -210 min |
| AMC Marquis 16 | The Drama | undefined | 8:15pm | 17.5% | -135 min |
| AMC Marquis 16 | The Drama | undefined | 6:45pm | 53.6% | -45 min |
| AMC Merchants Crossing 16 | The Super Mario Galaxy Movie | undefined | 5:45pm | 59.6% | 14 min |
| AMC Merchants Crossing 16 | The Drama | undefined | 10:05pm | 0% | -245 min |
| AMC Merchants Crossing 16 | The Drama | undefined | 8:50pm | 2.3% | -170 min |
| AMC Merchants Crossing 16 | The Drama | undefined | 7:20pm | 1.6% | -80 min |
| AMC Mobile 16 | The Super Mario Galaxy Movie | RealD 3D | 5:20pm | 5.4% | 39 min |
| AMC Mobile 16 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 9.6% | 59 min |
| AMC Mobile 16 | The Super Mario Galaxy Movie | undefined | 5:45pm | 14.3% | 14 min |
| AMC Mobile 16 | The Drama | undefined | 10:05pm | 1.1% | -245 min |
| AMC Mobile 16 | The Drama | undefined | 7:15pm | 13% | -75 min |
| AMC Monmouth Mall 15 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 15.5% | 29 min |
| AMC Monmouth Mall 15 | The Drama | Laser at AMC | 10:30pm | 1.1% | -270 min |
| AMC Monmouth Mall 15 | The Drama | Laser at AMC | 9:30pm | 3.3% | -210 min |
| AMC Monmouth Mall 15 | The Drama | Laser at AMC | 8:30pm | 5.2% | -150 min |
| AMC Monmouth Mall 15 | The Drama | Laser at AMC | 7:45pm | 21.7% | -105 min |
| AMC Monmouth Mall 15 | The Drama | Laser at AMC | 6:45pm | 9.8% | -45 min |
| AMC Montgomery 16 | The Drama | Laser at AMC | 10:20pm | 0% | -260 min |
| AMC Montgomery 16 | The Drama | Laser at AMC | 9:00pm | 16.7% | -180 min |
| AMC Montgomery 16 | The Drama | Laser at AMC | 7:30pm | 30.3% | -90 min |
| AMC Montgomery 16 | The Drama | Laser at AMC | 6:15pm | 53% | -15 min |
| AMC Morgantown 12 | The Super Mario Galaxy Movie | RealD 3D | 5:30pm | 53.3% | 29 min |
| AMC Morgantown 12 | The Drama | undefined | 10:00pm | 8.1% | -240 min |
| AMC Morgantown 12 | The Drama | undefined | 7:10pm | 22.6% | -71 min |
| AMC Mountainside 10 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 22.7% | 15 min |
| AMC Mountainside 10 | The Drama | Laser at AMC | 10:20pm | 0.7% | -259 min |
| AMC Mountainside 10 | The Drama | Laser at AMC | 7:30pm | 9.3% | -90 min |
| AMC Muncie 12 | The Drama | undefined | 9:45pm | 6.8% | -225 min |
| AMC Muncie 12 | The Drama | undefined | 7:30pm | 4.4% | -90 min |
| AMC Muncie 12 | The Drama | undefined | 7:00pm | 18.6% | -60 min |
| AMC New Brunswick 18 | The Drama | undefined | 10:00pm | 2.8% | -240 min |
| AMC New Brunswick 18 | The Drama | undefined | 7:00pm | 26.1% | -60 min |
| AMC North Dekalb 16 | The Drama | undefined | 11:00pm | 5% | -300 min |
| AMC North Dekalb 16 | The Drama | undefined | 7:00pm | 16.5% | -60 min |
| AMC Northgate 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 11% | 0 min |
| AMC Northgate 14 | The Drama | undefined | 10:00pm | 0% | -240 min |
| AMC Northgate 14 | The Drama | undefined | 7:10pm | 1.5% | -70 min |
| AMC Owings Mills 17 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 21.5% | 15 min |
| AMC Owings Mills 17 | The Drama | undefined | 9:55pm | 8.8% | -235 min |
| AMC Owings Mills 17 | The Drama | undefined | 7:00pm | 64.9% | -60 min |
| AMC Palisades 21 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 61.2% | 0 min |
| AMC Palisades 21 | The Drama | Laser at AMC | 10:00pm | 0% | -240 min |
| AMC Palisades 21 | The Drama | Laser at AMC | 9:00pm | 6.2% | -180 min |
| AMC Palisades 21 | The Drama | Laser at AMC | 7:15pm | 17.7% | -75 min |
| AMC Palisades 21 | The Drama | Laser at AMC | 6:15pm | 32.3% | -15 min |
| AMC Park Place 16 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 5:45pm | 38.9% | 15 min |
| AMC Park Place 16 | The Drama | undefined | 9:20pm | 4.9% | -199 min |
| AMC Park Place 16 | The Drama | undefined | 6:30pm | 73.2% | -30 min |
| AMC Park Terrace 6 | The Drama | undefined | 11:00pm | 8.6% | -300 min |
| AMC Park Terrace 6 | The Drama | undefined | 7:30pm | 85.7% | -90 min |
| AMC Parkway Pointe 15 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 6.9% | 0 min |
| AMC Parkway Pointe 15 | The Drama | Laser at AMC | 10:30pm | 13.1% | -270 min |
| AMC Parkway Pointe 15 | The Drama | Laser at AMC | 7:30pm | 60.7% | -90 min |
| AMC Parkway Pointe 15 | The Drama | Laser at AMC | 7:00pm | 79.5% | -60 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 10:00pm | 40.6% | -240 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 8:00pm | 63.2% | -120 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 7:15pm | 63.8% | -75 min |
| AMC Plainville 20 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 36.8% | 0 min |
| AMC Plainville 20 | The Drama | undefined | 10:45pm | 4.2% | -285 min |
| AMC Plainville 20 | The Drama | undefined | 10:15pm | 0% | -255 min |
| AMC Plainville 20 | The Drama | undefined | 8:00pm | 20.8% | -120 min |
| AMC Plainville 20 | The Drama | undefined | 7:30pm | 32.5% | -90 min |
| AMC Plainville 20 | The Drama | undefined | 7:00pm | 47.9% | -60 min |
| AMC Port Chester 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 34.6% | 0 min |
| AMC Port Chester 14 | The Drama | Laser at AMC | 10:00pm | 0% | -240 min |
| AMC Port Chester 14 | The Drama | Laser at AMC | 7:15pm | 7.9% | -75 min |
| AMC Port St Lucie 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 13% | 0 min |
| AMC Port St Lucie 14 | The Drama | undefined | 9:15pm | 0% | -194 min |
| AMC Port St Lucie 14 | The Drama | undefined | 6:20pm | 6.3% | -18 min |
| AMC Potomac Mills 18 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 11.6% | 0 min |
| AMC Ridge Park Square 8 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 26.6% | 0 min |
| AMC Ridge Park Square 8 | The Drama | undefined | 10:10pm | 1.4% | -249 min |
| AMC Ridge Park Square 8 | The Drama | undefined | 7:15pm | 8.3% | -74 min |
| AMC Ridgefield Park 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 38.6% | 0 min |
| AMC Ridgefield Park 12 | The Drama | undefined | 10:00pm | 6.7% | -239 min |
| AMC Ridgefield Park 12 | The Drama | undefined | 7:15pm | 57.3% | -74 min |
| AMC Ritz 13 | The Drama | undefined | 9:35pm | 8.3% | -214 min |
| AMC Ritz 13 | The Drama | undefined | 7:20pm | 1.6% | -78 min |
| AMC River Hills 10 | The Drama | undefined | 10:00pm | 5.6% | -239 min |
| AMC River Hills 10 | The Drama | undefined | 7:15pm | 47.2% | -74 min |
| AMC Rivertowne 12 | The Super Mario Galaxy Movie | RealD 3D | 5:40pm | 69.2% | 20 min |
| AMC Rivertowne 12 | The Drama | Laser at AMC | 8:00pm | 1.9% | -119 min |
| AMC Riverview 14 | The Super Mario Galaxy Movie | GDX | 6:00pm | 70.5% | 2 min |
| AMC Rockaway 16 | The Super Mario Galaxy Movie | XL at AMC | 6:00pm | 8.5% | 2 min |
| AMC Rockaway 16 | The Super Mario Galaxy Movie | Laser at AMC | 5:45pm | 8.8% | 17 min |
| AMC Rockaway 16 | The Drama | Laser at AMC | 9:45pm | 2.1% | -222 min |
| AMC Rockaway 16 | The Drama | Laser at AMC | 7:00pm | 6% | -57 min |
| AMC Royale 6 | The Super Mario Galaxy Movie | RealD 3D | 9:15pm | 8.1% | -192 min |
| AMC Royale 6 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 41.9% | -27 min |
| AMC Royale 6 | The Super Mario Galaxy Movie | undefined | 10:15pm | 0.9% | -252 min |
| AMC Royale 6 | The Super Mario Galaxy Movie | undefined | 7:30pm | 7.9% | -87 min |
| AMC Royale 6 | The Super Mario Galaxy Movie | undefined | 7:00pm | 3.4% | -57 min |
| AMC Saratoga Springs 11 | The Drama | undefined | 9:45pm | 0% | -222 min |
| AMC Saratoga Springs 11 | The Drama | undefined | 7:00pm | 6.1% | -57 min |
| AMC Schererville 12 | The Super Mario Galaxy Movie | XL at AMC | 5:45pm | 0.4% | 17 min |
| AMC Schererville 12 | The Super Mario Galaxy Movie | XL at AMC | 5:00pm | 11.2% | 62 min |
| AMC Schererville 12 | The Drama | Laser at AMC | 9:15pm | 0% | -192 min |
| AMC Schererville 12 | The Drama | Laser at AMC | 6:30pm | 0.7% | -27 min |
| AMC Schererville 16 | The Super Mario Galaxy Movie | XL at AMC | 5:15pm | 8.8% | 47 min |
| AMC Schererville 16 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 2.9% | 2 min |
| AMC Schererville 16 | The Drama | Laser at AMC | 10:15pm | 0% | -252 min |
| AMC Schererville 16 | The Drama | Laser at AMC | 7:30pm | 0.6% | -87 min |
| AMC Security Square 8 | The Drama | undefined | 10:30pm | 0% | -267 min |
| AMC Security Square 8 | The Drama | undefined | 7:30pm | 3.5% | -87 min |
| AMC SoNo8 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 18.1% | 2 min |
| AMC SoNo8 | The Drama | undefined | 10:00pm | 3.6% | -237 min |
| AMC SoNo8 | The Drama | undefined | 7:15pm | 29.1% | -72 min |
| AMC South Bay Center 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 19.1% | 2 min |
| AMC South Bay Center 12 | The Drama | Laser at AMC | 9:30pm | 6.1% | -207 min |
| AMC South Bay Center 12 | The Drama | Laser at AMC | 7:45pm | 36.8% | -102 min |
| AMC South Bay Center 12 | The Drama | Laser at AMC | 6:45pm | 44.7% | -42 min |
| AMC Southington 12 | The Super Mario Galaxy Movie | undefined | 5:35pm | 36.4% | 27 min |
| AMC Southington 12 | The Drama | undefined | 9:20pm | 2.5% | -197 min |
| AMC Southington 12 | The Drama | undefined | 7:00pm | 33.3% | -57 min |
| AMC Southpoint 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 60.3% | 2 min |
| AMC Southpoint 17 | The Super Mario Galaxy Movie | undefined | 5:35pm | 26.1% | 27 min |
| AMC Spring Hill 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0% | 2 min |
| AMC Spring Hill 12 | The Super Mario Galaxy Movie | RealD 3D | 5:00pm | 0.9% | 62 min |
| AMC Spring Hill 12 | The Super Mario Galaxy Movie | undefined | 5:30pm | 6.6% | 32 min |
| AMC Spring Hill 12 | The Drama | undefined | 5:30pm | 4.1% | 32 min |
| AMC Star Gratiot 15 | The Super Mario Galaxy Movie | undefined | 6:00pm | 14.4% | 2 min |
| AMC Star Gratiot 15 | The Super Mario Galaxy Movie | undefined | 5:40pm | 5.2% | 22 min |
| AMC Star Gratiot 15 | The Drama | undefined | 10:00pm | 0% | -237 min |
| AMC Star Gratiot 15 | The Drama | undefined | 7:15pm | 11.9% | -72 min |
| AMC Staten Island 11 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 69.6% | 2 min |
| AMC Stones River 9 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 5:30pm | 65.3% | 32 min |
| AMC Stones River 9 | The Super Mario Galaxy Movie | undefined | 6:00pm | 64% | 2 min |
| AMC Stones River 9 | The Drama | undefined | 9:45pm | 19.6% | -222 min |
| AMC Stones River 9 | The Drama | undefined | 6:45pm | 50% | -42 min |
| AMC Stonybrook 20 | The Super Mario Galaxy Movie | undefined | 6:00pm | 2.9% | 3 min |
| AMC Stonybrook 20 | The Super Mario Galaxy Movie | undefined | 5:45pm | 5.8% | 18 min |
| AMC Stonybrook 20 | The Drama | undefined | 10:15pm | 8.9% | -251 min |
| AMC Stonybrook 20 | The Drama | undefined | 8:30pm | 5.4% | -146 min |
| AMC Stonybrook 20 | The Drama | undefined | 7:15pm | 8.7% | -71 min |
| AMC Sunrise 8 | The Super Mario Galaxy Movie | undefined | 5:45pm | 74.6% | 18 min |
| AMC Sunrise 8 | The Drama | undefined | 9:15pm | 3.2% | -191 min |
| AMC Sunrise 8 | The Drama | undefined | 8:30pm | 11% | -146 min |
| AMC Tamiami 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 98.1% | 3 min |
| AMC Tamiami 18 | The Drama | Laser at AMC | 10:50pm | 3.4% | -286 min |
| AMC Tamiami 18 | The Drama | Laser at AMC | 10:05pm | 39.1% | -241 min |
| AMC Tamiami 18 | The Drama | Laser at AMC | 7:55pm | 65.2% | -112 min |
| AMC Tamiami 18 | The Drama | Laser at AMC | 7:10pm | 71.7% | -67 min |
| AMC Tiger 13 | The Super Mario Galaxy Movie | undefined | 5:35pm | 0% | 28 min |
| AMC Tiger 13 | The Super Mario Galaxy Movie | undefined | 5:05pm | 10.3% | 58 min |
| AMC Tiger 13 | The Drama | undefined | 9:55pm | 2.1% | -232 min |
| AMC Tiger 13 | The Drama | undefined | 7:10pm | 11.4% | -67 min |
| AMC Tilghman Square 8 | The Super Mario Galaxy Movie | Laser at AMC | 10:00pm | 4.3% | -236 min |
| AMC Tilghman Square 8 | The Super Mario Galaxy Movie | Laser at AMC | 9:30pm | 15.1% | -206 min |
| AMC Tilghman Square 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 21.2% | -101 min |
| AMC Tilghman Square 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 59.4% | -71 min |
| AMC Tilghman Square 8 | The Super Mario Galaxy Movie | RealD 3D | 10:30pm | 1.3% | -266 min |
| AMC Tilghman Square 8 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 34.1% | -41 min |
| AMC Tilghman Square 8 | The Drama | Laser at AMC | 9:20pm | 7.8% | -196 min |
| AMC Tilghman Square 8 | The Drama | Laser at AMC | 6:30pm | 39.2% | -26 min |
| AMC Traders Point 12 | The Super Mario Galaxy Movie | undefined | 6:00pm | 8% | 3 min |
| AMC Traders Point 12 | The Drama | undefined | 10:40pm | 0% | -277 min |
| AMC Traders Point 12 | The Drama | undefined | 9:50pm | 28.6% | -226 min |
| AMC Traders Point 12 | The Drama | undefined | 7:45pm | 35.6% | -101 min |
| AMC Tyngsboro 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 52% | 3 min |
| AMC Tyngsboro 12 | The Drama | Laser at AMC | 9:30pm | 4.5% | -206 min |
| AMC Tyngsboro 12 | The Drama | Laser at AMC | 8:00pm | 14.1% | -116 min |
| AMC Vestal Town Square 9 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 36.5% | 3 min |
| AMC Vestal Town Square 9 | The Drama | undefined | 9:05pm | 9.3% | -181 min |
| AMC Vestal Town Square 9 | The Drama | undefined | 6:20pm | 17.4% | -16 min |
| AMC Washington Square 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 12% | 3 min |
| AMC Washington Square 12 | The Drama | undefined | 10:00pm | 6.8% | -236 min |
| AMC Washington Square 12 | The Drama | undefined | 7:15pm | 15.3% | -71 min |
| AMC Wayne 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 65% | 3 min |
| AMC Wayne 14 | The Drama | Laser at AMC | 11:00pm | 21.3% | -296 min |
| AMC Wayne 14 | The Drama | Laser at AMC | 7:45pm | 75.3% | -101 min |
| AMC Webster 12 | The Super Mario Galaxy Movie | RealD 3D | 9:30pm | 3.3% | -206 min |
| AMC Webster 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -101 min |
| AMC Webster 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 27.2% | -41 min |
| AMC Webster 12 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:15pm | 30.4% | -11 min |
| AMC Webster 12 | The Super Mario Galaxy Movie | undefined | 10:00pm | 0% | -236 min |
| AMC Webster 12 | The Super Mario Galaxy Movie | undefined | 9:00pm | 3.3% | -176 min |
| AMC Webster 12 | The Super Mario Galaxy Movie | undefined | 7:15pm | 66.3% | -71 min |
| AMC Webster 12 | The Drama | undefined | 9:00pm | 15.4% | -176 min |
| AMC Webster 12 | The Drama | undefined | 6:15pm | 24.4% | -11 min |
| AMC West Melbourne 12 | The Super Mario Galaxy Movie | undefined | 5:40pm | 7% | 23 min |
| AMC West Melbourne 12 | The Drama | undefined | 10:15pm | 0% | -251 min |
| AMC West Melbourne 12 | The Drama | undefined | 7:30pm | 0% | -86 min |
| AMC West Oaks 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 59.1% | 3 min |
| AMC West Oaks 14 | The Drama | undefined | 10:25pm | 7.5% | -261 min |
| AMC West Oaks 14 | The Drama | undefined | 7:35pm | 47.8% | -90 min |
| AMC Westmoreland 15 | The Drama | undefined | 10:00pm | 0% | -236 min |
| AMC Westmoreland 15 | The Drama | undefined | 7:10pm | 0% | -66 min |
| AMC Weston 8 | The Super Mario Galaxy Movie | undefined | 5:45pm | 79.3% | 18 min |
| AMC Weston 8 | The Drama | undefined | 10:40pm | 0% | -276 min |
| AMC Weston 8 | The Drama | undefined | 7:45pm | 58.6% | -101 min |
| AMC Westwood Town Center 6 | The Drama | undefined | 10:00pm | 0% | -236 min |
| AMC Westwood Town Center 6 | The Drama | undefined | 7:15pm | 14.6% | -71 min |
| AMC Wheaton Mall 9 | The Super Mario Galaxy Movie | Laser at AMC | 10:30pm | 5.7% | -266 min |
| AMC Wheaton Mall 9 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 10.2% | -101 min |
| AMC Wheaton Mall 9 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 55.6% | -56 min |
| AMC Wheaton Mall 9 | The Super Mario Galaxy Movie | RealD 3D | 9:00pm | 8.1% | -176 min |
| AMC Wheaton Mall 9 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 59.3% | -11 min |
| AMC Wheaton Mall 9 | The Drama | Laser at AMC | 10:15pm | 10.2% | -251 min |
| AMC Wheaton Mall 9 | The Drama | Laser at AMC | 7:15pm | 34.7% | -71 min |
| AMC White Marsh 16 | The Super Mario Galaxy Movie | RealD 3D | 5:45pm | 42.7% | 18 min |
| AMC Woodhaven 10 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 62.7% | 3 min |
| AMC Woodhaven 10 | The Drama | Laser at AMC | 9:30pm | 35.8% | -206 min |
| AMC Woodhaven 10 | The Drama | Laser at AMC | 6:45pm | 52.8% | -41 min |
| AMC Yulee 10 | The Drama | undefined | 7:00pm | 0% | -56 min |

**Issues:** AMC Kips Bay 15: No seat map for The Drama undefined; AMC 34th Street 14: No seat map for The Drama Laser at AMC; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Braintree 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Sunset Place 24: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Pembroke Lakes 9: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Pompano Beach 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Bradenton 20: No seat map for The Super Mario Galaxy Movie undefined; AMC Altamonte Mall 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Hoffman Center 22: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Worldgate 9: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Neshaminy 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Cherry Hill 24: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC DINE-IN Fashion District 8: No seat map for The Super Mario Galaxy Movie PRIME 3D; AMC Phipps Plaza 14: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Northlake 14: No seat map for The Super Mario Galaxy Movie IMAX at AMC; AMC Sugarloaf Mills 18: No seat map for The Super Mario Galaxy Movie XL at AMC; AMC Barrett Commons 24: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Carolina Pavilion 22: No seat map for The Super Mario Galaxy Movie Open Caption (On-screen Subtitles); AMC Concord Mills 24: No seat map for The Drama undefined; AMC Forum 30: No seat map for The Super Mario Galaxy Movie undefined; AMC Star Great Lakes 25: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Livonia 20: No seat map for The Super Mario Galaxy Movie undefined; AMC Castleton Square 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Easton Town Center 30: No seat map for The Super Mario Galaxy Movie undefined; AMC Dublin Village 18: No seat map for The Super Mario Galaxy Movie undefined; AMC Regency 24: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Altoona 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Anderson Towne Center 9: No seat map for The Super Mario Galaxy Movie undefined; AMC Annapolis Mall 11: No seat map for The Super Mario Galaxy Movie undefined; AMC Aviation 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Bay Plaza Cinema 13: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Bradley Square 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Brick Plaza 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Camp Hill 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Chattanooga 18: No seat map for The Super Mario Galaxy Movie undefined; AMC Cherry Blossom 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Colonial 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Colonial 18: No seat map for The Drama Laser at AMC; AMC Columbus Park 15: No seat map for The Drama undefined; AMC Crystal Run 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Bridgewater 7: No seat map for The Super Mario Galaxy Movie Dine-In Delivery to Seat; AMC DINE-IN Essex Green 9: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC DINE-IN Holly Springs 9: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Danbury 16: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Deptford 8: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Evansville 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Evansville 16: No seat map for The Super Mario Galaxy Movie undefined; AMC Evansville 16: No seat map for The Drama undefined; AMC Fire Tower 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Freehold 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Glen Cove 6: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Hampton Towne Centre 24: No seat map for The Super Mario Galaxy Movie undefined; AMC Headquarters Plaza 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC High Point 8: No seat map for The Super Mario Galaxy Movie undefined; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Highwoods 20: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Holland 8: No seat map for The Super Mario Galaxy Movie undefined; AMC Huntington Square 12: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Indianapolis 17: No seat map for The Drama undefined; AMC Jersey Gardens 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Johnson City 14: No seat map for The Super Mario Galaxy Movie undefined; AMC Kalli 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Lake Square 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Lynnhaven 18: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Madison Yards 8: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Majestic 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Maple Ridge 8: No seat map for The Super Mario Galaxy Movie undefined; AMC Market Fair 15: No seat map for The Super Mario Galaxy Movie undefined; AMC MarketFair 10: No seat map for The Super Mario Galaxy Movie undefined; AMC Marple 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Marquis 16: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Merchants Crossing 16: No seat map for The Super Mario Galaxy Movie undefined; AMC Montgomery 16: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Muncie 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC New Brunswick 18: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC North Dekalb 16: No seat map for The Super Mario Galaxy Movie Spanish Language Dubbed with No Subtitles; AMC Northgate 14: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Northgate 14: No seat map for The Super Mario Galaxy Movie undefined; AMC Owings Mills 17: No seat map for The Super Mario Galaxy Movie undefined; AMC Palisades 21: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Park Place 16: No seat map for The Super Mario Galaxy Movie undefined; AMC Park Terrace 6: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Parkway Pointe 15: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Parkway Pointe 15: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Pembroke Lakes 9: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Plainville 20: No seat map for The Super Mario Galaxy Movie undefined; AMC Port St Lucie 14: No seat map for The Super Mario Galaxy Movie undefined; AMC Potomac Mills 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Potomac Mills 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Potomac Mills 18: No seat map for The Drama Laser at AMC; AMC Ridgefield Park 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Ritz 13: No seat map for The Super Mario Galaxy Movie undefined; AMC River Hills 10: No seat map for The Super Mario Galaxy Movie undefined; AMC Rivertowne 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Riverview 14: No seat map for The Super Mario Galaxy Movie undefined; AMC Riverview 14: No seat map for The Drama undefined; AMC Rockaway 16: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Saratoga Springs 11: No seat map for The Super Mario Galaxy Movie XL at AMC; AMC Security Square 8: No seat map for The Super Mario Galaxy Movie undefined; AMC SoNo8: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Southpoint 17: No seat map for The Drama undefined; AMC Star Gratiot 15: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Staten Island 11: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Staten Island 11: No seat map for The Drama Laser at AMC; AMC Stonybrook 20: No seat map for The Super Mario Galaxy Movie Open Caption (On-screen Subtitles); AMC Tallahassee 20: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Tallahassee 20: No seat map for The Drama undefined; AMC Tamiami 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Traders Point 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Tyngsboro 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Vestal Town Square 9: No seat map for The Super Mario Galaxy Movie undefined; AMC Vestal Town Square 9: No seat map for The Super Mario Galaxy Movie undefined; AMC Washington Square 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Washington Square 12: No seat map for The Super Mario Galaxy Movie undefined; AMC Wayne 14: No seat map for The Super Mario Galaxy Movie PRIME at AMC; AMC Westmoreland 15: No seat map for The Super Mario Galaxy Movie undefined; AMC Weston 8: No seat map for The Super Mario Galaxy Movie undefined; AMC Westwood Town Center 6: No seat map for The Super Mario Galaxy Movie undefined; AMC White Marsh 16: No seat map for The Drama undefined; AMC Woodhaven 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Woodhaven 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Yulee 10: No seat map for The Super Mario Galaxy Movie undefined

---

## 2026-04-07 08:25 — ET Group

**Polymarket movies tracked:** The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Empire 25 | The Drama | Laser at AMC | 11:00pm | 0% | -884 min |
| AMC Empire 25 | The Drama | Laser at AMC | 10:15pm | 6.2% | -839 min |
| AMC Empire 25 | The Drama | Laser at AMC | 9:45pm | 0.9% | -809 min |
| AMC Empire 25 | The Drama | Laser at AMC | 9:15pm | 34.5% | -779 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:15pm | 83.3% | -659 min |
| AMC Empire 25 | The Drama | Laser at AMC | 7:00pm | 86.2% | -644 min |
| AMC Empire 25 | The Drama | Laser at AMC | 6:30pm | 83.2% | -614 min |
| AMC Empire 25 | The Drama | Open Caption (On-screen Subtitles) | 7:30pm | 77.3% | -674 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 10:30pm | 5% | -854 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 9:30pm | 55% | -794 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 8:45pm | 83.8% | -749 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 7:30pm | 91% | -674 min |
| AMC Lincoln Square 13 | The Drama | Laser at AMC | 6:30pm | 93.6% | -614 min |
| AMC Kips Bay 15 | The Drama | undefined | 10:15pm | 4.8% | -839 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:45pm | 58.7% | -809 min |
| AMC Kips Bay 15 | The Drama | undefined | 9:15pm | 76.1% | -779 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:50pm | 78.9% | -753 min |
| AMC Kips Bay 15 | The Drama | undefined | 8:30pm | 83.4% | -734 min |
| AMC Kips Bay 15 | The Drama | undefined | 7:30pm | 85.5% | -674 min |
| AMC Kips Bay 15 | The Drama | undefined | 7:05pm | 97.4% | -648 min |
| AMC Kips Bay 15 | The Drama | undefined | 6:30pm | 95.7% | -614 min |
| AMC Kips Bay 15 | The Drama | undefined | 5:45pm | 79.3% | -569 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 10:30pm | 13% | -854 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 9:30pm | 56.7% | -794 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 8:45pm | 67.6% | -749 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 7:45pm | 82.6% | -689 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:45pm | 80.8% | -629 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 6:00pm | 76.5% | -584 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:30pm | 82.5% | -554 min |
| AMC 34th Street 14 | The Drama | Laser at AMC | 5:00pm | 69.6% | -524 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:35pm | 0% | -858 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 10:00pm | 18.4% | -824 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 8:00pm | 79% | -704 min |
| AMC 84th Street 6 | The Drama | Laser at AMC | 7:15pm | 88.6% | -659 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 10:15pm | 11.4% | -839 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 9:30pm | 63.1% | -794 min |
| AMC Newport Centre 11 | The Drama | Laser at AMC | 7:30pm | 100% | -674 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 10:00pm | 1.6% | -824 min |
| AMC Magic Johnson Harlem 9 | The Drama | Laser at AMC | 7:15pm | 27.8% | -659 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 10:00pm | 9.5% | -823 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 9:00pm | 29.6% | -763 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:45pm | 74.6% | -688 min |
| AMC Boston Common 19 | The Drama | Laser at AMC | 7:00pm | 79.1% | -643 min |
| AMC Boston Common 19 | The Drama | Open Caption (On-screen Subtitles) | 6:00pm | 16.5% | -583 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 10:15pm | 7.3% | -838 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 9:45pm | 35.1% | -808 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 8:00pm | 81.1% | -703 min |
| AMC Assembly Row 12 | The Drama | Laser at AMC | 5:00pm | 41.4% | -523 min |
| AMC Framingham 16 | The Drama | Laser at AMC | 9:30pm | 0% | -793 min |
| AMC Framingham 16 | The Drama | Open Caption (On-screen Subtitles) | 6:45pm | 31.4% | -628 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 10:30pm | 8.9% | -853 min |
| AMC Braintree 10 | The Drama | Laser at AMC | 7:40pm | 73.4% | -683 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 9:00pm | 17.4% | -763 min |
| AMC Burlington Cinema 10 | The Drama | Laser at AMC | 6:00pm | 37% | -583 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 9:45pm | 1.2% | -808 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 9:15pm | 8.6% | -778 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 8:30pm | 8% | -733 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 6:30pm | 39.5% | -613 min |
| AMC Methuen 20 | The Drama | Laser at AMC | 5:00pm | 3.7% | -523 min |
| AMC Methuen 20 | The Drama | Open Caption (On-screen Subtitles) | 7:45pm | 0% | -688 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 9:00pm | 1.8% | -763 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 7:30pm | 13.1% | -673 min |
| AMC Aventura 24 | The Drama | Laser at AMC | 6:15pm | 3.6% | -598 min |
| AMC Sunset Place 24 | The Drama | undefined | 10:05pm | 15.3% | -827 min |
| AMC Sunset Place 24 | The Drama | undefined | 8:10pm | 50.6% | -713 min |
| AMC Sunset Place 24 | The Drama | undefined | 7:10pm | 62.4% | -653 min |
| AMC Sunset Place 24 | The Drama | undefined | 5:10pm | 8.2% | -533 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 9:15pm | 26.1% | -778 min |
| AMC DINE-IN Coral Ridge 10 | The Drama | Dine-In Delivery to Seat | 6:30pm | 58.7% | -613 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 10:00pm | 10.3% | -823 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 7:15pm | 50.7% | -658 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 9:45pm | 5.1% | -808 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 7:00pm | 25.5% | -643 min |
| AMC Pompano Beach 18 | The Drama | Laser at AMC | 6:00pm | 31.6% | -583 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:15pm | 0% | -838 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 10:00pm | 5.8% | -823 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 9:15pm | 16.3% | -778 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 8:45pm | 50% | -748 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 7:10pm | 71% | -653 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 6:40pm | 57.8% | -623 min |
| AMC Veterans 24 | The Drama | Laser at AMC | 6:10pm | 65.1% | -593 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 10:00pm | 3% | -823 min |
| AMC Sundial 12 | The Drama | Laser at AMC | 7:15pm | 56.1% | -658 min |
| AMC West Shore 14 | The Drama | undefined | 9:15pm | 2.3% | -778 min |
| AMC West Shore 14 | The Drama | undefined | 6:30pm | 18.1% | -613 min |
| AMC Bradenton 20 | The Drama | undefined | 7:15pm | 8.3% | -658 min |
| AMC Bradenton 20 | The Drama | undefined | 6:15pm | 0% | -598 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 10:30pm | 6% | -853 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 9:00pm | 27.9% | -763 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Laser at AMC | 6:15pm | 63.1% | -598 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 10:00pm | 59.4% | -823 min |
| AMC DINE-IN Disney Springs 24 | The Drama | Dine-In Delivery to Seat | 7:15pm | 88.4% | -658 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 10:10pm | 11% | -833 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 9:10pm | 18% | -773 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 7:10pm | 41.2% | -653 min |
| AMC Altamonte Mall 18 | The Drama | Laser at AMC | 6:10pm | 31.5% | -593 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 10:00pm | 1.8% | -823 min |
| AMC Tysons Corner 16 | The Drama | Laser at AMC | 7:10pm | 34.5% | -653 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 10:00pm | 0% | -823 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 9:00pm | 1.1% | -763 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 8:00pm | 4.6% | -703 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 7:00pm | 39.4% | -643 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 6:00pm | 1.7% | -583 min |
| AMC Hoffman Center 22 | The Drama | Laser at AMC | 5:00pm | 1.7% | -523 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 10:00pm | 15.3% | -823 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 9:15pm | 55.4% | -778 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 8:30pm | 70.3% | -733 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 7:15pm | 84.7% | -658 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 6:15pm | 69.7% | -598 min |
| AMC Georgetown 14 | The Drama | Laser at AMC | 5:45pm | 63.5% | -568 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 10:00pm | 7.8% | -822 min |
| AMC Shirlington 7 | The Drama | Laser at AMC | 7:10pm | 76.5% | -652 min |
| AMC Worldgate 9 | The Drama | undefined | 7:30pm | 20.6% | -672 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 8:45pm | 5.3% | -747 min |
| AMC Neshaminy 24 | The Drama | Laser at AMC | 6:00pm | 8% | -582 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 10:00pm | 1.1% | -822 min |
| AMC Cherry Hill 24 | The Drama | Laser at AMC | 7:15pm | 10.9% | -657 min |
| AMC Voorhees 16 | The Drama | undefined | 9:05pm | 1.8% | -766 min |
| AMC Voorhees 16 | The Drama | undefined | 6:15pm | 3.6% | -597 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 10:00pm | 2.4% | -822 min |
| AMC Plymouth Meeting Mall 12 | The Drama | Laser at AMC | 7:15pm | 67.5% | -657 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 10:20pm | 29.5% | -841 min |
| AMC DINE-IN Fashion District 8 | The Drama | Dine-In Delivery to Seat | 7:20pm | 90.5% | -661 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 10:45pm | 1.1% | -867 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 10:15pm | 0% | -837 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 9:45pm | 0% | -807 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 9:15pm | 10.3% | -777 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 9:00pm | 47.8% | -762 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 7:45pm | 73.3% | -687 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 6:15pm | 58.7% | -597 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 6:00pm | 10.6% | -582 min |
| AMC Phipps Plaza 14 | The Drama | Laser at AMC | 5:00pm | 10.5% | -522 min |
| AMC Northlake 14 | The Drama | undefined | 10:00pm | 0% | -822 min |
| AMC Northlake 14 | The Drama | undefined | 7:15pm | 51.9% | -657 min |
| AMC Sugarloaf Mills 18 | The Drama | Laser at AMC | 10:00pm | 3.2% | -822 min |
| AMC Sugarloaf Mills 18 | The Drama | Laser at AMC | 7:00pm | 18.1% | -642 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 10:15pm | 4.9% | -837 min |
| AMC Barrett Commons 24 | The Drama | Laser at AMC | 7:40pm | 48.9% | -682 min |
| AMC Barrett Commons 24 | The Drama | Open Caption (On-screen Subtitles) | 8:10pm | 23.3% | -712 min |
| AMC Camp Creek 14 | The Drama | undefined | 9:15pm | 0% | -777 min |
| AMC Camp Creek 14 | The Drama | undefined | 6:30pm | 6.8% | -612 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 9:50pm | 3.7% | -811 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 8:15pm | 19.6% | -717 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 7:00pm | 29.6% | -642 min |
| AMC DINE-IN North Point Mall 12 | The Drama | Dine-In Delivery to Seat | 5:30pm | 25% | -552 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 10:00pm | 0% | -822 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 9:00pm | 1.4% | -762 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 8:00pm | 21.7% | -702 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 7:15pm | 58.9% | -657 min |
| AMC Carolina Pavilion 22 | The Drama | undefined | 6:15pm | 37% | -597 min |
| AMC Concord Mills 24 | The Drama | undefined | 10:15pm | 1.5% | -837 min |
| AMC Concord Mills 24 | The Drama | undefined | 9:15pm | 3.8% | -777 min |
| AMC Concord Mills 24 | The Drama | undefined | 8:15pm | 30.1% | -717 min |
| AMC Concord Mills 24 | The Drama | undefined | 7:15pm | 49.3% | -657 min |
| AMC Concord Mills 24 | The Drama | undefined | 6:15pm | 20.8% | -597 min |
| AMC Concord Mills 24 | The Drama | undefined | 5:15pm | 22.4% | -537 min |
| AMC Forum 30 | The Drama | undefined | 9:45pm | 0% | -807 min |
| AMC Forum 30 | The Drama | undefined | 7:00pm | 3.6% | -642 min |
| AMC Forum 30 | The Drama | undefined | 6:00pm | 0% | -582 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 8:05pm | 2.8% | -706 min |
| AMC Star Great Lakes 25 | The Drama | undefined | 5:10pm | 0% | -532 min |
| AMC Livonia 20 | The Drama | undefined | 10:00pm | 4.5% | -822 min |
| AMC Livonia 20 | The Drama | undefined | 7:45pm | 5.1% | -687 min |
| AMC John R 15 | The Drama | undefined | 9:05pm | 7% | -766 min |
| AMC John R 15 | The Drama | undefined | 6:20pm | 35.1% | -601 min |
| AMC Castleton Square 14 | The Drama | Open Caption (On-screen Subtitles) | 7:45pm | 1.4% | -686 min |
| AMC Castleton Square 14 | The Drama | undefined | 10:30pm | 1.4% | -851 min |
| AMC Castleton Square 14 | The Drama | undefined | 5:00pm | 28.6% | -521 min |
| AMC Perry Crossing 18 | The Drama | undefined | 9:45pm | 0% | -806 min |
| AMC Perry Crossing 18 | The Drama | undefined | 7:30pm | 2.2% | -671 min |
| AMC Thoroughbred 20 | The Drama | undefined | 10:30pm | 1% | -851 min |
| AMC Thoroughbred 20 | The Drama | undefined | 9:45pm | 0% | -806 min |
| AMC Thoroughbred 20 | The Drama | undefined | 7:50pm | 45.1% | -691 min |
| AMC Thoroughbred 20 | The Drama | undefined | 6:00pm | 9.8% | -581 min |
| AMC Thoroughbred 20 | The Drama | undefined | 5:00pm | 19.6% | -521 min |
| AMC Bellevue 12 | The Drama | undefined | 9:15pm | 21.7% | -776 min |
| AMC Bellevue 12 | The Drama | undefined | 6:15pm | 60.9% | -596 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:45pm | 0% | -806 min |
| AMC Easton Town Center 30 | The Drama | undefined | 9:15pm | 11.1% | -776 min |
| AMC Easton Town Center 30 | The Drama | undefined | 8:45pm | 6.5% | -746 min |
| AMC Easton Town Center 30 | The Drama | undefined | 8:00pm | 8.9% | -701 min |
| AMC Easton Town Center 30 | The Drama | undefined | 6:30pm | 70.4% | -611 min |
| AMC Dublin Village 18 | The Drama | undefined | 9:45pm | 10% | -806 min |
| AMC Dublin Village 18 | The Drama | undefined | 7:15pm | 66.7% | -656 min |
| AMC Grove City 14 | The Drama | undefined | 9:45pm | 0% | -806 min |
| AMC Grove City 14 | The Drama | undefined | 7:00pm | 3.7% | -641 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 10:20pm | 6.7% | -841 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 7:20pm | 54.5% | -661 min |
| AMC Newport On The Levee 20 | The Drama | undefined | 6:10pm | 37% | -591 min |
| AMC West Chester 18 | The Drama | undefined | 10:20pm | 9.2% | -841 min |
| AMC West Chester 18 | The Drama | undefined | 7:30pm | 40.8% | -671 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 9:25pm | 1.6% | -786 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 8:15pm | 62.1% | -716 min |
| AMC Waterfront 22 | The Drama | Laser at AMC | 5:30pm | 43.9% | -551 min |
| AMC Waterfront 22 | The Drama | Open Caption (On-screen Subtitles) | 6:35pm | 34.4% | -616 min |
| AMC Regency 24 | The Drama | undefined | 10:00pm | 0% | -821 min |
| AMC Regency 24 | The Drama | undefined | 8:30pm | 4.8% | -731 min |
| AMC Regency 24 | The Drama | undefined | 7:15pm | 45.2% | -656 min |
| AMC Regency 24 | The Drama | undefined | 5:45pm | 0% | -566 min |
| AMC Orange Park 24 | The Drama | undefined | 9:45pm | 0% | -806 min |
| AMC Orange Park 24 | The Drama | undefined | 8:15pm | 4.3% | -716 min |
| AMC Orange Park 24 | The Drama | undefined | 7:00pm | 43.1% | -641 min |
| AMC Orange Park 24 | The Drama | undefined | 5:30pm | 0% | -551 min |
| AMC Academy 8 | The Drama | Open Caption (On-screen Subtitles) | 7:00pm | 30.8% | -641 min |
| AMC Allegany 8 | The Drama | undefined | 7:00pm | 14.5% | -641 min |
| AMC Altoona 12 | The Drama | undefined | 7:45pm | 0.8% | -686 min |
| AMC Anderson Towne Center 9 | The Drama | undefined | 9:55pm | 0% | -816 min |
| AMC Anderson Towne Center 9 | The Drama | undefined | 7:30pm | 14.1% | -671 min |
| AMC Annapolis Mall 11 | The Drama | undefined | 10:30pm | 2% | -851 min |
| AMC Annapolis Mall 11 | The Drama | undefined | 7:40pm | 40.4% | -681 min |
| AMC Antioch 8 | The Drama | undefined | 7:30pm | 19.6% | -671 min |
| AMC Avenue 16 | The Drama | undefined | 10:10pm | 0% | -831 min |
| AMC Avenue 16 | The Drama | undefined | 7:30pm | 16.5% | -671 min |
| AMC Avenue Forsyth 12 | The Drama | Laser at AMC | 10:15pm | 0% | -836 min |
| AMC Avenue Forsyth 12 | The Drama | Laser at AMC | 7:15pm | 5.8% | -656 min |
| AMC Aviation 12 | The Drama | Laser at AMC | 10:00pm | 5.6% | -821 min |
| AMC Aviation 12 | The Drama | Laser at AMC | 7:00pm | 16.9% | -641 min |
| AMC Bay Plaza Cinema 13 | The Drama | Laser at AMC | 10:40pm | 2.7% | -861 min |
| AMC Bay Plaza Cinema 13 | The Drama | Laser at AMC | 7:45pm | 53.4% | -686 min |
| AMC Bay Plaza Cinema 13 | The Drama | Laser at AMC | 5:00pm | 15.1% | -521 min |
| AMC Bayou 15 | The Drama | undefined | 9:45pm | 2% | -806 min |
| AMC Bayou 15 | The Drama | undefined | 7:00pm | 5.4% | -641 min |
| AMC Boulevard 10 | The Drama | undefined | 10:30pm | 6.9% | -850 min |
| AMC Boulevard 10 | The Drama | undefined | 7:45pm | 9.2% | -685 min |
| AMC Boulevard 10 | The Drama | undefined | 5:00pm | 10% | -520 min |
| AMC Bradley Square 12 | The Drama | undefined | 9:30pm | 0% | -790 min |
| AMC Bradley Square 12 | The Drama | undefined | 7:15pm | 0% | -655 min |
| AMC Brick Plaza 10 | The Drama | Laser at AMC | 10:10pm | 5.4% | -830 min |
| AMC Brick Plaza 10 | The Drama | Laser at AMC | 7:15pm | 51.8% | -655 min |
| AMC Brick Plaza 10 | The Drama | Laser at AMC | 5:25pm | 3.6% | -545 min |
| AMC Broadstreet 7 | The Drama | Laser at AMC | 9:00pm | 11.3% | -760 min |
| AMC Broadstreet 7 | The Drama | Laser at AMC | 8:00pm | 67.9% | -700 min |
| AMC Broadstreet 7 | The Drama | Laser at AMC | 5:15pm | 26.4% | -535 min |
| AMC Brunswick Square 13 | The Drama | undefined | 9:45pm | 10.5% | -805 min |
| AMC Brunswick Square 13 | The Drama | undefined | 7:00pm | 38.6% | -640 min |
| AMC Camp Hill 12 | The Drama | undefined | 7:30pm | 4.2% | -670 min |
| AMC Chattanooga 18 | The Drama | undefined | 9:45pm | 0% | -805 min |
| AMC Chattanooga 18 | The Drama | undefined | 7:15pm | 6.9% | -655 min |
| AMC Cherry Blossom 14 | The Drama | undefined | 7:00pm | 0.5% | -640 min |
| AMC Clifton Commons 16 | The Drama | Laser at AMC | 10:30pm | 0.4% | -850 min |
| AMC Clifton Commons 16 | The Drama | Laser at AMC | 7:45pm | 24.8% | -685 min |
| AMC Colonial 18 | The Drama | Laser at AMC | 9:30pm | 26.4% | -790 min |
| AMC Colonial 18 | The Drama | Laser at AMC | 7:30pm | 55.6% | -670 min |
| AMC Colonial 18 | The Drama | Laser at AMC | 6:45pm | 39.6% | -625 min |
| AMC Colonial 18 | The Drama | Laser at AMC | 5:15pm | 30.8% | -535 min |
| AMC Columbia 14 | The Drama | undefined | 9:50pm | 0.6% | -809 min |
| AMC Columbia 14 | The Drama | undefined | 7:00pm | 34.4% | -640 min |
| AMC Columbus 10 | The Drama | undefined | 10:00pm | 0% | -820 min |
| AMC Columbus 10 | The Drama | undefined | 7:15pm | 19.6% | -655 min |
| AMC Columbus Park 15 | The Drama | Open Caption (On-screen Subtitles) | 6:30pm | 1.8% | -610 min |
| AMC Columbus Park 15 | The Drama | undefined | 9:15pm | 0% | -775 min |
| AMC Courthouse Plaza 8 | The Drama | Laser at AMC | 9:45pm | 26.3% | -805 min |
| AMC Courthouse Plaza 8 | The Drama | Laser at AMC | 8:45pm | 65.1% | -745 min |
| AMC Courthouse Plaza 8 | The Drama | Laser at AMC | 7:00pm | 88.2% | -640 min |
| AMC Crystal Run 16 | The Drama | Laser at AMC | 10:00pm | 0% | -820 min |
| AMC Crystal Run 16 | The Drama | Laser at AMC | 7:15pm | 74% | -655 min |
| AMC DINE-IN Berkshire 8 | The Drama | Dine-In Delivery to Seat | 9:45pm | 1.2% | -805 min |
| AMC DINE-IN Berkshire 8 | The Drama | Dine-In Delivery to Seat | 7:00pm | 19.5% | -640 min |
| AMC DINE-IN Bridgewater 7 | The Drama | Dine-In Delivery to Seat | 7:55pm | 28.1% | -695 min |
| AMC DINE-IN Bridgewater 7 | The Drama | Dine-In Delivery to Seat | 5:15pm | 9.4% | -535 min |
| AMC DINE-IN Essex Green 9 | The Drama | Dine-In Delivery to Seat | 9:00pm | 50.8% | -760 min |
| AMC DINE-IN Essex Green 9 | The Drama | Dine-In Delivery to Seat | 6:15pm | 54.1% | -595 min |
| AMC DINE-IN Holly Springs 9 | The Drama | Dine-In Delivery to Seat | 10:30pm | 4.5% | -850 min |
| AMC DINE-IN Holly Springs 9 | The Drama | Dine-In Delivery to Seat | 7:30pm | 42.7% | -670 min |
| AMC DINE-IN Menlo Park 12 | The Drama | Dine-In Delivery to Seat | 10:00pm | 4.1% | -820 min |
| AMC DINE-IN Menlo Park 12 | The Drama | Dine-In Delivery to Seat | 7:15pm | 41.8% | -655 min |
| AMC DINE-IN Midlothian 10 | The Drama | Dine-In Delivery to Seat | 8:00pm | 14.6% | -700 min |
| AMC DINE-IN Midlothian 10 | The Drama | Dine-In Delivery to Seat | 5:15pm | 4.2% | -535 min |
| AMC DINE-IN Painters Crossing 9 | The Drama | Dine-In Delivery to Seat | 8:25pm | 20% | -725 min |
| AMC DINE-IN Shops at Riverside 9 | The Drama | Dine-In Delivery to Seat | 9:30pm | 16% | -790 min |
| AMC DINE-IN Shops at Riverside 9 | The Drama | Dine-In Delivery to Seat | 7:15pm | 52.5% | -655 min |
| AMC DINE-IN Shops at Riverside 9 | The Drama | Dine-In Delivery to Seat | 6:30pm | 70% | -610 min |
| AMC Danbury 16 | The Drama | Laser at AMC | 10:30pm | 0% | -850 min |
| AMC Danbury 16 | The Drama | Laser at AMC | 7:30pm | 6.5% | -670 min |
| AMC Dartmouth Mall 11 | The Drama | undefined | 9:45pm | 16% | -804 min |
| AMC Dartmouth Mall 11 | The Drama | undefined | 7:00pm | 58% | -639 min |
| AMC Deptford 8 | The Drama | Laser at AMC | 10:00pm | 4.3% | -819 min |
| AMC Deptford 8 | The Drama | Laser at AMC | 7:15pm | 41.4% | -654 min |
| AMC Destin Commons 14 | The Drama | undefined | 9:00pm | 0% | -759 min |
| AMC Destin Commons 14 | The Drama | undefined | 7:45pm | 1.4% | -684 min |
| AMC Destin Commons 14 | The Drama | undefined | 5:00pm | 1.8% | -519 min |
| AMC East Hanover 12 | The Drama | Laser at AMC | 9:30pm | 17.8% | -789 min |
| AMC East Hanover 12 | The Drama | Laser at AMC | 6:45pm | 11% | -624 min |
| AMC Evansville 16 | The Drama | undefined | 5:00pm | 9.7% | -519 min |
| AMC Fayetteville 14 | The Drama | Open Caption (On-screen Subtitles) | 6:40pm | 1% | -619 min |
| AMC Fayetteville 14 | The Drama | undefined | 9:30pm | 0% | -789 min |
| AMC Fiesta Square 12 | The Drama | undefined | 10:15pm | 3.1% | -834 min |
| AMC Fiesta Square 12 | The Drama | undefined | 7:30pm | 62.5% | -669 min |
| AMC Fire Tower 12 | The Drama | undefined | 10:00pm | 5% | -819 min |
| AMC Fire Tower 12 | The Drama | undefined | 7:15pm | 21.7% | -654 min |
| AMC Fleming Island 12 | The Drama | undefined | 9:45pm | 6.6% | -804 min |
| AMC Fleming Island 12 | The Drama | undefined | 7:30pm | 13.1% | -669 min |
| AMC Foothills 12 | The Drama | undefined | 9:00pm | 0% | -759 min |
| AMC Foothills 12 | The Drama | undefined | 6:10pm | 1.6% | -589 min |
| AMC Freehold 14 | The Drama | Laser at AMC | 10:00pm | 0% | -819 min |
| AMC Freehold 14 | The Drama | Laser at AMC | 7:15pm | 43.7% | -654 min |
| AMC Freehold 14 | The Drama | Laser at AMC | 6:30pm | 9.2% | -609 min |
| AMC Garden State Plaza 16 | The Drama | Laser at AMC | 10:30pm | 0% | -849 min |
| AMC Garden State Plaza 16 | The Drama | Laser at AMC | 9:45pm | 3% | -804 min |
| AMC Garden State Plaza 16 | The Drama | Laser at AMC | 7:00pm | 26.5% | -639 min |
| AMC Glen Cove 6 | The Drama | Laser at AMC | 9:30pm | 9.5% | -789 min |
| AMC Glen Cove 6 | The Drama | Laser at AMC | 6:35pm | 28% | -614 min |
| AMC Grand Rapids 18 | The Drama | undefined | 9:00pm | 0% | -759 min |
| AMC Grand Rapids 18 | The Drama | undefined | 6:15pm | 6.5% | -594 min |
| AMC Hampton Towne Centre 24 | The Drama | undefined | 10:00pm | 8.1% | -819 min |
| AMC Hampton Towne Centre 24 | The Drama | undefined | 8:30pm | 0% | -729 min |
| AMC Hampton Towne Centre 24 | The Drama | undefined | 7:15pm | 24.3% | -654 min |
| AMC Hampton Towne Centre 24 | The Drama | undefined | 5:40pm | 8.9% | -559 min |
| AMC Hanes 12 | The Drama | Open Caption (On-screen Subtitles) | 9:30pm | 0% | -789 min |
| AMC Hanes 12 | The Drama | undefined | 6:45pm | 60.8% | -624 min |
| AMC Harbison 14 | The Drama | undefined | 9:15pm | 48.6% | -774 min |
| AMC Harbison 14 | The Drama | undefined | 6:30pm | 56.8% | -609 min |
| AMC Harbison 14 | The Drama | undefined | 5:00pm | 16.2% | -519 min |
| AMC Headquarters Plaza 10 | The Drama | Laser at AMC | 10:00pm | 0% | -819 min |
| AMC Headquarters Plaza 10 | The Drama | Laser at AMC | 7:15pm | 26.2% | -654 min |
| AMC Hialeah 12 | The Drama | undefined | 9:45pm | 0% | -804 min |
| AMC Hialeah 12 | The Drama | undefined | 7:00pm | 2.4% | -639 min |
| AMC Hickory 15 | The Drama | Open Caption (On-screen Subtitles) | 6:15pm | 18.8% | -594 min |
| AMC Hickory 15 | The Drama | undefined | 7:15pm | 21.6% | -654 min |
| AMC High Point 8 | The Drama | undefined | 6:30pm | 20.6% | -609 min |
| AMC Highland 12 | The Drama | undefined | 8:30pm | 0% | -729 min |
| AMC Highland 12 | The Drama | undefined | 5:45pm | 0% | -564 min |
| AMC Holland 8 | The Drama | undefined | 8:30pm | 5% | -729 min |
| AMC Huntington Square 12 | The Drama | Laser at AMC | 10:00pm | 11.1% | -818 min |
| AMC Huntington Square 12 | The Drama | Laser at AMC | 7:00pm | 65.4% | -638 min |
| AMC Indian Mound 9 | The Drama | undefined | 7:15pm | 10.8% | -653 min |
| AMC Indianapolis 17 | The Drama | undefined | 9:40pm | 1.9% | -798 min |
| AMC Indianapolis 17 | The Drama | undefined | 7:00pm | 45.2% | -638 min |
| AMC Jefferson Point 18 | The Drama | undefined | 9:40pm | 0% | -798 min |
| AMC Jefferson Point 18 | The Drama | undefined | 6:50pm | 1.5% | -627 min |
| AMC Jefferson Point 18 | The Drama | undefined | 5:00pm | 0% | -518 min |
| AMC Jersey Gardens 20 | The Drama | Laser at AMC | 10:45pm | 0.6% | -863 min |
| AMC Jersey Gardens 20 | The Drama | Laser at AMC | 7:45pm | 10.6% | -683 min |
| AMC Johnson City 14 | The Drama | Open Caption (On-screen Subtitles) | 9:35pm | 7% | -792 min |
| AMC Johnson City 14 | The Drama | undefined | 7:45pm | 14% | -683 min |
| AMC Johnson City 14 | The Drama | undefined | 5:00pm | 3.5% | -518 min |
| AMC Kalli 12 | The Drama | undefined | 10:00pm | 4% | -818 min |
| AMC Kalli 12 | The Drama | undefined | 7:10pm | 4% | -648 min |
| AMC Lake Square 12 | The Drama | undefined | 7:15pm | 10.1% | -653 min |
| AMC Lakeshore 8 | The Drama | undefined | 9:30pm | 0% | -788 min |
| AMC Lakeshore 8 | The Drama | undefined | 7:00pm | 5.4% | -638 min |
| AMC Loudoun Station 11 | The Drama | undefined | 9:00pm | 3.8% | -758 min |
| AMC Loudoun Station 11 | The Drama | undefined | 7:45pm | 33.3% | -683 min |
| AMC Loudoun Station 11 | The Drama | undefined | 5:00pm | 20.4% | -518 min |
| AMC Lynnhaven 18 | The Drama | undefined | 10:20pm | 0% | -837 min |
| AMC Lynnhaven 18 | The Drama | undefined | 7:10pm | 2.9% | -648 min |
| AMC Lynnhaven 18 | The Drama | undefined | 6:40pm | 4.9% | -618 min |
| AMC Lynnhaven 18 | The Drama | undefined | 5:20pm | 1.4% | -537 min |
| AMC Madison Yards 8 | The Drama | Laser at AMC | 10:45pm | 3.4% | -863 min |
| AMC Madison Yards 8 | The Drama | Laser at AMC | 9:40pm | 46.7% | -798 min |
| AMC Madison Yards 8 | The Drama | Laser at AMC | 8:15pm | 72.4% | -713 min |
| AMC Madison Yards 8 | The Drama | Laser at AMC | 7:00pm | 84.3% | -638 min |
| AMC Majestic 12 | The Drama | undefined | 8:30pm | 0.9% | -728 min |
| AMC Majestic 12 | The Drama | undefined | 7:30pm | 36% | -668 min |
| AMC Majestic 12 | The Drama | undefined | 5:45pm | 0% | -563 min |
| AMC Majestic 6 | The Drama | undefined | 9:50pm | 0% | -807 min |
| AMC Majestic 6 | The Drama | undefined | 7:00pm | 32.5% | -638 min |
| AMC Maple Ridge 8 | The Drama | undefined | 10:30pm | 7.5% | -848 min |
| AMC Maple Ridge 8 | The Drama | undefined | 6:30pm | 38.5% | -608 min |
| AMC Market Fair 15 | The Drama | undefined | 9:40pm | 17.4% | -798 min |
| AMC Market Fair 15 | The Drama | undefined | 6:50pm | 2.2% | -627 min |
| AMC MarketFair 10 | The Drama | undefined | 10:30pm | 8% | -848 min |
| AMC MarketFair 10 | The Drama | undefined | 7:15pm | 77.5% | -653 min |
| AMC Marlton 8 | The Drama | Laser at AMC | 9:45pm | 5.9% | -803 min |
| AMC Marlton 8 | The Drama | Laser at AMC | 7:00pm | 78.4% | -638 min |
| AMC Marple 10 | The Drama | Laser at AMC | 9:45pm | 2.3% | -802 min |
| AMC Marple 10 | The Drama | Laser at AMC | 7:00pm | 13.6% | -637 min |
| AMC Marquis 16 | The Drama | undefined | 10:00pm | 0% | -817 min |
| AMC Marquis 16 | The Drama | undefined | 9:30pm | 3.1% | -787 min |
| AMC Marquis 16 | The Drama | undefined | 8:45pm | 11.5% | -742 min |
| AMC Marquis 16 | The Drama | undefined | 6:45pm | 41.2% | -622 min |
| AMC Merchants Crossing 16 | The Drama | undefined | 8:45pm | 0% | -742 min |
| AMC Merchants Crossing 16 | The Drama | undefined | 7:20pm | 1.6% | -657 min |
| AMC Mobile 16 | The Drama | undefined | 7:15pm | 3.3% | -652 min |
| AMC Monmouth Mall 15 | The Drama | Laser at AMC | 10:30pm | 0% | -847 min |
| AMC Monmouth Mall 15 | The Drama | Laser at AMC | 8:45pm | 15.4% | -742 min |
| AMC Monmouth Mall 15 | The Drama | Laser at AMC | 7:45pm | 40.2% | -682 min |
| AMC Monmouth Mall 15 | The Drama | Laser at AMC | 5:00pm | 6.5% | -517 min |
| AMC Montgomery 16 | The Drama | Laser at AMC | 10:20pm | 0% | -837 min |
| AMC Montgomery 16 | The Drama | Laser at AMC | 9:30pm | 7.4% | -787 min |
| AMC Montgomery 16 | The Drama | Laser at AMC | 7:40pm | 30.3% | -677 min |
| AMC Montgomery 16 | The Drama | Laser at AMC | 6:45pm | 31.5% | -622 min |
| AMC Montgomery 16 | The Drama | Laser at AMC | 5:15pm | 13.6% | -532 min |
| AMC Morgantown 12 | The Drama | undefined | 9:00pm | 12.9% | -757 min |
| AMC Morgantown 12 | The Drama | undefined | 6:10pm | 4.8% | -587 min |
| AMC Mountainside 10 | The Drama | Laser at AMC | 10:20pm | 0% | -837 min |
| AMC Mountainside 10 | The Drama | Laser at AMC | 7:30pm | 19.3% | -667 min |
| AMC Muncie 12 | The Drama | undefined | 10:00pm | 0% | -817 min |
| AMC Muncie 12 | The Drama | undefined | 9:45pm | 0% | -802 min |
| AMC Muncie 12 | The Drama | undefined | 9:05pm | 0% | -762 min |
| AMC Muncie 12 | The Drama | undefined | 7:00pm | 71.2% | -637 min |
| AMC Muncie 12 | The Drama | undefined | 6:00pm | 6.7% | -577 min |
| AMC New Brunswick 18 | The Drama | undefined | 10:00pm | 1% | -817 min |
| AMC New Brunswick 18 | The Drama | undefined | 7:00pm | 25.6% | -637 min |
| AMC North Dekalb 16 | The Drama | undefined | 10:00pm | 0.8% | -817 min |
| AMC North Dekalb 16 | The Drama | undefined | 7:00pm | 11% | -637 min |
| AMC Northgate 14 | The Drama | undefined | 8:10pm | 0% | -707 min |
| AMC Northgate 14 | The Drama | undefined | 5:20pm | 0.5% | -537 min |
| AMC Owings Mills 17 | The Drama | undefined | 9:45pm | 3.5% | -802 min |
| AMC Owings Mills 17 | The Drama | undefined | 7:00pm | 19.3% | -637 min |
| AMC Palisades 21 | The Drama | Laser at AMC | 10:00pm | 9.7% | -817 min |
| AMC Palisades 21 | The Drama | Laser at AMC | 9:00pm | 15% | -757 min |
| AMC Palisades 21 | The Drama | Laser at AMC | 6:15pm | 35% | -592 min |
| AMC Palisades 21 | The Drama | Open Caption (On-screen Subtitles) | 7:15pm | 19.4% | -652 min |
| AMC Park Place 16 | The Drama | undefined | 7:00pm | 63.4% | -637 min |
| AMC Park Terrace 6 | The Drama | undefined | 10:30pm | 0% | -847 min |
| AMC Park Terrace 6 | The Drama | undefined | 7:30pm | 96.8% | -667 min |
| AMC Parkway Pointe 15 | The Drama | Laser at AMC | 10:20pm | 6% | -837 min |
| AMC Parkway Pointe 15 | The Drama | Laser at AMC | 7:30pm | 72.6% | -667 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 10:00pm | 10.3% | -817 min |
| AMC Pembroke Lakes 9 | The Drama | Laser at AMC | 7:15pm | 50.7% | -652 min |
| AMC Plainville 20 | The Drama | undefined | 10:00pm | 1.4% | -817 min |
| AMC Plainville 20 | The Drama | undefined | 9:00pm | 31% | -757 min |
| AMC Plainville 20 | The Drama | undefined | 7:10pm | 52.1% | -647 min |
| AMC Plainville 20 | The Drama | undefined | 6:15pm | 50.7% | -592 min |
| AMC Port Chester 14 | The Drama | Laser at AMC | 10:00pm | 0% | -817 min |
| AMC Port Chester 14 | The Drama | Laser at AMC | 7:15pm | 6.7% | -652 min |
| AMC Port Chester 14 | The Drama | Laser at AMC | 6:30pm | 6.7% | -607 min |
| AMC Port St Lucie 14 | The Drama | undefined | 7:30pm | 0% | -667 min |
| AMC Potomac Mills 18 | The Drama | Laser at AMC | 10:15pm | 0.7% | -832 min |
| AMC Potomac Mills 18 | The Drama | Laser at AMC | 9:45pm | 2.1% | -802 min |
| AMC Potomac Mills 18 | The Drama | Laser at AMC | 7:30pm | 4.9% | -667 min |
| AMC Potomac Mills 18 | The Drama | Laser at AMC | 7:00pm | 13.8% | -637 min |
| AMC Ridge Park Square 8 | The Drama | undefined | 9:20pm | 5.6% | -777 min |
| AMC Ridge Park Square 8 | The Drama | undefined | 6:30pm | 6.9% | -607 min |
| AMC Ridgefield Park 12 | The Drama | undefined | 10:00pm | 2.2% | -817 min |
| AMC Ridgefield Park 12 | The Drama | undefined | 7:15pm | 58.4% | -652 min |
| AMC Ritz 13 | The Drama | undefined | 9:25pm | 4.2% | -781 min |
| AMC Ritz 13 | The Drama | undefined | 6:40pm | 27.1% | -616 min |
| AMC River Hills 10 | The Drama | undefined | 9:50pm | 4.2% | -805 min |
| AMC River Hills 10 | The Drama | undefined | 7:00pm | 13.9% | -636 min |
| AMC Rivertowne 12 | The Drama | Laser at AMC | 8:45pm | 3.8% | -741 min |
| AMC Rivertowne 12 | The Drama | Laser at AMC | 6:00pm | 3.8% | -576 min |
| AMC Riverview 14 | The Drama | undefined | 10:15pm | 1% | -831 min |
| AMC Riverview 14 | The Drama | undefined | 8:15pm | 27.8% | -711 min |
| AMC Riverview 14 | The Drama | undefined | 7:30pm | 46.9% | -666 min |
| AMC Rockaway 16 | The Drama | Laser at AMC | 9:45pm | 0.4% | -801 min |
| AMC Rockaway 16 | The Drama | Laser at AMC | 8:00pm | 1.5% | -696 min |
| AMC Rockaway 16 | The Drama | Laser at AMC | 7:00pm | 8.1% | -636 min |
| AMC Saratoga Springs 11 | The Drama | undefined | 9:30pm | 0% | -786 min |
| AMC Saratoga Springs 11 | The Drama | undefined | 7:30pm | 2.4% | -666 min |
| AMC Schererville 12 | The Drama | Laser at AMC | 6:30pm | 8.1% | -606 min |
| AMC Schererville 16 | The Drama | Laser at AMC | 10:00pm | 1.1% | -816 min |
| AMC Schererville 16 | The Drama | Laser at AMC | 7:25pm | 0.6% | -661 min |
| AMC Security Square 8 | The Drama | undefined | 10:30pm | 1.8% | -846 min |
| AMC Security Square 8 | The Drama | undefined | 7:30pm | 3.5% | -666 min |
| AMC SoNo8 | The Drama | undefined | 10:15pm | 0% | -831 min |
| AMC SoNo8 | The Drama | undefined | 7:30pm | 61.8% | -666 min |
| AMC South Bay Center 12 | The Drama | Laser at AMC | 9:45pm | 10.5% | -801 min |
| AMC South Bay Center 12 | The Drama | Laser at AMC | 6:45pm | 55.3% | -621 min |
| AMC Southington 12 | The Drama | undefined | 9:15pm | 11.1% | -771 min |
| AMC Southington 12 | The Drama | undefined | 6:30pm | 27.8% | -606 min |
| AMC Southpoint 17 | The Drama | undefined | 10:45pm | 0% | -861 min |
| AMC Southpoint 17 | The Drama | undefined | 10:20pm | 5.8% | -835 min |
| AMC Southpoint 17 | The Drama | undefined | 8:00pm | 81.3% | -696 min |
| AMC Southpoint 17 | The Drama | undefined | 7:00pm | 65.5% | -636 min |
| AMC Southpoint 17 | The Drama | undefined | 6:30pm | 66.7% | -606 min |
| AMC Southpoint 17 | The Drama | undefined | 5:15pm | 45.8% | -531 min |
| AMC Spring Hill 12 | The Drama | undefined | 9:00pm | 0% | -756 min |
| AMC Spring Hill 12 | The Drama | undefined | 8:00pm | 0.7% | -696 min |
| AMC Spring Hill 12 | The Drama | undefined | 5:30pm | 0.8% | -546 min |
| AMC Star Gratiot 15 | The Drama | undefined | 7:15pm | 6.8% | -651 min |
| AMC Staten Island 11 | The Drama | Laser at AMC | 10:15pm | 15.7% | -831 min |
| AMC Staten Island 11 | The Drama | Laser at AMC | 8:15pm | 61.7% | -711 min |
| AMC Staten Island 11 | The Drama | Laser at AMC | 5:30pm | 44.7% | -546 min |
| AMC Stones River 9 | The Drama | undefined | 9:45pm | 6.1% | -801 min |
| AMC Stones River 9 | The Drama | undefined | 6:45pm | 32.9% | -621 min |
| AMC Stonybrook 20 | The Drama | undefined | 10:15pm | 0.9% | -831 min |
| AMC Stonybrook 20 | The Drama | undefined | 8:30pm | 18% | -726 min |
| AMC Stonybrook 20 | The Drama | undefined | 7:15pm | 5.4% | -651 min |
| AMC Sunrise 8 | The Drama | undefined | 8:15pm | 49.2% | -711 min |
| AMC Sunrise 8 | The Drama | English Spoken with Spanish Subtitles | 5:30pm | 6.3% | -546 min |
| AMC Tallahassee 20 | The Drama | undefined | 9:45pm | 67.8% | -801 min |
| AMC Tallahassee 20 | The Drama | undefined | 9:00pm | 17% | -756 min |
| AMC Tallahassee 20 | The Drama | undefined | 8:30pm | 83.1% | -726 min |
| AMC Tallahassee 20 | The Drama | undefined | 7:00pm | 71.2% | -636 min |
| AMC Tamiami 18 | The Drama | Laser at AMC | 10:25pm | 19.6% | -841 min |
| AMC Tamiami 18 | The Drama | Laser at AMC | 10:05pm | 65.2% | -820 min |
| AMC Tamiami 18 | The Drama | Laser at AMC | 7:10pm | 73.9% | -646 min |
| AMC Tamiami 18 | The Drama | Laser at AMC | 7:00pm | 70.6% | -636 min |
| AMC Tiger 13 | The Drama | undefined | 7:10pm | 13.6% | -646 min |
| AMC Tilghman Square 8 | The Drama | Laser at AMC | 9:20pm | 3.9% | -775 min |
| AMC Tilghman Square 8 | The Drama | Laser at AMC | 6:30pm | 58.8% | -606 min |
| AMC Traders Point 12 | The Drama | Open Caption (On-screen Subtitles) | 10:30pm | 0% | -845 min |
| AMC Traders Point 12 | The Drama | undefined | 7:45pm | 22% | -680 min |
| AMC Traders Point 12 | The Drama | undefined | 5:00pm | 3.4% | -515 min |
| AMC Tyngsboro 12 | The Drama | Laser at AMC | 9:00pm | 3.1% | -755 min |
| AMC Tyngsboro 12 | The Drama | Laser at AMC | 7:45pm | 26.9% | -680 min |
| AMC Vestal Town Square 9 | The Drama | undefined | 8:15pm | 7% | -710 min |
| AMC Vestal Town Square 9 | The Drama | undefined | 5:30pm | 7% | -545 min |
| AMC Washington Square 12 | The Drama | undefined | 7:00pm | 3.4% | -635 min |
| AMC Wayne 14 | The Drama | Laser at AMC | 11:00pm | 12.4% | -875 min |
| AMC Wayne 14 | The Drama | Laser at AMC | 7:45pm | 66.3% | -680 min |
| AMC Webster 12 | The Drama | undefined | 10:15pm | 0% | -830 min |
| AMC Webster 12 | The Drama | undefined | 8:15pm | 12% | -710 min |
| AMC Webster 12 | The Drama | undefined | 5:30pm | 5.4% | -545 min |
| AMC West Melbourne 12 | The Drama | undefined | 10:00pm | 0% | -815 min |
| AMC West Melbourne 12 | The Drama | undefined | 7:10pm | 0% | -645 min |
| AMC West Oaks 14 | The Drama | undefined | 9:00pm | 16.7% | -755 min |
| AMC West Oaks 14 | The Drama | undefined | 8:30pm | 34.6% | -725 min |
| AMC West Oaks 14 | The Drama | undefined | 6:15pm | 13.4% | -590 min |
| AMC West Oaks 14 | The Drama | undefined | 5:45pm | 42.3% | -560 min |
| AMC Westmoreland 15 | The Drama | undefined | 7:10pm | 2.7% | -645 min |
| AMC Weston 8 | The Drama | undefined | 9:30pm | 20.7% | -785 min |
| AMC Weston 8 | The Drama | undefined | 7:15pm | 39.7% | -650 min |
| AMC Westwood Town Center 6 | The Drama | undefined | 7:15pm | 34.4% | -650 min |
| AMC Wheaton Mall 9 | The Drama | Laser at AMC | 9:30pm | 8.2% | -785 min |
| AMC Wheaton Mall 9 | The Drama | Laser at AMC | 6:30pm | 18.4% | -605 min |
| AMC White Marsh 16 | The Drama | undefined | 10:30pm | 0.8% | -845 min |
| AMC White Marsh 16 | The Drama | undefined | 9:45pm | 4.8% | -800 min |
| AMC White Marsh 16 | The Drama | undefined | 8:15pm | 11% | -710 min |
| AMC White Marsh 16 | The Drama | undefined | 7:00pm | 15.3% | -635 min |
| AMC White Marsh 16 | The Drama | undefined | 5:30pm | 5.5% | -545 min |
| AMC Woodhaven 10 | The Drama | Laser at AMC | 9:30pm | 9.4% | -785 min |
| AMC Woodhaven 10 | The Drama | Laser at AMC | 6:45pm | 60.4% | -620 min |
| AMC Yulee 10 | The Drama | undefined | 7:15pm | 0% | -650 min |

**Issues:** AMC Evansville 16: No seat map for The Drama Open Caption (On-screen Subtitles); AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Highwoods 20: No seat map for The Drama Laser at AMC; AMC Washington Square 12: No seat map for The Drama undefined

---

## 2026-04-07 08:31 — CT Group

**Polymarket movies tracked:** The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC River East 21 | The Drama | Laser at AMC | 11:00pm | 0% | -934 min |
| AMC River East 21 | The Drama | Laser at AMC | 10:10pm | 1.3% | -884 min |
| AMC River East 21 | The Drama | Laser at AMC | 9:15pm | 2.9% | -829 min |
| AMC River East 21 | The Drama | Laser at AMC | 8:15pm | 68.6% | -769 min |
| AMC River East 21 | The Drama | Laser at AMC | 7:20pm | 73.7% | -713 min |
| AMC River East 21 | The Drama | Laser at AMC | 7:10pm | 71.7% | -704 min |
| AMC River East 21 | The Drama | Laser at AMC | 7:00pm | 19.6% | -694 min |
| AMC River East 21 | The Drama | Laser at AMC | 6:30pm | 61.8% | -664 min |
| AMC River East 21 | The Drama | Laser at AMC | 5:30pm | 62.7% | -604 min |
| AMC NEWCITY 14 | The Drama | Laser at AMC | 9:45pm | 11.9% | -859 min |
| AMC NEWCITY 14 | The Drama | Laser at AMC | 7:00pm | 88.1% | -694 min |
| AMC Village Crossing 18 | The Drama | Laser at AMC | 9:00pm | 4.5% | -814 min |
| AMC Village Crossing 18 | The Drama | Laser at AMC | 6:15pm | 15.4% | -649 min |
| AMC DINE-IN Block 37 | The Drama | Dine-In Delivery to Seat | 10:15pm | 5.4% | -889 min |
| AMC DINE-IN Block 37 | The Drama | Dine-In Delivery to Seat | 8:00pm | 43.2% | -754 min |
| AMC DINE-IN Block 37 | The Drama | Dine-In Delivery to Seat | 7:30pm | 83.8% | -724 min |
| AMC DINE-IN Rosemont 12 | The Drama | Dine-In Delivery to Seat | 10:15pm | 0% | -889 min |
| AMC DINE-IN Rosemont 12 | The Drama | Dine-In Delivery to Seat | 7:30pm | 45.8% | -724 min |
| AMC 600 North Michigan 9 | The Drama | undefined | 7:30pm | 71.9% | -724 min |
| AMC 600 North Michigan 9 | The Drama | undefined | 5:10pm | 55.2% | -584 min |
| AMC Roosevelt Collection 16 | The Drama | Laser at AMC | 9:40pm | 6.1% | -854 min |
| AMC Roosevelt Collection 16 | The Drama | Laser at AMC | 7:15pm | 63.2% | -709 min |
| AMC Roosevelt Collection 16 | The Drama | Laser at AMC | 7:00pm | 58.2% | -694 min |
| AMC Roosevelt Collection 16 | The Drama | Laser at AMC | 6:30pm | 55.6% | -664 min |
| AMC South Barrington 24 | The Drama | Laser at AMC | 10:00pm | 0% | -874 min |
| AMC South Barrington 24 | The Drama | Laser at AMC | 9:10pm | 6.9% | -824 min |
| AMC South Barrington 24 | The Drama | Laser at AMC | 8:10pm | 11.6% | -764 min |
| AMC South Barrington 24 | The Drama | Laser at AMC | 7:10pm | 23.3% | -704 min |
| AMC South Barrington 24 | The Drama | Laser at AMC | 5:10pm | 16.3% | -584 min |
| AMC Streets of Woodfield 20 | The Drama | Laser at AMC | 9:45pm | 0% | -859 min |
| AMC Streets of Woodfield 20 | The Drama | Laser at AMC | 8:00pm | 13.8% | -754 min |
| AMC Streets of Woodfield 20 | The Drama | Laser at AMC | 7:30pm | 19.5% | -724 min |
| AMC Streets of Woodfield 20 | The Drama | Laser at AMC | 5:15pm | 11.7% | -589 min |
| AMC Streets of Woodfield 20 | The Drama | Open Caption (On-screen Subtitles) | 7:00pm | 2.6% | -694 min |
| AMC Yorktown 18 | The Drama | Laser at AMC | 9:45pm | 2.9% | -859 min |
| AMC Yorktown 18 | The Drama | Laser at AMC | 7:00pm | 61.4% | -694 min |
| AMC Northbrook 14 | The Drama | undefined | 7:15pm | 18.2% | -709 min |
| AMC Oakbrook Center 12 | The Drama | Laser at AMC | 10:45pm | 0% | -919 min |
| AMC Oakbrook Center 12 | The Drama | Laser at AMC | 9:30pm | 6.7% | -844 min |
| AMC Oakbrook Center 12 | The Drama | Laser at AMC | 7:45pm | 36.6% | -739 min |
| AMC Randhurst 12 | The Drama | Laser at AMC | 9:25pm | 0.5% | -839 min |
| AMC Randhurst 12 | The Drama | Laser at AMC | 6:45pm | 2.1% | -679 min |
| AMC Niles 12 | The Drama | undefined | 7:15pm | 1.5% | -709 min |
| AMC Ford City 14 | The Drama | Laser at AMC | 10:00pm | 0% | -874 min |
| AMC Ford City 14 | The Drama | Laser at AMC | 9:15pm | 10.7% | -829 min |
| AMC Ford City 14 | The Drama | Laser at AMC | 6:30pm | 16% | -664 min |
| AMC DINE-IN Mesquite 30 | The Drama | Dine-In Delivery to Seat | 10:30pm | 0% | -904 min |
| AMC DINE-IN Mesquite 30 | The Drama | Dine-In Delivery to Seat | 9:25pm | 0% | -839 min |
| AMC DINE-IN Mesquite 30 | The Drama | Dine-In Delivery to Seat | 7:45pm | 20.7% | -739 min |
| AMC DINE-IN Mesquite 30 | The Drama | Dine-In Delivery to Seat | 6:40pm | 28.9% | -674 min |
| AMC DINE-IN Mesquite 30 | The Drama | Dine-In Delivery to Seat | 5:05pm | 0% | -578 min |
| AMC NorthPark 15 | The Drama | Laser at AMC | 10:00pm | 1.9% | -874 min |
| AMC NorthPark 15 | The Drama | Laser at AMC | 7:15pm | 58.5% | -709 min |
| AMC Stonebriar 24 | The Drama | Laser at AMC | 10:50pm | 4.5% | -923 min |
| AMC Stonebriar 24 | The Drama | Laser at AMC | 9:20pm | 9% | -833 min |
| AMC Stonebriar 24 | The Drama | Laser at AMC | 8:00pm | 20.5% | -754 min |
| AMC Stonebriar 24 | The Drama | Laser at AMC | 6:30pm | 24.4% | -664 min |
| AMC Stonebriar 24 | The Drama | Laser at AMC | 5:10pm | 15.9% | -584 min |
| AMC Grapevine Mills 24 | The Drama | Open Caption (On-screen Subtitles) | 6:40pm | 11.4% | -674 min |
| AMC Grapevine Mills 24 | The Drama | undefined | 9:40pm | 0% | -854 min |
| AMC Grapevine Mills 24 | The Drama | undefined | 8:35pm | 18.2% | -788 min |
| AMC Grapevine Mills 24 | The Drama | undefined | 5:45pm | 18.2% | -619 min |
| AMC Firewheel 18 | The Drama | Laser at AMC | 9:45pm | 2.5% | -859 min |
| AMC Firewheel 18 | The Drama | Laser at AMC | 7:00pm | 16.4% | -694 min |
| AMC Irving Mall 14 | The Drama | Laser at AMC | 9:45pm | 0% | -858 min |
| AMC Irving Mall 14 | The Drama | Laser at AMC | 7:00pm | 18.8% | -693 min |
| AMC Irving Mall 14 | The Drama | Laser at AMC | 5:40pm | 18.9% | -613 min |
| AMC The Parks At Arlington 18 | The Drama | Laser at AMC | 10:00pm | 3.4% | -873 min |
| AMC The Parks At Arlington 18 | The Drama | Laser at AMC | 7:15pm | 9.5% | -708 min |
| AMC Southlake 24 | The Drama | Laser at AMC | 10:30pm | 0% | -903 min |
| AMC Southlake 24 | The Drama | Laser at AMC | 9:30pm | 0% | -843 min |
| AMC Southlake 24 | The Drama | Laser at AMC | 8:15pm | 37.1% | -768 min |
| AMC Southlake 24 | The Drama | Laser at AMC | 7:15pm | 27.3% | -708 min |
| AMC Southlake 24 | The Drama | Laser at AMC | 6:15pm | 19.4% | -648 min |
| AMC Southlake 24 | The Drama | Laser at AMC | 5:15pm | 34.3% | -588 min |
| AMC Gulf Pointe 30 | The Drama | Laser at AMC | 10:45pm | 0.6% | -918 min |
| AMC Gulf Pointe 30 | The Drama | Laser at AMC | 9:45pm | 1.1% | -858 min |
| AMC Gulf Pointe 30 | The Drama | Laser at AMC | 8:45pm | 1.1% | -798 min |
| AMC Gulf Pointe 30 | The Drama | Laser at AMC | 7:45pm | 3.4% | -738 min |
| AMC Gulf Pointe 30 | The Drama | Laser at AMC | 6:45pm | 5.1% | -678 min |
| AMC Gulf Pointe 30 | The Drama | Laser at AMC | 5:45pm | 10.3% | -618 min |
| AMC Willowbrook 24 | The Drama | Laser at AMC | 10:25pm | 1.9% | -898 min |
| AMC Willowbrook 24 | The Drama | Laser at AMC | 9:55pm | 0% | -868 min |
| AMC Willowbrook 24 | The Drama | Laser at AMC | 8:25pm | 16.3% | -778 min |
| AMC Willowbrook 24 | The Drama | Laser at AMC | 6:20pm | 10.6% | -653 min |
| AMC First Colony 24 | The Drama | Laser at AMC | 10:00pm | 0% | -873 min |
| AMC First Colony 24 | The Drama | Laser at AMC | 9:05pm | 13% | -818 min |
| AMC First Colony 24 | The Drama | Laser at AMC | 7:20pm | 28.6% | -713 min |
| AMC First Colony 24 | The Drama | Open Caption (On-screen Subtitles) | 6:15pm | 21.7% | -648 min |
| AMC Deerbrook 24 | The Drama | undefined | 9:05pm | 0% | -818 min |
| AMC Deerbrook 24 | The Drama | undefined | 8:00pm | 0% | -753 min |
| AMC Deerbrook 24 | The Drama | undefined | 7:10pm | 0.8% | -703 min |
| AMC Deerbrook 24 | The Drama | undefined | 6:15pm | 3.2% | -648 min |
| AMC Katy Mills 20 | The Drama | Laser at AMC | 10:00pm | 0% | -873 min |
| AMC Katy Mills 20 | The Drama | Laser at AMC | 9:00pm | 6% | -813 min |
| AMC Katy Mills 20 | The Drama | Laser at AMC | 7:00pm | 4.5% | -693 min |
| AMC Katy Mills 20 | The Drama | Laser at AMC | 6:10pm | 9% | -643 min |
| AMC Fountains 18 | The Drama | Laser at AMC | 10:35pm | 0% | -908 min |
| AMC Fountains 18 | The Drama | Laser at AMC | 9:30pm | 6.8% | -843 min |
| AMC Fountains 18 | The Drama | Laser at AMC | 7:45pm | 47.4% | -738 min |
| AMC Fountains 18 | The Drama | Laser at AMC | 6:45pm | 21.1% | -678 min |
| AMC Fountains 18 | The Drama | Laser at AMC | 5:00pm | 15.8% | -573 min |
| AMC Houston 8 | The Drama | Laser at AMC | 9:00pm | 15.1% | -813 min |
| AMC Houston 8 | The Drama | Laser at AMC | 6:15pm | 27.4% | -648 min |
| AMC Eden Prairie Mall 18 | The Drama | undefined | 9:30pm | 6.9% | -843 min |
| AMC Eden Prairie Mall 18 | The Drama | undefined | 7:00pm | 56.3% | -693 min |
| AMC Rosedale 14 | The Drama | undefined | 9:15pm | 9.8% | -828 min |
| AMC Rosedale 14 | The Drama | undefined | 7:45pm | 42.5% | -738 min |
| AMC Rosedale 14 | The Drama | undefined | 6:30pm | 53.8% | -663 min |
| AMC Rosedale 14 | The Drama | undefined | 5:00pm | 6.3% | -573 min |
| AMC Southdale 16 | The Drama | undefined | 10:00pm | 2.5% | -873 min |
| AMC Southdale 16 | The Drama | undefined | 7:15pm | 82.8% | -708 min |
| AMC Coon Rapids 16 | The Drama | undefined | 8:15pm | 9.3% | -768 min |
| AMC Coon Rapids 16 | The Drama | undefined | 5:30pm | 32% | -603 min |
| AMC Inver Grove 16 | The Drama | undefined | 9:15pm | 0% | -828 min |
| AMC Inver Grove 16 | The Drama | undefined | 7:45pm | 0% | -738 min |
| AMC Inver Grove 16 | The Drama | undefined | 6:30pm | 47.2% | -663 min |
| AMC Inver Grove 16 | The Drama | undefined | 5:00pm | 0% | -573 min |
| AMC Metropark Square 10 | The Drama | Laser at AMC | 10:15pm | 0% | -888 min |
| AMC Metropark Square 10 | The Drama | Laser at AMC | 7:30pm | 26.2% | -723 min |
| AMC Spring 10 | The Drama | Laser at AMC | 10:15pm | 0% | -888 min |
| AMC Spring 10 | The Drama | Laser at AMC | 7:30pm | 13.5% | -723 min |
| AMC Spring 10 | The Drama | Laser at AMC | 5:15pm | 12.4% | -588 min |
| AMC Eastchase 9 | The Drama | Laser at AMC | 7:00pm | 0% | -692 min |
| AMC CLASSIC Brazos Mall 14 | The Drama | undefined | 7:30pm | 1.8% | -722 min |
| AMC Rio Cinemas 18 | The Drama | Laser at AMC | 10:30pm | 0% | -902 min |
| AMC Rio Cinemas 18 | The Drama | Laser at AMC | 9:45pm | 4.1% | -857 min |
| AMC Rio Cinemas 18 | The Drama | Laser at AMC | 8:30pm | 18.2% | -782 min |
| AMC Rio Cinemas 18 | The Drama | Laser at AMC | 7:00pm | 46.9% | -692 min |
| AMC Rio Cinemas 18 | The Drama | Laser at AMC | 5:30pm | 12.5% | -602 min |
| AMC Centerpoint 11 | The Drama | Laser at AMC | 9:30pm | 54.2% | -842 min |
| AMC Centerpoint 11 | The Drama | Laser at AMC | 6:45pm | 83.3% | -677 min |
| AMC Village On The Parkway 9 | The Drama | Laser at AMC | 10:20pm | 12.5% | -891 min |
| AMC Village On The Parkway 9 | The Drama | Laser at AMC | 7:30pm | 54.2% | -722 min |
| AMC Birchwood 10 | The Drama | undefined | 7:50pm | 0% | -741 min |
| AMC Birchwood 10 | The Drama | undefined | 5:05pm | 0% | -576 min |
| AMC Causeway 13 | The Drama | Laser at AMC | 10:00pm | 0% | -872 min |
| AMC Causeway 13 | The Drama | Laser at AMC | 9:40pm | 2% | -852 min |
| AMC Causeway 13 | The Drama | Laser at AMC | 8:40pm | 9.1% | -792 min |
| AMC Causeway 13 | The Drama | Laser at AMC | 7:20pm | 53% | -711 min |
| AMC Causeway 13 | The Drama | Laser at AMC | 7:00pm | 42% | -692 min |
| AMC Causeway 13 | The Drama | Laser at AMC | 6:00pm | 40.9% | -632 min |
| AMC Barrywoods 24 | The Drama | Laser at AMC | 10:00pm | 0% | -872 min |
| AMC Barrywoods 24 | The Drama | Laser at AMC | 9:00pm | 1.5% | -812 min |
| AMC Barrywoods 24 | The Drama | Laser at AMC | 8:00pm | 0% | -752 min |
| AMC Barrywoods 24 | The Drama | Laser at AMC | 7:15pm | 6.5% | -707 min |
| AMC Barrywoods 24 | The Drama | Laser at AMC | 6:00pm | 5.3% | -632 min |
| AMC Barrywoods 24 | The Drama | Laser at AMC | 5:15pm | 1.7% | -587 min |
| AMC Independence Commons 20 | The Drama | Laser at AMC | 10:00pm | 4.2% | -872 min |
| AMC Independence Commons 20 | The Drama | Laser at AMC | 9:00pm | 0% | -812 min |
| AMC Independence Commons 20 | The Drama | Laser at AMC | 7:05pm | 25% | -696 min |
| AMC Independence Commons 20 | The Drama | Laser at AMC | 6:10pm | 12.5% | -642 min |
| AMC Ward Parkway 14 | The Drama | Laser at AMC | 9:15pm | 3.6% | -827 min |
| AMC Ward Parkway 14 | The Drama | Laser at AMC | 7:20pm | 38.5% | -711 min |
| AMC Ward Parkway 14 | The Drama | Laser at AMC | 6:30pm | 50.9% | -662 min |
| AMC Town Center 20 | The Drama | Laser at AMC | 10:00pm | 6.8% | -872 min |
| AMC Town Center 20 | The Drama | Laser at AMC | 8:15pm | 24.3% | -767 min |
| AMC Town Center 20 | The Drama | Laser at AMC | 7:15pm | 55.9% | -707 min |
| AMC Legends 14 | The Drama | Laser at AMC | 10:30pm | 0% | -902 min |
| AMC Legends 14 | The Drama | Laser at AMC | 9:45pm | 3.6% | -857 min |
| AMC Legends 14 | The Drama | Laser at AMC | 7:45pm | 7.6% | -737 min |
| AMC Legends 14 | The Drama | Laser at AMC | 7:00pm | 8% | -692 min |
| AMC Barton Creek Square 14 | The Drama | undefined | 10:00pm | 31.1% | -872 min |
| AMC Barton Creek Square 14 | The Drama | undefined | 8:45pm | 82% | -797 min |
| AMC Barton Creek Square 14 | The Drama | undefined | 7:15pm | 82% | -707 min |
| AMC Barton Creek Square 14 | The Drama | undefined | 6:00pm | 73.8% | -632 min |
| AMC Barton Creek Square 14 | The Drama | undefined | 5:15pm | 25.7% | -587 min |
| AMC Baton Rouge 16 | The Drama | undefined | 9:45pm | 0% | -856 min |
| AMC Baton Rouge 16 | The Drama | undefined | 7:00pm | 23.6% | -691 min |
| AMC Boerne 11 | The Drama | undefined | 7:40pm | 2.2% | -731 min |
| AMC Burleson 14 | The Drama | Laser at AMC | 9:30pm | 3.6% | -841 min |
| AMC Burleson 14 | The Drama | Laser at AMC | 6:45pm | 14.3% | -676 min |
| AMC Champaign 13 | The Drama | Open Caption (On-screen Subtitles) | 7:30pm | 8.4% | -721 min |
| AMC Chantilly 13 | The Drama | undefined | 7:15pm | 1.4% | -706 min |
| AMC Chenal 9 | The Drama | undefined | 9:30pm | 0% | -841 min |
| AMC Chenal 9 | The Drama | undefined | 6:40pm | 22.2% | -671 min |
| AMC Council Bluffs 17 | The Drama | undefined | 10:00pm | 1.8% | -871 min |
| AMC Council Bluffs 17 | The Drama | undefined | 7:15pm | 19.5% | -706 min |
| AMC Creve Coeur 12 | The Drama | undefined | 10:00pm | 0% | -871 min |
| AMC Creve Coeur 12 | The Drama | undefined | 7:15pm | 35% | -706 min |
| AMC Creve Coeur 12 | The Drama | undefined | 6:15pm | 33.7% | -646 min |
| AMC DINE-IN Clearfork 8 | The Drama | Dine-In Delivery to Seat | 9:50pm | 13.9% | -860 min |
| AMC DINE-IN Clearfork 8 | The Drama | Dine-In Delivery to Seat | 7:00pm | 61.1% | -691 min |
| AMC DINE-IN Clearview Palace 12 | The Drama | Dine-In Delivery to Seat | 9:00pm | 6.2% | -811 min |
| AMC DINE-IN Clearview Palace 12 | The Drama | Dine-In Delivery to Seat | 6:00pm | 25.8% | -631 min |
| AMC DINE-IN Manhattan 13 | The Drama | Dine-In Delivery to Seat | 7:00pm | 23.8% | -691 min |
| AMC DINE-IN Tech Ridge 10 | The Drama | Dine-In Delivery to Seat | 10:00pm | 6.5% | -871 min |
| AMC DINE-IN Tech Ridge 10 | The Drama | Dine-In Delivery to Seat | 7:15pm | 69.2% | -706 min |
| AMC DINE-IN Vestavia Hills 10 | The Drama | Dine-In Delivery to Seat | 10:30pm | 0% | -901 min |
| AMC DINE-IN Vestavia Hills 10 | The Drama | Dine-In Delivery to Seat | 7:45pm | 33.9% | -736 min |
| AMC DINE-IN Vestavia Hills 10 | The Drama | Dine-In Delivery to Seat | 5:00pm | 16.9% | -571 min |
| AMC Dakota Square 9 | The Drama | undefined | 8:15pm | 4.5% | -766 min |
| AMC Dakota Square 9 | The Drama | undefined | 5:30pm | 9.1% | -601 min |
| AMC Decatur 12 | The Drama | undefined | 7:40pm | 0% | -731 min |
| AMC Edinburg 18 | The Drama | undefined | 9:50pm | 12% | -860 min |
| AMC Edinburg 18 | The Drama | undefined | 7:10pm | 58.3% | -701 min |
| AMC Edwardsville 12 | The Drama | undefined | 9:00pm | 0% | -811 min |
| AMC Edwardsville 12 | The Drama | undefined | 6:00pm | 4.5% | -631 min |
| AMC El Paso 16 | The Drama | undefined | 10:00pm | 0% | -871 min |
| AMC El Paso 16 | The Drama | undefined | 7:15pm | 35.4% | -706 min |
| AMC Elmwood Palace 20 | The Drama | undefined | 10:00pm | 0% | -871 min |
| AMC Elmwood Palace 20 | The Drama | undefined | 9:00pm | 0% | -811 min |
| AMC Elmwood Palace 20 | The Drama | undefined | 7:05pm | 6.2% | -695 min |
| AMC Elmwood Palace 20 | The Drama | undefined | 6:10pm | 3.4% | -641 min |
| AMC Esquire 7 | The Drama | undefined | 10:00pm | 12.7% | -871 min |
| AMC Esquire 7 | The Drama | undefined | 7:15pm | 76.4% | -706 min |
| AMC Evanston 12 | The Drama | Laser at AMC | 9:30pm | 10.5% | -841 min |
| AMC Evanston 12 | The Drama | Laser at AMC | 6:45pm | 16.9% | -676 min |
| AMC Festival Plaza 16 | The Drama | undefined | 9:00pm | 12.8% | -811 min |
| AMC Festival Plaza 16 | The Drama | undefined | 6:15pm | 12.8% | -646 min |
| AMC Fitchburg 18 | The Drama | undefined | 8:20pm | 36.2% | -770 min |
| AMC Fitchburg 18 | The Drama | undefined | 7:15pm | 67.6% | -706 min |
| AMC Fitchburg 18 | The Drama | undefined | 5:15pm | 41.9% | -586 min |
| AMC Galaxy 16 | The Drama | undefined | 7:20pm | 1.4% | -710 min |
| AMC Grand Prairie 18 | The Drama | undefined | 7:45pm | 0.4% | -736 min |
| AMC Grand Prairie 18 | The Drama | undefined | 5:00pm | 2.2% | -571 min |
| AMC Hammond Palace 10 | The Drama | undefined | 9:00pm | 0% | -810 min |
| AMC Hammond Palace 10 | The Drama | undefined | 7:30pm | 0% | -720 min |
| AMC Hawthorn 12 | The Drama | Laser at AMC | 9:30pm | 20% | -840 min |
| AMC Hawthorn 12 | The Drama | Laser at AMC | 6:45pm | 36.4% | -675 min |
| AMC Highland Village 12 | The Drama | Laser at AMC | 5:10pm | 7.4% | -580 min |
| AMC Houma Palace 10 | The Drama | undefined | 6:45pm | 0.9% | -675 min |
| AMC Lakeline 9 | The Drama | undefined | 9:05pm | 7% | -814 min |
| AMC Lakeline 9 | The Drama | undefined | 6:15pm | 18.6% | -645 min |
| AMC Longview 10 | The Drama | undefined | 10:00pm | 0% | -870 min |
| AMC Longview 10 | The Drama | undefined | 7:15pm | 4% | -705 min |
| AMC Lufkin 9 | The Drama | undefined | 7:45pm | 9.8% | -735 min |
| AMC Machesney Park 14 | The Drama | undefined | 7:15pm | 2.7% | -705 min |
| AMC Mall of Louisiana 15 | The Drama | undefined | 9:50pm | 2.2% | -859 min |
| AMC Mall of Louisiana 15 | The Drama | undefined | 7:05pm | 11.9% | -694 min |
| AMC Mayfair Mall 18 | The Drama | undefined | 7:15pm | 9.4% | -705 min |
| AMC Northrock 14 | The Drama | undefined | 9:30pm | 9.6% | -840 min |
| AMC Northrock 14 | The Drama | undefined | 6:45pm | 63.5% | -675 min |
| AMC Palace 9 | The Drama | Laser at AMC | 10:00pm | 0% | -870 min |
| AMC Palace 9 | The Drama | Laser at AMC | 7:15pm | 45.5% | -705 min |
| AMC Patriot 13 | The Drama | Open Caption (On-screen Subtitles) | 7:15pm | 0% | -705 min |
| AMC Patton Creek 15 | The Drama | undefined | 9:45pm | 0% | -855 min |
| AMC Patton Creek 15 | The Drama | undefined | 7:00pm | 2.6% | -690 min |
| AMC Penn Square 10 | The Drama | undefined | 10:15pm | 0% | -885 min |
| AMC Penn Square 10 | The Drama | undefined | 7:15pm | 7.1% | -705 min |
| AMC Penn Square 10 | The Drama | undefined | 5:15pm | 0% | -585 min |
| AMC Quail Springs Mall 24 | The Drama | undefined | 10:30pm | 1.1% | -900 min |
| AMC Quail Springs Mall 24 | The Drama | undefined | 9:45pm | 0% | -855 min |
| AMC Quail Springs Mall 24 | The Drama | undefined | 7:45pm | 3.4% | -735 min |
| AMC Quail Springs Mall 24 | The Drama | undefined | 7:00pm | 3.9% | -690 min |
| AMC Quail Springs Mall 24 | The Drama | undefined | 5:00pm | 1.1% | -570 min |
| AMC Rivercenter 11 | The Drama | undefined | 7:20pm | 13.3% | -709 min |
| AMC Rivercenter 11 | The Drama | undefined | 6:45pm | 15.6% | -675 min |
| AMC Robinson Crossing 6 | The Drama | undefined | 10:00pm | 5.6% | -870 min |
| AMC Robinson Crossing 6 | The Drama | undefined | 7:15pm | 8.5% | -705 min |
| AMC Rockford 16 | The Drama | undefined | 9:30pm | 0% | -840 min |
| AMC Rockford 16 | The Drama | undefined | 6:45pm | 1.4% | -675 min |
| AMC Sikes Senter 10 | The Drama | undefined | 7:10pm | 0% | -700 min |
| AMC Southern Hills 12 | The Drama | undefined | 7:45pm | 20.9% | -735 min |
| AMC Springfield 11 | The Drama | undefined | 9:50pm | 5.6% | -859 min |
| AMC Springfield 11 | The Drama | undefined | 7:00pm | 41.7% | -690 min |
| AMC Springfield 12 | The Drama | Open Caption (On-screen Subtitles) | 7:45pm | 0% | -735 min |
| AMC Springfield 12 | The Drama | undefined | 5:00pm | 1.4% | -570 min |
| AMC Springfield 8 | The Drama | undefined | 7:10pm | 21.8% | -700 min |
| AMC Stillwater 10 | The Drama | undefined | 7:00pm | 23.2% | -690 min |
| AMC Streets Of St Charles 8 | The Drama | undefined | 9:50pm | 1.6% | -859 min |
| AMC Streets Of St Charles 8 | The Drama | undefined | 7:00pm | 29% | -690 min |
| AMC Studio 28 | The Drama | Laser at AMC | 10:00pm | 0% | -869 min |
| AMC Studio 28 | The Drama | Laser at AMC | 8:15pm | 1.8% | -764 min |
| AMC Studio 28 | The Drama | Laser at AMC | 7:15pm | 14% | -704 min |
| AMC Studio 28 | The Drama | Laser at AMC | 6:30pm | 11% | -659 min |
| AMC Studio 28 | The Drama | Laser at AMC | 5:15pm | 4.9% | -584 min |
| AMC Summit 16 | The Drama | undefined | 10:15pm | 1% | -884 min |
| AMC Summit 16 | The Drama | undefined | 9:15pm | 0% | -824 min |
| AMC Summit 16 | The Drama | undefined | 7:30pm | 35% | -719 min |
| AMC Summit 16 | The Drama | undefined | 6:30pm | 4.5% | -659 min |
| AMC Tulsa Hills 12 | The Drama | undefined | 8:20pm | 1.7% | -769 min |
| AMC Tulsa Hills 12 | The Drama | undefined | 5:40pm | 9.1% | -609 min |
| AMC Tyler 14 | The Drama | Open Caption (On-screen Subtitles) | 6:35pm | 0% | -664 min |
| AMC Tyler 14 | The Drama | undefined | 10:15pm | 0.6% | -884 min |
| AMC Tyler 14 | The Drama | undefined | 9:30pm | 0% | -839 min |
| AMC Tyler 14 | The Drama | undefined | 7:30pm | 0% | -719 min |
| AMC Tyler 14 | The Drama | undefined | 5:45pm | 4.1% | -614 min |
| AMC University Place 8 | The Drama | undefined | 7:00pm | 5.6% | -689 min |
| AMC Valley Bend 18 | The Drama | Open Caption (On-screen Subtitles) | 7:35pm | 2.4% | -724 min |
| AMC West End Pointe 8 | The Drama | undefined | 9:30pm | 4.1% | -839 min |
| AMC West End Pointe 8 | The Drama | undefined | 6:45pm | 14.3% | -674 min |
| AMC Westbank Palace 16 | The Drama | undefined | 9:00pm | 9.3% | -809 min |
| AMC Westbank Palace 16 | The Drama | undefined | 6:35pm | 9.7% | -664 min |
| AMC Westroads 14 | The Drama | undefined | 8:00pm | 3.9% | -749 min |
| AMC Westroads 14 | The Drama | undefined | 5:15pm | 5.5% | -584 min |
| Cinema Centre 8 | The Drama | undefined | 8:30pm | 2.4% | -779 min |
| Cinema Centre 8 | The Drama | undefined | 5:45pm | 0% | -614 min |

**Issues:** AMC 600 North Michigan 9: No seat map for The Drama undefined; AMC CLASSIC Mounds View 15: No seat map for The Drama undefined; AMC CLASSIC Mounds View 15: No seat map for The Drama undefined; AMC CLASSIC Forney 12: No seat map for The Drama undefined; AMC CLASSIC Forney 12: No seat map for The Drama undefined; AMC CLASSIC Bloomington 12: No seat map for The Drama undefined; AMC Highland Village 12: No seat map for The Drama Laser at AMC

---

## 2026-04-07 08:32 — MT Group

**Polymarket movies tracked:** The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC 9+CO 10 | The Drama | Laser at AMC | 8:30pm | 71.4% | -839 min |
| AMC 9+CO 10 | The Drama | Laser at AMC | 5:45pm | 71.4% | -674 min |
| AMC Albuquerque 12 | The Drama | undefined | 7:20pm | 5% | -769 min |
| AMC Arrowhead 14 | The Drama | Laser at AMC | 10:40pm | 0% | -969 min |
| AMC Arrowhead 14 | The Drama | Laser at AMC | 6:30pm | 28.6% | -719 min |
| AMC Brighton 12 | The Drama | Laser at AMC | 7:15pm | 20.3% | -764 min |
| AMC Castle Rock 12 | The Drama | Laser at AMC | 8:00pm | 0% | -809 min |
| AMC Castle Rock 12 | The Drama | Laser at AMC | 5:10pm | 5.6% | -639 min |
| AMC Chapel Hills 13 | The Drama | undefined | 7:50pm | 2.6% | -799 min |
| AMC Chapel Hills 13 | The Drama | undefined | 5:05pm | 2.6% | -634 min |
| AMC DINE-IN Esplanade 14 | The Drama | Dine-In Delivery to Seat | 8:50pm | 6.8% | -859 min |
| AMC DINE-IN Esplanade 14 | The Drama | Dine-In Delivery to Seat | 8:15pm | 73.3% | -824 min |
| AMC DINE-IN Esplanade 14 | The Drama | Dine-In Delivery to Seat | 6:30pm | 73.7% | -719 min |
| AMC DINE-IN Esplanade 14 | The Drama | Dine-In Delivery to Seat | 5:30pm | 60% | -659 min |
| AMC DINE-IN SOUTHGATE 9 | The Drama | Dine-In Delivery to Seat | 9:55pm | 0% | -924 min |
| AMC DINE-IN SOUTHGATE 9 | The Drama | Dine-In Delivery to Seat | 8:15pm | 3.8% | -824 min |
| AMC DINE-IN SOUTHGATE 9 | The Drama | Dine-In Delivery to Seat | 5:30pm | 17% | -659 min |
| AMC Foothills 15 | The Drama | undefined | 9:00pm | 1.1% | -869 min |
| AMC Foothills 15 | The Drama | undefined | 6:15pm | 15.6% | -704 min |
| AMC Fort Collins 10 | The Drama | undefined | 7:15pm | 40% | -764 min |
| AMC Layton Hills 9 | The Drama | undefined | 9:50pm | 5.7% | -917 min |
| AMC Layton Hills 9 | The Drama | undefined | 7:00pm | 41.5% | -748 min |
| AMC Mesa Grand 14 | The Drama | Laser at AMC | 9:45pm | 2.7% | -913 min |
| AMC Mesa Grand 14 | The Drama | Laser at AMC | 7:00pm | 65.3% | -748 min |
| AMC Missoula 12 | The Drama | undefined | 8:15pm | 0% | -823 min |
| AMC Missoula 12 | The Drama | undefined | 5:00pm | 0% | -628 min |
| AMC Orchard 12 | The Drama | Laser at AMC | 9:45pm | 0% | -913 min |
| AMC Orchard 12 | The Drama | Laser at AMC | 7:40pm | 12% | -788 min |
| AMC Orchard 12 | The Drama | Laser at AMC | 5:30pm | 6.9% | -658 min |
| AMC Provo 8 | The Drama | undefined | 10:00pm | 16.8% | -928 min |
| AMC Provo 8 | The Drama | undefined | 7:15pm | 47.4% | -763 min |
| AMC Shiloh 14 | The Drama | undefined | 6:40pm | 2.3% | -728 min |
| AMC Superstition East 12 | The Drama | Laser at AMC | 9:10pm | 2.5% | -878 min |
| AMC Superstition East 12 | The Drama | Laser at AMC | 6:45pm | 71.1% | -733 min |
| AMC West Jordan 12 | The Drama | undefined | 7:00pm | 39.1% | -748 min |

---

## 2026-04-07 08:36 — PT Group

**Polymarket movies tracked:** The Drama

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC The Grove 14 | The Drama | Laser at AMC | 10:45pm | 0% | -1033 min |
| AMC The Grove 14 | The Drama | Laser at AMC | 10:00pm | 17.4% | -988 min |
| AMC The Grove 14 | The Drama | Laser at AMC | 9:00pm | 68.8% | -928 min |
| AMC The Grove 14 | The Drama | Laser at AMC | 8:15pm | 63.6% | -883 min |
| AMC The Grove 14 | The Drama | Laser at AMC | 8:00pm | 86.1% | -868 min |
| AMC The Grove 14 | The Drama | Laser at AMC | 7:00pm | 83.1% | -808 min |
| AMC The Grove 14 | The Drama | Laser at AMC | 6:00pm | 70.3% | -748 min |
| AMC The Grove 14 | The Drama | Laser at AMC | 5:00pm | 26.5% | -688 min |
| AMC Century City 15 | The Drama | Laser at AMC | 11:00pm | 0% | -1048 min |
| AMC Century City 15 | The Drama | Laser at AMC | 10:20pm | 13.3% | -1007 min |
| AMC Century City 15 | The Drama | Laser at AMC | 9:20pm | 55.1% | -947 min |
| AMC Century City 15 | The Drama | Laser at AMC | 8:05pm | 56.4% | -872 min |
| AMC Century City 15 | The Drama | Laser at AMC | 7:30pm | 79.6% | -838 min |
| AMC Century City 15 | The Drama | Laser at AMC | 6:30pm | 75.8% | -778 min |
| AMC Century City 15 | The Drama | Laser at AMC | 6:10pm | 29.5% | -758 min |
| AMC Burbank 16 | The Drama | XL at AMC | 9:30pm | 20% | -958 min |
| AMC Burbank 16 | The Drama | Laser at AMC | 10:35pm | 4.4% | -1022 min |
| AMC Burbank 16 | The Drama | Laser at AMC | 8:55pm | 48.2% | -923 min |
| AMC Burbank 16 | The Drama | Laser at AMC | 8:20pm | 71.2% | -887 min |
| AMC Burbank 16 | The Drama | Laser at AMC | 7:00pm | 69.3% | -808 min |
| AMC Burbank 16 | The Drama | Laser at AMC | 6:20pm | 60.6% | -767 min |
| AMC Burbank 16 | The Drama | Laser at AMC | 5:40pm | 41% | -728 min |
| AMC Burbank 16 | The Drama | Laser at AMC | 5:10pm | 11.7% | -698 min |
| AMC The Americana at Brand 18 | The Drama | Laser at AMC | 10:15pm | 3.8% | -1003 min |
| AMC The Americana at Brand 18 | The Drama | Laser at AMC | 9:45pm | 4.3% | -973 min |
| AMC The Americana at Brand 18 | The Drama | Laser at AMC | 9:00pm | 48.9% | -928 min |
| AMC The Americana at Brand 18 | The Drama | Laser at AMC | 7:30pm | 71.6% | -838 min |
| AMC The Americana at Brand 18 | The Drama | Laser at AMC | 7:00pm | 58.1% | -808 min |
| AMC The Americana at Brand 18 | The Drama | Laser at AMC | 5:45pm | 46.2% | -733 min |
| AMC Santa Monica 7 | The Drama | Laser at AMC | 9:50pm | 8.5% | -977 min |
| AMC Santa Monica 7 | The Drama | Laser at AMC | 7:55pm | 80.6% | -863 min |
| AMC Santa Monica 7 | The Drama | Laser at AMC | 7:00pm | 73.6% | -808 min |
| AMC Lakewood Mall 12 | The Drama | Laser at AMC | 10:05pm | 4.4% | -992 min |
| AMC Lakewood Mall 12 | The Drama | Laser at AMC | 7:25pm | 40% | -833 min |
| AMC DINE-IN Marina 6 | The Drama | Dine-In Delivery to Seat | 10:45pm | 12.5% | -1033 min |
| AMC DINE-IN Marina 6 | The Drama | Dine-In Delivery to Seat | 10:15pm | 3.2% | -1003 min |
| AMC DINE-IN Marina 6 | The Drama | Dine-In Delivery to Seat | 9:45pm | 53.4% | -973 min |
| AMC DINE-IN Marina 6 | The Drama | Dine-In Delivery to Seat | 8:00pm | 86.2% | -868 min |
| AMC DINE-IN Marina 6 | The Drama | Dine-In Delivery to Seat | 7:00pm | 96.6% | -808 min |
| AMC DINE-IN Fullerton 20 | The Drama | Laser at AMC | 10:00pm | 7.5% | -988 min |
| AMC DINE-IN Fullerton 20 | The Drama | Laser at AMC | 9:00pm | 21.6% | -928 min |
| AMC DINE-IN Fullerton 20 | The Drama | Laser at AMC | 7:15pm | 61.3% | -823 min |
| AMC DINE-IN Fullerton 20 | The Drama | Laser at AMC | 6:00pm | 30.2% | -748 min |
| AMC DINE-IN Fullerton 20 | The Drama | Dine-In Delivery to Seat | 9:30pm | 0% | -958 min |
| AMC Orange 30 | The Drama | Laser at AMC | 10:00pm | 5.3% | -988 min |
| AMC Orange 30 | The Drama | Laser at AMC | 9:15pm | 4% | -943 min |
| AMC Orange 30 | The Drama | Laser at AMC | 7:15pm | 26% | -823 min |
| AMC Orange 30 | The Drama | Laser at AMC | 6:15pm | 9.9% | -763 min |
| AMC Tustin 14 @ The District | The Drama | Laser at AMC | 10:30pm | 3.4% | -1017 min |
| AMC Tustin 14 @ The District | The Drama | Laser at AMC | 9:45pm | 3.4% | -972 min |
| AMC Tustin 14 @ The District | The Drama | Laser at AMC | 9:00pm | 27% | -927 min |
| AMC Tustin 14 @ The District | The Drama | Laser at AMC | 7:00pm | 65.1% | -807 min |
| AMC Tustin 14 @ The District | The Drama | Laser at AMC | 6:00pm | 61.1% | -747 min |
| AMC Puente Hills 20 | The Drama | Laser at AMC | 10:30pm | 2.7% | -1017 min |
| AMC Puente Hills 20 | The Drama | Laser at AMC | 9:30pm | 11.9% | -957 min |
| AMC Puente Hills 20 | The Drama | Laser at AMC | 7:15pm | 45.7% | -822 min |
| AMC Puente Hills 20 | The Drama | Laser at AMC | 6:30pm | 50% | -777 min |
| AMC Puente Hills 20 | The Drama | Laser at AMC | 5:00pm | 24.3% | -687 min |
| AMC Puente Hills 20 | The Drama | Open Caption (On-screen Subtitles) | 7:45pm | 27% | -852 min |
| AMC Norwalk 20 | The Drama | Laser at AMC | 10:30pm | 2.4% | -1017 min |
| AMC Norwalk 20 | The Drama | Laser at AMC | 10:00pm | 0% | -987 min |
| AMC Norwalk 20 | The Drama | Laser at AMC | 9:00pm | 46.4% | -927 min |
| AMC Norwalk 20 | The Drama | Laser at AMC | 7:30pm | 76.7% | -837 min |
| AMC Norwalk 20 | The Drama | Laser at AMC | 6:20pm | 32.7% | -766 min |
| AMC Norwalk 20 | The Drama | Laser at AMC | 6:00pm | 57.1% | -747 min |
| AMC Marina Pacifica 12 | The Drama | Laser at AMC | 9:40pm | 7.6% | -967 min |
| AMC Marina Pacifica 12 | The Drama | Laser at AMC | 8:35pm | 42.3% | -901 min |
| AMC Marina Pacifica 12 | The Drama | Laser at AMC | 7:40pm | 70.6% | -847 min |
| AMC Marina Pacifica 12 | The Drama | Laser at AMC | 6:40pm | 60.6% | -787 min |
| AMC Marina Pacifica 12 | The Drama | Laser at AMC | 5:45pm | 50% | -732 min |
| AMC Montebello 10 | The Drama | Laser at AMC | 10:15pm | 22.1% | -1002 min |
| AMC Montebello 10 | The Drama | Laser at AMC | 7:15pm | 67.3% | -822 min |
| AMC Montebello 10 | The Drama | Laser at AMC | 5:10pm | 52.5% | -697 min |
| AMC La Mirada 7 | The Drama | Laser at AMC | 9:30pm | 6.9% | -957 min |
| AMC La Mirada 7 | The Drama | Laser at AMC | 7:15pm | 50% | -822 min |
| AMC Metreon 16 | The Drama | Laser at AMC | 10:00pm | 2.2% | -987 min |
| AMC Metreon 16 | The Drama | Laser at AMC | 9:00pm | 50.5% | -927 min |
| AMC Metreon 16 | The Drama | Laser at AMC | 7:45pm | 69.8% | -852 min |
| AMC Metreon 16 | The Drama | Laser at AMC | 7:15pm | 70% | -822 min |
| AMC Metreon 16 | The Drama | Laser at AMC | 6:15pm | 77.4% | -762 min |
| AMC Metreon 16 | The Drama | Laser at AMC | 5:00pm | 46.5% | -687 min |
| AMC Mercado 20 | The Drama | Laser at AMC | 9:00pm | 53.8% | -927 min |
| AMC Mercado 20 | The Drama | Laser at AMC | 7:30pm | 68.3% | -837 min |
| AMC Mercado 20 | The Drama | Laser at AMC | 6:15pm | 66.3% | -762 min |
| AMC Mercado 20 | The Drama | Open Caption (On-screen Subtitles) | 10:15pm | 15% | -1002 min |
| AMC Eastridge 15 | The Drama | Laser at AMC | 9:00pm | 3.6% | -927 min |
| AMC Eastridge 15 | The Drama | Laser at AMC | 6:15pm | 11.5% | -762 min |
| AMC NewPark 12 | The Drama | Laser at AMC | 10:35pm | 2.9% | -1021 min |
| AMC NewPark 12 | The Drama | Laser at AMC | 6:00pm | 33.3% | -747 min |
| AMC Sunnyvale 12 | The Drama | Laser at AMC | 10:15pm | 33.3% | -1002 min |
| AMC Sunnyvale 12 | The Drama | Laser at AMC | 7:50pm | 4.4% | -856 min |
| AMC Sunnyvale 12 | The Drama | Laser at AMC | 7:30pm | 66.7% | -837 min |
| AMC Kabuki 8 | The Drama | Laser at AMC | 9:00pm | 25.6% | -927 min |
| AMC Kabuki 8 | The Drama | Laser at AMC | 7:30pm | 85.5% | -837 min |
| AMC Kabuki 8 | The Drama | Laser at AMC | 6:30pm | 76.1% | -777 min |
| AMC Kabuki 8 | The Drama | Laser at AMC | 5:30pm | 60% | -717 min |
| AMC Mission Valley 20 | The Drama | Laser at AMC | 10:30pm | 2.1% | -1017 min |
| AMC Mission Valley 20 | The Drama | Laser at AMC | 9:30pm | 6.7% | -957 min |
| AMC Mission Valley 20 | The Drama | Laser at AMC | 7:45pm | 59.9% | -852 min |
| AMC Mission Valley 20 | The Drama | Laser at AMC | 6:45pm | 70% | -792 min |
| AMC Mission Valley 20 | The Drama | Laser at AMC | 5:00pm | 9.5% | -687 min |
| AMC Fashion Valley 18 | The Drama | Laser at AMC | 9:00pm | 40.8% | -927 min |
| AMC Fashion Valley 18 | The Drama | Laser at AMC | 8:30pm | 53.2% | -897 min |
| AMC Fashion Valley 18 | The Drama | Laser at AMC | 7:45pm | 73.5% | -852 min |
| AMC Fashion Valley 18 | The Drama | Laser at AMC | 6:15pm | 68.4% | -762 min |
| AMC Fashion Valley 18 | The Drama | Laser at AMC | 5:40pm | 60.8% | -727 min |
| AMC Palm Promenade 24 | The Drama | Laser at AMC | 10:30pm | 0% | -1016 min |
| AMC Palm Promenade 24 | The Drama | Laser at AMC | 9:15pm | 2.2% | -941 min |
| AMC Palm Promenade 24 | The Drama | Laser at AMC | 7:45pm | 13.6% | -851 min |
| AMC Palm Promenade 24 | The Drama | Laser at AMC | 6:30pm | 5% | -776 min |
| AMC Palm Promenade 24 | The Drama | Laser at AMC | 5:00pm | 3.4% | -686 min |
| AMC La Jolla 12 | The Drama | Laser at AMC | 10:30pm | 25.7% | -1016 min |
| AMC La Jolla 12 | The Drama | Laser at AMC | 8:45pm | 76.3% | -911 min |
| AMC La Jolla 12 | The Drama | Laser at AMC | 7:45pm | 88.2% | -851 min |
| AMC La Jolla 12 | The Drama | Laser at AMC | 5:45pm | 86.7% | -731 min |
| AMC Chula Vista 10 | The Drama | Laser at AMC | 10:00pm | 3.6% | -986 min |
| AMC Chula Vista 10 | The Drama | Laser at AMC | 9:30pm | 6% | -956 min |
| AMC Chula Vista 10 | The Drama | Laser at AMC | 8:15pm | 39.5% | -881 min |
| AMC Chula Vista 10 | The Drama | Laser at AMC | 7:15pm | 73.2% | -821 min |
| AMC Otay Ranch 12 | The Drama | Laser at AMC | 8:30pm | 6.4% | -896 min |
| AMC Otay Ranch 12 | The Drama | Laser at AMC | 5:45pm | 5.3% | -731 min |
| AMC Plaza Bonita 14 | The Drama | Laser at AMC | 9:00pm | 1.5% | -926 min |
| AMC Plaza Bonita 14 | The Drama | Laser at AMC | 6:15pm | 24.4% | -761 min |
| AMC Poway 10 | The Drama | Laser at AMC | 9:15pm | 13.2% | -941 min |
| AMC Poway 10 | The Drama | Laser at AMC | 6:30pm | 55.9% | -776 min |
| AMC UTC 14 | The Drama | Laser at AMC | 10:30pm | 33.8% | -1016 min |
| AMC UTC 14 | The Drama | Laser at AMC | 9:30pm | 68.4% | -956 min |
| AMC UTC 14 | The Drama | Laser at AMC | 7:45pm | 77.5% | -851 min |
| AMC UTC 14 | The Drama | Laser at AMC | 6:45pm | 86% | -791 min |
| AMC UTC 14 | The Drama | Laser at AMC | 5:00pm | 62% | -686 min |
| AMC Southcenter 16 | The Drama | Laser at AMC | 10:30pm | 1.5% | -1016 min |
| AMC Southcenter 16 | The Drama | Laser at AMC | 5:00pm | 4.5% | -686 min |
| AMC Southcenter 16 | The Drama | Open Caption (On-screen Subtitles) | 7:45pm | 11.2% | -851 min |
| AMC Pacific Place 11 | The Drama | undefined | 9:30pm | 3.9% | -956 min |
| AMC Pacific Place 11 | The Drama | undefined | 7:30pm | 36.6% | -836 min |
| AMC Pacific Place 11 | The Drama | undefined | 6:15pm | 14.3% | -761 min |
| AMC Kent Station 14 | The Drama | Laser at AMC | 10:15pm | 4.5% | -1001 min |
| AMC Kent Station 14 | The Drama | Laser at AMC | 8:40pm | 3.9% | -906 min |
| AMC Kent Station 14 | The Drama | Laser at AMC | 7:45pm | 5.5% | -851 min |
| AMC Kent Station 14 | The Drama | Laser at AMC | 6:20pm | 40% | -766 min |
| AMC Alderwood Mall 16 | The Drama | Laser at AMC | 9:30pm | 0% | -956 min |
| AMC Alderwood Mall 16 | The Drama | Laser at AMC | 6:45pm | 23.5% | -791 min |
| AMC Factoria 8 | The Drama | Laser at AMC | 7:30pm | 28.6% | -836 min |
| AMC Woodinville 12 | The Drama | Laser at AMC | 10:00pm | 0% | -986 min |
| AMC Woodinville 12 | The Drama | Laser at AMC | 7:10pm | 56.2% | -816 min |
| AMC Woodinville 12 | The Drama | Laser at AMC | 5:30pm | 17.9% | -716 min |
| AMC Arizona Center 24 | The Drama | undefined | 8:15pm | 4.9% | -881 min |
| AMC Arizona Center 24 | The Drama | undefined | 5:30pm | 2.4% | -716 min |
| AMC Desert Ridge 18 | The Drama | Laser at AMC | 9:30pm | 4.8% | -956 min |
| AMC Desert Ridge 18 | The Drama | Laser at AMC | 7:15pm | 6.9% | -821 min |
| AMC Desert Ridge 18 | The Drama | Laser at AMC | 6:45pm | 51.2% | -791 min |
| AMC Deer Valley 17 | The Drama | Laser at AMC | 9:45pm | 2.8% | -971 min |
| AMC Deer Valley 17 | The Drama | Laser at AMC | 7:00pm | 4.7% | -806 min |
| AMC Deer Valley 17 | The Drama | Laser at AMC | 5:15pm | 27% | -701 min |
| AMC Ahwatukee 24 | The Drama | Laser at AMC | 9:15pm | 0% | -941 min |
| AMC Ahwatukee 24 | The Drama | Laser at AMC | 7:45pm | 46.3% | -851 min |
| AMC Ahwatukee 24 | The Drama | Laser at AMC | 6:25pm | 40% | -771 min |
| AMC Ahwatukee 24 | The Drama | Laser at AMC | 5:00pm | 14.8% | -686 min |
| AMC Westgate 20 | The Drama | Laser at AMC | 10:15pm | 0% | -1001 min |
| AMC Westgate 20 | The Drama | Laser at AMC | 8:45pm | 1.9% | -911 min |
| AMC Westgate 20 | The Drama | Laser at AMC | 7:30pm | 3.5% | -836 min |
| AMC Westgate 20 | The Drama | Laser at AMC | 6:00pm | 4.5% | -746 min |
| AMC Flatiron Crossing 14 | The Drama | Laser at AMC | 9:10pm | 13.3% | -935 min |
| AMC Flatiron Crossing 14 | The Drama | Laser at AMC | 7:05pm | 59.3% | -810 min |
| AMC Flatiron Crossing 14 | The Drama | Laser at AMC | 6:25pm | 35.6% | -770 min |
| AMC Highlands Ranch 24 | The Drama | Laser at AMC | 10:00pm | 0% | -985 min |
| AMC Highlands Ranch 24 | The Drama | Laser at AMC | 9:15pm | 21.2% | -940 min |
| AMC Highlands Ranch 24 | The Drama | Laser at AMC | 7:50pm | 42.4% | -855 min |
| AMC Highlands Ranch 24 | The Drama | Laser at AMC | 6:30pm | 71.2% | -775 min |
| AMC Highlands Ranch 24 | The Drama | Laser at AMC | 5:30pm | 26.9% | -715 min |
| AMC DINE-IN Southlands 16 | The Drama | Dine-In Delivery to Seat | 9:00pm | 4.3% | -925 min |
| AMC DINE-IN Southlands 16 | The Drama | Dine-In Delivery to Seat | 6:15pm | 47.8% | -760 min |
| AMC Arapahoe Crossing 16 | The Drama | Laser at AMC | 9:30pm | 4.2% | -955 min |
| AMC Arapahoe Crossing 16 | The Drama | Laser at AMC | 6:45pm | 57.9% | -790 min |
| AMC Anaheim GardenWalk 6 | The Drama | Laser at AMC | 10:00pm | 8% | -985 min |
| AMC Anaheim GardenWalk 6 | The Drama | Laser at AMC | 7:15pm | 50% | -820 min |
| AMC Bakersfield 6 | The Drama | undefined | 8:15pm | 20.7% | -880 min |
| AMC Burbank Town Center 8 | The Drama | Laser at AMC | 10:25pm | 3.3% | -1010 min |
| AMC Burbank Town Center 8 | The Drama | Laser at AMC | 9:00pm | 34.7% | -925 min |
| AMC Burbank Town Center 8 | The Drama | Laser at AMC | 7:30pm | 70% | -835 min |
| AMC Burbank Town Center 8 | The Drama | Laser at AMC | 6:15pm | 59.2% | -760 min |
| AMC Fallbrook 7 | The Drama | Laser at AMC | 10:15pm | 1.6% | -1000 min |
| AMC Fallbrook 7 | The Drama | Laser at AMC | 7:15pm | 59.8% | -820 min |
| AMC Kitsap 8 | The Drama | Laser at AMC | 9:00pm | 0% | -925 min |
| AMC Kitsap 8 | The Drama | Laser at AMC | 7:15pm | 14.9% | -820 min |
| AMC Manteca 16 | The Drama | Open Caption (On-screen Subtitles) | 5:15pm | 5.1% | -700 min |
| AMC Manteca 16 | The Drama | undefined | 8:15pm | 3.3% | -880 min |
| AMC Oak Tree 6 | The Drama | Laser at AMC | 6:45pm | 77.9% | -790 min |
| AMC Porter Ranch 9 | The Drama | Laser at AMC | 8:20pm | 60.6% | -885 min |
| AMC Porter Ranch 9 | The Drama | Laser at AMC | 7:00pm | 60.7% | -805 min |
| AMC Porter Ranch 9 | The Drama | Laser at AMC | 5:20pm | 57.7% | -705 min |
| AMC Progress Ridge 13 | The Drama | Open Caption (On-screen Subtitles) | 7:15pm | 12.2% | -820 min |
| AMC Rainbow Promenade 10 | The Drama | Laser at AMC | 9:15pm | 14.8% | -940 min |
| AMC Rainbow Promenade 10 | The Drama | Laser at AMC | 7:15pm | 39.8% | -820 min |
| AMC River Park Square 20 | The Drama | undefined | 10:15pm | 0% | -1000 min |
| AMC River Park Square 20 | The Drama | undefined | 9:35pm | 0% | -960 min |
| AMC River Park Square 20 | The Drama | undefined | 8:45pm | 8.9% | -910 min |
| AMC River Park Square 20 | The Drama | undefined | 7:45pm | 18% | -850 min |
| AMC River Park Square 20 | The Drama | undefined | 6:45pm | 10.4% | -790 min |
| AMC River Park Square 20 | The Drama | undefined | 5:45pm | 28.9% | -730 min |
| AMC Santa Anita 16 | The Drama | Laser at AMC | 10:15pm | 2.2% | -1000 min |
| AMC Santa Anita 16 | The Drama | Laser at AMC | 9:45pm | 1.6% | -970 min |
| AMC Santa Anita 16 | The Drama | Laser at AMC | 7:45pm | 3.7% | -850 min |
| AMC Santa Anita 16 | The Drama | Laser at AMC | 7:15pm | 43.2% | -820 min |
| AMC Topanga 12 | The Drama | Laser at AMC | 10:55pm | 0% | -1040 min |
| AMC Topanga 12 | The Drama | Laser at AMC | 10:15pm | 6.5% | -1000 min |
| AMC Topanga 12 | The Drama | Laser at AMC | 9:30pm | 30% | -955 min |
| AMC Topanga 12 | The Drama | Laser at AMC | 8:10pm | 57.1% | -875 min |
| AMC Topanga 12 | The Drama | Laser at AMC | 7:30pm | 63.4% | -835 min |
| AMC Topanga 12 | The Drama | Laser at AMC | 5:15pm | 34.3% | -700 min |
| AMC Town Square 18 | The Drama | Laser at AMC | 10:45pm | 0.7% | -1030 min |
| AMC Town Square 18 | The Drama | Laser at AMC | 8:00pm | 14.9% | -865 min |
| AMC Town Square 18 | The Drama | Laser at AMC | 6:20pm | 26.3% | -765 min |
| AMC Town Square 18 | The Drama | Laser at AMC | 5:10pm | 10.4% | -695 min |
| AMC Vancouver Mall 23 | The Drama | Open Caption (On-screen Subtitles) | 7:00pm | 1.1% | -805 min |
| AMC Vancouver Mall 23 | The Drama | undefined | 9:45pm | 0% | -970 min |
| AMC Victoria Gardens 12 | The Drama | Laser at AMC | 9:00pm | 3.2% | -925 min |
| AMC Victoria Gardens 12 | The Drama | Laser at AMC | 6:15pm | 10.7% | -760 min |

---

## 2026-04-08 05:06 — MT Group

**Polymarket movies tracked:** None found


**Issues:** No active Polymarket box office markets found

---

## 2026-04-08 05:50 — MT Group

**Polymarket movies tracked:** None found


**Issues:** No active Polymarket box office markets found

---

## 2026-04-08 06:15 — ALL Group

**Polymarket movies tracked:** None found


**Issues:** No active Polymarket box office markets found

---

## 2026-04-08 07:21 — ALL Group

**Polymarket movies tracked:** None found


**Issues:** No active Polymarket box office markets found

---

## 2026-04-08 21:41 — ALL Group

**Polymarket movies tracked:** None found


**Issues:** No active Polymarket box office markets found

---

## 2026-04-08 22:30 — ALL Group

**Polymarket movies tracked:** None found


**Issues:** No active Polymarket box office markets found

---

## 2026-04-08 23:28 — ALL Group

**Polymarket movies tracked:** None found


**Issues:** No active Polymarket box office markets found

---

## 2026-04-09 03:05 — ET Group

**Polymarket movies tracked:** None found


**Issues:** No active Polymarket box office markets found

---

## 2026-04-10 03:27 — ET Group

**Polymarket movies tracked:** You, Me & Tuscany

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Kips Bay 15 | You, Me & Tuscany | undefined | 11:00pm | 6.5% | 4 min |
| AMC DINE-IN Fashion District 8 | You, Me & Tuscany | Dine-In Delivery to Seat | 10:45pm | 8.4% | 23 min |
| AMC DINE-IN North Point Mall 12 | You, Me & Tuscany | Dine-In Delivery to Seat | 11:00pm | 6.2% | 10 min |
| AMC Bayou 15 | You, Me & Tuscany | undefined | 10:15pm | 3% | 57 min |
| AMC Boulevard 10 | You, Me & Tuscany | undefined | 10:15pm | 9% | 59 min |
| AMC Stones River 9 | You, Me & Tuscany | undefined | 10:30pm | 17% | 53 min |

**Issues:** AMC Empire 25: No seat map for You, Me & Tuscany Laser at AMC; AMC Empire 25: No seat map for You, Me & Tuscany Laser at AMC; AMC Lincoln Square 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Lincoln Square 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Lincoln Square 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Kips Bay 15: No seat map for You, Me & Tuscany undefined; AMC Kips Bay 15: No seat map for You, Me & Tuscany undefined; AMC Kips Bay 15: No seat map for You, Me & Tuscany undefined; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 84th Street 6: No seat map for You, Me & Tuscany Laser at AMC; AMC 84th Street 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Newport Centre 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Newport Centre 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Magic Johnson Harlem 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Magic Johnson Harlem 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Boston Common 19: No seat map for You, Me & Tuscany Laser at AMC; AMC Boston Common 19: No seat map for You, Me & Tuscany Laser at AMC; AMC Assembly Row 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Assembly Row 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Framingham 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Framingham 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Braintree 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Braintree 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Burlington Cinema 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Burlington Cinema 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Methuen 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Methuen 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Aventura 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Aventura 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Aventura 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Sunset Place 24: No seat map for You, Me & Tuscany undefined; AMC Sunset Place 24: No seat map for You, Me & Tuscany undefined; AMC Sunset Place 24: No seat map for You, Me & Tuscany undefined; AMC Sunset Place 24: No seat map for You, Me & Tuscany undefined; AMC DINE-IN Coral Ridge 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Coral Ridge 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Pembroke Lakes 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Pembroke Lakes 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Pompano Beach 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Pompano Beach 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Pompano Beach 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Sundial 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Sundial 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Sundial 12: No seat map for You, Me & Tuscany Laser at AMC; AMC West Shore 14: No seat map for You, Me & Tuscany undefined; AMC West Shore 14: No seat map for You, Me & Tuscany undefined; AMC Bradenton 20: No seat map for You, Me & Tuscany undefined; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Altamonte Mall 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Altamonte Mall 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Tysons Corner 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Tysons Corner 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Hoffman Center 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Hoffman Center 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Hoffman Center 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Hoffman Center 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Georgetown 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Georgetown 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Shirlington 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Worldgate 9: No seat map for You, Me & Tuscany undefined; AMC Neshaminy 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Neshaminy 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Cherry Hill 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Cherry Hill 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Cherry Hill 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Cherry Hill 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Voorhees 16: No seat map for You, Me & Tuscany undefined; AMC Plymouth Meeting Mall 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Plymouth Meeting Mall 12: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Fashion District 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Phipps Plaza 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Phipps Plaza 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Phipps Plaza 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Phipps Plaza 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Northlake 14: No seat map for You, Me & Tuscany undefined; AMC Northlake 14: No seat map for You, Me & Tuscany undefined; AMC Sugarloaf Mills 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Sugarloaf Mills 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrett Commons 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrett Commons 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Camp Creek 14: No seat map for You, Me & Tuscany undefined; AMC Camp Creek 14: No seat map for You, Me & Tuscany undefined; AMC Camp Creek 14: No seat map for You, Me & Tuscany undefined; AMC DINE-IN North Point Mall 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Carolina Pavilion 22: No seat map for You, Me & Tuscany undefined; AMC Carolina Pavilion 22: No seat map for You, Me & Tuscany undefined; AMC Concord Mills 24: No seat map for You, Me & Tuscany undefined; AMC Concord Mills 24: No seat map for You, Me & Tuscany undefined; AMC Forum 30: No seat map for You, Me & Tuscany undefined; AMC Forum 30: No seat map for You, Me & Tuscany undefined; AMC Star Great Lakes 25: No seat map for You, Me & Tuscany undefined; AMC Livonia 20: No seat map for You, Me & Tuscany undefined; AMC Livonia 20: No seat map for You, Me & Tuscany undefined; AMC Livonia 20: No seat map for You, Me & Tuscany undefined; AMC John R 15: No seat map for You, Me & Tuscany undefined; AMC John R 15: No seat map for You, Me & Tuscany undefined; AMC Castleton Square 14: No seat map for You, Me & Tuscany undefined; AMC Castleton Square 14: No seat map for You, Me & Tuscany undefined; AMC Castleton Square 14: No seat map for You, Me & Tuscany undefined; AMC Perry Crossing 18: No seat map for You, Me & Tuscany undefined; AMC Perry Crossing 18: No seat map for You, Me & Tuscany undefined; AMC Perry Crossing 18: No seat map for You, Me & Tuscany undefined; AMC Perry Crossing 18: No seat map for You, Me & Tuscany undefined; AMC Thoroughbred 20: No seat map for You, Me & Tuscany undefined; AMC Thoroughbred 20: No seat map for You, Me & Tuscany undefined; AMC Thoroughbred 20: No seat map for You, Me & Tuscany undefined; AMC Thoroughbred 20: No seat map for You, Me & Tuscany undefined; AMC Bellevue 12: No seat map for You, Me & Tuscany undefined; AMC Easton Town Center 30: No seat map for You, Me & Tuscany undefined; AMC Dublin Village 18: No seat map for You, Me & Tuscany undefined; AMC Dublin Village 18: No seat map for You, Me & Tuscany undefined; AMC Grove City 14: No seat map for You, Me & Tuscany undefined; AMC Newport On The Levee 20: No seat map for You, Me & Tuscany undefined; AMC Newport On The Levee 20: No seat map for You, Me & Tuscany undefined; AMC West Chester 18: No seat map for You, Me & Tuscany undefined; AMC West Chester 18: No seat map for You, Me & Tuscany undefined; AMC Waterfront 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Waterfront 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Regency 24: No seat map for You, Me & Tuscany undefined; AMC Regency 24: No seat map for You, Me & Tuscany undefined; AMC Regency 24: No seat map for You, Me & Tuscany undefined; AMC Regency 24: No seat map for You, Me & Tuscany undefined; AMC Orange Park 24: No seat map for You, Me & Tuscany undefined; AMC Orange Park 24: No seat map for You, Me & Tuscany undefined; AMC Orange Park 24: No seat map for You, Me & Tuscany undefined; AMC Academy 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Allegany 8: No seat map for You, Me & Tuscany undefined; AMC Altoona 12: No seat map for You, Me & Tuscany undefined; AMC Anderson Towne Center 9: No seat map for You, Me & Tuscany undefined; AMC Anderson Towne Center 9: No seat map for You, Me & Tuscany undefined; AMC Annapolis Mall 11: No seat map for You, Me & Tuscany undefined; AMC Annapolis Mall 11: No seat map for You, Me & Tuscany undefined; AMC Antioch 8: No seat map for You, Me & Tuscany undefined; AMC Antioch 8: No seat map for You, Me & Tuscany undefined; AMC Avenue 16: No seat map for You, Me & Tuscany undefined; AMC Avenue 16: No seat map for You, Me & Tuscany undefined; AMC Avenue Forsyth 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Avenue Forsyth 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Aviation 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Aviation 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Bay Plaza Cinema 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Bay Plaza Cinema 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Bayou 15: No seat map for You, Me & Tuscany undefined; AMC Bayou 15: No seat map for You, Me & Tuscany undefined; AMC Boulevard 10: No seat map for You, Me & Tuscany undefined; AMC Bradley Square 12: No seat map for You, Me & Tuscany undefined; AMC Bradley Square 12: No seat map for You, Me & Tuscany undefined; AMC Brick Plaza 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Brick Plaza 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Broadstreet 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Broadstreet 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Brunswick Square 13: No seat map for You, Me & Tuscany undefined; AMC Camp Hill 12: No seat map for You, Me & Tuscany undefined; AMC Chattanooga 18: No seat map for You, Me & Tuscany undefined; AMC Chattanooga 18: No seat map for You, Me & Tuscany undefined; AMC Cherry Blossom 14: No seat map for You, Me & Tuscany undefined; AMC Clifton Commons 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Clifton Commons 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Colonial 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Colonial 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Columbia 14: No seat map for You, Me & Tuscany undefined; AMC Columbus 10: No seat map for You, Me & Tuscany undefined; AMC Columbus 10: No seat map for You, Me & Tuscany undefined; AMC Columbus Park 15: No seat map for You, Me & Tuscany undefined; AMC Columbus Park 15: No seat map for You, Me & Tuscany undefined; AMC Columbus Park 15: No seat map for You, Me & Tuscany undefined; AMC Columbus Park 15: No seat map for You, Me & Tuscany undefined; AMC Courthouse Plaza 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Courthouse Plaza 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Crystal Run 16: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Berkshire 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Berkshire 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Bridgewater 7: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Essex Green 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Essex Green 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Essex Green 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Essex Green 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Holly Springs 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Holly Springs 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Menlo Park 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Menlo Park 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Midlothian 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Painters Crossing 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Shops at Riverside 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Shops at Riverside 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Danbury 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Danbury 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Dartmouth Mall 11: No seat map for You, Me & Tuscany undefined; AMC Dartmouth Mall 11: No seat map for You, Me & Tuscany undefined; AMC Deptford 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Deptford 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Destin Commons 14: No seat map for You, Me & Tuscany undefined; AMC East Hanover 12: No seat map for You, Me & Tuscany Laser at AMC; AMC East Hanover 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Evansville 16: No seat map for You, Me & Tuscany undefined; AMC Evansville 16: No seat map for You, Me & Tuscany undefined; AMC Evansville 16: No seat map for You, Me & Tuscany undefined; AMC Fayetteville 14: No seat map for You, Me & Tuscany undefined; AMC Fayetteville 14: No seat map for You, Me & Tuscany undefined; AMC Fiesta Square 12: No seat map for You, Me & Tuscany undefined; AMC Fire Tower 12: No seat map for You, Me & Tuscany undefined; AMC Fire Tower 12: No seat map for You, Me & Tuscany undefined; AMC Fleming Island 12: No seat map for You, Me & Tuscany undefined; AMC Fleming Island 12: No seat map for You, Me & Tuscany undefined; AMC Foothills 12: No seat map for You, Me & Tuscany undefined; AMC Freehold 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Freehold 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Garden State Plaza 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Garden State Plaza 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Glen Cove 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Glen Cove 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Grand Rapids 18: No seat map for You, Me & Tuscany undefined; AMC Hampton Towne Centre 24: No seat map for You, Me & Tuscany undefined; AMC Hanes 12: No seat map for You, Me & Tuscany undefined; AMC Hanes 12: No seat map for You, Me & Tuscany undefined; AMC Harbison 14: No seat map for You, Me & Tuscany undefined; AMC Harbison 14: No seat map for You, Me & Tuscany undefined; AMC Headquarters Plaza 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Headquarters Plaza 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Hialeah 12: No seat map for You, Me & Tuscany undefined; AMC Hialeah 12: No seat map for You, Me & Tuscany English Spoken with Spanish Subtitles; AMC Hialeah 12: No seat map for You, Me & Tuscany undefined; AMC Hickory 15: No seat map for You, Me & Tuscany undefined; AMC Hickory 15: No seat map for You, Me & Tuscany undefined; AMC Hickory 15: No seat map for You, Me & Tuscany undefined; AMC High Point 8: No seat map for You, Me & Tuscany undefined; AMC Highland 12: No seat map for You, Me & Tuscany undefined; AMC Highwoods 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Highwoods 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Highwoods 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Holland 8: No seat map for You, Me & Tuscany undefined; AMC Huntington Square 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Huntington Square 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Indian Mound 9: No seat map for You, Me & Tuscany undefined; AMC Indianapolis 17: No seat map for You, Me & Tuscany undefined; AMC Indianapolis 17: No seat map for You, Me & Tuscany undefined; AMC Jefferson Point 18: No seat map for You, Me & Tuscany undefined; AMC Jefferson Point 18: No seat map for You, Me & Tuscany undefined; AMC Jersey Gardens 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Jersey Gardens 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Johnson City 14: No seat map for You, Me & Tuscany undefined; AMC Kalli 12: No seat map for You, Me & Tuscany undefined; AMC Kalli 12: No seat map for You, Me & Tuscany undefined; AMC Lake Square 12: No seat map for You, Me & Tuscany undefined; AMC Lakeshore 8: No seat map for You, Me & Tuscany undefined; AMC Lakeshore 8: No seat map for You, Me & Tuscany undefined; AMC Loudoun Station 11: No seat map for You, Me & Tuscany undefined; AMC Loudoun Station 11: No seat map for You, Me & Tuscany undefined; AMC Lynnhaven 18: No seat map for You, Me & Tuscany undefined; AMC Lynnhaven 18: No seat map for You, Me & Tuscany undefined; AMC Madison Yards 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Madison Yards 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Madison Yards 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Madison Yards 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Majestic 12: No seat map for You, Me & Tuscany undefined; AMC Majestic 6: No seat map for You, Me & Tuscany undefined; AMC Majestic 6: No seat map for You, Me & Tuscany undefined; AMC Maple Ridge 8: No seat map for You, Me & Tuscany undefined; AMC Maple Ridge 8: No seat map for You, Me & Tuscany undefined; AMC Market Fair 15: No seat map for You, Me & Tuscany undefined; AMC Market Fair 15: No seat map for You, Me & Tuscany undefined; AMC MarketFair 10: No seat map for You, Me & Tuscany undefined; AMC MarketFair 10: No seat map for You, Me & Tuscany undefined; AMC Marlton 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Marlton 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Marple 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Marple 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Marquis 16: No seat map for You, Me & Tuscany undefined; AMC Marquis 16: No seat map for You, Me & Tuscany undefined; AMC Merchants Crossing 16: No seat map for You, Me & Tuscany undefined; AMC Mobile 16: No seat map for You, Me & Tuscany undefined; AMC Monmouth Mall 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Montgomery 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Montgomery 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Montgomery 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Morgantown 12: No seat map for You, Me & Tuscany undefined; AMC Morgantown 12: No seat map for You, Me & Tuscany undefined; AMC Mountainside 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Mountainside 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Muncie 12: No seat map for You, Me & Tuscany undefined; AMC Muncie 12: No seat map for You, Me & Tuscany undefined; AMC New Brunswick 18: No seat map for You, Me & Tuscany undefined; AMC New Brunswick 18: No seat map for You, Me & Tuscany undefined; AMC North Dekalb 16: No seat map for You, Me & Tuscany undefined; AMC North Dekalb 16: No seat map for You, Me & Tuscany undefined; AMC Northgate 14: No seat map for You, Me & Tuscany undefined; AMC Owings Mills 17: No seat map for You, Me & Tuscany undefined; AMC Owings Mills 17: No seat map for You, Me & Tuscany undefined; AMC Owings Mills 17: No seat map for You, Me & Tuscany undefined; AMC Palisades 21: No seat map for You, Me & Tuscany Laser at AMC; AMC Palisades 21: No seat map for You, Me & Tuscany Laser at AMC; AMC Park Place 16: No seat map for You, Me & Tuscany undefined; AMC Park Terrace 6: No seat map for You, Me & Tuscany undefined; AMC Park Terrace 6: No seat map for You, Me & Tuscany undefined; AMC Parkway Pointe 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Parkway Pointe 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Parkway Pointe 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Pembroke Lakes 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Pembroke Lakes 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Plainville 20: No seat map for You, Me & Tuscany undefined; AMC Plainville 20: No seat map for You, Me & Tuscany undefined; AMC Port Chester 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Port Chester 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Port St Lucie 14: No seat map for You, Me & Tuscany undefined; AMC Potomac Mills 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Potomac Mills 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Ridge Park Square 8: No seat map for You, Me & Tuscany undefined; AMC Ridge Park Square 8: No seat map for You, Me & Tuscany undefined; AMC Ridgefield Park 12: No seat map for You, Me & Tuscany undefined; AMC Ridgefield Park 12: No seat map for You, Me & Tuscany undefined; AMC Ritz 13: No seat map for You, Me & Tuscany undefined; AMC Ritz 13: No seat map for You, Me & Tuscany undefined; AMC River Hills 10: No seat map for You, Me & Tuscany undefined; AMC River Hills 10: No seat map for You, Me & Tuscany undefined; AMC Rivertowne 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Riverview 14: No seat map for You, Me & Tuscany undefined; AMC Riverview 14: No seat map for You, Me & Tuscany undefined; AMC Rockaway 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Rockaway 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Royale 6: No seat map for You, Me & Tuscany undefined; AMC Saratoga Springs 11: No seat map for You, Me & Tuscany undefined; AMC Saratoga Springs 11: No seat map for You, Me & Tuscany undefined; AMC Schererville 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Schererville 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Schererville 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Security Square 8: No seat map for You, Me & Tuscany undefined; AMC Security Square 8: No seat map for You, Me & Tuscany undefined; AMC SoNo8: No seat map for You, Me & Tuscany undefined; AMC SoNo8: No seat map for You, Me & Tuscany undefined; AMC South Bay Center 12: No seat map for You, Me & Tuscany Laser at AMC; AMC South Bay Center 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Southington 12: No seat map for You, Me & Tuscany undefined; AMC Southington 12: No seat map for You, Me & Tuscany undefined; AMC Southpoint 17: No seat map for You, Me & Tuscany undefined; AMC Southpoint 17: No seat map for You, Me & Tuscany undefined; AMC Spring Hill 12: No seat map for You, Me & Tuscany undefined; AMC Spring Hill 12: No seat map for You, Me & Tuscany undefined; AMC Star Gratiot 15: No seat map for You, Me & Tuscany undefined; AMC Staten Island 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Staten Island 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Stones River 9: No seat map for You, Me & Tuscany undefined; AMC Stonybrook 20: No seat map for You, Me & Tuscany undefined; AMC Stonybrook 20: No seat map for You, Me & Tuscany undefined; AMC Stonybrook 20: No seat map for You, Me & Tuscany undefined; AMC Sunrise 8: No seat map for You, Me & Tuscany undefined; AMC Tallahassee 20: No seat map for You, Me & Tuscany undefined; AMC Tallahassee 20: No seat map for You, Me & Tuscany undefined; AMC Tamiami 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Tamiami 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Tiger 13: No seat map for You, Me & Tuscany undefined; AMC Tilghman Square 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Tilghman Square 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Traders Point 12: No seat map for You, Me & Tuscany undefined; AMC Traders Point 12: No seat map for You, Me & Tuscany undefined; AMC Tyngsboro 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Tyngsboro 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Vestal Town Square 9: No seat map for You, Me & Tuscany undefined; AMC Washington Square 12: No seat map for You, Me & Tuscany undefined; AMC Washington Square 12: No seat map for You, Me & Tuscany undefined; AMC Wayne 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Wayne 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Webster 12: No seat map for You, Me & Tuscany undefined; AMC Webster 12: No seat map for You, Me & Tuscany undefined; AMC West Melbourne 12: No seat map for You, Me & Tuscany undefined; AMC West Melbourne 12: No seat map for You, Me & Tuscany undefined; AMC West Oaks 14: No seat map for You, Me & Tuscany undefined; AMC West Oaks 14: No seat map for You, Me & Tuscany undefined; AMC Westmoreland 15: No seat map for You, Me & Tuscany undefined; AMC Weston 8: No seat map for You, Me & Tuscany undefined; AMC Weston 8: No seat map for You, Me & Tuscany undefined; AMC Westwood Town Center 6: No seat map for You, Me & Tuscany undefined; AMC Wheaton Mall 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Wheaton Mall 9: No seat map for You, Me & Tuscany Laser at AMC; AMC White Marsh 16: No seat map for You, Me & Tuscany undefined; AMC White Marsh 16: No seat map for You, Me & Tuscany undefined; AMC Woodhaven 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodhaven 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Yulee 10: No seat map for You, Me & Tuscany undefined

---

## 2026-04-10 05:17 — CT Group

**Polymarket movies tracked:** You, Me & Tuscany


**Issues:** AMC River East 21: No seat map for You, Me & Tuscany Laser at AMC; AMC River East 21: No seat map for You, Me & Tuscany Laser at AMC; AMC NEWCITY 14: No seat map for You, Me & Tuscany Laser at AMC; AMC NEWCITY 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Village Crossing 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Village Crossing 18: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Block 37: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Block 37: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Block 37: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Rosemont 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Rosemont 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC 600 North Michigan 9: No seat map for You, Me & Tuscany undefined; AMC 600 North Michigan 9: No seat map for You, Me & Tuscany undefined; AMC Roosevelt Collection 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Roosevelt Collection 16: No seat map for You, Me & Tuscany Laser at AMC; AMC South Barrington 24: No seat map for You, Me & Tuscany Laser at AMC; AMC South Barrington 24: No seat map for You, Me & Tuscany Laser at AMC; AMC South Barrington 24: No seat map for You, Me & Tuscany Laser at AMC; AMC South Barrington 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Streets of Woodfield 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Streets of Woodfield 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Yorktown 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Yorktown 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Northbrook 14: No seat map for You, Me & Tuscany undefined; AMC Northbrook 14: No seat map for You, Me & Tuscany undefined; AMC Oakbrook Center 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Oakbrook Center 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Randhurst 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Niles 12: No seat map for You, Me & Tuscany undefined; AMC Ford City 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Ford City 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Ford City 14: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Mesquite 30: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Mesquite 30: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC NorthPark 15: No seat map for You, Me & Tuscany Laser at AMC; AMC NorthPark 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Stonebriar 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Stonebriar 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Stonebriar 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Grapevine Mills 24: No seat map for You, Me & Tuscany undefined; AMC Grapevine Mills 24: No seat map for You, Me & Tuscany undefined; AMC Firewheel 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Firewheel 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Firewheel 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Irving Mall 14: No seat map for You, Me & Tuscany Laser at AMC; AMC The Parks At Arlington 18: No seat map for You, Me & Tuscany Laser at AMC; AMC The Parks At Arlington 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Gulf Pointe 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Gulf Pointe 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Willowbrook 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Willowbrook 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Willowbrook 24: No seat map for You, Me & Tuscany Laser at AMC; AMC First Colony 24: No seat map for You, Me & Tuscany Laser at AMC; AMC First Colony 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Deerbrook 24: No seat map for You, Me & Tuscany undefined; AMC Deerbrook 24: No seat map for You, Me & Tuscany undefined; AMC Katy Mills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Katy Mills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Katy Mills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodlands Square 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodlands Square 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodlands Square 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Fountains 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Fountains 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Fountains 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Fountains 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Houston 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Eden Prairie Mall 18: No seat map for You, Me & Tuscany undefined; AMC Eden Prairie Mall 18: No seat map for You, Me & Tuscany undefined; AMC Rosedale 14: No seat map for You, Me & Tuscany undefined; AMC Rosedale 14: No seat map for You, Me & Tuscany undefined; AMC Southdale 16: No seat map for You, Me & Tuscany undefined; AMC Southdale 16: No seat map for You, Me & Tuscany undefined; AMC Coon Rapids 16: No seat map for You, Me & Tuscany undefined; AMC Inver Grove 16: No seat map for You, Me & Tuscany undefined; AMC Inver Grove 16: No seat map for You, Me & Tuscany undefined; AMC CLASSIC Mounds View 15: No seat map for You, Me & Tuscany undefined; AMC Metropark Square 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Metropark Square 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Spring 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Spring 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Eastchase 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Eastchase 9: No seat map for You, Me & Tuscany Laser at AMC; AMC CLASSIC Brazos Mall 14: No seat map for You, Me & Tuscany undefined; AMC Rio Cinemas 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Rio Cinemas 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Rio Cinemas 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Centerpoint 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Centerpoint 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Village On The Parkway 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Village On The Parkway 9: No seat map for You, Me & Tuscany Laser at AMC; AMC CLASSIC Forney 12: No seat map for You, Me & Tuscany undefined; AMC CLASSIC Forney 12: No seat map for You, Me & Tuscany undefined; AMC Birchwood 10: No seat map for You, Me & Tuscany undefined; AMC CLASSIC Bloomington 12: No seat map for You, Me & Tuscany undefined; AMC Causeway 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrywoods 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrywoods 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrywoods 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrywoods 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Independence Commons 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Independence Commons 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Ward Parkway 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Ward Parkway 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Center 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Center 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Center 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Legends 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Legends 14: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Prairiefire 17: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Barton Creek Square 14: No seat map for You, Me & Tuscany undefined; AMC Barton Creek Square 14: No seat map for You, Me & Tuscany undefined; AMC Baton Rouge 16: No seat map for You, Me & Tuscany undefined; AMC Baton Rouge 16: No seat map for You, Me & Tuscany undefined; AMC Boerne 11: No seat map for You, Me & Tuscany undefined; AMC Burleson 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Burleson 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Champaign 13: No seat map for You, Me & Tuscany undefined; AMC Chantilly 13: No seat map for You, Me & Tuscany Open Caption (On-screen Subtitles); AMC Chenal 9: No seat map for You, Me & Tuscany undefined; AMC Council Bluffs 17: No seat map for You, Me & Tuscany undefined; AMC Council Bluffs 17: No seat map for You, Me & Tuscany undefined; AMC Creve Coeur 12: No seat map for You, Me & Tuscany undefined; AMC Creve Coeur 12: No seat map for You, Me & Tuscany undefined; AMC DINE-IN Clearfork 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Clearfork 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Clearview Palace 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Manhattan 13: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Tech Ridge 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Tech Ridge 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Vestavia Hills 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Vestavia Hills 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Vestavia Hills 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Dakota Square 9: No seat map for You, Me & Tuscany undefined; AMC Decatur 12: No seat map for You, Me & Tuscany undefined; AMC Decatur 12: No seat map for You, Me & Tuscany undefined; AMC Decatur 12: No seat map for You, Me & Tuscany undefined; AMC Edinburg 18: No seat map for You, Me & Tuscany undefined; AMC Edinburg 18: No seat map for You, Me & Tuscany undefined; AMC Edwardsville 12: No seat map for You, Me & Tuscany undefined; AMC El Paso 16: No seat map for You, Me & Tuscany undefined; AMC El Paso 16: No seat map for You, Me & Tuscany undefined; AMC Elmwood Palace 20: No seat map for You, Me & Tuscany undefined; AMC Esquire 7: No seat map for You, Me & Tuscany undefined; AMC Esquire 7: No seat map for You, Me & Tuscany undefined; AMC Evanston 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Evanston 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Fitchburg 18: No seat map for You, Me & Tuscany undefined; AMC Galaxy 16: No seat map for You, Me & Tuscany undefined; AMC Grand Prairie 18: No seat map for You, Me & Tuscany undefined; AMC Grand Prairie 18: No seat map for You, Me & Tuscany undefined; AMC Grand Prairie 18: No seat map for You, Me & Tuscany undefined; AMC Hammond Palace 10: No seat map for You, Me & Tuscany undefined; AMC Hammond Palace 10: No seat map for You, Me & Tuscany undefined; AMC Hawthorn 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Hawthorn 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Highland Village 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Houma Palace 10: No seat map for You, Me & Tuscany undefined; AMC Lakeline 9: No seat map for You, Me & Tuscany undefined; AMC Lakeline 9: No seat map for You, Me & Tuscany undefined; AMC Longview 10: No seat map for You, Me & Tuscany undefined; AMC Longview 10: No seat map for You, Me & Tuscany undefined; AMC Lufkin 9: No seat map for You, Me & Tuscany undefined; AMC Machesney Park 14: No seat map for You, Me & Tuscany undefined; AMC Mall of Louisiana 15: No seat map for You, Me & Tuscany undefined; AMC Mall of Louisiana 15: No seat map for You, Me & Tuscany undefined; AMC Mayfair Mall 18: No seat map for You, Me & Tuscany undefined; AMC Norridge 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Norridge 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Northrock 14: No seat map for You, Me & Tuscany undefined; AMC Northrock 14: No seat map for You, Me & Tuscany undefined; AMC Palace 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Palace 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Patriot 13: No seat map for You, Me & Tuscany undefined; AMC Patton Creek 15: No seat map for You, Me & Tuscany undefined; AMC Patton Creek 15: No seat map for You, Me & Tuscany undefined; AMC Penn Square 10: No seat map for You, Me & Tuscany undefined; AMC Penn Square 10: No seat map for You, Me & Tuscany undefined; AMC Quail Springs Mall 24: No seat map for You, Me & Tuscany undefined; AMC Quail Springs Mall 24: No seat map for You, Me & Tuscany undefined; AMC Quail Springs Mall 24: No seat map for You, Me & Tuscany undefined; AMC Quail Springs Mall 24: No seat map for You, Me & Tuscany undefined; AMC Rivercenter 11: No seat map for You, Me & Tuscany undefined; AMC Robinson Crossing 6: No seat map for You, Me & Tuscany undefined; AMC Robinson Crossing 6: No seat map for You, Me & Tuscany undefined; AMC Rockford 16: No seat map for You, Me & Tuscany undefined; AMC Sikes Senter 10: No seat map for You, Me & Tuscany undefined; AMC Southern Hills 12: No seat map for You, Me & Tuscany undefined; AMC Southroads 20: No seat map for You, Me & Tuscany undefined; AMC Southroads 20: No seat map for You, Me & Tuscany undefined; AMC Springfield 11: No seat map for You, Me & Tuscany undefined; AMC Springfield 11: No seat map for You, Me & Tuscany undefined; AMC Springfield 12: No seat map for You, Me & Tuscany undefined; AMC Springfield 8: No seat map for You, Me & Tuscany undefined; AMC Stillwater 10: No seat map for You, Me & Tuscany undefined; AMC Streets Of St Charles 8: No seat map for You, Me & Tuscany undefined; AMC Streets Of St Charles 8: No seat map for You, Me & Tuscany undefined; AMC Studio 28: No seat map for You, Me & Tuscany Laser at AMC; AMC Studio 28: No seat map for You, Me & Tuscany Laser at AMC; AMC Studio 28: No seat map for You, Me & Tuscany Open Caption (On-screen Subtitles); AMC Summit 16: No seat map for You, Me & Tuscany undefined; AMC Summit 16: No seat map for You, Me & Tuscany undefined; AMC Tulsa Hills 12: No seat map for You, Me & Tuscany undefined; AMC Tyler 14: No seat map for You, Me & Tuscany Open Caption (On-screen Subtitles); AMC Tyler 14: No seat map for You, Me & Tuscany undefined; AMC University Place 8: No seat map for You, Me & Tuscany undefined; AMC Valley Bend 18: No seat map for You, Me & Tuscany undefined; AMC West End Pointe 8: No seat map for You, Me & Tuscany undefined; AMC West End Pointe 8: No seat map for You, Me & Tuscany undefined; AMC Westbank Palace 16: No seat map for You, Me & Tuscany undefined; AMC Westroads 14: No seat map for You, Me & Tuscany undefined; Cinema Centre 8: No seat map for You, Me & Tuscany undefined

---

## 2026-04-10 05:40 — ET Group

**Polymarket movies tracked:** You, Me & Tuscany


**Issues:** AMC Empire 25: No seat map for You, Me & Tuscany Laser at AMC; AMC Empire 25: No seat map for You, Me & Tuscany Laser at AMC; AMC Lincoln Square 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Lincoln Square 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Lincoln Square 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Kips Bay 15: No seat map for You, Me & Tuscany undefined; AMC Kips Bay 15: No seat map for You, Me & Tuscany undefined; AMC Kips Bay 15: No seat map for You, Me & Tuscany undefined; AMC Kips Bay 15: No seat map for You, Me & Tuscany undefined; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 34th Street 14: No seat map for You, Me & Tuscany Laser at AMC; AMC 84th Street 6: No seat map for You, Me & Tuscany Laser at AMC; AMC 84th Street 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Newport Centre 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Newport Centre 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Magic Johnson Harlem 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Magic Johnson Harlem 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Boston Common 19: No seat map for You, Me & Tuscany Laser at AMC; AMC Boston Common 19: No seat map for You, Me & Tuscany Laser at AMC; AMC Assembly Row 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Assembly Row 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Framingham 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Framingham 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Braintree 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Braintree 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Burlington Cinema 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Burlington Cinema 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Methuen 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Methuen 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Aventura 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Aventura 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Aventura 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Sunset Place 24: No seat map for You, Me & Tuscany undefined; AMC Sunset Place 24: No seat map for You, Me & Tuscany undefined; AMC Sunset Place 24: No seat map for You, Me & Tuscany undefined; AMC Sunset Place 24: No seat map for You, Me & Tuscany undefined; AMC DINE-IN Coral Ridge 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Coral Ridge 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Pembroke Lakes 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Pembroke Lakes 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Pompano Beach 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Pompano Beach 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Pompano Beach 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Veterans 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Sundial 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Sundial 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Sundial 12: No seat map for You, Me & Tuscany Laser at AMC; AMC West Shore 14: No seat map for You, Me & Tuscany undefined; AMC West Shore 14: No seat map for You, Me & Tuscany undefined; AMC Bradenton 20: No seat map for You, Me & Tuscany undefined; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Disney Springs 24: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Altamonte Mall 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Altamonte Mall 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Tysons Corner 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Tysons Corner 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Hoffman Center 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Hoffman Center 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Hoffman Center 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Hoffman Center 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Georgetown 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Georgetown 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Shirlington 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Worldgate 9: No seat map for You, Me & Tuscany undefined; AMC Neshaminy 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Neshaminy 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Cherry Hill 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Cherry Hill 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Cherry Hill 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Cherry Hill 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Voorhees 16: No seat map for You, Me & Tuscany undefined; AMC Plymouth Meeting Mall 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Plymouth Meeting Mall 12: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Fashion District 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Fashion District 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Phipps Plaza 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Phipps Plaza 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Phipps Plaza 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Phipps Plaza 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Northlake 14: No seat map for You, Me & Tuscany undefined; AMC Northlake 14: No seat map for You, Me & Tuscany undefined; AMC Sugarloaf Mills 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Sugarloaf Mills 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrett Commons 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrett Commons 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Camp Creek 14: No seat map for You, Me & Tuscany undefined; AMC Camp Creek 14: No seat map for You, Me & Tuscany undefined; AMC Camp Creek 14: No seat map for You, Me & Tuscany undefined; AMC DINE-IN North Point Mall 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN North Point Mall 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Carolina Pavilion 22: No seat map for You, Me & Tuscany undefined; AMC Carolina Pavilion 22: No seat map for You, Me & Tuscany undefined; AMC Concord Mills 24: No seat map for You, Me & Tuscany undefined; AMC Concord Mills 24: No seat map for You, Me & Tuscany undefined; AMC Forum 30: No seat map for You, Me & Tuscany undefined; AMC Forum 30: No seat map for You, Me & Tuscany undefined; AMC Star Great Lakes 25: No seat map for You, Me & Tuscany undefined; AMC Livonia 20: No seat map for You, Me & Tuscany undefined; AMC Livonia 20: No seat map for You, Me & Tuscany undefined; AMC Livonia 20: No seat map for You, Me & Tuscany undefined; AMC John R 15: No seat map for You, Me & Tuscany undefined; AMC John R 15: No seat map for You, Me & Tuscany undefined; AMC Castleton Square 14: No seat map for You, Me & Tuscany undefined; AMC Castleton Square 14: No seat map for You, Me & Tuscany undefined; AMC Castleton Square 14: No seat map for You, Me & Tuscany undefined; AMC Perry Crossing 18: No seat map for You, Me & Tuscany undefined; AMC Perry Crossing 18: No seat map for You, Me & Tuscany undefined; AMC Perry Crossing 18: No seat map for You, Me & Tuscany undefined; AMC Perry Crossing 18: No seat map for You, Me & Tuscany undefined; AMC Thoroughbred 20: No seat map for You, Me & Tuscany undefined; AMC Thoroughbred 20: No seat map for You, Me & Tuscany undefined; AMC Thoroughbred 20: No seat map for You, Me & Tuscany undefined; AMC Thoroughbred 20: No seat map for You, Me & Tuscany undefined; AMC Bellevue 12: No seat map for You, Me & Tuscany undefined; AMC Easton Town Center 30: No seat map for You, Me & Tuscany undefined; AMC Dublin Village 18: No seat map for You, Me & Tuscany undefined; AMC Dublin Village 18: No seat map for You, Me & Tuscany undefined; AMC Grove City 14: No seat map for You, Me & Tuscany undefined; AMC Newport On The Levee 20: No seat map for You, Me & Tuscany undefined; AMC Newport On The Levee 20: No seat map for You, Me & Tuscany undefined; AMC West Chester 18: No seat map for You, Me & Tuscany undefined; AMC West Chester 18: No seat map for You, Me & Tuscany undefined; AMC Waterfront 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Waterfront 22: No seat map for You, Me & Tuscany Laser at AMC; AMC Regency 24: No seat map for You, Me & Tuscany undefined; AMC Regency 24: No seat map for You, Me & Tuscany undefined; AMC Regency 24: No seat map for You, Me & Tuscany undefined; AMC Regency 24: No seat map for You, Me & Tuscany undefined; AMC Orange Park 24: No seat map for You, Me & Tuscany undefined; AMC Orange Park 24: No seat map for You, Me & Tuscany undefined; AMC Orange Park 24: No seat map for You, Me & Tuscany undefined; AMC Academy 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Allegany 8: No seat map for You, Me & Tuscany undefined; AMC Altoona 12: No seat map for You, Me & Tuscany undefined; AMC Anderson Towne Center 9: No seat map for You, Me & Tuscany undefined; AMC Anderson Towne Center 9: No seat map for You, Me & Tuscany undefined; AMC Annapolis Mall 11: No seat map for You, Me & Tuscany undefined; AMC Annapolis Mall 11: No seat map for You, Me & Tuscany undefined; AMC Antioch 8: No seat map for You, Me & Tuscany undefined; AMC Antioch 8: No seat map for You, Me & Tuscany undefined; AMC Avenue 16: No seat map for You, Me & Tuscany undefined; AMC Avenue 16: No seat map for You, Me & Tuscany undefined; AMC Avenue Forsyth 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Avenue Forsyth 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Aviation 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Aviation 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Bay Plaza Cinema 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Bay Plaza Cinema 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Bayou 15: No seat map for You, Me & Tuscany undefined; AMC Bayou 15: No seat map for You, Me & Tuscany undefined; AMC Bayou 15: No seat map for You, Me & Tuscany undefined; AMC Boulevard 10: No seat map for You, Me & Tuscany undefined; AMC Boulevard 10: No seat map for You, Me & Tuscany undefined; AMC Bradley Square 12: No seat map for You, Me & Tuscany undefined; AMC Bradley Square 12: No seat map for You, Me & Tuscany undefined; AMC Brick Plaza 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Brick Plaza 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Broadstreet 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Broadstreet 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Brunswick Square 13: No seat map for You, Me & Tuscany undefined; AMC Camp Hill 12: No seat map for You, Me & Tuscany undefined; AMC Chattanooga 18: No seat map for You, Me & Tuscany undefined; AMC Chattanooga 18: No seat map for You, Me & Tuscany undefined; AMC Cherry Blossom 14: No seat map for You, Me & Tuscany undefined; AMC Clifton Commons 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Clifton Commons 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Colonial 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Colonial 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Columbia 14: No seat map for You, Me & Tuscany undefined; AMC Columbus 10: No seat map for You, Me & Tuscany undefined; AMC Columbus 10: No seat map for You, Me & Tuscany undefined; AMC Columbus Park 15: No seat map for You, Me & Tuscany undefined; AMC Columbus Park 15: No seat map for You, Me & Tuscany undefined; AMC Columbus Park 15: No seat map for You, Me & Tuscany undefined; AMC Columbus Park 15: No seat map for You, Me & Tuscany undefined; AMC Courthouse Plaza 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Courthouse Plaza 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Crystal Run 16: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Berkshire 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Berkshire 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Bridgewater 7: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Essex Green 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Essex Green 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Essex Green 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Essex Green 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Holly Springs 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Holly Springs 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Menlo Park 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Menlo Park 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Midlothian 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Painters Crossing 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Shops at Riverside 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Shops at Riverside 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Danbury 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Danbury 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Dartmouth Mall 11: No seat map for You, Me & Tuscany undefined; AMC Dartmouth Mall 11: No seat map for You, Me & Tuscany undefined; AMC Deptford 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Deptford 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Destin Commons 14: No seat map for You, Me & Tuscany undefined; AMC East Hanover 12: No seat map for You, Me & Tuscany Laser at AMC; AMC East Hanover 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Evansville 16: No seat map for You, Me & Tuscany undefined; AMC Evansville 16: No seat map for You, Me & Tuscany undefined; AMC Evansville 16: No seat map for You, Me & Tuscany undefined; AMC Fayetteville 14: No seat map for You, Me & Tuscany undefined; AMC Fayetteville 14: No seat map for You, Me & Tuscany undefined; AMC Fiesta Square 12: No seat map for You, Me & Tuscany undefined; AMC Fire Tower 12: No seat map for You, Me & Tuscany undefined; AMC Fire Tower 12: No seat map for You, Me & Tuscany undefined; AMC Fleming Island 12: No seat map for You, Me & Tuscany undefined; AMC Fleming Island 12: No seat map for You, Me & Tuscany undefined; AMC Foothills 12: No seat map for You, Me & Tuscany undefined; AMC Freehold 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Freehold 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Garden State Plaza 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Garden State Plaza 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Glen Cove 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Glen Cove 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Grand Rapids 18: No seat map for You, Me & Tuscany undefined; AMC Hampton Towne Centre 24: No seat map for You, Me & Tuscany undefined; AMC Hanes 12: No seat map for You, Me & Tuscany undefined; AMC Hanes 12: No seat map for You, Me & Tuscany undefined; AMC Harbison 14: No seat map for You, Me & Tuscany undefined; AMC Harbison 14: No seat map for You, Me & Tuscany undefined; AMC Headquarters Plaza 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Headquarters Plaza 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Hialeah 12: No seat map for You, Me & Tuscany undefined; AMC Hialeah 12: No seat map for You, Me & Tuscany English Spoken with Spanish Subtitles; AMC Hialeah 12: No seat map for You, Me & Tuscany undefined; AMC Hickory 15: No seat map for You, Me & Tuscany undefined; AMC Hickory 15: No seat map for You, Me & Tuscany undefined; AMC Hickory 15: No seat map for You, Me & Tuscany undefined; AMC High Point 8: No seat map for You, Me & Tuscany undefined; AMC Highland 12: No seat map for You, Me & Tuscany undefined; AMC Highwoods 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Highwoods 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Highwoods 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Holland 8: No seat map for You, Me & Tuscany undefined; AMC Huntington Square 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Huntington Square 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Indian Mound 9: No seat map for You, Me & Tuscany undefined; AMC Indianapolis 17: No seat map for You, Me & Tuscany undefined; AMC Indianapolis 17: No seat map for You, Me & Tuscany undefined; AMC Jefferson Point 18: No seat map for You, Me & Tuscany undefined; AMC Jefferson Point 18: No seat map for You, Me & Tuscany undefined; AMC Jersey Gardens 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Jersey Gardens 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Johnson City 14: No seat map for You, Me & Tuscany undefined; AMC Kalli 12: No seat map for You, Me & Tuscany undefined; AMC Kalli 12: No seat map for You, Me & Tuscany undefined; AMC Lake Square 12: No seat map for You, Me & Tuscany undefined; AMC Lakeshore 8: No seat map for You, Me & Tuscany undefined; AMC Lakeshore 8: No seat map for You, Me & Tuscany undefined; AMC Loudoun Station 11: No seat map for You, Me & Tuscany undefined; AMC Loudoun Station 11: No seat map for You, Me & Tuscany undefined; AMC Lynnhaven 18: No seat map for You, Me & Tuscany undefined; AMC Lynnhaven 18: No seat map for You, Me & Tuscany undefined; AMC Madison Yards 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Madison Yards 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Madison Yards 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Madison Yards 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Majestic 12: No seat map for You, Me & Tuscany undefined; AMC Majestic 6: No seat map for You, Me & Tuscany undefined; AMC Majestic 6: No seat map for You, Me & Tuscany undefined; AMC Maple Ridge 8: No seat map for You, Me & Tuscany undefined; AMC Maple Ridge 8: No seat map for You, Me & Tuscany undefined; AMC Market Fair 15: No seat map for You, Me & Tuscany undefined; AMC Market Fair 15: No seat map for You, Me & Tuscany undefined; AMC MarketFair 10: No seat map for You, Me & Tuscany undefined; AMC MarketFair 10: No seat map for You, Me & Tuscany undefined; AMC Marlton 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Marlton 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Marple 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Marple 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Marquis 16: No seat map for You, Me & Tuscany undefined; AMC Marquis 16: No seat map for You, Me & Tuscany undefined; AMC Merchants Crossing 16: No seat map for You, Me & Tuscany undefined; AMC Mobile 16: No seat map for You, Me & Tuscany undefined; AMC Monmouth Mall 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Montgomery 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Montgomery 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Montgomery 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Morgantown 12: No seat map for You, Me & Tuscany undefined; AMC Morgantown 12: No seat map for You, Me & Tuscany undefined; AMC Mountainside 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Mountainside 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Muncie 12: No seat map for You, Me & Tuscany undefined; AMC Muncie 12: No seat map for You, Me & Tuscany undefined; AMC New Brunswick 18: No seat map for You, Me & Tuscany undefined; AMC New Brunswick 18: No seat map for You, Me & Tuscany undefined; AMC North Dekalb 16: No seat map for You, Me & Tuscany undefined; AMC North Dekalb 16: No seat map for You, Me & Tuscany undefined; AMC Northgate 14: No seat map for You, Me & Tuscany undefined; AMC Owings Mills 17: No seat map for You, Me & Tuscany undefined; AMC Owings Mills 17: No seat map for You, Me & Tuscany undefined; AMC Owings Mills 17: No seat map for You, Me & Tuscany undefined; AMC Palisades 21: No seat map for You, Me & Tuscany Laser at AMC; AMC Palisades 21: No seat map for You, Me & Tuscany Laser at AMC; AMC Park Place 16: No seat map for You, Me & Tuscany undefined; AMC Park Terrace 6: No seat map for You, Me & Tuscany undefined; AMC Park Terrace 6: No seat map for You, Me & Tuscany undefined; AMC Parkway Pointe 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Parkway Pointe 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Parkway Pointe 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Pembroke Lakes 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Pembroke Lakes 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Plainville 20: No seat map for You, Me & Tuscany undefined; AMC Plainville 20: No seat map for You, Me & Tuscany undefined; AMC Port Chester 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Port Chester 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Port St Lucie 14: No seat map for You, Me & Tuscany undefined; AMC Potomac Mills 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Potomac Mills 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Ridge Park Square 8: No seat map for You, Me & Tuscany undefined; AMC Ridge Park Square 8: No seat map for You, Me & Tuscany undefined; AMC Ridgefield Park 12: No seat map for You, Me & Tuscany undefined; AMC Ridgefield Park 12: No seat map for You, Me & Tuscany undefined; AMC Ritz 13: No seat map for You, Me & Tuscany undefined; AMC Ritz 13: No seat map for You, Me & Tuscany undefined; AMC River Hills 10: No seat map for You, Me & Tuscany undefined; AMC River Hills 10: No seat map for You, Me & Tuscany undefined; AMC Rivertowne 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Riverview 14: No seat map for You, Me & Tuscany undefined; AMC Riverview 14: No seat map for You, Me & Tuscany undefined; AMC Rockaway 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Rockaway 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Royale 6: No seat map for You, Me & Tuscany undefined; AMC Saratoga Springs 11: No seat map for You, Me & Tuscany undefined; AMC Saratoga Springs 11: No seat map for You, Me & Tuscany undefined; AMC Schererville 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Schererville 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Schererville 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Security Square 8: No seat map for You, Me & Tuscany undefined; AMC Security Square 8: No seat map for You, Me & Tuscany undefined; AMC SoNo8: No seat map for You, Me & Tuscany undefined; AMC SoNo8: No seat map for You, Me & Tuscany undefined; AMC South Bay Center 12: No seat map for You, Me & Tuscany Laser at AMC; AMC South Bay Center 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Southington 12: No seat map for You, Me & Tuscany undefined; AMC Southington 12: No seat map for You, Me & Tuscany undefined; AMC Southpoint 17: No seat map for You, Me & Tuscany undefined; AMC Southpoint 17: No seat map for You, Me & Tuscany undefined; AMC Spring Hill 12: No seat map for You, Me & Tuscany undefined; AMC Spring Hill 12: No seat map for You, Me & Tuscany undefined; AMC Star Gratiot 15: No seat map for You, Me & Tuscany undefined; AMC Staten Island 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Staten Island 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Stones River 9: No seat map for You, Me & Tuscany undefined; AMC Stones River 9: No seat map for You, Me & Tuscany undefined; AMC Stonybrook 20: No seat map for You, Me & Tuscany undefined; AMC Stonybrook 20: No seat map for You, Me & Tuscany undefined; AMC Stonybrook 20: No seat map for You, Me & Tuscany undefined; AMC Sunrise 8: No seat map for You, Me & Tuscany undefined; AMC Tallahassee 20: No seat map for You, Me & Tuscany undefined; AMC Tallahassee 20: No seat map for You, Me & Tuscany undefined; AMC Tamiami 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Tamiami 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Tiger 13: No seat map for You, Me & Tuscany undefined; AMC Tilghman Square 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Tilghman Square 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Traders Point 12: No seat map for You, Me & Tuscany undefined; AMC Traders Point 12: No seat map for You, Me & Tuscany undefined; AMC Tyngsboro 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Tyngsboro 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Vestal Town Square 9: No seat map for You, Me & Tuscany undefined; AMC Washington Square 12: No seat map for You, Me & Tuscany undefined; AMC Washington Square 12: No seat map for You, Me & Tuscany undefined; AMC Wayne 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Wayne 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Webster 12: No seat map for You, Me & Tuscany undefined; AMC Webster 12: No seat map for You, Me & Tuscany undefined; AMC West Melbourne 12: No seat map for You, Me & Tuscany undefined; AMC West Melbourne 12: No seat map for You, Me & Tuscany undefined; AMC West Oaks 14: No seat map for You, Me & Tuscany undefined; AMC West Oaks 14: No seat map for You, Me & Tuscany undefined; AMC Westmoreland 15: No seat map for You, Me & Tuscany undefined; AMC Weston 8: No seat map for You, Me & Tuscany undefined; AMC Weston 8: No seat map for You, Me & Tuscany undefined; AMC Westwood Town Center 6: No seat map for You, Me & Tuscany undefined; AMC Wheaton Mall 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Wheaton Mall 9: No seat map for You, Me & Tuscany Laser at AMC; AMC White Marsh 16: No seat map for You, Me & Tuscany undefined; AMC White Marsh 16: No seat map for You, Me & Tuscany undefined; AMC Woodhaven 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodhaven 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Yulee 10: No seat map for You, Me & Tuscany undefined

---

## 2026-04-10 06:13 — CT Group

**Polymarket movies tracked:** You, Me & Tuscany


**Issues:** AMC River East 21: No seat map for You, Me & Tuscany Laser at AMC; AMC River East 21: No seat map for You, Me & Tuscany Laser at AMC; AMC NEWCITY 14: No seat map for You, Me & Tuscany Laser at AMC; AMC NEWCITY 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Village Crossing 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Village Crossing 18: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Block 37: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Block 37: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Block 37: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Rosemont 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Rosemont 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC 600 North Michigan 9: No seat map for You, Me & Tuscany undefined; AMC 600 North Michigan 9: No seat map for You, Me & Tuscany undefined; AMC Roosevelt Collection 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Roosevelt Collection 16: No seat map for You, Me & Tuscany Laser at AMC; AMC South Barrington 24: No seat map for You, Me & Tuscany Laser at AMC; AMC South Barrington 24: No seat map for You, Me & Tuscany Laser at AMC; AMC South Barrington 24: No seat map for You, Me & Tuscany Laser at AMC; AMC South Barrington 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Streets of Woodfield 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Streets of Woodfield 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Yorktown 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Yorktown 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Northbrook 14: No seat map for You, Me & Tuscany undefined; AMC Northbrook 14: No seat map for You, Me & Tuscany undefined; AMC Oakbrook Center 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Oakbrook Center 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Randhurst 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Niles 12: No seat map for You, Me & Tuscany undefined; AMC Ford City 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Ford City 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Ford City 14: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Mesquite 30: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Mesquite 30: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC NorthPark 15: No seat map for You, Me & Tuscany Laser at AMC; AMC NorthPark 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Stonebriar 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Stonebriar 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Stonebriar 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Grapevine Mills 24: No seat map for You, Me & Tuscany undefined; AMC Grapevine Mills 24: No seat map for You, Me & Tuscany undefined; AMC Firewheel 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Firewheel 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Firewheel 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Irving Mall 14: No seat map for You, Me & Tuscany Laser at AMC; AMC The Parks At Arlington 18: No seat map for You, Me & Tuscany Laser at AMC; AMC The Parks At Arlington 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Southlake 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Gulf Pointe 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Gulf Pointe 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Willowbrook 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Willowbrook 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Willowbrook 24: No seat map for You, Me & Tuscany Laser at AMC; AMC First Colony 24: No seat map for You, Me & Tuscany Laser at AMC; AMC First Colony 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Deerbrook 24: No seat map for You, Me & Tuscany undefined; AMC Deerbrook 24: No seat map for You, Me & Tuscany undefined; AMC Katy Mills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Katy Mills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Katy Mills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodlands Square 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodlands Square 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodlands Square 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Fountains 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Fountains 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Fountains 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Fountains 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Houston 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Eden Prairie Mall 18: No seat map for You, Me & Tuscany undefined; AMC Eden Prairie Mall 18: No seat map for You, Me & Tuscany undefined; AMC Rosedale 14: No seat map for You, Me & Tuscany undefined; AMC Rosedale 14: No seat map for You, Me & Tuscany undefined; AMC Southdale 16: No seat map for You, Me & Tuscany undefined; AMC Southdale 16: No seat map for You, Me & Tuscany undefined; AMC Coon Rapids 16: No seat map for You, Me & Tuscany undefined; AMC Inver Grove 16: No seat map for You, Me & Tuscany undefined; AMC Inver Grove 16: No seat map for You, Me & Tuscany undefined; AMC CLASSIC Mounds View 15: No seat map for You, Me & Tuscany undefined; AMC Metropark Square 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Metropark Square 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Spring 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Spring 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Eastchase 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Eastchase 9: No seat map for You, Me & Tuscany Laser at AMC; AMC CLASSIC Brazos Mall 14: No seat map for You, Me & Tuscany undefined; AMC Rio Cinemas 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Rio Cinemas 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Rio Cinemas 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Centerpoint 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Centerpoint 11: No seat map for You, Me & Tuscany Laser at AMC; AMC Village On The Parkway 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Village On The Parkway 9: No seat map for You, Me & Tuscany Laser at AMC; AMC CLASSIC Forney 12: No seat map for You, Me & Tuscany undefined; AMC CLASSIC Forney 12: No seat map for You, Me & Tuscany undefined; AMC Birchwood 10: No seat map for You, Me & Tuscany undefined; AMC CLASSIC Bloomington 12: No seat map for You, Me & Tuscany undefined; AMC Causeway 13: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrywoods 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrywoods 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrywoods 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Barrywoods 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Independence Commons 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Independence Commons 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Ward Parkway 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Ward Parkway 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Center 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Center 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Center 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Legends 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Legends 14: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Prairiefire 17: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Barton Creek Square 14: No seat map for You, Me & Tuscany undefined; AMC Barton Creek Square 14: No seat map for You, Me & Tuscany undefined; AMC Baton Rouge 16: No seat map for You, Me & Tuscany undefined; AMC Baton Rouge 16: No seat map for You, Me & Tuscany undefined; AMC Boerne 11: No seat map for You, Me & Tuscany undefined; AMC Burleson 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Burleson 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Champaign 13: No seat map for You, Me & Tuscany undefined; AMC Chantilly 13: No seat map for You, Me & Tuscany Open Caption (On-screen Subtitles); AMC Chenal 9: No seat map for You, Me & Tuscany undefined; AMC Council Bluffs 17: No seat map for You, Me & Tuscany undefined; AMC Council Bluffs 17: No seat map for You, Me & Tuscany undefined; AMC Creve Coeur 12: No seat map for You, Me & Tuscany undefined; AMC Creve Coeur 12: No seat map for You, Me & Tuscany undefined; AMC DINE-IN Clearfork 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Clearfork 8: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Clearview Palace 12: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Manhattan 13: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Tech Ridge 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Tech Ridge 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Vestavia Hills 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Vestavia Hills 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Vestavia Hills 10: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Dakota Square 9: No seat map for You, Me & Tuscany undefined; AMC Decatur 12: No seat map for You, Me & Tuscany undefined; AMC Decatur 12: No seat map for You, Me & Tuscany undefined; AMC Decatur 12: No seat map for You, Me & Tuscany undefined; AMC Edinburg 18: No seat map for You, Me & Tuscany undefined; AMC Edinburg 18: No seat map for You, Me & Tuscany undefined; AMC Edwardsville 12: No seat map for You, Me & Tuscany undefined; AMC El Paso 16: No seat map for You, Me & Tuscany undefined; AMC El Paso 16: No seat map for You, Me & Tuscany undefined; AMC Elmwood Palace 20: No seat map for You, Me & Tuscany undefined; AMC Esquire 7: No seat map for You, Me & Tuscany undefined; AMC Esquire 7: No seat map for You, Me & Tuscany undefined; AMC Evanston 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Evanston 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Fitchburg 18: No seat map for You, Me & Tuscany undefined; AMC Galaxy 16: No seat map for You, Me & Tuscany undefined; AMC Grand Prairie 18: No seat map for You, Me & Tuscany undefined; AMC Grand Prairie 18: No seat map for You, Me & Tuscany undefined; AMC Grand Prairie 18: No seat map for You, Me & Tuscany undefined; AMC Hammond Palace 10: No seat map for You, Me & Tuscany undefined; AMC Hammond Palace 10: No seat map for You, Me & Tuscany undefined; AMC Hawthorn 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Hawthorn 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Highland Village 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Houma Palace 10: No seat map for You, Me & Tuscany undefined; AMC Lakeline 9: No seat map for You, Me & Tuscany undefined; AMC Lakeline 9: No seat map for You, Me & Tuscany undefined; AMC Longview 10: No seat map for You, Me & Tuscany undefined; AMC Longview 10: No seat map for You, Me & Tuscany undefined; AMC Lufkin 9: No seat map for You, Me & Tuscany undefined; AMC Machesney Park 14: No seat map for You, Me & Tuscany undefined; AMC Mall of Louisiana 15: No seat map for You, Me & Tuscany undefined; AMC Mall of Louisiana 15: No seat map for You, Me & Tuscany undefined; AMC Mayfair Mall 18: No seat map for You, Me & Tuscany undefined; AMC Norridge 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Norridge 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Northrock 14: No seat map for You, Me & Tuscany undefined; AMC Northrock 14: No seat map for You, Me & Tuscany undefined; AMC Palace 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Palace 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Patriot 13: No seat map for You, Me & Tuscany undefined; AMC Patton Creek 15: No seat map for You, Me & Tuscany undefined; AMC Patton Creek 15: No seat map for You, Me & Tuscany undefined; AMC Penn Square 10: No seat map for You, Me & Tuscany undefined; AMC Penn Square 10: No seat map for You, Me & Tuscany undefined; AMC Quail Springs Mall 24: No seat map for You, Me & Tuscany undefined; AMC Quail Springs Mall 24: No seat map for You, Me & Tuscany undefined; AMC Quail Springs Mall 24: No seat map for You, Me & Tuscany undefined; AMC Quail Springs Mall 24: No seat map for You, Me & Tuscany undefined; AMC Rivercenter 11: No seat map for You, Me & Tuscany undefined; AMC Robinson Crossing 6: No seat map for You, Me & Tuscany undefined; AMC Robinson Crossing 6: No seat map for You, Me & Tuscany undefined; AMC Rockford 16: No seat map for You, Me & Tuscany undefined; AMC Sikes Senter 10: No seat map for You, Me & Tuscany undefined; AMC Southern Hills 12: No seat map for You, Me & Tuscany undefined; AMC Southroads 20: No seat map for You, Me & Tuscany undefined; AMC Southroads 20: No seat map for You, Me & Tuscany undefined; AMC Springfield 11: No seat map for You, Me & Tuscany undefined; AMC Springfield 11: No seat map for You, Me & Tuscany undefined; AMC Springfield 12: No seat map for You, Me & Tuscany undefined; AMC Springfield 8: No seat map for You, Me & Tuscany undefined; AMC Stillwater 10: No seat map for You, Me & Tuscany undefined; AMC Streets Of St Charles 8: No seat map for You, Me & Tuscany undefined; AMC Streets Of St Charles 8: No seat map for You, Me & Tuscany undefined; AMC Studio 28: No seat map for You, Me & Tuscany Laser at AMC; AMC Studio 28: No seat map for You, Me & Tuscany Laser at AMC; AMC Studio 28: No seat map for You, Me & Tuscany Open Caption (On-screen Subtitles); AMC Summit 16: No seat map for You, Me & Tuscany undefined; AMC Summit 16: No seat map for You, Me & Tuscany undefined; AMC Tulsa Hills 12: No seat map for You, Me & Tuscany undefined; AMC Tyler 14: No seat map for You, Me & Tuscany Open Caption (On-screen Subtitles); AMC Tyler 14: No seat map for You, Me & Tuscany undefined; AMC University Place 8: No seat map for You, Me & Tuscany undefined; AMC Valley Bend 18: No seat map for You, Me & Tuscany undefined; AMC West End Pointe 8: No seat map for You, Me & Tuscany undefined; AMC West End Pointe 8: No seat map for You, Me & Tuscany undefined; AMC Westbank Palace 16: No seat map for You, Me & Tuscany undefined; AMC Westroads 14: No seat map for You, Me & Tuscany undefined; Cinema Centre 8: No seat map for You, Me & Tuscany undefined

---

## 2026-04-10 06:27 — MT Group

**Polymarket movies tracked:** You, Me & Tuscany


**Issues:** AMC 9+CO 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Albuquerque 12: No seat map for You, Me & Tuscany undefined; AMC Arrowhead 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Arrowhead 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Brighton 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Castle Rock 12: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Esplanade 14: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN SOUTHGATE 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Foothills 15: No seat map for You, Me & Tuscany undefined; AMC Foothills 15: No seat map for You, Me & Tuscany undefined; AMC Fort Collins 10: No seat map for You, Me & Tuscany undefined; AMC Layton Hills 9: No seat map for You, Me & Tuscany undefined; AMC Layton Hills 9: No seat map for You, Me & Tuscany undefined; AMC Mesa Grand 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Mesa Grand 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Mesa Grand 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Missoula 12: No seat map for You, Me & Tuscany undefined; AMC Orchard 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Orchard 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Provo 8: No seat map for You, Me & Tuscany undefined; AMC Provo 8: No seat map for You, Me & Tuscany undefined; AMC Shiloh 14: No seat map for You, Me & Tuscany undefined; AMC Superstition East 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Superstition East 12: No seat map for You, Me & Tuscany Laser at AMC; AMC West Jordan 12: No seat map for You, Me & Tuscany undefined

---

## 2026-04-10 07:12 — PT Group

**Polymarket movies tracked:** You, Me & Tuscany


**Issues:** AMC The Grove 14: No seat map for You, Me & Tuscany Laser at AMC; AMC The Grove 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Century City 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Century City 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Century City 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Burbank 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Burbank 16: No seat map for You, Me & Tuscany Laser at AMC; AMC The Americana at Brand 18: No seat map for You, Me & Tuscany Laser at AMC; AMC The Americana at Brand 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Santa Monica 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Santa Monica 7: No seat map for You, Me & Tuscany Laser at AMC; AMC The Regency 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Lakewood Mall 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Lakewood Mall 12: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Marina 6: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Marina 6: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Marina 6: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Brentwood 14: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Fullerton 20: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Fullerton 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Orange 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Orange 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Orange 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Tustin 14 @ The District: No seat map for You, Me & Tuscany Laser at AMC; AMC Tustin 14 @ The District: No seat map for You, Me & Tuscany Laser at AMC; AMC Puente Hills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Puente Hills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Norwalk 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Norwalk 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Norwalk 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Marina Pacifica 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Montebello 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Montebello 10: No seat map for You, Me & Tuscany Laser at AMC; AMC La Mirada 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Metreon 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Metreon 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Bay Street 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Bay Street 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Mercado 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Mercado 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Eastridge 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Saratoga 14: No seat map for You, Me & Tuscany Laser at AMC; AMC NewPark 12: No seat map for You, Me & Tuscany Laser at AMC; AMC NewPark 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Sunnyvale 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Sunnyvale 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Kabuki 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Mission Valley 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Mission Valley 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Fashion Valley 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Palm Promenade 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Palm Promenade 24: No seat map for You, Me & Tuscany Laser at AMC; AMC La Jolla 12: No seat map for You, Me & Tuscany Laser at AMC; AMC La Jolla 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Chula Vista 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Chula Vista 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Otay Ranch 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Plaza Bonita 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Plaza Bonita 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Poway 10: No seat map for You, Me & Tuscany Laser at AMC; AMC UTC 14: No seat map for You, Me & Tuscany Laser at AMC; AMC UTC 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Southcenter 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Southcenter 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Pacific Place 11: No seat map for You, Me & Tuscany undefined; AMC Pacific Place 11: No seat map for You, Me & Tuscany undefined; AMC Kent Station 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Kent Station 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Alderwood Mall 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Alderwood Mall 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Factoria 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodinville 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodinville 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Arizona Center 24: No seat map for You, Me & Tuscany undefined; AMC Desert Ridge 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Desert Ridge 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Deer Valley 17: No seat map for You, Me & Tuscany Laser at AMC; AMC Deer Valley 17: No seat map for You, Me & Tuscany Laser at AMC; AMC Ahwatukee 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Ahwatukee 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Westgate 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Westgate 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Westgate 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Westminster Promenade 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Flatiron Crossing 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Highlands Ranch 24: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Southlands 16: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Arapahoe Crossing 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Anaheim GardenWalk 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Bakersfield 6: No seat map for You, Me & Tuscany undefined; AMC Burbank Town Center 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Fallbrook 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Fallbrook 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Kitsap 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Kitsap 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Manteca 16: No seat map for You, Me & Tuscany undefined; AMC Oak Tree 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Porter Ranch 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Porter Ranch 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Progress Ridge 13: No seat map for You, Me & Tuscany undefined; AMC Rainbow Promenade 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Rainbow Promenade 10: No seat map for You, Me & Tuscany Laser at AMC; AMC River Park Square 20: No seat map for You, Me & Tuscany undefined; AMC River Park Square 20: No seat map for You, Me & Tuscany undefined; AMC River Park Square 20: No seat map for You, Me & Tuscany undefined; AMC Santa Anita 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Santa Anita 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Topanga 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Topanga 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Square 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Square 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Vancouver Mall 23: No seat map for You, Me & Tuscany undefined; AMC Vancouver Mall 23: No seat map for You, Me & Tuscany undefined; AMC Victoria Gardens 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Victoria Gardens 12: No seat map for You, Me & Tuscany Laser at AMC

---

## 2026-04-10 07:50 — PT Group

**Polymarket movies tracked:** You, Me & Tuscany


**Issues:** AMC The Grove 14: No seat map for You, Me & Tuscany Laser at AMC; AMC The Grove 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Century City 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Century City 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Century City 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Burbank 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Burbank 16: No seat map for You, Me & Tuscany Laser at AMC; AMC The Americana at Brand 18: No seat map for You, Me & Tuscany Laser at AMC; AMC The Americana at Brand 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Santa Monica 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Santa Monica 7: No seat map for You, Me & Tuscany Laser at AMC; AMC The Regency 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Lakewood Mall 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Lakewood Mall 12: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Marina 6: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Marina 6: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Marina 6: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Brentwood 14: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Fullerton 20: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Fullerton 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Orange 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Orange 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Orange 30: No seat map for You, Me & Tuscany Laser at AMC; AMC Tustin 14 @ The District: No seat map for You, Me & Tuscany Laser at AMC; AMC Tustin 14 @ The District: No seat map for You, Me & Tuscany Laser at AMC; AMC Puente Hills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Puente Hills 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Norwalk 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Norwalk 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Norwalk 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Marina Pacifica 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Montebello 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Montebello 10: No seat map for You, Me & Tuscany Laser at AMC; AMC La Mirada 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Metreon 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Metreon 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Bay Street 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Bay Street 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Mercado 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Mercado 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Eastridge 15: No seat map for You, Me & Tuscany Laser at AMC; AMC Saratoga 14: No seat map for You, Me & Tuscany Laser at AMC; AMC NewPark 12: No seat map for You, Me & Tuscany Laser at AMC; AMC NewPark 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Sunnyvale 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Sunnyvale 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Kabuki 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Mission Valley 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Mission Valley 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Fashion Valley 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Palm Promenade 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Palm Promenade 24: No seat map for You, Me & Tuscany Laser at AMC; AMC La Jolla 12: No seat map for You, Me & Tuscany Laser at AMC; AMC La Jolla 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Chula Vista 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Chula Vista 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Otay Ranch 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Plaza Bonita 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Plaza Bonita 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Poway 10: No seat map for You, Me & Tuscany Laser at AMC; AMC UTC 14: No seat map for You, Me & Tuscany Laser at AMC; AMC UTC 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Southcenter 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Southcenter 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Pacific Place 11: No seat map for You, Me & Tuscany undefined; AMC Pacific Place 11: No seat map for You, Me & Tuscany undefined; AMC Kent Station 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Kent Station 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Alderwood Mall 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Alderwood Mall 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Factoria 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodinville 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Woodinville 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Arizona Center 24: No seat map for You, Me & Tuscany undefined; AMC Desert Ridge 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Desert Ridge 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Deer Valley 17: No seat map for You, Me & Tuscany Laser at AMC; AMC Deer Valley 17: No seat map for You, Me & Tuscany Laser at AMC; AMC Ahwatukee 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Ahwatukee 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Westgate 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Westgate 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Westgate 20: No seat map for You, Me & Tuscany Laser at AMC; AMC Westminster Promenade 24: No seat map for You, Me & Tuscany Laser at AMC; AMC Flatiron Crossing 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Highlands Ranch 24: No seat map for You, Me & Tuscany Laser at AMC; AMC DINE-IN Southlands 16: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Arapahoe Crossing 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Anaheim GardenWalk 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Bakersfield 6: No seat map for You, Me & Tuscany undefined; AMC Burbank Town Center 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Fallbrook 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Fallbrook 7: No seat map for You, Me & Tuscany Laser at AMC; AMC Kitsap 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Kitsap 8: No seat map for You, Me & Tuscany Laser at AMC; AMC Manteca 16: No seat map for You, Me & Tuscany undefined; AMC Oak Tree 6: No seat map for You, Me & Tuscany Laser at AMC; AMC Porter Ranch 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Porter Ranch 9: No seat map for You, Me & Tuscany Laser at AMC; AMC Progress Ridge 13: No seat map for You, Me & Tuscany undefined; AMC Rainbow Promenade 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Rainbow Promenade 10: No seat map for You, Me & Tuscany Laser at AMC; AMC River Park Square 20: No seat map for You, Me & Tuscany undefined; AMC River Park Square 20: No seat map for You, Me & Tuscany undefined; AMC River Park Square 20: No seat map for You, Me & Tuscany undefined; AMC Santa Anita 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Santa Anita 16: No seat map for You, Me & Tuscany Laser at AMC; AMC Topanga 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Topanga 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Square 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Town Square 18: No seat map for You, Me & Tuscany Laser at AMC; AMC Vancouver Mall 23: No seat map for You, Me & Tuscany undefined; AMC Vancouver Mall 23: No seat map for You, Me & Tuscany undefined; AMC Victoria Gardens 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Victoria Gardens 12: No seat map for You, Me & Tuscany Laser at AMC

---

## 2026-04-11 06:03 — MT Group

**Polymarket movies tracked:** You, Me & Tuscany


**Issues:** AMC 9+CO 10: No seat map for You, Me & Tuscany Laser at AMC; AMC 9+CO 10: No seat map for You, Me & Tuscany Laser at AMC; AMC Albuquerque 12: No seat map for You, Me & Tuscany undefined; AMC Albuquerque 12: No seat map for You, Me & Tuscany undefined; AMC Arrowhead 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Arrowhead 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Brighton 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Brighton 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Castle Rock 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Castle Rock 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Chapel Hills 13: No seat map for You, Me & Tuscany undefined; AMC Chapel Hills 13: No seat map for You, Me & Tuscany undefined; AMC DINE-IN Esplanade 14: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Esplanade 14: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Esplanade 14: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Esplanade 14: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN Esplanade 14: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN SOUTHGATE 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC DINE-IN SOUTHGATE 9: No seat map for You, Me & Tuscany Dine-In Delivery to Seat; AMC Foothills 15: No seat map for You, Me & Tuscany undefined; AMC Foothills 15: No seat map for You, Me & Tuscany undefined; AMC Fort Collins 10: No seat map for You, Me & Tuscany undefined; AMC Fort Collins 10: No seat map for You, Me & Tuscany undefined; AMC Layton Hills 9: No seat map for You, Me & Tuscany undefined; AMC Layton Hills 9: No seat map for You, Me & Tuscany undefined; AMC Mesa Grand 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Mesa Grand 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Mesa Grand 14: No seat map for You, Me & Tuscany Laser at AMC; AMC Missoula 12: No seat map for You, Me & Tuscany undefined; AMC Orchard 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Orchard 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Provo 8: No seat map for You, Me & Tuscany undefined; AMC Provo 8: No seat map for You, Me & Tuscany undefined; AMC Shiloh 14: No seat map for You, Me & Tuscany undefined; AMC Shiloh 14: No seat map for You, Me & Tuscany undefined; AMC Shiloh 14: No seat map for You, Me & Tuscany undefined; AMC Superstition East 12: No seat map for You, Me & Tuscany Laser at AMC; AMC Superstition East 12: No seat map for You, Me & Tuscany Laser at AMC; AMC West Jordan 12: No seat map for You, Me & Tuscany undefined; AMC West Jordan 12: No seat map for You, Me & Tuscany undefined

---
