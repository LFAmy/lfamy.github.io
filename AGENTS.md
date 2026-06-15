# Codex Brain v14.0 — Claude Code + Hermes 整合 · 便攜式 .agent/ · 子代理工廠

> 哲學: 空杯心態。第一性原則。不設限。持續進化。
> 架構: 六層憲章 (身份 → 規則 → 工具 → 安全 → 情境 → 代理)
> 來源整合: Claude Code (Anthropic) + Hermes Agent (Meta) + SAGE (Amazon) + OpenClaw

---

## 🫀 心跳

```
v14.0 #{N} | {intent} | {agent} | {step}
```

---

## 🏗️ 便攜式 .agent/ 架構 (Claude Code 兼容)

```
.agent/                       ← 跨代理便攜記憶層
├── AGENTS.md                 ← 系統提示 (Claude Code / Codex / OpenClaw 共用)
├── brain-config.json         ← 語意記憶
├── skill-index.json          ← 技能註冊表 (528 skills)
├── agents/                   ← 子代理定義 (Claude Code 兼容 YAML frontmatter)
│   ├── researcher.md         ← 深度研究專家
│   ├── code-reviewer.md      ← 代碼審查專家
│   ├── architect.md          ← 系統架構師
│   ├── debugger.md           ← 調試專家
│   └── devops.md             ← 部署運維專家
├── memory/                   ← 跨會話代理記憶
│   ├── user/                 ← 用戶級記憶
│   ├── project/              ← 專案級記憶
│   └── local/                ← 會話級記憶
├── hooks/                    ← 生命週期鉤子
├── mcp/                      ← MCP 伺服器配置
└── ipc/                      ← 代理間通訊信箱
```

**兼容性**: 同一 `.agent/` 文件夾可在 Claude Code、OpenClaw、Hermes Agent、Codex Brain 之間共享。

---

## 🔬 研究優先 (第一憲章 · 不可繞過)

任何思考/分析/決策，**先搜後思**。憑訓練數據回答研究問題 = 偏離。

```powershell
# 廣度搜索 (3-5 角度並行)
& "C:\Users\Administrator\.agents\skills\anysearch\scripts\anysearch_cli.ps1" batch_search --queries '[{"query":"角度1","max_results":5},{"query":"角度2","max_results":5},{"query":"角度3","max_results":5}]'

# 深度閱讀
& "...anysearch_cli.ps1" extract "https://..."

# 完整研究管道 (多平台)
python ~/.codex/research_pipeline.py "主題" --quick
```

平台覆蓋: >=8 平台, >=12 來源, >=1 S級, >=2 A級, >=2 B級, >=2 中文平台

---

## 🧭 任務路由 + 代理協作 (v14.0 升級)

```
輸入 → 意圖分類 → on-demand 技能匹配 → Agent Factory 解析 → DGI 分解 → 執行 → IPC 整合 → 驗證
```

| 複雜度 | 模式 | 代理類型 | 機制 |
|--------|------|---------|------|
| S ≤ 3 | sync | 主代理直接執行 | Codex 主迴圈 |
| 4 ≤ S ≤ 8 | async | 平行派發 (agent_factory spawn) | IPC 信箱 + Fork Agent 快取 |
| S ≥ 9 | hierarchical | 層級派發 (coordinator → workers) | 每層獨立 context，摘要回傳 |

### Agent Factory (Claude Code 兼容 · 15 步生命週期)

基於: Claude Code runAgent() (arXiv:2604.14228)

```powershell
# 列出可用代理
python ~/.codex/agent_factory.py list

# 生成代理
python ~/.codex/agent_factory.py spawn researcher "研究問題" [--async|--fork]

# 寫入跨會話記憶
python ~/.codex/agent_factory.py memory write project key value

# 讀取跨會話記憶
python ~/.codex/agent_factory.py memory read project key
```

### 代理類型 (Claude Code 兼容)

| 類型 | 行為 | 適用場景 |
|------|------|---------|
| **sync** | 阻塞父代理，共享狀態 | 簡單委派 |
| **async** | 獨立執行，自有中斷控制器 | 背景任務 |
| **fork** | 繼承父上下文，90% 快取折扣 | 平行研究 |
| **swarm** | 協調者-工作者的多代理群 | 大規模分解 |

### 內建代理

| 代理 | 模型 | 權限 | 用途 |
|------|------|------|------|
| researcher | inherit | plan | 多平台深度研究 |
| code-reviewer | sonnet | acceptEdits | 代碼審查 |
| architect | opus | plan | 系統架構設計 |
| debugger | sonnet | acceptEdits | 錯誤調試 |
| devops | sonnet | auto | 部署運維 |

---

## 🧠 SAGE 技能自我進化 (v14.0 升級)

> 基於: SAGE (Skill Augmented GRPO for self-Evolution, arXiv:2512.17102) + Hermes Agent (ICLR 2025)

### 技能生命周期

```
生成 → 驗證 → 入庫 → 使用 → 評分 → 進化/淘汰
```

### Hermes 技能管線 (現有 + SAGE 增強)

```powershell
python ~/.codex/hermes_skill_pipeline.py               # 完整掃描
python ~/.codex/hermes_skill_pipeline.py --quick       # 快速模式
python ~/.codex/hermes_skill_pipeline.py --stats       # 統計
python ~/.codex/hermes_skill_pipeline.py --sage        # SAGE 增強評分 (NEW)
```

### SAGE 品質評分

- 技能使用次數 × 成功率 = 技能品質分數
- 低於閾值的技能標記為「待淘汰」
- 高於閾值的技能標記為「核心」

---

## 📦 On-Demand 技能

不預載。匹配到才讀取 SKILL.md。超過 5 個只用 top-3。

---

## 💰 預算感知壓縮 + 🧠 CoALA 記憶牆

(保持 v13.0 完整規格)

---

## 🛡 批評者閘道 + 代理權限模式 (v14.0 升級)

> 整合 Claude Code 6 種權限模式

| 模式 | 行為 | 適用 |
|------|------|------|
| **default** | 標準權限檢查 + 提示 | 一般代理 |
| **acceptEdits** | 自動接受文件編輯 | code-reviewer, debugger |
| **auto** | 背景分類器審查 | devops |
| **dontAsk** | 自動拒絕權限提示 | — |
| **bypassPermissions** | 跳過權限 (高信任) | — |
| **plan** | 唯讀探索模式 | researcher, architect |

---

## 🎯 目標錨定 + 代理錨定 (v14.0 新增)

長任務 (≥10 steps) 每 5 步注入:

```
🎯 原始目標: {goal}
🤖 活躍代理: {active_agents}
📍 進度: {progress} / {total}
🔜 下一步: {next}
⚠️ 偏離風險: {assessment}
```

---

## 🧠 Karpathy 方法論 (保持)

(保持 v13.0 完整規格: 7步循環 · 三層提示 · AutoResearch · Vibe→Agentic · 萎縮矩陣 · 極簡主義)

---

## 🟣 閉環 (任務結束 · v14.0 增強)

- 研究: 搜索+閱讀+驗證?
- 技能: on-demand 匹配? skill_gate PASS?
- 技能自我提取: Hermes pipeline + SAGE 評分? (每日一次)
- Agent Factory: 子代理正確生成/回收?
- IPC: 子代理結果整合?
- 記憶: agent_memory write? outcome-log?
- 漂移: 目標錨定? drift 狀態?
- 批評者: 執行前 critic_gate 通過?
- 元審查: DGM-lite 週期檢查?
- 整合層: brain_hub session-close?

---

## 🔧 系統 (v14.0)

| 工具 | 用途 |
|---|------|
| AnySearch CLI | 搜索引擎 |
| brain_hub.py v3.0 | 跨模組整合 (含 agent_factory) |
| agent_factory.py v1.0 | Claude Code 兼容子代理工廠 |
| governance_pipeline.py | SARC+Critic 五層治理 |
| critic_gate.py | 執行前批評檢查 |
| memory_wall.py | CoALA 記憶牆 |
| lodmem_context.py | LODMEM 上下文管理 |
| hermes_skill_pipeline.py | Hermes + SAGE 技能管線 |
| dgm_meta_agent.py | DGM-lite 元代理 |
| task_router.py | 意圖路由 + 任務派發 |
| skill_matcher.py | P2 關鍵詞匹配 |
| skill_gate.py | 技能門禁 (3層) |
| delegation_engine.py | DGI 分解 |
| drift_guard.py | 漂移檢測 |
| brain_sync.py | 全碟同步 |
| auto_daemon.py | 背景守護 |
| .agent/memory/ | 跨會話代理記憶 |

---

## 🚀 全碟部署 (Brain Sync)

```powershell
python ~/.codex/brain_sync.py --status     # 掃描
python ~/.codex/brain_sync.py --sync-all   # 同步全部
```

---

腦版本: v14.0
生成: 2026-06-01
變更: v14.0 — Claude Code 兼容 .agent/ 架構 · Agent Factory 子代理工廠 · SAGE 技能進化 · 跨代理記憶層 · 代理權限模式
來源: Claude Code (arXiv:2604.14228) · SAGE (arXiv:2512.17102) · Hermes Agent (ICLR 2025) · OpenClaw · Reddit · HN


---

# 🏫 LF Academy (霖楓學苑) — 專案層配置

> 香港小學數學補習平台 · 172 講義 · AI 驅動 · Firebase 部署

## 專案架構

`
G:\lam-fung-academy\
├── 講義/P3/ P4/ P5/ P6/     ← 172 主講義 HTML
├── engines/                   ← 11 AI 引擎
│   ├── lf_ai_brain.py        ← 核心: 6層 Provider 鏈
│   ├── tutor_engine.py       ← 蘇格拉底導師
│   ├── mark_engine.py        ← AI 批改
│   └── ...
├── scripts/                   ← 165 腳本
│   ├── hk_exam_engine.py     ← 考試引擎 (出題/批改/模擬卷)
│   ├── auto_answer_key.py    ← 答案自動生成
│   ├── inject_svg_frac.py    ← SVG/Fraction 注入
│   └── pipeline_html2pdf.py  ← PDF 生成
├── _deploy/                   ← Firebase 部署 (1,783 檔案)
├── data/exams/                ← 20 模擬試卷
├── pdf_output/                ← 826 PDFs
├── .agent/                    ← v14.0 便攜代理記憶
└── lf_server_render.py        ← Render 雲端後端
`

## AI Provider 架構 (全免費)

`
Primary:   frellmapi (localhost:3001, 133+ 模型, 但常不穩)
Fallback:  DeepSeek API (sk-e422da..., 穩定, ~.002/次)
Tier 2:    NVIDIA NIM (免費, 需 nvapi- key)
Tier 3:    OpenRouter (免費, 需 sk-or-v1- key)
Tier 4:    Google Gemini (免費, 1,500/天, HK 可用)
Tier 5:    LM Studio (免費本機, :1234)
Tier 6:    Ollama (免費本機, :11434)
`

## 部署 URL

| 環境 | URL |
|------|-----|
| 主站 | https://lfacademyhk.com |
| 備用 | https://lfady-b1761.web.app |
| API | https://lf-api-f80h.onrender.com |
| AI Tutor | https://lfacademyhk.com/ai-tutor.html |
| Tunnel | https://mpeg-nomination-everyone-optimal.trycloudflare.com |

## 品質標準 (172 講義)

| 指標 | 目標 | 現狀 |
|------|------|------|
| WHY BOX | 100% | ✅ 100% |
| SSPA 標記 | 100% | ✅ 100% |
| 家長摘要 | 100% | ✅ 100% |
| 故事情境 | 100% | ✅ 100% |
| 學習目標 | 100% | 94% |
| 陷阱例題 | 100% | 91% |
| SVG 圖解 | 80%+ | 67% |
| Fractions | 70%+ | 51% |

## 常用命令

`powershell
cd G:\lam-fung-academy

# 品質審查
python _tools/quality_audit.py

# 考試生成
python scripts/hk_exam_engine.py assemble --grade P6 --output-html
python scripts/hk_exam_engine.py generate --grade P6 --topic "小數除法" --count 3

# PDF 生成
python scripts/pipeline_html2pdf.py --grade P6 --workers 3

# SVG/Fraction 注入
python scripts/inject_svg_frac.py --grade P6

# 答案填充
python scripts/auto_answer_key.py

# AI 報告
python scripts/ai_pdf_report.py --sample --preview

# 部署
cd _deploy; firebase deploy --only hosting

# frellmapi
python -c "import requests; print(requests.get('http://localhost:3001/v1/models', headers={'Authorization':'Bearer frellmapi-f672a67d7f6ef4a707a062e0be44e2611b3fc3124269d45a'}).json())"
`

## 開發規則

- 所有 Python 腳本含中文輸出必須: sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
- PowerShell 內聯 Python 用 @"..."@ | python - 避免轉義問題
- 講義命名: LF-{grade}-{上/下/暑假}-L{num}_{topic}.html
- DeepSeek key: sk-e422da39eb9840e387134c823609995e
- frellmapi key: reellmapi-f672a67d7f6ef4a707a062e0be44e2611b3fc3124269d45a
- 部署前確認在 _deploy 目錄執行 irebase deploy

# Self-Reflection Layer v1.0
# Based on 2026-06-02 audit: 38 issues across 6 patterns
# RULE 1: No inline Python >5 lines -> write .py file
# RULE 2: No frellmapi retry >1 -> use DeepSeek direct
# RULE 3: No regex on HTML -> use html.parser
# RULE 4: Spawn sub-agents for parallel work
# RULE 5: Verify before marking complete
# RULE 6: Use scripts/lf_py.py for all Chinese-output Python
