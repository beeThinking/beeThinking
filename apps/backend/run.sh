#!/bin/bash

# Quick start script for development

echo "🐝 BeeThinking Backend - Quick Start"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  .env created. Using SQLite by default."
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
echo ""

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
