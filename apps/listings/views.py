import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

logger = logging.getLogger(__name__)
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import (
    send_contact_notifications,
    send_listing_submission_notification,
)

from .forms import ListingForm, ListingImageFormSet
from .models import Contact, Favorite, Listing, ListingImage, PublicInquiry
from .constants import MOROCCAN_DISTRICTS


def _is_admin(user):
    """Check if user is admin or staff."""
    return user.is_staff or user.is_superuser


admin_only = user_passes_test(_is_admin, login_url='home', redirect_field_name=None)


def listing_list(request):
    qs = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .select_related('owner')
        .prefetch_related('images')
        .order_by('-is_featured', '-created_at')
    )

    city = request.GET.get('city', '').strip()
    district = request.GET.get('district', '').strip()
    listing_type = request.GET.get('listing_type', '').strip()
    property_type = request.GET.get('property_type', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    min_bedrooms = request.GET.get('min_bedrooms', '').strip()
    min_bathrooms = request.GET.get('min_bathrooms', '').strip()
    search = request.GET.get('search', '').strip()
    
    # Amenities filters
    swimming_pool = request.GET.get('swimming_pool', '').strip()
    garden = request.GET.get('garden', '').strip()
    garage = request.GET.get('garage', '').strip()
    parking = request.GET.get('parking', '').strip()
    terrace = request.GET.get('terrace', '').strip()
    balcony = request.GET.get('balcony', '').strip()
    air_conditioning = request.GET.get('air_conditioning', '').strip()
    furnished = request.GET.get('furnished', '').strip()
    kitchen_equipped = request.GET.get('kitchen_equipped', '').strip()
    security = request.GET.get('security', '').strip()

    if city:
        qs = qs.filter(city__icontains=city)
    if district:
        qs = qs.filter(district__icontains=district)
    if listing_type:
        qs = qs.filter(listing_type=listing_type)
    if property_type:
        qs = qs.filter(property_type=property_type)
    if min_price:
        try:
            qs = qs.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(price__lte=float(max_price))
        except ValueError:
            pass
    if min_bedrooms:
        try:
            qs = qs.filter(bedrooms__gte=int(min_bedrooms))
        except ValueError:
            pass
    if min_bathrooms:
        try:
            qs = qs.filter(bathrooms__gte=int(min_bathrooms))
        except ValueError:
            pass
    
    # Apply amenities filters
    if swimming_pool == 'on':
        qs = qs.filter(swimming_pool=True)
    if garden == 'on':
        qs = qs.filter(garden=True)
    if garage == 'on':
        qs = qs.filter(garage=True)
    if parking == 'on':
        qs = qs.filter(parking=True)
    if terrace == 'on':
        qs = qs.filter(terrace=True)
    if balcony == 'on':
        qs = qs.filter(balcony=True)
    if air_conditioning == 'on':
        qs = qs.filter(air_conditioning=True)
    if furnished == 'on':
        qs = qs.filter(furnished=True)
    if kitchen_equipped == 'on':
        qs = qs.filter(kitchen_equipped=True)
    if security == 'on':
        qs = qs.filter(security=True)
    
    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(city__icontains=search)
            | Q(district__icontains=search)
            | Q(reference__icontains=search)
        )

    sort = request.GET.get('sort', '-created_at')
    if sort in ['-created_at', 'created_at', '-price', 'price']:
        qs = qs.order_by(sort)

    # Get all available cities with published listings
    available_cities = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED)
        .values_list('city', flat=True)
        .distinct()
        .order_by('city')
    )

    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page', 1)
    listings = paginator.get_page(page_number)

    # Get available districts for the selected city (if any)
    available_districts = []
    if city:
        available_districts = (
            Listing.objects.filter(status=Listing.Status.PUBLISHED, city__icontains=city)
            .values_list('district', flat=True)
            .distinct()
            .order_by('district')
        )

    context = {
        'listings': listings,
        'property_types': Listing.PropertyType.choices,
        'listing_types': Listing.ListingType.choices,
        'available_cities': available_cities,
        'available_districts': available_districts,
        'filters': {
            'city': city,
            'district': district,
            'listing_type': listing_type,
            'property_type': property_type,
            'min_price': min_price,
            'max_price': max_price,
            'min_bedrooms': min_bedrooms,
            'min_bathrooms': min_bathrooms,
            'search': search,
            'sort': sort,
            'swimming_pool': swimming_pool,
            'garden': garden,
            'garage': garage,
            'parking': parking,
            'terrace': terrace,
            'balcony': balcony,
            'air_conditioning': air_conditioning,
            'furnished': furnished,
            'kitchen_equipped': kitchen_equipped,
            'security': security,
        },
    }
    return render(request, 'listings/listing_list.html', context)


def listing_detail(request, pk):
    listing = get_object_or_404(
        Listing.objects.select_related('owner').prefetch_related(
            'images',
            'contacts__from_user',
        ),
        pk=pk,
    )

    is_allowed_private_view = (
        request.user.is_authenticated
        and (listing.owner == request.user or request.user.is_staff)
    )
    if listing.status != Listing.Status.PUBLISHED and not is_allowed_private_view:
        return render(
            request,
            '403.html',
            {
                'title': 'Annonce indisponible',
                'message': 'Cette annonce n est pas accessible publiquement pour le moment.',
                'suggestion': 'Retournez au catalogue ou reconnectez-vous avec le compte proprietaire.',
            },
            status=403,
        )

    if not request.user.is_authenticated or listing.owner != request.user:
        listing.views_count += 1
        listing.save(update_fields=['views_count'])

    contact_sent = False
    is_favorite = False
    if request.user.is_authenticated:
        contact_sent = Contact.objects.filter(
            listing=listing,
            from_user=request.user,
        ).exists()
        is_favorite = Favorite.objects.filter(
            listing=listing,
            user=request.user,
        ).exists()

    gallery_images = []
    if listing.image:
        gallery_images.append(
            {
                'url': listing.image.url,
                'alt': listing.title,
            }
        )

    for image in listing.images.all():
        gallery_images.append(
            {
                'url': image.image.url,
                'alt': image.alt_text or listing.title,
            }
        )

    amenities = []
    amenity_map = [
        ('Cuisine equipee', listing.kitchen_equipped),
        ('Piscine', listing.swimming_pool),
        ('Jardin', listing.garden),
        ('Garage', listing.garage),
        ('Parking', listing.parking),
        ('Terrasse', listing.terrace),
        ('Balcon', listing.balcony),
        ('Climatisation', listing.air_conditioning),
        ('Meuble', listing.furnished),
        ('Gardiennage/Securite', listing.security),
    ]
    for label, is_available in amenity_map:
        if is_available:
            amenities.append(label)

    contact_methods = []
    if listing.owner_email:
        contact_methods.append(
            {
                'label': 'Email',
                'value': listing.owner_email,
                'href': f'mailto:{listing.owner_email}',
                'is_external': False,
            }
        )
    if listing.owner_phone:
        contact_methods.append(
            {
                'label': 'Telephone',
                'value': listing.owner_phone,
                'href': f'tel:{listing.owner_phone}',
                'is_external': False,
            }
        )
    if listing.owner_whatsapp:
        whatsapp_number = listing.owner_whatsapp.lstrip('+')
        contact_methods.append(
            {
                'label': 'WhatsApp',
                'value': listing.owner_whatsapp,
                'href': f'https://wa.me/{whatsapp_number}',
                'is_external': True,
            }
        )

    detail_metrics = [
        {
            'value': listing.surface_area,
            'label': 'm² habitables',
        },
        {
            'value': listing.bedrooms,
            'label': f'Chambre{"s" if listing.bedrooms > 1 else ""}',
        },
        {
            'value': listing.bathrooms,
            'label': 'Salles de bain',
        },
    ]

    property_details = [
        {'label': 'Type de bien', 'value': listing.get_property_type_display()},
        {'label': 'Type d annonce', 'value': listing.get_listing_type_display()},
        {'label': 'Ville', 'value': listing.city},
        {'label': 'Quartier', 'value': listing.district or 'Non precisé'},
        {'label': 'Surface', 'value': f'{listing.surface_area} m²'},
        {'label': 'Publication', 'value': listing.created_at, 'is_datetime': True},
    ]

    return render(
        request,
        'listings/listing_detail.html',
        {
            'listing': listing,
            'gallery_images': gallery_images,
            'photo_count': len(gallery_images),
            'amenities': amenities,
            'contact_methods': contact_methods,
            'detail_metrics': detail_metrics,
            'property_details': property_details,
            'is_favorite': is_favorite,
            'can_edit': listing.can_edit(request.user),
            'can_delete': listing.can_delete(request.user),
        },
    )


@admin_only
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                listing = form.save(commit=False)
                listing.owner = request.user
                listing.status = Listing.Status.PUBLISHED
                listing.save()

                extra_images = request.FILES.getlist('extra_images')
                for idx, img_file in enumerate(extra_images):
                    ListingImage.objects.create(
                        listing=listing,
                        image=img_file,
                        order=idx,
                    )

            messages.success(request, 'L annonce a ete publiee.')
            return redirect('listing_detail', pk=listing.pk)
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = ListingForm()

    return render(
        request,
        'listings/listing_form.html',
        {
            'form': form,
            'formset': None,
            'page_title': 'Publier une annonce',
            'page_intro': 'Renseignez les informations essentielles pour diffuser un bien clair, complet et credible.',
            'submit_label': 'Publier l\'annonce',
        },
    )


@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(
        Listing.objects.prefetch_related('images'),
        pk=pk,
    )

    if not listing.can_edit(request.user):
        return render(
            request,
            '403.html',
            {
                'title': 'Modification impossible',
                'message': 'Vous ne pouvez modifier que vos propres annonces.',
                'suggestion': 'Retrouvez vos annonces dans votre espace proprietaire.',
            },
            status=403,
        )

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)

        if form.is_valid():
            with transaction.atomic():
                updated_listing = form.save()

                # Suppression des images cochées
                for key in request.POST:
                    if key.startswith('delete_image_'):
                        img_id = key.replace('delete_image_', '')
                        listing.images.filter(pk=img_id).delete()

                # Ajout des nouvelles photos
                extra_images = request.FILES.getlist('extra_images')
                logger.info('Upload: %d fichier(s) reçu(s) pour annonce pk=%s', len(extra_images), updated_listing.pk)
                existing_count = updated_listing.images.count()
                for idx, img_file in enumerate(extra_images):
                    try:
                        ListingImage.objects.create(
                            listing=updated_listing,
                            image=img_file,
                            order=existing_count + idx,
                        )
                        logger.info('Image %d sauvegardée : %s', idx, img_file.name)
                    except Exception as e:
                        logger.error('Erreur sauvegarde image %d : %s', idx, e)

            messages.success(request, 'Les modifications ont été enregistrées.')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm(instance=listing)
        formset = None

    return render(
        request,
        'listings/listing_form.html',
        {
            'form': form,
            'formset': formset,
            'page_title': 'Modifier l annonce',
            'page_intro': 'Mettez a jour les informations de votre bien avant sa prochaine publication.',
            'submit_label': 'Enregistrer les changements',
            'listing': listing,
        },
    )


@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if not listing.can_delete(request.user):
        return render(
            request,
            '403.html',
            {
                'title': 'Suppression impossible',
                'message': 'Vous pouvez supprimer uniquement les annonces qui ne sont pas encore publiees.',
                'suggestion': 'Si votre annonce est deja en ligne, contactez un administrateur.',
            },
            status=403,
        )

    if request.method == 'POST':
        title = listing.title
        listing.delete()
        messages.success(request, f'L annonce "{title}" a bien ete supprimee.')
        return redirect('dashboard')

    return render(request, 'listings/listing_confirm_delete.html', {'listing': listing})


@login_required
def contact_owner(request, pk):
    listing = get_object_or_404(Listing, pk=pk, status=Listing.Status.PUBLISHED)

    if listing.owner == request.user:
        return render(
            request,
            '403.html',
            {
                'title': 'Action impossible',
                'message': 'Vous ne pouvez pas envoyer de message a votre propre annonce.',
            },
            status=403,
        )

    existing_contact = Contact.objects.filter(
        listing=listing,
        from_user=request.user,
    ).first()

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message_text = request.POST.get('message', '').strip()

        if not email or not message_text:
            messages.error(
                request,
                'Veuillez renseigner votre email et un message avant l envoi.',
            )
        else:
            contact, created = Contact.objects.update_or_create(
                listing=listing,
                from_user=request.user,
                defaults={
                    'email': email,
                    'phone': phone,
                    'message': message_text,
                },
            )
            try:
                send_contact_notifications(contact, listing, is_update=not created)
            except Exception:
                messages.warning(
                    request,
                    'Votre demande a ete enregistree, mais les emails de confirmation n ont pas pu etre envoyes.',
                )
            messages.success(
                request,
                'Votre demande a bien ete envoyee au proprietaire.',
            )
            return redirect('listing_detail', pk=pk)

    return render(
        request,
        'listings/contact_form.html',
        {
            'listing': listing,
            'existing_contact': existing_contact,
        },
    )


def public_inquiry(request, pk):
    listing = get_object_or_404(Listing, pk=pk, status=Listing.Status.PUBLISHED)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        parts = full_name.split(None, 1)
        first_name = parts[0] if parts else ''
        last_name = parts[1] if len(parts) > 1 else ''
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message_text = request.POST.get('message', '').strip()
        want_similar = request.POST.get('want_similar') == 'on'

        if not full_name or not email or not message_text:
            messages.error(request, 'Merci de remplir tous les champs obligatoires (nom, email, message).')
        else:
            PublicInquiry.objects.create(
                listing=listing,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                message=message_text,
                want_similar=want_similar,
            )
            try:
                from django.core.mail import send_mail
                from django.conf import settings as django_settings
                agency_email = getattr(django_settings, 'DEFAULT_FROM_EMAIL', 'contact@yalaz-immo.com')
                similar_note = '\n✅ Souhaite recevoir des propositions similaires.' if want_similar else ''
                send_mail(
                    subject=f'[Yalaz] Nouvelle demande – {listing.title}',
                    message=(
                        f'Contact : {first_name} {last_name}\n'
                        f'Email : {email}\n'
                        f'Tél : {phone or "Non renseigné"}\n\n'
                        f'Message :\n{message_text}'
                        f'{similar_note}'
                    ),
                    from_email=agency_email,
                    recipient_list=[agency_email],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'Votre demande a bien été envoyée. Nous vous contacterons dans les meilleurs délais.')

    return redirect('listing_detail', pk=pk)


def get_districts_by_city(request):
    """API endpoint that returns districts for a given city with existing listings."""
    city = request.GET.get('city', '').strip()
    
    if not city:
        return JsonResponse({'districts': []})
    
    # Get districts only from listings that have published listings in that city
    districts = (
        Listing.objects.filter(status=Listing.Status.PUBLISHED, city__icontains=city)
        .values_list('district', flat=True)
        .distinct()
        .order_by('district')
    )
    
    return JsonResponse({'districts': list(districts)})


def get_all_districts_by_city(request):
    """API endpoint that returns ALL districts for a given city from the constants."""
    city = request.GET.get('city', '').strip()
    
    if not city:
        return JsonResponse({'districts': []})
    
    # Get all districts from the constants for the given city
    districts = MOROCCAN_DISTRICTS.get(city, [])
    
    return JsonResponse({'districts': districts})
