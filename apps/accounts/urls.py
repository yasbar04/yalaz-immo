from django.contrib.auth import views as auth_views
from django.urls import path

from .admin_views import (
    admin_dashboard, admin_listings, admin_listing_detail, admin_users,
    admin_user_detail, admin_reports, admin_report_detail, report_content,
    toggle_favorite, favorites,
    admin_staff_list, admin_staff_create, admin_staff_edit, admin_staff_delete,
    change_password_required,
)
from apps.core.views import (
    admin_seller_requests, admin_seller_request_detail,
    admin_contact_messages, admin_contact_message_detail,
)
from .views import (
    login_view,
    dashboard,
    profile_edit_view,
    profile_view,
    recover_verification_view,
    resend_email_verification_view,
    resend_sms_verification_view,
    signup_view,
    verify_account_view,
    verify_email_view,
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('change-password-required/', change_password_required, name='change_password_required'),
    path('signup/', signup_view, name='signup'),
    path('verify/', verify_account_view, name='verify_account'),
    path('verify/recover/', recover_verification_view, name='recover_verification'),
    path('verify/email/', verify_email_view, name='verify_email'),
    path('verify/resend-email/', resend_email_verification_view, name='resend_email_verification'),
    path('verify/resend-sms/', resend_sms_verification_view, name='resend_sms_verification'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),

    # Admin URLs
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('admin/listings/', admin_listings, name='admin_listings'),
    path('admin/listing/<int:pk>/', admin_listing_detail, name='admin_listing_detail'),
    path('admin/users/', admin_users, name='admin_users'),
    path('admin/user/<int:user_id>/', admin_user_detail, name='admin_user_detail'),
    path('admin/reports/', admin_reports, name='admin_reports'),
    path('admin/report/<int:report_id>/', admin_report_detail, name='admin_report_detail'),
    
    # Superadmin staff management
    path('admin/staff/', admin_staff_list, name='admin_staff_list'),
    path('admin/staff/add/', admin_staff_create, name='admin_staff_create'),
    path('admin/staff/<int:user_id>/edit/', admin_staff_edit, name='admin_staff_edit'),
    path('admin/staff/<int:user_id>/delete/', admin_staff_delete, name='admin_staff_delete'),

    # Demandes vendeurs (admin/staff)
    path('admin/seller-requests/', admin_seller_requests, name='admin_seller_requests'),
    path('admin/seller-requests/<int:request_id>/', admin_seller_request_detail, name='admin_seller_request_detail'),

    # Messages de contact (admin/staff)
    path('admin/contact-messages/', admin_contact_messages, name='admin_contact_messages'),
    path('admin/contact-messages/<int:message_id>/', admin_contact_message_detail, name='admin_contact_message_detail'),

    # User features
    path('report/<int:listing_id>/', report_content, name='report_listing'),
    path('favorite/<int:listing_id>/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', favorites, name='favorites'),
]
