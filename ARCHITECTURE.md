# LF Academy — System Architecture v1.0

> Hong Kong Primary Math Tutorial Platform | 909 Lectures | AI-Driven | Firebase Deployed
> Standards: ACIF 5-Gate | 1EdTech Best Practices | QM Higher Ed Rubric

## AI Provider Architecture (6-Tier Chain)
Tier 0: frellmapi (localhost:3001) -> Tier 1: DeepSeek API -> Tier 2: NVIDIA NIM -> Tier 3: OpenRouter -> Tier 4: Gemini -> Tier 5: LM Studio/Ollama
All keys centralized in .env -> _config/secrets.py

## Quality Framework
Based on ACIF (AI-Generated Content Integrity Framework) + 1EdTech BP v1.0 + QM Rubric 7th Ed.

### 5-Gate Pipeline
1. PRE-DELIVERY — Structural integrity (HTML, CSS, MathJax, Schema)
2. FACTUAL — F.A.C.T. hallucination detection (Find/Assess/Cross-ref/Tag)
3. AGE — Age-appropriateness for P3-P6 bands (8-12 years)
4. CURRICULUM — HK SSPA exam alignment, topic coverage, learning objectives
5. DEPLOY — File naming, size, encoding, link integrity

### Quality Metrics (2026-06-11 Audit, 909 files)
WHY BOX: 99% | SSPA Markers: 100% | Parent Summary: 99% | Story Context: 99%
Trap Examples: 99% | Learning Objectives: 97% | SVG Graphics: 97% | Fractions: 68%

### Quality Tools
- quality_audit.py v2.0 — Full-scan (909 files, JSON export)
- quality_gate.py v1.0 — ACIF 5-Gate pipeline
- fact_check.py v1.0 — F.A.C.T. hallucination detector
- inject_provenance.py v1.0 — AI provenance metadata (1EdTech-compliant)
- quality_dashboard.py v2.0 — HTML dashboard with real data

## Key Commands
  python _tools/quality_audit.py --json      # Full scan
  python _tools/quality_gate.py --grade P6   # 5-Gate check
  python _tools/fact_check.py --grade P6     # F.A.C.T. scan
  python _tools/quality_dashboard.py         # Dashboard
  python tests/test_smoke.py                # 15 engine tests
  cd _deploy; firebase deploy --only hosting

## Development Rules
1. No inline Python >5 lines -> write .py file
2. No frellmapi retry >1 -> use DeepSeek direct
3. No regex on HTML -> use html.parser/BeautifulSoup
4. Secrets in .env only -> _config/secrets.py
5. All Chinese-output scripts: io.TextIOWrapper wrapper
6. Lecture naming: LF-{grade}-{term}-L{num}_{topic}.html
