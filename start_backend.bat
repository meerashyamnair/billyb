@echo off
echo ========================================================
echo Starting Student Nominal Roll Search Portal - Backend
echo ========================================================
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
