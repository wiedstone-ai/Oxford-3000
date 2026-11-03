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

# Load cleaned dataset with GDrive links
with open('oxford_3000_final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print(f"Total entries loaded: {len(dataset)}")

headers_11 = [
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
    'Full Entry'
]

by_level = {'A1': [], 'A2': [], 'B1': [], 'B2': []}
for r in dataset:
    by_level[r['level']].append(r)

# --- 1. UPDATE GOOGLE SHEET VIA API ---
CRED_PATH = r'C:\Users\LILI\OneDrive - PDK Jateng\Dokumen\widio-titip\credentials_gdrive_widio.json'
SPREADSHEET_ID = '1_l6Ojulq3jMryReGtmN1z1PtWYSkVtggDC0PpEVcjqQ'
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

creds = Credentials.from_service_account_file(CRED_PATH, scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)
print(f"Terhubung ke Google Sheet: '{sh.title}'")

# Update 'All Words'
try:
    ws_all = sh.worksheet('All Words')
    ws_all.clear()
except gspread.exceptions.WorksheetNotFound:
    ws_all = sh.add_worksheet(title='All Words', rows=3400, cols=11)

all_matrix = [headers_11]
for r in dataset:
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
        r['full_entry']
    ])

ws_all.update(range_name=f'A1:K{len(all_matrix)}', values=all_matrix, value_input_option='USER_ENTERED')
ws_all.freeze(rows=1)
print(f"Sheet 'All Words' updated with {len(all_matrix)-1} rows & 11 columns.")

# Update 'A1', 'A2', 'B1', 'B2'
for cat in ['A1', 'A2', 'B1', 'B2']:
    try:
        ws = sh.worksheet(cat)
        ws.clear()
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=cat, rows=len(by_level[cat]) + 50, cols=11)
        
    cat_matrix = [headers_11]
    cat_idx = 1
    for r in by_level[cat]:
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
            r['full_entry']
        ])
        cat_idx += 1
        
    ws.update(range_name=f'A1:K{len(cat_matrix)}', values=cat_matrix, value_input_option='USER_ENTERED')
    ws.freeze(rows=1)
    print(f"Sheet '{cat}' updated with {len(cat_matrix)-1} rows & 11 columns.")

# --- 2. UPDATE LOCAL EXCEL WORKBOOK ---
print("Updating local Excel workbook Oxford_3000_by_CEFR_Level.xlsx...")
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

def populate_excel_sheet_11(ws, rows_data, color_key):
    ws.delete_rows(1, ws.max_row + 10)
    # Header
    for c_idx, h in enumerate(headers_11, start=1):
        cell = ws.cell(row=1, column=c_idx, value=h)
        cell.font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color=level_hex[color_key]['header'], fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    ws.row_dimensions[1].height = 28
    
    # Rows
    for r_idx, r in enumerate(rows_data, start=2):
        ws.cell(row=r_idx, column=1, value=r[0]).alignment = Alignment(horizontal='center')
        ws.cell(row=r_idx, column=2, value=r[1]).alignment = Alignment(horizontal='center')
        ws.cell(row=r_idx, column=3, value=r[2])
        ws.cell(row=r_idx, column=4, value=r[3]).alignment = Alignment(horizontal='center')
        ws.cell(row=r_idx, column=5, value=r[4]).alignment = Alignment(horizontal='center')
        ws.cell(row=r_idx, column=6, value=r[5]).alignment = Alignment(horizontal='center')
        ws.cell(row=r_idx, column=7, value=r[6]).alignment = Alignment(horizontal='center')
        ws.cell(row=r_idx, column=8, value=r[7])
        ws.cell(row=r_idx, column=9, value=r[8])
        ws.cell(row=r_idx, column=10, value=r[9])
        ws.cell(row=r_idx, column=11, value=r[10])
        
        # Zebra striping
        if r_idx % 2 == 1:
            for c in range(1, 12):
                ws.cell(row=r_idx, column=c).fill = PatternFill(start_color=level_hex[color_key]['accent'], fill_type='solid')
        for c in range(1, 12):
            ws.cell(row=r_idx, column=c).border = thin_border
            
    widths = [8, 8, 20, 18, 18, 12, 12, 18, 32, 48, 25]
    for c_idx, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(c_idx)].width = w

all_rows_excel = []
for r in dataset:
    all_rows_excel.append([
        r['no'], r['level'], r['word'], r['ipa_uk'], r['ipa_us'],
        r['audio_uk_formula'], r['audio_us_formula'],
        r['pos'], r['arti'], r['contoh_kalimat'], r['full_entry']
    ])
populate_excel_sheet_11(wb['All Words'], all_rows_excel, 'HEADER')

for cat in ['A1', 'A2', 'B1', 'B2']:
    cat_rows_excel = []
    c_idx = 1
    for r in by_level[cat]:
        cat_rows_excel.append([
            c_idx, r['level'], r['word'], r['ipa_uk'], r['ipa_us'],
            r['audio_uk_formula'], r['audio_us_formula'],
            r['pos'], r['arti'], r['contoh_kalimat'], r['full_entry']
        ])
        c_idx += 1
    populate_excel_sheet_11(wb[cat], cat_rows_excel, cat)

wb.save('Oxford_3000_by_CEFR_Level.xlsx')
print("File Excel Oxford_3000_by_CEFR_Level.xlsx updated successfully!")

# --- 3. UPDATE LOCAL CSV FILES ---
with open('Oxford_3000_All.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(headers_11)
    for r in all_rows_excel:
        writer.writerow(r)

for cat in ['A1', 'A2', 'B1', 'B2']:
    with open(f'Oxford_3000_{cat}.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers_11)
        c_i = 1
        for r in by_level[cat]:
            writer.writerow([
                c_i, r['level'], r['word'], r['ipa_uk'], r['ipa_us'],
                r['audio_uk_formula'], r['audio_us_formula'],
                r['pos'], r['arti'], r['contoh_kalimat'], r['full_entry']
            ])
            c_i += 1

print("[SUCCESS] All Google Sheets and Local Files updated with Google Drive Internal Audio links!")
