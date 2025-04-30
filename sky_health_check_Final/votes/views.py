from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg
from .models import Vote
from health_cards.models import HealthCard, HealthCheckSession
from teams.models import Team
from accounts.permissions import team_leader_required # Assuming this exists or will be created
import json
# Removed unused imports for torch and transformers
# import torch
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


@login_required
def vote_page(request):
    """View for the voting page"""
    # Get teams the user can vote for
    if request.user.has_admin_privileges: # Use the property defined in the User model
        # Admins and Senior Managers can see all teams
        teams = Team.objects.all()
    elif request.user.is_department_manager:
        # Department managers can see teams in their department(s)
        # Assuming a manager might manage multiple departments, adjust if needed
        teams = Team.objects.filter(department__department_manager=request.user)
    elif request.user.is_team_leader:
        # Team leaders can see their own team(s)
        teams = Team.objects.filter(leader=request.user)
    else:
        # Engineers can see their own team
        if request.user.team:
            teams = Team.objects.filter(id=request.user.team.id)
        else:
            teams = Team.objects.none()
    
    # TODO: Add logic to get active sessions for these teams
    # active_sessions = HealthCheckSession.objects.filter(team__in=teams, status='open')
    
    return render(request, 'votes/vote.html', {'teams': teams})

@login_required
def submit_vote(request):
    """API view to submit or update a vote"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        card_id = data.get('card_id')
        vote_value = data.get('vote_value')
        trend = data.get('trend') # Added trend based on model
        comment = data.get('comment', '')
        
        if not all([session_id, card_id, vote_value, trend]): # Added trend check
            return JsonResponse({'error': 'Missing required fields (session, card, vote, trend)'}, status=400)
        
        # Validate vote value and trend
        if vote_value not in dict(Vote.VOTE_VALUE_CHOICES).keys():
            return JsonResponse({'error': 'Invalid vote value'}, status=400)
        if trend not in dict(Vote.TREND_CHOICES).keys():
            return JsonResponse({'error': 'Invalid trend value'}, status=400)
            
        session = get_object_or_404(HealthCheckSession, id=session_id)
        card = get_object_or_404(HealthCard, id=card_id)
        
        # Check if session is open
        if session.status != 'open':
            return JsonResponse({'error': 'Session is not open for voting'}, status=400)
            
        # Check if card is part of the session
        if card not in session.cards.all():
             return JsonResponse({'error': 'Selected card is not part of this session'}, status=400)

        # Check if user belongs to the team associated with the session
        if request.user.team != session.team and not request.user.has_admin_privileges:
             # Allow admins/senior managers to vote for testing/override? Or restrict strictly?
             # For now, restrict strictly to team members.
             return JsonResponse({'error': 'You do not belong to the team for this session'}, status=403)

        # Use update_or_create for simplicity
        vote, created = Vote.objects.update_or_create(
            session=session,
            user=request.user,
            card=card,
            defaults={
                'vote_value': vote_value,
                'trend': trend,
                'comment': comment
            }
        )
        
        message = 'Vote submitted successfully' if created else 'Vote updated successfully'
        return JsonResponse({'success': True, 'message': message})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except HealthCheckSession.DoesNotExist:
         return JsonResponse({'error': 'Session not found'}, status=404)
    except HealthCard.DoesNotExist:
         return JsonResponse({'error': 'Health Card not found'}, status=404)
    except Exception as e:
        # Log the exception in a real application
        # logger.error(f"Error submitting vote: {e}", exc_info=True)
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

@login_required
def get_user_votes(request, session_id):
    """API view to get user's votes for a specific session"""
    session = get_object_or_404(HealthCheckSession, id=session_id)
    
    # Basic permission check: User must belong to the session's team or have admin rights
    if request.user.team != session.team and not request.user.has_admin_privileges:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    votes = Vote.objects.filter(
        session=session,
        user=request.user
    ).values('card_id', 'vote_value', 'trend', 'comment') # Use card_id instead of health_card_id
    
    # Convert to a dictionary keyed by card_id for easier frontend access
    user_votes_dict = {v['card_id']: v for v in votes}
    
    return JsonResponse({'votes': user_votes_dict})

@login_required
def get_session_votes(request, session_id):
    """API view to get aggregated vote data for a session (for Team Leaders/Managers/Admins)"""
    session = get_object_or_404(HealthCheckSession, id=session_id)
    
    # Permission check: Only TLs of the team, relevant Managers, or Admins can view
    is_relevant_manager = (request.user.is_department_manager and session.team.department.department_manager == request.user) or \
                          (request.user.is_senior_manager and session.team.department.senior_manager == request.user)
    is_team_leader = request.user.is_team_leader and session.team.leader == request.user
    
    if not (request.user.has_admin_privileges or is_relevant_manager or is_team_leader):
        return JsonResponse({'error': 'Permission denied to view session summary'}, status=403)
    
    votes = Vote.objects.filter(session=session)
    session_cards = session.cards.all() # Get cards associated with this session
    
    # Calculate overall vote distribution for the session
    vote_distribution = votes.values('vote_value').annotate(count=Count('id'))
    overall_distribution = {item['vote_value']: item['count'] for item in vote_distribution}
    
    # Calculate vote distribution and comments by card (only for cards in this session)
    card_data = {}
    for card in session_cards:
        card_votes = votes.filter(card=card)
        comments = list(card_votes.exclude(comment__isnull=True).exclude(comment__exact='').values(
            'user__email', # Use email as identifier
            'vote_value', 
            'trend',
            'comment', 
            'updated_at' # Use updated_at for latest comment time
        ).order_by('-updated_at'))
        
        card_data[str(card.id)] = {
            'title': card.title,
            'distribution': {
                'green': card_votes.filter(vote_value='green').count(),
                'amber': card_votes.filter(vote_value='amber').count(),
                'red': card_votes.filter(vote_value='red').count()
            },
            'trend_distribution': {
                'improving': card_votes.filter(trend='improving').count(),
                'stable': card_votes.filter(trend='stable').count(),
                'declining': card_votes.filter(trend='declining').count()
            },
            'comments': comments
        }
        
    # Calculate participation
    team_members_count = session.team.members.count()
    participants_count = votes.values('user').distinct().count()
    participation_rate = (participants_count / team_members_count * 100) if team_members_count > 0 else 0

    return JsonResponse({
        'session_id': session.id,
        'session_name': str(session),
        'team_name': session.team.name,
        'status': session.status,
        'overall_distribution': overall_distribution,
        'card_data': card_data,
        'participation': {
            'participants': participants_count,
            'team_size': team_members_count,
            'rate': round(participation_rate, 2)
        }
    })

@login_required
def summarize_comments_api(request, session_id, card_id):
    """API view to summarize comments for a card in a session (Beta)"""
    session = get_object_or_404(HealthCheckSession, id=session_id)
    card = get_object_or_404(HealthCard, id=card_id)
    
    # Permission check (similar to get_session_votes)
    is_relevant_manager = (request.user.is_department_manager and session.team.department.department_manager == request.user) or \
                          (request.user.is_senior_manager and session.team.department.senior_manager == request.user)
    is_team_leader = request.user.is_team_leader and session.team.leader == request.user
    
    if not (request.user.has_admin_privileges or is_relevant_manager or is_team_leader):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get non-empty comments for this card in this session
    comments = list(Vote.objects.filter(
        session=session, 
        card=card
    ).exclude(comment__isnull=True).exclude(comment__exact='').values_list('comment', flat=True))
    
    if not comments:
        return JsonResponse({'summary': 'No comments available to summarize for this card.'})
    
    # Combine comments into a single text block
    combined_comments = "\n\n".join(comments) # Separate comments by double newline
    
    try:
        # Use the simple placeholder summary function
        # In the future, this could call an external API or a more sophisticated local model
        summary = generate_simple_summary(combined_comments, len(comments))
        
        # Optionally, update the TeamSummary model (if calculation logic is moved here)
        # team_summary, _ = TeamSummary.objects.get_or_create(session=session, card=card, team=session.team)
        # team_summary.aggregated_comments_summary = summary
        # team_summary.save()
        
        return JsonResponse({'summary': summary, 'is_beta': True})
    except Exception as e:
        # Log the exception
        # logger.error(f"Error generating summary: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to generate summary.'}, status=500)

def generate_simple_summary(text, comment_count):
    """Generate a simple extractive summary (placeholder/beta)."""
    # Split into sentences (basic split, might need refinement)
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
    
    if not sentences:
        return "Could not extract meaningful sentences from comments."
    
    # Limit summary length (e.g., first 3 sentences or ~100 words)
    summary_sentences = sentences[:3]
    summary = ". ".join(summary_sentences) + "."
    
    # Add context about the number of comments
    summary += f" (Summary based on {comment_count} comment{'s' if comment_count != 1 else ''})."
    
    return summary

# Removed redundant vote_summary view, logic moved to get_session_votes API
# Removed close_session view, session closing should be an API call or admin action

# TODO: Add views/API endpoints for managing sessions (create, update, list, detail)
# TODO: Add views/API endpoints for managing health cards (CRUD)
# TODO: Add views/API endpoints for managing teams and departments (CRUD)
# TODO: Implement accounts.permissions.team_leader_required decorator

