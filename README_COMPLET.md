# 🏠 Aylaz - Marketplace Immobilière Professionnelle

Aylaz est une plateforme de marketplace immobilière moderne, construite avec Django et prête pour la production.

## 📋 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Stack Technologique](#stack-technologique)
- [Installation Locale](#installation-locale)
- [Déploiement Production](#déploiement-production)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Contribution](#contribution)

## ✨ Fonctionnalités

### Utilisateurs
- ✅ Authentification sécurisée (email + SMS)
- ✅ Profil utilisateur complet
- ✅ Récupération de mot de passe
- ✅ Vérification en deux étapes (Email + SMS)
- ✅ Gestion des favoris

### Annonces Immobilières
- ✅ Création/Édition d'annonces
- ✅ Galerie photos (multiple uploads)
- ✅ Validation administrative
- ✅ Recherche avancée et filtrage
- ✅ Sitemap généré automatiquement
- ✅ SEO optimisé

### Administration
- ✅ Tableau de bord admin
- ✅ Gestion des utilisateurs
- ✅ Validation des annonces
- ✅ Gestion des signalements

### API REST
- ✅ API v1 complète
- ✅ Authentification token
- ✅ Pagination et filtrage
- ✅ Rate limiting

## 🛠️ Stack Technologique

### Backend
- **Django 5.0+** - Framework web Python
- **Django REST Framework** - API REST
- **PostgreSQL** - Base de données production-ready
- **Redis** - Cache et sessions
- **Gunicorn** - Serveur WSGI
- **Nginx** - Reverse proxy

### Frontend (Optionnel)
- HTML/CSS/JavaScript
- Bootstrap 5
- HTMX (optional)

### DevOps
- **Docker** - Containerisation
- **Docker Compose** - Orchestration locale
- **GitHub Actions** - CI/CD
- **Sentry** - Error tracking
- **SendGrid/Mailgun** - Email transactionnel

## 🚀 Installation Locale

### Prérequis

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker et Docker Compose (optionnel)

### Installation Standard

```bash
# Cloner le repository
git clone <url-du-repo>
cd aylaz

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

L'application est accessible à `http://localhost:8000`

### Installation avec Docker

```bash
# Démarrer les services
docker-compose up -d

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser

# Accéder à http://localhost
```

## 📦 Déploiement Production

### Guide Complet

Pour un guide détaillé, consultez [DEPLOYMENT.md](DEPLOYMENT.md)

### Démarrage Rapide

```bash
# Sur votre serveur
ssh user@your-server

# Cloner et configurer
git clone <url-du-repo> /home/aylaz-app
cd /home/aylaz-app

# Lancer le setup
bash scripts/setup-prod.sh

# (Le script vous guidera pour configurer l'environnement)
```

### Environnement Production (.env.production)

```bash
# Sécurité
SECRET_KEY=<votre-clé-secrète-forte>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Base de données
DB_ENGINE=django.db.backends.postgresql
DB_NAME=aylaz
DB_USER=aylaz_user
DB_PASSWORD=<mot-de-passe-fort>
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<votre-clé-sendgrid>
DEFAULT_FROM_EMAIL=hello@your-domain.com

# Cache
REDIS_URL=redis://localhost:6379/0

# Monitoring
SENTRY_DSN=<votre-dsn-sentry>
```

### Commandes Principales

```bash
# Démarrer les services
make docker-up

# Voir les logs
make docker-logs

# Backup
make backup

# Vérifier la santé
make health
```

## 🏗️ Architecture

```
aylaz/
├── apps/
│   ├── accounts/          # Authentification utilisateurs
│   │   ├── models.py      # User custom, codes de vérification
│   │   ├── views.py       # Login, signup, password reset
│   │   └── serializers.py # API serializers
│   │
│   ├── core/              # Fonctionnalités principales
│   │   ├── views.py       # Pages principales, health check
│   │   └── health.py      # Endpoint de santé
│   │
│   ├── listings/          # Gestion des annonces
│   │   ├── models.py      # Listing, Photo, Report
│   │   ├── views.py       # CRUD des annonces
│   │   └── admin.py       # Validation admin
│   │
│   └── api/               # API REST
│       ├── viewsets.py    # Endpoints API
│       └── urls.py        # Routes API
│
├── aylaz/
│   ├── settings.py        # Configuration Django
│   ├── urls.py            # Routes principales
│   ├── wsgi.py            # WSGI production
│   └── asgi.py            # ASGI WebSocket
│
├── templates/             # Templates HTML
├── static/                # Fichiers statiques
├── media/                 # Uploads utilisateurs
├── logs/                  # Logs application
└── scripts/               # Scripts utiles

```

## 📊 Modèles de Données

### User (Custom)
```python
- email (unique)
- phone
- full_name
- is_verified_email
- is_verified_phone
- created_at
```

### Listing (Annonce)
```python
- user
- title
- description
- price
- location
- property_type (RENT/SALE)
- bedrooms
- bathrooms
- area
- status (DRAFT/PENDING/APPROVED/REJECTED)
- created_at
- photos (relation)
```

### Photo
```python
- listing
- image
- order
- uploaded_at
```

## 🔒 Sécurité

### Implémenté
- ✅ HTTPS/SSL obligatoire en production
- ✅ HSTS headers
- ✅ CSRF protection
- ✅ SQL injection prevention (ORM)
- ✅ XSS protection
- ✅ Rate limiting API
- ✅ Authentication token sécurisé
- ✅ Password hashing (PBKDF2)
- ✅ Two-factor authentication (Email + SMS)

### À Vérifier Avant Production

```bash
# Lancer les vérifications de sécurité
bash scripts/security-check.sh

# Vérifier les dépendances
pip check

# Scanner statique (optionnel)
bandit -r apps/
```

## 📝 Tests

```bash
# Lancer les tests
python -m pytest

# Avec coverage
pytest --cov=apps

# Tests spécifiques
pytest apps/accounts/tests.py::TestSignup -v
```

## 🔄 CI/CD

Le projet inclut des workflows GitHub Actions :

- **CI** (`.github/workflows/ci.yml`) : Tests, linting, couverture de code
- **Deploy** (`.github/workflows/deploy.yml`) : Build Docker et déploiement automatique

## 📚 API Documentation

### Endpoints Principales

```
GET    /api/v1/listings/              - Lister les annonces
POST   /api/v1/listings/              - Créer une annonce
GET    /api/v1/listings/{id}/         - Détails d'une annonce
PUT    /api/v1/listings/{id}/         - Modifier une annonce
DELETE /api/v1/listings/{id}/         - Supprimer une annonce

GET    /api/v1/users/{id}/            - Profil utilisateur
PUT    /api/v1/users/{id}/            - Modifier profil
POST   /api/auth/token/               - Obtenir un token API
```

### Authentication

```bash
# Obtenir un token
curl -X POST http://localhost:8000/api/auth/token/ \
  -d "username=user&password=pass"

# Utiliser le token
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/listings/
```

## 📞 Support et Contribution

Pour les bug reports et feature requests, ouvrez une issue sur GitHub.

## 📄 License

Ce projet est sous license [votre-license].

---

**Version**: 1.0.0  
**Dernière mise à jour**: Avril 2026  
**Status**: ✅ Production Ready
