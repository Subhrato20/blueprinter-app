#!/bin/bash

# Blueprinter Backend Runner Script
echo "🚀 Starting Blueprinter Backend..."

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -e .

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating one..."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "OPENAI_MODEL=gpt-5" >> .env
    echo "CORS_ORIGINS=http://localhost:5173,http://localhost:3000" >> .env
    echo "📝 Please edit backend/.env and add your OpenAI API key"
fi

# Start the server
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
