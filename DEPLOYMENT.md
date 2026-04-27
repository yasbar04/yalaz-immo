# DEPLOYMENT GUIDE - Aylaz

This guide will help you deploy Aylaz to production.

## Prerequisites

- Docker and Docker Compose installed on your production server
- Domain name pointing to your server
- Sentry account (optional but recommended)
- SendGrid/Mailgun account for email
- AWS access (optional, for backups)

## Quick Start

### 1. Prepare Your Server

```bash
ssh your-server

# Clone the repository
git clone <your-repo-url> /home/aylaz-app
cd /home/aylaz-app

# Run setup script
bash scripts/setup-prod.sh
```

### 2. Configure Environment

Edit `.env.production`:

```bash
# CRITICAL - Generate a strong SECRET_KEY
openssl rand -hex 32

# Configure database
DB_PASSWORD=generate-a-strong-password

# Configure email
EMAIL_HOST_USER=your-sendgrid-api-key
EMAIL_HOST_PASSWORD=your-smtp-password

# Configure Sentry (optional)
SENTRY_DSN=https://your-sentry-dsn
```

### 3. Start Services

```bash
# Build and start containers
docker-compose -f docker-compose.prod.yml up -d

# Verify services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f web
```

### 4. Setup SSL (Let's Encrypt)

```bash
# Using Certbot
docker-compose exec web certbot certonly --nginx -d your-domain.com

# Update nginx.conf to use SSL certs
# Then restart nginx
docker-compose restart nginx
```

### 5. Setup Automated Backups

```bash
# Add to crontab
0 2 * * * /home/aylaz-app/scripts/backup.sh all

# Verify backup script is executable
chmod +x /home/aylaz-app/scripts/backup.sh
```

## Monitoring

### Logs

```bash
# Django application logs
docker-compose logs -f web

# Nginx access/error logs
docker-compose logs -f nginx

# Database logs
docker-compose logs -f db
```

### Health Checks

```bash
# Application health
curl http://your-domain.com/health/

# Database connection
docker-compose exec db psql -U aylaz_user -d aylaz -c "SELECT 1"

# Redis connection
docker-compose exec redis redis-cli ping
```

### Performance Monitoring

- **Sentry**: Real-time error tracking
  - Configure in `.env.production`
  - Access at sentry.io

- **New Relic** (optional):
  ```bash
  pip install newrelic
  NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn ...
  ```

## Maintenance

### Database

```bash
# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access admin panel
https://your-domain.com/admin/

# Create admin user
docker-compose exec web python manage.py shell
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'password')
```

### Updates

```bash
# Pull latest code
cd /home/aylaz-app
git pull origin main

# Rebuild Docker image
docker build -t aylaz:latest -f Dockerfile .

# Apply migrations
docker-compose exec web python manage.py migrate

# Restart services
docker-compose restart web
```

### Scaling

```bash
# Add more gunicorn workers
# Edit docker-compose.prod.yml
# Change: gunicorn --workers 4
# To: gunicorn --workers 8

# Add load balancer (NGINX)
# Already configured in nginx.conf
# Adjust worker_processes for your CPU cores
```

## Production Checklist

- [ ] SECRET_KEY is strong and secret
- [ ] DEBUG=False
- [ ] Email configured and tested
- [ ] Database backups scheduled
- [ ] SSL certificate installed
- [ ] Monitoring/Sentry configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Admin user created
- [ ] Domain DNS records configured
- [ ] Firewall rules configured (only 80, 443 open)
- [ ] Regular backups verified
- [ ] Log rotation configured

## Troubleshooting

### Services won't start

```bash
# Check Docker logs
docker-compose logs web db redis nginx

# Verify .env variables
cat .env.production

# Check ports are not in use
netstat -tlnp | grep -E :(80|443|5432|6379|8000)
```

### Database connection issues

```bash
# Test database connection
docker-compose exec db psql -U ${DB_USER} -h localhost ${DB_NAME}

# Check PostgreSQL logs
docker-compose logs db
```

### No static files

```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check permissions
docker exec aylaz-web ls -la /app/staticfiles/
```

## Support

For issues, check:
- Application logs: `/home/aylaz-app/logs/django.log`
- Docker logs: `docker-compose logs`
- Sentry dashboard for error tracking
