@echo off
title Sakshi ALPR India - Backend Server
echo ========================================================
echo   Starting Sakshi ALPR India - FastAPI Backend
echo   Database: Neon PostgreSQL
echo   Port: 8000
echo   Docs: http://localhost:8000/docs
echo ========================================================
cd /d "%~dp0backend"
.\venv\Scripts\python.exe run_backend.py
pause
