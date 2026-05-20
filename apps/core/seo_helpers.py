"""
Django template context helpers for SEO optimization
Usage: Call add_seo_context() in views to inject SEO data
"""

from urllib.parse import urljoin


def add_seo_context(request, context=None, **kwargs):
    """
    Add SEO-related data to template context
    
    Usage in views:
        context = add_seo_context(request, {
            'title': 'Mon titre',
            'description': 'Ma description',
            'keywords': 'keyword1, keyword2',
        })
    """
    if context is None:
        context = {}
    
    base_url = f"{request.scheme}://{request.get_host()}"
    
    # Default SEO data
    seo_defaults = {
        'base_url': base_url,
        'page_url': request.build_absolute_uri(),
        'canonical_url': request.build_absolute_uri(),
    }
    
    # Merge with kwargs
    seo_data = {**seo_defaults, **kwargs}
    context.update(seo_data)
    
    return context


def get_listing_seo_data(listing, request):
    """
    Generate SEO data for a listing
    Returns dict with title, description, keywords, etc.
    """
    property_type = listing.get_property_type_display()
    listing_type = "à louer" if listing.listing_type == "rent" else "à vendre"
    
    title = f"{listing.title} - {property_type} {listing_type} | Yalaz"
    
    description = (
        f"{listing.title} - {property_type} {listing_type} à {listing.city}"
        f"{f', {listing.district}' if listing.district else ''} "
        f"- {listing.surface_area}m² - {listing.bedrooms} chambre"
        f"{'s' if listing.bedrooms > 1 else ''} | Yalaz Maroc"
    )
    
    keywords = [
        listing.title,
        f"{property_type} {listing_type}",
        listing.city,
        "immobilier maroc",
        f"{listing.bedrooms} chambre{'s' if listing.bedrooms > 1 else ''}",
    ]
    
    if listing.district:
        keywords.append(listing.district)
    
    return {
        'title': title,
        'description': description,
        'keywords': ', '.join(keywords),
        'property_type': property_type,
        'listing_type': listing_type,
    }


def get_city_page_seo_data(city, listing_type, request):
    """
    Generate SEO data for city-specific pages
    Example: /buy?city=Casablanca
    """
    type_label = "à louer" if listing_type == "rent" else "à vendre"
    type_fr = "Location" if listing_type == "rent" else "Vente"
    
    title = f"{city.title()} - Biens {type_label} | Yalaz Maroc"
    
    description = (
        f"Trouvez des propriétés {type_label} à {city}. "
        f"Consultez nos annonces immobilières à {city} - "
        f"{type_fr} d'apartements, maisons, villas et terrains. "
        f"Yalaz - Agence immobilière de confiance au Maroc."
    )
    
    keywords = [
        f"bien à {type_label} {city}",
        f"propriete à {type_label} {city}",
        f"immobilier {city}",
        city,
        "maroc",
        f"agence immobiliere {city}",
    ]
    
    return {
        'title': title,
        'description': description,
        'keywords': ', '.join(keywords),
    }
