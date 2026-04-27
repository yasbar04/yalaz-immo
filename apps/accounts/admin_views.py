from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import Q, Count
from django.utils.timezone import now
from datetime import timedelta
from apps.listings.models import Listing, Report, Favorite
from django.contrib import messages
from django import forms

from .services import send_listing_approved_notification

def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.groups.filter(name='Administrators').exists()


def is_superuser(user):
    """Check if user is superuser"""
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard admin avec stats"""
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
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_listings(request):
    """Gérer toutes les annonces"""
    status_filter = request.GET.get('status', '')
    listings = Listing.objects.all().select_related('owner')
    
    if status_filter:
        listings = listings.filter(status=status_filter)
    
    context = {
        'listings': listings,
        'status_choices': Listing.Status.choices,
        'current_status': status_filter,
    }
    
    return render(request, 'admin/listings.html', context)


@login_required
@user_passes_test(is_admin)
def admin_listing_detail(request, pk):
    """Détails d'une annonce pour l'admin"""
    listing = get_object_or_404(Listing, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            should_notify_approval = listing.status != Listing.Status.PUBLISHED
            listing.status = Listing.Status.PUBLISHED
            listing.save()
            if should_notify_approval:
                try:
                    send_listing_approved_notification(listing)
                except Exception:
                    messages.warning(
                        request,
                        'Annonce publiee, mais l email de validation n a pas pu etre envoye.',
                    )
            messages.success(request, f'Annonce "{listing.title}" publiée')
            
        elif action == 'reject':
            listing.status = Listing.Status.REJECTED
            listing.save()
            messages.success(request, f'Annonce "{listing.title}" refusée')
            
        elif action == 'feature':
            listing.is_featured = not listing.is_featured
            listing.save()
            status = "mise en avant" if listing.is_featured else "retirée de la mise en avant"
            messages.success(request, f'Annonce {status}')
            
        elif action == 'delete':
            title = listing.title
            listing.delete()
            messages.success(request, f'Annonce "{title}" supprimée')
            return redirect('admin_listings')
        
        return redirect('admin_listing_detail', pk=listing.pk)
    
    context = {
        'listing': listing,
        'status_choices': Listing.Status.choices,
    }
    
    return render(request, 'admin/listing_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """Gérer les utilisateurs"""
    search = request.GET.get('search', '')
    users = User.objects.all()
    
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search))
    
    context = {
        'users': users,
        'search': search,
    }
    
    return render(request, 'admin/users.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """Détails d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'make_admin':
            user.is_superuser = True
            user.is_staff = True
            user.save()
            admin_group, _ = Group.objects.get_or_create(name='Administrators')
            user.groups.add(admin_group)
            messages.success(request, f'{user.username} est maintenant admin')
            
        elif action == 'remove_admin':
            user.is_superuser = False
            user.is_staff = False
            user.save()
            admin_group = Group.objects.filter(name='Administrators').first()
            if admin_group:
                user.groups.remove(admin_group)
            messages.success(request, f'{user.username} n\'est plus admin')
            
        elif action == 'delete':
            username = user.username
            user.delete()
            messages.success(request, f'Utilisateur "{username}" supprimé')
            return redirect('admin_users')
        
        return redirect('admin_user_detail', user_id=user.id)
    
    user_listings = Listing.objects.filter(owner=user)
    user_reports_count = Report.objects.filter(Q(reporter=user) | Q(reported_user=user)).count()
    
    context = {
        'user': user,
        'user_listings': user_listings,
        'user_reports_count': user_reports_count,
        'is_admin_user': user.is_superuser or user.groups.filter(name='Administrators').exists(),
    }
    
    return render(request, 'admin/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    """Gérer les signalements"""
    status_filter = request.GET.get('status', 'pending')
    reports = Report.objects.all()
    
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    context = {
        'reports': reports,
        'status_choices': Report.Status.choices,
        'current_status': status_filter,
    }
    
    return render(request, 'admin/reports.html', context)


@login_required
@user_passes_test(is_admin)
def admin_report_detail(request, report_id):
    """Détails d'un signalement"""
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_note = request.POST.get('admin_note', '')
        
        if action == 'resolve':
            if report.listing:
                report.listing.delete()
                messages.success(request, f'Annonce supprimée')
            report.status = Report.Status.RESOLVED
            report.admin_note = admin_note
            report.save()
            messages.success(request, 'Signalement résolu')
            
        elif action == 'dismiss':
            report.status = Report.Status.DISMISSED
            report.admin_note = admin_note
            report.save()
            messages.info(request, 'Signalement rejeté')
            
        elif action == 'review':
            report.status = Report.Status.REVIEWED
            report.admin_note = admin_note
            report.save()
            messages.info(request, 'Signalement marqué comme examiné')
        
        return redirect('admin_reports')
    
    context = {
        'report': report,
        'status_choices': Report.Status.choices,
    }
    
    return render(request, 'admin/report_detail.html', context)


# Vues pour utilisateurs normaux

@login_required
def report_content(request, listing_id=None, user_id=None):
    """Signaler un contenu"""
    listing = None
    reported_user = None
    
    if listing_id:
        listing = get_object_or_404(Listing, id=listing_id)
    if user_id:
        reported_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        reason = request.POST.get('reason')
        
        Report.objects.create(
            reporter=request.user,
            listing=listing,
            reported_user=reported_user,
            report_type=report_type,
            reason=reason,
        )
        
        messages.success(request, 'Merci ! Votre signalement a été envoyé à notre équipe.')
        
        if listing:
            return redirect('listing_detail', pk=listing.id)
        return redirect('listing_list')
    
    context = {
        'listing': listing,
        'reported_user': reported_user,
        'report_types': Report.ReportType.choices,
    }
    
    return render(request, 'report_form.html', context)


@login_required
def toggle_favorite(request, listing_id):
    """Ajouter/retirer des favoris"""
    listing = get_object_or_404(Listing, id=listing_id)
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        listing=listing
    )
    
    if not created:
        favorite.delete()
        messages.info(request, 'Annonce retiree des favoris')
    else:
        messages.success(request, 'Annonce ajoutée aux favoris')
    
    return redirect('listing_detail', pk=listing.id)


@login_required
def favorites(request):
    """Liste des favoris"""
    favorites = (
        Favorite.objects.filter(user=request.user)
        .select_related('listing')
        .prefetch_related('listing__images', 'listing__contacts')
    )
    listings = [fav.listing for fav in favorites]
    
    context = {
        'listings': listings,
        'page_title': 'Mes Favoris',
    }
    
    return render(request, 'favorites.html', context)


# Superadmin staff management


@login_required
@user_passes_test(is_superuser)
def admin_staff_list(request):
    """Lister tous les utilisateurs staff"""
    staff_users = User.objects.filter(is_staff=True).annotate(
        published_count=Count('listings', filter=models.Q(listings__status=Listing.Status.PUBLISHED))
    ).order_by('-date_joined')
    
    context = {
        'staff_users': staff_users,
    }
    
    return render(request, 'admin/staff_list.html', context)


class StaffForm(forms.ModelForm):
    """Formulaire pour créer/modifier un utilisateur staff"""
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text='Laissez vide pour ne pas changer le mot de passe'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text='Confirmation du mot de passe'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        
        return cleaned_data


@login_required
@user_passes_test(is_superuser)
def admin_staff_create(request):
    """Créer un nouvel utilisateur staff"""
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            
            user.save()
            
            # Activer le flag de changement de mot de passe obligatoire
            user.profile.password_change_required = True
            user.profile.save()
            
            messages.success(request, f"Utilisateur staff '{user.username}' créé avec succès. Il devra changer son mot de passe à la première connexion.")
            return redirect('admin_staff_list')
    else:
        form = StaffForm()
    
    context = {
        'form': form,
        'page_title': 'Ajouter un nouvel utilisateur staff',
        'submit_label': 'Créer le compte',
    }
    
    return render(request, 'admin/staff_form.html', context)


@login_required
@user_passes_test(is_superuser)
def admin_staff_edit(request, user_id):
    """Modifier un utilisateur staff"""
    user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            
            user.save()
            messages.success(request, f"Utilisateur staff '{user.username}' modifié avec succès")
            return redirect('admin_staff_list')
    else:
        form = StaffForm(instance=user)
    
    context = {
        'form': form,
        'staff_user': user,
        'page_title': f'Modifier {user.get_full_name() or user.username}',
        'submit_label': 'Enregistrer les modifications',
    }
    
    return render(request, 'admin/staff_form.html', context)


@login_required
@user_passes_test(is_superuser)
def admin_staff_delete(request, user_id):
    """Supprimer un utilisateur staff"""
    user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Utilisateur staff '{username}' supprimé")
        return redirect('admin_staff_list')
    
    context = {
        'staff_user': user,
    }
    
    return render(request, 'admin/staff_delete_confirm.html', context)


# Changement de mot de passe obligatoire


class PasswordChangeRequiredForm(forms.Form):
    """Formulaire pour le changement de mot de passe obligatoire"""
    new_password1 = forms.CharField(
        label='Nouveau mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre nouveau mot de passe'}),
        min_length=8,
    )
    new_password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez votre mot de passe'}),
        min_length=8,
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        
        return cleaned_data


@login_required
def change_password_required(request):
    """Vue pour forcer le changement de mot de passe à la première connexion"""
    # Vérifier si l'utilisateur doit changer son mot de passe
    if not hasattr(request.user, 'profile') or not request.user.profile.password_change_required:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PasswordChangeRequiredForm(request.POST)
        if form.is_valid():
            # Changer le mot de passe
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            
            # Désactiver le flag
            request.user.profile.password_change_required = False
            request.user.profile.save()
            
            # Réauthentifier l'utilisateur avec le nouveau mot de passe
            from django.contrib.auth import authenticate, login as auth_login
            user = authenticate(username=request.user.username, password=form.cleaned_data['new_password1'])
            if user is not None:
                auth_login(request, user)
            
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('dashboard')
    else:
        form = PasswordChangeRequiredForm()
    
    context = {
        'form': form,
        'page_title': 'Changez votre mot de passe',
    }
    
    return render(request, 'accounts/change_password_required.html', context)
