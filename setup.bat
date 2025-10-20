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

echo [1/5] Checking Python version...
python --version

echo.
echo [2/5] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created successfully
)

echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [4/5] Installing PyTorch with CUDA 11.8...
echo This may take a few minutes...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo.
echo [5/5] Installing application dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Get HuggingFace token from: https://huggingface.co/settings/tokens
echo 2. Copy config\.env.example to config\.env
echo 3. Add your token to config\.env
echo 4. Run: run.bat
echo.
echo For more details, see: README.md or QUICKSTART.md
echo.
pause
