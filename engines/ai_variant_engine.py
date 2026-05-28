#!/usr/bin/env python3
"""LF AI Variant Engine v1.0 — frellmapi 語意變體生成 + 規則 fallback"""
import sys, json, random

sys.path.insert(0, r"G:\lam-fung-academy")
try:
    from lf_ai_brain import _call_frellmapi
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    def _call_frellmapi(*a, **kw): return ""

def ai_generate_variants(question_text: str, answer: str, topic: str, count: int = 3) -> list:
    """AI generates semantic variants of a question — same topic, new scenario/numbers"""
    if not AI_AVAILABLE:
        return _rule_variants(question_text, answer, topic, count)
    
    prompt = f"""你是一位香港數學出題專家。根據以下題目生成 {count} 個變體題目。

原題目: {question_text}
原答案: {answer}
主題: {topic}

要求:
1. 保持相同主題和難度
2. 改變數字、情境、名字，但保持數學結構
3. 每個變體必須有不同的答案
4. 格式為香港DSE/校內考試格式

回傳JSON: {{"variants": [{{"question": "...", "answer": "...", "difficulty": 1-5, "marks": 分數}}]}}
只回傳JSON，不要其他文字。"""
    
    try:
        raw = _call_frellmapi(prompt, role="creative_gen", max_tokens=800)
        result = json.loads(raw)
        return result.get("variants", [])
    except:
        return _rule_variants(question_text, answer, topic, count)

def _rule_variants(question_text: str, answer: str, topic: str, count: int = 3) -> list:
    """Rule-based fallback: simple number swapping"""
    import re
    variants = []
    numbers = re.findall(r'\d+', question_text)
    
    for i in range(count):
        new_q = question_text
        new_a = answer
        for num in numbers[:5]:
            new_val = str(int(num) + random.randint(1, 10) * random.choice([1, -1]))
            new_q = new_q.replace(num, new_val, 1)
            if answer and num in answer:
                new_a = new_a.replace(num, new_val, 1)
        variants.append({
            "question": new_q,
            "answer": new_a,
            "difficulty": 3,
            "marks": random.choice([3, 4, 5]),
            "method": "rule_based"
        })
    return variants

def generate_weak_topic_variants(student_name: str, weak_topics: list, conn, count_per_topic: int = 2) -> dict:
    """Generate targeted variants for student weak areas"""
    cur = conn.cursor()
    result = {"student": student_name, "variants_by_topic": {}}
    
    for topic in weak_topics[:3]:
        cur.execute("""
            SELECT question_text, answer FROM questions
            WHERE topic ILIKE %s AND answer IS NOT NULL AND answer != ''
            ORDER BY RANDOM() LIMIT 1
        """, (f"%{topic}%",))
        row = cur.fetchone()
        if row:
            variants = ai_generate_variants(row[0], row[1], topic, count_per_topic)
            result["variants_by_topic"][topic] = variants
    
    cur.close()
    return result

if __name__ == "__main__":
    test_q = "解方程: 2x + 5 = 13"
    test_a = "x = 4"
    print("AI Variant Engine Test:")
    variants = ai_generate_variants(test_q, test_a, "Algebra", 3)
    for i, v in enumerate(variants):
        print(f"  V{i+1}: {v.get('question', '?')[:80]}...")
        print(f"       Ans: {v.get('answer', '?')}")
