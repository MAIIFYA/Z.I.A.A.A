# Create health_cards/serializers.py
from rest_framework import serializers
from .models import HealthCard, HealthCheckSession
# Removed: from teams.serializers import TeamSerializer 
from accounts.serializers import UserSerializer # Assuming this exists
# Removed: from .serializers import HealthCardSerializer # Self import is not needed

class HealthCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCard
        fields = ["id", "title", "description", "example_awesome", "example_crappy", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class HealthCheckSessionSerializer(serializers.ModelSerializer):
    """Serializer for the HealthCheckSession model."""
    # Use string notation to avoid circular import
    team = serializers.StringRelatedField(read_only=True) # Simpler representation first
    # team = "teams.serializers.TeamSerializer"(read_only=True) # Alternative if nested needed
    created_by = UserSerializer(read_only=True)
    cards = HealthCardSerializer(many=True, read_only=True) # Show full card details on read
    
    # Use PrimaryKeyRelatedField for write operations to select existing objects by ID
    team_id = serializers.UUIDField(write_only=True, source="team")
    created_by_id = serializers.UUIDField(write_only=True, source="created_by", required=False, allow_null=True)
    card_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True, 
        queryset=HealthCard.objects.filter(is_active=True), 
        source="cards"
    )
    # Calculate participation dynamically if needed, or add as a read-only field if stored
    # participation_rate = serializers.SerializerMethodField() 

    class Meta:
        model = HealthCheckSession
        fields = [
            "id", "team", "quarter", "year", "status", "created_at", "cards", 
            "created_by", "closed_at", 
            "team_id", "created_by_id", "card_ids" # Writeable fields
            # "participation_rate"
        ]
        read_only_fields = ["id", "created_at", "closed_at", "team", "created_by", "cards"]

    # Optional: Add method for participation rate if not stored on model
    # def get_participation_rate(self, obj):
    #     team_members_count = obj.team.members.count()
    #     participants_count = obj.session_votes.values("user").distinct().count()
    #     return (participants_count / team_members_count * 100) if team_members_count > 0 else 0

    def create(self, validated_data):
        # Pop the M2M field data before creating the instance
        card_data = validated_data.pop("cards", None)
        # Assign created_by automatically if not provided (e.g., from request.user)
        # Ensure context["request"] exists before accessing it
        request = self.context.get("request")
        if request and hasattr(request, "user") and "created_by" not in validated_data:
             validated_data["created_by"] = request.user
             
        session = HealthCheckSession.objects.create(**validated_data)
        # Assign the M2M relationship after instance creation
        if card_data:
            session.cards.set(card_data)
        return session

    def update(self, instance, validated_data):
        # Pop the M2M field data before updating the instance
        card_data = validated_data.pop("cards", None)
        instance = super().update(instance, validated_data)
        # Update the M2M relationship if provided
        if card_data is not None: # Allow clearing cards by passing empty list
            instance.cards.set(card_data)
        return instance

