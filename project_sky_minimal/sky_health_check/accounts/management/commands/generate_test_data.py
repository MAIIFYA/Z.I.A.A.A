import random
import os
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from teams.models import Department, Team
from health_cards.models import HealthCheckSession, HealthCard
from votes.models import Vote
from django.conf import settings # Import settings

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = "Generates test data including departments, teams, users, sessions, and votes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users", type=int, default=50, help=
            "Number of users to create (default: 50)"
        )
        parser.add_argument(
            "--teams", type=int, default=10, help=
            "Number of teams to create (default: 10)"
        )
        parser.add_argument(
            "--departments", type=int, default=3, help=
            "Number of departments to create (default: 3)"
        )
        parser.add_argument(
            "--quarters", type=int, default=4, help=
            "Number of past quarters to create sessions for (default: 4)"
        )

    def handle(self, *args, **options):
        num_users = options["users"]
        num_teams = options["teams"]
        num_departments = options["departments"]
        num_quarters = options["quarters"]

        self.stdout.write("Starting data generation...")

        # --- Clear Existing Data (Except Superuser and Health Cards) ---
        self.stdout.write(self.style.WARNING("Clearing existing test data (Votes, Sessions, Users, Teams, Departments)..."))
        # Delete in order of dependency
        Vote.objects.all().delete()
        HealthCheckSession.objects.all().delete()
        User.objects.filter(is_superuser=False).delete() # Keep superuser
        Team.objects.all().delete()
        Department.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Existing test data cleared."))

        # --- Ensure Health Cards Exist ---
        if not HealthCard.objects.exists():
            self.stdout.write(self.style.WARNING(
                "No health cards found. Attempting to load them..."))
            try:
                from django.core.management import call_command
                json_file_path = os.path.join(settings.BASE_DIR, "health_cards_data.json")
                if not os.path.exists(json_file_path):
                     self.stderr.write(self.style.ERROR(f"Health card JSON file not found at {json_file_path}. Please create it first."))
                     return
                call_command("load_health_cards")
                self.stdout.write(self.style.SUCCESS("Health cards loaded."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"Failed to load health cards: {e}. Please run 'python manage.py load_health_cards' manually."))
                return

        all_health_cards = list(HealthCard.objects.all())
        if not all_health_cards:
            self.stderr.write(self.style.ERROR("Health cards could not be loaded or do not exist. Cannot generate votes."))
            return

        # --- Create Superuser ---
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write("Creating superuser...")
            User.objects.create_superuser(
                username="admin", email="admin@example.com", password="adminpass")
            self.stdout.write(self.style.SUCCESS(
                "Superuser created (admin/adminpass)"))

        # --- Create Departments ---
        self.stdout.write(f"Creating/finding {num_departments} departments...")
        departments = []
        for _ in range(num_departments):
            department_name = fake.unique.bs().title() + " Department"
            department, created = Department.objects.get_or_create(
                name=department_name)
            departments.append(department)
        self.stdout.write(self.style.SUCCESS(f"{len(departments)} departments ensured."))

        # --- Create Teams ---
        self.stdout.write(f"Creating/finding {num_teams} teams...")
        teams = []
        team_leaders = []
        for i in range(num_teams):
            team_name = fake.unique.word().capitalize() + " Team"
            department = random.choice(departments)
            team, created = Team.objects.get_or_create(
                name=team_name, department=department)
            teams.append(team)
        self.stdout.write(self.style.SUCCESS(f"{len(teams)} teams ensured."))

        # --- Create Users ---
        self.stdout.write(f"Creating {num_users} users...")
        users_created_count = 0
        all_users = []
        possible_roles = [role[0] for role in User.ROLE_CHOICES if role[0] != "admin"]

        # Assign Team Leaders first
        for team in teams:
            if not team.leader:
                first_name = fake.first_name()
                last_name = fake.last_name()
                username = f"leader_{team.name.lower().replace(' ', '_')}{random.randint(1, 99)}"
                email = f"{username}@example.com"
                counter = 0
                while User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                    counter += 1
                    username = f"leader_{team.name.lower().replace(' ', '_')}{random.randint(1, 99)}_{counter}"
                    email = f"{username}@example.com"
                    if counter > 10: break
                if counter > 10: continue

                try:
                    leader = User.objects.create_user(
                        username=username, email=email, password="password",
                        first_name=first_name, last_name=last_name,
                        role="team_leader", team=team, is_staff=True
                    )
                    team.leader = leader
                    team.save()
                    team_leaders.append(leader)
                    all_users.append(leader)
                    users_created_count += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Could not create leader for team {team.name}: {e}"))

        # Create remaining users
        remaining_users_needed = num_users - users_created_count
        for i in range(remaining_users_needed):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 99)}"
            email_base = f"{first_name.lower()}.{last_name.lower()}"
            email_suffix = fake.unique.domain_name()
            email = f"{email_base}@{email_suffix}"
            counter = 0
            while User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                counter += 1
                username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 99)}{counter}"
                email = f"{email_base}{counter}@{email_suffix}"
                if counter > 10: break
            if counter > 10:
                self.stderr.write(self.style.ERROR(f"Could not generate unique username/email for {first_name} {last_name} after 10 attempts."))
                continue

            password = "password"
            role = random.choice(possible_roles)
            team = random.choice(teams) if teams else None

            try:
                user = User.objects.create_user(
                    username=username, email=email, password=password,
                    first_name=first_name, last_name=last_name,
                    role=role, team=team
                )
                all_users.append(user)
                users_created_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Could not create user {username}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"{users_created_count} users created/ensured."))

        # --- Create Health Check Sessions ---
        self.stdout.write(f"Creating health check sessions for {num_quarters} quarters...")
        sessions_created_count = 0
        all_sessions = []
        today = timezone.now().date()
        for team in teams:
            for i in range(num_quarters):
                current_quarter = ((today.month - 1) // 3)
                target_quarter = (current_quarter - i) % 4
                year_offset = (current_quarter - i) // 4
                session_year = today.year + year_offset
                session_month = target_quarter * 3 + 1
                session_day = 1
                try:
                    session_date = timezone.datetime(session_year, session_month, session_day).date()
                    session_name = f"Q{target_quarter + 1} {session_year}"
                    status = "open" if i < 2 else "closed"

                    session, created = HealthCheckSession.objects.get_or_create(
                        team=team,
                        session_date=session_date,
                        defaults={"name": session_name, "status": status}
                    )
                    # Removed session.cards.set(all_health_cards) as the M2M no longer exists
                    if created:
                        sessions_created_count += 1
                    all_sessions.append(session)
                except ValueError:
                    pass

        self.stdout.write(self.style.SUCCESS(f"{sessions_created_count} health check sessions created."))

        # --- Generate Varied Votes ---
        self.stdout.write("Generating varied votes for open sessions...")
        votes_created_count = 0
        open_sessions = [s for s in all_sessions if s.status == "open"]

        if not open_sessions:
            self.stdout.write(self.style.WARNING("No open sessions found to generate votes for."))
        else:
            for session in open_sessions:
                team_members = User.objects.filter(team=session.team)
                # Use all_health_cards directly as sessions don't link to cards anymore
                session_cards = all_health_cards
                if not session_cards:
                    continue

                    if random.random() < 0.8:
                        for card in session_cards:
                            if random.random() < 0.9:
                                # Introduce more variety based on team/card
                                team_bias = hash(session.team.name) % 3 # 0, 1, 2
                                card_bias = hash(card.title) % 3 # 0, 1, 2

                                if team_bias == 0: # Team A tends to vote lower
                                    weights = [0.5, 0.3, 0.2]
                                elif team_bias == 1: # Team B tends to vote higher
                                    weights = [0.1, 0.3, 0.6]
                                else: # Team C is average
                                    weights = [0.3, 0.4, 0.3]

                                if card_bias == 0: # Card type A slightly shifts lower
                                    weights = [w + 0.1 if i == 0 else (w - 0.05 if i > 0 else w) for i, w in enumerate(weights)]
                                elif card_bias == 1: # Card type B slightly shifts higher
                                    weights = [w - 0.05 if i == 0 else (w + 0.1 if i == 2 else w) for i, w in enumerate(weights)]
                                
                                # Normalize weights to sum to 1
                                total_weight = sum(weights)
                                weights = [w / total_weight for w in weights]

                                vote_value = random.choices(["red", "amber", "green"], weights=weights, k=1)[0]

                                comment = ""
                                if random.random() < 0.3:
                                    comment = fake.sentence(nb_words=random.randint(5, 15))

                                try:
                                    Vote.objects.update_or_create(
                                        session=session,
                                        card=card, # Corrected field name
                                        user=member,
                                        defaults={
                                            "vote_value": vote_value,
                                            "comment": comment,
                                            "created_at": timezone.now() - timedelta(days=random.randint(0, 5))
                                        }
                                    )
                                    votes_created_count += 1
                                except Exception as e:
                                     self.stderr.write(self.style.ERROR(f"Could not create vote for user {member.username} on card {card.title}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"{votes_created_count} votes created/updated."))

        # --- Create Specific Test User ---
        self.stdout.write("Creating specific test user...")
        test_user_email = "test_engineer@example.com"
        test_user_username = "test_engineer"
        test_user_password = "password"
        test_user_role = "engineer"
        test_team = teams[0] if teams else None

        if test_team:
            # Ensure the test team has an open session
            open_session_exists = False
            for s in all_sessions:
                if s.team == test_team and s.status == "open":
                    open_session_exists = True
                    break
            if not open_session_exists:
                self.stdout.write(self.style.WARNING(f"Test team {test_team.name} has no open sessions. Creating one..."))
                today = timezone.now().date()
                session_date = today.replace(day=1)
                session_name = f"Current Quarter {today.year}"
                try:
                    session, created = HealthCheckSession.objects.get_or_create(
                        team=test_team,
                        session_date=session_date,
                        defaults={"name": session_name, "status": "open"}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created open session for {test_team.name}."))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Could not create open session for {test_team.name}: {e}"))

            # Create or update the test user
            try:
                test_user, created = User.objects.update_or_create(
                    email=test_user_email,
                    defaults={
                        "username": test_user_username,
                        "first_name": "Test",
                        "last_name": "Engineer",
                        "role": test_user_role,
                        "team": test_team,
                        "is_staff": False, # Engineers are not staff
                        "is_superuser": False
                    }
                )
                test_user.set_password(test_user_password)
                test_user.save()
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created test user: {test_user_email} / {test_user_password} (Role: {test_user_role}, Team: {test_team.name})"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated test user: {test_user_email} / {test_user_password} (Role: {test_user_role}, Team: {test_team.name})"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Could not create/update test user {test_user_email}: {e}"))
        else:
            self.stdout.write(self.style.WARNING("No teams exist, cannot create specific test user assigned to a team."))


        self.stdout.write(self.style.SUCCESS("Data generation complete."))

