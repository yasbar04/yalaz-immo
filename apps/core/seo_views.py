from django.shortcuts import render
from django.http import Http404
from django.utils.text import slugify
from apps.listings.models import Listing

# Slug → nom affiché (tel que stocké en base)
CITY_SLUG_MAP = {
    'casablanca': 'Casablanca',
    'marrakech': 'Marrakech',
    'rabat': 'Rabat',
    'tanger': 'Tanger',
    'fes': 'Fès',
    'agadir': 'Agadir',
    'meknes': 'Meknès',
    'oujda': 'Oujda',
    'sale': 'Salé',
    'kenitra': 'Kénitra',
    'tetouan': 'Tétouan',
    'el-jadida': 'El Jadida',
    'essaouira': 'Essaouira',
    'mohammedia': 'Mohammedia',
    'beni-mellal': 'Béni Mellal',
    'nador': 'Nador',
    'taza': 'Taza',
    'safi': 'Safi',
    'temara': 'Temara',
    'laayoune': 'Laâyoune',
    'settat': 'Settat',
    'berrechid': 'Berrechid',
    'khouribga': 'Khouribga',
    'bouskoura': 'Bouskoura',
}

PROPERTY_SLUG_MAP = {
    'appartement': {'db': 'apartment', 'sing': 'appartement', 'plur': 'Appartements', 'art': 'un'},
    'villa': {'db': 'villa', 'sing': 'villa', 'plur': 'Villas', 'art': 'une'},
    'maison': {'db': 'house', 'sing': 'maison', 'plur': 'Maisons', 'art': 'une'},
    'terrain': {'db': 'land', 'sing': 'terrain', 'plur': 'Terrains', 'art': 'un'},
    'bureau': {'db': 'office', 'sing': 'bureau', 'plur': 'Bureaux', 'art': 'un'},
    'local-commercial': {'db': 'commercial', 'sing': 'local commercial', 'plur': 'Locaux commerciaux', 'art': 'un'},
}

LISTING_TYPE_MAP = {
    'acheter': {'db': 'sale', 'label': 'à vendre', 'verb': 'Acheter', 'preposition': 'Vente'},
    'louer': {'db': 'rent', 'label': 'à louer', 'verb': 'Louer', 'preposition': 'Location'},
}

# Top cities for internal linking
TOP_CITIES = [
    ('casablanca', 'Casablanca'),
    ('marrakech', 'Marrakech'),
    ('rabat', 'Rabat'),
    ('tanger', 'Tanger'),
    ('agadir', 'Agadir'),
    ('fes', 'Fès'),
]


def city_listing(request, action_slug, city_slug, type_slug=None):
    """
    Pages SEO programmatiques pour les requêtes locales :
    /acheter/casablanca/ → Immobilier à vendre à Casablanca
    /acheter/casablanca/appartement/ → Appartements à vendre à Casablanca
    """
    action = LISTING_TYPE_MAP.get(action_slug)
    if not action:
        raise Http404

    city_name = CITY_SLUG_MAP.get(city_slug)
    if not city_name:
        raise Http404

    prop_type = None
    if type_slug:
        prop_type = PROPERTY_SLUG_MAP.get(type_slug)
        if not prop_type:
            raise Http404

    qs = Listing.objects.filter(
        status=Listing.Status.PUBLISHED,
        listing_type=action['db'],
        city__iexact=city_name,
    ).prefetch_related('images').order_by('-is_featured', '-created_at')

    if prop_type:
        qs = qs.filter(property_type=prop_type['db'])

    count = qs.count()

    if prop_type:
        h1 = f"{prop_type['plur']} {action['label']} à {city_name}"
        page_title = f"{prop_type['plur']} {action['label']} à {city_name} | Yalaz"
        meta_description = (
            f"Découvrez {count} {prop_type['sing']}{'' if count < 2 else 's'} "
            f"{action['label']} à {city_name}. Photos, prix, surface — "
            f"trouvez votre {prop_type['sing']} idéal avec Yalaz."
        )
    else:
        h1 = f"Immobilier {action['label']} à {city_name}"
        page_title = f"Immobilier {action['label']} à {city_name} — Annonces | Yalaz"
        meta_description = (
            f"Découvrez {count} bien{'s' if count != 1 else ''} immobilier{'s' if count != 1 else ''} "
            f"{action['label']} à {city_name}. "
            f"Appartements, villas, maisons — Yalaz vous accompagne."
        )

    # Types disponibles pour cette ville (liens internes)
    available_types = (
        Listing.objects.filter(
            status=Listing.Status.PUBLISHED,
            listing_type=action['db'],
            city__iexact=city_name,
        )
        .values_list('property_type', flat=True)
        .distinct()
    )
    type_links = []
    for prop_slug, prop_data in PROPERTY_SLUG_MAP.items():
        if prop_data['db'] in available_types:
            type_links.append({
                'slug': prop_slug,
                'label': prop_data['plur'],
                'url': f"/{action_slug}/{city_slug}/{prop_slug}/",
                'active': type_slug == prop_slug,
            })

    # Autres villes (liens internes)
    city_links = [
        {'slug': s, 'name': n, 'url': f"/{action_slug}/{s}/"}
        for s, n in TOP_CITIES if s != city_slug
    ]

    context = {
        'listings': qs,
        'city_name': city_name,
        'city_slug': city_slug,
        'action_slug': action_slug,
        'action': action,
        'prop_type': prop_type,
        'type_slug': type_slug,
        'h1': h1,
        'page_title': page_title,
        'meta_description': meta_description,
        'count': count,
        'type_links': type_links,
        'city_links': city_links,
        'property_slug_map': PROPERTY_SLUG_MAP,
    }
    return render(request, 'core/city_listing.html', context)


def get_all_city_type_urls():
    """Génère toutes les URLs actives pour le sitemap."""
    urls = []
    published = Listing.objects.filter(status=Listing.Status.PUBLISHED).values('city', 'listing_type', 'property_type').distinct()

    seen_city_action = set()
    seen_city_action_type = set()

    for row in published:
        city = row['city']
        city_slug = slugify(city)
        if city_slug not in CITY_SLUG_MAP:
            continue

        for action_slug, action_data in LISTING_TYPE_MAP.items():
            if action_data['db'] == row['listing_type']:
                # City-level URL
                key_ca = (city_slug, action_slug)
                if key_ca not in seen_city_action:
                    seen_city_action.add(key_ca)
                    urls.append(f"/{action_slug}/{city_slug}/")

                # City+type URL
                for prop_slug, prop_data in PROPERTY_SLUG_MAP.items():
                    if prop_data['db'] == row['property_type']:
                        key_cat = (city_slug, action_slug, prop_slug)
                        if key_cat not in seen_city_action_type:
                            seen_city_action_type.add(key_cat)
                            urls.append(f"/{action_slug}/{city_slug}/{prop_slug}/")

    return urls
