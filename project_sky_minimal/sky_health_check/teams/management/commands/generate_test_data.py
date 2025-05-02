import os
import django
import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sky_health_check.settings")
django.setup()

from accounts.models import User
from teams.models import Department, Team
from health_cards.models import HealthCard, HealthCheckSession

fake = Faker()

class Command(BaseCommand):
    help = "Generates test data for departments, teams, users, and sessions."

    def add_arguments(self, parser):
        parser.add_argument("--departments", type=int, default=5, help="Number of departments to create")
        parser.add_argument("--teams-per-dept", type=int, default=4, help="Number of teams per department")
        parser.add_argument("--users-per-team", type=int, default=10, help="Number of users per team")
        parser.add_argument("--sessions-per-team", type=int, default=2, help="Number of sessions per team")
        parser.add_argument("--password", type=str, default="password123", help="Default password for all users")

    def handle(self, *args, **options):
        num_departments = options["departments"]
        num_teams_per_dept = options["teams_per_dept"]
        num_users_per_team = options["users_per_team"]
        num_sessions_per_team = options["sessions_per_team"]
        default_password = make_password(options["password"])

        self.stdout.write("Generating test data...")

        # Get all health cards to assign to sessions
        all_health_cards = list(HealthCard.objects.all())
        if not all_health_cards:
            self.stderr.write(self.style.ERROR("No health cards found. Please load health cards first using load_health_cards command."))
            # Optionally create some default cards here if needed
            # HealthCard.objects.create(title="Default Card 1", description="Desc 1", example_awesome="Good", example_crappy="Bad")
            # all_health_cards = list(HealthCard.objects.all())
            # if not all_health_cards:
            #     return # Exit if still no cards

        # Create Admin User if not exists
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "password": default_password,
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created admin user: admin@example.com"))

        departments = []
        for _ in range(num_departments):
            dept_name = fake.bs().replace(" ", "") + " Department"
            # Create Department Manager
            manager_email = f"dept_manager_{fake.user_name()}@example.com"
            manager_username = manager_email.split("@")[0]
            dept_manager, created = User.objects.get_or_create(
                username=manager_username,
                defaults={
                    "email": manager_email,
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "password": default_password,
                    "role": "department_manager",
                    "is_staff": True, # Dept managers might need staff access
                }
            )
            if created:
                 self.stdout.write(f"Created Department Manager: {manager_email}")
                 
            department, created = Department.objects.get_or_create(
                name=dept_name,
                defaults={"senior_manager": dept_manager} # Assigning dept manager as senior manager for simplicity
            )
            if created:
                self.stdout.write(f"Created Department: {dept_name}")
            departments.append(department)

            teams = []
            for i in range(num_teams_per_dept):
                team_name = fake.job().replace(" ", "") + f"_Team_{i+1}"
                # Create Team Leader
                leader_email = f"team_leader_{fake.user_name()}@example.com"
                leader_username = leader_email.split("@")[0]
                team_leader, created = User.objects.get_or_create(
                    username=leader_username,
                    defaults={
                        "email": leader_email,
                        "first_name": fake.first_name(),
                        "last_name": fake.last_name(),
                        "password": default_password,
                        "role": "team_leader",
                        "is_staff": True, # Team leaders might need staff access
                    }
                )
                if created:
                    self.stdout.write(f"Created Team Leader: {leader_email}")
                    
                team, created = Team.objects.get_or_create(
                    name=team_name,
                    department=department,
                    defaults={"leader": team_leader}
                )
                if created:
                    self.stdout.write(f"  Created Team: {team_name} in {department.name}")
                teams.append(team)
                
                # Assign leader to team
                team_leader.team = team
                team_leader.save()

                # Create Engineers for the team
                for j in range(num_users_per_team):
                    user_email = f"engineer_{fake.user_name()}_{i}_{j}@example.com"
                    user_username = user_email.split("@")[0]
                    user, created = User.objects.get_or_create(
                        username=user_username,
                        defaults={
                            "email": user_email,
                            "first_name": fake.first_name(),
                            "last_name": fake.last_name(),
                            "password": default_password,
                            "role": "engineer",
                            "team": team,
                        }
                    )
                    if created:
                        self.stdout.write(f"    Created Engineer: {user_email} in {team.name}")
                        
                # Create Sessions for the team
                for k in range(num_sessions_per_team):
                    year = 2024 - (k // 4) # Example: create sessions for past years/quarters
                    quarter_num = (k % 4) + 1
                    quarter = f"Q{quarter_num}"
                    session, created = HealthCheckSession.objects.get_or_create(
                        team=team,
                        quarter=quarter,
                        year=year,
                        defaults={
                            "status": random.choice(["open", "closed"])
                        }
                    )
                    if created:
                        self.stdout.write(f"    Created Session: {quarter} {year} for {team.name}")
                        # Add all health cards to the session
                        if all_health_cards:
                            session.cards.set(all_health_cards)
                            self.stdout.write(f"      Added {len(all_health_cards)} cards to session {session.id}")
                    else:
                         self.stdout.write(f"    Session already exists: {quarter} {year} for {team.name}")


        self.stdout.write(self.style.SUCCESS("Successfully generated test data."))

# Note: This script needs to be placed inside a Django app's management/commands directory
# e.g., /home/ubuntu/project_sky_minimal/sky_health_check/teams/management/commands/generate_test_data.py

