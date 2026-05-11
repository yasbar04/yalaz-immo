from django.urls import path
from .views import (
    listing_list, listing_detail, listing_create,
    listing_edit, listing_delete, contact_owner, public_inquiry,
    get_districts_by_city, get_all_districts_by_city
)

urlpatterns = [
    path('', listing_list, name='listing_list'),
    path('create/', listing_create, name='listing_create'),
    path('<int:pk>/', listing_detail, name='listing_detail'),
    path('<int:pk>/edit/', listing_edit, name='listing_edit'),
    path('<int:pk>/delete/', listing_delete, name='listing_delete'),
    path('<int:pk>/contact/', contact_owner, name='contact_owner'),
    path('<int:pk>/demande/', public_inquiry, name='public_inquiry'),
    path('api/districts/', get_districts_by_city, name='get_districts_by_city'),
    path('api/all-districts/', get_all_districts_by_city, name='get_all_districts_by_city'),
]
