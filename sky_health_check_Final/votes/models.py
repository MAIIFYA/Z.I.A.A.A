from django.db import models
from django.conf import settings
import uuid

class Vote(models.Model):
    """
    Represents a single vote cast by a user for a specific health card within a session.
    Includes the vote value (traffic light), perceived trend, and an optional comment.
    """
    VOTE_VALUE_CHOICES = (
        ("green", "Green"),
        ("amber", "Amber"),
        ("red", "Red"),
    )

    TREND_CHOICES = (
        ("improving", "Improving"),
        ("stable", "Stable"),
        ("declining", "Declining"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                        help_text="Unique identifier for the vote.")
    session = models.ForeignKey("health_cards.HealthCheckSession", on_delete=models.CASCADE, 
                              related_name="session_votes", # Changed related_name for clarity
                              help_text="The health check session this vote belongs to.")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name="user_votes", # Changed related_name for clarity
                           help_text="The user who cast this vote.")
    card = models.ForeignKey("health_cards.HealthCard", on_delete=models.CASCADE, 
                           related_name="card_votes", # Changed related_name for clarity
                           help_text="The health card this vote is for.")
    vote_value = models.CharField(max_length=10, choices=VOTE_VALUE_CHOICES,
                                help_text="The traffic light value selected by the user.")
    trend = models.CharField(max_length=10, choices=TREND_CHOICES,
                           help_text="The trend perceived by the user.")
    comment = models.TextField(blank=True, null=True,
                             help_text="Optional comment provided by the user.")
    # Field for potential AI summary - marked as beta in UI
    comment_summary = models.TextField(blank=True, null=True, 
                                     help_text="(Beta) AI-generated summary of the comment.") 
    created_at = models.DateTimeField(auto_now_add=True,
                                    help_text="Timestamp when the vote was initially created.")
    updated_at = models.DateTimeField(auto_now=True,
                                    help_text="Timestamp when the vote was last updated.")

    def __str__(self):
        # Use user's display name (full name or email)
        user_display = self.user.get_full_name() or self.user.email
        return f"{user_display}'s vote on '{self.card.title}' for {self.session}"

    class Meta:
        # Ensure a user can only vote once per card within a single session
        unique_together = ("session", "user", "card")
        ordering = ["-created_at", "user__email"]
        verbose_name = "Vote"
        verbose_name_plural = "Votes"

