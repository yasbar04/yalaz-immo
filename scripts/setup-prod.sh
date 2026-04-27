#!/bin/bash
set -e

# Production setup script for Aylaz
# Run this on your production server

echo "🔧 Setting up production environment..."

# Create application directory
APP_DIR="/home/aylaz-app"
mkdir -p $APP_DIR

# Clone repository (or pull if exists)
if [ -d "$APP_DIR/.git" ]; then
    cd $APP_DIR
    git pull origin main
else
    git clone <your-repository-url> $APP_DIR
    cd $APP_DIR
fi

# Create environment files
echo "📝 Creating environment files..."
cp .env.production.example .env.production

echo ""
echo "⚠️  IMPORTANT: Edit the following file with your production values:"
echo "   $APP_DIR/.env.production"
echo ""
read -p "Press Enter after configuring your .env.production file..."

# Install Docker and Docker Compose if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Start services
echo "▶️  Starting services..."
docker-compose -f docker-compose.yml up -d

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 15

# Run migrations
echo "🗄️  Running migrations..."
docker-compose exec -T web python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
docker-compose exec web python manage.py createsuperuser

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Setup SSL with Let's Encrypt (optional)
read -p "Do you want to setup SSL with Let's Encrypt? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔒 Setting up SSL..."
    docker-compose exec web certbot certonly --nginx -d your-domain.com
fi

echo "✅ Production setup complete!"
echo ""
echo "📌 Next steps:"
echo "1. Configure your domain to point to this server"
echo "2. Setup SSL certificates"
echo "3. Configure backups"
echo "4. Monitor with Sentry (optional)"
