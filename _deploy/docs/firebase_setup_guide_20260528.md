# 霖楓學苑 · Firebase 一鍵部署包
## 從零到上線 · 完整設定指南

---

## 🚀 三步激活全部會員功能

### Step 1：建立 Firebase 專案（5分鐘）

1. 打開 https://console.firebase.google.com/
2. 點擊「新增專案」
3. 專案名稱：`lam-fung-academy`
4. Google Analytics：啟用（建議）
5. 建立完成後，點擊「</>」圖示新增 Web App
6. App 名稱：`lf-academy-web`
7. 複製 firebaseConfig 物件（下面會用到）

### Step 2：啟用需要的 Firebase 服務

在 Firebase Console 左側選單：

| 服務 | 路徑 | 用途 |
|------|------|------|
| **Authentication** | Build > Authentication | 家長/學生/老師登入 |
| → 登入方式 | Sign-in method | 啟用「Google」+「電子郵件/密碼」 |
| **Firestore Database** | Build > Firestore | 學生數據、練習記錄 |
| → 建立資料庫 | 選擇「測試模式」 | 開發階段方便測試 |

### Step 3：填入金鑰

將以下 `firebaseConfig` 物件中的 `YOUR_*` 替換為你的真實值：

```js
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

然後執行以下 PowerShell 命令（在專案根目錄）：

```powershell
# 替換所有頁面中的 Firebase placeholder
$files = @(
    "docs/login.html",
    "docs/student-platform.html",
    "docs/parent-dashboard.html",
    "docs/profile.html",
    "docs/crm.html",
    "docs/teacher-dashboard.html",
    "docs/admin-members.html",
    "docs/admin-approvals.html"
)
$config = @"
apiKey: "YOUR_REAL_API_KEY",
authDomain: "YOUR_PROJECT.firebaseapp.com",
projectId: "YOUR_PROJECT_ID",
storageBucket: "YOUR_PROJECT.appspot.com",
messagingSenderId: "YOUR_SENDER_ID",
appId: "YOUR_APP_ID"
"@
foreach($f in $files) {
    (Get-Content $f -Raw) -replace 'YOUR_API_KEY.*YOUR_APP_ID"[^"]*"', $config | Set-Content $f -Encoding UTF8
}
```

---

## 📊 Firebase 會自動解鎖的功能

| 頁面 | Firebase前 | Firebase後 |
|------|-----------|-----------|
| login.html | 靜態表單 | Google登入 + Email登入 |
| student-platform.html | 離線練習 | 雲端同步進度 + 跨裝置 |
| parent-dashboard.html | 空白儀表板 | 即時子女學習數據 |
| profile.html | 無 | 個人檔案 + 付款記錄 |
| crm.html | 無 | 學生管理 + 續費追蹤 |
| teacher-dashboard.html | 模擬數據 | 真實班級數據 |
| admin-members.html | 無 | 會員審批 + 權限管理 |
| admin-approvals.html | 無 | 試堂申請管理 |

---

## 💰 成本估算

Firebase Spark Plan（免費額度）足以支持 Year 1：

| 服務 | 免費額度 | 167學生用量 | 
|------|---------|-----------|
| Authentication | 10K/月 | ~200/月 ✅ |
| Firestore 讀取 | 50K/天 | ~5K/天 ✅ |
| Firestore 寫入 | 20K/天 | ~2K/天 ✅ |
| Firestore 儲存 | 1GB | ~200MB ✅ |

**Year 1 成本：HK$0**（全部在免費額度內）

---

*霖楓學苑·Firebase部署包 v1.0 | 2026-05-28*
