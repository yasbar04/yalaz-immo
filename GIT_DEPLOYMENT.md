# 🚀 DEPLOYMENT SUR GIT - GUIDE RAPIDE

## 📝 AVANT DE COMMENCER

Assurez-vous que:
- ✅ Git est installé: `git --version`
- ✅ Vous avez un repository Git (GitHub, GitLab, Gitea, etc.)
- ✅ Vous avez configuré Git localement:
  ```bash
  git config --global user.name "Votre Nom"
  git config --global user.email "votre-email@gmail.com"
  ```

---

## 🎯 ETAPES RAPIDES

### ETAPE 1: Naviguer dans le dossier du projet

```bash
cd "c:\Users\kikib\OneDrive\Documents\Projet perso\aylaz"
```

### ETAPE 2: Initialiser Git (si pas déjà fait)

```bash
# Vérifier si Git est déjà initialisé
git status

# Si erreur "not a git repository", initialiser:
git init
```

### ETAPE 3: Ajouter votre repository distant (si pas déjà fait)

```bash
# Ajouter l'URL de votre repository
git remote add origin https://github.com/VOTRE_USER/aylaz.git

# Ou si vous l'avez déjà, vérifier:
git remote -v
# Devrait afficher: origin https://github.com/VOTRE_USER/aylaz.git
```

### ETAPE 4: Vérifier le .gitignore

```bash
# Ouvrir .gitignore pour vérifier qu'il exclut les fichiers sensibles
cat .gitignore

# Doit contenir:
# .env.production (pas d'upload des secrets!)
# db.sqlite3
# __pycache__/
# *.pyc
# venv/
# media/volumes_data/
```

### ETAPE 5: Pusher le code sur Git

```bash
# Ajouter tous les fichiers
git add .

# Faire un commit
git commit -m "🚀 Deployment Aylaz avec guides Docker et FileZilla
- Configuration production (.env.production)
- Nginx optimisé (nginx-prod.conf)
- Docker Compose complet (docker-compose-prod-optimised.yml)
- Script de déploiement automatisé
- Guides de déploiement (Docker, FileZilla, FTP)
- Checklist pré-déploiement
- Documentation complète"

# Pousser vers GitHub/GitLab
git push -u origin main
# Ou si votre branche s'appelle 'master':
git push -u origin master
```

### ETAPE 6: Vérifier sur GitHub

1. Aller sur **github.com/VOTRE_USER/aylaz**
2. Vérifier que tous les fichiers sont là
3. Vérifier que `.env.production` n'est PAS visible (doit être dans .gitignore)

---

## 📋 FICHIERS A POUSSER

✅ À POUSSER:
```
✅ apps/
✅ aylaz/
✅ templates/
✅ static/
✅ scripts/
✅ manage.py
✅ requirements.txt
✅ requirements-prod.txt
✅ Dockerfile
✅ nginx-prod.conf
✅ docker-compose-prod-optimised.yml
✅ .env.production.example (template sans secrets)
✅ PRE_DEPLOYMENT_CHECKLIST.md
✅ DEPLOYMENT_QUICK_START.md
✅ DEPLOYMENT_FILEZILLA.md
✅ DEPLOYMENT_OVH.md
✅ START_HERE.md
✅ README.md
✅ .gitignore
```

❌ À NE PAS POUSSER (dans .gitignore):
```
❌ .env.production (secrets!)
❌ db.sqlite3 (vieille BD)
❌ __pycache__/
❌ *.pyc
❌ media/ (fichiers uploadés par users)
❌ logs/ (fichiers de logs)
❌ venv/ (virtualenv)
❌ .vscode/workspace.json (si vous en avez)
```

---

## ✅ VERIFICATION .gitignore

```bash
# Ouvrir et vérifier le contenu
nano .gitignore

# Ou l'éditer avec VS Code
code .gitignore
```

**Doit contenir:**
```gitignore
# Environment
.env
.env.production
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
venv/
ENV/
env/

# Django
db.sqlite3
/media/
/staticfiles/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Temp files
*.tmp
*.bak
~*
```

---

## 🔐 SECURITÉ: .env.production JAMAIS sur Git

**Important:** Créer `.env.production.example` (template):

```bash
# Copier le template
cp .env.production .env.production.example

# Éditer .env.production.example pour NE JAMAIS révéler les secrets
# Garder les TODO et exemples:
```

**Contenu de .env.production.example:**
```env
# Exemple - Configuration Production
# À copier vers .env.production et remplir avec VOS valeurs

DEBUG=False
SECRET_KEY=CHANGE_ME_TO_STRONG_KEY
ALLOWED_HOSTS=yalaz-immo.com,www.yalaz-immo.com
DB_PASSWORD=CHANGE_ME
REDIS_PASSWORD=CHANGE_ME
EMAIL_HOST_PASSWORD=CHANGE_ME
```

---

## 🔄 COMMANDES COMPLETE POUR PUSH

**Copier-coller cette séquence:**

```bash
# 1. Aller dans le dossier
cd "c:\Users\kikib\OneDrive\Documents\Projet perso\aylaz"

# 2. Vérifier le status
git status

# 3. Ajouter les fichiers
git add .

# 4. Vérifier avant de commit
git status
# Devrait montrer todos les fichiers en vert (added)

# 5. Faire le commit
git commit -m "🚀 Deployment files: Docker, Nginx, guides de déploiement"

# 6. Pousser vers Git (première fois)
git push -u origin main
# Ou:
git push -u origin master

# 7. Vérifier que c'est ok
echo "✅ Push completed!"
```

---

## 🚨 SI ERREUR "Permission denied"

```bash
# Vous avez besoin d'authentification

# Option 1: Token GitHub (recommandé)
# 1. Aller sur github.com/settings/tokens
# 2. Créer un token (avec permission 'repo')
# 3. Copier le token
# 4. Git va vous demander le password, coller le token

# Option 2: Clé SSH (avancé)
# 1. Générer une clé: ssh-keygen -t ed25519 -C "email@example.com"
# 2. Ajouter la clé sur GitHub
# 3. git remote set-url origin git@github.com:USER/aylaz.git
# 4. git push
```

---

## ✅ VERIFIER LE PUSH

Après le push, vérifier sur GitHub:

```bash
# Afficher le lien
echo "Accédez à votre repository:"
# Copier l'URL et vérifier que:
# - Tous les fichiers sont présents
# - .env.production N'EST PAS visible (✅ .gitignore fonctionne)
# - Les guides MD sont lisibles
```

---

## 🔗 LIEN VERS VOTRE REPO

Une fois pushé, votre repository sera à:

```
https://github.com/VOTRE_USERNAME/aylaz
```

**Plus tard, pour déployer sur le serveur OVH:**

```bash
# Sur le serveur OVH, cloner simplement:
git clone https://github.com/VOTRE_USERNAME/aylaz /var/www/aylaz
cd /var/www/aylaz

# Et copier le .env.production depuis votre fichier local:
cp /home/backup/.env.production .env.production

# Puis déployer normalement
```

---

## 📊 RESUME

| Étape | Commande | But |
|-------|----------|-----|
| **1** | `git init` | Initialiser Git |
| **2** | `git remote add origin ...` | Ajouter le repository |
| **3** | `git add .` | Ajouter tous les fichiers |
| **4** | `git commit -m "..."` | Faire un commit |
| **5** | `git push -u origin main` | Pousser sur GitHub |

---

## 🎯 APRES LE PUSH

### Pour mettre à jour le serveur OVH:

```bash
# Sur le serveur OVH:
cd /var/www/aylaz
git pull origin main  # Récupère les derniers changements
python manage.py migrate
python manage.py collectstatic
sudo systemctl restart aylaz
```

### Workflow futur (après première mise en ligne):

```bash
# Sur votre PC local (quand vous avez des changements)
git add .
git commit -m "Description des changements"
git push origin main

# Sur le serveur OVH (pour mettre à jour)
cd /var/www/aylaz
git pull
python manage.py migrate  # Si nécessaire
sudo systemctl restart aylaz
```

---

## ✨ AVANTAGES D'UTILISER GIT

✅ Versioning du code  
✅ Historique des changements  
✅ Collaboration facile  
✅ Deploiement simple (git pull)  
✅ Rollback rapide en cas de problème  
✅ CI/CD possible (GitHub Actions)  

---

**C'est bon ! Votre projet est prêt à être sur Git ! 🚀**

Après le push, vérifiez sur GitHub que tout est là et que `.env.production` N'EST PAS visible.
