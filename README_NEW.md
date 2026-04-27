# Aylaz - Marketplace Immobilière

Aylaz est une plateforme moderne de marketplace immobilière construite avec Django. Elle permet aux particuliers et aux agences immobilières de publier, découvrir et gérer des biens.

Plateforme prête pour la production avec une architecture scalable et une expérience utilisateur moderne.

## 🎯 Fonctionnalités Principales

- ✅ **Authentification Complète** - Inscription, connexion, gestion de profil
- ✅ **Gestion d'Annonces** - Créer, modifier, supprimer, publier des biens
- ✅ **Images Multiples** - Support de plusieurs images par annonce
- ✅ **Moteur de Recherche** - Recherche avancée avec filtres par prix, type, localisation
- ✅ **Système de Contact** - Contacter les vendeurs via formulaire intégré
- ✅ **Dashboard** - Tableau de bord complet pour gérer ses annonces
- ✅ **Modération** - Admin intégré pour modérer les contenus
- ✅ **Responsive Design** - Interface adaptée mobile et desktop
- ✅ **Sécurité Production** - Gestion des secrets, headers de sécurité, validation

## 🛠️ Stack Technique

- **Backend** : Django 5.0+
- **Database** : SQLite (développement), PostgreSQL (production)
- **Frontend** : HTML, CSS (modern, responsive), JavaScript vanilla
- **Images** : Pillow pour traitement d'images
- **Configuration** : python-dotenv pour variables d'environnement

## 📋 Prérequis

- Python 3.9+
- pip
- Virtual Environment (venv, virtualenv, etc.)

## 🚀 Démarrage Rapide

### 1. Cloner le projet et accéder au répertoire
```bash
cd aylaz
```

### 2. Créer et activer l'environnement virtuel

**Sur Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

**Sur macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer l'environnement
```bash
cp .env.example .env
# Éditer .env et changer SECRET_KEY pour un développement sécurisé
```

### 5. Préparer la base de données
```bash
python manage.py migrate
python manage.py createsuperuser  # Créer un utilisateur admin
```

### 6. Lancer le serveur de développement
```bash
python manage.py runserver
```

Accédez à http://127.0.0.1:8000

## 📱 Architecture du Projet

```
aylaz/
├── apps/
│   ├── accounts/          # Authentification et gestion d'utilisateurs
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   ├── core/              # Pages principales et configuration globale
│   │   └── views.py
│   └── listings/          # Gestion des annonces immobilières
│       ├── models.py      # Listing, ListingImage, Contact
│       ├── views.py
│       ├── forms.py
│       ├── admin.py
│       └── urls.py
├── aylaz/                 # Configuration Django
│   ├── settings.py        # Paramètres appliquation
│   ├── urls.py            # Routage principal
│   └── wsgi.py
├── templates/             # Templates HTML
│   ├── base.html
│   ├── accounts/
│   ├── listings/
│   └── core/
├── static/                # CSS, JavaScript, assets
│   ├── css/
│   └── js/
├── media/                 # Fichiers media uploadés
├── .env                   # Variables d'environnement (local)
├── .env.example           # Template pour .env
├── requirements.txt       # Dépendances Python
└── manage.py
```

## 🔑 Modèles de Données Principaux

### Listing
- Représente une annonce immobilière
- Statuts : DRAFT, PENDING, PUBLISHED, REJECTED
- Types : SALE, RENT
- Propriété types : APARTMENT, HOUSE, VILLA, LAND, OFFICE
- Suivi des vues et des contacts

### ListingImage
- Images supplémentaires pour une annonce
- Ordre configurable
- Alt text pour accessibilité

### Contact
- Messages des acheteurs/locataires aux vendeurs
- Marquer comme lu/non lu
- Historique traçable

## 🛡️ Sécurité

- Variables sensibles dans `.env` (SECRET_KEY, ALLOWED_HOSTS)
- Validation strict des entrées utilisateur
- Protection CSRF sur tous les formulaires
- Headers de sécurité en production
- Gestion des permissions utilisateur
- Validation des images uploadées

## 📈 Roadmap Recommandée

### Phase 2 - Backend
- [ ] API REST avec Django REST Framework
- [ ] Système de notifications par email
- [ ] Favoris/watchlist pour acheteurs
- [ ] Historique des annonces (soft delete)
- [ ] Audit trail pour modération

### Phase 3 - Scalabilité
- [ ] Passage à PostgreSQL
- [ ] Redis pour cache et sessions
- [ ] Elasticsearch pour la recherche avancée
- [ ] CDN pour les images
- [ ] Pagination optimisée

### Phase 4 - Monétisation
- [ ] Système de boosts/mise en avant
- [ ] Paiement avec Stripe
- [ ] Abonnements premium
- [ ] Analytics vendeur

### Phase 5 - Mobile
- [ ] Application React Native ou Flutter
- [ ] Push notifications

## 🤝 Contribution

Pour améliorer le projet :

1. Créer une branche feature
2. Commiter les modifications
3. Tester avant de fusionner
4. Respecter les conventions de code

## 📄 Configuration Production

Pour déployer en production :

1. **Changer DEBUG à False** dans `.env`
2. **Générer une nouvelle SECRET_KEY**
3. **Configurer ALLOWED_HOSTS** pour votre domaine
4. **Passer à PostgreSQL**
5. **Ajouter HTTPS/SSL**
6. **Configurer les emails transactionnels**
7. **Mettre en place les logs**
8. **Sauvegarder les images sur S3 ou similaire**
9. **Utiliser un serveur WSGI** (Gunicorn)
10. **Mettre à jour les headers de sécurité**

Exemple avec Gunicorn :
```bash
gunicorn aylaz.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

## 📞 Support & Contact

Pour des questions, consultez la documentation Django:
- [Django Docs](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

## 📜 License

Ce projet est open-source. À personnaliser selon vos besoins.

---

**Créé avec ❤️ par le team Aylaz | 2026**
