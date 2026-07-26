#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix LF Summer Accel P4 L07 lecture file with all 5 fixes."""

import sys
sys.stdout.reconfigure(encoding='utf-8')

FILEPATH = r'g:\lam-fung-academy\_deploy\講義\_summer2026_accel\學生版\LF-SUMMER-ACCEL-P4-L07_百分數應用：折扣與利息（P5下預習）_精英版.html'

with open(FILEPATH, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ====================================================================
# FIX 2: Enhance example steps
# ====================================================================

# 例题 1: Expand to show formula + substitution + computation
old1 = '<div class="step"><span class="step-num">1</span>八折 = 80% = 0.8</div>\n\t<div class="step"><span class="step-num">2</span>售價 $= 400 \\times 0.8$</div>\n\t<div class="step-result">'
new1 = '<div class="step"><span class="step-num">1</span>八折 = 80% = 0.8</div>\n\t<div class="step"><span class="step-num">2</span>售價 = 原價 × 折扣率</div>\n\t<div class="step"><span class="step-num">3</span>售價 $= 400 \\times 0.8$</div>\n\t<div class="step"><span class="step-num">4</span>$400 \\times 0.8 = 320$</div>\n\t<div class="step-result">'

if old1 in content:
    content = content.replace(old1, new1)
    changes += 1
    print(f"Fix 2a: 例题1 expanded (4 steps)")
else:
    print(f"Fix 2a: FAIL - pattern not found for 例题1")

# 例题 2: Expand simple interest steps
old2 = '<div class="step"><span class="step-num">1</span>已知：本金 $= 1000$，年利率 $= 2\\% = 0.02$，年數 $= 3$</div>\n\t<div class="step"><span class="step-num">2</span>利息 $= 1000 \\times 0.02 \\times 3 = 60$</div>\n\t<div class="step-result">'
new2 = '<div class="step"><span class="step-num">1</span>已知：本金 $= 1000$，年利率 $= 2\\% = 0.02$，年數 $= 3$</div>\n\t<div class="step"><span class="step-num">2</span>利息 = 本金 × 年利率 × 年數</div>\n\t<div class="step"><span class="step-num">3</span>利息 $= 1000 \\times 0.02 \\times 3$</div>\n\t<div class="step"><span class="step-num">4</span>$1000 \\times 0.02 \\times 3 = 60$</div>\n\t<div class="step-result">'

if old2 in content:
    content = content.replace(old2, new2)
    changes += 1
    print(f"Fix 2b: 例题2 expanded (4 steps)")
else:
    print(f"Fix 2b: FAIL - pattern not found for 例题2")

# 例题 2(b): Expand interest steps
old2b = '<div class="step"><span class="step-num">1</span>已知：本金 $= 5000$，年利率 $= 4\\% = 0.04$，半年 $= 0.5$ 年</div>\n\t<div class="step"><span class="step-num">2</span>利息 $= 5000 \\times 0.04 \\times 0.5 = 100$</div>\n\t<div class="step-result">'
new2b = '<div class="step"><span class="step-num">1</span>已知：本金 $= 5000$，年利率 $= 4\\% = 0.04$，半年 $= 0.5$ 年</div>\n\t<div class="step"><span class="step-num">2</span>利息 = 本金 × 年利率 × 年數</div>\n\t<div class="step"><span class="step-num">3</span>利息 $= 5000 \\times 0.04 \\times 0.5$</div>\n\t<div class="step"><span class="step-num">4</span>$5000 \\times 0.04 \\times 0.5 = 100$</div>\n\t<div class="step-result">'

if old2b in content:
    content = content.replace(old2b, new2b)
    changes += 1
    print(f"Fix 2c: 例题2(b) expanded (4 steps)")
else:
    print(f"Fix 2c: FAIL - pattern not found for 例题2(b)")

# 例题 1(b): The steps 售價 = 320 × 0.75 = 240 - split into substitution + computation
old1b = '<div class="step"><span class="step-num">1</span>七五折 = 75% = 0.75</div>\n\t<div class="step"><span class="step-num">2</span>售價 $= 320 \\times 0.75 = 240$</div>\n\t<div class="step"><span class="step-num">3</span>節省 $= 320 - 240 = 80$</div>'
new1b = '<div class="step"><span class="step-num">1</span>七五折 = 75% = 0.75</div>\n\t<div class="step"><span class="step-num">2</span>售價 $= 320 \\times 0.75$</div>\n\t<div class="step"><span class="step-num">3</span>$320 \\times 0.75 = 240$</div>\n\t<div class="step"><span class="step-num">4</span>節省 $= 320 - 240 = 80$</div>'

if old1b in content:
    content = content.replace(old1b, new1b)
    changes += 1
    print(f"Fix 2d: 例题1(b) expanded (4 steps)")
else:
    print(f"Fix 2d: FAIL - pattern not found for 例题1(b)")

# 例题 3: already has 2 detailed steps with computation inline - enhance
old3 = '<div class="step"><span class="step-num">1</span>加價 15%：新價 $= 80 \\times (1 + 0.15) = 80 \\times 1.15 = 92$</div>\n\t<div class="step"><span class="step-num">2</span>打九折：最終售價 $= 92 \\times 0.9 = 82.8$</div>\n\t<div class="step-result">✅ 最終售價 $= \\$82.80$</div>'
new3 = '<div class="step"><span class="step-num">1</span>加價 15%：新價 $= 80 \\times (1 + 0.15) = 80 \\times 1.15 = 92$</div>\n\t<div class="step"><span class="step-num">2</span>打九折：最終售價 $= 92 \\times 0.9$</div>\n\t<div class="step"><span class="step-num">3</span>$92 \\times 0.9 = 82.8$</div>\n\t<div class="step-result">✅ 最終售價 $= \\$82.80$</div>'

if old3 in content:
    content = content.replace(old3, new3)
    changes += 1
    print(f"Fix 2e: 例题3 expanded (3 steps)")
else:
    print(f"Fix 2e: FAIL - pattern not found for 例题3")

# 例题 3(b): already has 3 steps - split steps 1 and 2
old3b = '<div class="step"><span class="step-num">1</span>減價 10%：新價 $= 2400 \\times (1 - 0.1) = 2400 \\times 0.9 = 2160$</div>\n\t<div class="step"><span class="step-num">2</span>加價 5%：最終 $= 2160 \\times (1 + 0.05) = 2160 \\times 1.05 = 2268$</div>\n\t<div class="step"><span class="step-num">3</span>比較：$2268 < 2400$，比原價便宜了</div>'
new3b = '<div class="step"><span class="step-num">1</span>減價 10%：新價 $= 2400 \\times (1 - 0.1)$</div>\n\t<div class="step"><span class="step-num">2</span>$2400 \\times 0.9 = 2160$</div>\n\t<div class="step"><span class="step-num">3</span>加價 5%：最終 $= 2160 \\times (1 + 0.05)$</div>\n\t<div class="step"><span class="step-num">4</span>$2160 \\times 1.05 = 2268$</div>\n\t<div class="step"><span class="step-num">5</span>比較：$2268 < 2400$，比原價便宜了</div>'

if old3b in content:
    content = content.replace(old3b, new3b)
    changes += 1
    print(f"Fix 2f: 例题3(b) expanded (5 steps)")
else:
    print(f"Fix 2f: FAIL - pattern not found for 例题3(b)")

# ====================================================================
# FIX 5: Replace 純計算練習 with P5-level calculations (P4精英版 = push 1 grade)
# ====================================================================

# Find the 純計算練習 section and replace it
old_calc_section = '''\t<div class="lf-h2">🧮 課後純計算練習</div>
\t<div class="practice-section">

\t<div class="practice-q">
\t<span class="q-num">Q1</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">將 35% 化為小數。</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q2</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">將 0.28 化為百分數。</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q3</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$250 \\times 0.8 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q4</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$380 \\times 0.65 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q5</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$45\\% = ?$（化為小數）</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q6</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$75\\% = ?$（化為小數）</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q7</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$1200 \\times 0.7 \\times 0.9 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q8</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$5000 \\times 0.03 \\times 2 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q9</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$800 \\times 1.1 \\times 0.85 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q10</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$600 \\times 0.75 + 400 \\times 0.8 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t</div>'''

new_calc_section = '''\t<div class="lf-h2">🧮 課後純計算練習</div>
\t<div class="practice-section">

\t<div class="practice-q">
\t<span class="q-num">Q1</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$4800 \\times 0.75 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q2</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$3250 \\times 0.65 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q3</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$7200 \\times 0.08 \\times 3 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q4</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$5400 \\times 1.15 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q5</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$12500 \\times 0.7 \\times 0.9 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q6</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$8500 \\times 0.035 \\times 2 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q7</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$4800 \\times 1.2 \\times 0.75 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q8</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$7500 \\times 0.6 + 1800 \\times 0.85 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q9</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$6300 \\times 0.25 + 2700 \\times 0.4 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t<div class="practice-q">
\t<span class="q-num">Q10</span> <span class="q-level">計算</span>
\t<p style="margin-top:8pt;">$9600 \\times 0.55 - 2400 \\times 0.7 = ?$</p>
\t<div class="answer-line-double"></div>
\t</div>

\t</div>'''

if old_calc_section in content:
    content = content.replace(old_calc_section, new_calc_section)
    changes += 1
    print(f"Fix 5: 純計算練習 replaced with P5-level questions")
else:
    print(f"Fix 5: FAIL - pattern not found for 純計算練習 (trying substring match...)")
    # Debug: find parts of the section
    if '課後純計算練習' in content:
        print(f"  '課後純計算練習' found")
    if '將 35% 化為小數' in content:
        print(f"  '將 35% 化為小數' found")
    else:
        print(f"  '將 35% 化為小數' NOT found - encoding issue?")

print(f"\nTotal changes applied: {changes}")

if changes > 0:
    with open(FILEPATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("File written successfully.")
