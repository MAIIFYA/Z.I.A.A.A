from rest_framework import serializers
from .models import TeamSummary, VoteSummary
from teams.serializers import TeamSerializer # Assuming this exists
from health_cards.serializers import HealthCardSerializer, HealthCheckSessionSerializer # Assuming these exist

class TeamSummarySerializer(serializers.ModelSerializer):
    """Serializer for the TeamSummary model."""
    team = TeamSerializer(read_only=True)
    card = HealthCardSerializer(read_only=True)
    session = HealthCheckSessionSerializer(read_only=True)

    class Meta:
        model = TeamSummary
        fields = [
            "id", "team", "card", "session", 
            "green_count", "amber_count", "red_count",
            "improving_count", "stable_count", "declining_count", 
            "aggregated_comments_summary", "created_at", "updated_at"
        ]
        # These summaries are typically calculated and read-only via API
        read_only_fields = fields 

class VoteSummarySerializer(serializers.ModelSerializer):
    """Serializer for the VoteSummary (historical) model."""
    team = TeamSerializer(read_only=True)
    card = HealthCardSerializer(read_only=True)
    # Display quarter name using choices
    quarter_display = serializers.CharField(source="get_quarter_display", read_only=True)
    # Display trend name using choices
    aggregated_trend_display = serializers.CharField(source="get_aggregated_trend_display", read_only=True)

    class Meta:
        model = VoteSummary
        fields = [
            "id", "team", "card", "quarter", "quarter_display", "year", 
            "green_percentage", "amber_percentage", "red_percentage", 
            "aggregated_trend", "aggregated_trend_display",
            "created_at", "updated_at"
        ]
        # These summaries are typically calculated and read-only via API
        read_only_fields = fields

