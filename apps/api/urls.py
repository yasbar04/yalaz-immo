from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import ListingViewSet, ContactViewSet, FavoriteViewSet, UserViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'users', UserViewSet, basename='user')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
