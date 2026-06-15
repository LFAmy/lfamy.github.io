import sys, re, os, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

DEEPSEEK_KEY = "sk-86ee7fd32bd347a4a8e67e965a7fe50d"
BASE = r"G:\lam-fung-academy\講義"

SAMPLES = {
    "P3": "LF-P3-上-L01_萬以內數的認識.html",
    "P4": "LF-P4-上-L01_乘法性質+分配律.html", 
    "P5": "LF-P5-上-L01_多位數.html",
    "P6": "LF-P6-上-L01_小數除法.html",
}

def call_deepseek(prompt):
    body = json.dumps({"model": "deepseek-v4-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 800, "temperature": 0.2}).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=body, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]
    return ""

for grade, fname in SAMPLES.items():
    fpath = os.path.join(BASE, grade, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Extract body content only (skip CSS)
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    content = body_match.group(1)[:3000] if body_match else html[:3000]
    
    # Count key elements
    examples = html.count('class="lf-ex"')
    traps = html.count('lf-trap-card')
    tables = html.count('<table')
    story = 'lf-story' in html
    game = 'lf-game' in html
    why = 'lf-why' in html
    aiq = 'lf-ai-' in html
    size_kb = os.path.getsize(fpath) / 1024
    
    prompt = f"""你係香港小學數學教科書品質審查員。評估以下{grade}講義摘要（頭3000字），從1-10分評分：

評分維度：
1. 教學清晰度：概念解釋是否清楚易明
2. 例題品質：例題是否有效示範解題方法
3. 陷阱設計：是否有效預防常見錯誤
4. 生活連接：是否與香港學生生活相關
5. 排版組織：結構是否清晰有條理

講義統計：{size_kb:.0f}KB, {examples}例題, {traps}陷阱, {tables}表格, Story={story}, Game={game}, WHY={why}, AIQ={aiq}

講義內容摘要：
{content[:2500]}

返回嚴格JSON格式：
{{"clarity":分數,"examples":分數,"traps":分數,"relevance":分數,"layout":分數,"overall":分數,"suggestions":"一句改進建議"}}"""

    print(f"\n{grade} {fname} ({size_kb:.0f}KB)...", end=" ", flush=True)
    try:
        resp = call_deepseek(prompt)
        m = re.search(r'\{.*\}', resp, re.DOTALL)
        if m:
            data = json.loads(m.group())
            print(f"Overall:{data.get('overall','?')}/10 | {data.get('suggestions','')[:60]}")
    except Exception as e:
        print(f"Error: {e}")

print("\nDone.")
