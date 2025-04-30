from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model for Sky Health Check
    """
    ROLE_CHOICES = (
        ('engineer', 'Engineer'),
        ('team_leader', 'Team Leader'),
        ('senior_manager', 'Senior Manager'),
        ('department_manager', 'Department Manager'),
        ('admin', 'Administrator'),
    )
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='engineer')
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_engineer(self):
        return self.role == 'engineer'
    
    @property
    def is_team_leader(self):
        return self.role == 'team_leader'
    
    @property
    def is_senior_manager(self):
        return self.role == 'senior_manager'
    
    @property
    def is_department_manager(self):
        return self.role == 'department_manager'
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

class Admin(models.Model):
    """
    Admin model for additional admin-specific data
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Admin: {self.user.username}"
