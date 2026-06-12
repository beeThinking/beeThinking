#!/bin/bash

# Start script for BeeThinking Backend

echo "🐝 Starting BeeThinking Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and set your SECRET_KEY before starting!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Import bundled BeeIntouch PDFs once per file hash
echo "Running BeeIntouch PDF import..."
python -m app.importers.beeintouch_pdf_import --source-dir import_sources/beeintouch

# Start the server
echo "🚀 Starting server on http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
