#!/bin/bash
# Startup script for Render deployment

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
uvicorn app.main:socket_app --host 0.0.0.0 --port $PORT
