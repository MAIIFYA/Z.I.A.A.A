from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)

# Define app_name for namespacing if needed, although usually done in the main urls.py include
# app_name = "accounts"

urlpatterns = [
    path("api/", include(router.urls)),
    # Add other account-related paths (e.g., from django-allauth) if not handled globally
    # path("", include("allauth.urls")), # Example: If allauth URLs are scoped here
]

