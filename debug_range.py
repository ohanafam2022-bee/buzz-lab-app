from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1BtolneaNSnEbJlPGwwDm2WL6gJ86sUNtmj7AszT9v7U'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def debug_range():
    service = get_service()
    
    # Test 1: Master sheet (ASCII)
    print("Test 1: Master!A1")
    try:
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Master!A1').execute()
        print(f"Success: {result.get('values')}")
    except Exception as e:
        print(f"Failed Master: {e}")

    # Test 2: 行動管理 (Japanese)
    print("\nTest 2: 行動管理!A1")
    try:
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='行動管理!A1').execute()
        print(f"Success: {result.get('values')}")
    except Exception as e:
        print(f"Failed 行動管理: {e}")

    # Test 3: Quoted '行動管理'!A1
    print("\nTest 3: '行動管理'!A1")
    try:
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range="'行動管理'!A1").execute()
        print(f"Success: {result.get('values')}")
    except Exception as e:
        print(f"Failed Quoted: {e}")


    # Test 4: List Sheets
    print("\nTest 4: List Sheets")
    try:
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', [])
        for s in sheets:
            title = s.get("properties", {}).get("title", "Unknown")
            print(f"- '{title}' (Len: {len(title)})")
            # Print hex to be sure
            print(f"  Hex: {title.encode('utf-8').hex()}")
    except Exception as e:
        print(f"Failed List: {e}")

if __name__ == "__main__":
    debug_range()
