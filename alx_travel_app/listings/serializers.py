from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model to include in other serializers
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'user', 'rating', 'comment', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at']


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for Listing model
    """
    host = UserSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'host', 'title', 'description', 'category',
            'location', 'price_per_night', 'max_guests', 'available_from',
            'available_to', 'created_at', 'updated_at', 'reviews',
            'average_rating', 'total_reviews'
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        """Calculate average rating for the listing"""
        reviews = obj.reviews.all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            return round(total_rating / len(reviews), 2)
        return 0
    
    def get_total_reviews(self, obj):
        """Get total number of reviews for the listing"""
        return obj.reviews.count()
    
    def validate(self, data):
        """
        Validate that available_to is after available_from
        """
        if data.get('available_from') and data.get('available_to'):
            if data['available_to'] <= data['available_from']:
                raise serializers.ValidationError(
                    "Available to date must be after available from date."
                )
        return data


class ListingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating listings (without nested data)
    """
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'category', 'location',
            'price_per_night', 'max_guests', 'available_from', 'available_to'
        ]
    
    def validate(self, data):
        """
        Validate that available_to is after available_from
        """
        if data.get('available_from') and data.get('available_to'):
            if data['available_to'] <= data['available_from']:
                raise serializers.ValidationError(
                    "Available to date must be after available from date."
                )
        return data


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model
    """
    user = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    total_nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing', 'user', 'check_in_date', 'check_out_date',
            'guests', 'total_price', 'status', 'created_at', 'updated_at',
            'total_nights'
        ]
        read_only_fields = [
            'booking_id', 'total_price', 'created_at', 'updated_at'
        ]
    
    def get_total_nights(self, obj):
        """Calculate total nights for the booking"""
        return obj.calculate_total_nights()
    
    def validate(self, data):
        """
        Validate booking dates and guest capacity
        """
        # Validate check-out is after check-in
        if data.get('check_in_date') and data.get('check_out_date'):
            if data['check_out_date'] <= data['check_in_date']:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )
        
        # Validate guests don't exceed listing capacity
        if hasattr(self, 'listing') and data.get('guests'):
            if data['guests'] > self.listing.max_guests:
                raise serializers.ValidationError(
                    f"Number of guests ({data['guests']}) exceeds maximum capacity ({self.listing.max_guests})."
                )
        
        return data


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating bookings
    """
    listing_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'listing_id', 'check_in_date', 'check_out_date', 'guests'
        ]
    
    def validate(self, data):
        """
        Validate booking creation
        """
        # Validate check-out is after check-in
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )
        
        # Validate listing exists and is available
        try:
            listing = Listing.objects.get(listing_id=data['listing_id'])
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Listing not found.")
        
        # Validate guests don't exceed capacity
        if data['guests'] > listing.max_guests:
            raise serializers.ValidationError(
                f"Number of guests ({data['guests']}) exceeds maximum capacity ({listing.max_guests})."
            )
        
        # Validate listing is available for the requested dates
        if not listing.is_available(data['check_in_date'], data['check_out_date']):
            raise serializers.ValidationError(
                "Listing is not available for the selected dates."
            )
        
        # Check for conflicting bookings
        conflicting_bookings = Booking.objects.filter(
            listing=listing,
            status__in=['confirmed', 'pending'],
            check_in_date__lt=data['check_out_date'],
            check_out_date__gt=data['check_in_date']
        )
        
        if conflicting_bookings.exists():
            raise serializers.ValidationError(
                "Listing is already booked for the selected dates."
            )
        
        data['listing'] = listing
        return data
    
    def create(self, validated_data):
        """
        Create booking with calculated total price
        """
        listing = validated_data.pop('listing')
        validated_data.pop('listing_id')
        
        booking = Booking.objects.create(
            listing=listing,
            **validated_data
        )
        return booking


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating reviews
    """
    booking_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'booking_id']
    
    def validate(self, data):
        """
        Validate review creation
        """
        # Validate rating is within range
        if not (1 <= data['rating'] <= 5):
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        
        return data
