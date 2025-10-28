@echo off
echo ============================================
echo Elia Parking Bot V4 - Installation Script
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python found
python --version

echo.
echo [2/5] Installing Python packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python packages
    pause
    exit /b 1
)

echo.
echo [3/5] Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo [ERROR] Failed to install Playwright browsers
    pause
    exit /b 1
)

echo.
echo [4/5] Creating directories...
if not exist "logs" mkdir logs
if not exist "screenshots" mkdir screenshots
if not exist "session_data" mkdir session_data
if not exist "browser_data" mkdir browser_data

echo.
echo [5/5] Creating .env file from example...
if not exist ".env" (
    copy ".env.example" ".env"
    echo Created .env file - PLEASE EDIT IT WITH YOUR CREDENTIALS
) else (
    echo .env already exists - skipping
)

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your credentials
echo 2. Run: python main.py --setup
echo 3. Run: python main.py --test-auth
echo.
pause
