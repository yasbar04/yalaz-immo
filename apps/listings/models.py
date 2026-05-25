from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

# Codes ville 3 lettres pour la référence (CAS-APT-V-0042)
_CITY_CODES = {
    'Agadir': 'AGD', 'Al Hoceima': 'AHO', 'Azilal': 'AZL',
    'Béni Mellal': 'BML', 'Beni Mellal': 'BML', 'Berkane': 'BRK',
    'Berrechid': 'BRC', 'Bouskoura': 'BSK', 'Casablanca': 'CAS',
    'Chefchaouen': 'CHF', 'Dakhla': 'DKH', 'El Jadida': 'EJD',
    'Errachidia': 'ERR', 'Essaouira': 'ESS', 'Fès': 'FES', 'Fes': 'FES',
    'Guelmim': 'GLM', 'Ifrane': 'IFR', 'Kénitra': 'KNT', 'Kenitra': 'KNT',
    'Khémisset': 'KMS', 'Khemisset': 'KMS', 'Khouribga': 'KHR',
    'Laâyoune': 'LYN', 'Laayoune': 'LYN', 'Larache': 'LAR',
    'Marrakech': 'MRK', 'Meknès': 'MKN', 'Meknes': 'MKN',
    'Mohammedia': 'MOH', 'Nador': 'NAD', 'Ouarzazate': 'OUA',
    'Oujda': 'OJD', 'Rabat': 'RBT', 'Safi': 'SAF', 'Salé': 'SAL',
    'Sale': 'SAL', 'Settat': 'SET', 'Sidi Ifni': 'SIF', 'Skhirat': 'SKH',
    'Tanger': 'TNG', 'Taroudant': 'TRD', 'Tétouan': 'TET', 'Tetouan': 'TET',
    'Tiznit': 'TZN', 'Zagora': 'ZAG', 'Taza': 'TAZ', 'Tan-Tan': 'TNT',
    'Oued Zem': 'OZM', 'Fquih Ben Salah': 'FBS', 'Sidi Kacem': 'SKC',
    'Sidi Slimane': 'SSL', 'Souk El Arbaa': 'SEA', 'Temara': 'TMR',
}

_PROPERTY_CODES = {
    'apartment': 'APT', 'house': 'MAI', 'villa': 'VIL',
    'land': 'TER', 'office': 'BUR', 'commercial': 'COM',
}


def _city_code(city):
    code = _CITY_CODES.get(city.strip())
    if code:
        return code
    clean = ''.join(c for c in city.upper() if c.isalpha())
    return clean[:3] if len(clean) >= 3 else clean.ljust(3, 'X')


class Listing(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = 'apartment', 'Appartement'
        HOUSE = 'house', 'Maison'
        VILLA = 'villa', 'Villa'
        LAND = 'land', 'Terrain'
        OFFICE = 'office', 'Bureau'
        COMMERCIAL = 'commercial', 'Local commercial'

    class ListingType(models.TextChoices):
        SALE = 'sale', 'Vente'
        RENT = 'rent', 'Location'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        PENDING = 'pending', 'En attente'
        PUBLISHED = 'published', 'Publiee'
        REJECTED = 'rejected', 'Refusee'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
    )
    title = models.CharField(max_length=255)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices)
    listing_type = models.CharField(max_length=10, choices=ListingType.choices)
    city = models.CharField(max_length=120)
    district = models.CharField(max_length=120, blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    surface_area = models.PositiveIntegerField(help_text='Surface en m2')
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    kitchen_equipped = models.BooleanField(default=False, help_text='Cuisine equipee')
    swimming_pool = models.BooleanField(default=False, help_text='Piscine')
    garden = models.BooleanField(default=False, help_text='Jardin')
    garage = models.BooleanField(default=False, help_text='Garage')
    parking = models.BooleanField(default=False, help_text='Parking')
    terrace = models.BooleanField(default=False, help_text='Terrasse')
    balcony = models.BooleanField(default=False, help_text='Balcon')
    air_conditioning = models.BooleanField(default=False, help_text='Climatisation')
    furnished = models.BooleanField(default=False, help_text='Meuble')
    security = models.BooleanField(default=False, help_text='Gardiennage/Securite')
    description = models.TextField()
    image = models.ImageField(
        upload_to='listings/%Y/%m/',
        blank=True,
        null=True,
        help_text='Image de couverture',
    )
    owner_email = models.EmailField(
        blank=True,
        null=True,
        help_text='Email pour etre contacte (laissez vide pour cacher)',
    )
    owner_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Telephone pour etre contacte',
    )
    owner_whatsapp = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Numero WhatsApp',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reference = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        db_index=True,
        help_text='Référence unique (ex : CAS-APT-V-0042)',
    )
    is_featured = models.BooleanField(default=False, help_text='Affichee en avant')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['owner', 'status']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listing_detail', kwargs={'pk': self.pk})

    def _generate_reference(self):
        city = _city_code(self.city or 'YAL')
        prop = _PROPERTY_CODES.get(self.property_type, (self.property_type or 'BIE')[:3].upper())
        kind = 'V' if self.listing_type == 'sale' else 'L'
        return f"{city}-{prop}-{kind}-{self.pk:04d}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.reference:
            self.reference = self._generate_reference()
            Listing.objects.filter(pk=self.pk).update(reference=self.reference)

    def can_edit(self, user):
        if not getattr(user, 'is_authenticated', False):
            return False
        return self.owner == user or user.is_staff or user.is_superuser

    def can_delete(self, user):
        if not getattr(user, 'is_authenticated', False):
            return False
        if user.is_staff or user.is_superuser:
            return True
        return self.owner == user and self.status != self.Status.PUBLISHED


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='listings/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'Image for {self.listing.title}'


class Contact(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='contacts',
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_contacts',
    )
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('listing', 'from_user')

    def __str__(self):
        return f'Contact for {self.listing.title} from {self.from_user.username}'


class Report(models.Model):
    class ReportType(models.TextChoices):
        SPAM = 'spam', 'Spam'
        INAPPROPRIATE = 'inappropriate', 'Contenu inapproprie'
        FRAUD = 'fraud', 'Fraude/Arnaque'
        FAKE = 'fake', 'Annonce fake'
        OTHER = 'other', 'Autre'

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        REVIEWED = 'reviewed', 'Examine'
        RESOLVED = 'resolved', 'Resolu'
        DISMISSED = 'dismissed', 'Rejete'

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True,
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_by',
        null=True,
        blank=True,
    )
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_report_type_display()} - {self.status}'


class PublicInquiry(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='inquiries',
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    want_similar = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Demande de {self.first_name} {self.last_name} – {self.listing.title}'


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} -> {self.listing.title}'
