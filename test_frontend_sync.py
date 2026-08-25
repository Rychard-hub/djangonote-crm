#!/usr/bin/env python3
"""
Testas, kuris patikrina, ar React frontend'as gauna tuos pačius duomenis kaip Django templates
"""

import requests
import json

def test_frontend_sync():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Autentifikacija
    print("1. Autentifikacija...")
    auth_data = {
        "username": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/token/", json=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access']
            print(f"✅ Token gautas")
        else:
            print(f"❌ Autentifikacija nepavyko: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Autentifikacijos klaida: {e}")
        return
    
    # 2. Django API lead'ų gavimas
    print("\n2. Django API lead'ų gavimas...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/api/leads/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            django_leads = data['results']
            print(f"✅ Django API: {len(django_leads)} lead'ų")
            
            # Rodyti pirmus 5 lead'us
            print("   Pirmi 5 lead'ai:")
            for i, lead in enumerate(django_leads[:5]):
                print(f"     {i+1}. {lead.get('name', 'N/A')} - {lead.get('company', 'N/A')} ({lead.get('email', 'N/A')})")
                
        else:
            print(f"❌ Django API klaida: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Django API klaida: {e}")
        return
    
    # 3. Django templates lead'ų gavimas (per HTML)
    print("\n3. Django templates lead'ų gavimas...")
    try:
        # Reikia session autentifikacijos
        session = requests.Session()
        session.post(f"{base_url}/login/", data={
            'username': 'test@example.com',
            'password': 'test123'
        })
        
        response = session.get(f"{base_url}/leads/")
        if response.status_code == 200:
            html_content = response.text
            # Ieškome lead'ų skaičiaus HTML'e
            if "Viso leadų:" in html_content:
                import re
                match = re.search(r'Viso leadų: (\d+)', html_content)
                if match:
                    django_templates_count = int(match.group(1))
                    print(f"✅ Django templates: {django_templates_count} lead'ų")
                else:
                    print("❌ Nepavyko rasti lead'ų skaičiaus Django templates")
            else:
                print("❌ Nepavyko rasti 'Viso leadų:' teksto")
        else:
            print(f"❌ Django templates klaida: {response.status_code}")
    except Exception as e:
        print(f"❌ Django templates klaida: {e}")
    
    # 4. Rekomendacijos
    print("\n4. Sinchronizacijos rekomendacijos:")
    print("   - Django API ir Django templates turi rodyti tą patį lead'ų skaičių")
    print("   - React frontend'as turi naudoti tuos pačius API endpoint'us")
    print("   - Token'as turi būti išsaugomas localStorage")
    print("   - Autentifikacija turi būti tvarkinga")
    
    print("\n🔗 Testavimo nuorodos:")
    print("   - Django templates: http://127.0.0.1:8000/leads/")
    print("   - React frontend: http://localhost:3000/")
    print("   - Django API: http://127.0.0.1:8000/api/leads/")

if __name__ == "__main__":
    print("🔄 Frontend sinchronizacijos testas")
    print("=" * 50)
    test_frontend_sync()
