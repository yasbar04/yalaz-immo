from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import redirect, render

from apps.listings.models import Contact, Listing

from .forms import (
    SMSVerificationForm,
    SignUpForm,
    UserProfileForm,
    VerificationRecoveryForm,
    LoginForm,
)
from .models import UserProfile
from .services import (
    VerificationError,
    activate_user_if_ready,
    issue_signup_verifications,
    mask_email_address,
    mask_phone_number,
    resend_signup_email,
    resend_signup_sms,
    verify_email_token,
    verify_sms_code,
)

User = get_user_model()
PENDING_VERIFICATION_SESSION_KEY = 'pending_verification_user_id'


def _is_admin(user):
    """Check if user is admin or staff."""
    return user.is_staff or user.is_superuser


admin_only = user_passes_test(_is_admin, login_url='home', redirect_field_name=None)


def _set_pending_verification_user(request, user):
    request.session[PENDING_VERIFICATION_SESSION_KEY] = user.pk


def _clear_pending_verification_user(request):
    request.session.pop(PENDING_VERIFICATION_SESSION_KEY, None)


def _get_pending_verification_user(request):
    user_id = request.session.get(PENDING_VERIFICATION_SESSION_KEY)
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        _clear_pending_verification_user(request)
        return None


def login_view(request):
    """Admin-only login view."""
    # Check if user is already authenticated
    if request.user.is_authenticated:
        if _is_admin(request.user):
            return redirect('dashboard')
        else:
            logout(request)
            return render(request, 'accounts/admin_only.html', status=403)

    # Show login form
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not _is_admin(user):
                messages.error(request, 'Accès réservé aux membres de l\'équipe Yalaz.')
                return render(request, 'accounts/login.html', {'form': form})

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            if hasattr(user, 'profile') and user.profile.password_change_required:
                return redirect('change_password_required')

            return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@admin_only
def signup_view(request):
    """Admin-only endpoint for user creation."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()

            _set_pending_verification_user(request, user)
            try:
                issue_signup_verifications(user, request=request)
            except Exception:
                messages.warning(
                    request,
                    'Le compte a ete cree, mais un probleme est survenu pendant l envoi des confirmations. '
                    'Vous pourrez relancer les envois depuis l ecran de verification.',
                )
            else:
                messages.success(
                    request,
                    'Votre compte utilisateur a ete cree.',
                )
            return redirect('verify_account')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


@admin_only
def verify_account_view(request):
    """Admin-only endpoint for account verification."""
    user = _get_pending_verification_user(request)
    if user is None:
        return redirect('recover_verification')

    profile, _ = UserProfile.objects.get_or_create(user=user)
    form = SMSVerificationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            verify_sms_code(user, form.cleaned_data['sms_code'])
        except VerificationError as exc:
            messages.error(request, str(exc))
        else:
            if activate_user_if_ready(user):
                _clear_pending_verification_user(request)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(
                    request,
                    'Votre compte est maintenant verifie et actif.',
                )
                return redirect('admin_dashboard')

            messages.success(
                request,
                'Votre numero est confirme. Il ne reste plus qu a valider votre email.',
            )
            return redirect('verify_account')

    return render(
        request,
        'accounts/verify_account.html',
        {
            'form': form,
            'verification_user': user,
            'masked_email': mask_email_address(user.email),
            'masked_phone': mask_phone_number(profile.phone_number),
            'email_verified': profile.is_email_verified,
            'phone_verified': profile.is_phone_verified,
        },
    )


def verify_email_view(request):
    token = request.GET.get('token', '').strip()
    if not token:
        messages.error(request, 'Le lien de confirmation email est incomplet.')
        return redirect('signup')

    try:
        user = verify_email_token(token)
    except VerificationError as exc:
        messages.error(request, str(exc))
        return redirect('signup')

    _set_pending_verification_user(request, user)
    if activate_user_if_ready(user):
        _clear_pending_verification_user(request)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Votre email et votre telephone sont verifies.')
        return redirect('admin_dashboard')

    messages.success(
        request,
        'Votre email est confirme. Saisissez maintenant le code SMS pour finaliser l activation.',
    )
    return redirect('verify_account')


def resend_email_verification_view(request):
    user = _get_pending_verification_user(request)
    if user is None:
        messages.error(request, 'Aucun compte en attente de verification n a ete trouve.')
        return redirect('signup')

    try:
        resend_signup_email(user, request=request)
    except VerificationError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, 'Un nouvel email de confirmation vient d etre envoye.')
    return redirect('verify_account')


def resend_sms_verification_view(request):
    user = _get_pending_verification_user(request)
    if user is None:
        messages.error(request, 'Aucun compte en attente de verification n a ete trouve.')
        return redirect('signup')

    try:
        resend_signup_sms(user)
    except VerificationError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, 'Un nouveau code SMS vient d ete envoye.')
    return redirect('verify_account')


@admin_only
def recover_verification_view(request):
    """Admin-only recovery view."""
    form = VerificationRecoveryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].strip().lower()
        user = (
            User.objects.filter(email__iexact=email, is_active=False)
            .order_by('pk')
            .first()
        )
        if user is None:
            messages.error(
                request,
                'Aucun compte en attente de verification n a ete trouve pour cette adresse email.',
            )
        else:
            _set_pending_verification_user(request, user)
            email_sent = False
            sms_sent = False

            try:
                resend_signup_email(user, request=request)
                email_sent = True
            except VerificationError:
                pass

            try:
                resend_signup_sms(user)
                sms_sent = True
            except VerificationError:
                pass

            if email_sent or sms_sent:
                messages.success(
                    request,
                    'Les confirmations disponibles ont ete relancees. Vous pouvez reprendre la verification.',
                )
            else:
                messages.info(
                    request,
                    'Le compte a ete retrouve. Vous pouvez reprendre la verification ou patienter avant un nouvel envoi.',
                )
            return redirect('verify_account')

    return render(
        request,
        'accounts/recover_verification.html',
        {'form': form},
    )


@admin_only
@login_required
def dashboard(request):
    """User dashboard or staff back office."""
    from django.utils.timezone import now
    from datetime import timedelta
    from apps.listings.models import Listing, Report
    from django.db.models import Q
    
    # Staff users see back office dashboard
    if request.user.is_staff or request.user.is_superuser:
        last_7_days = now() - timedelta(days=7)
        
        stats = {
            'total_users': User.objects.count(),
            'total_listings': Listing.objects.count(),
            'published_listings': Listing.objects.filter(status=Listing.Status.PUBLISHED).count(),
            'pending_listings': Listing.objects.filter(status=Listing.Status.PENDING).count(),
            'pending_reports': Report.objects.filter(status=Report.Status.PENDING).count(),
            'new_users_7days': User.objects.filter(date_joined__gte=last_7_days).count(),
            'new_listings_7days': Listing.objects.filter(created_at__gte=last_7_days).count(),
            'total_admins': User.objects.filter(is_superuser=True).count(),
        }
        
        recent_listings = Listing.objects.all()[:10]
        recent_reports = Report.objects.filter(status=Report.Status.PENDING)[:5]
        pending_listings = Listing.objects.filter(status=Listing.Status.PENDING)[:10]
        
        context = {
            'stats': stats,
            'recent_listings': recent_listings,
            'recent_reports': recent_reports,
            'pending_listings': pending_listings,
            'is_staff_view': True,
        }
        
        return render(request, 'admin/dashboard.html', context)
    
    # Regular user dashboard
    listings = (
        Listing.objects.filter(owner=request.user)
        .prefetch_related('contacts', 'images')
        .order_by('-created_at')
    )
    listings_count = listings.count()
    total_views = sum(listing.views_count for listing in listings)
    total_contacts = sum(listing.contacts.count() for listing in listings)

    return render(
        request,
        'accounts/dashboard.html',
        {
            'listings': listings,
            'listing_stats': listings_count > 0,
            'listings_count': listings_count,
            'total_views': total_views,
            'total_contacts': total_contacts,
        },
    )


@admin_only
def profile_view(request):
    """Admin-only profile view."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_listings = (
        Listing.objects.filter(owner=request.user)
        .prefetch_related('images')
        .order_by('-created_at')
    )
    favorites = (
        request.user.favorites.select_related('listing')
        .prefetch_related('listing__images')
        .order_by('-created_at')
    )

    listings_count = user_listings.count()
    published_count = user_listings.filter(status=Listing.Status.PUBLISHED).count()
    total_views = user_listings.aggregate(total=Sum('views_count'))['total'] or 0
    favorites_count = favorites.count()
    contacts_received = Contact.objects.filter(listing__owner=request.user).count()
    sent_contacts_count = request.user.sent_contacts.count()

    completion_sections = [
        ('Ajouter une photo de profil', bool(profile.avatar)),
        ('Renseigner votre prenom', bool(request.user.first_name)),
        ('Renseigner votre nom', bool(request.user.last_name)),
        ('Ajouter une adresse email', bool(request.user.email)),
        ('Ajouter un numero de telephone', bool(profile.phone_number)),
        ('Ecrire une courte presentation', bool(profile.bio)),
    ]
    completed_items_count = sum(1 for _, is_complete in completion_sections if is_complete)
    completion_percent = round(
        (completed_items_count / len(completion_sections)) * 100
    )
    missing_profile_items = [
        label for label, is_complete in completion_sections if not is_complete
    ]

    return render(
        request,
        'accounts/profile.html',
        {
            'profile': profile,
            'listings_count': listings_count,
            'published_count': published_count,
            'total_views': total_views,
            'favorites_count': favorites_count,
            'contacts_received': contacts_received,
            'sent_contacts_count': sent_contacts_count,
            'completion_percent': completion_percent,
            'completed_items_count': completed_items_count,
            'completion_items_total': len(completion_sections),
            'missing_profile_items': missing_profile_items,
            'recent_listings': user_listings[:3],
            'recent_favorites': favorites[:3],
        },
    )


@admin_only
def profile_edit_view(request):
    """Admin-only profile edit view."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Mettre a jour les informations utilisateur
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()

            # Sauvegarder le profil
            form.save()

            messages.success(
                request,
                'Votre profil a ete mis a jour avec succes!',
            )
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(
        request,
        'accounts/profile_edit.html',
        {'form': form, 'profile': profile},
    )
