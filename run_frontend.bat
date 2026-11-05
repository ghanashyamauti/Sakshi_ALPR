@echo off
title Sakshi ALPR India - Frontend Dashboard
echo ========================================================
echo   Starting Sakshi ALPR India - Web Dashboard
echo   Port: 3000
echo   URL: http://localhost:3000
echo ========================================================
cd /d "%~dp0frontend"
..\backend\venv\Scripts\python.exe run_frontend.py
pause
