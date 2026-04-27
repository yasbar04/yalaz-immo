from django.urls import path
from .views import (
    home, about, buy, rent, estimate, sell, contact,
    financial_dashboard, financial_stats_api,
    FinancialTransactionListView, FinancialTransactionCreateView,
    FinancialTransactionUpdateView, FinancialTransactionDeleteView,
    FinancialTransactionDetailView,
)
from .sitemaps import SitemapView, SitemapListingsView, SitemapIndexView
from .health import health_check

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
    
    # Sitemaps
    path('sitemap.xml', SitemapView.as_view(), name='sitemap'),
    path('sitemap-listings.xml', SitemapListingsView.as_view(), name='sitemap_listings'),
    path('sitemap-index.xml', SitemapIndexView.as_view(), name='sitemap_index'),
]

