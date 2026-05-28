import base64
import logging
import secrets
from datetime import timedelta
from urllib import parse, request as urllib_request

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.core import signing
from django.core.mail import EmailMultiAlternatives
from django.core.signing import BadSignature, SignatureExpired
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .models import UserProfile, VerificationChallenge

logger = logging.getLogger(__name__)
User = get_user_model()


class VerificationError(Exception):
    """Base verification error."""


class VerificationThrottled(VerificationError):
    """Raised when a verification challenge is resent too quickly."""


class VerificationExpired(VerificationError):
    """Raised when a verification code or link has expired."""


class VerificationInvalid(VerificationError):
    """Raised when the verification code or link is invalid."""


def normalize_phone_number(phone_number):
    raw = (phone_number or '').strip()
    if not raw:
        return ''

    digits = ''.join(char for char in raw if char.isdigit())
    if len(digits) < 8 or len(digits) > 15:
        return ''
    return f'+{digits}'


def mask_email_address(email):
    if not email or '@' not in email:
        return email
    local_part, domain = email.split('@', 1)
    if len(local_part) <= 2:
        masked_local = f'{local_part[0]}*'
    else:
        masked_local = f'{local_part[:2]}***'
    return f'{masked_local}@{domain}'


def mask_phone_number(phone_number):
    if not phone_number:
        return ''
    visible_suffix = phone_number[-3:]
    return f'*** *** {visible_suffix}'


def _build_absolute_url(path, request=None):
    if request is not None:
        return request.build_absolute_uri(path)
    return f"{settings.APP_BASE_URL.rstrip('/')}{path}"


def _render_email_body(template_prefix, context):
    text_body = render_to_string(f'{template_prefix}.txt', context).strip()
    try:
        html_body = render_to_string(f'{template_prefix}.html', context)
    except TemplateDoesNotExist:
        html_body = None
    return text_body, html_body


def send_templated_email(subject, recipient_list, template_prefix, context):
    recipients = [email for email in recipient_list if email]
    if not recipients:
        return

    text_body, html_body = _render_email_body(template_prefix, context)
    message = EmailMultiAlternatives(
        subject=subject.replace('\n', ' ').strip(),
        body=text_body,
        from_email=settings.TRANSACTIONAL_FROM_EMAIL,
        to=recipients,
    )
    if html_body:
        message.attach_alternative(html_body, 'text/html')
    message.send(fail_silently=False)


def send_sms_message(phone_number, message):
    if not phone_number:
        return

    if settings.SMS_BACKEND == 'console':
        logger.info('SMS to %s: %s', phone_number, message)
        return

    if settings.SMS_BACKEND != 'twilio':
        raise VerificationError('Aucun backend SMS valide n est configure.')

    if not (
        settings.SMS_TWILIO_ACCOUNT_SID
        and settings.SMS_TWILIO_AUTH_TOKEN
        and settings.SMS_TWILIO_FROM_NUMBER
    ):
        raise VerificationError('La configuration Twilio est incomplete.')

    url = (
        f'https://api.twilio.com/2010-04-01/Accounts/'
        f'{settings.SMS_TWILIO_ACCOUNT_SID}/Messages.json'
    )
    payload = parse.urlencode(
        {
            'To': phone_number,
            'From': settings.SMS_TWILIO_FROM_NUMBER,
            'Body': message,
        }
    ).encode()
    credentials = (
        f'{settings.SMS_TWILIO_ACCOUNT_SID}:{settings.SMS_TWILIO_AUTH_TOKEN}'
    ).encode()
    auth_header = base64.b64encode(credentials).decode()
    http_request = urllib_request.Request(
        url,
        data=payload,
        method='POST',
        headers={'Authorization': f'Basic {auth_header}'},
    )
    with urllib_request.urlopen(http_request, timeout=15):
        return


def _get_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def _get_latest_challenge(user, channel, purpose=VerificationChallenge.Purpose.SIGNUP):
    return (
        VerificationChallenge.objects.filter(
            user=user,
            channel=channel,
            purpose=purpose,
            verified_at__isnull=True,
        )
        .order_by('-created_at')
        .first()
    )


def _ensure_resend_allowed(user, channel, purpose=VerificationChallenge.Purpose.SIGNUP):
    latest = _get_latest_challenge(user, channel, purpose)
    if not latest:
        return

    cooldown = settings.VERIFICATION_RESEND_COOLDOWN_SECONDS
    remaining = cooldown - int((timezone.now() - latest.created_at).total_seconds())
    if remaining > 0:
        raise VerificationThrottled(
            f'Patientez encore {remaining} seconde{"s" if remaining > 1 else ""} avant un nouvel envoi.'
        )


def _create_challenge(user, channel, destination, purpose=VerificationChallenge.Purpose.SIGNUP):
    VerificationChallenge.objects.filter(
        user=user,
        channel=channel,
        purpose=purpose,
        verified_at__isnull=True,
    ).delete()

    code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
    challenge = VerificationChallenge.objects.create(
        user=user,
        channel=channel,
        purpose=purpose,
        destination=destination,
        code_hash=make_password(code),
        expires_at=timezone.now() + timedelta(minutes=settings.VERIFICATION_CODE_TTL_MINUTES),
    )
    return challenge, code


def build_email_verification_token(user):
    return signing.dumps(
        {
            'user_id': user.pk,
            'email': user.email,
        },
        salt='accounts.email-verification',
    )


def build_email_verification_url(user, request=None):
    token = build_email_verification_token(user)
    path = f"{reverse('verify_email')}?token={parse.quote(token)}"
    return _build_absolute_url(path, request=request)


def issue_signup_verifications(user, request=None):
    profile = _get_profile(user)
    email_challenge, email_code = _create_challenge(
        user,
        VerificationChallenge.Channel.EMAIL,
        user.email,
    )
    sms_challenge, sms_code = _create_challenge(
        user,
        VerificationChallenge.Channel.SMS,
        profile.phone_number or '',
    )

    send_signup_verification_email(user, email_code, request=request)
    send_signup_verification_sms(user, sms_code)
    return email_challenge, sms_challenge


def resend_signup_email(user, request=None):
    _ensure_resend_allowed(user, VerificationChallenge.Channel.EMAIL)
    challenge, code = _create_challenge(
        user,
        VerificationChallenge.Channel.EMAIL,
        user.email,
    )
    send_signup_verification_email(user, code, request=request)
    return challenge


def resend_signup_sms(user):
    profile = _get_profile(user)
    _ensure_resend_allowed(user, VerificationChallenge.Channel.SMS)
    challenge, code = _create_challenge(
        user,
        VerificationChallenge.Channel.SMS,
        profile.phone_number or '',
    )
    send_signup_verification_sms(user, code)
    return challenge


def send_signup_verification_email(user, email_code, request=None):
    verification_url = build_email_verification_url(user, request=request)
    context = {
        'platform_name': settings.PLATFORM_NAME,
        'user': user,
        'email_code': email_code,
        'verification_url': verification_url,
        'support_email': settings.TRANSACTIONAL_FROM_EMAIL,
        'code_ttl_minutes': settings.VERIFICATION_CODE_TTL_MINUTES,
    }
    send_templated_email(
        subject=f'Confirmez votre adresse email sur {settings.PLATFORM_NAME}',
        recipient_list=[user.email],
        template_prefix='accounts/emails/signup_verification',
        context=context,
    )


def send_signup_verification_sms(user, sms_code):
    profile = _get_profile(user)
    send_sms_message(
        profile.phone_number,
        (
            f'{settings.PLATFORM_NAME} : votre code de verification est {sms_code}. '
            f'Il expire dans {settings.VERIFICATION_CODE_TTL_MINUTES} minutes.'
        ),
    )


def verify_email_token(token):
    try:
        payload = signing.loads(
            token,
            salt='accounts.email-verification',
            max_age=settings.EMAIL_VERIFICATION_LINK_MAX_AGE,
        )
    except SignatureExpired as exc:
        raise VerificationExpired(
            'Le lien de confirmation email a expire. Demandez un nouvel envoi.'
        ) from exc
    except BadSignature as exc:
        raise VerificationInvalid('Le lien de confirmation email est invalide.') from exc

    try:
        user = User.objects.get(pk=payload['user_id'], email=payload['email'])
    except User.DoesNotExist as exc:
        raise VerificationInvalid('Le compte associe a ce lien est introuvable.') from exc

    profile = _get_profile(user)
    profile.mark_email_verified()
    VerificationChallenge.objects.filter(
        user=user,
        channel=VerificationChallenge.Channel.EMAIL,
        purpose=VerificationChallenge.Purpose.SIGNUP,
        verified_at__isnull=True,
    ).update(verified_at=timezone.now())
    return user


def verify_sms_code(user, submitted_code):
    challenge = _get_latest_challenge(user, VerificationChallenge.Channel.SMS)
    if not challenge:
        raise VerificationInvalid('Aucun code SMS actif n est disponible pour ce compte.')

    if challenge.verified_at:
        raise VerificationInvalid('Ce code SMS a deja ete utilise.')

    if challenge.expires_at <= timezone.now():
        raise VerificationExpired('Le code SMS a expire. Demandez un nouvel envoi.')

    if challenge.attempts >= settings.VERIFICATION_MAX_ATTEMPTS:
        raise VerificationInvalid('Le nombre maximal d essais a ete atteint. Demandez un nouveau code.')

    if not check_password(submitted_code, challenge.code_hash):
        challenge.attempts += 1
        challenge.save(update_fields=['attempts', 'updated_at'])
        raise VerificationInvalid('Le code SMS saisi est incorrect.')

    challenge.verified_at = timezone.now()
    challenge.save(update_fields=['verified_at', 'updated_at'])

    profile = _get_profile(user)
    profile.mark_phone_verified()
    return True


def activate_user_if_ready(user):
    profile = _get_profile(user)
    if user.is_active or not profile.is_fully_verified:
        return False

    user.is_active = True
    user.save(update_fields=['is_active'])
    send_welcome_email(user)
    return True


def send_welcome_email(user):
    context = {
        'platform_name': settings.PLATFORM_NAME,
        'user': user,
        'dashboard_url': _build_absolute_url(reverse('dashboard')),
    }
    send_templated_email(
        subject=f'Bienvenue sur {settings.PLATFORM_NAME}',
        recipient_list=[user.email],
        template_prefix='accounts/emails/welcome',
        context=context,
    )


def send_listing_submission_notification(listing):
    owner = listing.owner
    if not owner.email:
        return

    context = {
        'platform_name': settings.PLATFORM_NAME,
        'user': owner,
        'listing': listing,
        'dashboard_url': _build_absolute_url(reverse('dashboard')),
        'listing_url': _build_absolute_url(listing.get_absolute_url()),
    }
    send_templated_email(
        subject=f'Votre annonce est en attente de validation sur {settings.PLATFORM_NAME}',
        recipient_list=[owner.email],
        template_prefix='accounts/emails/listing_submission',
        context=context,
    )


def send_listing_approved_notification(listing):
    owner = listing.owner
    if not owner.email:
        return

    context = {
        'platform_name': settings.PLATFORM_NAME,
        'user': owner,
        'listing': listing,
        'dashboard_url': _build_absolute_url(reverse('dashboard')),
        'listing_url': _build_absolute_url(listing.get_absolute_url()),
    }
    send_templated_email(
        subject=f'Votre annonce a ete validee sur {settings.PLATFORM_NAME}',
        recipient_list=[owner.email],
        template_prefix='accounts/emails/listing_approved',
        context=context,
    )


def send_contact_notifications(contact, listing, is_update=False):
    owner_email = listing.owner.email or listing.owner_email
    owner_display_name = listing.owner.get_full_name() or listing.owner.username
    requester_name = contact.from_user.get_full_name() or contact.from_user.username

    owner_context = {
        'platform_name': settings.PLATFORM_NAME,
        'listing': listing,
        'contact': contact,
        'owner_display_name': owner_display_name,
        'requester_name': requester_name,
        'listing_url': _build_absolute_url(listing.get_absolute_url()),
    }
    send_templated_email(
        subject=(
            f'{"Mise a jour" if is_update else "Nouvelle demande"} de contact pour "{listing.title}"'
        ),
        recipient_list=[owner_email],
        template_prefix='accounts/emails/contact_owner_notification',
        context=owner_context,
    )

    requester_context = {
        'platform_name': settings.PLATFORM_NAME,
        'listing': listing,
        'contact': contact,
        'owner_display_name': owner_display_name,
        'listing_url': _build_absolute_url(listing.get_absolute_url()),
    }
    send_templated_email(
        subject=f'Confirmation de votre demande sur {settings.PLATFORM_NAME}',
        recipient_list=[contact.email],
        template_prefix='accounts/emails/contact_request_confirmation',
        context=requester_context,
    )
