#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug - show exact content of example sections."""

FILEPATH = r'g:\lam-fung-academy\_deploy\講義\_summer2026_accel\學生版\LF-SUMMER-ACCEL-P4-L07_百分數應用：折扣與利息（P5下預習）_精英版.html'
OUTFILE = r'g:\lam-fung-academy\_deploy\講義\_summer2026_accel\學生版\debug_examples_output.txt'

with open(FILEPATH, 'r', encoding='utf-8') as f:
    content = f.read()

lines = []
for term in ['例題 1', '例題 2', '例題 3', '例題 1(b)', '例題 2(b)', '例題 3(b)']:
    idx = content.find(term)
    if idx >= 0:
        chunk = content[idx-5:idx+400]
        lines.append(f"=== {term} ===")
        lines.append(repr(chunk))
        lines.append("")

with open(OUTFILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f"Written to {OUTFILE}")
