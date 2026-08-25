"""
Testinio vartotojo kūrimas API testavimui
"""

import os
import django

# Django nustatymai
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

from django.contrib.auth.models import User
from crm.models import Profile

def create_test_user():
    """Sukuria testinį vartotoją"""
    
    # Ištrinam egzistuojantį testinį vartotoją
    User.objects.filter(username='test@example.com').delete()
    
    # Sukuriam naują testinį vartotoją
    user = User.objects.create_user(
        username='test@example.com',
        email='test@example.com',
        password='test123',
        first_name='Test',
        last_name='User'
    )
    
    # Sukuriam profilį
    profile = Profile.objects.create(
        user=user,
        organization='Test Company',
        timezone='Europe/Vilnius',
        reminder_days=1
    )
    
    print(f"✅ Testinis vartotojas sukurtas:")
    print(f"   El. paštas: test@example.com")
    print(f"   Slaptažodis: test123")
    print(f"   Vartotojo ID: {user.id}")
    
    return user

if __name__ == "__main__":
    create_test_user()
