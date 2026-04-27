# Système de Gestion Financière - Yalaz Agence

## Vue d'ensemble

Le système de gestion financière permet au back-office (admin et staff) de suivre toutes les entrées et sorties d'argent de manière organisée et visuelle.

## Fonctionnalités

### 1. **Tableau de Bord Financier** (`/admin/finances/`)
- **Statistiques en temps réel** : Revenus totaux, dépenses totales, solde net
- **Filtres rapides** : Par période (7, 30, 90, 365 jours)
- **Filtrage par type** : Revenus, Dépenses, Commissions, Remboursements
- **Tableau récapitulatif** : Dernières 20 transactions

### 2. **Liste Complète des Transactions** (`/admin/finances/transactions/`)
- **Recherche avancée** : Par description, utilisateur, dates
- **Filtres** : Type, statut, plage de dates
- **Pagination** : 50 transactions par page
- **Actions rapides** : Voir détails, modifier, supprimer

### 3. **Créer une Transaction** (`/admin/finances/transactions/new/`)
- **Types de transactions** :
  - 📥 **Revenus** : Argent entrant
  - 📤 **Dépenses** : Frais, coûts
  - 💰 **Commissions** : Résultant d'une vente/location
  - 🔄 **Remboursements** : Remboursements de clients

- **Informations requises** :
  - Type de transaction *
  - Montant *
  - Description (ex: "Vidéo 500dh", "Commission vente Villa")
  - Date *

- **Informations optionnelles** :
  - Catégorie (ex: "Vidéo", "Photographie", "Commission")
  - Bien immobilier associé
  - Personne affectée
  - Notes supplémentaires

### 4. **Détails d'une Transaction**
- **Vue complète** : Toutes les informations
- **Validation visuelle** : Badges couleur pour type et statut
- **Traçabilité** : Qui a créé ? Quand ? Modifié quand ?
- **Lien bien immobilier** : Si applicable

### 5. **API Statistiques** (`/api/finances/stats/`)
Récupère les statistiques en JSON :
```bash
GET /api/finances/stats/?days=30
```
Retourne :
- `total_income` : Revenus totaux
- `total_expense` : Dépenses totales
- `by_type` : Ventilation par type
- `by_category` : Ventilation par catégorie

## Couleurs et Badges

### Types de Transactions
- 🟢 **Revenus** : Vert (#10b981)
- 🔴 **Dépenses** : Rouge (#ef4444)
- 🔵 **Commissions** : Bleu (#3b82f6)
- 🟠 **Remboursements** : Orange (#f59e0b)

### Statuts
- ✅ **Complété** : Vert
- ⏳ **En attente** : Orange
- ❌ **Annulé** : Rouge

## Exemples d'Utilisation

### Exemple 1 : Enregistrer une vidéo professionnelle
```
Type: Dépenses
Montant: 500 DH
Description: Vidéo professionnelle (2 biens)
Catégorie: Vidéo
Date: 27/04/2026
Statut: Complété
```

### Exemple 2 : Enregistrer une commission de vente
```
Type: Commission
Montant: 50000 DH
Description: Commission vente Villa à Casablanca
Catégorie: Commission
Bien immobilier: Villa Centro Casablanca
Attribué à: [Agent qui a vendu]
Date: 27/04/2026
Statut: Complété
```

### Exemple 3 : Remboursement client
```
Type: Remboursement
Montant: 5000 DH
Description: Remboursement droits agence (bien non signé)
Catégorie: Remboursement
Date: 27/04/2026
Statut: Complété
```

## Contrôle d'Accès

- **Admin** (superuser) : Accès complet + suppression
- **Staff** : Accès complet sauf suppression définitive

## Déploiement

### Étape 1 : Appliquer la migration
```bash
python manage.py migrate
```

### Étape 2 : Accéder au dashboard
```
http://localhost:8000/admin/finances/
```

### Étape 3 : Ajouter des transactions
1. Cliquez sur "Nouvelle Transaction"
2. Remplissez les informations
3. Cliquez "Créer la Transaction"

## Rapports et Analyses

### Via Dashboard
- Vue d'ensemble instantanée
- Filtres par période
- Comparaisons rapides

### Via API
```python
import requests

response = requests.get(
    'http://localhost:8000/api/finances/stats/',
    params={'days': 30}
)
data = response.json()
print(f"Revenus: {data['total_income']} DH")
print(f"Dépenses: {data['total_expense']} DH")
```

## Modèle de Données

```
FinancialTransaction
├── type (income, expense, commission, refund)
├── status (pending, completed, cancelled)
├── amount (Decimal)
├── description (CharField)
├── category (CharField, optionnel)
├── transaction_date (DateField)
├── listing (ForeignKey -> Listing, optionnel)
├── created_by (ForeignKey -> User)
├── assigned_to (ForeignKey -> User, optionnel)
├── notes (TextField, optionnel)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

## Bonnes Pratiques

1. **Descriptions claires** : Soyez spécifique
   - ✅ "Commission vente Apt 2 chambres, Agadir"
   - ❌ "Commission"

2. **Catégories cohérentes** : Utilisez les mêmes catégories
   - Exemples : Vidéo, Photographie, Shooting, Commission

3. **Dates exactes** : La date de transaction ≠ date d'enregistrement
   - Enregistrez la vraie date de la dépense/revenu

4. **Notes pour contexte** : Explicitez si besoin
   - "Réduction appliquée: -10%"
   - "Paiement en plusieurs fois"

5. **Attribuer les commissions** : Liez au bon agent
   - Cela aide au suivi de performance

## Support

Pour toute question ou problème, contactez l'admin Yalaz Agence.
