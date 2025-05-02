from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, F
from .models import Vote
from health_cards.models import HealthCard, HealthCheckSession
from teams.models import Team
from accounts.permissions import team_leader_required
import json
# Removed torch and transformers imports
# import torch
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


@login_required
def vote_page(request):
    """View for the voting page"""
    # Get teams the user can vote for
    if request.user.is_admin:
        # Admins can see all teams
        teams = Team.objects.all()
    elif request.user.is_department_manager:
        # Department managers can see teams in their department
        # Assuming department has a manager field, adjust if needed
        # This might need refinement based on exact model structure
        teams = Team.objects.filter(department__senior_manager=request.user) # Assuming senior_manager is the dept head
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

    # Get active sessions for these teams
    active_sessions = HealthCheckSession.objects.filter(team__in=teams, status="open").select_related("team")

    return render(request, "votes/vote.html", {"sessions": active_sessions})

@login_required
def submit_vote(request):
    """API view to submit a vote"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        session_id = data.get("session_id")
        card_id = data.get("card_id")
        vote_value = data.get("vote_value")
        comment = data.get("comment", "")

        if not all([session_id, card_id, vote_value]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Validate vote value
        if vote_value not in ["red", "amber", "green"]:
            return JsonResponse({"error": "Invalid vote value"}, status=400)

        session = get_object_or_404(HealthCheckSession, id=session_id)
        card = get_object_or_404(HealthCard, id=card_id)

        # Check if session is open
        if session.status != "open":
            return JsonResponse({"error": "Session is not open for voting"}, status=400)

        # Refined permission check: Only team members or the team leader can submit votes
        can_submit = False
        if request.user.is_authenticated:
            # Check if the user is the leader of the session's team
            if request.user.is_team_leader and session.team.leader and request.user == session.team.leader:
                can_submit = True
            # Check if the user is a member of the session's team (and not the leader)
            elif not request.user.is_team_leader and request.user.team and request.user.team == session.team:
                can_submit = True

        if not can_submit:
            return JsonResponse({"error": "Permission denied. Only team members and leaders can submit votes for this session."}, status=403)

        # Check if user has already voted for this card in this session
        existing_vote, created = Vote.objects.update_or_create(
            session=session,
            card=card, # Corrected field name
            user=request.user,
            defaults={
                "vote_value": vote_value,
                "comment": comment
            }
        )

        if created:
            return JsonResponse({"success": True, "message": "Vote submitted successfully"})
        else:
            return JsonResponse({"success": True, "message": "Vote updated successfully"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except HealthCheckSession.DoesNotExist:
         return JsonResponse({"error": "Session not found"}, status=404)
    except HealthCard.DoesNotExist:
         return JsonResponse({"error": "Health card not found"}, status=404)
    except Exception as e:
        # Log the exception e
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)

@login_required
def get_user_votes(request, session_id):
    """API view to get user"s votes for a session"""
    session = get_object_or_404(HealthCheckSession, id=session_id)

       # Refined permission check: Only team members or the team leader can load votes for voting
    is_voter = False
    if request.user.is_authenticated:
        # Check if the user is the leader of the session's team
        if request.user.is_team_leader and session.team.leader and request.user == session.team.leader:
            is_voter = True
        # Check if the user is a member of the session's team (and not the leader, handled above)
        elif not request.user.is_team_leader and request.user.team and request.user.team == session.team:
            is_voter = True
        # Allow admin to load for testing/debugging? Or deny? Let's deny for strictness.
        # elif request.user.is_admin:
        #     is_voter = True 

    if not is_voter:
        # Log details for debugging
        print(f"Permission denied for user {request.user.username} (role: {request.user.role}, team: {request.user.team}) attempting to load voting data for session {session_id} (team: {session.team.name}, leader: {session.team.leader})")
        return JsonResponse({"error": "Permission denied. Only team members and leaders can load data for voting."}, status=403)

    # Fetch votes only for the requesting user
    votes = Vote.objects.filter(
        session=session,
        user=request.user
    ).values("card_id", "vote_value", "comment").annotate(health_card_id=F("card_id")) # Alias card_id as health_card_id for JS

    # Get all health cards, as sessions no longer link directly to cards
    all_health_cards = HealthCard.objects.all().values(
        "id", "title", "description", 
        "example_green", "example_amber", "example_red", # Use correct field names
        "image_path"
    )

    return JsonResponse({"votes": list(votes), "cards": list(all_health_cards)})

@login_required
def get_session_votes(request, session_id):
    """API view to get all votes for a session (for managers/admins)"""
    session = get_object_or_404(HealthCheckSession, id=session_id)

    # Check if user has permission to view all votes (leader, manager, admin)
    if not (request.user.is_admin or
            (request.user.is_team_leader and request.user == session.team.leader) or
            (request.user.is_department_manager and request.user == session.team.department.senior_manager) # Assuming senior_manager is dept head
           ):
        return JsonResponse({"error": "Permission denied"}, status=403)

    votes = Vote.objects.filter(session=session)

    # Calculate vote distribution
    vote_distribution = votes.values("vote_value").annotate(count=Count("id"))
    distribution_dict = {item["vote_value"]: item["count"] for item in vote_distribution}
    distribution_dict.setdefault("red", 0)
    distribution_dict.setdefault("amber", 0)
    distribution_dict.setdefault("green", 0)

    # Calculate vote distribution by card
    card_votes_query = votes.values("health_card__id", "health_card__title", "vote_value").annotate(count=Count("id"))
    card_votes = {}
    for item in card_votes_query:
        card_id = item["health_card__id"]
        if card_id not in card_votes:
            card_votes[card_id] = {
                "title": item["health_card__title"],
                "red": 0,
                "amber": 0,
                "green": 0
            }
        card_votes[card_id][item["vote_value"]] = item["count"]

    # Get comments by card
    card_comments_query = votes.exclude(comment="").order_by("health_card__title", "created_at") \
                           .values("health_card__id", "health_card__title", "user__username", "vote_value", "comment", "created_at")
    card_comments = {}
    for item in card_comments_query:
        card_id = item["health_card__id"]
        if card_id not in card_comments:
            card_comments[card_id] = {
                "title": item["health_card__title"],
                "comments": []
            }
        card_comments[card_id]["comments"].append({
            "user": item["user__username"],
            "vote": item["vote_value"],
            "comment": item["comment"],
            "timestamp": item["created_at"].isoformat()
        })

    return JsonResponse({
        "vote_distribution": distribution_dict,
        "card_votes": card_votes,
        "card_comments": card_comments
    })

@login_required
def summarize_comments(request, session_id, card_id):
    """API view to summarize comments for a card in a session (placeholder)"""
    session = get_object_or_404(HealthCheckSession, id=session_id)
    card = get_object_or_404(HealthCard, id=card_id)

    # Check if user has permission to view comments (leader, manager, admin)
    if not (request.user.is_admin or
            (request.user.is_team_leader and request.user == session.team.leader) or
            (request.user.is_department_manager and request.user == session.team.department.senior_manager) # Assuming senior_manager is dept head
           ):
        return JsonResponse({"error": "Permission denied"}, status=403)

    # Get comments for this card in this session
    votes = Vote.objects.filter(session=session, health_card=card).exclude(comment="")
    comments = [vote.comment for vote in votes]

    if not comments:
        return JsonResponse({"summary": "No comments to summarize."})

    # Combine comments into a single text
    combined_comments = " ".join(comments)

    try:
        # Use the simpler placeholder summary logic
        summary = generate_placeholder_summary(combined_comments)
        return JsonResponse({"summary": summary})
    except Exception as e:
        # Log the exception e
        return JsonResponse({"error": "Error generating summary."}, status=500)

def generate_placeholder_summary(text):
    """Generate a placeholder summary of the given text."""
    # Simple extractive summarization (placeholder)
    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return "No meaningful comments to summarize."

    if len(sentences) <= 3:
        summary = ". ".join(sentences) + "."
    else:
        summary = ". ".join(sentences[:3]) + "."
        summary += f" Plus {len(sentences) - 3} more comments."

    return summary

@team_leader_required # Ensure only team leaders can access this
def close_session(request, session_id):
    """View to close a health check session"""
    session = get_object_or_404(HealthCheckSession, id=session_id, team=request.user.team)

    if request.method == "POST":
        session.status = "closed"
        session.save()
        # Redirect to a relevant page, e.g., dashboard or session list
        return redirect("dashboard") # Assuming a dashboard URL exists

    return render(request, "votes/close_session_confirm.html", {"session": session})

@login_required
def vote_summary(request, session_id):
    """View for vote summary page"""
    session = get_object_or_404(HealthCheckSession, id=session_id)

    # Check if user has permission to view this session summary
    if not (request.user.is_admin or
            request.user.team == session.team or
            (request.user.is_team_leader and request.user == session.team.leader) or
            (request.user.is_department_manager and request.user == session.team.department.senior_manager) # Assuming senior_manager is dept head
           ):
         # Redirect or show error if no permission
        return redirect("dashboard") # Or render an error page

    votes = Vote.objects.filter(session=session)

    # Calculate participation rate
    team_members_count = session.team.members.count()
    participants_count = votes.values("user").distinct().count()
    participation_rate = (participants_count / team_members_count * 100) if team_members_count > 0 else 0

    # Calculate vote distribution
    vote_distribution_query = votes.values("vote_value").annotate(count=Count("id"))
    distribution_dict = {item["vote_value"]: item["count"] for item in vote_distribution_query}
    distribution_dict.setdefault("red", 0)
    distribution_dict.setdefault("amber", 0)
    distribution_dict.setdefault("green", 0)

    # Calculate vote distribution by card
    card_votes_query = votes.values("health_card__id", "health_card__title", "vote_value").annotate(count=Count("id"))
    card_votes = {}
    # Ensure all health cards are included, even if they have no votes
    all_health_cards = HealthCard.objects.all()
    for card in all_health_cards:
         card_votes[card.id] = {
            "title": card.title,
            "red": 0,
            "amber": 0,
            "green": 0
        }
    for item in card_votes_query:
        card_id = item["health_card__id"]
        if card_id in card_votes: # Should always be true if cards are loaded correctly
            card_votes[card_id][item["vote_value"]] = item["count"]

    # Get comments by card
    card_comments_query = votes.exclude(comment="").order_by("health_card__title", "created_at") \
                           .values("health_card__id", "health_card__title", "user__username", "vote_value", "comment", "created_at")
    card_comments = {}
    # Ensure all health cards are included
    all_health_cards_for_comments = HealthCard.objects.all()
    for card in all_health_cards_for_comments:
        card_comments[card.id] = {
            "title": card.title,
            "comments": []
        }
    for item in card_comments_query:
        card_id = item["health_card__id"]
        if card_id in card_comments:
            card_comments[card_id]["comments"].append({
                "user": item["user__username"],
                "vote": item["vote_value"],
                "comment": item["comment"],
                "timestamp": item["created_at"].isoformat()
            })

    return render(request, "votes/vote_summary.html", {
        "session": session,
        "participation_rate": participation_rate,
        "vote_distribution": distribution_dict,
        "card_votes": card_votes,
        "card_comments": card_comments
    })

