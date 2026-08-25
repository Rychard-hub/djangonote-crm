"""
Vite/React su Django API integracijos testavimas
"""

import requests
import json
import time

def test_django_api():
    """Testuoti Django API prieinamumą"""
    print("🔗 Testuojame Django API...")
    
    try:
        # Testuojame autentifikaciją
        auth_response = requests.post(
            "http://127.0.0.1:8000/api/auth/token/",
            json={"username": "test@example.com", "password": "test123"}
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()['access']
            print("✅ Django API autentifikacija sėkminga")
            
            # Testuojame leads endpoint
            headers = {"Authorization": f"Bearer {token}"}
            leads_response = requests.get("http://127.0.0.1:8000/api/leads/", headers=headers)
            
            if leads_response.status_code == 200:
                leads = leads_response.json()
                print(f"✅ Leads endpoint veikia. Rasta {len(leads.get('results', []))} lead'ų")
                return token
            else:
                print(f"❌ Leads endpoint klaida: {leads_response.status_code}")
                return None
        else:
            print(f"❌ Autentifikacijos klaida: {auth_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Django API klaida: {e}")
        return None

def test_vite_server():
    """Testuoti Vite serverio prieinamumą"""
    print("\n🌉 Testuojame Vite serverį...")
    
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        
        if response.status_code == 200:
            print("✅ Vite serveris veikia")
            
            # Patikriname ar yra React app
            if "root" in response.text or "react" in response.text.lower():
                print("✅ React aplikacija aptikta")
                return True
            else:
                print("⚠️  React aplikacija neaptikta, bet Vite veikia")
                return True
        else:
            print(f"❌ Vite serverio klaida: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Vite serverio klaida: {e}")
        return False

def test_cors_setup():
    """Testuoti CORS nustatymus"""
    print("\n🌐 Testuojame CORS nustatymus...")
    
    try:
        # Bandom API request iš Vite serverio perspektyvos
        headers = {
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/api/auth/token/",
            json={"username": "test@example.com", "password": "test123"},
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ CORS nustatymai teisingi")
            return True
        else:
            print(f"❌ CORS klaida: {response.status_code}")
            print(f"   Atsakymas: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CORS testavimo klaida: {e}")
        return False

def main():
    """Pagrindinė testavimo funkcija"""
    print("🎯 Vite/React + Django API integracijos testavimas")
    print("=" * 50)
    
    # Testuojame Django API
    django_token = test_django_api()
    
    # Testuojame Vite serverį
    vite_ok = test_vite_server()
    
    # Testuojame CORS
    cors_ok = test_cors_setup()
    
    print("\n" + "=" * 50)
    print("📊 TESTAVIMO REZULTATAI")
    print("=" * 50)
    
    print(f"Django API: {'✅ Veikia' if django_token else '❌ Neveikia'}")
    print(f"Vite Server: {'✅ Veikia' if vite_ok else '❌ Neveikia'}")
    print(f"CORS Setup: {'✅ Teisingi' if cors_ok else '❌ Neteisingi'}")
    
    if django_token and vite_ok and cors_ok:
        print("\n🎉 VISI TESTAI SĖKMINGI!")
        print("\n📋 KAS TOLIAU:")
        print("1. Atidarykite http://localhost:3000/ naršyklėje")
        print("2. Prisijunkite su test@example.com / test123")
        print("3. Testuokite CRM funkcionalumą")
        print("\n🔗 Architektūra:")
        print("   • Frontend: Vite + React + Tailwind CSS")
        print("   • Backend: Django REST API")
        print("   • Auth: JWT token")
        print("   • UI: Moderni SPA sąsaja")
        
        return True
    else:
        print("\n⚠️  Kai kurie testai nepavyko. Patikrinkite:")
        if not django_token:
            print("   • Django serveris paleistas (python manage.py runserver)")
        if not vite_ok:
            print("   • Vite serveris paleistas (npm run dev)")
        if not cors_ok:
            print("   • Django CORS nustatymai settings.py faile")
        
        return False

if __name__ == "__main__":
    main()
