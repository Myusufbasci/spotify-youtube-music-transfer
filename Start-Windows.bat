@echo off
chcp 65001 >nul
title Spotify ^<^> YouTube Music Transfer
cd /d "%~dp0"

echo ========================================================
echo   Spotify ^<-^> YouTube Music Transfer
echo ========================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python was not found on your system.
    echo [*] Installing Python 3.12 automatically via Windows Package Manager ^(winget^)...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [!] Automatic Python installation failed. Opening python.org/downloads...
        start https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
)

:: 2. Install/verify dependencies quietly
echo [*] Checking required packages...
python -c "import flask, ytmusicapi, rapidfuzz, bs4, playwright" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing dependencies ^(first-time setup^)...
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt
)

:: 3. Launch Web UI and open browser automatically
echo [*] Starting Web Interface at http://127.0.0.1:5050 ...
python app.py --web --open --port 5050
pause
