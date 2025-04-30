from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, TeamViewSet, DepartmentSummaryViewSet

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet)
router.register(r"teams", TeamViewSet)
router.register(r"department-summaries", DepartmentSummaryViewSet)

# app_name = "teams"

urlpatterns = [
    path("api/", include(router.urls)),
]

