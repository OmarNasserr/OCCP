import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocpp_backend.settings')
django.setup()

User = get_user_model()

try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Superuser created successfully.")
    else:
        print("Superuser already exists.")
except Exception as e:
    print('Error creating superuser:', e)
    print('please manually create superuser using python manage.py createsuperuser')