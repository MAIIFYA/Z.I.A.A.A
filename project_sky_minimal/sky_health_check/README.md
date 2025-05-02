# Sky Health Check Website

A comprehensive health check system for Sky teams to evaluate their performance and track improvements over time.

## Features

- **User Authentication**: Secure login and registration system with role-based permissions
- **Multiple User Roles**: Support for Engineers, Team Leaders, Senior Leaders, Department Leaders, and Administrators
- **Health Card Voting**: Interactive traffic light voting system for team health evaluation
- **Team and Department Management**: Comprehensive management of organizational structure
- **Session Management**: Create and manage health check sessions for teams
- **Summary and Reporting**: Visual dashboards with charts and trends
- **Comment Summarization**: AI-powered summarization of feedback comments
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Smooth animations and transitions for enhanced user experience

## Technology Stack

- **Backend**: Django 4.2.7, Python 3.10
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Authentication**: Django Authentication System with custom user model
- **Charts**: Chart.js for data visualization
- **Animations**: CSS animations and JavaScript transitions

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/your-username/sky-health-check.git
cd sky-health-check
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up the database**

```bash
python manage.py migrate
```

5. **Create a superuser (admin)**

```bash
python manage.py createsuperuser
```

6. **Run the development server**

```bash
python manage.py runserver
```

7. **Access the application**

Open your browser and navigate to http://127.0.0.1:8000/

## User Roles and Permissions

- **Engineer**: Can participate in health check votes and view their team's results
- **Team Leader**: Can create sessions, view team results, and manage their team
- **Senior Leader**: Can view multiple teams and department-level summaries
- **Department Leader**: Can manage departments and view department-level summaries
- **Administrator**: Has full access to all features and can manage users, teams, and departments

## Testing

### Running Tests

To run the automated tests:

```bash
python manage.py test
```

### Manual Testing

1. **User Authentication**
   - Register a new user
   - Log in with existing credentials
   - Test password reset functionality
   - Verify role-based access control

2. **Team Management**
   - Create, edit, and delete teams
   - Assign team leaders and members
   - Verify team hierarchy

3. **Health Check Sessions**
   - Create new sessions
   - Submit votes using the traffic light system
   - Add comments to votes
   - Close sessions

4. **Summaries and Reports**
   - View team summaries
   - Check department summaries
   - Verify historical trends
   - Test comment summarization

## Deployment Options

### Option 1: PythonAnywhere (Recommended for Small Projects)

1. Sign up for a PythonAnywhere account at https://www.pythonanywhere.com/
2. Upload the project files
3. Set up a virtual environment and install dependencies
4. Configure the WSGI file
5. Set up a web app with Django

Pros:
- Free tier available
- Easy setup
- Managed environment

### Option 2: Heroku

1. Create a Heroku account at https://www.heroku.com/
2. Install the Heroku CLI
3. Create a `Procfile` with: `web: gunicorn sky_health_check.wsgi --log-file -`
4. Add `django-heroku` to requirements.txt
5. Configure `settings.py` for Heroku
6. Deploy using Git

Pros:
- Good scalability
- Easy integration with CI/CD
- Add-ons for databases and monitoring

### Option 3: AWS Elastic Beanstalk

1. Create an AWS account
2. Install the EB CLI
3. Configure the application for EB
4. Deploy using `eb deploy`

Pros:
- Highly scalable
- Enterprise-grade infrastructure
- Integrated with other AWS services

### Option 4: Docker + Any Cloud Provider

1. Create a Dockerfile and docker-compose.yml
2. Build the Docker image
3. Deploy to any cloud provider that supports Docker (AWS, GCP, Azure, DigitalOcean)

Pros:
- Consistent environment
- Easy scaling
- Platform independence

## Configuration for Production

Before deploying to production, make sure to:

1. Set `DEBUG = False` in settings.py
2. Configure a proper database (PostgreSQL recommended)
3. Set up proper `SECRET_KEY` environment variable
4. Configure static files serving
5. Set up HTTPS with proper SSL certificates
6. Configure email settings for password reset functionality

## Maintenance

### Database Backups

Regular database backups are recommended:

```bash
python manage.py dumpdata > backup.json
```

### Updates and Upgrades

1. Pull the latest code changes
2. Install any new dependencies
3. Apply migrations
4. Restart the application

## Troubleshooting

### Common Issues

1. **Database migration errors**
   - Solution: Try `python manage.py migrate --fake-initial`

2. **Static files not loading**
   - Solution: Run `python manage.py collectstatic`

3. **Permission issues**
   - Solution: Check user roles and permissions in the admin panel

## Support

For any issues or questions, please contact the development team at support@example.com.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
