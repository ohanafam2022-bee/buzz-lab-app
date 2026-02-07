from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# This is now the MASTER spreadsheet ID (containing 'Master', 'Questions', etc.)
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

# Cache for Student Configs to avoid frequent lookups
STUDENT_CONFIG_CACHE = {}

def get_student_config(student_id):
    """
    Retrieves the Spreadsheet ID and Sheet Name for a given student_id from the 'Master' sheet.
    Returns a dict: {'spreadsheet_id': str, 'sheet_name': str}
    """
    if student_id in STUDENT_CONFIG_CACHE:
        return STUDENT_CONFIG_CACHE[student_id]

    service = get_service()
    if not service: 
        return None

    try:
        # Read 'Master' sheet
        # A: Student ID, B: Spreadsheet ID, C: Name, D: Sheet Name (Optional)
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Master!A2:D').execute()
        rows = result.get('values', [])
        
        for row in rows:
            if len(row) >= 2 and row[0] == student_id:
                config = {
                    'spreadsheet_id': row[1],
                    # Default to '行動管理' if Column D is missing or empty
                    'sheet_name': row[3] if len(row) > 3 and row[3].strip() else '行動管理'
                }
                STUDENT_CONFIG_CACHE[student_id] = config
                return config
        
        print(f"Student ID {student_id} not found in Master sheet.")
        return None

    except Exception as e:
        print(f"Error fetching student config for {student_id}: {e}")
        return None

def get_tasks(student_id):
    service = get_service()
    if not service:
        return []

    config = get_student_config(student_id)
    if not config:
        print(f"No config found for {student_id}")
        return []

    target_spreadsheet_id = config['spreadsheet_id']
    target_sheet_name = config['sheet_name']

    try:
        sheet = service.spreadsheets()
        # Use dynamic sheet name
        # Note: If sheet name contains spaces/special chars, API handles it usually, 
        # but quoting 'Sheet Name'!A1 is safer if we control the string. 
        # However, purely relying on the string from Master sheet is most flexible.
        range_name = f"'{target_sheet_name}'!A6:E" 
        result = sheet.values().get(spreadsheetId=target_spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        
        tasks = []
        current_week = ""
        
        for i, row in enumerate(rows):
            sheet_row_index = 6 + i
            col_a = row[0] if len(row) > 0 else ""
            col_b = row[1] if len(row) > 1 else ""
            col_c = row[2] if len(row) > 2 else ""
            col_d = row[3] if len(row) > 3 else "未着手"
            
            if col_a.strip().startswith("Week"):
                current_week = col_a.strip()
            
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

    config = get_student_config(student_id)
    if not config:
        return False

    target_spreadsheet_id = config['spreadsheet_id']
    target_sheet_name = config['sheet_name']

    try:
        row_index = int(task_id)
        range_name = f"'{target_sheet_name}'!D{row_index}"
        body = {'values': [[status]]}
        service.spreadsheets().values().update(
            spreadsheetId=target_spreadsheet_id, 
            range=range_name, 
            valueInputOption='USER_ENTERED', 
            body=body
        ).execute()
        return True
    except Exception as e:
        print(f"Error updating task: {e}")
        return False

def get_user_info(student_id):
    service = get_service()
    if not service:
        return {}

    config = get_student_config(student_id)
    if not config:
        return {}

    target_spreadsheet_id = config['spreadsheet_id']
    target_sheet_name = config['sheet_name']

    try:
        result = service.spreadsheets().values().get(spreadsheetId=target_spreadsheet_id, range=f"'{target_sheet_name}'!A1:F5").execute()
        rows = result.get('values', [])
        
        info = {
            "monthly_goal": "",
            "bottleneck": "",
            "weekly_focus": "",
            "current_week": "",
            "mentor": ""
        }

        if len(rows) > 1:
            row2 = rows[1]
            if len(row2) > 0: info["monthly_goal"] = row2[0]
            if len(row2) > 2: info["bottleneck"] = row2[2]
            
        if len(rows) > 3:
            row4 = rows[3]
            if len(row4) > 0: info["weekly_focus"] = row4[0]
            if len(row4) > 3: info["current_week"] = row4[3]
            if len(row4) > 4: info["mentor"] = row4[4]
            
        return info

    except Exception as e:
        print(f"Error fetching user info: {e}")
        return {}

def submit_question(student_id, question_text):
    service = get_service()
    if not service:
        return False

    # Questions are submitted to the CENTRAL spreadsheet (where '質問' sheet lives)
    # NOT the individual student spreadsheet.
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "未回答"
        values = [[timestamp, student_id, question_text, status, ""]]
        body = {'values': values}
        
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='質問!A:E',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return True
    except Exception as e:
        print(f"Error submitting question: {e}")
        return False
