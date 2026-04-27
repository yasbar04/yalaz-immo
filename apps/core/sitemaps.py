from django.views.generic import TemplateView
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Q
from apps.listings.models import Listing
import json
from urllib.parse import urljoin


class SitemapView(TemplateView):
    """Generate XML sitemap for search engines"""
    content_type = 'application/xml'
    template_name = 'sitemaps/sitemap.xml'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        base_url = f"{self.request.scheme}://{self.request.get_host()}"
        
        # Static pages
        static_pages = [
            {'url': reverse('home'), 'priority': '1.0', 'changefreq': 'daily'},
            {'url': reverse('listing_list'), 'priority': '0.9', 'changefreq': 'hourly'},
            {'url': reverse('buy'), 'priority': '0.9', 'changefreq': 'daily'},
            {'url': reverse('rent'), 'priority': '0.9', 'changefreq': 'daily'},
            {'url': reverse('sell'), 'priority': '0.8', 'changefreq': 'weekly'},
            {'url': reverse('estimate'), 'priority': '0.8', 'changefreq': 'weekly'},
            {'url': reverse('about'), 'priority': '0.7', 'changefreq': 'monthly'},
        ]
        
        # Dynamic listings
        listings = Listing.objects.filter(status='published').values('pk', 'updated_at')
        
        urls = []
        for page in static_pages:
            urls.append({
                'loc': urljoin(base_url, page['url']),
                'lastmod': '',
                'priority': page['priority'],
                'changefreq': page['changefreq'],
            })
        
        for listing in listings:
            urls.append({
                'loc': urljoin(base_url, reverse('listing_detail', kwargs={'pk': listing['pk']})),
                'lastmod': listing['updated_at'].isoformat(),
                'priority': '0.8',
                'changefreq': 'weekly',
            })
        
        context['urls'] = urls
        return context


class SitemapListingsView(TemplateView):
    """Generate XML sitemap for listings (large dataset support)"""
    content_type = 'application/xml'
    template_name = 'sitemaps/sitemap-listings.xml'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        base_url = f"{self.request.scheme}://{self.request.get_host()}"
        
        # Get all published listings
        listings = Listing.objects.filter(status='published').values('pk', 'updated_at', 'listing_type', 'city')
        
        urls = []
        for listing in listings:
            urls.append({
                'loc': urljoin(base_url, reverse('listing_detail', kwargs={'pk': listing['pk']})),
                'lastmod': listing['updated_at'].isoformat(),
                'priority': '0.8',
                'changefreq': 'weekly',
                'listing_type': listing['listing_type'],
                'city': listing['city'],
            })
        
        context['urls'] = urls
        return context


class SitemapIndexView(TemplateView):
    """Generate sitemap index for multiple sitemaps"""
    content_type = 'application/xml'
    template_name = 'sitemaps/sitemap-index.xml'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        base_url = f"{self.request.scheme}://{self.request.get_host()}"
        
        sitemaps = [
            {'url': urljoin(base_url, '/sitemap.xml')},
            {'url': urljoin(base_url, '/sitemap-listings.xml')},
        ]
        
        context['sitemaps'] = sitemaps
        return context
