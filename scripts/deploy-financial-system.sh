#!/bin/bash
# Script de déploiement - Système de Gestion Financière
# Yalaz Agence - 27/04/2026

echo "================================"
echo "Déploiement Gestion Financière"
echo "================================"
echo ""

# Vérifier Python
echo "✓ Vérification Python..."
python --version

# Vérifier Django
echo "✓ Vérification Django..."
python -c "import django; print(f'Django {django.VERSION}')"

# Appliquer les migrations
echo ""
echo "📦 Étape 1: Application des migrations..."
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "✗ Erreur lors de la migration"
    exit 1
fi
echo "✓ Migrations appliquées avec succès"

# Créer les données de test (optionnel)
echo ""
echo "📊 Étape 2: Création des données de test (optionnel)..."
read -p "Voulez-vous créer des données de test? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py shell < test_financial_system.py
    echo "✓ Données de test créées"
else
    echo "⊘ Données de test non créées"
fi

# Collectes des fichiers statiques
echo ""
echo "📁 Étape 3: Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

if [ $? -ne 0 ]; then
    echo "✗ Erreur lors de la collecte"
    exit 1
fi
echo "✓ Fichiers statiques collectés"

echo ""
echo "================================"
echo "✅ Installation Terminée!"
echo "================================"
echo ""
echo "🔗 URLs d'accès:"
echo "  - Dashboard:    http://localhost:8000/admin/finances/"
echo "  - Transactions: http://localhost:8000/admin/finances/transactions/"
echo "  - API Stats:    http://localhost:8000/api/finances/stats/"
echo ""
echo "📚 Documentation:"
echo "  - FINANCIAL_SYSTEM_README.md"
echo "  - FINANCIAL_SYSTEM.md"
echo ""
echo "🚀 Démarrer le serveur:"
echo "  python manage.py runserver"
echo ""
