from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model for Sky Health Check
    Extends the default Django user model, using email as the unique identifier.
    Includes role-based access control.
    """
    ROLE_CHOICES = (
        ("engineer", "Engineer"),
        ("team_leader", "Team Leader"),
        ("senior_manager", "Senior Manager"),
        ("department_manager", "Department Manager"),
        ("admin", "Administrator"),
    )

    # Remove the default username field requirement from AbstractUser
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=False, # Allow multiple users to potentially have the same (unused) username
        null=True, # Allow null username
        blank=True, # Allow blank username in forms
        help_text=(
            _("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")
        ),
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), unique=True, 
                              help_text=_("Required. Used for login."))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="engineer",
                          help_text=_("User role determining permissions."))
    team = models.ForeignKey("teams.Team", on_delete=models.SET_NULL, null=True, blank=True, 
                           related_name="members", help_text=_("The team this user belongs to, if any."))

    # Use email for authentication instead of username
    USERNAME_FIELD = "email"
    # email is already required by USERNAME_FIELD, username is not required for createsuperuser
    REQUIRED_FIELDS = [] 

    def __str__(self):
        # Display user's full name if available, otherwise email
        display_name = self.get_full_name() or self.email
        return f"{display_name} ({self.get_role_display()})"

    # --- Role Properties --- 
    # These properties provide convenient checks for user roles in templates and views.

    @property
    def is_engineer(self):
        return self.role == "engineer"

    @property
    def is_team_leader(self):
        return self.role == "team_leader"

    @property
    def is_senior_manager(self):
        # Senior Managers have admin-like capabilities as per user request
        return self.role == "senior_manager"

    @property
    def is_department_manager(self):
        return self.role == "department_manager"

    @property
    def has_admin_privileges(self):
        # Check if user is superuser, has 'admin' role, or 'senior_manager' role
        return self.is_superuser or self.role == "admin" or self.role == "senior_manager"

    def save(self, *args, **kwargs):
        # Ensure senior managers are also marked as staff for Django admin access
        if self.role == "senior_manager":
            self.is_staff = True
        # Ensure users with admin role are marked as staff
        elif self.role == "admin":
             self.is_staff = True
        # Non-admin/senior manager roles should not automatically be staff unless explicitly set
        # (Superusers are handled by Django's default logic)
        elif not self.is_superuser:
             self.is_staff = False # Ensure non-admins/seniors aren't staff by default
             
        super().save(*args, **kwargs)

# Removed the separate Admin model as role and superuser status are handled within the User model.

