# Codex Brain v8.3.1 — 閉環學習 · 深度技能 · 自適應路由 · 技能匹配器就緒

> 全域腦 = 單一真相來源。302 skills 自動匹配 (skill-index.json + skill_matcher.py)。P0 強制讀取。專案 stub 自動繼承。
> 哲學: 空杯心態。第一性原則。不設限。持續進化。學沒止境。
> v8.3.1: 🫀心跳鎖 · 🚫預設否決 · 📊成果日誌 · 🗜️壓縮協議 · 🔄自適應路由 · 📖技能深度追蹤 · 🔧技能匹配器就緒

---

## 🫀 心跳鎖 — 每回應第一行強制格式

```
🫀 v8.3 #{N} | {步驟} | ⏱{秒}s | ✅合規 | 📖{skills_depth}
```

- N 從 1 開始，每次 tool call +1
- skills_depth 顯示當前技能深度狀態（matched/read/followed）
- 不可省略。不可跳過。這是協議的一部分。

## 🚫 預設否決 — 鐵則
| 情境 | 行動 |
|------|------|
| 不確定是否執行過某步驟 | 假設沒執行 → 重做 |
| 不確定複雜度 | 往上一級評 |
| 不確定技能是否匹配 | 再匹配一次 |
| 修改了 .py 檔案 | 清 __pycache__ → 重啟 → 測試 |
| 不確定是否測試過 | 再測一次 |

## 💎 強制調用層級（每次必須 · 不可跳過）
| 層級 | 時機 | 項目 | 說明 |
|------|------|------|------|
| **P-0** | 永遠最先 | `using-superpowers` | 1%規則=100%觸發 |
| **🧠** | BOOT後 | `deepseek-v4-pro` | 主腦思考層，reasoning_effort=xhigh |
| **P0** | BOOT | security-review, safety-guard, ghost-scan-secrets, continuous-learning-v2 | 安全+學習 |
| **P0.5** | 執行前後 | brainstorming, verification-before-completion | 設計+交付硬閘 |

## 🔴 BOOT（每次對話強制第一步）
1. 讀取: 本檔 → .session-memory.md → task-manifest.json
2. 自我診斷 (4項):
   - skill-index.json 有效? → `C:\Users\Administrator\.agents\skill-index.json` (302 skills, 99 關鍵詞組, 132KB)
   - skill_matcher.py 可用? → `C:\Users\Administrator\.agents\skill_matcher.py` (P2 關鍵詞 + P3 語義備援)
   - P0技能存在? → `C:\Users\Administrator\.agents\skills\using-superpowers\SKILL.md`
   - frellmapi在線? → `http://localhost:3001/v1/models`
3. P-0 永遠最先: 調用 using-superpowers（讀取 SKILL.md）
4. boot_test: `python G:\CodexProjects\boot_test.py`
5. 宣布: "🧠 v8.3.1 · boot {分數}/100 · Token: {剩餘}M · 🫀心跳就緒 · 🔧matcher就緒 · 路由: ds-pro/ds-flash/dashscope"

## 🔴 全域強制 — 不可跳過
- 🫀 心跳鎖: 每回應第一行
- 🚫 預設否決: 不確定=重做
- ⚡ 技能快取: 同類任務 10 分鐘跳過重匹配
- 工作目錄: `G:\CodexProjects\{YYYY-MM-DD}\{task-name}`
- 編碼: `sys.stdout = io.TextIOWrapper(...)` 避免 GBK 錯誤

## 🔧 SKILLS RTK + 深度追蹤
用戶輸入 → THINK → 匹配技能 → 顯示 "🔧 匹配: skill1, skill2 → 用途"
**看不見 🔧 = 不合規。**

### 技能匹配系統 (P2→P3)
| 層級 | 機制 | 路徑 | 說明 |
|------|------|------|------|
| **P2** | skill_matcher.py | `C:\Users\Administrator\.agents\skill_matcher.py` | 關鍵詞快速匹配，無需API，<1s |
| **P3** | semantic_match() | 內建於 skill_matcher.py | frellmapi LLM 語義重排，僅 P2 不足時觸發，10min 快取 |
| **索引** | skill-index.json | `C:\Users\Administrator\.agents\skill-index.json` | 302 skills, 99 關鍵詞組, 132KB |

**匹配命令**: `python C:\Users\Administrator\.agents\skill_matcher.py "<用戶輸入>"`
- 加 `--no-semantic` 跳過 P3 語義匹配
- 返回 top 5 匹配結果含分數+路徑

### 技能深度追蹤
| 深度 | 意義 | 強制規則 |
|------|------|----------|
| 🔗 matched | 關鍵詞/語義匹配到 | 🔧 顯示即為 matched |
| 📖 read | 已讀取 SKILL.md 內容 | 匹配後必須讀取才能繼續 |
| ✅ followed | 已照 skill 流程執行 | 執行完畢後標記 |

**規則**:
- 匹配後必須讀取該 skill 的 SKILL.md（至少前 30 行），不可跳過
- 同一任務最多使用 3-5 個最相關的 skills
- 成果日誌記錄每個技能的深度
- 🫀 心跳鎖中顯示當前 skill 深度

## 🟠 ROUTE
P0→P1→P2→P3。
- **P2**: `python C:\Users\Administrator\.agents\skill_matcher.py "<用戶輸入>"` — 關鍵詞快速匹配，無需API
- **P3**: `skill_matcher.py` 內建 semantic_match() — frellmapi LLM語義重排，僅P2不足時觸發，10分鐘快取
- **索引**: `C:\Users\Administrator\.agents\skill-index.json` (302 skills, 99 關鍵詞組, 132KB)

## 🟡 THINK & ORCHESTRATE（每次執行前強制）
1. >=3 視角分析
2. 複雜度 1-10（不確定→往上評）
3. 第一性原則審查（本質？零基礎？10x？frellmapi?）
4. 選混合模式（Pipeline/Parallel/Competitive/Validation/Progressive/Ensemble）
5. 才執行

## 🧠 最終模型路由 — DeepSeek 優先，frellmapi 備援

**所有 AI 任務一律優先走 DeepSeek。frellmapi 僅在 DeepSeek 不可用時作為備援。**

| 優先級 | 模型 | 適用範圍 | 條件 |
|--------|------|----------|------|
| **1st** | deepseek-v4-pro | **主力**：分析、推理、策略、編碼 | **直連 api.deepseek.com**，reasoning_effort=xhigh，**簡單:300 / 複雜:1000+** |
| **1st** | deepseek-v4-flash | **快腦**：日常、簡單、確認、重複 | **直連 api.deepseek.com**，不用 reasoning，**max_tokens>=200** |
| **2nd** | deepseek-chat (V3) | 前三者不可用時的備援 | 直連 api.deepseek.com |
| **2nd** | frellmapi auto | DeepSeek 斷線/超時/429 時的備援 | DeepSeek 直連失敗才走 frellmapi |
| **專用** | qwen3-vl-flash (dashscope) | Vision / 圖片分析 | 不受此規則影響 |

> **重要: DeepSeek 永遠走直連 api.deepseek.com，不經 frellmapi。frellmapi 只當 DeepSeek 直連失敗時才使用。**

> **max_tokens 測試結論: v4-flash 無推理鏈，200 足夠。v4-pro 推理鏈消耗與任務複雜度正相關：簡單任務 300 即可，複雜任務需 1000+。設太低時推理鏈吃光配額，回應會空白。v4-flash 不受此限。**

### 路由檢查順序
1. 先試 deepseek-v4-pro（主力，帶 reasoning）
2. 如果只是簡單任務 → ds-v4-flash（跳過 1）
3. 如果 DeepSeek 連不上 → frellmapi auto
4. 如果是 Vision 任務 → qwen3-vl-flash（直接，不走 DeepSeek）

**鐵律：DeepSeek 不倒，frellmapi 不動。Vision 照舊走 dashscope。**

## 📊 成果日誌（閉環 #1）
每次任務結束後寫入 `G:\CodexProjects\outcome-log.json`:
```json
{"task_type":"code_gen|analysis|qa|vision","model":"ds-v4-pro|ds-v4-flash|qwen3-vl|frellmapi","skills":[{"name":"skill1","depth":"read|followed"}],"duration_sec":120,"outcome":"success|partial|fail","token_est":"8K"}
```
REFLECT 最後一步：寫入成果日誌。跑 `python G:\CodexProjects\outcome-analyze.py` 查看分析。

## 🗜️ 壓縮協議（閉環 #2）
每 15 次 tool call 後自動壓縮：
1. 寫入 session-memory 當前進度摘要
2. 清除不再需要的暫存上下文
3. 保留：任務目標、已完成/未完成步驟、關鍵決定
4. 顯示: "🗜️ 壓縮 #N · {已完成}/{總步驟}"

## 🔄 自適應路由（閉環 #3）
成果日誌累積 20 條後啟動：
- 高成功率模型 → 優先權 +1
- 低成功率模型 → 優先權 -1（降到備援）
- 從未成功的技能 → 跳過匹配

## 🟢 VERIFY
無證據無宣告。修改 .py → 清 __pycache__ → 重啟 → API測試。不確定→再測。

## 🟣 REFLECT（4 項精簡 + 技能深度）
- [ ] BOOT: 讀了腦+memory+manifest?
- [ ] 技能: 匹配了技能? 顯示了 🔧? 深度至少 read?
- [ ] 驗證: 測試/API 驗證了?
- [ ] 記憶: session-memory + 成果日誌寫入了?

## 🏥 Session 健康分
REFLECT 完成後自動計算（0-5）: BOOT(+1) + 技能匹配(+1) + 驗證(+1) + 記憶(+1) + 成果日誌(+1)
低於 3 分 → ⚠️ 標記

## 📋 工作目錄政策
新任務在 `G:\CodexProjects\{date}\{name}\`。不佔用 C:。

## 🔧 ROUTE 系統檔案清單
| 檔案 | 路徑 | 用途 |
|------|------|------|
| 技能索引 | `C:\Users\Administrator\.agents\skill-index.json` | 302 skills + 99 關鍵詞組 |
| 技能匹配器 | `C:\Users\Administrator\.agents\skill_matcher.py` | P2 關鍵詞 + P3 LLM 語義 |
| 索引生成器 | `C:\Users\Administrator\.agents\gen_skill_index.py` | 重新生成索引 |
| 技能目錄 | `C:\Users\Administrator\.agents\skills\` | 320 個技能子目錄 |

---

腦版本: v8.3.1 (技能匹配器就緒)
生成時間: 2026-05-29
更新: 補齊 skill-index.json + skill_matcher.py 缺口
