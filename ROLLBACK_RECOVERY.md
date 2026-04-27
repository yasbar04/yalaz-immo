# 🔄 Rollback & Recovery Guide

## Scénarios de Récupération

### Scenario 1: Migrations cassées

**Problème**: Migration appliquée mais génère une erreur

```bash
# 1. Identifier la migration problématique
migrations list

# 2. Rollback la dernière migration
python manage.py migrate app_name 0XXX  # version précédente

# 3. Fixer la migration
# - Éditer la migration
# - Tests complets

# 4. Re-appliquer
python manage.py migrate
```

### Scenario 2: Data corruption

**Problème**: Données corrompues après une opération

```bash
# 1. Restaurer depuis le dernier backup
bash scripts/backup.sh list  # voir les backups

# 2. Arrêter l'application
docker-compose down

# 3. Restaurer database
gunzip < /backups/aylaz/db_YYYYMMDD_HHMMSS.sql.gz | \
  psql -U aylaz_user aylaz

# 4. Redémarrer
docker-compose up -d
```

### Scenario 3: Application crash complet

**Problème**: App devient inaccessible

```bash
# 1. Aller au commit qu'on sait qui marche
git log --oneline | head -20
git revert HEAD~2  # ou git reset

# 2. Rebuild Docker image
docker build -t aylaz:latest .

# 3. Restart containers
docker-compose restart web

# 4. Vérifier
curl http://localhost/health/
```

### Scenario 4: Database n'est pas accessible

**Problème**: PostgreSQL down

```bash
# 1. Vérifier container
docker ps | grep postgres

# 2. Checker logs
docker logs aylaz-db

# 3. Restart database
docker restart aylaz-db

# 4. Attendre que ça démarre
# Prendre 10-15 secondes

# 5. Verify connection
docker-compose exec db psql -U aylaz_user -d aylaz -c "SELECT 1"
```

### Scenario 5: Disk space full

**Problème**: Serveur à court d'espace disque

```bash
# 1. Cleanup old logs
find /app/logs -name "*.log" -mtime +30 -delete

# 2. Cleanup Docker images
docker image prune -a

# 3. Cleanup Docker volumes
docker volume prune

# 4. Cleanup temporary files
rm -rf /tmp/*

# 5. Check remaining space
df -h
```

### Scenario 6: Memory leak

**Problème**: RAM augmente constamment

```bash
# 1. Monitorer
docker stats

# 2. Identifier le processus
ps aux | sort -nrk 3,3 | head

# 3. Redémarrer le service
docker restart aylaz-web

# 4. Si ça revient: vérifier les logs
docker logs -f aylaz-web 2>&1 | grep -i memory
```

### Scenario 7: Deployment failed mid-way

**Problème**: Déploiement interrompu

```bash
# 1. Vérifier status
docker-compose ps

# 2. Voir les erreurs
docker-compose logs web

# 3. Cleanup & restart
docker-compose down
docker compose rm -f  # Force remove

# 4. Re-run deployment
bash scripts/deploy.sh production

# NB: Containers vont redownload et restart clean
```

## Stratégie de Backup

### Automated Backups
```bash
# Ajouter au crontab pour automatiser
0 2 * * * cd /home/aylaz-app && /bin/bash scripts/backup.sh all

# Vérifier le cron
crontab -l
```

### Manual Backup
```bash
# Database only
docker-compose exec -T db pg_dump -U aylaz_user aylaz | gzip > backup.sql.gz

# Full backup (data + media)
tar -czf backup_$(date +%Y%m%d).tar.gz media/ logs/
```

### Restore from Backup
```bash
# From SQL backup
gunzip < backup.sql.gz | \
  docker-compose exec -T db psql -U aylaz_user aylaz

# From full backup
tar -xzf backup_20240101.tar.gz
```

## Monitoring pour Prévention

```bash
# Setup alerts pour:
- [ ] Disk usage > 80%
- [ ] Memory usage > 90%
- [ ] CPU usage > 95%
- [ ] Database connection errors
- [ ] Application error rate > 1%
- [ ] Response time > 1s
- [ ] Sentry errors > threshold
```

## Version Control Rollback

```bash
# Voir l'historique
git log --oneline

# Rollback
git revert COMMIT_HASH

# ou reset (⚠️ destructive)
git reset --hard COMMIT_HASH

# Push
git push origin main
```

## Zero-Downtime Deployment

```bash
# 1. Health check en place
curl http://localhost/health/

# 2. New version with rolling update
docker-compose up -d --no-deps --build web

# 3. Vérifier avant de terminer l'old
sleep 10
curl http://localhost/health/

# 4. Old container terminé auto
# (par docker-compose)
```

## Test Disaster Recovery

**Important**: Tester RÉGULIÈREMENT!

```bash
# 1. Restore from backup dans environnement de test
# 2. Vérifier que data est intact
# 3. Vérifier les services marchent
# 4. Documenter les résultats

# Schedule mensuel:
0 3 1 * * /home/aylaz-app/scripts/test-recovery.sh
```

## Checklist pour Gestion de Crise

- [ ] Identifier le problème exactement
- [ ] Notifier le team
- [ ] Ne pas paniquer - vérifier les logs
- [ ] Tester la solution en dev d'abord
- [ ] Faire backup avant modification
- [ ] Exécuter avec confirmation
- [ ] Monitorer après le fix
- [ ] Post-mortem si incident majeur
- [ ] Documenter la leçon

---

**Remember**: Un backup testé = Un backup utile!
Un plan documenté = Récupération rapide!
