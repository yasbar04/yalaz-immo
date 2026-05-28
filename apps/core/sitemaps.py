from datetime import date
from django.views.generic import TemplateView
from django.urls import reverse
from apps.listings.models import Listing
from urllib.parse import urljoin
from .seo_views import get_all_city_type_urls


class SitemapView(TemplateView):
    """Generate XML sitemap for search engines"""
    content_type = 'application/xml'
    template_name = 'sitemaps/sitemap.xml'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_url = f"{self.request.scheme}://{self.request.get_host()}"
        today = date.today().isoformat()

        static_pages = [
            {'url': reverse('home'), 'priority': '1.0', 'changefreq': 'daily', 'lastmod': today},
            {'url': reverse('listing_list'), 'priority': '0.9', 'changefreq': 'hourly', 'lastmod': today},
            {'url': reverse('buy'), 'priority': '0.9', 'changefreq': 'daily', 'lastmod': today},
            {'url': reverse('rent'), 'priority': '0.9', 'changefreq': 'daily', 'lastmod': today},
            {'url': reverse('sell'), 'priority': '0.8', 'changefreq': 'weekly', 'lastmod': today},
            {'url': reverse('estimate'), 'priority': '0.8', 'changefreq': 'weekly', 'lastmod': today},
            {'url': reverse('about'), 'priority': '0.7', 'changefreq': 'monthly', 'lastmod': today},
            {'url': reverse('contact'), 'priority': '0.6', 'changefreq': 'monthly', 'lastmod': today},
        ]

        urls = []
        for page in static_pages:
            urls.append({
                'loc': urljoin(base_url, page['url']),
                'lastmod': page['lastmod'],
                'priority': page['priority'],
                'changefreq': page['changefreq'],
            })

        # Pages SEO programmatiques par ville+type
        for city_type_url in get_all_city_type_urls():
            urls.append({
                'loc': urljoin(base_url, city_type_url),
                'lastmod': today,
                'priority': '0.85',
                'changefreq': 'daily',
            })

        # Dynamic listings (with slug-based canonical URLs)
        listings = Listing.objects.filter(status='published').values('pk', 'slug', 'updated_at')
        for listing in listings:
            if listing['slug']:
                loc = urljoin(base_url, reverse('listing_detail', kwargs={'pk': listing['pk'], 'slug': listing['slug']}))
            else:
                loc = urljoin(base_url, reverse('listing_detail_pk', kwargs={'pk': listing['pk']}))
            urls.append({
                'loc': loc,
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

        listings = Listing.objects.filter(status='published').values('pk', 'slug', 'updated_at', 'listing_type', 'city')
        urls = []
        for listing in listings:
            if listing['slug']:
                loc = urljoin(base_url, reverse('listing_detail', kwargs={'pk': listing['pk'], 'slug': listing['slug']}))
            else:
                loc = urljoin(base_url, reverse('listing_detail_pk', kwargs={'pk': listing['pk']}))
            urls.append({
                'loc': loc,
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
        context['sitemaps'] = [
            {'url': urljoin(base_url, '/sitemap.xml')},
            {'url': urljoin(base_url, '/sitemap-listings.xml')},
        ]
        return context
