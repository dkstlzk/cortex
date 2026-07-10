#!/usr/bin/env bash

# Export the uv path
export PATH="$HOME/.local/bin:$PATH"

cd backend

echo "Starting RQ Ingestion Worker in the background..."
# Run the worker in the background using '&'
uv run python -m ingestion_worker.main &

echo "Starting FastAPI Web Server..."
# Run the web server in the foreground so Render detects the open port
uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
