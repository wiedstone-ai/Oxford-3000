import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('sheet_all_words_dump.json', 'r', encoding='utf-8') as f:
    rows = json.load(f)

header = rows[0]
print("Columns:", header)

w_idx = header.index('Word')
pos_idx = header.index('Part of Speech')
arti_idx = header.index('Arti (Bahasa Indonesia)')
lvl_idx = header.index('Level')
no_idx = header.index('No')

issues = []

for idx, r in enumerate(rows[1:], start=2):
    no = r[no_idx]
    lvl = r[lvl_idx]
    w = r[w_idx].strip()
    pos = r[pos_idx].strip()
    arti = r[arti_idx].strip()
    
    # 1. Error values
    if arti.startswith('#') or arti.startswith('='):
        issues.append({
            'row': idx, 'no': no, 'level': lvl, 'word': w, 'pos': pos, 'arti': arti,
            'issue_type': 'Formula Error / #NAME?',
            'description': f"Nilai berupa formula atau error: '{arti}'"
        })
        continue
        
    # 2. Empty or dash
    if not arti or arti in ['-', '?', 'none', 'null']:
        issues.append({
            'row': idx, 'no': no, 'level': lvl, 'word': w, 'pos': pos, 'arti': arti,
            'issue_type': 'Empty / Blank',
            'description': "Arti kosong atau tanda strip"
        })
        continue
        
    # 3. Untranslated (Arti == Word)
    w_clean = re.sub(r'[^a-zA-Z]', '', w).lower()
    arti_clean = re.sub(r'[^a-zA-Z]', '', arti).lower()
    if w_clean and arti_clean and w_clean == arti_clean:
        # Check if it's a known Indonesian loanword that is actually the same, e.g. 'radio', 'bank', 'hotel'
        loanwords = ['radio', 'hotel', 'bank', 'bus', 'film', 'gas', 'internet', 'kilo', 'kilometer', 'kopi', 'lamp', 'lemon', 'mama', 'motor', 'music', 'organ', 'papa', 'park', 'passport', 'pasta', 'pelican', 'photo', 'pizza', 'plus', 'police', 'post', 'program', 'radio', 'restoran', 'salad', 'salmon', 'sandal', 'saos', 'sauna', 'skate', 'ski', 'sofa', 'soup', 'stadium', 'studio', 'taxi', 'teh', 'tenis', 'toilet', 'tomat', 'tour', 'traktor', 'truk', 'tsunami', 'vanilla', 'video', 'virus', 'vitamin', 'volleyball', 'whisky', 'yoghurt', 'zebra', 'zoo']
        if w_clean not in loanwords:
            issues.append({
                'row': idx, 'no': no, 'level': lvl, 'word': w, 'pos': pos, 'arti': arti,
                'issue_type': 'Untranslated English',
                'description': f"Arti sama persis dengan kata bahasa Inggrisnya: '{arti}'"
            })
            continue

    # 4. Check POS context
    # E.g. If POS is exclusively 'v.' (verb), but Indonesian translation starts with 'sebuah', 'hal', 'orang' or has no verb sense
    # Or if POS is 'n.' but translation starts with 'secara', 'dengan', 'sangat' (adverb)
    if 'v.' in pos and not any(p in pos for p in ['n.', 'adj.']):
        # purely verb
        pass # We will check deeper

print(f"Total issues found: {len(issues)}")
for iss in issues[:30]:
    print(f"Row {iss['row']} | No {iss['no']} [{iss['level']}] {iss['word']} ({iss['pos']}) -> '{iss['arti']}' | {iss['issue_type']}")

with open('audit_initial_issues.json', 'w', encoding='utf-8') as f:
    json.dump(issues, f, ensure_ascii=False, indent=2)
