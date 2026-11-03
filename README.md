# The Oxford 3000™ by CEFR Level Wordlist (A1 – B2)

Kumpulan lengkap dan terstruktur dari daftar kata **The Oxford 3000™ by CEFR Level** resmi dari Oxford University Press, diperkaya dengan:
- 🇬🇧 **Transkripsi Fonetik IPA British (UK)** & 🇺🇸 **American (US)**
- 🔊 **Tautan Audio Pelafalan Asli Oxford & Google Drive Internal**
- 🇮🇩 **Terjemahan Kontekstual Bahasa Indonesia**
- 💬 **Contoh Kalimat Alami Bahasa Inggris**
- 📑 **Ekspor Lengkap:** Google Sheets, Excel (.xlsx), CSV, dan JSON

---

## 📊 Statistik Kosa Kata per Tingkat CEFR

| Level CEFR | Tingkat Kemahiran | Jumlah Kata | Persentase | Karakteristik Kosa Kata |
| :---: | :--- | :---: | :---: | :--- |
| **A1** | Beginner (Pemula Dasar) | **900** kata | 27.2% | Kosakata dasar untuk komunikasi sehari-hari |
| **A2** | Elementary (Dasar Lanjutan) | **872** kata | 26.4% | Kosakata situasi rutin, informasi pribadi/keluarga, lingkungan |
| **B1** | Intermediate (Menengah Mandiri) | **809** kata | 24.5% | Kosakata umum pekerjaan, studi, mendeskripsikan pengalaman |
| **B2** | Upper Intermediate (Menengah Atas) | **727** kata | 22.0% | Kosakata kompleks, teks akademis, ekspresi profesional |
| **TOTAL** | **A1 – B2** | **3.308** entri | **100.0%** | **Daftar Lengkap Oxford 3000** |

---

## 📋 Struktur Data (13 Kolom)

1. `No`: Nomor urut kata
2. `Level`: Tingkat kemahiran CEFR (A1, A2, B1, B2)
3. `Word`: Entri kata bahasa Inggris (*headword*)
4. `Pronunciation (UK)`: Transkripsi IPA British English
5. `Pronunciation (US)`: Transkripsi IPA American English *(ditandai `(Sama)` jika identik)*
6. `Audio UK`: Audio pelafalan British
7. `Audio US`: Audio pelafalan American
8. `Part of Speech`: Kelas kata resmi (*n., v., adj., adv., prep., dll.*)
9. `Arti (Bahasa Indonesia)`: Terjemahan bahasa Indonesia yang kontekstual dan akurat
10. `Contoh Kalimat`: Kalimat contoh penggunaan bahasa Inggris alami
11. `Full Entry`: Entri rujukan asli Oxford
12. `Oxford Fallback UK`: Tautan cadangan resmi Oxford Learner's Dictionaries (UK)
13. `Oxford Fallback US`: Tautan cadangan resmi Oxford Learner's Dictionaries (US)

---

## 📁 Struktur Berkas Repositori

```
Oxford-3000/
├── Oxford_3000_by_CEFR_Level.xlsx    # Buku kerja Excel lengkap (styling CEFR, 13 kolom)
├── Oxford_3000_All.csv               # CSV konsolidasi 3.308 entri
├── Oxford_3000_A1.csv                # CSV khusus tingkat A1
├── Oxford_3000_A2.csv                # CSV khusus tingkat A2
├── Oxford_3000_B1.csv                # CSV khusus tingkat B1
├── Oxford_3000_B2.csv                # CSV khusus tingkat B2
├── oxford_3000_final.json            # Database JSON lengkap 3.308 entri
├── oxford_player_apps_script.js      # Skrip pemutar audio in-sheet Google Apps Script
├── oxford_3000.pdf                   # Dokumen sumber resmi Oxford University Press
├── en_UK.txt                         # Kamus IPA British English
├── en_US.txt                         # Kamus IPA American English
├── sync_oxford_sheet_11cols.py       # Skrip otomatisasi sinkronisasi data
└── update_sheet_with_fallback.py     # Skrip update Google Sheets & Excel
```

---

## 🎧 Pemutar Audio In-Sheet Google Sheets
Repositori ini menyertakan `oxford_player_apps_script.js` untuk Google Sheets:
- Memutar suara langsung di panel samping (*Sidebar*) tanpa membuka tab baru di browser.
- Otomatis mendeteksi baris kata yang sedang dipilih/diklik.
- Dilengkapi pengatur kecepatan suara (`0.8x`, `1.0x`, `1.2x`).

---

## 📄 Lisensi & Sumber Data
- Daftar kata bersumber dari **The Oxford 3000™ by CEFR Level**, © Oxford University Press.
- Disusun untuk tujuan pendidikan dan pembelajaran bahasa Inggris.
