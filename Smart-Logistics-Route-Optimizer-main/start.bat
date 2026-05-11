@echo off
echo ========================================================
echo   SMART LOGISTICS ROUTE OPTIMIZER + AI MULTI-AGENT
echo ========================================================

echo.
echo [1/2] Starting Python LangGraph AI Backend (Port 8000)...
start cmd /k "cd python_backend && pip install -r requirements.txt && python main.py"

echo.
echo [2/2] Starting React Frontend (Port 3000)...
start cmd /k "cd frontend && npm install && npm start"

echo.
echo All components are starting up! 
echo Keep the 2 terminal windows open while using the application.
echo You can access the UI at: http://localhost:3000
echo.
pause
