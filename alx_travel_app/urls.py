from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="ALX Travel App API",
      default_version='v1',
      description="API documentation for the ALX Travel App project. This platform will serve as a travel listing service.",
      terms_of_service="https://www.google.com/policies/terms/", # Replace with your terms
      contact=openapi.Contact(email="contact@alxtravel.local"), # Replace with your contact
      license=openapi.License(name="BSD License"), # Replace with your license
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Swagger UI:
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Add your app's URLs here later, e.g.:
    # path('api/listings/', include('listings.urls')),
    
    # API endpoints
    path('api/', include('alx_travel_app.listings.urls')),
]