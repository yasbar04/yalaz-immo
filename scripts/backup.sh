#!/bin/bash
set -e

# Backup script for Aylaz
# Usage: ./scripts/backup.sh [database|all]

BACKUP_TYPE=${1:-all}
BACKUP_DIR="/backups/aylaz"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "🔄 Starting backup ($BACKUP_TYPE)..."

if [ "$BACKUP_TYPE" = "database" ] || [ "$BACKUP_TYPE" = "all" ]; then
    echo "🗄️  Backing up database..."
    docker-compose exec -T db pg_dump -U ${DB_USER} ${DB_NAME} | gzip > "$BACKUP_DIR/db_${TIMESTAMP}.sql.gz"
    echo "✅ Database backup completed"
fi

if [ "$BACKUP_TYPE" = "all" ]; then
    echo "📦 Backing up media files..."
    tar -czf "$BACKUP_DIR/media_${TIMESTAMP}.tar.gz" ./media/ 2>/dev/null || true
    echo "✅ Media backup completed"
fi

# Keep only last 7 backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed!"
echo "📁 Backups stored in: $BACKUP_DIR"

# Optional: Upload to S3 or cloud storage
# aws s3 cp "$BACKUP_DIR/db_${TIMESTAMP}.sql.gz" s3://your-bucket/backups/
