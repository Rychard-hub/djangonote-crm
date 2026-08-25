import os
import django
from datetime import date, timedelta
from django.contrib.auth.models import User

# Django nustatymai
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

from crm.models import Lead, Comment, Task, Activity, Profile

# Sukuriam testinius duomenis
print("Kuriu testinius duomenis...")

# Patikrinam ar yra vartotojų
if User.objects.count() == 0:
    user = User.objects.create_user(
        username='test@example.com',
        email='test@example.com',
        password='test123'
    )
    Profile.objects.create(user=user, organization='Test Company')
    print("Sukurtas testinis vartotojas")
else:
    user = User.objects.first()
    print(f"Naudotas egzistuojantis vartotojas: {user.email}")

# Ištrinam senus leadus (jei nori)
Lead.objects.filter(owner=user).delete()
print("Ištrinti seni lead'ai")

# Sukuriam naujus leadus
leads_data = [
    {
        'name': 'Jonas Petrauskas',
        'company': 'IT Solutions Ltd',
        'email': 'jonas@itsolutions.lt',
        'phone': '+37061234567',
        'status': 'new',
        'budget': 5000.00,
        'notes': 'Susidomėjo web development projekt',
        'next_follow_up': date.today() + timedelta(days=1)
    },
    {
        'name': 'Agnė Stankevičienė',
        'company': 'Marketing Agency',
        'email': 'agne@marketing.lt',
        'phone': '+37069876543',
        'status': 'contacted',
        'budget': 3000.00,
        'notes': 'Siųstas pasiūlymas, laukiame atsakymo',
        'last_contacted': date.today() - timedelta(days=2),
        'next_follow_up': date.today() - timedelta(days=1)  # Vėluojantis
    },
    {
        'name': 'Marius Kazlauskas',
        'company': 'E-commerce Store',
        'email': 'marius@shop.lt',
        'phone': '+37065555555',
        'status': 'proposal',
        'budget': 8000.00,
        'notes': 'Peržiūrima techninė specifikacija',
        'last_contacted': date.today() - timedelta(days=5),
        'next_follow_up': date.today()
    },
    {
        'name': 'Laura Vitkauskienė',
        'company': 'Startup Hub',
        'email': 'laura@startup.lt',
        'status': 'won',
        'budget': 12000.00,
        'notes': 'Projektas pradėtas, sutartis pasirašyta',
        'last_contacted': date.today() - timedelta(days=10)
    },
    {
        'name': 'Tomas Rimkus',
        'company': 'Restaurant Chain',
        'email': 'tomas@restaurant.lt',
        'status': 'lost',
        'budget': 2000.00,
        'notes': 'Pasirinko konkurentą',
        'last_contacted': date.today() - timedelta(days=15)
    }
]

created_leads = []
for lead_data in leads_data:
    lead = Lead.objects.create(owner=user, **lead_data)
    created_leads.append(lead)
    
    # Sukuriam keletą komentarų ir užduočių
    if lead.status in ['contacted', 'proposal']:
        Comment.objects.create(
            lead=lead,
            body='Pirmasis kontaktas telefonu, aptartos pagrindinės detalės',
            kind='call',
            author='Mano',
            created_by=user
        )
        
        Task.objects.create(
            lead=lead,
            title='Paruošti techninę specifikaciją',
            created_by=user
        )
    
    print(f"Sukurtas lead: {lead.name} ({lead.company})")

print(f"Iš viso sukurta {len(created_leads)} leadų")
print("Testiniai duomenys sėkmingai sukurti!")
print(f"Prisijungti galite su: test@example.com / test123")
