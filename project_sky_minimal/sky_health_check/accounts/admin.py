from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User # Removed Admin model import as it wasn't used
from .forms import UserAdminCreationForm, UserAdminChangeForm

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "team_display", # Use a method for potentially missing team
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_staff", "is_active", "team__department", "team") # Filter by department
    search_fields = ("username", "first_name", "last_name", "email", "team__name")
    ordering = ("username",)

    # Group fieldsets more logically
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Role & Team"), {"fields": ("role", "team")}), # Group role and team
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            # Ensure role and team are in the add form
            "fields": ("username", "email", "password", "password2", "role", "team", "first_name", "last_name"),
        }),
    )

    @admin.display(description="Team", ordering="team") # Corrected syntax
    def team_display(self, obj):
        return obj.team.name if obj.team else _("No Team Assigned")

# No need to register Admin model if it is not being used directly

