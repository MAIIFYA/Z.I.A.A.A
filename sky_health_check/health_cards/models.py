from django.db import models
import uuid

class HealthCard(models.Model):
    """
    Health Card model for Sky Health Check
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    example_awesome = models.TextField(help_text="Example of good practice")
    example_crappy = models.TextField(help_text="Example of bad practice")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']

class HealthCheckSession(models.Model):
    """
    Health Check Session model for team health check sessions
    """
    QUARTER_CHOICES = (
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='sessions')
    quarter = models.CharField(max_length=2, choices=QUARTER_CHOICES)
    year = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    cards = models.ManyToManyField(HealthCard, related_name='sessions')
    
    def __str__(self):
        return f"{self.team.name} - {self.quarter} {self.year}"
    
    class Meta:
        ordering = ['-year', '-quarter']
        unique_together = ('team', 'quarter', 'year')
