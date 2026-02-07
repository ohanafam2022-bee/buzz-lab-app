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
    print("\n--- Checking student_id_002 (Hyperlink Verification) ---")
    # SKIPPING WRITE to preserve Hyperlinks
    # service = get_service()
    
    # ... (omitted write logic) ...

    # Invalidate cache
    from sheets_handler import STUDENT_CONFIG_CACHE
    if 'student_id_002' in STUDENT_CONFIG_CACHE:
        del STUDENT_CONFIG_CACHE['student_id_002']

    # 3. Verify student_id_002 Config
    print("\n--- Checking student_id_002 ---")
    config_2 = get_student_config('student_id_002')
    print(f"Config for student_id_002: {config_2}")
    
    if config_2 and config_2.get('sheet_name') == '行動管理②':
        print("SUCCESS: correctly retrieved custom sheet name.")
        # We expect get_tasks to SUCCEED now because the sheet exists!
        tasks_2 = get_tasks('student_id_002')
        print(f"Tasks found for student_id_002: {len(tasks_2)}")
    else:
        print("FAILED: student_id_002 config incorrect.")

if __name__ == "__main__":
    verify_multi_user()
