from django.urls import path
from . import views

urlpatterns = [
    path('health-cards/', views.health_card_list, name='health_card_list'),
    path('health-cards/<int:card_id>/', views.health_card_detail, name='health_card_detail'),
    path('health-cards/create/', views.health_card_create, name='health_card_create'),
    path('health-cards/<int:card_id>/update/', views.health_card_update, name='health_card_update'),
    path('health-cards/<int:card_id>/delete/', views.health_card_delete, name='health_card_delete'),
    
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/create/', views.session_create, name='session_create'),
    path('sessions/<int:session_id>/update/', views.session_update, name='session_update'),
    path('sessions/<int:session_id>/delete/', views.session_delete, name='session_delete'),
    
    # API endpoints
    path('api/sessions/<int:session_id>/cards/', views.get_session_cards, name='get_session_cards'),
    path('api/teams/<int:team_id>/sessions/', views.get_team_sessions, name='get_team_sessions'),
]
