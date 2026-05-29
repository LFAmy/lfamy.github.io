# EN Translation Pipeline — Design Spec
*2026-05-23 | 霖楓學苑 Lam Fung Academy*

## Goal
Translate all P5 handouts (39 files) from Traditional Chinese to professional English, preserving v6 template structure, SVG diagrams, and CSS fractions.

## Approach: Semi-Automated Pipeline (Route B)

### Architecture
```
[Chinese HTML] → [Text Extractor] → [Glossary + API Translation] → [Re-inject] → [English HTML]
```

### Components

**1. Glossary System** (`scripts/en_glossary.json`)
- 200+ math terms (中→英)
- Structural terms (陷阱→trap, 口訣→mnemonic, 知識點→knowledge point)
- Difficulty levels (🌱基礎→Basic, 🌿進階→Advanced, 🏔️挑戰→Challenge, ⚡極端→Extreme)
- Section headers (一、→I., 二、→II., etc.)
- Brand terms (霖楓學苑→Lam Fung Academy)

**2. Translation Script** (`scripts/translate_p5.py`)
- BeautifulSoup HTML parser
- Text node extraction (skip SVG, CSS, structural HTML)
- Glossary-first translation (exact matches)
- Pattern matching for common structures
- Fallback to Claude API for complex text
- Metadata update (lang, title, footer)

**3. Quality Validator** (reuse `validate_quality.py`)
- Check question count preserved
- Check SVG count preserved
- Check footer format correct
- Check v6 CSS classes intact

### Translation Rules

**Preserve:**
- All `<svg>` elements and attributes
- CSS fraction classes (`.f`, `.fd`, `.fi`)
- HTML structure and class names
- Math notation (fractions written as `<span class="f">`)

**Translate:**
- Question text
- Knowledge point explanations
- Trap descriptions
- Mnemonics (creative translation, not literal)
- Section headers
- Cover page info
- Footer (update format)

**Adapt:**
- 🌱 → Basic, 🌿 → Advanced, 🏔️ → Challenge, ⚡ → Extreme
- 一、二、三 → I., II., III.
- 小五 → Primary 5
- 第 X 堂 → Lesson X

### File Naming
- Source: `講義/P5/LF-P5-上-L08_異分母分數加法.html`
- Output: `講義/P5/EN/LF-P5-上-L08_EN_Adding_Fractions_With_Different_Denominators.html`

### Quality Standards
- Mathematical accuracy: 100% (zero tolerance for wrong translations)
- Grammar: Native English speaker level
- Consistency: Same term translated same way across all files
- Cultural adaptation: HK-specific examples preserved (HKD, local references)

## Scope
- Phase 1: P5 (39 files) — current
- Phase 2: P6 (39 files) — after P5
- Phase 3: P3/P4 (80 files) — after P6

## Success Criteria
- All 39 P5 EN files pass quality validator
- PDFs generated for all 39 EN files
- Random sample of 3 files reviewed by human
