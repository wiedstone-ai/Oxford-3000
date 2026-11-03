import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('sheet_all_words_dump.json', 'r', encoding='utf-8') as f:
    rows = json.load(f)

header = rows[0]
w_idx = header.index('Word')
pos_idx = header.index('Part of Speech')
arti_idx = header.index('Arti (Bahasa Indonesia)')
lvl_idx = header.index('Level')
no_idx = header.index('No')
entry_idx = header.index('Full Entry')

all_issues = []

# Known valid Indonesian words that match English spelling
valid_same_spelling = {
    'april', 'dvd', 'museum', 'november', 'piano', 'september', 'radio', 
    'hotel', 'bank', 'bus', 'film', 'gas', 'internet', 'kilo', 'kilometer', 
    'lemon', 'motor', 'organ', 'passport', 'pasta', 'photo', 'pizza', 
    'police', 'post', 'program', 'salad', 'salmon', 'sandal', 'sauna', 
    'skate', 'ski', 'sofa', 'soup', 'stadium', 'studio', 'taxi', 'tennis', 
    'toilet', 'tour', 'tsunami', 'vanilla', 'video', 'virus', 'vitamin', 
    'volleyball', 'whisky', 'yoghurt', 'zebra', 'zoo', 'cd', 'tv', 'ok'
}

junk_patterns = [
    r'Sl\.:', r'Mus\.:', r'ngak - ngik-nguk', r'-kkt', r'-kki', r':\s*[a-z]+-[a-z]+',
    r'lead-pipe', r'potlot', r'beruang\.-kkt', r'#NAME\?', r'#ERROR\!', r'#VALUE\!', r'#REF\!'
]

for idx, r in enumerate(rows[1:], start=2):
    no = r[no_idx]
    lvl = r[lvl_idx]
    w = r[w_idx].strip()
    pos = r[pos_idx].strip()
    arti = r[arti_idx].strip()
    entry = r[entry_idx].strip()
    
    reasons = []
    
    # 1. Formula / Error
    if arti.startswith('=') or arti.startswith('#'):
        reasons.append("Formula Error (#NAME? / =...)")
        
    # 2. Blank
    if not arti or arti in ['-', '?', 'none', 'null']:
        reasons.append("Arti kosong / tidak ada")
        
    # 3. Dictionary junk / raw regex tags
    for jp in junk_patterns:
        if re.search(jp, arti, re.IGNORECASE):
            reasons.append(f"Terdapat teks kamus mentah/rusak ('{jp}')")
            break
            
    # 4. Untranslated English
    w_clean = re.sub(r'[^a-zA-Z]', '', w).lower()
    arti_clean = re.sub(r'[^a-zA-Z]', '', arti).lower()
    if w_clean and arti_clean and w_clean == arti_clean:
        if w_clean not in valid_same_spelling:
            reasons.append(f"Belum diterjemahkan (masih bahasa Inggris: '{arti}')")
            
    # 5. Homonym / Specific sense mismatch
    # Check parenthetical sense in entry, e.g. "bear (deal with) v."
    m_sense = re.search(r'\((.*?)\)', entry)
    if m_sense:
        sense = m_sense.group(1).lower()
        if 'deal with' in sense and 'beruang' in arti.lower():
            reasons.append(f"Konteks kata tidak sesuai ('{entry}'): bear (deal with) v. diterjemahkan sebagai 'beruang' (seharusnya: menahan, menanggung)")
        elif 'river' in sense and not any(k in arti.lower() for k in ['sungai', 'tepi', 'bantaran']):
            reasons.append(f"Konteks kata tidak sesuai ('{entry}'): bank (river) harusnya bermakna tepi/bantaran sungai")
        elif 'taking time' in sense and not any(k in arti.lower() for k in ['berlangsung', 'bertahan']):
            reasons.append(f"Konteks kata tidak sesuai ('{entry}'): last (taking time) harusnya bermakna bertahan/berlangsung")
        elif 'sleep' in sense and 'sisa' in arti.lower() and not any(k in arti.lower() for k in ['istirahat', 'tidur']):
            reasons.append(f"Konteks kata tidak sesuai ('{entry}'): rest (sleep) harusnya bermakna istirahat")
        elif 'remaining' in sense and 'istirahat' in arti.lower() and not any(k in arti.lower() for k in ['sisa']):
            reasons.append(f"Konteks kata tidak sesuai ('{entry}'): rest (remaining) harusnya bermakna sisa/bagian tersisa")
        elif 'animal' in sense and 'memikul' in arti.lower():
            reasons.append(f"Konteks kata tidak sesuai ('{entry}'): bear (animal) tercampur makna kata kerja memikul")
        elif 'caring' in sense and 'jenis' in arti.lower() and not any(k in arti.lower() for k in ['baik', 'ramah']):
            reasons.append(f"Konteks kata tidak sesuai ('{entry}'): kind (caring) harusnya bermakna baik hati/ramah")
        elif 'type' in sense and 'ramah' in arti.lower() and not any(k in arti.lower() for k in ['jenis', 'macam']):
            reasons.append(f"Konteks kata tidak sesuai ('{entry}'): kind (type) harusnya bermakna jenis/macam")
            
    # Specific known mistranslations from audit
    if w == 'lead' and 'timah' in arti and 'memimpin' not in arti and 'v.' in pos:
        reasons.append("Konteks lead v. salah (diterjemahkan timah, seharusnya memimpin)")
    if w == 'wind' and 'v.' in pos and arti == 'angin':
        reasons.append("Konteks wind v. salah (diterjemahkan angin, seharusnya memutar/melilit)")
    if w == 'tear' and 'v.' in pos and 'air mata' in arti and 'robek' not in arti:
        reasons.append("Konteks tear v. salah (diterjemahkan air mata, seharusnya merobek/menyobek)")
    if w == 'trip' and 'v.' in pos and 'perjalanan' in arti and 'sandung' not in arti:
        reasons.append("Konteks trip v. salah (diterjemahkan perjalanan, seharusnya tersandung/menjegal)")
    if w == 'book' and 'v.' in pos and 'memesan' not in arti:
        reasons.append("Konteks book v. salah (seharusnya memesan tiket/tempat)")
    if w == 'cross' and 'Rel' in arti:
        reasons.append("Terdapat kata 'Rel' yang aneh untuk kata cross")
    if w == 'fair' and 'pekan raya' in arti and 'adj.' in pos:
        reasons.append("Konteks fair adj. salah (diterjemahkan pekan raya, seharusnya adil/wajar)")
    if w == 'stick' and 'v.' in pos and 'tongkat' in arti and 'tempel' not in arti:
        reasons.append("Konteks stick v. salah (diterjemahkan tongkat, seharusnya menempelkan/menusukkan)")
    if w == 'spring' and 'v.' in pos and 'musim semi' in arti and 'lompat' not in arti:
        reasons.append("Konteks spring v. salah (diterjemahkan musim semi, seharusnya melompat/memantul)")
    if w == 'board' and 'v.' in pos and 'papan' in arti and 'naik' not in arti:
        reasons.append("Konteks board v. salah (diterjemahkan papan, seharusnya menaiki/menumpang kapal/pesawat)")

    if reasons:
        all_issues.append({
            'row': idx,
            'no': no,
            'level': lvl,
            'word': w,
            'pos': pos,
            'entry': entry,
            'arti_current': arti,
            'reasons': reasons
        })

print(f"Total entries with translation issues identified: {len(all_issues)}")
with open('all_translation_issues.json', 'w', encoding='utf-8') as f:
    json.dump(all_issues, f, ensure_ascii=False, indent=2)

print("Saved to all_translation_issues.json successfully!")
