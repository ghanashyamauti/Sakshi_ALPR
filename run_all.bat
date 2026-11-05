@echo off
title Sakshi ALPR India - Launcher
echo ========================================================
echo   Launching Sakshi ALPR India (Backend + Frontend)
echo ========================================================
cd /d "%~dp0"
start "Sakshi ALPR Backend" cmd /k "cd backend && .\venv\Scripts\python.exe run_backend.py"
timeout /t 3 /nobreak >nul
start "Sakshi ALPR Frontend" cmd /k "cd frontend && ..\backend\venv\Scripts\python.exe run_frontend.py"
timeout /t 1 /nobreak >nul
start http://localhost:3000
echo Both Backend (Port 8000) and Frontend (Port 3000) are running!
