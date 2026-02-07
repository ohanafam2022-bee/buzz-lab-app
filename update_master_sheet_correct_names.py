from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1BtolneaNSnEbJlPGwwDm2WL6gJ86sUNtmj7AszT9v7U'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def update_master():
    service = get_service()
    
    # 1. Update student_id_001 to use '行動管理①'
    print("Updating student_id_001...")
    # Find row first? Assume row 2 (index 2 for user, 1 for 0-based header skip? No, A2 is row 2)
    # Let's search to be safe
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Master!A:A').execute()
    rows = result.get('values', [])
    
    for i, row in enumerate(rows):
        if len(row) > 0 and row[0] == 'student_id_001':
            row_idx = i + 1
            # Update columns B, C, D
            # B=SpreadsheetID (Same), C=Name (Keep), D=SheetName (NEW)
            range_name = f'Master!B{row_idx}:D{row_idx}'
            values = [[SPREADSHEET_ID, '岩口 永遠', '行動管理①']]
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID, range=range_name, 
                valueInputOption='RAW', body={'values': values}
            ).execute()
            print(f"Updated student_id_001 at row {row_idx}")

        if len(row) > 0 and row[0] == 'student_id_002':
            row_idx = i + 1
            range_name = f'Master!B{row_idx}:D{row_idx}'
            values = [[SPREADSHEET_ID, 'Test User 2', '行動管理① のコピー']]
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID, range=range_name, 
                valueInputOption='RAW', body={'values': values}
            ).execute()
            print(f"Updated student_id_002 at row {row_idx}")

    # Invalidate cache if running in app (not needed for this script but good practice)
    print("Master sheet updated.")

if __name__ == "__main__":
    update_master()
