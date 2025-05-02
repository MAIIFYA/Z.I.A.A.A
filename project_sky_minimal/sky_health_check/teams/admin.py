from django.contrib import admin
from .models import Department, Team
# Removed DepartmentSummary import as it's likely in the summaries app

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "senior_manager_display", # Use display method
        "team_count", # Add team count
        "created_at",
    )
    search_fields = ("name", "senior_manager__username", "senior_manager__email")
    list_filter = ("created_at",)
    # Removed updated_at as it doesn\u0027t exist on the model
    readonly_fields = ("created_at",)

    @admin.display(description="Senior Manager", ordering="senior_manager")
    def senior_manager_display(self, obj):
        return obj.senior_manager.get_full_name() or obj.senior_manager.username if obj.senior_manager else "-"

    @admin.display(description="Teams")
    def team_count(self, obj):
        return obj.teams.count()

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "department",
        "leader_display", # Use display method
        "member_count", # Add member count
        "created_at",
    )
    search_fields = ("name", "department__name", "leader__username", "leader__email")
    list_filter = ("department", "created_at")
    autocomplete_fields = ["leader", "department"] # Easier selection for FKs
    # Removed updated_at as it doesn\u0027t exist on the model
    readonly_fields = ("created_at",)

    @admin.display(description="Leader", ordering="leader")
    def leader_display(self, obj):
        return obj.leader.get_full_name() or obj.leader.username if obj.leader else "-"

    @admin.display(description="Members")
    def member_count(self, obj):
        # Assuming User model has a ForeignKey or M2M relation to Team named \u0027team\u0027
        # Adjust the filter if the relation name is different
        return obj.members.count() # Use the related name \u0027members\u0027 from User model

# Removed DepartmentSummaryAdmin as it belongs in the summaries app

