@echo off
chcp 65001 >nul
cd /d G:\lam-fung-academy
echo.
echo ╔══════════════════════════════════════════╗
echo ║  霖楓學苑 LF Academy — 一鍵同步部署  ║
echo ╚══════════════════════════════════════════╝
echo.
echo [1/4] 重建便攜版網頁...
python _tools\build_portable.py >nul 2>&1
if errorlevel 1 (
    echo   ❌ 重建失敗！
    pause
    exit /b 1
)
echo   ✅ 便攜版已重建

echo [2/4] 同步到 docs 文件夾...
python -c "import os,shutil;src=r'G:\lam-fung-academy\_portable\web';dst=r'G:\lam-fung-academy\docs';shutil.rmtree(dst,ignore_errors=True);shutil.copytree(src,dst);print('OK')" >nul 2>&1

REM Copy latest operations files
python -c "import os,shutil,glob;ops_src=r'G:\lam-fung-academy\_operations';ops_dst=r'G:\lam-fung-academy\docs\_operations';os.makedirs(ops_dst,exist_ok=True);[shutil.copy2(f,os.path.join(ops_dst,os.path.basename(f))) for f in glob.glob(os.path.join(ops_src,'*.html'))];[shutil.copy2(f,os.path.join(ops_dst,os.path.basename(f))) for f in glob.glob(os.path.join(ops_src,'answer_keys','*.html'))];print('OK')" >nul 2>&1
echo   ✅ 已同步

echo [3/4] 提交到 Git...
git add docs/ -f >nul 2>&1
git commit -m "Auto-sync: website update %date% %time%" >nul 2>&1
echo   ✅ 已提交

echo [4/4] 推送至 lfamy.github.io...
for /f "tokens=*" %%i in ('gh auth token') do set GH_TOKEN=%%i
git push https://lui62233:%GH_TOKEN%@github.com/LFAmy/lfamy.github.io.git main --force >nul 2>&1
if errorlevel 1 (
    echo   ❌ 推送失敗！請檢查網絡連接
    pause
    exit /b 1
)
echo   ✅ 已推送

echo.
echo ╔══════════════════════════════════════════╗
echo ║  ✅ 部署完成！                          ║
echo ║                                          ║
echo ║  🌐 https://lfamy.github.io/             ║
echo ║                                          ║
echo ║  ⏱️  1-2 分鐘後全球 CDN 生效            ║
echo ╚══════════════════════════════════════════╝
echo.
timeout /t 3 >nul
