from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .permissions import admin_required # Use the custom decorator logic if needed, or DRF permissions
from rest_framework.permissions import IsAdminUser, IsAuthenticated

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    Restricted to admin users.
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    # Use DRF permissions for viewset-level control
    # IsAdminUser checks request.user.is_staff
    # Ensure our User model correctly sets is_staff for admin/senior_manager roles
    permission_classes = [IsAdminUser] 

    # If more granular permissions are needed (e.g., user can edit self), 
    # override get_permissions or add custom permission classes.

