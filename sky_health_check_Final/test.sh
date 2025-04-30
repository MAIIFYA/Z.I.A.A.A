#!/bin/bash

# Sky Health Check Testing Script
# This script automates the testing process for the Sky Health Check application

echo "=== Sky Health Check Testing Script ==="
echo "This script will run tests for the Sky Health Check application."
echo

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️ Virtual environment is not activated."
    echo "Please activate the virtual environment first:"
    echo "source venv/bin/activate"
    exit 1
fi

# Run unit tests
echo "Running unit tests..."
python manage.py test accounts teams health_cards votes summaries
if [ $? -eq 0 ]; then
    echo "✅ Unit tests passed successfully."
else
    echo "❌ Unit tests failed."
    exit 1
fi

# Run coverage tests
echo
echo "Running coverage tests..."
if command -v coverage &>/dev/null; then
    coverage run --source='.' manage.py test accounts teams health_cards votes summaries
    coverage report
    if [ $? -eq 0 ]; then
        echo "✅ Coverage tests completed successfully."
    else
        echo "❌ Coverage tests failed."
        exit 1
    fi
else
    echo "⚠️ Coverage tool not installed. Install with: pip install coverage"
fi

# Run linting
echo
echo "Running linting checks..."
if command -v flake8 &>/dev/null; then
    flake8 .
    if [ $? -eq 0 ]; then
        echo "✅ Linting checks passed successfully."
    else
        echo "⚠️ Linting checks found issues. Please review the output above."
    fi
else
    echo "⚠️ Flake8 not installed. Install with: pip install flake8"
fi

echo
echo "=== Testing Complete ==="
echo "If all tests passed, the application is ready for deployment."
