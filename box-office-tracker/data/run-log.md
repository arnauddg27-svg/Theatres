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


## 2026-04-02 04:29 — PT Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC The Grove 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:00pm | 68% | -934 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 67.9% | -814 min |
| AMC The Grove 14 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 21.1% | -904 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 44% | -844 min |
| AMC Century City 15 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 19.3% | -904 min |
| AMC Burbank 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 67.4% | -814 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:00pm | 68.9% | -934 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:30pm | 65.2% | -964 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | XL at AMC | 9:00pm | 9.9% | -994 min |
| AMC The Americana at Brand 18 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 28.8% | -889 min |
| AMC Santa Monica 7 | The Super Mario Galaxy Movie | Laser at AMC | 6:20pm | 20.8% | -834 min |
| AMC Santa Monica 7 | The Super Mario Galaxy Movie | RealD 3D | 7:20pm | 17.3% | -894 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:10pm | 29.9% | -885 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 66.9% | -814 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 11.8% | -919 min |
| AMC The Regency 20 | The Super Mario Galaxy Movie | RealD 3D | 6:35pm | 0% | -849 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 32.2% | -889 min |
| AMC Lakewood Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 6.1% | -859 min |
| AMC DINE-IN Marina 6 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:30pm | 77.6% | -904 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | IMAX at AMC | 6:00pm | 7.6% | -814 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 45.4% | -874 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 3.5% | -889 min |
| AMC Brentwood 14 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 1.4% | -844 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 55.5% | -904 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 7.3% | -874 min |
| AMC DINE-IN Fullerton 20 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:30pm | 55.6% | -844 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 62.9% | -844 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 8.7% | -934 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 0% | -859 min |
| AMC Orange 30 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 2.6% | -874 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:30pm | 74.3% | -844 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 69.3% | -919 min |
| AMC Tustin 14 @ The District | The Super Mario Galaxy Movie | RealD 3D | 7:10pm | 23.8% | -885 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 35% | -934 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 65.9% | -874 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:35pm | 64.7% | -848 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 23.6% | -904 min |
| AMC Norwalk 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:40pm | 5.6% | -854 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 45.3% | -874 min |
| AMC Marina Pacifica 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 20.9% | -844 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:10pm | 74.1% | -884 min |
| AMC Montebello 10 | The Super Mario Galaxy Movie | RealD 3D | 6:25pm | 35.9% | -839 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 13.8% | -874 min |
| AMC La Mirada 7 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 1.7% | -919 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 46.8% | -904 min |
| AMC Metreon 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 8.6% | -844 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 50% | -919 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | XL at AMC | 8:30pm | 0% | -964 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 4% | -889 min |
| AMC Bay Street 16 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 2% | -859 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 36.4% | -874 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 12.5% | -844 min |
| AMC Mercado 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 10.4% | -904 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 31.7% | -844 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 3.3% | -874 min |
| AMC Eastridge 15 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 0.9% | -889 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 9.1% | -829 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | XL at AMC | 8:30pm | 2.5% | -964 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:45pm | 0% | -979 min |
| AMC Saratoga 14 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -919 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 13.4% | -814 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 10.9% | -844 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 7.8% | -919 min |
| AMC NewPark 12 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 7:15pm | 0% | -889 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 44.8% | -828 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 33.5% | -888 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 14.8% | -918 min |
| AMC Sunnyvale 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 1.9% | -858 min |
| AMC Kabuki 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 15.4% | -873 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 77.7% | -903 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 5.1% | -873 min |
| AMC Mission Valley 20 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 3.1% | -888 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 52% | -918 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | XL at AMC | 6:00pm | 21.4% | -813 min |
| AMC Palm Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 33.2% | -888 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 31% | -888 min |
| AMC La Jolla 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 22.2% | -858 min |
| AMC Chula Vista 10 | The Super Mario Galaxy Movie | undefined | 7:30pm | 45.5% | -903 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 54.2% | -888 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | XL at AMC | 6:45pm | 2.2% | -858 min |
| AMC Otay Ranch 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 0% | -918 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:15pm | 16.8% | -888 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 70.7% | -828 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | XL at AMC | 6:45pm | 2.9% | -858 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:45pm | 0% | -918 min |
| AMC Plaza Bonita 14 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 0% | -948 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 46.7% | -888 min |
| AMC Poway 10 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 12.1% | -858 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 65.1% | -873 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | PRIME at AMC | 8:00pm | 12.2% | -933 min |
| AMC UTC 14 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 22.8% | -843 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 27.2% | -902 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | XL at AMC | 7:00pm | 1.1% | -872 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 1.8% | -842 min |
| AMC Southcenter 16 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 1% | -812 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 4.4% | -961 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 9:00pm | 0% | -991 min |
| AMC Pacific Place 11 | The Super Mario Galaxy Movie | undefined | 7:15pm | 3.4% | -887 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 8:00pm | 4.2% | -932 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 36.3% | -872 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 7.9% | -887 min |
| AMC Kent Station 14 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 11.1% | -812 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 31.9% | -842 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 0% | -932 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 6.1% | -872 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 0.9% | -812 min |
| AMC Alderwood Mall 16 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 7:45pm | 2.4% | -917 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 16.9% | -887 min |
| AMC Factoria 8 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 6.5% | -961 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 36% | -917 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 28.8% | -887 min |
| AMC Woodinville 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 7.4% | -842 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 0.6% | -872 min |
| AMC Arizona Center 24 | The Super Mario Galaxy Movie | undefined | 6:30pm | 0% | -842 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 13.3% | -812 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 30.3% | -857 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 13.1% | -887 min |
| AMC Desert Ridge 18 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 5.9% | -872 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 3.9% | -812 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 12.6% | -917 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 11.3% | -857 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 13.6% | -872 min |
| AMC Deer Valley 17 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 9:00pm | 0% | -991 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | PRIME 3D | 7:00pm | 19.4% | -872 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 29.7% | -857 min |
| AMC Ahwatukee 24 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 9.9% | -827 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 10.1% | -812 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 36% | -902 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 0% | -827 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 0% | -917 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 8:00pm | 0% | -932 min |
| AMC Westgate 20 | The Super Mario Galaxy Movie | English Spoken with Spanish Subtitles | 9:00pm | 0% | -991 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 46.5% | -872 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 50% | -812 min |
| AMC Westminster Promenade 24 | The Super Mario Galaxy Movie | RealD 3D | 8:15pm | 23.2% | -947 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:15pm | 29.5% | -826 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:25pm | 16.9% | -896 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | Laser at AMC | 8:00pm | 0% | -931 min |
| AMC Flatiron Crossing 14 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 5.6% | -871 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 36.7% | -871 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | Laser at AMC | 6:45pm | 11.5% | -856 min |
| AMC Highlands Ranch 24 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 3.8% | -886 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 44.6% | -871 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 0% | -961 min |
| AMC DINE-IN Southlands 16 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 6:45pm | 22.2% | -856 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | IMAX at AMC | 6:45pm | 15.9% | -856 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:30pm | 13.2% | -961 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 16.8% | -901 min |
| AMC Arapahoe Crossing 16 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 9.5% | -826 min |

**Issues:** AMC Century City 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Century City 15: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Burbank 16: No seat map for The Super Mario Galaxy Movie SCREENX at AMC; AMC DINE-IN Marina 6: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Orange 30: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Puente Hills 20: No showtimes retrieved; AMC Metreon 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Bay Street 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mercado 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Eastridge 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Saratoga 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC NewPark 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Mission Valley 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Fashion Valley 18: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Palm Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Palm Promenade 24: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Chula Vista 10: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Chula Vista 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Otay Ranch 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Southcenter 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Alderwood Mall 16: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Westminster Promenade 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Highlands Ranch 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC

---

## 2026-04-03 01:28 — ET Group

**Polymarket movies tracked:** The Super Mario Galaxy Movie

| Theatre | Movie | Format | Showtime | Occupancy | Check Delta |
|---------|-------|--------|----------|-----------|-------------|
| AMC Empire 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 64.6% | -996 min |
| AMC Kips Bay 15 | The Super Mario Galaxy Movie | undefined | 6:15pm | 27% | -1011 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 68.8% | -1056 min |
| AMC 84th Street 6 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 27.3% | -996 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 56% | -1071 min |
| AMC Newport Centre 11 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 38.5% | -1026 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 60.5% | -1026 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | XL at AMC | 8:15pm | 8.4% | -1131 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 6.4% | -1056 min |
| AMC Boston Common 19 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 6.5% | -996 min |
| AMC Assembly Row 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 63.8% | -1071 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | PRIME at AMC | 7:45pm | 68.4% | -1101 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 17.9% | -1086 min |
| AMC Framingham 16 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 33.6% | -1056 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 48.6% | -1086 min |
| AMC Braintree 10 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 23.9% | -996 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | Laser at AMC | 7:30pm | 52.5% | -1085 min |
| AMC Burlington Cinema 10 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 41.3% | -1055 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:00pm | 46.2% | -1115 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Laser at AMC | 6:00pm | 71.9% | -994 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 38.9% | -1085 min |
| AMC Methuen 20 | The Super Mario Galaxy Movie | Open Caption (On-screen Subtitles) | 6:30pm | 7.4% | -1025 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 42.8% | -1025 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 11.8% | -1055 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 12.8% | -1085 min |
| AMC Aventura 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 16.5% | -1040 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | IMAX at AMC | 8:00pm | 34% | -1115 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 76.9% | -1070 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 3.1% | -1145 min |
| AMC Sunset Place 24 | The Super Mario Galaxy Movie | undefined | 7:00pm | 36.4% | -1055 min |
| AMC DINE-IN Coral Ridge 10 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:00pm | 65.2% | -1055 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | PRIME 3D | 7:15pm | 25.3% | -1070 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 20.4% | -1025 min |
| AMC Pompano Beach 18 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 6% | -1009 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 73.3% | -1040 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:15pm | 65.8% | -1070 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | RealD 3D | 8:30pm | 24% | -1145 min |
| AMC Veterans 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:30pm | 20.5% | -1025 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 48.1% | -1040 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | RealD 3D | 8:45pm | 3% | -1160 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:00pm | 1.5% | -994 min |
| AMC West Shore 14 | The Super Mario Galaxy Movie | undefined | 7:15pm | 0% | -1070 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 8.3% | -1055 min |
| AMC Bradenton 20 | The Super Mario Galaxy Movie | undefined | 6:30pm | 26.6% | -1025 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 8:15pm | 88.7% | -1130 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 52.7% | -1055 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 9.2% | -1070 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:00pm | 36.2% | -994 min |
| AMC DINE-IN Disney Springs 24 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 7:45pm | 80.4% | -1100 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:45pm | 70.8% | -1100 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:15pm | 19.2% | -1009 min |
| AMC Altamonte Mall 18 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 9% | -1070 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 17.9% | -994 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | Laser at AMC | 7:05pm | 16.2% | -1059 min |
| AMC Georgetown 14 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 7.6% | -1039 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 51.5% | -1054 min |
| AMC Plymouth Meeting Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:30pm | 0% | -1024 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:00pm | 73.2% | -1054 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | PRIME 3D | 8:00pm | 12.8% | -1114 min |
| AMC DINE-IN Fashion District 8 | The Super Mario Galaxy Movie | RealD 3D | 6:10pm | 16.3% | -1004 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 57.5% | -1084 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | XL at AMC | 8:00pm | 0% | -1114 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Laser at AMC | 6:30pm | 4.2% | -1024 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 5% | -1054 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:15pm | 6.5% | -1129 min |
| AMC Sugarloaf Mills 18 | The Super Mario Galaxy Movie | English Spoken with Chinese and English Subtitles | 8:30pm | 0% | -1144 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 79.6% | -994 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:30pm | 31.3% | -1024 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | Laser at AMC | 7:00pm | 24.9% | -1054 min |
| AMC Barrett Commons 24 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 10.6% | -1084 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 2.4% | -1069 min |
| AMC Camp Creek 14 | The Super Mario Galaxy Movie | undefined | 6:45pm | 4.7% | -1039 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 33.8% | -1009 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | RealD 3D | 6:45pm | 0% | -1039 min |
| AMC DINE-IN North Point Mall 12 | The Super Mario Galaxy Movie | Dine-In Delivery to Seat | 8:15pm | 35% | -1129 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 23.9% | -1053 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:30pm | 16% | -1143 min |
| AMC Carolina Pavilion 22 | The Super Mario Galaxy Movie | undefined | 6:40pm | 34.7% | -1033 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 6:00pm | 31% | -993 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 77.2% | -1083 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | RealD 3D | 7:00pm | 28.1% | -1053 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 7:10pm | 22.9% | -1063 min |
| AMC Concord Mills 24 | The Super Mario Galaxy Movie | undefined | 6:30pm | 52.7% | -1023 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | IMAX at AMC | 8:30pm | 0.4% | -1143 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 4.8% | -1068 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 0% | -1113 min |
| AMC Star Great Lakes 25 | The Super Mario Galaxy Movie | undefined | 6:20pm | 1.1% | -1013 min |
| AMC John R 15 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 10.9% | -1068 min |
| AMC John R 15 | The Super Mario Galaxy Movie | undefined | 6:45pm | 0% | -1038 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | IMAX at AMC | 6:15pm | 53% | -1008 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:30pm | 42.5% | -1083 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | RealD 3D | 8:00pm | 9.5% | -1113 min |
| AMC Castleton Square 14 | The Super Mario Galaxy Movie | undefined | 7:00pm | 18% | -1053 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 30.6% | -1098 min |
| AMC Indianapolis 17 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 64.8% | -1038 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 25.3% | -1053 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:00pm | 68.4% | -993 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | RealD 3D | 7:15pm | 10.8% | -1068 min |
| AMC Thoroughbred 20 | The Super Mario Galaxy Movie | undefined | 6:30pm | 2.4% | -1023 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | RealD 3D | 6:00pm | 15.1% | -993 min |
| AMC Bellevue 12 | The Super Mario Galaxy Movie | undefined | 7:00pm | 22.8% | -1053 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | IMAX with Laser at AMC | 7:00pm | 25.7% | -1052 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:15pm | 38.1% | -1006 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | RealD 3D | 7:30pm | 0% | -1082 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 6:45pm | 0% | -1037 min |
| AMC Easton Town Center 30 | The Super Mario Galaxy Movie | undefined | 6:30pm | 13.4% | -1021 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | IMAX at AMC | 7:00pm | 41.8% | -1052 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 4.8% | -1097 min |
| AMC Grove City 14 | The Super Mario Galaxy Movie | undefined | 7:15pm | 12.8% | -1067 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | IMAX at AMC | 7:45pm | 12.3% | -1097 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 6:45pm | 9.9% | -1037 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | RealD 3D | 6:15pm | 0% | -1006 min |
| AMC Newport On The Levee 20 | The Super Mario Galaxy Movie | undefined | 7:15pm | 11.1% | -1067 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | IMAX at AMC | 8:15pm | 12.9% | -1127 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | Dolby Cinema at AMC | 7:15pm | 58.4% | -1067 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | RealD 3D | 7:45pm | 27.1% | -1097 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | Spanish Language Dubbed with No Subtitles | 8:00pm | 10.4% | -1112 min |
| AMC West Chester 18 | The Super Mario Galaxy Movie | undefined | 7:00pm | 60.6% | -1052 min |

**Issues:** AMC Empire 25: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Empire 25: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Empire 25: No seat map for The Super Mario Galaxy Movie Open Caption (On-screen Subtitles); AMC Lincoln Square 13: No showtimes retrieved; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Kips Bay 15: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC 34th Street 14: No showtimes retrieved; AMC Magic Johnson Harlem 9: No showtimes retrieved; AMC Boston Common 19: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie Laser at AMC; AMC Assembly Row 12: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Braintree 10: No seat map for The Super Mario Galaxy Movie PRIME at AMC; AMC Methuen 20: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Aventura 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC DINE-IN Coral Ridge 10: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Pembroke Lakes 9: No showtimes retrieved; AMC Veterans 24: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Sundial 12: No showtimes retrieved; AMC Altamonte Mall 18: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Tysons Corner 16: No showtimes retrieved; AMC Hoffman Center 22: No showtimes retrieved; AMC Georgetown 14: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Shirlington 7: No showtimes retrieved; AMC Worldgate 9: No showtimes retrieved; AMC Neshaminy 24: No showtimes retrieved; AMC Cherry Hill 24: No showtimes retrieved; AMC Voorhees 16: No showtimes retrieved; AMC Phipps Plaza 14: No showtimes retrieved; AMC Northlake 14: No showtimes retrieved; AMC DINE-IN North Point Mall 12: No seat map for The Super Mario Galaxy Movie IMAX with Laser at AMC; AMC Highwoods 20: No showtimes retrieved; AMC Forum 30: No showtimes retrieved; AMC Livonia 20: No showtimes retrieved; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie RealD 3D; AMC Indianapolis 17: No seat map for The Super Mario Galaxy Movie undefined; AMC Perry Crossing 18: No showtimes retrieved; AMC CLASSIC Murfreesboro 16: No showtimes retrieved; AMC Bellevue 12: No seat map for The Super Mario Galaxy Movie Dolby Cinema at AMC; AMC Dublin Village 18: No showtimes retrieved; AMC Waterfront 22: No showtimes retrieved; AMC Regency 24: No showtimes retrieved; AMC Orange Park 24: No showtimes retrieved

---
