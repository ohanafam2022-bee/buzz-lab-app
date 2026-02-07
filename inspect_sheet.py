from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1BtolneaNSnEbJlPGwwDm2WL6gJ86sUNtmj7AszT9v7U'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def inspect():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Credentials file not found.")
        return

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # Inspect '質問' sheet
    target_sheet = '質問'
    print(f"Inspecting '{target_sheet}'...")
    try:
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=f'{target_sheet}!A1:E5').execute()
        values = result.get('values', [])
        for i, row in enumerate(values):
            print(f"Row {i+1}: {row}")
    except Exception as e:
        print(f"Error reading {target_sheet}: {e}")

if __name__ == "__main__":
    try:
        inspect()
    except Exception as e:
        import traceback
        traceback.print_exc()
