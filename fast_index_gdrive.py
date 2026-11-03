import sys
import json
import socket

# Force IPv4 because IPv6 routing on this host times out
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

sys.stdout.reconfigure(encoding='utf-8')

CREDS_FILE = r'c:\Users\LILI\OneDrive - PDK Jateng\Dokumen\widio-titip\credentials_gdrive_widio.json'
creds = service_account.Credentials.from_service_account_file(
    CREDS_FILE,
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)
print("Refreshing token with IPv4...", flush=True)
creds.refresh(Request())
token = creds.token
print("Token acquired successfully!", flush=True)

headers = {'Authorization': f'Bearer {token}'}
folder_id = '1sv87iGNTSUKSpvf28VKx78ROZ5KWeUR-'

all_files = {}
page_token = None

print(f"Indexing files in {folder_id}...", flush=True)
while True:
    params = {
        'q': f"'{folder_id}' in parents and trashed=false",
        'pageSize': 1000,
        'fields': 'nextPageToken, files(id, name)'
    }
    if page_token:
        params['pageToken'] = page_token
    
    r = requests.get('https://www.googleapis.com/drive/v3/files', headers=headers, params=params, timeout=30)
    data = r.json()
    files = data.get('files', [])
    for f in files:
        all_files[f['name']] = f['id']
    print(f"Fetched {len(files)} files (Total so far: {len(all_files)})", flush=True)
    page_token = data.get('nextPageToken')
    if not page_token:
        break

print(f"Total files indexed: {len(all_files)}", flush=True)
with open('gdrive_audio_map.json', 'w', encoding='utf-8') as f:
    json.dump(all_files, f, indent=2)

print("Saved gdrive_audio_map.json successfully!", flush=True)
