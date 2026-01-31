#!/bin/bash

# Exit on error
set -e

echo "--- Starting Migrations ($(date)) ---"
# Use -u for unbuffered output so logs show up immediately
python -u migrate.py

echo "--- Starting Custom Worker in Background ($(date)) ---"
python -u worker.py > worker.log 2>&1 &

echo "--- Starting Gunicorn Web Server ($(date)) ---"
# Bind to $PORT which is required by Render
exec gunicorn main:app \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --log-level info \
    --access-logfile - \
    --error-logfile -

