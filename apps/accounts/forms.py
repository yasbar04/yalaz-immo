from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import UserProfile
from .services import normalize_phone_number


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nom d utilisateur'
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-input',
                'placeholder': 'Votre nom d utilisateur',
                'autocomplete': 'username',
            }
        )
        self.fields['password'].label = 'Mot de passe'
        self.fields['password'].widget.attrs.update(
            {
                'class': 'form-input',
                'placeholder': 'Votre mot de passe',
                'autocomplete': 'current-password',
            }
        )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                'Votre compte n est pas encore verifie. Confirmez votre email et votre code SMS pour l activer.',
                code='inactive',
            )
        super().confirm_login_allowed(user)


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=301,
        required=True,
        label='Nom et Prénom',
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Votre nom et prénom',
                'autocomplete': 'name',
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Votre adresse email',
                'autocomplete': 'email',
            }
        ),
    )
    phone_number = forms.CharField(
        required=True,
        label='Telephone',
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Ex: +212 6 12 34 56 78',
                'autocomplete': 'tel',
            }
        ),
        help_text='Un code SMS vous sera envoye pour finaliser l activation du compte.',
    )

    class Meta:
        model = User
        fields = (
            'username',
            'full_name',
            'email',
            'phone_number',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Nom d utilisateur'
        self.fields['username'].help_text = (
            'Jusqu a 150 caracteres. Lettres, chiffres et caracteres ./+/-/_ uniquement.'
        )
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-input',
                'placeholder': 'Choisissez un nom d utilisateur',
                'autocomplete': 'username',
            }
        )

        self.fields['password1'].label = 'Mot de passe'
        self.fields['password1'].help_text = (
            '<ul>'
            '<li>Votre mot de passe doit contenir au moins 8 caracteres.</li>'
            '<li>Il ne doit pas etre trop proche de vos informations personnelles.</li>'
            '<li>Il ne doit pas etre un mot de passe couramment utilise.</li>'
            '<li>Il ne peut pas etre entierement numerique.</li>'
            '</ul>'
        )
        self.fields['password1'].widget.attrs.update(
            {
                'class': 'form-input',
                'placeholder': 'Creez un mot de passe',
                'autocomplete': 'new-password',
            }
        )

        self.fields['password2'].label = 'Confirmation du mot de passe'
        self.fields['password2'].help_text = (
            'Saisissez le meme mot de passe une seconde fois pour confirmation.'
        )
        self.fields['password2'].widget.attrs.update(
            {
                'class': 'form-input',
                'placeholder': 'Confirmez votre mot de passe',
                'autocomplete': 'new-password',
            }
        )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Cette adresse email est deja utilisee.')
        return email

    def clean_phone_number(self):
        phone_number = normalize_phone_number(self.cleaned_data['phone_number'])
        if not phone_number:
            raise forms.ValidationError('Renseignez un numero de telephone valide.')
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Ce numero de telephone est deja utilise.')
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        parts = self.cleaned_data['full_name'].strip().split(None, 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''
        user.email = self.cleaned_data['email']
        user.is_active = False

        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.phone_verified_at = None
            profile.email_verified_at = None
            profile.save()

        return user


class SMSVerificationForm(forms.Form):
    sms_code = forms.CharField(
        label='Code SMS',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Entrez le code a 6 chiffres',
                'autocomplete': 'one-time-code',
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
            }
        ),
    )

    def clean_sms_code(self):
        sms_code = ''.join(filter(str.isdigit, self.cleaned_data['sms_code']))
        if len(sms_code) != 6:
            raise forms.ValidationError('Saisissez un code SMS valide a 6 chiffres.')
        return sms_code


class VerificationRecoveryForm(forms.Form):
    email = forms.EmailField(
        label='Email du compte',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Votre adresse email',
                'autocomplete': 'email',
            }
        ),
    )


class UserProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=301,
        required=False,
        label='Nom et Prénom',
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Votre nom et prénom',
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Votre email',
            }
        ),
    )

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'bio', 'avatar']
        labels = {
            'phone_number': 'Numero de telephone',
            'bio': 'Biographie',
            'avatar': 'Photo de profil',
        }
        widgets = {
            'phone_number': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Ex: +212 6 12 34 56 78',
                }
            ),
            'bio': forms.Textarea(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Dites-nous quelques mots sur vous...',
                    'rows': 4,
                }
            ),
            'avatar': forms.FileInput(
                attrs={
                    'class': 'form-input',
                    'accept': 'image/*',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            full = f"{self.instance.user.first_name} {self.instance.user.last_name}".strip()
            self.fields['full_name'].initial = full
            self.fields['email'].initial = self.instance.user.email
