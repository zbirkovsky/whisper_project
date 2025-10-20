@echo off
REM CloudCall Transcription Application Launcher

REM Change to script directory
cd /d "%~dp0"

echo.
echo ========================================
echo  CloudCall Transcription Application
echo ========================================
echo.
echo Working directory: %CD%
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first or create venv manually.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Starting CloudCall Transcription...
echo.

REM Run the application
python -m transcription_app.main

REM Check exit code
if errorlevel 1 (
    echo.
    echo ERROR: Application exited with error code %errorlevel%
    echo Check the log file at: %USERPROFILE%\.cloudcall\app.log
    echo.
    pause
)

deactivate
