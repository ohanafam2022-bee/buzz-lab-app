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
    return render_template('dashboard.html')

@app.route('/api/progress', methods=['GET'])
def get_progress():
    user_id = "student_id_001"
    
    # Get Tasks
    tasks = sheets_handler.get_tasks(user_id)
    
    # Get User Info (Goals, etc.)
    user_info = sheets_handler.get_user_info(user_id)
    
    return jsonify({
        "name": user_info.get("mentor", "Buzz Student"), # Use mentor name as student name placeholder for now? Or just "Buzz Student"
        "tasks": tasks,
        "user_info": user_info
    })

@app.route('/api/progress', methods=['POST'])
def update_progress():
    data = request.json
    user_id = "student_id_001" 
    task_id = data.get('task_id')
    status = data.get('status')
    
    success = sheets_handler.update_task_status(user_id, task_id, status)
    
    if success:
        return jsonify({"status": "success", "message": "Progress updated"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to update"}), 500

@app.route('/api/question', methods=['POST'])
def submit_question():
    data = request.json
    user_id = "student_id_001"
    question = data.get('question')
    
    if not question:
        return jsonify({"status": "error", "message": "Question is empty"}), 400
        
    success = sheets_handler.submit_question(user_id, question)
    
    if success:
        return jsonify({"status": "success", "message": "Question submitted"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to submit"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8081, host='0.0.0.0')
