@echo off
cd /d G:\lam-fung-academy
echo ========================================
echo 霖楓學苑 LF Academy - 系統健康檢查
echo ========================================
python _tools\master_control.py check
echo.
echo 檢查完成。按任意鍵關閉...
pause >nul
