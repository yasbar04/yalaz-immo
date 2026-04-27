# 💎 Système de Gestion Financière - Yalaz Agence

## ✨ Nouvelles Fonctionnalités

Un système complet pour la gestion des flux monétaires (entrées et sorties) du back-office admin et staff, avec une interface moderne et intuitive.

## 🚀 Installation Rapide

### 1. Appliquer les migrations
```bash
python manage.py migrate
```

### 2. Accéder au tableau de bord
```
http://localhost:8000/admin/finances/
```

## 📋 Fonctionnalités Principales

### Dashboard Financier
- **📊 Statistiques en temps réel** : Revenus, dépenses, solde net
- **📅 Filtres temporels** : 7, 30, 90, 365 jours
- **🏷️ Filtres avancés** : Type, statut, plage de dates
- **📈 Tableau récapitulatif** : 20 dernières transactions

### Gestion des Transactions
- **➕ Créer** : Nouvelle transaction
- **👁️ Voir** : Détails complets
- **✏️ Modifier** : Mettre à jour les infos
- **🗑️ Supprimer** : Suppression définitive

### Types de Transactions
1. **📥 Revenus** : Argent entrant général
2. **📤 Dépenses** : Frais, coûts, achats
3. **💰 Commissions** : Ventes et locations
4. **🔄 Remboursements** : Retours d'argent

## 📝 Exemple d'Utilisation

### Cas 1 : Enregistrer une vidéo professionnelle de 500 DH
```
Aller à: /admin/finances/transactions/new/

Type: Dépenses
Montant: 500 DH
Description: Vidéo professionnelle (2 biens)
Catégorie: Vidéo
Date: Aujourd'hui
Statut: Complété

→ Cliquer "Créer la Transaction"
```

### Cas 2 : Enregistrer une commission de vente de 50 000 DH
```
Aller à: /admin/finances/transactions/new/

Type: Commission
Montant: 50000 DH
Description: Commission vente Villa luxe Casablanca
Catégorie: Commission
Bien: [Sélectionner le bien]
Attribué à: [Sélectionner l'agent]
Date: Date de la vente
Notes: Villa vendue 2M900k DH, commission 2%

→ Cliquer "Créer la Transaction"
```

## 🎨 Interface Utilisateur

### Design Principles (UI/UX)
- ✅ **Minimalisme** : Interface épurée et claire
- ✅ **Accessibilité** : Contraste élevé (4.5:1), labels explicites
- ✅ **Responsive** : Fonctionne sur mobiles et desktops
- ✅ **Performance** : Chargement rapide, recherche optimisée
- ✅ **Badges colorés** : Identification rapide des types et statuts

### Palette de Couleurs
```
Revenus/Commission:  Vert (#10b981)
Dépenses:            Rouge (#ef4444)
Commissions:         Bleu (#3b82f6)
Remboursements:      Orange (#f59e0b)
En attente:          Orange (#f59e0b)
Complété:            Vert (#10b981)
Annulé:              Rouge (#ef4444)
```

## 🔐 Contrôle d'Accès

| Rôle | Créer | Voir | Modifier | Supprimer |
|------|-------|------|----------|-----------|
| Admin (superuser) | ✅ | ✅ | ✅ | ✅ |
| Staff | ✅ | ✅ | ✅ | ❌ |
| Utilisateur normal | ❌ | ❌ | ❌ | ❌ |

## 📊 API Statistiques

### Récupérer les statistiques en JSON
```bash
curl "http://localhost:8000/api/finances/stats/?days=30"
```

**Réponse:**
```json
{
    "total_income": 75000.00,
    "total_expense": 2000.00,
    "by_type": {
        "income": 3000.00,
        "commission": 72000.00,
        "expense": 2000.00
    },
    "by_category": {
        "Commission": 72000.00,
        "Frais": 3000.00,
        "Vidéo": 500.00,
        "Photographie": 1500.00
    }
}
```

## 🧪 Tester le Système

### Créer des données de test
```bash
python manage.py shell
```

Puis dans le shell Django:
```python
exec(open('test_financial_system.py').read())
```

Cela créera:
- 6 transactions de test variées
- 2 agents (staff) avec données réalistes
- Exemples de commissions et dépenses

## 📚 Documentation Complète

Voir [FINANCIAL_SYSTEM.md](FINANCIAL_SYSTEM.md) pour:
- Modèle de données détaillé
- Guide complet d'utilisation
- Bonnes pratiques
- Requêtes API avancées

## 🔗 URLs Principales

| Page | URL |
|------|-----|
| Dashboard | `/admin/finances/` |
| Toutes les transactions | `/admin/finances/transactions/` |
| Nouvelle transaction | `/admin/finances/transactions/new/` |
| Détails d'une transaction | `/admin/finances/transactions/<id>/` |
| Modifier une transaction | `/admin/finances/transactions/<id>/edit/` |
| Supprimer une transaction | `/admin/finances/transactions/<id>/delete/` |
| API Statistiques | `/api/finances/stats/?days=30` |

## 🎯 Prochaines Améliorations Possibles

- [ ] Export CSV/Excel
- [ ] Graphiques interactifs
- [ ] Rapports mensuels automatiques
- [ ] Intégration bancaire
- [ ] Approvals workflow
- [ ] Notifications pour seuils

## 💬 Support

Pour toute question sur le système de gestion financière, consultez:
1. La documentation complète: `FINANCIAL_SYSTEM.md`
2. L'interface d'aide dans l'application
3. Contact admin Yalaz Agence

---

**Version:** 1.0  
**Dernière mise à jour:** 27 Avril 2026  
**Créé pour:** Yalaz Agence - Plateforme Immobilière Marocaine
