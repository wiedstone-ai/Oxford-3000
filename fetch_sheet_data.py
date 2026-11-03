import sys
import json
import socket

# Force IPv4
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

import gspread
from google.oauth2.service_account import Credentials

sys.stdout.reconfigure(encoding='utf-8')

CRED_PATH = r'C:\Users\LILI\OneDrive - PDK Jateng\Dokumen\widio-titip\credentials_gdrive_widio.json'
SPREADSHEET_ID = '1_l6Ojulq3jMryReGtmN1z1PtWYSkVtggDC0PpEVcjqQ'
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

creds = Credentials.from_service_account_file(CRED_PATH, scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)

ws = sh.worksheet('All Words')
rows = ws.get_all_values()
print(f"Total rows fetched from 'All Words': {len(rows)}")
print("Header:", rows[0])

# Save raw fetched rows for deep analysis
with open('sheet_all_words_dump.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

print("Saved to sheet_all_words_dump.json successfully!")
