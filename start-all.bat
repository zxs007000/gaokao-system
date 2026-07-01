@echo off
chcp 65001 >nul
title Gaokao System

echo.
echo   ========================================
echo     Gaokao System - One Click Start
echo     Backend: 8005  Frontend: 3000
echo   ========================================
echo.

cd /d "%~dp0"

REM === 1. Kill old backend on port 8005 ===
echo [1/2] Starting backend (port 8005) ...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8005.*LISTENING" 2^>nul') do taskkill /F /PID %%a >nul 2>&1
start "Gaokao-Backend-8005" cmd /k "cd /d %~dp0 && python -m uvicorn api.main:app --host 0.0.0.0 --port 8005 --reload"

REM === 2. Kill old frontend on port 3000 ===
echo [2/2] Starting frontend (port 3000) ...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000.*LISTENING" 2^>nul') do taskkill /F /PID %%a >nul 2>&1

if not exist "%~dp0frontend\node_modules" (
    echo [Install] Installing frontend dependencies ...
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
)

start "Gaokao-Frontend-3000" cmd /k "cd /d %~dp0frontend && npm run dev"

REM === 3. Wait and check ===
echo.
echo   Waiting ~8 seconds ...
echo   Backend:  http://localhost:8005
echo   Frontend: http://localhost:3000
echo.
timeout /t 8 /nobreak >nul

curl -s -o NUL http://localhost:8005/api/health 2>nul
if %errorlevel%==0 (echo   [OK] Backend ready) else (echo   [..] Backend starting)

curl -s -o NUL http://localhost:3000 2>nul
if %errorlevel%==0 (echo   [OK] Frontend ready) else (echo   [..] Frontend compiling)

echo.
echo   Open: http://localhost:3000
echo   Close: shut both console windows
echo.
start "" http://localhost:3000
pause
