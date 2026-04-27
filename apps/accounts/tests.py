from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import UserProfile, VerificationChallenge
from .services import build_email_verification_token

User = get_user_model()


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    SMS_BACKEND='console',
    APP_BASE_URL='http://testserver',
)
class SignupVerificationFlowTests(TestCase):
    def test_signup_creates_inactive_user_and_sends_verification_email(self):
        response = self.client.post(
            reverse('signup'),
            data={
                'username': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'phone_number': '+212612345678',
                'password1': 'SecuriseTest123!',
                'password2': 'SecuriseTest123!',
            },
        )

        self.assertRedirects(response, reverse('verify_account'))
        user = User.objects.get(username='newuser')
        profile = UserProfile.objects.get(user=user)

        self.assertFalse(user.is_active)
        self.assertEqual(profile.phone_number, '+212612345678')
        self.assertEqual(
            VerificationChallenge.objects.filter(user=user).count(),
            2,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Confirmez votre adresse email', mail.outbox[0].subject)

        session = self.client.session
        self.assertEqual(session.get('pending_verification_user_id'), user.pk)

    def test_email_and_sms_verification_activate_the_account(self):
        self.client.post(
            reverse('signup'),
            data={
                'username': 'flowuser',
                'first_name': 'Flow',
                'last_name': 'User',
                'email': 'flowuser@example.com',
                'phone_number': '+212600000001',
                'password1': 'SecuriseTest123!',
                'password2': 'SecuriseTest123!',
            },
        )

        user = User.objects.get(username='flowuser')
        sms_challenge = VerificationChallenge.objects.get(
            user=user,
            channel=VerificationChallenge.Channel.SMS,
        )
        sms_challenge.code_hash = make_password('123456')
        sms_challenge.save(update_fields=['code_hash', 'updated_at'])

        verify_email_response = self.client.get(
            reverse('verify_email'),
            {'token': build_email_verification_token(user)},
        )
        self.assertRedirects(verify_email_response, reverse('verify_account'))

        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertTrue(UserProfile.objects.get(user=user).is_email_verified)

        verify_sms_response = self.client.post(
            reverse('verify_account'),
            data={'sms_code': '123456'},
        )
        self.assertRedirects(verify_sms_response, reverse('dashboard'))

        user.refresh_from_db()
        profile = UserProfile.objects.get(user=user)
        self.assertTrue(user.is_active)
        self.assertTrue(profile.is_email_verified)
        self.assertTrue(profile.is_phone_verified)
        self.assertEqual(len(mail.outbox), 2)
