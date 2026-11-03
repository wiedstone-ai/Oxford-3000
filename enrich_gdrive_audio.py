import sys
import json
import socket

# Force IPv4
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load data
with open('oxford_3000_final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

with open('gdrive_audio_map.json', 'r', encoding='utf-8') as f:
    gmap = json.load(f)

matched_uk = 0
matched_us = 0

for r in dataset:
    w = r['word'].strip().lower()
    w_clean = "".join(c for c in w if c.isalnum() or c in [' ', '_', '-']).strip().replace(' ', '_')
    
    uk_fname = f"{w_clean}_uk.mp3"
    us_fname = f"{w_clean}_us.mp3"
    
    uk_id = gmap.get(uk_fname)
    us_id = gmap.get(us_fname)
    
    if uk_id:
        matched_uk += 1
        r['gdrive_uk_id'] = uk_id
        r['gdrive_uk_url'] = f"https://drive.google.com/uc?export=download&id={uk_id}"
    else:
        r['gdrive_uk_id'] = None
        r['gdrive_uk_url'] = r.get('audio_uk_url') # fallback to oxford
        
    if us_id:
        matched_us += 1
        r['gdrive_us_id'] = us_id
        r['gdrive_us_url'] = f"https://drive.google.com/uc?export=download&id={us_id}"
    else:
        r['gdrive_us_id'] = None
        r['gdrive_us_url'] = r.get('audio_us_url') # fallback to oxford
        
    r['oxford_uk_url'] = r.get('audio_uk_url')
    r['oxford_us_url'] = r.get('audio_us_url')
    
    # Formulas point to internal Google Drive audio
    r['audio_uk_formula'] = f'=HYPERLINK("{r["gdrive_uk_url"]}", "🔊 UK")'
    r['audio_us_formula'] = f'=HYPERLINK("{r["gdrive_us_url"]}", "🔊 US")'

print(f"Total dataset entries: {len(dataset)}")
print(f"Matched GDrive UK: {matched_uk}")
print(f"Matched GDrive US: {matched_us}")

with open('oxford_3000_final.json', 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("Updated oxford_3000_final.json with internal Google Drive IDs & URLs!")
