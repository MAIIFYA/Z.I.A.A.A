from django.db import models
import uuid

class TeamSummary(models.Model):
    """
    Team Summary model for aggregated team data
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="summaries")
    card = models.ForeignKey("health_cards.HealthCard", on_delete=models.CASCADE)
    session = models.ForeignKey("health_cards.HealthCheckSession", on_delete=models.CASCADE)
    green_count = models.IntegerField(default=0)
    amber_count = models.IntegerField(default=0)
    red_count = models.IntegerField(default=0)
    improving_count = models.IntegerField(default=0)
    stable_count = models.IntegerField(default=0)
    declining_count = models.IntegerField(default=0)
    comments_summary = models.TextField(blank=True, null=True, help_text="AI-generated summary of all comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for {self.team.name} - {self.session}"

    class Meta:
        unique_together = ("team", "card", "session")
        verbose_name_plural = "Team summaries"

class VoteSummary(models.Model):
    """
    Vote Summary model for historical tracking of votes over time
    (Note: This model might need further refinement based on how trends are calculated)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="vote_history")
    card = models.ForeignKey("health_cards.HealthCard", on_delete=models.CASCADE)
    # Replaced quarter/year with session FK
    session = models.ForeignKey("health_cards.HealthCheckSession", on_delete=models.CASCADE, null=True, blank=True) # Allow null initially if calculated later
    # quarter = models.CharField(max_length=2)
    # year = models.IntegerField()
    green_percentage = models.FloatField(default=0)
    amber_percentage = models.FloatField(default=0)
    red_percentage = models.FloatField(default=0)
    trend = models.CharField(max_length=10, default="stable")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return f"Vote history for {self.team.name} - {self.card.title} - {self.quarter} {self.year}"
        session_name = self.session.name if self.session else "N/A"
        return f"Vote history for {self.team.name} - {self.card.title} - {session_name}"

    class Meta:
        # unique_together = ("team", "card", "quarter", "year")
        unique_together = ("team", "card", "session") # Updated unique constraint
        # ordering = ["-year", "-quarter"]
        ordering = ["-session__session_date"] # Order by session date

