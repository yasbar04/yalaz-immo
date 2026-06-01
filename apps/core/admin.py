from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage, FinancialTransaction


@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'type_badge', 'amount_display', 'description', 'created_by_name', 'status_badge')
    list_filter = ('type', 'status', 'transaction_date', 'category')
    search_fields = ('description', 'notes', 'created_by__username', 'assigned_to__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Informations de Transaction', {
            'fields': ('type', 'status', 'amount', 'transaction_date'),
            'description': 'Détails principaux de la transaction',
        }),
        ('Description et Catégorie', {
            'fields': ('description', 'category', 'notes'),
        }),
        ('Relations', {
            'fields': ('listing', 'created_by', 'assigned_to'),
            'description': 'Liens avec les biens et utilisateurs',
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def type_badge(self, obj):
        colors = {
            'entry': '#10b981',   # Vert
            'exit': '#ef4444',    # Rouge
        }
        color = colors.get(obj.type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_type_display()
        )
    type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',      # Orange
            'completed': '#10b981',    # Vert
            'cancelled': '#ef4444',    # Rouge
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def amount_display(self, obj):
        color = '#10b981' if obj.type == 'entry' else '#ef4444'
        sign = '+' if obj.type == 'entry' else '−'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {:.2f} DH</span>',
            color,
            sign,
            obj.amount
        )
    amount_display.short_description = 'Montant'
    
    def created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return "—"
    created_by_name.short_description = 'Créé par'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('created_by', 'assigned_to', 'listing', 'listing__owner')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('subject', 'created_at', 'is_read')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at', 'ip_address')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'ip_address', 'is_read'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False  # Messages cannot be added manually from admin

