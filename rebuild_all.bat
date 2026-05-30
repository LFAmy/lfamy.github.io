@echo off
cd /d G:\lam-fung-academy
echo ========================================
echo 霖楓學苑 LF Academy - 重建系統資產
echo ========================================
python _tools\master_control.py rebuild
echo.
echo 重建完成。按任意鍵關閉...
pause >nul
