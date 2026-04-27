#!/usr/bin/env python
"""Add staff user to Administrators group"""
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aylaz.settings')
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

django.setup()

from django.contrib.auth.models import User, Group

try:
    # Créer le groupe Administrators s'il n'existe pas
    admin_group, created = Group.objects.get_or_create(name='Administrators')
    if created:
        print("✓ Groupe 'Administrators' créé")
    else:
        print("✓ Groupe 'Administrators' existe déjà")
    
    # Récupérer l'utilisateur "ali"
    try:
        user = User.objects.get(username='ali')
        print(f"✓ Utilisateur 'ali' trouvé")
        
        # Ajouter au groupe
        user.groups.add(admin_group)
        user.save()
        print(f"✓ Utilisateur 'ali' ajouté au groupe 'Administrators'")
        print(f"\n✅ SUCCESS: 'ali' peut maintenant accéder au back office!")
        print(f"   Allez sur: /accounts/admin/")
        
    except User.DoesNotExist:
        print(f"❌ ERREUR: Utilisateur 'ali' non trouvé")
        print(f"\nUtilisateurs disponibles:")
        for u in User.objects.all():
            print(f"   - {u.username}")
            
except Exception as e:
    print(f"❌ ERREUR: {e}")
