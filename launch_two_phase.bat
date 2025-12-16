@echo off
REM Two-Phase Tracking UI Launcher
REM הפעלת ממשק המעקב הדו-שלבי

cd /d "%~dp0"

echo Starting Two-Phase Tracking UI...
echo.

python test_new_ui.py

if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to close...
    pause > nul
)
