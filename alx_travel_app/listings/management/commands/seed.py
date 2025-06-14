from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random
from listings.models import Listing, Booking, Review


class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=30,
            help='Number of bookings to create'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=25,
            help='Number of reviews to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(
                self.style.WARNING('Clearing existing data...')
            )
            self.clear_data()

        self.stdout.write('Starting database seeding...')
        
        # Create users
        users = self.create_users(options['users'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(users)} users')
        )
        
        # Create listings
        listings = self.create_listings(users, options['listings'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(listings)} listings')
        )
        
        # Create bookings
        bookings = self.create_bookings(users, listings, options['bookings'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(bookings)} bookings')
        )
        
        # Create reviews
        reviews = self.create_reviews(users, listings, bookings, options['reviews'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(reviews)} reviews')
        )
        
        self.stdout.write(
            self.style.SUCCESS('Database seeding completed successfully!')
        )

    def clear_data(self):
        """Clear existing data"""
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        # Only delete users that aren't superusers
        User.objects.filter(is_superuser=False).delete()

    def create_users(self, count):
        """Create sample users"""
        users = []
        
        # Sample user data
        first_names = [
            'John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank',
            'Grace', 'Henry', 'Ivy', 'Jack', 'Kate', 'Liam', 'Mia', 'Noah',
            'Olivia', 'Paul', 'Quinn', 'Rachel'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin'
        ]
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{i+1}"
            email = f"{username}@example.com"
            
            # Check if user already exists
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password='password123'
                )
                users.append(user)
        
        return users

    def create_listings(self, users, count):
        """Create sample listings"""
        listings = []
        
        # Sample listing data
        categories = [
            'Apartment', 'House', 'Villa', 'Condo', 'Cabin', 'Loft', 'Studio',
            'Townhouse', 'Cottage', 'Chalet'
        ]
        
        locations = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
            'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA',
            'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Jacksonville, FL',
            'Fort Worth, TX', 'Columbus, OH', 'Charlotte, NC', 'San Francisco, CA',
            'Indianapolis, IN', 'Seattle, WA', 'Denver, CO', 'Boston, MA'
        ]
        
        adjectives = [
            'Beautiful', 'Cozy', 'Luxury', 'Modern', 'Charming', 'Spacious',
            'Elegant', 'Stylish', 'Comfortable', 'Stunning', 'Amazing', 'Perfect'
        ]
        
        for i in range(count):
            category = random.choice(categories)
            location = random.choice(locations)
            adjective = random.choice(adjectives)
            
            title = f"{adjective} {category} in {location.split(',')[0]}"
            
            description = f"""
            This {adjective.lower()} {category.lower()} offers a perfect getaway experience.
            Located in the heart of {location}, you'll have easy access to local attractions,
            restaurants, and entertainment. The space is well-appointed with modern amenities
            and comfortable furnishings. Perfect for couples, families, or business travelers
            looking for a memorable stay.
            
            Features:
            - Prime location in {location}
            - Modern furnishings and decor
            - Fully equipped kitchen
            - High-speed WiFi
            - Air conditioning/heating
            - Clean and sanitized
            """.strip()
            
            price_per_night = Decimal(random.randint(50, 500))
            max_guests = random.randint(1, 8)
            
            # Set availability dates
            available_from = date.today() + timedelta(days=random.randint(0, 30))
            available_to = available_from + timedelta(days=random.randint(90, 365))
            
            listing = Listing.objects.create(
                host=random.choice(users),
                title=title,
                description=description,
                category=category,
                location=location,
                price_per_night=price_per_night,
                max_guests=max_guests,
                available_from=available_from,
                available_to=available_to
            )
            listings.append(listing)
        
        return listings

    def create_bookings(self, users, listings, count):
        """Create sample bookings"""
        bookings = []
        
        status_choices = ['pending', 'confirmed', 'cancelled', 'completed']
        
        for i in range(count):
            listing = random.choice(listings)
            user = random.choice([u for u in users if u != listing.host])
            
            # Generate booking dates within listing availability
            days_offset = random.randint(0, 60)
            check_in_date = listing.available_from + timedelta(days=days_offset)
            nights = random.randint(1, 14)
            check_out_date = check_in_date + timedelta(days=nights)
            
            # Ensure check_out_date is within availability
            if check_out_date > listing.available_to:
                check_out_date = listing.available_to
                nights = (check_out_date - check_in_date).days
                if nights <= 0:
                    continue
            
            guests = random.randint(1, min(listing.max_guests, 4))
            
            # Check for conflicts with existing bookings
            conflicting_bookings = Booking.objects.filter(
                listing=listing,
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date,
                status__in=['confirmed', 'pending']
            )
            
            if conflicting_bookings.exists():
                continue
            
            total_price = listing.price_per_night * nights
            status = random.choice(status_choices)
            
            booking = Booking.objects.create(
                listing=listing,
                user=user,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                guests=guests,
                total_price=total_price,
                status=status
            )
            bookings.append(booking)
        
        return bookings

    def create_reviews(self, users, listings, bookings, count):
        """Create sample reviews"""
        reviews = []
        
        review_comments = [
            "Amazing place! Everything was perfect. Highly recommended!",
            "Great location and very clean. The host was very responsive.",
            "Beautiful property with stunning views. We had a wonderful time.",
            "Perfect for a weekend getaway. Will definitely book again!",
            "The listing was exactly as described. Great value for money.",
            "Lovely accommodation in a prime location. Very comfortable stay.",
            "Excellent host and beautiful property. Exceeded our expectations!",
            "Clean, comfortable, and well-located. Perfect for our needs.",
            "Outstanding experience! The place was immaculate and well-equipped.",
            "Great communication from the host. The space was perfect for our group.",
            "Wonderful stay! The property had everything we needed and more.",
            "Highly recommend this place. Great amenities and fantastic location.",
            "Perfect getaway spot! Clean, comfortable, and beautifully decorated.",
            "Exceptional property with great attention to detail. Will return!",
            "Fantastic location and beautiful space. Host was very accommodating."
        ]
        
        # Create reviews for completed bookings
        completed_bookings = [b for b in bookings if b.status == 'completed']
        
        for i in range(min(count, len(completed_bookings))):
            booking = random.choice(completed_bookings)
            
            # Check if review already exists for this booking
            if hasattr(booking, 'review'):
                continue
            
            rating = random.choices(
                [1, 2, 3, 4, 5],
                weights=[5, 5, 15, 35, 40]  # Weighted towards higher ratings
            )[0]
            
            comment = random.choice(review_comments)
            
            review = Review.objects.create(
                listing=booking.listing,
                user=booking.user,
                booking=booking,
                rating=rating,
                comment=comment
            )
            reviews.append(review)
            completed_bookings.remove(booking)  # Avoid duplicate reviews
        
        # Create some additional reviews for listings without bookings
        remaining_count = count - len(reviews)
        if remaining_count > 0:
            for i in range(remaining_count):
                listing = random.choice(listings)
                user = random.choice([u for u in users if u != listing.host])
                
                # Check if user already reviewed this listing
                if Review.objects.filter(listing=listing, user=user).exists():
                    continue
                
                rating = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[5, 5, 15, 35, 40]  # Weighted towards higher ratings
                )[0]
                
                comment = random.choice(review_comments)
                
                try:
                    review = Review.objects.create(
                        listing=listing,
                        user=user,
                        rating=rating,
                        comment=comment
                    )
                    reviews.append(review)
                except Exception:
                    # Skip if constraint violation (duplicate review)
                    continue
        
        return reviews
