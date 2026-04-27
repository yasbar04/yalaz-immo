from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


class FinancialTransaction(models.Model):
    """
    Modèle pour gérer les flux monétaires (entrées et sorties)
    pour le back office admin et staff
    """

    TYPE_CHOICES = [
        ('entry', 'Entrée'),
        ('exit', 'Sortie'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('cancelled', 'Annulé'),
    ]

    CATEGORY_CHOICES = [
        ('commission_vente', 'Commission vente'),
        ('commission_location', 'Commission location'),
        ('marketing', 'Marketing / Réseaux sociaux'),
        ('video_shooting', 'Vidéo / Shooting'),
        ('frais_divers', 'Frais divers'),
        ('autre', 'Autre'),
    ]

    PAYMENT_SOURCE_CHOICES = [
        ('owner', 'Propriétaire'),
        ('client', 'Client'),
        ('both', 'Les deux'),
    ]

    # Informations de base
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Montant en DH'
    )

    # Description et catégorie
    description = models.CharField(max_length=255, help_text='Exemple: Vidéo 500dh, Commission vente bien, etc.')
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='autre',
    )

    # Champs commission immobilière (optionnels)
    property_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Prix total du bien (pour calcul commission)'
    )
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Pourcentage de commission (ex: 2.5)'
    )

    # Source du paiement (qui a payé la commission)
    payment_source = models.CharField(
        max_length=10,
        choices=PAYMENT_SOURCE_CHOICES,
        null=True,
        blank=True,
        help_text='Qui a payé la commission'
    )
    owner_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Montant payé par le propriétaire'
    )
    client_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Montant payé par le client'
    )

    # Relation avec listing (optionnel)
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='financial_transactions',
        help_text='Bien immobilier associé (si applicable)'
    )

    # Utilisateur responsable
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='financial_transactions_created',
        help_text='Personne qui a enregistré la transaction'
    )

    # Membre du staff concerné (peut être différent du créateur)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='financial_transactions_assigned',
        help_text='Membre du staff concerné par cette transaction'
    )

    # Dates
    transaction_date = models.DateField(
        default=timezone.now,
        help_text='Date de la transaction'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notes
    notes = models.TextField(blank=True, help_text='Notes supplémentaires')

    class Meta:
        ordering = ['-transaction_date', '-created_at']
        verbose_name = 'Transaction Financière'
        verbose_name_plural = 'Transactions Financières'
        indexes = [
            models.Index(fields=['-transaction_date']),
            models.Index(fields=['type', 'status']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} DH - {self.description}"

    @property
    def is_entry(self):
        return self.type == 'entry'

    @property
    def is_commission(self):
        return self.category in ('commission_vente', 'commission_location')

    @property
    def display_name(self):
        return f"{self.get_type_display()} - {self.amount} DH"


class SellerRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('in_progress', 'En cours'),
        ('accepted', 'Accepté'),
        ('rejected', 'Refusé'),
    ]

    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Appartement'),
        ('house', 'Maison'),
        ('villa', 'Villa'),
        ('riad', 'Riad'),
        ('land', 'Terrain'),
        ('office', 'Bureau / Local commercial'),
        ('other', 'Autre'),
    ]

    LISTING_TYPE_CHOICES = [
        ('sale', 'Vente'),
        ('rent', 'Location'),
    ]

    # Coordonnées du vendeur
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # Informations du bien
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, default='sale')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    surface = models.PositiveIntegerField(null=True, blank=True, help_text='Surface en m²')
    rooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True, help_text='Prix souhaité en MAD')
    description = models.TextField(blank=True)

    # Équipements
    has_parking = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    has_terrace = models.BooleanField(default=False)
    has_elevator = models.BooleanField(default=False)
    has_security = models.BooleanField(default=False)

    # Champs admin
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_note = models.TextField(blank=True)

    # Métadonnées
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Demande vendeur'
        verbose_name_plural = 'Demandes vendeurs'

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.city} ({self.get_status_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class SellerRequestImage(models.Model):
    seller_request = models.ForeignKey(SellerRequest, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='seller_requests/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Photo #{self.pk} — {self.seller_request}"


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('acheter', 'Je souhaite acheter un bien'),
        ('vendre', 'Je souhaite vendre un bien'),
        ('louer', 'Je souhaite louer un bien'),
        ('estimation', 'Je souhaite une estimation'),
        ('agence', 'Je souhaite des informations sur l\'agence'),
        ('autre', 'Autre'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"
