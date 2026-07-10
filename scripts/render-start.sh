#!/usr/bin/env bash

cd backend

# Export the virtual environment path
export PATH="$PWD/.venv/bin:$PATH"

echo "Starting RQ Ingestion Worker in the background..."
# Run the worker using the persisted virtual environment
python -m ingestion_worker.main &

echo "Starting FastAPI Web Server..."
# Run the web server in the foreground
uvicorn app.main:app --host 0.0.0.0 --port $PORT
