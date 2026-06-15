# frellmapi startup script
$env:PORT = "3002"
$env:NODE_PATH = "$env:APPDATA\npm\node_modules"

Set-Location "G:\lam-fung-academy\_freellmapi"

# First, ensure shared types package exists
$sharedDir = "node_modules\@freellmapi\shared"
if (-not (Test-Path "$sharedDir\types.js")) {
    New-Item -ItemType Directory -Force -Path $sharedDir | Out-Null
    @"
{
  "name": "@freellmapi/shared",
  "version": "1.0.0",
  "type": "module",
  "main": "types.js"
}
"@ | Set-Content "$sharedDir\package.json"
    @"
export const Platform = {GOOGLE:"google",OPENAI:"openai",ANTHROPIC:"anthropic",COHERE:"cohere",MISTRAL:"mistral",META:"meta",DEEPSEEK:"deepseek",OPENROUTER:"openrouter",NVIDIA:"nvidia",CLOUDFLARE:"cloudflare",POLLINATIONS:"pollinations",LLM7:"llm7",KILO:"kilo"};
export const KeyStatus = {HEALTHY:"healthy",RATE_LIMITED:"rate_limited",QUOTA_EXCEEDED:"quota_exceeded",EXPIRED:"expired",INVALID:"invalid",UNKNOWN:"unknown"};
"@ | Set-Content "$sharedDir\types.js"
}

# Ensure DB is in the right place
$dataDir = "data"
if (-not (Test-Path "$dataDir\freeapi.db")) {
    New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
    Copy-Item "G:\lam-fung-academy\_freellmapi_data\freeapi.db" "$dataDir\freeapi.db" -Force
}

# Also ensure dotenv is available
if (-not (Test-Path "node_modules\dotenv")) {
    npm install dotenv --no-save --no-audit --no-fund 2>&1 | Out-Null
}

# Start server
$tsxLoader = "file:///C:/Users/Administrator/AppData/Roaming/npm/node_modules/tsx/dist/loader.mjs"
$proc = Start-Process -FilePath "D:\nodejs\node.exe" -ArgumentList "--import $tsxLoader server/src/index.ts" -NoNewWindow -PassThru -RedirectStandardOutput "$env:TEMP\freellmapi_out.txt" -RedirectStandardError "$env:TEMP\freellmapi_err.txt"
Write-Host "frellmapi PID: $($proc.Id)"
Start-Sleep -Seconds 5
try { $r = Invoke-WebRequest "http://localhost:3002/v1/models" -TimeoutSec 3 -UseBasicParsing; Write-Host "✅ frellmapi running!" } catch { Write-Host "⚠️ Not responding yet, check logs" }
