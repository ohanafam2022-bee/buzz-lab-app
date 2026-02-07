from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1BtolneaNSnEbJlPGwwDm2WL6gJ86sUNtmj7AszT9v7U'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def create_questions_sheet():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Credentials file not found.")
        return

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # 1. Check if sheet exists
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', [])
    for s in sheets:
        if s['properties']['title'] == '質問':
            print("'質問' sheet already exists.")
            return

    # 2. Create sheet if not exists
    print("Creating '質問' sheet...")
    req_add_sheet = {
        'requests': [
            {
                'addSheet': {
                    'properties': {
                        'title': '質問'
                    }
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=req_add_sheet).execute()
    
    # 3. Add Headers
    print("Adding headers...")
    headers = [['日時', '生徒ID', '質問内容', 'ステータス', '回答']]
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='質問!A1:E1',
        valueInputOption='RAW',
        body={'values': headers}
    ).execute()
    
    print("Done!")

if __name__ == "__main__":
    create_questions_sheet()
