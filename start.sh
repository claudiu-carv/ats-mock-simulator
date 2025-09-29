#!/bin/bash

# ATS Mock API Server Startup Script

echo "🚀 Starting ATS Mock API Server..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Install Python dependencies if needed
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Install Node.js dependencies if needed
echo "📦 Installing Node.js dependencies..."
npm install

echo "🔧 Starting backend server..."
# Start backend in background
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo "🎨 Starting frontend development server..."
# Start frontend in background
cd frontend && npm run dev &
FRONTEND_PID=$!

echo "✅ Servers started successfully!"
echo "   - Backend API: http://localhost:8000"
echo "   - Frontend UI: http://localhost:3000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script termination
trap cleanup INT TERM

# Wait for background processes
wait
