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
                    'name': row[2] if len(row) > 2 else 'Unknown',
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

# --- Admin Dashboard Functions ---

def get_all_students():
    """
    Fetches all students from the Master sheet.
    Returns a list of dicts: {'student_id': str, 'name': str, 'sheet_name': str}
    """
    service = get_service()
    if not service: return []

    try:
        # Read Master sheet A:D
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Master!A2:D').execute()
        rows = result.get('values', [])
        
        students = []
        for row in rows:
            if len(row) >= 3: # Must have ID, SpreadsheetID, Name
                students.append({
                    'student_id': row[0],
                    'spreadsheet_id': row[1],
                    'name': row[2],
                    'sheet_name': row[3] if len(row) > 3 else '行動管理'
                })
        return students
    except Exception as e:
        print(f"Error fetching all students: {e}")
        return []

def get_unanswered_questions():
    """
    Fetches all questions with status '未回答' or empty status.
    """
    service = get_service()
    if not service: return []

    try:
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='質問!A2:E').execute()
        rows = result.get('values', [])
        
        questions = []
        for i, row in enumerate(rows):
            # Format: Timestamp, StudentID, Question, Status, Reply
            status = row[3] if len(row) > 3 else "未回答"
            if status == "未回答" or not status.strip():
                questions.append({
                    'row_index': i + 2, # 1-indexed, +header
                    'timestamp': row[0] if len(row) > 0 else "",
                    'student_id': row[1] if len(row) > 1 else "",
                    'question': row[2] if len(row) > 2 else "",
                    'status': status
                })
        return questions
    except Exception as e:
        print(f"Error fetching unanswered questions: {e}")
        return []

def get_admin_dashboard_data():
    """
    Aggregates data for the admin dashboard.
    """
    students = get_all_students()
    unanswered_questions = get_unanswered_questions()
    
    detailed_students = []
    
    for student in students:
        try:
            info = get_user_info(student['student_id'])
            student['current_week'] = info.get('current_week', '-')
            student['monthly_goal'] = info.get('monthly_goal', '-')
        except Exception as e:
            print(f"Error fetching info for {student['student_id']}: {e}")
            student['current_week'] = 'Error'
            student['monthly_goal'] = 'Error'
            
        detailed_students.append(student)
        
    return {
        'students': detailed_students,
        'unanswered_questions': unanswered_questions,
        'total_students': len(students),
        'total_questions': len(unanswered_questions)
    }

CIRCLED_NUMBERS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"

def get_next_sheet_name(service, spreadsheet_id):
    """
    Scans existing sheets to find the next available '行動管理X' name.
    Supports circled numbers ①-⑳.
    """
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get('sheets', [])
        existing_indices = []
        
        for s in sheets:
            title = s['properties']['title']
            if title.startswith("行動管理"):
                suffix = title.replace("行動管理", "").strip()
                # Check for circled number
                if suffix in CIRCLED_NUMBERS:
                    idx = CIRCLED_NUMBERS.index(suffix) + 1
                    existing_indices.append(idx)
                # Check for regular number (fallback)
                elif suffix.isdigit():
                    existing_indices.append(int(suffix))
        
        next_idx = max(existing_indices) + 1 if existing_indices else 1
        
        if next_idx <= 20:
            return f"行動管理{CIRCLED_NUMBERS[next_idx-1]}"
        else:
            return f"行動管理{next_idx}" # Fallback to normal number > 20
            
    except Exception as e:
        print(f"Error determining next sheet name: {e}")
        return f"行動管理_New"

def create_new_student(name, student_id):
    """
    1. Copies the '行動管理③' (latest template) sheet.
    2. Renames it to the next available circled number (e.g., '行動管理④').
    3. Adds row to Master sheet.
    """
    service = get_service()
    if not service: return False
    
    try:
        # Determine Template: Use '行動管理③' as the source.
        # If not found, try '99_マスター', else fail.
        template_name = '行動管理③'
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = spreadsheet.get('sheets', [])
        template_id = None
        
        # Check if intended template exists
        for s in sheets:
            if s['properties']['title'] == template_name:
                template_id = s['properties']['sheetId']
                break
        
        # Fallback if specific template missing (useful for testing if user deleted it)
        if template_id is None:
             print(f"Template '{template_name}' not found. Searching for any '行動管理'.")
             for s in sheets:
                 if "行動管理" in s['properties']['title']:
                     template_id = s['properties']['sheetId']
                     break

        if template_id is None:
            print("No suitable template sheet found.")
            return False

        # 2. Determine New Name
        new_sheet_name = get_next_sheet_name(service, SPREADSHEET_ID)

        # 3. Copy the sheet
        copy_request = service.spreadsheets().sheets().copyTo(
            spreadsheetId=SPREADSHEET_ID,
            sheetId=template_id,
            body={'destinationSpreadsheetId': SPREADSHEET_ID}
        ).execute()
        
        new_sheet_id = copy_request['sheetId']
        
        # 4. Rename the new sheet
        update_body = {
            'requests': [{
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': new_sheet_id,
                        'title': new_sheet_name,
                    },
                    'fields': 'title'
                }
            }]
        }
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=update_body).execute()
        
        # 5. Add to Master sheet
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={new_sheet_id}"
        hyperlink_formula = f'=HYPERLINK("{url}", "{new_sheet_name}")'
        
        values = [[student_id, SPREADSHEET_ID, name, hyperlink_formula]]
        append_body = {'values': values}
        
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Master!A:D',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=append_body
        ).execute()
        
        return True

    except Exception as e:
        print(f"Error creating new student: {e}")
        return False

def delete_student(student_id):
    """
    Deletes a student from the Master sheet.
    Deletes ALL rows matching the student_id (to handle duplicates).
    DOES NOT delete the individual student sheet (for safety).
    """
    service = get_service()
    if not service: return False

    try:
        # 1. Find the row indices of the student in Master sheet
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Master!A:A').execute()
        rows = result.get('values', [])
        
        rows_to_delete = []
        for i, row in enumerate(rows):
            if row and row[0] == student_id:
                rows_to_delete.append(i)
        
        if not rows_to_delete:
            print(f"Student ID {student_id} not found in Master sheet.")
            return False

        # 2. Delete the rows using batchUpdate with deleteDimension
        # Sort in descending order to avoid index shifting issues when deleting multiple rows
        rows_to_delete.sort(reverse=True)
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        master_sheet_id = 0
        for s in spreadsheet.get('sheets', []):
            if s['properties']['title'] == 'Master':
                master_sheet_id = s['properties']['sheetId']
                break

        requests = []
        for row_idx in rows_to_delete:
            requests.append({
                'deleteDimension': {
                    'range': {
                        'sheetId': master_sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': row_idx,
                        'endIndex': row_idx + 1
                    }
                }
            })

        request_body = {'requests': requests}

        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=request_body).execute()
        print(f"Deleted student {student_id} from Master sheet (Rows: {[r+1 for r in rows_to_delete]}).")
        
        # Clear cache
        if student_id in STUDENT_CONFIG_CACHE:
            del STUDENT_CONFIG_CACHE[student_id]
            
        return True

    except Exception as e:
        print(f"Error deleting student: {e}")
        return False
