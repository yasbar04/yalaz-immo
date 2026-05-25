from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from .models import Listing, ListingImage
from .constants import MOROCCAN_CITIES_CHOICES


class BaseListingImageFormSet(BaseInlineFormSet):
    """Formset personnalisé qui ignore les formes vides"""
    def clean(self):
        super().clean()
        # Ne pas valider les formes vides
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('image'):
                form.cleaned_data['DELETE'] = True


class ListingForm(forms.ModelForm):
    city = forms.ChoiceField(
        choices=MOROCCAN_CITIES_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'id': 'id_city'
            }
        ),
        label='Ville'
    )
    
    class Meta:
        model = Listing
        fields = [
            'title',
            'property_type',
            'listing_type',
            'city',
            'district',
            'price',
            'surface_area',
            'bedrooms',
            'bathrooms',
            'kitchen_equipped',
            'swimming_pool',
            'garden',
            'garage',
            'parking',
            'terrace',
            'balcony',
            'air_conditioning',
            'furnished',
            'security',
            'description',
            'image',
            'owner_email',
            'owner_phone',
            'owner_whatsapp',
        ]
        labels = {
            'title': 'Titre de l annonce',
            'property_type': 'Type de bien',
            'listing_type': 'Type d offre',
            'city': 'Ville',
            'district': 'Quartier',
            'price': 'Prix',
            'surface_area': 'Surface',
            'bedrooms': 'Chambres',
            'bathrooms': 'Salles de bain',
            'kitchen_equipped': 'Cuisine equipee',
            'swimming_pool': 'Piscine',
            'garden': 'Jardin',
            'garage': 'Garage',
            'parking': 'Parking',
            'terrace': 'Terrasse',
            'balcony': 'Balcon',
            'air_conditioning': 'Climatisation',
            'furnished': 'Meuble',
            'security': 'Gardiennage/Securite',
            'description': 'Description',
            'image': 'Photo de couverture',
            'owner_email': 'Email public',
            'owner_phone': 'Telephone public',
            'owner_whatsapp': 'WhatsApp',
        }
        help_texts = {
            'surface_area': 'Surface du bien en m2.',
            'owner_email': 'Laissez vide si vous ne souhaitez pas afficher votre email.',
            'owner_phone': 'Laissez vide si vous ne souhaitez pas afficher votre numero.',
            'owner_whatsapp': 'Optionnel. Ajoutez un numero WhatsApp pour faciliter les prises de contact.',
        }
        widgets = {
            'description': forms.Textarea(
                attrs={
                    'rows': 6,
                    'placeholder': 'Decrivez le bien, son etat, ses atouts, le quartier et toute information utile avant une visite.',
                }
            ),
            'title': forms.TextInput(
                attrs={'placeholder': 'Ex: Appartement 3 chambres avec terrasse et parking'}
            ),
            'district': forms.Select(
                attrs={
                    'id': 'id_district',
                    'class': 'form-select',
                }
            ),
            'image': forms.FileInput(
                attrs={'class': 'form-input', 'accept': 'image/*'}
            ),
            'price': forms.NumberInput(attrs={'placeholder': 'Laisser vide → "Contactez-nous"', 'min': '0'}),
            'surface_area': forms.NumberInput(
                attrs={'placeholder': 'Ex: 120', 'min': '0'}
            ),
            'bedrooms': forms.NumberInput(
                attrs={'placeholder': 'Ex: 3', 'min': '0'}
            ),
            'bathrooms': forms.NumberInput(
                attrs={'placeholder': 'Ex: 2', 'min': '0'}
            ),
            'owner_email': forms.EmailInput(attrs={'placeholder': 'Ex: contact@agence.com'}),
            'owner_phone': forms.TextInput(
                attrs={'placeholder': 'Ex: +212 6 12 34 56 78'}
            ),
            'owner_whatsapp': forms.TextInput(
                attrs={'placeholder': 'Ex: +212 6 12 34 56 78'}
            ),
            'kitchen_equipped': forms.CheckboxInput(),
            'swimming_pool': forms.CheckboxInput(),
            'garden': forms.CheckboxInput(),
            'garage': forms.CheckboxInput(),
            'parking': forms.CheckboxInput(),
            'terrace': forms.CheckboxInput(),
            'balcony': forms.CheckboxInput(),
            'air_conditioning': forms.CheckboxInput(),
            'furnished': forms.CheckboxInput(),
            'security': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            current_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{current_classes} form-input'.strip()


class ListingImageForm(forms.ModelForm):
    class Meta:
        model = ListingImage
        fields = ['image', 'alt_text', 'order']
        labels = {
            'image': 'Photo',
            'alt_text': 'Description',
            'order': 'Ordre',
        }
        widgets = {
            'alt_text': forms.TextInput(
                attrs={
                    'placeholder': 'Ex: Salon principal avec balcon',
                    'class': 'form-input',
                }
            ),
            'order': forms.NumberInput(attrs={'min': '0', 'class': 'form-input'}),
            'image': forms.FileInput(
                attrs={'class': 'form-input', 'accept': 'image/*'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs optionnels pour le formset
        self.fields['image'].required = False
        self.fields['order'].required = False
        self.fields['alt_text'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        # Si l'image est vide, marquer pour suppression
        if not cleaned_data.get('image'):
            self.cleaned_data['DELETE'] = True
        return cleaned_data



ListingImageFormSet = inlineformset_factory(
    Listing,
    ListingImage,
    form=ListingImageForm,
    fields=['image', 'alt_text', 'order'],
    formset=BaseListingImageFormSet,
    extra=10,
    can_delete=True,
    max_num=20,
)
