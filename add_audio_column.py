import os
import sys
import json
import re
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

base_dir = r'C:\Users\LILI\OneDrive - PDK Jateng\Dokumen\Oxford-3000'
json_path = os.path.join(base_dir, 'oxford_3000_enriched.json')

with open(json_path, 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print(f"Loaded {len(dataset)} records from {json_path}")

# Function to get clean word for TTS
def get_clean_tts_word(w):
    # e.g. can1 -> can, bank (money) -> bank, a, an -> a
    w_clean = re.sub(r'\d+', '', w)
    w_clean = re.sub(r'\(.*?\)', '', w_clean).strip()
    if ',' in w_clean:
        w_clean = w_clean.split(',')[0].strip()
    return w_clean

# Update dataset with audio formula and url
for r in dataset:
    tts_word = get_clean_tts_word(r['word'])
    encoded_word = urllib.parse.quote(tts_word)
    audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q={encoded_word}"
    r['audio_word'] = tts_word
    r['audio_url'] = audio_url
    r['audio_formula'] = f'=HYPERLINK("{audio_url}", "🔊 Dengar")'

# Save updated JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("Updated oxford_3000_enriched.json with audio fields.")

# 9 Columns
headers_9 = [
    'No',
    'Level',
    'Word',
    'Pronunciation',
    'Audio (Dengar)',
    'Part of Speech',
    'Arti (Bahasa Indonesia)',
    'Contoh Kalimat',
    'Full Entry'
]

# Split by level
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
print(f"Terhubung ke Google Sheet: '{sh.title}'")

cat_colors = {
    'A1': {"red": 0.11, "green": 0.37, "blue": 0.13},
    'A2': {"red": 0.05, "green": 0.28, "blue": 0.63},
    'B1': {"red": 0.90, "green": 0.32, "blue": 0.00},
    'B2': {"red": 0.72, "green": 0.11, "blue": 0.11},
    'HEADER': {"red": 0.15, "green": 0.20, "blue": 0.22}
}

# Update All Words in Google Sheet
try:
    ws_all = sh.worksheet('All Words')
    ws_all.clear()
except gspread.exceptions.WorksheetNotFound:
    ws_all = sh.add_worksheet(title='All Words', rows=3400, cols=9)

all_matrix = [headers_9]
for r in dataset:
    all_matrix.append([
        r['no'],
        r['level'],
        r['word'],
        r['pronunciation'],
        r['audio_formula'],
        r['pos'],
        r['arti'],
        r['contoh_kalimat'],
        r['full_entry']
    ])

ws_all.update(range_name=f'A1:I{len(all_matrix)}', values=all_matrix, value_input_option='USER_ENTERED')
ws_all.freeze(rows=1)
print(f"Sheet 'All Words' diperbarui dengan 9 kolom.")

# Update A1, A2, B1, B2 in Google Sheet
for cat in ['A1', 'A2', 'B1', 'B2']:
    try:
        ws = sh.worksheet(cat)
        ws.clear()
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=cat, rows=len(by_level[cat]) + 50, cols=9)
        
    cat_matrix = [headers_9]
    cat_idx = 1
    for r in by_level[cat]:
        cat_matrix.append([
            cat_idx,
            r['level'],
            r['word'],
            r['pronunciation'],
            r['audio_formula'],
            r['pos'],
            r['arti'],
            r['contoh_kalimat'],
            r['full_entry']
        ])
        cat_idx += 1
        
    ws.update(range_name=f'A1:I{len(cat_matrix)}', values=cat_matrix, value_input_option='USER_ENTERED')
    ws.freeze(rows=1)
    print(f"Sheet '{cat}' diperbarui dengan 9 kolom.")

# Format Headers & Column widths in Google Sheet
requests = []
sheet_ids = {ws.title: ws.id for ws in sh.worksheets()}

# Format All Words header
requests.append({
    "repeatCell": {
        "range": {"sheetId": sheet_ids['All Words'], "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 9},
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
            "range": {"sheetId": sheet_ids[cat], "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 9},
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

# Set Column widths for Google Sheets: [No, Level, Word, Pron, Audio, POS, Arti, Contoh, Full]
col_widths = [55, 55, 150, 130, 110, 140, 260, 380, 200]
for s_title in ['All Words', 'A1', 'A2', 'B1', 'B2']:
    s_id = sheet_ids[s_title]
    for c_i, w_px in enumerate(col_widths):
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

sh.batch_update({'requests': requests})
print("Styling Google Sheet dan lebar kolom baru berhasil diterapkan!")

# 2. Update local Excel workbook Oxford_3000_by_CEFR_Level.xlsx
excel_file = os.path.join(base_dir, 'Oxford_3000_by_CEFR_Level.xlsx')
print(f"Memperbarui file Excel lokal {excel_file}...")
wb = openpyxl.load_workbook(excel_file)

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

def populate_excel_sheet_9(ws, rows_data, color_key):
    ws.delete_rows(1, ws.max_row + 10)
    for c_idx, h in enumerate(headers_9, start=1):
        cell = ws.cell(row=1, column=c_idx, value=h)
        cell.font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color=level_hex[color_key]['header'], fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    ws.row_dimensions[1].height = 28
    
    for r_idx, r in enumerate(rows_data, start=2):
        ws.cell(row=r_idx, column=1, value=r[0]).alignment = Alignment(horizontal='center')
        ws.cell(row=r_idx, column=2, value=r[1]).alignment = Alignment(horizontal='center')
        ws.cell(row=r_idx, column=3, value=r[2])
        ws.cell(row=r_idx, column=4, value=r[3]).alignment = Alignment(horizontal='center')
        
        # Audio cell with hyperlink
        c_audio = ws.cell(row=r_idx, column=5, value="🔊 Dengar")
        c_audio.hyperlink = r[4]
        c_audio.font = Font(name='Segoe UI', color='0000FF', underline='single')
        c_audio.alignment = Alignment(horizontal='center', vertical='center')
        
        ws.cell(row=r_idx, column=6, value=r[5])
        ws.cell(row=r_idx, column=7, value=r[6])
        ws.cell(row=r_idx, column=8, value=r[7])
        ws.cell(row=r_idx, column=9, value=r[8])
        
        if r_idx % 2 == 1:
            for c in range(1, 10):
                if c != 5:
                    ws.cell(row=r_idx, column=c).fill = PatternFill(start_color=level_hex[color_key]['accent'], fill_type='solid')
        for c in range(1, 10):
            ws.cell(row=r_idx, column=c).border = thin_border
            
    widths = [8, 8, 22, 18, 14, 18, 35, 50, 25]
    for c_idx, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(c_idx)].width = w

# Update All Words in Excel
all_rows_excel = []
for r in dataset:
    all_rows_excel.append([
        r['no'], r['level'], r['word'], r['pronunciation'],
        r['audio_url'], r['pos'], r['arti'], r['contoh_kalimat'], r['full_entry']
    ])
populate_excel_sheet_9(wb['All Words'], all_rows_excel, 'HEADER')

# Update A1, A2, B1, B2 in Excel
for cat in ['A1', 'A2', 'B1', 'B2']:
    cat_rows_excel = []
    c_idx = 1
    for r in by_level[cat]:
        cat_rows_excel.append([
            c_idx, r['level'], r['word'], r['pronunciation'],
            r['audio_url'], r['pos'], r['arti'], r['contoh_kalimat'], r['full_entry']
        ])
        c_idx += 1
    populate_excel_sheet_9(wb[cat], cat_rows_excel, cat)

wb.save(excel_file)
print(f"File Excel {excel_file} berhasil diperbarui!")

# Update CSV files in Oxford-3000
import csv
csv_all = os.path.join(base_dir, 'Oxford_3000_All.csv')
with open(csv_all, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(headers_9)
    for r in all_rows_excel:
        writer.writerow(r)

for cat in ['A1', 'A2', 'B1', 'B2']:
    csv_cat = os.path.join(base_dir, f'Oxford_3000_{cat}.csv')
    with open(csv_cat, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers_9)
        c_i = 1
        for r in by_level[cat]:
            writer.writerow([
                c_i, r['level'], r['word'], r['pronunciation'],
                r['audio_url'], r['pos'], r['arti'], r['contoh_kalimat'], r['full_entry']
            ])
            c_i += 1

print("[SUCCESS] SEMUA DATA 9 KOLOM DENGAN AUDIO TELAH BERHASIL DIPERBARUI!")
