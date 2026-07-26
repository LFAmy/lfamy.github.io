#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug - write exact content patterns to a log file."""

FILEPATH = r'g:\lam-fung-academy\_deploy\講義\_summer2026_accel\學生版\LF-SUMMER-ACCEL-P4-L07_百分數應用：折扣與利息（P5下預習）_精英版.html'

with open(FILEPATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the 純計算練習 section
idx = content.find('課後純計算練習')
out = []
out.append(f"Index of 課後純計算練習: {idx}")
out.append("")

# Show exact repr of the first calc question area
start = content.find('35%')
out.append(f"Index of 35%: {start}")
if start >= 0:
    chunk = content[start-30:start+100]
    out.append(f"repr: {repr(chunk)}")

# Show the full 純計算練習 section
calc_start = content.find('lf-h2">🧮 課後純計算練習')
calc_end = content.find('</div>', content.find('</div>', calc_start + 100) + 10)
# Actually let's find where it ends - after the 10th Q10
q10_start = content.rfind('Q10')
q10_end = content.find('</div>', q10_start)
calc_end = content.find('</div>', q10_end + 10) + 7

section = content[calc_start:calc_end]
out.append(f"\nFull section length: {len(section)}")
out.append(f"\nSection repr (first 200 chars):")
out.append(repr(section[:200]))
out.append(f"\nSection repr (last 200 chars):")
out.append(repr(section[-200:]))

# Check for tab characters
out.append(f"\nTab chars in section: {section.count(chr(9))}")
out.append(f"Tab chars before Q1: {section[:section.find('Q1')].count(chr(9))}")

# Show the exact content from lf-h2 to the end of practice-section
h2_idx = content.rfind('lf-h2">🧮 課後純計算練習')
section_end = content.find('</div>\n\n\t</div>\n\t</body>')
if section_end < 0:
    section_end = content.find('</body>')
full_section = content[h2_idx:section_end]
out.append(f"\nFull section from h2 to body: {len(full_section)} chars")
out.append(f"\nrepr of full section:")
out.append(repr(full_section))

with open(r'g:\lam-fung-academy\_deploy\講義\_summer2026_accel\學生版\debug_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print("Debug output written to debug_output.txt")
