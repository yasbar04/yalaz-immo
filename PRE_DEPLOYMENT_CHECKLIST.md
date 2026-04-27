# ✅ CHECKLIST PRE-DEPLOIEMENT FINAL

Avant de pousser le site en production sur OVH, vérifier chaque point.

## 📋 Configuration du projet local

- [ ] Python 3.11+ installé
- [ ] virtualenv ou pyenv activé
- [ ] `pip install -r requirements.txt` exécuté
- [ ] Base de données SQLite créée et testée localement
- [ ] `python manage.py runserver` fonctionne sans erreur
- [ ] Admin Django accessible sur `http://localhost:8000/admin/`

## 🔐 Fichiers de configuration production

- [ ] `.env.production` créé (copie de `.env.production.example`)
- [ ] `SECRET_KEY` changée (50+ caractères aléatoires)
- [ ] `DB_PASSWORD` changée pour PostgreSQL
- [ ] `REDIS_PASSWORD` changée pour Redis
- [ ] `EMAIL_HOST_USER` et `EMAIL_HOST_PASSWORD` configurés
- [ ] `ALLOWED_HOSTS` mis à jour: `yalaz-immo.com,www.yalaz-immo.com`
- [ ] `DEBUG=False` en production
- [ ] `SECURE_SSL_REDIRECT=True`

## 🐳 Docker et déploiement

- [ ] `Dockerfile` présent et testé localement
- [ ] `docker-compose-prod-optimised.yml` présent et valide
- [ ] `nginx-prod.conf` présent avec le bon domaine
- [ ] `.dockerignore` configuré correctement
- [ ] `requirements-prod.txt` actualisé avec les dépendances

## 🔧 Scripts de déploiement

- [ ] `scripts/deploy-ovh.sh` présent et exécutable
- [ ] `scripts/backup.sh` présent et testé
- [ ] Tous les scripts ont le shebang `#!/bin/bash`

## 📚 Documentation

- [ ] `DEPLOYMENT_QUICK_START.md` rédigé et clair
- [ ] `DEPLOYMENT_OVH.md` rédigé et clair
- [ ] `DEPLOIEMENT_RESUME.md` rédigé
- [ ] Tous les guides contiennent les étapes essentielles

## 🚀 Préparation OVH

### Serveur

- [ ] Serveur OVH commandé et accessible en SSH
- [ ] IP publique du serveur notée
- [ ] Accès SSH testé
- [ ] Clé SSH configurée correctement

### Domaine

- [ ] Domaine `yalaz-immo.com` acheté
- [ ] Domaine dans votre compte OVH ou chez le registrar
- [ ] Accès à la gestion DNS disponible
- [ ] A comprendre: comment pointer le DNS vers le serveur

### Email

- [ ] Compte Gmail (ou autre serveur SMTP) disponible
- [ ] 2-Step Verification activée pour Gmail
- [ ] App Password généré pour Gmail
- [ ] Les identifiants sont dans `.env.production`

## 🔍 Vérifications de code

- [ ] `DEBUG=False` dans settings production
- [ ] `ALLOWED_HOSTS` correctement configuré
- [ ] `SECRET_KEY` pas en dur dans le code
- [ ] Pas de mots de passe en dur dans les fichiers
- [ ] `.gitignore` inclut `.env.production` et `.env`
- [ ] Aucun token/API key dans le repository

## 📦 Git et dépôt

- [ ] Tout le code commité localement
- [ ] Branches nettoyées (main/master à jour)
- [ ] `.env.production` NEpasPas commité (dans .gitignore)
- [ ] Repository en ligne (GitHub, GitLab, etc.)
- [ ] Aucune erreur npm/pip install en affichage

## 🗄️ Base de données

- [ ] Migrations Django créées et testées
- [ ] `python manage.py makemigrations` exécuté
- [ ] `python manage.py migrate` exécuté sur la BD test
- [ ] Aucune erreur dans les migrations
- [ ] Données de test supprimées

## 📂 Fichiers statiques et media

- [ ] `collectstatic` fonctionne sans erreur
- [ ] `/static/` et `/media/` répertoires existent
- [ ] `.gitignore` exclut les fichiers générés (collectstatic)
- [ ] CSS/JS/images minimifiés (optionnel)

## ✉️ Email et notifications

- [ ] Serveur SMTP testé en local
- [ ] Test d'envoi d'email fonctionne
- [ ] Templates d'email en place
- [ ] Adresses "from" et "reply-to" configurées

## 🔐 Sécurité

- [ ] `CSRF_TRUSTED_ORIGINS` configuré avec le domaine HTTPS
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True` en production
- [ ] `SESSION_COOKIE_HTTPONLY=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] Headers de sécurité extra ajoutés (nginx-prod.conf)
- [ ] Rate limiting activé
- [ ] CORS restreint à domaine autorisé

## 📝 Logs et monitoring

- [ ] Dossier `/logs/` créé
- [ ] Logging configuré dans settings
- [ ] Health check endpoint testable
- [ ] Monitoring/Sentry configuré (optionnel mais recommandé)

## 🔄 Processus de mise à jour

- [ ] Stratégie de rollback documentée
- [ ] Backup automatique configuré
- [ ] Script de sauvegarde BD testé
- [ ] Plan pour mettre à jour le code post-déploiement

## 🧪 Tests finaux (après déploiement)

- [ ] Site accessible sur `https://yalaz-immo.com`
- [ ] Redirection HTTP→HTTPS fonctionne
- [ ] SSL certificate valide et pas d'erreur
- [ ] Admin accessible `/admin/` 
- [ ] Health check répond `/health/`
- [ ] Aucune erreur 500 ou 404
- [ ] Logs sans erreurs critiques
- [ ] Email fonctionne (test d'envoi réussi)
- [ ] Base de données accessible et fonctionnelle
- [ ] Fichiers statiques chargent correctement
- [ ] Cache Redis fonctionne

## 📋 Dernier jour avant le go-live

- [ ] Tester le site complet en local
- [ ] Faire un test de déploiement sur staging si possible
- [ ] Vérifier tous les liens externes
- [ ] Tester les formulaires
- [ ] Tester les uploads de fichiers
- [ ] Tester l'authentification user
- [ ] Tester les transactions financières si applicables
- [ ] Vérifier le SEO (sitemap.xml, robots.txt)

## 📊 Documentation finale

- [ ] README.md clair pour les développeurs
- [ ] DEPLOYMENT guides bien écrits
- [ ] Contactez/Support défini
- [ ] Backup procedures documentées
- [ ] Monitoring tools expliqués

---

## ✅ SIGNATURE PRE-DEPLOIEMENT

Une fois TOUS les points cochés ✅, vous pouvez procéder au déploiement:

```bash
# 1. Commit final
git add .
git commit -m "🚀 Pre-production deployment - all checks passed"
git push origin main

# 2. Connectez-vous au serveur OVH
ssh root@VOTRE_IP_OVH

# 3. Déployez
cd /var/www/aylaz
bash scripts/deploy-ovh.sh
```

**Date de déploiement:** __________  
**Responsable:** __________  
**Signature:** __________  

---

## 🚨 EN CAS DE PROBLEME

Si quelque chose échoue:

1. **Arrêtez immédiatement le déploiement**
2. **Consultez `DEPLOYMENT_OVH.md` section dépannage**
3. **Vérifiez les logs:** `docker-compose logs -f`
4. **Rollback:** `docker-compose down` puis redémarrer anciens conteneurs

**Ne jamais forcer** - il vaut mieux attendre et bien faire que d'avoir un site en panne.

---

**Bonne chance ! 🚀**
