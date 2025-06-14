#!/usr/bin/env python
"""
API Testing Script for ALX Travel App
This script demonstrates the API endpoints and their functionality.
"""

import os
import django
import json
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from alx_travel_app.listings.models import Listing, Booking, Review


def test_api_endpoints():
    """Test all API endpoints"""
    client = APIClient()
    
    print("=" * 60)
    print("ALX Travel App API Testing")
    print("=" * 60)
    
    # Create test user
    print("\n1. Creating test user...")
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print(f"✓ Created user: {user.username}")
    
    # Test listings endpoint (unauthenticated)
    print("\n2. Testing Listings API...")
    response = client.get('/api/listings/')
    print(f"GET /api/listings/ - Status: {response.status_code}")
    
    # Test with filters
    response = client.get('/api/listings/?category=apartment&search=beach')
    print(f"GET /api/listings/?category=apartment&search=beach - Status: {response.status_code}")
    
    # Test available endpoint
    response = client.get('/api/listings/available/?guests=2&check_in_date=2024-07-01&check_out_date=2024-07-07')
    print(f"GET /api/listings/available/ with params - Status: {response.status_code}")
    
    # Authenticate user
    print("\n3. Testing with authentication...")
    client.force_authenticate(user=user)
    
    # Create a listing
    listing_data = {
        'title': 'Beautiful Beach House',
        'description': 'A stunning oceanfront property with amazing views',
        'category': 'Beach House',
        'location': 'Malibu, CA',
        'price_per_night': '250.00',
        'max_guests': 6,
        'available_from': str(date.today()),
        'available_to': str(date.today() + timedelta(days=365))
    }
    
    response = client.post('/api/listings/', listing_data, format='json')
    print(f"POST /api/listings/ - Status: {response.status_code}")
    
    if response.status_code == 201:
        listing_id = response.data['listing_id']
        print(f"✓ Created listing with ID: {listing_id}")
        
        # Test booking creation
        print("\n4. Testing Bookings API...")
        booking_data = {
            'listing_id': listing_id,
            'check_in_date': str(date.today() + timedelta(days=30)),
            'check_out_date': str(date.today() + timedelta(days=35)),
            'guests': 4
        }
        
        response = client.post('/api/bookings/', booking_data, format='json')
        print(f"POST /api/bookings/ - Status: {response.status_code}")
        
        if response.status_code == 201:
            booking_id = response.data['booking_id']
            print(f"✓ Created booking with ID: {booking_id}")
            
            # Update booking status
            status_data = {'status': 'confirmed'}
            response = client.post(f'/api/bookings/{booking_id}/update_status/', status_data, format='json')
            print(f"POST /api/bookings/{booking_id}/update_status/ - Status: {response.status_code}")
            
            # Test review creation
            print("\n5. Testing Reviews API...")
            review_data = {
                'listing_id': listing_id,
                'rating': 5,
                'comment': 'Amazing stay! The view was incredible and the host was very accommodating.'
            }
            
            response = client.post('/api/reviews/', review_data, format='json')
            print(f"POST /api/reviews/ - Status: {response.status_code}")
            
            if response.status_code == 201:
                print(f"✓ Created review with rating: {response.data['rating']}")
        
        # Test listing retrieval
        response = client.get(f'/api/listings/{listing_id}/')
        print(f"GET /api/listings/{listing_id}/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✓ Retrieved listing: {response.data['title']}")
            print(f"  Average rating: {response.data['average_rating']}")
            print(f"  Total reviews: {response.data['total_reviews']}")
    
    # Test user's bookings
    print("\n6. Testing user bookings...")
    response = client.get('/api/bookings/')
    print(f"GET /api/bookings/ - Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✓ User has {len(response.data)} booking(s)")
    
    print("\n" + "=" * 60)
    print("API Testing Completed!")
    print("=" * 60)
    
    # Print available endpoints
    print("\nAvailable API Endpoints:")
    print("------------------------")
    print("Listings:")
    print("  GET    /api/listings/                    - List all listings")
    print("  POST   /api/listings/                    - Create listing (auth required)")
    print("  GET    /api/listings/{id}/               - Get specific listing")
    print("  PUT    /api/listings/{id}/               - Update listing (host only)")
    print("  DELETE /api/listings/{id}/               - Delete listing (host only)")
    print("  GET    /api/listings/available/          - Search available listings")
    
    print("\nBookings:")
    print("  GET    /api/bookings/                    - List user bookings (auth required)")
    print("  POST   /api/bookings/                    - Create booking (auth required)")
    print("  GET    /api/bookings/{id}/               - Get specific booking")
    print("  PUT    /api/bookings/{id}/               - Update booking")
    print("  DELETE /api/bookings/{id}/               - Cancel booking")
    print("  POST   /api/bookings/{id}/update_status/ - Update booking status")
    
    print("\nReviews:")
    print("  GET    /api/reviews/                     - List all reviews")
    print("  POST   /api/reviews/                     - Create review (auth required)")
    print("  GET    /api/reviews/{id}/                - Get specific review")
    print("  PUT    /api/reviews/{id}/                - Update review (author only)")
    print("  DELETE /api/reviews/{id}/                - Delete review (author only)")
    
    print("\nDocumentation:")
    print("  GET    /swagger/                         - Swagger UI")
    print("  GET    /redoc/                           - ReDoc UI")
    print("  GET    /swagger.json                     - OpenAPI Schema")


if __name__ == '__main__':
    test_api_endpoints()
