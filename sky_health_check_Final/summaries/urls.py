from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamSummaryViewSet, VoteSummaryViewSet

router = DefaultRouter()
router.register(r"team-summaries", TeamSummaryViewSet, basename="teamsummary")
router.register(r"vote-summaries", VoteSummaryViewSet, basename="votesummary") # Historical summaries

# app_name = "summaries"

urlpatterns = [
    path("api/", include(router.urls)),
]

