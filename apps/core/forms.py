from django import forms
from django.utils import timezone
from .models import FinancialTransaction, SellerRequest


class FinancialTransactionForm(forms.ModelForm):
    """Formulaire pour créer/modifier une transaction financière"""
    
    class Meta:
        model = FinancialTransaction
        fields = ['type', 'amount', 'description', 'category', 'listing', 'assigned_to', 'transaction_date', 'status', 'is_recurring', 'recurrence', 'notes']
        widgets = {
            'type': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'required': True,
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Exemple: Vidéo 500dh, Commission vente bien...',
                'required': True,
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Exemple: Vidéo, Photographie, Commission...',
            }),
            'listing': forms.Select(attrs={
                'class': 'form-control',
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-control',
            }),
            'transaction_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'value': timezone.now().date().isoformat(),
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes supplémentaires...',
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'id': 'id_is_recurring',
            }),
            'recurrence': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_recurrence',
            }),
        }
        labels = {
            'type': 'Type de transaction',
            'amount': 'Montant (DH)',
            'description': 'Description *',
            'category': 'Catégorie',
            'listing': 'Bien immobilier (optionnel)',
            'assigned_to': 'Attribué à',
            'transaction_date': 'Date *',
            'status': 'Statut',
            'is_recurring': 'Transaction récurrente',
            'recurrence': 'Fréquence',
            'notes': 'Notes',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Rendre assigned_to requis pour certains types
        if self.instance.pk and self.instance.type in ['commission']:
            self.fields['assigned_to'].required = True
        
        # Filtrer les listings actifs
        from apps.listings.models import Listing
        self.fields['listing'].queryset = Listing.objects.filter(
            status='published'
        ).select_related('owner')


class QuickTransactionForm(forms.ModelForm):
    """Formulaire simplifié pour créer rapidement une transaction"""
    
    class Meta:
        model = FinancialTransaction
        fields = ['type', 'amount', 'description', 'category', 'assigned_to', 'status']
        widgets = {
            'type': forms.Select(attrs={
                'class': 'form-control form-control-sm',
                'required': True,
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'number',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'required': True,
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Description...',
                'required': True,
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Catégorie...',
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-control form-control-sm',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control form-control-sm',
            }),
        }


class SellerRequestForm(forms.ModelForm):
    class Meta:
        model = SellerRequest
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'listing_type', 'property_type', 'city', 'district',
            'surface', 'rooms', 'bathrooms', 'price', 'description',
            'has_parking', 'has_pool', 'has_garden', 'has_terrace',
            'has_elevator', 'has_security',
        ]
