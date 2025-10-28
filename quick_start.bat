@echo off
REM Quick start script for Elia Parking Bot V4

:menu
cls
echo ============================================
echo    ELIA PARKING BOT V4 - Quick Menu
echo ============================================
echo.
echo 1. Initial Setup (First time use)
echo 2. Test Authentication
echo 3. Test Spot Detection (Executive)
echo 4. Test Spot Detection (Regular)
echo 5. Reserve Executive Spot NOW
echo 6. Reserve Regular Spot NOW
echo 7. Setup Windows Scheduled Tasks
echo 8. Run Daemon Mode (24/7)
echo 9. View Today's Logs
echo 0. Exit
echo.
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto test_auth
if "%choice%"=="3" goto test_exec
if "%choice%"=="4" goto test_reg
if "%choice%"=="5" goto reserve_exec
if "%choice%"=="6" goto reserve_reg
if "%choice%"=="7" goto windows_tasks
if "%choice%"=="8" goto daemon
if "%choice%"=="9" goto logs
if "%choice%"=="0" goto end
goto menu

:setup
cls
echo Running initial setup...
python main.py --setup
pause
goto menu

:test_auth
cls
echo Testing authentication...
python main.py --test-auth
pause
goto menu

:test_exec
cls
echo Testing executive spot detection...
python main.py --test-spots executive
pause
goto menu

:test_reg
cls
echo Testing regular spot detection...
python main.py --test-spots regular
pause
goto menu

:reserve_exec
cls
echo Reserving executive spot...
python main.py --reserve executive
pause
goto menu

:reserve_reg
cls
echo Reserving regular spot...
python main.py --reserve regular
pause
goto menu

:windows_tasks
cls
echo Setting up Windows scheduled tasks...
echo Note: Requires administrator privileges
python main.py --setup-tasks
pause
goto menu

:daemon
cls
echo Starting daemon mode...
echo Press Ctrl+C to stop
python main.py --daemon
pause
goto menu

:logs
cls
echo Viewing today's logs...
echo.
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
if exist "logs\elia_bot_%mydate%.log" (
    type "logs\elia_bot_%mydate%.log"
) else (
    echo No logs found for today
)
echo.
pause
goto menu

:end
echo Goodbye!
exit /b 0
