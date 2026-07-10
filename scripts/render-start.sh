#!/usr/bin/env bash

# Export the virtual environment path (it's inside backend/)
export PATH="$PWD/backend/.venv/bin:$PATH"

echo "Starting RQ Ingestion Worker in the background..."
# Run the worker using the persisted virtual environment
python -m backend.ingestion_worker.main &

echo "Starting FastAPI Web Server..."
# Run the web server in the foreground with proxy headers for HTTPS
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"
