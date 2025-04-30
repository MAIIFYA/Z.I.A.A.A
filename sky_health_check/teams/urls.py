from django.urls import path
from . import views

urlpatterns = [
    path('teams/', views.team_list, name='team_list'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<int:team_id>/update/', views.team_update, name='team_update'),
    path('teams/<int:team_id>/delete/', views.team_delete, name='team_delete'),
    
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:department_id>/', views.department_detail, name='department_detail'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:department_id>/update/', views.department_update, name='department_update'),
    path('departments/<int:department_id>/delete/', views.department_delete, name='department_delete'),
    
    # API endpoints
    path('api/teams/<int:team_id>/members/', views.get_team_members, name='get_team_members'),
    path('api/departments/<int:department_id>/teams/', views.get_department_teams, name='get_department_teams'),
]
