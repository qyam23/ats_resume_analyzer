@echo off
cd /d %~dp0
if not exist .venv (
  py -3.10 -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
echo.
echo Setup complete.
echo Next:
echo   copy .env.example .env
echo   run_local.bat
