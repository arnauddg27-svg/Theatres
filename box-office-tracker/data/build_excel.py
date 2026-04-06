import csv
import json
import re
import pandas as pd
import xlsxwriter

CSV_PATH = "./box-office-tracker/data/seat-counts.csv"
OUT_PATH = "./box-office-tracker/data/2026-04-05-box-office.xlsx"
# TARGET_DATES: set to specific dates, or leave None to use the most recent weekend in the CSV
TARGET_DATES = None

# ── Load CSV ──────────────────────────────────────────────────────────────────
rows = []
with open(CSV_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'amc_seat_map_url' not in row:
            row['amc_seat_map_url'] = ''
        rows.append(dict(row))

df = pd.DataFrame(rows)
df = df[df['total_seats'].astype(str).str.strip() != ''].copy()

# Auto-detect most recent weekend if TARGET_DATES not set
if TARGET_DATES is None:
    latest_weekend = df['weekend_of'].max() if 'weekend_of' in df.columns else None
    if latest_weekend:
        TARGET_DATES = set(df[df['weekend_of'] == latest_weekend]['date'].unique())
    else:
        TARGET_DATES = set(df['date'].unique())
df = df[df['date'].isin(TARGET_DATES)].copy()
df = df[df['total_seats'].notna()].copy()

for col in ['total_seats', 'seats_sold', 'seats_available', 'occupancy_pct']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Dedup: keep best valid row per showtime (prefer has-URL, then highest occupancy)
df['_key'] = df['theatre_name'].str.strip() + '|' + df['auditorium_type'].str.strip() + '|' + df['showtime'].str.strip()
df['_has_url'] = df['amc_seat_map_url'].str.strip().ne('').astype(int)
df = df.sort_values(['_key', '_has_url', 'occupancy_pct'], ascending=[True, False, False])
df = df.drop_duplicates(subset='_key', keep='first').drop(columns=['_key', '_has_url'])

def showtime_sort_key(st):
    if not isinstance(st, str):
        return 9999
    m = re.match(r'(\d+):(\d+)(am|pm)', st.strip().lower())
    if not m:
        return 9999
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3)
    if ap == 'pm' and h != 12:
        h += 12
    if ap == 'am' and h == 12:
        h = 0
    return h * 60 + mi

FORMAT_PRIORITY = {'IMAX at AMC': 0, 'IMAX with Laser at AMC': 0, 'Dolby Cinema at AMC': 1,
                   'Laser at AMC': 2, 'PRIME at AMC': 3, 'XL at AMC': 4}
df['_fmt_pri'] = df['auditorium_type'].map(FORMAT_PRIORITY).fillna(99)
df['_show_sort'] = df['showtime'].apply(showtime_sort_key)
tz_order = {'ET': 0, 'CT': 1, 'MT': 2, 'PT': 3}
df['_tz_order'] = df['timezone'].map(tz_order).fillna(9)

# ── Load national theatre counts ──────────────────────────────────────────────
THEATRE_COUNTS_PATH = "./box-office-tracker/data/theatre-counts.json"
national_counts = {}
try:
    with open(THEATRE_COUNTS_PATH) as f:
        raw_counts = json.load(f)
    national_counts = {k: v for k, v in raw_counts.items() if not k.startswith('_') and isinstance(v, int)}
except FileNotFoundError:
    pass

def get_national_count(movie):
    if movie in national_counts:
        return national_counts[movie]
    m = movie.lower()
    for k, v in national_counts.items():
        if k.lower() in m or m in k.lower():
            return v
    return None

# ── Build dataframes ──────────────────────────────────────────────────────────

# Summary
summary_rows = []
for (movie, date, tz), g in df.groupby(['movie_title', 'date', 'timezone']):
    dow = g['day_of_week'].iloc[0]
    occ = g['occupancy_pct'].dropna()
    # Avg showings per cinema: total showtimes ÷ unique theatres
    n_theatres = g['theatre_name'].nunique()
    avg_showings = round(len(g) / n_theatres, 1) if n_theatres else None
    summary_rows.append({
        'Movie': movie, 'Date': str(date), 'Day of Week': dow, 'TZ': tz,
        'AMC Theatres (sample)': n_theatres,
        'National Theatres': get_national_count(movie),
        'Avg Showings/Cinema': avg_showings,
        '# Showtime Records': len(g),
        'Avg Occupancy %': round(occ.mean(), 1) if len(occ) else None,
        'Max Occupancy %': round(occ.max(), 1) if len(occ) else None,
        'Min Occupancy %': round(occ.min(), 1) if len(occ) else None,
    })
summary_df = pd.DataFrame(summary_rows)
summary_df['_tz_order'] = summary_df['TZ'].map(tz_order).fillna(9)
summary_df = summary_df.sort_values(['Movie', 'Date', '_tz_order']).drop(columns=['_tz_order'])

# By Theatre
by_theatre_rows = []
for (theatre, movie, date), g in df.groupby(['theatre_name', 'movie_title', 'date']):
    valid = g[g['occupancy_pct'].notna()]
    best = valid.loc[valid['occupancy_pct'].idxmax()] if len(valid) else g.iloc[0]
    by_theatre_rows.append({
        'Movie': movie, 'Date': str(date), 'TZ': best['timezone'],
        'Theatre': theatre, 'City': best['theatre_city'],
        'Top Format': best['auditorium_type'],
        'Best Occupancy %': best['occupancy_pct'],
        '# Formats': g['auditorium_type'].nunique(),
        '# Showtimes': len(g),
        'Showings/Cinema': round(len(g) / g['theatre_name'].nunique(), 1) if g['theatre_name'].nunique() else None,
        '_amc_url': best['amc_seat_map_url'] if pd.notna(best['amc_seat_map_url']) else '',
        '_tz_order': tz_order.get(best['timezone'], 9),
    })
by_theatre_df = pd.DataFrame(by_theatre_rows)
by_theatre_df = by_theatre_df.sort_values(['Date', '_tz_order', 'Theatre']).reset_index(drop=True)

# By Showtime
showtime_df = df.sort_values(['date', '_tz_order', 'theatre_name', '_fmt_pri', '_show_sort']).reset_index(drop=True)

# ── Workbook ──────────────────────────────────────────────────────────────────
DARK_BLUE = '#1F3864'
WHITE     = '#FFFFFF'
ALT_ROW   = '#EBF2FA'
LINK_COLOR = '#0563C1'

wb = xlsxwriter.Workbook(OUT_PATH, {'strings_to_urls': False})

def make_formats(wb):
    base = {'font_name': 'Arial', 'font_size': 10, 'border': 1,
            'border_color': '#CCCCCC', 'valign': 'vcenter'}
    hdr  = {'font_name': 'Arial', 'font_size': 11, 'bold': True,
            'font_color': WHITE, 'bg_color': DARK_BLUE,
            'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
            'border': 1, 'border_color': '#CCCCCC'}
    fmts = {}
    for alt in (False, True):
        bg = ALT_ROW if alt else WHITE
        for align in ('left', 'center'):
            for nf, key in [('', ''), ('0.0%', 'pct'), ('#,##0', 'num')]:
                d = {**base, 'bg_color': bg, 'align': align}
                if nf:
                    d['num_format'] = nf
                tag = f"{'alt' if alt else 'reg'}_{align}{'_'+key if key else ''}"
                fmts[tag] = wb.add_format(d)
    fmts['header'] = wb.add_format(hdr)
    link_base = {**base, 'font_color': LINK_COLOR, 'underline': True,
                 'align': 'center', 'bg_color': WHITE}
    link_alt  = {**link_base, 'bg_color': ALT_ROW}
    fmts['link']     = wb.add_format(link_base)
    fmts['link_alt'] = wb.add_format(link_alt)
    return fmts

fmts = make_formats(wb)

def hdr(ws, headers, widths):
    ws.set_row(0, 32, fmts['header'])
    for c, h in enumerate(headers):
        ws.write(0, c, h, fmts['header'])
    for c, w in enumerate(widths):
        ws.set_column(c, c, w)
    ws.freeze_panes(1, 0)

def fmt(alt, align='left', kind=''):
    tag = f"{'alt' if alt else 'reg'}_{align}{'_'+kind if kind else ''}"
    return fmts.get(tag, fmts[f"{'alt' if alt else 'reg'}_{align}"])

def write_url_cell(ws, row, col, url, display, alt):
    f = fmts['link_alt'] if alt else fmts['link']
    if url and str(url).strip().startswith('http'):
        ws.write_url(row, col, str(url).strip(), f, display)
    else:
        ws.write(row, col, '', fmt(alt, 'center'))

# ──────────────── Sheet 1: Summary ───────────────────────────────────────────
ws1 = wb.add_worksheet('Summary')
s_headers = ['Movie', 'Date', 'Day of Week', 'TZ',
             'AMC Theatres\n(our sample)', 'National\nTheatres', 'Avg Showings\n/Cinema',
             '# Showtime Records', 'Avg Occupancy %', 'Max Occupancy %', 'Min Occupancy %']
s_widths   = [32, 14, 14, 6, 16, 14, 14, 20, 16, 16, 16]
hdr(ws1, s_headers, s_widths)

for i, (_, row) in enumerate(summary_df.iterrows()):
    alt = i % 2 == 1
    ws1.write(i+1, 0, row['Movie'],                fmt(alt, 'left'))
    ws1.write(i+1, 1, row['Date'],                 fmt(alt, 'center'))
    ws1.write(i+1, 2, row['Day of Week'],          fmt(alt, 'left'))
    ws1.write(i+1, 3, row['TZ'],                   fmt(alt, 'center'))
    ws1.write(i+1, 4, row['AMC Theatres (sample)'], fmt(alt, 'center'))
    nat = row['National Theatres']
    ws1.write(i+1, 5, int(nat) if pd.notna(nat) else None, fmt(alt, 'center'))
    ws1.write(i+1, 6, row['Avg Showings/Cinema'],  fmt(alt, 'center'))
    ws1.write(i+1, 7, row['# Showtime Records'],   fmt(alt, 'center'))
    for j, col_k in enumerate(['Avg Occupancy %', 'Max Occupancy %', 'Min Occupancy %'], 8):
        v = row[col_k]
        ws1.write(i+1, j, (v / 100) if pd.notna(v) else None, fmt(alt, 'center', 'pct'))

# ──────────────── Sheet 2: By Theatre ────────────────────────────────────────
ws2 = wb.add_worksheet('By Theatre')
t_headers = ['Movie', 'Date', 'TZ', 'Theatre', 'City', 'Top Format',
             'Best Occupancy %', '# Formats', '# Showtimes', 'Showings/Cinema', 'Seat Map']
t_widths   = [32, 14, 6, 36, 20, 24, 18, 10, 12, 14, 12]
hdr(ws2, t_headers, t_widths)

for i, (_, row) in enumerate(by_theatre_df.iterrows()):
    alt = i % 2 == 1
    ws2.write(i+1, 0, row['Movie'],           fmt(alt, 'left'))
    ws2.write(i+1, 1, row['Date'],            fmt(alt, 'center'))
    ws2.write(i+1, 2, row['TZ'],              fmt(alt, 'center'))
    ws2.write(i+1, 3, row['Theatre'],         fmt(alt, 'left'))
    ws2.write(i+1, 4, row['City'],            fmt(alt, 'left'))
    ws2.write(i+1, 5, row['Top Format'],      fmt(alt, 'left'))
    v = row['Best Occupancy %']
    ws2.write(i+1, 6, (v / 100) if pd.notna(v) else None, fmt(alt, 'center', 'pct'))
    ws2.write(i+1, 7, row['# Formats'],      fmt(alt, 'center'))
    ws2.write(i+1, 8, row['# Showtimes'],    fmt(alt, 'center'))
    ws2.write(i+1, 9, row['Showings/Cinema'], fmt(alt, 'center'))
    url = row['_amc_url'] if pd.notna(row['_amc_url']) else ''
    write_url_cell(ws2, i+1, 10, url, 'View Seats', alt)

# ──────────────── Sheet 3: By Showtime ───────────────────────────────────────
ws3 = wb.add_worksheet('By Showtime')
st_headers = ['Movie', 'Date', 'Day', 'TZ', 'Theatre', 'City', 'Format', 'Showtime',
              'Total Seats', 'Seats Sold', 'Seats Available', 'Occupancy %', 'Seat Map']
st_widths  = [32, 14, 10, 6, 36, 20, 24, 10, 12, 12, 16, 14, 12]
hdr(ws3, st_headers, st_widths)

for i, (_, row) in enumerate(showtime_df.iterrows()):
    alt = i % 2 == 1
    ws3.write(i+1, 0, row['movie_title'],      fmt(alt, 'left'))
    ws3.write(i+1, 1, str(row['date']),        fmt(alt, 'center'))
    ws3.write(i+1, 2, row['day_of_week'],      fmt(alt, 'left'))
    ws3.write(i+1, 3, row['timezone'],         fmt(alt, 'center'))
    ws3.write(i+1, 4, row['theatre_name'],     fmt(alt, 'left'))
    ws3.write(i+1, 5, row['theatre_city'],     fmt(alt, 'left'))
    ws3.write(i+1, 6, row['auditorium_type'],  fmt(alt, 'left'))
    ws3.write(i+1, 7, row['showtime'],         fmt(alt, 'center'))
    def num(v): return v if pd.notna(v) else None
    ws3.write(i+1, 8,  num(row['total_seats']),     fmt(alt, 'center', 'num'))
    ws3.write(i+1, 9,  num(row['seats_sold']),       fmt(alt, 'center', 'num'))
    ws3.write(i+1, 10, num(row['seats_available']),  fmt(alt, 'center', 'num'))
    occ = row['occupancy_pct']
    ws3.write(i+1, 11, (occ / 100) if pd.notna(occ) else None, fmt(alt, 'center', 'pct'))
    url = row['amc_seat_map_url'] if pd.notna(row['amc_seat_map_url']) else ''
    write_url_cell(ws3, i+1, 12, url, 'View', alt)

# Conditional formatting on Occupancy % (col 11 = L, 0-indexed)
last = len(showtime_df) + 1
ws3.conditional_format(1, 11, last, 11, {
    'type': 'cell', 'criteria': '>=', 'value': 0.70,
    'format': wb.add_format({'bg_color': '#C6EFCE', 'font_color': '#276221'})})
ws3.conditional_format(1, 11, last, 11, {
    'type': 'cell', 'criteria': 'between', 'minimum': 0.40, 'maximum': 0.6999,
    'format': wb.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})})
ws3.conditional_format(1, 11, last, 11, {
    'type': 'cell', 'criteria': '<', 'value': 0.40,
    'format': wb.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})})

# ──────────────── Sheet 4: Raw ───────────────────────────────────────────────
ws4 = wb.add_worksheet('Raw')
raw_df = df.drop(columns=[c for c in df.columns if c and str(c).startswith('_')]).copy()
raw_df = raw_df[[c for c in raw_df.columns if c is not None]]
raw_cols = list(raw_df.columns)
RAW_WIDTHS = {'weekend_of':14,'run_id':24,'date':14,'day_of_week':12,'theatre_name':32,
              'theatre_city':18,'timezone':8,'movie_title':28,'polymarket_market':36,
              'showtime':10,'check_time':24,'minutes_after_showtime':22,'auditorium_name':24,
              'auditorium_type':26,'total_seats':12,'seats_sold':12,'seats_available':14,
              'occupancy_pct':14,'notes':50,'amc_seat_map_url':36}
hdr(ws4, raw_cols, [RAW_WIDTHS.get(c, 16) for c in raw_cols])

for i, (_, row) in enumerate(raw_df.iterrows()):
    alt = i % 2 == 1
    for j, col in enumerate(raw_cols):
        v = row[col]
        if isinstance(v, float) and pd.isna(v):
            v = None
        if col == 'amc_seat_map_url' and v and str(v).startswith('http'):
            f = fmts['link_alt'] if alt else fmts['link']
            ws4.write_url(i+1, j, str(v), f, str(v))
        else:
            ws4.write(i+1, j, v, fmt(alt, 'left'))

wb.close()
print(f"Saved: {OUT_PATH}")
print(f"Summary rows: {len(summary_df)}")
print(f"By Theatre rows: {len(by_theatre_df)}")
print(f"By Showtime rows: {len(showtime_df)}")
print(f"Raw rows: {len(raw_df)}")
