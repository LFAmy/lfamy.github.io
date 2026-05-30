@echo off
cd /d G:\lam-fung-academy
echo ========================================
echo 霖楓學苑 LF Academy - 批次建立 PDF
echo 警告：此操作需時 20-30 分鐘
echo ========================================
python _tools\master_control.py rebuild
echo.
echo PDF 建立完成。按任意鍵關閉...
pause >nul
