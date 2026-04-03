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
