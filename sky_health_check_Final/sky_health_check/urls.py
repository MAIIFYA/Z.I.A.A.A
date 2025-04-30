from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required

# Import views from your apps if needed for frontend pages
# Example: from accounts.views import profile_view
# Example: from summaries.views import summary_dashboard_view

# API URL patterns (keep as is)
api_urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("teams/", include("teams.urls")),
    path("health-cards/", include("health_cards.urls")),
    path("votes/", include("votes.urls")),
    path("summaries/", include("summaries.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/v1/", include(api_urlpatterns)),
    # Authentication (django-allauth)
    path("auth/", include("allauth.urls")), 

    # Frontend Pages (require login)
    path("dashboard/", login_required(TemplateView.as_view(template_name="dashboard.html")), name="dashboard"),
    path("vote/", login_required(TemplateView.as_view(template_name="votes/vote_page.html")), name="vote_page"),
    # TODO: Add URLs for Profile, Summaries, Admin frontend pages when created
    # path("profile/", login_required(profile_view), name="profile"),
    # path("summaries/", login_required(summary_dashboard_view), name="summaries"),
    # path("administration/", login_required(admin_dashboard_view), name="administration"), # Needs appropriate permission check too

    # Root URL: Redirect to dashboard if logged in, otherwise to login page
    path("", RedirectView.as_view(pattern_name="dashboard", permanent=False), name="home_redirect_authenticated"), # This might need adjustment based on how allauth handles redirects
    # A simpler approach might be a custom view or handling this in middleware/login view.
    # For now, let's assume allauth redirects to LOGIN_REDIRECT_URL which we can set to /dashboard/
    path("", TemplateView.as_view(template_name="home.html"), name="home"), # A simple landing/home page if needed before login

]

# Update LOGIN_REDIRECT_URL in settings.py to point to "/dashboard/"
# Update LOGOUT_REDIRECT_URL in settings.py if needed (e.g., to "/auth/login/")

# Serve static files during development (using Django's staticfiles app)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Note: static() helper is usually for user-uploaded media files.
    # Static files (CSS, JS, images) are typically handled by the staticfiles app automatically in DEBUG mode.
    # Ensure settings.STATIC_URL = 
    # Ensure settings.STATICFILES_DIRS is configured if static files are outside app directories.

