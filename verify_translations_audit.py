import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('oxford_3000_final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

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

remaining_issues = []

for r in dataset:
    w = r['word'].strip()
    pos = r['pos'].strip()
    arti = r.get('arti', '').strip()
    entry = r.get('full_entry', '').strip()
    
    # 1. Formula / Error
    if arti.startswith('=') or arti.startswith('#'):
        remaining_issues.append((w, pos, arti, "Formula error"))
    # 2. Blank
    if not arti or arti in ['-', '?', 'none', 'null']:
        remaining_issues.append((w, pos, arti, "Blank arti"))
    # 3. Junk
    for jp in junk_patterns:
        if re.search(jp, arti, re.IGNORECASE):
            remaining_issues.append((w, pos, arti, f"Junk pattern: {jp}"))
            break
    # 4. Untranslated
    w_clean = re.sub(r'[^a-zA-Z]', '', w).lower()
    arti_clean = re.sub(r'[^a-zA-Z]', '', arti).lower()
    if w_clean and arti_clean and w_clean == arti_clean:
        if w_clean not in valid_same_spelling:
            remaining_issues.append((w, pos, arti, "Untranslated"))

print(f"Total remaining issues after audit & fix: {len(remaining_issues)}")
for iss in remaining_issues:
    print(iss)
