from django.db import models
from django.contrib.auth.models import User


class Contract(models.Model):
    TYPE_CHOICES = [
        ('bon_visite_vente', 'Bon de visite (Vente)'),
        ('bon_visite_location', 'Bon de visite (Location)'),
        ('mandat_vente', 'Mandat de vente'),
        ('mandat_location', 'Mandat de location'),
        ('mandat_recherche', 'Mandat de recherche'),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    reference = models.CharField(max_length=50, unique=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contrat'
        verbose_name_plural = 'Contrats'

    def save(self, *args, **kwargs):
        if not self.reference:
            abbr = {
                'bon_visite_vente': 'BVV',
                'bon_visite_location': 'BVL',
                'mandat_vente': 'MVT',
                'mandat_location': 'MLO',
                'mandat_recherche': 'MRC',
            }.get(self.type, 'CON')
            count = Contract.objects.filter(type=self.type).count() + 1
            self.reference = f'{abbr}-{count:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_type_display()} — {self.reference}'

    def get_client_name(self):
        d = self.data
        if self.type in ('bon_visite_vente', 'bon_visite_location'):
            return d.get('visiteur_nom_prenom') or d.get('nom_prenom', '')
        return d.get('mandant_nom', '')

    def get_pdf_template(self):
        return f'contracts/pdf/{self.type}.html'
