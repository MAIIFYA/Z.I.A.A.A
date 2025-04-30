import sys
from django.contrib.auth import get_user_model
from django.utils import timezone
from teams.models import Department, Team
from health_cards.models import HealthCard, HealthCheckSession

User = get_user_model()

# --- Configuration ---
ADMIN_USERNAME = "admin"
TEST_DEPARTMENT_NAME = "Technology"
TEST_TEAM_NAME = "Alpha Squad"

print("--- Starting Initial Data Setup ---")

# --- Get Admin User ---
try:
    admin_user = User.objects.get(username=ADMIN_USERNAME)
    print(f"Found admin user: {admin_user.username}")
except User.DoesNotExist:
    print(f"Error: Admin user 
    sys.exit(1)

# --- Create Department (if not exists) ---
department, created = Department.objects.get_or_create(
    name=TEST_DEPARTMENT_NAME,
    defaults={
        "senior_manager": admin_user,
        "department_manager": admin_user
    }
)
if created:
    print(f"Department 
else:
    print(f"Department 

# --- Create Team (if not exists) ---
team, created = Team.objects.get_or_create(
    name=TEST_TEAM_NAME,
    department=department,
    defaults={
        "leader": admin_user
    }
)
if created:
    print(f"Team 
else:
    print(f"Team 

# --- Add Admin User to Team Members (if not already) ---
if not team.members.filter(id=admin_user.id).exists():
    team.members.add(admin_user)
    print(f"Added {admin_user.username} to team {team.name}")
else:
    print(f"{admin_user.username} is already a member of team {team.name}")

# --- Create Health Cards (if not exist) ---
cards_data = [
    {"title": "Team Confidence", "description": "How confident are you in our team's ability to meet our goals?", "example_awesome": "We are smashing it!", "example_crappy": "We are struggling to keep up."},
    {"title": "Team Morale", "description": "How is the overall morale within the team?", "example_awesome": "Everyone is positive and motivated.", "example_crappy": "People seem stressed and unhappy."},
    {"title": "Technical Debt", "description": "Are we effectively managing technical debt?", "example_awesome": "We refactor regularly and keep our codebase clean.", "example_crappy": "Shortcuts are piling up, making changes difficult."},
]

created_cards = []
print("--- Creating/Verifying Health Cards ---")
for card_info in cards_data:
    card, created = HealthCard.objects.get_or_create(
        title=card_info["title"],
        defaults=card_info
    )
    if created:
        print(f"Health Card 
    else:
        print(f"Health Card 
    created_cards.append(card)

# --- Create Health Check Session (if no open session for team exists) ---
current_year = timezone.now().year
current_quarter = (timezone.now().month - 1) // 3 + 1

print("--- Checking/Creating Health Check Session ---")
open_session = HealthCheckSession.objects.filter(
    team=team,
    status=HealthCheckSession.StatusChoices.OPEN
).first() # Get the first open session if it exists

if not open_session:
    session = HealthCheckSession.objects.create(
        team=team,
        quarter=current_quarter,
        year=current_year,
        created_by=admin_user,
        status=HealthCheckSession.StatusChoices.OPEN
    )
    session.cards.set(created_cards)
    print(f"Created new OPEN Health Check Session (ID: {session.id}) for team {team.name} with {len(created_cards)} cards.")
else:
    print(f"An OPEN Health Check Session (ID: {open_session.id}) already exists for team {team.name}.")
    # Ensure existing open session has the cards
    open_session.cards.add(*created_cards)
    print(f"Ensured cards are associated with existing session {open_session.id}.")

print("--- Initial data setup complete. ---")

