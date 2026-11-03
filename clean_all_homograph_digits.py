import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('oxford_3000_final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

cleaned_list = []

for r in dataset:
    w = r['word']
    entry = r.get('full_entry', '')
    
    # Check if word has digits
    if re.search(r'\d+', w):
        # Remove digits from word
        w_new = re.sub(r'\d+', '', w).strip()
        w_new = re.sub(r'\s+', ' ', w_new)
        
        # Remove digits from full_entry as well
        entry_new = re.sub(r'([a-zA-Z]+)\d+', r'\1', entry)
        
        cleaned_list.append({
            'no': r['no'],
            'level': r['level'],
            'old_word': w,
            'new_word': w_new,
            'old_entry': entry,
            'new_entry': entry_new
        })
        
        r['word'] = w_new
        r['full_entry'] = entry_new

print(f"Total words cleaned of digits: {len(cleaned_list)}")
for item in cleaned_list:
    print(f"No {item['no']:4d} [{item['level']}] '{item['old_word']}' -> '{item['new_word']}' | Entry: '{item['new_entry']}'")

# Save cleaned dataset
with open('oxford_3000_final.json', 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("\nSaved oxford_3000_final.json successfully!")
