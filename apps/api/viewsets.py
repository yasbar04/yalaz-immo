from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models import Q

from apps.listings.models import Listing, Contact, Favorite
from apps.listings.serializers import (
    ListingDetailSerializer,
    ListingListSerializer,
    ListingCreateUpdateSerializer,
    ContactSerializer,
    FavoriteSerializer,
)
from apps.accounts.models import UserProfile
from apps.accounts.serializers import UserSerializer, UserUpdateSerializer, RegisterSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    API pour les annonces immobilières.
    
    GET    /api/listings/              - List published listings
    GET    /api/listings/{id}/         - Detail of a listing
    POST   /api/listings/              - Create new listing (authenticated)
    PUT    /api/listings/{id}/         - Update listing (owner only)
    DELETE /api/listings/{id}/         - Delete listing (owner only)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['city', 'district', 'property_type', 'listing_type', 'status']
    search_fields = ['title', 'description', 'city', 'district']
    ordering_fields = ['created_at', 'price', 'views_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # Pour les utilisateurs anonymes: seulement les publiées
        if not user.is_authenticated:
            return Listing.objects.filter(status=Listing.Status.PUBLISHED).select_related('owner').prefetch_related('images')
        
        # Pour les users: leurs annonces + toutes les publiées
        if user.is_staff or user.is_superuser:
            # Admin voit tout
            return Listing.objects.select_related('owner').prefetch_related('images')
        
        # User normal voit ses annonces + les publiées des autres
        return Listing.objects.filter(
            Q(owner=user) | Q(status=Listing.Status.PUBLISHED)
        ).select_related('owner').prefetch_related('images')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ListingListSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return ListingCreateUpdateSerializer
        return ListingDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        # Seulement le propriétaire ou admin peut modifier
        listing = self.get_object()
        if listing.owner != self.request.user and not self.request.user.is_staff:
            self.permission_denied(self.request)
        serializer.save()
    
    def perform_destroy(self, instance):
        # Seulement le propriétaire ou admin peut supprimer
        if instance.owner != self.request.user and not self.request.user.is_staff:
            self.permission_denied(self.request)
        instance.delete()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        """Ajouter/retirer des favoris"""
        listing = self.get_object()
        favorite, created = Favorite.objects.get_or_create(listing=listing, user=request.user)
        
        if not created:
            favorite.delete()
            return Response({'status': 'removed from favorites'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'added to favorites'}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """Récupérer les contacts reçus d'une annonce"""
        listing = self.get_object()
        
        # Seulement le propriétaire peut voir les contacts
        if listing.owner != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        contacts = listing.contacts.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)


class ContactViewSet(viewsets.ModelViewSet):
    """
    API pour les demandes de contact.
    
    GET    /api/contacts/              - List user's contacts (authenticated)
    POST   /api/contacts/              - Send contact message
    """
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Utilisateur voit ses demandes envoyées ET reçues
        return Contact.objects.filter(
            Q(from_user=user) | Q(listing__owner=user)
        )
    
    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    API pour les favoris.
    
    GET    /api/favorites/             - List user's favorites (authenticated)
    DELETE /api/favorites/{id}/        - Remove from favorites
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user and not self.request.user.is_staff:
            self.permission_denied(self.request)
        instance.delete()


class UserViewSet(viewsets.ModelViewSet):
    """
    API pour les utilisateurs.
    
    GET    /api/users/me/              - Get current user info (authenticated)
    PUT    /api/users/me/              - Update current user (authenticated)
    POST   /api/auth/register/         - Register new user
    POST   /api/auth/login/            - Get auth token (credentials)
    POST   /api/auth/logout/           - Logout (authenticated)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get or update current user info"""
        user = request.user
        
        if request.method == 'PUT':
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register new user"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """Logout - delete token"""
        request.user.auth_token.delete()
        return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)
