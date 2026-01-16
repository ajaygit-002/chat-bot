@echo off
REM NovaChat AI - Start Both Frontend and Backend
REM This batch file starts both services simultaneously

title NovaChat AI - Starting Services
color 0B
cls

echo ==========================================
echo   NovaChat AI - Starting Services
echo ==========================================
echo.

REM Get the directory where this script is located
set ROOT_DIR=%~dp0

REM Start Backend in new window
echo Starting Backend (FastAPI)...
echo   Server: http://127.0.0.1:8000
start "NovaChat Backend" cmd /k "cd /d "%ROOT_DIR%backend" && venv\Scripts\activate.bat && uvicorn main:app --reload"

REM Wait a moment for backend to start
timeout /t 2 /nobreak

REM Start Frontend in new window
echo Starting Frontend (Vite + React)...
echo   Server: http://localhost:5173
start "NovaChat Frontend" cmd /k "cd /d "%ROOT_DIR%frontend" && npm run dev"

REM Wait a moment
timeout /t 2 /nobreak

echo.
echo ==========================================
echo   Both services are starting!
echo ==========================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://127.0.0.1:8000
echo.
echo Make sure your OpenAI API key is set in .env
echo.

pause
