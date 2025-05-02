from django.contrib import admin
from .models import HealthCard, HealthCheckSession
from django.utils.html import format_html
from django.templatetags.static import static # To resolve static paths

@admin.register(HealthCard)
class HealthCardAdmin(admin.ModelAdmin):
    list_display = ("title", "display_image", "created_at")
    search_fields = ("title", "description")
    # Removed updated_at as it doesn\u0027t exist on the model
    readonly_fields = ("created_at", "display_image_large")
    fieldsets = (
        (None, {"fields": ("title", "description")}),
        ("Visuals", {"fields": ("image_path", "display_image_large")}),
        ("Examples", {"fields": ("example_green", "example_amber", "example_red")}),
        ("Timestamps", {"fields": ("created_at",)}), # Removed updated_at
    )

    @admin.display(description="Image")
    def display_image(self, obj):
        if obj.image_path:
            image_url = static(obj.image_path)
            return format_html("<img src=\"{}\" width=\"50\" height=\"50\" style=\"object-fit: contain;\" />", image_url)
        return "No Image"

    @admin.display(description="Image Preview")
    def display_image_large(self, obj):
        if obj.image_path:
            image_url = static(obj.image_path)
            return format_html("<img src=\"{}\" width=\"150\" height=\"150\" style=\"object-fit: contain;\" />", image_url)
        return "No Image"

@admin.register(HealthCheckSession)
class HealthCheckSessionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "team",
        "session_date",
        "status",
        "card_count", # Add card count
        "vote_count", # Add vote count
        "created_at",
    )
    list_filter = ("status", "session_date", "team__department", "team") # Filter by department
    search_fields = ("name", "team__name", "team__department__name")
    date_hierarchy = "session_date" # Add date navigation
    autocomplete_fields = ["team"] # Easier team selection
    # Removed updated_at as it doesn\u0027t exist on the model
    readonly_fields = ("created_at", "card_count", "vote_count")
    fieldsets = (
        (None, {"fields": ("name", "team", "session_date", "status")}),
        ("Details", {"fields": ("card_count", "vote_count")}),
        ("Timestamps", {"fields": ("created_at",)}), # Removed updated_at
    )

    @admin.display(description="Cards")
    def card_count(self, obj):
        return HealthCard.objects.count()

    @admin.display(description="Votes")
    def vote_count(self, obj):
        return obj.votes.count()


