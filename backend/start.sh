#!/bin/bash

# Exit on error
set -e

echo "--- Starting Migrations ($(date)) ---"
# Use -u for unbuffered output so logs show up immediately
python -u migrate.py

echo "--- Starting Custom Worker (Merged into Web Server) ---"
# Worker now starts inside main.py for memory efficiency

echo "--- Starting Gunicorn Web Server ($(date)) ---"
# Bind to $PORT which is required by the environment
exec gunicorn main:app \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -

