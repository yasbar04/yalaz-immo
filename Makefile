# Makefile for Aylaz - Common development and deployment tasks

.PHONY: help install dev test lint format migrations migrate collect-static clean deploy backup health

help:
	@echo "Aylaz - Marketplace immobilière"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev              - Start development server"
	@echo "  make install          - Install dependencies"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run linting checks"
	@echo "  make format           - Format code with Black"
	@echo "  make migrations       - Create database migrations"
	@echo "  make migrate          - Apply database migrations"
	@echo "  make collect-static   - Collect static files"
	@echo "  make clean            - Clean temporary files"
	@echo "  make security-check   - Run security checks"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make shell            - Open Django shell"
	@echo "  make createsuperuser  - Create admin user"

install:
	pip install -r requirements.txt
	python manage.py migrate

dev:
	python manage.py runserver

test:
	pytest

lint:
	black --check .
	flake8 apps aylaz --max-line-length=120 --ignore=E203,W503

format:
	black .

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

collect-static:
	python manage.py collectstatic --noinput

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov .coverage

security-check:
	bash scripts/security-check.sh

docker-build:
	docker build -t aylaz:latest -f Dockerfile .

docker-up:
	docker-compose -f docker-compose.prod.yml up -d

docker-down:
	docker-compose -f docker-compose.prod.yml down

docker-logs:
	docker-compose -f docker-compose.prod.yml logs -f

shell:
	python manage.py shell

createsuperuser:
	python manage.py createsuperuser

backup:
	bash scripts/backup.sh all

health:
	@echo "🔍 Checking application health..."
	@curl -s http://localhost:8000/health/ && echo "✅ Health check passed" || echo "❌ Health check failed"

.DEFAULT_GOAL := help
