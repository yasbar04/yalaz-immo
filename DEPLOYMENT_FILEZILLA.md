# 📤 DEPLOIEMENT AVEC FILEZILLA - GUIDE SIMPLIFIE

## ⚠️ Important: FileZilla + SSH Terminal

**FileZilla** = transfert de fichiers (SFTP)  
**SSH Terminal** = exécuter les commandes  
**Vous aurez besoin des DEUX**

---

## 🚀 ETAPES DE DEPLOIEMENT FILEZILLA

### ETAPE 1: Configurer FileZilla

**Ouvrir FileZilla et créer un nouveau site:**

```
Host:       VOTRE_IP_OVH (ex: 123.45.67.89)
Protocol:   SFTP - SSH File Transfer Protocol
User:       root (ou votre utilisateur)
Password:   votre_mot_de_passe_OVH
Port:       22
```

**Ou si vous préférez une clé SSH:**
```
Host:       VOTRE_IP_OVH
Protocol:   SFTP
User:       root
Key file:   C:\chemin\vers\votre\clé\privée.pem
Port:       22
```

**Cliquer "Connect"**

### ETAPE 2: Créer l'arborescence sur le serveur

Dans FileZilla, créer ces dossiers:

```
/var/www/
    └── aylaz/
        ├── apps/
        ├── aylaz/
        ├── templates/
        ├── static/
        ├── media/
        ├── logs/
        └── scripts/
```

**Comment faire:**
1. Naviguer à `/var/www/` (panneau droit)
2. Clic droit → "Create directory" → taper "aylaz"
3. Répéter pour les sous-dossiers

### ETAPE 3: Uploader les fichiers du projet

Dans FileZilla:

**Côté gauche (local):** Naviguer vers votre dossier aylaz  
**Côté droit (serveur):** Naviguer vers `/var/www/aylaz/`

**Sélectionner et uploader:**
- Tous les fichiers `.py`
- Tous les `apps/`
- `templates/`
- `static/`
- `manage.py`
- `requirements.txt`
- `requirements-prod.txt`
- `.env.production` ← IMPORTANT!
- `nginx-prod.conf` ← IMPORTANT!
- `Dockerfile`
- `docker-compose-prod-optimised.yml`
- `scripts/`

**Ne PAS uploader:**
- `media/` (trop volumineux)
- `__pycache__/`
- `*.pyc`
- `.git/` (si vous utilisez Git)
- `db.sqlite3` (vieille BD de dev)

### ETAPE 4: Ouvrir un terminal SSH

**Dans FileZilla:**
1. Menu → "Server" → "Enter Custom Command" (ou Ctrl+T)
2. Ou utiliser **PuTTY** ou **Windows Terminal** avec SSH

```bash
ssh root@VOTRE_IP_OVH
# Entrer le mot de passe
```

### ETAPE 5: Installer les dépendances sur le serveur

Dans le terminal SSH:

```bash
# Se placer dans le dossier
cd /var/www/aylaz

# Installer Python et pip
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Créer un virtualenv
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements-prod.txt
pip install psycopg2-binary gunicorn
```

### ETAPE 6: Installer PostgreSQL et Redis

**Option A: Sur le serveur (simple)**

```bash
# Installer PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Installer Redis
sudo apt install -y redis-server

# Démarrer les services
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl enable postgresql
sudo systemctl enable redis-server

# Vérifier
sudo systemctl status postgresql
sudo systemctl status redis-server
```

**Option B: Utiliser Docker** (recommandé)

```bash
# Installer Docker
curl -fsSL https://get.docker.com | sudo sh

# Démarrer PostgreSQL en Docker
sudo docker run -d \
  --name aylaz-db \
  -e POSTGRES_DB=aylaz_prod \
  -e POSTGRES_USER=aylaz_user \
  -e POSTGRES_PASSWORD=MOT_DE_PASSE_FORT \
  -v aylaz_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine

# Démarrer Redis en Docker
sudo docker run -d \
  --name aylaz-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### ETAPE 7: Configurer la base de données

Dans le terminal:

```bash
cd /var/www/aylaz
source venv/bin/activate

# Appliquer les migrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser
# Email: admin@yalaz-immo.com
# Password: entrer un mot de passe
```

### ETAPE 8: Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### ETAPE 9: Configurer Nginx

**Uploader la config Nginx** avec FileZilla:

```bash
# Local: nginx-prod.conf
# Serveur: /etc/nginx/sites-available/aylaz
```

Dans le terminal:

```bash
# Copier la config
sudo cp /var/www/aylaz/nginx-prod.conf /etc/nginx/sites-available/aylaz

# Créer le lien
sudo ln -s /etc/nginx/sites-available/aylaz /etc/nginx/sites-enabled/

# Tester la config
sudo nginx -t

# Redémarrer
sudo systemctl restart nginx
```

### ETAPE 10: Générer le certificat SSL

```bash
# Installer Certbot
sudo apt install -y certbot python3-certbot-nginx

# Générer le certificat
sudo certbot certonly --nginx \
  -d yalaz-immo.com \
  -d www.yalaz-immo.com \
  --email admin@yalaz-immo.com \
  --agree-tos \
  --non-interactive

# Redémarrer Nginx
sudo systemctl restart nginx
```

### ETAPE 11: Lancer Gunicorn

```bash
cd /var/www/aylaz
source venv/bin/activate

# Tester Gunicorn
gunicorn --bind 0.0.0.0:8000 aylaz.wsgi:application

# Pour arrêter: Ctrl+C
```

### ETAPE 12: Configurer Gunicorn en service systemd (optionnel mais recommandé)

Créer un fichier `/etc/systemd/system/aylaz.service`:

```ini
[Unit]
Description=Aylaz Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/aylaz
Environment="PATH=/var/www/aylaz/venv/bin"
ExecStart=/var/www/aylaz/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    aylaz.wsgi:application
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

**Puis:**

```bash
# Créer le fichier (avec nano)
sudo nano /etc/systemd/system/aylaz.service
# Coller le contenu ci-dessus
# Ctrl+X, Y, Enter

# Recharger systemd
sudo systemctl daemon-reload

# Démarrer le service
sudo systemctl start aylaz
sudo systemctl enable aylaz

# Vérifier
sudo systemctl status aylaz
```

### ETAPE 13: Configurer le DNS

Chez votre registrar (OVH ou autre), ajouter:

```
A record
Domain: yalaz-immo.com
IP: VOTRE_IP_OVH

CNAME record (optionnel)
Domain: www.yalaz-immo.com
Target: yalaz-immo.com
```

Attendre 1-24h pour propagation DNS.

### ETAPE 14: Tester!

```bash
# Vérifier que tout tourne
curl https://yalaz-immo.com
curl https://yalaz-immo.com/admin/
curl https://yalaz-immo.com/health/

# Voir les logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Voir les logs Django
sudo journalctl -u aylaz -f
```

---

## 📋 CHECKLIST FILEZILLA

- [ ] FileZilla configuré et connecté au serveur OVH
- [ ] Dossiers créés sur le serveur (`/var/www/aylaz/`)
- [ ] Tous les fichiers Python uploadés
- [ ] `.env.production` uploadé et personnalisé
- [ ] `nginx-prod.conf` uploadé
- [ ] `docker-compose-prod-optimised.yml` uploadé (optionnel si pas Docker)

## 🖥️ CHECKLIST TERMINAL SSH

- [ ] SSH connecté à `/var/www/aylaz`
- [ ] Python 3 et pip installés
- [ ] virtualenv créé et activé
- [ ] Dépendances installées (`pip install -r requirements-prod.txt`)
- [ ] PostgreSQL installé/configuré
- [ ] Redis installé/configuré
- [ ] Migrations appliquées (`python manage.py migrate`)
- [ ] Superuser créé
- [ ] Fichiers statiques collectés
- [ ] Nginx configuré
- [ ] SSL certificate généré
- [ ] Gunicorn lancé/accès au service
- [ ] DNS configuré
- [ ] Site accessible en HTTPS

---

## 🔄 MISE À JOUR (après déploiement initial)

Pour mettre à jour le code:

**Avec FileZilla:**
1. Uploader les fichiers modifiés
2. Ouvrir terminal SSH
3. Exécuter:

```bash
cd /var/www/aylaz
source venv/bin/activate
python manage.py migrate  # Si changements BD
python manage.py collectstatic --noinput
sudo systemctl restart aylaz  # Redémarrer Django
sudo systemctl restart nginx    # Redémarrer Nginx
```

---

## 🆘 PROBLEMES COURANTS

### Site ne répond pas

```bash
# Vérifier que Nginx tourne
sudo systemctl status nginx

# Vérifier que Django tourne
sudo systemctl status aylaz

# Voir les erreurs Nginx
sudo tail -50 /var/log/nginx/error.log

# Voir les erreurs Django
sudo journalctl -u aylaz -n 50
```

### Erreur "Cannot connect to database"

```bash
# Vérifier PostgreSQL
sudo systemctl status postgresql

# Vérifier les identifiants dans .env.production
grep DATABASE /var/www/aylaz/.env.production

# Tester la connection
psql -h localhost -U aylaz_user -d aylaz_prod
```

### Erreur "502 Bad Gateway"

Django n'est pas en train de tourner:

```bash
# Vérifier le service
sudo systemctl status aylaz

# Relancer
sudo systemctl restart aylaz

# Voir les logs
sudo journalctl -u aylaz -f
```

### StaticFiles ne charge pas

```bash
# Collecter les fichiers
cd /var/www/aylaz
source venv/bin/activate
python manage.py collectstatic --noinput

# Vérifier que Nginx pointe au bon endroit
grep "location /static" /etc/nginx/sites-available/aylaz
# Devrait montrer: alias /var/www/aylaz/staticfiles/;
```

---

## 📊 ARCHITECTURE FINALE

```
Internet (HTTPS)
  ↓
Nginx (port 80/443)
  ← nginx-prod.conf
  ↓
Gunicorn (port 8000)
  ← service systemd
  ↓
  ├─ PostgreSQL (port 5432)
  └─ Redis (port 6379)
```

---

## 💾 BACKUP REGULIER

Créer un script `/home/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/backups"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR

# Backup DB
sudo -u postgres pg_dump -d aylaz_prod > $BACKUP_DIR/db-$DATE.sql

# Backup files
tar -czf $BACKUP_DIR/files-$DATE.tar.gz /var/www/aylaz/media/

echo "Backup complété: $DATE"
```

**Ajouter au cron:**
```bash
sudo crontab -e
# Ajouter: 0 2 * * * bash /home/backup.sh
```

---

## ✅ C'EST BON!

Vous pouvez maintenant:
1. Uploader les fichiers avec **FileZilla**
2. Exécuter les commandes avec **SSH Terminal**
3. Avoir un site 100% fonctionnel en production

**Avantages FileZilla:**
- Simple pour transférer les fichiers
- Interface graphique

**Inconvénients:**
- Plus lent que Git pour les mises à jour
- Nécessite SSH pour les commandes
- Pas d'automatisation

**Alternative:** Utiliser Git sur le serveur (plus professionnel)
```bash
git clone votre-repo /var/www/aylaz
git pull  # pour mettre à jour
```

Bonne chance ! 🚀
