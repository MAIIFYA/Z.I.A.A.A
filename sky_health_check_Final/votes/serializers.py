from rest_framework import serializers
from .models import Vote
from accounts.serializers import UserSerializer # Assuming this exists
from health_cards.serializers import HealthCardSerializer, HealthCheckSessionSerializer # Assuming these exist

class VoteSerializer(serializers.ModelSerializer):
    """Serializer for the Vote model."""
    # Read-only nested serializers for displaying related object details
    user = UserSerializer(read_only=True)
    card = HealthCardSerializer(read_only=True)
    session = HealthCheckSessionSerializer(read_only=True)
    
    # Writeable fields using IDs for relationships
    # These are inferred from the model definition, but explicitly defining 
    # can help with clarity or custom validation if needed.
    # session_id = serializers.UUIDField(write_only=True) # Handled by view context usually
    # user_id = serializers.UUIDField(write_only=True) # Handled by request.user usually
    # card_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Vote
        fields = [
            "id", "session", "user", "card", "vote_value", "trend", "comment", 
            "comment_summary", "created_at", "updated_at"
            # Add writeable IDs if not handled by view context
            # "session_id", "user_id", "card_id" 
        ]
        read_only_fields = ["id", "created_at", "updated_at", "session", "user", "card", "comment_summary"]
        # Ensure vote_value and trend are required on creation/update
        extra_kwargs = {
            "vote_value": {"required": True},
            "trend": {"required": True},
            "comment": {"required": False, "allow_blank": True, "allow_null": True}
        }

    # Add validation if needed, e.g., ensure the user belongs to the session's team
    def validate(self, data):
        # Access context passed from the view (e.g., request.user, session instance)
        request = self.context.get("request")
        session = self.context.get("session")
        card = self.context.get("card")
        user = request.user if request else None

        if not session or not card or not user:
             # This validation might be better placed in the view
             raise serializers.ValidationError("Session, card, and user context are required.")

        # Check if session is open
        if session.status != "open":
            raise serializers.ValidationError("Voting is closed for this session.")
            
        # Check if card is part of the session
        if card not in session.cards.all():
             raise serializers.ValidationError("Selected card is not part of this session.")

        # Check if user belongs to the team
        if user.team != session.team and not user.has_admin_privileges:
            raise serializers.ValidationError("You do not belong to the team for this session.")
            
        # Check for existing vote (update handled by view's get_object_or_404 or update_or_create)
        # If creating, ensure uniqueness is handled (unique_together in model Meta)

        return data

