@echo off
REM CloudCall Transcription Application Setup Script

REM Change to script directory
cd /d "%~dp0"

echo.
echo ========================================
echo  CloudCall Transcription Setup
echo ========================================
echo.
echo Working directory: %CD%
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or 3.11 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/7] Checking Python version...
python --version

echo.
echo [2/7] Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg is not installed or not in PATH
    echo FFmpeg is required for audio processing.
    echo.
    echo Install FFmpeg using one of these methods:
    echo   1. winget install ffmpeg
    echo   2. choco install ffmpeg
    echo   3. Download from https://ffmpeg.org/download.html
    echo.
    echo After installing FFmpeg, run this setup again.
    pause
    exit /b 1
)
echo FFmpeg found!

echo.
echo [3/7] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created successfully
)

echo.
echo [4/7] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [5/7] Installing PyTorch with CUDA 12.1...
echo This may take a few minutes...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo [6/7] Installing application dependencies...
pip install -r requirements.txt

echo.
echo [7/7] Creating configuration file...
if not exist "config\.env" (
    if exist "config\.env.example" (
        copy "config\.env.example" "config\.env" >nul
        echo Created config\.env from template
        echo IMPORTANT: Edit config\.env and add your HuggingFace token for speaker diarization
    ) else (
        echo WARNING: config\.env.example not found, skipping .env creation
    )
) else (
    echo config\.env already exists, skipping...
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Get HuggingFace token from: https://huggingface.co/settings/tokens
echo 2. Edit config\.env and add your token
echo 3. Run: run.bat
echo.
echo For more details, see: README.md or QUICKSTART.md
echo.
pause
