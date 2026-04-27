from rest_framework import serializers
from .models import Listing, ListingImage, Contact, Favorite


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'alt_text', 'order']
        read_only_fields = ['id']


class ListingDetailSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'property_type',
            'listing_type',
            'city',
            'district',
            'price',
            'surface_area',
            'bedrooms',
            'bathrooms',
            'kitchen_equipped',
            'swimming_pool',
            'garden',
            'garage',
            'parking',
            'terrace',
            'balcony',
            'air_conditioning',
            'furnished',
            'security',
            'description',
            'image',
            'owner_email',
            'owner_phone',
            'owner_whatsapp',
            'owner_username',
            'owner_name',
            'status',
            'is_featured',
            'views_count',
            'created_at',
            'updated_at',
            'images',
        ]
        read_only_fields = ['id', 'owner_username', 'owner_name', 'views_count', 'created_at', 'updated_at', 'status']


class ListingListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes"""
    image = serializers.ImageField()
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'price',
            'city',
            'district',
            'property_type',
            'listing_type',
            'surface_area',
            'bedrooms',
            'bathrooms',
            'image',
            'views_count',
            'created_at',
        ]
        read_only_fields = ['id', 'views_count', 'created_at']


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier des annonces"""
    class Meta:
        model = Listing
        fields = [
            'title',
            'property_type',
            'listing_type',
            'city',
            'district',
            'price',
            'surface_area',
            'bedrooms',
            'bathrooms',
            'kitchen_equipped',
            'swimming_pool',
            'garden',
            'garage',
            'parking',
            'terrace',
            'balcony',
            'air_conditioning',
            'furnished',
            'security',
            'description',
            'image',
            'owner_email',
            'owner_phone',
            'owner_whatsapp',
        ]
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        validated_data['status'] = Listing.Status.PENDING
        return super().create(validated_data)


class ContactSerializer(serializers.ModelSerializer):
    from_user_username = serializers.CharField(source='from_user.username', read_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'listing', 'email', 'phone', 'message', 'from_user_username', 'created_at', 'is_read']
        read_only_fields = ['id', 'from_user_username', 'created_at']


class FavoriteSerializer(serializers.ModelSerializer):
    listing = ListingListSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'listing', 'created_at']
        read_only_fields = ['id', 'created_at']
