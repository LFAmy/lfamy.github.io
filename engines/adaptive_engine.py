#!/usr/bin/env python3
"""LF AI Adaptive Engine v2.0 — AI 認知模型 + 動態學習路徑"""
import psycopg2
import sys, json

sys.path.insert(0, r"G:\lam-fung-academy")
try:
    from lf_ai_brain import ai_analyze_student
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    def ai_analyze_student(*a, **kw): return {"weak_concepts": [], "strength_concepts": [], "learning_style": "未知", "next_best_action": "繼續練習"}

def get_next_question(student_name, conn, weak_topic=None, preferred_difficulty=None):
    """AI-powered adaptive question selection"""
    cur = conn.cursor()
    
    # Get student progress for AI analysis
    cur.execute("""
        SELECT q.topic, sp.score, sp.max_score, sp.status, q.difficulty
        FROM student_progress sp
        JOIN questions q ON sp.question_id = q.id
        WHERE sp.student_name = %s
        ORDER BY sp.created_at DESC LIMIT 30
    """, (student_name,))
    rows = cur.fetchall()
    
    progress = [
        {"topic": r[0], "score": float(r[1] or 0), "max_score": float(r[2] or 5), "status": r[3], "difficulty": r[4]}
        for r in rows
    ]
    
    # AI cognitive analysis
    if AI_AVAILABLE and len(progress) >= 5:
        ai_model = ai_analyze_student(student_name, progress)
        weak_concepts = ai_model.get("weak_concepts", [])
    else:
        weak_concepts = []
    
    # Find weakest topic
    if not weak_topic:
        if weak_concepts:
            weak_topic = weak_concepts[0]
        else:
            cur.execute("""
                SELECT topic, AVG(score/NULLIF(max_score,0)) as avg_pct
                FROM student_progress
                WHERE student_name = %s
                GROUP BY topic ORDER BY avg_pct ASC LIMIT 1
            """, (student_name,))
            row = cur.fetchone()
            weak_topic = row[0] if row else None
    
    # Pick question: weak topic + appropriate difficulty + unanswered
    if weak_topic:
        diff_filter = f"AND q.difficulty <= {preferred_difficulty}" if preferred_difficulty else ""
        cur.execute(f"""
            SELECT q.id, q.topic, q.difficulty, q.question_text
            FROM questions q
            WHERE q.topic ILIKE %s {diff_filter}
            AND q.id NOT IN (
                SELECT question_id FROM student_progress WHERE student_name = %s
            )
            ORDER BY q.difficulty ASC, RANDOM()
            LIMIT 1
        """, (f"%{weak_topic}%", student_name))
    else:
        cur.execute("""
            SELECT q.id, q.topic, q.difficulty, q.question_text
            FROM questions q
            WHERE q.id NOT IN (
                SELECT question_id FROM student_progress WHERE student_name = %s
            )
            ORDER BY RANDOM() LIMIT 1
        """, (student_name,))
    
    row = cur.fetchone()
    if row:
        return row[0], weak_topic, row[2]  # id, topic, difficulty
    
    # Fallback
    cur.execute("SELECT id, topic, difficulty FROM questions ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    return row[0] if row else 1, weak_topic, row[2] if row else 3

def generate_learning_path(student_name, conn):
    """AI generates a personalized 5-step learning path"""
    cur = conn.cursor()
    cur.execute("""
        SELECT q.topic, sp.score, sp.max_score, sp.status
        FROM student_progress sp
        JOIN questions q ON sp.question_id = q.id
        WHERE sp.student_name = %s
        ORDER BY sp.created_at DESC LIMIT 50
    """, (student_name,))
    rows = cur.fetchall()
    progress = [
        {"topic": r[0], "score": float(r[1] or 0), "max_score": float(r[2] or 5), "status": r[3]}
        for r in rows
    ]
    
    if AI_AVAILABLE and len(progress) >= 5:
        model = ai_analyze_student(student_name, progress)
        return {
            "student": student_name,
            "weak_concepts": model.get("weak_concepts", []),
            "strength_concepts": model.get("strength_concepts", []),
            "learning_style": model.get("learning_style", ""),
            "next_best_action": model.get("next_best_action", ""),
            "questions_analyzed": len(progress),
            "ai_powered": True
        }
    
    # Rule-based fallback
    from misconception_engine import detect_misconceptions
    diag = detect_misconceptions(student_name, conn)
    return {
        "student": student_name,
        "weak_areas": [w["topic"] for w in diag.get("weak_areas", [])],
        "recommendation": diag.get("recommendation", "繼續練習"),
        "ai_powered": False
    }
