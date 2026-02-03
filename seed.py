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
# Create Superuser for Admin access
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(username='admin', email='admin@example.com', password='Raju@143')
    print("Created superuser: admin")
else:
    u = User.objects.get(username='admin')
    u.set_password('Raju@143')
    u.is_staff = True
    u.is_superuser = True
    u.save()
    print("Updated superuser: admin")
