# CLAUDE.md — 霖楓學苑 (Lam Fung Academy) + Ruflo Swarm

## 專案定位

香港小學數學補習教材生產系統 + 教育營銷內容工廠
- Python + Node.js 混合工具鏈 (SVG/MathJax/OCR)
- 70+ 份 P5/P6 HTML 講義, 自行開發幾何 SVG 庫
- 教育內容+營運文件+市場研究三合一
- **Ruflo Swarm = 教材批量生產 + 宣傳資料平行輸出**

## 🔴 強制基礎設施規則

- 創建 `.gitignore` 排除 `node_modules/`, `__pycache__/`, `.ipynb_checkpoints/`
- 創建 `requirements.txt` 記錄 Python 依賴
- 商業機密文件需確認是否應納入版本控制

## 🔴 Ruflo 強制規則

- 批量講義生產（5+ 份）→ Batch Fan-out 模式
- 宣傳資料+文案+市場材料可並行 → Fan-out
- 教育內容品質審查 → Pipeline 模式

---

## 技能綁定

| 場景 | 技能 |
|------|------|
| 🔴 每次對話開始 | `using-superpowers` |
| Python 工具開發 | `python-patterns`, `python-testing` |
| 前端/HTML 模板 | `frontend-design`, `design-system`, `ui-ux-pro-max` |
| 內容生產自動化 | `content-engine` |
| AI 圖片生成 | `fal-ai-media` |
| 文件生成 (PDF/DOCX) | `pdf`, `docx`, `markitdown` |
| 品牌設計 | `brand-guidelines`, `theme-factory` |
| 除錯/報錯 | `systematic-debugging` |
| 規劃新功能 | `writing-plans`, `brainstorming` |
| 程式碼重整 | `coding-standards`, `simplify` |
| 安全檢查 | `security-review` |
| 行銷文案 | `copywriter`, `writing-skills` |
| 市場研究 | `market-research` |
| Token 壓縮 | `caveman`, `caveman-commit` |

---

## Ruflo Swarm 教育生產路由

### 三種平行模式

| Pattern | Flow | Use When |
|---------|------|----------|
| **Fan-out** | Lead → 文案A, 文案B, 設計C, 研究D → Lead | 宣傳資料多管道同步生產 |
| **Batch Fan-out** | Lead → 講義P5團隊, 講義P6團隊, 文案團隊 → Lead | 教材+宣傳同步輸出 |
| **Pipeline** | 研究 → 撰寫 → 審查 → 排版 → 輸出 | 高品質單份講義 |

### Agent 路由表

| 任務 | Agents | Topology | 觸發條件 |
|------|--------|----------|---------|
| 批量講義生產 | lecture-writer x N | batch-fan-out | "同時做 P5 第3-8 課" |
| 宣傳資料包 | copywriter, designer, market-researcher | fan-out | "做一組宣傳資料" |
| 多平台文案 | xiaohongshu-writer, facebook-writer, whatsapp-writer | fan-out | "同步發各平台文案" |
| 市場研究 | competitor-analyst, trend-researcher, pricing-analyst | fan-out | "研究競品和市場" |
| 講義品質審查 | math-reviewer, design-reviewer, content-reviewer | fan-out | "審查這批講義" |
| 課綱設計 | curriculum-designer, exercise-generator, assessment-designer | pipeline | "設計新課綱" |
| 品牌物料 | brand-designer, copywriter, visual-designer | fan-out | "做品牌宣傳資料" |

### 平行 Agent 定義

```
教育內容團隊 = {
  lecture-writer:     講義 HTML 撰寫 + MathJax 公式 + SVG 圖形
  exercise-generator: 練習題生成 + 答案 + 解題步驟
  copywriter:         廣告文案 + 社群貼文 + 家長通告
  designer:           排版 + 色彩 + 品牌一致
  market-researcher:  競品分析 + 定價研究 + 市場趨勢
  math-reviewer:      數學正確性檢查 + 難度評估
  brand-designer:     品牌物料 + Logo + 海報 + 宣傳單
}
```

---

## Ruflo 批量生產 SOP

```
# 步驟 1: 同時啟動講義生產團隊
Agent({ name: "lecture-p5-3", subagent_type: "general-purpose", run_in_background: true,
  prompt: "生產 P5 第3課講義。使用 _templates/ 模板，MathJax 公式，SVG 幾何圖。完成後 SendMessage 給 lead。" })
Agent({ name: "lecture-p5-4", subagent_type: "general-purpose", run_in_background: true,
  prompt: "生產 P5 第4課講義。" })
Agent({ name: "lecture-p5-5", subagent_type: "general-purpose", run_in_background: true,
  prompt: "生產 P5 第5課講義。" })

# 步驟 2: 同時生產多平台宣傳文案
Agent({ name: "copy-fb", subagent_type: "general-purpose", run_in_background: true,
  prompt: "撰寫 Facebook 宣傳文案，推廣 P5 數學課程。" })
Agent({ name: "copy-xhs", subagent_type: "general-purpose", run_in_background: true,
  prompt: "撰寫小紅書宣傳文案。" })
Agent({ name: "copy-wa", subagent_type: "general-purpose", run_in_background: true,
  prompt: "撰寫 WhatsApp 家長群組廣播文案。" })

# 步驟 3: 品質審查
Agent({ name: "qa-reviewer", subagent_type: "general-purpose", run_in_background: true,
  prompt: "審查所有講義和文案的數學正確性、品牌一致性、排版品質。" })
```

---

## 專案架構

```
lam-fung-academy/
├── _tools/                  # Python 生產工具
│   ├── svg_geometry.py      # SVG 幾何庫 v2.3
│   ├── render_math.py       # LaTeX→PNG 渲染
│   ├── build_demo.py        # 講義建構器
│   └── replace_*.py         # 批次替換工具
├── _templates/              # HTML 模板
├── 講義/                    # 所有講義
│   ├── P5/                  # P5 (40課 + SSPA模擬)
│   └── P6/                  # P6 (20+課)
├── _ocr_pages/              # 掃描課本頁面
├── _ocr_text/               # OCR 輸出
├── ocr_batch.cjs            # 批次 OCR 腳本
└── *.md                     # 營運文件
```

---

## 3-Tier Model Routing (Ruflo 成本優化)

| Tier | Handler | Use Cases |
|------|---------|-----------|
| 1 | Haiku | 簡單文案變體、OCR 文字清理、格式轉換 |
| 2 | Sonnet | 講義內容撰寫、宣傳文案、課綱設計 |
| 3 | Opus | 整體課程體系設計、品牌策略、市場定位 |

---

## 關鍵限制

- HTML 講義為自包含格式 (SVG 內嵌, base64 圖片), 無外部依賴
- MathJax v4.1.2 CDN 載入 (需網路), PDF 輸出為離線版本
