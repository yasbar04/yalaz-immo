# Using default Django User model for V1.
from django.conf import settings
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Numero de telephone',
    )
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text='Breve description de vous',
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        help_text='Photo de profil',
    )
    email_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Date de verification de l email',
    )
    phone_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Date de verification du numero de telephone',
    )
    password_change_required = models.BooleanField(
        default=False,
        help_text='Changer le mot de passe obligatoire à la prochaine connexion',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Profil de {self.user.username}'

    @property
    def is_email_verified(self):
        return bool(self.email_verified_at)

    @property
    def is_phone_verified(self):
        return bool(self.phone_verified_at)

    @property
    def is_fully_verified(self):
        return self.is_email_verified and self.is_phone_verified

    def mark_email_verified(self):
        if not self.email_verified_at:
            self.email_verified_at = timezone.now()
            self.save(update_fields=['email_verified_at', 'updated_at'])

    def mark_phone_verified(self):
        if not self.phone_verified_at:
            self.phone_verified_at = timezone.now()
            self.save(update_fields=['phone_verified_at', 'updated_at'])


class VerificationChallenge(models.Model):
    class Channel(models.TextChoices):
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'

    class Purpose(models.TextChoices):
        SIGNUP = 'signup', 'Inscription'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_challenges',
    )
    channel = models.CharField(max_length=10, choices=Channel.choices)
    purpose = models.CharField(
        max_length=20,
        choices=Purpose.choices,
        default=Purpose.SIGNUP,
    )
    destination = models.CharField(max_length=255)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'channel', 'purpose']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.get_channel_display()} {self.get_purpose_display()} for {self.user.username}'
