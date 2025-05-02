from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum
from teams.models import Team, Department
from health_cards.models import HealthCheckSession, HealthCard
from votes.models import Vote
from accounts.permissions import team_leader_required, department_manager_required, senior_manager_required, admin_required
import json
import datetime

@login_required
def team_summary(request):
    """View for team summary page"""
    # Get teams the user can view
    if request.user.is_admin:
        # Admins can see all teams
        teams = Team.objects.all()
    elif request.user.is_department_manager:
        # Department managers can see teams in their department
        teams = Team.objects.filter(department__manager=request.user)
    elif request.user.is_senior_manager:
        # Senior managers can see teams in departments they manage
        teams = Team.objects.filter(department__senior_manager=request.user)
    elif request.user.is_team_leader:
        # Team leaders can see their own team
        teams = Team.objects.filter(leader=request.user)
    else:
        # Engineers can see their own team
        if request.user.team:
            teams = Team.objects.filter(id=request.user.team.id)
        else:
            teams = Team.objects.none()
    
    return render(request, 'summaries/team_summary.html', {'teams': teams})

@login_required
def get_team_summary(request, team_id, session_id=None):
    """API view to get summary data for a team"""
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user has permission to view this team
    if not (request.user.is_admin or 
            (request.user.is_department_manager and team.department.manager == request.user) or
            (request.user.is_senior_manager and team.department.senior_manager == request.user) or
            (request.user.is_team_leader and team.leader == request.user) or
            (request.user.team and request.user.team.id == team.id)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # If session_id is provided, get summary for that session
    if session_id:
        session = get_object_or_404(HealthCheckSession, id=session_id, team=team)
        sessions = [session]
    else:
        # Otherwise, get the most recent session
        sessions = HealthCheckSession.objects.filter(team=team).order_by('-created_at')[:1]
    
    if not sessions:
        return JsonResponse({'error': 'No sessions found for this team'}, status=404)
    
    session = sessions[0]
    
    # Get votes for this session
    votes = Vote.objects.filter(session=session)
    
    # Calculate participation rate
    team_members_count = team.members.count()
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
            'red': votes.filter(card=card, vote_value='red').count(),
            'amber': votes.filter(card=card, vote_value='amber').count(),
            'green': votes.filter(card=card, vote_value='green').count()
        }
    
    # Calculate trend (compare with previous session)
    previous_sessions = HealthCheckSession.objects.filter(
        team=team,
        created_at__lt=session.created_at
    ).order_by('-created_at')[:1]
    
    trend = {
        'improving': 0,
        'stable': 0,
        'declining': 0
    }
    
    if previous_sessions:
        previous_session = previous_sessions[0]
        previous_votes = Vote.objects.filter(session=previous_session)
        
        previous_distribution = {
            'red': previous_votes.filter(vote_value='red').count(),
            'amber': previous_votes.filter(vote_value='amber').count(),
            'green': previous_votes.filter(vote_value='green').count()
        }
        
        # Simple trend calculation
        if vote_distribution['green'] > previous_distribution['green']:
            trend['improving'] = 100
        elif vote_distribution['green'] < previous_distribution['green']:
            trend['declining'] = 100
        else:
            trend['stable'] = 100
    else:
        # No previous session, so we'll say it's stable
        trend['stable'] = 100
    
    # Get historical data for trend chart
    historical_sessions = HealthCheckSession.objects.filter(team=team).order_by('created_at')
    historical_data = []
    
    for hist_session in historical_sessions:
        hist_votes = Vote.objects.filter(session=hist_session)
        total_votes = hist_votes.count()
        
        if total_votes > 0:
            red_percent = hist_votes.filter(vote_value='red').count() / total_votes * 100
            amber_percent = hist_votes.filter(vote_value='amber').count() / total_votes * 100
            green_percent = hist_votes.filter(vote_value='green').count() / total_votes * 100
        else:
            red_percent = amber_percent = green_percent = 0
        
        historical_data.append({
            'label': f"Q{hist_session.quarter} {hist_session.year}",
            'red': red_percent,
            'amber': amber_percent,
            'green': green_percent
        })
    
    return JsonResponse({
        'session': {
            'id': session.id,
            'quarter': session.quarter,
            'year': session.year,
            'status': session.status,
            'created_at': session.created_at.strftime('%Y-%m-%d')
        },
        'team': {
            'id': team.id,
            'name': team.name,
            'department': team.department.name,
            'leader': team.leader.get_full_name() if team.leader else 'Not Assigned',
            'members_count': team_members_count
        },
        'participation_rate': participation_rate,
        'vote_distribution': vote_distribution,
        'card_votes': card_votes,
        'trend': trend,
        'historical_data': historical_data
    })

@login_required
def department_summary(request):
    """View for department summary page"""
    # Get departments the user can view
    if request.user.is_admin:
        # Admins can see all departments
        departments = Department.objects.all()
    elif request.user.is_department_manager:
        # Department managers can see departments they manage
        departments = Department.objects.filter(manager=request.user)
    elif request.user.is_senior_manager:
        # Senior managers can see departments they manage
        departments = Department.objects.filter(senior_manager=request.user)
    else:
        # Others can see their own department if they have one
        if request.user.team and request.user.team.department:
            departments = Department.objects.filter(id=request.user.team.department.id)
        else:
            departments = Department.objects.none()
    
    return render(request, 'summaries/department_summary.html', {'departments': departments})

@login_required
def get_department_summary(request, department_id, quarter=None, year=None):
    """API view to get summary data for a department"""
    department = get_object_or_404(Department, id=department_id)
    
    # Check if user has permission to view this department
    if not (request.user.is_admin or 
            (request.user.is_department_manager and department.manager == request.user) or
            (request.user.is_senior_manager and department.senior_manager == request.user) or
            (request.user.team and request.user.team.department.id == department.id)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get teams in this department
    teams = Team.objects.filter(department=department)
    
    # If quarter and year are provided, get sessions for that quarter/year
    if quarter and year:
        sessions = HealthCheckSession.objects.filter(
            team__in=teams,
            quarter=quarter,
            year=year
        )
    else:
        # Otherwise, get the most recent quarter/year that has sessions
        latest_session = HealthCheckSession.objects.filter(
            team__in=teams
        ).order_by('-year', '-quarter').first()
        
        if latest_session:
            quarter = latest_session.quarter
            year = latest_session.year
            sessions = HealthCheckSession.objects.filter(
                team__in=teams,
                quarter=quarter,
                year=year
            )
        else:
            return JsonResponse({'error': 'No sessions found for this department'}, status=404)
    
    # Get all votes for these sessions
    votes = Vote.objects.filter(session__in=sessions)
    
    # Calculate department-wide vote distribution
    vote_distribution = {
        'red': votes.filter(vote_value='red').count(),
        'amber': votes.filter(vote_value='amber').count(),
        'green': votes.filter(vote_value='green').count()
    }
    
    # Calculate vote distribution by team
    team_votes = {}
    for team in teams:
        team_sessions = sessions.filter(team=team)
        team_vote_objects = Vote.objects.filter(session__in=team_sessions)
        total_votes = team_vote_objects.count()
        
        if total_votes > 0:
            red_votes = team_vote_objects.filter(vote_value='red').count()
            amber_votes = team_vote_objects.filter(vote_value='amber').count()
            green_votes = team_vote_objects.filter(vote_value='green').count()
            
            # Calculate trend
            previous_sessions = HealthCheckSession.objects.filter(
                team=team,
                year__lt=year if quarter == 1 else year,
                quarter=4 if quarter == 1 else quarter - 1 if quarter > 1 else None
            )
            
            trend = 'stable'
            if previous_sessions.exists():
                previous_votes = Vote.objects.filter(session__in=previous_sessions)
                previous_total = previous_votes.count()
                
                if previous_total > 0:
                    previous_green_percent = previous_votes.filter(vote_value='green').count() / previous_total * 100
                    current_green_percent = green_votes / total_votes * 100
                    
                    if current_green_percent > previous_green_percent + 5:
                        trend = 'improving'
                    elif current_green_percent < previous_green_percent - 5:
                        trend = 'declining'
            
            team_votes[team.id] = {
                'name': team.name,
                'red_percent': red_votes / total_votes * 100,
                'amber_percent': amber_votes / total_votes * 100,
                'green_percent': green_votes / total_votes * 100,
                'trend': trend
            }
        else:
            team_votes[team.id] = {
                'name': team.name,
                'red_percent': 0,
                'amber_percent': 0,
                'green_percent': 0,
                'trend': 'stable'
            }
    
    # Calculate vote distribution by card
    cards = HealthCard.objects.all()
    card_votes = {}
    for card in cards:
        card_vote_objects = votes.filter(card=card)
        total_card_votes = card_vote_objects.count()
        
        if total_card_votes > 0:
            card_votes[card.id] = {
                'title': card.title,
                'red_percent': card_vote_objects.filter(vote_value='red').count() / total_card_votes * 100,
                'amber_percent': card_vote_objects.filter(vote_value='amber').count() / total_card_votes * 100,
                'green_percent': card_vote_objects.filter(vote_value='green').count() / total_card_votes * 100
            }
        else:
            card_votes[card.id] = {
                'title': card.title,
                'red_percent': 0,
                'amber_percent': 0,
                'green_percent': 0
            }
    
    # Get historical data for trend chart
    quarters = []
    for y in range(year - 1, year + 1):
        for q in range(1, 5):
            if y < year or (y == year and q <= quarter):
                quarters.append({'year': y, 'quarter': q})
    
    historical_data = []
    for q in quarters:
        q_sessions = HealthCheckSession.objects.filter(
            team__in=teams,
            quarter=q['quarter'],
            year=q['year']
        )
        
        if q_sessions.exists():
            q_votes = Vote.objects.filter(session__in=q_sessions)
            total_q_votes = q_votes.count()
            
            if total_q_votes > 0:
                historical_data.append({
                    'label': f"Q{q['quarter']} {q['year']}",
                    'red': q_votes.filter(vote_value='red').count() / total_q_votes * 100,
                    'amber': q_votes.filter(vote_value='amber').count() / total_q_votes * 100,
                    'green': q_votes.filter(vote_value='green').count() / total_q_votes * 100
                })
    
    # Calculate department statistics
    total_engineers = sum(team.members.count() for team in teams)
    total_participants = votes.values('user').distinct().count()
    participation_rate = (total_participants / total_engineers * 100) if total_engineers > 0 else 0
    
    return JsonResponse({
        'department': {
            'id': department.id,
            'name': department.name,
            'manager': department.manager.get_full_name() if department.manager else 'Not Assigned',
            'senior_manager': department.senior_manager.get_full_name() if department.senior_manager else 'Not Assigned'
        },
        'period': {
            'quarter': quarter,
            'year': year
        },
        'statistics': {
            'total_teams': teams.count(),
            'total_engineers': total_engineers,
            'participation_rate': participation_rate
        },
        'vote_distribution': vote_distribution,
        'team_votes': team_votes,
        'card_votes': card_votes,
        'historical_data': historical_data
    })

@login_required
def get_available_quarters(request, department_id):
    """API view to get available quarters for a department"""
    department = get_object_or_404(Department, id=department_id)
    
    # Check if user has permission to view this department
    if not (request.user.is_admin or 
            (request.user.is_department_manager and department.manager == request.user) or
            (request.user.is_senior_manager and department.senior_manager == request.user) or
            (request.user.team and request.user.team.department.id == department.id)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get teams in this department
    teams = Team.objects.filter(department=department)
    
    # Get all quarters that have sessions
    sessions = HealthCheckSession.objects.filter(team__in=teams).values('quarter', 'year').distinct().order_by('-year', '-quarter')
    
    quarters = [{'quarter': s['quarter'], 'year': s['year']} for s in sessions]
    
    return JsonResponse({'quarters': quarters})

@login_required
def get_card_comments(request, session_id, card_id):
    """API view to get comments for a card in a session"""
    session = get_object_or_404(HealthCheckSession, id=session_id)
    card = get_object_or_404(HealthCard, id=card_id)
    
    # Check if user has permission to view this session
    if not (request.user.is_admin or 
            (request.user.is_department_manager and session.team.department.manager == request.user) or
            (request.user.is_senior_manager and session.team.department.senior_manager == request.user) or
            (request.user.is_team_leader and session.team.leader == request.user) or
            (request.user.team and request.user.team.id == session.team.id)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get comments for this card in this session
    votes = Vote.objects.filter(session=session, health_card=card).exclude(comment='')
    
    comments = []
    for vote in votes:
        comments.append({
            'user': vote.user.get_full_name() or vote.user.username,
            'vote_value': vote.vote_value,
            'comment': vote.comment,
            'created_at': vote.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Generate AI summary if there are comments
    summary = ""
    if comments:
        # Combine comments into a single text
        combined_comments = " ".join([c['comment'] for c in comments])
        
        # Use a simple extractive summarization
        sentences = combined_comments.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            if len(sentences) <= 3:
                summary = ". ".join(sentences) + "."
            else:
                summary = ". ".join(sentences[:3]) + f". Plus {len(sentences) - 3} more comments."
        else:
            summary = "No meaningful comments to summarize."
    else:
        summary = "No comments to summarize."
    
    return JsonResponse({
        'card': {
            'id': card.id,
            'title': card.title
        },
        'comments': comments,
        'summary': summary
    })
