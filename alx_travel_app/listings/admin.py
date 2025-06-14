from django.contrib import admin
from .models import Listing, Booking, Review


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'host', 'category', 'location', 'price_per_night', 'max_guests', 'created_at']
    list_filter = ['category', 'location', 'created_at']
    search_fields = ['title', 'description', 'location']
    ordering = ['-created_at']
    readonly_fields = ['listing_id', 'created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'listing', 'user', 'check_in_date', 'check_out_date', 'status', 'total_price']
    list_filter = ['status', 'created_at', 'check_in_date']
    search_fields = ['listing__title', 'user__username', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'listing', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['listing__title', 'user__username', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['review_id', 'created_at', 'updated_at']
