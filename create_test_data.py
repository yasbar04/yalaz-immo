#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aylaz.settings')
django.setup()

from django.contrib.auth.models import User
from apps.listings.models import Listing

# Créer utilisateurs de test
users = [
    {'username': 'vendeur1', 'email': 'vendeur1@aylaz.com', 'password': 'Test1234!'},
    {'username': 'vendeur2', 'email': 'vendeur2@aylaz.com', 'password': 'Test1234!'},
    {'username': 'acheteur1', 'email': 'acheteur1@aylaz.com', 'password': 'Test1234!'},
]

for user_data in users:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'first_name': user_data['username'].capitalize(),
        }
    )
    if created:
        user.set_password(user_data['password'])
        user.save()
        print(f"✓ Créé: {user_data['username']}")
    else:
        print(f"✓ Existe: {user_data['username']}")

# Créer annonces de test
vendeur1 = User.objects.get(username='vendeur1')
vendeur2 = User.objects.get(username='vendeur2')

listings = [
    {
        'owner': vendeur1,
        'title': 'Bel appartement 3pcs au centre-ville',
        'property_type': Listing.PropertyType.APARTMENT,
        'listing_type': Listing.ListingType.RENT,
        'city': 'Casablanca',
        'district': 'Maarif',
        'price': 8500,
        'surface_area': 120,
        'bedrooms': 3,
        'bathrooms': 2,
        'description': 'Superbe appartement lumineux avec vue sur la ville.\n- Cuisine équipée\n- Balcon spacieux\n- Parking privé\n- Immeuble sécurisé',
        'status': Listing.Status.PUBLISHED,
    },
    {
        'owner': vendeur1,
        'title': 'Terrain 1000m² à Marrakech',
        'property_type': Listing.PropertyType.LAND,
        'listing_type': Listing.ListingType.SALE,
        'city': 'Marrakech',
        'district': 'Gueliz',
        'price': 450000,
        'surface_area': 1000,
        'bedrooms': 0,
        'bathrooms': 0,
        'description': 'Terrain parfait pour construction.\n- Viabilisé\n- Vue panoramique\n- Zone prisée',
        'status': Listing.Status.PUBLISHED,
    },
    {
        'owner': vendeur2,
        'title': 'Villa moderne 4 chambres',
        'property_type': Listing.PropertyType.VILLA,
        'listing_type': Listing.ListingType.SALE,
        'city': 'Rabat',
        'district': 'Souissi',
        'price': 2500000,
        'surface_area': 350,
        'bedrooms': 4,
        'bathrooms': 3,
        'description': 'Villa luxueuse avec piscine et jardin aménagé.\n- Home cinéma\n- Garage double\n- Salle de sport\n- Climatisation centrale',
        'status': Listing.Status.PUBLISHED,
    },
    {
        'owner': vendeur2,
        'title': 'Bureau 200m² à Fès',
        'property_type': Listing.PropertyType.OFFICE,
        'listing_type': Listing.ListingType.RENT,
        'city': 'Fès',
        'district': 'Ville Nouvelle',
        'price': 3500,
        'surface_area': 200,
        'bedrooms': 0,
        'bathrooms': 2,
        'description': 'Bureau professionnel bien situé.\n- Réception\n- 4 bureaux\n- Salle de réunion\n- Internet haut débit',
        'status': Listing.Status.PUBLISHED,
    },
    {
        'owner': vendeur1,
        'title': 'Maison traditionnelle à Fès',
        'property_type': Listing.PropertyType.HOUSE,
        'listing_type': Listing.ListingType.SALE,
        'city': 'Fès',
        'district': 'Médina',
        'price': 650000,
        'surface_area': 180,
        'bedrooms': 3,
        'bathrooms': 2,
        'description': 'Belle maison anscrale avec patio.\n- Terrasse sur le toit\n- Cuisine traditionnelle\n- 3 niveaux\n- Cachet authentique',
        'status': Listing.Status.PUBLISHED,
    },
]

for listing_data in listings:
    listing, created = Listing.objects.get_or_create(
        title=listing_data['title'],
        owner=listing_data['owner'],
        defaults=listing_data
    )
    if created:
        print(f"✓ Annonce créée: {listing_data['title']}")
        listing.views_count = 10 + (hash(listing.title) % 50)
        listing.save()
    else:
        print(f"✓ Annonce existe: {listing_data['title']}")

print("\n" + "="*60)
print("✅ IDENTIFIANTS DE TEST CRÉÉS:")
print("="*60)
print("\n👤 VENDEURS (avec annonces):")
print("  - vendeur1 / Test1234!")
print("  - vendeur2 / Test1234!")
print("\n👤 ACHETEUR (pour chercher):")
print("  - acheteur1 / Test1234!")
print("\n👨‍💼 ADMIN (pour modérer):")
print("  - admin / test1234")
print("\n" + "="*60)
