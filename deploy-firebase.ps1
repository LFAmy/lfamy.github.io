# ═══════════════════════════════════════════════════
# 霖楓學苑 · 一鍵部署腳本
# 首次使用：先執行 firebase login (只需一次)
# 之後：直接執行此腳本即可
# ═══════════════════════════════════════════════════
$ErrorActionPreference = "Continue"
Write-Host "`n🔥 霖楓學苑 · Firebase 一鍵部署" -ForegroundColor Cyan

# 檢查登入
$loginOk = $false
try { firebase projects:list 2>&1 | Out-Null; $loginOk = $true } catch {}

if (-not $loginOk) {
    Write-Host "`n首次使用需要登入。正在打開瀏覽器..." -ForegroundColor Yellow
    firebase login 2>&1
    Write-Host "登入完成後請重新執行此腳本" -ForegroundColor Green
    exit 0
}

Write-Host "Deploying Firestore rules..." -ForegroundColor Cyan
firebase deploy --only firestore 2>&1

Write-Host "Deploying Firebase Hosting..." -ForegroundColor Cyan
firebase deploy --only hosting 2>&1

Write-Host "`nDONE: https://lfady-b1761.web.app" -ForegroundColor Green