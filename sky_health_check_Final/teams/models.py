from django.db import models
from django.conf import settings
import uuid

class Department(models.Model):
    """
    Represents a department within the organization.
    Each department can have multiple teams and is managed by a Senior Manager.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                        help_text="Unique identifier for the department.")
    name = models.CharField(max_length=100, unique=True, 
                          help_text="Name of the department.")
    created_at = models.DateTimeField(auto_now_add=True,
                                    help_text="Timestamp when the department was created.")
    # Allow null in case a senior manager leaves or is unassigned
    senior_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="managed_departments",
        limit_choices_to={"role": "senior_manager"}, # Ensure only senior managers can be assigned
        help_text="The Senior Manager responsible for overseeing this department."
    )
    # Add department manager relationship as per ERD (Manages relationship)
    department_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="directly_managed_departments",
        limit_choices_to={"role": "department_manager"}, # Ensure only department managers can be assigned
        help_text="The Department Manager directly managing this department."
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"

class Team(models.Model):
    """
    Represents a team within a department.
    Each team has a leader and belongs to a specific department.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                        help_text="Unique identifier for the team.")
    name = models.CharField(max_length=100, 
                          help_text="Name of the team.")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, 
                                 related_name="teams",
                                 help_text="The department this team belongs to.")
    # Allow null in case a team leader leaves or is unassigned
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="led_teams",
        limit_choices_to={"role": "team_leader"}, # Ensure only team leaders can be assigned
        help_text="The Team Leader responsible for this team."
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                    help_text="Timestamp when the team was created.")

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    class Meta:
        ordering = ["department__name", "name"]
        unique_together = ("name", "department") # Team names should be unique within a department
        verbose_name = "Team"
        verbose_name_plural = "Teams"

class DepartmentSummary(models.Model):
    """
    Stores aggregated health check summary data for a department per card per session.
    This model facilitates reporting and trend analysis at the department level.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                        help_text="Unique identifier for the department summary record.")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, 
                                 related_name="department_summaries",
                                 help_text="The department this summary belongs to.")
    card = models.ForeignKey("health_cards.HealthCard", on_delete=models.CASCADE,
                           help_text="The health card this summary relates to.")
    session = models.ForeignKey("health_cards.HealthCheckSession", on_delete=models.CASCADE,
                              help_text="The health check session this summary is for.")
    
    # Aggregated vote counts
    green_count = models.IntegerField(default=0, help_text="Number of 'Green' votes.")
    amber_count = models.IntegerField(default=0, help_text="Number of 'Amber' votes.")
    red_count = models.IntegerField(default=0, help_text="Number of 'Red' votes.")
    
    # Aggregated trend counts
    improving_count = models.IntegerField(default=0, help_text="Number of 'Improving' trend votes.")
    stable_count = models.IntegerField(default=0, help_text="Number of 'Stable' trend votes.")
    declining_count = models.IntegerField(default=0, help_text="Number of 'Declining' trend votes.")
    
    created_at = models.DateTimeField(auto_now_add=True,
                                    help_text="Timestamp when the summary record was created.")
    updated_at = models.DateTimeField(auto_now=True,
                                    help_text="Timestamp when the summary record was last updated.")

    def __str__(self):
        return f"Summary for {self.department.name} - Card: {self.card.title} - Session: {self.session}"

    class Meta:
        # Ensure only one summary record exists per department, card, and session combination
        unique_together = ("department", "card", "session")
        verbose_name = "Department Summary"
        verbose_name_plural = "Department Summaries"
        ordering = ["-session__year", "-session__quarter", "department__name", "card__title"]

