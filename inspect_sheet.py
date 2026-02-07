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

    # Inspect specific rows of '行動管理' to find Status and Description columns
    target_sheet = '行動管理'
    print(f"Inspecting '{target_sheet}' A-J...")
    try:
        # Read columns A to J (Indices 0 to 9)
        # Expected: B=Title, D=Status?, F=Check?, ?=Description
        # Read columns A to F, Rows 1 to 10 to see top section
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=f'{target_sheet}!A1:F10').execute()
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
