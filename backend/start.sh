#!/bin/bash

# Exit on error
set -e

echo "--- Starting Migrations ---"
python migrate.py

echo "--- Starting Custom Worker in Background ---"
# We run the worker in the background so the web server can start
# This uses the custom TaskQueue based on Redis, not Celery
python worker.py &

echo "--- Starting Gunicorn Web Server ---"
# The web server must run in the foreground (hold the process)
gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
