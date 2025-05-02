#!/bin/bash

# Sky Health Check Installation Script
# This script automates the setup process for the Sky Health Check application

echo "=== Sky Health Check Installation Script ==="
echo "This script will set up the Sky Health Check application."
echo

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python is installed: $PYTHON_VERSION"
else
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check if pip is installed
if command -v pip3 &>/dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo "✅ pip is installed: $PIP_VERSION"
else
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Create virtual environment
echo
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -eq 0 ]; then
    echo "✅ Virtual environment created successfully."
else
    echo "❌ Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
echo
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -eq 0 ]; then
    echo "✅ Virtual environment activated successfully."
else
    echo "❌ Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
echo
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully."
else
    echo "❌ Failed to install dependencies."
    exit 1
fi

# Run migrations
echo
echo "Setting up database..."
python manage.py migrate
if [ $? -eq 0 ]; then
    echo "✅ Database setup completed successfully."
else
    echo "❌ Failed to set up database."
    exit 1
fi

# Create superuser
echo
echo "Would you like to create a superuser account? (y/n)"
read -r CREATE_SUPERUSER

if [ "$CREATE_SUPERUSER" = "y" ] || [ "$CREATE_SUPERUSER" = "Y" ]; then
    echo "Creating superuser account..."
    python manage.py createsuperuser
    if [ $? -eq 0 ]; then
        echo "✅ Superuser created successfully."
    else
        echo "❌ Failed to create superuser."
    fi
fi

# Collect static files
echo
echo "Collecting static files..."
python manage.py collectstatic --noinput
if [ $? -eq 0 ]; then
    echo "✅ Static files collected successfully."
else
    echo "❌ Failed to collect static files."
    exit 1
fi

# Create sample data
echo
echo "Would you like to create sample data? (y/n)"
read -r CREATE_SAMPLE_DATA

if [ "$CREATE_SAMPLE_DATA" = "y" ] || [ "$CREATE_SAMPLE_DATA" = "Y" ]; then
    echo "Creating sample data..."
    python manage.py loaddata sample_data.json
    if [ $? -eq 0 ]; then
        echo "✅ Sample data created successfully."
    else
        echo "❌ Failed to create sample data."
    fi
fi

# Start development server
echo
echo "Setup completed successfully!"
echo
echo "To start the development server, run:"
echo "source venv/bin/activate"
echo "python manage.py runserver"
echo
echo "Then open your browser and navigate to: http://127.0.0.1:8000/"
echo
echo "=== Installation Complete ==="
