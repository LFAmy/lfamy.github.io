#!/usr/bin/env python3
"""LF AI Tutor Engine v2.0 — frellmapi Socratic 對話引導 + 規則 fallback"""
import psycopg2
import re
import sys

sys.path.insert(0, r"G:\lam-fung-academy")
try:
    from lf_ai_brain import ai_generate_hints
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    def ai_generate_hints(*a, **kw): return ["請嘗試思考這道題目涉及什麼概念。"]

def get_hint(question_id, student_answer, conn):
    cur = conn.cursor()
    cur.execute("SELECT question_text, answer, topic, difficulty FROM questions WHERE id = %s", (question_id,))
    row = cur.fetchone()
    if not row:
        return {"error": "Question not found"}, None

    question, correct_answer, topic, difficulty = row
    hints = generate_hints(question, correct_answer, topic, difficulty, student_answer)

    is_correct = False
    if student_answer and correct_answer:
        try:
            from lf_ai_brain import ai_semantic_mark
            result = ai_semantic_mark(student_answer, correct_answer, question)
            is_correct = result.get("status") == "CORRECT"
        except:
            is_correct = student_answer.strip().lower() == correct_answer.strip().lower()

    return {
        "question_id": question_id,
        "topic": topic,
        "is_correct": is_correct,
        "hints": hints,
        "hint_level": 1
    }, is_correct

def generate_hints(question_text, answer, topic="", difficulty="", student_answer=""):
    # Try AI first
    if AI_AVAILABLE and question_text and answer:
        try:
            return ai_generate_hints(question_text, answer, student_answer)
        except:
            pass

    # Fallback: rule-based hints
    hints = [f"這是一道{topic}題目。思考相關的公式和概念。"]
    numbers = re.findall(r"\d+", question_text)
    if numbers:
        hints.append(f"題目中的關鍵數字：{', '.join(numbers[:5])}。它們之間有什麼關係？")
    
    ops = {
        "Algebra": "試著移項，把未知數隔離到等號一邊。",
        "Geometry": "畫一個圖，標出所有已知數值。",
        "Statistics": "整理數據，確定要計算哪個統計量。",
        "Arithmetic": "把問題拆成更小的步驟。",
        "Ratio": "設定比例關係。",
        "Percentage": "把百分比轉為小數再計算。",
    }
    topic_hint = "先判斷題目類型，再選擇合適方法。"
    for key, val in ops.items():
        if key.lower() in (topic or "").lower():
            topic_hint = val
            break
    hints.append(topic_hint)
    if answer and answer.strip():
        hints.append(f"答案有 {len(answer.strip())} 個字符。仔細逐步推理。")
    return hints

def get_next_hint(question_id, hint_level, conn):
    cur = conn.cursor()
    cur.execute("SELECT question_text, answer FROM questions WHERE id = %s", (question_id,))
    row = cur.fetchone()
    if not row:
        return {"error": "Question not found"}
    question, answer = row

    progressive = {
        2: f"專注：{question[:100]}... 第一步是什麼？",
        3: "步驟：1) 找出已知數值 2) 套用公式 3) 逐步求解",
        4: f"答案格式類似：{'*' * len(answer.strip()) if answer else '一個數字'}",
        5: f"最後提示：答案以「{answer.strip()[:2] if answer else '?'}」開頭...",
    }
    return {
        "question_id": question_id,
        "hint_level": min(hint_level + 1, 5),
        "hint": progressive.get(hint_level + 1, "沒有更多提示了。盡力作答吧！")
    }
