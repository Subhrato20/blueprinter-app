#!/bin/bash

# Blueprint Snap Backend Runner
# Dev DNA Edition

set -e

echo "🔧 Starting Blueprint Snap Backend"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run setup_env.py first."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found. Please run from project root."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install dependencies if needed
if [ ! -d "backend/.venv" ] && [ ! -d "backend/venv" ]; then
    echo "📦 Installing backend dependencies..."
    cd backend
    python3 -m pip install -e .
    cd ..
fi

# Start backend
echo "🚀 Starting backend server..."
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
