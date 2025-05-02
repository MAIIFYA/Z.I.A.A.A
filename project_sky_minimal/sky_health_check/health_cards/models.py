from django.db import models
import uuid

class HealthCard(models.Model):
    """
    Health Card model for Sky Health Check
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    # Renamed from example_awesome to match JSON
    example_green = models.TextField(help_text="Example of green status")
    # Added field to match JSON
    example_amber = models.TextField(help_text="Example of amber status", default=".")
    # Renamed from example_crappy to match JSON
    example_red = models.TextField(help_text="Example of red status")
    # Added field to match JSON
    image_path = models.CharField(max_length=255, blank=True, help_text="Path to the card image relative to static files")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]

class HealthCheckSession(models.Model):
    """
    Health Check Session model for team health check sessions
    """
    # Removed QUARTER_CHOICES as name/date is used
    # QUARTER_CHOICES = (
    #     ("Q1", "Q1"),
    #     ("Q2", "Q2"),
    #     ("Q3", "Q3"),
    #     ("Q4", "Q4"),
    # )

    STATUS_CHOICES = (
        ("open", "Open"),
        ("closed", "Closed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="sessions")
    name = models.CharField(max_length=100, help_text="Session name, e.g., Q1 2024") # Added name field
    session_date = models.DateField(help_text="Date the session represents or was held") # Added date field
    # Removed quarter and year fields, replaced by name/date
    # quarter = models.CharField(max_length=2, choices=QUARTER_CHOICES)
    # year = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    # Removed cards M2M, seems redundant if votes link session and card
    # cards = models.ManyToManyField(HealthCard, related_name="sessions")

    def __str__(self):
        # return f"{self.team.name} - {self.quarter} {self.year}"
        return f"{self.team.name} - {self.name}"

    class Meta:
        # ordering = ["-year", "-quarter"]
        ordering = ["-session_date"]
        # unique_together = ("team", "quarter", "year")
        unique_together = ("team", "name") # Ensure unique session names per team

