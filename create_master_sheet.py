from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1BtolneaNSnEbJlPGwwDm2WL6gJ86sUNtmj7AszT9v7U'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def create_master_sheet():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Credentials file not found.")
        return

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # 1. Check if sheet exists
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', [])
    for s in sheets:
        if s['properties']['title'] == 'Master':
            print("'Master' sheet already exists.")
            return

    # 2. Create sheet if not exists
    print("Creating 'Master' sheet...")
    req_add_sheet = {
        'requests': [
            {
                'addSheet': {
                    'properties': {
                        'title': 'Master'
                    }
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=req_add_sheet).execute()
    
    # 3. Add Headers
    print("Adding headers...")
    headers = [['生徒ID', 'スプレッドシートID', '名前']]
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Master!A1:C1',
        valueInputOption='RAW',
        body={'values': headers}
    ).execute()
    
    # 4. Add Initial Data (Self-reference for testing)
    print("Adding initial data...")
    # Using the same Spreadsheet ID for student_id_001 for now to test
    initial_data = [['student_id_001', SPREADSHEET_ID, 'Buzz Student (Test)']]
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Master!A2:C2',
        valueInputOption='RAW',
        body={'values': initial_data}
    ).execute()
    
    print("Done!")

if __name__ == "__main__":
    create_master_sheet()
