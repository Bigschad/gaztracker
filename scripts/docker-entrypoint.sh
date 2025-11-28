#!/bin/bash
# =============================================================================
# Docker Entrypoint Script for GazTracker
# =============================================================================

set -e

echo "🚀 Starting GazTracker Application..."

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "⏳ Waiting for PostgreSQL to be ready..."

    # Support both DATABASE_* and POSTGRES_* environment variables
    DB_HOST=${POSTGRES_HOST:-${DATABASE_HOST:-postgres}}
    DB_USER=${POSTGRES_USER:-${DATABASE_USER:-gaztracker_user}}
    DB_PASSWORD=${POSTGRES_PASSWORD:-${DATABASE_PASSWORD}}
    DB_NAME=${POSTGRES_DB:-${DATABASE_NAME:-gaztracker_db}}
    DB_PORT=${POSTGRES_PORT:-${DATABASE_PORT:-5432}}

    until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done

    echo "✅ PostgreSQL is ready!"
}

# Function to wait for Redis
wait_for_redis() {
    echo "⏳ Waiting for Redis to be ready..."

    REDIS_HOST_VAR=${REDIS_HOST:-redis}
    REDIS_PORT_VAR=${REDIS_PORT:-6379}

    # Try to connect to Redis using Python (redis-cli not available in Python image)
    until python -c "import socket; s = socket.socket(); s.settimeout(1); result = s.connect_ex(('${REDIS_HOST_VAR}', ${REDIS_PORT_VAR})); s.close(); exit(0 if result == 0 else 1)" 2>/dev/null; do
        echo "Redis is unavailable - sleeping"
        sleep 2
    done

    # Verify Redis is responding using Python redis client
    until python -c "import redis; r = redis.Redis(host='${REDIS_HOST_VAR}', port=${REDIS_PORT_VAR}, socket_timeout=1); r.ping()" 2>/dev/null; do
        echo "Redis is not responding - sleeping"
        sleep 2
    done

    echo "✅ Redis is ready!"
}

# Wait for services
wait_for_postgres
wait_for_redis

# Ensure logs directory exists and has correct permissions
echo "📁 Setting up logs directory..."
mkdir -p /app/logs
touch /app/logs/gaztracker.log 2>/dev/null || true
# Try to fix permissions if we have write access
chmod 777 /app/logs 2>/dev/null || true
chmod 666 /app/logs/gaztracker.log 2>/dev/null || true

# Run database migrations
echo "🔄 Running database migrations..."
echo "   Checking current database state..."
alembic current || echo "   No migrations applied yet"

echo "   Applying migrations..."
alembic upgrade heads

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully!"
    echo "   Current revision:"
    alembic current
else
    echo "❌ Migration failed!"
    exit 1
fi

# Execute the main command
echo "🎯 Starting application server..."
exec "$@"
