# 🚀 GUIDE DE DEPLOIEMENT - AYLAZ SUR OVH

## 1️⃣ PREPARATION INITIALE (VPS OVH)

### A. Connexion au serveur OVH
```bash
ssh root@your-server-ip
# ou avec votre utilisateur OVH
ssh your-user@your-server-ip
```

### B. Mise à jour du système
```bash
apt update && apt upgrade -y
apt install -y curl wget git htop
```

### C. Installation de Docker et Docker Compose
```bash
# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Vérifier Docker
docker --version
docker run hello-world

# Installer Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### D. Installation de PostgreSQL et Redis (optionnel si dans Docker)
```bash
# Option 1: Sur le serveur
apt install -y postgresql postgresql-contrib redis-server

# Vérifier
sudo systemctl status postgresql
sudo systemctl status redis-server

# Option 2: Utiliser les images Docker (recommandé)
# Voir la section Docker Compose plus bas
```

---

## 2️⃣ CLONER LE PROJET

```bash
cd /var/www
git clone https://votre-repo.git aylaz
cd aylaz
```

---

## 3️⃣ CONFIGURATION PRODUCTION

### A. Créer le fichier .env.production
```bash
nano .env.production
```

**Copier ce contenu et PERSONNALISER :**
```
DEBUG=False
SECRET_KEY=VOTRE_SECRET_KEY_TRES_LONG_ET_ALEATOIRE_50_CARACTERES_MINIMUM
ALLOWED_HOSTS=yalaz-immo.com,www.yalaz-immo.com
CSRF_TRUSTED_ORIGINS=https://yalaz-immo.com,https://www.yalaz-immo.com
APP_BASE_URL=https://yalaz-immo.com

# Base de données
DATABASE_URL=postgresql://aylaz_user:PASSWORD_FORT@db:5432/aylaz_prod
DATABASE_NAME=aylaz_prod
DATABASE_USER=aylaz_user
DATABASE_PASSWORD=PASSWORD_FORT
DATABASE_HOST=db
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password
DEFAULT_FROM_EMAIL=noreply@yalaz-immo.com
```

**Générer une SECRET_KEY robuste :**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### B. Créer les répertoires de logs
```bash
sudo mkdir -p /var/log/aylaz
sudo chmod 755 /var/log/aylaz
```

---

## 4️⃣ CONFIGURATION NGINX

### A. Copier la config Nginx
```bash
sudo cp nginx.conf /etc/nginx/sites-available/aylaz
sudo ln -s /etc/nginx/sites-available/aylaz /etc/nginx/sites-enabled/

# Vérifier la syntaxe
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

### B. SSL Certificate avec Let's Encrypt
```bash
sudo apt install -y certbot python3-certbot-nginx

# Générer le certificat
sudo certbot certonly --nginx -d yalaz-immo.com -d www.yalaz-immo.com

# Vérifier le renouvellement automatique
sudo systemctl status certbot.timer
```

---

## 5️⃣ DEPLOIEMENT AVEC DOCKER COMPOSE

### A. Services Docker (Production)
```bash
# Démarrer les services
docker-compose -f docker-compose.prod.yml up -d

# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs -f

# Vérifier les services
docker-compose -f docker-compose.prod.yml ps
```

### B. Migrations et Setup initial
```bash
# Créer les tables
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Créer un superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collecter les fichiers statiques
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 6️⃣ CONFIGURATION DU DOMAINE

### A. DNS (chez OVH ou votre registrar)
Ajouter les enregistrements A :
```
Domaine: yalaz-immo.com
Type: A
Cible: VOTRE_IP_SERVEUR

Domaine: www.yalaz-immo.com
Type: CNAME
Cible: yalaz-immo.com
```

### B. Vérifier
```bash
nslookup yalaz-immo.com
dig yalaz-immo.com
```

---

## 7️⃣ MONITORING & LOGS

### A. Vérifier l'application
```bash
# Logs Django
docker-compose -f docker-compose.prod.yml logs web

# Logs Nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Vérifier la santé
curl https://yalaz-immo.com/health/
```

### B. Sauvegardes automatiques
```bash
# Éditer le cron
sudo crontab -e

# Ajouter :
0 2 * * * cd /var/www/aylaz && bash scripts/backup.sh
```

---

## 8️⃣ MISE À JOUR ET MAINTENANCE

### A. Déployer une nouvelle version
```bash
cd /var/www/aylaz
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### B. Redémarrer après erreur
```bash
docker-compose -f docker-compose.prod.yml restart
```

### C. Voir l'utilisation des ressources
```bash
docker stats
docker-compose -f docker-compose.prod.yml ps
```

---

## 9️⃣ VARIABLES IMPORTANTES À CHANGER

- ❌ `SECRET_KEY` - Générer une nouvelle clé
- ❌ `DATABASE_PASSWORD` - Mettre un mot de passe fort
- ❌ `EMAIL_HOST_USER` et `EMAIL_HOST_PASSWORD`
- ❌ `ALLOWED_HOSTS` - Votre domaine exact
- ✅ `DEBUG=False` - TOUJOURS False en production

---

## 🔟 DEPANNAGE

### Site pas accessible
```bash
# Vérifier Nginx
sudo systemctl status nginx
sudo nginx -t

# Vérifier les conteneurs
docker-compose -f docker-compose.prod.yml ps

# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs web
```

### Erreur de connexion DB
```bash
# Vérifier PostgreSQL
docker-compose -f docker-compose.prod.yml logs db

# Réinitialiser la DB
docker-compose -f docker-compose.prod.yml exec db psql -U aylaz_user -d aylaz_prod
```

### Port déjà utilisé
```bash
# Trouver le processus
sudo lsof -i :8000
sudo lsof -i :5432

# Arrêter Docker complètement
docker-compose -f docker-compose.prod.yml down
docker system prune
```

---

## ✅ CHECKLIST FINAL

- [ ] Serveur OVH accéssible par SSH
- [ ] Docker et Docker Compose installés
- [ ] Git clonné
- [ ] Fichier .env.production configuré
- [ ] Secret key changée
- [ ] Nginx configuré
- [ ] SSL certificate généré
- [ ] DNS pointé vers le serveur
- [ ] Conteneurs Docker démarrés
- [ ] Migrations exécutées
- [ ] Superuser créé
- [ ] Site accessible à https://yalaz-immo.com
- [ ] Admin accessible à https://yalaz-immo.com/admin/
- [ ] Logs OK

---

**Besoin d'aide ? Consultez DEPLOYMENT.md pour plus de détails.**
