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
