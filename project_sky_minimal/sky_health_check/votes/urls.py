from django.urls import path
from . import views

urlpatterns = [
    path('vote/', views.vote_page, name='vote_page'),
    path("vote/summary/<uuid:session_id>/", views.vote_summary, name="vote_summary"),
    path("sessions/<uuid:session_id>/close/", views.close_session, name="close_session"),
    
    # API endpoints
    path('api/vote/submit/', views.submit_vote, name='submit_vote'),
    path("api/vote/user/<uuid:session_id>/", views.get_user_votes, name="get_user_votes"),
    path("api/vote/session/<uuid:session_id>/", views.get_session_votes, name="get_session_votes"),
    path("api/vote/summarize/<uuid:session_id>/<uuid:card_id>/", views.summarize_comments, name="summarize_comments"),
]
