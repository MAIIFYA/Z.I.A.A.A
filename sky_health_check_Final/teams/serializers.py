from rest_framework import serializers
from .models import Department, Team, DepartmentSummary
from accounts.serializers import UserSerializer # Assuming UserSerializer exists
# Import HealthCardSerializer directly
from health_cards.serializers import HealthCardSerializer 
# Removed: HealthCheckSessionSerializer to break circular import

class DepartmentSerializer(serializers.ModelSerializer):
    # Use nested serializers for related objects if needed, or just IDs
    senior_manager = UserSerializer(read_only=True)
    department_manager = UserSerializer(read_only=True)
    senior_manager_id = serializers.UUIDField(write_only=True, required=False, allow_null=True, source="senior_manager")
    department_manager_id = serializers.UUIDField(write_only=True, required=False, allow_null=True, source="department_manager")

    class Meta:
        model = Department
        fields = ["id", "name", "created_at", "senior_manager", "department_manager", 
                  "senior_manager_id", "department_manager_id"]
        read_only_fields = ["id", "created_at", "senior_manager", "department_manager"]

    # Add validation or custom create/update logic if needed
    # e.g., to assign managers based on ID during write operations

class TeamSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    leader = UserSerializer(read_only=True)
    department_id = serializers.UUIDField(write_only=True, source="department")
    leader_id = serializers.UUIDField(write_only=True, required=False, allow_null=True, source="leader")
    member_count = serializers.IntegerField(source="members.count", read_only=True)

    class Meta:
        model = Team
        fields = ["id", "name", "department", "leader", "created_at", 
                  "department_id", "leader_id", "member_count"]
        read_only_fields = ["id", "created_at", "department", "leader", "member_count"]

class DepartmentSummarySerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    card = HealthCardSerializer(read_only=True)
    # Use string notation for session to avoid circular import
    session = serializers.StringRelatedField(read_only=True)
    # session = "health_cards.serializers.HealthCheckSessionSerializer"(read_only=True) # Alternative

    class Meta:
        model = DepartmentSummary
        fields = ["id", "department", "card", "session", "green_count", "amber_count", "red_count",
                  "improving_count", "stable_count", "declining_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "department", "card", "session"]

