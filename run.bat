@echo off
REM Clothing Rating and Outfit Designer - Windows Launcher

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in system PATH
    echo Please install Python 3.7+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Run the application
echo Starting Clothing Rating and Outfit Designer...
python clothing_rating_app.py

if errorlevel 1 (
    echo An error occurred while running the application
    pause
)
