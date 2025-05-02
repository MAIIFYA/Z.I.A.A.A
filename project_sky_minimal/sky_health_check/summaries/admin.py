from django.contrib import admin
from .models import TeamSummary, VoteSummary # Removed DepartmentSummary import from here
from teams.models import DepartmentSummary # Import DepartmentSummary from teams.models
from health_cards.models import HealthCheckSession # Import needed for session access
from django.utils.html import format_html

# Common function for trend icons
def get_trend_icon(trend):
    if trend == "improving":
        return format_html("<span style=\"color: green; font-size: 1.2em;\" title=\"Improving\">&#9650;</span>") # Up arrow
    elif trend == "declining":
        return format_html("<span style=\"color: red; font-size: 1.2em;\" title=\"Declining\">&#9660;</span>") # Down arrow
    elif trend == "stable":
        return format_html("<span style=\"color: orange; font-size: 1.2em;\" title=\"Stable\">&#9654;</span>") # Right arrow
    return "-"

@admin.register(TeamSummary)
class TeamSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "team",
        "card",
        "session_name_link", # Link to session
        "green_count",
        "amber_count",
        "red_count",
        "updated_at",
    )
    search_fields = ("team__name", "card__title", "session__name")
    list_filter = ("team__department", "session__session_date", "card", "team")
    date_hierarchy = "session__session_date"
    readonly_fields = (
        "session",
        "team",
        "card",
        "green_count",
        "amber_count",
        "red_count",
        "comments_summary", # Keep if model has this field
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "team",
        "card",
        "session",
    ) # Optimize queries

    @admin.display(ordering="session__name", description="Session")
    def session_name_link(self, obj):
        from django.urls import reverse
        if obj.session:
            link = reverse("admin:health_cards_healthchecksession_change", args=[obj.session.id])
            return format_html("<a href=\"{}\">{}</a>", link, obj.session.name)
        return "N/A"

@admin.register(DepartmentSummary)
class DepartmentSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "department",
        "card",
        "session_name_link", # Link to session
        "green_count",
        "amber_count",
        "red_count",
        "updated_at",
    )
    search_fields = ("department__name", "card__title", "session__name")
    list_filter = ("department", "session__session_date", "card")
    date_hierarchy = "session__session_date"
    readonly_fields = (
        "session",
        "department",
        "card",
        "green_count",
        "amber_count",
        "red_count",
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "department",
        "card",
        "session",
    ) # Optimize queries

    @admin.display(ordering="session__name", description="Session")
    def session_name_link(self, obj):
        from django.urls import reverse
        if obj.session:
            link = reverse("admin:health_cards_healthchecksession_change", args=[obj.session.id])
            return format_html("<a href=\"{}\">{}</a>", link, obj.session.name)
        return "N/A"

@admin.register(VoteSummary)
class VoteSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "team",
        "card",
        "session_name_link", # Link to session
        "session_date",
        "green_percentage_display",
        "amber_percentage_display",
        "red_percentage_display",
        "trend_icon",
        "created_at",
    )
    search_fields = ("team__name", "card__title", "session__name")
    list_filter = ("team__department", "session__session_date", "card", "trend", "team")
    date_hierarchy = "session__session_date"
    readonly_fields = (
        "session",
        "team",
        "card",
        "green_percentage",
        "amber_percentage",
        "red_percentage",
        "trend",
        "created_at",
    )
    list_select_related = (
        "team",
        "card",
        "session",
    ) # Optimize queries

    @admin.display(ordering="session__name", description="Session")
    def session_name_link(self, obj):
        from django.urls import reverse
        if obj.session:
            link = reverse("admin:health_cards_healthchecksession_change", args=[obj.session.id])
            return format_html("<a href=\"{}\">{}</a>", link, obj.session.name)
        return "N/A"

    @admin.display(ordering="session__session_date", description="Session Date")
    def session_date(self, obj):
        return obj.session.session_date if obj.session else "N/A"

    @admin.display(ordering="green_percentage", description="Green %")
    def green_percentage_display(self, obj):
        return f"{obj.green_percentage:.1f}%" if obj.green_percentage is not None else "-"

    @admin.display(ordering="amber_percentage", description="Amber %")
    def amber_percentage_display(self, obj):
        return f"{obj.amber_percentage:.1f}%" if obj.amber_percentage is not None else "-"

    @admin.display(ordering="red_percentage", description="Red %")
    def red_percentage_display(self, obj):
        return f"{obj.red_percentage:.1f}%" if obj.red_percentage is not None else "-"

    @admin.display(ordering="trend", description="Trend")
    def trend_icon(self, obj):
        return get_trend_icon(obj.trend)


