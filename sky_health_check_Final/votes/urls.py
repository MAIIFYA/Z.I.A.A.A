from django.urls import path
from . import views

# Define app_name for namespacing
app_name = "votes"

urlpatterns = [
    # Page Views (Consider moving to a different app or using DRF for API-first approach)
    path("page/", views.vote_page, name="vote_page"), # Example page view, might need refinement
    
    # API endpoints
    path("api/submit/", views.submit_vote, name="submit_vote_api"),
    path("api/user/<uuid:session_id>/", views.get_user_votes, name="get_user_votes_api"),
    path("api/session/<uuid:session_id>/", views.get_session_votes, name="get_session_votes_api"),
    path("api/summarize/<uuid:session_id>/<uuid:card_id>/", views.summarize_comments_api, name="summarize_comments_api"),
    
    # Removed old/redundant URLs:
    # path("vote/summary/<int:session_id>/", views.vote_summary, name="vote_summary"), # Replaced by API
    # path("sessions/<int:session_id>/close/", views.close_session, name="close_session"), # Session management should be separate
]

