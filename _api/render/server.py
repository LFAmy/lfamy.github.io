# -*- coding: utf-8 -*-
"""
霖楓學苑 LF AI API Server v2.0 — Cloud Edition
適用於 Render/Railway 雲端部署
"""
import sys, os, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add engines path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'engines'))

from flask import Flask, request, jsonify
from flask_cors import CORS

# Import AI engine (with graceful fallback)
try:
    from lf_ai_brain import (
        ai_semantic_mark, ai_generate_hints, ai_analyze_student,
        ai_daily_summary, ai_detect_misconceptions, ai_generate_question, check_health
    )
    ENGINE_LOADED = True
    print("[API] lf_ai_brain.py loaded")
except Exception as e:
    print(f"[API] WARNING: lf_ai_brain import failed: {e}")
    ENGINE_LOADED = False
    
    # Fallback stubs
    def check_health(): return {"frellmapi": "unavailable", "fallback": "cloud_mode"}
    def ai_semantic_mark(s, m, q, mx): return {"status": "CORRECT" if s.strip() == m.strip() else "WRONG", "confidence": 0.9}
    def ai_generate_hints(q, a): return ["請嘗試思考這道題目涉及的數學概念。", "試著從已知條件開始推理。"]
    def ai_analyze_student(n, p): return {"weak_concepts": [], "strength_concepts": [], "learning_style": "待分析"}
    def ai_daily_summary(n, d): return f"{n} 今天努力學習了！繼續保持。"
    def ai_detect_misconceptions(n, e): return {"patterns": [], "root_cause": "分析暫時不可用"}
    def ai_generate_question(t, d): return {"question": f"請練習 {t} 相關題目", "answer": "請參考筆記"}

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        "service": "LF AI API v2.0 (Cloud)",
        "version": "2.0",
        "status": "online",
        "engine_loaded": ENGINE_LOADED,
        "endpoints": ["/health", "/api/mark", "/api/hints", "/api/analyze", "/api/report", "/api/misconceptions", "/api/generate"]
    })

@app.route('/health')
def health():
    try:
        h = check_health()
        return jsonify({"status": "ok", "engine": "lf_ai_brain", "health": h, "mode": "cloud"})
    except:
        return jsonify({"status": "ok", "engine": "fallback", "mode": "cloud"}), 200

@app.route('/api/mark', methods=['POST'])
def api_mark():
    data = request.get_json()
    if not data: return jsonify({"error": "need JSON"}), 400
    try:
        r = ai_semantic_mark(data.get('student_answer',''), data.get('model_answer',''), data.get('question',''), data.get('max_score',5))
        return jsonify({"status": "ok", "result": r})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/hints', methods=['POST'])
def api_hints():
    data = request.get_json()
    q = (data or {}).get('question', '')
    a = (data or {}).get('model_answer', '')
    try:
        hints = ai_generate_hints(q, a)
        return jsonify({"status": "ok", "hints": hints})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json()
    if not data: return jsonify({"error": "need JSON"}), 400
    try:
        r = ai_analyze_student(data.get('student_name',''), data.get('progress_data',[]))
        return jsonify({"status": "ok", "analysis": r})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/report', methods=['POST'])
def api_report():
    data = request.get_json()
    if not data: return jsonify({"error": "need JSON"}), 400
    try:
        s = ai_daily_summary(data.get('student_name',''), data.get('today_data',{}))
        return jsonify({"status": "ok", "summary": s})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/misconceptions', methods=['POST'])
def api_misconceptions():
    data = request.get_json()
    if not data: return jsonify({"error": "need JSON"}), 400
    try:
        r = ai_detect_misconceptions(data.get('student_name',''), data.get('errors',[]))
        return jsonify({"status": "ok", "result": r})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.get_json()
    if not data: return jsonify({"error": "need JSON"}), 400
    try:
        q = ai_generate_question(data.get('topic',''), data.get('difficulty',3))
        return jsonify({"status": "ok", "question": q})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"LF AI API v2.0 Cloud | port={port} | engine={'loaded' if ENGINE_LOADED else 'fallback'}")
    app.run(host='0.0.0.0', port=port, debug=False)
