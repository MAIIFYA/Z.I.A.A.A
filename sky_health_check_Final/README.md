# Sky Health Check Website

A comprehensive health check system for Sky teams to evaluate their performance and track improvements over time.

## Features

- **User Authentication**: Secure login and registration system with role-based permissions (using django-allauth).
- **Multiple User Roles**: Support for Engineers, Team Leaders, Senior Managers (with Admin capabilities), Department Managers, and Administrators.
- **Health Card Voting**: Interactive traffic light voting system (Declining, Stable, Improving) for team health evaluation.
- **Team and Department Management**: Comprehensive management of organizational structure.
- **Session Management**: Create and manage health check sessions for teams.
- **Summary and Reporting**: Basic structure for visual dashboards (further implementation needed).
- **Comment Summarization (Beta)**: Placeholder for AI-powered summarization of feedback comments.
- **Responsive Design**: Basic structure, works on desktop and mobile devices.
- **Modern UI**: Basic styling matching provided mockups, with CSS animations for smooth transitions.

## Technology Stack

- **Backend**: Django 4.2.7, Python 3.10
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (development/default)
- **Authentication**: Django Authentication System + django-allauth
- **API**: Django REST Framework (for potential future API needs)
- **Animations**: CSS animations

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1.  **Unzip the Project**
    Unzip the provided `sky_health_check_final.zip` file into a directory of your choice.

2.  **Navigate to the Project Directory**
    Open your terminal or command prompt and change into the project's root directory (the one containing `manage.py`):
    ```bash
    cd path/to/sky_health_check
    ```

3.  **Create and Activate a Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate    # On Windows
    ```

4.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up the Database**
    This will create the SQLite database file and apply the necessary table structures.
    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser (Admin)**
    This account will have full administrative privileges.
    ```bash
    python manage.py createsuperuser
    ```
    When prompted:
    - Username: `admin`
    - Email address: (enter any valid email)
    - Password: `testpassword123` (or choose your own, but remember it)

7.  **Create Initial Test Data (Optional but Recommended)**
    To populate the system with a sample department, team, user roles, health cards, and an open session for testing, run the following commands in the Django shell:

    ```bash
    python manage.py shell
    ```

    Then, paste and execute the following Python code block inside the shell:

    ```python
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from teams.models import Department, Team
    from health_cards.models import HealthCard, HealthCheckSession
    User = get_user_model()

    # Get the admin user (assuming username is 'admin')
    try:
        admin_user = User.objects.get(username='admin')
        print(f'Got user: {admin_user.username}')
    except User.DoesNotExist:
        print("Admin user 'admin' not found. Please create it first using 'python manage.py createsuperuser'.")
        exit()

    # Create Department
    department, created = Department.objects.get_or_create(
        name="Technology",
        defaults={"senior_manager": admin_user, "department_manager": admin_user}
    )
    print(f"Department 'Technology' {'created' if created else 'retrieved'}.")

    # Create Team
    team, created = Team.objects.get_or_create(
        name="Alpha Squad",
        department=department,
        defaults={"leader": admin_user}
    )
    print(f"Team 'Alpha Squad' {'created' if created else 'retrieved'}.")

    # Add admin user to the team members
    team.members.add(admin_user)
    print(f"Added {admin_user.username} to team {team.name}")

    # Create Health Cards
    card1, created1 = HealthCard.objects.get_or_create(title="Team Confidence", defaults={"description": "How confident are you in our team's ability to meet our goals?", "example_awesome": "We are smashing it!", "example_crappy": "We are struggling to keep up."})
    card2, created2 = HealthCard.objects.get_or_create(title="Team Morale", defaults={"description": "How is the overall morale within the team?", "example_awesome": "Everyone is positive and motivated.", "example_crappy": "People seem stressed and unhappy."})
    card3, created3 = HealthCard.objects.get_or_create(title="Technical Debt", defaults={"description": "Are we effectively managing technical debt?", "example_awesome": "We refactor regularly and keep our codebase clean.", "example_crappy": "Shortcuts are piling up, making changes difficult."})
    print(f"Health Card 'Team Confidence' {'created' if created1 else 'retrieved'}.")
    print(f"Health Card 'Team Morale' {'created' if created2 else 'retrieved'}.")
    print(f"Health Card 'Technical Debt' {'created' if created3 else 'retrieved'}.")

    # Create Health Check Session
    current_year = timezone.now().year
    current_quarter = (timezone.now().month - 1) // 3 + 1
    session, created = HealthCheckSession.objects.get_or_create(
        team=team,
        quarter=f"Q{current_quarter}", # Ensure quarter is string like 'Q1', 'Q2' etc.
        year=current_year,
        defaults={
            "status": 'open',
            "created_by": admin_user
        }
    )
    print(f"Health Check Session for {team.name} Q{current_quarter} {current_year} {'created' if created else 'retrieved'}.")

    # Associate cards with the session
    session.cards.set([card1, card2, card3])
    print(f"Associated {session.cards.count()} cards with session {session.id}")

    # Exit the shell
    exit()
    ```

8.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```

9.  **Access the Application**
    Open your browser and navigate to http://127.0.0.1:8000/
    Log in using the superuser credentials (`admin` / `testpassword123` or your chosen password).

## User Roles and Permissions (Summary)

- **Engineer**: Can participate in health check votes for their team.
- **Team Leader**: Can manage their team, create/manage sessions, view team results.
- **Senior Manager**: Has Administrator capabilities (can manage users, teams, departments, view all summaries).
- **Department Manager**: Can manage their department, view department summaries.
- **Administrator**: Has full access to all features via the Django Admin interface (`/admin/`).

## Testing

Basic manual testing is recommended:

1.  **Login/Logout**: Test with the created admin user.
2.  **Navigate**: Explore the Dashboard, Vote, Summaries, Profile, and Administration links (note: some pages like Summaries might be basic placeholders).
3.  **Voting**: Go to the 'Vote' page. Select the 'Alpha Squad' team and the current session. Try casting votes (Declining/Stable/Improving) and adding comments for each card.
4.  **Admin Interface**: Access `/admin/` to view and manage Users, Departments, Teams, Health Cards, Sessions, and Votes directly.

*(Note: Automated tests mentioned in the original README are not fully implemented in this version.)*

## Next Steps / Potential Enhancements

- Implement detailed Summary views with charts and trend analysis.
- Integrate a real AI/LLM for comment summarization.
- Flesh out role-specific dashboards and permissions more granularly in the frontend views.
- Add more comprehensive automated tests.
- Implement email notifications.
- Refine UI/UX and animations.

## Deployment Options

(Refer to the original README section for various deployment options like PythonAnywhere, Heroku, AWS, Docker. Remember to configure settings like `DEBUG=False`, `SECRET_KEY`, database, and static files for production.)

## License

This project is provided as-is. Please review licensing if applicable.

