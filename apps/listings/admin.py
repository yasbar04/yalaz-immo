from django.contrib import admin
from .models import Listing, ListingImage, Contact, PublicInquiry


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ('image', 'alt_text', 'order')


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'listing_type', 'price', 'status', 'owner', 'views_count', 'created_at')
    list_filter = ('status', 'listing_type', 'property_type', 'city', 'created_at')
    search_fields = ('title', 'city', 'district', 'description')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'views_count')
    inlines = [ListingImageInline]
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'owner', 'image')
        }),
        ('Détails du bien', {
            'fields': ('property_type', 'listing_type', 'price', 'surface_area', 'bedrooms', 'bathrooms')
        }),
        ('Localisation', {
            'fields': ('city', 'district')
        }),
        ('Modération', {
            'fields': ('status', 'views_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('listing__title', 'alt_text')
    ordering = ('listing', 'order')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'listing', 'email', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('listing__title', 'from_user__username', 'email', 'message')
    readonly_fields = ('from_user', 'listing', 'email', 'phone', 'message', 'created_at')
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = 'Marquer comme lu'


@admin.register(PublicInquiry)
class PublicInquiryAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'listing', 'want_similar', 'is_read', 'created_at')
    list_filter = ('is_read', 'want_similar', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'listing__title', 'message')
    readonly_fields = ('first_name', 'last_name', 'email', 'phone', 'message', 'want_similar', 'listing', 'created_at')
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = 'Marquer comme lu'
