#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"
# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations orderbook
python manage.py migrate

# Start server
echo "Starting server"
daphne -b 0.0.0.0 -p 8001 backend.asgi:application