import os
import sys
import json
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = '1_l6Ojulq3jMryReGtmN1z1PtWYSkVtggDC0PpEVcjqQ'
CRED_PATH = r'C:\Users\LILI\OneDrive - PDK Jateng\Dokumen\widio-titip\credentials_gdrive_widio.json'

print(f"Menggunakan kredensial: {CRED_PATH}")
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_service_account_file(CRED_PATH, scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)
print(f"Berhasil terhubung ke spreadsheet: '{sh.title}'")

from parse_oxford import categories, pos_pattern

records_by_cat = {'A1': [], 'A2': [], 'B1': [], 'B2': []}
for cat, items in categories.items():
    idx = 1
    for item in items:
        m = pos_pattern.search(item)
        if m:
            word = item[:m.start()].strip()
            pos = item[m.start():].strip()
        else:
            word = item
            pos = ''
        records_by_cat[cat].append([idx, cat, word, pos, item])
        idx += 1

# 1. Update Sheet Ringkasan
try:
    ws_sum = sh.worksheet('Ringkasan')
    ws_sum.clear()
except gspread.exceptions.WorksheetNotFound:
    ws_sum = sh.add_worksheet(title='Ringkasan', rows=25, cols=10, index=0)

sum_rows = [
    ['', 'The Oxford 3000™ by CEFR Level Wordlist'],
    ['', 'Sumber: Oxford University Press | Total Entri: 3.308 Kata'],
    [],
    ['', 'Level CEFR', 'Jumlah Kata', 'Persentase', 'Deskripsi Tingkat Kemahiran'],
    ['', 'A1', len(categories['A1']), f"{len(categories['A1'])/3308*100:.1f}%", 'Beginner (Pemula Dasar) - Kosa kata dasar untuk kebutuhan sehari-hari'],
    ['', 'A2', len(categories['A2']), f"{len(categories['A2'])/3308*100:.1f}%", 'Elementary (Dasar Lanjutan) - Kosa kata rutin dan situasi sederhana'],
    ['', 'B1', len(categories['B1']), f"{len(categories['B1'])/3308*100:.1f}%", 'Intermediate (Menengah Mandiri) - Kosa kata topik umum, kerja, dan studi'],
    ['', 'B2', len(categories['B2']), f"{len(categories['B2'])/3308*100:.1f}%", 'Upper Intermediate (Menengah Tingkat Atas) - Kosa kata kompleks, abstrak, dan profesional'],
    ['', 'TOTAL', 3308, '100.0%', 'Daftar Lengkap Oxford 3000 per Tingkat CEFR (A1 - B2)']
]
ws_sum.update(range_name='A1:E9', values=sum_rows, value_input_option='USER_ENTERED')
print("Sheet 'Ringkasan' berhasil diperbarui.")

# 2. Update Sheets per Level (A1, A2, B1, B2)
for cat in ['A1', 'A2', 'B1', 'B2']:
    try:
        ws = sh.worksheet(cat)
        ws.clear()
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=cat, rows=len(categories[cat]) + 20, cols=5)
    
    rows = [['No', 'Level', 'Word', 'Part of Speech', 'Full Entry']] + records_by_cat[cat]
    ws.update(range_name=f'A1:E{len(rows)}', values=rows, value_input_option='USER_ENTERED')
    ws.freeze(rows=1)
    print(f"Sheet '{cat}' ({len(records_by_cat[cat])} kata) berhasil diperbarui.")

# 3. Update Sheet All Words
try:
    ws_all = sh.worksheet('All Words')
    ws_all.clear()
except gspread.exceptions.WorksheetNotFound:
    ws_all = sh.add_worksheet(title='All Words', rows=3400, cols=5)

all_rows = [['No', 'Level', 'Word', 'Part of Speech', 'Full Entry']]
g_id = 1
for cat in ['A1', 'A2', 'B1', 'B2']:
    for r in records_by_cat[cat]:
        all_rows.append([g_id, cat, r[2], r[3], r[4]])
        g_id += 1

ws_all.update(range_name=f'A1:E{len(all_rows)}', values=all_rows, value_input_option='USER_ENTERED')
ws_all.freeze(rows=1)
print(f"Sheet 'All Words' (3.308 kata) berhasil diperbarui.")

# 4. Update Sheet Side-by-Side
try:
    ws_sbs = sh.worksheet('Side-by-Side')
    ws_sbs.clear()
except gspread.exceptions.WorksheetNotFound:
    ws_sbs = sh.add_worksheet(title='Side-by-Side', rows=1000, cols=8)

max_l = max(len(categories[c]) for c in ['A1', 'A2', 'B1', 'B2'])
sbs_rows = [
    ['A1 Level (900 words)', '', 'A2 Level (872 words)', '', 'B1 Level (809 words)', '', 'B2 Level (727 words)', ''],
    ['Word', 'Part of Speech', 'Word', 'Part of Speech', 'Word', 'Part of Speech', 'Word', 'Part of Speech']
]
for i in range(max_l):
    r_item = []
    for c in ['A1', 'A2', 'B1', 'B2']:
        if i < len(records_by_cat[c]):
            r_item.extend([records_by_cat[c][i][2], records_by_cat[c][i][3]])
        else:
            r_item.extend(['', ''])
    sbs_rows.append(r_item)

ws_sbs.update(range_name=f'A1:H{len(sbs_rows)}', values=sbs_rows, value_input_option='USER_ENTERED')
ws_sbs.freeze(rows=2)
print("Sheet 'Side-by-Side' berhasil diperbarui.")

# Apply styling to Ringkasan and Header formats
requests = []
sheet_ids = {ws.title: ws.id for ws in sh.worksheets()}

# Format Ringkasan
sum_id = sheet_ids['Ringkasan']
# Merge B1:E1
requests.append({
    "mergeCells": {
        "range": {"sheetId": sum_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 1, "endColumnIndex": 5},
        "mergeType": "MERGE_ALL"
    }
})
# Merge B2:E2
requests.append({
    "mergeCells": {
        "range": {"sheetId": sum_id, "startRowIndex": 1, "endRowIndex": 2, "startColumnIndex": 1, "endColumnIndex": 5},
        "mergeType": "MERGE_ALL"
    }
})
# Style B1:E1 (Dark Blue Banner)
requests.append({
    "repeatCell": {
        "range": {"sheetId": sum_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 1, "endColumnIndex": 5},
        "cell": {
            "userEnteredFormat": {
                "backgroundColor": {"red": 0.1, "green": 0.14, "blue": 0.49},
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "MIDDLE",
                "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "fontSize": 14, "bold": True}
            }
        },
        "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,textFormat)"
    }
})
# Style B4:E4 (Table Header)
requests.append({
    "repeatCell": {
        "range": {"sheetId": sum_id, "startRowIndex": 3, "endRowIndex": 4, "startColumnIndex": 1, "endColumnIndex": 5},
        "cell": {
            "userEnteredFormat": {
                "backgroundColor": {"red": 0.22, "green": 0.28, "blue": 0.31},
                "horizontalAlignment": "CENTER",
                "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "fontSize": 10, "bold": True}
            }
        },
        "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)"
    }
})
# Style Category badges in Ringkasan
cat_colors = {
    4: {"red": 0.11, "green": 0.37, "blue": 0.13}, # A1 green
    5: {"red": 0.05, "green": 0.28, "blue": 0.63}, # A2 blue
    6: {"red": 0.90, "green": 0.32, "blue": 0.00}, # B1 orange
    7: {"red": 0.72, "green": 0.11, "blue": 0.11}  # B2 red
}
for r_idx, c_rgb in cat_colors.items():
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sum_id, "startRowIndex": r_idx, "endRowIndex": r_idx + 1, "startColumnIndex": 1, "endColumnIndex": 2},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": c_rgb,
                    "horizontalAlignment": "CENTER",
                    "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
                }
            },
            "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)"
        }
    })
# Style Total row in Ringkasan
requests.append({
    "repeatCell": {
        "range": {"sheetId": sum_id, "startRowIndex": 8, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 5},
        "cell": {
            "userEnteredFormat": {
                "backgroundColor": {"red": 0.93, "green": 0.94, "blue": 0.95},
                "textFormat": {"bold": True}
            }
        },
        "fields": "userEnteredFormat(backgroundColor,textFormat)"
    }
})

# Format Headers of Category sheets (A1, A2, B1, B2)
for cat, c_rgb in [('A1', cat_colors[4]), ('A2', cat_colors[5]), ('B1', cat_colors[6]), ('B2', cat_colors[7])]:
    c_id = sheet_ids[cat]
    requests.append({
        "repeatCell": {
            "range": {"sheetId": c_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 5},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": c_rgb,
                    "horizontalAlignment": "CENTER",
                    "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
                }
            },
            "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)"
        }
    })

# Format All Words Header
all_id = sheet_ids['All Words']
requests.append({
    "repeatCell": {
        "range": {"sheetId": all_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 5},
        "cell": {
            "userEnteredFormat": {
                "backgroundColor": {"red": 0.15, "green": 0.20, "blue": 0.22},
                "horizontalAlignment": "CENTER",
                "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
            }
        },
        "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)"
    }
})

# Format Side-by-Side Headers
sbs_id = sheet_ids['Side-by-Side']
# Level headers
for col_start, c_rgb in [(0, cat_colors[4]), (2, cat_colors[5]), (4, cat_colors[6]), (6, cat_colors[7])]:
    requests.append({
        "mergeCells": {
            "range": {"sheetId": sbs_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": col_start, "endColumnIndex": col_start + 2},
            "mergeType": "MERGE_ALL"
        }
    })
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sbs_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": col_start, "endColumnIndex": col_start + 2},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": c_rgb,
                    "horizontalAlignment": "CENTER",
                    "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
                }
            },
            "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)"
        }
    })

sh.batch_update({'requests': requests})
print("Styling dan format visual berhasil diterapkan ke seluruh sheet!")
print("\n[SUCCESS] SEMUA PROSES BERHASIL! Google Sheet kini terisi lengkap dan rapi.")
