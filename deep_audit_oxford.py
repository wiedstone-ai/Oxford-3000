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

all_words = []
for idx, r in enumerate(rows[1:], start=2):
    all_words.append({
        'row': idx,
        'no': r[no_idx],
        'level': r[lvl_idx],
        'word': r[w_idx],
        'pos': r[pos_idx],
        'arti': r[arti_idx],
        'entry': r[entry_idx]
    })

# Check specific multi-meaning words or homonyms
print("--- AUDIT HOMONYMS & POS CONTEXT ---")
homonyms_to_check = [
    'can', 'may', 'will', 'like', 'close', 'lead', 'wind', 'tear', 'present', 
    'record', 'object', 'fine', 'well', 'kind', 'match', 'park', 'ring', 
    'watch', 'spring', 'fall', 'left', 'right', 'flat', 'light', 'train',
    'bank', 'bear', 'date', 'fair', 'fly', 'lie', 'point', 'rock', 'rose',
    'sign', 'stick', 'trip', 'wave', 'board', 'book', 'box', 'cross', 'fast',
    'hard', 'last', 'mean', 'miss', 'play', 'rest', 'second', 'sound', 'star'
]

homonym_reports = []
for item in all_words:
    clean_w = re.sub(r'\d+', '', item['word']).strip().lower()
    clean_w = re.sub(r'\(.*?\)', '', clean_w).strip()
    if clean_w in homonyms_to_check:
        homonym_reports.append(item)

print(f"Found {len(homonym_reports)} homonym entries in Oxford 3000:")
for h in homonym_reports:
    print(f"Row {h['row']:4d} | No {h['no']} [{h['level']}] {h['entry']:<30} -> Arti: '{h['arti']}'")

with open('homonym_audit.json', 'w', encoding='utf-8') as f:
    json.dump(homonym_reports, f, ensure_ascii=False, indent=2)
