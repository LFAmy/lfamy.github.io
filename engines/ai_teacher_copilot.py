#!/usr/bin/env python3
"""LF AI Teacher Co-Pilot v1.0 — PDF上傳 → AI拆題 → 入庫 → 生成工作紙"""
import sys, os, json, re, io, tempfile
from pathlib import Path

sys.path.insert(0, r"G:\lam-fung-academy")
try:
    from lf_ai_brain import _call_frellmapi, ai_generate_question
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using available tools"""
    # Try pymupdf first
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text
    except:
        pass
    
    # Try pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        pass
    
    return ""

def ai_decompose_paper(pdf_text: str, subject: str = "Mathematics", level: str = "S1") -> list:
    """AI decomposes exam paper into individual questions with answers"""
    if not AI_AVAILABLE or not pdf_text.strip():
        return []
    
    # Truncate if too long
    text_snippet = pdf_text[:8000]
    
    prompt = f"""你是香港考試試卷分析專家。以下是{level} {subject}試卷的OCR文本。請將每道題目拆解成獨立問題。

試卷文本:
{text_snippet}

請為每道題目回傳JSON:
{{"questions": [
  {{"number": 題號, "question_text": "完整題目", "answer": "標準答案", "topic": "主題", "difficulty": 1-5, "marks": 分數, "type": "MC/短答/長題目"}}
]}}

只回傳JSON，不要其他文字。每題最大分數不超過10分。主題用繁體中文。"""
    
    try:
        raw = _call_frellmapi(prompt, role="analyst_deep", max_tokens=2000)
        result = json.loads(raw)
        return result.get("questions", [])
    except:
        return []

def ai_generate_worksheet(topic: str, difficulty: int = 3, question_count: int = 5, student_name: str = "") -> dict:
    """AI generates a custom worksheet for a student"""
    questions = []
    for i in range(question_count):
        q = ai_generate_question(topic, difficulty + (i % 3) - 1)
        if q:
            q["number"] = i + 1
            questions.append(q)
    
    return {
        "title": f"{topic} 練習工作紙",
        "student": student_name,
        "topic": topic,
        "difficulty": difficulty,
        "total_marks": sum(q.get("marks", 3) for q in questions),
        "questions": questions,
        "generated_by": "AI Teacher Co-Pilot"
    }

def ai_analyze_class_performance(class_data: list) -> dict:
    """AI analyzes entire class performance and generates teaching suggestions"""
    if not AI_AVAILABLE or not class_data:
        return {"summary": "需要更多數據"}
    
    summary = "\n".join([
        f"學生: {s.get('name','?')}, 平均分: {s.get('avg_score',0):.1f}, 強項: {s.get('strengths','?')}, 弱項: {s.get('weaknesses','?')}"
        for s in class_data[:30]
    ])
    
    prompt = f"""你是香港數學教學顧問。分析以下班級表現數據並提供教學建議。

{summary}

回傳JSON:
{{"class_avg": 平均分, "top_strength": "全班最強主題", "top_weakness": "全班最弱主題", 
 "suggestions": ["建議1", "建議2", "建議3"], "grouping": [{{"group": "組名", "students": [], "focus": "重點"}}]}}"""
    
    try:
        raw = _call_frellmapi(prompt, role="analyst_deep", max_tokens=500)
        return json.loads(raw)
    except:
        return {"summary": "分析暫時不可用", "class_avg": 0}

if __name__ == "__main__":
    print("🧑‍🏫 AI Teacher Co-Pilot v1.0")
    print("=" * 40)
    
    # Test worksheet generation
    ws = ai_generate_worksheet("Algebra", 3, 3, "test_student")
    print(f"工作紙: {ws['title']}")
    print(f"題數: {len(ws.get('questions', []))}")
    print(f"總分: {ws.get('total_marks', 0)}")
    print("✅ Ready")
