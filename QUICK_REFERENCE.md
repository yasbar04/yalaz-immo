# ⚡ QUICK REFERENCE - Commandes essentielles

## 🚀 Démarrage

```bash
# Local development
make dev

# Docker local
make docker-up

# Production server
docker-compose -f docker-compose.prod.yml up -d
```

## 🗄️ Database

```bash
# Migrations
make migrations
make migrate

# Backup
make backup

# Shell Django
make shell

# Create superuser
make createsuperuser
```

## 🧪 Tests & Quality

```bash
# Tests
make test

# Linting
make lint

# Format
make format

# Security
make security-check
```

## 📊 Monitoring

```bash
# Logs
make docker-logs

# Health check
make health

# Database check
docker-compose exec db psql -U aylaz_user aylaz
```

## 🔒 Security

```bash
# Rigadier security checklist
bash scripts/security-check.sh

# Generate new SECRET_KEY
openssl rand -hex 32
```

## 📦 Static Files

```bash
# Collect
make collect-static

# Clean
make clean
```

## 🐳 Docker

```bash
# Build
make docker-build

# Push
docker push your-registry/aylaz:latest

# Rebuild after code change
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🌐 API Tests

```bash
# Get token
curl -X POST http://localhost:8000/api/auth/token/ \
  -d "username=admin&password=pass"

# Use token
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/listings/

# Health check
curl http://localhost:8000/health/
```

## 📧 Email Test

```python
# In Django shell
python manage.py shell

from django.core.mail import send_mail
send_mail('Test', 'test', 'from@example.com', ['to@example.com'])
```

## 🔄 Update Deployment

```bash
cd /home/aylaz-app
git pull origin main
bash scripts/deploy.sh production
```

## 🚨 Emergency

```bash
# View recent errors
docker-compose logs web -n 100

# Restart services
docker-compose restart web

# Full rebuild
docker-compose down
docker-compose up -d --build
```

## 📊 Sentry

- Dashboard: https://sentry.io
- DSN: Check in .env.production
- Releases: `sentry-cli releases create -p aylaz ...`

---

**Tip**: Utilisez `make help` pour voir toutes les commandes disponibles!
