@echo off
chcp 65001 >nul
title Stop Gaokao System

echo.
echo   ========================================
echo     Stopping Gaokao System ...
echo   ========================================
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" 2^>nul') do (
    echo [Stop] Frontend PID=%%a
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8005" 2^>nul') do (
    echo [Stop] Backend PID=%%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo   All services stopped.
echo.
timeout /t 2 >nul
