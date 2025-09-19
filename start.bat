@echo off
REM Skynet Core startup script for Windows
echo 🚀 Starting Skynet Core...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Ollama doesn't seem to be running
    echo Starting Ollama...
    start "" ollama serve
    timeout /t 5 /nobreak >nul
)

REM Install dependencies if needed
if not exist "venv\" (
    echo 📦 Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Start Skynet Core
echo ✅ Launching Skynet Core...
python main.py

pause
