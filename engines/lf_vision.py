# -*- coding: utf-8 -*-
"""
LF Vision Engine v1.0 - AI-driven SVG diagram generation
Uses frellmapi gateway for MiniMax M2.5 vision model.
Falls back to offline SVG template library.

Usage:
  python engines/lf_vision.py --test
  python engines/lf_vision.py --enhance-all --dry-run
  python engines/lf_vision.py --topic triangle_area
"""
import sys, io, json, re, time, urllib.request, urllib.error
from pathlib import Path

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


try:
    if not isinstance(sys.stdout, io.TextIOWrapper) and hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

# Configuration
FRELLMAPI_KEY = FRELLMAPI_KEY
FRELLMAPI_CHAT = f"{FRELLMAPI_URL}/v1/chat/completions"
DEEPSEEK_KEY = DEEPSEEK_KEY
DEEPSEEK_URL = DEEPSEEK_URL
# MIMO v2.5 direct API (vision-capable, primary for SVG generation)
MIMO_KEY = "tp-snhe8xafawoier045vqcybvjivmwdrj4cm4z62jg1jglfvds"
MIMO_URL = "https://token-plan-sgp.xiaomimimo.com/v1/chat/completions"
MIMO_MODEL = "mimo-v2.5"
TIMEOUT = 120

BASE = Path("G:/lam-fung-academy")
HANDOUT_DIR = BASE / "講義"

# ═══════════════════════════════════════════
# COLOR SCHEME (LF Academy brand)
# ═══════════════════════════════════════════
C = {
    "blue": "#1A3C6D", "gold": "#C9A84C", "red": "#DC2626",
    "green": "#16A34A", "purple": "#7C3AED", "gray": "#6B7280",
    "light": "#F3F4F6", "fill": "#F0F7FF",
}


def svg_wrap(inner, w=400, h=250):
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;margin:12px 0;">{inner}</svg>'


# ═══════════════════════════════════════════
# OFFLINE SVG TEMPLATE LIBRARY
# ═══════════════════════════════════════════

TEMPLATES = {
    "triangle_area": lambda: svg_wrap(f'''
<defs><marker id="aL" markerWidth="8" markerHeight="6" refX="0" refY="3" orient="auto"><path d="M8,0 L0,3 L8,6" fill="{C['red']}"/></marker><marker id="aR" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="{C['red']}"/></marker></defs>
<polygon points="160,20 40,180 280,180" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2.5"/>
<line x1="160" y1="20" x2="160" y2="180" stroke="{C['red']}" stroke-width="1.5" stroke-dasharray="6,4"/>
<text x="175" y="105" font-size="12" font-weight="700" fill="{C['red']}">h</text>
<text x="160" y="12" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">三角形</text>
<line x1="40" y1="200" x2="280" y2="200" stroke="{C['red']}" stroke-width="1.5" marker-start="url(#aL)" marker-end="url(#aR)"/>
<text x="160" y="218" text-anchor="middle" font-size="13" font-weight="700" fill="{C['red']}">底 (b)</text>
<rect x="160" y="170" width="10" height="10" fill="none" stroke="{C['gray']}" stroke-width="1"/>
''', 320, 240),

    "right_triangle": lambda: svg_wrap(f'''
<polygon points="40,180 40,40 280,180" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2.5"/>
<rect x="40" y="170" width="10" height="10" fill="none" stroke="{C['gray']}" stroke-width="1.5"/>
<text x="160" y="200" text-anchor="middle" font-size="12" fill="{C['red']}">底</text>
<text x="20" y="115" font-size="12" fill="{C['red']}">高</text>
<text x="160" y="12" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">直角三角形</text>
<text x="160" y="232" text-anchor="middle" font-size="11" fill="{C['gray']}">面積 = 底 x 高 / 2</text>
''', 320, 250),

    "circle_area": lambda: svg_wrap(f'''
<circle cx="160" cy="120" r="80" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2.5"/>
<line x1="160" y1="120" x2="240" y2="120" stroke="{C['red']}" stroke-width="2"/>
<text x="200" y="112" text-anchor="middle" font-size="13" font-weight="700" fill="{C['red']}">r</text>
<text x="160" y="12" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">圓形</text>
<text x="160" y="228" text-anchor="middle" font-size="12" fill="{C['gray']}">面積 = πr² | 周界 = 2πr</text>
<line x1="160" y1="40" x2="160" y2="200" stroke="{C['gray']}" stroke-width="0.5" stroke-dasharray="3,5"/>
<line x1="80" y1="120" x2="240" y2="120" stroke="{C['gray']}" stroke-width="0.5" stroke-dasharray="3,5"/>
''', 320, 250),

    "circle_parts": lambda: svg_wrap(f'''
<circle cx="160" cy="130" r="85" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2.5"/>
<line x1="160" y1="130" x2="245" y2="130" stroke="{C['red']}" stroke-width="2"/>
<line x1="160" y1="130" x2="160" y2="45" stroke="{C['red']}" stroke-width="2"/>
<text x="200" y="122" font-size="12" font-weight="700" fill="{C['red']}">半徑(r)</text>
<text x="130" y="80" font-size="12" font-weight="700" fill="{C['red']}">直徑(d=2r)</text>
<circle cx="160" cy="130" r="3" fill="{C['blue']}"/>
<text x="160" y="140" font-size="10" fill="{C['gray']}">圓心</text>
<text x="160" y="10" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">圓的各部分</text>
<text x="160" y="230" text-anchor="middle" font-size="11" fill="{C['gray']}">圓周 = π x 直徑 = 2πr</text>
''', 320, 248),

    "trapezoid_area": lambda: svg_wrap(f'''
<defs><marker id="aL2" markerWidth="8" markerHeight="6" refX="0" refY="3" orient="auto"><path d="M8,0 L0,3 L8,6" fill="{C['red']}"/></marker><marker id="aR2" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="{C['red']}"/></marker></defs>
<polygon points="60,20 280,20 320,180 20,180" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2.5"/>
<line x1="60" y1="20" x2="60" y2="180" stroke="{C['red']}" stroke-width="1.5" stroke-dasharray="6,4"/>
<text x="48" y="105" font-size="12" font-weight="700" fill="{C['red']}">h</text>
<rect x="60" y="170" width="10" height="10" fill="none" stroke="{C['gray']}" stroke-width="1"/>
<text x="170" y="10" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">梯形</text>
<line x1="20" y1="198" x2="320" y2="198" stroke="{C['red']}" stroke-width="1.5" marker-start="url(#aL2)" marker-end="url(#aR2)"/>
<text x="45" y="214" text-anchor="middle" font-size="11" fill="{C['red']}">上底</text>
<text x="300" y="214" text-anchor="middle" font-size="11" fill="{C['red']}">下底</text>
<text x="170" y="240" text-anchor="middle" font-size="12" fill="{C['gray']}">面積 = (上底 + 下底) x h / 2</text>
''', 350, 258),

    "parallelogram_area": lambda: svg_wrap(f'''
<defs><marker id="aL3" markerWidth="8" markerHeight="6" refX="0" refY="3" orient="auto"><path d="M8,0 L0,3 L8,6" fill="{C['red']}"/></marker><marker id="aR3" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="{C['red']}"/></marker></defs>
<polygon points="50,20 290,20 250,170 10,170" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2.5"/>
<line x1="50" y1="20" x2="50" y2="170" stroke="{C['red']}" stroke-width="1.5" stroke-dasharray="6,4"/>
<text x="38" y="100" font-size="12" font-weight="700" fill="{C['red']}">h</text>
<rect x="50" y="160" width="10" height="10" fill="none" stroke="{C['gray']}" stroke-width="1"/>
<text x="150" y="10" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">平行四邊形</text>
<line x1="10" y1="188" x2="250" y2="188" stroke="{C['red']}" stroke-width="1.5" marker-start="url(#aL3)" marker-end="url(#aR3)"/>
<text x="130" y="204" text-anchor="middle" font-size="13" font-weight="700" fill="{C['red']}">底 (b)</text>
<text x="150" y="240" text-anchor="middle" font-size="12" fill="{C['gray']}">面積 = 底 x 高</text>
''', 300, 255),

    "cuboid_volume": lambda: svg_wrap(f'''
<rect x="60" y="50" width="200" height="120" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2.5" rx="2"/>
<rect x="90" y="20" width="200" height="120" fill="none" stroke="{C['blue']}" stroke-width="2" rx="2"/>
<line x1="60" y1="50" x2="90" y2="20" stroke="{C['blue']}" stroke-width="2"/>
<line x1="260" y1="50" x2="290" y2="20" stroke="{C['blue']}" stroke-width="2"/>
<line x1="60" y1="170" x2="90" y2="140" stroke="{C['blue']}" stroke-width="2"/>
<line x1="260" y1="170" x2="290" y2="140" stroke="{C['blue']}" stroke-width="2"/>
<text x="160" y="10" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">長方體</text>
<text x="48" y="115" font-size="11" fill="{C['red']}" font-weight="700">高</text>
<text x="160" y="200" text-anchor="middle" font-size="11" fill="{C['red']}" font-weight="700">長</text>
<text x="278" y="90" font-size="11" fill="{C['red']}" font-weight="700">闊</text>
<text x="160" y="245" text-anchor="middle" font-size="12" fill="{C['gray']}">體積 = 長 x 闊 x 高</text>
<text x="160" y="258" text-anchor="middle" font-size="10" fill="{C['gray']}">表面面積 = 2(長x闊 + 長x高 + 闊x高)</text>
''', 320, 272),

    "composite_area": lambda: svg_wrap(f'''
<rect x="20" y="60" width="180" height="120" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2.5" rx="2"/>
<rect x="200" y="60" width="120" height="70" fill="#FEF3C7" stroke="{C['blue']}" stroke-width="2" rx="2"/>
<text x="110" y="125" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">A</text>
<text x="260" y="100" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">B</text>
<text x="160" y="12" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">複合圖形面積</text>
<text x="160" y="210" text-anchor="middle" font-size="12" fill="{C['gray']}">分割法：將圖形分成 A+B 分別計算面積再相加</text>
<text x="160" y="228" text-anchor="middle" font-size="11" fill="{C['gray']}">填補法：先計大圖形再減去空白部分</text>
''', 340, 248),

    "symmetry": lambda: svg_wrap(f'''
<line x1="160" y1="20" x2="160" y2="200" stroke="{C['gray']}" stroke-width="1.5" stroke-dasharray="8,4"/>
<text x="170" y="28" font-size="10" fill="{C['gray']}">對稱軸</text>
<polygon points="160,60 120,100 120,160 160,180 160,60" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2"/>
<polygon points="160,60 200,100 200,160 160,180 160,60" fill="#FEF3C7" stroke="{C['blue']}" stroke-width="2"/>
<text x="160" y="14" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">軸對稱圖形</text>
<text x="160" y="240" text-anchor="middle" font-size="11" fill="{C['gray']}">對稱軸兩邊的圖形完全重疊</text>
''', 320, 255),

    "fraction_model": lambda: svg_wrap(f'''
<circle cx="85" cy="110" r="70" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="2"/>
<line x1="85" y1="40" x2="85" y2="180" stroke="{C['blue']}" stroke-width="1.5"/>
<line x1="85" y1="110" x2="155" y2="110" stroke="{C['blue']}" stroke-width="1.5"/>
<text x="115" y="90" font-size="16" font-weight="700" fill="{C['red']}">1/4</text>
<rect x="20" y="210" width="60" height="20" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="1"/>
<rect x="80" y="210" width="60" height="20" fill="#FEF3C7" stroke="{C['blue']}" stroke-width="1"/>
<rect x="140" y="210" width="60" height="20" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="1"/>
<rect x="200" y="210" width="60" height="20" fill="{C['fill']}" stroke="{C['blue']}" stroke-width="1"/>
<text x="110" y="225" text-anchor="middle" font-size="10" fill="{C['red']}">1/4</text>
<text x="160" y="10" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">分數模型</text>
<text x="160" y="248" text-anchor="middle" font-size="11" fill="{C['gray']}">圓形分數模型 — 4等份中的1份 = 1/4</text>
''', 280, 262),

    "bar_chart": lambda: svg_wrap(f'''
<line x1="50" y1="190" x2="50" y2="30" stroke="{C['blue']}" stroke-width="2"/>
<line x1="50" y1="190" x2="310" y2="190" stroke="{C['blue']}" stroke-width="2"/>
<rect x="70" y="90" width="40" height="100" fill="#DBEAFE" stroke="{C['blue']}" stroke-width="1.5"/>
<text x="90" y="82" text-anchor="middle" font-size="10" fill="{C['blue']}">40</text>
<rect x="130" y="110" width="40" height="80" fill="#FEF3C7" stroke="{C['blue']}" stroke-width="1.5"/>
<text x="150" y="102" text-anchor="middle" font-size="10" fill="{C['blue']}">32</text>
<rect x="190" y="60" width="40" height="130" fill="#DCFCE7" stroke="{C['blue']}" stroke-width="1.5"/>
<text x="210" y="52" text-anchor="middle" font-size="10" fill="{C['blue']}">52</text>
<rect x="250" y="140" width="40" height="50" fill="#FEE2E2" stroke="{C['blue']}" stroke-width="1.5"/>
<text x="270" y="132" text-anchor="middle" font-size="10" fill="{C['blue']}">20</text>
<text x="160" y="14" text-anchor="middle" font-size="14" font-weight="700" fill="{C['blue']}">棒形圖</text>
<text x="90" y="215" text-anchor="middle" font-size="10" fill="{C['gray']}">蘋果</text>
<text x="150" y="215" text-anchor="middle" font-size="10" fill="{C['gray']}">香蕉</text>
<text x="210" y="215" text-anchor="middle" font-size="10" fill="{C['gray']}">橙</text>
<text x="270" y="215" text-anchor="middle" font-size="10" fill="{C['gray']}">提子</text>
''', 320, 225),
}


# ═══════════════════════════════════════════
# AI VISION PROVIDER (MiniMax M2.5 via frellmapi)
# ═══════════════════════════════════════════

def call_vision_model(prompt, system_prompt=""):
    """Call the vision-capable model via frellmapi or DeepSeek direct."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Try MIMO direct API first (best vision quality), then frellmapi, then DeepSeek
    models_to_try = [
        (MIMO_URL, MIMO_KEY, MIMO_MODEL),
        (FRELLMAPI_CHAT, FRELLMAPI_KEY, "minimax/minimax-m2.5:free"),
        (FRELLMAPI_CHAT, FRELLMAPI_KEY, "gemini-2.5-flash"),
        (DEEPSEEK_URL, DEEPSEEK_KEY, "deepseek-chat"),
    ]
    
    for url, key, model in models_to_try:
        try:
            data = json.dumps({
                "model": model,
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.3,
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            })
            
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if "choices" in result and len(result["choices"]) > 0:
                    text = result["choices"][0]["message"]["content"]
                    return text
        except Exception as e:
            continue
    
    return None


def generate_svg_ai(description, topic=""):
    """Generate SVG diagram using AI vision model."""
    system = """You are an SVG diagram generator for primary school mathematics.
Generate clean, labeled, print-ready SVG diagrams.
- viewBox with responsive sizing
- Colors: fill=#F0F7FF, stroke=#1A3C6D (dark blue), dims=#DC2626 (red)
- Chinese labels where appropriate
- Professional, textbook-quality
Return ONLY the SVG code in a ```svg code block."""
    
    prompt = f"""Generate an SVG diagram for a Hong Kong primary math lecture.

Topic: {topic}
Description: {description}

Requirements:
- Proper geometric proportions
- Dimension lines with labels
- Clean, minimal design suitable for print
- Include the relevant formula if applicable

Return ONLY the SVG code."""
    
    text = call_vision_model(prompt, system)
    if not text:
        return None
    
    # Extract SVG from code block
    m = re.search(r'```(?:svg)?\s*(<svg.*?</svg>)\s*```', text, re.DOTALL)
    if m:
        return m.group(1)
    m2 = re.search(r'(<svg.*?</svg>)', text, re.DOTALL)
    if m2:
        return m2.group(1)
    return None


def get_svg_for_topic(topic_key, use_ai=False):
    """Get SVG diagram - AI or template."""
    if use_ai:
        svg = generate_svg_ai(f"Primary math diagram for {topic_key}", topic_key)
        if svg:
            return f'<div class="lf-graphics ai-generated" style="text-align:center;margin:16px 0;">{svg}</div>'
    
    if topic_key in TEMPLATES:
        svg = TEMPLATES[topic_key]()
        return f'<div class="lf-graphics" style="text-align:center;margin:16px 0;">{svg}</div>'
    
    return None


# ═══════════════════════════════════════════
# LECTURE ENHANCEMENT
# ═══════════════════════════════════════════

TOPIC_KEYWORDS = {
    "triangle_area": ["三角形面積", "triangle area", "三角形"],
    "right_triangle": ["直角三角形", "right triangle"],
    "circle_area": ["圓面積", "circle area", "圓周"],
    "circle_parts": ["圓的認識", "圓形", "半徑", "直徑", "圓心"],
    "trapezoid_area": ["梯形", "trapezoid", "trapezium"],
    "parallelogram_area": ["平行四邊形", "parallelogram"],
    "cuboid_volume": ["長方體", "正方體", "cuboid", "cube", "體積", "表面面積"],
    "composite_area": ["複合圖形", "組合圖形", "composite"],
    "symmetry": ["對稱", "symmetry", "軸對稱"],
    "fraction_model": ["分數模型", "分數", "fraction"],
    "bar_chart": ["棒形圖", "bar chart", "數據"],
}


def analyze_svg_needs(html_path):
    """Determine which SVG diagrams a lecture needs."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    name = Path(html_path).name
    svg_count = content.count('<svg')
    needs = []
    
    for key, keywords in TOPIC_KEYWORDS.items():
        if any(kw in name for kw in keywords):
            # Check if this specific SVG type is already present
            if svg_count < 3 or key not in content:
                needs.append(key)
    
    return needs


def enhance_lecture(html_path, dry_run=False, use_ai=False):
    """Enhance a lecture with additional SVG diagrams."""
    name = Path(html_path).name
    
    # Skip variants
    if '_AK' in name or '_EN' in name or '_學生' in name or '_backup' in name:
        return None
    
    needs = analyze_svg_needs(html_path)
    if not needs:
        return None
    
    if dry_run:
        return f"DRY: {name} -> {', '.join(needs)}"
    
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    modified = content
    added = []
    
    for key in needs:
        svg_html = get_svg_for_topic(key, use_ai=use_ai)
        if not svg_html:
            continue
        
        # Find injection point: after first key-point or example
        injection = None
        for marker in ['class="kp"', 'class="ex"', 'WHY BOX']:
            idx = modified.find(marker)
            if idx > 0:
                # Find closing </div>
                depth = 0
                i = modified.find('<div', idx)
                while i < len(modified):
                    if modified[i:i+4] == '<div':
                        depth += 1
                    elif modified[i:i+6] == '</div>':
                        depth -= 1
                        if depth == 0:
                            injection = i + 6
                            break
                    i += 1
                if injection:
                    break
        
        if injection:
            modified = modified[:injection] + '\n' + svg_html + '\n' + modified[injection:]
            added.append(key)
    
    if not added:
        return None
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(modified)
    
    return f"OK ({'+'.join(added)}): {name}"


def enhance_all(dry_run=True, use_ai=False):
    """Enhance all geometry lectures."""
    results = []
    for grade_dir in sorted(HANDOUT_DIR.iterdir()):
        if not grade_dir.is_dir() or grade_dir.name.startswith('_'):
            continue
        for f in sorted(grade_dir.glob('LF-*.html')):
            result = enhance_lecture(f, dry_run=dry_run, use_ai=use_ai)
            if result:
                results.append(result)
                print(f"  {result}")
    
    print(f"\nTotal: {len(results)} lectures enhanced")
    return results


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LF Vision Engine v1.0")
    parser.add_argument("--test", action="store_true", help="Test templates and AI")
    parser.add_argument("--topic", help="Generate SVG for a specific topic")
    parser.add_argument("--enhance-all", action="store_true", help="Enhance all lectures")
    parser.add_argument("--enhance", help="Enhance a specific lecture file")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--use-ai", action="store_true", help="Use AI generation (slower)")
    args = parser.parse_args()
    
    if args.test:
        print("=== LF Vision Engine v1.0 ===")
        print(f"Templates available: {len(TEMPLATES)}")
        for key in TEMPLATES:
            svg = TEMPLATES[key]()
            print(f"  {key}: {len(svg)} chars")
        
        print("\n=== Testing AI Vision (MiniMax M2.5) ===")
        svg = generate_svg_ai("right triangle with base 6cm height 8cm", "right_triangle")
        if svg:
            print(f"  AI SVG OK: {len(svg)} chars")
            print(svg[:400])
        else:
            print("  AI unavailable (frellmapi/DeepSeek) - falling back to templates")
    
    elif args.topic:
        svg = get_svg_for_topic(args.topic, use_ai=args.use_ai)
        if svg:
            print(svg)
        else:
            print(f"No template for: {args.topic}")
            print(f"Available: {', '.join(TEMPLATES.keys())}")
    
    elif args.enhance:
        result = enhance_lecture(args.enhance, dry_run=args.dry_run, use_ai=args.use_ai)
        if result:
            print(result)
        else:
            print("No enhancement needed")
    
    elif args.enhance_all:
        print(f"=== Enhancing all lectures (dry_run={args.dry_run}, use_ai={args.use_ai}) ===")
        enhance_all(dry_run=args.dry_run, use_ai=args.use_ai)
    
    else:
        parser.print_help()
