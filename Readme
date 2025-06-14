# ALX Travel App 0x01 - API Development

A Django REST Framework API for managing travel listings and bookings with comprehensive Swagger documentation.

## Project Overview

This project builds upon the database modeling foundation to provide a complete API solution for a travel booking platform. It includes ViewSets for CRUD operations, advanced filtering capabilities, and comprehensive API documentation.

## Features Implemented

### 1. API ViewSets
- **ListingViewSet**: Complete CRUD operations for travel listings with filtering and search
- **BookingViewSet**: User-specific booking management with status updates
- **ReviewViewSet**: Review system with listing-specific filtering

### 2. RESTful API Endpoints
- `/api/listings/` - Listings management with advanced filtering
- `/api/bookings/` - Booking lifecycle management
- `/api/reviews/` - Review and rating system
- `/api/listings/available/` - Availability search with date/guest filtering

### 3. API Documentation
- **Swagger UI**: Interactive API documentation at `/swagger/`
- **ReDoc**: Alternative documentation interface at `/redoc/`
- **OpenAPI Schema**: Complete API specification

### 4. Advanced Features
- **Filtering**: Category, location, capacity, status-based filtering
- **Search**: Full-text search across title, description, and location
- **Ordering**: Sortable results by price, date, rating
- **Permissions**: Role-based access control
- **Validation**: Comprehensive data validation with meaningful error messages

### 5. Database Models
- **Listing Model**: Travel property listings with host information, pricing, and availability
- **Booking Model**: Booking management with date validation and status tracking  
- **Review Model**: User reviews with ratings and comments

### 2. API Serializers
- Complete serializers for all models with nested relationships
- Separate create serializers with validation
- Calculated fields like average ratings and total nights

### 3. Data Seeding
- Management command to populate database with realistic sample data
- Configurable data generation (users, listings, bookings, reviews)
- Data integrity validation and relationship management
- **Booking System**: Book listings with date validation and conflict checking
- **Review System**: Leave reviews for completed bookings
- **User Management**: User authentication and profile management
- **Admin Interface**: Django admin for managing all data

## Models

### Listing
- Unique identifier (UUID)
- Host (User relationship)
- Basic information (title, description, category, location)
- Pricing and capacity (price_per_night, max_guests)
- Availability dates
- Timestamps

### Booking
- Unique identifier (UUID)
- Listing and User relationships
- Booking details (check-in/out dates, guests, total_price)
- Status tracking (pending, confirmed, cancelled, completed)
- Automatic price calculation
- Date validation constraints

### Review
- Unique identifier (UUID)
- Listing, User, and optional Booking relationships
- Rating (1-5 scale) and comment
- Unique constraint per user-listing pair

## API Serializers

- **ListingSerializer**: Full listing data with reviews and ratings
- **ListingCreateSerializer**: Simplified serializer for creating listings
- **BookingSerializer**: Full booking data with calculated fields
- **BookingCreateSerializer**: Booking creation with validation
- **ReviewSerializer**: Review data with user information
- **ReviewCreateSerializer**: Review creation with validation

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL
- RabbitMQ (for Celery)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alx_travel_app_0x00
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=mysql://username:password@localhost:3306/alx_travel_db
   CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Seed Database (Optional)**
   ```bash
   python manage.py seed --listings 20 --users 10 --bookings 30 --reviews 25
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Management Commands

### Seed Command
The `seed` management command populates the database with sample data:

```bash
python manage.py seed [options]
```

**Options:**
- `--listings N`: Number of listings to create (default: 20)
- `--users N`: Number of users to create (default: 10)
- `--bookings N`: Number of bookings to create (default: 30)
- `--reviews N`: Number of reviews to create (default: 25)
- `--clear`: Clear existing data before seeding

**Examples:**
```bash
# Seed with default values
python manage.py seed

# Seed with custom values
python manage.py seed --listings 50 --users 20 --bookings 100 --reviews 80

# Clear existing data and reseed
python manage.py seed --clear --listings 10 --users 5
```

## API Endpoints

The application provides RESTful API endpoints for:
- Listings CRUD operations
- Booking management
- Review system
- User authentication

## Admin Interface

Access the Django admin interface at `/admin/` to manage:
- Users
- Listings
- Bookings
- Reviews

## Database Schema

### Key Relationships
- **User → Listings**: One-to-many (host relationship)
- **User → Bookings**: One-to-many (guest relationship)
- **User → Reviews**: One-to-many (reviewer relationship)
- **Listing → Bookings**: One-to-many
- **Listing → Reviews**: One-to-many
- **Booking → Review**: One-to-one (optional)

### Constraints
- Check-out date must be after check-in date
- Booking guests cannot exceed listing capacity
- Users can only review each listing once
- Booking date conflicts are prevented

## Data Validation

- **Listings**: Date validation, capacity constraints
- **Bookings**: Date validation, availability checking, conflict detection
- **Reviews**: Rating range validation (1-5), uniqueness constraints

## File Structure

```
alx_travel_app_0x00/
├── manage.py
├── requirements.txt
├── README.md
├── alx_travel_app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── listings/
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── admin.py
    ├── views.py
    ├── apps.py
    ├── tests.py
    ├── migrations/
    └── management/
        └── commands/
            └── seed.py
```

## Development Notes

- Uses UUID primary keys for security
- Implements proper model relationships and constraints
- Includes comprehensive validation in serializers
- Provides flexible seeding for development and testing
- Uses Django best practices for model design

## Quick Start

### 1. Start the development server:
```bash
python manage.py runserver
```

### 2. Access API Documentation:
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin Panel**: http://localhost:8000/admin/

### 3. Test API Endpoints:
```bash
# Test the API endpoints
python test_api.py

# Or manually test with curl:
curl -X GET "http://localhost:8000/api/listings/"
curl -X GET "http://localhost:8000/api/listings/available/?guests=2&check_in_date=2024-07-01&check_out_date=2024-07-07"
```

## API Endpoint Examples

### Listings
```bash
# List all listings with filtering
GET /api/listings/?category=apartment&location=paris&max_guests=4

# Search listings
GET /api/listings/?search=beach&ordering=-price_per_night

# Get available listings for specific dates
GET /api/listings/available/?check_in_date=2024-07-01&check_out_date=2024-07-07&guests=2
```

### Bookings (Authentication Required)
```bash
# Create a booking
POST /api/bookings/
{
  "listing_id": "uuid-here",
  "check_in_date": "2024-07-01", 
  "check_out_date": "2024-07-07",
  "guests": 2
}

# Update booking status
POST /api/bookings/{id}/update_status/
{
  "status": "confirmed"
}
```

### Reviews
```bash
# Create a review
POST /api/reviews/
{
  "listing_id": "uuid-here",
  "rating": 5,
  "comment": "Amazing place!"
}

# Get reviews for a specific listing
GET /api/reviews/?listing_id=uuid-here
```

## Testing

Run the comprehensive API test:
```bash
python test_api.py
```

This will test:
- ✅ All CRUD operations
- ✅ Authentication and permissions  
- ✅ Data validation
- ✅ Filtering and search
- ✅ Custom endpoints (availability, status updates)

## Production Deployment

1. **Environment Setup**:
   ```bash
   export DEBUG=False
   export SECRET_KEY='your-production-secret-key'
   export DATABASE_URL='your-production-database-url'
   ```

2. **Install Production Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

4. **Create Admin User**:
   ```bash
   python manage.py createsuperuser
   ```
