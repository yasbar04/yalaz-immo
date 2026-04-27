#!/bin/bash
set -e

# Deployment script for Aylaz
# Usage: ./scripts/deploy.sh [production|staging]

ENVIRONMENT=${1:-staging}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"

echo "🚀 Deploying Aylaz to $ENVIRONMENT..."

# Load environment variables
if [ -f "$PROJECT_DIR/.env.$ENVIRONMENT" ]; then
    export $(cat "$PROJECT_DIR/.env.$ENVIRONMENT" | grep -v '^#' | xargs)
else
    echo "❌ Error: .env.$ENVIRONMENT not found"
    exit 1
fi

# Pull latest code
echo "📥 Pulling latest code..."
cd "$PROJECT_DIR"
git pull origin main

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t aylaz:$ENVIRONMENT -f Dockerfile .

# Stop old containers
echo "🛑 Stopping old containers..."
docker-compose -f docker-compose.yml down

# Start new containers
echo "▶️  Starting new containers..."
docker-compose -f docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Clear cache
echo "🧹 Clearing cache..."
docker-compose exec -T redis redis-cli FLUSHDB

# Run health checks
echo "🏥 Running health checks..."
if curl -sf http://localhost/health/ > /dev/null; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    docker-compose logs web
    exit 1
fi

echo "✅ Deployment successful!"
