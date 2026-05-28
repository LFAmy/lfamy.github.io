#!/usr/bin/env python3
"""LF AI Misconception Engine v2.0 — AI 深度錯誤模式分析 + 規則 fallback"""
import sys

sys.path.insert(0, r"G:\lam-fung-academy")
try:
    from lf_ai_brain import ai_detect_misconceptions, ai_analyze_student
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    def ai_detect_misconceptions(*a, **kw): return {"patterns": [], "root_cause": "", "fix_suggestions": []}
    def ai_analyze_student(*a, **kw): return {}

MISCONCEPTIONS = {
    "Algebra": {
        "sign_error": "檢查正負號是否正確",
        "distributive": "括號內每一項都要乘",
        "inverse_ops": "使用正確的逆運算順序",
    },
    "Fractions": {
        "common_denom": "加減前先找公分母",
        "reciprocal": "除法時乘以倒數",
        "simplify": "最後答案要約簡",
    },
    "Geometry": {
        "angle_sum": "三角形內角和 = 180°",
        "parallel_lines": "檢查同位角/錯角規則",
        "units": "確保單位一致",
    },
    "Statistics": {
        "mean_calc": "總和除以個數",
        "median_sort": "先排序再找中間值",
        "mode_count": "眾數是出現次數最多的值",
    },
    "Ratio": {
        "order": "保持比例順序一致",
        "total_parts": "先找總份數再計算",
        "units": "先轉換相同單位",
    },
}

def detect_misconceptions(student_name, conn):
    """AI + 規則雙重錯誤分析"""
    cur = conn.cursor()
    cur.execute("""
        SELECT q.topic, q.question_text, q.answer, sp.score, sp.max_score, sp.status
        FROM student_progress sp
        JOIN questions q ON sp.question_id = q.id
        WHERE sp.student_name = %s AND sp.status != 'CORRECT'
        ORDER BY sp.created_at DESC LIMIT 20
    """, (student_name,))
    errors = cur.fetchall()
    
    if not errors:
        return {"student": student_name, "weak_areas": [], "message": "沒有錯誤 — 做得很好！", "ai_analysis": None}
    
    # Rule-based analysis
    topic_errors = {}
    for topic, question, correct_ans, score, max_score, status in errors:
        if topic not in topic_errors:
            topic_errors[topic] = []
        topic_errors[topic].append({
            "question": question[:80] if question else "",
            "correct_answer": correct_ans,
            "score": float(score or 0),
            "max_score": float(max_score or 5),
            "status": status
        })
    
    weak_areas = []
    for topic, errs in sorted(topic_errors.items(), key=lambda x: -len(x[1])):
        misconceptions = MISCONCEPTIONS.get(topic, {})
        area = {
            "topic": topic,
            "error_count": len(errs),
            "possible_issues": list(misconceptions.values())[:3] if misconceptions else ["重溫此課題"],
            "recent_errors": errs[:3],
        }
        weak_areas.append(area)
    
    result = {
        "student": student_name,
        "total_errors": len(errors),
        "weak_areas": weak_areas,
        "recommendation": f"重點複習：{weak_areas[0]['topic']}" if weak_areas else "繼續努力！",
    }
    
    # AI deep analysis
    if AI_AVAILABLE and len(errors) >= 3:
        try:
            ai_errors = [
                {"topic": e[0], "question": e[1][:100] if e[1] else "", "correct_answer": e[2]}
                for e in errors[:10]
            ]
            ai_result = ai_detect_misconceptions(student_name, ai_errors)
            result["ai_analysis"] = {
                "patterns": ai_result.get("patterns", []),
                "root_cause": ai_result.get("root_cause", ""),
                "fix_suggestions": ai_result.get("fix_suggestions", []),
            }
        except:
            result["ai_analysis"] = None
    
    return result
