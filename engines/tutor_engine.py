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

# ═══ v3.0 Intelligent Socratic Chat ═══
def socratic_chat(message: str, conversation_history: str = "", topic: str = "",
                  student_answer: str = "", correct_answer: str = "",
                  student_name: str = "") -> dict:
    """
    Intelligent Socratic response that integrates:
    - Topic knowledge base (grade-appropriate prompts)
    - Misconception detection (error pattern analysis)
    - Adaptive hint branching (targeted guidance)
    - Multi-turn dialogue awareness
    """
    from topic_knowledge import get_topic_knowledge, get_socratic_strategy, SOCRATIC_STRATEGIES

    tk = get_topic_knowledge(topic) if topic else {"socratic": [], "common_mistakes": [], "key_concepts": []}
    socratic_prompts = tk.get("socratic", [])
    misconceptions = tk.get("common_mistakes", [])
    key_concepts = tk.get("key_concepts", [])

    # Determine student situation
    situation = "stuck"  # default
    if student_answer and correct_answer:
        try:
            from lf_ai_brain import ai_semantic_mark
            result = ai_semantic_mark(student_answer, correct_answer, message)
            if result.get("status") == "CORRECT":
                situation = "correct_answer"
            else:
                situation = "wrong_answer"
        except:
            is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
            situation = "correct_answer" if is_correct else "wrong_answer"

    # Try misconception detection for wrong answers
    misconception_hint = ""
    if situation == "wrong_answer" and topic:
        try:
            from misconception_engine import detect_misconceptions
            # Quick topic-based misconception lookup
            for m in misconceptions:
                if any(kw in (student_answer or "").lower() for kw in m.lower().split()):
                    misconception_hint = m
                    situation = "misconception_detected"
                    break
        except:
            pass

    # Build context-aware prompt
    strategy = get_socratic_strategy(situation)

    concept_list = "、".join(key_concepts[:5]) if key_concepts else "相關數學概念"

    topic_prompt = ""
    if socratic_prompts:
        import random
        topic_prompt = random.choice(socratic_prompts)

    system = f"""你是霖楓學苑的 AI 數學導師。以蘇格拉底式對話引導香港小學學生思考。

當前課題：{topic or '數學'}
核心概念：{concept_list}
常見錯誤：{'；'.join(misconceptions[:3]) if misconceptions else '計算粗心'}

{misconception_hint if misconception_hint else ''}

對話策略：{strategy}

規則：
1. 如果學生答對→正面鼓勵 + 追問為什麼這樣想
2. 如果學生答錯→追問思路，不直接說「錯」
3. 如果學生困惑→用{concept_list}引導
4. 每次只問一個引導性問題
5. 用香港小學程度繁體中文
6. 參考課題提示：{topic_prompt if topic_prompt else '因應學生情況引導'}"""

    context_block = ""
    if conversation_history:
        recent = conversation_history.split("\n")[-8:]
        context_block = "\n".join(recent)

    full_prompt = f"{system}\n\n{'對話歷史：' + chr(10) + context_block if context_block else ''}\n學生說：{message}\n\n引導回應："

    try:
        from lf_ai_brain import _call_frellmapi
        response = _call_frellmapi(full_prompt, "tutor_socratic", max_tokens=400)
    except:
        if topic_prompt:
            response = topic_prompt
        else:
            response = strategy

    return {
        "response": response,
        "situation": situation,
        "topic": topic,
        "misconception_detected": bool(misconception_hint),
        "misconception_hint": misconception_hint,
        "key_concepts_used": key_concepts[:3],
    }


# ═══ v3.0 Adaptive Hint Branch ═══
def adaptive_hint_branch(question_id, student_answer, conn):
    """
    Decision-tree hint system that replaces the linear 5-level ladder.
    Branches based on: error type → hint category → targeted Socratic question.
    """
    from topic_knowledge import get_topic_knowledge

    cur = conn.cursor()
    cur.execute("SELECT question_text, answer, topic, difficulty FROM questions WHERE id = %s", (question_id,))
    row = cur.fetchone()
    if not row:
        return {"error": "Question not found"}, None

    question, correct_answer, topic, difficulty = row
    tk = get_topic_knowledge(topic)

    # Step 1: Check if answer is correct
    is_correct = False
    if student_answer and correct_answer:
        try:
            from lf_ai_brain import ai_semantic_mark
            result = ai_semantic_mark(student_answer, correct_answer, question)
            is_correct = result.get("status") == "CORRECT"
        except:
            is_correct = student_answer.strip().lower() == correct_answer.strip().lower()

    if is_correct:
        return {
            "question_id": question_id,
            "is_correct": True,
            "branch": "correct",
            "hint": tk.get("socratic", ["答對了！你能解釋一下你的思路嗎？"])[0] if tk.get("socratic") else "答對了！你能解釋一下你的思路嗎？",
            "next_action": "praise_and_extend"
        }, True

    # Step 2: Classify error type
    error_type = "unknown"
    if student_answer:
        student_clean = student_answer.strip().lower()
        correct_clean = correct_answer.strip().lower()

        # Numeric comparison
        try:
            s_num = float(student_clean)
            c_num = float(correct_clean)
            if s_num == -c_num:
                error_type = "sign_error"
            elif abs(s_num - c_num) < 0.01 * abs(c_num):
                error_type = "rounding_error"
            elif s_num * 2 == c_num or c_num * 2 == s_num:
                error_type = "factor_error"
        except:
            pass

        # Length-based heuristics
        if len(student_clean) == len(correct_clean) and student_clean != correct_clean:
            error_type = "calculation_error"

    # Step 3: Map error type to hint branch
    branch_hints = {
        "sign_error": {
            "category": "concept",
            "hint": "檢查正負號！移項時符號會改變。讓我們重新看看等號兩邊。",
        },
        "calculation_error": {
            "category": "calculation",
            "hint": "數字很接近了！讓我們重新一步一步計算，看看哪一步出了小問題。",
        },
        "rounding_error": {
            "category": "precision",
            "hint": "留意題目要求精確到哪一位？四捨五入的規則還記得嗎？",
        },
        "factor_error": {
            "category": "concept",
            "hint": "你的答案和正確答案有倍數關係。你是不是漏掉了某個步驟？",
        },
        "unknown": {
            "category": "general",
            "hint": tk.get("common_mistakes", ["讓我們重新審視這道題目。"])[0] if tk.get("common_mistakes") else "讓我們重新看看這道題目需要什麼。",
        }
    }

    branch = branch_hints.get(error_type, branch_hints["unknown"])

    return {
        "question_id": question_id,
        "is_correct": False,
        "error_type": error_type,
        "branch": branch["category"],
        "hint": branch["hint"],
        "topic_misconceptions": tk.get("common_mistakes", [])[:2],
        "next_action": "targeted_hint"
    }, False


# ═══ v3.0 Reasoning Validator ═══
def validate_reasoning(student_reasoning: str, question: str, correct_answer: str) -> dict:
    """
    AI-powered step-by-step reasoning validation.
    Analyzes intermediate steps, not just final answers.
    """
    prompt = f"""你是香港小學數學老師。請分析學生的推理過程。

題目：{question}
正確答案：{correct_answer}
學生推理：{student_reasoning}

請評估：
1. 推理過程是否正確？(correct/partially_correct/incorrect)
2. 哪個步驟出了問題？（如果有的話）
3. 應該如何引導學生修正？

以 JSON 格式回覆：{{"status":"...", "error_step":"...", "guidance":"..."}}"""

    try:
        from lf_ai_brain import _call_frellmapi
        import json
        result = _call_frellmapi(prompt, "math_checker", max_tokens=300)
        # Try to parse JSON
        try:
            parsed = json.loads(result)
            return parsed
        except:
            return {"status": "uncertain", "error_step": "", "guidance": result}
    except:
        return {
            "status": "unavailable",
            "error_step": "",
            "guidance": "讓我們一起逐步檢查你的推理過程。每一步都確認無誤後再繼續。"
        }


# ═══ v3.0 Session Summary Generator ═══
def generate_session_summary(session_data: dict) -> str:
    """Generate AI-powered learning summary after a tutoring session."""
    dialogue_count = session_data.get("dialogue_length", 0)
    attempts = session_data.get("attempts", 0)
    resolved = session_data.get("resolved", False)
    topic = session_data.get("topic", "數學")
    misconceptions = session_data.get("misconceptions", [])
    elapsed = session_data.get("elapsed_sec", 0)

    prompt = f"""你是霖楓學苑的學習分析師。為學生生成課後學習摘要。

課題：{topic}
對話輪數：{dialogue_count}
嘗試次數：{attempts}
最終解決：{'是' if resolved else '否'}
錯誤模式：{', '.join(misconceptions) if misconceptions else '無'}
用時：{elapsed}秒

請用繁體中文生成簡短摘要（100字內），包含：
1. 本課學到什麼
2. 需要注意的地方
3. 下次建議"""

    try:
        from lf_ai_brain import _call_frellmapi
        return _call_frellmapi(prompt, "fast_summary", max_tokens=200)
    except:
        parts = [f"今天我們一起學習了{topic}。"]
        if resolved:
            parts.append("你成功解決了問題，表現很好！")
        else:
            parts.append("繼續努力，下次我們再一起研究。")
        if misconceptions:
            parts.append(f"特別留意：{'、'.join(misconceptions[:2])}。")
        return "".join(parts)