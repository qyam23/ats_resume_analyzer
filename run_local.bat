@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
start "ATS Backend" cmd /k uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
timeout /t 3 >nul
start "ATS Frontend" cmd /k streamlit run frontend/app.py --server.port 8501

