import json
import re

# Load UK and US IPA dictionaries
uk_dict = {}
with open('en_UK.txt', 'r', encoding='utf-8') as f:
    for line in f:
        p = line.strip().split('\t')
        if len(p) >= 2:
            # take first variant if multiple
            uk_dict[p[0].lower()] = p[1].split(',')[0].strip()

us_dict = {}
with open('en_US.txt', 'r', encoding='utf-8') as f:
    for line in f:
        p = line.strip().split('\t')
        if len(p) >= 2:
            us_dict[p[0].lower()] = p[1].split(',')[0].strip()

# Load current enriched dataset
with open('oxford_3000_enriched.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Load oxford audio map
import urllib.request
url = 'https://raw.githubusercontent.com/samuraitruong/oxford-3000/master/data/oxford-5000.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    oxford_audio_data = json.loads(resp.read().decode('utf-8'))

audio_map = {}
for item in oxford_audio_data:
    w = item.get('word', '').lower().strip()
    sound = item.get('sound') or {}
    uk_list = sound.get('uk') or []
    us_list = sound.get('us') or []
    uk = next((s for s in uk_list if isinstance(s, str) and s.endswith('.mp3')), None)
    us = next((s for s in us_list if isinstance(s, str) and s.endswith('.mp3')), None)
    if w and (uk or us):
        audio_map[w] = {
            'uk': ('https://www.oxfordlearnersdictionaries.com' + uk) if uk else None,
            'us': ('https://www.oxfordlearnersdictionaries.com' + us) if us else None
        }

# Process each record
same_ipa_count = 0
diff_ipa_count = 0

for r in dataset:
    w = r['word'].strip()
    w_clean = re.sub(r'\d+', '', w)
    w_clean = re.sub(r'\(.*?\)', '', w_clean).strip()
    if ',' in w_clean:
        w_clean = w_clean.split(',')[0].strip()
    w_low = w_clean.lower()
    
    # 1. IPA UK & US
    ipa_uk = uk_dict.get(w_low)
    ipa_us = us_dict.get(w_low)
    
    # Fallback to existing pronunciation if missing
    fallback = r.get('pronunciation', f"/{w_low}/").strip('/')
    if not ipa_uk:
        ipa_uk = fallback
    if not ipa_us:
        ipa_us = fallback
        
    r['ipa_uk'] = f"/{ipa_uk}/"
    
    # Check if identical
    if ipa_uk == ipa_us:
        same_ipa_count += 1
        r['ipa_us'] = "(Sama)"
        r['is_ipa_same'] = True
    else:
        diff_ipa_count += 1
        r['ipa_us'] = f"/{ipa_us}/"
        r['is_ipa_same'] = False
        
    # 2. Audio URLs (Oxford official)
    a_info = audio_map.get(w_low) or audio_map.get(w.lower()) or {}
    r['audio_oxford_uk'] = a_info.get('uk') or f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en-gb&q={w_low}"
    r['audio_oxford_us'] = a_info.get('us') or f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en-us&q={w_low}"

print(f"Total processed: {len(dataset)}")
print(f"IPA Same: {same_ipa_count}, IPA Different: {diff_ipa_count}")

# Save updated dataset
with open('oxford_3000_uk_us.json', 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("Saved to oxford_3000_uk_us.json successfully!")
