@echo off
echo ========================================================
echo   STUDENT NOMINAL ROLL SEARCH PORTAL - SYSTEM LAUNCHER
echo ========================================================
echo.
echo Launching Backend server at http://127.0.0.1:8000 ...
start "Nominal Roll Backend (FastAPI)" cmd /c "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Launching Frontend interface at http://localhost:5173 ...
start "Nominal Roll Frontend (React)" cmd /c "cd frontend && npm run dev"

echo.
echo Both services launched!
echo Open your browser at: http://localhost:5173
echo.
pause
