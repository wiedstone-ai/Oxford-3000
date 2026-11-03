import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CREDS_FILE = r'c:\Users\LILI\OneDrive - PDK Jateng\Dokumen\widio-titip\credentials_gdrive_widio.json'
creds = service_account.Credentials.from_service_account_file(
    CREDS_FILE,
    scopes=['https://www.googleapis.com/auth/drive']
)
service = build('drive', 'v3', credentials=creds)

TARGET_FOLDER_ID = '10jI8gtIRQ449pMnbzmLCra8U6-vrjbal'
ZIP_PATH = r'c:\Users\LILI\OneDrive - PDK Jateng\Dokumen\Oxford-3000\Audio_Oxford_3000_Full.zip'

print(f"Uploading {ZIP_PATH} ({os.path.getsize(ZIP_PATH)/(1024*1024):.2f} MB) to GDrive folder {TARGET_FOLDER_ID}...")

# Check if zip already exists in folder
res = service.files().list(
    q=f"'{TARGET_FOLDER_ID}' in parents and name='Audio_Oxford_3000_Full.zip' and trashed=false",
    fields='files(id, name)'
).execute()
existing = res.get('files', [])
if existing:
    print(f"Zip already exists with ID: {existing[0]['id']}")
else:
    file_metadata = {
        'name': 'Audio_Oxford_3000_Full.zip',
        'parents': [TARGET_FOLDER_ID]
    }
    media = MediaFileUpload(ZIP_PATH, mimetype='application/zip', resumable=True, chunksize=10*1024*1024)
    request = service.files().create(body=file_metadata, media_body=media, fields='id, name, webViewLink')
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    print(f"Upload complete! File ID: {response.get('id')}")
    print(f"Link: {response.get('webViewLink')}")
