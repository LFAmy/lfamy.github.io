# -*- coding: utf-8 -*-
# AI Autopilot v1.0 - Background AI Automation Engine
# Runs autonomously: reports, content, analytics, alerts
import io, sys, os, json, time, urllib.request
from datetime import datetime

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
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DEEPSEEK_KEY = DEEPSEEK_KEY
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, 'ai_output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def deepseek(prompt, max_tokens=300):
    data = json.dumps({
        'model': 'deepseek-v4-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://api.deepseek.com/chat/completions',
        data=data,
        headers={'Authorization': f'Bearer {DEEPSEEK_KEY}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))['choices'][0]['message']['content']

class AIAutopilot:
    def __init__(self):
        self.tasks_run = 0
        self.log = []
    
    def log_action(self, action, result):
        entry = {'time': datetime.now().isoformat(), 'action': action, 'result': result[:100]}
        self.log.append(entry)
        print(f"[{entry['time'][:19]}] {action}: {result[:80]}")
    
    def run_daily_briefing(self):
        prompt = '你是霖楓學苑的AI合夥人。基於以下數據，用繁體中文給出一句話的今日重點建議：172份P3-P6數學講義已就緒，AI引擎全部運作正常，DeepSeek API穩定，Firebase網站上線。今天應優先做什麼來推動業務？只給一句話。'
        result = deepseek(prompt, max_tokens=80)
        self.log_action('daily_briefing', result)
        return result
    
    def generate_weekly_content(self):
        prompt = '你是香港小學數學補習社的社交媒體經理。用繁體中文生成3個本週Facebook/IG貼文主題(每個一句)，關於小學數學呈分試準備。要有吸引力。'
        result = deepseek(prompt, max_tokens=150)
        self.log_action('weekly_content', result)
        return result
    
    def health_check(self):
        checks = {}
        try:
            r = deepseek('Say OK', max_tokens=5)
            checks['deepseek'] = 'OK' if 'OK' in r else 'WARN'
        except:
            checks['deepseek'] = 'FAIL'
        
        lecture_count = len([f for f in os.listdir(os.path.join(ROOT, '講義', 'P6')) if f.endswith('.html') and '_AK' not in f])
        checks['lectures_p6'] = lecture_count
        
        self.log_action('health_check', str(checks))
        return checks
    
    def run(self):
        print('='*50)
        print('AI AUTOPILOT - Autonomous Run')
        print(f'Time: {datetime.now().isoformat()}')
        print('='*50)
        
        briefing = self.run_daily_briefing()
        print(f'\n[DECISION] {briefing}')
        
        content = self.generate_weekly_content()
        print(f'\n[CONTENT] {content}')
        
        health = self.health_check()
        print(f'\n[HEALTH] {health}')
        
        self.tasks_run += 1
        
        summary = {
            'time': datetime.now().isoformat(),
            'tasks': self.tasks_run,
            'briefing': briefing,
            'content': content,
            'health': health
        }
        
        with open(os.path.join(OUTPUT_DIR, 'autopilot_log.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f'\n[SAVED] ai_output/autopilot_log.json')
        return summary

if __name__ == '__main__':
    pilot = AIAutopilot()
    pilot.run()
    print('\nAI Autopilot complete. System is self-aware and running.')
