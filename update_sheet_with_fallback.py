import json
import sys
import socket

# Force IPv4
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import csv
import gspread
from google.oauth2.service_account import Credentials

sys.stdout.reconfigure(encoding='utf-8')

with open('oxford_3000_final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print(f"Loaded {len(dataset)} records from oxford_3000_final.json")

headers_13 = [
    'No',
    'Level',
    'Word',
    'Pronunciation (UK)',
    'Pronunciation (US)',
    'Audio UK',
    'Audio US',
    'Part of Speech',
    'Arti (Bahasa Indonesia)',
    'Contoh Kalimat',
    'Full Entry',
    'Oxford Fallback UK',
    'Oxford Fallback US'
]

by_level = {'A1': [], 'A2': [], 'B1': [], 'B2': []}
for r in dataset:
    by_level[r['level']].append(r)

# 1. Update Google Sheet via API
CRED_PATH = r'C:\Users\LILI\OneDrive - PDK Jateng\Dokumen\widio-titip\credentials_gdrive_widio.json'
SPREADSHEET_ID = '1_l6Ojulq3jMryReGtmN1z1PtWYSkVtggDC0PpEVcjqQ'
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

creds = Credentials.from_service_account_file(CRED_PATH, scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)
print(f"Connected to Google Sheet: '{sh.title}'")

cat_colors = {
    'A1': {"red": 0.11, "green": 0.37, "blue": 0.13},
    'A2': {"red": 0.05, "green": 0.28, "blue": 0.63},
    'B1': {"red": 0.90, "green": 0.32, "blue": 0.00},
    'B2': {"red": 0.72, "green": 0.11, "blue": 0.11},
    'HEADER': {"red": 0.15, "green": 0.20, "blue": 0.22}
}

# Update All Words
try:
    ws_all = sh.worksheet('All Words')
    ws_all.clear()
except gspread.exceptions.WorksheetNotFound:
    ws_all = sh.add_worksheet(title='All Words', rows=3400, cols=13)

all_matrix = [headers_13]
for r in dataset:
    fb_uk_formula = f'=HYPERLINK("{r.get("oxford_uk_url", "")}", "🌐 Oxford UK")' if r.get('oxford_uk_url') else '-'
    fb_us_formula = f'=HYPERLINK("{r.get("oxford_us_url", "")}", "🌐 Oxford US")' if r.get('oxford_us_url') else '-'
    all_matrix.append([
        r['no'],
        r['level'],
        r['word'],
        r['ipa_uk'],
        r['ipa_us'],
        r['audio_uk_formula'],
        r['audio_us_formula'],
        r['pos'],
        r['arti'],
        r['contoh_kalimat'],
        r['full_entry'],
        fb_uk_formula,
        fb_us_formula
    ])

ws_all.update(range_name=f'A1:M{len(all_matrix)}', values=all_matrix, value_input_option='USER_ENTERED')
ws_all.freeze(rows=1)
print(f"Sheet 'All Words' updated with {len(all_matrix)-1} rows & 13 columns.")

# Update A1, A2, B1, B2
for cat in ['A1', 'A2', 'B1', 'B2']:
    try:
        ws = sh.worksheet(cat)
        ws.clear()
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=cat, rows=len(by_level[cat]) + 50, cols=13)
        
    cat_matrix = [headers_13]
    cat_idx = 1
    for r in by_level[cat]:
        fb_uk_formula = f'=HYPERLINK("{r.get("oxford_uk_url", "")}", "🌐 Oxford UK")' if r.get('oxford_uk_url') else '-'
        fb_us_formula = f'=HYPERLINK("{r.get("oxford_us_url", "")}", "🌐 Oxford US")' if r.get('oxford_us_url') else '-'
        cat_matrix.append([
            cat_idx,
            r['level'],
            r['word'],
            r['ipa_uk'],
            r['ipa_us'],
            r['audio_uk_formula'],
            r['audio_us_formula'],
            r['pos'],
            r['arti'],
            r['contoh_kalimat'],
            r['full_entry'],
            fb_uk_formula,
            fb_us_formula
        ])
        cat_idx += 1
        
    ws.update(range_name=f'A1:M{len(cat_matrix)}', values=cat_matrix, value_input_option='USER_ENTERED')
    ws.freeze(rows=1)
    print(f"Sheet '{cat}' updated with {len(cat_matrix)-1} rows & 13 columns.")

# Format headers & widths
requests = []
sheet_ids = {ws.title: ws.id for ws in sh.worksheets()}

requests.append({
    "repeatCell": {
        "range": {"sheetId": sheet_ids['All Words'], "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 13},
        "cell": {
            "userEnteredFormat": {
                "backgroundColor": cat_colors['HEADER'],
                "horizontalAlignment": "CENTER",
                "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
            }
        },
        "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)"
    }
})

for cat in ['A1', 'A2', 'B1', 'B2']:
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_ids[cat], "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 13},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": cat_colors[cat],
                    "horizontalAlignment": "CENTER",
                    "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
                }
            },
            "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)"
        }
    })

col_widths_13 = [60, 65, 150, 140, 140, 85, 85, 130, 260, 380, 200, 115, 115]
for s_title in ['All Words', 'A1', 'A2', 'B1', 'B2']:
    s_id = sheet_ids[s_title]
    for c_i, w_px in enumerate(col_widths_13):
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": s_id,
                    "dimension": "COLUMNS",
                    "startIndex": c_i,
                    "endIndex": c_i + 1
                },
                "properties": {"pixelSize": w_px},
                "fields": "pixelSize"
            }
        })
    # Center alignment for columns A, B, D, E, F, G, L, M
    for c_idx in [0, 1, 3, 4, 5, 6, 11, 12]:
        requests.append({
            "repeatCell": {
                "range": {"sheetId": s_id, "startRowIndex": 1, "endRowIndex": 3400 if s_title == 'All Words' else 1000, "startColumnIndex": c_idx, "endColumnIndex": c_idx + 1},
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment)"
            }
        })

sh.batch_update({'requests': requests})
print("Google Sheet styling successfully applied!")

# 2. Update Excel
print("Updating Excel file...")
wb = openpyxl.load_workbook('Oxford_3000_by_CEFR_Level.xlsx')
level_hex = {
    'A1': {'header': '1B5E20', 'accent': 'E8F5E9'},
    'A2': {'header': '0D47A1', 'accent': 'E3F2FD'},
    'B1': {'header': 'E65100', 'accent': 'FFF3E0'},
    'B2': {'header': 'B71C1C', 'accent': 'FFEBEE'},
    'HEADER': {'header': '263238', 'accent': 'F9FAFB'}
}
thin_border = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC')
)

def populate_excel_sheet_13(ws, rows_data, color_key):
    ws.delete_rows(1, ws.max_row + 10)
    for c_idx, h in enumerate(headers_13, start=1):
        cell = ws.cell(row=1, column=c_idx, value=h)
        cell.font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color=level_hex[color_key]['header'], fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    ws.row_dimensions[1].height = 28
    
    for r_idx, r in enumerate(rows_data, start=2):
        for c_idx in range(1, 14):
            c_val = r[c_idx - 1]
            cell = ws.cell(row=r_idx, column=c_idx, value=c_val)
            if c_idx in [1, 2, 4, 5, 6, 7, 12, 13]:
                cell.alignment = Alignment(horizontal='center')
            if r_idx % 2 == 1:
                cell.fill = PatternFill(start_color=level_hex[color_key]['accent'], fill_type='solid')
            cell.border = thin_border
            
    widths = [8, 8, 20, 18, 18, 12, 12, 18, 32, 48, 25, 16, 16]
    for c_idx, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(c_idx)].width = w

all_rows_excel = []
for r in dataset:
    fb_uk = f'=HYPERLINK("{r.get("oxford_uk_url", "")}", "🌐 Oxford UK")' if r.get('oxford_uk_url') else '-'
    fb_us = f'=HYPERLINK("{r.get("oxford_us_url", "")}", "🌐 Oxford US")' if r.get('oxford_us_url') else '-'
    all_rows_excel.append([
        r['no'], r['level'], r['word'], r['ipa_uk'], r['ipa_us'],
        r['audio_uk_formula'], r['audio_us_formula'],
        r['pos'], r['arti'], r['contoh_kalimat'], r['full_entry'],
        fb_uk, fb_us
    ])
populate_excel_sheet_13(wb['All Words'], all_rows_excel, 'HEADER')

for cat in ['A1', 'A2', 'B1', 'B2']:
    cat_rows = []
    c_idx = 1
    for r in by_level[cat]:
        fb_uk = f'=HYPERLINK("{r.get("oxford_uk_url", "")}", "🌐 Oxford UK")' if r.get('oxford_uk_url') else '-'
        fb_us = f'=HYPERLINK("{r.get("oxford_us_url", "")}", "🌐 Oxford US")' if r.get('oxford_us_url') else '-'
        cat_rows.append([
            c_idx, r['level'], r['word'], r['ipa_uk'], r['ipa_us'],
            r['audio_uk_formula'], r['audio_us_formula'],
            r['pos'], r['arti'], r['contoh_kalimat'], r['full_entry'],
            fb_uk, fb_us
        ])
        c_idx += 1
    populate_excel_sheet_13(wb[cat], cat_rows, cat)

wb.save('Oxford_3000_by_CEFR_Level.xlsx')
print("File Excel updated successfully!")

# 3. CSV
with open('Oxford_3000_All.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(headers_13)
    for r in all_rows_excel:
        writer.writerow(r)

print("[SUCCESS] All files and Google Sheets synchronized with Internal Drive and Oxford Fallback!")
