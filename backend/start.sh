#!/bin/bash

# Exit on error
set -e

echo "--- Starting Migrations ---"
python migrate.py

echo "--- Starting Celery Worker in Background ---"
# We run the worker in the background so the web server can start
celery -A worker.celery worker --loglevel=info --concurrency=1 &

echo "--- Starting Gunicorn Web Server ---"
# The web server must run in the foreground (hold the process)
gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
