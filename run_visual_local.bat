@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [SignalCV] Python virtual environment was not found.
  echo Run setup_local.bat first, then run this file again.
  pause
  exit /b 1
)

set "APP_ENV=development"
set "API_HOST=127.0.0.1"
set "PORT=8000"
set "API_PORT=8000"
set "ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000,http://localhost:8501,http://127.0.0.1:8501"
set "LLM_PROVIDER=local_llm"
set "LOCAL_LLM_BASE_URL=http://127.0.0.1:11434/v1"
set "LOCAL_LLM_MODEL=gemma3:4b"
set "ENABLE_LLM_ENHANCEMENTS=true"
set "ENABLE_WEB_RESEARCH=false"
set "API_ONLY_MODE=true"
set "ENABLE_INTERNAL_ENDPOINTS=true"
set "SITE_AUTH_ENABLED=true"
set "SITE_PASSWORD=local"
set "SITE_AUTH_SECRET=local-visual-session-secret-change-me"

where ollama >nul 2>nul
if %ERRORLEVEL%==0 (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null } catch { Start-Process cmd -ArgumentList '/k ollama serve' | Out-Null }"
) else (
  echo [SignalCV] Ollama was not found in PATH. Local AI will be skipped unless another OpenAI-compatible local server is running.
)

echo.
echo [SignalCV] Starting local visual product...
echo [SignalCV] URL: http://127.0.0.1:8000
echo [SignalCV] Local password: local
echo [SignalCV] Local LLM: %LOCAL_LLM_MODEL% at %LOCAL_LLM_BASE_URL%
echo.

start "" cmd /k "cd /d ""%~dp0"" && call .venv\Scripts\activate.bat && set APP_ENV=%APP_ENV%&& set API_HOST=%API_HOST%&& set PORT=%PORT%&& set API_PORT=%API_PORT%&& set ALLOWED_ORIGINS=%ALLOWED_ORIGINS%&& set LLM_PROVIDER=%LLM_PROVIDER%&& set LOCAL_LLM_BASE_URL=%LOCAL_LLM_BASE_URL%&& set LOCAL_LLM_MODEL=%LOCAL_LLM_MODEL%&& set ENABLE_LLM_ENHANCEMENTS=%ENABLE_LLM_ENHANCEMENTS%&& set ENABLE_WEB_RESEARCH=%ENABLE_WEB_RESEARCH%&& set API_ONLY_MODE=%API_ONLY_MODE%&& set ENABLE_INTERNAL_ENDPOINTS=%ENABLE_INTERNAL_ENDPOINTS%&& set SITE_AUTH_ENABLED=%SITE_AUTH_ENABLED%&& set SITE_PASSWORD=%SITE_PASSWORD%&& set SITE_AUTH_SECRET=%SITE_AUTH_SECRET%&& python launch.py"

timeout /t 4 /nobreak >nul
start "" "http://127.0.0.1:8000"

echo [SignalCV] Browser opened. Keep the backend window open while testing.
pause
