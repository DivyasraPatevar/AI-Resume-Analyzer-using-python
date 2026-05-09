#!/bin/bash

# AI Resume Analyzer - Setup & Run Script

echo "🚀 AI Resume Analyzer - Setup Script"
echo "====================================="

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    VENV_BIN="venv\\Scripts"
    ACTIVATE_CMD="venv\\Scripts\\activate"
else
    VENV_BIN="venv/bin"
    ACTIVATE_CMD="source venv/bin/activate"
fi

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    read -p "Run with Docker? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting services with Docker Compose..."
        docker-compose up --build
        exit 0
    fi
fi

# Local setup
echo "📦 Setting up local environment..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
$ACTIVATE_CMD

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "Downloading NLTK resources..."
python -m nltk.downloader punkt stopwords wordnet averaged_perceptron_tagger

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "1. Terminal 1 (FastAPI Backend):"
echo "   $ACTIVATE_CMD"
echo "   python -m uvicorn api.main:app --reload --port 8000"
echo ""
echo "2. Terminal 2 (Streamlit Frontend):"
echo "   $ACTIVATE_CMD"
echo "   streamlit run AA.py"
echo ""
echo "Then visit:"
echo "   🌐 Frontend: http://localhost:8501"
echo "   📚 API Docs: http://localhost:8000/docs"
echo ""
