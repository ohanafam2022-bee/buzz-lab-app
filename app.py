from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import os
import sheets_handler

app = Flask(__name__, template_folder='templates', static_folder='static')
# Secure secret key (in production, use env var)
app.secret_key = os.environ.get('SECRET_KEY', 'default_dev_secret_key')
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
    # Redirect root to dashboard (which will redirect to login if needed)
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        
        # Verify if student exists
        config = sheets_handler.get_student_config(student_id)
        if config:
            # Login Success
            session['student_id'] = student_id
            session['student_name'] = config.get('name', 'Unknown')
            return redirect(url_for('dashboard'))
        else:
            # Login Failed
            return render_template('login.html', error="IDが見つかりません。正しい生徒IDを入力してください。")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    # Auth Check
    if 'student_id' not in session:
        return redirect(url_for('login'))
        
    student_id = session['student_id']
    student_name = session.get('student_name', 'Student')
    
    # Pass student_id and student_name to template
    return render_template('dashboard.html', student_id=student_id, student_name=student_name)

@app.route('/api/progress', methods=['GET'])
def get_progress():
    # API Protection
    # We rely on session.
    student_id = session.get('student_id')
    
    if not student_id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    # Get Tasks
    tasks = sheets_handler.get_tasks(student_id)
    
    # Get User Info (Goals, etc.)
    user_info = sheets_handler.get_user_info(student_id)
    
    return jsonify({
        "name": user_info.get("mentor", "Buzz Student"), 
        "tasks": tasks,
        "user_info": user_info
    })

@app.route('/api/progress', methods=['POST'])
def update_progress():
    if 'student_id' not in session:
         return jsonify({"status": "error", "message": "Unauthorized"}), 401
         
    data = request.json
    student_id = session['student_id']
    task_id = data.get('task_id')
    status = data.get('status')
    
    success = sheets_handler.update_task_status(student_id, task_id, status)
    
    if success:
        return jsonify({"status": "success", "message": "Progress updated"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to update"}), 500

@app.route('/api/question', methods=['POST'])
def submit_question():
    if 'student_id' not in session:
         return jsonify({"status": "error", "message": "Unauthorized"}), 401
         
    data = request.json
    student_id = session['student_id']
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
