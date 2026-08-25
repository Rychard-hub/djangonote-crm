#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --settings=crm_project.settings_production

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=crm_project.settings_production

# Create superuser if needed (optional)
# python manage.py createsuperuser --settings=crm_project.settings_production --noinput

# Start the application
exec "$@"
