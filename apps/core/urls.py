from django.urls import path
from django.views.generic import TemplateView
from .views import (
    home, about, buy, rent, estimate, sell, contact,
    financial_dashboard, financial_stats_api, estimate_track_api,
    FinancialTransactionListView, FinancialTransactionCreateView,
    FinancialTransactionUpdateView, FinancialTransactionDeleteView,
    FinancialTransactionDetailView,
    mentions_legales, politique_confidentialite, politique_cookies, cgu,
    cron_recurring_transactions,
)
from .analytics_views import analytics_dashboard
from .sitemaps import SitemapView, SitemapListingsView, SitemapIndexView
from .health import health_check
from .seo_views import city_listing

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('buy/', buy, name='buy'),
    path('rent/', rent, name='rent'),
    path('estimate/', estimate, name='estimate'),
    path('sell/', sell, name='sell'),
    path('contact/', contact, name='contact'),
    path('health/', health_check, name='health_check'),
    
    # Transactions financières (staff uniquement)
    path('finances/', financial_dashboard, name='financial_dashboard'),
    path('finances/transactions/', FinancialTransactionListView.as_view(), name='financial_transactions_list'),
    path('finances/transactions/new/', FinancialTransactionCreateView.as_view(), name='financial_transaction_create'),
    path('finances/transactions/<int:pk>/', FinancialTransactionDetailView.as_view(), name='financial_transaction_detail'),
    path('finances/transactions/<int:pk>/edit/', FinancialTransactionUpdateView.as_view(), name='financial_transaction_update'),
    path('finances/transactions/<int:pk>/delete/', FinancialTransactionDeleteView.as_view(), name='financial_transaction_delete'),
    path('api/finances/stats/', financial_stats_api, name='financial_stats_api'),
    path('api/estimate/track/', estimate_track_api, name='estimate_track_api'),
    path('superadmin/analytics/', analytics_dashboard, name='analytics_dashboard'),
    
    # Pages légales
    path('mentions-legales/', mentions_legales, name='mentions_legales'),
    path('confidentialite/', politique_confidentialite, name='politique_confidentialite'),
    path('cookies/', politique_cookies, name='politique_cookies'),
    path('cgu/', cgu, name='cgu'),
    path('internal/cron/recurring/', cron_recurring_transactions, name='cron_recurring_transactions'),

    # Sitemaps
    path('sitemap.xml', SitemapView.as_view(), name='sitemap'),
    path('sitemap-listings.xml', SitemapListingsView.as_view(), name='sitemap_listings'),
    path('sitemap-index.xml', SitemapIndexView.as_view(), name='sitemap_index'),

    # llms.txt — AI search discoverability (ChatGPT, Perplexity, Claude)
    path('llms.txt', TemplateView.as_view(template_name='llms.txt', content_type='text/plain'), name='llms_txt'),

    # Pages SEO programmatiques par ville et type
    # Chemins EXPLICITES acheter/ et louer/ pour éviter tout conflit avec listings/
    path('acheter/<slug:city_slug>/', city_listing, {'action_slug': 'acheter'}, name='city_listing_acheter'),
    path('acheter/<slug:city_slug>/<slug:type_slug>/', city_listing, {'action_slug': 'acheter'}, name='city_listing_acheter_type'),
    path('louer/<slug:city_slug>/', city_listing, {'action_slug': 'louer'}, name='city_listing_louer'),
    path('louer/<slug:city_slug>/<slug:type_slug>/', city_listing, {'action_slug': 'louer'}, name='city_listing_louer_type'),
]

