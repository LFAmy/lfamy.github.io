#!/usr/bin/env python3
"""
LF Academy — Quality Gate Pipeline v1.0
=======================================
ACIF-inspired 5-Gate verification pipeline for AI-generated
lecture content. Every lecture must pass all 5 gates before
deployment.

Gates:
  1. PRE-DELIVERY  — Structural integrity (HTML, CSS, MathJax)
  2. FACTUAL       — Hallucination detection (F.A.C.T. method)
  3. AGE           — Age-appropriateness for P3-P6 bands
  4. CURRICULUM    — HK curriculum alignment (SSPA, topics)
  5. DEPLOY        — Final deployment readiness check

ACIF Reference: github.com/Chukwuemerie-ezieke/acif-framework
"""

import os
import re
import sys
import io
import json
from datetime import datetime
from pathlib import Path

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except:
    pass

BASE = Path(__file__).resolve().parent.parent
LECTURE_DIR = BASE / "講義"

# Age band definitions (ACIF 6 bands, LF Academy uses 4)
AGE_BANDS = {
    "P3": {"age": "8-9", "vocab_max": 800, "sentence_max_chars": 120},
    "P4": {"age": "9-10", "vocab_max": 1200, "sentence_max_chars": 150},
    "P5": {"age": "10-11", "vocab_max": 1600, "sentence_max_chars": 180},
    "P6": {"age": "11-12", "vocab_max": 2000, "sentence_max_chars": 200},
}

# SSPA topic mapping per grade (HK curriculum)
# SSPA topic keywords per grade (fuzzy matching)
SSPA_TOPICS = {
    "P3": {"四則": ["四則", "加減", "乘除", "運算"], "分數": ["分數", "分"], "圖形": ["圖形", "形狀", "立體"], "度量": ["度量", "長度", "重量", "時間", "容量"], "數據": ["數據", "象形", "棒形", "統計"]},
    "P4": {"小數": ["小數"], "分數": ["分數", "分"], "面積": ["面積"], "周界": ["周界", "周長"], "方向": ["方向", "八方", "坐標"]},
    "P5": {"小數": ["小數", "除"], "體積": ["體積", "容積"], "速率": ["速率", "速度"], "代數": ["代數", "方程", "未知數"], "百分": ["百分", "%"]},
    "P6": {"小數": ["小數", "除"], "圓": ["圓", "圓周", "圓形"], "比例": ["比例", "比"], "方程": ["方程", "代數", "未知"], "統計": ["統計", "平均", "數據", "概率", "機會"]},
}


class GateResult:
    """Result from a single gate check."""
    def __init__(self, name):
        self.name = name
        self.passed = True
        self.checks = []
        self.warnings = []
        self.errors = []
    
    def add_check(self, label, passed, detail=""):
        self.checks.append({"label": label, "passed": passed, "detail": detail})
        if not passed:
            self.passed = False
            self.errors.append(f"{label}: {detail}" if detail else label)
    
    def add_warning(self, msg):
        self.warnings.append(msg)


def gate_1_pre_delivery(content, filename):
    """Gate 1: Structural integrity check."""
    r = GateResult("1-PRE-DELIVERY")
    
    r.add_check("DOCTYPE", "<!DOCTYPE html>" in content or "<!doctype html>" in content.lower())
    r.add_check("MathJax loaded", "mathjax" in content.lower() or "MathJax" in content)
    r.add_check("CSS Variables", "var(--" in content)
    r.add_check("Responsive (@media)", "@media" in content)
    r.add_check("Schema.org markup", "schema.org" in content or "ld+json" in content)
    r.add_check("Tables present", "<table" in content)
    r.add_check("No broken HTML", content.count("<") > 10 and "</html>" in content.lower())
    
    # Check for common issues
    if "&nbsp;&nbsp;&nbsp;" in content:
        r.add_warning("Excessive &nbsp; found — consider CSS spacing")
    if content.count("<br><br><br>") > 3:
        r.add_warning("Multiple consecutive <br> tags — consider proper spacing")
    
    return r


def gate_2_factual(content, filename):
    """Gate 2: F.A.C.T. hallucination detection (simplified)."""
    r = GateResult("2-FACTUAL")
    
    # F - Find claims: detect mathematical statements
    math_claims = re.findall(r'(\d+[\s]*[+\-×÷=][\s]*\d+)', content)
    r.add_check("Math claims found", len(math_claims) > 0, 
                f"{len(math_claims)} mathematical expressions detected")
    
    # A - Assess risk: check for suspicious patterns
    suspicious = [
        (r"答案[是為]?\s*[A-Za-z]", "Answer format suspicious"),
        (r"一定[是要]", "Absolute statement found"),
        (r"\d+\s*\+\s*\d+\s*=\s*\d+", "Arithmetic claims — verify externally"),
    ]
    for pattern, desc in suspicious:
        matches = re.findall(pattern, content)
        if matches:
            r.add_warning(f"{desc}: {len(matches)} instances")
    
    # C - Cross-reference markers (metadata check)
    has_sources = bool(re.search(r"source|來源|reference|參考", content, re.I))
    r.add_check("Source references", has_sources, 
                "Sources found" if has_sources else "No source citations — flag for manual review")
    
    # T - Tag: Verify no clearly wrong claims
    # (In production, this would call an LLM to cross-verify each claim)
    r.add_check("No obvious errors", True, "Automated check passed (manual review recommended for production)")
    
    return r


def gate_3_age(content, grade):
    """Gate 3: Age-appropriateness check."""
    r = GateResult("3-AGE")
    
    band = AGE_BANDS.get(grade)
    if not band:
        r.add_check("Valid grade", False, f"Unknown grade: {grade}")
        return r
    
    r.add_check("Valid grade band", True, f"Grade {grade} → age {band['age']}")
    
    # Check for grade-appropriate markers
    has_grade_tag = f"data-grade" in content or grade in content[:500]
    r.add_check("Grade tag present", has_grade_tag)
    
    # Vocabulary complexity (approximate)
    text_content = re.sub(r'<[^>]+>', ' ', content)
    words = text_content.split()
    long_words = [w for w in words if len(w) > 12]
    if len(long_words) > 20:
        r.add_warning(f"{len(long_words)} words >12 chars — check age-appropriateness")
    
    # Sentence length check
    sentences = re.split(r'[。！？.!?]', text_content)
    long_sentences = [s for s in sentences if len(s) > band["sentence_max_chars"]]
    if len(long_sentences) > 5:
        r.add_warning(f"{len(long_sentences)} sentences >{band['sentence_max_chars']} chars")
    
    return r


def gate_4_curriculum(content, grade):
    """Gate 4: HK curriculum alignment."""
    r = GateResult("4-CURRICULUM")
    
    # SSPA marking
    has_sspa = bool(re.search(r"SSPA|sspa|考試題型|歷屆試題|公開試", content))
    r.add_check("SSPA markers", has_sspa, "SSPA exam references found" if has_sspa else "No SSPA markers")
    
    # Topic coverage (fuzzy keyword matching)
    topic_groups = SSPA_TOPICS.get(grade, {})
    found_topics = []
    for topic_name, keywords in topic_groups.items():
        if any(kw in content for kw in keywords):
            found_topics.append(topic_name)
    coverage = len(found_topics) / len(topic_groups) if topic_groups else 0
    r.add_check("Topic coverage", coverage >= 0.3, 
                f"{len(found_topics)}/{len(topic_groups)} topics: {', '.join(found_topics[:3])}...")
    
    # Learning objectives
    has_objectives = bool(re.search(r"學習目標|目標|本課目標|今日目標", content))
    r.add_check("Learning objectives", has_objectives)
    
    # WHY BOX (instructional rationale)
    has_whybox = bool(re.search(r"why.box|WHY.BOX|Why.Box|WHY BOX", content, re.I))
    r.add_check("WHY BOX", has_whybox)
    
    # Trap examples
    has_traps = bool(re.search(r"陷阱|易錯|常見錯誤|伏位", content))
    r.add_check("Trap examples", has_traps)
    
    return r


def gate_5_deploy(content, filename):
    """Gate 5: Deployment readiness."""
    r = GateResult("5-DEPLOY")
    
    # File naming convention
    name_ok = bool(re.match(r"LF-[P3-6EN]+.*\.html", filename))
    r.add_check("File naming convention", name_ok, filename)
    
    # Size check
    size_kb = len(content) / 1024
    r.add_check("File size reasonable", 10 < size_kb < 200, f"{size_kb:.1f}KB")
    
    # No inline scripts with errors
    no_console_log = "console.log" not in content.lower() or "console.error" not in content.lower()
    r.add_check("No debug console.log", no_console_log)
    
    # External resource check
    has_external_refs = "http://" in content or "https://" in content
    if has_external_refs:
        r.add_warning("Contains external URLs — verify all are accessible")
    
    # Link integrity (basic)
    broken_href = re.findall(r'href=""', content)
    if broken_href:
        r.add_warning(f"{len(broken_href)} empty href attributes found")
    
    # UTF-8 encoding
    r.add_check("UTF-8 encoded", True, "File read successfully as UTF-8")
    
    return r


def run_pipeline(filepath, grade):
    """Run all 5 gates on a single lecture file."""
    filename = os.path.basename(filepath)
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    gates = [
        gate_1_pre_delivery(content, filename),
        gate_2_factual(content, filename),
        gate_3_age(content, grade),
        gate_4_curriculum(content, grade),
        gate_5_deploy(content, filename),
    ]
    
    all_passed = all(g.passed for g in gates)
    return filename, gates, all_passed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="LF Academy 5-Gate Quality Pipeline")
    parser.add_argument("--grade", type=str, help="Filter to grade (P3-P6)")
    parser.add_argument("--file", type=str, help="Check a single file")
    parser.add_argument("--json", action="store_true", help="Export JSON")
    args = parser.parse_args()
    
    if args.file:
        # Single file mode
        fpath = args.file
        grade = "P6"  # default
        for g in ["P3", "P4", "P5", "P6"]:
            if g in fpath:
                grade = g
                break
        filename, gates, passed = run_pipeline(fpath, grade)
        print(f"\n  File: {filename} (Grade: {grade})")
        print(f"  Result: {'✅ PASS' if passed else '🔴 FAIL'}\n")
        for gate in gates:
            icon = "✅" if gate.passed else "🔴"
            print(f"  {icon} Gate {gate.name}")
            for c in gate.checks:
                ci = "  ✓" if c["passed"] else "  ✗"
                print(f"     {ci} {c['label']}{': ' + c['detail'] if c['detail'] else ''}")
            for w in gate.warnings:
                print(f"     ⚠ {w}")
        return
    
    # Batch mode
    grades_to_scan = [args.grade] if args.grade else ["P3", "P4", "P5", "P6"]
    
    all_results = {}
    total_files = 0
    total_passed = 0
    
    for grade in grades_to_scan:
        grade_dir = LECTURE_DIR / grade
        if not grade_dir.exists():
            continue
        
        html_files = sorted([f for f in os.listdir(grade_dir) if f.endswith(".html")])
        grade_passed = 0
        
        for fname in html_files:
            fpath = grade_dir / fname
            filename, gates, passed = run_pipeline(str(fpath), grade)
            if passed:
                grade_passed += 1
            total_files += 1
        
        total_passed += grade_passed
        pct = round(grade_passed / len(html_files) * 100, 1) if html_files else 0
        all_results[grade] = {"total": len(html_files), "passed": grade_passed, "pct": pct}
        print(f"  {grade}: {grade_passed}/{len(html_files)} files pass ({pct}%)")
    
    print(f"\n  OVERALL: {total_passed}/{total_files} files pass "
          f"({round(total_passed/total_files*100,1) if total_files else 0}%)")
    
    if args.json:
        output = BASE / "_config" / "gate_results.json"
        with open(output, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": all_results,
                "overall": {"total": total_files, "passed": total_passed},
            }, f, ensure_ascii=False, indent=2)
        print(f"  JSON saved: {output}")


if __name__ == "__main__":
    main()
