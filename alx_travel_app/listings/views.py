from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import serializers
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Listing, Booking, Review
from .serializers import (
    ListingSerializer, 
    ListingCreateSerializer,
    BookingSerializer, 
    BookingCreateSerializer,
    ReviewSerializer,
    ReviewCreateSerializer
)


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing listings.
    Provides CRUD operations for listings with filtering and search capabilities.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'location', 'max_guests']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price_per_night', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        if self.action == 'create':
            return ListingCreateSerializer
        return ListingSerializer

    def perform_create(self, serializer):
        """
        Set the current user as the host when creating a listing.
        """
        serializer.save(host=self.request.user)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'check_in_date',
                openapi.IN_QUERY,
                description="Check-in date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'check_out_date',
                openapi.IN_QUERY,
                description="Check-out date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'guests',
                openapi.IN_QUERY,
                description="Number of guests",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={200: ListingSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get listings available for specific dates and guest count.
        """
        check_in_date = request.query_params.get('check_in_date')
        check_out_date = request.query_params.get('check_out_date')
        guests = request.query_params.get('guests')

        queryset = self.get_queryset()

        # Filter by guest capacity
        if guests:
            try:
                guests = int(guests)
                queryset = queryset.filter(max_guests__gte=guests)
            except ValueError:
                return Response(
                    {'error': 'Invalid guests parameter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Filter by date availability
        if check_in_date and check_out_date:
            try:
                from datetime import datetime
                check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
                
                if check_out <= check_in:
                    return Response(
                        {'error': 'Check-out date must be after check-in date'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Filter listings that are available in the date range
                queryset = queryset.filter(
                    available_from__lte=check_in,
                    available_to__gte=check_out
                )

                # Exclude listings with conflicting bookings
                conflicting_bookings = Booking.objects.filter(
                    status__in=['confirmed', 'pending'],
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in
                ).values_list('listing_id', flat=True)

                queryset = queryset.exclude(listing_id__in=conflicting_bookings)

            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    Provides CRUD operations for bookings with user-specific filtering.
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'listing']
    ordering_fields = ['created_at', 'check_in_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return bookings for the current user only.
        """
        return Booking.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        """
        Set the current user when creating a booking.
        """
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['pending', 'confirmed', 'cancelled', 'completed']
                )
            },
            required=['status']
        ),
        responses={
            200: BookingSerializer(),
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of a booking.
        """
        booking = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'Status is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {valid_statuses}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = new_status
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.
    Provides CRUD operations for reviews with listing-specific filtering.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['listing', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return all reviews or filter by listing if specified.
        """
        queryset = Review.objects.all()
        listing_id = self.request.query_params.get('listing_id')
        if listing_id:
            queryset = queryset.filter(listing__listing_id=listing_id)
        return queryset

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        """
        Set the current user when creating a review.
        """
        # Get the listing from the request data
        listing_id = self.request.data.get('listing_id')
        if not listing_id:
            raise serializers.ValidationError({'listing_id': 'This field is required.'})
        
        try:
            listing = Listing.objects.get(listing_id=listing_id)
        except Listing.DoesNotExist:
            raise serializers.ValidationError({'listing_id': 'Listing not found.'})

        serializer.save(user=self.request.user, listing=listing)
