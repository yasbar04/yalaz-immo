from datetime import timedelta
from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import localtime

from apps.listings.models import Favorite, Listing, PublicInquiry
from .models import EstimateEvent

User = get_user_model()

PERIOD_CONFIG = {
    '24h': {'days': 1,   'label': '24 dernières heures', 'trunc': 'day',   'n_bars': 2},
    '48h': {'days': 2,   'label': '48 dernières heures', 'trunc': 'day',   'n_bars': 3},
    '7d':  {'days': 7,   'label': '7 derniers jours',    'trunc': 'day',   'n_bars': 7},
    '30d': {'days': 30,  'label': '30 derniers jours',   'trunc': 'day',   'n_bars': 30},
    '6m':  {'days': 182, 'label': '6 derniers mois',     'trunc': 'month', 'n_bars': 6},
    '1y':  {'days': 365, 'label': '12 derniers mois',    'trunc': 'month', 'n_bars': 12},
}

PERIODS_NAV = [
    {'key': '24h', 'label': '24h'},
    {'key': '48h', 'label': '48h'},
    {'key': '7d',  'label': '7j'},
    {'key': '30d', 'label': '30j'},
    {'key': '6m',  'label': '6 mois'},
    {'key': '1y',  'label': '1 an'},
]


def superuser_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped


def _build_bars(trunc, n_bars, now, since):
    local_now = localtime(now)

    if trunc == 'day':
        bars = []
        for i in range(n_bars - 1, -1, -1):
            d = (local_now - timedelta(days=i)).date()
            bars.append({'key': d, 'label': d.strftime('%d/%m'), 'listings': 0, 'inquiries': 0})

        rows_l = (
            Listing.objects.filter(created_at__gte=since)
            .annotate(day=TruncDay('created_at'))
            .values('day').annotate(count=Count('id')).order_by('day')
        )
        rows_i = (
            PublicInquiry.objects.filter(created_at__gte=since)
            .annotate(day=TruncDay('created_at'))
            .values('day').annotate(count=Count('id')).order_by('day')
        )
        for row in rows_l:
            rd = localtime(row['day']).date()
            for b in bars:
                if b['key'] == rd:
                    b['listings'] = row['count']
        for row in rows_i:
            rd = localtime(row['day']).date()
            for b in bars:
                if b['key'] == rd:
                    b['inquiries'] = row['count']
    else:
        local_first = local_now.replace(day=1)
        bars = []
        for i in range(n_bars - 1, -1, -1):
            d = (local_first - timedelta(days=i * 30)).replace(day=1)
            bars.append({'key': d, 'label': d.strftime('%b'), 'listings': 0, 'inquiries': 0})

        rows_l = (
            Listing.objects.filter(created_at__gte=since)
            .annotate(month=TruncMonth('created_at'))
            .values('month').annotate(count=Count('id')).order_by('month')
        )
        rows_i = (
            PublicInquiry.objects.filter(created_at__gte=since)
            .annotate(month=TruncMonth('created_at'))
            .values('month').annotate(count=Count('id')).order_by('month')
        )
        for row in rows_l:
            lm = localtime(row['month'])
            for b in bars:
                if b['key'].year == lm.year and b['key'].month == lm.month:
                    b['listings'] = row['count']
        for row in rows_i:
            lm = localtime(row['month'])
            for b in bars:
                if b['key'].year == lm.year and b['key'].month == lm.month:
                    b['inquiries'] = row['count']

    return bars


@superuser_required
def analytics_dashboard(request):
    now = timezone.now()

    period_key = request.GET.get('period', '30d')
    if period_key not in PERIOD_CONFIG:
        period_key = '30d'
    cfg = PERIOD_CONFIG[period_key]
    since = now - timedelta(days=cfg['days'])

    # KPIs globaux
    total_published  = Listing.objects.filter(status=Listing.Status.PUBLISHED).count()
    total_pending    = Listing.objects.filter(status=Listing.Status.PENDING).count()
    total_views      = Listing.objects.aggregate(t=Sum('views_count'))['t'] or 0
    total_inquiries  = PublicInquiry.objects.count()
    unread_inquiries = PublicInquiry.objects.filter(is_read=False).count()
    total_favorites  = Favorite.objects.count()
    total_users      = User.objects.count()
    total_estimates  = EstimateEvent.objects.count()

    # KPIs sur la période sélectionnée
    new_listings  = Listing.objects.filter(created_at__gte=since).count()
    new_inquiries = PublicInquiry.objects.filter(created_at__gte=since).count()
    new_users     = User.objects.filter(date_joined__gte=since).count()
    new_favorites = Favorite.objects.filter(created_at__gte=since).count()
    new_estimates = EstimateEvent.objects.filter(created_at__gte=since).count()

    # Top annonces (tous temps)
    top_listings = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .order_by('-views_count')[:10]
    )
    max_views = top_listings[0].views_count if top_listings else 1

    # Graphique évolution
    bars = _build_bars(cfg['trunc'], cfg['n_bars'], now, since)
    max_bar = max((b['listings'] for b in bars), default=1) or 1

    # Villes
    cities = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .values('city').annotate(count=Count('id')).order_by('-count')[:8]
    )
    max_city = cities[0]['count'] if cities else 1

    # Par type de bien
    by_property = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .values('property_type').annotate(count=Count('id')).order_by('-count')
    )
    property_labels = {v: l for v, l in Listing.PropertyType.choices}

    # Vente vs location
    by_listing_type = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .values('listing_type').annotate(count=Count('id'))
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
        'total_estimates': total_estimates,
        'new_listings': new_listings,
        'new_inquiries': new_inquiries,
        'new_users': new_users,
        'new_favorites': new_favorites,
        'new_estimates': new_estimates,
        'top_listings': top_listings,
        'max_views': max_views or 1,
        'bars': bars,
        'max_bar': max_bar,
        'cities': cities,
        'max_city': max_city or 1,
        'by_property': [
            {**r, 'label': property_labels.get(r['property_type'], r['property_type'])}
            for r in by_property
        ],
        'sale_count': sale_count,
        'rent_count': rent_count,
        'recent_inquiries': recent_inquiries,
        'active_period': period_key,
        'period_label': cfg['label'],
        'periods': PERIODS_NAV,
    }
    return render(request, 'admin/analytics.html', context)
