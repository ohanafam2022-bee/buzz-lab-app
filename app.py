from flask import Flask, render_template, jsonify, request
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

# Mock Database (In-memory for now, will replace with Google Sheets later)
PROGRESS_DB = {
    "student_id_001": {
        "name": "Buzz Student",
        "tasks": [
            {"id": 1, "title": "オリエンテーション視聴", "completed": True},
            {"id": 2, "title": "第1回課題提出", "completed": False},
            {"id": 3, "title": "第2回課題提出", "completed": False},
            {"id": 4, "title": "中間面談", "completed": False},
            {"id": 5, "title": "最終課題提出", "completed": False}
        ]
    }
}

import sheets_handler

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    student_id = request.args.get('student_id', 'student_id_001') # Default to 001 for now
    return render_template('dashboard.html', student_id=student_id)

@app.route('/api/progress', methods=['GET'])
def get_progress():
    student_id = request.args.get('student_id', 'student_id_001')
    
    # Get Tasks
    tasks = sheets_handler.get_tasks(student_id)
    
    # Get User Info (Goals, etc.)
    user_info = sheets_handler.get_user_info(student_id)
    
    return jsonify({
        "name": user_info.get("mentor", "Buzz Student"), # Mentor name as student name or separate?
        # Actually user_info might have name if we add it to Master, but for now user_info comes from sheet
        "tasks": tasks,
        "user_info": user_info
    })

@app.route('/api/progress', methods=['POST'])
def update_progress():
    data = request.json
    # student_id should be passed in body or query. Let's expect body.
    student_id = data.get('student_id', 'student_id_001')
    task_id = data.get('task_id')
    status = data.get('status')
    
    success = sheets_handler.update_task_status(student_id, task_id, status)
    
    if success:
        return jsonify({"status": "success", "message": "Progress updated"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to update"}), 500

@app.route('/api/question', methods=['POST'])
def submit_question():
    data = request.json
    student_id = data.get('student_id', 'student_id_001')
    question = data.get('question')
    
    if not question:
        return jsonify({"status": "error", "message": "Question is empty"}), 400
        
    success = sheets_handler.submit_question(student_id, question)
    
    if success:
        return jsonify({"status": "success", "message": "Question submitted"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to submit"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8081, host='0.0.0.0')
