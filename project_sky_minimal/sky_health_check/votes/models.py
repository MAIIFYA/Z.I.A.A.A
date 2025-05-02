from django.db import models
import uuid

class Vote(models.Model):
    """
    Vote model for Sky Health Check
    """
    VOTE_VALUE_CHOICES = (
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red'),
    )
    
    TREND_CHOICES = (
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey('health_cards.HealthCheckSession', on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='votes')
    card = models.ForeignKey('health_cards.HealthCard', on_delete=models.CASCADE, related_name='votes')
    vote_value = models.CharField(max_length=10, choices=VOTE_VALUE_CHOICES)
    trend = models.CharField(max_length=10, choices=TREND_CHOICES)
    comment = models.TextField(blank=True, null=True)
    comment_summary = models.TextField(blank=True, null=True, help_text="AI-generated summary of comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s vote on {self.card.title} for {self.session}"
    
    class Meta:
        unique_together = ('session', 'user', 'card')
        ordering = ['-created_at']
