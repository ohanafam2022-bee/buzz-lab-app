from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1BtolneaNSnEbJlPGwwDm2WL6gJ86sUNtmj7AszT9v7U'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_service():
    # Check for Environment Variable (for Render)
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json_str:
        try:
            creds_json = json.loads(creds_json_str)
            creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
            return build('sheets', 'v4', credentials=creds)
        except Exception as e:
            print(f"Error loading credentials from Env Var: {e}")
            return None

    # Fallback to local file
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        return None
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def get_tasks(student_id):
    service = get_service()
    if not service:
        # Fallback Mock Data if credentials missing
        return []

    try:
        sheet = service.spreadsheets()
        # Read '行動管理' sheet from A6 downwards. 
        # A: Week Label, B: Title, C: Description, D: Status
        target_sheet = '行動管理'
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'{target_sheet}!A6:E').execute()
        rows = result.get('values', [])
        
        tasks = []
        current_week = ""
        
        for i, row in enumerate(rows):
            # Row index in sheet = 6 + i
            sheet_row_index = 6 + i
            
            # Extract values, handling partial rows
            col_a = row[0] if len(row) > 0 else ""
            col_b = row[1] if len(row) > 1 else ""
            col_c = row[2] if len(row) > 2 else "" # Description
            col_d = row[3] if len(row) > 3 else "未着手" # Status
            
            # Update current week context if Column A has value
            if col_a.strip().startswith("Week"):
                current_week = col_a.strip()
            
            # If Column B (Title) is not empty, it's a task
            title = col_b.strip()
            if title:
                tasks.append({
                    "id": sheet_row_index,
                    "title": title,
                    "description": col_c,
                    "status": col_d,
                    "week": current_week
                })
        return tasks
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []

def update_task_status(student_id, task_id, status):
    service = get_service()
    if not service:
        return False

    try:
        # task_id is directly the row index
        row_index = int(task_id)
        
        # Update Column D (Index 3 -> 'D') with Status text
        range_name = f'行動管理!D{row_index}'
        
        body = {'values': [[status]]}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, 
            range=range_name, 
            valueInputOption='USER_ENTERED', 
            body=body
        ).execute()
        return True

    except Exception as e:
        print(f"Error updating task: {e}")
        return False
