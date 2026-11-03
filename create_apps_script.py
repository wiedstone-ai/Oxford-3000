import json

with open('Oxford_3000_All.csv', 'r', encoding='utf-8') as f:
    lines = [line.strip().split(',') for line in f if line.strip()]

# Let's load the parsed records from parse_oxford
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

js_code = """/**
 * Google Apps Script untuk mengisi Google Sheet Oxford 3000 by CEFR Level
 * 
 * CARA MENGGUNAKAN:
 * 1. Buka spreadsheet: https://docs.google.com/spreadsheets/d/1_l6Ojulq3jMryReGtmN1z1PtWYSkVtggDC0PpEVcjqQ
 * 2. Klik menu: Extensions > Apps Script
 * 3. Hapus kode default (jika ada), lalu copy-paste seluruh isi file ini ke editor
 * 4. Klik ikon Save (Disket), lalu pilih fungsi 'populateOxford3000' dan klik 'Run'
 * 5. Berikan izin (Authorize) jika diminta. Selesai!
 */

function populateOxford3000() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  const colors = {
    'A1': '#1B5E20',
    'A2': '#0D47A1',
    'B1': '#E65100',
    'B2': '#B71C1C',
    'HEADER': '#263238',
    'GRAY': '#ECEFF1'
  };

  const dataByCat = """ + json.dumps(records_by_cat, ensure_ascii=False) + """;

  // 1. Create Summary Sheet
  let sumSheet = ss.getSheetByName('Ringkasan');
  if (!sumSheet) {
    sumSheet = ss.insertSheet('Ringkasan', 0);
  } else {
    sumSheet.clear();
  }
  
  sumSheet.appendRow(['', 'The Oxford 3000™ by CEFR Level Wordlist']);
  sumSheet.appendRow(['', 'Sumber: Oxford University Press | Total: 3.308 Kata']);
  sumSheet.appendRow([]);
  sumSheet.appendRow(['', 'Level CEFR', 'Jumlah Kata', 'Persentase', 'Deskripsi Tingkat Kemahiran']);
  
  const desc = {
    'A1': 'Beginner (Pemula Dasar) - Kosa kata dasar untuk kebutuhan sehari-hari',
    'A2': 'Elementary (Dasar Lanjutan) - Kosa kata rutin dan situasi sederhana',
    'B1': 'Intermediate (Menengah Mandiri) - Kosa kata topik umum, kerja, dan studi',
    'B2': 'Upper Intermediate (Menengah Atas) - Kosa kata kompleks, abstrak, dan profesional'
  };
  
  let totalWords = 0;
  for (let cat of ['A1', 'A2', 'B1', 'B2']) {
    totalWords += dataByCat[cat].length;
  }

  for (let cat of ['A1', 'A2', 'B1', 'B2']) {
    let count = dataByCat[cat].length;
    let pct = (count / totalWords * 100).toFixed(1) + '%';
    sumSheet.appendRow(['', cat, count, pct, desc[cat]]);
  }
  sumSheet.appendRow(['', 'TOTAL', totalWords, '100.0%', 'Daftar Lengkap Oxford 3000 per Tingkat CEFR']);

  // Format Summary
  sumSheet.getRange('B1:E1').merge().setBackground('#1A237E').setFontColor('#FFFFFF').setFontSize(14).setFontWeight('bold').setHorizontalAlignment('center');
  sumSheet.getRange('B2:E2').merge().setFontSize(10).setFontStyle('italic').setFontColor('#555555').setHorizontalAlignment('center');
  sumSheet.getRange('B4:E4').setBackground('#37474F').setFontColor('#FFFFFF').setFontWeight('bold').setHorizontalAlignment('center');
  sumSheet.getRange('B5:E8').setHorizontalAlignment('center');
  sumSheet.getRange('E5:E8').setHorizontalAlignment('left');
  sumSheet.getRange('B9:E9').setBackground('#ECEFF1').setFontWeight('bold').setHorizontalAlignment('center');

  // Format Category Colors in Summary
  sumSheet.getRange('B5').setBackground(colors['A1']).setFontColor('#FFFFFF').setFontWeight('bold');
  sumSheet.getRange('B6').setBackground(colors['A2']).setFontColor('#FFFFFF').setFontWeight('bold');
  sumSheet.getRange('B7').setBackground(colors['B1']).setFontColor('#FFFFFF').setFontWeight('bold');
  sumSheet.getRange('B8').setBackground(colors['B2']).setFontColor('#FFFFFF').setFontWeight('bold');
  sumSheet.autoResizeColumns(2, 4);

  // 2. Individual Category Sheets
  for (let cat of ['A1', 'A2', 'B1', 'B2']) {
    let sheet = ss.getSheetByName(cat);
    if (!sheet) {
      sheet = ss.insertSheet(cat);
    } else {
      sheet.clear();
    }
    
    const rows = [['No', 'Level', 'Word', 'Part of Speech', 'Full Entry']];
    for (let r of dataByCat[cat]) {
      rows.push(r);
    }
    
    sheet.getRange(1, 1, rows.length, 5).setValues(rows);
    sheet.getRange(1, 1, 1, 5).setBackground(colors[cat]).setFontColor('#FFFFFF').setFontWeight('bold').setHorizontalAlignment('center');
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, 5);
  }

  // 3. All Words Sheet
  let allSheet = ss.getSheetByName('All Words');
  if (!allSheet) {
    allSheet = ss.insertSheet('All Words');
  } else {
    allSheet.clear();
  }
  
  const allRows = [['No', 'Level', 'Word', 'Part of Speech', 'Full Entry']];
  let gId = 1;
  for (let cat of ['A1', 'A2', 'B1', 'B2']) {
    for (let r of dataByCat[cat]) {
      allRows.push([gId, cat, r[2], r[3], r[4]]);
      gId++;
    }
  }
  allSheet.getRange(1, 1, allRows.length, 5).setValues(allRows);
  allSheet.getRange(1, 1, 1, 5).setBackground(colors['HEADER']).setFontColor('#FFFFFF').setFontWeight('bold').setHorizontalAlignment('center');
  allSheet.setFrozenRows(1);
  allSheet.autoResizeColumns(1, 5);

  SpreadsheetApp.flush();
}
"""

with open('google_apps_script.js', 'w', encoding='utf-8') as f:
    f.write(js_code)

print("google_apps_script.js generated successfully! Size:", len(js_code))
