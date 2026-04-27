#!/bin/bash
set -e

# Security checklist for Aylaz
# Run this before deploying to production

echo "🔒 Running security checks..."

FAILED=0

# Check 1: DEBUG is False
if grep -q "^DEBUG=True" .env; then
    echo "❌ DEBUG is enabled in .env"
    FAILED=1
fi

# Check 2: SECRET_KEY doesn't contain default
if grep -q "django-insecure" .env; then
    echo "❌ Using insecure SECRET_KEY"
    FAILED=1
fi

# Check 3: Check for hardcoded passwords or API keys
if grep -rE "(password|api_key|secret|token)\s*=\s*['\"]" apps/ --include="*.py"; then
    echo "❌ Found potential hardcoded credentials"
    FAILED=1
fi

# Check 4: Check for SQL injection patterns
if grep -rE "(raw|execute|cursor)" apps/ --include="*.py" | grep -v "test" | grep -v ".pyc"; then
    echo "⚠️  Found raw SQL queries (verify they are safe)"
fi

# Check 5: Check for debug print statements in production code
if grep -rE "print\(|pdb|ipdb" apps/ --include="*.py" | grep -v test | grep -v ".pyc"; then
    echo "⚠️  Found debug statements (remove before production)"
fi

# Check 6: Verify ALLOWED_HOSTS is not wildcard
if grep -q "ALLOWED_HOSTS.*\*" aylaz/settings.py; then
    echo "❌ ALLOWED_HOSTS contains wildcard"
    FAILED=1
fi

# Check 7: Check dependencies for known vulnerabilities
pip check

if [ $FAILED -eq 0 ]; then
    echo "✅ All security checks passed!"
else
    echo "❌ Security checks failed!"
    exit 1
fi
