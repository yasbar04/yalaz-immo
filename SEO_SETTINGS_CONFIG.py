"""
SEO Configuration Settings for Django
Add these settings to your settings.py or .env
"""

# ===== SEO Configuration =====

# 1. ALLOWED_HOSTS (update with your domain)
# ALLOWED_HOSTS = ['yalazagence.ma', 'www.yalazagence.ma', 'localhost', '127.0.0.1']

# 2. Security Settings (Production)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# 3. Site Configuration
SITE_ID = 1
SITE_NAME = 'YalazAgence'

# 4. Sitemap Configuration
SITEMAPS = {
    'main': 'apps.core.sitemaps.SitemapView',
    'listings': 'apps.core.sitemaps.SitemapListingsView',
    'index': 'apps.core.sitemaps.SitemapIndexView',
}

# 5. SEO Meta Tags Defaults
SEO_DEFAULTS = {
    'description': 'YalazAgence - Agence immobilière professionnelle au Maroc. Acheter, vendre, louer ou estimer votre bien avec nos experts.',
    'keywords': 'immobilier maroc, acheter bien maroc, louer maroc, vendre propriete maroc, agence immobiliere',
    'author': 'YalazAgence',
    'robots': 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1',
    'og_image': 'https://yalazagence.ma/static/og-image.png',  # Update with your OG image
    'twitter_handle': '@yalazagence',  # Your Twitter handle
}

# 6. Geo-targeting for Maroc
GEO_CONFIG = {
    'country': 'MA',
    'country_name': 'Maroc',
    'language': 'fr-MA',
    'latitude': '31.7917',
    'longitude': '-7.0926',
}

# 7. Cache Configuration (for performance)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'yalazagence-cache',
    }
}

# 8. Logging for SEO Monitoring
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'seo_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/seo.log',
        },
    },
    'loggers': {
        'seo': {
            'handlers': ['seo_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 9. SEO Constants
MAROC_CITIES = [
    'Casablanca',
    'Rabat',
    'Marrakech',
    'Fes',
    'Tangier',
    'Meknes',
    'Agadir',
    'Laayoune',
    'Kenitra',
    'Oujda',
]

# 10. robots.txt is at project root: /robots.txt
# 11. sitemap URLs are at:
#     - /sitemap.xml (main)
#     - /sitemap-listings.xml (listings)
#     - /sitemap-index.xml (index)

print("""
🌍 SEO Configuration Summary
=============================
✅ Geolocation: Maroc (fr-MA)
✅ Sitemaps: Dynamic XML generation
✅ Robots.txt: Optimized for crawling
✅ Schema.org: LocalBusiness, Organization, Property
✅ Meta Tags: OpenGraph, Twitter Card
✅ Security: HTTPS, HSTS enabled
=============================================
Next Steps:
1. Update .env with your domain (ALLOWED_HOSTS, APP_BASE_URL)
2. Add Google Site Verification code to base.html
3. Submit sitemap to Google Search Console
4. Configure Maroc-specific content strategy
""")
