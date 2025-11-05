#!/bin/bash
# =============================================================================
# Docker Entrypoint Script for GazTracker
# =============================================================================

set -e

echo "🚀 Starting GazTracker Application..."

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "⏳ Waiting for PostgreSQL to be ready..."

    until PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c '\q' 2>/dev/null; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done

    echo "✅ PostgreSQL is ready!"
}

# Function to wait for Redis
wait_for_redis() {
    echo "⏳ Waiting for Redis to be ready..."

    until timeout 1 bash -c "cat < /dev/null > /dev/tcp/${REDIS_HOST}/${REDIS_PORT}" 2>/dev/null; do
        echo "Redis is unavailable - sleeping"
        sleep 2
    done

    echo "✅ Redis is ready!"
}

# Wait for services
wait_for_postgres
wait_for_redis

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head
echo "✅ Migrations completed!"

# Execute the main command
echo "🎯 Starting application server..."
exec "$@"
