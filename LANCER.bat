@echo off
title Smart Logistics - Startup
color 0A

echo.
echo  ============================================
echo   SMART LOGISTICS - Multi-Agent System
echo   LangChain + LlamaIndex + Groq
echo  ============================================
echo.

echo  [1/2] Starting backend AI (port 8000)...
start "Backend API" cmd /k "cd /d %~dp0Smart-Logistics-Route-Optimizer-main\python_backend && set PYTHONPATH=. && %~dp0.venv\Scripts\python.exe main.py"

echo  Waiting for backend startup (8 seconds)...
ping -n 9 127.0.0.1 >nul

echo  [2/2] Starting React frontend (port 3000)...
start "Frontend React" cmd /k "cd /d %~dp0Smart-Logistics-Route-Optimizer-main\frontend && npm start"

echo  Waiting for interface startup (15 seconds)...
ping -n 16 127.0.0.1 >nul

echo  [OK] Opening in Firefox...
start firefox http://localhost:3000

echo.
echo  ============================================
echo   Application available at:
echo   http://localhost:3000
echo  ============================================
echo.
echo  (Keep both black windows open)
echo  (To stop: close both black windows)
echo.
pause
