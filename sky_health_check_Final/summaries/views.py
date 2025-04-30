from rest_framework import viewsets, permissions
from .models import TeamSummary, VoteSummary
from .serializers import TeamSummarySerializer, VoteSummarySerializer
from rest_framework.permissions import IsAuthenticated

class TeamSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Team Summaries.
    Read-only access. Permissions depend on who should see these summaries.
    """
    serializer_class = TeamSummarySerializer
    permission_classes = [IsAuthenticated] # Base permission

    def get_queryset(self):
        """Filter summaries based on user role."""
        user = self.request.user
        if user.has_admin_privileges:
            return TeamSummary.objects.select_related("team", "card", "session").all()
        elif user.is_department_manager:
            # Department managers see summaries for teams in their department(s)
            return TeamSummary.objects.filter(team__department__department_manager=user).select_related("team", "card", "session")
        elif user.is_team_leader:
            # Team leaders see summaries for teams they lead
            return TeamSummary.objects.filter(team__leader=user).select_related("team", "card", "session")
        elif user.is_engineer:
            # Engineers see summaries for their team
            if user.team:
                return TeamSummary.objects.filter(team=user.team).select_related("team", "card", "session")
            else:
                return TeamSummary.objects.none()
        return TeamSummary.objects.none()

class VoteSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing historical Vote Summaries.
    Read-only access. Permissions similar to TeamSummary.
    """
    serializer_class = VoteSummarySerializer
    permission_classes = [IsAuthenticated] # Base permission

    def get_queryset(self):
        """Filter historical summaries based on user role."""
        user = self.request.user
        if user.has_admin_privileges:
            return VoteSummary.objects.select_related("team", "card").all()
        elif user.is_department_manager:
            return VoteSummary.objects.filter(team__department__department_manager=user).select_related("team", "card")
        elif user.is_team_leader:
            return VoteSummary.objects.filter(team__leader=user).select_related("team", "card")
        elif user.is_engineer:
            # Do engineers need to see historical trends? Maybe just TL/Managers.
            # For now, restrict to TL/Managers/Admins.
            return VoteSummary.objects.none()
        return VoteSummary.objects.none()

