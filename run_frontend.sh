#!/bin/bash

# Blueprinter Frontend Runner Script
echo "🎨 Starting Blueprinter Frontend..."

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌟 Starting Vite development server on http://localhost:5173"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

npm run dev
