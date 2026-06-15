#!/usr/bin/env python3
"""LF Academy — Core Engine Smoke Tests v1.0"""
import sys, os, io

sys.path.insert(0, ".")
sys.path.insert(0, "engines")
sys.path.insert(0, "scripts")

passed = 0
failed = 0

def test(name, import_path):
    global passed, failed
    try:
        mod = __import__(import_path)
        print(f"  PASS  {name}")
        passed += 1
        return True
    except Exception as e:
        print(f"  FAIL  {name}: {str(e)[:100]}")
        failed += 1
        return False

print("=" * 60)
print("  LF Academy Core Engine Smoke Tests")
print("=" * 60)
print()

engines = [
    ("lf_ai_brain", "engines.lf_ai_brain"),
    ("tutor_engine", "engines.tutor_engine"),
    ("mark_engine", "engines.mark_engine"),
    ("lf_vision", "engines.lf_vision"),
    ("ai_autopilot", "engines.ai_autopilot"),
    ("marketing_brain", "engines.marketing_brain"),
    ("parent_report_engine", "engines.parent_report_engine"),
    ("enrichment_engine", "engines.enrichment_engine"),
    ("gamification", "engines.gamification"),
    ("misconception_engine", "engines.misconception_engine"),
    ("class_analytics", "engines.class_analytics"),
    ("adaptive_engine", "engines.adaptive_engine"),
    ("payment_engine", "engines.payment_engine"),
    ("_config/secrets.py", "_config.secrets"),
]

for name, path in engines:
    test(name, path)

# Verify quality_audit.py is parseable
try:
    with open("_tools/quality_audit.py", "r", encoding="utf-8") as f:
        compile(f.read(), "quality_audit.py", "exec")
    print("  PASS  quality_audit.py (parseable)")
    passed += 1
except Exception as e:
    print(f"  FAIL  quality_audit.py: {str(e)[:100]}")
    failed += 1

print()
print("-" * 60)
print(f"  Results: {passed} passed, {failed} failed ({passed+failed} total)")
if failed == 0:
    print("  ALL SMOKE TESTS PASSED")
else:
    print(f"  {failed} TESTS FAILED")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
