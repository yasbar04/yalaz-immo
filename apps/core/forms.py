from django import forms
from django.utils import timezone
from .models import FinancialTransaction, SellerRequest


class FinancialTransactionForm(forms.ModelForm):
    """Formulaire pour créer/modifier une transaction financière"""
    
    class Meta:
        model = FinancialTransaction
        fields = [
            'type', 'status', 'amount', 'transaction_date',
            'description', 'category',
            'property_price', 'commission_percentage', 'payment_source', 'owner_amount', 'client_amount',
            'listing', 'assigned_to',
            'is_recurring', 'recurrence',
            'notes',
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00', 'required': True,
            }),
            'transaction_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
                'value': timezone.now().date().isoformat(),
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Vidéo shooting, Commission vente villa…',
                'required': True,
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'property_price': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '1', 'min': '0', 'placeholder': 'Ex : 2500000',
            }),
            'commission_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': 'Ex : 2.5',
            }),
            'payment_source': forms.Select(attrs={'class': 'form-control'}),
            'owner_amount': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00',
            }),
            'client_amount': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00',
            }),
            'listing': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'is_recurring': forms.CheckboxInput(attrs={'id': 'id_is_recurring'}),
            'recurrence': forms.Select(attrs={'class': 'form-control', 'id': 'id_recurrence'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Notes supplémentaires…',
            }),
        }
        labels = {
            'type': 'Type de transaction',
            'status': 'Statut',
            'amount': 'Montant (DH)',
            'transaction_date': 'Date',
            'description': 'Description',
            'category': 'Catégorie',
            'property_price': 'Prix du bien (DH)',
            'commission_percentage': 'Taux de commission (%)',
            'payment_source': 'Qui a payé la commission',
            'owner_amount': 'Part propriétaire (DH)',
            'client_amount': 'Part client (DH)',
            'listing': 'Bien immobilier (optionnel)',
            'assigned_to': 'Attribué à',
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
