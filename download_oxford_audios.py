import os
import sys
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import zipfile

base_dir = r'C:\Users\LILI\OneDrive - PDK Jateng\Dokumen\Oxford-3000'
audio_dir = os.path.join(base_dir, 'Audio Oxford 3000')
os.makedirs(audio_dir, exist_ok=True)

with open(os.path.join(base_dir, 'oxford_3000_uk_us.json'), 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Collect all download tasks
tasks = {} # filename -> url

for r in dataset:
    w = r['word'].strip().lower()
    # clean for filename
    w_clean = re_w = "".join(c for c in w if c.isalnum() or c in [' ', '_', '-']).strip().replace(' ', '_')
    
    uk_url = r['audio_oxford_uk']
    us_url = r['audio_oxford_us']
    
    if uk_url and 'oxfordlearnersdictionaries.com' in uk_url:
        tasks[f"{w_clean}_uk.mp3"] = uk_url
    if us_url and 'oxfordlearnersdictionaries.com' in us_url:
        tasks[f"{w_clean}_us.mp3"] = us_url

print(f"Total audio files to download: {len(tasks)}")

def download_one(filename, url):
    dest_path = os.path.join(audio_dir, filename)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return filename, True, "already exists"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 500:
                with open(dest_path, 'wb') as f:
                    f.write(data)
                return filename, True, len(data)
            else:
                return filename, False, "too small"
    except Exception as e:
        return filename, False, str(e)

start_time = time.time()
success_count = 0
failed_count = 0

print("Memulai unduhan paralel (30 threads)...")
with ThreadPoolExecutor(max_workers=30) as executor:
    futures = {executor.submit(download_one, fn, u): fn for fn, u in tasks.items()}
    done_count = 0
    for f in as_completed(futures):
        fn, ok, msg = f.result()
        done_count += 1
        if ok:
            success_count += 1
        else:
            failed_count += 1
        if done_count % 500 == 0 or done_count == len(tasks):
            elapsed = time.time() - start_time
            print(f"Progress: {done_count}/{len(tasks)} ({done_count/len(tasks)*100:.1f}%) | Sukses: {success_count} | Waktu: {elapsed:.1f}s")

print(f"\nSelesai mengunduh dalam {time.time()-start_time:.1f}s!")
print(f"Total berhasil: {success_count}, Gagal: {failed_count}")

# Create ZIP archive
zip_path = os.path.join(base_dir, 'Audio_Oxford_3000_Full.zip')
print(f"Membuat arsip zip: {zip_path}...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(audio_dir):
        for file in files:
            file_p = os.path.join(root, file)
            zipf.write(file_p, arcname=os.path.join('Audio Oxford 3000', file))

print(f"Arsip ZIP selesai dibuat! Ukuran: {os.path.getsize(zip_path)/(1024*1024):.1f} MB")
