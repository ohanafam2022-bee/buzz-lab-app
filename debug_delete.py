from sheets_handler import delete_student
import traceback

student_id = 'test_student_1770490825'

print(f"Attempting to delete {student_id}...")
try:
    result = delete_student(student_id)
    print(f"Result: {result}")
except Exception:
    traceback.print_exc()
