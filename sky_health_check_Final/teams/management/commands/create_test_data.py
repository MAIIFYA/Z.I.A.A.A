from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from teams.models import Department, Team
from health_cards.models import HealthCard, HealthCheckSession
import sys

User = get_user_model()

class Command(BaseCommand):
    help = "Creates initial test data: Department, Team, Health Cards, and an open Health Check Session."

    # --- Configuration ---
    ADMIN_USERNAME = "admin"
    TEST_DEPARTMENT_NAME = "Technology"
    TEST_TEAM_NAME = "Alpha Squad"

    def handle(self, *args, **options):
        self.stdout.write("--- Starting Initial Data Setup ---")

        # --- Get Admin User ---
        try:
            admin_user = User.objects.get(username=self.ADMIN_USERNAME)
            self.stdout.write(self.style.SUCCESS(f"Found admin user: {admin_user.username}"))
        except User.DoesNotExist:
            # Corrected f-string and CommandError usage
            raise CommandError(f"Error: Admin user 

        # --- Create Department (if not exists) ---
        department, created = Department.objects.get_or_create(
            name=self.TEST_DEPARTMENT_NAME,
            defaults={
                "senior_manager": admin_user,
                "department_manager": admin_user
            }
        )
        if created:
            # Corrected f-string
            self.stdout.write(self.style.SUCCESS(f"Department 
        else:
            # Corrected f-string
            self.stdout.write(f"Department 

        # --- Create Team (if not exists) ---
        team, created = Team.objects.get_or_create(
            name=self.TEST_TEAM_NAME,
            department=department,
            defaults={
                "leader": admin_user
            }
        )
        if created:
            # Corrected f-string
            self.stdout.write(self.style.SUCCESS(f"Team 
        else:
            # Corrected f-string
            self.stdout.write(f"Team 

        # --- Add Admin User to Team Members (if not already) ---
        if not team.members.filter(id=admin_user.id).exists():
            team.members.add(admin_user)
            self.stdout.write(self.style.SUCCESS(f"Added {admin_user.username} to team {team.name}"))
        else:
            self.stdout.write(f"{admin_user.username} is already a member of team {team.name}")

        # --- Create Health Cards (if not exist) ---
        cards_data = [
            # Corrected escaped quote
            {"title": "Team Confidence", "description": "How confident are you in our team\"s ability to meet our goals?", "example_awesome": "We are smashing it!", "example_crappy": "We are struggling to keep up."},
            {"title": "Team Morale", "description": "How is the overall morale within the team?", "example_awesome": "Everyone is positive and motivated.", "example_crappy": "People seem stressed and unhappy."},
            {"title": "Technical Debt", "description": "Are we effectively managing technical debt?", "example_awesome": "We refactor regularly and keep our codebase clean.", "example_crappy": "Shortcuts are piling up, making changes difficult."},
        ]

        created_cards = []
        self.stdout.write("--- Creating/Verifying Health Cards ---")
        for card_info in cards_data:
            card, created = HealthCard.objects.get_or_create(
                title=card_info["title"],
                defaults=card_info
            )
            if created:
                # Corrected f-string
                self.stdout.write(self.style.SUCCESS(f"Health Card 
            else:
                # Corrected f-string
                self.stdout.write(f"Health Card 
            created_cards.append(card)

        # --- Create Health Check Session (if no open session for team exists) ---
        current_year = timezone.now().year
        current_quarter = (timezone.now().month - 1) // 3 + 1

        self.stdout.write("--- Checking/Creating Health Check Session ---")
        open_session = HealthCheckSession.objects.filter(
            team=team,
            status=HealthCheckSession.StatusChoices.OPEN
        ).first()

        if not open_session:
            session = HealthCheckSession.objects.create(
                team=team,
                quarter=current_quarter,
                year=current_year,
                created_by=admin_user,
                status=HealthCheckSession.StatusChoices.OPEN
            )
            session.cards.set(created_cards)
            self.stdout.write(self.style.SUCCESS(f"Created new OPEN Health Check Session (ID: {session.id}) for team {team.name} with {len(created_cards)} cards."))
        else:
            self.stdout.write(f"An OPEN Health Check Session (ID: {open_session.id}) already exists for team {team.name}.")
            # Ensure existing open session has the cards
            open_session.cards.add(*created_cards)
            self.stdout.write(self.style.SUCCESS(f"Ensured cards are associated with existing session {open_session.id}."))

        self.stdout.write(self.style.SUCCESS("--- Initial data setup complete. ---"))

