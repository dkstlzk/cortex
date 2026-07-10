#!/usr/bin/env bash

# Export the virtual environment path (it's inside backend/)
export PATH="$PWD/backend/.venv/bin:$PATH"

echo "Scheduling RQ Ingestion Worker to start in 20 seconds..."
# Run the worker in the background after a delay to prevent ONNX/CPU deadlock with Uvicorn
(sleep 20 && echo "Starting RQ Ingestion Worker now..." && python -m backend.ingestion_worker.main) &

echo "Starting FastAPI Web Server..."
# Run the web server in the foreground with proxy headers for HTTPS
uvicorn backend.fabric_api.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"
