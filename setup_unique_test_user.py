from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
MASTER_SPREADSHEET_ID = '1BtolneaNSnEbJlPGwwDm2WL6gJ86sUNtmj7AszT9v7U'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_service():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Credentials file not found.")
        return None
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def setup_unique_test_user():
    service = get_service()
    if not service: return

    print("Setting up unique test user (student_id_002)...")

    # 1. Create a NEW Spreadsheet
    spreadsheet_body = {
        'properties': {
            'title': 'Buzz Lab Action Plan (Test User 2)'
        }
    }
    
    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()
    new_spreadsheet_id = response['spreadsheetId']
    print(f"Created new spreadsheet: {new_spreadsheet_id}")

    # 2. Setup '行動管理' sheet structure in the new spreadsheet
    # Rename default Sheet1 to '行動管理'
    sheet_id = response['sheets'][0]['properties']['sheetId']
    requests = [
        {
            'updateSheetProperties': {
                'properties': {
                    'sheetId': sheet_id,
                    'title': '行動管理'
                },
                'fields': 'title'
            }
        }
    ]
    service.spreadsheets().batchUpdate(spreadsheetId=new_spreadsheet_id, body={'requests': requests}).execute()

    # 3. Populate with Sample Data (Goal & Tasks)
    # Header Info (Rows 1-5)
    header_data = [
        ['今月の目標', '', '課題・ボトルネック', '', 'メンター'],
        ['売上10万', '', '時間が足りない', '', 'TestMentor'],
        ['', '', '', '', ''],
        ['今週の注力', '', '', 'Current Week', 'Week1'],
        ['集客', '', '', '', '']
    ]
    
    # Task Data (Rows 6+)
    # Week, Title, Description, Status
    task_data = [
        ['Week1', 'Test User 2 Task A', 'Unique task for user 2', '未着手'],
        ['Week1', 'Test User 2 Task B', 'Another unique task', '進行中'],
        ['Week2', 'Future Task', 'Planning ahead', '未着手']
    ]

    all_values = header_data + task_data
    
    service.spreadsheets().values().update(
        spreadsheetId=new_spreadsheet_id,
        range='行動管理!A1',
        valueInputOption='USER_ENTERED',
        body={'values': all_values}
    ).execute()
    print("Populated new spreadsheet with data.")

    # 4. Update Master Sheet to point student_id_002 to this NEW Spreadsheet
    # First, find if row exists to update, or append.
    # For simplicity, we'll read all lines, find student_id_002, and update that line.
    
    master_data = service.spreadsheets().values().get(spreadsheetId=MASTER_SPREADSHEET_ID, range='Master!A:C').execute().get('values', [])
    
    row_index_to_update = -1
    for i, row in enumerate(master_data):
        if len(row) > 0 and row[0] == 'student_id_002':
            row_index_to_update = i + 1 # 1-based index
            break
            
    if row_index_to_update != -1:
        # Update existing row
        range_name = f'Master!B{row_index_to_update}'
        service.spreadsheets().values().update(
            spreadsheetId=MASTER_SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body={'values': [[new_spreadsheet_id]]}
        ).execute()
        print(f"Updated Master sheet row {row_index_to_update} for student_id_002.")
    else:
        # Append new row
        values = [['student_id_002', new_spreadsheet_id, 'Test User 2']]
        service.spreadsheets().values().append(
            spreadsheetId=MASTER_SPREADSHEET_ID,
            range='Master!A:C',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': values}
        ).execute()
        print("Appended new row to Master sheet for student_id_002.")

    # 5. Share the new sheet (Optional, but good if User wants to see it)
    # We'll print the URL
    print(f"\nSUCCESS! New Spreadsheet URL: https://docs.google.com/spreadsheets/d/{new_spreadsheet_id}")
    print("Please verify by accessing: /dashboard?student_id=student_id_002")

if __name__ == "__main__":
    setup_unique_test_user()
