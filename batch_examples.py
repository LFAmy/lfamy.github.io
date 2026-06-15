import sys, re, os, json, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

DEEPSEEK_KEY = "sk-86ee7fd32bd347a4a8e67e965a7fe50d"
BASE = r"G:\lam-fung-academy\講義"

def call_deepseek(prompt):
    body = json.dumps({"model": "deepseek-v4-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1200, "temperature": 0.3}).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=body, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]
    return ""

def gen_examples(topic, grade):
    prompt = f"""Generate 2 worked examples for HK {grade} math: {topic}. Each example: question (Traditional Chinese, HK context), wrong answer with wrong reasoning, right answer with step-by-step solution, one-line trap tip. Return ONLY valid JSON: {{"examples":[{{"question":"...","wrong_answer":"...","wrong_reason":"...","right_answer":"...","right_steps":"...","trap_tip":"..."}}]}}. 2 examples total."""
    try:
        resp = call_deepseek(prompt)
        m = re.search(r'\{.*\}', resp, re.DOTALL)
        if m:
            txt = re.sub(r',\s*}', '}', re.sub(r',\s*]', ']', m.group()))
            return json.loads(txt)
    except: pass
    return None

def build(exs):
    parts = []
    for i, ex in enumerate(exs.get("examples", [])):
        parts.append(f'<div class="lf-ex"><div class="lf-ex-title">🪤 陷阱引爆例題 {i+1}</div><div class="lf-ex-q">{ex["question"]}</div><div class="lf-ex-compare"><div class="lf-ex-wrong"><div class="lf-ex-label">❌ 常見錯誤</div>{ex["wrong_answer"]}<div style="font-size:9pt;color:#991B1B;margin-top:4pt;">{ex["wrong_reason"]}</div></div><div class="lf-ex-right"><div class="lf-ex-label">✅ 正確解法</div>{ex["right_answer"]}<div style="font-size:9pt;color:#14532D;margin-top:4pt;">{ex["right_steps"]}</div></div></div><div style="font-size:9pt;color:#6B7280;margin-top:4pt;font-style:italic;">💡 {ex["trap_tip"]}</div></div>')
    return '\n'.join(parts)

# Skip patterns (review/mock sessions where examples don't fit)
SKIP_PATTERNS = ['SSPA模擬', '總複習', '學期總結', '陷阱總複習', '寒假計劃', '暑假', '個人弱項', '閉環']

count = total_added = skipped = 0
for grade in ["P3", "P4", "P5", "P6"]:
    grade_dir = os.path.join(BASE, grade)
    for fname in sorted(os.listdir(grade_dir)):
        if not fname.endswith('.html') or '_AK' in fname or '_EN' in fname: continue
        fpath = os.path.join(grade_dir, fname)
        
        with open(fpath, 'r', encoding='utf-8') as f: html = f.read()
        ex_count = html.count('class="lf-ex"')
        if ex_count >= 4: continue
        
        # Skip review/mock sessions
        if any(p in fname for p in SKIP_PATTERNS) and ex_count == 0:
            skipped += 1
            continue
        
        size_kb = os.path.getsize(fpath) / 1024
        topic = re.sub(r'^LF-P[3-6]-[上下暑]-L\d+[a-z]?_', '', fname.replace('.html', ''))
        
        print(f"{grade} {topic[:35]} ({size_kb:.0f}KB, {ex_count}ex)...", end=" ", flush=True)
        
        data = gen_examples(topic, grade)
        if data and data.get("examples"):
            ex_html = build(data)
            if 'class="lf-ai-section"' in html:
                html = html.replace('<div class="lf-ai-section">', ex_html + '\n<div class="lf-ai-section">')
            elif 'class="lf-h1"' in html:
                last_h1 = html.rfind('class="lf-h1"')
                html = html[:last_h1] + ex_html + '\n' + html[last_h1:]
            else:
                html = html.replace('</div>\n</body>', ex_html + '\n</div>\n</body>')
            
            with open(fpath, 'w', encoding='utf-8') as f: f.write(html)
            new_size = len(html.encode('utf-8')) / 1024
            added = new_size - size_kb
            total_added += added
            count += 1
            print(f"+{added:.1f}KB")
        else:
            print("skip")
        time.sleep(1)

print(f"\n{count} expanded (+{total_added:.1f}KB), {skipped} skipped (review/mock)")
