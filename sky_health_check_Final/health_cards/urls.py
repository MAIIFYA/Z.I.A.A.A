from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthCardViewSet, HealthCheckSessionViewSet

router = DefaultRouter()
router.register(r"cards", HealthCardViewSet)
router.register(r"sessions", HealthCheckSessionViewSet)

# app_name = "health_cards"

urlpatterns = [
    path("api/", include(router.urls)),
]

