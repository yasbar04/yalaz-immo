#!/bin/bash
set -e

# Post-deployment setup script
# Run this after successful deployment to production

echo "🚀 Post-Deployment Setup"
echo "========================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in docker container
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please run this inside the Django container.${NC}"
    exit 1
fi

echo -e "${YELLOW}📝 Creating admin user...${NC}"
python manage.py createsuperuser

echo -e "${YELLOW}🗄️  Running migrations...${NC}"
python manage.py migrate

echo -e "${YELLOW}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear

echo -e "${YELLOW}🧪 Running health checks...${NC}"
python manage.py shell << EOF
from django.db import connection
from django.core.cache import cache

# Test database
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("${GREEN}✅ Database connection OK${NC}")
except Exception as e:
    print(f"${RED}❌ Database connection failed: {e}${NC}")

# Test cache
try:
    cache.set('health_check', 'ok', 10)
    cache.get('health_check')
    print("${GREEN}✅ Cache (Redis) OK${NC}")
except Exception as e:
    print(f"${YELLOW}⚠️  Cache not available: {e}${NC}")

# Test email
from django.core.mail import send_mail
try:
    send_mail(
        'Test Email from Aylaz',
        'If you received this, email is working correctly!',
        'noreply@aylaz.local',
        ['admin@example.com'],
        fail_silently=True,
    )
    print("${GREEN}✅ Email backend OK${NC}")
except Exception as e:
    print(f"${YELLOW}⚠️  Email test: {e}${NC}")
EOF

echo ""
echo -e "${GREEN}✅ Post-deployment setup completed!${NC}"
echo ""
echo "📝 Next steps:"
echo "1. Access admin panel: https://your-domain.com/admin/"
echo "2. Create content/listings"
echo "3. Test API endpoints"
echo "4. Verify email notifications"
echo "5. Monitor Sentry for errors"
echo ""
