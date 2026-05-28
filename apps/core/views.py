import csv
import json
from datetime import timedelta
from functools import wraps
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.core.mail import send_mail
from django.conf import settings
from apps.listings.models import Listing
from .forms import FinancialTransactionForm, SellerRequestForm
from .models import ContactMessage, EstimateEvent, FinancialTransaction, SellerRequest, SellerRequestImage

User = get_user_model()

# Chemin vers le CSV des prix immobiliers
_CSV_PATH = Path(settings.BASE_DIR) / 'données_estimation' / 'real_estate_prices.csv'


def _load_price_data():
    """
    Lit le CSV et retourne un dict structuré :
    {
      "Casablanca": [
        {"district": "Val Fleuri", "apt": 13297, "villa": 9271},
        {"district": "Ain Diab",   "apt": 24520, "villa": 10191},
        ...
      ],
      ...
    }
    Les valeurs "-" sont stockées comme None.
    """
    data = {}
    try:
        with open(_CSV_PATH, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                city = row['city'].strip()
                district = row['district'].strip()

                def parse(val):
                    v = val.strip() if val else '-'
                    try:
                        return int(float(v))
                    except (ValueError, TypeError):
                        return None

                apt = parse(row.get('apartment_price_per_m2', '-'))
                villa = parse(row.get('villa_price_per_m2', '-'))

                if city not in data:
                    data[city] = []
                data[city].append({
                    'district': district,
                    'apt': apt,
                    'villa': villa,
                })
    except FileNotFoundError:
        pass
    return data


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


def staff_required(view_func):
    """Redirige les anonymes vers login, lève 403 pour les connectés sans accès staff."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped


def home(request):
    featured_listings = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .prefetch_related('images')
        .order_by('-is_featured', '-created_at')[:6]
    )
    context = {
        'featured_listings': featured_listings,
    }
    return render(request, 'core/home.html', context)


def about(request):
    context = {}
    return render(request, 'core/about.html', context)


def buy(request):
    listings = Listing.objects.filter(
        status=Listing.Status.PUBLISHED,
        listing_type=Listing.ListingType.SALE,
    ).prefetch_related('images').order_by('-created_at')

    available_cities = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .values_list('city', flat=True)
        .distinct()
        .order_by('city')
    )

    context = {
        'listings': listings,
        'page_title': 'Acheter',
        'available_cities': available_cities,
        'property_types': Listing.PropertyType.choices,
        'default_listing_type': 'sale',
    }
    return render(request, 'core/buy.html', context)


def rent(request):
    listings = Listing.objects.filter(
        status=Listing.Status.PUBLISHED,
        listing_type=Listing.ListingType.RENT,
    ).prefetch_related('images').order_by('-created_at')

    available_cities = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .values_list('city', flat=True)
        .distinct()
        .order_by('city')
    )

    context = {
        'listings': listings,
        'page_title': 'Louer',
        'available_cities': available_cities,
        'property_types': Listing.PropertyType.choices,
        'default_listing_type': 'rent',
    }
    return render(request, 'core/rent.html', context)


def estimate(request):
    price_data = _load_price_data()
    context = {
        'page_title': 'Estimer votre bien',
        'price_data_json': json.dumps(price_data, ensure_ascii=False),
        'cities': sorted(price_data.keys()),
    }
    return render(request, 'core/estimate.html', context)


def sell(request):
    price_data = _load_price_data()
    cities = sorted(price_data.keys())

    if request.method == 'POST':
        form = SellerRequestForm(request.POST)
        if form.is_valid():
            seller_request = form.save(commit=False)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            seller_request.ip_address = (
                x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            )
            seller_request.save()

            for image_file in request.FILES.getlist('photos'):
                SellerRequestImage.objects.create(
                    seller_request=seller_request,
                    image=image_file,
                )

            messages.success(
                request,
                'Votre demande a bien été envoyée ! Notre équipe vous contactera sous 24h.',
            )
            return redirect('sell')

        messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = SellerRequestForm()

    context = {
        'page_title': 'Vendre votre bien',
        'form': form,
        'cities': cities,
    }
    return render(request, 'core/sell.html', context)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '')
        message_text = request.POST.get('message', '').strip()

        if not all([name, email, phone, subject, message_text]):
            messages.error(request, 'Tous les champs sont obligatoires.')
            return redirect('contact')

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        contact_msg = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text,
            ip_address=ip
        )

        try:
            subject_display = dict(ContactMessage.SUBJECT_CHOICES).get(subject, 'Autre')
            admin_email = settings.DEFAULT_FROM_EMAIL or 'admin@yalaz-immo.com'

            email_body = f"""
Nouveau message de contact de Yalaz:

Nom: {name}
Email: {email}
Téléphone: {phone}
Sujet: {subject_display}

Message:
{message_text}

---
Message ID: {contact_msg.id}
Adresse IP: {ip}
            """

            send_mail(
                f'Nouveau message de contact - {subject_display}',
                email_body,
                settings.DEFAULT_FROM_EMAIL or 'contact@yalaz-immo.com',
                [admin_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending email: {e}")

        messages.success(request, 'Votre message a été envoyé avec succès. Nous vous recontacterons bientôt!')
        return redirect('contact')

    context = {
        'page_title': 'Nous Contacter',
    }
    return render(request, 'core/contact.html', context)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_staff_user(self.request.user)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


def financial_queryset(request):
    queryset = FinancialTransaction.objects.select_related(
        'created_by',
        'assigned_to',
        'listing',
    )

    type_filter = request.GET.get('type', '').strip()
    status_filter = request.GET.get('status', '').strip()
    category_filter = request.GET.get('category', '').strip()
    listing_filter = request.GET.get('listing', '').strip()
    staff_filter = request.GET.get('staff', '').strip()

    if type_filter:
        queryset = queryset.filter(type=type_filter)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if category_filter:
        queryset = queryset.filter(category=category_filter)
    if listing_filter:
        queryset = queryset.filter(listing_id=listing_filter)
    if staff_filter:
        queryset = queryset.filter(assigned_to_id=staff_filter)

    return queryset


def _compute_summary(queryset):
    completed = queryset.filter(status='completed')
    total_entries = completed.filter(type='entry').aggregate(total=Sum('amount'))['total'] or 0
    total_exits = completed.filter(type='exit').aggregate(total=Sum('amount'))['total'] or 0
    total_commissions = completed.filter(
        type='entry',
        category__in=['commission_vente', 'commission_location']
    ).aggregate(total=Sum('amount'))['total'] or 0
    return {
        'total_entries': total_entries,
        'total_exits': total_exits,
        'balance': total_entries - total_exits,
        'total_commissions': total_commissions,
    }


@staff_required
def financial_dashboard(request):
    date_filter = request.GET.get('date_range', '30')
    try:
        days = int(date_filter)
    except ValueError:
        days = 30

    start_date = timezone.localdate() - timedelta(days=days)
    transactions = financial_queryset(request).filter(transaction_date__gte=start_date)
    summary = _compute_summary(transactions)

    context = {
        'transactions': transactions[:10],
        'total_count': transactions.count(),
        'date_filter': str(days),
        'type_filter': request.GET.get('type', '').strip(),
        'status_filter': request.GET.get('status', '').strip(),
        **summary,
    }
    return render(request, 'admin/financial_dashboard.html', context)


@staff_required
def financial_stats_api(request):
    transactions = financial_queryset(request)
    summary = _compute_summary(transactions)
    return JsonResponse({
        'total_entries': float(summary['total_entries']),
        'total_exits': float(summary['total_exits']),
        'balance': float(summary['balance']),
        'total_commissions': float(summary['total_commissions']),
        'total_count': transactions.count(),
    })


@require_POST
def estimate_track_api(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = {}
    EstimateEvent.objects.create(
        city=str(data.get('city', ''))[:100],
        district=str(data.get('district', ''))[:100],
        property_type=str(data.get('property_type', ''))[:50],
        surface=data.get('surface') or None,
    )
    return JsonResponse({'ok': True})


class FinancialTransactionListView(StaffRequiredMixin, ListView):
    model = FinancialTransaction
    template_name = 'admin/financial_transactions_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = financial_queryset(self.request)
        search = self.request.GET.get('search', '').strip()
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()

        if search:
            queryset = queryset.filter(
                Q(description__icontains=search)
                | Q(created_by__first_name__icontains=search)
                | Q(created_by__last_name__icontains=search)
                | Q(assigned_to__first_name__icontains=search)
                | Q(assigned_to__last_name__icontains=search)
                | Q(listing__title__icontains=search)
            )
        if date_from:
            queryset = queryset.filter(transaction_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(transaction_date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        full_qs = self.get_queryset()
        summary = _compute_summary(full_qs)

        context.update({
            'search': self.request.GET.get('search', '').strip(),
            'type_filter': self.request.GET.get('type', '').strip(),
            'status_filter': self.request.GET.get('status', '').strip(),
            'category_filter': self.request.GET.get('category', '').strip(),
            'listing_filter': self.request.GET.get('listing', '').strip(),
            'staff_filter': self.request.GET.get('staff', '').strip(),
            'date_from': self.request.GET.get('date_from', '').strip(),
            'date_to': self.request.GET.get('date_to', '').strip(),
            'listings': Listing.objects.filter(status='published').order_by('title'),
            'staff_members': User.objects.filter(is_staff=True).order_by('first_name', 'last_name'),
            'category_choices': FinancialTransaction.CATEGORY_CHOICES,
            **summary,
        })
        return context


class FinancialTransactionCreateView(StaffRequiredMixin, CreateView):
    model = FinancialTransaction
    form_class = FinancialTransactionForm
    template_name = 'admin/financial_transaction_form.html'
    success_url = reverse_lazy('financial_transactions_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Transaction créée avec succès.')
        return super().form_valid(form)


class FinancialTransactionUpdateView(StaffRequiredMixin, UpdateView):
    model = FinancialTransaction
    form_class = FinancialTransactionForm
    template_name = 'admin/financial_transaction_form.html'
    success_url = reverse_lazy('financial_transactions_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Transaction mise à jour avec succès.')
        return super().form_valid(form)


class FinancialTransactionDetailView(StaffRequiredMixin, DetailView):
    model = FinancialTransaction
    template_name = 'admin/financial_transaction_detail.html'
    context_object_name = 'transaction'


class FinancialTransactionDeleteView(StaffRequiredMixin, DeleteView):
    model = FinancialTransaction
    template_name = 'admin/financial_transaction_confirm_delete.html'
    success_url = reverse_lazy('financial_transactions_list')

    def form_valid(self, form):
        messages.success(self.request, 'Transaction supprimée avec succès.')
        return super().form_valid(form)


@staff_required
def admin_seller_requests(request):
    status_filter = request.GET.get('status', '')
    qs = SellerRequest.objects.prefetch_related('images')

    if status_filter:
        qs = qs.filter(status=status_filter)

    context = {
        'seller_requests': qs,
        'status_choices': SellerRequest.STATUS_CHOICES,
        'current_status': status_filter,
        'new_count': SellerRequest.objects.filter(status='new').count(),
    }
    return render(request, 'admin/seller_requests.html', context)


@staff_required
def admin_seller_request_detail(request, request_id):
    seller_request = get_object_or_404(SellerRequest, id=request_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_note = request.POST.get('admin_note', '')

        if action in ('new', 'in_progress', 'accepted', 'rejected'):
            seller_request.status = action
            seller_request.admin_note = admin_note
            seller_request.save()
            messages.success(request, f'Statut mis à jour : {seller_request.get_status_display()}')

        elif action == 'save_note':
            seller_request.admin_note = admin_note
            seller_request.save()
            messages.success(request, 'Note interne enregistrée.')

        elif action == 'delete':
            seller_request.delete()
            messages.success(request, 'Demande supprimée.')
            return redirect('admin_seller_requests')

        return redirect('admin_seller_request_detail', request_id=seller_request.id)

    context = {
        'seller_request': seller_request,
        'status_choices': SellerRequest.STATUS_CHOICES,
    }
    return render(request, 'admin/seller_request_detail.html', context)


@staff_required
def admin_contact_messages(request):
    status_filter = request.GET.get('status', '')
    qs = ContactMessage.objects.all()

    if status_filter == 'unread':
        qs = qs.filter(is_read=False)
    elif status_filter == 'read':
        qs = qs.filter(is_read=True)

    context = {
        'contact_messages': qs,
        'current_status': status_filter,
        'unread_count': ContactMessage.objects.filter(is_read=False).count(),
    }
    return render(request, 'admin/contact_messages.html', context)


@staff_required
def admin_contact_message_detail(request, message_id):
    contact_msg = get_object_or_404(ContactMessage, id=message_id)

    if not contact_msg.is_read:
        contact_msg.is_read = True
        contact_msg.save(update_fields=['is_read'])

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_unread':
            contact_msg.is_read = False
            contact_msg.save(update_fields=['is_read'])
            messages.success(request, 'Message marqué comme non lu.')
        elif action == 'delete':
            contact_msg.delete()
            messages.success(request, 'Message supprimé.')
            return redirect('admin_contact_messages')
        return redirect('admin_contact_message_detail', message_id=contact_msg.id)

    context = {'contact_msg': contact_msg}
    return render(request, 'admin/contact_message_detail.html', context)


def csrf_failure(request, reason=''):
    return render(request, '403.html', {'reason': reason}, status=403)


def mentions_legales(request):
    return render(request, 'core/mentions_legales.html')


def politique_confidentialite(request):
    return render(request, 'core/politique_confidentialite.html')


def politique_cookies(request):
    return render(request, 'core/politique_cookies.html')


def cgu(request):
    return render(request, 'core/cgu.html')
