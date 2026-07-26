#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug - find exact content patterns in the file."""

FILEPATH = r'g:\lam-fung-academy\_deploy\講義\_summer2026_accel\學生版\LF-SUMMER-ACCEL-P4-L07_百分數應用：折扣與利息（P5下預習）_精英版.html'

with open(FILEPATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Show exact repr of the section around 純計算練習
idx = content.find('課後純計算練習')
if idx >= 0:
    chunk = content[idx-10:idx+1500]
    # Print as repr to see exact characters
    print(repr(chunk))
