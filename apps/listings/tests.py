from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.services import (
    send_listing_approved_notification,
    send_listing_submission_notification,
)

from .models import Listing

User = get_user_model()


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    APP_BASE_URL='http://testserver',
)
class ListingNotificationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='SecuriseTest123!',
            is_active=True,
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminSecurise123!',
        )
        self.listing = Listing.objects.create(
            owner=self.owner,
            title='Villa front de mer',
            property_type=Listing.PropertyType.VILLA,
            listing_type=Listing.ListingType.SALE,
            city='Casablanca',
            district='Anfa',
            price=2500000,
            surface_area=320,
            bedrooms=4,
            bathrooms=3,
            description='Une villa premium avec vue mer.',
            status=Listing.Status.PENDING,
        )

    def test_submission_notification_mentions_pending_validation(self):
        send_listing_submission_notification(self.listing)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('en attente de validation', mail.outbox[0].subject.lower())
        self.assertIn('en attente de validation', mail.outbox[0].body.lower())

    def test_admin_approval_sends_validation_email(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('admin_listing_detail', kwargs={'pk': self.listing.pk}),
            data={'action': 'approve'},
        )

        self.assertRedirects(
            response,
            reverse('admin_listing_detail', kwargs={'pk': self.listing.pk}),
        )

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, Listing.Status.PUBLISHED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('a ete validee', mail.outbox[0].subject.lower())

        mail.outbox.clear()
        send_listing_approved_notification(self.listing)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('maintenant visible', mail.outbox[0].body.lower())
