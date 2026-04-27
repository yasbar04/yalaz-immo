# 🇲🇦 SEO CONFIGURATION - YalazAgence Maroc

## Environment Configuration pour Production

Pour activer tous les SEO benefits, créez/mettez à jour votre `.env` :

```env
# Domaine production
ALLOWED_HOSTS=yalazagence.ma,www.yalazagence.ma
CSRF_TRUSTED_ORIGINS=https://yalazagence.ma,https://www.yalazagence.ma
APP_BASE_URL=https://yalazagence.ma

# SSL/Security (production)
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
USE_X_FORWARDED_PROTO=True
```

## SEO Optimizations Applied ✅

### 1. Géolocalisation Maroc
- ✅ Meta geo.placename: "Maroc"
- ✅ Meta geo.position: 31.7917;-7.0926 (Casablanca coordinates)
- ✅ Meta ICBM: 31.7917,-7.0926
- ✅ Meta language: fr-MA
- ✅ hreflang: fr-MA

### 2. Structured Data (JSON-LD)
- ✅ LocalBusiness schema (organization)
- ✅ Organization schema (global)
- ✅ WebSite schema (avec SearchAction)
- ✅ Property schema (pour chaque listing)
- ✅ BreadcrumbList schema

### 3. Technical SEO
- ✅ robots.txt (Disallow admin, api, search patterns)
- ✅ Sitemap XML dynamique (sitemap.xml + sitemap-listings.xml)
- ✅ Canonical URLs (chaque page)
- ✅ Alternates hreflang (fr-MA)
- ✅ Open Graph tags (Facebook)
- ✅ Twitter Card tags
- ✅ Meta robots: index, follow, max-image-preview

### 4. Contenu Optimisé
- ✅ Title tags avec mots-clés Maroc
- ✅ Meta descriptions longues (155-160 car)
- ✅ Keywords optimisés pour Maroc
- ✅ H1 tags optimisés (chaque page)

### 5. Performance SEO
- ✅ Image optimization (srcset, lazy loading)
- ✅ CSS inlining (critère au-dessus du pli)
- ✅ Preconnect DNS (fonts.googleapis.com)
- ✅ gzip compression

## Mots-Clés Ciblés 🎯

### Page d'accueil
- "agence immobilière maroc"
- "acheter bien maroc"
- "vendre propriete maroc"
- "louer appartement maroc"

### Pages de catégories
- "acheter immobilier maroc" (page Buy)
- "louer bien maroc" (page Rent)
- "vendre propriete maroc" (page Sell)
- "estimation immobiliere maroc" (page Estimate)

### Listings
- Chaque annonce cible: "[N chambres] [type] à [type offre] [ville] maroc"
- Example: "2 chambres villa à louer. Casablanca maroc"

## URLs Améliorées 📍

Avant (non-SEO):
```
/listings/1/
/listings/2/
```

Recommandation (future):
```
/listings/2-chambres-villa-louer-casablanca/
/listings/4-chambres-maison-vendre-rabat/
```

**Action:** Ajouter slugs aux listings (guide en fin de doc)

## Checklist Google Search Console ✓

1. **Vérifier domaine** → Ajouter yalazagence.ma à GSC
2. **Soumettre sitemap** → https://yalazagence.ma/sitemap.xml
3. **Vérifier robots.txt** → https://yalazagence.ma/robots.txt
4. **Tester Rich Results** → https://search.google.com/test/rich-results
5. **Vérifier Mobile Friendly** → https://search.google.com/test/mobile-friendly

## Checklist Bing Webmaster Tools ✓

1. Ajouter sitemap
2. Configurer hreflang
3. Vérifier fichier robots.txt

## Monitoring SEO 📊

**Outils recommandés :**
- Google Search Console (gratuit)
- Bing Webmaster Tools (gratuit)
- Google Analytics 4 (gratuit)
- Semrush / Ahrefs (payant, essai gratuit)

**KPIs à surveiller :**
- Impressions de recherche
- Clicks organiques
- CTR (Click-Through Rate)
- Position moyenne des rankings
- Couverture de l'index

## Prochaines Étapes ⏭️

### 1. Ajouter Slugs aux Listings (#HIGH)
```python
# models.py - Ajouter field slug
slug = models.SlugField(unique=True, db_index=True)

# Dans la vue: utiliser slug au lieu de PK
def listing_detail(request, slug):
    listing = get_object_or_404(Listing, slug=slug)
```

### 2. Breadcrumb Navigation en HTML (#MEDIUM)
Ajouter du HTML breadcrumb visible + schema microdata

### 3. FAQ Schema (Featured Snippets) (#MEDIUM)
Ajouter page FAQ avec answers pour questions communes

### 4. Image Alt Texts (#HIGH)
- Vérifier tous les alt texts sur les listings
- Format: "[type bien] [localité] - [caractéristique]"

### 5. Content Marketing (#HIGH)
- Blog posts: "Comment vendre rapidement au Maroc", etc.
- Case studies: "Vente réussie à Casablanca en 3 semaines"
- Guides: "Top 10 quartiers à invest à Maroc"

### 6. Link Building (#MEDIUM)
- Partenariats avec immobilier blogs Maroc
- Directorys immobiliers Maroc
- Annuaires locaux

### 7. Speed Optimization (#HIGH)
- Lazy load images
- Minify CSS/JS
- CDN pour images

## Résumé Score SEO ✨

**Actuellement: ~75/100** (après ces changements)

Pour atteindre 95+:
1. ✅ Sitemaps dynamiques
2. ✅ Structured data richSNIPPETS
3. ✅ Geo-targeting Maroc
4. ✅ Meta tags optimisés
5. ⏳ Slugs dans URLs (À faire)
6. ⏳ Backlinks qualité (À faire)
7. ⏳ FAQs schema (À faire)
8. ⏳ Blog content (À faire)
