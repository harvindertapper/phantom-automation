#!/bin/bash

echo "🚀 Starting Phantom Automation Services..."

# Activate virtual environment
source venv/bin/activate

# Start AI Engine
echo "🧠 Starting AI Engine..."
python services/ai/ai_engine.py &
AI_PID=$!

# Wait a bit
sleep 2

# Start Browser Service
echo "🌐 Starting Browser Service..."
python services/browser/browser_service.py &
BROWSER_PID=$!

# Wait a bit
sleep 2

# Start Task Executor
echo "🔧 Starting Task Executor..."
python services/automation/task_executor.py &
EXECUTOR_PID=$!

echo ""
echo "✅ All services started!"
echo "   AI Engine: http://localhost:5001"
echo "   Browser Service: http://localhost:5002"
echo "   Task Executor: http://localhost:5003"
echo ""
echo "   N8N: http://localhost:5678"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $AI_PID $BROWSER_PID $EXECUTOR_PID; exit" INT
wait
