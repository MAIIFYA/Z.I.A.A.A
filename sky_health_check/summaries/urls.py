from django.urls import path
from . import views

urlpatterns = [
    path('team-summary/', views.team_summary, name='team_summary'),
    path('department-summary/', views.department_summary, name='department_summary'),
    
    # API endpoints
    path('api/team-summary/<int:team_id>/', views.get_team_summary, name='get_team_summary'),
    path('api/team-summary/<int:team_id>/<int:session_id>/', views.get_team_summary, name='get_team_session_summary'),
    path('api/department-summary/<int:department_id>/', views.get_department_summary, name='get_department_summary'),
    path('api/department-summary/<int:department_id>/<int:quarter>/<int:year>/', views.get_department_summary, name='get_department_quarter_summary'),
    path('api/department/<int:department_id>/quarters/', views.get_available_quarters, name='get_available_quarters'),
    path('api/comments/<int:session_id>/<int:card_id>/', views.get_card_comments, name='get_card_comments'),
]
