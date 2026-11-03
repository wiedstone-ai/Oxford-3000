import fitz
import re
import csv
import json
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 1. Parse PDF
doc = fitz.open('oxford_3000.pdf')
all_raw_lines = []

for pno, page in enumerate(doc):
    blocks = page.get_text('blocks')
    valid_blocks = [b for b in blocks if not (b[1] > 800 or (pno == 0 and b[1] < 100))]
    valid_blocks.sort(key=lambda b: (int(round(b[0] / 100)), b[1]))
    for b in valid_blocks:
        for l in b[4].split('\n'):
            l = l.strip().replace('\xa0', ' ').replace('\u2019', "'")
            if l:
                all_raw_lines.append((pno + 1, l))

# Merge wrapped lines
merged_lines = []
i = 0
while i < len(all_raw_lines):
    pno, line = all_raw_lines[i]
    if i + 1 < len(all_raw_lines):
        p_next, next_line = all_raw_lines[i + 1]
        if line.endswith(',') or line.endswith('/') or line.endswith('-') or next_line in ['adj.', 'number', 'v.', 'n.', 'adv.', 'pron.', 'article']:
            merged_lines.append((pno, line + ("" if line.endswith('/') else " ") + next_line))
            i += 2
            continue
    merged_lines.append((pno, line))
    i += 1

# Group by category
categories = {'A1': [], 'A2': [], 'B1': [], 'B2': []}
current_cat = None

for pno, line in merged_lines:
    if line in ['A1', 'A2', 'B1', 'B2']:
        current_cat = line
    elif current_cat:
        categories[current_cat].append(line)

pos_pattern = re.compile(r'\s+(adj\.|adv\.|conj\.|det\.|det\./pron\.|det\./adj\.|det\./number|exclam\.|n\.|number|prep\.|prep\./adv\.|pron\.|v\.|modal\s+v\.|auxiliary\s+v\.|indefinite\s+article|definite\s+article)')

parsed_data = []
global_idx = 1
for cat, items in categories.items():
    cat_idx = 1
    for item in items:
        m = pos_pattern.search(item)
        if m:
            word = item[:m.start()].strip()
            pos = item[m.start():].strip()
        else:
            word = item
            pos = ''
        parsed_data.append({
            'global_id': global_idx,
            'cat_id': cat_idx,
            'level': cat,
            'word': word,
            'pos': pos,
            'full_entry': item
        })
        global_idx += 1
        cat_idx += 1

print(f"Total parsed records: {len(parsed_data)}")

# 2. Export CSVs
# Consolidated CSV
with open('Oxford_3000_All.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['No', 'Level', 'Word', 'Part of Speech', 'Full Entry'])
    for r in parsed_data:
        writer.writerow([r['global_id'], r['level'], r['word'], r['pos'], r['full_entry']])

# Per-level CSVs
for cat in ['A1', 'A2', 'B1', 'B2']:
    with open(f'Oxford_3000_{cat}.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['No', 'Level', 'Word', 'Part of Speech', 'Full Entry'])
        for r in parsed_data:
            if r['level'] == cat:
                writer.writerow([r['cat_id'], r['level'], r['word'], r['pos'], r['full_entry']])

# Side-by-Side CSV
max_len = max(len(categories[cat]) for cat in ['A1', 'A2', 'B1', 'B2'])
cat_records = {cat: [r for r in parsed_data if r['level'] == cat] for cat in ['A1', 'A2', 'B1', 'B2']}

with open('Oxford_3000_Side_by_Side.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'A1 Word', 'A1 Part of Speech',
        'A2 Word', 'A2 Part of Speech',
        'B1 Word', 'B1 Part of Speech',
        'B2 Word', 'B2 Part of Speech'
    ])
    for i in range(max_len):
        row = []
        for cat in ['A1', 'A2', 'B1', 'B2']:
            if i < len(cat_records[cat]):
                row.extend([cat_records[cat][i]['word'], cat_records[cat][i]['pos']])
            else:
                row.extend(['', ''])
        writer.writerow(row)

# 3. Create Excel Workbook with openpyxl
wb = openpyxl.Workbook()
# remove default sheet
wb.remove(wb.active)

# Color palettes
level_colors = {
    'A1': {'header': '1B5E20', 'accent': 'E8F5E9', 'badge': '4CAF50'}, # Green
    'A2': {'header': '0D47A1', 'accent': 'E3F2FD', 'badge': '2196F3'}, # Blue
    'B1': {'header': 'E65100', 'accent': 'FFF3E0', 'badge': 'FF9800'}, # Orange
    'B2': {'header': 'B71C1C', 'accent': 'FFEBEE', 'badge': 'F44336'}, # Red
    'MAIN': {'header': '263238', 'accent': 'ECEFF1', 'badge': '455A64'} # Blue grey
}

thin_border = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC')
)

# Sheet 1: Summary (Ringkasan)
ws_sum = wb.create_sheet(title='Ringkasan')
ws_sum.views.sheetView[0].showGridLines = True

ws_sum.column_dimensions['A'].width = 6
ws_sum.column_dimensions['B'].width = 18
ws_sum.column_dimensions['C'].width = 18
ws_sum.column_dimensions['D'].width = 22
ws_sum.column_dimensions['E'].width = 45

# Title
ws_sum.merge_cells('B2:E2')
title_cell = ws_sum['B2']
title_cell.value = "The Oxford 3000™ by CEFR Level Wordlist"
title_cell.font = Font(name='Segoe UI', size=16, bold=True, color='FFFFFF')
title_cell.fill = PatternFill(start_color='1A237E', end_color='1A237E', fill_type='solid')
title_cell.alignment = Alignment(horizontal='center', vertical='center')
ws_sum.row_dimensions[2].height = 40

ws_sum.merge_cells('B3:E3')
sub_cell = ws_sum['B3']
sub_cell.value = "Sumber: Oxford University Press (A1 - B2 Level) | Total Entri: 3.308 Kata"
sub_cell.font = Font(name='Segoe UI', size=11, italic=True, color='555555')
sub_cell.alignment = Alignment(horizontal='center', vertical='center')
ws_sum.row_dimensions[3].height = 25

# Summary Table Header
headers_sum = ['Level CEFR', 'Jumlah Kata', 'Persentase', 'Deskripsi Tingkat Kemahiran']
for col_idx, h in enumerate(headers_sum, start=2):
    cell = ws_sum.cell(row=5, column=col_idx, value=h)
    cell.font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
    cell.fill = PatternFill(start_color='37474F', end_color='37474F', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border = thin_border
ws_sum.row_dimensions[5].height = 28

descriptions = {
    'A1': 'Beginner (Pemula Dasar) - Kosa kata dasar untuk kebutuhan sehari-hari',
    'A2': 'Elementary (Dasar Lanjutan) - Kosa kata rutin dan situasi sederhana',
    'B1': 'Intermediate (Menengah Mandiri) - Kosa kata topik umum, kerja, dan studi',
    'B2': 'Upper Intermediate (Menengah Tingkat Atas) - Kosa kata kompleks, abstrak, dan profesional'
}

row_idx = 6
for cat in ['A1', 'A2', 'B1', 'B2']:
    cnt = len(categories[cat])
    pct = cnt / len(parsed_data)
    
    c_cat = ws_sum.cell(row=row_idx, column=2, value=cat)
    c_cat.font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
    c_cat.fill = PatternFill(start_color=level_colors[cat]['header'], fill_type='solid')
    c_cat.alignment = Alignment(horizontal='center', vertical='center')
    c_cat.border = thin_border
    
    c_cnt = ws_sum.cell(row=row_idx, column=3, value=cnt)
    c_cnt.font = Font(name='Segoe UI', size=11, bold=True)
    c_cnt.alignment = Alignment(horizontal='right', vertical='center')
    c_cnt.number_format = '#,##0'
    c_cnt.border = thin_border
    
    c_pct = ws_sum.cell(row=row_idx, column=4, value=pct)
    c_pct.font = Font(name='Segoe UI', size=11)
    c_pct.alignment = Alignment(horizontal='right', vertical='center')
    c_pct.number_format = '0.0%'
    c_pct.border = thin_border
    
    c_desc = ws_sum.cell(row=row_idx, column=5, value=descriptions[cat])
    c_desc.font = Font(name='Segoe UI', size=10)
    c_desc.alignment = Alignment(horizontal='left', vertical='center')
    c_desc.border = thin_border
    
    ws_sum.row_dimensions[row_idx].height = 24
    row_idx += 1

# Total Row
c_t1 = ws_sum.cell(row=row_idx, column=2, value="TOTAL")
c_t1.font = Font(name='Segoe UI', size=11, bold=True)
c_t1.alignment = Alignment(horizontal='center', vertical='center')
c_t1.border = thin_border
c_t1.fill = PatternFill(start_color='ECEFF1', fill_type='solid')

c_t2 = ws_sum.cell(row=row_idx, column=3, value=len(parsed_data))
c_t2.font = Font(name='Segoe UI', size=11, bold=True)
c_t2.alignment = Alignment(horizontal='right', vertical='center')
c_t2.number_format = '#,##0'
c_t2.border = thin_border
c_t2.fill = PatternFill(start_color='ECEFF1', fill_type='solid')

c_t3 = ws_sum.cell(row=row_idx, column=4, value=1.0)
c_t3.font = Font(name='Segoe UI', size=11, bold=True)
c_t3.alignment = Alignment(horizontal='right', vertical='center')
c_t3.number_format = '0.0%'
c_t3.border = thin_border
c_t3.fill = PatternFill(start_color='ECEFF1', fill_type='solid')

c_t4 = ws_sum.cell(row=row_idx, column=5, value="Daftar Lengkap Oxford 3000 per Tingkat CEFR")
c_t4.font = Font(name='Segoe UI', size=10, italic=True)
c_t4.border = thin_border
c_t4.fill = PatternFill(start_color='ECEFF1', fill_type='solid')
ws_sum.row_dimensions[row_idx].height = 26

# Sheet 2: All Words (Consolidated)
ws_all = wb.create_sheet(title='All Words')
ws_all.views.sheetView[0].showGridLines = True
headers_all = ['No', 'Level', 'Word', 'Part of Speech', 'Full Entry']
for c_idx, h in enumerate(headers_all, start=1):
    c = ws_all.cell(row=1, column=c_idx, value=h)
    c.font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
    c.fill = PatternFill(start_color='263238', fill_type='solid')
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = thin_border
ws_all.row_dimensions[1].height = 28

for r_idx, r in enumerate(parsed_data, start=2):
    ws_all.cell(row=r_idx, column=1, value=r['global_id']).alignment = Alignment(horizontal='center')
    lvl_cell = ws_all.cell(row=r_idx, column=2, value=r['level'])
    lvl_cell.alignment = Alignment(horizontal='center')
    lvl_cell.font = Font(name='Segoe UI', bold=True)
    
    ws_all.cell(row=r_idx, column=3, value=r['word'])
    ws_all.cell(row=r_idx, column=4, value=r['pos'])
    ws_all.cell(row=r_idx, column=5, value=r['full_entry'])
    
    # Zebra striping
    if r_idx % 2 == 1:
        for c in range(1, 6):
            ws_all.cell(row=r_idx, column=c).fill = PatternFill(start_color='F9FAFB', fill_type='solid')
    for c in range(1, 6):
        ws_all.cell(row=r_idx, column=c).border = thin_border

ws_all.column_dimensions['A'].width = 8
ws_all.column_dimensions['B'].width = 10
ws_all.column_dimensions['C'].width = 30
ws_all.column_dimensions['D'].width = 25
ws_all.column_dimensions['E'].width = 35

# Sheet 3-6: Individual Tabs per Level
for cat in ['A1', 'A2', 'B1', 'B2']:
    ws_cat = wb.create_sheet(title=cat)
    ws_cat.views.sheetView[0].showGridLines = True
    color_info = level_colors[cat]
    
    headers_cat = ['No', 'Level', 'Word', 'Part of Speech', 'Full Entry']
    for c_idx, h in enumerate(headers_cat, start=1):
        c = ws_cat.cell(row=1, column=c_idx, value=h)
        c.font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
        c.fill = PatternFill(start_color=color_info['header'], fill_type='solid')
        c.alignment = Alignment(horizontal='center', vertical='center')
        c.border = thin_border
    ws_cat.row_dimensions[1].height = 28
    
    cat_rows = [r for r in parsed_data if r['level'] == cat]
    for r_idx, r in enumerate(cat_rows, start=2):
        ws_cat.cell(row=r_idx, column=1, value=r['cat_id']).alignment = Alignment(horizontal='center')
        lvl_cell = ws_cat.cell(row=r_idx, column=2, value=r['level'])
        lvl_cell.alignment = Alignment(horizontal='center')
        lvl_cell.font = Font(name='Segoe UI', bold=True)
        
        ws_cat.cell(row=r_idx, column=3, value=r['word'])
        ws_cat.cell(row=r_idx, column=4, value=r['pos'])
        ws_cat.cell(row=r_idx, column=5, value=r['full_entry'])
        
        if r_idx % 2 == 1:
            for c in range(1, 6):
                ws_cat.cell(row=r_idx, column=c).fill = PatternFill(start_color=color_info['accent'], fill_type='solid')
        for c in range(1, 6):
            ws_cat.cell(row=r_idx, column=c).border = thin_border
            
    ws_cat.column_dimensions['A'].width = 8
    ws_cat.column_dimensions['B'].width = 10
    ws_cat.column_dimensions['C'].width = 30
    ws_cat.column_dimensions['D'].width = 25
    ws_cat.column_dimensions['E'].width = 35

# Sheet 7: Side-by-Side Comparison
ws_sbs = wb.create_sheet(title='Side-by-Side')
ws_sbs.views.sheetView[0].showGridLines = True

# Top Header (merged level titles)
level_cols_start = {'A1': 1, 'A2': 3, 'B1': 5, 'B2': 7}
for cat, start_col in level_cols_start.items():
    ws_sbs.merge_cells(start_row=1, start_column=start_col, end_row=1, end_column=start_col + 1)
    cell = ws_sbs.cell(row=1, column=start_col, value=f"{cat} Level ({len(categories[cat])} words)")
    cell.font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
    cell.fill = PatternFill(start_color=level_colors[cat]['header'], fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border = thin_border
    ws_sbs.cell(row=1, column=start_col + 1).border = thin_border
ws_sbs.row_dimensions[1].height = 26

# Sub Header: Word | POS
subheaders = ['Word', 'Part of Speech', 'Word', 'Part of Speech', 'Word', 'Part of Speech', 'Word', 'Part of Speech']
for c_idx, sh in enumerate(subheaders, start=1):
    c = ws_sbs.cell(row=2, column=c_idx, value=sh)
    c.font = Font(name='Segoe UI', size=10, bold=True, color='333333')
    c.fill = PatternFill(start_color='E0E0E0', fill_type='solid')
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = thin_border
ws_sbs.row_dimensions[2].height = 22

for i in range(max_len):
    r_num = i + 3
    for cat, start_col in level_cols_start.items():
        if i < len(cat_records[cat]):
            w = cat_records[cat][i]['word']
            p = cat_records[cat][i]['pos']
        else:
            w = ''
            p = ''
        c1 = ws_sbs.cell(row=r_num, column=start_col, value=w)
        c2 = ws_sbs.cell(row=r_num, column=start_col + 1, value=p)
        c1.border = thin_border
        c2.border = thin_border
        if r_num % 2 == 1:
            c1.fill = PatternFill(start_color='FAFAFA', fill_type='solid')
            c2.fill = PatternFill(start_color='FAFAFA', fill_type='solid')

for col_idx in [1, 3, 5, 7]:
    ws_sbs.column_dimensions[get_column_letter(col_idx)].width = 25
for col_idx in [2, 4, 6, 8]:
    ws_sbs.column_dimensions[get_column_letter(col_idx)].width = 18

excel_path = 'Oxford_3000_by_CEFR_Level.xlsx'
wb.save(excel_path)
print(f"Successfully generated Excel workbook: {excel_path}")
