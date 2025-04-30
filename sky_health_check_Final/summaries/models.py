from django.db import models
from django.conf import settings
import uuid

class TeamSummary(models.Model):
    """
    Stores aggregated health check summary data for a specific team, card, and session.
    This facilitates reporting and displaying results at the team level.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                        help_text="Unique identifier for the team summary record.")
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, 
                           related_name="team_summaries", # Changed related_name
                           help_text="The team this summary belongs to.")
    card = models.ForeignKey("health_cards.HealthCard", on_delete=models.CASCADE,
                           help_text="The health card this summary relates to.")
    session = models.ForeignKey("health_cards.HealthCheckSession", on_delete=models.CASCADE,
                              help_text="The health check session this summary is for.")
    
    # Aggregated vote counts for the team in this session for this card
    green_count = models.IntegerField(default=0, help_text="Number of 'Green' votes.")
    amber_count = models.IntegerField(default=0, help_text="Number of 'Amber' votes.")
    red_count = models.IntegerField(default=0, help_text="Number of 'Red' votes.")
    
    # Aggregated trend counts for the team in this session for this card
    improving_count = models.IntegerField(default=0, help_text="Number of 'Improving' trend votes.")
    stable_count = models.IntegerField(default=0, help_text="Number of 'Stable' trend votes.")
    declining_count = models.IntegerField(default=0, help_text="Number of 'Declining' trend votes.")
    
    # Field for potential AI summary of all comments for this card in this session
    aggregated_comments_summary = models.TextField(blank=True, null=True, 
                                               help_text="(Beta) AI-generated summary of all comments for this card in this session.",
                                               verbose_name="Aggregated Comments Summary (Beta)")
    
    created_at = models.DateTimeField(auto_now_add=True,
                                    help_text="Timestamp when the summary record was created.")
    updated_at = models.DateTimeField(auto_now=True,
                                    help_text="Timestamp when the summary record was last updated (e.g., when votes are added/changed).")

    def __str__(self):
        return f"Summary for {self.team.name} - Card: {self.card.title} - Session: {self.session}"

    class Meta:
        # Ensure only one summary record exists per team, card, and session combination
        unique_together = ("team", "card", "session")
        verbose_name = "Team Summary"
        verbose_name_plural = "Team Summaries"
        ordering = ["-session__year", "-session__quarter", "team__name", "card__title"]

class VoteSummary(models.Model):
    """
    Stores historical, aggregated vote data (percentages and overall trend) 
    for a team and card combination over a specific quarter/year.
    This is used for tracking trends over time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                        help_text="Unique identifier for the vote summary record.")
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, 
                           related_name="vote_history",
                           help_text="The team this historical summary belongs to.")
    card = models.ForeignKey("health_cards.HealthCard", on_delete=models.CASCADE,
                           help_text="The health card this historical summary relates to.")
    quarter = models.CharField(max_length=2, 
                             choices=settings.QUARTER_CHOICES, # Assuming QUARTER_CHOICES is defined in settings or imported
                             help_text="The quarter this summary represents.")
    year = models.IntegerField(help_text="The year this summary represents.")
    
    # Calculated percentages based on votes in the corresponding session
    green_percentage = models.FloatField(default=0, help_text="Percentage of 'Green' votes.")
    amber_percentage = models.FloatField(default=0, help_text="Percentage of 'Amber' votes.")
    red_percentage = models.FloatField(default=0, help_text="Percentage of 'Red' votes.")
    
    # Calculated overall trend based on votes in the corresponding session
    aggregated_trend = models.CharField(max_length=10, 
                                      choices=settings.TREND_CHOICES, # Assuming TREND_CHOICES is defined or imported
                                      default="stable", 
                                      help_text="Overall calculated trend for this card in this period.",
                                      verbose_name="Aggregated Trend")
    
    created_at = models.DateTimeField(auto_now_add=True,
                                    help_text="Timestamp when the historical summary record was created.")
    updated_at = models.DateTimeField(auto_now=True, # Add updated_at for tracking changes
                                    help_text="Timestamp when the historical summary record was last updated.")

    def __str__(self):
        return f"Vote History for {self.team.name} - Card: {self.card.title} - {self.get_quarter_display()} {self.year}"

    class Meta:
        # Ensure only one historical summary exists per team, card, quarter, and year
        unique_together = ("team", "card", "quarter", "year")
        ordering = ["-year", "-quarter", "team__name", "card__title"]
        verbose_name = "Vote Summary (Historical)"
        verbose_name_plural = "Vote Summaries (Historical)"

