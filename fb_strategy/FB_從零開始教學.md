# LF Academy — Facebook 從零開始完整教學

> 你不需要任何 FB 經驗，跟著這份教學一步一步做就可以。
> 全程約 30 分鐘。

---

## 🟢 第一階段：建立 Facebook 帳號 (如果你已有帳號，跳到第二階段)

### 1. 打開 Facebook

在瀏覽器打開: **https://www.facebook.com**

### 2. 註冊

看到這個畫面，填寫：

```
姓名：霖楓學苑 (或你的真實姓名)
手機或電郵：你的 Email
密碼：設定一個密碼
生日：你的生日
性別：你的性別

→ 點擊綠色「註冊」按鈕
```

### 3. 驗證

Facebook 會發送一個驗證碼到你的 Email 或手機。
輸入驗證碼，完成註冊。

> ✅ 完成後你就有個人 FB 帳號了

---

## 🔵 第二階段：建立 LF Academy 專頁 (最重要的步驟)

### 1. 建立專頁

登入後，在 FB 首頁右上角點你的 **大頭貼** → 選 **「建立粉絲專頁」**

或者直接打開: **https://www.facebook.com/pages/create**

### 2. 填寫專頁資料

```
專頁名稱：霖楓學苑 LF Academy — 香港小學數學呈分試專家
類別：教育網站 / 補習班
簡介：霖楓學苑專注香港小學數學，172+ 講義、AI 診斷系統，
      幫助 P3-P6 學生征服呈分試。
```

→ 點擊「建立專頁」

### 3. 設定專頁圖片

- **大頭貼 (Profile Picture)**：上傳 LF Academy Logo
  - 建議 720×720 像素
  - 如果有 Logo 檔案就上傳，沒有就用 Canva 做一個（見下方）

- **封面照片 (Cover Photo)**：上傳一張吸引的封面
  - 建議 820×312 像素
  - 可以是品牌色背景 + 標語文字

### 4. 完成專頁資訊

在專頁左側點「設定」→「專頁設定」，填寫：

```
用戶名稱：@lfacademyhk  (這很重要！這是你的專頁網址)
網站：https://lfacademyhk.com
聯絡電話：你的電話
電郵：你的 Email
地址：你的地址（可選填）
營業時間：（可選填）
```

### 5. 設定行動按鈕 (CTA)

在專頁封面圖下方，點「新增按鈕」→ 選擇：
```
「與你聯絡」→「傳送訊息」或「立即預約」
```

> ✅ 完成！你現在有了一個專業的 FB 專頁。
> 專頁網址會是: https://www.facebook.com/lfacademyhk

---

## 🟡 第三階段：開通 API 權限 (讓自動化系統可以發文)

### 1. 打開 Meta 開發者平台

打開: **https://developers.facebook.com**

點右上角「我的應用程式」→「建立應用程式」

### 2. 建立應用程式

```
類型：選擇「其他」
名稱：LF Academy Auto
用途：選擇「自己使用」
→ 點擊「建立應用程式」
```

### 3. 獲取 Access Token

在左側選單點「工具」→「Graph API Explorer」

```
(1) 在「Meta App」下拉選單 → 選擇「LF Academy Auto」
(2) 在「權限」右側點「Add a Permission」→ 
    在搜尋框輸入以下權限，逐一加入：
    
    ✦ pages_manage_posts     (發布帖子)
    ✦ pages_read_engagement  (讀取互動)
    ✦ pages_show_list        (列出專頁)
    
(3) 點擊「Generate Access Token」
    → FB 會跳出授權視窗 → 點「繼續」
    
(4) 在右側的「User or Page」下拉選單中
    → 選擇你的專頁「霖楓學苑 LF Academy」
    
(5) 現在你會看到一個新的 Token
    → 這就是你的 Page Access Token
    → 複製它！（長長的一串英數字）
```

### 4. 記下你的 Page ID

在 Graph API Explorer 頂部的 URL 欄位中，
把 `me` 改成你的專頁名稱或 ID。

或者直接在 FB 專頁上，查看網址列中的數字 ID。

> ✅ 完成！你現在有兩個關鍵資料：
> - **Page ID**：一串數字
> - **Access Token**：一長串英數字

---

## 🟣 第四階段：執行自動化設定

### 1. 執行設定精靈

打開 PowerShell，輸入：

```powershell
cd G:\lam-fung-academy
python fb_strategy\fb_setup.py
```

### 2. 選擇 [1] 直接輸入

精靈會問你選擇方式，輸入 `1`

然後輸入：
```
FB 專頁 ID：你的 Page ID
Page Access Token：你的 Access Token
專頁名稱：霖楓學苑 LF Academy
```

### 3. 驗證

系統會自動驗證，顯示：
```
✅ 設定成功！
```

### 4. 測試發布

```powershell
python fb_strategy\fb_api_client.py post --message "🎉 霖楓學苑正式登陸 Facebook！我哋專注香港小學數學呈分試，即刻 Follow 我哋獲取每日免費練習！"
```

如果成功，你的專頁上就會出現第一篇帖子！

### 5. 啟動全自動化

```powershell
# 生成一週內容（18 篇帖）
python fb_strategy\fb_content_pipeline.py generate

# 自動發布到專頁
python fb_strategy\fb_content_pipeline.py publish
```

---

## 🎨 加分：用 Canva 做專頁圖片 (免費)

如果你沒有 Logo 和封面圖：

1. 打開: **https://www.canva.com** (免費註冊)
2. 搜尋「Facebook Profile Picture」→ 選模板
3. 文字打上「霖楓學苑」「LF Academy」
4. 下載 → 上傳到 FB 專頁

封面圖同理，搜尋「Facebook Cover」即可。

---

## 📋 需要幫忙？

過程中遇到任何問題，告訴我：
- 卡在哪一步
- 看到什麼錯誤訊息
- 截圖也可以

我會幫你解決。
