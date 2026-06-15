# Codex Brain v15.0 — LF Academy Production

> 生產級 AI 工程 · EdTech 模式 · 品質閘道
> 哲學: 空杯心態。第一性原則。不設限。持續進化。

## 🫀 心跳
v15.0 #{N} | {intent} | {agent} | {step} | {quality_gate}

## 🔬 研究優先
任何分析/決策先搜後思。憑訓練數據回答 = 偏離。

## 🧭 任務路由
S ≤ 3: sync 直接執行 | 4 ≤ S ≤ 8: async 平行派發 | S ≥ 9: hierarchical 層級派發

## 🛡 品質閘道 + 權限
default / acceptEdits / plan — 依代理類型選用。

## 🎯 目標錨定
長任務 (≥10 steps) 每 5 步注入目標進度檢查。

## 🟣 閉環
研究驗證 → 技能匹配 → 代理回收 → IPC整合 → 記憶寫入 → 漂移檢測 → 品質閘道 → 部署同步

---

# 🏫 LF Academy (霖楓學苑)

香港小學數學補習平台 · 172 講義 · AI 驅動 · Firebase 部署

## 專案架構
```
G:\lam-fung-academy\
├── 講義/P3/ P4/ P5/ P6/     ← 172 主講義 HTML
├── engines/                   ← 11 AI 引擎 (lf_ai_brain.py 核心: 6層 Provider 鏈)
├── scripts/                   ← 165 腳本 (hk_exam_engine.py, inject_svg_frac.py 等)
├── _deploy/                   ← Firebase 部署 (1,783 檔案)
├── data/exams/                ← 20 模擬試卷
├── pdf_output/                ← 826 PDFs
└── .agent/                    ← 便攜代理記憶
```

## AI Provider 鏈 (全免費)
Primary: frellmapi (localhost:3001) → Fallback: DeepSeek API → Tier 2: NVIDIA NIM → Tier 3: OpenRouter → Tier 4: Gemini → Tier 5: LM Studio → Tier 6: Ollama

## 部署 URL
- 主站: https://lfacademyhk.com
- 備用: https://lfady-b1761.web.app
- API: https://lf-api-f80h.onrender.com
- AI Tutor: https://lfacademyhk.com/ai-tutor.html

## 品質標準 (172 講義)
| 指標 | 目標 | 現狀 |
|------|------|------|
| WHY BOX / SSPA 標記 / 家長摘要 / 故事情境 | 100% | ✅ 100% |
| 學習目標 | 100% | 94% |
| 陷阱例題 | 100% | 91% |
| SVG 圖解 | 80%+ | 67% |
| Fractions | 70%+ | 51% |

## 常用命令
```powershell
cd G:\lam-fung-academy
python _tools/quality_audit.py                           # 品質審查
python scripts/hk_exam_engine.py assemble --grade P6 --output-html
python scripts/hk_exam_engine.py generate --grade P6 --topic "小數除法" --count 3
python scripts/pipeline_html2pdf.py --grade P6 --workers 3
python scripts/inject_svg_frac.py --grade P6
python scripts/auto_answer_key.py
cd _deploy; firebase deploy --only hosting
```

## 開發規則
1. No inline Python >5 lines → write .py file
2. No frellmapi retry >1 → use DeepSeek direct
3. No regex on HTML → use html.parser
4. Spawn sub-agents for parallel work
5. Verify before marking complete
6. Use scripts/lf_py.py for all Chinese-output Python
7. 所有 Python 腳本含中文輸出: sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
8. 講義命名: LF-{grade}-{上/下/暑假}-L{num}_{topic}.html
