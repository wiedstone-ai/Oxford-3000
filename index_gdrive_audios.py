import sys
import json
import time
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDS_FILE = r'c:\Users\LILI\OneDrive - PDK Jateng\Dokumen\widio-titip\credentials_gdrive_widio.json'
creds = service_account.Credentials.from_service_account_file(
    CREDS_FILE,
    scopes=['https://www.googleapis.com/auth/drive']
)
service = build('drive', 'v3', credentials=creds)

folder_id = '1sv87iGNTSUKSpvf28VKx78ROZ5KWeUR-'

print(f"Fetching all files in folder {folder_id}...")
all_files = {}
page_token = None

for attempt in range(10):
    try:
        while True:
            res = service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                pageSize=1000,
                fields='nextPageToken, files(id, name)',
                pageToken=page_token
            ).execute()
            files = res.get('files', [])
            for f in files:
                all_files[f['name']] = f['id']
            page_token = res.get('nextPageToken')
            print(f"Loaded {len(all_files)} files...")
            if not page_token:
                break
        break
    except Exception as e:
        print(f"Error on attempt {attempt+1}: {e}. Retrying in 3s...")
        time.sleep(3)

print(f"Total files indexed from Google Drive: {len(all_files)}")
with open('gdrive_audio_map.json', 'w', encoding='utf-8') as f:
    json.dump(all_files, f, indent=2)

print("Saved to gdrive_audio_map.json successfully!")
