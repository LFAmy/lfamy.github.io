#!/usr/bin/env python3
"""
LF Academy Render Server - Production API
Deploy: Render Web Service | DB: DATABASE_URL env var
"""
import sys, os, io, json, re, random, urllib.request
from pathlib import Path


from flask import Flask, jsonify, request
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
        return psycopg2.connect(db_url)
    # Fallback to local
    return psycopg2.connect("host='localhost' dbname='question_bank' user='postgres' password=''")

# === Load AI Engines ===
try:
    from engines.mark_engine import mark_with_feedback
    from engines.adaptive_engine import get_next_question
    from engines.tutor_engine import get_hint, generate_hints
    from engines.misconception_engine import detect_misconceptions
    from engines.ai_orchestrator import smart_pipeline
    ENGINES_LOADED = True
except Exception as e:
    print(f"[WARN] Engines import failed: {e}, trying direct import...")
    try:
        from mark_engine import mark_with_feedback
        from adaptive_engine import get_next_question
        from tutor_engine import get_hint, generate_hints
        from misconception_engine import detect_misconceptions
        from ai_orchestrator import smart_pipeline
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
FRELLMAPI_KEY = os.environ.get("FRELLMAPI_KEY", "")
FRELLMAPI_URL = os.environ.get("FRELLMAPI_URL", "http://localhost:3001/v1")

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
        model = ai_analyze_student(student)
        return jsonify({"student": student, "cognitive_model": model})
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

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
@app.route("/api/health")
def health():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM questions")
        q_count = cur.fetchone()[0]
        conn.close()
        db_ok = True
    except:
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

@app.route("/")
def home():
    return jsonify({
        "service": "LF Academy API",
        "version": "3.0",
        "docs": "/api/health",
        "endpoints": ["/api/topics","/api/questions/random","/api/ai/tutor/hint","/api/ai/mark","/api/ai/smart"]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"LF Academy Render Server starting on port {port}")
    app.run(host="0.0.0.0", port=port)
