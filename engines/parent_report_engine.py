# -*- coding: utf-8 -*-
# AI Parent Report Engine v1.0
# Generates personalized weekly student reports for parents
# Uses DeepSeek API for intelligent analysis
import io, sys, os, json, urllib.request

# === SECRETS loaded from .env via _config/secrets.py ===
import os as _os, sys as _sys
_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) if "__file__" in dir() else _os.path.dirname(_os.path.abspath("."))
for _p in [_root, _os.path.join(_root, "_config")]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
try:
    from _config.secrets import FRELLMAPI_KEY, FRELLMAPI_URL, DEEPSEEK_KEY, DEEPSEEK_URL
except ImportError:
    FRELLMAPI_KEY = _os.environ.get("FRELLMAPI_KEY", "")
    FRELLMAPI_URL = _os.environ.get("FRELLMAPI_URL", "http://localhost:3001")
    DEEPSEEK_KEY = _os.environ.get("DEEPSEEK_KEY", "")
    DEEPSEEK_URL = _os.environ.get("DEEPSEEK_URL", "https://api.deepseek.com/chat/completions")
# === END SECRETS ===


os.environ['PYTHONIOENCODING'] = 'utf-8'

DEEPSEEK_KEY = DEEPSEEK_KEY
DEEPSEEK_URL = 'https://api.deepseek.com/chat/completions'

STUDENT_PROFILES = {
    'demo_student_1': {
        'name': '小明',
        'grade': 'P6',
        'recent_topics': ['小數除法', '百分數應用', '速率'],
        'scores': {'小數除法': 85, '百分數應用': 62, '速率': 78},
        'common_mistakes': ['除數移位後餘數小數點忘記還原', '百分數折扣方向混淆'],
        'attendance': '4/4',
        'homework_completion': '3/4',
        'teacher_notes': '上課專注，但做題速度偏慢，應用題審題需加強'
    },
    'demo_student_2': {
        'name': '小美',
        'grade': 'P5',
        'recent_topics': ['分數加減', '面積計算', '方程入門'],
        'scores': {'分數加減': 92, '面積計算': 88, '方程入門': 75},
        'common_mistakes': ['方程等號兩邊不平衡'],
        'attendance': '4/4',
        'homework_completion': '4/4',
        'teacher_notes': '數學基礎扎實，方程新課題需多練習，潛力很大'
    }
}

def call_deepseek(prompt, max_tokens=500):
    data = json.dumps({
        'model': 'deepseek-v4-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens
    }).encode('utf-8')
    req = urllib.request.Request(DEEPSEEK_URL, data=data, headers={
        'Authorization': f'Bearer {DEEPSEEK_KEY}',
        'Content-Type': 'application/json'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))['choices'][0]['message']['content']

def generate_parent_report(student_id):
    s = STUDENT_PROFILES.get(student_id)
    if not s:
        return {'error': f'Student {student_id} not found'}
    
    # Build prompt with student data
    topics_str = ', '.join(s['recent_topics'])
    scores_str = ', '.join([f'{k}:{v}分' for k,v in s['scores'].items()])
    mistakes_str = ', '.join(s['common_mistakes'])
    
    prompt = f"""你是香港小學數學補習老師。為以下學生生成一份給家長的每週學習報告。

學生: {s['name']} ({s['grade']})
本週課題: {topics_str}
課題得分: {scores_str}
常見錯誤: {mistakes_str}
出席率: {s['attendance']}
功課完成: {s['homework_completion']}
老師評語: {s['teacher_notes']}

請生成報告，格式如下:

📊 {s['name']} 本週學習報告

【本週表現總結】(2-3句概括)

【強項】(列出1-2個做得好的地方)

【需要加強】(列出1-2個弱項及具體建議)

【家中鞏固建議】(具體可操作的練習建議，2-3項)

【下週預告】(根據進度建議下週重點)

署名: 霖楓學苑 AI 導師系統"""
    
    try:
        report = call_deepseek(prompt, max_tokens=400)
        return {
            'student': s['name'],
            'grade': s['grade'],
            'report': report,
            'generated_at': '2026-06-02',
            'status': 'success'
        }
    except Exception as e:
        return {'error': str(e), 'status': 'failed'}

def batch_generate_reports():
    results = []
    for sid in STUDENT_PROFILES:
        result = generate_parent_report(sid)
        results.append(result)
    return results

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print('='*50)
    print('AI PARENT REPORT ENGINE - DEMO')
    print('='*50)
    
    for sid in STUDENT_PROFILES:
        result = generate_parent_report(sid)
        if result.get('status') == 'success':
            print(f"\n{'='*50}")
            print(f"Student: {result['student']} ({result['grade']})")
            print(f"{'='*50}")
            print(result['report'])
        else:
            print(f"ERROR: {result.get('error')}")
