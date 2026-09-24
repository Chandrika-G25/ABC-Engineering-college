@echo off
title Student Management System Server
cd /d "%~dp0"

echo ================================================================
echo          Student Management System - Server Launcher
echo ================================================================
echo.
echo [1] Local Browser Link (This PC):
echo     http://127.0.0.1:8000/
echo     or
echo     http://localhost:8000/
echo.
echo [2] Network Link (Open from any device/mobile on same Wi-Fi):
echo     http://192.168.0.107:8000/
echo.
echo [3] Admin Dashboard:
echo     http://127.0.0.1:8000/admin/
echo.
echo ================================================================
echo Opening default web browser in 2 seconds...
echo (You can safely close Antigravity; the app will keep running!)
echo To stop the server anytime, press Ctrl+C in this window.
echo ================================================================
echo.

timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000/

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
) else if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
) else (
    py -3.11 manage.py runserver 0.0.0.0:8000
)
pause
