from sheets_handler import get_spreadsheet_id, get_tasks, get_service, SPREADSHEET_ID

def verify_multi_user():
    print("Verifying Multi-User Support...")
    
    # 1. Verify student_id_001 (Should exist)
    print("\n--- Checking student_id_001 ---")
    sheet_id_1 = get_spreadsheet_id('student_id_001')
    print(f"Spreadsheet ID for student_id_001: {sheet_id_1}")
    
    if sheet_id_1:
        tasks_1 = get_tasks('student_id_001')
        print(f"Tasks found for student_id_001: {len(tasks_1)}")
    else:
        print("FAILED: student_id_001 not found.")

    # 2. Add student_id_002 to Master if not exists (for testing)
    print("\n--- Setting up student_id_002 (Test User) ---")
    service = get_service()
    
    # Check if exists first (poor man's check)
    existing_id = get_spreadsheet_id('student_id_002')
    
    if not existing_id:
        print("Adding student_id_002 to Master sheet...")
        # Pointing to SAME spreadsheet for testing purposes
        values = [['student_id_002', SPREADSHEET_ID, 'Test User 2']]
        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Master!A:C',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        print("Added student_id_002.")
        
        # Invalidate cache for testing
        from sheets_handler import SPREADSHEET_ID_CACHE
        if 'student_id_002' in SPREADSHEET_ID_CACHE:
            del SPREADSHEET_ID_CACHE['student_id_002']
    else:
        print("student_id_002 already exists.")

    # 3. Verify student_id_002
    print("\n--- Checking student_id_002 ---")
    sheet_id_2 = get_spreadsheet_id('student_id_002')
    print(f"Spreadsheet ID for student_id_002: {sheet_id_2}")
    
    if sheet_id_2:
        tasks_2 = get_tasks('student_id_002')
        print(f"Tasks found for student_id_002: {len(tasks_2)}")
    else:
        print("FAILED: student_id_002 not found.")

    # 4. Verify Unknown User
    print("\n--- Checking unknown_user ---")
    sheet_id_unknown = get_spreadsheet_id('unknown_user')
    print(f"Spreadsheet ID for unknown_user: {sheet_id_unknown}")
    if sheet_id_unknown is None:
        print("SUCCESS: unknown_user currently returns None as expected.")
    else:
        print("WARNING: unknown_user returned an ID?")

if __name__ == "__main__":
    verify_multi_user()
