#!/bin/bash

# Environment Setup Assistant
# Run this to generate a secure .env.production file

echo "🔧 Aylaz Production Environment Setup"
echo "====================================="
echo ""

# Function to generate random string
generate_random() {
    openssl rand -hex 32
}

# Check if .env.production already exists
if [ -f ".env.production" ]; then
    read -p "⚠️  .env.production already exists. Overwrite? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create .env.production from template
cp .env.production.example .env.production

# Function to prompt for value
prompt_value() {
    local key=$1
    local prompt_text=$2
    local default=$3
    
    if [ -z "$default" ]; then
        read -p "▶️  $prompt_text: " value
    else
        read -p "▶️  $prompt_text [$default]: " value
        value=${value:-$default}
    fi
    
    # Escape special characters for sed
    value=$(echo "$value" | sed 's/[&/\]/\\&/g')
    sed -i "s/^$key=.*/$key=$value/" .env.production
}

echo "⚙️  Configuration Interactive"
echo "=============================="
echo ""

# Core Django Settings
echo "📌 Django Core Settings:"
SECRET=$(generate_random)
sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET/" .env.production
echo "✓ SECRET_KEY generated ($(echo $SECRET | cut -c1-8)...)"

prompt_value "ALLOWED_HOSTS" "Domain names (comma-separated)" "localhost,127.0.0.1"
prompt_value "PLATFORM_NAME" "Platform name" "Aylaz"

# Database Settings
echo ""
echo "🗄️  Database Settings:"
prompt_value "DB_PASSWORD" "PostgreSQL password" "$(generate_random | cut -c1-16)"
prompt_value "DB_NAME" "Database name" "aylaz"
prompt_value "DB_USER" "Database user" "aylaz_user"

# Email Settings
echo ""
echo "📧 Email Settings:"
prompt_value "EMAIL_HOST" "SMTP host (SendGrid: smtp.sendgrid.net)" "smtp.sendgrid.net"
prompt_value "EMAIL_HOST_USER" "SMTP username (SendGrid: apikey)" "apikey"
prompt_value "EMAIL_HOST_PASSWORD" "SMTP password / API key" ""
prompt_value "DEFAULT_FROM_EMAIL" "Sender email address" "noreply@aylaz.local"

# Optional: SMS Settings
echo ""
echo "📱 SMS Settings (optional, press Enter to skip):"
read -p "▶️  Do you want to setup SMS? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    prompt_value "SMS_TWILIO_ACCOUNT_SID" "Twilio Account SID" ""
    prompt_value "SMS_TWILIO_AUTH_TOKEN" "Twilio Auth Token" ""
    prompt_value "SMS_TWILIO_FROM_NUMBER" "Twilio From Number" ""
fi

# Optional: Sentry Setup
echo ""
echo "🔍 Sentry Error Tracking (optional, press Enter to skip):"
read -p "▶️  Do you want to setup Sentry? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    prompt_value "SENTRY_DSN" "Sentry DSN URL" ""
fi

# Redis Setup
echo ""
echo "⚡ Redis Setup:"
REDIS_PASS=$(generate_random | cut -c1-16)
sed -i "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASS/" .env.production
echo "✓ Redis password generated"

# SSL Setup
echo ""
echo "🔒 SSL/TLS Setup:"
prompt_value "SECURE_SSL_REDIRECT" "Force HTTPS? (True/False)" "True"

echo ""
echo "✅ Configuration Complete!"
echo ""
echo "📦 Next steps:"
echo "1. Verify all values in .env.production"
echo "2. Run security check: bash scripts/security-check.sh"
echo "3. Commit (if secure): git add .env.production"
echo "4. Deploy: bash scripts/setup-prod.sh"
echo ""
echo "File: .env.production"
grep -v "^#" .env.production | head -5
echo "..."
