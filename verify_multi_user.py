from sheets_handler import get_student_config, get_tasks, get_service, SPREADSHEET_ID

def verify_multi_user():
    print("Verifying Multi-User Support (Tab-based)...")
    
    # 1. Verify student_id_001 (Should exist)
    print("\n--- Checking student_id_001 ---")
    config_1 = get_student_config('student_id_001')
    print(f"Config for student_id_001: {config_1}")
    
    if config_1:
        tasks_1 = get_tasks('student_id_001')
        print(f"Tasks found for student_id_001: {len(tasks_1)}")
    else:
        print("FAILED: student_id_001 not found.")

    # 2. Add student_id_002 to Master if not exists (for testing)
    print("\n--- Setting up student_id_002 (Test User) ---")
    service = get_service()
    
    # Always overwrite student_id_002 for testing
    print("Updating/Adding student_id_002 to Master sheet with Custom Sheet Name...")
    
    # First delete if exists (simplest way to ensure clean state for this test script)
    # Actually, let's just Append a defined row and rely on logic to pick the first one? 
    # No, sheets_handler picks the first match. If an old row is first, it picks that.
    # So we MUST update the EXISTING row.
    
    # Read Master sheet to find row index
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Master!A:A').execute()
    rows = result.get('values', [])
    row_index = -1
    for i, row in enumerate(rows):
        if len(row) > 0 and row[0] == 'student_id_002':
            row_index = i + 1
            break
            
    if row_index != -1:
        # Use valid existing sheet "行動管理① のコピー" for testing
        values = [['student_id_002', SPREADSHEET_ID, 'Test User 2', '行動管理① のコピー']]
        body = {'values': values}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Master!A{row_index}:D{row_index}',
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f"Updated Master sheet row {row_index}.")
    else:
        values = [['student_id_002', SPREADSHEET_ID, 'Test User 2', '行動管理① のコピー']]
        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Master!A:D',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        print("Appended new row.")

    # Invalidate cache
    from sheets_handler import STUDENT_CONFIG_CACHE
    if 'student_id_002' in STUDENT_CONFIG_CACHE:
        del STUDENT_CONFIG_CACHE['student_id_002']

    # 3. Verify student_id_002 Config
    print("\n--- Checking student_id_002 ---")
    config_2 = get_student_config('student_id_002')
    print(f"Config for student_id_002: {config_2}")
    
    if config_2 and config_2.get('sheet_name') == '行動管理① のコピー':
        print("SUCCESS: correctly retrieved custom sheet name.")
        # We expect get_tasks to SUCCEED now because the sheet exists!
        tasks_2 = get_tasks('student_id_002')
        print(f"Tasks found for student_id_002: {len(tasks_2)}")
    else:
        print("FAILED: student_id_002 config incorrect.")

if __name__ == "__main__":
    verify_multi_user()
