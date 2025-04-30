from rest_framework import viewsets, permissions
from .models import HealthCard, HealthCheckSession
from .serializers import HealthCardSerializer, HealthCheckSessionSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class HealthCardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Health Cards.
    Restricted to Admins/Senior Managers.
    """
    queryset = HealthCard.objects.all().order_by("title")
    serializer_class = HealthCardSerializer
    permission_classes = [IsAdminUser] # Only staff users can manage health cards

class HealthCheckSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Health Check Sessions.
    Admins/Managers can manage all. Team Leaders can manage their team's sessions.
    Other users might have read-only access depending on requirements.
    """
    queryset = HealthCheckSession.objects.select_related("team", "created_by").prefetch_related("cards").all().order_by("-year", "-quarter", "team__name")
    serializer_class = HealthCheckSessionSerializer
    # permission_classes = [IsAuthenticated] # Base permission: must be logged in

    def get_permissions(self):
        """Instantiates and returns the list of permissions that this view requires."""
        if self.action in ["create", "update", "partial_update", "destroy", "close", "reopen"]:
            # Only Admins/Senior Managers or the Team Leader of the specific team can modify
            # Custom permission class might be better here for object-level checks
            permission_classes = [IsAuthenticated, IsAdminUser] # Simplified for now
        else: # list, retrieve
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter sessions based on user role."""
        user = self.request.user
        if user.has_admin_privileges:
            return HealthCheckSession.objects.all()
        elif user.is_department_manager:
            return HealthCheckSession.objects.filter(team__department__department_manager=user)
        elif user.is_team_leader:
            # Team leaders see sessions for teams they lead
            return HealthCheckSession.objects.filter(team__leader=user)
        elif user.is_engineer:
            # Engineers see sessions for their team
            if user.team:
                return HealthCheckSession.objects.filter(team=user.team)
            else:
                return HealthCheckSession.objects.none()
        return HealthCheckSession.objects.none()

    # Add custom actions for closing/reopening sessions
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser]) # Adjust permissions as needed
    def close(self, request, pk=None):
        session = self.get_object()
        if session.status == "open":
            session.close_session()
            return Response({"status": "session closed"})
        else:
            return Response({"status": "session already closed"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser]) # Adjust permissions as needed
    def reopen(self, request, pk=None):
        session = self.get_object()
        if session.status == "closed":
            session.reopen_session()
            return Response({"status": "session reopened"})
        else:
            return Response({"status": "session already open"}, status=status.HTTP_400_BAD_REQUEST)

    # Pass request context to serializer for create action
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

