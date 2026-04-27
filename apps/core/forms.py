from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import FinancialTransaction

User = get_user_model()


class FinancialTransactionForm(forms.ModelForm):

    # Champs virtuels pour le calcul de commission (non stockés directement)
    property_price_input = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=15,
        decimal_places=2,
        label='Prix du bien (DH)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Ex: 2 000 000',
            'id': 'id_property_price_input',
        }),
    )
    commission_percentage_input = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=5,
        decimal_places=2,
        label='Pourcentage commission (%)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'max': '100',
            'placeholder': 'Ex: 2.5',
            'id': 'id_commission_percentage_input',
        }),
    )

    class Meta:
        model = FinancialTransaction
        fields = [
            'type', 'amount', 'transaction_date', 'description', 'category',
            'listing', 'assigned_to', 'status', 'notes',
            'property_price', 'commission_percentage',
            'payment_source', 'owner_amount', 'client_amount',
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control', 'id': 'id_type'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'id': 'id_amount',
            }),
            'transaction_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Vidéo réseaux sociaux avec Lina, Commission vente villa...',
            }),
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
            'listing': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes supplémentaires...',
            }),
            'property_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ex: 2 000 000',
                'id': 'id_property_price',
            }),
            'commission_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Ex: 2.5',
                'id': 'id_commission_percentage',
            }),
            'payment_source': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_payment_source',
            }),
            'owner_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant payé par le propriétaire',
                'id': 'id_owner_amount',
            }),
            'client_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant payé par le client',
                'id': 'id_client_amount',
            }),
        }
        labels = {
            'type': 'Type',
            'amount': 'Montant (DH)',
            'transaction_date': 'Date',
            'description': 'Description',
            'category': 'Catégorie',
            'listing': 'Bien immobilier (optionnel)',
            'assigned_to': 'Membre du staff concerné',
            'status': 'Statut',
            'notes': 'Notes',
            'property_price': 'Prix du bien (DH)',
            'commission_percentage': 'Taux de commission (%)',
            'payment_source': 'Qui a payé ?',
            'owner_amount': 'Part du propriétaire (DH)',
            'client_amount': 'Part du client (DH)',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Pré-remplir la date avec aujourd'hui
        if not self.instance.pk:
            self.fields['transaction_date'].widget.attrs['value'] = timezone.now().date().isoformat()

        # Filtrer les listings publiés uniquement
        from apps.listings.models import Listing
        self.fields['listing'].queryset = Listing.objects.filter(
            status='published'
        ).select_related('owner').order_by('title')
        self.fields['listing'].empty_label = '— Aucun bien lié —'

        # Filtrer les membres staff uniquement
        self.fields['assigned_to'].queryset = User.objects.filter(
            is_staff=True
        ).order_by('first_name', 'last_name')
        self.fields['assigned_to'].empty_label = '— Non assigné —'

        # payment_source: ajouter l'option vide
        self.fields['payment_source'].empty_value = ''

        # Pré-remplir les champs virtuels si on édite une transaction existante
        if self.instance.pk:
            self.fields['property_price_input'].initial = self.instance.property_price
            self.fields['commission_percentage_input'].initial = self.instance.commission_percentage

    def clean(self):
        cleaned_data = super().clean()
        payment_source = cleaned_data.get('payment_source')
        owner_amount = cleaned_data.get('owner_amount')
        client_amount = cleaned_data.get('client_amount')
        amount = cleaned_data.get('amount')

        if payment_source == 'both':
            if not owner_amount and owner_amount != 0:
                self.add_error('owner_amount', 'Veuillez préciser le montant du propriétaire.')
            if not client_amount and client_amount != 0:
                self.add_error('client_amount', 'Veuillez préciser le montant du client.')
            if owner_amount and client_amount and amount:
                total = owner_amount + client_amount
                if abs(total - amount) > 1:  # tolérance de 1 DH
                    self.add_error(
                        'owner_amount',
                        f'La somme ({total} DH) doit être égale au montant total ({amount} DH).'
                    )

        return cleaned_data
