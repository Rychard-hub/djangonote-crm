#!/usr/bin/env python3
"""
Testas, kuris patikrina React frontend sinchronizaciją su Django API
"""

import requests
import json
import time

def test_react_sync():
    print("🔄 React Frontend Sinchronizacijos Testas")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Patikriname Django API
    print("\n1. Django API patikrinimas...")
    try:
        auth_response = requests.post(f"{base_url}/api/auth/token/", json={
            "username": "test@example.com",
            "password": "test123"
        })
        
        if auth_response.status_code == 200:
            token = auth_response.json()['access']
            headers = {"Authorization": f"Bearer {token}"}
            
            leads_response = requests.get(f"{base_url}/api/leads/", headers=headers)
            if leads_response.status_code == 200:
                data = leads_response.json()
                django_count = len(data['results'])
                print(f"✅ Django API: {django_count} lead'ų")
                
                # Rodyti pirmus 3 lead'us
                print("   Pirmi 3 lead'ai:")
                for i, lead in enumerate(data['results'][:3]):
                    print(f"     {i+1}. {lead.get('name', 'N/A')} - {lead.get('company', 'N/A')}")
            else:
                print(f"❌ Django API klaida: {leads_response.status_code}")
                return
        else:
            print(f"❌ Autentifikacija nepavyko: {auth_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Django API klaida: {e}")
        return
    
    # 2. Patikriname React frontend
    print("\n2. React frontend patikrinimas...")
    print("   📱 Atidarykite http://localhost:3000 naršyklėje")
    print("   🔧 Atidarykite naršyklės konsolę (F12)")
    print("   🔍 Ieškokite šių žinučių:")
    print("      - '🔍 React useLeads: Gauti leadai: X'")
    print("      - '🔑 API fetch su token: /leads/'")
    print("      - '📡 API atsakymas: /leads/ 200'")
    
    # 3. Instrukcijos testavimui
    print("\n3. Testavimo instrukcijos:")
    print("   a) Prisijunkite prie React frontend su:")
    print("      - El. paštas: test@example.com")
    print("      - Slaptažodis: test123")
    print("   b) Perjunkite į 'Lead'ai' puslapį")
    print("   c) Patikrinkite konsolėje, kiek lead'ų gauta")
    print("   d) Palyginkite su Django API rezultatais")
    
    # 4. Sinchronizacijos patikrinimas
    print("\n4. Sinchronizacijos patikrinimas:")
    print(f"   Django API rodo: {django_count} lead'ų")
    print("   React frontend turi rodyti tą patį skaičių")
    print("   Jei skaičiai nesutampa - problema yra autentifikacijoje")
    
    # 5. Galimos problemos ir sprendimai
    print("\n5. Galimos problemos ir sprendimai:")
    print("   ❌ Jei rodo 0 lead'ų:")
    print("      - Patikrinkite, ar token'as išsaugotas localStorage")
    print("      - Patikrinkite, ar API kvietimai vyksta su token'u")
    print("   ❌ Jei rodo klaidą 401:")
    print("      - Token'as gali būti nebegaliojantis")
    print("      - Reikia prisijungti iš naujo")
    print("   ❌ Jei rodo klaidą 403:")
    print("      - Vartotojas neturi teisių")
    print("   ✅ Jei viskas veikia:")
    print("      - React frontend'as sinchronizuotas")
    print("      - Galima naudoti sistemą")
    
    print("\n🔗 Naudingos nuorodos:")
    print("   - React frontend: http://localhost:3000")
    print("   - Django templates: http://127.0.0.1:8000/leads/")
    print("   - Django API: http://127.0.0.1:8000/api/leads/")

if __name__ == "__main__":
    test_react_sync()
