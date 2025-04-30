from rest_framework import viewsets, permissions
from .models import Department, Team, DepartmentSummary
from .serializers import DepartmentSerializer, TeamSerializer, DepartmentSummarySerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from accounts.permissions import admin_required # Or use DRF permissions

# Permissions note: 
# - IsAdminUser checks user.is_staff. Ensure roles needing admin access have is_staff=True.
# - IsAuthenticated ensures the user is logged in.
# - Custom permissions might be needed for more granular control (e.g., TL edits own team).

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Departments.
    Typically restricted to Admins/Senior Managers.
    """
    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUser] # Only staff users (Admins/Senior Managers) can manage departments

class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Teams.
    Admins/Managers can manage all. Team Leaders might have limited edit scope.
    """
    queryset = Team.objects.select_related("department", "leader").all().order_by("department__name", "name")
    serializer_class = TeamSerializer
    # More complex permissions might be needed here:
    # - Admins/Managers: Full CRUD
    # - Team Leaders: Maybe PUT/PATCH for their own team?
    # For now, restrict to staff users for simplicity.
    permission_classes = [IsAdminUser] 

class DepartmentSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Department Summaries.
    Read-only access, permissions depend on who should see these summaries.
    """
    queryset = DepartmentSummary.objects.select_related("department", "card", "session").all()
    serializer_class = DepartmentSummarySerializer
    # Permissions: Admins, Senior Managers, relevant Department Managers?
    permission_classes = [IsAuthenticated] # Start with authenticated, refine later if needed
    # Add filtering based on user role (e.g., manager sees own department summary)
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.has_admin_privileges:
    #         return DepartmentSummary.objects.all()
    #     elif user.is_department_manager:
    #         return DepartmentSummary.objects.filter(department__department_manager=user)
    #     # Add other roles as needed
    #     return DepartmentSummary.objects.none()

