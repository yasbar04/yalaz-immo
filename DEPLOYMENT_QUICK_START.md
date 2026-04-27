# 🚀 DEPLOIEMENT AYLAZ SUR OVH - GUIDE COMPLET

## ⚡ RESUME RAPIDE (5 étapes)

```bash
# 1. Connexion SSH au serveur OVH
ssh root@votre-ip-ovh

# 2. Installer Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 3. Cloner et configurer
cd /var/www
git clone votre-repo.git aylaz && cd aylaz

# 4. Générer les secrets
python3 -c "import secrets; print(secrets.token_urlsafe(50))" > secret.txt

# 5. Configurer et déployer
# Éditer .env.production avec les valeurs
nano .env.production
docker-compose -f docker-compose-prod-optimised.yml up -d
```

---

## 📋 INSTALLATION DETAILLEE

### ETAPE 1: Connectez-vous à OVH

```bash
ssh root@VOTRE_IP_OVH
# D'vous pouvez aussi utiliser votre utilisateur OVH
ssh votre-user@VOTRE_IP_OVH
```

### ETAPE 2: Installation de Docker

```bash
# Télécharger et installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker

# Vérifier l'installation
docker --version
docker run hello-world
```

### ETAPE 3: Installation de Docker Compose

```bash
# Vérifier la dernière version sur https://github.com/docker/compose/releases
sudo curl -L https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Vérifier
docker-compose --version
```

### ETAPE 4: Cloner le projet

```bash
# Créer le répertoire web
sudo mkdir -p /var/www
cd /var/www

# Cloner le repository (vous devez avoir accès Git configuré)
git clone https://votre-repo-github.git aylaz
cd aylaz

# Ou si vous avez déjà un zip/tar, le décompresser
# tar -xzf aylaz.tar.gz
# cd aylaz
```

### ETAPE 5: Générer les secrets

**A. Générer la SECRET_KEY robuste:**

```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"
# Copier la valeur (ex: SECRET_KEY=AbCdEfGhIjKlMnOpQrStUvWxYz...)
```

**B. Générer le mot de passe PostgreSQL:**

```bash
python3 -c "import secrets; print('DB_PASSWORD=' + secrets.token_urlsafe(20))"
```

**C. Générer le mot de passe Redis:**

```bash
python3 -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(20))"
```

### ETAPE 6: Configurer les variables d'environnement

```bash
# Copier le fichier exemple
cp .env.production.example .env.production

# Éditer avec les vraies valeurs
nano .env.production
```

**VARIABLES A ABSOLUMENT CONFIGURER:**

```env
# Remplacer par les valeurs générées
DEBUG=False
SECRET_KEY=VOTRE_SECRET_KEY_GENEREE_ICI
ALLOWED_HOSTS=yalaz-immo.com,www.yalaz-immo.com

# Base de données (remplacer le mot de passe)
DB_NAME=aylaz_prod
DB_USER=aylaz_user
DB_PASSWORD=VOTRE_DB_PASSWORD_ICI

# Redis
REDIS_PASSWORD=VOTRE_REDIS_PASSWORD_ICI

# Email (configurer votre serveur SMTP)
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password-gmail

# Domaine
APP_BASE_URL=https://yalaz-immo.com
CSRF_TRUSTED_ORIGINS=https://yalaz-immo.com,https://www.yalaz-immo.com
```

**Comment obtenir EMAIL_HOST_PASSWORD pour Gmail:**
1. Activer 2-Step Verification: https://myaccount.google.com/security
2. Créer une "App Password": https://myaccount.google.com/apppasswords
3. Copier le mot de passe généré dans EMAIL_HOST_PASSWORD

### ETAPE 7: Structurer les répertoires

```bash
# Créer les répertoires nécessaires
mkdir -p logs/nginx
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p backups

# Donner les bonnes permissions
chmod 755 logs
chmod 755 certbot
```

### ETAPE 8: Déployer l'application

**Option A: Déploiement avec le script (recommandé)**

```bash
# Rendre le script exécutable
chmod +x scripts/deploy-ovh.sh

# Exécuter le déploiement
sudo bash scripts/deploy-ovh.sh
```

**Option B: Déploiement manuel**

```bash
# Démarrer les conteneurs
docker-compose -f docker-compose-prod-optimised.yml up -d

# Vérifier le démarrage
docker-compose -f docker-compose-prod-optimised.yml ps

# Voir les logs
docker-compose -f docker-compose-prod-optimised.yml logs -f web
```

### ETAPE 9: Générer le certificat SSL

```bash
# Générer le certificat Let's Encrypt
docker-compose -f docker-compose-prod-optimised.yml exec certbot certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d yalaz-immo.com \
  -d www.yalaz-immo.com \
  --email admin@yalaz-immo.com \
  --agree-tos \
  --non-interactive

# Redémarrer Nginx après génération du cert
docker-compose -f docker-compose-prod-optimised.yml restart nginx
```

### ETAPE 10: Configurer le DNS

**Chez votre registrar DNS (OVH ou autre):**

1. Ajouter un enregistrement A:
   - Domaine: `yalaz-immo.com`
   - Type: `A`
   - Cible: `VOTRE_IP_OVH`

2. Ajouter un enregistrement CNAME (optionnel, pour www):
   - Domaine: `www.yalaz-immo.com`
   - Type: `CNAME`
   - Cible: `yalaz-immo.com`

3. Vérifier la propagation DNS (5-24 heures):
   ```bash
   nslookup yalaz-immo.com
   dig yalaz-immo.com
   ```

### ETAPE 11: Créer le superuser

```bash
# Accéder au shell Django
docker-compose -f docker-compose-prod-optimised.yml exec web python manage.py createsuperuser

# Suivre les instructions
# Email: admin@yalaz-immo.com
# Password: entrer un mot de passe fort
# Repeat: confirmer
```

### ETAPE 12: Tester l'accès

```bash
# Attendre quelques minutes pour la propagation DNS puis:

# Site public
curl https://yalaz-immo.com
# Ou dans le navigateur: https://yalaz-immo.com

# Admin
https://yalaz-immo.com/admin/
# Entrer les identifiants superuser

# Health check
curl https://yalaz-immo.com/health/
```

---

## 🔧 COMMANDS UTILES

### Vérification et Monitoring

```bash
# Status des conteneurs
docker-compose -f docker-compose-prod-optimised.yml ps

# Logs en temps réel
docker-compose -f docker-compose-prod-optimised.yml logs -f web

# Logs de Nginx
docker-compose -f docker-compose-prod-optimised.yml logs -f nginx

# Ressources utilisées
docker stats

# Accès à la base de données
docker-compose -f docker-compose-prod-optimised.yml exec db psql -U aylaz_user -d aylaz_prod
```

### Maintenance

```bash
# Sauvegarder la base de données
docker-compose -f docker-compose-prod-optimised.yml exec db pg_dump -U aylaz_user aylaz_prod > backup-$(date +%Y%m%d).sql

# Mise à jour du code (pull depuis Git)
git pull origin main
docker-compose -f docker-compose-prod-optimised.yml restart web

# Redémarrer tous les services
docker-compose -f docker-compose-prod-optimised.yml restart

# Arrêter les services
docker-compose -f docker-compose-prod-optimised.yml down

# Accès shell Django
docker-compose -f docker-compose-prod-optimised.yml exec web bash
```

---

## ✅ CHECKLIST VERIFICATION

Avant de dire que c'est en production, vérifier:

- [ ] SSH accessible depuis votre IP
- [ ] Docker installé et fonctionnel
- [ ] Git repository accessible
- [ ] Fichier `.env.production` créé avec les bonnes valeurs
- [ ] Les 3 secrets (SECRET_KEY, DB_PASSWORD, REDIS_PASSWORD) changés
- [ ] Email SMTP configuré et testé
- [ ] Répertoires créés (logs, certbot, backups)
- [ ] Conteneurs démarrés sans erreur
- [ ] Migrations appliquées (pas d'erreurs de migration)
- [ ] Superuser créé
- [ ] Certificat SSL généré
- [ ] DNS pointé vers le serveur OVH
- [ ] Site accessible à https://yalaz-immo.com
- [ ] Admin accessible à https://yalaz-immo.com/admin/
- [ ] Health check OK: https://yalaz-immo.com/health/
- [ ] Logs propres (pas d'erreurs)
- [ ] HTTPS fonctionne (pas de warning SSL)

---

## 🆘 DEPANNAGE

### "Connection refused" sur SSH

```bash
# Vérifier que le serveur est en ligne
ping VOTRE_IP_OVH

# Vérifier le port SSH (défaut 22)
ssh -p 22 root@VOTRE_IP_OVH

# Contacter OVH si serveur down
```

### "Docker command not found"

```bash
# Réinstaller Docker
curl -fsSL https://get.docker.com | sh

# Ajouter au groupe
sudo usermod -aG docker $USER
newgrp docker
```

### Les conteneurs ne démarrent pas

```bash
# Voir l'erreur détaillée
docker-compose -f docker-compose-prod-optimised.yml logs web

# Vérifier les variables .env.production
grep -v "^#" .env.production | grep -v "^$"

# Arrêter et redémarrer
docker-compose -f docker-compose-prod-optimised.yml down
docker-compose -f docker-compose-prod-optimised.yml up -d
```

### "Migration error"

```bash
# Voir l'erreur complète
docker-compose -f docker-compose-prod-optimised.yml logs web

# Réappliquer les migrations
docker-compose -f docker-compose-prod-optimised.yml exec web python manage.py migrate --noinput

# Si grave, réinitialiser (ATTENTION DATA LOSS!)
# docker-compose -f docker-compose-prod-optimised.yml down -v
```

### "Email not working"

```bash
# Tester la connexion SMTP
docker-compose -f docker-compose-prod-optimised.yml exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test email', 'from@example.com', ['to@example.com'])
# Devrait retourner 1 si OK
```

### Certificat SSL expiré

```bash
# Renouveler manuellement
docker-compose -f docker-compose-prod-optimised.yml exec certbot certbot renew --force-renewal

# Redémarrer nginx
docker-compose -f docker-compose-prod-optimised.yml restart nginx
```

---

## 📞 SUPPORT

Pour toute question ou bug:
1. Vérifier les logs: `docker-compose logs`
2. Consulter DEPLOYMENT.md pour plus de détails
3. Vérifier la configuration .env.production
4. Redémarrer: `docker-compose down && docker-compose up -d`

**Domaine en production:** https://yalaz-immo.com  
**Admin:** https://yalaz-immo.com/admin/  
**Health:** https://yalaz-immo.com/health/
