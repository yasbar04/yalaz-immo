import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aylaz.settings')


def pytest_configure():
    """Configure pytest with Django settings."""
    if not settings.configured:
        django.setup()


# Fixtures can be defined here and reused across all tests
import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def django_user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Create a test admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def client():
    """Return Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, django_user):
    """Return authenticated test client."""
    client.login(username='testuser', password='testpass123')
    return client
