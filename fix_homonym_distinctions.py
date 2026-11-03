import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('oxford_3000_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for r in data:
    w = r['word'].strip().lower()
    pos = r['pos'].strip()
    no = r['no']
    
    # 1. can
    if w == 'can' and 'modal' in pos:
        r['arti'] = 'bisa, dapat, mampu'
    elif w == 'can' and pos == 'n.':
        r['arti'] = 'kaleng, wadah kaleng'
        
    # 2. will
    if w == 'will' and 'modal' in pos:
        r['arti'] = 'akan, hendak, mau'
    elif w == 'will' and pos == 'n.':
        r['arti'] = 'kemauan, tekad, surat wasiat'
        
    # 3. May
    if r['word'].strip() == 'May' and pos == 'n.':
        r['arti'] = 'Mei (bulan ke-5)'
    elif w == 'may' and 'modal' in pos:
        r['arti'] = 'boleh, mungkin, dapat'
        
    # 4. lie
    if no == 434: # lie1 v. (lie down)
        r['arti'] = 'berbaring, merebahkan diri, terletak'
    elif no == 2176: # lie2 (tell a lie) v., n.
        r['arti'] = 'berbohong, berdusta, kebohongan'
        
    # 5. ring
    if no == 1552: # ring1 n. (jewelry)
        r['arti'] = 'cincin, gelanggang, arena'
    elif no == 1553: # ring2 v. (phone/sound)
        r['arti'] = 'berdering, menelepon, membunyikan'
    elif no == 2380: # ring2 n. (sound of phone/bell)
        r['arti'] = 'dering, bunyi bel, panggilan telepon'
        
    # 6. tear
    if no == 3236: # tear1 v., n. (rip)
        r['arti'] = 'merobek, menyobek, sobekan'
    elif no == 3237: # tear2 n. (eye)
        r['arti'] = 'air mata'
        
    # 7. wind
    if no == 1759: # wind1 n. (air)
        r['arti'] = 'angin, hembusan angin'
    elif no == 3297: # wind2 v. (turn/coil)
        r['arti'] = 'memutar, melilit, berliku-liku'

with open('oxford_3000_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Homonym sense distinctions perfected!")
