from django.db import models
import uuid

class Department(models.Model):
    """
    Department model for Sky Health Check
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    senior_manager = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name='managed_departments')
    
    def __str__(self):
        return self.name

class Team(models.Model):
    """
    Team model for Sky Health Check
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')
    leader = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='led_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.department.name})"
    
    class Meta:
        ordering = ['name']

class DepartmentSummary(models.Model):
    """
    Department Summary model for aggregated department data
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='summaries')
    card = models.ForeignKey('health_cards.HealthCard', on_delete=models.CASCADE)
    session = models.ForeignKey('health_cards.HealthCheckSession', on_delete=models.CASCADE)
    green_count = models.IntegerField(default=0)
    amber_count = models.IntegerField(default=0)
    red_count = models.IntegerField(default=0)
    improving_count = models.IntegerField(default=0)
    stable_count = models.IntegerField(default=0)
    declining_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Summary for {self.department.name} - {self.session}"
    
    class Meta:
        unique_together = ('department', 'card', 'session')
        verbose_name_plural = 'Department summaries'
