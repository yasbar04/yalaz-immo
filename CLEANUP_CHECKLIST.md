# 🧹 CLEANUP CHECKLIST - Before First Commit & Deployment

## Files to Remove ❌

These files should be deleted before committing to production:

```bash
# Temporary Java error logs
rm -f hs_err_pid*.log
rm -f replay_pid*.log

# Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -path ./venv -prune -o -type f -name "*.pyo" -delete

# Testing artifacts
rm -rf .pytest_cache/
rm -f .coverage
rm -rf htmlcov/

# IDE artifacts
rm -rf .idea/
rm -rf .vscode/
rm -f *.swp
rm -f *.swo
```

## Files Already in .gitignore ✓

These will be ignored automatically:
- `.env` (dev environment)
- `db.sqlite3` (SQLite database)
- `media/` (User uploads)
- `staticfiles/` (Collected static files)
- `logs/` (Application logs)
- `/ssl/` (SSL certificates)

## Directories to Create 📁

Ensure these exist or will be created:

```bash
# Create if missing
mkdir -p logs/
mkdir -p media/avatars
mkdir -p media/listings
mkdir -p media/front
mkdir -p scripts/
mkdir -p .github/workflows/
```

## Draft Files to Finalize 📝

Review and finalize:

- [ ] `.env.production.example` - Update with your domain
- [ ] `DEPLOYMENT.md` - Update server details
- [ ] `PRODUCTION_CHECKLIST.md` - Customize for your team

## Security Pre-Flight Check 🔒

```bash
# Run before first production deployment
bash scripts/security-check.sh

# Things it checks:
# ✓ DEBUG=False
# ✓ SECRET_KEY is strong
# ✓ No hardcoded credentials
# ✓ No SQL injection patterns
# ✓ ALLOWED_HOSTS is not wildcard
# ✓ Dependencies have no vulnerabilities
```

## Code Quality Check 🧪

```bash
# Format code
black .

# Check formatting
black --check .

# Lint
flake8 apps aylaz

# Run tests
pytest apps/

# Check coverage
pytest --cov=apps
```

## Configuration Verification ✅

### .env Files
- [ ] `.env.example` is up-to-date
- [ ] `.env.production.example` is complete
- [ ] `.env.production` exists and is populated (NOT in git)

### Docker Files
- [ ] `Dockerfile` builds successfully
- [ ] `docker-compose.yml` works locally
- [ ] `docker-compose.prod.yml` is ready

### Documentation
- [ ] All README files are accurate
- [ ] API documentation is up-to-date
- [ ] DEPLOYMENT.md is reviewed

## Git Pre-Deployment

```bash
# Check your status
git status

# Should NOT see:
# - .env files
# - *.log files
# - __pycache__/
# - *.pyc

# Add everything
git add .

# Review changes
git diff --cached

# Commit
git commit -m "feat: Production-ready deployment configuration"
```

## Commit Message Guidelines

Use conventional commits:

```
feat: Production-ready deployment configuration
- Added Docker setup (Dockerfile, docker-compose)
- Added CI/CD workflows (GitHub Actions)
- Enhanced settings for production (PostgreSQL, Redis, Sentry, Logging)
- Added comprehensive documentation
- Added deployment scripts and automation
```

## Final Deployment Verification

Before going live:

```bash
# 1. Pull latest
git pull origin main

# 2. Build locally
docker build -t aylaz:latest .

# 3. Test locally
docker-compose run web python manage.py check --deploy

# 4. Security scan
bash scripts/security-check.sh

# 5. All tests pass
pytest apps/

# ✅ Then deploy to production
```

---

**⚠️ Important**: Never commit:
- `.env` files with real credentials
- Private SSL keys
- Database backups
- Media uploads
- Logs

**Tips**:
- Use `.gitignore` to prevent accidents
- Use `.env.example` as a template
- Document your values somewhere secure (e.g., vault, 1password)
