# ✅ CHECKLIST SEO - ACTION IMMÉDIATE

## Phase 1: Déploiement Technique (URGENT - 1-2 jours)

```
☐ 1. Mettre à jour .env en production:
    ALLOWED_HOSTS=yalazagence.ma,www.yalazagence.ma
    APP_BASE_URL=https://yalazagence.ma
    DEBUG=False
    SECURE_SSL_REDIRECT=True
    SECURE_HSTS_SECONDS=31536000

☐ 2. Redémarrer le serveur Django

☐ 3. Vérifier les URLs fonctionnent:
    - https://yalazagence.ma/robots.txt ✓
    - https://yalazagence.ma/sitemap.xml ✓
    - https://yalazagence.ma/sitemap-listings.xml ✓

☐ 4. Activer SSL/HTTPS (Let's Encrypt gratuit)

☐ 5. Vérifier le score de sécurité:
    https://www.ssllabs.com/ssltest/
```

---

## Phase 2: Google Search Console (URGENT - Jour 1)

```
☐ 1. Créer compte: https://search.google.com/search-console
    
☐ 2. Ajouter propriété yalazagence.ma

☐ 3. Vérifier propriété (choosir: HTML tag ou DNS)
    - Récupérer le code de vérification
    - Ajouter dans templates/base.html
    - Redéployer

☐ 4. Soumettre Sitemap:
    Sitemaps > Ajouter
    → https://yalazagence.ma/sitemap.xml
    → https://yalazagence.ma/sitemap-listings.xml

☐ 5. Checker Règles robots.txt:
    Outils > Testeur de robots.txt
    → Vérifier /listings/ est allowed
    → Vérifier /admin/ est disallowed

☐ 6. Demander une couverture (crawl budget):
    Outils > Inspecter une URL
    → https://yalazagence.ma/

☐ 7. Attendre l'indexation (24-48h)
```

---

## Phase 3: Bing Webmaster Tools (Jour 2)

```
☐ 1. Créer compte: https://www.bing.com/webmasters

☐ 2. Ajouter site yalazagence.ma

☐ 3. Vérifier propriété (recommandé: fichier HTML)

☐ 4. Soumettre sitemap:
    Sitemaps > Soumettre un sitemap
    → https://yalazagence.ma/sitemap.xml

☐ 5. Configurer Crawl Settings:
    Site Configuration > Crawl Control
    → Set crawl delays (respecter les vôtres)
```

---

## Phase 4: Google Analytics (Jour 3)

```
☐ 1. Créer compte: https://analytics.google.com

☐ 2. Créer Data Stream (Web)
    → Domain: yalazagence.ma
    → URLs: https://yalazagence.ma

☐ 3. Ajouter tracking code (GA4) dans base.html
    <script async src="https://www.googletagmanager.com/..."></script>

☐ 4. Connecter avec Google Search Console:
    Admin > Links Management > Search Console > Link

☐ 5. Vérifier le tracking fonctionne (Real-time)
```

---

## Phase 5: Optimisations Complémentaires (Semaines 1-2)

```
☐ 1. Ajouter slugs aux listings (Haute Priorité)
    - CREATE TABLE migration
    - Générer slugs auto: title → slug
    - Update URLs: /listings/{id}/ → /listings/{slug}/
    - Redirects 301 /listings/{id}/ → /listings/{slug}/

☐ 2. Optimiser images:
    - Ajouter srcset pour responsivité
    - Lazy loading: loading="lazy"
    - Alt text descriptifs: "[type] [lieu] - [caractéristique]"
    - Format: WebP + JPEG fallback

☐ 3. Ajouter FAQ Schema:
    - Créer page /faq/
    - JSON-LD FAQPage schema
    - 10-15 questions importantes

☐ 4. Page contact SEO-optimisée:
    - LocalBusiness complètes (adresse, phone)
    - Map intégrée (Google Maps)
    - Schema ContactPoint

☐ 5. Breadcrumb navigation (visible + schema)
    - Accueil > Listings > [Ville] > [Annonce title]
```

---

## Phase 6: Content Strategy (Semaines 2-4)

```
☐ 1. Créer Blog (10 articles priorité haute):
    Topics SEO:
    ✓ "Comment vendre rapidement au Maroc"
    ✓ "Top 10 quartiers à investir à Casablanca"
    ✓ "Guide achat première propriété Maroc"
    ✓ "Financement immobilier Maroc 2024"
    ✓ "Taxes et légal acheter propriété Maroc"
    
    Format: 800-1500 mots, structure H1-H3, images
    
☐ 2. Internal Linking:
    - Linking articles → Listings par ville
    - Linking Listings → Articles pertinents
    - Anchor text: Keywords naturels

☐ 3. Case Studies (3-5):
    - Real success stories
    - Vente réussie: "Vendu en 3 semaines, +15% prix"
    - Format: Story + Results + Impact
    
☐ 4. Video Content:
    - Tour de propriétés premium
    - Virtual tours
    - Interviews agents
    - Upload YouTube + embed site
```

---

## Phase 7: Link Building (Semaines 3-8)

```
☐ 1. Local Directories:
    - Ajouter dans Google Business
    - Mappy, PagesJaunes (équivalent Maroc)
    - Directorys immobiliers Maroc

☐ 2. Outils Cite Locales:
    - Chamber of Commerce Maroc
    - Business directories Maroc-focused
    - Real Estate associations

☐ 3. Partnership Outreach:
    - Blogs immobiliers Maroc
    - Agences partenaires
    - Médias locaux
    - Pitch: "Guest post opportunity"

☐ 4. Social Signals:
    - LinkedIn: Share articles, engage
    - Facebook: Community building
    - Instagram: Property showcases
    - TikTok: Short property tours
```

---

## Phase 8: Monitoring Continu (Mensuel)

```
☐ Google Search Console:
    - Dashboard > Performance
    - Check: Impressions, Clicks, CTR, Position
    - Note: Evolution mois-sur-mois

☐ Google Analytics:
    - Organic Traffic trend
    - Top landing pages
    - Conversion rate (leads/contacts)
    - User engagement (pages/session, bounce)

☐ Rankings Check:
    - Tools: SEMrush, Ahrefs (7-day free trial)
    - Track: Top 20 keywords
    - Position: Target top 3

☐ Technical Health:
    - PageSpeed Insights: LCP, FID, CLS
    - Mobile Usability
    - Core Web Vitals

☐ Competitor Analysis:
    - Who ranks #1 for "bien à louer maroc"?
    - What keywords do they target?
    - Backlink strategy?
```

---

## 🎯 MOTS-CLÉS À CIBLER (Ordre de Priorité)

### Priority 1: HIGH VOLUME + LOW DIFFICULTY
```
1. "bien à louer maroc"
2. "acheter propriete maroc"
3. "immobilier maroc"
4. "vendre maison maroc"
5. "estimation immobiliere maroc"
```

### Priority 2: MEDIUM VOLUME + MEDIUM DIFFICULTY
```
6. "louer casablanca"
7. "acheter casablanca"
8. "immobilier casablanca"
9. "villa à louer rabat"
10. "propriete vendre marrakech"
```

### Priority 3: LOCAL/SPECIFIC
```
11. "appartement louer fes"
12. "terrain vendre agadir"
13. "maison acheter tanger"
14. "bien location kenitra"
15. "propriete vendre meknes"
```

---

## 📊 SUCCESS METRICS (À Tracker)

### Month 1-2:
```
Goal 1: Indexation complète
✓ Pages indexées: 100+ (depuis 0)
✓ Featured snippets: 5+ (depuis 0)
✓ Sitelinks Google: Affichage
```

### Month 3-4:
```
Goal 2: Organic traffic
✓ Sessions organiques: +50% vs baseline
✓ Landing pages: Top 20 keywords
✓ Leads from organic: +30
```

### Month 6+:
```
Goal 3: Rankings first page
✓ Keywords ranking page 1: 20+
✓ Keywords ranking top 3: 5+
✓ Organic revenue: +100% vs baseline
```

---

## 🚨 COMMON MISTAKES TO AVOID

```
❌ Ne pas mettre à jour robots.txt dans production
❌ Oublier de soumettre sitemap à GSC
❌ Keywords stuffing (Google va pénaliser)
❌ Contenu dupliqué (canonical URL oublié)
❌ Images sans alt text (manque de contexte)
❌ Pas de SSL/HTTPS (Google downrank)
❌ Site lent (PageSpeed < 50)
❌ Pas de mobile optimization
❌ Ignorer Analytics (pas de data = pas d'amélioration)
```

---

## 📞 SUPPORT & RESSOURCES

### Outils Gratuits:
- Google Search Console: search.google.com/search-console
- Google Analytics: analytics.google.com
- PageSpeed Insights: pagespeed.web.dev
- Bing Webmaster: bing.com/webmasters
- Schema.org Validator: schema.org/validator

### Outils Payants (Freemium):
- SEMrush: 7 days free, $120/month
- Ahrefs: $7 trial, $99/month
- Moz Pro: 30 days free, $99/month

### Documentation:
- Google SEO Starter Guide
- Bing Webmaster Guidelines
- Schema.org documentation

---

## ✨ FINAL SCORE ESTIMATE

```
Actuellement:      30/100 (Non-optimisé)
Après Phase 1-2:   70/100 (Indexable)
Après Phase 1-5:   82/100 (Solid)
Après Phase 1-7:   92/100 (Excellent)
```

---

*Dernière mise à jour: 25/04/2026*
*Document: Google/Bing SEO Best Practices + Maroc-specific optimization*
