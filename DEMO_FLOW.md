# LF Academy v4.0 · Demo 體驗流程

## 🎯 五角色演示路線

### 🎒 學生體驗（P5 小明）
1. 打開 https://lfacademyhk.com → 看到會員列顯示「🤖 免費試用AI導師」
2. 點擊進入 ai-tutor.html → 看到積分顯示 + 年級選擇
3. 選「小五 P5」→「簡易方程」→ 題目出現：「2x + 5 = 13, 求 x」
4. 輸入答案「x=5」→ AI 批改：❌ 唔啱 → 自動觸發蘇格拉底引導
5. AI 導師回應：「讓我們再想想。2x 代表什麼？如果 x=5，2x 是多少？」
6. 點「💡 提示」→ 自適應分支診斷 → 偵測到 calculation_error → 針對性提示
7. 輸入「x=4」→ 🎉 正確！+10分！
8. 累積積分達 50 → 🥉 銅章彈出
9. 點「📋 結束學習」→ AI 生成摘要 → 顯示三選一：再練/家長報告/升級會員

### 👨‍👩‍👧 家長體驗（小明媽媽）
1. 打開 parent-dashboard.html → 輸入「小明」
2. Dashboard 顯示：今日完成 12 題 · 正確率 75% · 積分 120
3. 折線圖顯示本週正確率趨勢（真實 API 數據）
4. 弱項診斷：「簡易方程(移項錯誤)」「分數乘法(約分時機)」
5. AI 分析建議：「建議重點加強：簡易方程、分數乘法」
6. 看到孩子連續學習 5 日 🔥 → 決定續報

### 🏢 營運體驗（Admin）
1. Firebase Console → Firestore Rules → 驗證 events 寫入需 _server==true
2. Stripe Dashboard → 看到付款記錄
3. pricing.html → 點「立即報名」→ Stripe Checkout → 付款成功頁
4. 會員狀態即時更新 → membership-bar 顯示「Pro · 30日」

### 🔧 系統體驗（Developer）
1. `python system_health.py` → 8/8 A+
2. `git log` → fe5f9f5 LF Academy v4.0
3. CI 自動部署 → Firebase Hosting + Render API

### 🧠 AI 智能驗證
- 蘇格拉底對話：多輪引導，不直接給答案
- 錯誤診斷：sign_error / calculation_error / rounding_error / factor_error
- 自適應提示：根據錯誤類型分支
- 知識覆蓋：56 個課題，P3-P6 全覆蓋
- 推理驗證：逐步分析學生推理過程