web: gunicorn gescoches.wsgi:application
release: python manage.py migrate && python create_admin.py && python manage.py collectstatic --noinput
