from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    team_name = serializers.CharField(source="team.name", read_only=True, allow_null=True)
    department_name = serializers.CharField(source="team.department.name", read_only=True, allow_null=True)

    class Meta:
        model = User
        # Include fields relevant for display or management
        fields = [
            "id", "email", "first_name", "last_name", "role", 
            "team", "team_name", "department_name",
            "is_active", "is_staff", "is_superuser", "date_joined"
        ]
        read_only_fields = ["id", "date_joined", "is_staff", "is_superuser", "team_name", "department_name"]
        # Use extra_kwargs to make password write-only and not required for updates
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "team": {"required": False, "allow_null": True} # Allow setting team via ID
        }

    def create(self, validated_data):
        # Handle password creation properly
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Handle password update properly
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        # Update other fields
        return super().update(instance, validated_data)

