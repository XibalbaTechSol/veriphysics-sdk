#!/bin/bash
# Kill process on port 3000 (node)
kill -9 $(lsof -t -i:3000) 2>/dev/null
pkill -f "uvicorn" 2>/dev/null

echo "Starting Backend..."
cd /home/xibalbasolutions/Desktop/veriphysics-sdk/backend
export VERIPHYSICS_CLI_PATH=../cpp_core/build/vp_cli
export LD_LIBRARY_PATH=../cpp_core/build
nohup ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > /home/xibalbasolutions/Desktop/veriphysics-sdk/backend.log 2>&1 &
echo "Backend PID: $!"

echo "Starting Frontend..."
cd /home/xibalbasolutions/Desktop/veriphysics-sdk/frontend
nohup npm run dev -- -p 3000 > /home/xibalbasolutions/Desktop/veriphysics-sdk/frontend.log 2>&1 &
echo "Frontend PID: $!"

echo "Services started."
