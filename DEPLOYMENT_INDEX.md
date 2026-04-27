# 📖 INDEX - GUIDE DE DEPLOIEMENT AYLAZ

## 🎯 PAR OÙ COMMENCER

### 1️⃣ LISEZ D'ABORD (5 min)
**Fichier:** `DEPLOIEMENT_RESUME.md`  
**Pourquoi:** Vue d'ensemble rapide de ce qui a été créé et comment ça marche

### 2️⃣ CHECKLIST PRE-DEPLOIEMENT (10 min)
**Fichier:** `PRE_DEPLOYMENT_CHECKLIST.md`  
**Pourquoi:** S'assurer que tout est prêt avant de commencer

### 3️⃣ GUIDE ETAPE PAR ETAPE (30 min - 1 heure)
**Fichier:** `DEPLOYMENT_QUICK_START.md`  
**Pourquoi:** Instructions précises et détaillées pour le déploiement

### 4️⃣ GUIDE DETAILLE (référence)
**Fichier:** `DEPLOYMENT_OVH.md`  
**Pourquoi:** Pour les détails, dépannage et troubleshooting

---

## 📦 TOUS LES FICHIERS CREÉS/MODIFIES

### Configuration

| Fichier | Rôle | Note |
|---------|------|------|
| `.env.production` | Variables d'env production | ⚠️ À personnaliser |
| `.env.production.example` | Template consommable | ✅ Exemple référence |
| `nginx-prod.conf` | Configuration Nginx avec HTTPS | ✅ Prêt à utiliser |

### Docker & Déploiement

| Fichier | Rôle | Note |
|---------|------|------|
| `docker-compose-prod-optimised.yml` | Services Docker (DB, Redis, Django, Nginx) | ✅ Prêt à utiliser |
| `Dockerfile` | Image Docker Django | ✅ Déjà existant |
| `scripts/deploy-ovh.sh` | Déploiement automatisé | ⚠️ À tester |

### Documentation

| Fichier | Quand le lire | Durée |
|---------|---------------|-------|
| `DEPLOIEMENT_RESUME.md` | En premier | 5 min |
| `PRE_DEPLOYMENT_CHECKLIST.md` | Avant de déployer | 10 min |
| `DEPLOYMENT_QUICK_START.md` | Pendant le déploiement | 30 min - 1h |
| `DEPLOYMENT_OVH.md` | Pour la référence | 30 min |
| `DEPLOYMENT.md` | Pour approfondir | 60 min |
| `QUICK_REFERENCE.md` | Commandes utiles | 5 min |

---

## 🚀 PROCESSUS COMPLET

### PHASE 1: Préparation locale (1 heure)

```
✅ Tester le site localement
✅ Vérifier les migrations BD
✅ Tester les emails
✅ Tester les fichiers statiques
```

Fichiers à consulter: `PRE_DEPLOYMENT_CHECKLIST.md`

### PHASE 2: Configuration production (30 minutes)

```
✅ Personnaliser .env.production
✅ Générer les secrets
✅ Configurer les emails
✅ Mettre à jour les domaines
```

Fichier à consulter: `DEPLOYMENT_QUICK_START.md` (Étapes 5-6)

### PHASE 3: Préparation serveur (30 minutes)

```
✅ Installer Docker
✅ Installer Docker Compose
✅ Cloner le repository
✅ Créer les répertoires
```

Fichier à consulter: `DEPLOYMENT_QUICK_START.md` (Étapes 1-4)

### PHASE 4: DNS et domaine (variable)

```
✅ Configurer les enregistrements A/CNAME
✅ Attendre la propagation DNS (1-24h)
✅ Vérifier avec `nslookup` ou `dig`
```

Fichier à consulter: `DEPLOYMENT_QUICK_START.md` (Étape 10)

### PHASE 5: Déploiement (15 minutes)

```
✅ Exécuter le script deploy-ovh.sh OU
✅ Suivre docker-compose manuellement
✅ Générer le certificat SSL
✅ Redémarrer les services
```

Fichier à consulter: `DEPLOYMENT_QUICK_START.md` (Étapes 7-8-9)

### PHASE 6: Vérification (15 minutes)

```
✅ Tester le site en HTTPS
✅ Tester l'admin
✅ Tester la santé /health/
✅ Vérifier les logs
```

Fichier à consulter: `DEPLOYMENT_QUICK_START.md` (Étape 12)

---

## 🎓 COMMANDES PRINCIPALES

### Déploiement initial
```bash
cd /var/www/aylaz
sudo bash scripts/deploy-ovh.sh
```

### Vérification
```bash
docker-compose -f docker-compose-prod-optimised.yml ps
docker-compose -f docker-compose-prod-optimised.yml logs -f web
```

### Maintenance
```bash
# Backup
docker-compose -f docker-compose-prod-optimised.yml exec db pg_dump -U aylaz_user aylaz_prod > backup.sql

# Mise à jour du code
git pull origin main
docker-compose -f docker-compose-prod-optimised.yml restart web

# Shell Django
docker-compose -f docker-compose-prod-optimised.yml exec web bash
```

---

## 🚨 EN CAS D'URGENCE

Si le site tombe:

```bash
# 1. Vérifier les logs
docker-compose -f docker-compose-prod-optimised.yml logs web | tail -100

# 2. Vérifier les services
docker-compose -f docker-compose-prod-optimised.yml ps

# 3. Redémarrer
docker-compose -f docker-compose-prod-optimised.yml restart

# 4. Arrêter si critique
docker-compose -f docker-compose-prod-optimised.yml down
```

Voir section "Dépannage" dans `DEPLOYMENT_OVH.md`

---

## 📚 FICHES DE REFERENCE

### Variables d'environnement essentielles
```env
SECRET_KEY=votre-cle-de-50-caracteres
DB_PASSWORD=mot-de-passe-fort
REDIS_PASSWORD=mot-de-passe-redis
EMAIL_HOST_PASSWORD=app-password-gmail
DEBUG=False
```

### Services Docker activés
- **PostgreSQL** (port 5432 interne)
- **Redis** (port 6379 interne)
- **Django + Gunicorn** (port 8000 interne)
- **Nginx** (ports 80, 443 publics)
- **Certbot** (renouvellement SSL auto)

### Domaines
- **Production:** https://yalaz-immo.com
- **Admin:** https://yalaz-immo.com/admin/
- **Health:** https://yalaz-immo.com/health/

---

## ✅ CHECKLIST RAPIDE AVANT LE GO LIVE

- [ ] `.env.production` rempli avec bonnes valeurs
- [ ] SECRET_KEY changée (50+ chars)
- [ ] Mots de passe DB et Redis changés
- [ ] Email configuré et testé
- [ ] Domaine pointé vers ServeurOVH
- [ ] SSH accessible
- [ ] Docker installé
- [ ] Code cloné et à jour
- [ ] FAQ PRE_DEPLOYMENT_CHECKLIST validée
- [ ] Commandes de test exécutées
- [ ] Logs consultés sans erreurs
- [ ] Site répondant sur https://

---

## 🤝 SUPPORT

**Est-ce dans cette doc?**
→ Consulter l'index ci-dessus

**Problème spécifique?**
→ Consulter `DEPLOYMENT_OVH.md` (section dépannage)

**Question générale Docker?**
→ https://docs.docker.com/

**Question générale Django?**
→ https://docs.djangoproject.com/

---

## 🎉 APRÈS LE DEPLOIEMENT

Une fois en production:

1. **Configurer les backups automatiques**
   ```bash
   # Éditer le cron
   sudo crontab -e
   # Ajouter: 0 2 * * * cd /var/www/aylaz && bash scripts/backup.sh
   ```

2. **Mettre en place le monitoring** (optionnel)
   - Sentry pour les erreurs
   - Uptime robot pour la disponibilité
   - New Relic pour la performance

3. **Mettre à jour régulièrement**
   ```bash
   git pull origin main
   docker-compose restart web
   ```

4. **Vérifier régulièrement les logs**
   ```bash
   docker-compose logs --tail=100 web | grep ERROR
   ```

---

**Bon déploiement ! 🚀**

Pour commencer: Lisez **DEPLOIEMENT_RESUME.md** en premier !
