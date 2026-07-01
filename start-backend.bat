@echo off
chcp 65001 >nul
title Gaokao Backend

echo ============================================
echo   Gaokao System - Backend (API)
echo   Port: 8005
echo ============================================
echo.

cd /d "%~dp0"

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8005.*LISTENING" 2^>nul') do (
    echo [Kill] Old process PID=%%a
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 1 /nobreak >nul
)

echo [Start] Starting Python backend...
echo.
python -m uvicorn api.main:app --host 0.0.0.0 --port 8005 --reload

echo.
echo [Done] Backend stopped.
pause
