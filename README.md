# Aylaz

Aylaz est une base propre de marketplace immobilière construite avec Django.

## Fonctionnalités incluses
- authentification utilisateur
- dépôt d'annonce
- liste des biens
- détail d'un bien
- tableau de bord simple “mes annonces”
- panneau d'administration Django
- structure prête pour évoluer vers une API mobile plus tard

## Stack
- Django
- SQLite par défaut pour démarrer vite
- architecture modulaire par apps

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Structure
```text
aylaz/
├── apps/
│   ├── accounts/
│   ├── core/
│   └── listings/
├── aylaz/
├── media/
├── static/
└── templates/
```

## Évolution recommandée
1. Ajouter la modération avancée des annonces
2. Ajouter Django REST Framework pour l'application mobile
3. Passer sur PostgreSQL
4. Ajouter Redis pour le cache
5. Brancher un stockage externe pour les images
