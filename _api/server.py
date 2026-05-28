# -*- coding: utf-8 -*-
"""
霖楓學苑 LF AI API Server v1.0
Flask REST API 服務 — 連接 lf_ai_brain.py 引擎到前端
使用方式: python _api/server.py
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'engines'))

# Fix GBK encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify
from flask_cors import CORS

# Import AI engine
from lf_ai_brain import (
    ai_semantic_mark,
    ai_generate_hints,
    ai_analyze_student,
    ai_daily_summary,
    ai_detect_misconceptions,
    ai_generate_question,
    check_health
)

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Firebase hosting

# ═══════════════════════════════════
# API 端點
# ═══════════════════════════════════

@app.route('/')
def index():
    return jsonify({
        "service": "LF AI API",
        "version": "1.0",
        "status": "online",
        "endpoints": {
            "GET /health": "健康檢查",
            "POST /api/mark": "語意批改: {student_answer, model_answer, question, max_score}",
            "POST /api/hints": "蘇格拉底提示: {question, model_answer}",
            "POST /api/analyze": "學生分析: {student_name, progress_data}",
            "POST /api/report": "家長日報: {student_name, today_data}",
            "POST /api/misconceptions": "錯誤分析: {student_name, errors}",
            "POST /api/generate": "智能出題: {topic, difficulty}"
        }
    })

@app.route('/health')
def health():
    """健康檢查端點"""
    try:
        h = check_health()
        return jsonify({"status": "ok", "engine": "lf_ai_brain", "health": h})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/mark', methods=['POST'])
def api_mark():
    """AI 語意批改"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "需要JSON body"}), 400
    
    student_answer = data.get('student_answer', '')
    model_answer = data.get('model_answer', '')
    question = data.get('question', '')
    max_score = data.get('max_score', 5)
    
    if not student_answer or not model_answer:
        return jsonify({"error": "需要 student_answer 和 model_answer"}), 400
    
    try:
        result = ai_semantic_mark(student_answer, model_answer, question, max_score)
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/hints', methods=['POST'])
def api_hints():
    """AI 蘇格拉底式提示"""
    data = request.get_json()
    question = data.get('question', '') if data else ''
    model_answer = data.get('model_answer', '') if data else ''
    
    try:
        hints = ai_generate_hints(question, model_answer)
        return jsonify({"status": "ok", "hints": hints})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """AI 學生認知分析"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "需要JSON body"}), 400
    
    student_name = data.get('student_name', '')
    progress_data = data.get('progress_data', [])
    
    try:
        analysis = ai_analyze_student(student_name, progress_data)
        return jsonify({"status": "ok", "analysis": analysis})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/report', methods=['POST'])
def api_report():
    """AI 家長日報生成"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "需要JSON body"}), 400
    
    student_name = data.get('student_name', '')
    today_data = data.get('today_data', {})
    
    try:
        summary = ai_daily_summary(student_name, today_data)
        return jsonify({"status": "ok", "summary": summary})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/misconceptions', methods=['POST'])
def api_misconceptions():
    """AI 錯誤模式分析"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "需要JSON body"}), 400
    
    student_name = data.get('student_name', '')
    errors = data.get('errors', [])
    
    try:
        result = ai_detect_misconceptions(student_name, errors)
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """AI 智能出題"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "需要JSON body"}), 400
    
    topic = data.get('topic', '')
    difficulty = data.get('difficulty', 3)
    
    try:
        question = ai_generate_question(topic, difficulty)
        return jsonify({"status": "ok", "question": question})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/batch-hints', methods=['POST'])
def api_batch_hints():
    """批量提示生成（供課堂副駕駛使用）"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "需要JSON body"}), 400
    
    questions = data.get('questions', [])
    results = []
    
    for q in questions:
        try:
            hints = ai_generate_hints(q.get('question',''), q.get('answer',''))
            results.append({"question": q.get('question',''), "hints": hints})
        except:
            results.append({"question": q.get('question',''), "hints": ["分析暫時不可用"]})
    
    return jsonify({"status": "ok", "results": results})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🍁 LF AI API Server v1.0")
    print(f"   Listen on: http://0.0.0.0:{port}")
    print(f"   Engine: lf_ai_brain.py")
    print(f"   Endpoints: /health, /api/mark, /api/hints, /api/analyze, /api/report, /api/misconceptions, /api/generate")
    app.run(host='0.0.0.0', port=port, debug=False)
