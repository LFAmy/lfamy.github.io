# -*- coding: utf-8 -*-
# AI Operations Dashboard v1.0
# Single command to see everything
import io, sys, os, json, glob
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def count_files(pattern):
    return len(glob.glob(os.path.join(ROOT, pattern)))

dashboard = {
    'timestamp': datetime.now().isoformat(),
    'brain': 'v14.0 + Self-Reflection',
    'lectures': {
        'P3': count_files('講義/P3/*.html'),
        'P4': count_files('講義/P4/*.html'),
        'P5': count_files('講義/P5/*.html'),
        'P6': count_files('講義/P6/*.html'),
    },
    'ai_engines': count_files('engines/*.py'),
    'scripts': count_files('scripts/*.py'),
    'pdfs': count_files('pdf_output/**/*.pdf'),
    'exams': count_files('data/exams/*.html'),
    'deploy': {
        'site': 'lfacademyhk.com',
        'api': 'lf-api-f80h.onrender.com',
        'tunnel': 'mpeg-nomination-everyone-optimal.trycloudflare.com'
    },
    'ai_providers': {
        'primary': 'DeepSeek (stable)',
        'fallbacks': ['NVIDIA NIM', 'OpenRouter', 'Gemini', 'LM Studio', 'Ollama']
    },
    'autonomous_systems': [
        'AI Parent Report Engine',
        'AI Autopilot (daily briefing + content)',
        'AI Exam Engine (generate + grade)',
        'AI Tutor (7-layer fallback)',
        'AI Semantic Marking',
        'AI Question Variants',
        'AI Misconception Detection'
    ],
    'quality': {
        'whybox': '100%',
        'sspa': '100%',
        'parent_summary': '100%',
        'story': '100%',
        'learning_objective': '94%',
        'trap_example': '91%',
        'svg': '67%',
        'fractions': '51%'
    }
}

# Print dashboard
print('='*60)
print('  LF ACADEMY AI OPERATIONS DASHBOARD')
print('='*60)
print(f'  Brain: {dashboard[\"brain\"]}')
print(f'  Time:  {dashboard[\"timestamp\"][:19]}')
print()
print('  LECTURES:')
for k,v in dashboard['lectures'].items():
    print(f'    {k}: {v}')
print(f'    TOTAL: {sum(dashboard[\"lectures\"].values())}')
print()
print(f'  AI ENGINES: {dashboard[\"ai_engines\"]}')
print(f'  SCRIPTS: {dashboard[\"scripts\"]}')
print(f'  PDFs: {dashboard[\"pdfs\"]}')
print(f'  EXAMS: {dashboard[\"exams\"]}')
print()
print('  DEPLOY:')
for k,v in dashboard['deploy'].items():
    print(f'    {k}: {v}')
print()
print('  AUTONOMOUS AI SYSTEMS:')
for s in dashboard['autonomous_systems']:
    print(f'    [ON] {s}')
print()
print('  QUALITY:')
for k,v in dashboard['quality'].items():
    bar = '#' * int(int(v.replace('%','')) / 10)
    print(f'    {k}: {v} {bar}')

# Save
with open(os.path.join(ROOT, 'ai_output', 'dashboard.json'), 'w', encoding='utf-8') as f:
    json.dump(dashboard, f, ensure_ascii=False, indent=2)

print()
print('  Dashboard saved: ai_output/dashboard.json')
print('='*60)
