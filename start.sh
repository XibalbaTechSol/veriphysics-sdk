#!/bin/bash

# Kill existing servers
pkill -f "uvicorn" || true
pkill -f "next dev" || true

echo "🚀 Starting VeriPhysics Ecosystem..."

# Start Backend
echo "Backend: Starting on http://localhost:8000"
cd backend
export VERIPHYSICS_CLI_PATH=../cpp_core/build/vp_cli
export LD_LIBRARY_PATH=../cpp_core/build
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "Frontend: Starting on http://localhost:3000"
cd ../frontend
npm run dev -- -p 3000 &
FRONTEND_PID=$!

echo "✅ Services started. Backend PID: $BACKEND_PID, Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop both services."

trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
