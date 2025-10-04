#!/bin/bash

# Blueprint Snap Frontend Runner
# Dev DNA Edition

set -e

echo "🌐 Starting Blueprint Snap Frontend"
echo "==================================="

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
fi

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found. Please run from project root."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start frontend
echo "🚀 Starting frontend server..."
cd frontend
npm run dev
