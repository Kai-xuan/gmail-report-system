@echo off
chcp 65001 > nul
title Gmail 報告系統

echo.
echo  ╔══════════════════════════════════╗
echo  ║     Gmail 智慧報告系統 啟動中    ║
echo  ╚══════════════════════════════════╝
echo.

cd /d "%~dp0"

:: 檢查 Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先安裝 Python 3.8 以上版本
    pause
    exit /b 1
)

:: 檢查 credentials.json
if not exist "credentials.json" (
    echo [錯誤] 找不到 credentials.json，請先放入 Google 憑證檔案
    pause
    exit /b 1
)

:: 啟動 Flask 並自動開啟瀏覽器
echo  ✓ 系統啟動成功
echo  ✓ 請在瀏覽器使用：http://localhost:5000
echo.
echo  （關閉此視窗即停止系統）
echo.

:: 延遲 1.5 秒後開啟瀏覽器
start "" cmd /c "timeout /t 2 /nobreak > nul && start http://localhost:5000"

python app.py

pause
