import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('oxford_3000_final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

with open('clean_corrections_map.json', 'r', encoding='utf-8') as f:
    corrections = json.load(f)

updated_count = 0
detailed_changes = []

def clean_general_artifacts(text):
    if not text:
        return text
    # Clean up dictionary abbreviations and relics
    cleaned = text
    cleaned = re.sub(r'Sl\.:\s*', '', cleaned)
    cleaned = re.sub(r'Mus\.:\s*', '', cleaned)
    cleaned = re.sub(r'Anat\.:\s*', '', cleaned)
    cleaned = re.sub(r'Nav\.:\s*', '', cleaned)
    cleaned = re.sub(r'Then\.:\s*', '', cleaned)
    cleaned = re.sub(r'-kkt\b', '', cleaned)
    cleaned = re.sub(r'-kki\b', '', cleaned)
    cleaned = re.sub(r'\s*,\s*:\s*', ', ', cleaned)
    cleaned = re.sub(r'^\s*:\s*', '', cleaned)
    cleaned = re.sub(r'\s*;\s*', ', ', cleaned)
    cleaned = re.sub(r'\s*,\s*', ', ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned.strip(',').strip()
    return cleaned

for r in dataset:
    w = r['word'].strip()
    pos = r['pos'].strip()
    entry = r.get('full_entry', '').strip()
    old_arti = r.get('arti', '').strip()
    
    w_low = w.lower()
    w_clean = re.sub(r'\d+', '', w_low)
    w_clean = re.sub(r'\(.*?\)', '', w_clean).strip()
    
    new_arti = None
    
    # 1. Match from curated corrections map
    if w_clean in corrections:
        c_val = corrections[w_clean]
        if isinstance(c_val, dict):
            # Check POS matching or sense matching
            for p_key, trans in c_val.items():
                if '(' in p_key:
                    # parenthetical sense, e.g. "n. (remaining part)"
                    sense_tag = p_key.split('(')[1].rstrip(')').lower()
                    if sense_tag in entry.lower():
                        new_arti = trans
                        break
                elif p_key == pos or p_key in pos:
                    new_arti = trans
                    break
            if not new_arti and len(c_val) > 0:
                # fallback to first entry in dict
                first_key = list(c_val.keys())[0]
                new_arti = c_val[first_key]
        else:
            new_arti = c_val
            
    # 2. If no direct match in corrections, clean up general artifacts
    if not new_arti:
        cleaned_existing = clean_general_artifacts(old_arti)
        if cleaned_existing != old_arti:
            new_arti = cleaned_existing
            
    if new_arti and new_arti != old_arti:
        detailed_changes.append({
            'row': r['no'],
            'level': r['level'],
            'word': w,
            'pos': pos,
            'entry': entry,
            'old': old_arti,
            'new': new_arti
        })
        r['arti'] = new_arti
        updated_count += 1

print(f"Total entries updated: {updated_count}")
with open('applied_translation_changes.json', 'w', encoding='utf-8') as f:
    json.dump(detailed_changes, f, ensure_ascii=False, indent=2)

with open('oxford_3000_final.json', 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("Saved updated dataset to oxford_3000_final.json successfully!")
