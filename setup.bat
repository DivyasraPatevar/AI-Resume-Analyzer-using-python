@echo off
REM AI Resume Analyzer - Windows Setup Script

echo.
echo ========================================
echo AI Resume Analyzer - Setup Script
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10+
    exit /b 1
)

REM Check if Docker is available
where docker >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ Docker found
    set /p DOCKER_CHOICE="Run with Docker? (y/n): "
    if /i "%DOCKER_CHOICE%"=="y" (
        echo Starting services with Docker Compose...
        docker-compose up --build
        exit /b 0
    )
)

REM Local setup
echo.
echo 📦 Setting up local environment...
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Download NLTK data
echo.
echo Downloading NLTK resources...
python -m nltk.downloader punkt stopwords wordnet averaged_perceptron_tagger

REM Download spaCy model
echo Downloading spaCy model...
python -m spacy download en_core_web_sm

echo.
echo ✅ Setup complete!
echo.
echo To start the application:
echo.
echo 1. Terminal 1 (FastAPI Backend):
echo    venv\Scripts\activate.bat
echo    python -m uvicorn api.main:app --reload --port 8000
echo.
echo 2. Terminal 2 (Streamlit Frontend):
echo    venv\Scripts\activate.bat
echo    streamlit run AA.py
echo.
echo Then visit:
echo    🌐 Frontend: http://localhost:8501
echo    📚 API Docs: http://localhost:8000/docs
echo.
pause
