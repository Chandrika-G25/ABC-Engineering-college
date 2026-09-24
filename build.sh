#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files into staticfiles/
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Seed database with initial departments, courses, teachers, students, and admin
python manage.py seed_all
