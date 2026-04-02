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
