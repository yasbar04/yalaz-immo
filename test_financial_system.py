"""
Script pour tester le système de gestion financière
Crée des transactions de test pour vérifier le fonctionnement

Usage: python manage.py shell < test_financial_system.py
Ou: python manage.py shell
    >>> exec(open('test_financial_system.py').read())
"""

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from apps.core.models import FinancialTransaction
from apps.listings.models import Listing

User = get_user_model()

print("=" * 60)
print("TEST - Système de Gestion Financière")
print("=" * 60)

# Obtenir ou créer un utilisateur admin
try:
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.local',
            password='admin123'
        )
        print("✓ Utilisateur admin créé")
    else:
        print(f"✓ Utilisateur admin trouvé: {admin_user.username}")
except Exception as e:
    print(f"✗ Erreur création admin: {e}")
    exit(1)

# Créer quelques utilisateurs staff/agents
try:
    agent1, created = User.objects.get_or_create(
        username='agent_aziz',
        defaults={
            'email': 'aziz@yalaz.ma',
            'first_name': 'Aziz',
            'last_name': 'Benali',
            'is_staff': True,
        }
    )
    if created:
        agent1.set_password('password123')
        agent1.save()
        print(f"✓ Agent créé: {agent1.username}")
    else:
        print(f"✓ Agent trouvé: {agent1.username}")

    agent2, created = User.objects.get_or_create(
        username='agent_sarah',
        defaults={
            'email': 'sarah@yalaz.ma',
            'first_name': 'Sarah',
            'last_name': 'Romaine',
            'is_staff': True,
        }
    )
    if created:
        agent2.set_password('password123')
        agent2.save()
        print(f"✓ Agent créé: {agent2.username}")
    else:
        print(f"✓ Agent trouvé: {agent2.username}")
except Exception as e:
    print(f"✗ Erreur création agents: {e}")
    exit(1)

# Exemples de transactions
transactions_data = [
    {
        'type': 'expense',
        'amount': Decimal('500.00'),
        'description': 'Vidéo professionnelle (2 biens)',
        'category': 'Vidéo',
        'status': 'completed',
        'assigned_to': agent1,
        'transaction_date': timezone.now().date() - timedelta(days=5),
    },
    {
        'type': 'commission',
        'amount': Decimal('50000.00'),
        'description': 'Commission vente Villa à Casablanca',
        'category': 'Commission',
        'status': 'completed',
        'assigned_to': agent1,
        'transaction_date': timezone.now().date() - timedelta(days=3),
        'notes': 'Villa luxe vendue 2M900k DH, commission 2%',
    },
    {
        'type': 'expense',
        'amount': Decimal('1500.00'),
        'description': 'Photographie immobilière profesionnelle',
        'category': 'Photographie',
        'status': 'completed',
        'assigned_to': agent2,
        'transaction_date': timezone.now().date() - timedelta(days=2),
    },
    {
        'type': 'commission',
        'amount': Decimal('25000.00'),
        'description': 'Commission location Appartement 2ch Agadir',
        'category': 'Commission',
        'status': 'completed',
        'assigned_to': agent2,
        'transaction_date': timezone.now().date() - timedelta(days=1),
        'notes': 'Loyer: 8000 DH/mois, commission 3 mois',
    },
    {
        'type': 'income',
        'amount': Decimal('3000.00'),
        'description': 'Frais de dossier clients',
        'category': 'Frais',
        'status': 'completed',
        'transaction_date': timezone.now().date(),
    },
    {
        'type': 'expense',
        'amount': Decimal('200.00'),
        'description': 'Maintenance site web',
        'category': 'Maintenance',
        'status': 'pending',
        'transaction_date': timezone.now().date(),
        'notes': 'Hébergement et certificat SSL',
    },
]

print("\n" + "-" * 60)
print("Création de transactions de test...")
print("-" * 60)

created_count = 0
for i, trans_data in enumerate(transactions_data, 1):
    try:
        trans = FinancialTransaction.objects.create(
            created_by=admin_user,
            **trans_data
        )
        created_count += 1
        
        sign = "+" if trans.type in ['income', 'commission'] else "-"
        status_emoji = "✓" if trans.status == 'completed' else "⏳"
        
        print(f"{status_emoji} Transaction {i}: {sign}{trans.amount} DH - {trans.description}")
    except Exception as e:
        print(f"✗ Erreur transaction {i}: {e}")

print("\n" + "=" * 60)
print(f"RÉSULTATS: {created_count}/{len(transactions_data)} transactions créées")
print("=" * 60)

# Afficher les statistiques
print("\n📊 STATISTIQUES:\n")

all_transactions = FinancialTransaction.objects.all()
completed = all_transactions.filter(status='completed')
income = completed.filter(type__in=['income', 'commission']).aggregate(total=Sum('amount'))['total'] or 0
expense = completed.filter(type__in=['expense', 'refund']).aggregate(total=Sum('amount'))['total'] or 0

print(f"Total transactions: {all_transactions.count()}")
print(f"  - Complétées: {completed.count()}")
print(f"  - En attente: {all_transactions.filter(status='pending').count()}")
print(f"\nSolde financier:")
print(f"  - Revenus: {income:,.2f} DH")
print(f"  - Dépenses: {expense:,.2f} DH")
print(f"  - Solde net: {income - expense:,.2f} DH")

print("\n" + "=" * 60)
print("✅ Test terminé avec succès!")
print("Accédez au dashboard: http://localhost:8000/admin/finances/")
print("=" * 60)
