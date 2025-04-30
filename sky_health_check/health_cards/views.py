from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg
from .models import HealthCard, HealthCheckSession
from teams.models import Team
from accounts.permissions import admin_required, team_leader_required
from votes.models import Vote
import datetime

@login_required
def health_card_list(request):
    """View for listing health cards"""
    health_cards = HealthCard.objects.all().order_by('title')
    return render(request, 'health_cards/health_cards.html', {'health_cards': health_cards})

@login_required
def health_card_detail(request, card_id):
    """View for health card details"""
    card = get_object_or_404(HealthCard, id=card_id)
    return render(request, 'health_cards/health_card_detail.html', {'card': card})

@admin_required
def health_card_create(request):
    """View for creating a new health card"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        crappy_example = request.POST.get('crappy_example')
        awesome_example = request.POST.get('awesome_example')
        
        if title and description and crappy_example and awesome_example:
            card = HealthCard.objects.create(
                title=title,
                description=description,
                crappy_example=crappy_example,
                awesome_example=awesome_example
            )
            return redirect('health_card_detail', card_id=card.id)
    
    return render(request, 'health_cards/health_card_form.html')

@admin_required
def health_card_update(request, card_id):
    """View for updating a health card"""
    card = get_object_or_404(HealthCard, id=card_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        crappy_example = request.POST.get('crappy_example')
        awesome_example = request.POST.get('awesome_example')
        
        if title and description and crappy_example and awesome_example:
            card.title = title
            card.description = description
            card.crappy_example = crappy_example
            card.awesome_example = awesome_example
            card.save()
            return redirect('health_card_detail', card_id=card.id)
    
    return render(request, 'health_cards/health_card_form.html', {'card': card})

@admin_required
def health_card_delete(request, card_id):
    """View for deleting a health card"""
    card = get_object_or_404(HealthCard, id=card_id)
    
    if request.method == 'POST':
        # Check if the card is used in any votes
        if Vote.objects.filter(health_card=card).exists():
            return render(request, 'health_cards/health_card_confirm_delete.html', {
                'card': card,
                'error': 'Cannot delete health card with existing votes. Please archive it instead.'
            })
        
        card.delete()
        return redirect('health_card_list')
    
    return render(request, 'health_cards/health_card_confirm_delete.html', {'card': card})

@login_required
def session_list(request):
    """View for listing health check sessions"""
    if request.user.is_admin:
        # Admins can see all sessions
        sessions = HealthCheckSession.objects.all().order_by('-created_at')
    elif request.user.is_department_manager:
        # Department managers can see sessions for teams in their department
        sessions = HealthCheckSession.objects.filter(
            team__department__manager=request.user
        ).order_by('-created_at')
    elif request.user.is_senior_manager:
        # Senior managers can see sessions for teams in departments they manage
        sessions = HealthCheckSession.objects.filter(
            team__department__senior_manager=request.user
        ).order_by('-created_at')
    elif request.user.is_team_leader:
        # Team leaders can see sessions for their team
        sessions = HealthCheckSession.objects.filter(
            team__leader=request.user
        ).order_by('-created_at')
    else:
        # Engineers can see sessions for their team
        if request.user.team:
            sessions = HealthCheckSession.objects.filter(
                team=request.user.team
            ).order_by('-created_at')
        else:
            sessions = HealthCheckSession.objects.none()
    
    return render(request, 'health_cards/session_list.html', {'sessions': sessions})

@login_required
def session_detail(request, session_id):
    """View for health check session details"""
    session = get_object_or_404(HealthCheckSession, id=session_id)
    
    # Check if user has permission to view this session
    if not (request.user.is_admin or 
            (request.user.is_department_manager and session.team.department.manager == request.user) or
            (request.user.is_senior_manager and session.team.department.senior_manager == request.user) or
            (request.user.is_team_leader and session.team.leader == request.user) or
            (request.user.team and request.user.team.id == session.team.id)):
        return redirect('session_list')
    
    # Get votes for this session
    votes = Vote.objects.filter(session=session)
    
    # Calculate participation rate
    team_members_count = session.team.members.count()
    participants_count = votes.values('user').distinct().count()
    participation_rate = (participants_count / team_members_count * 100) if team_members_count > 0 else 0
    
    # Calculate vote distribution
    vote_distribution = {
        'red': votes.filter(vote_value='red').count(),
        'amber': votes.filter(vote_value='amber').count(),
        'green': votes.filter(vote_value='green').count()
    }
    
    # Calculate vote distribution by card
    cards = HealthCard.objects.all()
    card_votes = {}
    for card in cards:
        card_votes[card.id] = {
            'title': card.title,
            'red': votes.filter(health_card=card, vote_value='red').count(),
            'amber': votes.filter(health_card=card, vote_value='amber').count(),
            'green': votes.filter(health_card=card, vote_value='green').count()
        }
    
    return render(request, 'health_cards/session_detail.html', {
        'session': session,
        'participation_rate': participation_rate,
        'vote_distribution': vote_distribution,
        'card_votes': card_votes
    })

@team_leader_required
def session_create(request):
    """View for creating a new health check session"""
    # Team leaders can only create sessions for their team
    team = request.user.team
    
    if not team:
        return redirect('session_list')
    
    if request.method == 'POST':
        quarter = request.POST.get('quarter')
        year = request.POST.get('year')
        status = request.POST.get('status', 'open')
        
        if quarter and year:
            # Check if a session already exists for this team, quarter, and year
            existing_session = HealthCheckSession.objects.filter(
                team=team,
                quarter=quarter,
                year=year
            ).exists()
            
            if existing_session:
                return render(request, 'health_cards/session_form.html', {
                    'team': team,
                    'error': 'A session already exists for this team, quarter, and year.'
                })
            
            session = HealthCheckSession.objects.create(
                team=team,
                quarter=quarter,
                year=year,
                status=status
            )
            return redirect('session_detail', session_id=session.id)
    
    # Get current quarter and year for default values
    now = datetime.datetime.now()
    current_quarter = (now.month - 1) // 3 + 1
    current_year = now.year
    
    return render(request, 'health_cards/session_form.html', {
        'team': team,
        'current_quarter': current_quarter,
        'current_year': current_year
    })

@team_leader_required
def session_update(request, session_id):
    """View for updating a health check session"""
    session = get_object_or_404(HealthCheckSession, id=session_id)
    
    # Team leaders can only update sessions for their team
    if request.user.team != session.team:
        return redirect('session_list')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        
        if status:
            session.status = status
            session.save()
            return redirect('session_detail', session_id=session.id)
    
    return render(request, 'health_cards/session_form.html', {'session': session})

@team_leader_required
def session_delete(request, session_id):
    """View for deleting a health check session"""
    session = get_object_or_404(HealthCheckSession, id=session_id)
    
    # Team leaders can only delete sessions for their team
    if request.user.team != session.team:
        return redirect('session_list')
    
    if request.method == 'POST':
        # Check if the session has votes
        if Vote.objects.filter(session=session).exists():
            return render(request, 'health_cards/session_confirm_delete.html', {
                'session': session,
                'error': 'Cannot delete session with existing votes. Please close it instead.'
            })
        
        session.delete()
        return redirect('session_list')
    
    return render(request, 'health_cards/session_confirm_delete.html', {'session': session})

@login_required
def get_session_cards(request, session_id):
    """API view to get health cards for a session"""
    session = get_object_or_404(HealthCheckSession, id=session_id)
    
    # Check if user has permission to view this session
    if not (request.user.is_admin or 
            (request.user.is_department_manager and session.team.department.manager == request.user) or
            (request.user.is_senior_manager and session.team.department.senior_manager == request.user) or
            (request.user.is_team_leader and session.team.leader == request.user) or
            (request.user.team and request.user.team.id == session.team.id)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get all health cards
    cards = HealthCard.objects.all().values('id', 'title', 'description', 'crappy_example', 'awesome_example')
    
    # Get user's votes for this session
    user_votes = Vote.objects.filter(session=session, user=request.user).values('health_card_id', 'vote_value', 'comment')
    
    # Create a dictionary of user votes for easy lookup
    user_vote_dict = {vote['health_card_id']: {'value': vote['vote_value'], 'comment': vote['comment']} for vote in user_votes}
    
    # Add user's vote to each card
    for card in cards:
        if card['id'] in user_vote_dict:
            card['user_vote'] = user_vote_dict[card['id']]['value']
            card['user_comment'] = user_vote_dict[card['id']]['comment']
        else:
            card['user_vote'] = None
            card['user_comment'] = ''
    
    return JsonResponse({'cards': list(cards)})

@login_required
def get_team_sessions(request, team_id):
    """API view to get sessions for a team"""
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user has permission to view this team's sessions
    if not (request.user.is_admin or 
            (request.user.is_department_manager and team.department.manager == request.user) or
            (request.user.is_senior_manager and team.department.senior_manager == request.user) or
            (request.user.is_team_leader and team.leader == request.user) or
            (request.user.team and request.user.team.id == team.id)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    sessions = HealthCheckSession.objects.filter(team=team).values('id', 'quarter', 'year', 'status')
    return JsonResponse({'sessions': list(sessions)})
