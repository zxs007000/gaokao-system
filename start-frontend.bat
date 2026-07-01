@echo off
chcp 65001 >nul
title Gaokao Frontend

echo ============================================
echo   Gaokao System - Frontend (Next.js)
echo   Port: 3000   http://localhost:3000
echo ============================================
echo.

cd /d "%~dp0frontend"

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000.*LISTENING" 2^>nul') do (
    echo [Kill] Old process PID=%%a
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 1 /nobreak >nul
)

if not exist "node_modules" (
    echo [Install] Installing dependencies...
    call npm install
    echo.
)

echo [Start] Starting Next.js dev server...
echo   Open http://localhost:3000 after "ready"
echo.

start "" http://localhost:3000
call npm run dev

echo.
echo [Done] Frontend stopped.
pause
