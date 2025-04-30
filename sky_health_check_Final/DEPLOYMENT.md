# Deployment Guide for Sky Health Check

This guide provides detailed instructions for deploying the Sky Health Check application to various hosting platforms.

## Table of Contents
1. [Local Deployment](#local-deployment)
2. [PythonAnywhere Deployment](#pythonanywhere-deployment)
3. [Heroku Deployment](#heroku-deployment)
4. [AWS Elastic Beanstalk Deployment](#aws-elastic-beanstalk-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Production Settings](#production-settings)

## Local Deployment

For local deployment or testing, follow these steps:

1. Clone the repository and navigate to the project directory
2. Run the installation script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
3. Start the development server:
   ```bash
   source venv/bin/activate
   python manage.py runserver
   ```
4. Access the application at http://127.0.0.1:8000/

## PythonAnywhere Deployment

PythonAnywhere is a great option for small to medium-sized projects with minimal setup.

1. Sign up for a PythonAnywhere account at https://www.pythonanywhere.com/
2. Upload the project files:
   - Use Git: `git clone https://github.com/your-username/sky-health-check.git`
   - Or upload the zip file and extract it
3. Create a virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 sky_health_check_env
   cd sky_health_check
   pip install -r requirements.txt
   ```
4. Set up the database:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Configure a new web app:
   - Go to the Web tab in PythonAnywhere
   - Click "Add a new web app"
   - Select "Manual configuration" and Python 3.10
   - Set the path to your project directory
   - Configure the WSGI file to point to your Django project
   - Set the virtual environment path
6. Configure static files:
   - In the Web tab, add the static files mapping:
     - URL: /static/
     - Directory: /home/yourusername/sky_health_check/static/
7. Reload the web app and access it at yourusername.pythonanywhere.com

## Heroku Deployment

Heroku provides easy deployment with good scalability.

1. Create a Heroku account at https://www.heroku.com/
2. Install the Heroku CLI and log in:
   ```bash
   heroku login
   ```
3. Create a `Procfile` in the project root with:
   ```
   web: gunicorn sky_health_check.wsgi --log-file -
   ```
4. Add the following to requirements.txt:
   ```
   gunicorn==20.1.0
   django-heroku==0.3.1
   ```
5. Create a `runtime.txt` file with:
   ```
   python-3.10.12
   ```
6. Update settings.py for Heroku:
   ```python
   import django_heroku
   
   # At the bottom of the file
   django_heroku.settings(locals())
   ```
7. Create a new Heroku app:
   ```bash
   heroku create sky-health-check
   ```
8. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY='your_secret_key'
   heroku config:set DEBUG=False
   ```
9. Deploy the application:
   ```bash
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku main
   ```
10. Run migrations:
    ```bash
    heroku run python manage.py migrate
    heroku run python manage.py createsuperuser
    ```
11. Access your app at https://sky-health-check.herokuapp.com/

## AWS Elastic Beanstalk Deployment

AWS Elastic Beanstalk provides a robust, scalable environment.

1. Install the EB CLI:
   ```bash
   pip install awsebcli
   ```
2. Initialize EB:
   ```bash
   eb init -p python-3.10 sky-health-check
   ```
3. Create a `.ebextensions/django.config` file:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: sky_health_check.wsgi:application
     aws:elasticbeanstalk:environment:proxy:staticfiles:
       /static: static
   ```
4. Create a requirements.txt file if not already present
5. Create an EB environment:
   ```bash
   eb create sky-health-check-env
   ```
6. Set environment variables:
   ```bash
   eb setenv SECRET_KEY=your_secret_key DEBUG=False
   ```
7. Deploy the application:
   ```bash
   eb deploy
   ```
8. Run migrations:
   ```bash
   eb ssh
   cd /opt/python/current/app
   source /opt/python/run/venv/bin/activate
   python manage.py migrate
   python manage.py createsuperuser
   ```
9. Access your app at the provided EB URL

## Docker Deployment

Docker provides a consistent environment across different platforms.

1. Create a `Dockerfile` in the project root:
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   RUN python manage.py collectstatic --noinput
   
   EXPOSE 8000
   
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "sky_health_check.wsgi"]
   ```
2. Create a `docker-compose.yml` file:
   ```yaml
   version: '3'
   
   services:
     web:
       build: .
       command: gunicorn sky_health_check.wsgi --bind 0.0.0.0:8000
       volumes:
         - .:/app
       ports:
         - "8000:8000"
       environment:
         - SECRET_KEY=your_secret_key
         - DEBUG=False
       depends_on:
         - db
     db:
       image: postgres:13
       volumes:
         - postgres_data:/var/lib/postgresql/data/
       environment:
         - POSTGRES_PASSWORD=postgres
         - POSTGRES_USER=postgres
         - POSTGRES_DB=sky_health_check
   
   volumes:
     postgres_data:
   ```
3. Build and run the Docker containers:
   ```bash
   docker-compose up -d --build
   ```
4. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```
5. Access your app at http://localhost:8000/

## Production Settings

Before deploying to production, update the following settings in `settings.py`:

1. Set DEBUG to False:
   ```python
   DEBUG = False
   ```
2. Configure allowed hosts:
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```
3. Set up a secure SECRET_KEY:
   ```python
   SECRET_KEY = os.environ.get('SECRET_KEY', 'default_key_for_dev')
   ```
4. Configure a production database:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.environ.get('DB_NAME', 'sky_health_check'),
           'USER': os.environ.get('DB_USER', 'postgres'),
           'PASSWORD': os.environ.get('DB_PASSWORD', ''),
           'HOST': os.environ.get('DB_HOST', 'localhost'),
           'PORT': os.environ.get('DB_PORT', '5432'),
       }
   }
   ```
5. Configure static files:
   ```python
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   STATIC_URL = '/static/'
   ```
6. Set up HTTPS:
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```
7. Configure email settings:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.yourmailprovider.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
   ```

Remember to set these environment variables in your hosting platform's configuration.
