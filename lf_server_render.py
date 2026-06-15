#!/usr/bin/env python3
"""
LF Academy Render Server - Production API
Deploy: Render Web Service | DB: DATABASE_URL env var
"""
import sys, os, io, json, re, random, urllib.request
from pathlib import Path


from flask import Flask, jsonify, request, send_from_directory
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

app = Flask(__name__)

if CORS_AVAILABLE:
    CORS(app)

# === Database ===
def get_db():
    import psycopg2
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url:
        # Add 5s timeout for production stability
        if "?" in db_url:
            return psycopg2.connect(db_url + "&connect_timeout=5")
        return psycopg2.connect(db_url + "?connect_timeout=5")
    # Fallback to local
    return psycopg2.connect("host='localhost' dbname='question_bank' user='postgres' password='postgres' connect_timeout=3")

# === Load AI Engines ===
try:
    from engines.mark_engine import mark_with_feedback
    from engines.adaptive_engine import get_next_question
    from engines.tutor_engine import get_hint, generate_hints, socratic_chat, adaptive_hint_branch, validate_reasoning, generate_session_summary
    from engines.socratic_session import create_session, get_session, end_session, active_sessions
    from engines.payment_engine import create_checkout_session, get_checkout_session, handle_webhook, get_plans, get_plan_by_grade, create_trial_membership, check_membership_status
    from engines.lf_ai_brain import ai_tutor_chat, ai_tutor_solve
    from engines.misconception_engine import detect_misconceptions
    from engines.ai_orchestrator import smart_pipeline
    from engines.gamification import update_gamification, get_leaderboard, get_badge
    from engines.class_analytics import get_class_heatmap, get_class_summary, get_student_matrix
    from engines.content_sync import get_sync_status, mark_synced, scan_changes
    from engines.mab_flowzone import get_flowzone_recommendation
    GAMIFICATION_ACTIVE = True
    ENGINES_LOADED = True
except Exception as e:
    print(f"[WARN] Engines import failed: {e}, trying direct import...")
    try:
        from mark_engine import mark_with_feedback
        from adaptive_engine import get_next_question
        from tutor_engine import get_hint, generate_hints
        from misconception_engine import detect_misconceptions
        from ai_orchestrator import smart_pipeline
        from gamification import update_gamification, get_leaderboard, get_badge
        from class_analytics import get_class_heatmap, get_class_summary, get_student_matrix
        from content_sync import get_sync_status, mark_synced, scan_changes
        from mab_flowzone import get_flowzone_recommendation
        GAMIFICATION_ACTIVE = True
        ENGINES_LOADED = True
    except Exception as e2:
        print(f"[WARN] Direct import also failed: {e2}")
        ENGINES_LOADED = False
    def mark_with_feedback(*a,**kw): return {"status":"ERROR","message":"Engine offline"}
    def get_next_question(*a,**kw): return {}
    def get_hint(*a,**kw): return ""
    def generate_hints(*a,**kw): return ["請嘗試從已知條件推理"]
    def detect_misconceptions(*a,**kw): return {"weak_areas":[]}
    def smart_pipeline(*a,**kw): return {"error":"Engine offline"}
    GAMIFICATION_ACTIVE = False
    def update_gamification(*a,**kw): return {}
    def get_leaderboard(*a,**kw): return []
    def get_badge(*a,**kw): return ""
    def get_class_heatmap(*a,**kw): return {}
    def get_class_summary(*a,**kw): return {}
    def get_student_matrix(*a,**kw): return {}
    def get_sync_status(*a,**kw): return {}
    def mark_synced(*a,**kw): return {}
    def scan_changes(*a,**kw): return {}
    def get_flowzone_recommendation(*a,**kw): return {}

try:
    from engines.lf_ai_brain import ai_daily_summary, ai_analyze_student, ai_generate_question, check_health
    AI_BRAIN = True
except:
    try:
        from lf_ai_brain import ai_daily_summary, ai_analyze_student, ai_generate_question, check_health
        AI_BRAIN = True
    except:
        AI_BRAIN = False
        def ai_daily_summary(*a,**kw): return "AI service unavailable"
        def ai_analyze_student(*a,**kw): return {}
        def ai_generate_question(*a,**kw): return {}
        def check_health(): return {"frellmapi":"offline"}

# Config
from _config.secrets import FRELLMAPI_KEY
FRELLMAPI_URL = os.environ.get("FRELLMAPI_URL", "https://watches-organized-mission-vision.trycloudflare.com/v1")

# === Free AI Providers (0 cost, works from Render) ===
# Setup: Set GEMINI_API_KEY or CF_ACCOUNT_ID+CF_API_TOKEN in Render env vars
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "")
CF_API_TOKEN = os.environ.get("CF_API_TOKEN", "")

def call_gemini_free(prompt, system_prompt="", max_tokens=512, timeout=12):
    """Google Gemini free tier - great Chinese support, 15 RPM"""
    if not GEMINI_API_KEY:
        return ""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": system_prompt}]})
            contents.append({"role": "model", "parts": [{"text": "OK"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        body = json.dumps({"contents": contents, "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    except Exception as e:
        print(f"[FreeAI] Gemini: {e}", file=sys.stderr)
        return ""

def call_cf_workers_ai(prompt, system_prompt="", max_tokens=512, timeout=15):
    """Cloudflare Workers AI free tier - 10K requests/day"""
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        return ""
    try:
        url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/deepseek-ai/deepseek-r1-distill-qwen-32b"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = json.dumps({"messages": messages, "max_tokens": max_tokens}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CF_API_TOKEN}"
        })
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("result", {}).get("response", "")
    except Exception as e:
        print(f"[FreeAI] CF: {e}", file=sys.stderr)
        return ""

def call_frellmapi_remote(prompt, system_prompt="", max_tokens=512, timeout=12):
    """Call frellmapi when exposed via Cloudflare Tunnel/ngrok. FRELLMAPI_URL must be set."""
    if not FRELLMAPI_URL or "localhost" in FRELLMAPI_URL:
        return ""
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = json.dumps({
            "model": "auto",
            "messages": messages,
            "max_tokens": max_tokens
        }).encode("utf-8")
        url = FRELLMAPI_URL.rstrip("/") + "/chat/completions"
        headers = {"Content-Type": "application/json"}
        if FRELLMAPI_KEY:
            headers["Authorization"] = "Bearer " + FRELLMAPI_KEY
        req = urllib.request.Request(url, data=body, headers=headers)
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"[FreeAI] frellmapi remote: {e}", file=sys.stderr)
        return ""

def call_free_ai(prompt, system_prompt="", max_tokens=512):
    """Try frellmapi -> Gemini -> CF Workers -> return empty"""
    # Step 1: frellmapi (aggregates 12 free providers, 99 models)
    result = call_frellmapi_remote(prompt, system_prompt, max_tokens)
    if result:
        return result
    # Step 2: Google Gemini free tier
    result = call_gemini_free(prompt, system_prompt, max_tokens)
    if result:
        return result
    # Step 3: Cloudflare Workers AI
    result = call_cf_workers_ai(prompt, system_prompt, max_tokens)
    if result:
        return result
    return ""

def generate_socratic_response(message, topic=""):
    """Socratic tutor response using free AI"""
    system = """You are an AI Math Tutor for Hong Kong primary students (P3-P6). Use Socratic dialogue. Rules:
1. Ask ONE guiding question only, give clear step-by-step teaching. ALWAYS explain the concept with examples
2. If student is correct, encourage and ask next step
3. If student is wrong, don't say 'wrong', guide them to rethink
4. Use Traditional Chinese with HK Cantonese style
5. If student asks non-math, politely redirect to math
6. Be encouraging and suitable for primary schoolers"""

    prompt_text = f"Topic: {topic if topic else 'Primary Math'}\nStudent: {message}\nGive a clear teaching response in HK-style Traditional Chinese with steps and examples:"

    result = call_free_ai(prompt_text, system, max_tokens=300)
    if result:
        return result
    # Local fallback
    fallbacks = [
        "好問題！等我解釋俾你聽。先睇題目數字，再揀正確方法計算！",
        "明白！我教你點解呢類題目。首先睇清楚題目問咩，然後逐步計！",
        "數學題可以拆開步驟做。先找出關鍵數字，再選擇正確公式！",
        "我解釋你聽！呢類題目有固定解法。先找出已知條件，再應用公式！",
        "圖像化係好方法！等我示範俾你睇點樣用圖解理解呢類題目！",
    ]
    import random as _random
    return _random.choice(fallbacks)

# ==================== TOPIC BROWSER APIs ====================
@app.route("/api/topics")
def api_topics():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT form, topic, COUNT(*) as cnt,
                   COUNT(*) FILTER (WHERE answer IS NOT NULL AND answer != '') as ans
            FROM questions GROUP BY form, topic ORDER BY form, cnt DESC
        """)
        rows = cur.fetchall()
        conn.close()
        topics = {}
        for form, topic, count, answered in rows:
            f = form or "S1"
            if f not in topics: topics[f] = []
            topics[f].append({
                "topic": topic or "general",
                "question_count": count,
                "answered_count": answered,
                "display_name": (topic or "general").replace("_", " ").title()
            })
        return jsonify({"topics": topics, "total_forms": len(topics)})
    except Exception as e:
        return jsonify({"error": str(e)[:200]}), 500

@app.route("/api/question/<int:qid>")
def api_get_question(qid):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, question_text, answer, topic, form, difficulty, marks
            FROM questions WHERE id = %s
        """, (qid,))
        row = cur.fetchone()
        conn.close()
        if not row: return jsonify({"error": "Not found"}), 404
        return jsonify({
            "id": row[0], "question_text": row[1], "answer": row[2],
            "topic": row[3], "form": row[4], "difficulty": row[5] or "medium",
            "marks": row[6] or 5
        })
    except Exception as e:
        return jsonify({"error": str(e)[:200]}), 500

@app.route("/api/questions/random", methods=["POST"])
def api_random_question():
    data = request.get_json() or {}
    topic = data.get("topic")
    form = data.get("form")
    try:
        conn = get_db()
        cur = conn.cursor()
        query = """SELECT id, question_text, answer, topic, form, difficulty, question_type, marks
                   FROM questions WHERE answer IS NOT NULL AND answer != %s"""
        params = [""]
        if topic:
            query += " AND topic = %s"
            params.append(topic)
        if form:
            query += " AND form = %s"
            params.append(form)
        query += " ORDER BY RANDOM() LIMIT 1"
        cur.execute(query, params)
        row = cur.fetchone()
        conn.close()
        if not row: return jsonify({"error": "No question found"}), 404
        return jsonify({
            "id": row[0], "question_text": row[1], "answer": row[2],
            "topic": row[3], "form": row[4], "difficulty": row[5] or "medium",
            "question_type": row[6], "marks": row[7] or 5
        })
    except Exception as e:
        return jsonify({"error": str(e)[:200]}), 500

# ==================== AI MATH APIs ====================
@app.route("/api/ai/tutor/hint", methods=["POST"])
def api_tutor():
    data = request.get_json()
    try:
        hints = generate_hints(data.get("question",""), data.get("student_answer",""))
        level = min(data.get("hint_level", 1), len(hints))
        return jsonify({"hints": hints, "current": hints[level-1] if hints else "", "level": level})
    except Exception as e:
        return jsonify({"hints": ["試下從已知條件開始推理"], "current": "試下從已知條件開始推理", "level": 1})

@app.route("/api/ai/mark", methods=["POST"])
def api_mark():
    data = request.get_json()
    qid = data.get("question_id")
    if not qid:
        return jsonify({"error": "question_id required"}), 400
    try:
        conn = get_db()
        result = mark_with_feedback(data.get("student_answer",""), int(qid))
        # Gamification hook
        student_name = data.get("student", "anonymous")
        is_correct = result.get("status") == "CORRECT"
        try:
            game_result = update_gamification(student_name, is_correct, conn)
            result["gamification"] = game_result
        except Exception:
            pass
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/ai/smart", methods=["POST"])
def api_smart():
    data = request.get_json()
    qid = data.get("question_id")
    if not qid:
        return jsonify({"error": "question_id required"}), 400
    try:
        conn = get_db()
        result = smart_pipeline(
            data.get("student", "anonymous"),
            int(qid),
            data.get("student_answer", ""),
            conn
        )
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

# === Gamification API (v7.0 Activated) ===
@app.route("/api/gamification/status/<student>")
def api_gamification_status(student):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT points, streak, badge, last_played, daily_date, daily_correct, daily_bonus_claimed FROM gamification WHERE student_name = %s",
            (student,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return jsonify({
                "student_name": student,
                "points": row[0], "streak": row[1], "badge": row[2],
                "last_played": str(row[3]) if row[3] else None,
                "daily_correct": row[5], "daily_bonus_claimed": row[6]
            })
        return jsonify({"student_name": student, "points": 0, "streak": 0, "badge": "🥉 銅章", "new_student": True})
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/gamification/leaderboard")
def api_leaderboard():
    try:
        conn = get_db()
        lb = get_leaderboard(conn, limit=20)
        conn.close()
        return jsonify({"leaderboard": lb, "total": len(lb)})
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/gamification/badge-history/<student>")
def api_badge_history(student):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT sp.created_at, sp.score, sp.status, q.topic FROM student_progress sp JOIN questions q ON sp.question_id = q.id WHERE sp.student_name = %s ORDER BY sp.created_at DESC LIMIT 50",
            (student,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        history = [{"date": str(r[0]), "score": float(r[1] or 0), "status": r[2], "topic": r[3]} for r in rows]
        return jsonify({"student_name": student, "recent_activity": history, "count": len(history)})
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

# === Class Analytics API (v7.0) ===
# === Content Sync API (v7.0) ===
@app.route("/api/content/sync-status")
def api_sync_status():
    try:
        status = get_sync_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/content/mark-synced", methods=["POST"])
def api_mark_synced():
    try:
        result = mark_synced()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

# === BKT: Bayesian Knowledge Tracking (v7.0) ===
@app.route("/api/ai/bkt/<student>")
def api_bkt(student):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT q.topic,
                   COUNT(*) FILTER (WHERE sp.status='CORRECT') as correct,
                   COUNT(*) as total
            FROM student_progress sp
            JOIN questions q ON sp.question_id = q.id
            WHERE sp.student_name = %s
            GROUP BY q.topic
        """, (student,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        bkt = {}
        for topic, correct, total in rows:
            p_learned = (correct + 1) / (total + 2)  # Laplace smoothing
            if total < 3:
                confidence = "low"
            elif total < 8:
                confidence = "medium"
            else:
                confidence = "high"
            bkt[topic] = {
                "topic": topic,
                "correct": correct, "total": total,
                "p_mastery": round(p_learned, 3),
                "confidence": confidence,
                "recommendation": "mastered" if p_learned > 0.85 else "practice" if p_learned > 0.6 else "relearn"
            }
        
        return jsonify({"student": student, "knowledge_tracking": bkt, "topics": len(bkt)})
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

# === Spaced Repetition System (v7.0) ===
@app.route("/api/ai/spaced-review/<student>")
def api_spaced_review(student):
    try:
        conn = get_db()
        cur = conn.cursor()
        # Get topics practiced and their last practice date
        cur.execute("""
            SELECT q.topic, MAX(sp.created_at) as last_practice,
                   AVG(CASE WHEN sp.status='CORRECT' THEN 1.0 ELSE 0.0 END) as accuracy
            FROM student_progress sp
            JOIN questions q ON sp.question_id = q.id
            WHERE sp.student_name = %s
            GROUP BY q.topic
            ORDER BY last_practice ASC
        """, (student,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        from datetime import datetime, timedelta
        now = datetime.now()
        review_queue = []
        
        for topic, last_practice, accuracy in rows:
            days_since = (now - last_practice).days if last_practice else 999
            acc = float(accuracy) if accuracy else 0.5
            
            # Ebbinghaus spacing: harder = review sooner
            if acc < 0.5:
                interval = 1  # 1 day
            elif acc < 0.7:
                interval = 3  # 3 days
            elif acc < 0.85:
                interval = 7  # 1 week
            else:
                interval = 14  # 2 weeks
            
            due = days_since >= interval
            review_queue.append({
                "topic": topic,
                "accuracy": round(acc * 100, 1),
                "last_practice": str(last_practice)[:10] if last_practice else None,
                "days_since": days_since,
                "review_interval_days": interval,
                "due": due,
                "urgency": "now" if due and acc < 0.5 else "soon" if due else "ok"
            })
        
        return jsonify({"student": student, "review_queue": review_queue, "total": len(review_queue)})
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

# === AI Exam Generator (v7.0) ===
@app.route("/api/ai/generate-exam", methods=["POST"])
def api_generate_exam():
    try:
        data = request.get_json()
        topic = data.get("topic", "")
        difficulty = data.get("difficulty", 3)
        count = data.get("count", 10)
        trap_ratio = data.get("trap_ratio", 0.3)
        
        conn = get_db()
        cur = conn.cursor()
        
        # Get questions from DB
        trap_count = max(1, int(count * trap_ratio))
        normal_count = count - trap_count
        
        cur.execute("""
            SELECT id, question_text, answer, topic, difficulty, question_type
            FROM questions
            WHERE topic ILIKE %s
            ORDER BY RANDOM() LIMIT %s
        """, (f"%{topic}%", normal_count))
        normal_qs = cur.fetchall()
        
        # Get variants for trap questions
        cur.execute("""
            SELECT v.id, v.question_text, v.answer, v.topic, v.difficulty, v.variant_type
            FROM variants v
            WHERE v.topic ILIKE %s
            ORDER BY RANDOM() LIMIT %s
        """, (f"%{topic}%", trap_count))
        trap_qs = cur.fetchall()
        
        cur.close()
        conn.close()
        
        questions = []
        for q in normal_qs:
            questions.append({
                "id": q[0], "text": q[1], "answer": q[2],
                "topic": q[3], "difficulty": q[4], "type": q[5],
                "is_trap": False
            })
        for q in trap_qs:
            questions.append({
                "id": q[0], "text": q[1], "answer": q[2],
                "topic": q[3], "difficulty": q[4], "type": q[5],
                "is_trap": True
            })
        
        import random
        random.shuffle(questions)
        
        return jsonify({
            "exam_title": f"LF Academy {topic} Test",
            "topic": topic,
            "total_questions": len(questions),
            "trap_questions": trap_count,
            "difficulty": difficulty,
            "questions": questions,
        })
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

# === MAB Flow-Zone API (v7.0) ===
@app.route("/api/ai/flowzone/<student>")
def api_flowzone(student):
    try:
        conn = get_db()
        result = get_flowzone_recommendation(student, conn)
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/class/heatmap")
def api_class_heatmap():
    try:
        conn = get_db()
        grade = request.args.get("grade")
        heatmap = get_class_heatmap(conn, grade_filter=grade)
        conn.close()
        return jsonify({"heatmap": heatmap, "topics": len(heatmap)})
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/class/summary")
def api_class_summary():
    try:
        conn = get_db()
        grade = request.args.get("grade")
        summary = get_class_summary(conn, grade_filter=grade)
        conn.close()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/class/student-matrix")
def api_student_matrix():
    try:
        conn = get_db()
        grade = request.args.get("grade")
        matrix = get_student_matrix(conn, grade_filter=grade)
        conn.close()
        return jsonify(matrix)
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/ai/diagnose/<student>")
def api_diagnose(student):
    try:
        conn = get_db()
        result = detect_misconceptions(student, conn)
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/ai/parent/<student>")
def api_parent_briefing(student):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) as total,
                   COUNT(*) FILTER (WHERE status='CORRECT') as correct,
                   AVG(score) as avg_score
            FROM student_progress
            WHERE student_name = %s AND created_at::date = CURRENT_DATE
        """, (student,))
        row = cur.fetchone()
        today_total = row[0] or 0
        today_correct = row[1] or 0
        today_avg = float(row[2]) if row[2] else 0
        diag = detect_misconceptions(student, conn)
        weak_areas = diag.get("weak_areas", [])
        summary = ai_daily_summary(student, today_total, today_correct, weak_areas)
        conn.close()
        return jsonify({
            "student": student,
            "today": {"total": today_total, "correct": today_correct, "avg_score": round(today_avg, 1)},
            "weak_areas": weak_areas,
            "ai_summary": summary,
            "ai_powered": AI_BRAIN
        })
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/ai/learning-path/<student>")
def api_learning_path(student):
    try:
        conn = get_db()
        diag = detect_misconceptions(student, conn)
        weak = diag.get("weak_areas", ["algebra"])
        conn.close()
        return jsonify({
            "student": student,
            "weak_areas": weak,
            "suggested_path": [{"topic": w, "priority": i+1} for i, w in enumerate(weak[:5])]
        })
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/ai/generate-question", methods=["POST"])
def api_generate_question():
    data = request.get_json()
    topic = data.get("topic", "Algebra")
    difficulty = data.get("difficulty", "medium")
    try:
        q = ai_generate_question(topic, difficulty)
        return jsonify(q if q else {"question": "AI generation offline", "answer": ""})
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@app.route("/api/ai/cognitive-model/<student>")
def api_cognitive_model(student):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT q.topic, sp.score, sp.max_score, sp.status, sp.created_at
            FROM student_progress sp
            JOIN questions q ON sp.question_id = q.id
            WHERE sp.student_name = %s
            ORDER BY sp.created_at DESC LIMIT 30
        """, (student,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        progress_data = [
            {"topic": r[0], "score": float(r[1] or 0), "max_score": float(r[2] or 5), "status": r[3]}
            for r in rows
        ]
        
        model = ai_analyze_student(student, progress_data)
        return jsonify({"student": student, "cognitive_model": model, "data_points": len(progress_data)})
    except Exception as e:
        return jsonify({"error": str(e)[:100], "student": student, "cognitive_model": {"weak_concepts": ["需要更多數據"], "learning_style": "待分析"}}), 200

@app.route("/api/ai/generate-variants", methods=["POST"])
def api_generate_variants():
    data = request.get_json()
    qid = data.get("question_id")
    count = data.get("count", 3)
    try:
        conn = get_db()
        cur = conn.cursor()
        if qid:
            cur.execute("SELECT question_text, answer, topic FROM questions WHERE id = %s", (qid,))
        else:
            cur.execute("SELECT question_text, answer, topic FROM questions WHERE answer IS NOT NULL AND answer != '' ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        conn.close()
        if not row: return jsonify({"error": "No question"}), 404
        try:
            try:
                from engines.ai_variant_engine import ai_generate_variants
            except:
                from ai_variant_engine import ai_generate_variants
            variants = ai_generate_variants(row[0], row[1], row[2], count)
            return jsonify({"source": row[0][:100], "variants": variants, "count": len(variants)})
        except:
            return jsonify({"source": row[0][:100], "variants": [], "count": 0, "message": "Variant engine offline"})
    except Exception as e:
        return jsonify({"error": str(e)[:200]}), 500

@app.route("/api/ai/worksheet/<student>")
def api_worksheet(student):
    topic = request.args.get("topic", "Algebra")
    difficulty = int(request.args.get("difficulty", 3))
    count = int(request.args.get("count", 5))
    try:
        try:
            try:
                from engines.ai_teacher_copilot import ai_generate_worksheet
            except:
                from ai_teacher_copilot import ai_generate_worksheet
            ws = ai_generate_worksheet(topic, difficulty, count, student)
        except:
            ws = {"questions": [], "generated_by": "offline"}
        return jsonify(ws)
    except Exception as e:
        return jsonify({"error": str(e)[:200]}), 500

# ==================== HEALTH ====================

# ═══ AI Tutor Chat (Free Ask) ═══
@app.route('/api/ai/tutor/chat', methods=['POST'])
def api_tutor_chat():
    try:
        data = request.get_json(force=True) or {}
        message = data.get('message', '')
        mode = data.get('mode', 'math_tutor')
        session_id = data.get('session_id', '')
        topic = data.get('topic', '')
        student_answer = data.get('student_answer', '')
        correct_answer = data.get('correct_answer', '')

        if not message:
            return jsonify({'response': '請輸入你的問題，我們一起來思考！', 'mode': mode})

        # Get or create session
        session = get_session(session_id) if session_id else None
        history = ''
        if session:
            history = session.get_context()
            session.add_message('user', message)
        else:
            session = create_session(student_name='student', topic=topic)
            session.add_message('user', message)
            session_id = session.session_id

        # Try intelligent Socratic chat first
        response_text = ""
        ai_provider = "socratic"
        try:
            result = socratic_chat(
                message=message,
                conversation_history=history,
                topic=topic or getattr(session, 'topic', ''),
                student_answer=student_answer,
                correct_answer=correct_answer,
                student_name=getattr(session, 'student_name', ''),
                mode=mode
            )
            response_text = result.get('response', '')
        except Exception:
            result = {"situation": "stuck"}

        # Validate: if socratic returned garbage (list string, too short, etc), use free AI
        if not response_text or len(response_text) < 20 or response_text.startswith("[") or "引導思考" in response_text[:50] and len(response_text) < 50:
            free_resp = generate_socratic_response(message, topic)
            if free_resp and len(free_resp) > 20:
                response_text = free_resp
                ai_provider = "free_ai"

        # Final fallback if still no good response
        if not response_text or len(response_text) < 10:
            response_text = "好問題！等我哋一齊諗下～等我解釋呢個數學概念俾你聽！首先我哋要睇清楚題目，然後逐步計出答案。你需要我詳細解釋嗎？！"

        if session and hasattr(session, 'add_message'):
            try:
                session.add_message('assistant', response_text)
            except:
                pass

        return jsonify({
            'response': response_text,
            'mode': mode,
            'session_id': session_id,
            'situation': result.get('situation', 'stuck') if isinstance(result, dict) else 'stuck',
            'topic': topic,
            'ai_provider': ai_provider,
        })
    except Exception as e:
        # Fallback: try free AI (Gemini/CF Workers)
        try:
            free_response = generate_socratic_response(message, topic)
            if free_response and len(free_response) > 10:
                return jsonify({'response': free_response, 'mode': mode, 'session_id': session_id, 'situation': 'stuck', 'topic': topic, 'ai_provider': 'free_ai'})
        except:
            pass
        return jsonify({'response': '讓我幫你思考這道題目。你可以先告訴我題目中給了哪些數字和條件？', 'error': str(e)[:100]})

@app.route('/api/ai/tutor/solve', methods=['POST'])
def api_tutor_solve():
    try:
        data = request.get_json(force=True) or {}
        question = data.get('question', '')
        session_id = data.get('session_id', '')
        if not question:
            return jsonify({'solution': '沒有收到題目，請重新嘗試。'})
        if session_id:
            session = get_session(session_id)
            if session:
                session.mark_resolved()
        solution = ai_tutor_solve(question)
        return jsonify({'solution': solution, 'question': question[:100]})
    except Exception as e:
        return jsonify({'solution': '請嘗試從已知條件開始推理。先找出題目中的關鍵數字，再決定用什麼公式。', 'error': str(e)})

@app.route('/api/ai/tutor/session', methods=['GET'])
def api_tutor_session():
    session_id = request.args.get('id', '')
    if not session_id:
        return jsonify({'active_sessions': active_sessions()})
    session = get_session(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(session.to_dict())


@app.route('/api/ai/tutor/reasoning', methods=['POST'])
def api_validate_reasoning():
    try:
        data = request.get_json(force=True) or {}
        reasoning = data.get('reasoning', '')
        question = data.get('question', '')
        correct_answer = data.get('correct_answer', '')
        if not reasoning:
            return jsonify({'error': '請提供學生的推理過程'}), 400
        result = validate_reasoning(reasoning, question, correct_answer)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'error_step': '', 'guidance': '無法驗證推理過程，請重新嘗試。'})

@app.route('/api/ai/tutor/summary', methods=['POST'])
def api_session_summary():
    try:
        data = request.get_json(force=True) or {}
        session_id = data.get('session_id', '')
        if session_id:
            session = get_session(session_id)
            if session:
                summary = generate_session_summary(session.to_dict())
                return jsonify({'summary': summary, 'session': session.to_dict()})
        return jsonify({'summary': '本次學習結束。繼續努力！'})
    except Exception as e:
        return jsonify({'summary': '本次學習結束。繼續努力！', 'error': str(e)})


# ═══ Payment API ═══
@app.route('/api/payment/plans', methods=['GET'])
def api_payment_plans():
    grade = request.args.get('grade', '')
    if grade:
        return jsonify({'plans': get_plan_by_grade(grade)})
    return jsonify({'plans': get_plans()})

@app.route('/api/payment/checkout', methods=['POST'])
def api_payment_checkout():
    try:
        data = request.get_json(force=True) or {}
        plan_id = data.get('plan_id', '')
        email = data.get('email', '')
        name = data.get('student_name', '')
        success_url = data.get('success_url', '')
        cancel_url = data.get('cancel_url', '')

        if not plan_id:
            return jsonify({'error': '請選擇方案', 'available_plans': ["P3_monthly","P4_monthly","P5_monthly","P6_monthly","P3_annual","P4_annual","P5_annual","P6_annual","trial"]})

        if plan_id == 'trial':
            membership = create_trial_membership(email, name, data.get('grade', ''))
            return jsonify({
                'success': True,
                'trial': True,
                'membership': membership,
                'message': '試堂已開通！',
            })

        result = create_checkout_session(plan_id, email, name, success_url, cancel_url)

        if result.get('mock'):
            return jsonify({
                'mock': True,
                'checkout_url': result.get('mock_url'),
                'plan': result.get('plan'),
                'message': '開發模式：Stripe 未配置',
            })

        if result.get('error'):
            return jsonify({'error': result.get('error', '付款系統暫時無法使用')}), 500

        return jsonify({
            'checkout_url': result.get('url', ''),
            'session_id': result.get('id', ''),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payment/webhook', methods=['POST'])
def api_payment_webhook():
    try:
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature', '')
        result = handle_webhook(payload, signature)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/payment/session/<session_id>', methods=['GET'])
def api_payment_session(session_id):
    result = get_checkout_session(session_id)
    return jsonify(result)

@app.route('/api/payment/membership/status', methods=['POST'])
def api_membership_status():
    try:
        data = request.get_json(force=True) or {}
        membership = data.get('membership', {})
        result = check_membership_status(membership)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/講義/<path:filepath>')
def serve_lecture(filepath):
    """Serve lecture HTML files from the _deploy/講義 directory"""
    import os as _os
    deploy_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '_deploy', '講義')
    return send_from_directory(deploy_path, filepath)

@app.route('/docs/<path:filepath>')
def serve_docs(filepath):
    """Serve doc HTML files"""
    import os as _os
    docs_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '_deploy', 'docs')
    return send_from_directory(docs_path, filepath)

@app.route("/api/health")
def health():
    import signal as _signal
    q_count = 0
    db_ok = False

    def _timeout_handler(signum, frame):
        raise TimeoutError("DB health check timed out")

    try:
        # Use alarm-based timeout on Unix; on Windows just catch the exception quickly
        old_handler = _signal.signal(_signal.SIGALRM, _timeout_handler) if hasattr(_signal, 'SIGALRM') else None
        if hasattr(_signal, 'SIGALRM'):
            _signal.alarm(4)  # 4s max for health check

        conn = get_db()  # Has 3-5s connect_timeout
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM questions")
        q_count = cur.fetchone()[0]
        conn.close()
        db_ok = True

        if hasattr(_signal, 'SIGALRM'):
            _signal.alarm(0)
    except Exception:
        q_count = 0
        db_ok = False
    
    return jsonify({
        "status": "online" if db_ok else "degraded",
        "brand": "LF Academy",
        "version": "3.0-render",
        "ai_engines": ["tutor","mark","smart","diagnose","variant","worksheet"],
        "question_count": q_count,
        "engines_loaded": ENGINES_LOADED,
        "ai_brain": AI_BRAIN
    })


@app.route("/site/", defaults={"path": "index.html"})
@app.route("/site/<path:path>")
def serve_site(path):
    """Serve the full site from _deploy directory"""
    import os as _os
    site_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "_deploy")
    return send_from_directory(site_path, path)

@app.route("/")
def home():
    return jsonify({
        "service": "LF Academy API",
        "version": "3.0",
        "docs": "/api/health",
        "endpoints": ["/api/topics","/api/questions/random","/api/ai/tutor/hint","/api/ai/tutor/chat","/api/ai/tutor/solve","/api/ai/tutor/session","/api/ai/tutor/reasoning","/api/ai/tutor/summary","/api/ai/mark","/api/ai/smart","/api/payment/plans","/api/payment/checkout","/api/payment/webhook","/api/payment/session/<id>","/api/payment/membership/status"]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"LF Academy Render Server starting on port {port}")
    app.run(host="0.0.0.0", port=port)




def _load_bank():
    """Load question bank from local unified_bank.json"""
    try:
        bank_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_operations", "question_bank", "unified_bank.json")
        if os.path.exists(bank_path):
            with open(bank_path, "r", encoding="utf-8") as f:
                return json.load(f)
        # Fallback: try engine bank
        from engines.mark_engine import _load_bank as _engine_bank
        return {"questions": _engine_bank()}
    except Exception as e:
        print(f"[WARN] _load_bank: {e}", file=sys.stderr)
        return {"questions": []}


@app.route("/api/worksheets/<grade>")
def api_worksheets(grade):
    """Generate 3-tier worksheet: 5 basic + 5 consolidate + 5 advanced"""
    if grade not in ("P3", "P4", "P5", "P6"):
        return jsonify({"error": "Invalid grade"}), 400
    
    import random
    bank = _load_bank()
    if not bank:
        return jsonify({"error": "Bank unavailable"}), 503
    
    questions = [q for q in bank.get("questions", []) if q.get("grade") == grade]
    DIFF_MAP = {"🌱": 1, "🌿": 2, "🌳": 3, "🏔️": 4}
    tiers = {"basic": [], "consolidate": [], "advanced": []}
    for q in questions:
        d = DIFF_MAP.get(str(q.get("difficulty", "")).strip(), 2)
        if d <= 1: tiers["basic"].append(q)
        elif d <= 2: tiers["consolidate"].append(q)
        else: tiers["advanced"].append(q)
    
    today = __import__("datetime").datetime.now().day
    random.seed(today + hash(grade) % 10000)
    
    def pick(items, n=5):
        return random.sample(items, min(n, len(items)))
    
    return jsonify({
        "grade": grade,
        "basic": [{k: q.get(k, "") for k in ("id","question_text","topic","difficulty","sspa_relevance")} for q in pick(tiers["basic"])],
        "consolidate": [{k: q.get(k, "") for k in ("id","question_text","topic","difficulty","sspa_relevance")} for q in pick(tiers["consolidate"])],
        "advanced": [{k: q.get(k, "") for k in ("id","question_text","topic","difficulty","sspa_relevance")} for q in pick(tiers["advanced"])],
    })


@app.route("/api/daily10/<grade>")
def api_daily10(grade):
    """Generate 10 daily questions, SSPA prioritized"""
    if grade not in ("P3", "P4", "P5", "P6"):
        return jsonify({"error": "Invalid grade"}), 400
    
    import random
    bank = _load_bank()
    if not bank:
        return jsonify({"error": "Bank unavailable"}), 503
    
    questions = [q for q in bank.get("questions", []) if q.get("grade") == grade]
    sspa_qs = [q for q in questions if "🔴" in str(q.get("sspa_relevance", ""))]
    normal_qs = [q for q in questions if "🔴" not in str(q.get("sspa_relevance", ""))]
    
    today = __import__("datetime").datetime.now().day
    random.seed(today + hash(grade) % 10000)
    
    selected = []
    selected.extend(random.sample(sspa_qs, min(5, len(sspa_qs))))
    remaining = 10 - len(selected)
    if remaining > 0 and normal_qs:
        selected.extend(random.sample(normal_qs, min(remaining, len(normal_qs))))
    random.shuffle(selected)
    
    date_str = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
    
    return jsonify({
        "grade": grade,
        "date": date_str,
        "questions": [{k: q.get(k, "") for k in ("id","question_text","topic","difficulty","sspa_relevance")} for q in selected[:10]],
        "sspa_count": len([q for q in selected[:10] if "🔴" in str(q.get("sspa_relevance", ""))])
    })


@app.route("/api/curriculum/<grade>")
def api_curriculum(grade):
    """Return curriculum structure for grade"""
    CURRICULUM = {
        "P3": {"name": "小三", "topics": ["萬以內數","加法","減法","乘法","除法","分數","時間","周界","容量","圖形","方向","象形圖"]},
        "P4": {"name": "小四", "topics": ["五位數","乘法","除法","因數倍數","分數","小數","面積","對稱","棒形圖","24小時制"]},
        "P5": {"name": "小五", "topics": ["小數乘除","分數乘除","百分數","體積","面積","代數","平均數","速率","折線圖","SSPA衝刺"]},
        "P6": {"name": "小六", "topics": ["百分數應用","比與比例","圓","立體圖形","統計","方程","SSPA殺手題","中一預習"]},
    }
    if grade not in CURRICULUM:
        return jsonify({"error": "Invalid grade"}), 400
    return jsonify(CURRICULUM[grade])
