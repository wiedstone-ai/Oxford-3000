import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load current uk_us dataset
with open('oxford_3000_uk_us.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def clean_ipa(ipa_str):
    if not ipa_str:
        return ""
    # strip all slashes, spaces, brackets
    cleaned = ipa_str.strip()
    while cleaned.startswith('/') or cleaned.startswith('\\'):
        cleaned = cleaned[1:]
    while cleaned.endswith('/') or cleaned.endswith('\\'):
        cleaned = cleaned[:-1]
    cleaned = cleaned.strip()
    return cleaned

cleaned_records = []
same_count = 0
diff_count = 0

for r in data:
    word = r.get('word', '').strip()
    pos = r.get('pos', '').strip()
    level = r.get('level', '').strip()
    arti = r.get('arti', '').strip()
    contoh = r.get('contoh_kalimat', '').strip()
    full_entry = r.get('full_entry', '').strip()
    
    raw_uk = r.get('ipa_uk', '')
    raw_us = r.get('ipa_us', '')
    
    clean_uk = clean_ipa(raw_uk)
    clean_us = clean_ipa(raw_us)
    
    # If raw_us was "(Sama)", compare with fallback or check
    if raw_us == "(Sama)":
        is_same = True
        clean_us = clean_uk
    elif clean_uk and clean_us and clean_uk == clean_us:
        is_same = True
    else:
        is_same = False
        
    display_uk = f"/{clean_uk}/" if clean_uk else "-"
    if is_same:
        display_us = "(Sama)"
        same_count += 1
    else:
        display_us = f"/{clean_us}/" if clean_us else "-"
        diff_count += 1
        
    audio_uk = r.get('audio_oxford_uk') or f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en-gb&q={word}"
    audio_us = r.get('audio_oxford_us') or f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en-us&q={word}"
    
    audio_uk_formula = f'=HYPERLINK("{audio_uk}", "🔊 UK")'
    audio_us_formula = f'=HYPERLINK("{audio_us}", "🔊 US")'
    
    rec = {
        'no': r.get('no'),
        'level': level,
        'word': word,
        'ipa_uk': display_uk,
        'ipa_us': display_us,
        'is_ipa_same': is_same,
        'audio_uk_url': audio_uk,
        'audio_us_url': audio_us,
        'audio_uk_formula': audio_uk_formula,
        'audio_us_formula': audio_us_formula,
        'pos': pos,
        'arti': arti,
        'contoh_kalimat': contoh,
        'full_entry': full_entry
    }
    cleaned_records.append(rec)

print(f"Total processed: {len(cleaned_records)}")
print(f"Same IPA (marked as (Sama)): {same_count}")
print(f"Different IPA: {diff_count}")

with open('oxford_3000_final.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_records, f, ensure_ascii=False, indent=2)

print("Saved to oxford_3000_final.json successfully!")
