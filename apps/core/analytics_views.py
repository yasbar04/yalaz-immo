from datetime import timedelta
from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from apps.listings.models import Favorite, Listing, PublicInquiry

User = get_user_model()


def superuser_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped


@superuser_required
def analytics_dashboard(request):
    now = timezone.now()
    six_months_ago = now - timedelta(days=182)
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    total_published  = Listing.objects.filter(status=Listing.Status.PUBLISHED).count()
    total_pending    = Listing.objects.filter(status=Listing.Status.PENDING).count()
    total_views      = Listing.objects.aggregate(t=Sum('views_count'))['t'] or 0
    total_inquiries  = PublicInquiry.objects.count()
    unread_inquiries = PublicInquiry.objects.filter(is_read=False).count()
    total_favorites  = Favorite.objects.count()
    total_users      = User.objects.count()
    new_users_30d    = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    new_listings_7d  = Listing.objects.filter(created_at__gte=seven_days_ago).count()
    new_listings_30d = Listing.objects.filter(created_at__gte=thirty_days_ago).count()

    top_listings = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .order_by('-views_count')[:10]
    )
    max_views = top_listings[0].views_count if top_listings else 1

    monthly_listings = (
        Listing.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    monthly_inquiries = (
        PublicInquiry.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months = []
    for i in range(5, -1, -1):
        d = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        months.append({'month': d, 'label': d.strftime('%b'), 'listings': 0, 'inquiries': 0})

    for row in monthly_listings:
        for m in months:
            if m['month'].year == row['month'].year and m['month'].month == row['month'].month:
                m['listings'] = row['count']
    for row in monthly_inquiries:
        for m in months:
            if m['month'].year == row['month'].year and m['month'].month == row['month'].month:
                m['inquiries'] = row['count']

    max_monthly = max((m['listings'] for m in months), default=1) or 1

    cities = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .values('city')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )
    max_city = cities[0]['count'] if cities else 1

    by_property = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .values('property_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    property_labels = {v: l for v, l in Listing.PropertyType.choices}

    by_listing_type = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .values('listing_type')
        .annotate(count=Count('id'))
    )
    sale_count = next((r['count'] for r in by_listing_type if r['listing_type'] == 'sale'), 0)
    rent_count = next((r['count'] for r in by_listing_type if r['listing_type'] == 'rent'), 0)

    recent_inquiries = PublicInquiry.objects.select_related('listing').order_by('-created_at')[:8]

    context = {
        'total_published': total_published,
        'total_pending': total_pending,
        'total_views': total_views,
        'total_inquiries': total_inquiries,
        'unread_inquiries': unread_inquiries,
        'total_favorites': total_favorites,
        'total_users': total_users,
        'new_users_30d': new_users_30d,
        'new_listings_7d': new_listings_7d,
        'new_listings_30d': new_listings_30d,
        'top_listings': top_listings,
        'max_views': max_views or 1,
        'months': months,
        'max_monthly': max_monthly,
        'cities': cities,
        'max_city': max_city or 1,
        'by_property': [
            {**r, 'label': property_labels.get(r['property_type'], r['property_type'])}
            for r in by_property
        ],
        'sale_count': sale_count,
        'rent_count': rent_count,
        'recent_inquiries': recent_inquiries,
    }
    return render(request, 'admin/analytics.html', context)
