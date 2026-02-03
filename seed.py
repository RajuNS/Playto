import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playto_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

users = ['alice', 'bob', 'charlie']
for username in users:
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username=username, password='password')
        print(f"Created user: {username}")
    else:
        # Reset password to ensure it matches 'password' just in case
        u = User.objects.get(username=username)
        u.set_password('password')
        u.save()
        print(f"Updated user: {username}")
