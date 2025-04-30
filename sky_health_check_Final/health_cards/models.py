from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

class HealthCard(models.Model):
    """
    Represents a specific area or topic to be evaluated during a health check.
    Each card has a title, description, and examples of good/bad practices.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                        help_text="Unique identifier for the health card.")
    title = models.CharField(max_length=100, unique=True, 
                           help_text="Concise title for the health card topic.")
    description = models.TextField(help_text="Detailed description of the health card topic.")
    example_awesome = models.TextField(help_text="Example illustrating a positive state (Green).", 
                                     verbose_name="Awesome Example")
    example_crappy = models.TextField(help_text="Example illustrating a negative state (Red).", 
                                    verbose_name="Crappy Example")
    created_at = models.DateTimeField(auto_now_add=True,
                                    help_text="Timestamp when the health card was created.")
    is_active = models.BooleanField(default=True, 
                                  help_text="Whether this card is currently active and available for sessions.")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        verbose_name = "Health Card"
        verbose_name_plural = "Health Cards"

class HealthCheckSession(models.Model):
    """
    Represents a specific health check event for a team, typically tied to a quarter and year.
    It defines the period during which team members can vote on selected health cards.
    """
    QUARTER_CHOICES = (
        ("Q1", "Q1 (Jan-Mar)"),
        ("Q2", "Q2 (Apr-Jun)"),
        ("Q3", "Q3 (Jul-Sep)"),
        ("Q4", "Q4 (Oct-Dec)"),
    )

    STATUS_CHOICES = (
        ("open", "Open"),         # Session is active, voting is allowed
        ("closed", "Closed"),       # Session is finished, voting is not allowed
        # Potentially add other statuses like 'scheduled' in the future
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                        help_text="Unique identifier for the health check session.")
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, 
                           related_name="health_check_sessions", # Changed related_name for clarity
                           help_text="The team participating in this session.")
    quarter = models.CharField(max_length=2, choices=QUARTER_CHOICES,
                             help_text="The quarter this session belongs to.")
    # Use current year as default for convenience
    year = models.IntegerField(default=timezone.now().year, 
                             help_text="The year this session belongs to.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open",
                            help_text="Current status of the session (Open/Closed).")
    created_at = models.DateTimeField(auto_now_add=True,
                                    help_text="Timestamp when the session was created.")
    # Use ManyToManyField to link selected cards for this specific session
    cards = models.ManyToManyField(HealthCard, related_name="health_check_sessions", # Changed related_name for clarity
                                 help_text="Health cards included in this session.",
                                 limit_choices_to={"is_active": True}) # Only allow active cards
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                 null=True, blank=True, related_name="created_sessions",
                                 help_text="User who created this session (typically Team Leader or Admin).")
    closed_at = models.DateTimeField(null=True, blank=True,
                                   help_text="Timestamp when the session was closed.")

    def __str__(self):
        return f"{self.team.name} - {self.get_quarter_display()} {self.year}"

    def close_session(self):
        """Marks the session as closed and records the closing time."""
        if self.status == "open":
            self.status = "closed"
            self.closed_at = timezone.now()
            self.save()

    def reopen_session(self):
        """Reopens a closed session."""
        if self.status == "closed":
            self.status = "open"
            self.closed_at = None # Clear the closed timestamp
            self.save()

    class Meta:
        ordering = ["-year", "-quarter", "team__name"]
        # Ensure only one session exists per team, quarter, and year combination
        unique_together = ("team", "quarter", "year")
        verbose_name = "Health Check Session"
        verbose_name_plural = "Health Check Sessions"

