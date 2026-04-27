#!/bin/bash

# 🚀 SCRIPT DE DEPLOIEMENT AUTOMATIQUE - AYLAZ SUR OVH
# Usage: bash deploy-ovh.sh

set -e

echo "========================================="
echo "🚀 DEPLOIEMENT AYLAZ - PRODUCTION OVH"
echo "========================================="
echo ""

# Vérifier les prérequis
echo "📋 Vérification des prérequis..."
command -v docker &> /dev/null || { echo "❌ Docker non installé"; exit 1; }
command -v docker-compose &> /dev/null || { echo "❌ Docker Compose non installé"; exit 1; }
command -v nginx &> /dev/null || { echo "⚠️  Nginx non trouvé (optionnel)"; }

# Variables
PROJECT_DIR="/var/www/aylaz"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
ENV_FILE="$PROJECT_DIR/.env.production"

# Vérifier que le répertoire existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Le répertoire $PROJECT_DIR n'existe pas"
    exit 1
fi

cd "$PROJECT_DIR"

# Vérifier le fichier .env.production
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Fichier $ENV_FILE non trouvé"
    echo "📝 Veuillez d'abord copier .env.example vers .env.production et configurer les variables"
    exit 1
fi

echo "✅ Vérifications OK"
echo ""

# Sauvegarder la base de données
echo "💾 Sauvegarde de la base de données..."
mkdir -p backups
docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_dump -U ${DB_USER} ${DB_NAME} > "backups/backup-$(date +%Y%m%d-%H%M%S).sql"
echo "✅ Sauvegarde complétée"
echo ""

# Arrêter les anciens conteneurs
echo "🛑 Arrêt des conteneurs existants..."
docker-compose -f "$DOCKER_COMPOSE_FILE" down || true
echo "✅ Conteneurs arrêtés"
echo ""

# Rebuild des images
echo "🔨 Construction des images Docker..."
docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
echo "✅ Images construites"
echo ""

# Démarrer les services
echo "🚀 Démarrage des services..."
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
echo "✅ Services démarrés"
echo ""

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 10

# Appliquer les migrations
echo "🔄 Application des migrations..."
docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py migrate
echo "✅ Migrations appliquées"
echo ""

# Collecter les fichiers statiques
echo "📦 Collecte des fichiers statiques..."
docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py collectstatic --noinput --clear
echo "✅ Fichiers statiques collectés"
echo ""

# Vérifier la santé
echo "🏥 Vérification de la santé du système..."
if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T web python manage.py shell -c "from django.core.management import call_command; print('✅ Django OK')" 2>/dev/null; then
    echo "✅ Application Django OK"
else
    echo "⚠️  Attention: Vérification Django échouée"
fi

# Vérifier les logs
echo ""
echo "📝 Vérification des logs..."
echo ""
docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=20 web
echo ""

# Afficher le status
echo ""
echo "========================================="
echo "✅ DEPLOIEMENT COMPLETE !"
echo "========================================="
echo ""
echo "Status des services:"
docker-compose -f "$DOCKER_COMPOSE_FILE" ps
echo ""
echo "🌐 Site disponible à: https://yalaz-immo.com"
echo "🔐 Admin disponible à: https://yalaz-immo.com/admin/"
echo "📊 Health check: https://yalaz-immo.com/health/"
echo ""
echo "📝 Logs en temps réel:"
echo "   docker-compose -f $DOCKER_COMPOSE_FILE logs -f web"
echo ""
echo "🔍 Commandes utiles:"
echo "   docker-compose -f $DOCKER_COMPOSE_FILE ps          # Status"
echo "   docker-compose -f $DOCKER_COMPOSE_FILE logs web   # Logs Django"
echo "   docker-compose -f $DOCKER_COMPOSE_FILE exec web bash  # Shell"
echo ""
