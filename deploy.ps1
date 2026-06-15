# ═══════════════════════════════════════════════════
# LF Academy · One-Click Deploy Script
# ═══════════════════════════════════════════════════

Write-Host "🚀 LF Academy Deploy v15.0" -ForegroundColor Cyan

# Step 1: Sync all changed files to _deploy
$syncMap = @(
    @{S="ai-tutor.html"; D="ai-tutor.html"},
    @{S="launchpad.html"; D="launchpad.html"},
    @{S="auth.html"; D="auth.html"},
    @{S="docs/social/social_calendar_ultimate.html"; D="docs/social/social_calendar_ultimate.html"},
    @{S="docs/social/social_calendar_july_2026.html"; D="docs/social/social_calendar_july_2026.html"},
    @{S="docs/social/social_calendar_august_2026.html"; D="docs/social/social_calendar_august_2026.html"},
    @{S="講義/P3/index.html"; D="講義/P3/index.html"},
    @{S="講義/P4/index.html"; D="講義/P4/index.html"},
    @{S="講義/P5/index.html"; D="講義/P5/index.html"},
    @{S="講義/P6/index.html"; D="講義/P6/index.html"},
    @{S="講義/EN/index.html"; D="講義/EN/index.html"}
)

$base = "G:\lam-fung-academy"
$deploy = "$base\_deploy"

foreach ($m in $syncMap) {
    $src = "$base\$($m.S)"
    $dst = "$deploy\$($m.D)"
    $dstDir = Split-Path $dst -Parent
    if (!(Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
    if (Test-Path $src) {
        Copy-Item $src -Destination $dst -Force
        Write-Host "  ✅ $($m.S)" -ForegroundColor Green
    }
}

# Step 2: Update tunnel-url.txt
$aiContent = Get-Content "$base\ai-tutor.html" -Raw
if ($aiContent -match 'const TUNNEL_FALLBACKS = \[[^\]]*"([^"]+trycloudflare[^"]+)"') {
    $tunnelUrl = $matches[1]
    $tunnelUrl | Set-Content "$deploy\tunnel-url.txt"
    Write-Host "  ✅ tunnel-url.txt updated: $tunnelUrl" -ForegroundColor Green
}

# Step 3: Deploy
Write-Host "`n📤 Deploying to Firebase..." -ForegroundColor Yellow
Set-Location $deploy
$env:NODE_OPTIONS = "--max-old-space-size=4096"
npx firebase deploy --only hosting

Write-Host "`n✅ Deploy complete!" -ForegroundColor Green
