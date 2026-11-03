import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDS_FILE = r'c:\Users\LILI\OneDrive - PDK Jateng\Dokumen\widio-titip\credentials_gdrive_widio.json'
creds = service_account.Credentials.from_service_account_file(
    CREDS_FILE,
    scopes=['https://www.googleapis.com/auth/drive']
)
service = build('drive', 'v3', credentials=creds)

parent_id = '1QiWHDEHP6C7MN816NRZRGvvd7jc4_GVA'

print("Scanning English parent folder...")
res = service.files().list(
    q=f"'{parent_id}' in parents and trashed=false",
    pageSize=50,
    fields='files(id, name, mimeType, size)'
).execute()
files = res.get('files', [])
print(f"Total items in parent folder: {len(files)}")
for f in files:
    print(f"- [{f['mimeType']}] {f['name']} (ID: {f['id']})")

# Also check subfolders if any
for f in files:
    if f['mimeType'] == 'application/vnd.google-apps.folder':
        sub_id = f['id']
        sub_name = f['name']
        sub_res = service.files().list(
            q=f"'{sub_id}' in parents and trashed=false",
            pageSize=10,
            fields='files(id, name, mimeType, size)'
        ).execute()
        sub_items = sub_res.get('files', [])
        print(f"\nInside folder '{sub_name}' (ID: {sub_id}): sample {len(sub_items)} items")
        for sf in sub_items:
            print(f"  * {sf['name']} (ID: {sf['id']})")
